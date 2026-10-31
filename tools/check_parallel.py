"""Run test modules concurrently and print their results in discovery order.

Each module runs as ``python -m unittest -v <module>`` in its own process
group. Workers have a bounded concurrency and timeout; ``CHECK_PARALLEL=0``
in Makefile retains serial unittest discovery.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys

if __package__:
    from tools.argument_parsing import EscapingArgumentParser, positive_int
    from tools.check_parallel_discovery import (
        DiscoveryError, _log_paths, discover_modules,
    )
    from tools.check_parallel_order import (
        cache_path, load_durations, order_modules, save_durations,
    )
    from tools.check_parallel_results import _plural, _print_results
    from tools.check_parallel_workers import _supervise
    from tools.diagnostics import create_scratch_directory
    from tools.process_group import exit_on_termination
    from tools.repo_root import ROOT
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/check_parallel.py
    from argument_parsing import EscapingArgumentParser, positive_int
    from check_parallel_discovery import (
        DiscoveryError, _log_paths, discover_modules,
    )
    from check_parallel_order import (
        cache_path, load_durations, order_modules, save_durations,
    )
    from check_parallel_results import _plural, _print_results
    from check_parallel_workers import _supervise
    from diagnostics import create_scratch_directory
    from process_group import exit_on_termination
    from repo_root import ROOT
    from terminal import escape_controls


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse the coordinator's command line."""
    parser = EscapingArgumentParser(
        prog="tools/check_parallel.py",
        description=("Run test modules as parallel worker processes, "
                     "one module per worker."),
    )
    parser.add_argument("-p", "--pattern", default="test*.py",
                        help="test-module filename glob (default test*.py, as `make check`)")
    parser.add_argument("--tests-dir", default="tests",
                        help="the suite's top-level directory (default tests)")
    parser.add_argument("--workers", type=positive_int("--workers"), default=None,
                        help="concurrent worker count (default: one per core, bounded by the module count)")
    parser.add_argument("--timeout", type=positive_int("--timeout"), default=900,
                        help="per-module wall-time limit in seconds (default 900)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Coordinate one parallel suite run."""
    options = parse_args(sys.argv[1:] if argv is None else argv)
    tests_dir = options.tests_dir
    if not os.path.isabs(tests_dir):
        tests_dir = os.path.join(str(ROOT), tests_dir)
    if not os.path.isdir(tests_dir):
        print("check: --tests-dir must name a directory: "
              f"{escape_controls(options.tests_dir)}", file=sys.stderr)
        return 2
    try:
        modules = discover_modules(tests_dir, options.pattern)
    except DiscoveryError as exc:
        # One unreadable directory (a permission error, or a directory swept
        # away while discovery walks the tree) must not abort startup as a
        # bare ``OSError`` traceback: nothing has run and nothing was
        # changed, so the shared exit-2 diagnostic names the directory and
        # the error instead of losing the run to a traceback.
        print(f"check: error: {escape_controls(str(exc))}", file=sys.stderr)
        return 2
    if not modules:
        print(f"check: -p '{escape_controls(options.pattern)}' matches no test module in "
              f"{escape_controls(tests_dir)}", file=sys.stderr)
        return 2
    workers = options.workers or min(len(modules), os.cpu_count() or 1)
    print(f"check: -p '{escape_controls(options.pattern)}', "
          f"{_plural(len(modules), 'module')}, {_plural(workers, 'worker')}")
    # Order the queue by the previous run's recorded durations so the slowest
    # module starts first, and record this run's for the next one. Both
    # directions are best-effort: with no readable cache the queue is plain
    # discovery order, and a cache write failure only names itself on stderr
    # without touching the run's exit status. A module that never finished
    # (never spawned, or the run ended mid-flight) records nothing and keeps
    # discovery order in the next queue.
    durations: dict[str, float] = {}
    ordered = order_modules(modules, load_durations(cache_path()))
    scratch_path = create_scratch_directory("check", "check-parallel-")
    if scratch_path is None:
        return 2
    scratch = str(scratch_path)
    log_paths = _log_paths(modules, scratch)
    try:
        with exit_on_termination():
            statuses = _supervise(
                ordered, [sys.executable, "-m", "unittest", "-v"],
                tests_dir, log_paths, options.timeout, workers,
                durations=durations,
            )
        try:
            save_durations(
                cache_path(),
                {module: durations[module] for module in modules
                 if module in durations},
            )
        except OSError as exc:
            print(
                "check: note: could not record module durations for the "
                f"next run: {escape_controls(str(exc))}",
                file=sys.stderr,
            )
        return _print_results(modules, statuses, log_paths, options.timeout)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
