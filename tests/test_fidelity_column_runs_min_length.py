"""Minimum length filtering for vertical fidelity mismatch runs."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import (  # noqa: E402
    difference_pair,
    make_png,
)
from tools import fidelity  # noqa: E402


class TestColumnRunsMinimumLength(FidelityCliTestCase):
    def _pair(self):
        return difference_pair(
            7, 4, ({0, 1, 3}, {1, 3}, {1, 3}, {3}), vertical=False)

    def test_crop_relative_column_intervals_filter_inclusively(self):
        candidate, reference = self._pair()
        base = ("--difference-column-runs", "--difference-runs",
                "--longest-difference-column-run", "--longest-difference-run",
                "--candidate-crop", "1,0,5,4", "--crop", "1,0,5,4", "--json")
        full = self._run_png_pair(candidate, reference, *base)
        filtered = self._run_png_pair(candidate, reference, *base,
                                      "--min-difference-column-run-length", "4")
        before, after = json.loads(full.stdout), json.loads(filtered.stdout)
        self.assertEqual(before["difference_column_runs"], [
            {"x": 0, "y": 0, "length": 3},
            {"x": 2, "y": 0, "length": 4},
        ])
        self.assertEqual(after["difference_column_runs"], [
            {"x": 2, "y": 0, "length": 4},
        ])
        self.assertEqual(after["metrics"], before["metrics"])
        self.assertEqual(after["difference_runs"], before["difference_runs"])
        self.assertEqual(after["longest_difference_column_run"],
                         before["longest_difference_column_run"])
        empty = json.loads(self._run_png_pair(
            candidate, reference, *base, "--min-difference-column-run-length", "5").stdout)
        self.assertEqual(empty["difference_column_runs"], [])
        self.assertIsNotNone(empty["longest_difference_column_run"])

    def test_cutoff_one_and_longest_share_unfiltered_intervals(self):
        candidate, reference = self._pair()
        args = ("--difference-column-runs", "--longest-difference-column-run", "--json")
        plain = json.loads(self._run_png_pair(candidate, reference, *args).stdout)
        cutoff = json.loads(self._run_png_pair(
            candidate, reference, *args, "--min-difference-column-run-length", "1").stdout)
        self.assertEqual(cutoff["difference_column_runs"], plain["difference_column_runs"])
        self.assertEqual(cutoff["longest_difference_column_run"],
                         plain["longest_difference_column_run"])
        with mock.patch.object(fidelity, "difference_column_runs", return_value=[
            {"x": 0, "y": 0, "length": 1}, {"x": 1, "y": 0, "length": 3},
        ]) as helper:
            result = self._run_png_pair(candidate, reference, *args,
                                      "--min-difference-column-run-length", "2")
        helper.assert_called_once()
        data = json.loads(result.stdout)
        self.assertEqual(data["difference_column_runs"], [{"x": 1, "y": 0, "length": 3}])
        self.assertEqual(data["longest_difference_column_run"], {"x": 1, "y": 0, "length": 3})

    def test_dependency_and_invalid_lengths_are_usage_errors_before_read(self):
        for value in ("0", "-1", "١", "1.5", "bad"):
            result = self._run("missing.png", "missing.png", "--difference-column-runs",
                               "--min-difference-column-run-length", value)
            self._assert_usage_error(result, "--min-difference-column-run-length")
        result = self._run("missing.png", "missing.png",
                           "--min-difference-column-run-length", "2")
        self._assert_usage_error(result, "requires --difference-column-runs")
        with mock.patch.object(fidelity, "_read_source", side_effect=AssertionError("read")):
            with self.assertRaises(SystemExit) as raised:
                fidelity.main(["missing.png", "missing.png",
                               "--min-difference-column-run-length", "2"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
