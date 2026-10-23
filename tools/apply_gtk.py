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
sheet is missing, 2 for a usage error, an unresolvable home directory, or a
settings or user-CSS file that cannot be read or written.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.atomic_write import write_atomically
    from tools.diagnostics import report_error, report_failure
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/apply_gtk.py
    from argument_parsing import EscapingArgumentParser
    from atomic_write import write_atomically
    from diagnostics import report_error, report_failure
    from terminal import escape_controls

TOOL = "apply_gtk"
GTK_ID = "org.macos8.desktop"
GTK4_CSS_MARKER = "/* org.macos8.desktop GTK 4 user CSS */"
_BOM = "\ufeff"


class _ConfigError(Exception):
    """A GTK settings or user-CSS file could not be read or written.

    The message names the offending path and the underlying error, so
    ``main`` can report it as the one-line diagnostic instead of letting a
    bare ``OSError`` or ``UnicodeDecodeError`` traceback escape. A decoder's
    own error names the byte that failed but not the file it came from.
    """


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


def _read_text(path: Path) -> str:
    """Return *path*'s UTF-8 text, reporting a read failure by path."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise _ConfigError(f"cannot read {path}: {exc}") from exc


def _discard(staging: Path) -> None:
    """Remove a staging file, ignoring a path that never became one."""
    try:
        staging.unlink()
    except OSError:
        pass


def _stage(path: Path, text: str) -> Path:
    """Write *text* to a ``.staging`` sibling and return its path."""
    staging = path.with_name(f".{path.name}.staging")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            raise _ConfigError(f"cannot write {path}: is a directory")
        write_atomically(
            staging, lambda destination: destination.write(text.encode("utf-8"))
        )
    except OSError as exc:
        _discard(staging)
        raise _ConfigError(f"cannot write {path}: {exc}") from exc
    return staging


def _stage_all(writes: list[tuple[Path, str]]) -> list[tuple[Path, Path]]:
    """Stage every ``(path, text)`` write, discarding all on a failure."""
    staged = []
    try:
        for path, text in writes:
            staged.append((path, _stage(path, text)))
    except _ConfigError:
        for _, staging in staged:
            _discard(staging)
        raise
    return staged


def _commit(staged: list[tuple[Path, Path]]) -> None:
    """Rename each staged file over its target, discarding leftovers."""
    try:
        for path, staging in staged:
            try:
                os.replace(staging, path)
            except OSError as exc:
                raise _ConfigError(f"cannot write {path}: {exc}") from exc
    finally:
        for _, staging in staged:
            _discard(staging)


def _settings_path(config_home: Path, version: str) -> Path:
    """Return the ``gtk-3.0`` or ``gtk-4.0`` settings file below *config_home*."""
    return config_home / version / "settings.ini"


def _user_css_path(config_home: Path) -> Path:
    """Return the libadwaita user stylesheet below *config_home*."""
    return config_home / "gtk-4.0" / "gtk.css"


def _user_css_write(
    config_home: Path, sheet: Path
) -> tuple[Path, str] | None:
    """Return the ``(path, text)`` user-CSS write, or None to leave it alone.

    A foreign ``gtk.css`` is read and left untouched. The read happens here,
    before any settings write, so an unreadable file changes nothing.
    """
    path = _user_css_path(config_home)
    if path.is_file():
        first = _read_text(path).splitlines()
        if not first or first[0] != GTK4_CSS_MARKER:
            _note(f"{path} exists but is not our user CSS; leaving it untouched")
            return None
    content = f'{GTK4_CSS_MARKER}\n@import url("{sheet.as_uri()}");\n'
    return path, content


def _user_css_remove(config_home: Path) -> Path | None:
    """Return the marker-led user CSS to delete, or None to keep the file.

    The file is read here, before any settings write, so an unreadable
    ``gtk.css`` changes nothing.
    """
    path = _user_css_path(config_home)
    if not path.is_file():
        return None
    first = _read_text(path).splitlines()
    if first and first[0] == GTK4_CSS_MARKER:
        return path
    return None


def _unlink(path: Path) -> None:
    """Delete *path*, reporting a failure by path."""
    try:
        path.unlink()
    except OSError as exc:
        raise _ConfigError(f"cannot remove {path}: {exc}") from exc


def _apply(data_home: Path, config_home: Path) -> int:
    """Select our GTK themes in both settings files and the user CSS."""
    sheet = _installed_sheet(data_home)
    if not sheet.is_file():
        return report_failure(
            TOOL,
            f"installed GTK 4 sheet is missing: {sheet}; run make install-gtk",
        )
    # Read every settings and user-CSS file before writing any, so an
    # unreadable file leaves every file unmodified instead of applying half
    # the selection.
    writes = []
    for version in ("gtk-3.0", "gtk-4.0"):
        path = _settings_path(config_home, version)
        original = _read_text(path) if path.is_file() else ""
        updated = _set_theme_name(original, GTK_ID)
        if updated != original:
            writes.append((path, updated))
    css = _user_css_write(config_home, sheet)
    if css is not None:
        writes.append(css)
    # Stage every write before replacing anything: an unwritable settings
    # file or user CSS leaves all of them unmodified.
    _commit(_stage_all(writes))
    return 0


def _remove(config_home: Path) -> int:
    """Clear our selection from both settings files and the user CSS."""
    writes = []
    for version in ("gtk-3.0", "gtk-4.0"):
        path = _settings_path(config_home, version)
        if not path.is_file():
            continue
        updated, removed = _remove_theme_name(_read_text(path))
        if removed:
            writes.append((path, updated))
    css = _user_css_remove(config_home)
    # Stage the settings, then delete the user CSS, then replace the settings:
    # a failure in either step leaves every settings file unmodified.
    staged = _stage_all(writes)
    if css is not None:
        try:
            _unlink(css)
        except _ConfigError:
            for _, staging in staged:
                _discard(staging)
            raise
    _commit(staged)
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
            "sheet is missing, 2 for a usage error, an unresolvable home "
            "directory, or a settings file that cannot be read or written"
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

    try:
        status = (
            _remove(config_home) if args.remove else _apply(data_home, config_home)
        )
    except _ConfigError as exc:
        return report_error(TOOL, str(exc))
    if status == 0:
        _note("restart running GTK applications to pick up the theme")
    return status


if __name__ == "__main__":
    sys.exit(main())
