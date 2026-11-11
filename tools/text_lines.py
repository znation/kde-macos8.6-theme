"""Shared handling for the newline forms and BOM a text file may carry."""

from __future__ import annotations

import re

# One UTF-8 BOM. Some editors prepend it to a text file's first line, where
# it would hide a first-line marker or a leading ``[Section]``; readers here
# strip it before matching. Defined once because every reader must name the
# same byte.
BOM = "\ufeff"

_LINE_BREAK = re.compile(r"\r\n|\r|\n")


def split_lines(text: str) -> list[str]:
    """Split on LF, CRLF, or bare CR without splitting other Unicode separators."""
    return _LINE_BREAK.split(text)


def first_line(text: str) -> str:
    """Return the first LF/CRLF/CR-delimited line, without its ending."""
    return split_lines(text)[0]


def strip_bom(text: str) -> str:
    """Return *text* without its leading UTF-8 BOM, if it has one."""
    return text[len(BOM) :] if text.startswith(BOM) else text


def has_first_line_marker(text: str, marker: str) -> bool:
    """Return whether the first line equals *marker*, allowing one BOM."""
    return first_line(text).removeprefix(BOM) == marker
