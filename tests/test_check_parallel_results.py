"""Tests for bounded worker-log reporting in check_parallel_results."""

from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.check_parallel_results import (
    _LOG_TAIL_BYTES,
    _MARKER_COUNTS_DOTS,
    _MARKER_SEEKS_PAREN,
    _MARKER_SEEKS_SPACE,
    _bounded_log_text,
    print_results,
    _test_marker_step,
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


class TestTestMarkerStep(unittest.TestCase):
    """Pin the verbose test-start marker's per-byte transitions."""

    @staticmethod
    def _scan(text: str) -> int | None:
        """Return the 0-based byte index where the marker completes."""
        state = _MARKER_SEEKS_PAREN
        dots = 0
        for index, char in enumerate(text.encode("utf-8")):
            state, dots, completed = _test_marker_step(char, state, dots)
            if completed:
                return index
        return None

    def test_marker_completes_on_the_space_after_three_dots(self):
        self.assertEqual(self._scan("test_x (pkg.Cls) ... ok"), 20)

    def test_two_dots_do_not_complete_the_marker(self):
        self.assertIsNone(self._scan("test_x (pkg.Cls) .. ok"))

    def test_four_dots_then_a_space_do_not_complete_the_marker(self):
        self.assertIsNone(self._scan("test_x (pkg.Cls) .... ok"))

    def test_a_newline_forgets_partial_dots(self):
        # A newline inside the dot count forgets the partial run and drops
        # the scan back to the paren seek, so dots left on one line can no
        # longer be completed by a later line's whitespace.
        state, dots, completed = _test_marker_step(
            ord("\n"), _MARKER_COUNTS_DOTS, 2
        )
        self.assertEqual(state, _MARKER_SEEKS_PAREN)
        self.assertEqual(dots, 0)
        self.assertFalse(completed)
        self.assertIsNone(self._scan("test_x (pkg.Cls) ..\nok"))

    def test_the_whitespace_after_the_id_may_be_a_newline(self):
        # The step description allows the whitespace after the id's ``)``
        # to be a newline itself, so the dots of the following line can
        # still complete the marker. Every end-to-end fixture prints the
        # realistic ``) ... `` spelling on one line, so no other test
        # reaches this whitespace form.
        state, dots, completed = _test_marker_step(
            ord("\n"), _MARKER_SEEKS_SPACE, 0
        )
        self.assertEqual(state, _MARKER_COUNTS_DOTS)
        self.assertEqual(dots, 0)
        self.assertFalse(completed)
        # (pkg.Cls) ends at byte 15, the newline is the sought whitespace
        # at 16, the three dots take 17-19, and the space at 20 completes.
        self.assertEqual(self._scan("test_x (pkg.Cls)\n... ok"), 20)

    def test_an_extra_paren_before_the_whitespace_keeps_looking(self):
        # A second ``)`` still sits where the whitespace after the id is
        # expected: the seek state keeps looking instead of returning to
        # the paren seek, so the following whitespace and dots still find
        # the marker.
        state, _, completed = _test_marker_step(
            ord(")"), _MARKER_SEEKS_SPACE, 0
        )
        self.assertEqual(state, _MARKER_SEEKS_SPACE)
        self.assertFalse(completed)
        # - "test_x " is bytes 0-6, "(pkg.Cls))" is bytes 7-16, the space
        # at 17 is the sought whitespace, the three dots take 18-20, and
        # the space at 21 completes.
        self.assertEqual(self._scan("test_x (pkg.Cls)) ... ok"), 21)

    def test_a_stray_byte_inside_the_dot_count_resets_only_the_count(self):
        # An ordinary stray byte inside the dot count clears the partial
        # count but stays in the counting state, unlike the newline above
        # it, which returns to the paren seek: a later contiguous dot run
        # in the same line can still complete the marker.
        state, dots, completed = _test_marker_step(
            ord("x"), _MARKER_COUNTS_DOTS, 1
        )
        self.assertEqual(state, _MARKER_COUNTS_DOTS)
        self.assertEqual(dots, 0)
        self.assertFalse(completed)
        # - the space at 16 after "(pkg.Cls)", the dot at 17 counts 1,
        # the stray byte at 18 clears the count, the dots at 19-21 count
        # to 3, and the space at 22 completes.
        self.assertEqual(self._scan("test_x (pkg.Cls) .x... ok"), 22)

    def test_stray_byte_after_the_space_returns_to_the_paren_seek(self):
        # A stray byte where the whitespace after the id was expected drops
        # the scan back to the paren seek, and the marker's space after a
        # full dot count completes it one byte at a time.
        state, _, completed = _test_marker_step(ord("x"), _MARKER_SEEKS_SPACE, 0)
        self.assertEqual(state, _MARKER_SEEKS_PAREN)
        self.assertFalse(completed)
        state, _, completed = _test_marker_step(ord(" "), _MARKER_COUNTS_DOTS, 3)
        self.assertTrue(completed)


if __name__ == "__main__":
    unittest.main()
