"""Tests for tools/required_command.py -- the shared required-command mapping.

``apply_theme`` and ``apply_cursor`` route every command they cannot run
without through :func:`tools.required_command.run_required`. Their own tests
reach each outcome through the CLI, but none pins
the helpers' contracts at their boundaries: that the shared helper hands the
command, environment, log, timeout and working directory straight to
:func:`tools.process_group.run_logged`, returns ``None`` only on success, and
maps an unstartable command to exit 2 while a timeout or non-zero exit
becomes exit 1 with the bounded log tail, and that the read helper keeps the
streams apart and returns the raw stdout bytes only on success. A regression
that dropped or reordered one of those arguments (the working directory and
timeout are not observable through the caller tests) would change what the
external command sees without failing either CLI suite.

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
    """Base class: the scratch root, log, cwd and environment ``run_required`` uses."""

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
    def test_an_empty_command_is_rejected_before_starting_a_child(self):
        with mock.patch.object(required_command, "run_logged") as runner:
            with self.assertRaisesRegex(
                ValueError,
                r"^run_required\(\) requires a non-empty executable name$",
            ):
                self.run_required([])
        runner.assert_not_called()

    def test_an_empty_executable_is_rejected_before_starting_a_child(self):
        with mock.patch.object(required_command, "run_logged") as runner:
            with self.assertRaisesRegex(
                ValueError,
                r"^run_required\(\) requires a non-empty executable name$",
            ):
                self.run_required([""])
        runner.assert_not_called()

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


class RunRequiredOutputCase(RequiredCommandCase):
    """Defaults for :func:`run_required_output` over the case's log paths."""

    def run_output(self, command=COMMAND, timeout=30.0):
        """Call the read helper and return (value, status, stderr)."""
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            value, status = required_command.run_required_output(
                TOOL,
                command,
                self.env,
                self.root / "read.log",
                self.root / "read.stderr.log",
                timeout,
                self.cwd,
            )
        return value, status, stderr.getvalue()


