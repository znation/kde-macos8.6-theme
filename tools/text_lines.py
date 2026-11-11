"""Shared handling for the three newline forms accepted in text files."""

from __future__ import annotations

import re

_LINE_BREAK = re.compile(r"\r\n|\r|\n")


def split_lines(text: str) -> list[str]:
    """Split on LF, CRLF, or bare CR without splitting other Unicode separators."""
    return _LINE_BREAK.split(text)


def first_line(text: str) -> str:
    """Return the first LF/CRLF/CR-delimited line, without its ending."""
    return split_lines(text)[0]


def has_first_line_marker(text: str, marker: str) -> bool:
    """Return whether the first line equals *marker*, allowing one BOM."""
    return first_line(text).removeprefix("\ufeff") == marker
