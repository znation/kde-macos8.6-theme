"""Tests for the suite's subprocess timeout runner.

`process_runner.run` is the suite's timeout runner: the tests route their
`make` / `plasma-apply-*` / `kpackagetool6` calls through it, so a fake `make`
that never exits raises `subprocess.TimeoutExpired` instead of stalling `make
check` forever. (One lock test starts `make install` itself to poll it, then
finishes it through `process_runner.running`, which kills the child if the poll
raises.) The install-timeout test drives a real `make install` through
`theme_install`, and the grandchild test starts the fake make through
`process_runner.running` so its setup can finish before the timeout; both prove
the runner against the child chain it protects.
"""

import contextlib
import io
import os
import signal
import subprocess
import sys
import time
import unittest
import unittest.mock
from pathlib import Path

from support import process_runner
from support import theme_install
from support.tmp_dir import make_tmp_dir


def _process_alive(pid):
    """Return True while a process with *pid* still exists."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


@contextlib.contextmanager
def _short_subprocess_timeout(seconds=0.25):
    """Temporarily shorten `process_runner.SUBPROCESS_TIMEOUT` for one block.

    Each timeout test cuts the suite's 60-second budget to a fraction of a
    second; the global must be restored even when the body raises, or every
    later subprocess call in the suite would time out. The default is ample
    for the tests whose child is a `sleep` that cannot exit on its own -- they
    only need it still running when the timeout fires -- and one of them times
    out twice (`finish` waits again for the escaped descendant's pipes), so
    the default bounds the whole class to about a second and a half. The
    grandchild test passes a longer *seconds* so the group kill's second wait
    has room on a loaded host; its setup finishes before that timeout starts.
    """
    original = process_runner.SUBPROCESS_TIMEOUT
    process_runner.SUBPROCESS_TIMEOUT = seconds
    try:
        yield
    finally:
        process_runner.SUBPROCESS_TIMEOUT = original


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


class _StillRunning:
    """A `Popen` stand-in whose child has not exited while the pidfile is read."""

    def poll(self):
        return None


class _AlreadyExited:
    """A `Popen` stand-in that exited before it started its child."""

    def poll(self):
        return 3


class TestWaitForPidfile(unittest.TestCase):
    def test_returns_the_pid_a_running_child_wrote(self):
        root = Path(make_tmp_dir(self))
        pidfile = root / "pid"
        pidfile.write_text("1234\n", encoding="utf-8")
        self.assertEqual(
            1234,
            process_runner.wait_for_pidfile(
                self, _StillRunning(), pidfile, tool="tool", child="child"
            ),
        )

    def test_fails_when_the_tool_exits_before_its_child_starts(self):
        root = Path(make_tmp_dir(self))
        with self.assertRaises(AssertionError) as caught:
            process_runner.wait_for_pidfile(
                self,
                _AlreadyExited(),
                root / "pid",
                tool="tool",
                child="child",
            )
        self.assertIn("tool exited before the child started", str(caught.exception))


class TestSubprocessTimeout(unittest.TestCase):
    def _assert_process_dies(self, pid, message):
        """Assert process *pid* is gone within a short deadline.

        A killed process can linger as a zombie until it is reaped, so poll
        briefly instead of probing once.
        """
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and _process_alive(pid):
            time.sleep(0.05)
        self.assertFalse(_process_alive(pid), message)

    def test_install_times_out_when_make_hangs(self):
        tmp = str(make_tmp_dir(self))
        env = theme_install.shadow_command_env(
            tmp, "make", "#!/bin/sh\nexec sleep 5\n"
        )
        with unittest.mock.patch.dict(os.environ, env):
            with _short_subprocess_timeout():
                with self.assertRaises(subprocess.TimeoutExpired):
                    theme_install.install(tmp)

    def test_timeout_kills_grandchildren(self):
        """A timeout must kill the whole make/flock/make chain, not just make.

        `make install` runs `flock ... make _install`, so the process the suite
        starts has descendants that survive when only the direct child is
        killed -- still running against the throwaway DESTDIR and still
        holding the data-home lock. The fake make backgrounds a long sleep and
        records its pid, so the test can tell whether that descendant outlived
        the timeout. The child is started and allowed to finish that setup --
        waiting for the pidfile to hold the written pid, not merely to exist,
        since the shell creates it before it writes -- before `finish` applies
        the timeout. The stronger check runs before the `running` context
        exits: its own cleanup would kill the group, hiding a `finish` that
        did not.
        """
        tmp = str(make_tmp_dir(self))
        pidfile = os.path.join(tmp, "grandchild.pid")
        env = theme_install.shadow_command_env(
            tmp,
            "make",
            "#!/bin/sh\n"
            "sleep 60 &\n"
            'echo "$!" > "$GRANDCHILD_PIDFILE"\n'
            "exec sleep 60\n",
        )
        env["GRANDCHILD_PIDFILE"] = pidfile
        with process_runner.running(
            [os.path.join(tmp, "fakebin", "make")], cwd=tmp, env=env
        ) as process:
            deadline = time.monotonic() + 30
            grandchild = None
            while (
                grandchild is None
                and process.poll() is None
                and time.monotonic() < deadline
            ):
                try:
                    with open(pidfile, encoding="utf-8") as handle:
                        grandchild = int(handle.read())
                except (FileNotFoundError, ValueError):
                    # The shell creates the file before it writes the pid, so
                    # an empty read is a setup race, not a failure.
                    time.sleep(0.01)
            self.assertIsNotNone(
                grandchild, "the fake make never recorded its grandchild"
            )
            with _short_subprocess_timeout(seconds=0.5):
                with self.assertRaises(subprocess.TimeoutExpired):
                    process_runner.finish(process)
            # Checked inside the block: `running` kills the group on exit, so
            # checking after it would pass even if `finish` never did.
            # The grandchild sleeps for a minute, far longer than the setup
            # deadline and the timeout, so it is still alive if the timeout
            # failed to kill it.
            self._assert_process_dies(
                grandchild, "grandchild survived the timeout"
            )

    def test_finish_kills_a_hung_child(self):
        """A caller-started child that times out must be killed, not leaked.

        `test_lookandfeel` starts `make install` itself to poll it, then waits
        with `process_runner.finish`. A child that outlives the timeout must be
        SIGKILLed with its process group, so a hung `make install` -- and its
        `flock` descendants -- cannot keep running after the test has failed.
        """
        process = process_runner.start(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            capture_output=True,
        )
        with _short_subprocess_timeout():
            with self.assertRaises(subprocess.TimeoutExpired):
                process_runner.finish(process)
        self._assert_process_dies(
            process.pid, "child survived finish()'s timeout"
        )

    def test_kill_process_group_falls_back_to_direct_kill(self):
        """A failed group lookup must still kill the direct child.

        ``_kill_process_group`` SIGKILLs the child's whole process group, but
        ``os.getpgid`` can fail -- a ``ProcessLookupError`` when the child
        exited in the race before the kill, or another ``OSError`` -- and the
        fallback then signals the child directly. Pin that the fallback really
        kills: with the group lookup forced to fail, the child must still be
        SIGKILLed rather than left running.
        """
        process = process_runner.start(
            [sys.executable, "-c", "import time; time.sleep(30)"],
        )
        try:
            with unittest.mock.patch.object(
                process_runner.os, "getpgid", side_effect=ProcessLookupError
            ):
                process_runner._kill_process_group(process)
            self.assertEqual(process.wait(), -signal.SIGKILL)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()

    def test_kill_process_group_tolerates_an_already_reaped_child(self):
        """A child that already exited is not an error to kill.

        The group lookup fails once the child is reaped, and the direct
        signal is then a no-op because ``Popen.kill`` returns early for a
        reaped process. ``_kill_process_group`` must return quietly instead of
        letting the ``OSError`` escape into the caller's cleanup.
        """
        process = process_runner.start([sys.executable, "-c", "pass"])
        process.wait()
        with unittest.mock.patch.object(
            process_runner.os, "getpgid", side_effect=ProcessLookupError
        ):
            process_runner._kill_process_group(process)

    def test_start_capture_output_pipes_the_streams(self):
        """`start` must expand `capture_output` into the two `Popen` pipes.

        `run` and `running` forward `capture_output` to `start`, so a child
        that prints on both streams must have them captured; a `start` that
        ignored the flag would inherit the suite's fds and `finish` would
        report `None` for both.
        """
        process = process_runner.start(
            [
                sys.executable,
                "-c",
                "import sys; print('out'); print('err', file=sys.stderr)",
            ],
            capture_output=True,
        )
        stdout, stderr = process_runner.finish(process)
        self.assertEqual(stdout, b"out\n")
        self.assertEqual(stderr, b"err\n")

    def _kill_escaped(self, pidfile):
        """SIGKILL the escaped grandchild whose pid *pidfile* holds, if any."""
        try:
            with open(pidfile, encoding="utf-8") as handle:
                pid = int(handle.read())
        except (OSError, ValueError):
            return
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    @unittest.skipUnless(hasattr(os, "setsid"), "needs os.setsid")
    def test_finish_reports_a_descendant_that_escaped_the_process_group(self):
        """A descendant outside the group must not make finish() block again.

        Killing the direct child's process group reaps its descendants, but a
        descendant that called setsid() has left that group and still holds
        the child's stdout/stderr pipes. communicate() then cannot reach EOF
        and times out a second time; finish must report the timeout with no
        captured output instead of blocking on the escaped descendant.
        """
        tmp = str(make_tmp_dir(self))
        pidfile = os.path.join(tmp, "escaped.pid")
        readyfile = os.path.join(tmp, "escaped.ready")
        grandchild = (
            "import os, sys, time\n"
            "os.setsid()\n"
            "open(sys.argv[1], 'w').write('ok')\n"
            "time.sleep(30)\n"
        )
        child = (
            "import subprocess, sys, time\n"
            "p = subprocess.Popen(\n"
            "    [sys.executable, '-c', sys.argv[3], sys.argv[2]])\n"
            "open(sys.argv[1], 'w').write(str(p.pid))\n"
            "time.sleep(30)\n"
        )
        process = process_runner.start(
            [sys.executable, "-c", child, pidfile, readyfile, grandchild],
            capture_output=True,
        )
        try:
            # The grandchild writes `readyfile` only after setsid(), so
            # the group kill below cannot race its escape.
            deadline = time.monotonic() + 5.0
            while (
                not os.path.exists(readyfile)
                and time.monotonic() < deadline
            ):
                time.sleep(0.01)
            self.assertTrue(
                os.path.exists(readyfile),
                "the child did not spawn an escaped grandchild",
            )
            with _short_subprocess_timeout():
                with self.assertRaises(subprocess.TimeoutExpired) as caught:
                    process_runner.finish(process)
            # The escaped-descendant path re-raises with no captured
            # output; the normal path drains the killed child's pipes and
            # includes their (empty) bytes.
            self.assertIsNone(caught.exception.output)
            self.assertIsNone(caught.exception.stderr)
        finally:
            self._kill_escaped(pidfile)
            if process.poll() is None:
                process.kill()
            process.wait()
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    stream.close()

    def test_running_kills_the_child_when_the_block_raises(self):
        """An abandoned started child must be killed, not left running.

        `test_lookandfeel` starts `make install`, polls it, and only then
        finishes it. If the poll raises -- the operator interrupts `make
        check`, or the poll itself fails -- the child and its `flock`
        descendants would keep running and holding the data-home lock after
        the test has failed. `running` kills the child's process group on the
        way out whatever happens.
        """
        with self.assertRaises(RuntimeError):
            with process_runner.running(
                [sys.executable, "-c", "import time; time.sleep(30)"],
                capture_output=True,
            ) as process:
                raise RuntimeError("poll failed")
        self.assertIsNotNone(process.poll())
        self._assert_process_dies(process.pid, "running left the child alive")

    def test_running_leaves_a_finished_child_alone(self):
        """A child the caller already finished must not be touched again.

        The lock test calls `finish` inside the `running` block, so `running`
        must see the exited child and do nothing; re-signalling or waiting on
        it would fail the normal path.
        """
        with process_runner.running(
            [sys.executable, "-c", "pass"],
            capture_output=True,
        ) as process:
            process_runner.finish(process)
        self.assertEqual(process.returncode, 0)

    def test_running_closes_the_pipes_of_an_exited_child(self):
        """A child that exits before the block does must not leak its pipes.

        `running` only has to kill a still-running child, but the caller may
        leave the block without `finish` after the child has already exited --
        an interrupt during the lock test's poll, once `make install` has
        finished, is exactly that. The child is reaped, but its stdout/stderr
        read ends stay open until the `Popen` is collected unless `running`
        closes them, so close every pipe on the way out whether or not a kill
        was needed.
        """
        with process_runner.running(
            [sys.executable, "-c", "pass"],
            capture_output=True,
        ) as process:
            deadline = time.monotonic() + 5.0
            while process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertIsNotNone(process.poll())
        self.assertTrue(process.stdout.closed, "stdout pipe leaked")
        self.assertTrue(process.stderr.closed, "stderr pipe leaked")

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
