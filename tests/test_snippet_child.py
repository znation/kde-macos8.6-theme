"""Tests for `support.snippet_child`: the cheap child process the guards use.

The FIFO guards run a reader in a child process so a reader that blocks on a
pipe cannot stall `make check`. `snippet_child.run` keeps that guarantee --
a separate process, a captured stdout and stderr and a bounded timeout -- while
forking instead of starting a fresh interpreter, so the snippet does not
re-import the module under test.
"""

from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import process_runner, snippet_child


def _block_buffer(stream):
    """Make *stream* hold what it is given instead of writing it at once.

    Returns the original line-buffering setting, or None when the stream
    cannot be reconfigured (a redirected stream, say).
    """
    if not hasattr(stream, "reconfigure"):
        return None
    original = stream.line_buffering
    stream.reconfigure(line_buffering=False)
    return original


def _restore_buffering(stream, original):
    """Undo `_block_buffer`, restoring *stream*'s line-buffering setting."""
    if original is None:
        return
    stream.reconfigure(line_buffering=original)


class TestSnippetChild(unittest.TestCase):
    def test_a_snippet_that_succeeds_reports_zero_and_its_stdout(self):
        child = snippet_child.run(["print('hello')"])
        self.assertEqual(0, child.returncode)
        self.assertEqual("hello\n", child.stdout)
        self.assertEqual("", child.stderr)

    def test_a_snippet_that_raises_reports_one_and_its_traceback(self):
        child = snippet_child.run(["raise ValueError('boom')"])
        self.assertEqual(1, child.returncode)
        self.assertIn("ValueError: boom", child.stderr)
        self.assertIn("Traceback", child.stderr)

    def test_a_snippet_that_exits_reports_that_status(self):
        child = snippet_child.run(["import sys; sys.exit(3)"])
        self.assertEqual(3, child.returncode)

    def test_the_snippet_reads_its_arguments_from_sys_argv(self):
        child = snippet_child.run(["import sys; print(sys.argv)", "one", "two"])
        self.assertEqual(0, child.returncode)
        self.assertEqual("['-c', 'one', 'two']\n", child.stdout)

    def test_the_snippet_runs_in_the_given_working_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            child = snippet_child.run(
                ["import os; print(os.getcwd())"], cwd=tmp
            )
            self.assertEqual(0, child.returncode)
            self.assertEqual(
                os.path.realpath(tmp),
                os.path.realpath(child.stdout.strip()),
            )

    def test_the_snippet_finds_a_module_next_to_the_working_directory(self):
        # `python -c` puts the working directory first on sys.path; a module
        # there is importable, which is how the guards reach the module they
        # exercise.
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "snippet_probe_module.py").write_text(
                "VALUE = 'found'\n", encoding="utf-8"
            )
            child = snippet_child.run(
                [
                    "import snippet_probe_module; "
                    "print(snippet_probe_module.VALUE)"
                ],
                cwd=tmp,
            )
        self.assertEqual(0, child.returncode, child.stderr)
        self.assertEqual("found\n", child.stdout)

    def test_a_snippet_that_outlives_the_timeout_is_killed(self):
        start = time.monotonic()
        with self.assertRaises(subprocess.TimeoutExpired):
            snippet_child.run(["import time; time.sleep(30)"], timeout=0.5)
        self.assertLess(time.monotonic() - start, 20)

    def test_the_child_does_not_capture_the_parents_output(self):
        # The parent's own stdout is not the child's: a snippet that prints
        # must not take the suite's output with it, and the parent's pending
        # output must not be duplicated into the captured streams.
        child = snippet_child.run(["print('child only')"])
        self.assertEqual("child only\n", child.stdout)
        self.assertEqual("", child.stderr)

    def test_the_command_recorded_is_the_snippet_it_ran(self):
        child = snippet_child.run(["pass", "arg"])
        self.assertEqual(
            [sys.executable, "-c", "pass", "arg"], list(child.args)
        )


class TestParentsOutput(unittest.TestCase):
    """The parent's own pending output is written once, by the parent."""

    def test_the_parents_pending_output_is_written_once(self):
        # The parent writes to its own stdout and leaves the bytes in the
        # buffer. The child must not write them again: the child inherits a
        # copy of the buffer, and flushing it there would put the parent's
        # bytes on the real stdout, which the parent would then write a
        # second time when it flushed its own copy.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stdout.txt"
            with path.open("wb") as handle:
                saved = os.dup(1)
                buffering = None
                try:
                    sys.stdout.flush()
                    os.dup2(handle.fileno(), 1)
                    buffering = _block_buffer(sys.stdout)
                    sys.stdout.write("parent-only\n")
                    child = snippet_child.run(["print('child only')"])
                finally:
                    sys.stdout.flush()
                    os.dup2(saved, 1)
                    os.close(saved)
                    _restore_buffering(sys.stdout, buffering)
            written = path.read_text(encoding="utf-8")
        self.assertEqual("child only\n", child.stdout)
        self.assertEqual("", child.stderr)
        self.assertEqual(1, written.count("parent-only"))


class TestTimeoutPath(unittest.TestCase):
    """The timeout path acts only on a child that is still running."""

    def test_a_child_that_has_exited_is_not_signalled(self):
        # The snippet exits at once but leaves a writer holding the pipe
        # open, so the parent's wait outlives the timeout. The child has
        # been reaped by then, and a signal sent to a reaped pid would
        # target whatever process owns that number now.
        code = (
            "import os, sys, time\n"
            "if os.fork() == 0:\n"
            "    time.sleep(2)\n"
            "    os._exit(0)\n"
            "sys.exit(0)\n"
        )
        signalled = []

        def record(pid, sig):
            signalled.append((pid, sig))

        with mock.patch.object(snippet_child.os, "kill", record):
            child = snippet_child.run([code], timeout=0.5)
        self.assertEqual([], signalled)
        self.assertEqual(0, child.returncode)

    def test_the_reap_after_the_kill_is_bounded(self):
        # A child the kernel does not release must not stall the suite from
        # the cleanup path, so the reap that follows the kill waits with a
        # bound and reports the stuck child on stderr.
        real_waitpid = os.waitpid
        waited = []

        def never_released(pid, options):
            waited.append(pid)
            if options == 0:
                # The unbounded wait the bound removes.
                time.sleep(6)
            return (0, 0)

        stderr = io.StringIO()
        with mock.patch.object(snippet_child.os, "waitpid", never_released):
            with mock.patch.object(process_runner, "REAP_TIMEOUT", 0.2):
                with contextlib.redirect_stderr(stderr):
                    start = time.monotonic()
                    with self.assertRaises(subprocess.TimeoutExpired):
                        snippet_child.run(
                            ["import time; time.sleep(30)"], timeout=0.2
                        )
                    elapsed = time.monotonic() - start
        for pid in waited:
            try:
                real_waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                pass
        self.assertLess(elapsed, 5)
        self.assertIn("was not released", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
