"""Select or clear the opt-in GTK 3 and GTK 4 Platinum themes.

``make apply-gtk`` installs the GTK theme files and then runs this script.
It sets ``gtk-theme-name=org.macos8.desktop`` in the GTK 3 and GTK 4
``settings.ini`` files and writes a ``gtk-4.0/gtk.css`` user stylesheet that
imports the installed GTK 4 sheet, because libadwaita applications read user
CSS instead of the ``gtk-theme-name`` setting. ``make remove-gtk`` runs the
same script with ``--remove``: it deletes only our ``gtk-theme-name`` lines and
the marker user stylesheet, leaving foreign values and files alone.

Usage::

    python3 tools/apply_gtk.py
    python3 tools/apply_gtk.py --remove

Exit status: 0 when the selection or removal ran, 1 when the installed GTK 4
sheet is missing, 2 for a usage error or an unresolvable home directory.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.diagnostics import report_error, report_failure
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/apply_gtk.py
    from argument_parsing import EscapingArgumentParser
    from diagnostics import report_error, report_failure
    from terminal import escape_controls

TOOL = "apply_gtk"
GTK_ID = "org.macos8.desktop"
GTK4_CSS_MARKER = "/* org.macos8.desktop GTK 4 user CSS */"
_BOM = "\ufeff"


def _note(message: str) -> None:
    """Print ``apply_gtk: note: <message>`` on stdout."""
    print(f"{TOOL}: note: {escape_controls(message)}")


def _absolute(env: dict[str, str], name: str) -> Path | None:
    """Return *name* from *env* when it is an absolute path, else ``None``."""
    value = env.get(name, "")
    return Path(value) if os.path.isabs(value) else None


def _home_child(env: dict[str, str], *parts: str) -> Path | None:
    """Return an absolute ``$HOME`` joined with *parts*, else ``None``."""
    home = env.get("HOME", "")
    if not os.path.isabs(home):
        return None
    return Path(home).joinpath(*parts)


def _config_home(env: dict[str, str]) -> Path | None:
    """Resolve the GTK config home: absolute XDG, else ``$HOME/.config``.

    The XDG Base Directory spec treats an empty or relative
    ``XDG_CONFIG_HOME`` as invalid and falls back to ``$HOME/.config``; with
    an unusable ``HOME`` there is no absolute path to write, so the result is
    ``None`` and the caller refuses instead of guessing.
    """
    return _absolute(env, "XDG_CONFIG_HOME") or _home_child(env, ".config")


def _data_home(env: dict[str, str]) -> Path | None:
    """Resolve the data home: absolute XDG, else ``$HOME/.local/share``.

    This is the same resolution ``make install`` uses for the installed theme
    files; a relative ``XDG_DATA_HOME`` is invalid and falls back to
    ``$HOME/.local/share``, and an unusable ``HOME`` returns ``None``.
    """
    return _absolute(env, "XDG_DATA_HOME") or _home_child(env, ".local", "share")


def _installed_sheet(data_home: Path) -> Path:
    """Return the installed GTK 4 sheet below *data_home*."""
    return data_home / "themes" / GTK_ID / "gtk-4.0" / "gtk.css"


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


def _set_theme_name(text: str, value: str) -> str:
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


def _remove_theme_name(text: str) -> tuple[str, bool]:
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


def _write_atomic(path: Path, text: str) -> None:
    """Write *text* through a ``.staging`` sibling then ``os.replace`` it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_name(f".{path.name}.staging")
    try:
        staging.write_text(text, encoding="utf-8")
        os.replace(staging, path)
    finally:
        try:
            staging.unlink()
        except FileNotFoundError:
            pass


def _write_user_css(config_home: Path, sheet: Path) -> None:
    """Write the libadwaita user CSS, leaving a foreign ``gtk.css`` alone."""
    path = config_home / "gtk-4.0" / "gtk.css"
    if path.is_file():
        first = path.read_text(encoding="utf-8").splitlines()
        if not first or first[0] != GTK4_CSS_MARKER:
            _note(f"{path} exists but is not our user CSS; leaving it untouched")
            return
    content = f'{GTK4_CSS_MARKER}\n@import url("{sheet.as_uri()}");\n'
    _write_atomic(path, content)


def _remove_user_css(config_home: Path) -> None:
    """Delete ``gtk-4.0/gtk.css`` only when our marker opens it."""
    path = config_home / "gtk-4.0" / "gtk.css"
    if not path.is_file():
        return
    first = path.read_text(encoding="utf-8").splitlines()
    if first and first[0] == GTK4_CSS_MARKER:
        path.unlink()


def _apply(data_home: Path, config_home: Path) -> int:
    """Select our GTK themes in both settings files and the user CSS."""
    sheet = _installed_sheet(data_home)
    if not sheet.is_file():
        return report_failure(
            TOOL,
            f"installed GTK 4 sheet is missing: {sheet}; run make install-gtk",
        )
    for version in ("gtk-3.0", "gtk-4.0"):
        path = config_home / version / "settings.ini"
        original = path.read_text(encoding="utf-8") if path.is_file() else ""
        updated = _set_theme_name(original, GTK_ID)
        if updated != original:
            _write_atomic(path, updated)
    _write_user_css(config_home, sheet)
    return 0


def _remove(config_home: Path) -> int:
    """Clear our selection from both settings files and the user CSS."""
    for version in ("gtk-3.0", "gtk-4.0"):
        path = config_home / version / "settings.ini"
        if not path.is_file():
            continue
        original = path.read_text(encoding="utf-8")
        updated, removed = _remove_theme_name(original)
        if removed:
            _write_atomic(path, updated)
    _remove_user_css(config_home)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the GTK selection CLI; *argv* excludes the program name."""
    parser = EscapingArgumentParser(
        prog=TOOL,
        description=(
            "Select or clear the Mac OS 8.6 GTK 3 and GTK 4 Platinum themes."
        ),
        epilog=(
            "exit status: 0 when the selection ran, 1 when the installed GTK 4 "
            "sheet is missing, 2 usage error or an unresolvable home directory"
        ),
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="remove our gtk-theme-name lines and marker user CSS",
    )
    args = parser.parse_args(argv)

    env = os.environ
    data_home = _data_home(env)
    config_home = _config_home(env)
    if data_home is None:
        return report_error(
            TOOL,
            "XDG_DATA_HOME is unset or not absolute and HOME cannot provide "
            "$HOME/.local/share; set XDG_DATA_HOME to an absolute path or "
            "export an absolute HOME",
        )
    if config_home is None:
        return report_error(
            TOOL,
            "XDG_CONFIG_HOME is unset or not absolute and HOME cannot provide "
            "$HOME/.config; set XDG_CONFIG_HOME to an absolute path or "
            "export an absolute HOME",
        )

    status = _remove(config_home) if args.remove else _apply(data_home, config_home)
    if status == 0:
        _note("restart running GTK applications to pick up the theme")
    return status


if __name__ == "__main__":
    sys.exit(main())
