"""Fixtures for holding a directory flock during serialization tests.

The GTK, cursor and theme apply-lock suites use this to model an install or
uninstall that already holds the data-home lock, and the lock-time-out suites
call :func:`assert_run_lock_time_out` to run their tool against a held lock.
"""

import fcntl
import os
from unittest import mock

from support.process_assertions import assert_lock_time_out

# The fast lock ceiling every lock-time-out test patches a tool module's
# LOCK_TIMEOUT to, so a held flock makes the run give up in a fraction of a
# second instead of waiting out the production timeout.
LOCK_TIME_OUT_TEST_SECONDS = 0.05


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


def assert_run_lock_time_out(case, module, run, message, path):
    """Run *run* with *module*'s ``LOCK_TIMEOUT`` patched short; assert refusal.

    A lock-time-out test holds a directory flock with
    :func:`hold_directory_flock`, runs the tool while the tool module's
    ``LOCK_TIMEOUT`` is patched to :data:`LOCK_TIME_OUT_TEST_SECONDS`, and
    asserts the shared bounded-wait refusal: exit 2 with no traceback, the
    holder diagnostic *message* and the locked *path* on stderr. This helper
    does those three steps once, so no suite repeats the three-part
    assertion. Its call sites are the lock-time-out suites
    ``tests/test_apply_gtk_locks.py``, ``tests/test_apply_theme_locks.py``,
    ``tests/test_apply_cursor_locks.py``,
    ``tests/test_install_firefox_lock.py`` and ``tests/test_remove_kvantum.py``.
    """
    with mock.patch.object(module, "LOCK_TIMEOUT", LOCK_TIME_OUT_TEST_SECONDS):
        result = run()
    assert_lock_time_out(case, result, message, path)