class TestRunRequiredOutput(RunRequiredOutputCase):
    def test_an_empty_command_is_rejected_before_starting_a_child(self):
        with mock.patch.object(
            required_command, "run_logged_split"
        ) as runner:
            with self.assertRaisesRegex(
                ValueError,
                r"^run_required_output\(\) requires a non-empty executable "
                r"name$",
            ):
                self.run_output([])
        runner.assert_not_called()

    def test_an_empty_executable_is_rejected_before_starting_a_child(self):
        with mock.patch.object(
            required_command, "run_logged_split"
        ) as runner:
            with self.assertRaisesRegex(
                ValueError,
                r"^run_required_output\(\) requires a non-empty executable "
                r"name$",
            ):
                self.run_output([""])
        runner.assert_not_called()

    def test_success_returns_the_stdout_bytes_only_and_leaves_no_logs(self):
        value, status, stderr = self.run_output(
            ["sh", "-c", 'printf "%s=%s" "$MARK" "$PWD" > /dev/stdout; '
             'echo warning >&2']
        )
        self.assertIsNone(status)
        self.assertEqual("", stderr)
        mark, cwd = value.decode("utf-8").split("=")
        self.assertEqual("m1", mark)
        self.assertEqual(os.path.realpath(self.cwd), os.path.realpath(cwd))
        # The streams stay apart on success: no log carries the warning, so
        # no caller can mistake it for part of the value.
        self.assertEqual([], list(self.root.glob("*.log")))

    def test_a_stderr_log_that_cannot_be_removed_keeps_the_value(self):
        """A log deletion that fails never discards a value already read."""

        def succeed(command, env, stdout_log, stderr_log, timeout, cwd):
            stdout_log.write_bytes(b"recorded")
            stderr_log.write_bytes(b"warning")
            os.chmod(self.root, 0o500)  # removal in the read-only home fails
            return 0

        try:
            with mock.patch.object(
                required_command, "run_logged_split", side_effect=succeed
            ):
                value, status, stderr = self.run_output()
        finally:
            os.chmod(self.root, 0o700)
        self.assertIsNone(status)
        self.assertEqual(b"recorded", value)
        self.assertEqual("", stderr)

    def test_a_stdout_log_that_cannot_be_removed_still_cleans_stderr(self):
        """Failure removing the first log does not skip the second one."""
        def succeed(command, env, stdout_log, stderr_log, timeout, cwd):
            stdout_log.write_bytes(b"recorded")
            stderr_log.write_bytes(b"warning")
            return 0

        stdout_log = self.root / "read.log"
        stderr_log = self.root / "read.stderr.log"
        unlink = type(stdout_log).unlink

        def unlink_with_stdout_failure(path, *args, **kwargs):
            if path == stdout_log:
                raise PermissionError("cannot remove stdout log")
            return unlink(path, *args, **kwargs)

        with mock.patch.object(
            required_command, "run_logged_split", side_effect=succeed
        ), mock.patch.object(type(stdout_log), "unlink", unlink_with_stdout_failure):
            value, status, stderr = self.run_output()

        self.assertIsNone(status)
        self.assertEqual(b"recorded", value)
        self.assertEqual("", stderr)
        self.assertTrue(stdout_log.exists())
        self.assertFalse(stderr_log.exists())

    def test_a_stdout_log_that_cannot_be_read_reports_exit_2_by_its_name(self):
        """A failed value read is the tool's exit-2 error, not a traceback."""

        def succeed(command, env, stdout_log, stderr_log, timeout, cwd):
            stdout_log.write_bytes(b"recorded")
            stderr_log.write_bytes(b"")
            os.chmod(stdout_log, 0)  # the owner cannot open the file either
            return 0

        with mock.patch.object(
            required_command, "run_logged_split", side_effect=succeed
        ):
            value, status, stderr = self.run_output()
        self.assertEqual(2, status)
        self.assertEqual(b"", value)
        # The diagnostic names the log the value was to come from, never the
        # stderr tail: the command itself succeeded.
        self.assertIn("cannot read read.log:", stderr)
        self.assertNotIn("Traceback", stderr)
        # A run that never read its value is not a success, so neither log is
        # removed: the failed helper leaves both for the failure report.
        self.assertTrue((self.root / "read.log").exists())
        self.assertTrue((self.root / "read.stderr.log").exists())

    def test_a_nonempty_unreadable_stderr_log_reports_the_unreadable_tail(self):
        """A failure's stderr content that cannot be opened stays visible as lost."""

        def fail(command, env, stdout_log, stderr_log, timeout, cwd):
            stdout_log.write_bytes(b"recorded")
            stderr_log.write_bytes(b"secret diagnostics\n")
            os.chmod(stderr_log, 0)  # the owner cannot read the stderr back
            return 3

        with mock.patch.object(
            required_command, "run_logged_split", side_effect=fail
        ):
            value, status, stderr = self.run_output()
        self.assertEqual(b"", value)
        self.assertEqual(1, status)
        self.assertIn("a_tool: error: slowcmd exited 3", stderr)
        # The chosen log is the unreadable one, and its lost tail is said so:
        # no traceback, and never the stdout value in its place.
        self.assertIn("log could not be read:", stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertNotIn("recorded", stderr)

    def test_a_stderr_log_gone_from_disk_falls_back_to_the_stdout_tail(self):
        """A log swept away mid-run cannot abort failure triage with a traceback."""

        def fail(command, env, stdout_log, stderr_log, timeout, cwd):
            stdout_log.write_bytes(b"partial\n")
            stderr_log.write_bytes(b"")
            stderr_log.unlink()  # removed while the command still ran
            return 3

        with mock.patch.object(
            required_command, "run_logged_split", side_effect=fail
        ):
            value, status, stderr = self.run_output()
        self.assertEqual(b"", value)
        self.assertEqual(1, status)
        self.assertIn("a_tool: error: slowcmd exited 3", stderr)
        # The fallback names the surviving stdout log's tail; without the
        # OSError guard the vanished stderr log would traceback instead.
        self.assertIn("\n  partial\n", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_runs_where_asked_with_the_given_environment(self):
        def succeed(command, env, stdout_log, stderr_log, timeout, cwd):
            stdout_log.write_bytes(b"recorded")
            stderr_log.write_bytes(b"")
            return 0

        with mock.patch.object(
            required_command, "run_logged_split", side_effect=succeed
        ) as runner:
            value, status, stderr = self.run_output(timeout=12.5)
        self.assertIsNone(status)
        self.assertEqual(b"recorded", value)
        self.assertEqual("", stderr)
        runner.assert_called_once_with(
            COMMAND, self.env,
            self.root / "read.log", self.root / "read.stderr.log",
            12.5, self.cwd,
        )

    def test_a_nonzero_exit_returns_one_with_the_stderr_tail(self):
        value, status, stderr = self.run_output(
            ["sh", "-c", "echo broken >&2; echo value; exit 3"]
        )
        self.assertEqual(b"", value)
        self.assertEqual(1, status)
        self.assertIn("a_tool: error: sh exited 3", stderr)
        self.assertIn("\n  broken\n", stderr)
        self.assertNotIn("value", stderr.replace("broken", ""))

    def test_a_failed_command_with_no_stderr_falls_back_to_stdout(self):
        value, status, stderr = self.run_output(
            ["sh", "-c", "echo partial; exit 3"]
        )
        self.assertEqual(b"", value)
        self.assertEqual(1, status)
        self.assertIn("a_tool: error: sh exited 3", stderr)
        self.assertIn("\n  partial\n", stderr)

    def test_a_timeout_returns_one_with_what_did_reach_the_logs(self):
        with mock.patch.object(
            required_command, "run_logged_split", return_value=None
        ) as runner:
            value, status, stderr = self.run_output(timeout=0.25)
        runner.assert_called_once()
        self.assertEqual(b"", value)
        self.assertEqual(1, status)
        self.assertIn("a_tool: error: slowcmd timed out after 0.25s", stderr)

    def test_an_unstartable_command_returns_two_without_a_traceback(self):
        error = FileNotFoundError(
            2, "No such file or directory", "/nonexistent/interpreter"
        )
        with mock.patch.object(
            required_command, "run_logged_split", side_effect=error
        ):
            value, status, stderr = self.run_output()
        self.assertEqual(b"", value)
        self.assertEqual(2, status)
        self.assertIn("a_tool: error: cannot run slowcmd:", stderr)
        self.assertIn(str(error), stderr)
        self.assertNotIn("Traceback", stderr)

    def test_signal_death_names_the_signal_and_keeps_the_tail(self):
        value, status, stderr = self.run_output([
            sys.executable, "-c",
            "import os, signal, sys; print('before termination', "
            "flush=True); print('stopped', file=sys.stderr, flush=True); "
            "os.kill(os.getpid(), signal.SIGTERM)",
        ])
        self.assertEqual(b"", value)
        self.assertEqual(1, status)
        self.assertIn(
            f"a_tool: error: {sys.executable} killed by signal SIGTERM",
            stderr,
        )
        self.assertIn("\n  stopped\n", stderr)


if __name__ == "__main__":
    unittest.main()
