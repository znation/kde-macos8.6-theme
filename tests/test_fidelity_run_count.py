"""Scalar horizontal mismatch-run count diagnostics."""

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from tools import fidelity  # noqa: E402
from tools.fidelity_spatial import difference_run_count  # noqa: E402
from tools.png import Image  # noqa: E402


class TestDifferenceRunCount(unittest.TestCase):
    def test_streaming_count_handles_rows_and_tolerance(self):
        rgb = (bytes([11, 0, 0, 12, 0, 0, 0, 0, 0, 11, 0, 0])
               + bytes(12)
               + bytes([11, 0, 0, 12, 0, 0, 13, 0, 0, 14, 0, 0]))
        candidate = Image(4, 3, rgb)
        reference = Image(4, 3, bytes(len(rgb)))
        self.assertEqual(difference_run_count(candidate, reference, 10), 3)
        self.assertEqual(difference_run_count(candidate, reference, 255), 0)


class TestDifferenceRunCountCli(FidelityCliTestCase):
    def test_count_json_text_and_no_extra_scan_with_run_list(self):
        candidate = make_png(4, 3, [bytes([11, 0, 0, 12, 0, 0, 0, 0, 0, 11, 0, 0]),
                                   bytes(12),
                                   bytes([11, 0, 0, 12, 0, 0, 13, 0, 0, 14, 0, 0])])
        reference = make_png(4, 3, [bytes(12), bytes(12), bytes(12)])
        with mock.patch.object(fidelity, "difference_runs", wraps=fidelity.difference_runs):
            result = self._run_png_pair(candidate, reference, "--difference-run-count", "--json")
        self.assertEqual(json.loads(result.stdout)["difference_run_count"], 3)
        self.assertEqual(json.loads(result.stdout)["metrics"]["differing"], 7)
        text = self._run_png_pair(candidate, reference, "--difference-run-count")
        self.assertIn("difference run count: 3", text.stdout)
        with mock.patch.object(fidelity, "difference_run_count", side_effect=AssertionError):
            listed = self._run_png_pair(candidate, reference, "--difference-run-count",
                                         "--difference-runs", "--json")
        self.assertEqual(json.loads(listed.stdout)["difference_run_count"], 3)
        ordinary = self._run_png_pair(candidate, reference, "--json")
        self.assertNotIn("difference_run_count", json.loads(ordinary.stdout))


if __name__ == "__main__":
    unittest.main()
