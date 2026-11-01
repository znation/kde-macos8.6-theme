"""Tests for bounded worker-log reporting in check_parallel_results."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.check_parallel_results import _LOG_TAIL_BYTES, _bounded_log_text


class TestBoundedLogText(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
