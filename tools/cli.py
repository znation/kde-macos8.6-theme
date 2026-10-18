"""Shared argument-parsing helpers for the command-line tools.

Each tool in this directory takes contributor-supplied paths and numbers on
its command line. Four concerns recur across them: argparse's own
diagnostics are formatted from raw argv and must not print control
characters, a numeric option must reject Python-only spellings (underscore
separators, non-ASCII digits, surrounding whitespace) that would silently
name a different value, a caught read/comparison failure is reported as one
escaped, tool-named line with exit status 2, and a failed external command as
that same line plus a tail of its log with exit status 1. All of these live
here so ``tools/fidelity.py``, ``tools/sample.py``, ``tools/render_surface.py``
and ``tools/apply_theme.py`` share one implementation.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

if __package__:
    from tools.terminal import escape_controls
else:  # imported from a directly run tool
    from terminal import escape_controls


class EscapingArgumentParser(argparse.ArgumentParser):
    """ArgumentParser whose error diagnostics escape control characters.

    argparse formats some of its own errors (notably ``unrecognized
    arguments: ...``) from raw argv. The documented workflow fills argv from a
    shell glob over the contributor-owned screenshot directory, so those bytes
    never pass through the tool's own escaping of its paths; escaping the
    message here closes that gap at the output boundary.
    """

    def error(self, message: str) -> None:
        super().error(escape_controls(message))


def report_error(tool: str, message: str) -> int:
    """Print ``tool: error: <escaped message>`` to stderr and return 2.

    The tools that call this report an operator-facing failure the same way:
    one control-character-escaped diagnostic line prefixed with the tool's
    name, and exit status 2. Keeping the format here means the prefix and the
    escaping cannot drift between ``tools/fidelity.py``, ``tools/sample.py``
    and ``tools/render_surface.py``. *message* is the unescaped text; a caller
    passes an exception's ``str()`` or a diagnostic it built itself.
    """
    print(f"{tool}: error: {escape_controls(message)}", file=sys.stderr)
    return 2


_LOG_TAIL_LINES = 12


def report_failure(tool: str, message: str, log: Path | None = None) -> int:
    """Print ``tool: error: <escaped message>`` and a log tail; return 1.

    A tool whose external command failed reports it the same way: one
    control-character-escaped diagnostic line prefixed with the tool's name,
    the last ``_LOG_TAIL_LINES`` lines of the command's log (each escaped and
    indented) when *log* names a file, and exit status 1. *message* is the
    unescaped text. ``tools/apply_theme.py`` and ``tools/render_surface.py``
    both return this result directly as the process exit status.
    """
    text = f"{tool}: error: {escape_controls(message)}"
    if log is not None and log.is_file():
        tail = log.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in tail[-_LOG_TAIL_LINES:]:
            text += f"\n  {escape_controls(line)}"
    print(text, file=sys.stderr)
    return 1


def is_plain_ascii_number(value: str) -> bool:
    """Return True when *value* is ASCII numeric text with no Python extras.

    ``int()``/``float()`` accept forms a command-line number should not:
    underscore digit separators (``1_0`` is 10), non-ASCII decimal digits
    (``\u0661\u0662`` is 12), and surrounding whitespace. Each silently turns
    a stray character into a different value, so a CLI checks the text before
    parsing it. Callers that parse a structured value (the crop rectangle)
    strip each field first, so this whitespace rule applies to the scalar
    options.
    """
    return value.isascii() and "_" not in value and value == value.strip()


_Number = TypeVar("_Number", int, float)


def plain_number(
    value: str,
    option: str,
    noun: str,
    article: str,
    parse: Callable[[str], _Number],
) -> _Number:
    """Return ``parse(value)``, rejecting Python-only numeric text.

    ``int()``/``float()`` accept forms a command-line number should not --
    underscore digit separators, non-ASCII decimal digits and surrounding
    whitespace -- so the text is checked before parsing. *noun* names the
    value in the diagnostics ("number" for a float option, "integer" for an
    int one) and *article* is its indefinite article ("a" or "an"); *parse*
    is the stdlib constructor whose ``ValueError`` becomes the option-named
    rejection.
    """
    if not is_plain_ascii_number(value):
        raise argparse.ArgumentTypeError(
            f"{option} must be a plain ASCII {noun}: {value!r}"
        )
    try:
        return parse(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"{option} must be {article} {noun}: {value!r}"
        ) from exc
