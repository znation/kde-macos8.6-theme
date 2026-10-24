"""Failure injection for tests that make one path's ``Path.unlink`` fail.

The GTK staging and apply suites each fail the unlink of a single CSS file
while every other unlink still succeeds::

    with unlink_failing_for(css):
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
