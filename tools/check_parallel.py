"""Run test modules concurrently and print their results in discovery order.

Each module runs as ``python -m unittest -v <module>`` in its own process
group. Workers have a bounded concurrency and timeout; ``CHECK_PARALLEL=0``
in Makefile retains serial unittest discovery.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import shutil
import sys

if __package__:
    from tools.argument_parsing import EscapingArgumentParser, positive_int
    from tools.check_parallel_discovery import (
        DiscoveryError, assign_log_paths, discover_modules,
    )
    from tools.check_parallel_order import (
        cache_path, load_durations, merge_durations, order_modules,
        save_durations,
    )
    from tools.check_parallel_results import count_noun, print_results
    from tools.check_parallel_workers import supervise
    from tools.diagnostics import create_scratch_directory, report_error
    from tools.process_group import exit_on_termination
    from tools.repo_root import ROOT
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/check_parallel.py
    from argument_parsing import EscapingArgumentParser, positive_int
    from check_parallel_discovery import (
        DiscoveryError, assign_log_paths, discover_modules,
    )
    from check_parallel_order import (
        cache_path, load_durations, merge_durations, order_modules,
        save_durations,
    )
    from check_parallel_results import count_noun, print_results
    from check_parallel_workers import supervise
    from diagnostics import create_scratch_directory, report_error
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
        return report_error(
            "check",
            f"--tests-dir must name a directory: {options.tests_dir}",
        )
    try:
        all_modules = discover_modules(tests_dir)
        modules = [
            module for module in all_modules
            if fnmatch.fnmatch(f"{module.rsplit('.', 1)[-1]}.py", options.pattern)
        ]
    except DiscoveryError as exc:
        # One unreadable directory (a permission error, or a directory swept
        # away while discovery walks the tree) must not abort startup as a
        # bare ``OSError`` traceback: nothing has run and nothing was
        # changed, so the shared exit-2 diagnostic names the directory and
        # the error instead of losing the run to a traceback.
        print(f"check: error: {escape_controls(str(exc))}", file=sys.stderr)
        return 2
    if not modules:
        return report_error(
            "check",
            f"-p '{options.pattern}' matches no test module in {tests_dir}",
        )
    workers = options.workers or min(len(modules), os.cpu_count() or 1)
    print(f"check: -p '{escape_controls(options.pattern)}', "
          f"{count_noun(len(modules), 'module')}, {count_noun(workers, 'worker')}")
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
    log_paths = assign_log_paths(modules, scratch)
    try:
        with exit_on_termination():
            statuses = supervise(
                ordered, [sys.executable, "-m", "unittest", "-v"],
                tests_dir, log_paths, options.timeout, workers,
                durations=durations,
            )
        try:
            save_durations(
                cache_path(),
                merge_durations(
                    cache_path(),
                    {module: durations[module] for module in modules
                     if module in durations},
                    # The merge needs the whole-tree module list: a narrow
                    # pattern must not prune the sibling durations the next
                    # full run's queue orders by, while modules removed or
                    # renamed since their last run leave nothing behind.
                    # The walk lists the test tree only -- one os.listdir
                    # per directory, the same family of calls the discovery
                    # pass above already exercised -- and its OSError or
                    # DiscoveryError keeps the save best-effort, as at
                    # startup.
                    set(all_modules),
                ),
            )
        except (OSError, DiscoveryError) as exc:
            print(
                "check: note: could not record module durations for the "
                f"next run: {escape_controls(str(exc))}",
                file=sys.stderr,
            )
        return print_results(modules, statuses, log_paths, options.timeout)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
