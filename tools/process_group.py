"""Run a child in its own process group and tear the whole group down.

:func:`run_logged` supervises one command with a timeout and a log file;
:func:`run_logged_split` does the same with the two output streams logged
separately, for callers that read a value from stdout and must not log the
streams merged;
:func:`exit_on_termination` makes SIGTERM and SIGHUP unwind the caller's
``finally`` blocks. ``tools/render_surface.py`` and ``tools/apply_theme.py``
use both around the external commands they run;
``tools/required_command.py`` wraps :func:`run_logged` with the shared
required-command diagnostic for ``tools/apply_theme.py``,
``tools/cursor_selection.py`` (the selector used by ``tools/apply_cursor.py``).

A Ctrl-C (SIGINT) is not one of ``exit_on_termination``'s signals, but its
default handler raises ``KeyboardInterrupt`` at the next bytecode just the
same, so :func:`run_logged` defers it around the child's start too.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import threading
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


def kill_group(process: subprocess.Popen) -> None:
    """Kill *process*'s group, ignoring a nonpositive pid or gone group."""
    if process.pid <= 0:
        return
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except OSError:
        pass


def reap(process: subprocess.Popen) -> None:
    """Wait briefly for a killed process without blocking on a wedged kernel."""
    try:
        process.wait(timeout=_REAP_TIMEOUT)
    except subprocess.TimeoutExpired:
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
        # Defer signals until the cleanup try below is ready to own the child:
        # the handlers are swapped back inside the try, so a signal that
        # arrives as they are restored raises where the group kill runs.
        process, deferred, previous, previous_interrupts = popen_deferred(
            argv,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=sink,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            restore_termination(previous)
            restore_termination(previous_interrupts)
            replay_deferred(deferred)
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return None
        finally:
            kill_group(process)
            # The child has not been released yet, so there is nothing more
            # to do: SIGKILL is already sent. A reap timeout must not replace
            # the caller's real outcome.
            reap(process)


def run_logged_split(
    argv: list[str],
    env: dict[str, str],
    stdout_log: Path,
    stderr_log: Path,
    timeout: float,
    cwd: Path,
    stdin_bytes: bytes | None = None,
) -> int | None:
    """Run *argv* logging stdout and stderr to separate files; None = timeout.

    The shared :func:`run_logged` merges a command's streams into one log,
    which is what a caller that never reads the streams wants. A caller that
    takes a value from stdout and must keep stderr warnings separate cannot
    use it, so this variant logs the streams to separate files under the same
    supervision: stdin is closed, the whole process group is killed on the
    way out, and the bounded reap cannot stall past the timeout. A command
    that cannot be started raises the ``OSError`` for the caller to report.

    Callers that feed the command bytes on stdin pass *stdin_bytes* (written
    by a daemon thread and closed when written, so a child that stops reading
    cannot stall the timeout past the kill); the default keeps stdin closed
    exactly as before.
    """
    with stdout_log.open("wb") as out, stderr_log.open("wb") as err:
        # Defer signals until the cleanup try below is ready to own the child:
        # the handlers are swapped back inside the try, so a signal that
        # arrives as they are restored raises where the group kill runs.
        process, deferred, previous, previous_interrupts = popen_deferred(
            argv,
            cwd=cwd,
            env=env,
            stdin=subprocess.PIPE if stdin_bytes is not None else subprocess.DEVNULL,
            stdout=out,
            stderr=err,
            start_new_session=True,
        )
        writer = (
            threading.Thread(
                target=_feed_stdin, args=(process.stdin, stdin_bytes), daemon=True
            )
            if stdin_bytes is not None
            else None
        )
        writer_started = False
        try:
            if writer is not None:
                writer.start()
                writer_started = True
            restore_termination(previous)
            restore_termination(previous_interrupts)
            replay_deferred(deferred)
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return None
        finally:
            kill_group(process)
            reap(process)
            _finish_writer(process, writer, writer_started)


def _finish_writer(process, writer, writer_started) -> None:
    """Shut the stdin writer down after the supervised wait.

    A writer that never started cannot be joined -- its thread never ran --
    so its pipe is closed here to unblock a child still reading. A started
    writer closes its own pipe once written and is joined with a bounded
    timeout, so cleanup cannot stall past it.
    """
    if writer is None:
        return
    if not writer_started:
        try:
            process.stdin.close()
        except OSError:
            pass
        return
    writer.join(_REAP_TIMEOUT)


def _feed_stdin(sink, data: bytes) -> None:
    """Write *data* into *sink* and close it, swallowing a gone reader.

    Runs in a daemon thread so a child that stops reading (or dies early)
    cannot block the supervised wait past its timeout. The whole group is
    already being killed by the caller's cleanup, and the write then fails
    with a broken pipe the run's outcome does not care about.
    """
    try:
        sink.write(data)
    except (BrokenPipeError, OSError):
        pass
    finally:
        try:
            sink.close()
        except (BrokenPipeError, OSError):
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

    handler._process_group_termination_handler = True

    signals = _TERMINATION_SIGNALS
    previous = [signal.signal(number, handler) for number in signals]
    try:
        yield
    finally:
        for number, old in zip(signals, previous):
            signal.signal(number, old)
