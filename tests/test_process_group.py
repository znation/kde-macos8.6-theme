"""Tests for tools/process_group.py, the render and apply scripts' process supervisor."""

from __future__ import annotations

import os
import signal
import subprocess
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.popen_signal import gone  # noqa: E402
from support.popen_signal import kill_tracked  # noqa: E402
from support.popen_signal import signal_into_popen  # noqa: E402
from tools import process_group  # noqa: E402


class TestKillGroup(unittest.TestCase):
    def test_ignores_a_process_group_that_is_already_gone(self):
        # run_logged's finally block calls kill_group after the child has
        # been waited for, so a child that left no group member behind is
        # already reaped and os.killpg raises ProcessLookupError. The cleanup
        # must swallow that OSError; otherwise a normal exit would surface as
        # a traceback and mask the child's exit status. The race is forced
        # here because staging it for real is not deterministic.
        process = mock.Mock(pid=4242)
        with mock.patch.object(
            process_group.os, "killpg", side_effect=ProcessLookupError
        ) as killpg:
            process_group.kill_group(process)
        killpg.assert_called_once_with(4242, signal.SIGKILL)


class TestReplayDeferred(unittest.TestCase):
    def test_replays_only_the_first_signal_recorded_while_the_child_starts(self):
        # A start can be interrupted by more than one signal: a terminal
        # hangup followed by a kill, or a second Ctrl-C. _defer_signals
        # records each one; replay_deferred must re-raise the first, so the
        # shell convention reports the signal that ended the run. Replaying a
        # later one would change the exit status, or turn a termination into
        # a Ctrl-C, even though the earlier signal is what stopped it.
        cases = (
            ([signal.SIGHUP, signal.SIGTERM], SystemExit, 128 + signal.SIGHUP),
            ([signal.SIGTERM, signal.SIGINT], SystemExit, 128 + signal.SIGTERM),
            ([signal.SIGINT, signal.SIGTERM], KeyboardInterrupt, None),
        )
        for deferred, expected, code in cases:
            with self.subTest(
                deferred=[number.name for number in deferred]
            ):
                with self.assertRaises(expected) as caught:
                    process_group.replay_deferred(deferred)
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
        self.assertTrue(gone(int(pidfile.read_text(encoding="utf-8"))))

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
        self.assertTrue(gone(pid))

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
        ), mock.patch.object(process_group, "kill_group") as kill_group:
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
        tracked = {}
        self.addCleanup(kill_tracked, tracked)
        with mock.patch.object(
            process_group.subprocess,
            "Popen",
            side_effect=signal_into_popen(number, tracked),
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
        self.assertTrue(gone(tracked["pid"]))
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

    def test_a_custom_sigint_handler_keeps_its_behavior_during_start(self):
        received = []
        handler = lambda number, frame: received.append(number)
        old = signal.signal(signal.SIGINT, handler)
        self.addCleanup(signal.signal, signal.SIGINT, old)
        with mock.patch.object(
            process_group.subprocess,
            "Popen",
            side_effect=signal_into_popen(signal.SIGINT),
        ):
            self.assertEqual(0, self.run_sh("exit 0"))
        self.assertEqual([signal.SIGINT], received)
        self.assertIs(handler, signal.getsignal(signal.SIGINT))

    def test_a_custom_sigterm_handler_keeps_its_behavior_during_start(self):
        received = []
        handler = lambda number, frame: received.append(number)
        old = signal.signal(signal.SIGTERM, handler)
        self.addCleanup(signal.signal, signal.SIGTERM, old)
        with mock.patch.object(
            process_group.subprocess,
            "Popen",
            side_effect=signal_into_popen(signal.SIGTERM),
        ):
            self.assertEqual(0, self.run_sh("exit 0"))
        self.assertEqual([signal.SIGTERM], received)
        self.assertIs(handler, signal.getsignal(signal.SIGTERM))

    def test_default_signal_handlers_allow_running_from_a_worker_thread(self):
        for number in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
            handler = (
                signal.default_int_handler if number == signal.SIGINT
                else signal.SIG_DFL
            )
            old = signal.signal(number, handler)
            self.addCleanup(signal.signal, number, old)
        with ThreadPoolExecutor(max_workers=1) as executor:
            self.assertEqual(3, executor.submit(self.run_sh, "exit 3").result(10))

    def _run_while_handlers_are_restored(self, number, raises):
        """Run the logged runner while *number* arrives as handlers swap back.

        Restoring the real handlers is the second half of the startup race:
        once the recording handlers are swapped back out, the next signal
        raises immediately, so it must raise inside ``run_logged``'s cleanup
        try -- where the group kill runs -- not before that try exists. The
        signal is injected at the second restore, the one that re-arms the
        raising handlers, so the race is deterministic. The child is killed
        in a cleanup so a regression does not leave it running, and this
        fails unless it is gone by the time the exception escapes.
        """
        real_restore = process_group.restore_termination
        real_popen = subprocess.Popen
        child = {}
        restores = []

        def restore_then_signal(previous):
            real_restore(previous)
            restores.append(previous)
            if len(restores) == 2:
                os.kill(os.getpid(), number)

        def capture_popen(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            child["pid"] = process.pid
            return process

        def kill_child():
            pid = child.get("pid")
            if pid is not None:
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass

        self.addCleanup(kill_child)
        with (
            mock.patch.object(
                process_group.subprocess, "Popen", side_effect=capture_popen
            ),
            mock.patch.object(
                process_group, "restore_termination",
                side_effect=restore_then_signal,
            ),
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
        self.assertTrue(gone(child["pid"]))
        return caught.exception

    def test_a_sigterm_while_the_handlers_are_restored_still_kills_the_child(self):
        # A SIGTERM that arrives just as the recording handlers are swapped
        # back for the real ones raises at the next bytecode. If that raise
        # happens before run_logged's try/finally exists -- in the startup
        # helper, not in the caller's cleanup -- the group kill is skipped
        # and the command keeps running after the caller died.
        caught = self._run_while_handlers_are_restored(
            signal.SIGTERM, SystemExit
        )
        self.assertEqual(128 + signal.SIGTERM, caught.code)

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
        ), mock.patch.object(process_group, "kill_group"):
            with self.assertRaises(SystemExit) as caught:
                process_group.run_logged(
                    ["slow"], dict(os.environ), self.log, 0.1, self.root
                )
        self.assertEqual(128 + signal.SIGTERM, caught.exception.code)
        timeouts = [call.kwargs.get("timeout") for call in process.wait.call_args_list]
        self.assertEqual(2, len(timeouts))
        for wait_timeout in timeouts:
            self.assertIsNotNone(wait_timeout)

    def test_a_termination_signal_during_a_failed_start_is_replayed(self):
        # popen_deferred's cleanup for a failing Popen restores the handlers
        # and then replays whatever the deferral recorded before the start
        # error is raised. A SIGTERM that arrives while the start is failing
        # must therefore unwind the caller with the shell's 128 + SIGTERM
        # status, not with the OSError the caller reports as "cannot run
        # ...": the run was terminated, and the exit status has to say so.
        # Dropping the replay from that cleanup would turn a terminated start
        # into a start-failure diagnostic instead.
        def popen_then_signal_then_fail(*args, **kwargs):
            os.kill(os.getpid(), signal.SIGTERM)
            raise FileNotFoundError("not-startable")

        with mock.patch.object(
            process_group.subprocess,
            "Popen",
            side_effect=popen_then_signal_then_fail,
        ):
            with self.assertRaises(SystemExit) as caught:
                with process_group.exit_on_termination():
                    process_group.run_logged(
                        ["not-startable"],
                        dict(os.environ),
                        self.log,
                        30,
                        self.root,
                    )
        self.assertEqual(128 + signal.SIGTERM, caught.exception.code)

    def test_a_failed_start_restores_the_default_interrupt_handler(self):
        # The deferral swaps SIGINT's default handler for the recording one
        # around every start, including one whose Popen raises. The except
        # arm must restore it: a dropped restore would leave the recording
        # handler installed, so a later Ctrl-C would be appended to a list
        # nobody replays instead of raising KeyboardInterrupt.
        with mock.patch.object(
            process_group.subprocess,
            "Popen",
            side_effect=FileNotFoundError("not-startable"),
        ):
            with self.assertRaises(FileNotFoundError):
                process_group.run_logged(
                    ["not-startable"], dict(os.environ), self.log, 30, self.root
                )
        self.assertIs(
            signal.default_int_handler, signal.getsignal(signal.SIGINT)
        )


class TestRunLoggedSplit(unittest.TestCase):
    """The split-output variant of the logged supervisor.

    A caller that reads a value from a command's stdout cannot use the merged
    log, because the command's stderr warnings would become part of the
    value; :func:`run_logged_split` is the same supervision with the two
    streams in separate files.
    """

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.stdout_log = self.root / "out.log"
        self.stderr_log = self.root / "err.log"

    def run_sh(self, script, timeout=30):
        """Run *script* with split logs and return its exit status."""
        return process_group.run_logged_split(
            ["sh", "-c", script],
            dict(os.environ),
            self.stdout_log,
            self.stderr_log,
            timeout,
            self.root,
        )

    def test_returns_the_exit_status_and_keeps_the_streams_apart(self):
        status = self.run_sh("echo out; echo err >&2; exit 3")
        self.assertEqual(3, status)
        self.assertEqual(["out"],
                         self.stdout_log.read_text(encoding="utf-8").split())
        self.assertEqual(["err"],
                         self.stderr_log.read_text(encoding="utf-8").split())

    def test_runs_in_the_given_directory_with_the_given_environment(self):
        process_group.run_logged_split(
            ["sh", "-c", 'echo "$PWD $MARK"'],
            {"PATH": os.environ["PATH"], "MARK": "m1"},
            self.stdout_log,
            self.stderr_log,
            30,
            self.root,
        )
        cwd, mark = self.stdout_log.read_text(encoding="utf-8").split()
        self.assertEqual(os.path.realpath(self.root), os.path.realpath(cwd))
        self.assertEqual("m1", mark)

    def test_custom_sigterm_handler_keeps_its_behavior_during_start(self):
        received = []
        handler = lambda number, frame: received.append(number)
        old = signal.signal(signal.SIGTERM, handler)
        self.addCleanup(signal.signal, signal.SIGTERM, old)
        with mock.patch.object(
            process_group.subprocess,
            "Popen",
            side_effect=signal_into_popen(signal.SIGTERM),
        ):
            self.assertEqual(0, self.run_sh("exit 0"))
        self.assertEqual([signal.SIGTERM], received)
        self.assertIs(handler, signal.getsignal(signal.SIGTERM))

    def test_a_descendant_outliving_the_child_is_killed_on_normal_exit(self):
        pidfile = self.root / "pid"
        status = self.run_sh(f'sleep 60 & echo $! > "{pidfile}"; exit 0')
        self.assertEqual(0, status)
        self.assertTrue(gone(int(pidfile.read_text(encoding="utf-8"))))

    def test_stdin_is_closed(self):
        self.assertEqual(0, self.run_sh("cat; exit 0", timeout=10))
        self.assertEqual("", self.stdout_log.read_text(encoding="utf-8"))

    def test_stdin_bytes_are_written_and_closed(self):
        payload = b"first line\n\x00last line\n"
        status = process_group.run_logged_split(
            ["cat"],
            dict(os.environ),
            self.stdout_log,
            self.stderr_log,
            10,
            self.root,
            stdin_bytes=payload,
        )
        self.assertEqual(0, status)
        self.assertEqual(payload, self.stdout_log.read_bytes())
        self.assertEqual(b"", self.stderr_log.read_bytes())

    def test_thread_start_failure_kills_the_child(self):
        child = {}
        real_popen = subprocess.Popen

        def capture_popen(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            child["pid"] = process.pid
            return process

        with mock.patch.object(
            process_group.subprocess, "Popen", side_effect=capture_popen
        ), mock.patch.object(
            process_group.threading.Thread,
            "start",
            side_effect=RuntimeError("thread start failed"),
        ):
            with self.assertRaisesRegex(RuntimeError, "thread start failed"):
                process_group.run_logged_split(
                    ["/bin/sleep", "60"],
                    dict(os.environ),
                    self.stdout_log,
                    self.stderr_log,
                    30,
                    self.root,
                    stdin_bytes=b"input",
                )

        self.assertTrue(gone(child["pid"]))


class TestFeedStdin(unittest.TestCase):
    """_feed_stdin runs in a daemon thread and must never raise out of it.

    A child that exits or stops reading makes the write fail with a broken
    pipe; the run's outcome does not depend on that write, so the error is
    swallowed. The sink must still be closed, or the child waiting for EOF
    would hang.
    """

    def test_a_broken_pipe_on_write_is_swallowed_and_the_sink_is_closed(self):
        sink = mock.Mock()
        sink.write.side_effect = BrokenPipeError
        process_group._feed_stdin(sink, b"payload")
        sink.write.assert_called_once_with(b"payload")
        sink.close.assert_called_once_with()

    def test_an_os_error_on_write_is_swallowed_and_the_sink_is_closed(self):
        sink = mock.Mock()
        sink.write.side_effect = OSError
        process_group._feed_stdin(sink, b"payload")
        sink.close.assert_called_once_with()

    def test_an_error_on_close_is_swallowed(self):
        sink = mock.Mock()
        sink.close.side_effect = BrokenPipeError
        process_group._feed_stdin(sink, b"payload")
        sink.write.assert_called_once_with(b"payload")
        sink.close.assert_called_once_with()

    def test_a_child_that_exits_without_reading_stdin_keeps_its_status(self):
        # The payload is far larger than a pipe buffer, so the write cannot
        # finish until the child is gone; the broken pipe must not replace
        # the child's exit status or stall the run past its timeout.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            status = process_group.run_logged_split(
                ["sh", "-c", "exit 7"],
                dict(os.environ),
                root / "out.log",
                root / "err.log",
                10,
                root,
                stdin_bytes=b"x" * (1 << 20),
            )
        self.assertEqual(7, status)


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
