"""Install and configure the theme inside a render's scratch session."""

from __future__ import annotations

from pathlib import Path

if __package__:
    from tools.atomic_write import write_bytes_atomically
    from tools.gtk_selection import ConfigError as _ConfigError  # noqa: F401 (re-exported)
    from tools.gtk_selection import apply as _gtk_apply
    from tools.gtk_selection import installed_sheets as _gtk_installed_sheets
    from tools.process_group import run_logged
    from tools.render_session import Session
    from tools.repo_root import ROOT
    from tools.theme_defaults import write_configs
else:  # run directly from render_surface.py
    from atomic_write import write_bytes_atomically
    from gtk_selection import ConfigError as _ConfigError
    from gtk_selection import apply as _gtk_apply, installed_sheets as _gtk_installed_sheets
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


def write_desktop_selection(session: Session) -> None:
    """Select the look-and-feel in the scratch config home for plasmashell.

    Writes the selection keys the published apply records (``[KDE]
    LookAndFeelPackage=org.macos8.desktop``) into both ``plasmarc`` and
    ``kdeglobals``. The session configs the defaults writer just published
    are appended to, not replaced, so their own sections (``plasmarc``'s
    ``[Theme]`` name) survive the selection.
    """
    selection = f"[KDE]\nLookAndFeelPackage={KVANTUM_THEME}\n".encode("utf-8")
    for name in ("plasmarc", "kdeglobals"):
        path = session.config / name
        try:
            existing = path.read_bytes()
        except FileNotFoundError:
            existing = b""
        # Keep the appended group on its own line even when the file does
        # not end in a newline.
        joiner = b"" if (not existing or existing.endswith(b"\n")) else b"\n"
        write_bytes_atomically(path, existing + joiner + selection)


def write_kvantum_selection(session: Session) -> None:
    """Select the Kvantum theme in the scratch config home for Qt clients."""
    directory = session.config / "Kvantum"
    directory.mkdir(parents=True, exist_ok=True)
    write_bytes_atomically(
        directory / "kvantum.kvconfig",
        f"[General]\ntheme={KVANTUM_THEME}\n".encode("utf-8"),
    )


def install_gtk_selection(session: Session) -> None:
    """Select the GTK themes in the scratch config home for GTK clients.

    This is the existing ``apply-gtk`` selection transaction pointed at the
    scratch homes: both installed sheets must exist below the scratch data
    home, and ``apply`` publishes the settings theme-name keys and the user
    CSS into the scratch config home. The scratch config home is fresh, so
    the selection never finds a foreign user CSS to back up and the note
    callback never fires; it is routed to a discard for that reason alone.
    Raises :class:`ConfigError` where ``apply`` raises one, and when the
    scratch install left a sheet missing.
    """
    sheets = _gtk_installed_sheets(session.data)
    if sheets is None:
        raise _ConfigError(
            "the scratch install left a GTK sheet missing; the zenity "
            "client would start unthemed"
        )
    _gtk_apply(sheets, session.config, lambda _note: None)
