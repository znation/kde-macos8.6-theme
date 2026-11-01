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
    _bounded_log_text,
    _print_results,
)


class TestBoundedLogText(unittest.TestCase):
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
        self.assertIn(" earlier log bytes hidden; showing the last ", result)
        self.assertTrue(result.endswith("visible\n"), result[-80:])
        self.assertNotIn("x", result)


class TestPrintResults(unittest.TestCase):
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
                status = _print_results(
                    ["example"], {"example": 5}, {"example": str(path)}, 30
                )

        self.assertEqual(status, 1)
        self.assertIn(
            "example: exit 5 but the log shows a started test beside ",
            output.getvalue(),
        )
        self.assertIn("check: 1 module, 1 module failed", output.getvalue())


if __name__ == "__main__":
    unittest.main()
