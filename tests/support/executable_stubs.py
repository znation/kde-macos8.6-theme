"""Write executable fake tools for tests that put stubs on PATH."""

from __future__ import annotations

from pathlib import Path


def write_executable(path, text):
    """Write *text* verbatim to *path*, mark it 0755, and return the path.

    *text* keeps its own ``#!`` line, so a stub can be a shell script or
    any other interpreter the test needs.
    """
    path = Path(path)
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)
    return path
