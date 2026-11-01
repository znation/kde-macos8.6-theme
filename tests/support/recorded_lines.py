"""Read the lines a shell stub appended to a log file."""

from __future__ import annotations

from pathlib import Path


def recorded_lines(log: Path) -> list[str]:
    """Return the lines in *log*, or ``[]`` when no stub has written it yet."""
    try:
        contents = log.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    return contents.splitlines()
