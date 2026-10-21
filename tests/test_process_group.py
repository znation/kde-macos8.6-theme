"""Tests for tools/process_group.py, the render and apply scripts' process supervisor."""

from __future__ import annotations

import os
import signal
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import process_group  # noqa: E402


def is_gone(pid):
    """Return True once *pid* no longer exists, waiting up to five seconds."""
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.02)
    return False


class TestKillGroup(unittest.TestCase):
    def test_ignores_a_process_group_that_is_already_gone(self):
        # run_logged's finally block calls _kill_group after the child has
        # been waited for, so a child that left no group member behind is
        # already reaped and os.killpg raises ProcessLookupError. The cleanup
        # must swallow that OSError; otherwise a normal exit would surface as
        # a traceback and mask the child's exit status. The race is forced
        # here because staging it for real is not deterministic.
        process = mock.Mock(pid=4242)
        with mock.patch.object(
            process_group.os, "killpg", side_effect=ProcessLookupError
        ) as killpg:
            process_group._kill_group(process)
        killpg.assert_called_once_with(4242, signal.SIGKILL)


class TestRunLogged(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.log = self.root / "log"

    def run_sh(self, script, timeout=30):
        """Run *script* through the logged runner and return its exit status."""
        return process_group.run_logged(
            ["sh", "-c", script], dict(os.environ), self.log, timeout, self.root
        )

    def test_returns_the_exit_status_and_logs_stdout_and_stderr(self):
        status = self.run_sh("echo out; echo err >&2; exit 3")
        self.assertEqual(3, status)
        lines = self.log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(["err", "out"], sorted(lines))

    def test_runs_in_the_given_directory_with_the_given_environment(self):
        process_group.run_logged(
            ["sh", "-c", 'echo "$PWD $MARK"'],
            {"PATH": os.environ["PATH"], "MARK": "m1"},
            self.log,
            30,
            self.root,
        )
        cwd, mark = self.log.read_text(encoding="utf-8").split()
        self.assertEqual(os.path.realpath(self.root), os.path.realpath(cwd))
        self.assertEqual("m1", mark)

    def test_a_descendant_outliving_the_child_is_killed_on_normal_exit(self):
        pidfile = self.root / "pid"
        status = self.run_sh(f'sleep 60 & echo $! > "{pidfile}"; exit 0')
        self.assertEqual(0, status)
        self.assertTrue(is_gone(int(pidfile.read_text(encoding="utf-8"))))

    def test_timeout_returns_none_and_kills_the_group(self):
        pidfile = self.root / "pid"
        started = time.monotonic()
        # The shell must fork its background sleep and write the pidfile
        # before the timeout fires, so the budget is a little more than the
        # setup needs -- the same 0.5 s the process_runner timeout tests use
        # for a child that has to finish setup before it is killed. The child
        # sleeps for 60 s, so any budget here times out.
        status = self.run_sh(f'sleep 60 & echo $! > "{pidfile}"; wait', timeout=0.5)
        self.assertIsNone(status)
        self.assertLess(time.monotonic() - started, 30)
        self.assertTrue(is_gone(int(pidfile.read_text(encoding="utf-8"))))

    def test_stdin_is_closed(self):
        self.assertEqual(0, self.run_sh("cat; exit 0", timeout=10))
        self.assertEqual("", self.log.read_text(encoding="utf-8"))


class TestExitOnTermination(unittest.TestCase):
    def _kill_self_under_exit_on_termination(self, number):
        """Send *number* to this process and return the shell-convention code."""
        with process_group.exit_on_termination():
            with self.assertRaises(SystemExit) as caught:
                os.kill(os.getpid(), number)
                time.sleep(5)
        return caught.exception.code

    def test_sigterm_and_sighup_raise_system_exit_with_shell_codes(self):
        for number in (signal.SIGTERM, signal.SIGHUP):
            with self.subTest(signal=number.name):
                self.assertEqual(
                    128 + number,
                    self._kill_self_under_exit_on_termination(number),
                )

    def test_previous_handlers_are_restored_even_after_an_exception(self):
        before = (signal.getsignal(signal.SIGTERM), signal.getsignal(signal.SIGHUP))
        with self.assertRaises(RuntimeError):
            with process_group.exit_on_termination():
                raise RuntimeError
        after = (signal.getsignal(signal.SIGTERM), signal.getsignal(signal.SIGHUP))
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
