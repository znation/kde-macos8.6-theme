"""The render CLI's failure-path suite, against shell stubs of the external tools.

``tools/render_surface.py``'s argument handling and its workflow's failure
behavior -- a missing or unrunnable tool, an unusable scratch directory, an
unpainted or failed capture, publication that must keep the previous output
whole -- run here against stub executables, without any Plasma session; the
pixel gates that drive the same CLI against a real headless session live in
``tests/test_render_surface.py``, ``tests/test_render_dialog_gates.py`` and
``tests/test_render_file_dialog.py`` beside the ``Test...DialogRender``
gates. Environment-isolation cases live in ``tests/test_render_environment.py``. The output-publication cases (refusal
before installing, copy-over, the previous output kept, ``make render`` passing
a dash-leading output) live in ``tests/test_render_output_cli.py``. The per-mode
session wiring (the client each mode launches and the configs it writes) lives in
``tests/test_render_session_modes.py``. The live-session capture outcomes (the
real session script's applet liveness check and the refusal of a bad capture)
live in ``tests/test_render_live_capture.py``.
"""

from __future__ import annotations

import errno
import os
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from support import process_runner
from support.cli_fixtures import assert_missing_tool_named, call_main
from tools import (
    render_setup,
    render_surface,
    render_workflow,
)  # noqa: E402
from support.render_stub_tools import StubTools


