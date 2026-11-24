"""Diagnose a render's capture from its session log and its RGB plane.

After the session returns, the render workflow in :mod:`tools.render.workflow`
asks three questions: whether the captured RGB plane is entirely black,
whether the session log records the client dying mid-capture, and which log
tail to print on a painted pass. These checks read the log or the pixels and
decide nothing else, so they live here while the workflow only sequences them.
"""

from __future__ import annotations

import os
from pathlib import Path

if __package__.startswith("tools"):
    from tools.containment import open_regular_binary
    from tools.diagnostics import log_tail_lines, report_note
    from tools.render.session import CLIENT_EXITED_DURING_CAPTURE
else:  # run directly from render_surface.py
    from containment import open_regular_binary
    from diagnostics import log_tail_lines, report_note
    from render.session import CLIENT_EXITED_DURING_CAPTURE


def capture_is_unpainted(rgb: bytes) -> bool:
    """Return whether a capture's RGB plane is entirely black."""
    return not any(rgb)


def log_size(log: Path) -> str:
    """Return the log's size, ``missing`` when absent, or the stat error.

    Only a ``FileNotFoundError`` names an absent log: any other ``OSError``
    (an unreadable directory, a permission error) leaves the log in place,
    so reporting ``missing`` would send the operator looking for a file
    that exists but cannot be inspected; the error text names it instead.
    """
    try:
        return f"{log.stat().st_size} bytes"
    except FileNotFoundError:
        return "missing"
    except OSError as exc:
        return f"unreadable: {exc}"


def report_render_log(log: Path, tool: str) -> None:
    """Print the session log's last lines on stdout after a painted capture.

    A passing render discards its session log with the scratch directory, so
    a later pixel mismatch could not show which settle path ran. Printing the
    tail keeps that evidence in the run's own output; a log that cannot be
    read is reported in its place rather than failing a capture that painted.
    """
    try:
        lines = log_tail_lines(log)
    except (OSError, ValueError) as exc:
        report_note(tool, f"render log unreadable: {exc}")
        return
    report_note(tool, f"render log ({log_size(log)}), last lines:")
    for line in lines:
        report_note(tool, f"  {line}")


# How far into the session log the black-capture diagnosis looks for the
# client's exit marker: the marker is written after the capture command
# returns and before the reap line, so it sits at the log's end and a
# bounded tail covers it however chatty the client's own output was.
_EXIT_MARKER_TAIL_BYTES = 1 << 16


def client_exited_during_capture(log: Path) -> bool:
    """Return whether the session log recorded the client dying mid-capture.

    The session script prints :data:`CLIENT_EXITED_DURING_CAPTURE` when the
    client that passed the settle's liveness check is gone by the time the
    capture command returns; its window was destroyed before or while the
    frame was taken, so a black capture then names the vanished client, not
    an unpainted window. The read is a bounded tail like the failure
    report's, and an unreadable log keeps the generic diagnosis instead of
    failing the report.
    """
    try:
        with open_regular_binary(str(log)) as handle:
            handle.seek(0, os.SEEK_END)
            start = max(0, handle.tell() - _EXIT_MARKER_TAIL_BYTES)
            handle.seek(start)
            return CLIENT_EXITED_DURING_CAPTURE in handle.read(
                _EXIT_MARKER_TAIL_BYTES
            ).decode("utf-8", "replace")
    except (OSError, ValueError):
        # ValueError names a non-regular log (the open guard's FIFO or device
        # refusal), the same pair the failure report and the publish path
        # catch for this guard, so the generic diagnosis survives it too.
        return False
