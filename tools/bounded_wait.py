"""Bounded waits that name the wait that expired.

A bare ``process.wait(timeout=...)`` raises ``TimeoutExpired`` with no hint of
which step timed out, and a caller that maps the timeout to ``None`` loses even
that. :func:`wait_bounded` raises :class:`WaitExpired`, whose message carries
the caller's label, so the next failure names the wait that expired.
"""

from __future__ import annotations

import subprocess


class WaitExpired(TimeoutError):
    """A bounded wait ran out of time; ``str()`` names the wait and its budget."""


def wait_bounded(process: subprocess.Popen, timeout: float, label: str) -> int:
    """Wait up to *timeout* seconds for *process* and return its exit status.

    Raises :class:`WaitExpired` naming *label* and *timeout* if the process is
    still running when the budget runs out. The process is left running: the
    caller decides whether to kill it.
    """
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise WaitExpired(
            f"{label} did not finish within {timeout:g}s (pid {process.pid})"
        ) from exc
