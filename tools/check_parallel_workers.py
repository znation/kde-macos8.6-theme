"""Start, supervise, and clean up parallel check workers."""

from __future__ import annotations

from collections import deque
import os
import stat
import subprocess
import sys
import time

if __package__:
    from tools.process_group import (
        kill_group, popen_deferred, reap, restore_termination,
        replay_deferred,
    )
    from tools.terminal import escape_controls
else:
    from process_group import (
        kill_group, popen_deferred, reap, restore_termination,
        replay_deferred,
    )
    from terminal import escape_controls

# Bound the requested sleep before noticing a finished worker and filling
# its slot. Each iteration polls every running worker without blocking.
_POLL_SECONDS = 0.01


def _open_log(path: str):
    """Open a worker log without blocking on a raced FIFO or device."""
    descriptor = os.open(
        path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NONBLOCK, 0o666
    )
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise OSError(f"{path} is not a regular file")
        return os.fdopen(descriptor, "wb")
    except BaseException:
        os.close(descriptor)
        raise


class _NeverStarted:
    """Stand-in for a worker whose process could not be started."""
    @staticmethod
    def poll() -> int:
        return 1

    @staticmethod
    def wait(timeout: float | None = None) -> int:
        return 1

    pid = 0


class _Worker:
    """One worker and the state needed to supervise it."""
    def __init__(self, module: str, log_path: str,
                 process: subprocess.Popen | _NeverStarted,
                 deadline: float, started: float) -> None:
        self.module = module
        self.log_path = log_path
        self.process = process
        self.deadline = deadline
        self.started = started


def _spawn(module: str, argv: list[str], cwd: str, log_path: str,
           timeout: float) -> _Worker:
    """Start one worker in its own session and log its output."""
    exc: OSError | None = None
    started = time.monotonic()
    process: subprocess.Popen | _NeverStarted = _NeverStarted()
    try:
        with _open_log(log_path) as sink:
            try:
                process, deferred, previous, previous_interrupts = (
                    popen_deferred(
                        argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=sink,
                        stderr=subprocess.STDOUT, start_new_session=True,
                    )
                )
                # Swap the handlers back here, where the outer cleanup below
                # owns the child: a signal that arrives as they are restored
                # still reaches the group kill instead of unwinding past it.
                restore_termination(previous)
                restore_termination(previous_interrupts)
                replay_deferred(deferred)
            except OSError as failure:
                process = _NeverStarted()
                exc = failure
    except BaseException:
        kill_group(process)
        reap(process)
        raise
    if exc is not None:
        with _open_log(log_path) as note:
            note.write(f"check: the worker could not be started: {exc}\n".encode())
    return _Worker(module, log_path, process,
                   time.monotonic() + timeout, started)


def _poll_running(running: list[_Worker], durations: dict[str, float] | None,
                  results: dict[str, int | None]) -> list[_Worker]:
    """Reap each finished or timed-out worker and return the rest.

    A finished worker records its exit status; a worker past its deadline is
    killed, reaped and recorded as ``None``. With *durations*, both also
    record the worker's elapsed wall time.
    """
    remaining: list[_Worker] = []
    for entry in running:
        status = entry.process.poll()
        if status is not None:
            _record_duration(entry, durations)
            results[entry.module] = status
        elif time.monotonic() >= entry.deadline:
            _record_duration(entry, durations)
            kill_group(entry.process)
            reap(entry.process)
            results[entry.module] = None
        else:
            remaining.append(entry)
    return remaining


def supervise(modules: list[str], argv_prefix: list[str], cwd: str,
               log_paths: dict[str, str], timeout: float,
               workers: int,
               durations: dict[str, float] | None = None) -> dict[str,
                                                                    int | None]:
    """Run each module with a bounded number of workers.

    A worker count below one is refused before the loop runs: the fill loop
    starts a worker only while fewer than *workers* are running, so with zero
    workers the queue can never drain and the poll loop would spin at full
    CPU with no output instead of returning an error.

    When *durations* is a mapping, each finished worker's elapsed wall time is
    recorded into it: completion is polled within ``_POLL_SECONDS`` and a
    timed-out worker records its timeout-span, so the values carry spawn and
    teardown, which is the time the module held a worker -- exactly what the
    next run's ordering needs.
    """
    if (not isinstance(workers, int) or isinstance(workers, bool)
            or workers < 1):
        raise ValueError(
            f"supervise() requires a positive integer worker count: "
            f"workers={workers!r}"
        )
    results: dict[str, int | None] = {}
    queue = deque(modules)
    running: list[_Worker] = []
    try:
        while queue or running:
            running = _poll_running(running, durations, results)
            _fill_workers(queue, running, results, argv_prefix, cwd,
                          log_paths, timeout, workers)
            if running:
                time.sleep(_POLL_SECONDS)
    finally:
        for entry in running:
            kill_group(entry.process)
            reap(entry.process)
    return results


def _fill_workers(queue: deque[str], running: list[_Worker],
                  results: dict[str, int | None], argv_prefix: list[str],
                  cwd: str, log_paths: dict[str, str], timeout: float,
                  workers: int) -> None:
    """Start queued workers until the concurrency limit is reached."""
    while len(running) < workers and queue:
        module = queue.popleft()
        try:
            running.append(_spawn(module, [*argv_prefix, module], cwd,
                                  log_paths[module], timeout))
        except OSError as exc:
            # _spawn opens the log before the worker starts; an open that
            # cannot succeed must fail this module without stopping the run.
            print(
                "check: error: cannot open the worker log for "
                f"{escape_controls(module)}: {escape_controls(str(exc))}",
                file=sys.stderr,
            )
            results[module] = 1


def _record_duration(entry: _Worker,
                     durations: dict[str, float] | None) -> None:
    """Record one started worker's elapsed time under its module key."""
    if durations is None:
        return
    durations[entry.module] = time.monotonic() - entry.started
