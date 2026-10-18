"""Install the built theme and re-apply it to the running Plasma session.

``make apply`` runs ``make install`` and then this script. It re-selects the
global theme, the color scheme and the desktop theme so Plasma and KDE
applications reread the freshly installed files without a logout, tells
Kvantum which of its installed themes to draw, and asks KWin to reconfigure
so the window decoration reloads. The startup splash is
read at login, so a splash change appears only on the next login.

The global theme is applied without ``--resetLayout``: Plasma replaces the
user's panels only when that flag is given, so applying the theme this way
leaves them alone. The color scheme and desktop theme are selected after the
global theme because ``lookandfeeltool`` applies the theme's defaults
wholesale; the explicit selections then hold whatever the user had chosen.

Usage::

    python3 tools/apply_theme.py

Exit status: 0 when the theme was applied, 1 when a required command failed,
2 for a usage error or a missing external tool.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

if __package__:
    from tools.cli import EscapingArgumentParser, report_failure, report_missing_tool
    from tools.process_group import exit_on_termination, run_logged
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/apply_theme.py
    from cli import EscapingArgumentParser, report_failure, report_missing_tool
    from process_group import exit_on_termination, run_logged
    from terminal import escape_controls

TOOL = "apply_theme"
ROOT = Path(__file__).resolve().parents[1]
LNF_ID = "org.macos8.desktop"
DTHEME_ID = "org.macos8.desktop"
COLOR_SCHEME = "MacOS8"
# The Kvantum theme name, i.e. the directory under ``theme/kvantum/`` that
# ``make install`` copies into Kvantum's search path. tests/test_apply_theme.py
# pins it to that shipped package so the two cannot drift.
KVANTUM_THEME = "org.macos8.desktop"

# The commands steps 1-3 need; a missing one is a hard error. qdbus and
# kvantummanager are not in this list: the KWin reconfigure and the Kvantum
# theme selection are best-effort, so a missing one only prints a note.
REQUIRED_TOOLS = (
    "lookandfeeltool",
    "plasma-apply-colorscheme",
    "plasma-apply-desktoptheme",
)
# Each required step as (tool name, argv), in the order it runs.
STEPS = (
    ("lookandfeeltool", ["lookandfeeltool", "-a", LNF_ID]),
    ("plasma-apply-colorscheme", ["plasma-apply-colorscheme", COLOR_SCHEME]),
    ("plasma-apply-desktoptheme", ["plasma-apply-desktoptheme", DTHEME_ID]),
)
COMMAND_TIMEOUT = 60.0


def _note(message: str) -> None:
    """Print ``apply_theme: note: <message>`` to stderr."""
    print(f"{TOOL}: note: {escape_controls(message)}", file=sys.stderr)


def _session_env() -> dict[str, str]:
    """Return ``os.environ`` with the session bus address defaulted if needed.

    A non-login shell (the local post-commit hook, for example) may run
    without ``DBUS_SESSION_BUS_ADDRESS`` set. When it is unset, the runtime
    directory is an absolute path, and ``$XDG_RUNTIME_DIR/bus`` exists, point
    the variable at that socket so the ``plasma-apply-*`` tools can reach the
    running session. Otherwise the environment is returned unchanged.
    """
    env = dict(os.environ)
    if env.get("DBUS_SESSION_BUS_ADDRESS"):
        return env
    runtime = env.get("XDG_RUNTIME_DIR", "")
    if os.path.isabs(runtime):
        bus = Path(runtime) / "bus"
        if bus.exists():
            env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={bus}"
    return env


def _run_best_effort(
    scratch: Path,
    env: dict[str, str],
    argv: list[str],
    log_name: str,
    *,
    label: str,
    consequence: str,
) -> None:
    """Run *argv*, noting a timeout or non-zero exit; never change the status.

    *label* names the command in the note and *consequence* completes the
    sentence with what happens because the command did not run. The missing-
    tool note is the caller's, since each tool needs a different remedy. A
    successful run prints nothing.
    """
    log = scratch / log_name
    status = run_logged(argv, env, log, COMMAND_TIMEOUT, ROOT)
    if status is None:
        _note(f"{label} timed out after {COMMAND_TIMEOUT:g}s; {consequence}")
    elif status != 0:
        _note(f"{label} exited {status}; {consequence}")


def _reconfigure_kwin(scratch: Path, env: dict[str, str]) -> int:
    """Ask KWin to reload the decoration; a failure is a note, never an error.

    The reconfigure is best-effort: KWin reloads the decoration on its next
    start anyway, so a missing qdbus6/qdbus, a timeout, or a non-zero exit
    only prints a note and leaves the exit status at 0.
    """
    qdbus = shutil.which("qdbus6") or shutil.which("qdbus")
    if qdbus is None:
        _note(
            "neither qdbus6 nor qdbus is on PATH; KWin reloads the decoration "
            "on its next start"
        )
        return 0
    _run_best_effort(
        scratch,
        env,
        [qdbus, "org.kde.KWin", "/KWin", "reconfigure"],
        "qdbus.log",
        label="KWin reconfigure",
        consequence="KWin reloads the decoration on its next start",
    )
    return 0


def _select_kvantum_theme(scratch: Path, env: dict[str, str]) -> int:
    """Select our Kvantum theme; a missing engine is a note, never an error.

    The global theme sets ``widgetStyle=kvantum``, but Kvantum draws whichever
    of its installed themes was selected last; this points it at ours. The
    selection is best-effort because Kvantum is a separate package the theme
    cannot install: without ``kvantummanager`` the widgets fall back to another
    style and the apply still succeeds.
    """
    manager = shutil.which("kvantummanager")
    if manager is None:
        _note(
            "kvantummanager is not on PATH; install Kvantum and choose its "
            f"{KVANTUM_THEME} theme in System Settings -> Application Style"
        )
        return 0
    _run_best_effort(
        scratch,
        env,
        [manager, "--set", KVANTUM_THEME],
        "kvantummanager.log",
        label="kvantummanager --set",
        consequence="the widgets fall back to another style",
    )
    return 0


def _apply() -> int:
    """Run the required steps, then the best-effort selections."""
    scratch = Path(tempfile.mkdtemp(prefix="apply-theme-"))
    try:
        env = _session_env()
        for tool, argv in STEPS:
            log = scratch / f"{tool}.log"
            status = run_logged(argv, env, log, COMMAND_TIMEOUT, ROOT)
            if status is None:
                return report_failure(
                    TOOL, f"{tool} timed out after {COMMAND_TIMEOUT:g}s", log
                )
            if status != 0:
                return report_failure(TOOL, f"{tool} exited {status}", log)
        _select_kvantum_theme(scratch, env)
        return _reconfigure_kwin(scratch, env)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    """Run the apply CLI; *argv* is the argument list without a program name."""
    parser = EscapingArgumentParser(
        prog="apply_theme",
        description=(
            "Install and re-apply the Mac OS 8.6 theme to the running Plasma "
            "session."
        ),
        epilog=(
            "exit status: 0 when the theme was applied, 1 when a required "
            "command failed, 2 usage error or missing external tool"
        ),
    )
    parser.parse_args(argv)

    missing = report_missing_tool(TOOL, REQUIRED_TOOLS)
    if missing is not None:
        return missing
    with exit_on_termination():
        return _apply()


if __name__ == "__main__":
    sys.exit(main())
