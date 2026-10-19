"""Run a child in its own process group and tear the whole group down.

:func:`run_logged` supervises one command with a timeout and a log file;
:func:`exit_on_termination` makes SIGTERM and SIGHUP unwind the caller's
``finally`` blocks. ``tools/render_surface.py`` and ``tools/apply_theme.py``
use both around the external commands they run.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
from collections.abc import Iterator
from pathlib import Path
from types import FrameType


def _kill_group(process: subprocess.Popen) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except OSError:
        pass


def run_logged(
    argv: list[str], env: dict[str, str], log: Path, timeout: float, cwd: Path
) -> int | None:
    """Run *argv* in its own session logging to *log*; None means it timed out.

    Output goes to a file, not a pipe, so a descendant that outlives the
    child cannot keep the wait open. The whole process group is killed on the
    way out, whatever happened.
    """
    with log.open("wb") as sink:
        process = subprocess.Popen(
            argv,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=sink,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return None
        finally:
            _kill_group(process)
            process.wait()


@contextlib.contextmanager
def exit_on_termination() -> Iterator[None]:
    """Turn SIGTERM and SIGHUP into ``SystemExit`` so the ``finally`` blocks run.

    A child started with :func:`run_logged` runs in its own session, so a
    terminated caller would otherwise leave it running with no timeout, and
    any scratch directory behind it. Exits with the shell convention 128 +
    signal number.
    """

    def handler(signum: int, frame: FrameType | None) -> None:
        raise SystemExit(128 + signum)

    signals = (signal.SIGTERM, signal.SIGHUP)
    previous = [signal.signal(number, handler) for number in signals]
    try:
        yield
    finally:
        for number, old in zip(signals, previous):
            signal.signal(number, old)
