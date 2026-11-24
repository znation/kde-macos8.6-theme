"""Tests for bounded worker-log reporting in tools/check/parallel_results.py.

The started-test marker scan is pinned in ``tests/test_check_parallel_marker.py``.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.tmp_dir import make_tmp_dir
from tools.check.parallel_results import (
    _LOG_TAIL_BYTES,
    _bounded_log_text,
    print_results,
    count_noun,
)


def _run_report(modules, statuses, log_paths, timeout=30):
    """Run print_results with stdout captured; return (status, printed text).

    Both reporter suites (TestPrintResults and TestPrintResultsOrder) call
    the reporter in-process with stdout captured; this is the one place
    holding that boilerplate. Twenty-two call sites.
    """
    output = StringIO()
    with redirect_stdout(output):
        status = print_results(modules, statuses, log_paths, timeout)
    return status, output.getvalue()


class TestBoundedLogText(unittest.TestCase):
    def test_log_exactly_the_tail_window_is_not_marked_truncated(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "worker.log"
            contents = b"x" * (_LOG_TAIL_BYTES - 1) + b"\n"
            path.write_bytes(contents)

            result = _bounded_log_text(str(path))

        self.assertEqual(result, contents.decode("ascii"))
        self.assertNotIn("earlier log bytes hidden", result)

    def test_normalizes_crlf_and_bare_cr_line_endings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "worker.log"
            path.write_bytes(b"first\r\nsecond\rthird\n")

            result = _bounded_log_text(str(path))

        self.assertEqual(result, "first\nsecond\nthird\n")

    def test_large_log_starts_after_first_complete_line_in_tail_window(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "worker.log"
            # The tail window starts in this line. The reporter must discard
            # its partial suffix, then account for those bytes as hidden.
            prefix = b"x" * (_LOG_TAIL_BYTES + 20) + b"\nvisible\n"
            path.write_bytes(prefix)

            result = _bounded_log_text(str(path))

        self.assertTrue(result.startswith("check: "), result[:80])
        # Only "visible\n" (8 bytes) survives; every earlier byte, including
        # the discarded partial line inside the window, is counted hidden.
        shown = len(b"visible\n")
        self.assertEqual(
            f"check: {len(prefix) - shown} earlier log bytes hidden; "
            f"showing the last {shown}",
            result.split("\n", 1)[0],
        )
        self.assertTrue(result.endswith("visible\n"), result[-80:])
        self.assertNotIn("x", result)

    def test_large_single_line_log_stays_bounded_without_a_line_break(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "worker.log"
            contents = b"x" * (_LOG_TAIL_BYTES + 20)
            path.write_bytes(contents)

            result = _bounded_log_text(str(path))

        expected = (
            f"check: 20 earlier log bytes hidden; showing the last {_LOG_TAIL_BYTES}\n"
            + "x" * _LOG_TAIL_BYTES
        )
        self.assertEqual(result, expected)


class TestPrintResults(unittest.TestCase):
    def test_directory_worker_log_fails_without_stopping_the_report(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            status, text = _run_report(
                ["broken", "ok"],
                {"broken": 0, "ok": 0},
                {"broken": str(path)},
                30,
            )

        self.assertEqual(status, 1)
        self.assertIn("===== broken: worker log could not be read =====", text)
        self.assertIn("===== ok: exit 0 =====", text)
        self.assertIn("check: 2 modules, 1 module failed", text)

    def test_a_log_without_a_final_newline_ends_before_the_next_header(self):
        # Each section's log is followed by the next "=====" header. A log
        # whose last line has no newline must get one, or the next header is
        # glued onto that line; a log that already ends in a newline must not
        # gain a blank line.
        cases = (
            (b"partial output", "partial output\n"),
            (b"done\n", "done\n"),
        )
        for contents, body in cases:
            with self.subTest(contents=contents), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "first.log"
                path.write_bytes(contents)
                status, text = _run_report(
                    ["first", "second"],
                    {"first": 0, "second": 0},
                    {"first": str(path)},
                    30,
                )

                self.assertEqual(status, 0)
                self.assertEqual(
                    text,
                    "===== first: exit 0 =====\n" + body
                    + "===== second: exit 0 =====\n",
                )

    def test_module_name_control_characters_are_escaped_in_the_header(self):
        module = "pkg\x1b[31m\nforged"
        _, text = _run_report([module], {module: 0}, {}, 30)
        self.assertNotIn("\x1b", text)
        self.assertIn("pkg\\u001b[31m\\u000aforged: exit 0", text)

    def test_exit_five_with_test_line_and_empty_run_markers_is_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "worker.log"
            path.write_text(
                "test_example (__main__.Example) ... ok\n"
                "Ran 0 tests\nNO TESTS RAN\n",
                encoding="utf-8",
            )
            status, text = _run_report(
                ["example"], {"example": 5}, {"example": str(path)}, 30
            )

        self.assertEqual(status, 1)
        self.assertIn(
            "example: exit 5 but the log shows a started test beside ",
            text,
        )
        self.assertIn("check: 1 module, 1 module failed", text)

    def test_exit_five_without_the_summary_is_failure_not_no_tests(self):
        log_path = make_tmp_dir(self) / "worker.log"
        # A worker that exits 5 but leaves a log cut before unittest's
        # summary (killed mid-write, or a crash before the runner reported)
        # must count as a failed module, not as "ran no tests": without the
        # summary the log proves nothing about which tests the worker ran.
        log_path.write_text(
            "test_example\nok\nworker died before the runner reported\n",
            encoding="utf-8",
        )
        status, text = _run_report(
            ["test_ok"], {"test_ok": 5}, {"test_ok": str(log_path)}, 10
        )
        self.assertEqual(1, status)
        self.assertIn(
            "===== test_ok: exit 5 but the log shows no unittest "
            "NO TESTS RAN summary =====",
            text,
        )
        self.assertIn("worker died before the runner reported", text)
        self.assertIn(
            "check: test_ok: exit 5 but the log shows no unittest "
            "NO TESTS RAN summary",
            text,
        )
        self.assertIn("1 module failed", text)

    def test_missing_worker_log_fails_even_when_worker_exited_zero(self):
        status, text = _run_report(
            ["test_ok"], {"test_ok": 0}, {"test_ok": "/missing/worker.log"}, 10
        )
        self.assertEqual(1, status)
        self.assertIn("test_ok: worker log could not be read", text)
        self.assertIn("1 module failed", text)

    def test_fifo_worker_log_read_fails_without_blocking(self):
        fifo = make_tmp_dir(self) / "worker.log"
        os.mkfifo(fifo)
        status, text = _run_report(
            ["test_ok"], {"test_ok": 0}, {"test_ok": str(fifo)}, 10
        )
        self.assertEqual(1, status)
        self.assertIn("test_ok: worker log could not be read", text)
        self.assertIn("1 module failed", text)

    def test_a_fifo_started_test_scan_fails_without_blocking(self):
        fifo = make_tmp_dir(self) / "worker.log"
        os.mkfifo(fifo)
        # An exit-5 log with a complete NO TESTS RAN summary reaches the
        # started-test scan, so the bounded tail read must see a regular file
        # and a FIFO substituted before that scan still fails the module: the
        # scan's plain open() used to block on the pipe with no writer.
        with mock.patch(
            "tools.check.parallel_results._bounded_log_text",
            return_value="Ran 0 tests\nNO TESTS RAN\n",
        ):
            status, text = _run_report(
                ["test_ok"], {"test_ok": 5}, {"test_ok": str(fifo)}, 10
            )
        self.assertEqual(1, status)
        self.assertIn("test_ok: worker log could not be read", text)
        self.assertIn("1 module failed", text)

    def test_missing_worker_status_reports_did_not_finish_and_keeps_log(self):
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_text("partial worker output\n", encoding="utf-8")
        status, text = _run_report(
            ["test_ok"], {}, {"test_ok": str(log_path)}, 10
        )
        self.assertEqual(1, status)
        self.assertIn("===== test_ok: did not finish =====", text)
        self.assertIn("partial worker output", text)
        self.assertIn("1 module not finished", text)

    def test_a_flooded_log_prints_a_bounded_tail_with_a_hidden_byte_note(self):
        """A log past the printed section's cap keeps only its tail.

        A worker killed at its timeout while flooding its log can leave a
        file far larger than the tail worth reading: the section reads only
        the last window, opens it on a line break, and names the hidden
        bytes on a leading note line instead of loading and echoing the
        whole flood (whose MemoryError would never be the OSError the
        unreadable-log case catches, killing the whole results report).
        """
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(b"x" * 100_000 + b"\n" + b"tail line\n" + b"Ran 1 test in 0.001s\n\nOK\n")
        status, text = _run_report(
            ["test_ok"], {"test_ok": 0}, {"test_ok": str(log_path)}, 10
        )
        self.assertEqual(0, status)
        # The flood is gone from the printout: a window cut at 64 KiB falls
        # inside the x-run, and everything through the flood line's break
        # (the partial line the window opens on) is dropped with it.
        self.assertNotIn("x" * 65_536, text)
        self.assertNotIn("x" * 55_000, text)
        self.assertLess(len(text), 100_000)
        # The truncation is named, not silent, and the log's own tail survives.
        self.assertIn(
            "===== test_ok: exit 0 =====\ncheck: ",
            text,
        )
        self.assertIn("earlier log bytes hidden; showing the last ", text)
        self.assertIn("tail line\n", text)
        self.assertIn("Ran 1 test in 0.001s", text)
        self.assertIn("\nOK\n", text)

    def test_a_flooded_log_keeps_its_end_of_log_summary_verdict(self):
        """The exit-5 summary check still sees unittest's end-of-log summary.

        unittest prints its ``Ran 0 tests``/``NO TESTS RAN`` summary at the
        very end of the worker log, so the bounded tail window always holds
        both markers: a flooded log must not misreport a genuinely empty run
        as one without an exit-5 verdict.
        """
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(
            # A realistic flood: the summary follows the flood's own line
            # break, as unittest's summary always ends a line it started.
            b"x" * 100_000
            + b"\n"
            + b"Ran 0 tests in 0.000s\n\nNO TESTS RAN\n"
        )
        status, text = _run_report(
            ["test_ok"], {"test_ok": 5}, {"test_ok": str(log_path)}, 10
        )
        self.assertEqual(0, status)
        self.assertIn(
            "===== test_ok: ran no tests (unittest's NO TESTS RAN, exit 5) =====",
            text,
        )

    def test_invalid_utf8_in_worker_log_is_replaced(self):
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(b"worker output: \xff\n")
        status, text = _run_report(
            ["test_ok"], {"test_ok": 0}, {"test_ok": str(log_path)}, 10
        )
        self.assertEqual(0, status)
        self.assertIn("worker output: \ufffd", text)

    def test_a_window_without_any_line_break_is_shown_whole(self):
        # A worker killed while writing one continuous line can leave a log
        # whose whole tail window carries no newline at all: there is no
        # break to open on, so the note must still account every byte
        # exactly -- the window is shown whole (65536) and the difference
        # from the file's size is named -- instead of dropping the tail.
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(b"x" * 100_000)
        status, text = _run_report(
            ["test_ok"], {"test_ok": 0}, {"test_ok": str(log_path)}, 10
        )
        self.assertEqual(0, status)
        self.assertIn(
            "check: 34464 earlier log bytes hidden; showing the last 65536",
            text,
        )
        self.assertIn("x" * 65_536, text)

    def test_crlf_worker_log_lines_end_before_the_line_breaks(self):
        # The bounded read replaced a text-mode whole-file read, whose
        # universal newlines folded CRLF and bare CR into LF. A CRLF
        # worker log must still read as one line per record after the
        # switch to the binary bounded read -- not as one line carrying
        # literal carriage returns.
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(b"line one\r\nline two\r\nRan 1 test in 0.001s\n\nOK\n")
        status, text = _run_report(
            ["test_ok"], {"test_ok": 0}, {"test_ok": str(log_path)}, 10
        )
        self.assertEqual(0, status)
        self.assertIn("line one\nline two\n", text)
        self.assertNotIn("line one\r", text)
        self.assertNotIn("\u000d", text)

    def test_mixed_empty_and_failed_modules_report_both_outcomes(self):
        empty_log = make_tmp_dir(self) / "empty.log"
        empty_log.write_text(
            "Ran 0 tests in 0.000s\n\nNO TESTS RAN\n", encoding="utf-8"
        )
        failed_log = make_tmp_dir(self) / "failed.log"
        failed_log.write_text("failure detail\n", encoding="utf-8")
        status, text = _run_report(
            ["test_empty", "test_failed"],
            {"test_empty": 5, "test_failed": 1},
            {"test_empty": str(empty_log), "test_failed": str(failed_log)},
            10,
        )
        self.assertEqual(1, status)
        self.assertIn("test_empty: ran no tests", text)
        self.assertIn("test_failed: exit 1", text)
        self.assertIn(
            "check: 2 modules, 1 module failed, 1 module ran no tests",
            text,
        )

    def test_summary_combines_failed_timed_out_and_unfinished_modules(self):
        failed_log = make_tmp_dir(self) / "failed.log"
        failed_log.write_text("failure detail\n", encoding="utf-8")
        timeout_log = make_tmp_dir(self) / "timeout.log"
        timeout_log.write_text("partial output\n", encoding="utf-8")
        status, rendered = _run_report(
            ["test_failed", "test_timeout", "test_unfinished"],
            {"test_failed": 1, "test_timeout": None},
            {"test_failed": str(failed_log), "test_timeout": str(timeout_log)},
            2,
        )
        self.assertEqual(1, status)
        self.assertIn("test_failed: exit 1", rendered)
        self.assertIn("test_timeout: timed out after 2s (process group killed)", rendered)
        self.assertIn("test_unfinished: did not finish", rendered)
        self.assertIn(
            "check: 3 modules, 1 module failed, 1 module timed out, "
            "1 module not finished",
            rendered,
        )

    def test_summary_counts_multiple_failed_workers_including_a_signal_exit(self):
        status, rendered = _run_report(
            ["test_failed", "test_signalled"],
            {"test_failed": 1, "test_signalled": -9},
            {},
            10,
        )
        self.assertEqual(1, status)
        self.assertIn("test_failed: exit 1", rendered)
        self.assertIn("test_signalled: exit -9", rendered)
        self.assertIn("check: 2 modules, 2 modules failed", rendered)

    def test_summary_counts_empty_module_alongside_a_timeout(self):
        empty_log = make_tmp_dir(self) / "empty.log"
        empty_log.write_text(
            "Ran 0 tests in 0.000s\n\nNO TESTS RAN\n", encoding="utf-8"
        )
        status, rendered = _run_report(
            ["test_empty", "test_timeout"],
            {"test_empty": 5, "test_timeout": None},
            {"test_empty": str(empty_log)},
            3,
        )
        self.assertEqual(1, status)
        self.assertIn("test_empty: ran no tests", rendered)
        self.assertIn(
            "test_timeout: timed out after 3s (process group killed)", rendered
        )
        self.assertIn(
            "check: 2 modules, 1 module timed out, 1 module ran no tests",
            rendered,
        )


class TestPrintResultsOrder(unittest.TestCase):
    """Unsuccessful modules print last, with check lines above the summary."""

    def test_unsuccessful_sections_print_last_with_check_lines_above_summary(self):
        directory = make_tmp_dir(self)
        texts = {
            "a_bad": "alpha-failure-text\n",
            "b_ok": "bravo-pass-text\n",
            "c_empty": "Ran 0 tests in 0.000s\n\nNO TESTS RAN\n",
            "d_hung": "delta-hung-text\n",
            "f_ok": "foxtrot-pass-text\n",
        }
        log_paths = {}
        for module, text in texts.items():
            path = directory / f"{module}.log"
            path.write_text(text, encoding="utf-8")
            log_paths[module] = str(path)
        modules = ["a_bad", "b_ok", "c_empty", "d_hung", "e_lost", "f_ok"]
        statuses = {
            "a_bad": 1,
            "b_ok": 0,
            "c_empty": 5,
            "d_hung": None,
            "f_ok": 0,
        }

        status, out = _run_report(modules, statuses, log_paths)

        self.assertEqual(1, status)
        headers = [line for line in out.splitlines() if line.startswith("=====")]
        self.assertEqual(
            [
                "===== b_ok: exit 0 =====",
                "===== c_empty: ran no tests (unittest's NO TESTS RAN, exit 5) =====",
                "===== f_ok: exit 0 =====",
                "===== a_bad: exit 1 =====",
                "===== d_hung: timed out after 30s (process group killed) =====",
                "===== e_lost: did not finish =====",
            ],
            headers,
        )
        for text in texts.values():
            self.assertEqual(1, out.count(text.rstrip("\n")), text)
        self.assertEqual(
            [
                "check: a_bad: exit 1",
                "check: d_hung: timed out after 30s (process group killed)",
                "check: e_lost: did not finish",
                "check: 6 modules, 1 module failed, 1 module timed out, "
                "1 module not finished, 1 module ran no tests",
            ],
            out.splitlines()[-4:],
        )

    def test_zero_status_unreadable_log_prints_in_the_unsuccessful_group(self):
        unreadable = make_tmp_dir(self)
        status, out = _run_report(
            ["a_ok", "b_bad", "c_ok"],
            {"a_ok": 0, "b_bad": 0, "c_ok": 0},
            {"b_bad": str(unreadable)},
        )

        self.assertEqual(1, status)
        headers = [line for line in out.splitlines() if line.startswith("=====")]
        self.assertEqual(
            [
                "===== a_ok: exit 0 =====",
                "===== c_ok: exit 0 =====",
                "===== b_bad: worker log could not be read =====",
            ],
            headers,
        )
        self.assertEqual(
            [
                "check: b_bad: worker log could not be read",
                "check: 3 modules, 1 module failed",
            ],
            out.splitlines()[-2:],
        )

    def test_passing_and_no_tests_runs_print_sections_only(self):
        directory = make_tmp_dir(self)
        empty_log = directory / "b_empty.log"
        empty_log.write_text("Ran 0 tests in 0.000s\n\nNO TESTS RAN\n", encoding="utf-8")
        status, out = _run_report(
            ["a_ok", "b_empty", "c_ok"],
            {"a_ok": 0, "b_empty": 5, "c_ok": 0},
            {"b_empty": str(empty_log)},
        )

        self.assertEqual(0, status)
        headers = [line for line in out.splitlines() if line.startswith("=====")]
        self.assertEqual(
            [
                "===== a_ok: exit 0 =====",
                "===== b_empty: ran no tests (unittest's NO TESTS RAN, exit 5) =====",
                "===== c_ok: exit 0 =====",
            ],
            headers,
        )
        self.assertNotIn("check:", out)

    def test_failed_module_check_line_escapes_its_name_onto_one_line(self):
        name = "bad\x1b[31m\nname"
        status, out = _run_report([name], {name: 1}, {})

        self.assertEqual(1, status)
        self.assertNotIn("\x1b", out)
        lines = out.splitlines()
        self.assertFalse(any(line.startswith("name") for line in lines), out)
        check_lines = [
            line for line in lines
            if line.startswith("check: bad") and line.endswith(": exit 1")
        ]
        self.assertEqual(1, len(check_lines), out)


class TestCountNoun(unittest.TestCase):
    """``count_noun`` renders the ``<count> <noun>`` summary phrase.

    The summary line in tools/check_parallel.py reads ``check: ..., 1 module,
    4 workers``: a single item takes the bare noun, every other count (zero
    included) takes the ``s`` form, and the count and noun are joined by one
    space.
    """

    def test_one_item_takes_the_singular_noun(self):
        self.assertEqual(count_noun(1, "module"), "1 module")

    def test_zero_takes_the_plural_noun(self):
        self.assertEqual(count_noun(0, "module"), "0 modules")

    def test_many_items_take_the_plural_noun(self):
        self.assertEqual(count_noun(2, "module"), "2 modules")
        self.assertEqual(count_noun(4, "worker"), "4 workers")

    def test_count_and_noun_are_joined_by_one_space(self):
        self.assertEqual(count_noun(1, "worker"), "1 worker")


if __name__ == "__main__":
    unittest.main()
