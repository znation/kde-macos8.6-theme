"""Tests for the started-test marker scan in tools/check/parallel_results.py.

Pins ``_test_marker_step``'s per-byte transitions and ``_log_has_started_test``
carrying the marker state across its 8192-byte reads. The results report
itself is pinned in ``tests/test_check_parallel_results.py``.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.check.parallel_results import (
    _MARKER_COUNTS_DOTS,
    _MARKER_SEEKS_PAREN,
    _MARKER_SEEKS_SPACE,
    _log_has_started_test,
    _test_marker_step,
)


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

    def test_tab_after_the_id_enters_the_dot_count(self):
        # The whitespace set after the id's ``)`` is b" \t\r\n\v\f"; the
        # space and newline spellings are pinned above, so pin the tab
        # spelling here: a class narrowed to the printed forms would
        # otherwise pass every other test in this class.
        state, dots, completed = _test_marker_step(
            ord("\t"), _MARKER_SEEKS_SPACE, 0
        )
        self.assertEqual(state, _MARKER_COUNTS_DOTS)
        self.assertEqual(dots, 0)
        self.assertFalse(completed)
        # - "test_x " is bytes 0-6, "(pkg.Cls)" is bytes 7-15, the tab at
        # 16 is the sought whitespace, the dots take 17-19, and the space
        # at 20 completes.
        self.assertEqual(self._scan("test_x (pkg.Cls)\t... ok"), 20)

    def test_carriage_return_vtab_and_formfeed_after_the_id_also_enter_the_dot_count(self):
        # The remaining three whitespace bytes of the b" \t\r\n\v\f" set
        # after the id's ``)`` each enter the dot count, leaving dots at 0.
        for whitespace in ("\r", "\v", "\f"):
            with self.subTest(whitespace=whitespace):
                state, dots, completed = _test_marker_step(
                    ord(whitespace), _MARKER_SEEKS_SPACE, 0
                )
                self.assertEqual(state, _MARKER_COUNTS_DOTS)
                self.assertEqual(dots, 0)
                self.assertFalse(completed)

    def test_tab_vtab_and_formfeed_after_three_dots_complete_the_marker(self):
        # The completion set after a full three-dot run is b" \t\v\f":
        # the space spelling is pinned above, so pin the three control
        # spellings. Each stays in the counting state and keeps the count,
        # and each completes the marker in a whole-log scan.
        for whitespace in ("\t", "\v", "\f"):
            with self.subTest(whitespace=whitespace):
                state, dots, completed = _test_marker_step(
                    ord(whitespace), _MARKER_COUNTS_DOTS, 3
                )
                self.assertEqual(state, _MARKER_COUNTS_DOTS)
                self.assertEqual(dots, 3)
                self.assertTrue(completed)
                # - "test_x " is bytes 0-6, "(pkg.Cls)" is bytes 7-15, the
                # space at 16 is the id's whitespace, the dots take 17-19,
                # and the completing whitespace sits at 20.
                text = "test_x (pkg.Cls) ..." + whitespace
                self.assertEqual(self._scan(text), 20)

    def test_a_carriage_return_inside_the_dot_count_returns_to_the_paren_seek(self):
        # The counting state treats a carriage return like the newline
        # pinned above: both are line terminators in the b"\r\n" reset
        # set, so a CR forgets the partial dot run and drops the scan back
        # to the paren seek instead of completing the marker.
        state, dots, completed = _test_marker_step(
            ord("\r"), _MARKER_COUNTS_DOTS, 2
        )
        self.assertEqual(state, _MARKER_SEEKS_PAREN)
        self.assertEqual(dots, 0)
        self.assertFalse(completed)
        self.assertIsNone(self._scan("test_x (pkg.Cls) ..\rok"))


class TestStartedTestMarkerAcrossReadChunks(unittest.TestCase):
    """The file scan reads the log 8192 bytes at a time and must carry the
    marker state across the read boundary.

    Each case places a marker so the boundary falls after *k* of its bytes,
    for every *k* that leaves its completing byte in the second chunk. A scan
    that restarted its state at each read would miss the marker.
    """

    READ_CHUNK = 8192  # the scan's log.read() size in _log_marks_started_test

    def _log_with_marker_at_boundary(self, marker: bytes, k: int) -> bool:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "worker.log"
            prefix = b"x" * (self.READ_CHUNK - k)
            path.write_bytes(prefix + marker + b"\n")
            return _log_has_started_test(str(path))

    def test_a_marker_split_across_the_read_boundary_is_found(self):
        marker = b") ... "  # the marker's dots and completing space
        for k in range(1, len(marker)):  # boundary after k marker bytes
            with self.subTest(bytes_before_boundary=k):
                self.assertTrue(self._log_with_marker_at_boundary(marker, k))

    def test_two_dots_split_across_the_read_boundary_are_not_a_marker(self):
        non_marker = b") .. "
        for k in range(1, len(non_marker)):
            with self.subTest(bytes_before_boundary=k):
                self.assertFalse(self._log_with_marker_at_boundary(non_marker, k))


if __name__ == "__main__":
    unittest.main()
