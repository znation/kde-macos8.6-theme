"""Tests for the subprocess timeout runner's reap bound.

These pin the reap bound on `process_runner.running`'s cleanup and on
`process_runner.finish`'s second pipe wait. They use `Popen` stand-ins, so no
real child is started. The live-child timeout, group-kill and other `running`
tests stay in `tests/test_process_runner.py`.
"""

import contextlib
import io
import subprocess
import unittest
import unittest.mock

from support import process_runner


class _UnreapableProcess:
    """A `Popen` stand-in for a child the kernel never releases.

    A child stuck in uninterruptible I/O ignores SIGKILL until the kernel lets
    go, so a wait on it never returns. The stand-in reports every wait as
    timed out and records the bound it was given, so a test can see whether the
    cleanup bounded that wait.

    Its `pid` is -1, which no process can have: if the group kill were ever to
    reach the real `_kill_process_group`, `os.getpgid` would fail with ESRCH
    and the stand-in's own `kill` would raise instead of signalling anything.
    """

    def __init__(self):
        self.pid = -1
        self.args = ["fake-child"]
        self.returncode = None
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.wait_timeouts = []

    def poll(self):
        return None

    def wait(self, timeout=None):
        self.wait_timeouts.append(timeout)
        raise subprocess.TimeoutExpired(self.args, timeout or 0)

    def kill(self):
        raise AssertionError("the stand-in was asked to kill a process")


class _TimedOutCommunicate:
    """A `Popen` stand-in whose pipes time out and then reach EOF.

    `finish` kills a child that outlives its timeout and waits for the pipes
    a second time. A descendant that escaped the process group holds the
    write ends, so that second wait can time out too; this stand-in raises
    on the first `communicate`, returns captured output on the second, and
    records every bound it was handed, so a test can see whether `finish`
    bounded the second wait. Its `pid` is -1, which no process can have: if
    the group kill were ever to reach the real `_kill_process_group`,
    `os.getpgid` would fail with ESRCH and the stand-in's own `kill` would
    raise instead of signalling anything.
    """

    def __init__(self):
        self.pid = -1
        self.args = ["fake-child"]
        self.communicate_bounds = []

    def communicate(self, timeout=None):
        self.communicate_bounds.append(timeout)
        if len(self.communicate_bounds) == 1:
            raise subprocess.TimeoutExpired(self.args, timeout or 0)
        return (b"out", b"err")

    def kill(self):
        raise AssertionError("the stand-in was asked to kill a process")


class TestReapBounds(unittest.TestCase):
    def test_running_bounds_the_reap_of_a_child_the_kernel_does_not_release(self):
        """The cleanup's reap must be bounded and must not replace the error.

        `running` kills the child's process group on the way out and then waits
        for the child to be released. A child stuck in uninterruptible I/O is
        not released until the kernel lets go, which may be never, so an
        unbounded wait there stalls `make check` with no diagnostic -- on the
        cleanup path of a test that was already failing. The wait must be
        bounded, and a reap that still times out must not be raised out of the
        `finally`: that would replace the exception the block was unwinding
        with a cleanup timeout and hide the real failure.
        """
        unreapable = _UnreapableProcess()
        stderr = io.StringIO()
        with unittest.mock.patch.object(
            process_runner, "start", return_value=unreapable
        ), unittest.mock.patch.object(
            process_runner, "_kill_process_group"
        ) as kill, contextlib.redirect_stderr(stderr):
            with self.assertRaises(RuntimeError):
                with process_runner.running(["fake-child"]):
                    raise RuntimeError("poll failed")
        kill.assert_called_once_with(unreapable)
        self.assertEqual(
            unreapable.wait_timeouts,
            [process_runner.REAP_TIMEOUT],
            "the cleanup's reap wait was not bounded",
        )
        self.assertIn("not released", stderr.getvalue())

    def test_finish_bounds_the_second_pipe_wait_by_the_reap_timeout(self):
        """`finish`'s second pipe wait must use the reap bound, not the budget.

        A child that outlives its timeout is SIGKILLed with its group before
        `finish` waits for the pipes a second time. Normally the killed child
        closes its pipes and the second wait reaches EOF at once, but a
        descendant that escaped the group still holds the write ends, and
        waiting for the caller's whole budget again would double the
        worst-case stall: a 60s SUBPROCESS_TIMEOUT would cost 120s. The
        second wait must be bounded by the reap bound -- or by the caller's
        budget when that is smaller -- with the caller's budget still reported
        to the test and whatever the bounded wait captured handed over as
        the exception's output.
        """
        fake = _TimedOutCommunicate()
        with unittest.mock.patch.object(
            process_runner, "_kill_process_group"
        ) as kill:
            with self.assertRaises(subprocess.TimeoutExpired) as caught:
                process_runner.finish(fake, timeout=60.0)
        kill.assert_called_once_with(fake)
        self.assertEqual(
            fake.communicate_bounds,
            [60.0, process_runner.REAP_TIMEOUT],
            "the second pipe wait did not use the reap bound",
        )
        self.assertEqual(caught.exception.output, b"out")
        self.assertEqual(caught.exception.stderr, b"err")

        smaller = _TimedOutCommunicate()
        with unittest.mock.patch.object(process_runner, "_kill_process_group"):
            with self.assertRaises(subprocess.TimeoutExpired):
                process_runner.finish(smaller, timeout=2.0)
        self.assertEqual(
            smaller.communicate_bounds,
            [2.0, 2.0],
            "a smaller caller budget was not kept as the bound",
        )


if __name__ == "__main__":
    unittest.main()
