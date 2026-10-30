"""Apply or remove the GTK theme selection in the user's config files.

Home resolution, lock ordering and CLI diagnostics belong to
``tools/apply_gtk.py``. This module owns the config-file workflow once those
paths and locks are established: checking installed sheets, preserving
foreign content, and publishing or removing the selection.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

if __package__:
    from tools.diagnostics import report_failure
    from tools.gtk_settings import GTK_ID, remove_theme_name, set_theme_name
    from tools.gtk_staging import commit, stage_all
    from tools.gtk_user_files import (
        ConfigError,
        MAX_CONFIG_FILE_BYTES,
        read_config_text,
        settings_path,
        user_css_remove,
        user_css_write,
    )
    from tools.symlink_refusal import refuse_symlink
else:  # imported from a directly run tool
    from diagnostics import report_failure
    from gtk_settings import GTK_ID, remove_theme_name, set_theme_name
    from gtk_staging import commit, stage_all
    from gtk_user_files import (
        ConfigError,
        MAX_CONFIG_FILE_BYTES,
        read_config_text,
        settings_path,
        user_css_remove,
        user_css_write,
    )
    from symlink_refusal import refuse_symlink

TOOL = "apply_gtk"


def _refuse_symlinked_config_dirs(config_home: Path, action: str) -> None:
    """Keep GTK config operations inside the selected config home."""
    for version in ("gtk-3.0", "gtk-4.0"):
        refuse_symlink(config_home / version, action, ConfigError)


def installed_sheet(data_home: Path, version: str) -> Path:
    """Return the installed GTK *version* sheet below *data_home*."""
    return data_home / "themes" / GTK_ID / version / "gtk.css"


def installed_sheets(data_home: Path) -> dict[str, Path] | None:
    """Return both installed sheets, or report the first one missing.

    Both settings files name our theme, so both sheets must exist: selecting
    a GTK 3 theme whose sheet is absent would silently leave GTK 3 unstyled.
    """
    sheets = {}
    for version in ("gtk-4.0", "gtk-3.0"):
        sheet = installed_sheet(data_home, version)
        if not sheet.is_file():
            report_failure(
                TOOL,
                f"installed {version} sheet is missing: {sheet}; "
                "run make install-gtk",
            )
            return None
        sheets[version] = sheet
    return sheets


def apply(
    sheets: dict[str, Path], config_home: Path, note: Callable[[str], None]
) -> int:
    """Select our GTK themes in both settings files and the user CSS."""
    _refuse_symlinked_config_dirs(config_home, "write")
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
    css = user_css_write(config_home, sheet, note)
    if css is not None:
        writes.append(css)
    # A symlinked config path is the user's link, not ours: refuse it before
    # staging any write instead of replacing the link with a regular file.
    for path, _text in writes:
        refuse_symlink(path, "write", ConfigError)
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


def remove(config_home: Path) -> int:
    """Clear our selection from both settings files and the user CSS."""
    _refuse_symlinked_config_dirs(config_home, "remove")
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
    removals = [css] if css is not None else []
    # A symlinked config path is the user's link: refuse it before staging
    # any write or removal instead of replacing or deleting the link.
    for path, _text in writes:
        refuse_symlink(path, "remove", ConfigError)
    for path in removals:
        refuse_symlink(path, "remove", ConfigError)
    # Replace settings and delete user CSS together, restoring every file
    # changed so far if either operation fails.
    commit(staged=stage_all(writes), removals=removals)
    return 0
