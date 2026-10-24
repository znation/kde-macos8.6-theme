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

Exit status: 0 when the selection or removal ran, 1 when an installed GTK 3
or GTK 4 sheet is missing, 2 for a usage error, an unresolvable config home
(or data home when applying), or a settings or user-CSS file that cannot be
read or written.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__:
    from tools import xdg_homes
    from tools.argument_parsing import EscapingArgumentParser
    from tools.diagnostics import report_error, report_failure, report_note
    from tools.gtk_settings import GTK_ID, remove_theme_name, set_theme_name
    from tools.gtk_staging import commit, discard, stage_all
    from tools.gtk_user_files import (
        ConfigError,
        MAX_CONFIG_FILE_BYTES,
        read_config_text,
        settings_path,
        unlink,
        user_css_remove,
        user_css_write,
    )
else:  # run directly: python3 tools/apply_gtk.py
    import xdg_homes
    from argument_parsing import EscapingArgumentParser
    from diagnostics import report_error, report_failure, report_note
    from gtk_settings import GTK_ID, remove_theme_name, set_theme_name
    from gtk_staging import commit, discard, stage_all
    from gtk_user_files import (
        ConfigError,
        MAX_CONFIG_FILE_BYTES,
        read_config_text,
        settings_path,
        unlink,
        user_css_remove,
        user_css_write,
    )

TOOL = "apply_gtk"


def _note(message: str) -> None:
    """Print ``apply_gtk: note: <message>`` on stdout."""
    report_note(TOOL, message)


def _installed_sheet(data_home: Path, version: str) -> Path:
    """Return the installed GTK *version* sheet below *data_home*."""
    return data_home / "themes" / GTK_ID / version / "gtk.css"


def _require_home(path: Path | None, variable: str, fallback: str) -> Path:
    """Return *path*, or refuse naming the unusable XDG *variable*.

    *fallback* is the ``$HOME``-relative path the XDG spec falls back to,
    included in the diagnostic so the user can see which directory could not
    be resolved. Every caller resolves its path through
    :mod:`tools.xdg_homes` and must refuse rather than guess where to write,
    so the diagnostic lives here once.
    """
    if path is None:
        raise ConfigError(
            f"{variable} is unset or not absolute and HOME cannot provide "
            f"{fallback}; set {variable} to an absolute path or export an "
            "absolute HOME"
        )
    return path


def _apply(data_home: Path, config_home: Path) -> int:
    """Select our GTK themes in both settings files and the user CSS."""
    # Both settings files name our theme, so both sheets must exist: selecting
    # a GTK 3 theme whose sheet is absent would silently leave GTK 3 unstyled.
    sheets = {}
    for version in ("gtk-4.0", "gtk-3.0"):
        sheet = _installed_sheet(data_home, version)
        if not sheet.is_file():
            return report_failure(
                TOOL,
                f"installed {version} sheet is missing: {sheet}; "
                "run make install-gtk",
            )
        sheets[version] = sheet
    sheet = sheets["gtk-4.0"]
    # Read every settings and user-CSS file before writing any, so an
    # unreadable file leaves every file unmodified instead of applying half
    # the selection.
    writes = []
    for version in ("gtk-3.0", "gtk-4.0"):
        path = settings_path(config_home, version)
        original = read_config_text(path) or ""
        updated = set_theme_name(original, GTK_ID)
        if updated != original:
            writes.append((path, updated))
    css = user_css_write(config_home, sheet, _note)
    if css is not None:
        writes.append(css)
    # A settings file at the read cap can grow past it when our longer value
    # replaces a shorter foreign one. Refuse before staging, or a later apply
    # or removal would refuse the file this run wrote.
    for path, text in writes:
        if len(text.encode("utf-8")) > MAX_CONFIG_FILE_BYTES:
            raise ConfigError(
                f"{path} would grow past the {MAX_CONFIG_FILE_BYTES}-byte "
                "limit this tool reads; refusing to write it"
            )
    # Stage every write before replacing anything: an unwritable settings
    # file or user CSS leaves all of them unmodified.
    commit(stage_all(writes))
    return 0


def _remove(config_home: Path) -> int:
    """Clear our selection from both settings files and the user CSS."""
    writes = []
    for version in ("gtk-3.0", "gtk-4.0"):
        path = settings_path(config_home, version)
        original = read_config_text(path)
        if original is None:
            continue
        updated, removed = remove_theme_name(original)
        if removed:
            writes.append((path, updated))
    css = user_css_remove(config_home)
    # Stage the settings, then delete the user CSS, then replace the settings:
    # a failure in either step leaves every settings file unmodified.
    staged = stage_all(writes)
    if css is not None:
        try:
            unlink(css)
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
            "exit status: 0 when the selection or removal ran, 1 when an "
            "installed GTK 3 or GTK 4 sheet is missing, 2 for a usage error, "
            "an unresolvable config home (or data home when applying), or a "
            "settings or user-CSS file that cannot be read or written"
        ),
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="remove our gtk-theme-name lines and marker user CSS",
    )
    args = parser.parse_args(argv)

    env = os.environ
    try:
        if args.remove:
            # Removal touches only the config home, so it must work when no
            # data home resolves: refusing it would block clearing a
            # selection that is already installed.
            status = _remove(
                _require_home(
                    xdg_homes.config_home(env),
                    "XDG_CONFIG_HOME",
                    "$HOME/.config",
                )
            )
        else:
            status = _apply(
                _require_home(
                    xdg_homes.data_home(env),
                    "XDG_DATA_HOME",
                    "$HOME/.local/share",
                ),
                _require_home(
                    xdg_homes.config_home(env),
                    "XDG_CONFIG_HOME",
                    "$HOME/.config",
                ),
            )
    except ConfigError as exc:
        return report_error(TOOL, str(exc))
    if status == 0:
        _note("restart running GTK applications to pick up the theme")
    return status


if __name__ == "__main__":
    sys.exit(main())
