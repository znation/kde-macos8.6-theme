"""Failure injection for tests that pin ``tools/atomic_write.py`` crash safety.

The local-hook and wallpaper suites each simulate a process death part-way
through a temporary file's write and a symlink swap after ``mkstemp``'s
exclusive create. Both suites inject the same wrappers, so this module names
them once::

    with mock.patch.object(os, "fdopen", crashing_fdopen(OSError("..."))):
        ...
    with mock.patch.object(tempfile, "mkstemp", swapping_mkstemp(victim)):
        ...
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def crashing_fdopen(error: OSError):
    """Return an ``os.fdopen`` replacement that dies part-way through a write.

    The returned file object delegates to the real one but writes only the
    first half of each payload and then raises *error*, leaving a truncated
    temporary file as a process death would.
    """
    real_fdopen = os.fdopen

    def fdopen(descriptor, *args, **kwargs):
        handle = real_fdopen(descriptor, *args, **kwargs)

        class CrashingWriter:
            def __getattr__(self, name):
                return getattr(handle, name)

            def __enter__(self):
                return self

            def __exit__(self, *exc_info):
                handle.close()
                return False

            def write(self, data):
                handle.write(data[: len(data) // 2])
                raise error

        return CrashingWriter()

    return fdopen


def swapping_mkstemp(victim: Path):
    """Return a ``mkstemp`` replacement that swaps its file for *victim*.

    After the real ``mkstemp`` creates the temporary file, the returned
    function unlinks it and parks a symlink to *victim* at that name, so a
    writer that reopens the path by name would overwrite *victim* instead of
    the descriptor's file.
    """
    real_mkstemp = tempfile.mkstemp

    def mkstemp(*args, **kwargs):
        descriptor, name = real_mkstemp(*args, **kwargs)
        os.unlink(name)
        os.symlink(victim, name)
        return descriptor, name

    return mkstemp
