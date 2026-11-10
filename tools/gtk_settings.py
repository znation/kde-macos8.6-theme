"""Edit the ``gtk-theme-name`` key in GTK ``settings.ini`` text.

The functions here are pure text transforms: they preserve every foreign
line with its own line ending, keep a leading UTF-8 BOM, and leave text
unchanged when removal finds nothing of ours. ``tools/gtk_user_files.py``
reads the files, ``tools/apply_gtk.py`` drives the selection and
``tools/gtk_staging.py`` publishes the writes.
"""

from __future__ import annotations

GTK_ID = "org.macos8.desktop"
_BOM = "\ufeff"
# Every boundary ``str.splitlines`` recognises, longest first so a CRLF is not
# mistaken for a lone CR.
_ENDINGS = (
    "\r\n",
    "\r",
    "\n",
    "\v",
    "\f",
    "\x1c",
    "\x1d",
    "\x1e",
    "\x85",
    "\u2028",
    "\u2029",
)


def _section_name(line: str) -> str | None:
    """Return the name of a ``[Section]`` line, else ``None``."""
    stripped = line.strip()
    if len(stripped) >= 2 and stripped.startswith("[") and stripped.endswith("]"):
        return stripped[1:-1].strip()
    return None


def _key_value(line: str) -> tuple[str, str] | None:
    """Return the trimmed key and value of an assignment, else ``None``."""
    stripped = line.strip()
    if not stripped or stripped[0] in "#;":
        return None
    name, separator, value = stripped.partition("=")
    return (name.strip(), value.strip()) if separator else None


def _split_bom(text: str) -> tuple[bool, str]:
    """Split a leading UTF-8 BOM from *text*, returning ``(had_bom, body)``."""
    if text.startswith(_BOM):
        return True, text[len(_BOM) :]
    return False, text


def _with_bom(had_bom: bool, text: str) -> str:
    """Prepend a UTF-8 BOM to *text* when *had_bom* is true."""
    return _BOM + text if had_bom else text


def _split_lines(body: str) -> list[tuple[str, str]]:
    """Split *body* into ``(content, ending)`` pairs, keeping each ending.

    ``str.splitlines`` treats CRLF, a lone CR, LF, the vertical tab, form feed,
    the ASCII file/group/record separators and the Unicode line/paragraph
    separators as line boundaries. Pairing each content line with its own
    ending lets a rewrite put every foreign line back byte-for-byte.
    """
    lines = []
    for raw in body.splitlines(keepends=True):
        for ending in _ENDINGS:
            if raw.endswith(ending):
                lines.append((raw[: -len(ending)], ending))
                break
        else:
            lines.append((raw, ""))
    return lines


def _join_lines(lines: list[tuple[str, str]]) -> str:
    """Return the text of ``(content, ending)`` pairs."""
    return "".join(content + ending for content, ending in lines)


def _default_ending(lines: list[tuple[str, str]]) -> str:
    """Return the first line ending in *lines*, or ``"\n"`` when none is."""
    for _, ending in lines:
        if ending:
            return ending
    return "\n"


def remove_key_from_section(
    text: str, section: str, key: str, value: str
) -> tuple[str, bool]:
    """Remove ``key=value`` lines naming *value* inside ``[section]``.

    Returns ``(new_text, removed)``. Only a *key* under *section* whose value
    trims to exactly *value* is deleted; a foreign value (and the same key
    name in another section), every comment, every other key and each line's
    own ending are kept byte-identical. A leading UTF-8 BOM is matched
    through and written back. A file that did not end with a line ending
    still does not end with one, even when the removed key was its last
    line. When nothing matched, *text* is returned unchanged so a foreign
    file is not rewritten.

    The ini scanners of :mod:`tools.gtk_settings` serve both callers:
    :func:`tools.gtk_settings.remove_theme_name` (``[Settings]``
    ``gtk-theme-name``) and :func:`tools.kvantum_selection.remove_theme`
    (``[General]`` ``theme``).
    """
    had_bom, body = _split_bom(text)
    lines = _split_lines(body)
    kept = []
    focused = None
    removed = False
    for content, ending in lines:
        name = _section_name(content)
        if name is not None:
            focused = name
            kept.append((content, ending))
            continue
        assignment = _key_value(content)
        if focused == section and assignment == (key, value):
            removed = True
            continue
        kept.append((content, ending))
    if not removed:
        return text, False
    if kept and not any(body.endswith(ending) for ending in _ENDINGS):
        # The file had no final line ending; removing its unterminated last
        # line must not give the new last line one.
        kept[-1] = (kept[-1][0], "")
    return _with_bom(had_bom, _join_lines(kept)), True


def set_theme_name(text: str, value: str) -> str:
    """Return *text* with ``gtk-theme-name=value`` in its ``[Settings]``.

    Every other line, and every line's own ending, is preserved, except that
    inserting after an unterminated header or appending a new section must
    first terminate the last line. The last matching key in the section is
    replaced; with no key a line is inserted after the header, and with no
    ``[Settings]`` section one is appended. A leading UTF-8 BOM is kept for
    matching but written back, as GTK accepts a BOM-prefixed file.
    """
    if any(ending in value for ending in _ENDINGS):
        raise ValueError(f"GTK theme name must be a single line: {value!r}")
    had_bom, body = _split_bom(text)
    lines = _split_lines(body)
    header = None
    last_key = None
    section = None
    for index, (content, _ending) in enumerate(lines):
        name = _section_name(content)
        if name is not None:
            section = name
            if name == "Settings" and header is None:
                header = index
            continue
        assignment = _key_value(content)
        if section == "Settings" and assignment is not None and (
            assignment[0] == "gtk-theme-name"
        ):
            last_key = index
    assignment = f"gtk-theme-name={value}"
    if last_key is not None:
        lines[last_key] = (assignment, lines[last_key][1])
    elif header is not None:
        ending = lines[header][1]
        if not ending:
            # The header was the unterminated last line: give it the separator
            # the inserted line needs and leave the new line unterminated too.
            lines[header] = (lines[header][0], _default_ending(lines))
        lines.insert(header + 1, (assignment, ending))
    else:
        ended = not lines or bool(lines[-1][1])
        ending = _default_ending(lines)
        if lines and not lines[-1][1]:
            lines[-1] = (lines[-1][0], ending)
        lines.append(("[Settings]", ending))
        lines.append((assignment, ending if ended else ""))
    return _with_bom(had_bom, _join_lines(lines))


def remove_theme_name(text: str) -> tuple[str, bool]:
    """Remove our ``gtk-theme-name`` lines from ``[Settings]``.

    Returns ``(new_text, removed)``. Only a key whose value is exactly
    ``org.macos8.desktop`` is deleted; a foreign value, and every other line
    with its own line ending, is kept. A leading UTF-8 BOM is preserved. A
    file that did not end with a line ending still does not end with one, even
    when the removed key was its last line. When nothing matched, *text* is
    returned unchanged so a foreign file is not rewritten.
    """
    return remove_key_from_section(text, "Settings", "gtk-theme-name", GTK_ID)
