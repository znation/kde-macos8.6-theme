"""Prepare and launch the throwaway KWin session a render runs in.

The render CLI keeps one job -- parse its options, publish the capture and
report failures -- while this module owns everything that must exist only for
one render: the scratch XDG directories, the environment that points the
session at them, the theme install, the session config files and the command
that starts KWin, opens the applet and captures the surface.

The scratch root is created by :meth:`Session.create` and removed by the
context manager, whether the render succeeds or fails.
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
    "XDG_CONFIG_DIRS",
)


@dataclass(frozen=True)
class Session:
    """The scratch layout, environment and logs of one render session."""

    root: Path
    runtime: Path
    config: Path
    data: Path
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
            data = root / "data"
            for directory in (runtime, config, data):
                directory.mkdir()
            runtime.chmod(0o700)
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
            )
        except BaseException:
            shutil.rmtree(root, ignore_errors=True)
            raise
        return cls(
            root=root,
            runtime=runtime,
            config=config,
            data=data,
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
    """Return the ``sh -c`` script that opens the applet, settles and captures.

    The positional parameters are the applet id, the settle seconds and the
    output path, so ``sh`` receives them after the script and never parses
    them as shell syntax. The script fails the session if the backgrounded
    applet is no longer running after the settle; without that check
    ``spectacle`` would still publish a capture of an empty session.
    """
    # `plasmawindowed` runs in the background, so its exit status would
    # otherwise be lost: if it cannot start or crashes during the settle wait,
    # `spectacle` still captures the empty session and reports success,
    # publishing a render of no window. The liveness check therefore runs
    # before the capture and fails the session with a log line naming
    # `plasmawindowed` instead.
    return (
        f"plasma-apply-colorscheme {COLOR_SCHEME} || exit 1; "
        'plasmawindowed "$1" & applet=$!; '
        'sleep "$2"; '
        'if ! kill -0 "$applet" 2>/dev/null; then '
        'echo "plasmawindowed exited before the capture" >&2; exit 1; fi; '
        'spectacle -b -n -f -o "$3"; status=$?; '
        'kill "$applet" 2>/dev/null; '
        "exit $status"
    )


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


def write_session_configs(session: Session) -> None:
    """Write the global theme's config defaults into the scratch config home."""
    write_configs(session.config, CONFIG_FILES)


def session_command(
    session: Session,
    applet: str,
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
            applet,
            str(settle),
            str(session.surface),
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
