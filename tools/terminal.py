"""Escape contributor-supplied text before it is printed to a terminal.

Both command-line tools in this directory print file paths and arguments that
can come from the repository or from a shell glob. Printed raw, a control
character in such a name would drive the operator's terminal (an ESC sequence)
or forge an extra diagnostic line (a newline), so every tool routes that text
through :func:`escape_controls` before it reaches stdout or stderr.
"""

from __future__ import annotations


def _escape(ch: str) -> str:
    """Return *ch*, or its visible escape when it is not printable.

    A printable character is returned unchanged, except a literal backslash:
    doubling it (``\\\\``) keeps a printed escape sequence unambiguous, so a
    name that literally contains the six characters ``\\u001b`` cannot be
    mistaken for the escaped ESC it would otherwise resemble. A non-printable
    character is escaped as ``\\uXXXX`` when it lies in the Basic Multilingual
    Plane and as ``\\UXXXXXXXX`` when it is above it, so every escape is
    well-formed: a five- or six-digit ``\\u`` escape for an astral character
    would be ambiguous with the four hex digits that follow it.
    """
    if ch == "\\":
        return "\\\\"
    if ch.isprintable():
        return ch
    codepoint = ord(ch)
    if codepoint > 0xFFFF:
        return f"\\U{codepoint:08x}"
    return f"\\u{codepoint:04x}"


def escape_controls(text: str) -> str:
    """Render *text* with control characters escaped for terminal output.

    Every non-printable character becomes a visible escape -- ``\\uXXXX``
    for a Basic Multilingual Plane codepoint, ``\\UXXXXXXXX`` above it -- so
    a path carrying an ESC or newline is shown literally instead of being
    interpreted by the terminal. A literal backslash is doubled, so a name
    that contains the escape text itself (``\\u001b``) reads differently from
    the ESC that escapes to the same characters.
    """
    return "".join(_escape(ch) for ch in text)
