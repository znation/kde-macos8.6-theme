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
sheet is missing, 2 for a usage error, an unresolvable config home (or data
home when applying), or a settings or user-CSS file that cannot be read or
written.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.diagnostics import report_error, report_failure
    from tools.gtk_settings import GTK_ID, remove_theme_name, set_theme_name
    from tools.gtk_staging import ConfigError, commit, discard, stage_all
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/apply_gtk.py
    from argument_parsing import EscapingArgumentParser
    from diagnostics import report_error, report_failure
    from gtk_settings import GTK_ID, remove_theme_name, set_theme_name
    from gtk_staging import ConfigError, commit, discard, stage_all
    from terminal import escape_controls

TOOL = "apply_gtk"
GTK4_CSS_MARKER = "/* org.macos8.desktop GTK 4 user CSS */"


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


def _read_text(path: Path) -> str:
    """Return *path*'s UTF-8 text, reporting a read failure by path."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc


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
        raise ConfigError(f"cannot remove {path}: {exc}") from exc


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
        updated = set_theme_name(original, GTK_ID)
        if updated != original:
            writes.append((path, updated))
    css = _user_css_write(config_home, sheet)
    if css is not None:
        writes.append(css)
    # Stage every write before replacing anything: an unwritable settings
    # file or user CSS leaves all of them unmodified.
    commit(stage_all(writes))
    return 0


def _remove(config_home: Path) -> int:
    """Clear our selection from both settings files and the user CSS."""
    writes = []
    for version in ("gtk-3.0", "gtk-4.0"):
        path = _settings_path(config_home, version)
        if not path.is_file():
            continue
        updated, removed = remove_theme_name(_read_text(path))
        if removed:
            writes.append((path, updated))
    css = _user_css_remove(config_home)
    # Stage the settings, then delete the user CSS, then replace the settings:
    # a failure in either step leaves every settings file unmodified.
    staged = stage_all(writes)
    if css is not None:
        try:
            _unlink(css)
        except ConfigError:
            for _, staging in staged:
                discard(staging)
            raise
    commit(staged)
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
            "sheet is missing, 2 for a usage error, an unresolvable config home "
            "(or data home when applying), or a settings file that cannot be "
            "read or written"
        ),
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="remove our gtk-theme-name lines and marker user CSS",
    )
    args = parser.parse_args(argv)

    env = os.environ
    if args.remove:
        # Removal touches only the config home, so it must work when no data
        # home resolves: refusing it would block clearing a selection that is
        # already installed.
        config_home = _config_home(env)
        if config_home is None:
            return report_error(
                TOOL,
                "XDG_CONFIG_HOME is unset or not absolute and HOME cannot "
                "provide $HOME/.config; set XDG_CONFIG_HOME to an absolute "
                "path or export an absolute HOME",
            )
        try:
            status = _remove(config_home)
        except ConfigError as exc:
            return report_error(TOOL, str(exc))
    else:
        data_home = _data_home(env)
        if data_home is None:
            return report_error(
                TOOL,
                "XDG_DATA_HOME is unset or not absolute and HOME cannot "
                "provide $HOME/.local/share; set XDG_DATA_HOME to an absolute "
                "path or export an absolute HOME",
            )
        config_home = _config_home(env)
        if config_home is None:
            return report_error(
                TOOL,
                "XDG_CONFIG_HOME is unset or not absolute and HOME cannot "
                "provide $HOME/.config; set XDG_CONFIG_HOME to an absolute "
                "path or export an absolute HOME",
            )
        try:
            status = _apply(data_home, config_home)
        except ConfigError as exc:
            return report_error(TOOL, str(exc))
    if status == 0:
        _note("restart running GTK applications to pick up the theme")
    return status


if __name__ == "__main__":
    sys.exit(main())
