"""Install the built theme and re-apply it to the running Plasma session.

``make apply`` runs ``make install`` and then this script. It re-selects the
global theme, the color scheme and the desktop theme so Plasma and KDE
applications reread the freshly installed files without a logout, writes the
theme's window-button layout into `kwinrc` (the global theme's look-and-feel
apply drops those two keys, leaving KWin's stock right-hand cluster instead of
the reference's close box at the leading edge), tells Kvantum which of its
installed themes to draw, and asks KWin to reconfigure so the window
decoration reloads. The startup splash is read at login, so a splash change
appears only on the next login.

The global theme is applied without ``--resetLayout``: Plasma replaces the
user's panels only when that flag is given, so applying the theme this way
leaves them alone. The color scheme and desktop theme are selected after the
global theme because ``lookandfeeltool`` applies the theme's defaults
wholesale; the explicit selections then hold whatever the user had chosen.

The best-effort selections -- telling Kvantum which of its installed themes
to draw and asking KWin to reconfigure -- and their missing-tool and failure
policies live in ``apply_optional``; this module owns the required
selections, the decoration button layout, the locks and the exit status.

Usage::

    python3 tools/apply_theme.py

Exit status: 0 when the theme was applied, 1 when a required command failed,
2 for a usage error, an unusable HOME, a missing external tool, one that cannot
be started, a scratch directory that cannot be created, or another install or
uninstall holding the data-home lock past the wait, and 128 plus the signal
number when a SIGTERM or SIGHUP ends the run.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.diagnostics import (
        report_error,
        report_missing_tool,
        scratch_directory,
    )
    from tools.file_lock import installed_data_lock
    from tools import xdg_homes
    from tools.process_group import exit_on_termination
    from tools.repo_root import ROOT
    from tools.required_command import run_required
    from tools.session_bus import session_env
    from tools.apply_optional import run_optional_selections
else:  # run directly: python3 tools/apply_theme.py
    from argument_parsing import EscapingArgumentParser
    from diagnostics import (
        report_error,
        report_missing_tool,
        scratch_directory,
    )
    from file_lock import installed_data_lock
    import xdg_homes
    from process_group import exit_on_termination
    from repo_root import ROOT
    from required_command import run_required
    from session_bus import session_env
    from apply_optional import run_optional_selections

TOOL = "apply_theme"
LNF_ID = "org.macos8.desktop"
DTHEME_ID = "org.macos8.desktop"
COLOR_SCHEME = "MacOS8"


class ApplyError(Exception):
    """An apply that cannot run: the data home the selections need is unusable."""

# The commands steps 1-3 need; a missing one is a hard error. qdbus and
# kvantummanager are not in this list: the KWin reconfigure and the Kvantum
# theme selection are best-effort (apply_optional), so a missing one
# only prints a note.
REQUIRED_TOOLS = (
    "lookandfeeltool",
    "plasma-apply-colorscheme",
    "plasma-apply-desktoptheme",
    "kwriteconfig6",
)
# The window decoration's button layout, written after the global theme so a
# look-and-feel apply cannot reset it. The values are the global theme's own
# `contents/defaults` ([kwinrc][org.kde.kdecoration2]); tests/test_apply_theme.py
# pins the pair to that file. The Mac OS 8.6 reference window puts the close box
# at the leading edge and the zoom/collapse boxes at the trailing edge, and the
# theme's defaults name exactly those buttons (X; A, L).
DECORATION_FILE = "kwinrc"
DECORATION_GROUP = "org.kde.kdecoration2"
DECORATION_BUTTONS = (("ButtonsOnLeft", "X"), ("ButtonsOnRight", "AL"))
# Each required step's argv, in the order it runs; argv[0] names the tool.
STEPS = (
    ["lookandfeeltool", "-a", LNF_ID],
    ["plasma-apply-colorscheme", COLOR_SCHEME],
    ["plasma-apply-desktoptheme", DTHEME_ID],
    *(
        [
            "kwriteconfig6",
            "--file",
            DECORATION_FILE,
            "--group",
            DECORATION_GROUP,
            "--key",
            key,
            value,
        ]
        for key, value in DECORATION_BUTTONS
    ),
)
COMMAND_TIMEOUT = 60.0
# The wait for the data-home lock matches make install/uninstall's own
# FLOCK_TIMEOUT default, so a holder stopped with SIGSTOP cannot block this
# run forever either.
LOCK_TIMEOUT = 60.0


def _apply(data_home: Path, environ: dict[str, str]) -> int:
    """Run the required steps, then the best-effort selections."""
    with scratch_directory(TOOL, "apply-theme-") as scratch:
        if scratch is None:
            return 2
        # Hold the data-home lock make install/uninstall hold across the
        # selections: lookandfeeltool, plasma-apply-* and the best-effort
        # kvantummanager all read installed packages a concurrent uninstall
        # can otherwise remove between and after these selections, leaving a
        # selection that silently falls back with no diagnostic. Taking the
        # same flock orders apply against uninstall: a theme removed before
        # this run wins the lock makes the next required step fail loudly.
        with installed_data_lock(
            data_home, "for the theme apply", LOCK_TIMEOUT, error=ApplyError
        ):
            env = session_env(environ)
            status = _run_required_steps(scratch, env)
            if status is not None:
                return status
            run_optional_selections(scratch, env, COMMAND_TIMEOUT)
            return 0


def _run_required_steps(scratch: Path, env: dict[str, str]) -> int | None:
    """Run each required step in order; return the first failing status, else None."""
    for argv in STEPS:
        status = run_required(
            TOOL,
            argv,
            env,
            scratch / f"{argv[0]}.log",
            COMMAND_TIMEOUT,
            ROOT,
        )
        if status is not None:
            return status
    return None


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
            "command failed, 2 usage error, an unusable HOME, a missing "
            "external tool, one that cannot be started, a scratch directory "
            "that cannot be created, or another install or uninstall holding "
            "the data-home lock past the wait, and 128 plus the signal number "
            "when a SIGTERM or SIGHUP ends the run"
        ),
    )
    parser.parse_args(argv)

    missing = report_missing_tool(TOOL, REQUIRED_TOOLS)
    if missing is not None:
        return missing
    with exit_on_termination():
        try:
            data_home = xdg_homes.data_home(dict(os.environ))
            if data_home is None:
                raise ApplyError(
                    "HOME is unset or not an absolute path, so the data home "
                    "make install and make uninstall serialize on cannot be "
                    "resolved; export an absolute HOME"
                )
            return _apply(data_home, dict(os.environ))
        except ApplyError as exc:
            return report_error(TOOL, str(exc))


if __name__ == "__main__":
    sys.exit(main())
