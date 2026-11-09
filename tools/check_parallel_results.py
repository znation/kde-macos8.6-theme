"""Interpret worker logs and print ordered parallel check results."""

from __future__ import annotations

import os
import stat
import sys

if __package__:
    from tools.containment import open_regular_binary
    from tools.diagnostics import plural
    from tools.terminal import escape_controls
    from tools.text_lines import split_lines
else:
    from containment import open_regular_binary
    from diagnostics import plural
    from terminal import escape_controls
    from text_lines import split_lines

_NO_TESTS_RAN = 5
# The most of a worker log one printed section keeps. A worker killed at its
# timeout while flooding its log (a test that prints in a loop) leaves a file
# far larger than the tail worth printing, so the printed window matches the
# bounded-window pattern the shared failure reporter reads a command log's
# tail with (tools/diagnostics.py's _LOG_TAIL_BYTES).
_LOG_TAIL_BYTES = 1 << 16
_NO_TESTS_RAN_MARKERS = ("Ran 0 tests", "NO TESTS RAN")


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
    descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise OSError(f"worker log is not a regular file: {path}")
        log = os.fdopen(descriptor, "rb")
        descriptor = -1
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    with log:
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
    lines = split_lines(window.decode("utf-8", errors="replace"))
    if size > _LOG_TAIL_BYTES:
        hidden = size - shown
        lines.insert(
            0,
            f"check: {hidden} earlier log bytes hidden; "
            f"showing the last {shown}",
        )
    return "\n".join(escape_controls(line) for line in lines)


# unittest's verbose runner prints each test as ``test_x (pkg.Cls) ... ok``.
# The scan below looks for the ``)`` closing the test id, the whitespace after
# it, and the three dots of the ``...`` suffix; the states follow that order.
_MARKER_SEEKS_PAREN = 0
_MARKER_SEEKS_SPACE = 1
_MARKER_COUNTS_DOTS = 2


def _test_marker_step(byte: int, state: int, dots: int) -> tuple[int, int, bool]:
    """Consume one byte of the verbose test-start marker scan.

    Return the next ``(state, dots)`` pair and whether the byte completed
    the ``) `` plus three-dot marker. A newline forgets a partial match so
    a closing parenthesis or dots in ordinary text never carry over to a
    later line.
    """
    if state == _MARKER_SEEKS_PAREN:
        if byte == ord(")"):
            return _MARKER_SEEKS_SPACE, dots, False
        return _MARKER_SEEKS_PAREN, dots, False
    if state == _MARKER_SEEKS_SPACE:
        if byte in b" \t\r\n\v\f":
            return _MARKER_COUNTS_DOTS, 0, False
        if byte == ord(")"):
            return _MARKER_SEEKS_SPACE, dots, False
        return _MARKER_SEEKS_PAREN, dots, False
    # _MARKER_COUNTS_DOTS: inside the test line, after the id's whitespace.
    if byte in b"\r\n":
        return _MARKER_SEEKS_PAREN, 0, False
    if byte == ord("."):
        return _MARKER_COUNTS_DOTS, dots + 1, False
    if dots == 3 and byte in b" \t\v\f":
        return _MARKER_COUNTS_DOTS, dots, True
    return _MARKER_COUNTS_DOTS, 0, False


def _log_has_started_test(path: str) -> bool:
    """Find unittest's verbose test-start marker without loading the log.

    The log is opened through the shared regular-file reader: the bounded
    tail read above can see a log as a regular file, and a replacement that
    turns it into a FIFO before this scan would block plain ``open()`` on a
    pipe with no writer, stalling the whole run's result report. The byte
    transitions live in ``_test_marker_step``; this loop only feeds bytes
    and stops at the first completed marker.
    """
    state = _MARKER_SEEKS_PAREN
    dots = 0
    with open_regular_binary(path) as log:
        while chunk := log.read(8192):
            for byte in chunk:
                state, dots, completed = _test_marker_step(byte, state, dots)
                if completed:
                    return True
    return False


def _module_verdict(module: str, statuses: dict[str, int | None],
                    log_paths: dict[str, str], timeout: float
                    ) -> tuple[str, str, str]:
    """Return a module's display verdict, summary category and log text."""
    log_text = ""
    if module in log_paths:
        try:
            log_text = _bounded_log_text(log_paths[module])
        except OSError:
            return "worker log could not be read", "failed", ""
    if module not in statuses:
        return "did not finish", "not_finished", log_text
    status = statuses[module]
    if status is None:
        return (f"timed out after {timeout:.0f}s (process group killed)",
                "timed_out", log_text)
    if status != _NO_TESTS_RAN:
        return f"exit {status}", "failed" if status != 0 else "ok", log_text
    if module in log_paths:
        try:
            started_test = _log_has_started_test(log_paths[module])
        except (OSError, ValueError):
            return "worker log could not be read", "failed", ""
    else:
        started_test = False
    has_summary = all(marker in log_text for marker in _NO_TESTS_RAN_MARKERS)
    if has_summary and not started_test:
        return "ran no tests (unittest's NO TESTS RAN, exit 5)", "no_tests", log_text
    if not has_summary:
        return ("exit 5 but the log shows no unittest NO TESTS RAN summary",
                "failed", log_text)
    return ("exit 5 but the log shows a started test beside "
            "unittest's NO TESTS RAN summary", "failed", log_text)


def _print_results(modules: list[str], statuses: dict[str, int | None],
                   log_paths: dict[str, str], timeout: float) -> int:
    """Print each module's section in discovery order and return its status."""
    failed = timed_out = not_finished = no_tests = 0
    for module in modules:
        verdict, category, log_text = _module_verdict(
            module, statuses, log_paths, timeout
        )
        failed += category == "failed"
        timed_out += category == "timed_out"
        not_finished += category == "not_finished"
        no_tests += category == "no_tests"
        # The module name is contributor-supplied text: discovery's filename
        # validator covers only a module's final file name, not the directory
        # names of the package path, so a checked-in test directory may carry
        # an ESC byte or a newline into the module name. Escaped here, it
        # cannot drive the operator's terminal or forge a verdict line the
        # way the raw name would.
        print(f"===== {escape_controls(module)}: {verdict} =====")
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
