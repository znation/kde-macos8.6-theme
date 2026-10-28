"""Run the test suite's modules in parallel worker processes.

Serial `unittest discover` runs every module one after another, so the
suite's wall time is the sum of all module times. The modules are independent:
each already runs in its own interpreter (the install, GTK, cursor and Firefox
suites spawn real `make`/tool children per test) and isolates its scratch
state under a temporary directory, so the wall time can instead be the
slowest module plus scheduling overhead. This tool runs each pattern-matched
module as one worker process -- the same interpreter, `python -m unittest -v
<module>` from the tests directory, that the Makefile's CHECK_TESTS recipe
uses -- a bounded number at a time, and prints every module's captured output
in discovery order so the run stays diffable.

The guarantees the serial run gave each worker are restated here:

- a worker is its own process group (`start_new_session`), with stdin from
  DEVNULL and its output captured to one log file per module under a scratch
  directory that is removed when the run ends;
- a module that exceeds ``--timeout`` has its whole process group killed and
  the reap bounded (a descendant stuck in uninterruptible I/O cannot stall
  the run), the module is reported as timed out, and the run fails;
- SIGTERM and SIGHUP become ``SystemExit`` and Ctrl-C becomes
  ``KeyboardInterrupt`` (the machinery of ``tools/process_group.py``), so the
  cleanup below runs and kills every still-running group: an interrupted
  coordinator leaves no workers behind;
- the exit status is 0 only when every module exited 0, 1 when a module
  failed or timed out, and 2 for usage errors.

`make check` runs this tool by default; `make check CHECK_PARALLEL=0` keeps
the serial `unittest discover` path, and `CHECK_PARALLEL=n` bounds the worker
count instead of one per core.

Usage::

    python3 tools/check_parallel.py [-p PATTERN] [--tests-dir DIR]
        [--workers N] [--timeout S]

Exit status: 0 when every module passed, 1 when one failed or timed out, 2
usage error.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

if __package__:
    from tools.argument_parsing import EscapingArgumentParser, positive_int
    from tools.process_group import (
        _INTERRUPT_SIGNALS,
        _TERMINATION_SIGNALS,
        _defer_signals,
        _replay_deferred,
        _restore_termination,
        exit_on_termination,
    )
    from tools.diagnostics import plural
    from tools.repo_root import ROOT
else:  # run directly: python3 tools/check_parallel.py
    from argument_parsing import EscapingArgumentParser, positive_int
    from process_group import (
        _INTERRUPT_SIGNALS,
        _TERMINATION_SIGNALS,
        _defer_signals,
        _replay_deferred,
        _restore_termination,
        exit_on_termination,
    )
    from diagnostics import plural
    from repo_root import ROOT

# How often the supervisor wakes to reap finished workers and start queued
# ones. Workers are processes that run for seconds, so a 50ms poll adds
# nothing a child would notice and keeps the supervisor simple: one process
# per module, no thread per child, no output streaming.
_POLL_SECONDS = 0.05

# Bounded reap after a group kill, as in tools/process_group.py: a child the
# kernel has not released cannot turn an already-fired timeout back into an
# unbounded wait.
_REAP_SECONDS = 5.0

# The supervisor kills a timed-out group outright rather than first asking it
# to terminate: a worker mid-`make` cannot relay a SIGTERM to its own
# children, and the module's fate (timeout) is already decided.
_KILL_SIGNAL = 9

# unittest discovery loads a file as a test module only when its basename is
# a valid Python identifier ending in .py (TestLoader's VALID_MODULE_NAME),
# checked before the pattern match; discovery mirrors that gate here.
_VALID_MODULE_NAME = re.compile(r"[_a-zA-Z]\w*\.py$")


def discover_modules(tests_dir: str, pattern: str) -> list[str]:
    """Return the dotted module names ``unittest discover`` would import.

    Discovery gates each filename on unittest's ``VALID_MODULE_NAME`` (a
    valid Python identifier ending in .py), matches it against *pattern*,
    and recurses into a subdirectory only when it is a package (one holding
    ``__init__.py``), exactly as ``unittest discover`` does; the returned
    names are the dotted paths discovery would import, in sorted order.
    Real discovery also imports each package's own ``__init__.py`` module
    (loading the tests it defines); this scan returns file modules only, and
    the suite-structure guard ``tests/test_suite_discovery.py`` holds tests
    out of package ``__init__.py`` files so the two paths run the same tests.
    """
    names: list[str] = []

    def visit(directory: str, prefix: str) -> None:
        for entry in sorted(os.listdir(directory)):
            path = os.path.join(directory, entry)
            if os.path.isdir(path):
                if os.path.isfile(os.path.join(path, "__init__.py")):
                    visit(path, f"{prefix}{entry}.")
            elif _VALID_MODULE_NAME.match(entry) and fnmatch.fnmatch(
                entry, pattern
            ):
                names.append(f"{prefix}{entry[:-len('.py')]}")

    visit(tests_dir, "")
    return names


def _log_paths(modules: list[str], scratch: str) -> dict[str, str]:
    """Map each module to a unique log path under *scratch*.

    The dotted module name becomes one ``_``-joined stem, but two distinct
    modules can share it -- a package's ``test_a.test_b`` module and a
    top-level ``test_a_test_b.py`` both give ``test_a_test_b`` -- and two
    workers opening one log file would truncate and interleave each other's
    output while the result sections print that one file twice. A later
    collision therefore takes a ``_<n>`` suffix, checked against every
    module's natural stem and every already-assigned suffix, so no third
    module's own natural log name is ever claimed.
    """
    reserved = {f"{module.replace('.', '_')}.log" for module in modules}
    names: dict[str, str] = {}
    for module in modules:
        natural = f"{module.replace('.', '_')}.log"
        if natural not in names.values():
            names[module] = natural
            continue
        suffix = 2
        while True:
            candidate = f"{natural[:-len('.log')]}_{suffix}.log"
            suffix += 1
            if candidate not in reserved:
                reserved.add(candidate)
                names[module] = candidate
                break
    return {
        module: os.path.join(scratch, name) for module, name in names.items()
    }


class _NeverStarted:
    """Stand-in for a worker whose process could not be started.

    It reports a failed exit so the run fails naming the module, and the
    kill and reap paths have nothing to do.
    """

    @staticmethod
    def poll() -> int:
        return 1

    @staticmethod
    def wait(timeout: float | None = None) -> int:
        return 1

    pid = 0


class _Worker:
    """One started worker and what the supervisor needs to supervise it."""

    def __init__(
        self,
        module: str,
        log_path: str,
        process: subprocess.Popen | _NeverStarted,
        deadline: float,
    ) -> None:
        self.module = module
        self.log_path = log_path
        self.process = process
        self.deadline = deadline


def _spawn(
    module: str, argv: list[str], cwd: str, log_path: str, timeout: float
) -> _Worker:
    """Start one worker in its own session, logging to *log_path*.

    A worker that cannot be started (a missing interpreter, an unwritable
    scratch directory) is reported as that module's failure rather than
    aborting the run: the other modules' results stay valid. A termination
    signal or Ctrl-C that arrives while ``Popen`` is still returning is
    deferred -- ``tools/process_group.py``'s machinery, the defense
    ``run_logged`` applies -- and replayed only once the worker exists, so
    the replay can kill and reap the started group instead of unwinding
    before any cleanup could reach it.
    """
    exc: OSError | None = None
    with open(log_path, "wb") as sink:
        deferred: list[int] = []
        previous = _defer_signals(_TERMINATION_SIGNALS, deferred)
        previous_interrupts = _defer_signals(_INTERRUPT_SIGNALS, deferred)
        try:
            process: subprocess.Popen | _NeverStarted = subprocess.Popen(
                argv,
                cwd=cwd,
                stdin=subprocess.DEVNULL,
                stdout=sink,
                stderr=subprocess.STDOUT,
                start_new_session=True,
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
            # The replayed signal unwinds the caller before the worker is
            # ever appended to the supervised set, so the group kill and
            # reap that the supervisor's finally block would do have to
            # happen here: an interrupted spawn leaves no worker behind.
            _kill_group(process)
            _reap(process)
            raise
    if exc is not None:
        with open(log_path, "w", encoding="utf-8") as note:
            note.write(f"check: the worker could not be started: {exc}\n")
    return _Worker(module, log_path, process, time.monotonic() + timeout)


def _kill_group(process: subprocess.Popen | _NeverStarted) -> None:
    """Kill the worker's whole group; the reap stays with the caller.

    A worker that never started has pid 0, and ``os.killpg(0, ...)`` would
    signal the coordinator's own process group -- under ``make check``,
    make's jobserver -- so a non-positive pid reaches no signal at all.
    """
    if process.pid <= 0:
        return
    try:
        os.killpg(process.pid, _KILL_SIGNAL)
    except OSError:
        pass


def _reap(process: subprocess.Popen | _NeverStarted) -> None:
    """Wait briefly for a group-killed worker, ignoring a wedged kernel."""
    try:
        process.wait(timeout=_REAP_SECONDS)
    except subprocess.TimeoutExpired:
        pass


def _supervise(
    modules: list[str],
    argv_prefix: list[str],
    cwd: str,
    log_paths: dict[str, str],
    timeout: float,
    workers: int,
) -> dict[str, int | None]:
    """Run every module through at most *workers* concurrent processes.

    Returns each module's worker status: the exit code, or None when the
    module timed out and its process group was killed. A module still running
    when the call unwinds (the coordinator was signalled) gets no status; the
    finally block kills every such group, so an interrupted run leaves no
    worker behind.
    """
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
                running.append(
                    _spawn(
                        module,
                        [*argv_prefix, module],
                        cwd,
                        log_paths[module],
                        timeout,
                    )
                )
            if running:
                time.sleep(_POLL_SECONDS)
    finally:
        for entry in running:
            _kill_group(entry.process)
            _reap(entry.process)
    return results


def _plural(count: int, noun: str) -> str:
    """Return *count* and *noun* with a plural only when it reads as one."""
    return f"{count} {plural(count, noun)}"


def _print_results(
    modules: list[str],
    statuses: dict[str, int | None],
    log_paths: dict[str, str],
    timeout: float,
) -> int:
    """Print each module's section in discovery order; return the exit status.

    The sections are printed after every worker has finished, so the output
    is grouped and ordered by module no matter when each worker ended. A
    module with no status was still running when the run unwound; it is
    reported as not finished and fails the run.
    """
    failed = 0
    timed_out = 0
    not_finished = 0
    for module in modules:
        if module not in statuses:
            verdict = "did not finish"
            not_finished += 1
        elif statuses[module] is None:
            verdict = (
                f"timed out after {timeout:.0f}s (process group killed)"
            )
            timed_out += 1
        else:
            verdict = f"exit {statuses[module]}"
            failed += statuses[module] != 0
        print(f"===== {module}: {verdict} =====")
        with open(log_paths[module], encoding="utf-8", errors="replace") as log:
            shutil.copyfileobj(log, sys.stdout)
    if failed or timed_out or not_finished:
        summary = [f"{_plural(len(modules), 'module')}"]
        if failed:
            summary.append(f"{_plural(failed, 'module')} failed")
        if timed_out:
            summary.append(f"{_plural(timed_out, 'module')} timed out")
        if not_finished:
            summary.append(f"{_plural(not_finished, 'module')} not finished")
        print("check: " + ", ".join(summary))
        return 1
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse the coordinator's command line."""
    parser = EscapingArgumentParser(
        prog="tools/check_parallel.py",
        description=(
            "Run the test suite's pattern-matched modules as parallel "
            "worker processes, one module per worker."
        ),
    )
    parser.add_argument(
        "-p",
        "--pattern",
        default="test*.py",
        help="test-module filename glob (default test*.py, as `make check`)",
    )
    parser.add_argument(
        "--tests-dir",
        default="tests",
        help="the suite's top-level directory (default tests)",
    )
    parser.add_argument(
        "--workers",
        type=positive_int("--workers"),
        default=None,
        help=(
            "concurrent worker count (default: one per core, bounded by "
            "the module count)"
        ),
    )
    parser.add_argument(
        "--timeout",
        type=positive_int("--timeout"),
        default=900,
        help=(
            "per-module wall-time limit in seconds (default 900); a module "
            "that exceeds it has its process group killed"
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Coordinate one parallel suite run; see the module docstring."""
    options = parse_args(sys.argv[1:] if argv is None else argv)
    tests_dir = options.tests_dir
    if not os.path.isabs(tests_dir):
        tests_dir = os.path.join(str(ROOT), tests_dir)
    if not os.path.isdir(tests_dir):
        print(
            f"check: --tests-dir must name a directory: {options.tests_dir}",
            file=sys.stderr,
        )
        return 2
    modules = discover_modules(tests_dir, options.pattern)
    if not modules:
        print(
            f"check: -p '{options.pattern}' matches no test module in "
            f"{tests_dir}",
            file=sys.stderr,
        )
        return 2
    workers = options.workers or min(len(modules), os.cpu_count() or 1)
    print(
        f"check: -p '{options.pattern}', {_plural(len(modules), 'module')}, "
        f"{_plural(workers, 'worker')}"
    )
    scratch = tempfile.mkdtemp(prefix="check-parallel-")
    log_paths = _log_paths(modules, scratch)
    try:
        with exit_on_termination():
            statuses = _supervise(
                modules,
                [sys.executable, "-m", "unittest", "-v"],
                tests_dir,
                log_paths,
                options.timeout,
                workers,
            )
        return _print_results(modules, statuses, log_paths, options.timeout)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
