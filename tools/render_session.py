"""Prepare and launch the throwaway KWin session a render runs in.

The render CLI keeps one job -- parse its options, publish the capture and
report failures -- while this module owns everything that must exist only for
one render: the scratch XDG directories, the environment that points the
session at them, the theme install, the session config files and the command
that starts KWin, opens the applet and captures the surface.

The scratch root is created by :meth:`Session.create` and removed by the
context manager, whether the render succeeds or fails.

The scratch session also gets a ``HOME`` of its own: Kvantum searches its
theme under ``$HOME/.local/share/themes/`` with that literal path, so the
scratch home links ``.local/share/themes`` to the scratch data home's
``themes/``, which ``make install`` populates. Without that link Kvantum
can find no theme and draws its compiled-in default instead.
"""

from __future__ import annotations

import os
import shlex
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

if __package__:
    from tools.process_group import run_logged
    from tools.repo_root import ROOT
    from tools.theme_defaults import write_configs
else:  # run directly: python3 tools/render_surface.py
    from process_group import run_logged
    from repo_root import ROOT
    from theme_defaults import write_configs

# The config files the global theme's defaults feed that `plasma-apply-colorscheme`
# does not write. The render applies the colour scheme in the session and leaves the
# `[kdeglobals][KDE] widgetStyle` default unapplied.
CONFIG_FILES = ("kwinrc", "plasmarc")
COLOR_SCHEME = "MacOS8"
KVANTUM_THEME = "org.macos8.desktop"
SOCKET = "render-surface"
INSTALL_TIMEOUT = 60.0

# The caller's display, staging and config-search settings must not reach the
# session: it starts its own virtual display, installs into the scratch data
# home, and reads configuration only from the scratch config home.
_DROPPED_ENVIRONMENT = (
    "WAYLAND_DISPLAY",
    "DISPLAY",
    "DESTDIR",
    "MAKEFLAGS",
    "MAKEFILES",
    "XDG_CONFIG_DIRS",
)


@dataclass(frozen=True)
class Session:
    """The scratch layout, environment and logs of one render session."""

    root: Path
    runtime: Path
    config: Path
    data: Path
    home: Path
    surface: Path
    install_log: Path
    render_log: Path
    environment: dict[str, str]

    @classmethod
    def create(cls) -> "Session":
        """Create a fresh scratch session, removing it if setup fails."""
        root = Path(tempfile.mkdtemp(prefix="render-surface-"))
        try:
            runtime = root / "rt"
            config = root / "cfg"
            home = root / "home"
            home.mkdir()
            data = root / "data"
            for directory in (runtime, config, data):
                directory.mkdir()
            runtime.chmod(0o700)
            # `KVANTUM_THEME` reaches the session only through the literal
            # `HOME`-joined path documented in the README, so link the scratch
            # home's themes into the scratch data home the install targets.
            data_themes = data / "themes"
            kvantum_themes = home / ".local" / "share" / "themes"
            if data_themes.is_dir() and not kvantum_themes.exists():
                kvantum_themes.symlink_to(data_themes)
            surface = root / "surface.png"

            # DESTDIR must not reach the install: the theme has to land in the
            # scratch data home. It arrives both as an environment variable
            # and, when the caller ran `make DESTDIR=... render`, through
            # MAKEFLAGS, which the child make imports as a command-line
            # override.
            environment = {
                key: value
                for key, value in os.environ.items()
                if key not in _DROPPED_ENVIRONMENT
            }
            environment.update(
                XDG_RUNTIME_DIR=str(runtime),
                XDG_CONFIG_HOME=str(config),
                XDG_DATA_HOME=str(data),
                HOME=str(home),
            )
        except BaseException:
            shutil.rmtree(root, ignore_errors=True)
            raise
        return cls(
            root=root,
            runtime=runtime,
            config=config,
            data=data,
            home=home,
            surface=surface,
            install_log=root / "install.log",
            render_log=root / "render.log",
            environment=environment,
        )

    def cleanup(self) -> None:
        """Remove the scratch root, leaving no session files behind."""
        shutil.rmtree(self.root, ignore_errors=True)

    def __enter__(self) -> "Session":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.cleanup()


@dataclass(frozen=True)
class SessionCommand:
    """The session argv, its log and the timeout that supervises it."""

    argv: list[str]
    log: Path
    timeout: float


