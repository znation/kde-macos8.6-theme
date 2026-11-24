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

try:
    from tools.diagnostics import report_note
    from tools.render.session_script import session_script
except ImportError:  # imported from a directly run tool
    from diagnostics import report_note
    from render.session_script import session_script

SOCKET = "render-surface"
COLOR_SCHEME = "MacOS8"
CLIENT_EXITED_DURING_CAPTURE = "render-session: client exited during the capture"


def _remove_scratch_root(root: Path) -> None:
    """Remove the scratch *root*; a failure is reported, not raised.

    A removal that fails leaves the session's files behind on disk, so the
    note names that leftover path and the error on stderr. It does not raise:
    the caller is already finishing a render, and that render's own outcome
    (a failure it reports, or the exception it is unwinding) must stay the one
    the operator sees.
    """
    errors: list[OSError] = []
    # A handler that returns lets rmtree go on to the remaining entries, so
    # one undeletable or vanished entry leaves only itself behind. Python 3.10
    # has no ``onexc``.
    shutil.rmtree(root, onerror=lambda _func, _path, info: errors.append(info[1]))
    if errors and os.path.lexists(root):
        report_note(
            "render_surface",
            f"could not remove scratch session directory {root}: {errors[0]}",
            err=True,
        )


def _session_directories(root: Path) -> tuple[Path, Path, Path, Path, Path]:
    runtime, config, data = (root / name for name in ("rt", "cfg", "data"))
    home = root / "home"
    home.mkdir()
    for directory in (runtime, config, data):
        directory.mkdir()
    runtime.chmod(0o700)
    return runtime, config, data, home, root / "surface.png"


def _session_environment(runtime: Path, config: Path, data: Path, home: Path) -> dict[str, str]:
    dropped_environment = {
        "WAYLAND_DISPLAY", "DISPLAY", "DESTDIR", "MAKEFLAGS", "MAKEFILES",
        "XDG_CONFIG_DIRS", "LANGUAGE",
    }
    environment = {
        key: value for key, value in os.environ.items()
        if key not in dropped_environment
    }
    environment.update(
        XDG_RUNTIME_DIR=str(runtime), WAYLAND_DISPLAY=SOCKET,
        QT_QPA_PLATFORM="offscreen", KWIN_SCREENSHOT_NO_PERMISSION_CHECKS="1",
        SPECTACLE_VIDEO_PLATFORM="VideoPlatformNull",
        XDG_CONFIG_HOME=str(config), XDG_DATA_HOME=str(data), HOME=str(home),
        LANG=MEASUREMENT_LOCALE, LC_ALL=MEASUREMENT_LOCALE,
    )
    return environment

# The locale the scratch session pins over the caller's. A client's
# layout follows the caller shell's LANG/LC_*: kdialog starts the
# calendar's day grid on the locale's first day of week, and Qt's C
# locale -- what an unset LANG gives -- is Monday-first, while every
# dialog capture pin was measured under this host's en_US default
# (Sunday-first grid). A caller without that default therefore shifts
# the whole grid one column left and turns the calendar gates' red
# Sunday-ink pins dark, gray and white. Qt derives the locale from the
# string alone, and a host that has not generated it only degrades
# glibc's setlocale to C with a warning, so the pin never fails a
# render. ``LANGUAGE`` is dropped with the rest: it overrides the
# message catalogs for Qt and KDE clients regardless of LC_ALL, and the
# measured captures show the untranslated English client strings.
MEASUREMENT_LOCALE = "en_US.UTF-8"

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
            runtime, config, data, home, surface = _session_directories(root)
            environment = _session_environment(runtime, config, data, home)
        except BaseException:
            _remove_scratch_root(root)
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
        """Remove the scratch root; a leftover is named on stderr, not raised."""
        _remove_scratch_root(self.root)

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




def session_command(
    session: Session,
    client: list[str] | tuple[str, ...],
    settle: float,
    width: int,
    height: int,
    timeout: float,
    focus_script: str | None = None,
    readiness_script: str | None = None,
) -> SessionCommand:
    """Build the KWin session command for *session* and its supervision timeout.

    The settle script paths ride to :func:`session_script`.
    """
    script = shlex.join(
        [
            "sh",
            "-c",
            session_script(focus_script, readiness_script),
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
