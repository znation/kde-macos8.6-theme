"""Read the lines a shell stub appended to a log file."""

from __future__ import annotations

from pathlib import Path


def recorded_lines(log: Path) -> list[str]:
    """Return the lines in *log*, or ``[]`` when no stub has written it yet."""
    if not log.exists():
        return []
    return log.read_text(encoding="utf-8").splitlines()
