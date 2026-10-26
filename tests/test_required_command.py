"""Tests for tools/required_command.py -- the shared required-command mapping.

``apply_theme`` and ``apply_cursor`` route every command they cannot run
without through :func:`tools.required_command.run_required`. Their own tests
reach each outcome through the CLI, but none pins the helper's contract at its
own boundary: that it hands the command, environment, log, timeout and working
directory straight to :func:`tools.process_group.run_logged`, returns ``None``
only on success, and maps an unstartable command to exit 2 while a timeout or
non-zero exit becomes exit 1 with the bounded log tail. A regression that
dropped or reordered one of those arguments (the working directory and timeout
are not observable through the caller tests) would change what the external
command sees without failing either CLI suite.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import contextlib
import io
import os
import sys
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.tmp_dir import make_tmp_dir
from tools import required_command

TOOL = "a_tool"
COMMAND = ["slowcmd", "--flag"]


class RequiredCommandCase(unittest.TestCase):
    def setUp(self):
        self.root = make_tmp_dir(self)
        self.log = self.root / "command.log"
        self.cwd = self.root / "work"
        self.cwd.mkdir()
        self.env = {"PATH": os.environ["PATH"], "MARK": "m1"}

    def run_required(self, command=COMMAND, timeout=30.0):
        """Call the helper with the case's defaults and return status, stderr."""
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = required_command.run_required(
                TOOL, command, self.env, self.log, timeout, self.cwd
            )
        return status, stderr.getvalue()


class TestRunRequired(RequiredCommandCase):
    def test_success_returns_none_runs_where_asked_and_logs_the_output(self):
        # A real child proves the environment, working directory and log path
        # reach run_logged: the command reports both values through its log.
        status, stderr = self.run_required(
            ["sh", "-c", 'printf "%s\\n%s\\n" "$PWD" "$MARK"']
        )
        self.assertIsNone(status)
        self.assertEqual("", stderr)
        cwd, mark = self.log.read_text(encoding="utf-8").split()
        self.assertEqual(os.path.realpath(self.cwd), os.path.realpath(cwd))
        self.assertEqual("m1", mark)

    def test_every_argument_is_forwarded_to_the_logged_runner(self):
        with mock.patch.object(
            required_command, "run_logged", return_value=0
        ) as runner:
            status, stderr = self.run_required(timeout=12.5)
        self.assertIsNone(status)
        self.assertEqual("", stderr)
        runner.assert_called_once_with(
            COMMAND, self.env, self.log, 12.5, self.cwd
        )

    def test_a_timeout_returns_one_with_the_timing_and_log_tail(self):
        self.log.write_text("warning\nstill running\n", encoding="utf-8")
        with mock.patch.object(
            required_command, "run_logged", return_value=None
        ):
            status, stderr = self.run_required(timeout=0.25)
        self.assertEqual(1, status)
        self.assertIn("a_tool: error: slowcmd timed out after 0.25s", stderr)
        self.assertIn("\n  warning\n  still running\n", stderr)

    def test_a_nonzero_exit_returns_one_with_the_status_and_log_tail(self):
        self.log.write_text("command exploded\n", encoding="utf-8")
        with mock.patch.object(
            required_command, "run_logged", return_value=3
        ):
            status, stderr = self.run_required()
        self.assertEqual(1, status)
        self.assertIn("a_tool: error: slowcmd exited 3", stderr)
        self.assertIn("\n  command exploded\n", stderr)

    def test_an_unstartable_command_returns_two_without_a_traceback(self):
        error = FileNotFoundError(
            2, "No such file or directory", "/nonexistent/interpreter"
        )
        with mock.patch.object(
            required_command, "run_logged", side_effect=error
        ):
            status, stderr = self.run_required()
        self.assertEqual(2, status)
        self.assertIn("a_tool: error: cannot run slowcmd:", stderr)
        self.assertIn(str(error), stderr)
        self.assertNotIn("Traceback", stderr)

    def test_signal_death_names_the_signal_and_keeps_the_log_tail(self):
        status, stderr = self.run_required([
            sys.executable, "-c",
            "import os, signal; print('before termination', flush=True); "
            "os.kill(os.getpid(), signal.SIGTERM)",
        ])
        self.assertEqual(1, status)
        self.assertIn(f"{sys.executable} killed by signal SIGTERM", stderr)
        self.assertIn("\n  before termination\n", stderr)

    def test_unknown_signal_number_is_reported_without_a_traceback(self):
        with mock.patch.object(required_command, "run_logged", return_value=-99999):
            status, stderr = self.run_required()
        self.assertEqual(1, status)
        self.assertIn("slowcmd killed by signal 99999", stderr)
        self.assertNotIn("Traceback", stderr)


if __name__ == "__main__":
    unittest.main()
