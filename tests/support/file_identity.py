"""The stat identity that test-side unchanged-file caches key on.

Two caches reuse a parsed result while the file it came from is unchanged:
the SVG tree cache in :mod:`support.svg_case` and the Xcursor parse cache in
:mod:`support.xcursor`. Both fall back to a fresh read when the file cannot be
statted, so this module holds that one identity rule instead of a copy in each
cache.
"""

from __future__ import annotations

import os


def fingerprint_or_none(path):
    """Return *path*'s stat fingerprint, or None when it cannot be read.

    The tuple is ``(st_ino, st_size, st_mtime_ns, st_ctime_ns)``. A failed stat
    is not cached, so the caller's read still reports the missing or unreadable
    path the way it did before. ``tests/support/invariants.py`` keeps its own
    fingerprint that lets ``os.stat`` raise: its register checker reports a
    missing module rather than re-reading it, so it is not this helper's
    caller.
    """
    try:
        stat = os.stat(path)
    except OSError:
        return None
    return (stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
