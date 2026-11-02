"""Install and configure the theme inside a render's scratch session."""

from __future__ import annotations

from pathlib import Path

if __package__:
    from tools.atomic_write import write_bytes_atomically
    from tools.process_group import run_logged
    from tools.render_session import Session
    from tools.repo_root import ROOT
    from tools.theme_defaults import write_configs
else:  # run directly from render_surface.py
    from atomic_write import write_bytes_atomically
    from process_group import run_logged
    from render_session import Session
    from repo_root import ROOT
    from theme_defaults import write_configs

# Config files supplied by the global theme's defaults that the color-scheme
# command does not write itself.
CONFIG_FILES = ("kwinrc", "plasmarc")
KVANTUM_THEME = "org.macos8.desktop"
INSTALL_TIMEOUT = 60.0


def link_kvantum_themes(session: Session) -> tuple[OSError | None, Path]:
    """Link the scratch home's themes path after the scratch install."""
    themes = session.home / ".local" / "share" / "themes"
    try:
        (session.home / ".local" / "share").mkdir(parents=True, exist_ok=False)
        themes.symlink_to(session.data / "themes")
    except OSError as exc:
        return exc, themes
    return None, themes


def install_theme(session: Session) -> tuple[int | None, Path]:
    """Run ``make install`` into *session*'s data home and return its result."""
    status = run_logged(
        ["make", "install", f"XDG_DATA_HOME={session.data}"],
        session.environment,
        session.install_log,
        INSTALL_TIMEOUT,
        ROOT,
    )
    return status, session.install_log


def write_session_configs(session: Session, files: tuple[str, ...] = CONFIG_FILES) -> None:
    """Write the global theme's config defaults into the scratch config home."""
    write_configs(session.config, files)


def write_kvantum_selection(session: Session) -> None:
    """Select the Kvantum theme in the scratch config home for Qt clients."""
    directory = session.config / "Kvantum"
    directory.mkdir(parents=True, exist_ok=True)
    write_bytes_atomically(
        directory / "kvantum.kvconfig",
        f"[General]\ntheme={KVANTUM_THEME}\n".encode("utf-8"),
    )
