"""Failure injection for tests that make one path's ``Path.unlink`` fail.

The GTK staging and apply, local-hook and cursor suites inject an unlink failure
for a selected path (a CSS file, hook or cursor symlink), delegating other paths
to the real ``Path.unlink``::

    with unlink_failing_for(target):
        ...
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from unittest import mock


@contextmanager
def unlink_failing_for(target: Path, message: str = "injected unlink failure"):
    """Patch ``Path.unlink`` to raise ``OSError(message)`` for *target* only."""
    real_unlink = Path.unlink

    def failing_unlink(path, *args, **kwargs):
        if path == target:
            raise OSError(message)
        return real_unlink(path, *args, **kwargs)

    with mock.patch.object(Path, "unlink", failing_unlink):
        yield
