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


class TestReplayDeferred(unittest.TestCase):
    def test_replays_only_the_first_signal_recorded_while_the_child_starts(self):
        # A start can be interrupted by more than one signal: a terminal
        # hangup followed by a kill, or a second Ctrl-C. _defer_signals
        # records each one; _replay_deferred must re-raise the first, so the
        # shell convention reports the signal that ended the run. Replaying a
        # later one would change the exit status, or turn a termination into
        # a Ctrl-C, even though the earlier signal is what stopped it.
        cases = (
            ([signal.SIGHUP, signal.SIGTERM], SystemExit, 128 + signal.SIGHUP),
            ([signal.SIGINT, signal.SIGTERM], KeyboardInterrupt, None),
        )
        for deferred, expected, code in cases:
            with self.subTest(
                deferred=[number.name for number in deferred]
            ):
                with self.assertRaises(expected) as caught:
                    process_group._replay_deferred(deferred)
                if code is not None:
                    self.assertEqual(code, caught.exception.code)


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
        # The shell must fork its background sleep and write its pid before
        # the timeout fires, or the group has no member to check. A loaded
        # host can delay that setup past the 0.5 s budget -- the same budget
        # the process_runner timeout tests use for a child that has to finish
        # setup before it is killed -- leaving no pidfile to read. Retry with
        # a fresh file per attempt, so a retry cannot read an earlier run's
        # pid; each timed-out attempt has already had its whole group killed
        # by run_logged, so none leaks. The deadline bounds the retries, so a
        # host that never starts the shell fails instead of spinning.
        started = time.monotonic()
        deadline = started + 30
        while True:
            self.assertLess(
                time.monotonic(),
                deadline,
                "the shell never wrote the background pid before the timeout",
            )
            pidfile = self.root / f"pid-{time.monotonic_ns()}"
            status = self.run_sh(
                f'sleep 60 & echo $! > "{pidfile}"; wait', timeout=0.5
            )
            self.assertIsNone(status)
            try:
                pid = int(pidfile.read_text(encoding="utf-8"))
            except (FileNotFoundError, ValueError):
                # The timeout fired before the shell finished its setup, so
                # this attempt proved nothing about the group kill.
                continue
            break
        # One attempt may return just under the deadline; allow for it.
        self.assertLess(time.monotonic() - started, 31)
        self.assertTrue(is_gone(pid))

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

    def _run_while_popen_returns(self, number, raises):
        """Run the logged runner while *number* arrives inside Popen.

        Popen is the exact point where a real signal races the supervisor's
        try/finally: the signal is delivered before ``run_logged`` enters it,
        so this reproduces the startup race deterministically. The caller runs
        under ``exit_on_termination`` so SIGTERM and SIGHUP become
        ``SystemExit``; SIGINT keeps its default ``KeyboardInterrupt``.
        *raises* is the exception the caller expects that signal to raise.
        The child is killed in a cleanup so a regression does not leave it
        running, and this fails unless it is gone by the time the exception
        escapes.
        """
        real_popen = subprocess.Popen
        child = {}

        def popen_then_signal(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            child["pid"] = process.pid
            os.kill(os.getpid(), number)
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
            process_group.subprocess, "Popen", side_effect=popen_then_signal
        ):
            with self.assertRaises(raises) as caught:
                with process_group.exit_on_termination():
                    process_group.run_logged(
                        ["/bin/sleep", "60"],
                        dict(os.environ),
                        self.log,
                        30,
                        self.root,
                    )
        self.assertTrue(is_gone(child["pid"]))
        return caught.exception

    def test_a_sigterm_while_popen_returns_still_kills_the_child(self):
        # exit_on_termination's handler raises SystemExit at the next
        # bytecode. A SIGTERM that arrives while Popen is still returning was
        # raised before run_logged's try/finally was entered, so the group
        # kill was skipped and the command kept running after the caller
        # died.
        caught = self._run_while_popen_returns(signal.SIGTERM, SystemExit)
        self.assertEqual(128 + signal.SIGTERM, caught.code)

    def test_a_sigint_while_popen_returns_still_kills_the_child(self):
        # Ctrl-C's default handler raises KeyboardInterrupt at the next
        # bytecode, so an interrupt that arrives while Popen is still
        # returning unwinds the caller before run_logged's try/finally is
        # entered: the group kill is skipped and the command keeps running.
        self._run_while_popen_returns(signal.SIGINT, KeyboardInterrupt)

    def test_a_sighup_while_popen_returns_still_kills_the_child(self):
        # exit_on_termination handles SIGHUP as well as SIGTERM: a terminal
        # hangup must not leave the command running either. The SIGTERM race
        # test above would keep passing if SIGHUP were dropped from the
        # deferral, so this pins the same cleanup for SIGHUP.
        caught = self._run_while_popen_returns(signal.SIGHUP, SystemExit)
        self.assertEqual(128 + signal.SIGHUP, caught.code)

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
