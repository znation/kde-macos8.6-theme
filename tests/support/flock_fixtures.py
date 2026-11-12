"""Fixtures for holding a directory flock during serialization tests.

The GTK, cursor and theme apply-lock suites use this to model an install or
uninstall that already holds the data-home lock.
"""

import fcntl
import os


def _open_directory(directory):
    return os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))


def hold_directory_flock(case, directory):
    """Take an exclusive non-blocking flock on *directory* until cleanup."""
    descriptor = _open_directory(directory)
    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    case.addCleanup(os.close, descriptor)


def assert_directory_flock_free(directory):
    """Fail with BlockingIOError if another holder still has *directory*'s flock.

    Used after a run to show it released the lock for the next run: the
    non-blocking attempt succeeds only when nothing else holds it.
    """
    descriptor = _open_directory(directory)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    finally:
        os.close(descriptor)
