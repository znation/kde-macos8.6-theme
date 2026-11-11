"""Pagination for vertical fidelity mismatch intervals."""

from __future__ import annotations

import json
import unittest

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import difference_pair  # noqa: E402


class TestDifferenceColumnRunsOffset(FidelityCliTestCase):
    """Test paging vertical runs by their global offset."""
    def _pair(self):
        return difference_pair(
            2, 9, ({0, 2, 3, 5, 6, 7}, {0, 1, 2, 3, 8}), vertical=True)

    def test_offset_is_global_after_length_filters(self):
        candidate, reference = self._pair()
        base = ("--difference-column-runs", "--difference-column-run-count",
                "--longest-difference-column-run", "--json")
        all_runs = [
            {"x": 0, "y": 0, "length": 1}, {"x": 0, "y": 2, "length": 2},
            {"x": 0, "y": 5, "length": 3}, {"x": 1, "y": 0, "length": 4},
            {"x": 1, "y": 8, "length": 1},
        ]
        page = json.loads(self._run_png_pair(
            candidate, reference, *base, "--max-difference-column-runs", "2",
            "--difference-column-run-offset", "2").stdout)
        self.assertEqual(page["difference_column_runs"], all_runs[2:4])
        self.assertEqual(page["omitted_difference_column_runs"], 3)
        self.assertEqual(page["difference_column_run_offset"], 2)
        self.assertEqual(page["difference_column_run_count"], 5)
        self.assertEqual(page["longest_difference_column_run"],
                         {"x": 1, "y": 0, "length": 4})

        minimum = json.loads(self._run_png_pair(
            candidate, reference, *base, "--min-difference-column-run-length", "2",
            "--max-difference-column-runs", "1", "--difference-column-run-offset", "1").stdout)
        self.assertEqual(minimum["difference_column_runs"], [all_runs[2]])
        self.assertEqual(minimum["omitted_difference_column_runs"], 2)
        maximum = json.loads(self._run_png_pair(
            candidate, reference, *base, "--max-difference-column-run-length", "2",
            "--max-difference-column-runs", "1", "--difference-column-run-offset", "1").stdout)
        self.assertEqual(maximum["difference_column_runs"], [all_runs[1]])
        self.assertEqual(maximum["omitted_difference_column_runs"], 2)
        beyond = json.loads(self._run_png_pair(
            candidate, reference, *base, "--max-difference-column-runs", "2",
            "--difference-column-run-offset", "5").stdout)
        self.assertEqual(beyond["difference_column_runs"], [])
        self.assertEqual(beyond["omitted_difference_column_runs"], 5)

    def test_zero_text_and_omitted_offset_contract(self):
        candidate, reference = self._pair()
        text = self._run_png_pair(candidate, reference, "--difference-column-runs",
                                  "--max-difference-column-runs", "2",
                                  "--difference-column-run-offset", "0")
        self.assertIn("difference column run offset: 0", text.stdout)
        self.assertIn('difference column runs: [{"x": 0, "y": 0, "length": 1}, {"x": 0, "y": 2, "length": 2}]', text.stdout)
        unpaged = json.loads(self._run_png_pair(
            candidate, reference, "--difference-column-runs", "--json").stdout)
        self.assertNotIn("difference_column_run_offset", unpaged)
        self.assertNotIn("omitted_difference_column_runs", unpaged)

    def test_invalid_offset_and_dependencies_fail_before_reads(self):
        for value in ("-1", "+1", "1.5", " 1", "x", "١"):
            result = self._run("missing.png", "missing.png", "--difference-column-runs",
                               "--max-difference-column-runs", "2",
                               "--difference-column-run-offset", value)
            self._assert_usage_error(result, "--difference-column-run-offset")
            self.assertEqual(result.stdout, "")
        for args, message in [
            (("--difference-column-runs", "--difference-column-run-offset", "0"),
             "--difference-column-run-offset requires --max-difference-column-runs"),
            (("--max-difference-column-runs", "2", "--difference-column-run-offset", "0"),
             "--max-difference-column-runs requires --difference-column-runs"),
        ]:
            result = self._run("missing.png", "missing.png", *args)
            self._assert_usage_error(result, message)
            self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
