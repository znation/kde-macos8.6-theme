"""Tests for tools/render_surface.py, the headless Plasma render-and-capture script."""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import repo_root  # noqa: F401
import process_runner
from platinum_palette import FACE
from tools import render_surface  # noqa: E402
from tools.png import pixel_at, read_png  # noqa: E402

SCRIPT = str(repo_root.ROOT / "tools" / "render_surface.py")


def call_main(*argv):
    """Run ``main(argv)`` in-process; return ``(status, stderr)``."""
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        try:
            status = render_surface.main(list(argv))
        except SystemExit as exit_:
            status = exit_.code
    return status, stderr.getvalue()


class TestDefaultsGroups(unittest.TestCase):
    def test_reads_the_decoration_and_desktop_theme_from_the_global_theme(self):
        groups = render_surface._defaults_groups()
        decoration = groups[("kwinrc", "org.kde.kdecoration2")]
        self.assertEqual("__aurorae__svg__org.macos8.desktop", decoration["theme"])
        self.assertEqual("org.macos8.desktop", groups[("plasmarc", "Theme")]["name"])

    def test_skips_sections_that_name_no_config_file(self):
        groups = render_surface._defaults_groups()
        self.assertNotIn("Wallpaper", {group for _, group in groups})

    def test_parses_comments_blank_lines_and_spacing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "defaults"
            path.write_text(
                "# note\n[a][B]\n k = v \n\n[Plain]\nx=1\n[a][C]\nz=2=3\n",
                encoding="utf-8",
            )
            self.assertEqual(
                {("a", "B"): {"k": "v"}, ("a", "C"): {"z": "2=3"}},
                render_surface._defaults_groups(path),
            )

    def test_written_configs_follow_the_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            render_surface._write_configs(Path(directory))
            kwinrc = (Path(directory) / "kwinrc").read_text(encoding="utf-8")
            plasmarc = (Path(directory) / "plasmarc").read_text(encoding="utf-8")
            self.assertEqual(
                {"kwinrc", "plasmarc"}, set(os.listdir(directory))
            )
        self.assertIn("[org.kde.kdecoration2]\n", kwinrc)
        self.assertIn("theme=__aurorae__svg__org.macos8.desktop\n", kwinrc)
        self.assertIn("[Theme]\nname=org.macos8.desktop\n", plasmarc)
        self.assertNotIn("ColorScheme", kwinrc + plasmarc)


class TestArguments(unittest.TestCase):
    def assert_usage_error(self, *argv):
        status, stderr = call_main(*argv)
        self.assertEqual(2, status)
        return stderr

    def test_rejects_non_positive_and_non_plain_sizes(self):
        for option in ("--width", "--height"):
            for value in ("0", "-3", "1_0", "abc", "1.5"):
                with self.subTest(option=option, value=value):
                    self.assertIn(
                        option, self.assert_usage_error("out.png", option, value)
                    )

    def test_rejects_bad_durations(self):
        for argv in (
            ("--settle", "-1"),
            ("--settle", "nan"),
            ("--settle", "inf"),
            ("--timeout", "0"),
            ("--timeout", "1_0"),
        ):
            with self.subTest(argv=argv):
                self.assertIn(argv[0], self.assert_usage_error("out.png", *argv))

    def test_rejects_option_like_applet(self):
        self.assertIn(
            "--applet", self.assert_usage_error("out.png", "--applet=--help-all")
        )

    def test_requires_an_output_path(self):
        self.assert_usage_error()


class StubTools(unittest.TestCase):
    """Base for tests that run `main` against shell stubs of the external tools."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="render-surface-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
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
        path = self.bin / name
        path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def assert_scratch_removed(self):
        self.assertEqual([], os.listdir(self.scratch_parent))


class TestMissingTool(unittest.TestCase):
    def test_names_the_first_missing_tool_and_exits_2(self):
        with tempfile.TemporaryDirectory() as empty:
            with mock.patch.dict(os.environ, {"PATH": empty}):
                status, stderr = call_main("out.png")
        self.assertEqual(2, status)
        self.assertIn(render_surface.REQUIRED_TOOLS[0], stderr)
        self.assertIn("render_surface: error:", stderr)

    def test_a_single_missing_tool_is_the_one_named(self):
        for missing in render_surface.REQUIRED_TOOLS:
            with self.subTest(missing=missing):
                with tempfile.TemporaryDirectory() as directory:
                    for name in render_surface.REQUIRED_TOOLS:
                        if name != missing:
                            tool = Path(directory) / name
                            tool.write_text("#!/bin/sh\n", encoding="utf-8")
                            tool.chmod(0o755)
                    with mock.patch.dict(os.environ, {"PATH": directory}):
                        status, stderr = call_main("out.png")
                self.assertEqual(2, status)
                self.assertTrue(stderr.rstrip().endswith(missing), stderr)


class TestFailurePaths(StubTools):
    def run_main(self, *extra):
        output = self.root / "out.png"
        status, stderr = call_main(str(output), *extra)
        return status, stderr, output

    def test_failed_install_exits_1_and_removes_scratch(self):
        self.stub("make", "echo install exploded; exit 4")
        status, stderr, output = self.run_main()
        self.assertEqual(1, status)
        self.assertIn("make install exited 4", stderr)
        self.assertIn("install exploded", stderr)
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
            [sys.executable, SCRIPT, cls.output],
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
        self.assertEqual(FACE, "#%02X%02X%02X" % pixel)


if __name__ == "__main__":
    unittest.main()
