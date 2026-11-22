"""The minimal installed cursor theme that the apply-cursor suites stage.

``tools.cursor.link.require_installed`` accepts a theme only when both
``index.theme`` and ``cursors/left_ptr`` exist, so every suite that needs a
working installed theme writes exactly these two files::

    write_cursor_theme(installed)   # installed = data_home/icons/<theme>
"""

from __future__ import annotations

from pathlib import Path


def write_cursor_theme(installed: Path) -> Path:
    """Write ``index.theme`` and ``cursors/left_ptr`` under *installed*.

    Existing directories are kept, so a caller may stage over a partly
    prepared tree. Returns *installed* for convenience.
    """
    (installed / "cursors").mkdir(parents=True, exist_ok=True)
    (installed / "index.theme").write_text(
        "[Icon Theme]\nName=Mac OS 8.6\n", encoding="utf-8"
    )
    (installed / "cursors" / "left_ptr").write_bytes(b"cursor\n")
    return installed
