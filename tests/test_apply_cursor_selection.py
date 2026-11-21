"""Tests for the ``plasma-apply-cursortheme`` step of ``apply_cursor``.

``apply_cursor`` hands the installed theme name to the selector, and these arms
pin that step: the selector gets the theme name; a missing or unrunnable selector
and an unusable scratch directory exit 2 without a traceback; a failing or
timed-out selector exits 1 with the log tail; ``--optional`` still selects, and
still fails, when the selector is present; the restart note prints only after a
successful selection; and a SIGTERM kills the selector's process group and
removes the scratch directory.

The home and install arms live in ``tests/test_apply_cursor.py``, removal in
``tests/test_apply_cursor_remove.py``, and the shared temp-home base is
``CursorTestCase`` in ``tests/support/cursor_case.py``.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import unittest
from unittest import mock

from support import process_runner
from support.executable_stubs import write_executable
from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cursor_case import CursorTestCase
from support.process_assertions import (
    assert_exit_2_without_traceback,
    assert_failed,
    assert_succeeded,
)
from tools import apply_cursor, cursor_selection, diagnostics, required_command


class TestSelection(CursorTestCase):
    def test_unusable_scratch_directory_exits_2_without_a_traceback(self):
        # The selector runs with a scratch directory for its log. Creating that
        # directory can fail before the selector starts (a full or unwritable
        # TMPDIR); it must be this tool's own exit-2 diagnostic, not a
        # traceback that skips the exit contract.
        self.install_theme()
        self.stub_selector()
        with mock.patch.object(
            diagnostics.tempfile, "mkdtemp", side_effect=OSError("no space left")
        ):
            result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn("cannot create a scratch directory", result.stderr)
        self.assertIn("no space left", result.stderr)

    def test_selector_is_invoked_with_the_theme_name(self):
        self.install_theme()
        self.stub_selector()
        assert_succeeded(self, self.run_tool())
        self.assertEqual([cursor_selection.CURSOR_THEME], self.recorded())

    def test_missing_selector_exits_2_naming_it(self):
        self.install_theme()
        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertIn(cursor_selection.SELECT_TOOL, result.stderr)

    def test_missing_selector_refuses_before_linking_the_home(self):
        # A standalone apply must refuse a missing selector before it touches
        # the user's home: no ~/.icons link may be created for a refused run.
        self.install_theme()
        result = self.run_tool()
        assert_exit_2_without_traceback(self, result)
        self.assertFalse(self.link.is_symlink())
        self.assertFalse(self.link.parent.exists())

    def test_optional_install_still_selects_when_the_selector_is_present(self):
        # --optional skips only the selection when the KDE selector is absent.
        # With the selector on PATH it must still run the selection, and must
        # not print the "not on PATH" note.
        self.install_theme()
        self.stub_selector()
        result = self.run_tool("--optional")
        assert_succeeded(self, result)
        self.assertEqual([cursor_selection.CURSOR_THEME], self.recorded())
        self.assertNotIn("is not on PATH", result.stdout)

    def test_optional_install_still_fails_when_the_selector_fails(self):
        # --optional must not swallow a selector that is present but fails.
        self.install_theme()
        self.stub_selector("echo selector exploded >&2\nexit 3")
        result = self.run_tool("--optional")
        assert_failed(self, result)
        self.assertEqual(1, result.returncode)
        self.assertIn(f"{cursor_selection.SELECT_TOOL} exited 3", result.stderr)

    def test_successful_install_recommends_restarting_applications(self):
        # cursor_workflow.apply prints the restart advice only once the
        # selection has succeeded, as an apply_cursor note on stdout.
        self.install_theme()
        self.stub_selector()
        result = self.run_tool()
        assert_succeeded(self, result)
        self.assertIn(
            "apply_cursor: note: restart running applications", result.stdout
        )

    def test_failed_selection_does_not_recommend_restarting_applications(self):
        # A selector that fails means nothing was applied, so the restart
        # advice must not be printed as though the pointer had changed.
        self.install_theme()
        self.stub_selector("exit 3")
        result = self.run_tool()
        assert_failed(self, result)
        self.assertNotIn("restart running applications", result.stdout)

    def test_failed_selector_exits_1_with_the_log_tail(self):
        self.install_theme()
        self.stub_selector("echo selector exploded >&2\nexit 3")
        result = self.run_tool()
        assert_failed(self, result)
        self.assertEqual(1, result.returncode)
        self.assertIn(f"{cursor_selection.SELECT_TOOL} exited 3", result.stderr)
        self.assertIn("selector exploded", result.stderr)

    def test_selector_timeout_exits_1_with_the_log_tail(self):
        self.install_theme()
        self.stub_selector()
        with mock.patch.object(
            required_command, "run_logged", return_value=None
        ):
            result = self.run_tool()
        assert_failed(self, result)
        self.assertEqual(1, result.returncode)
        self.assertIn("timed out", result.stderr)

    def test_sigterm_kills_the_selector_group_and_removes_scratch(self):
        # run_logged starts the selector in its own session, so without a
        # SIGTERM handler the tool dies before its finally blocks: the
        # selector keeps running and the scratch directory is left behind.
        self.install_theme()
        scratch_parent = self.root / "tmp"
        scratch_parent.mkdir()
        pidfile = self.root / "selector.pid"
        self.stub_selector(f'echo $$ > "{pidfile}"; exec sleep 60')
        env = dict(
            self.env,
            PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}",
            TMPDIR=str(scratch_parent),
        )
        selector_pid = None

        def kill_selector():
            if selector_pid is not None:
                try:
                    os.kill(selector_pid, signal.SIGKILL)
                except OSError:
                    pass

        self.addCleanup(kill_selector)
        with process_runner.running(
            [sys.executable, apply_cursor.__file__],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ) as process:
            selector_pid = process_runner.wait_for_pidfile(
                self, process, pidfile, tool="apply_cursor", child="selector"
            )
            process.send_signal(signal.SIGTERM)
            process_runner.finish(process)
        self.assertEqual(128 + signal.SIGTERM, process.returncode)
        self.assertEqual([], os.listdir(scratch_parent))
        with self.assertRaises(ProcessLookupError):
            os.kill(selector_pid, 0)

    def test_unrunnable_selector_exits_2_without_a_traceback(self):
        # `shutil.which` finds an executable script whose interpreter is
        # missing, so the missing-tool check passes, but Popen raises OSError.
        # The selector is as unusable as a missing one and must be reported as
        # this tool's own diagnostic, not a traceback that skips the exit
        # contract. PATH holds only the stub bin, so execvp cannot fall
        # through to a real selector later on PATH.
        self.install_theme()
        selector = self.bin / cursor_selection.SELECT_TOOL
        write_executable(selector, "#!/nonexistent/interpreter\n")

        result = self.run_tool()

        assert_exit_2_without_traceback(self, result)
        self.assertIn(
            f"cannot run {cursor_selection.SELECT_TOOL}", result.stderr
        )
        self.assertTrue(self.link.is_symlink())


if __name__ == "__main__":
    unittest.main()
