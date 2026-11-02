"""Shared handling for the three newline forms accepted in text files."""

from __future__ import annotations

import re

_LINE_BREAK = re.compile(r"\r\n|\r|\n")


def split_lines(text: str) -> list[str]:
    """Split on LF, CRLF, or bare CR without splitting other Unicode separators."""
    return _LINE_BREAK.split(text)
