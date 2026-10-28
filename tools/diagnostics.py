"""The operator-facing diagnostic contract shared by the command-line tools.

A tool reports a failure the same way everywhere: one control-character-escaped
``<tool>: error: <message>`` line on stderr, with exit status 2 for a usage or
input error (:func:`report_error`) and 1 for a failed external command
(:func:`report_failure`, which appends a bounded tail of the command's log). A
tool that needs external commands refuses to run when one is absent from PATH
through :func:`report_missing_tool`. A successful run with something to tell
the operator prints one ``<tool>: note: <message>`` line through
:func:`report_note`. Keeping the formats and the exit statuses here means they
cannot drift between ``tools/fidelity.py``, ``tools/sample.py``,
``tools/apply_theme.py``, ``tools/apply_gtk.py``, ``tools/local_hook.py``,
``tools/make_wallpaper.py``, ``tools/render_surface.py``,
``tools/make_cursors.py``, ``tools/install_firefox.py``,
``tools/apply_cursor.py`` and ``tools/check_references.py``.

Argument parsing lives in the sibling ``tools/argument_parsing.py``; the escaping itself in
``tools/terminal.py``.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from collections.abc import Iterable
from pathlib import Path

if __package__:
    from tools.terminal import escape_controls
else:  # imported from a directly run tool
    from terminal import escape_controls


def _require_str(helper: str, parameter: str, value: object) -> None:
    """Reject a non-str *value*, naming *helper* and *parameter* by type."""
    if not isinstance(value, str):
        raise ValueError(
            f"{helper}() requires str: {parameter} must be str, "
            f"not {type(value).__name__}"
        )


def plural(count: int, singular: str) -> str:
    """Return *singular*, pluralized with ``s`` unless *count* is one.

    Count-bearing diagnostics read as broken English when a single item is
    followed by ``(s)``; the wording lives here so the tools that print a
    count (``tools/check_references.py`` for the bare word,
    ``tools/check_parallel.py`` for the ``<count> <noun>`` phrase) cannot
    disagree about where the ``s`` goes.
    """
    _require_str("plural", "singular", singular)
    return singular if count == 1 else singular + "s"


def report_error(tool: str, message: str) -> int:
    """Print ``tool: error: <escaped message>`` to stderr and return 2.

    The tools that call this report an operator-facing failure the same way:
    one control-character-escaped diagnostic line prefixed with the tool's
    name, and exit status 2. Keeping the format here means the prefix and the
    escaping cannot drift between the tools that report through it. *message*
    is the unescaped text; a caller passes an exception's ``str()`` or a
    diagnostic it built itself.
    """
    _require_str("report_error", "tool", tool)
    _require_str("report_error", "message", message)
    print(f"{tool}: error: {escape_controls(message)}", file=sys.stderr)
    return 2


# Only CR, LF and CRLF end a log line. ``str.splitlines`` also breaks on
# U+000B, U+000C, the C0 separators, NEL and U+2028/U+2029, so a log line
# carrying one (an escaped byte, a form feed in captured output) would be
# split into two reported lines and, at the twelve-line tail boundary, push a
# complete line out of the diagnostic. ``reference_validation`` splits its
# contributor-supplied record for the same reason.
_LINE_BREAK = re.compile(r"\r\n|\r|\n")
_LOG_TAIL_LINES = 12
# The log belongs to the external command, not to us: a command that loops on
# a warning for its whole timeout can leave a file far larger than the twelve
# lines ``report_failure`` prints. Read only the end of it, so a multi-megabyte
# (or larger) log is never loaded whole just to show its tail.
_LOG_TAIL_BYTES = 1 << 16


def _log_tail_lines(log: Path) -> list[str]:
    """Return at most the last ``_LOG_TAIL_LINES`` lines of *log*, read bounded.

    At most ``_LOG_TAIL_BYTES`` bytes are read from the end of the file. A
    window that starts mid-line drops its partial first line -- unless the
    window holds no line break at all, where the single (partial) line is kept
    so the diagnostic is never empty. A window that opens on the ``\n`` half
    of a ``\r\n`` pair starts inside that one break, so its empty first line
    is the tail of the break and is dropped the same way. Only ``\r``,
    ``\n`` and ``\r\n`` end a line; an exotic break byte inside a line (a
    vertical tab, a form feed) stays part of that line.
    """
    with log.open("rb") as handle:
        size = handle.seek(0, os.SEEK_END)
        start = max(0, size - _LOG_TAIL_BYTES)
        if start:
            handle.seek(start - 1)
            previous = handle.read(1)
            first = handle.read(1)
            # ``\r\n`` is one line break: opening on its ``\n`` half is not a
            # line boundary, while a lone ``\r`` (a rewritten progress line)
            # is.
            boundary = previous == b"\n" or (
                previous == b"\r" and first != b"\n"
            )
        else:
            boundary = True
        handle.seek(start)
        data = handle.read(_LOG_TAIL_BYTES)
    lines = _LINE_BREAK.split(data.decode("utf-8", errors="replace"))
    if lines and lines[-1] == "":
        # A file that ends in a break ends its last line there; splitlines
        # omits that final empty element, so drop the one re.split adds.
        lines.pop()
    if not boundary and len(lines) > 1:
        lines = lines[1:]
    return lines[-_LOG_TAIL_LINES:]


def report_failure(tool: str, message: str, log: Path | None = None) -> int:
    """Print ``tool: error: <escaped message>`` and a log tail; return 1.

    A tool whose external command failed reports it the same way: one
    control-character-escaped diagnostic line prefixed with the tool's name,
    the last ``_LOG_TAIL_LINES`` lines of the command's log (each escaped and
    indented) when *log* names a file, and exit status 1. *message* is the
    unescaped text. ``tools/apply_theme.py``, ``tools/apply_gtk.py`` and
    ``tools/render_surface.py`` return this result directly as the process exit
    status.
    """
    _require_str("report_failure", "tool", tool)
    _require_str("report_failure", "message", message)
    if log is not None and not isinstance(log, Path):
        raise ValueError(
            f"report_failure() requires pathlib.Path or None: log must be "
            f"Path or None, not {type(log).__name__}"
        )
    text = f"{tool}: error: {escape_controls(message)}"
    if log is not None and log.is_file():
        for line in _log_tail_lines(log):
            text += f"\n  {escape_controls(line)}"
    print(text, file=sys.stderr)
    return 1


def report_missing_tool(tool: str, required: Iterable[str]) -> int | None:
    """Return the missing-tool exit status, or None when every tool is on PATH.

    ``tools/apply_theme.py`` and ``tools/render_surface.py`` both refuse to run
    when an external command they need is absent, naming the first missing one
    in the shared ``report_error`` diagnostic. *required* is checked in order,
    so the tool the message names is deterministic. A bare str *required* is
    rejected: iterating it would look up each character as a tool name.
    """
    _require_str("report_missing_tool", "tool", tool)
    if isinstance(required, (str, bytes)):
        raise ValueError(
            "report_missing_tool() requires an iterable of str: required must "
            f"not be a bare {type(required).__name__}"
        )
    for name in required:
        _require_str("report_missing_tool", "required item", name)
        if shutil.which(name) is None:
            return report_error(tool, f"required tool not found on PATH: {name}")
    return None


def report_note(tool: str, message: str, *, err: bool = False) -> None:
    """Print ``tool: note: <escaped message>`` on stdout, or stderr with *err*.

    A run that succeeds but leaves something for the operator to know -- a
    foreign file it left untouched, a restart it recommends, an optional
    command that is absent -- says so the same way: one control-character-
    escaped ``<tool>: note: <message>`` line. Most notes go to stdout; the
    tools whose notes describe failed optional steps write them to stderr, so
    those stay beside their error diagnostics. *message* is the unescaped
    text; the formatting and escaping live here so the prefix cannot drift.
    """
    _require_str("report_note", "tool", tool)
    _require_str("report_note", "message", message)
    stream = sys.stderr if err else sys.stdout
    print(f"{tool}: note: {escape_controls(message)}", file=stream)
