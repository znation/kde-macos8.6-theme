"""Start, supervise, and clean up parallel check workers."""

from __future__ import annotations

import os
import subprocess
import sys
import time

if __package__:
    from tools.process_group import (
        _INTERRUPT_SIGNALS, _TERMINATION_SIGNALS, _defer_signals,
        _replay_deferred, _restore_termination,
    )
    from tools.terminal import escape_controls
else:
    from process_group import (
        _INTERRUPT_SIGNALS, _TERMINATION_SIGNALS, _defer_signals,
        _replay_deferred, _restore_termination,
    )
    from terminal import escape_controls

_POLL_SECONDS = 0.05
_REAP_SECONDS = 5.0
_KILL_SIGNAL = 9


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
                 deadline: float) -> None:
        self.module = module
        self.log_path = log_path
        self.process = process
        self.deadline = deadline


def _spawn(module: str, argv: list[str], cwd: str, log_path: str,
           timeout: float) -> _Worker:
    """Start one worker in its own session and log its output."""
    exc: OSError | None = None
    with open(log_path, "wb") as sink:
        deferred: list[int] = []
        previous = _defer_signals(_TERMINATION_SIGNALS, deferred)
        previous_interrupts = _defer_signals(_INTERRUPT_SIGNALS, deferred)
        try:
            process: subprocess.Popen | _NeverStarted = subprocess.Popen(
                argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=sink,
                stderr=subprocess.STDOUT, start_new_session=True,
            )
        except OSError as failure:
            _restore_termination(previous)
            _restore_termination(previous_interrupts)
            _replay_deferred(deferred)
            process = _NeverStarted()
            exc = failure
        except BaseException:
            _restore_termination(previous)
            _restore_termination(previous_interrupts)
            _replay_deferred(deferred)
            raise
        try:
            _restore_termination(previous)
            _restore_termination(previous_interrupts)
            _replay_deferred(deferred)
        except BaseException:
            _kill_group(process)
            _reap(process)
            raise
    if exc is not None:
        with open(log_path, "w", encoding="utf-8") as note:
            note.write(f"check: the worker could not be started: {exc}\n")
    return _Worker(module, log_path, process, time.monotonic() + timeout)


def _kill_group(process: subprocess.Popen | _NeverStarted) -> None:
    """Kill a worker's process group, ignoring an already-gone group."""
    if process.pid <= 0:
        return
    try:
        os.killpg(process.pid, _KILL_SIGNAL)
    except OSError:
        pass


def _reap(process: subprocess.Popen | _NeverStarted) -> None:
    """Wait briefly for a killed worker without blocking on a wedged kernel."""
    try:
        process.wait(timeout=_REAP_SECONDS)
    except subprocess.TimeoutExpired:
        pass


def _supervise(modules: list[str], argv_prefix: list[str], cwd: str,
               log_paths: dict[str, str], timeout: float,
               workers: int) -> dict[str, int | None]:
    """Run each module with a bounded number of workers."""
    results: dict[str, int | None] = {}
    queue = list(modules)
    running: list[_Worker] = []
    try:
        while queue or running:
            for entry in running[:]:
                status = entry.process.poll()
                if status is not None:
                    results[entry.module] = status
                    running.remove(entry)
                elif time.monotonic() >= entry.deadline:
                    _kill_group(entry.process)
                    _reap(entry.process)
                    results[entry.module] = None
                    running.remove(entry)
            while len(running) < workers and queue:
                module = queue.pop(0)
                try:
                    running.append(_spawn(module, [*argv_prefix, module], cwd,
                                          log_paths[module], timeout))
                except OSError as exc:
                    # _spawn opens the log before the worker starts; an open
                    # that cannot succeed -- a scratch volume that filled
                    # mid-run, or a log path a sweep removed -- must not get
                    # out: it would unwind _supervise past every module that
                    # already finished and kill the run as a traceback with
                    # no diagnostic. Record the module as never started
                    # (exit 1, the same status _spawn's own "could not be
                    # started" note produces) with one stderr diagnostic
                    # naming the module and the OS error, and keep
                    # supervising the rest of the run. _print_results reads
                    # the same path for the section, so the module's verdict
                    # is its unreadable-log failure.
                    print(
                        "check: error: cannot open the worker log for "
                        f"{escape_controls(module)}: {escape_controls(str(exc))}",
                        file=sys.stderr,
                    )
                    results[module] = 1
            if running:
                time.sleep(_POLL_SECONDS)
    finally:
        for entry in running:
            _kill_group(entry.process)
            _reap(entry.process)
    return results
