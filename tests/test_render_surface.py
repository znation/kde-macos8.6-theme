"""Tests for tools/render_surface.py, the headless Plasma render-and-capture script."""

from __future__ import annotations

import errno
import os
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import process_runner
from support.cli_fixtures import assert_missing_tool_named, call_main
from support.platinum_palette import FACE, hex_colour
from support.reference_image import read_reference, skip_unless_materialized
from tools import render_surface  # noqa: E402
from tools.fidelity_metrics import compare, crop  # noqa: E402
from tools.png import pixel_at, read_png  # noqa: E402
from tools.png.write import encode_png  # noqa: E402

SCRIPT = str(repo_root.ROOT / "tools" / "render_surface.py")
REFERENCE = str(
    repo_root.ROOT / "macos8.6-screenshots" / "aboutsystem_betawiki.png"
)
# The retail Japanese 8.6 System Profiler window shows a zoom box; the
# aboutsystem window cannot be zoomed, so its title bar has none.
PROFILER_REFERENCE = str(
    repo_root.ROOT / "macos8.6-screenshots" / "systemprofiler_betawiki.png"
)
# The render's title bar sits at the top of the 320x240 capture (row 0 is the
# top outline, row 21 the bottom outline); the reference screenshot has the
# same chrome at y=25..46, so the strips are compared at those offsets.
CANDIDATE_CROP = (30, 0, 80, 22)
REFERENCE_CROP = (30, 25, 80, 22)
# The frame's side and bottom borders sit at the render's edges; the reference
# screenshot has the same chrome offset by its window position (left outline
# x=7, top outline y=25). The reference window is taller than the render, so
# the side strips cover only the straight run between the title bar and the
# bottom border (212 rows), and the bottom strip the border between the two
# corners (308 columns).
LEFT_BORDER_CANDIDATE = (0, 22, 6, 212)
LEFT_BORDER_REFERENCE = (7, 47, 6, 212)
RIGHT_BORDER_CANDIDATE = (314, 22, 6, 212)
RIGHT_BORDER_REFERENCE = (354, 47, 6, 212)
BOTTOM_BORDER_CANDIDATE = (6, 234, 308, 6)
BOTTOM_BORDER_REFERENCE = (13, 419, 308, 6)
# The title-bar boxes: the 13x13 close and collapse boxes and the 21x13 zoom
# canvas (its stripe-free gap plus the 13px box). The render puts the window
# at the capture's origin; aboutsystem's window is at (7, 25), so its close
# box sits at (11, 29) and its collapse box at (343, 29), while the profiler
# window's zoom canvas is at (776, 26).
CLOSE_CANDIDATE = (4, 4, 13, 13)
CLOSE_REFERENCE = (11, 29, 13, 13)
COLLAPSE_CANDIDATE = (303, 4, 13, 13)
COLLAPSE_REFERENCE = (343, 29, 13, 13)
ZOOM_CANDIDATE = (282, 4, 21, 13)
ZOOM_REFERENCE = (776, 26, 21, 13)


