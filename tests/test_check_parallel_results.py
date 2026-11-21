"""Tests for bounded worker-log reporting in check_parallel_results.

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
from tools.check_parallel_results import (
    _LOG_TAIL_BYTES,
    _bounded_log_text,
    print_results,
    count_noun,
)


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
            output = StringIO()
            with redirect_stdout(output):
                status = print_results(
                    ["broken", "ok"],
                    {"broken": 0, "ok": 0},
                    {"broken": str(path)},
                    30,
                )

        self.assertEqual(status, 1)
        self.assertIn("===== broken: worker log could not be read =====", output.getvalue())
        self.assertIn("===== ok: exit 0 =====", output.getvalue())
        self.assertIn("check: 2 modules, 1 module failed", output.getvalue())

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
                output = StringIO()
                with redirect_stdout(output):
                    status = print_results(
                        ["first", "second"],
                        {"first": 0, "second": 0},
                        {"first": str(path)},
                        30,
                    )

                self.assertEqual(status, 0)
                self.assertEqual(
                    output.getvalue(),
                    "===== first: exit 0 =====\n" + body
                    + "===== second: exit 0 =====\n",
                )

    def test_module_name_control_characters_are_escaped_in_the_header(self):
        module = "pkg\x1b[31m\nforged"
        output = StringIO()
        with redirect_stdout(output):
            print_results([module], {module: 0}, {}, 30)

        text = output.getvalue()
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
            output = StringIO()
            with redirect_stdout(output):
                status = print_results(
                    ["example"], {"example": 5}, {"example": str(path)}, 30
                )

        self.assertEqual(status, 1)
        self.assertIn(
            "example: exit 5 but the log shows a started test beside ",
            output.getvalue(),
        )
        self.assertIn("check: 1 module, 1 module failed", output.getvalue())

    def test_missing_worker_log_fails_even_when_worker_exited_zero(self):
        output = StringIO()
        with redirect_stdout(output):
            status = print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": "/missing/worker.log"}, 10
            )
        self.assertEqual(1, status)
        self.assertIn("test_ok: worker log could not be read", output.getvalue())
        self.assertIn("1 module failed", output.getvalue())

    def test_fifo_worker_log_read_fails_without_blocking(self):
        fifo = make_tmp_dir(self) / "worker.log"
        os.mkfifo(fifo)
        output = StringIO()
        with redirect_stdout(output):
            status = print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": str(fifo)}, 10
            )
        self.assertEqual(1, status)
        self.assertIn("test_ok: worker log could not be read", output.getvalue())
        self.assertIn("1 module failed", output.getvalue())

    def test_a_fifo_started_test_scan_fails_without_blocking(self):
        fifo = make_tmp_dir(self) / "worker.log"
        os.mkfifo(fifo)
        # An exit-5 log with a complete NO TESTS RAN summary reaches the
        # started-test scan, so the bounded tail read must see a regular file
        # and a FIFO substituted before that scan still fails the module: the
        # scan's plain open() used to block on the pipe with no writer.
        with mock.patch(
            "tools.check_parallel_results._bounded_log_text",
            return_value="Ran 0 tests\nNO TESTS RAN\n",
        ):
            output = StringIO()
            with redirect_stdout(output):
                status = print_results(
                    ["test_ok"], {"test_ok": 5}, {"test_ok": str(fifo)}, 10
                )
        self.assertEqual(1, status)
        self.assertIn("test_ok: worker log could not be read", output.getvalue())
        self.assertIn("1 module failed", output.getvalue())

    def test_missing_worker_status_reports_did_not_finish_and_keeps_log(self):
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_text("partial worker output\n", encoding="utf-8")
        output = StringIO()
        with redirect_stdout(output):
            status = print_results(
                ["test_ok"], {}, {"test_ok": str(log_path)}, 10
            )
        self.assertEqual(1, status)
        self.assertIn("===== test_ok: did not finish =====", output.getvalue())
        self.assertIn("partial worker output", output.getvalue())
        self.assertIn("1 module not finished", output.getvalue())

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
        output = StringIO()
        with redirect_stdout(output):
            status = print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": str(log_path)}, 10
            )
        text = output.getvalue()
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
        output = StringIO()
        with redirect_stdout(output):
            status = print_results(
                ["test_ok"], {"test_ok": 5}, {"test_ok": str(log_path)}, 10
            )
        self.assertEqual(0, status)
        self.assertIn(
            "===== test_ok: ran no tests (unittest's NO TESTS RAN, exit 5) =====",
            output.getvalue(),
        )

    def test_invalid_utf8_in_worker_log_is_replaced(self):
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(b"worker output: \xff\n")
        output = StringIO()
        with redirect_stdout(output):
            status = print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": str(log_path)}, 10
            )
        self.assertEqual(0, status)
        self.assertIn("worker output: \ufffd", output.getvalue())

    def test_a_window_without_any_line_break_is_shown_whole(self):
        # A worker killed while writing one continuous line can leave a log
        # whose whole tail window carries no newline at all: there is no
        # break to open on, so the note must still account every byte
        # exactly -- the window is shown whole (65536) and the difference
        # from the file's size is named -- instead of dropping the tail.
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(b"x" * 100_000)
        output = StringIO()
        with redirect_stdout(output):
            status = print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": str(log_path)}, 10
            )
        self.assertEqual(0, status)
        self.assertIn(
            "check: 34464 earlier log bytes hidden; showing the last 65536",
            output.getvalue(),
        )
        self.assertIn("x" * 65_536, output.getvalue())

    def test_crlf_worker_log_lines_end_before_the_line_breaks(self):
        # The bounded read replaced a text-mode whole-file read, whose
        # universal newlines folded CRLF and bare CR into LF. A CRLF
        # worker log must still read as one line per record after the
        # switch to the binary bounded read -- not as one line carrying
        # literal carriage returns.
        log_path = make_tmp_dir(self) / "worker.log"
        log_path.write_bytes(b"line one\r\nline two\r\nRan 1 test in 0.001s\n\nOK\n")
        output = StringIO()
        with redirect_stdout(output):
            status = print_results(
                ["test_ok"], {"test_ok": 0}, {"test_ok": str(log_path)}, 10
            )
        self.assertEqual(0, status)
        text = output.getvalue()
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
        output = StringIO()
        with redirect_stdout(output):
            status = print_results(
                ["test_empty", "test_failed"],
                {"test_empty": 5, "test_failed": 1},
                {"test_empty": str(empty_log), "test_failed": str(failed_log)},
                10,
            )
        self.assertEqual(1, status)
        self.assertIn("test_empty: ran no tests", output.getvalue())
        self.assertIn("test_failed: exit 1", output.getvalue())
        self.assertIn(
            "check: 2 modules, 1 module failed, 1 module ran no tests",
            output.getvalue(),
        )

    def test_summary_combines_failed_timed_out_and_unfinished_modules(self):
        failed_log = make_tmp_dir(self) / "failed.log"
        failed_log.write_text("failure detail\n", encoding="utf-8")
        timeout_log = make_tmp_dir(self) / "timeout.log"
        timeout_log.write_text("partial output\n", encoding="utf-8")
        output = StringIO()
        with redirect_stdout(output):
            status = print_results(
                ["test_failed", "test_timeout", "test_unfinished"],
                {"test_failed": 1, "test_timeout": None},
                {"test_failed": str(failed_log), "test_timeout": str(timeout_log)},
                2,
            )
        self.assertEqual(1, status)
        rendered = output.getvalue()
        self.assertIn("test_failed: exit 1", rendered)
        self.assertIn("test_timeout: timed out after 2s (process group killed)", rendered)
        self.assertIn("test_unfinished: did not finish", rendered)
        self.assertIn(
            "check: 3 modules, 1 module failed, 1 module timed out, "
            "1 module not finished",
            rendered,
        )

    def test_summary_counts_multiple_failed_workers_including_a_signal_exit(self):
        output = StringIO()
        with redirect_stdout(output):
            status = print_results(
                ["test_failed", "test_signalled"],
                {"test_failed": 1, "test_signalled": -9},
                {},
                10,
            )
        rendered = output.getvalue()
        self.assertEqual(1, status)
        self.assertIn("test_failed: exit 1", rendered)
        self.assertIn("test_signalled: exit -9", rendered)
        self.assertIn("check: 2 modules, 2 modules failed", rendered)

    def test_summary_counts_empty_module_alongside_a_timeout(self):
        empty_log = make_tmp_dir(self) / "empty.log"
        empty_log.write_text(
            "Ran 0 tests in 0.000s\n\nNO TESTS RAN\n", encoding="utf-8"
        )
        output = StringIO()
        with redirect_stdout(output):
            status = print_results(
                ["test_empty", "test_timeout"],
                {"test_empty": 5, "test_timeout": None},
                {"test_empty": str(empty_log)},
                3,
            )
        self.assertEqual(1, status)
        rendered = output.getvalue()
        self.assertIn("test_empty: ran no tests", rendered)
        self.assertIn(
            "test_timeout: timed out after 3s (process group killed)", rendered
        )
        self.assertIn(
            "check: 2 modules, 1 module timed out, 1 module ran no tests",
            rendered,
        )


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
