"""Run a required external command and report its failure in the shared format.

A step a tool cannot do without -- ``apply_theme``'s required selections and
``apply_cursor``'s selector -- treats every failure the same way: a command
that ``PATH`` found but cannot start is the tool's exit-2 diagnostic, a
timeout or a non-zero exit is its exit-1 diagnostic with the command's log
tail, and any of them stops the run. :func:`run_required` supervises the
command with :func:`tools.process_group.run_logged` and returns the status to
exit with, so the three outcomes live here once instead of in each caller.

A best-effort command (a missing Kvantum, an optional KWin reconfigure) does
not use this: its failure is a note and must not change the exit status.
"""

from __future__ import annotations

import signal
from pathlib import Path

if __package__:
    from tools.diagnostics import report_error, report_failure
    from tools.process_group import run_logged
else:  # imported from a directly run tool
    from diagnostics import report_error, report_failure
    from process_group import run_logged


def run_required(
    tool: str,
    command: list[str],
    env: dict[str, str],
    log: Path,
    timeout: float,
    cwd: Path,
) -> int | None:
    """Run *command* and return the exit status to report, or None on success.

    *tool* names the calling tool in the diagnostic and *log* receives the
    command's output. ``run_logged`` reports a command that ``PATH`` found but
    cannot start as an ``OSError``; that is as unusable as a missing one, so
    it becomes the tool's exit-2 :func:`report_error` diagnostic instead of a
    traceback. A timeout (``None`` from ``run_logged``) and a non-zero exit
    become exit-1 :func:`report_failure` diagnostics naming ``command[0]``,
    with the log tail. The caller returns the result directly, so a failed
    required command stops the run.
    """
    try:
        status = run_logged(command, env, log, timeout, cwd)
    except OSError as exc:
        return report_error(tool, f"cannot run {command[0]}: {exc}")
    if status is None:
        return report_failure(
            tool, f"{command[0]} timed out after {timeout:g}s", log
        )
    if status < 0:
        number = -status
        try:
            name = signal.Signals(number).name
        except ValueError:
            name = str(number)
        return report_failure(tool, f"{command[0]} killed by signal {name}", log)
    if status != 0:
        return report_failure(tool, f"{command[0]} exited {status}", log)
    return None
