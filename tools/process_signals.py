"""Defer catchable signals around a child's start, and make them unwind.

:func:`popen_deferred` starts a child with SIGTERM, SIGHUP and Ctrl-C recorded
instead of raised; :func:`replay_deferred` raises the first recorded one once
the caller's cleanup owns the child, and :func:`restore_termination` swaps the
previous handlers back. :func:`exit_on_termination` makes SIGTERM and SIGHUP
unwind the caller's ``finally`` blocks. :mod:`tools.process_group` supervises
child runs on these primitives.
"""

from __future__ import annotations

import contextlib
import signal
import subprocess
import threading
from collections.abc import Iterator
from types import FrameType

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
        # Only the default Ctrl-C handler has the KeyboardInterrupt semantics
        # replayed below. Other handlers belong to the caller. Signals execute
        # on the main thread, and Python forbids installing handlers elsewhere.
        if number == signal.SIGINT and (
            old is not signal.default_int_handler
            or threading.current_thread() is not threading.main_thread()
        ):
            continue
        if number in _TERMINATION_SIGNALS and not getattr(
            old, "_process_group_termination_handler", False
        ):
            continue
        if callable(old):
            previous.append((number, old))
            signal.signal(
                number, lambda signum, frame: deferred.append(signum)
            )
    return previous


def replay_deferred(deferred: list[int]) -> None:
    """Raise the first recorded signal's ordinary exception inside the cleanup try.

    More than one signal can be recorded while the child starts (a terminal
    hangup followed by a kill, or a second Ctrl-C). The process is already
    exiting, so only the first is replayed: a later signal must not replace
    the shell-convention exit status or the exception type.
    """
    if not deferred:
        return
    number = deferred[0]
    if number == signal.SIGINT:
        raise KeyboardInterrupt
    raise SystemExit(128 + number)


def restore_termination(previous: list[tuple[int, object]]) -> None:
    """Restore the catchable signals' previous handlers and drop the deferral."""
    for number, old in previous:
        signal.signal(number, old)
    previous.clear()


def popen_deferred(
    *args, **kwargs
) -> tuple[
    subprocess.Popen,
    list[int],
    list[tuple[int, object]],
    list[tuple[int, object]],
]:
    """Start a child with catchable signals deferred; return them and handlers.

    On a successful start the recorded handlers are returned, not restored:
    the caller must swap them back inside its own cleanup try, where the
    group kill runs, or a signal arriving in between would unwind before any
    cleanup exists and leave the child running. A failed start leaves no
    child to own, so the handlers are restored here and the first recorded
    signal is replayed before the original error re-raises.
    """
    deferred: list[int] = []
    previous = _defer_signals(_TERMINATION_SIGNALS, deferred)
    previous_interrupts = _defer_signals(_INTERRUPT_SIGNALS, deferred)
    try:
        process = subprocess.Popen(*args, **kwargs)
    except BaseException:
        restore_termination(previous)
        restore_termination(previous_interrupts)
        replay_deferred(deferred)
        raise
    return process, deferred, previous, previous_interrupts




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

    handler._process_group_termination_handler = True

    signals = _TERMINATION_SIGNALS
    previous = [signal.signal(number, handler) for number in signals]
    try:
        yield
    finally:
        for number, old in zip(signals, previous):
            signal.signal(number, old)