def session_script() -> str:
    """Return the ``sh -c`` script that opens the client, settles and captures.

    The positional parameters are the settle seconds, the capture path and
    the client argv itself, so ``sh`` receives them after the script and
    never parses them as shell syntax: the client words are passed through
    ``shlex``-joined child ``sh -c`` argv, each a separate positional word
    of this script. The script fails the session if the backgrounded
    client is no longer running after the settle; without that check
    ``spectacle`` would still publish a capture of an empty session.
    """
    # The client runs in the background, so its exit status would otherwise
    # be lost: if it cannot start or crashes during the settle wait,
    # `spectacle` still captures the empty session and reports success,
    # publishing a render of no window. The liveness check therefore runs
    # before the capture and fails the session with a log line naming the
    # client's first word instead.
    return (
        f"plasma-apply-colorscheme {COLOR_SCHEME} || exit 1; "
        'settle="$1"; capture="$2"; shift 2; '
        '"$@" & client=$!; '
        'sleep "$settle"; '
        'if ! kill -0 "$client" 2>/dev/null; then '
        'echo "$1 exited before the capture" >&2; exit 1; fi; '
        'spectacle -b -n -f -o "$capture"; status=$?; '
        'kill "$client" 2>/dev/null; '
        "exit $status"
    )


def link_kvantum_themes(session: Session) -> tuple[OSError | None, Path]:
    """Link the scratch home's ``themes`` onto the data home's.

    Kvantum searches its theme themes under the literal
    ``$HOME/.local/share/themes/`` path the README records, which the scratch
    ``XDG_DATA_HOME`` does not satisfy: the session home is linked so the
    engine reads the same theme directory ``make install`` populated.
    """
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
    """Select ``KVANTUM_THEME`` in the scratch config home for Qt clients.

    Plasma applets draw through the desktop theme, but every other Qt
    client (``kdialog`` and friends) reads ``widgetStyle=kvantum`` from
    ``kdeglobals``, then the Kvantum engine reads its selected theme name
    from this file. Without the name the engine falls back to its
    compiled-in default theme.
    """
    directory = session.config / "Kvantum"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "kvantum.kvconfig").write_text(
        f"[General]\ntheme={KVANTUM_THEME}\n", encoding="utf-8"
    )


def checkbox_dialog_client(session: Session) -> tuple[str, ...]:
    """Return the Qt client argv the widget gate renders.

    A ``kdialog`` warning whose ``--dontagain`` check box is a real
    ``QCheckBox``: the engine draws its indicator through this theme's
    ``checkbox-*`` art and ``check_size``, the pixels the widget gate
    byte-compares. The ``--dontagain`` config file lands in the scratch
    config home, never the caller's.
    """
    dontagain = session.config / "kde-dontagain"
    return (
        "kdialog",
        "--title",
        "Test",
        "--warningyesno",
        "Delete?",
        "--dontagain",
        f"{dontagain}:widgets",
    )


def combobox_dialog_client(_session: Session) -> tuple[str, ...]:
    """Return the Qt client argv the combo arrow gate renders.

    A ``kdialog`` chooser with a real ``QComboBox``: the engine draws its
    indicator through this theme's ``comboarrow-*`` art and
    ``[ComboBox] indicator.size``, the pixels the widget gate byte-compares.
    The session argument is taken for symmetry with the other dialog client
    and for future clients that write scratch config files; the combo dialog
    itself needs none.
    """
    return (
        "kdialog",
        "--title",
        "Test",
        "--combobox",
        "Choose a disk:",
        "Macintosh HD",
        "Zip Disk",
    )


def session_command(
    session: Session,
    client: list[str] | tuple[str, ...],
    settle: float,
    width: int,
    height: int,
    timeout: float,
) -> SessionCommand:
    """Build the KWin session command for *session* and its supervision timeout."""
    script = shlex.join(
        [
            "sh",
            "-c",
            session_script(),
            "sh",
            str(settle),
            str(session.surface),
            *client,
        ]
    )
    return SessionCommand(
        argv=[
            "dbus-run-session",
            "--",
            "kwin_wayland",
            "--virtual",
            "--no-lockscreen",
            "--width",
            str(width),
            "--height",
            str(height),
            "--socket",
            SOCKET,
            "--exit-with-session",
            script,
        ],
        log=session.render_log,
        timeout=timeout,
    )
