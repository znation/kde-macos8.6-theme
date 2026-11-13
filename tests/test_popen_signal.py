"""Tests for tests/support/popen_signal.py -- the shared Popen race helpers.

The suites that share these helpers (``test_process_group`` and
``test_check_parallel_workers``) drive ``signal_into_popen`` through both its
tracked and untracked paths, but call ``kill_tracked`` only as an unasserted
cleanup and ask ``gone`` only about pids that were already reaped: nothing
failed when the cleanup stopped killing, and the timeout path was never
reached. This module pins those behaviours: the cleanup really SIGKILLs the
recorded child, tolerates an empty tracking mapping and a child that already
exited, and ``gone`` reports False while the child lives and True once the
pid is reaped.
"""

from __future__ import annotations

import signal
import subprocess
import sys
import unittest
from unittest import mock

from support import popen_signal
from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.popen_signal import GONE_TIMEOUT
from support.popen_signal import gone  # noqa: E402
from support.popen_signal import kill_tracked  # noqa: E402


def start_sleeper(case):
    """Start a child that sleeps, with cleanups that stop it if a test fails."""
    # Cleanups run last-added-first: kill first, then reap without a
    # timeout, so a failure never waits on the live sleeper.
    sleeper = subprocess.Popen(["/bin/sleep", "30"])
    case.addCleanup(sleeper.wait)
    case.addCleanup(sleeper.kill)
    return sleeper


class TestKillTracked(unittest.TestCase):
    def test_kills_the_recorded_child(self):
        # The process-group suites rely on this cleanup so a regression does
        # not leave the raced child running; a cleanup that killed nothing
        # would leak the sleeper and still pass every suite. The reaped exit
        # status is the direct evidence the signal was SIGKILL, not a milder
        # one the sleeper would survive or ignore.
        sleeper = start_sleeper(self)
        tracked = {"pid": sleeper.pid}
        kill_tracked(tracked)
        self.assertEqual(-signal.SIGKILL, sleeper.wait(timeout=GONE_TIMEOUT))

    def test_ignores_an_untracked_mapping(self):
        # A race whose ``Popen`` never returned records no pid, so the cleanup
        # must treat a pid-less mapping as nothing to do instead of raising.
        self.assertIsNone(kill_tracked({}))

    def test_tolerates_a_child_that_already_exited(self):
        # The cleanup runs after a test whose child raced itself to death, so
        # killing an already-exited pid must be swallowed, not raise. The
        # child's own exit status stays untouched.
        child = subprocess.Popen([sys.executable, "-c", "pass"])
        self.assertEqual(0, child.wait(timeout=GONE_TIMEOUT))
        kill_tracked({"pid": child.pid})
        self.assertEqual(0, child.returncode)


class TestGone(unittest.TestCase):
    def test_reports_true_once_the_pid_is_reaped(self):
        # The suites use this to prove a raced child died; pin the reaped-pid
        # answer they rely on. The exit is immediate, so the poll returns on
        # its first ProcessLookupError, not near the deadline.
        child = subprocess.Popen([sys.executable, "-c", "pass"])
        self.assertEqual(0, child.wait(timeout=GONE_TIMEOUT))
        self.assertTrue(gone(child.pid))

    def test_reports_false_while_the_child_lives(self):
        # The deadline is a module constant so this path is testable without
        # a five-second wait: a live child keeps the poll answering until the
        # shortened deadline passes, and the answer is False, not an error.
        sleeper = start_sleeper(self)
        with mock.patch.object(popen_signal, "GONE_TIMEOUT", 0.2):
            self.assertFalse(gone(sleeper.pid))


if __name__ == "__main__":
    unittest.main()