class StubTools(unittest.TestCase):
    """Base for tests that run `main` against shell stubs of the external tools."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="render-surface-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        # Capture the real make before the stub directory goes on PATH.
        self.real_make = shutil.which("make")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.scratch_parent = self.root / "tmp"
        self.scratch_parent.mkdir()
        self.stub("make", "exit 0")
        for name in render_surface.REQUIRED_TOOLS:
            if name != "make":
                self.stub(name, "exit 0")
        path = f"{self.bin}{os.pathsep}{os.environ['PATH']}"
        patches = (
            mock.patch.dict(os.environ, {"PATH": path}),
            mock.patch.object(tempfile, "tempdir", str(self.scratch_parent)),
        )
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def stub(self, name, body):
        """Write an executable stub named *name* that runs *body*."""
        path = self.bin / name
        path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def assert_scratch_removed(self):
        """Assert the scratch parent holds no leftover entries."""
        self.assertEqual([], os.listdir(self.scratch_parent))


class TestMissingTool(unittest.TestCase):
    def test_names_the_first_missing_tool_and_exits_2(self):
        with tempfile.TemporaryDirectory() as empty:
            with mock.patch.dict(os.environ, {"PATH": empty}):
                status, stderr = call_main(render_surface.main, "out.png")
        self.assertEqual(2, status)
        self.assertIn(render_surface.REQUIRED_TOOLS[0], stderr)
        self.assertIn("render_surface: error:", stderr)

    def test_a_single_missing_tool_is_the_one_named(self):
        assert_missing_tool_named(
            self, render_surface.main, render_surface.REQUIRED_TOOLS, ("out.png",)
        )


class TestFailurePaths(StubTools):
    def run_main(self, *extra):
        """Run ``main`` on ``out.png`` with *extra* and return status, stderr, output."""
        output = self.root / "out.png"
        status, stderr = call_main(render_surface.main, str(output), *extra)
        return status, stderr, output

    def test_failed_install_exits_1_and_removes_scratch(self):
        self.stub("make", "echo install exploded; exit 4")
        status, stderr, output = self.run_main()
        self.assertEqual(1, status)
        self.assertIn("make install exited 4", stderr)
        self.assertIn("install exploded", stderr)
        self.assertFalse(output.exists())
        self.assert_scratch_removed()

    def test_install_timeout_exits_1_with_a_timeout_diagnostic(self):
        # A hung `make install` is killed by run_logged, which reports the
        # timeout as None. The diagnostic must name the timeout rather than
        # the raw status ("exited None"), and the failure must still exit 1
        # and remove the scratch root. The real install timeout is minutes
        # long, so run_logged is stubbed instead of waited out; the render
        # session's own timeout is covered by
        # test_timeout_kills_the_session_group_and_exits_1.
        with mock.patch.object(render_surface, "run_logged", return_value=None):
            status, stderr, output = self.run_main()
        self.assertEqual(1, status)
        self.assertIn("make install timed out", stderr)
        self.assertFalse(output.exists())
        self.assert_scratch_removed()

    def test_failed_session_exits_1_and_removes_scratch(self):
        self.stub("dbus-run-session", "echo no display; exit 3")
        status, stderr, output = self.run_main()
        self.assertEqual(1, status)
        self.assertIn("render session exited 3", stderr)
        self.assertIn("no display", stderr)
        self.assertFalse(output.exists())
        self.assert_scratch_removed()

    def test_session_without_a_capture_exits_1(self):
        status, stderr, output = self.run_main()
        self.assertEqual(1, status)
        self.assertIn("not a readable PNG", stderr)
        self.assertFalse(output.exists())
        self.assert_scratch_removed()

    def test_a_capture_of_the_wrong_size_exits_1_and_writes_nothing(self):
        # spectacle can hand back a surface captured at the wrong geometry. The
        # render must refuse it: publishing that PNG would report success for a
        # size the fidelity comparison never asked to check.
        self.stub_capture()
        status, stderr, output = self.run_main("--width", "64", "--height", "48")
        self.assertEqual(1, status)
        self.assertIn("capture is 320x240, expected 64x48", stderr)
        self.assertFalse(output.exists())
        self.assert_scratch_removed()

    def test_unwritable_output_is_refused_before_installing(self):
        marker = self.root / "make-ran"
        self.stub("make", f"touch {marker}")
        for label, output in (
            ("a directory", self.root),
            ("an empty path", Path("")),
            ("a missing directory", self.root / "missing" / "out.png"),
        ):
            with self.subTest(label):
                status, stderr = call_main(render_surface.main, str(output))
                self.assertEqual(2, status)
                self.assertIn("render_surface: error: cannot write", stderr)
                self.assertFalse(marker.exists())
                self.assert_scratch_removed()

    def test_a_read_only_output_directory_is_refused_before_installing(self):
        # The last branch of `_output_problem`: the directory exists but this
        # user may not write it. `os.access` is the only check that sees that,
        # and a refusal here keeps the failure a named diagnostic instead of
        # letting the copy fail later with an errno the operator has to read
        # out of a traceback.
        marker = self.root / "make-ran"
        self.stub("make", f"touch {marker}")
        locked = self.root / "locked"
        locked.mkdir()
        locked.chmod(0o500)
        self.addCleanup(locked.chmod, 0o700)
        if os.access(locked, os.W_OK):
            self.skipTest("directory permissions are not enforced for this user")
        status, stderr = call_main(render_surface.main, str(locked / "out.png"))
        self.assertEqual(2, status)
        self.assertIn("render_surface: error: cannot write", stderr)
        self.assertIn("its directory is not writable", stderr)
        self.assertFalse(marker.exists())
        self.assert_scratch_removed()

    def hidden_files(self):
        """Return the dot-prefixed entries left in the scratch root."""
        return [name for name in os.listdir(self.root) if name.startswith(".")]

    def stub_capture(self):
        """Make the stubbed session write a valid 320x240 PNG where spectacle would."""
        fixture = self.root / "capture.png"
        fixture.write_bytes(encode_png(320, 240, bytes(320 * 240 * 3)))
        self.stub("dbus-run-session", f'for a; do :; done; cp "{fixture}" "${{a##* }}"')
        return fixture

    def test_a_capture_is_copied_to_the_output(self):
        fixture = self.stub_capture()
        status, stderr, output = self.run_main()
        self.assertEqual((0, ""), (status, stderr))
        self.assertEqual(fixture.read_bytes(), output.read_bytes())
        self.assertEqual([], self.hidden_files())

    def test_a_failed_copy_keeps_the_previous_output_and_leaves_no_partial_file(self):
        self.stub_capture()
        output = self.root / "out.png"
        output.write_bytes(b"previous good render")

        def die_midway(src, dst):
            dst.write(b"half a PNG")
            raise OSError(errno.ENOSPC, "No space left on device")

        with mock.patch.object(shutil, "copyfileobj", die_midway):
            status, stderr = call_main(render_surface.main, str(output))
        self.assertEqual(1, status)
        self.assertIn("cannot write", stderr)
        self.assertEqual(b"previous good render", output.read_bytes())
        self.assertEqual([], self.hidden_files())
        self.assert_scratch_removed()

    def test_make_render_passes_a_dash_leading_output_as_a_path(self):
        real_path = os.pathsep.join(
            entry
            for entry in os.environ["PATH"].split(os.pathsep)
            if entry != str(self.bin)
        )
        result = subprocess.run(
            ["make", "-n", "render", "RENDER_OUTPUT=-x.png"],
            cwd=repo_root.ROOT,
            env={**os.environ, "PATH": real_path},
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertIn('render_surface.py -- "-x.png"', result.stdout)

    def test_session_receives_the_geometry_and_the_themed_configs(self):
        record = self.root / "args"
        self.stub(
            "dbus-run-session",
            f'echo "$@" > "{record}"; cat "$XDG_CONFIG_HOME/kwinrc" >> "{record}";'
            f' echo "$XDG_DATA_HOME $WAYLAND_DISPLAY $DISPLAY" >> "{record}"',
        )
        with mock.patch.dict(os.environ, {"WAYLAND_DISPLAY": "wl", "DISPLAY": ":9"}):
            self.run_main("--width", "64", "--height", "48", "--applet", "a b")
        text = record.read_text(encoding="utf-8")
        self.assertIn("--width 64 --height 48", text)
        self.assertIn("--socket render-surface", text)
        self.assertIn("theme=__aurorae__svg__org.macos8.desktop", text)
        self.assertIn("--exit-with-session", text)
        last = text.splitlines()[-1].split()
        self.assertTrue(Path(last[0]).parent.name.startswith("render-surface-"))
        self.assertEqual(1, len(last), "WAYLAND_DISPLAY and DISPLAY leaked")

    def test_install_ignores_a_destdir_from_the_environment(self):
        record = self.root / "make-env"
        self.stub("make", f'echo "[$DESTDIR] $*" > "{record}"')
        with mock.patch.dict(os.environ, {"DESTDIR": str(self.root / "stage")}):
            self.run_main()
        argv = record.read_text(encoding="utf-8")
        self.assertTrue(argv.startswith("[] install XDG_DATA_HOME="), argv)

    def test_install_ignores_a_destdir_from_the_outer_make_command_line(self):
        # `make DESTDIR=/stage render` exports the command-line variable through
        # MAKEFLAGS as well as the environment, so dropping DESTDIR alone leaves
        # the inner `make install` staging the theme outside the scratch home.
        # Run the real make so it imports MAKEFLAGS the way the outer one would.
        record = self.root / "make-destdir"
        makefile = self.root / "install.mk"
        makefile.write_text(
            f'install:\n\t@echo "[$(DESTDIR)]" > "{record}"\n', encoding="utf-8"
        )
        self.stub("make", f'exec "{self.real_make}" -f "{makefile}" "$@"')
        with mock.patch.dict(
            os.environ, {"MAKEFLAGS": f"-- DESTDIR={self.root / 'stage'}"}
        ):
            self.run_main()
        self.assertEqual("[]", record.read_text(encoding="utf-8").strip())

    def test_timeout_kills_the_session_group_and_exits_1(self):
        pidfile = self.root / "pid"
        self.stub("dbus-run-session", f'echo $$ > "{pidfile}"; exec sleep 60')
        status, stderr, output = self.run_main("--timeout", "1")
        self.assertEqual(1, status)
        self.assertIn("render timed out after 1s", stderr)
        self.assertFalse(output.exists())
        self.assert_scratch_removed()
        pid = int(pidfile.read_text(encoding="utf-8"))
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)

    def test_sigterm_kills_the_session_group_and_removes_scratch(self):
        pidfile = self.root / "pid"
        self.stub("dbus-run-session", f'echo $$ > "{pidfile}"; exec sleep 60')
        env = dict(os.environ, TMPDIR=str(self.scratch_parent))
        argv = [sys.executable, render_surface.__file__, str(self.root / "o.png")]
        with process_runner.running(
            argv, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ) as process:
            deadline = time.monotonic() + 30
            while not (pidfile.is_file() and pidfile.read_text(encoding="utf-8").strip()):
                self.assertIsNone(process.poll(), "render exited before the session started")
                self.assertLess(time.monotonic(), deadline, "session never started")
                time.sleep(0.05)
            pid = int(pidfile.read_text(encoding="utf-8"))
            process.send_signal(signal.SIGTERM)
            process_runner.finish(process)
        self.assertEqual(128 + signal.SIGTERM, process.returncode)
        self.assert_scratch_removed()
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)


REAL_TOOLS = ("kwin_wayland", "dbus-run-session", "plasmawindowed", "spectacle",
              "plasma-apply-colorscheme")


@unittest.skipUnless(
    all(shutil.which(tool) for tool in REAL_TOOLS),
    "needs kwin_wayland, dbus-run-session, plasmawindowed, spectacle and "
    "plasma-apply-colorscheme on PATH",
)
class TestRender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp(prefix="render-surface-test-")
        cls.addClassCleanup(shutil.rmtree, cls.directory, ignore_errors=True)
        cls.output = os.path.join(cls.directory, "render.png")
        process = process_runner.start(
            [sys.executable, SCRIPT, "--settle", "3", cls.output],
            capture_output=True,
            text=True,
        )
        cls.stdout, cls.stderr = process_runner.finish(process, timeout=150)
        cls.returncode = process.returncode

    def test_exits_zero(self):
        self.assertEqual(0, self.returncode, self.stderr)

    def test_writes_a_320x240_png(self):
        image = read_png(self.output)
        self.assertEqual((320, 240), (image.width, image.height))

    def test_window_body_is_the_platinum_face(self):
        pixel = pixel_at(read_png(self.output), 300, 200)
        self.assertEqual(FACE, hex_colour(pixel))

    def assert_strip_pixels_match(
        self, candidate_crop, reference_crop, reference_path=REFERENCE
    ):
        """Byte-compare one strip with the same ``crop``/``compare`` the CLI calls.

        Each strip is compared in process, reusing the process-cached
        reference decode instead of spawning the CLI and re-decoding the
        1024x768 screenshot once per strip. The CLI's crop options, including
        ``--candidate-crop`` and ``--crop`` in one run, stay covered end to
        end by ``tests/test_fidelity_cli_crops.py``.
        """
        reference, error = read_reference(reference_path)
        skip_unless_materialized(self, reference_path, error)
        candidate = crop(read_png(self.output), *candidate_crop)
        expected = crop(reference, *reference_crop)
        self.assertEqual(0, compare(candidate, expected).differing)

    def test_title_bar_matches_the_reference(self):
        self.assert_strip_pixels_match(CANDIDATE_CROP, REFERENCE_CROP)

    def test_title_bar_boxes_match_the_reference(self):
        for candidate_crop, reference_crop, reference_path in (
            (CLOSE_CANDIDATE, CLOSE_REFERENCE, REFERENCE),
            (COLLAPSE_CANDIDATE, COLLAPSE_REFERENCE, REFERENCE),
            (ZOOM_CANDIDATE, ZOOM_REFERENCE, PROFILER_REFERENCE),
        ):
            with self.subTest(candidate_crop=candidate_crop):
                self.assert_strip_pixels_match(
                    candidate_crop, reference_crop, reference_path
                )

    def test_frame_borders_match_the_reference(self):
        for candidate_crop, reference_crop in (
            (LEFT_BORDER_CANDIDATE, LEFT_BORDER_REFERENCE),
            (RIGHT_BORDER_CANDIDATE, RIGHT_BORDER_REFERENCE),
            (BOTTOM_BORDER_CANDIDATE, BOTTOM_BORDER_REFERENCE),
        ):
            with self.subTest(candidate_crop=candidate_crop):
                self.assert_strip_pixels_match(candidate_crop, reference_crop)


if __name__ == "__main__":
    unittest.main()
