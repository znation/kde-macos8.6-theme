"""Filesystem policy for exposing the installed cursor theme to Xcursor."""

from __future__ import annotations

import os
from pathlib import Path

CURSOR_THEME = "org.macos8.desktop"


class CursorError(Exception):
    """A refused cursor path, reported by the apply-cursor command."""


def installed_theme(data_home: Path) -> Path:
    """Return the installed icon-theme directory that carries the cursor."""
    return data_home / "icons" / CURSOR_THEME


def require_installed(data_home: Path) -> Path:
    """Return the installed theme, refusing a missing index or pointer."""
    theme = installed_theme(data_home)
    for path in (theme / "index.theme", theme / "cursors" / "left_ptr"):
        if not path.is_file():
            raise CursorError(
                f"installed cursor theme is missing {path}; run "
                "make install INSTALL_PACKAGES=icon-theme"
            )
    return theme


def link_target(home: Path) -> Path:
    """Return the Xcursor-path link that exposes the installed theme."""
    return home / ".icons" / CURSOR_THEME


def install_link(home: Path, theme: Path) -> None:
    """Create our Xcursor link, refusing to replace a foreign path."""
    icons = home / ".icons"
    target = link_target(home)
    if os.path.lexists(icons) and not icons.is_dir():
        raise CursorError(f"{icons} exists but is not a directory")
    if target.is_symlink():
        link = os.readlink(target)
        if link == str(theme):
            return
        raise CursorError(
            f"{target} is a symlink to {link}, not our installed theme; "
            "leaving it untouched"
        )
    if os.path.lexists(target):
        raise CursorError(
            f"{target} exists and is not our symlink; leaving it untouched"
        )
    try:
        icons.mkdir(parents=True, exist_ok=True)
        os.symlink(str(theme), str(target))
    except OSError as exc:
        raise CursorError(f"cannot create {target}: {exc}") from exc


def remove_link(home: Path, data_home: Path) -> tuple[Path, bool]:
    """Remove our link and return its path and whether a foreign path remains."""
    target = link_target(home)
    if target.is_symlink():
        if os.readlink(target) == str(installed_theme(data_home)):
            try:
                target.unlink()
            except OSError as exc:
                raise CursorError(f"cannot remove {target}: {exc}") from exc
            return target, False
        return target, True
    return target, os.path.lexists(target)
