"""Tests for tools/file_lock.py -- the shared bounded-wait exclusive flock.

The installers' integration suites (``test_apply_gtk_locks.py`` and
``test_install_firefox.py``) exercise the lock's refusal arms: a directory
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
from support.flock_fixtures import assert_directory_flock_free, hold_directory_flock
from tools.file_lock import (
    POLL_SECONDS,
    exclusive_flock,
    installed_data_lock,
    parent_dir_lock,
)


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

    def test_repeated_interruptions_still_honor_the_deadline(self):
        with (
            mock.patch("tools.file_lock.time.monotonic", side_effect=[0, 1, 2]),
            mock.patch.object(
                fcntl, "flock",
                side_effect=[
                    OSError(errno.EINTR, "first interrupt"),
                    OSError(errno.EINTR, "second interrupt"),
                    AssertionError("retried after the deadline"),
                ],
            ) as flock,
            mock.patch("tools.file_lock.time.sleep") as sleep,
            mock.patch("tools.file_lock.os.close", wraps=os.close) as close,
        ):
            with self.assertRaisesRegex(
                LockRefused, "gave up after 2s waiting for another test run"
            ):
                self.acquire(timeout=2)
            self.assertEqual(flock.call_count, 2)
            sleep.assert_not_called()
            close.assert_called_once_with(flock.call_args.args[0])
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


class TestParentDirLock(unittest.TestCase):
    def setUp(self):
        self.child = tmp_dir.make_tmp_dir(self) / "missing" / "cfg-home"

    def acquire(self) -> bool:
        """Purchase and release the parent lock; return whether the body ran."""
        with exclusive_flock(
            self.child.parent,
            "for the test selection",
            "another test run",
            10.0,
            error=LockRefused,
        ):
            return True

    def test_the_parent_is_created_locked_and_left_for_the_child(self):
        """The parent is created and held while the child stays untouched."""
        with parent_dir_lock(
            self.child,
            "for the test selection",
            "another test run",
            10.0,
            error=LockRefused,
        ):
            lock_dir = self.child.parent
            self.assertTrue(lock_dir.is_dir())
            # The helper already holds the parent: opening is not exclusive,
            # so contention is the observable difference.
            holder = open_directory(lock_dir)
            self._assert_second_selection_refused(lock_dir, holder)
            self.assertFalse(
                self.child.exists(), "the helper created the child itself"
            )

        self.assertTrue(self.acquire(), "the lock was not released after the body")

    def _assert_second_selection_refused(self, lock_dir, holder):
        """Pin a contending exclusive selection refused, then close *holder*."""
        try:
            with self.assertRaises(LockRefused):
                with exclusive_flock(
                    lock_dir,
                    "for the second selection",
                    "the body above",
                    0.0,
                    error=LockRefused,
                ):
                    pass
        finally:
            os.close(holder)

    def test_an_uncreatable_parent_is_refused_with_the_helper_error(self):
        """A parent that cannot be created raises *error* naming the directory."""
        blocked = self.child.parent  # an absent-but-named lock directory
        blocked.write_text(
            "refuse\n"
        )  # a file, so a directory cannot be created in its place
        self.addCleanup(blocked.unlink)
        with self.assertRaises(LockRefused) as caught:
            with parent_dir_lock(
                self.child,
                "for the test selection",
                "another test run",
                10.0,
                error=LockRefused,
            ):
                pass
        self.assertIn(f"cannot create {blocked}", str(caught.exception))


class TestInstalledDataLock(unittest.TestCase):
    """The data-home wrapper the Makefile's ``flock "$(DATA_HOME)"`` pairs with.

    ``make install``/``uninstall`` run their whole recipe under an exclusive
    flock over the data home (``run_locked`` in the Makefile), and the apply
    and selection tools re-check their installed files while this wrapper
    holds the same inode. The wording of *holder* is the tool-side half of
    the pairing: it must name install/uninstall, the way the Makefile's own
    timeout diagnostic names ``another install or uninstall``.
    """

    def setUp(self):
        self.data_home = tmp_dir.make_tmp_dir(self)

    def test_an_install_or_uninstall_holder_is_named_in_the_refusal(self):
        """A holder on the data home refuses the wrapper, naming the holder.

        Contention is against the data home's own inode -- the one
        ``flock "$(DATA_HOME)"`` takes -- not the parent directory, so a
        swap of either argument would let an apply run overlap an uninstall.
        """
        hold_directory_flock(self, self.data_home)
        with self.assertRaisesRegex(
            LockRefused,
            r"gave up after 0s waiting for another install or uninstall to"
            r" finish with " + str(self.data_home),
        ):
            with installed_data_lock(
                self.data_home,
                "for the theme apply",
                0.0,
                error=LockRefused,
            ):
                pass

    def test_the_body_holds_the_data_home_inode_and_releases_it_afterward(self):
        """The body runs under the lock, blocks a fresh holder, then releases.

        The reverse direction of the pairing: while the wrapper holds the
        data home, an install or uninstall contending the way the Makefile
        does (a non-blocking flock on the directory) is refused, and once
        the body ends the directory is lockable again.
        """
        body_ran = False
        with installed_data_lock(
            self.data_home,
            "for the theme apply",
            10.0,
            error=LockRefused,
        ):
            body_ran = True
            holder = open_directory(self.data_home)
            try:
                with self.assertRaises(OSError):
                    fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
            finally:
                os.close(holder)
        self.assertTrue(body_ran, "the wrapper did not run its body")
        assert_directory_flock_free(self.data_home)

    def test_a_missing_data_home_is_refused_not_created(self):
        """A data home that does not exist yet raises *error*, not a mkdir.

        The Makefile creates the data home before taking the lock and the
        apply tools check their installed files before locking, so the
        wrapper locking a directory it just created would serialize nothing
        and leave a stray ``.local/share`` behind.
        """
        missing = self.data_home / "absent" / "share"
        with self.assertRaisesRegex(
            LockRefused,
            "cannot lock " + str(missing) + " for the theme apply",
        ):
            with installed_data_lock(
                missing,
                "for the theme apply",
                10.0,
                error=LockRefused,
            ):
                pass
        self.assertFalse(missing.exists(), "the wrapper created the data home")


if __name__ == "__main__":
    unittest.main()
