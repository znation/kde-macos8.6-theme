"""The Popen-return signal race the process-group suites share.

`Popen` is the exact point where a real signal can arrive before
`exit_on_termination` enters its try/finally, so the process-group suites
patch `subprocess.Popen` with a wrapper that starts the real child and then
sends *number* to this process: the signal is delivered deterministically on
the return path the suites race, and the py-code-side signal handler records
and replays it like any other. The race helpers here are one shared copy of
the inline closures these suites used to restate; `kill_tracked` is the
`addCleanup` that stops the started sleeper after its pid has been recorded,
and `gone` proves the child died.
"""

from __future__ import annotations

import os
import signal
import subprocess
import time

# Bound on the gone-poll below, the same deadline the inline copies kept: a
# sleeper the cleanup killed normally disappears within the second, so a
# five-second wait only delays a genuinely stuck child's reporting.
GONE_TIMEOUT = 5


def signal_into_popen(number: int, tracked: dict | None = None):
    """Return a `Popen` ``side_effect`` that signals this process at return.

    The returned callable starts the real child, records its pid in the
    *tracked* mapping when one is given, and then sends *number* to this
    process, so the wrapped supervisor leaves ``Popen`` with a real child it
    has not registered yet and the deferral machinery racing the same signal.
    """
    real_popen = subprocess.Popen

    def popen_then_signal(*args, **kwargs):
        process = real_popen(*args, **kwargs)
        if tracked is not None:
            tracked["pid"] = process.pid
        os.kill(os.getpid(), number)
        return process

    return popen_then_signal


def kill_tracked(tracked: dict) -> None:
    """SIGKILL the child a tracked race recorded, tolerating races.

    Killing again a child that already exited is harmless; the ``OSError``
    is swallowed so the cleanup cannot mask the test's own failure.
    """
    pid = tracked.get("pid")
    if pid is not None:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass


def gone(pid: int) -> bool:
    """Return True once *pid* no longer exists, waiting up to five seconds."""
    deadline = time.monotonic() + GONE_TIMEOUT
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.02)
    return False
