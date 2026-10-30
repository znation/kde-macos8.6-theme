"""Interpret worker logs and print ordered parallel check results."""

from __future__ import annotations

import re
import sys

if __package__:
    from tools.diagnostics import plural
    from tools.terminal import escape_controls
else:
    from diagnostics import plural
    from terminal import escape_controls

_NO_TESTS_RAN = 5
_NO_TESTS_RAN_MARKERS = ("Ran 0 tests", "NO TESTS RAN")
_TEST_STARTED = re.compile(r"\)\s(?:[^\n]*\s)?\.\.\.\s")


def _plural(count: int, noun: str) -> str:
    """Return a count and its correctly pluralized noun."""
    return f"{count} {plural(count, noun)}"


def _print_results(modules: list[str], statuses: dict[str, int | None],
                   log_paths: dict[str, str], timeout: float) -> int:
    """Print each module's section in discovery order and return its status."""
    failed = timed_out = not_finished = no_tests = 0
    for module in modules:
        log_text = ""
        log_error = None
        if module in log_paths:
            try:
                with open(log_paths[module], encoding="utf-8", errors="replace") as log:
                    log_text = "\n".join(
                        escape_controls(line) for line in log.read().split("\n")
                    )
            except OSError:
                log_error = "worker log could not be read"
        if log_error is not None:
            verdict = log_error
            failed += 1
        elif module not in statuses:
            verdict = "did not finish"
            not_finished += 1
        elif statuses[module] is None:
            verdict = f"timed out after {timeout:.0f}s (process group killed)"
            timed_out += 1
        elif (statuses[module] == _NO_TESTS_RAN
              and all(marker in log_text for marker in _NO_TESTS_RAN_MARKERS)
              and not _TEST_STARTED.search(log_text)):
            verdict = "ran no tests (unittest's NO TESTS RAN, exit 5)"
            no_tests += 1
        elif statuses[module] == _NO_TESTS_RAN and not all(
            marker in log_text for marker in _NO_TESTS_RAN_MARKERS
        ):
            verdict = "exit 5 but the log shows no unittest NO TESTS RAN summary"
            failed += 1
        elif statuses[module] == _NO_TESTS_RAN:
            verdict = ("exit 5 but the log shows a started test beside "
                       "unittest's NO TESTS RAN summary")
            failed += 1
        else:
            verdict = f"exit {statuses[module]}"
            failed += statuses[module] != 0
        print(f"===== {module}: {verdict} =====")
        sys.stdout.write(log_text)
        if log_text and not log_text.endswith("\n"):
            sys.stdout.write("\n")
    if failed or timed_out or not_finished:
        summary = [_plural(len(modules), "module")]
        if failed:
            summary.append(_plural(failed, "module") + " failed")
        if timed_out:
            summary.append(_plural(timed_out, "module") + " timed out")
        if not_finished:
            summary.append(_plural(not_finished, "module") + " not finished")
        if no_tests:
            summary.append(_plural(no_tests, "module") + " ran no tests")
        print("check: " + ", ".join(summary))
        return 1
    return 0
