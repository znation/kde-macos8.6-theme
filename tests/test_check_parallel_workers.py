"""Tests for tools/check_parallel_workers.py's spawn and clean-up defenses.

The coordinator's worker supervision -- Popen deferral against SIGTERM, HUP
and Ctrl-C races before a worker can be signaled, group-kill and bounded
reap on the way out, and self-defenses against a spawn error or an
unopenable log -- carries the same guarantee set ``test_process_group.py``
pins for the shared ``process_group`` primitives; these tests show the
worker-start side upholds it. They need their own module over the
coordinator's scratch-suite runs, so a spawn sweep can run its mock-patched
cases without dragging the whole subprocess-based coordinator suite along.
"""

from __future__ import annotations

import contextlib
import io
import os
import signal
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

from support.check_parallel_fixtures import OK_MODULE, _write_module
from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir
from tools import check_parallel_workers, process_group




class TestSpawnDefenses(unittest.TestCase):
    """The spawn/kill primitives keep the guarantees test_process_group pins.

    ``tools.process_group.py::_popen_deferred`` protects both command and
    worker starts from SIGTERM, SIGHUP and Ctrl-C races; worker cleanup also
    never signals a non-positive pid.
    """

    def test_a_worker_start_error_is_recorded_in_its_log(self):
        log_path = str(make_tmp_dir(self) / "spawn.log")
        with mock.patch.object(
            check_parallel_workers.subprocess, "Popen",
            side_effect=OSError("executable unavailable"),
        ):
            worker = check_parallel_workers._spawn(
                "test_missing", ["missing-python"], str(ROOT), log_path, 30
            )

        self.assertEqual(1, worker.process.poll())
        self.assertEqual(
            "check: the worker could not be started: executable unavailable\n",
            Path(log_path).read_text(encoding="utf-8"),
        )

    def test_a_non_regular_log_path_is_refused_not_written_through(self):
        # _open_log's write-side regular-file check mirrors the read-side
        # check _print_results pins through the FIFO and directory log
        # tests: a worker log path that opens successfully but is not a
        # regular file must not become the sink the worker's output is
        # streamed into. /dev/zero is the one non-regular file the open
        # flags (O_WRONLY|O_CREAT|O_TRUNC|O_NONBLOCK) still succeed on --
        # O_CREAT and O_TRUNC are ignored on a device -- so only the
        # regular-file check can refuse it, while a FIFO ENXIOes before
        # the check runs (pinned at test_fifo_worker_log_fails...
        # through _supervise).
        if not os.path.exists("/dev/zero"):
            self.skipTest("/dev/zero is Linux-specific")
        with self.assertRaisesRegex(
            OSError, r"/dev/zero is not a regular file"
        ):
            check_parallel_workers._open_log("/dev/zero")

    def test_a_non_regular_log_closes_the_descriptor_it_opened(self):
        # Refusing must not leak the descriptor _open_log opened, or a
        # scratch volume seeded with openable non-regular names would drain
        # the run's open-file limit one descriptor per module. /proc/self/fd
        # is the sure way to observe that a descriptor this process opened
        # and did not hand out is gone; skip where it is unavailable.
        if not os.path.exists("/dev/zero"):
            self.skipTest("/dev/zero is Linux-specific")
        if not os.path.isdir("/proc/self/fd"):
            self.skipTest("/proc/self/fd is Linux-specific")
        open_before = len(os.listdir("/proc/self/fd"))
        with self.assertRaises(OSError):
            check_parallel_workers._open_log("/dev/zero")
        self.assertEqual(len(os.listdir("/proc/self/fd")), open_before)

    def test_a_non_regular_log_fails_only_its_module(self):
        # Through _supervise: the refusal arrives as an OSError like any
        # other failed log open, so the module is recorded as never started
        # (exit 1) with one stderr diagnostic naming it and the refused
        # path, and the other workers still run -- never a traceback
        # killing the run.
        if not os.path.exists("/dev/zero"):
            self.skipTest("/dev/zero is Linux-specific")
        tests_dir = str(make_tmp_dir(self) / "tests")
        os.mkdir(tests_dir)
        _write_module(tests_dir, "test_two.py", OK_MODULE)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            statuses = check_parallel_workers._supervise(
                ["test_ok", "test_two"],
                [sys.executable, "-m", "unittest", "-v"],
                tests_dir,
                {"test_ok": "/dev/zero", "test_two":
                 str(make_tmp_dir(self) / "worker.log")},
                60,
                2,
            )
        self.assertEqual(1, statuses["test_ok"])
        self.assertEqual(0, statuses["test_two"])
        stderr_text = stderr.getvalue()
        self.assertIn("cannot open the worker log for test_ok", stderr_text)
        self.assertIn("/dev/zero is not a regular file", stderr_text)

    def test_log_close_failure_kills_a_started_worker(self):
        log_path = str(make_tmp_dir(self) / "spawn.log")
        processes = []

        class CloseFails:
            def __init__(self, handle):
                self.handle = handle

            def __enter__(self):
                return self.handle

            def __exit__(self, *args):
                self.handle.close()
                raise OSError("log close failed")

        real_popen = subprocess.Popen

        def capture_popen(*args, **kwargs):
            process = real_popen(*args, **kwargs)
            processes.append(process)
            return process

        real_fdopen = os.fdopen

        def failing_fdopen(descriptor, *args, **kwargs):
            handle = real_fdopen(descriptor, *args, **kwargs)
            return CloseFails(handle) if descriptor else handle

        with (
            mock.patch.object(check_parallel_workers.os, "fdopen", side_effect=failing_fdopen),
            mock.patch.object(check_parallel_workers.subprocess, "Popen",
                              side_effect=capture_popen),
        ):
            with self.assertRaisesRegex(OSError, "log close failed"):
                check_parallel_workers._spawn(
                    "test_sleep", [sys.executable, "-c", "import time; time.sleep(30)"],
                    str(ROOT), log_path, 30,
                )

        self.assertEqual(1, len(processes))
        self.assertIsNotNone(processes[0].poll())

    def test_an_unexpected_popen_error_restores_deferred_signals(self):
        log_path = str(make_tmp_dir(self) / "spawn.log")
        termination_handlers = [(signal.SIGTERM, object())]
        interrupt_handlers = [(signal.SIGINT, object())]
        with (
            mock.patch.object(
                check_parallel_workers.subprocess, "Popen",
                side_effect=RuntimeError("broken popen wrapper"),
            ),
            mock.patch.object(
                process_group, "_defer_signals",
                side_effect=[termination_handlers, interrupt_handlers],
            ),
            mock.patch.object(
                process_group, "_restore_termination"
            ) as restore,
            mock.patch.object(
                process_group, "_replay_deferred"
            ) as replay,
        ):
            with self.assertRaisesRegex(RuntimeError, "broken popen wrapper"):
                check_parallel_workers._spawn(
                    "test_broken", ["python"], str(ROOT), log_path, 30
                )

        self.assertEqual(
            [mock.call(termination_handlers), mock.call(interrupt_handlers)],
            restore.call_args_list,
        )
        replay.assert_called_once_with([])

    def test_kill_group_ignores_a_worker_that_never_started(self):
        # A _NeverStarted worker has pid 0, and os.killpg(0, ...) signals the
        # coordinator's own process group -- under `make check`, make's
        # jobserver. The guard must reach no signal at all.
        with mock.patch.object(process_group.os, "killpg") as killpg:
            check_parallel_workers._kill_group(
                check_parallel_workers._NeverStarted()
            )
        killpg.assert_not_called()

    def test_kill_group_ignores_a_worker_group_that_already_exited(self):
        process = mock.Mock(pid=123)
        with mock.patch.object(
            process_group.os, "killpg",
            side_effect=ProcessLookupError,
        ) as killpg:
            check_parallel_workers._kill_group(process)

        killpg.assert_called_once_with(123, signal.SIGKILL)

    def test_reap_ignores_a_worker_that_does_not_exit_within_the_bound(self):
        process = mock.Mock()
        process.wait.side_effect = subprocess.TimeoutExpired("worker", 5)

        check_parallel_workers._reap(process)

        process.wait.assert_called_once_with(timeout=5.0)

    def _spawn_while_popen_signals(self, number, raises):
        """Signal the coordinator *number* while Popen returns; spawn a sleeper.

        Returns the started worker's pid -- kill -0 proves whether the
        deferral machinery killed its group on the way out.
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
        log_path = str(make_tmp_dir(self) / "spawn.log")
        with mock.patch.object(
            check_parallel_workers.subprocess, "Popen", side_effect=popen_then_signal
        ):
            with self.assertRaises(raises) as caught:
                with process_group.exit_on_termination():
                    check_parallel_workers._spawn(
                        "test_probe",
                        [sys.executable, "-c", "import time; time.sleep(60)"],
                        str(ROOT),
                        log_path,
                        30,
                    )
        return child["pid"], caught.exception

    def test_a_sigterm_while_popen_returns_still_kills_the_worker(self):
        # Without the deferral, exit_on_termination's handler raises
        # SystemExit before the worker is appended to the supervised set, so
        # the finally block never saw it: the worker outlived the
        # coordinator. The replay must arrive only after _spawn's own kill
        # and reap have run, and with the shell-convention exit code.
        pid, exception = self._spawn_while_popen_signals(
            signal.SIGTERM, SystemExit
        )
        self.assertEqual(128 + signal.SIGTERM, exception.code)
        self.assertTrue(_gone(pid))

    def test_a_sigint_while_popen_returns_still_kills_the_worker(self):
        # Ctrl-C's default handler raises KeyboardInterrupt at the next
        # bytecode; deferred and replayed inside _spawn's cleanup, it must
        # still take the worker's group down on the way out.
        pid, _ = self._spawn_while_popen_signals(
            signal.SIGINT, KeyboardInterrupt
        )
        self.assertTrue(_gone(pid))


def _gone(pid):
    """Return True once *pid* no longer exists, waiting up to five seconds."""
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.02)
    return False

if __name__ == "__main__":
    unittest.main()
