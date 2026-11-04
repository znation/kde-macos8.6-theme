"""Read the selected cursor theme from KDE's ``kcminputrc`` config."""

from __future__ import annotations

from pathlib import Path

if __package__:
    from tools.containment import read_text
    from tools.repo_root import ROOT
    from tools.text_lines import split_lines
else:  # imported from a directly run tool
    from containment import read_text
    from repo_root import ROOT
    from text_lines import split_lines


def cursor_theme_setting(config_home: Path) -> str | None:
    """Return ``[Mouse] cursorTheme`` from ``kcminputrc``, or ``None``.

    A missing, unreadable, non-regular or non-UTF-8 file reads as no setting.
    The shared regular-file reader opens with ``O_NONBLOCK`` and checks the
    opened descriptor, so a FIFO or device at the path is refused at once.
    Only LF, CR and CRLF end a line (``tools/text_lines.py``): an exotic
    Unicode separator inside a comment or a value is part of that line.
    """
    path = config_home / "kcminputrc"
    try:
        text = read_text(path, ROOT, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    section = None
    value = None
    for line in split_lines(text):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ";")):
            continue
        section, setting = _cursor_theme_line(stripped, section)
        if setting is not None:
            value = setting
    return value


def _cursor_theme_line(
    line: str, section: str | None
) -> tuple[str | None, str | None]:
    """Return the updated section and any cursor-theme value on *line*."""
    if line.startswith("[") and line.endswith("]"):
        return line[1:-1].strip(), None
    if section != "Mouse" or "=" not in line:
        return section, None
    key, _, setting = line.partition("=")
    if key.strip() != "cursorTheme":
        return section, None
    return section, setting.strip()
