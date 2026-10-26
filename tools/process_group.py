"""Run a child in its own process group and tear the whole group down.

:func:`run_logged` supervises one command with a timeout and a log file;
:func:`exit_on_termination` makes SIGTERM and SIGHUP unwind the caller's
``finally`` blocks. ``tools/render_surface.py`` and ``tools/apply_theme.py``
use both around the external commands they run; ``tools/required_command.py``
wraps :func:`run_logged` with the shared required-command diagnostic for
``tools/apply_theme.py`` and ``tools/apply_cursor.py``.

A Ctrl-C (SIGINT) is not one of ``exit_on_termination``'s signals, but its
default handler raises ``KeyboardInterrupt`` at the next bytecode just the
same, so :func:`run_logged` defers it around the child's start too.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
from collections.abc import Iterator
from pathlib import Path
from types import FrameType

# A child that was just SIGKILLed normally dies at once. One stuck in
# uninterruptible I/O (a hung network or FUSE mount) can keep the kernel from
# reaping it for as long as that I/O lasts, which may be forever. The reap that
# follows the group kill must not wait on that: a timeout that has already
# fired must not turn back into an unbounded wait.
_REAP_TIMEOUT = 5.0

# The signals exit_on_termination turns into SystemExit. run_logged records
# them while it starts a child, so the handler's exception cannot arrive before
# its cleanup try/finally is established.
_TERMINATION_SIGNALS = (signal.SIGTERM, signal.SIGHUP)

# Ctrl-C is not exit_on_termination's concern, but its default handler also
# raises at the next bytecode. run_logged defers it around the start for the
# same reason, then re-raises KeyboardInterrupt inside the cleanup try.
_INTERRUPT_SIGNALS = (signal.SIGINT,)


def _defer_signals(
    signals: tuple[int, ...], deferred: list[int]
) -> list[tuple[int, object]]:
    """Record delivery of *signals* instead of raising while a child starts.

    Only a callable handler is swapped out: the default action and an ignored
    signal are left alone, since neither raises past the child's cleanup.
    Returns the handlers to restore; *deferred* collects the signal numbers in
    the order they arrive.
    """
    previous: list[tuple[int, object]] = []
    for number in signals:
        old = signal.getsignal(number)
        if callable(old):
            previous.append((number, old))
            signal.signal(
                number, lambda signum, frame: deferred.append(signum)
            )
    return previous


def _replay_deferred(deferred: list[int]) -> None:
    """Raise the recorded signal's ordinary exception inside the cleanup try."""
    if not deferred:
        return
    number = deferred[0]
    if number == signal.SIGINT:
        raise KeyboardInterrupt
    raise SystemExit(128 + number)


def _restore_termination(previous: list[tuple[int, object]]) -> None:
    for number, old in previous:
        signal.signal(number, old)
    previous.clear()


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
    way out, whatever happened. The reap after that kill is bounded too: a
    child in uninterruptible I/O ignores SIGKILL until the kernel lets go, and
    waiting for it forever would stall the caller after its timeout had
    already fired. A reap that still times out is never re-raised: the first
    wait either returned (the child is already reaped, so the second wait
    cannot time out) or raised, in which case re-raising would replace the
    timeout result or the in-flight ``SystemExit``/``KeyboardInterrupt``.
    """
    with log.open("wb") as sink:
        # Popen returns only after fork/exec, so a termination signal or
        # Ctrl-C can arrive while it is still returning, before the cleanup
        # below exists. exit_on_termination's SIGHUP/SIGTERM handler raises
        # SystemExit at the next bytecode and SIGINT's default handler raises
        # KeyboardInterrupt, so either would skip the group kill and leave the
        # command running after the caller dies. Swap in handlers that record
        # the signal instead, restore the real handlers once the try is
        # entered, and raise the recorded signal's exception there, where the
        # cleanup runs.
        deferred: list[int] = []
        previous = _defer_signals(_TERMINATION_SIGNALS, deferred)
        previous_interrupts = _defer_signals(_INTERRUPT_SIGNALS, deferred)
        try:
            process = subprocess.Popen(
                argv,
                cwd=cwd,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=sink,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        except BaseException:
            _restore_termination(previous)
            _restore_termination(previous_interrupts)
            _replay_deferred(deferred)
            raise
        try:
            _restore_termination(previous)
            _restore_termination(previous_interrupts)
            _replay_deferred(deferred)
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return None
        finally:
            _kill_group(process)
            try:
                process.wait(timeout=_REAP_TIMEOUT)
            except subprocess.TimeoutExpired:
                # The child has not been released yet, so there is nothing
                # more to do: SIGKILL is already sent. Re-raising here would
                # replace the caller's real outcome -- the None from the
                # timeout path, or the SystemExit/KeyboardInterrupt the first
                # wait raised -- with a spurious reap timeout. A child that
                # exits normally was reaped by the first wait, which returned,
                # so this second wait cannot time out on that path.
                pass


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

    signals = _TERMINATION_SIGNALS
    previous = [signal.signal(number, handler) for number in signals]
    try:
        yield
    finally:
        for number, old in zip(signals, previous):
            signal.signal(number, old)