class TestMissingTool(unittest.TestCase):
    def test_names_the_first_missing_tool_and_exits_2(self):
        with tempfile.TemporaryDirectory() as empty:
            with mock.patch.dict(os.environ, {"PATH": empty}):
                status, stderr = call_main(render_surface.main, "out.png")
        self.assertEqual(2, status)
        self.assertIn(render_surface.REQUIRED_TOOLS[0], stderr)
        self.assertIn("render_surface: error:", stderr)

    def test_applet_id_with_nul_is_rejected_as_usage_error(self):
        with tempfile.TemporaryDirectory() as empty:
            with mock.patch.dict(os.environ, {"PATH": empty}):
                status, stderr = call_main(
                    render_surface.main, "out.png", "--applet", "org.example\0widget"
                )
        self.assertEqual(2, status)
        self.assertIn("--applet must be a plasmoid id without NUL", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_a_single_missing_tool_is_the_one_named(self):
        assert_missing_tool_named(
            self, render_surface.main, render_surface.REQUIRED_TOOLS, ("out.png",)
        )


class TestFailurePaths(StubTools, unittest.TestCase):
    def assert_unrunnable_command_is_reported(self, command, diagnostic):
        """Check the CLI handles a found executable that cannot be started."""
        executable = self.bin / command
        executable.write_text("#!/nonexistent/interpreter\n", encoding="utf-8")
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)

        # Keep execvp from falling through to a real command after ENOENT.
        with mock.patch.dict(os.environ, {"PATH": str(self.bin)}):
            status, stderr, output = self.run_main()

        self.assert_failed_run(status, stderr, output, 2, diagnostic)

    def test_a_failed_gtk_selection_install_exits_1_and_removes_scratch(self):
        self.stub("zenity", "exit 0")
        with mock.patch.object(
            render_workflow,
            "install_gtk_selection",
            side_effect=render_setup._ConfigError("sheet is missing"),
        ) as install, mock.patch.object(
            render_workflow, "run_logged", return_value=0
        ):
            status, stderr, output = self.run_main("--gtk-dialog")

        self.assert_failed_run(
            status,
            stderr,
            output,
            1,
            "cannot install the GTK selection",
            "sheet is missing",
        )
        install.assert_called_once()

    def test_unusable_scratch_directory_exits_2_without_a_traceback(self):
        # The scratch session is created before the install starts. Creating it
        # can fail (a full or unwritable TMPDIR) before there is anything to
        # clean up; it must be this tool's own exit-2 diagnostic, not a
        # traceback that skips the exit contract.
        with mock.patch.object(
            tempfile, "mkdtemp", side_effect=OSError("no space left")
        ):
            status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 2,
            "cannot create a scratch session directory", "no space left",
        )

    def test_failed_install_exits_1_and_removes_scratch(self):
        self.stub("make", "echo install exploded; exit 4")
        status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1,
            "make install exited 4", "install exploded",
        )

    def test_an_unrunnable_make_exits_2_and_removes_scratch(self):
        # `which` still finds an executable script whose interpreter is gone,
        # so the missing-tool check passes and Popen raises OSError. The tool
        # must report that itself instead of letting the OSError traceback.
        self.assert_unrunnable_command_is_reported(
            "make", "render_surface: error: cannot run make:"
        )

    def test_an_unrunnable_session_launcher_exits_2_and_removes_scratch(self):
        # Same fault as the make test, at the second command the tool starts
        # itself: `shutil.which` finds dbus-run-session, but Popen raises
        # OSError. It must be the tool's own exit-2 diagnostic, not a
        # traceback that skips the scratch cleanup.
        self.assert_unrunnable_command_is_reported(
            "dbus-run-session", "render_surface: error: cannot run dbus-run-session:"
        )

    def test_a_failed_session_config_write_exits_1_with_a_diagnostic(self):
        # The session config is derived from the shipped defaults and written
        # into the scratch config home. A write that fails there (a full disk),
        # a defaults file that cannot be decoded, or a malformed section
        # heading the reader rejects must become the tool's own diagnostic and
        # exit 1, not a traceback that bypasses the documented exit status.
        def die(config_home, names):
            raise failure

        for label, failure in (
            ("a full disk", OSError(errno.ENOSPC, "No space left on device")),
            (
                "a non-UTF-8 defaults file",
                UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"),
            ),
            (
                "a malformed defaults heading",
                ValueError("malformed section heading '[a][b] # note'"),
            ),
        ):
            with self.subTest(label):
                with mock.patch.object(render_setup, "write_configs", die):
                    status, stderr, output = self.run_main()
                self.assert_failed_run(
                    status, stderr, output, 1,
                    "render_surface: error:", "session config",
                )

    def test_a_failed_themes_link_exits_2_and_removes_scratch(self):
        # The scratch home's themes link is made after `make install`, at the
        # one place the engine's literal `$HOME/.local/share/themes/` search
        # path is satisfied. When the link cannot be made (an entry raced in
        # at the link name), the tool must report its own exit-2 diagnostic
        # naming the path, not a traceback that skips the scratch cleanup.
        themes = self.root / "themes"
        problem = OSError(errno.EEXIST, "File exists")

        def die(session):
            return problem, themes

        with mock.patch.object(render_workflow, "link_kvantum_themes", die):
            status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 2,
            "render_surface: error: cannot link",
            str(themes), "File exists",
        )

    def test_a_failed_kvantum_selection_write_exits_1_and_removes_scratch(self):
        # A dialog render selects the Kvantum theme in the scratch config
        # home before the session starts; without the name the engine falls
        # back to its compiled-in default and the gate would silently compare
        # the wrong theme's pixels. A selection write that fails there (a
        # full disk) must become the tool's own exit-1 diagnostic, not a
        # traceback that skips the scratch cleanup or a render that goes out
        # carrying an unthemed widget.
        def die(session):
            raise OSError(errno.ENOSPC, "No space left on device")

        with mock.patch.object(render_workflow, "write_kvantum_selection", die):
            status, stderr, output = self.run_main("--menu-dialog")
        self.assert_failed_run(
            status, stderr, output, 1,
            "render_surface: error:",
            "cannot write the Kvantum selection",
            "No space left on device",
        )

    def test_install_timeout_exits_1_with_a_timeout_diagnostic(self):
        # A hung `make install` is killed by run_logged, which reports the
        # timeout as None. The diagnostic must name the timeout rather than
        # the raw status ("exited None"), and the failure must still exit 1
        # and remove the scratch root. The real install timeout is minutes
        # long, so run_logged is stubbed instead of waited out; the render
        # session's own timeout is covered by
        # test_timeout_kills_the_session_group_and_exits_1.
        with mock.patch.object(render_setup, "run_logged", return_value=None):
            status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1, "make install timed out",
        )

    def test_failed_session_exits_1_and_removes_scratch(self):
        self.stub("dbus-run-session", "echo no display; exit 3")
        status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1,
            "render session exited 3", "no display",
        )

    def test_session_without_a_capture_exits_1(self):
        # The session exits 0 but never writes the PNG. The diagnostic must
        # say so and report the render log's size, so a zero-status run with
        # no capture is not indistinguishable from a session that logged.
        # The stub logs exactly six bytes ("hello\n") before exiting 0.
        self.stub("dbus-run-session", "printf 'hello\\n'; exit 0")
        status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1,
            "not a readable PNG",
            "the session exited 0 and wrote no capture",
            "(render log 6 bytes)",
        )

    def test_timeout_kills_the_session_group_and_exits_1(self):
        # The session must write its pid before the one-second timeout fires,
        # or the timeout kills it first and the read below has nothing to
        # check. A loaded host can lose that race, so retry with a fresh
        # pidfile per attempt; each timed-out attempt has already had its
        # whole group killed by run_logged, so retrying leaks nothing. The
        # deadline bounds the retries, so a host that never starts the session
        # fails instead of spinning.
        started = time.monotonic()
        deadline = started + 30
        while True:
            self.assertLess(
                time.monotonic(),
                deadline,
                "the session never wrote its pid before the timeout",
            )
            pidfile = self.root / f"pid-{time.monotonic_ns()}"
            self.stub(
                "dbus-run-session", f'echo $$ > "{pidfile}"; exec sleep 60'
            )
            status, stderr, output = self.run_main(
                "--settle", "0", "--timeout", "1"
            )
            self.assert_failed_run(
                status, stderr, output, 1, "render timed out after 1s",
            )
            try:
                pid = int(pidfile.read_text(encoding="utf-8"))
            except (FileNotFoundError, ValueError):
                # The timeout fired before the session finished its setup, so
                # this attempt proved nothing about the group kill.
                continue
            break
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)

    def test_sigterm_kills_the_session_group_and_removes_scratch(self):
        pidfile = self.root / "pid"
        self.stub("dbus-run-session", f'echo $$ > "{pidfile}"; exec sleep 60')
        env = dict(os.environ, TMPDIR=str(self.scratch_parent))
        argv = [sys.executable, render_surface.__file__, str(self.root / "o.png")]
        log = self.root / "render.log"
        with log.open("w", encoding="utf-8") as err, process_runner.running(
            argv, env=env, stdout=subprocess.DEVNULL, stderr=err
        ) as process:
            pid = process_runner.wait_for_pidfile(
                self, process, pidfile, tool="render", child="session", log=log
            )
            process.send_signal(signal.SIGTERM)
            process_runner.finish(process)
        self.assertEqual(128 + signal.SIGTERM, process.returncode)
        self.assert_scratch_removed()
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)



if __name__ == "__main__":
    unittest.main()
