"""Escape contributor-supplied text before it is printed to a terminal.

Both command-line tools in this directory print file paths and arguments that
can come from the repository or from a shell glob. Printed raw, a control
character in such a name would drive the operator's terminal (an ESC sequence)
or forge an extra diagnostic line (a newline), so every tool routes that text
through :func:`escape_controls` before it reaches stdout or stderr.
"""

from __future__ import annotations


def escape_controls(text: str) -> str:
    """Render *text* with control characters escaped for terminal output.

    Every non-printable character becomes a visible ``\\uXXXX`` escape, so a
    path carrying an ESC or newline is shown literally instead of being
    interpreted by the terminal.
    """
    return "".join(
        ch if ch.isprintable() else f"\\u{ord(ch):04x}" for ch in text
    )
