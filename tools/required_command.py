"""Run a required external command and report its failure in the shared format.

A step a tool cannot do without -- ``apply_theme``'s required selections and
``apply_cursor``'s selector -- treats every failure the same way: a command
that ``PATH`` found but cannot start is the tool's exit-2 diagnostic, a
timeout or a non-zero exit is its exit-1 diagnostic with the command's log
tail, and any of them stops the run. :func:`run_required` supervises the
command with :func:`tools.process_group.run_logged` and returns the status to
exit with, so the three outcomes live here once instead of in each caller;
:func:`run_required_output` is its variant for command outputs that a caller
reads, where a merged stderr would corrupt the value.

A best-effort command (a missing Kvantum, an optional KWin reconfigure) does
not use this: its failure is a note and must not change the exit status.
"""

from __future__ import annotations

import signal
from pathlib import Path

if __package__:
    from tools.diagnostics import report_error, report_failure
    from tools.process_group import run_logged, run_logged_split
else:  # imported from a directly run tool
    from diagnostics import report_error, report_failure
    from process_group import run_logged, run_logged_split


def _signal_name(status: int) -> str:
    """Return the name of the signal that produced a negative wait status."""
    number = -status
    try:
        return signal.Signals(number).name
    except ValueError:
        return str(number)


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
    if not command or not command[0]:
        raise ValueError("run_required() requires a non-empty executable name")
    try:
        status = run_logged(command, env, log, timeout, cwd)
    except OSError as exc:
        return report_error(tool, f"cannot run {command[0]}: {exc}")
    if status is None:
        return report_failure(
            tool, f"{command[0]} timed out after {timeout:g}s", log
        )
    if status < 0:
        return report_failure(
            tool,
            f"{command[0]} killed by signal {_signal_name(status)}",
            log,
        )
    if status != 0:
        return report_failure(tool, f"{command[0]} exited {status}", log)
    return None


def _failure_log(stdout_log: Path, stderr_log: Path) -> Path:
    """Return the split log that can explain a failed command.

    A command's diagnostics are its stderr; only a drain that wrote nothing
    there falls back to its stdout, which is how the shared triage reports a
    failure whose log the caller reads. Both files always exist once the run
    has started, so an unreadable one is reported as an unreadable tail by
    :func:`tools.diagnostics.report_failure` on the fallback.
    """
    try:
        if stderr_log.stat().st_size:
            return stderr_log
    except OSError:
        pass
    return stdout_log


def run_required_output(
    tool: str,
    command: list[str],
    env: dict[str, str],
    stdout_log: Path,
    stderr_log: Path,
    timeout: float,
    cwd: Path,
) -> tuple[bytes, int | None]:
    """Run a required command and return its stdout; a failure returns a status.

    :func:`run_required` logs stdout and stderr merged, which is what every
    caller that never reads the streams wants. A caller that takes a value
    from stdout whose stderr warnings must not become part of the value needs
    the streams apart, so
    this variant logs them to *stdout_log* and *stderr_log*, returns the raw
    stdout bytes, and only reports a failure when the command failed. The
    failure triage is the shared one: the status plus the same exit-1 and
    exit-2 diagnostics, and on failure the log whose tail explains it. The
    caller owns the two log paths, so the logs land in its scratch directory
    rather than under names derived from ``command[0]``: an absolute
    executable path would otherwise redirect them out of that directory. A
    succeeding run removes both logs, so no stream is left on disk for a
    later step to mistake for the value; a removal that cannot succeed is
    ignored, because the value is already read and failing the run would
    discard it, and what the helper returns are the bytes the caller decodes.
    """
    if not command or not command[0]:
        raise ValueError(
            "run_required_output() requires a non-empty executable name"
        )
    try:
        status = run_logged_split(
            command, env, stdout_log, stderr_log, timeout, cwd
        )
    except OSError as exc:
        return b"", report_error(tool, f"cannot run {command[0]}: {exc}")
    log = _failure_log(stdout_log, stderr_log)
    if status is None:
        return b"", report_failure(
            tool, f"{command[0]} timed out after {timeout:g}s", log
        )
    if status < 0:
        return b"", report_failure(
            tool,
            f"{command[0]} killed by signal {_signal_name(status)}",
            log,
        )
    if status != 0:
        return b"", report_failure(
            tool, f"{command[0]} exited {status}", log
        )
    try:
        value = stdout_log.read_bytes()
    except OSError as exc:
        return b"", report_error(
            tool, f"cannot read {stdout_log.name}: {exc}"
        )
    for log in (stdout_log, stderr_log):
        try:
            log.unlink()
        except OSError:
            pass
    return value, None
