"""Tests for tools/process_group.py, the render and apply scripts' process supervisor."""

from __future__ import annotations

import os
import signal
import subprocess
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

    def test_an_unkillable_child_does_not_stall_after_its_timeout(self):
        # A process in uninterruptible I/O (a hung network or FUSE mount)
        # ignores SIGKILL until the kernel releases it, which may be never.
        # `run_logged`'s cleanup wait used to have no timeout, so it would
        # block forever after the command's own timeout had already fired;
        # `make apply` and `make render` (and the post-commit hook running
        # apply) would never return. The reap must be bounded like the wait.
        process = mock.Mock(pid=4242)
        process.wait.side_effect = [
            subprocess.TimeoutExpired(["slow"], 0.1),
            subprocess.TimeoutExpired(["slow"], 0.1),
        ]
        with mock.patch.object(
            process_group.subprocess, "Popen", return_value=process
        ), mock.patch.object(process_group, "_kill_group") as kill_group:
            status = process_group.run_logged(
                ["slow"], dict(os.environ), self.log, 0.1, self.root
            )
        self.assertIsNone(status)
        kill_group.assert_called_once_with(process)
        timeouts = [call.kwargs.get("timeout") for call in process.wait.call_args_list]
        self.assertEqual(2, len(timeouts))
        for wait_timeout in timeouts:
            self.assertIsNotNone(wait_timeout)

    def test_a_sigterm_while_popen_returns_still_kills_the_child(self):
        # exit_on_termination's handler raises SystemExit at the next
        # bytecode. A SIGTERM that arrives while Popen is still returning was
        # raised before run_logged's try/finally was entered, so the group
        # kill was skipped and the command kept running after the caller
        # died. Deliver the signal from inside Popen, at the exact point the
        # real one returns, so the race is deterministic.
        real_popen = subprocess.Popen
        child = {}

        def popen_then_terminate(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            child["pid"] = process.pid
            os.kill(os.getpid(), signal.SIGTERM)
            return process

        def kill_child():
            pid = child.get("pid")
            if pid is not None:
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass

        self.addCleanup(kill_child)
        with mock.patch.object(
            process_group.subprocess, "Popen", side_effect=popen_then_terminate
        ):
            with process_group.exit_on_termination():
                with self.assertRaises(SystemExit) as caught:
                    process_group.run_logged(
                        ["/bin/sleep", "60"],
                        dict(os.environ),
                        self.log,
                        30,
                        self.root,
                    )
        self.assertEqual(128 + signal.SIGTERM, caught.exception.code)
        self.assertTrue(is_gone(child["pid"]))

    def test_a_reap_timeout_does_not_replace_the_signal_that_interrupted_the_wait(self):
        # A SIGTERM or SIGHUP makes exit_on_termination's handler raise
        # SystemExit out of the first wait. If the just-killed child is in
        # uninterruptible I/O, the bounded reap times out too; re-raising that
        # would replace the shell-convention exit code (128 + signal) with a
        # traceback, so `make render`/`make apply` would die noisy instead of
        # unwinding.
        process = mock.Mock(pid=4242)
        process.wait.side_effect = [
            SystemExit(128 + signal.SIGTERM),
            subprocess.TimeoutExpired(["slow"], 0.1),
        ]
        with mock.patch.object(
            process_group.subprocess, "Popen", return_value=process
        ), mock.patch.object(process_group, "_kill_group"):
            with self.assertRaises(SystemExit) as caught:
                process_group.run_logged(
                    ["slow"], dict(os.environ), self.log, 0.1, self.root
                )
        self.assertEqual(128 + signal.SIGTERM, caught.exception.code)
        timeouts = [call.kwargs.get("timeout") for call in process.wait.call_args_list]
        self.assertEqual(2, len(timeouts))
        for wait_timeout in timeouts:
            self.assertIsNotNone(wait_timeout)


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
