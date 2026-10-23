"""Edit the ``gtk-theme-name`` key in GTK ``settings.ini`` text.

The functions here are pure text transforms: they preserve every foreign
line, keep a leading UTF-8 BOM, and leave text unchanged when removal finds
nothing of ours. ``tools/apply_gtk.py`` reads the files and
``tools/gtk_staging.py`` publishes the writes.
"""

from __future__ import annotations

GTK_ID = "org.macos8.desktop"
_BOM = "\ufeff"


def _section_name(line: str) -> str | None:
    """Return the name of a ``[Section]`` line, else ``None``."""
    stripped = line.strip()
    if len(stripped) >= 2 and stripped.startswith("[") and stripped.endswith("]"):
        return stripped[1:-1].strip()
    return None


def _key_name(line: str) -> str | None:
    """Return the key name of a ``key=value`` line, else ``None``."""
    stripped = line.strip()
    if not stripped or stripped[0] in "#;":
        return None
    name, separator, _ = stripped.partition("=")
    return name.strip() if separator else None


def _split_bom(text: str) -> tuple[bool, str]:
    """Split a leading UTF-8 BOM from *text*, returning ``(had_bom, body)``."""
    if text.startswith(_BOM):
        return True, text[len(_BOM) :]
    return False, text


def _with_bom(had_bom: bool, text: str) -> str:
    """Prepend a UTF-8 BOM to *text* when *had_bom* is true."""
    return _BOM + text if had_bom else text


def set_theme_name(text: str, value: str) -> str:
    """Return *text* with ``gtk-theme-name=value`` in its ``[Settings]``.

    Every other line is preserved. The last matching key in the section is
    replaced; with no key a line is inserted after the header, and with no
    ``[Settings]`` section one is appended. A leading UTF-8 BOM is kept for
    matching but written back, as GTK accepts a BOM-prefixed file.
    """
    had_bom, body = _split_bom(text)
    had_newline = body.endswith("\n")
    lines = body.splitlines()
    header = None
    last_key = None
    section = None
    for index, line in enumerate(lines):
        name = _section_name(line)
        if name is not None:
            section = name
            if name == "Settings" and header is None:
                header = index
            continue
        if section == "Settings" and _key_name(line) == "gtk-theme-name":
            last_key = index
    assignment = f"gtk-theme-name={value}"
    if last_key is not None:
        lines[last_key] = assignment
    elif header is not None:
        lines.insert(header + 1, assignment)
    else:
        lines.append("[Settings]")
        lines.append(assignment)
    result = "\n".join(lines)
    if had_newline or not body:
        result += "\n"
    return _with_bom(had_bom, result)


def remove_theme_name(text: str) -> tuple[str, bool]:
    """Remove our ``gtk-theme-name`` lines from ``[Settings]``.

    Returns ``(new_text, removed)``. Only a key whose value is exactly
    ``org.macos8.desktop`` is deleted; a foreign value, and every other line,
    is kept. A leading UTF-8 BOM is preserved. When nothing matched, *text* is
    returned unchanged so a foreign file is not rewritten.
    """
    had_bom, body = _split_bom(text)
    had_newline = body.endswith("\n")
    lines = body.splitlines()
    kept = []
    section = None
    removed = False
    for line in lines:
        name = _section_name(line)
        if name is not None:
            section = name
            kept.append(line)
            continue
        if section == "Settings" and _key_name(line) == "gtk-theme-name":
            value = line.split("=", 1)[1].strip()
            if value == GTK_ID:
                removed = True
                continue
        kept.append(line)
    if not removed:
        return text, False
    result = "\n".join(kept)
    if had_newline and kept:
        result += "\n"
    return _with_bom(had_bom, result), True
