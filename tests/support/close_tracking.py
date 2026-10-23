"""Close-tracking patches for tests that pin descriptor cleanup.

An atomic writer opens a temporary file with ``os.open`` and must close the raw
descriptor when a later step fails -- wrapping it with ``os.fdopen``, changing
its mode, or before either; the PNG loader must do the same when ``os.fstat``
fails. The render-output, wallpaper, local-hook, theme-defaults and png-loader
suites each pinned that with the same close-tracking patch, so this module
names it once::

    with failing_fdopen() as closed:
        with self.assertRaises(OSError):
            writer(...)
    self.assertEqual(1, len(closed))

``tracking_closes`` is the bare wrapper for tests that inject the failure
somewhere other than ``os.fdopen``.
"""

from __future__ import annotations

import contextlib
import os


@contextlib.contextmanager
def tracking_closes():
    """Yield a list that records each descriptor closed while active.

    ``os.close`` is wrapped rather than replaced outright, so the descriptors
    still really close. It is restored when the context exits, even on error.
    """
    real_close = os.close
    closed = []

    def track_close(fd):
        closed.append(fd)
        return real_close(fd)

    os.close = track_close
    try:
        yield closed
    finally:
        os.close = real_close


@contextlib.contextmanager
def failing_fdopen():
    """Make ``os.fdopen`` raise OSError, yielding the closed descriptors.

    The yielded list comes from ``tracking_closes``; ``os.fdopen`` is restored
    when the context exits, even on error.
    """
    real_fdopen = os.fdopen

    def boom(*args, **kwargs):
        raise OSError("simulated fdopen failure")

    with tracking_closes() as closed:
        os.fdopen = boom
        try:
            yield closed
        finally:
            os.fdopen = real_fdopen
