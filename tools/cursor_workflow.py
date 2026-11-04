"""Apply and remove the cursor theme across its installed and session state."""

from __future__ import annotations

import stat
from pathlib import Path

if __package__:
    from tools import cursor_config, cursor_link, cursor_selection
    from tools.diagnostics import report_note
    from tools.file_lock import installed_data_lock
else:  # run directly through apply_cursor.py
    import cursor_config
    import cursor_link
    import cursor_selection
    from diagnostics import report_note
    from file_lock import installed_data_lock

CursorError = cursor_link.CursorError
LOCK_TIMEOUT = 60.0
CURSOR_THEME = cursor_link.CURSOR_THEME
SELECT_TOOL = cursor_selection.SELECT_TOOL


def apply(home: Path, data_home: Path, env: dict[str, str], optional: bool) -> int:
    """Link the installed theme and select it while holding its data lock."""
    theme = cursor_link.require_installed(data_home)
    with installed_data_lock(
        data_home,
        "for the cursor selection",
        LOCK_TIMEOUT,
        error=CursorError,
    ):
        theme = cursor_link.require_installed(data_home)
        cursor_link.install_link(home, theme)
        status = cursor_selection.select(env, optional)
    if status == 0:
        report_note(
            "apply_cursor",
            "restart running applications for the new pointer to display correctly",
        )
    return status


def remove(home: Path, data_home: Path, config_home: Path) -> int:
    """Remove our Xcursor link, preserving foreign paths and config."""
    try:
        data_home_mode = data_home.stat().st_mode
    except FileNotFoundError:
        data_home_mode = None
    except OSError as exc:
        raise CursorError(f"cannot inspect data home {data_home}: {exc}") from exc
    if data_home_mode is not None and stat.S_ISDIR(data_home_mode):
        with installed_data_lock(
            data_home,
            "for the cursor removal",
            LOCK_TIMEOUT,
            error=CursorError,
        ):
            target, foreign = cursor_link.remove_link(home, data_home)
    else:
        target, foreign = cursor_link.remove_link(home, data_home)
    if foreign:
        report_note("apply_cursor", f"{target} is not our symlink; leaving it untouched")
    if cursor_config.cursor_theme_setting(config_home) == CURSOR_THEME:
        report_note(
            "apply_cursor",
            f"[Mouse] cursorTheme in {config_home / 'kcminputrc'} still names "
            f"{CURSOR_THEME}; run {SELECT_TOOL} breeze_cursors to reset",
        )
    return 0
