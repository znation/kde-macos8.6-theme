"""Tests for tools/file_lock.py -- the shared bounded-wait exclusive flock.

The installers' integration suites (``test_gtk_apply.py`` and
``test_firefox_install.py``) exercise the lock's refusal arms: a directory
that cannot be opened, a flock that fails for another reason, and a holder
that outlasts the timeout. They never reach the retry loop's recovery arms --
an ``EINTR`` interrupt that must be retried rather than refused, and a holder
that releases during the wait so the pending run acquires the lock after all.
These tests do, so a change to the retry rule or the release-on-raise cleanup
is caught at the shared module instead of surfacing as a flaky install.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import errno
import fcntl
import os
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from tools.file_lock import POLL_SECONDS, exclusive_flock


class LockRefused(Exception):
    """Stands in for the ConfigError classes each installer passes."""


def open_directory(directory: Path) -> int:
    """Open *directory* the way :func:`exclusive_flock` does, for holders."""
    return os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))


class TestExclusiveFlock(unittest.TestCase):
    def setUp(self):
        self.directory = tmp_dir.make_tmp_dir(self)
        self.error = LockRefused

    def acquire(self, timeout: float = 10.0) -> bool:
        """Take and release the lock; return whether the body ran."""
        with exclusive_flock(
            self.directory,
            "for the test selection",
            "another test run",
            timeout,
            error=self.error,
        ):
            return True

    def test_a_holder_releasing_during_the_wait_lets_the_run_acquire(self):
        """A holder that releases inside the bounded wait is acquired after.

        The timeout and refusal arms are pinned by the installer suites;
        this is the other half of the loop: contention that is resolved by
        the holder's release, not by giving up.
        """
        holder_ready = threading.Event()

        def hold_and_release():
            descriptor = open_directory(self.directory)
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                holder_ready.set()
                # Outlast several poll intervals, then let the waiter in.
                time.sleep(POLL_SECONDS * 4)
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            finally:
                os.close(descriptor)

        holder = threading.Thread(target=hold_and_release)
        holder.start()
        try:
            holder_ready.wait(10)
            self.assertTrue(
                self.acquire(), "the body did not run after the holder released"
            )
        finally:
            holder.join(10)

    def test_an_interrupted_flock_call_is_retried_not_refused(self):
        """One EINTR from flock ends the call, not the wait.

        ``flock`` may report EINTR when a signal arrives; the loop must
        retry, because refusing would make every installer fail on an
        ordinary signal delivery.
        """
        real_flock = fcntl.flock
        interrupted = []

        def interrupt_the_first_call(descriptor, operation):
            if not interrupted:
                interrupted.append(descriptor)
                raise OSError(errno.EINTR, "simulated interrupt")
            return real_flock(descriptor, operation)

        with mock.patch.object(
            fcntl, "flock", side_effect=interrupt_the_first_call
        ):
            self.assertTrue(self.acquire())
        self.assertEqual(1, len(interrupted))

        # A fresh call after the patch is restored proves the retry left
        # the lock in a state where the directory can be locked again.
        self.assertTrue(self.acquire())

    def test_the_lock_is_released_when_the_body_raises(self):
        """A raising body still releases the lock for the next run."""
        with self.assertRaises(RuntimeError):
            with exclusive_flock(
                self.directory,
                "for the test selection",
                "another test run",
                10.0,
                error=self.error,
            ):
                raise RuntimeError("the body failed")

        self.assertTrue(self.acquire(), "the lock was not released after the raise")


if __name__ == "__main__":
    unittest.main()
