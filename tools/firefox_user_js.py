"""Edit the marker-delimited Platinum preference block in a Firefox user.js.

The transforms are pure: they take the file text and return the new text, so
the installer never has to reason about foreign lines or their line endings.
"""

from __future__ import annotations

from collections import Counter

USER_JS_MARKER = "// org.macos8.desktop Firefox Platinum userChrome"
PREF_LINE = 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);'


def _lines(text: str) -> list[tuple[str, str]]:
    """Return ``(content, ending)`` pairs, keeping every line's own ending.

    The final pair's ending is ``""`` when the text does not end with a line
    break, so joining the pairs reproduces *text* exactly.
    """
    lines = []
    index = 0
    while index < len(text):
        end = index
        while end < len(text) and text[end] not in "\r\n":
            end += 1
        if end == len(text):
            lines.append((text[index:end], ""))
            break
        if text[end] == "\r" and end + 1 < len(text) and text[end + 1] == "\n":
            lines.append((text[index:end], "\r\n"))
            end += 2
        else:
            lines.append((text[index:end], text[end]))
            end += 1
        index = end
    return lines


def _join(lines: list[tuple[str, str]]) -> str:
    """Join ``(content, ending)`` pairs back into text."""
    return "".join(content + ending for content, ending in lines)


def _dominant_ending(lines: list[tuple[str, str]]) -> str:
    """Return the line ending the file uses most, or ``"\\n"`` for no lines.

    Ties keep the earliest-seen ending, so a file with one CRLF and one LF
    keeps the CRLF its first line used.
    """
    endings = Counter(ending for _, ending in lines if ending)
    if not endings:
        return "\n"
    return endings.most_common(1)[0][0]


def _without_block(lines: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Drop each marker line and the exact pref line immediately after it."""
    kept = []
    index = 0
    while index < len(lines):
        if lines[index][0] == USER_JS_MARKER:
            index += 1
            if index < len(lines) and lines[index][0] == PREF_LINE:
                index += 1
            continue
        kept.append(lines[index])
        index += 1
    return kept


def first_line(text: str) -> str:
    """Return *text*'s first line without its ending."""
    lines = _lines(text)
    return lines[0][0] if lines else ""


def set_user_js(text: str) -> str:
    """Return *text* with exactly one marker-plus-pref block at the end.

    Foreign lines keep their own endings. An earlier block is removed first,
    so a repeat install does not duplicate it. An unterminated last foreign
    line is terminated before the block is appended, and the block uses the
    file's dominant ending (``"\\n"`` for a new file). A foreign setting of
    the same preference is left alone, so our line follows it.
    """
    lines = _without_block(_lines(text))
    ending = _dominant_ending(lines)
    if lines and not lines[-1][1]:
        content, _ = lines[-1]
        lines[-1] = (content, ending)
    lines.append((USER_JS_MARKER, ending))
    lines.append((PREF_LINE, ending))
    return _join(lines)


def remove_user_js(text: str) -> str:
    """Return *text* without our marker-plus-pref block, foreign lines intact."""
    return _join(_without_block(_lines(text)))
