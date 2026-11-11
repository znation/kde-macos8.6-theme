"""Tests for reading optional subprocess call logs."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support.recorded_lines import recorded_lines


class RecordedLinesTests(unittest.TestCase):
    """Tests for ``support.recorded_lines``' call-log reading."""

    def test_missing_log_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual([], recorded_lines(Path(directory) / "calls"))

    def test_reads_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "calls"
            log.write_text("first\nsecond\n", encoding="utf-8")
            self.assertEqual(["first", "second"], recorded_lines(log))

    def test_propagates_read_errors(self):
        log = Path("calls")
        with mock.patch.object(Path, "read_text", side_effect=PermissionError("denied")):
            with self.assertRaisesRegex(PermissionError, "denied"):
                recorded_lines(log)


if __name__ == "__main__":
    unittest.main()
