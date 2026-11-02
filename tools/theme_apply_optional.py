"""The theme apply's optional external integrations.

The apply's required selections make the installed theme visible to the
running session and must not fail quietly; the Kvantum theme selection and
the KWin reconfigure are best-effort integrations with separate engines and
distinct missing-tool remedies, so their command policy lives here: every
failure -- a missing tool, one that cannot start, a timeout or a non-zero
exit -- is a note and never changes the apply's exit status. A successful run
prints nothing. ``tools/apply_theme.py`` imports
:func:`run_optional_selections` and calls it, after all required selections,
while it still holds the data-home lock and inside its scratch directory.

Usage from the apply::

    run_optional_selections(scratch, env, apply_theme.COMMAND_TIMEOUT)
"""

from __future__ import annotations

import shutil
from pathlib import Path

if __package__:
    from tools.diagnostics import report_note
    from tools.process_group import run_logged
    from tools.repo_root import ROOT
else:  # imported from a directly run tool
    from diagnostics import report_note
    from process_group import run_logged
    from repo_root import ROOT

TOOL = "apply_theme"
# The Kvantum theme name, i.e. the directory under ``theme/kvantum/`` that
# ``make install`` copies into Kvantum's search path. tests/test_apply_theme.py
# pins it to that shipped package so the two cannot drift.
KVANTUM_THEME = "org.macos8.desktop"


def _note(message: str) -> None:
    """Print ``apply_theme: note: <message>`` to stderr."""
    report_note(TOOL, message, err=True)


def run_best_effort(
    scratch: Path,
    env: dict[str, str],
    argv: list[str],
    log_name: str,
    command_timeout: float,
    *,
    label: str,
    consequence: str,
) -> None:
    """Run *argv*, noting a timeout, exit or start failure; never change the status.

    *label* names the command in the note and *consequence* completes the
    sentence with what happens because the command did not run. A command that
    ``shutil.which`` found can still fail to start (a corrupt binary, or a
    script whose interpreter is missing); ``run_logged`` reports that as an
    ``OSError``, and a best-effort selection must turn it into a note like any
    other failure rather than aborting the apply. The missing-tool note is the
    caller's, since each tool needs a different remedy. A successful run prints
    nothing.
    """
    log = scratch / log_name

    try:
        status = run_logged(argv, env, log, command_timeout, ROOT)
    except OSError as exc:
        _note(f"{label} could not be started: {exc}; {consequence}")
        return
    if status is None:
        _note(f"{label} timed out after {command_timeout:g}s; {consequence}")
    elif status != 0:
        _note(f"{label} exited {status}; {consequence}")


def reconfigure_kwin(scratch: Path, env: dict[str, str], command_timeout: float) -> int:
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
    run_best_effort(
        scratch,
        env,
        [qdbus, "org.kde.KWin", "/KWin", "reconfigure"],
        "qdbus.log",
        command_timeout,
        label="KWin reconfigure",
        consequence="KWin reloads the decoration on its next start",
    )
    return 0


def select_kvantum_theme(
    scratch: Path, env: dict[str, str], command_timeout: float
) -> int:
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
    run_best_effort(
        scratch,
        env,
        [manager, "--set", KVANTUM_THEME],
        "kvantummanager.log",
        command_timeout,
        label="kvantummanager --set",
        consequence="the widgets fall back to another style",
    )
    return 0


def run_optional_selections(
    scratch: Path, env: dict[str, str], command_timeout: float
) -> int:
    """Run the optional selections in the apply's existing order.

    Kvantum's selection first (a widget style the session picks up without a
    window-manager reload), then the KWin reconfigure (a hint whose failure
    the next KWin start repairs). Both are best-effort, so the return status
    is always 0.
    """
    select_kvantum_theme(scratch, env, command_timeout)
    return reconfigure_kwin(scratch, env, command_timeout)
