"""Interpret worker logs and print ordered parallel check results."""

from __future__ import annotations

import os
import re
import sys

if __package__:
    from tools.diagnostics import plural
    from tools.terminal import escape_controls
else:
    from diagnostics import plural
    from terminal import escape_controls

_NO_TESTS_RAN = 5
# The most of a worker log one printed section keeps. A worker killed at its
# timeout while flooding its log (a test that prints in a loop) leaves a file
# far larger than the tail worth printing, so the printed window matches the
# bounded-window pattern the shared failure reporter reads a command log's
# tail with (tools/diagnostics.py's _LOG_TAIL_BYTES).
_LOG_TAIL_BYTES = 1 << 16
_NO_TESTS_RAN_MARKERS = ("Ran 0 tests", "NO TESTS RAN")
_TEST_STARTED = re.compile(r"\)\s(?:[^\n]*\s)?\.\.\.\s")


def _plural(count: int, noun: str) -> str:
    """Return a count and its correctly pluralized noun."""
    return f"{count} {plural(count, noun)}"


def _bounded_log_text(path: str) -> str:
    """Return the printable, escaped text of a worker log's bounded tail.

    A worker killed at its timeout while flooding its log (a test that
    prints in a loop) leaves a file far larger than the tail worth printing.
    Reading it whole would load the flood into memory -- and a MemoryError,
    which is not an OSError, would escape as a traceback that loses the
    printed results of every module that finished -- and echo the whole
    flood to the terminal. At most the last ``_LOG_TAIL_BYTES`` bytes are
    read, that window opens on a line break, and a leading ``check:`` line
    names the hidden byte count so the truncation is never silent. The
    plain ``\r``/``\r\n``-to-``\n`` translation keeps CRLF logs reading as
    single-character-broken lines, as the whole-file text read did.
    """
    with open(path, "rb") as log:
        # The unbounded read is replaced by a bounded one: anchor at the
        # window's own start -- the size minus the window, or the file's
        # start when it is smaller than the window -- and read no farther.
        size = log.seek(0, os.SEEK_END)
        log.seek(size - _LOG_TAIL_BYTES if size > _LOG_TAIL_BYTES else 0)
        window = log.read()
    if size > _LOG_TAIL_BYTES:
        # Open on a line break: a window cut into a line's middle would
        # otherwise print that line's tail as if it were a whole line.
        break_at = window.find(b"\n")
        if break_at >= 0:
            window = window[break_at + 1 :]
    shown = len(window)
    text = (
        window.decode("utf-8", errors="replace")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )
    lines = text.split("\n")
    if size > _LOG_TAIL_BYTES:
        hidden = size - shown
        lines.insert(
            0,
            f"check: {hidden} earlier log bytes hidden; "
            f"showing the last {shown}",
        )
    return "\n".join(escape_controls(line) for line in lines)


def _print_results(modules: list[str], statuses: dict[str, int | None],
                   log_paths: dict[str, str], timeout: float) -> int:
    """Print each module's section in discovery order and return its status."""
    failed = timed_out = not_finished = no_tests = 0
    for module in modules:
        log_text = ""
        log_error = None
        if module in log_paths:
            try:
                log_text = _bounded_log_text(log_paths[module])
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
