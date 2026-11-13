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
can find no theme and draws its compiled-in default instead. The link is
made after the theme's scratch install (:func:`link_kvantum_themes`), not
by :meth:`Session.create`: at creation the data home holds no ``themes/``
directory yet, so a creation-time link could point at nothing.
"""

from __future__ import annotations

import os
import shlex
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

SOCKET = "render-surface"
COLOR_SCHEME = "MacOS8"

# The session-log marker for a client that was alive at the settle's
# liveness check but died before the capture command returned. Such a
# client's window was destroyed before or while the frame was taken, so a
# black capture of that session is a vanished client, not an unpainted
# one -- the render's black-capture diagnosis greps this marker (near the
# log's end, written after the capture returns and before the reap) to
# name that cause instead of blaming the paint budget.
CLIENT_EXITED_DURING_CAPTURE = "render-session: client exited during the capture"


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
            surface = root / "surface.png"

            # DESTDIR must not reach the install: the theme has to land in the
            # scratch data home. It arrives both as an environment variable
            # and, when the caller ran `make DESTDIR=... render`, through
            # MAKEFLAGS, which the child make imports as a command-line
            # override.
            dropped_environment = (
                "WAYLAND_DISPLAY", "DISPLAY", "DESTDIR", "MAKEFLAGS",
                "MAKEFILES", "XDG_CONFIG_DIRS",
            )
            environment = {
                key: value
                for key, value in os.environ.items()
                if key not in dropped_environment
            }
            environment.update(
                XDG_RUNTIME_DIR=str(runtime),
                # The host's display must not leak, but the nested session
                # still needs a display of its own: the private bus
                # `dbus-run-session` starts hands this environment to every
                # service it activates, and a GUI service started without a
                # display (KWin asks for the settings portal during startup)
                # aborts in QGuiApplication and D-Bus retries it in a
                # core-dump loop.
                WAYLAND_DISPLAY=SOCKET,
                QT_QPA_PLATFORM="offscreen",
                # The private bus hands this environment to every service it
                # D-Bus-activates, and those services must not try to open
                # WAYLAND_DISPLAY=SOCKET: while the nested KWin socket is not
                # yet listening (or after KWin exits) an activating Qt service
                # such as xdg-desktop-portal-kde aborts in QGuiApplication and
                # the bus re-activates it in a coredump loop. Pin the whole
                # nested bus subtree to a display-free platform here; the
                # session script below overrides it to "wayland" for the
                # clients that must draw on the nested compositor, and KWin
                # itself selects its virtual backend from --virtual.
                # KWin 6.6 refuses ScreenShot2 calls from a process it cannot
                # map to a desktop-file identity. This throwaway compositor
                # and its private bus have no such identity to offer, so the
                # capture is refused before Spectacle can write the PNG.
                # Disable the check only for this scratch session.
                KWIN_SCREENSHOT_NO_PERMISSION_CHECKS="1",
                # Spectacle constructs its Wayland video platform even for a
                # still capture; that path binds KWin's screencast interface
                # and starts PipeWire, which the headless runner does not run.
                # A still render has no video platform, so force Spectacle's
                # null one (its documented testing override) in this session.
                SPECTACLE_VIDEO_PLATFORM="VideoPlatformNull",
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

    Every stage logs a millisecond timestamp, so a failed capture's log
    shows the client's start, the settle's end and the capture's span on
    one wall clock. After the capture returns, the script records whether
    the client was still running: a client that died between the settle's
    liveness check and the capture's end took its window with it, and its
    timestamped exit marker is what lets the black-capture diagnosis
    distinguish a vanished client from a window that never painted.

    The client that passed the liveness check is frozen with SIGSTOP
    before the capture starts and resumed with SIGCONT immediately before
    the post-capture termination: Spectacle's startup latency is unbounded
    under concurrent renders, while a client such as ``ksplashqml --test``
    has a finite lifetime, so an unfrozen client could take its window
    down mid-capture. A stopped client keeps its last-painted buffer —
    the compositor captures from it — and the aliveness check after the
    capture still reads it (a stopped process answers ``kill -0``), so
    the diagnosis and the ``kill -9`` fallback are unchanged. The shell
    also exports the client's pid as ``RENDER_SESSION_CLIENT_PID``: a
    capture-side helper can only target the client through a pid the
    session shell owns, because the freeze can land before the client's
    first instruction and a pidfile the client was meant to write then
    never appears.
    """
    # The client runs in the background, so its exit status would otherwise
    # be lost: if it cannot start or crashes during the settle wait,
    # `spectacle` still captures the empty session and reports success,
    # publishing a render of no window. The liveness check therefore runs
    # before the capture and fails the session with a log line naming the
    # client's first word instead.
    return (
        # Qt selects its platform plugin from the ambient session type, which
        # a headless caller does not set even though this session exports its
        # own WAYLAND_DISPLAY. Pin the clients to the nested compositor's
        # Wayland socket here, inside the session shell only, so the choice
        # cannot fall through to xcb and abort before the client is visible.
        "export QT_QPA_PLATFORM=wayland; "
        f"plasma-apply-colorscheme {COLOR_SCHEME} || exit 1; "
        'settle="$1"; capture="$2"; shift 2; '
        'started=$(date +%s%3N); "$@" & client=$!; '
        'export RENDER_SESSION_CLIENT_PID="$client"; '
        'echo "render-session: client started at $started" >&2; '
        'sleep "$settle"; '
        'echo "render-session: settle done at $(date +%s%3N)" >&2; '
        'if ! kill -0 "$client" 2>/dev/null; then '
        'echo "$1 exited before the capture" >&2; exit 1; fi; '
        'if kill -STOP "$client" 2>/dev/null; then '
        'echo "render-session: client held at $(date +%s%3N)" >&2; fi; '
        'echo "render-session: capturing at $(date +%s%3N)" >&2; '
        'spectacle -b -n -f -o "$capture"; status=$?; '
        'capture_done=$(date +%s%3N); '
        'echo "render-session: capture status $status at $capture_done" >&2; '
        'if kill -0 "$client" 2>/dev/null; then '
        'echo "render-session: client alive after the capture at $capture_done" >&2; '
        'else '
        f'echo "{CLIENT_EXITED_DURING_CAPTURE} at $capture_done" >&2; fi; '
        'kill -CONT "$client" 2>/dev/null; '
        'kill "$client" 2>/dev/null; '
        'waited=0; '
        'while kill -0 "$client" 2>/dev/null && [ "$waited" -lt 50 ]; do '
        'sleep 0.1; waited=$((waited + 1)); done; '
        'kill -9 "$client" 2>/dev/null; '
        'wait "$client" 2>/dev/null; '
        'echo "render-session: client reaped" >&2; '
        "exit $status"
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
