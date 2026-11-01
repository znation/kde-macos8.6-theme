"""Fixtures for holding a directory flock during serialization tests.

The GTK, cursor and theme apply-lock suites use this to model an install or
uninstall that already holds the data-home lock.
"""

import fcntl
import os


def hold_directory_flock(case, directory):
    """Take an exclusive non-blocking flock on *directory* until cleanup."""
    descriptor = os.open(directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    case.addCleanup(os.close, descriptor)
