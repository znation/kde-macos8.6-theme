"""Tests for tools/process_group.py::run_logged_split and its stdin and writer helpers.

The split-output variant of the logged supervisor runs one command with its
stdout and stderr captured apart, feeds stdin from a writer thread, and
finishes that writer on every exit path. These classes were the last part of
``test_process_group``; they move here verbatim, under the same names.
"""

import os
import signal
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.popen_signal import assert_custom_handler_keeps_its_behavior_during_start  # noqa: E402
from support.popen_signal import gone  # noqa: E402
from tools import process_group  # noqa: E402


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
        assert_custom_handler_keeps_its_behavior_during_start(
            self, signal.SIGTERM
        )

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

    def test_timeout_returns_none_and_kills_the_process_group(self):
        process = mock.Mock(pid=4242, stdin=None)
        process.wait.side_effect = subprocess.TimeoutExpired(["slow"], 0.25)
        with mock.patch.object(
            process_group.subprocess, "Popen", return_value=process
        ), mock.patch.object(process_group, "kill_group") as kill_group:
            status = process_group.run_logged_split(
                ["slow"], dict(os.environ), self.stdout_log, self.stderr_log,
                0.25, self.root,
            )
        self.assertIsNone(status)
        kill_group.assert_called_once_with(process)
        self.assertEqual(
            [mock.call(timeout=0.25), mock.call(timeout=process_group._REAP_TIMEOUT)],
            process.wait.call_args_list,
        )
        self.assertEqual(b"", self.stdout_log.read_bytes())
        self.assertEqual(b"", self.stderr_log.read_bytes())

    def test_split_custom_sigint_handler_keeps_its_behavior_during_start(self):
        assert_custom_handler_keeps_its_behavior_during_start(
            self, signal.SIGINT
        )

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


class TestFinishWriter(unittest.TestCase):
    """_finish_writer is the cleanup step that retires the stdin writer.

    A writer that never started cannot be joined, so the child's stdin is
    closed here to unblock a child still reading. A started writer closes its
    own pipe, and is joined with the bounded reap timeout so cleanup cannot
    stall. A failure closing the unstarted pipe is swallowed.
    """

    def test_no_writer_leaves_the_child_stdin_alone(self):
        with tempfile.TemporaryFile() as sink:
            process = SimpleNamespace(stdin=sink)
            process_group._finish_writer(process, None, False)
            self.assertFalse(sink.closed)

    def test_an_unstarted_writer_closes_the_child_stdin_without_a_join(self):
        read_fd, write_fd = os.pipe()
        with os.fdopen(read_fd, "rb") as source, os.fdopen(write_fd, "wb") as sink:
            process = SimpleNamespace(stdin=sink)
            writer = threading.Thread()
            process_group._finish_writer(process, writer, False)
            self.assertTrue(sink.closed)
            os.set_blocking(source.fileno(), False)
            self.assertEqual(b"", source.read(1))

    def test_an_error_closing_an_unstarted_writers_stdin_is_swallowed(self):
        process = mock.Mock()
        process.stdin.close.side_effect = BrokenPipeError
        writer = mock.Mock()
        process_group._finish_writer(process, writer, False)
        process.stdin.close.assert_called_once_with()
        writer.join.assert_not_called()

    def test_a_started_writer_is_joined_within_the_reap_timeout(self):
        process = mock.Mock()
        writer = mock.Mock()
        process_group._finish_writer(process, writer, True)
        writer.join.assert_called_once_with(process_group._REAP_TIMEOUT)
        process.stdin.close.assert_not_called()


    def test_cleanup_returns_while_a_started_writer_is_still_blocked(self):
        release = threading.Event()
        writer = threading.Thread(target=release.wait, daemon=True)
        # Release even if cleanup regresses to an unbounded join, so the test
        # fails without leaving a stuck test process or worker thread.
        watchdog = threading.Timer(2, release.set)
        writer.start()
        watchdog.start()
        try:
            with tempfile.TemporaryFile() as sink:
                process = SimpleNamespace(stdin=sink)
                with mock.patch.object(process_group, "_REAP_TIMEOUT", 0.01):
                    process_group._finish_writer(process, writer, True)
                self.assertTrue(writer.is_alive())
                self.assertFalse(sink.closed)
        finally:
            release.set()
            watchdog.cancel()
            watchdog.join()
            writer.join(2)


if __name__ == "__main__":
    unittest.main()
