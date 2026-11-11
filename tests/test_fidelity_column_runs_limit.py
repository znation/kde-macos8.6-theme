"""Output count cap for vertical fidelity mismatch runs."""

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


class TestColumnRunsLimit(FidelityCliTestCase):
    def _pair(self):
        return difference_pair(
            2, 9, ({0, 2, 3, 5, 6, 7}, {0, 1, 2, 3, 8}), vertical=True)

    def test_cap_follows_column_order_and_length_filters_without_changing_summaries(self):
        candidate, reference = self._pair()
        base = ("--difference-column-runs", "--difference-column-run-count",
                "--longest-difference-column-run", "--json")
        full = json.loads(self._run_png_pair(candidate, reference, *base).stdout)
        self.assertEqual(full["difference_column_run_count"], 5)
        for args, expected, omitted in (
            (("--max-difference-column-runs", "2"),
             [{"x": 0, "y": 0, "length": 1}, {"x": 0, "y": 2, "length": 2}], 3),
            (("--min-difference-column-run-length", "2", "--max-difference-column-runs", "1"),
             [{"x": 0, "y": 2, "length": 2}], 2),
            (("--max-difference-column-run-length", "2", "--max-difference-column-runs", "2"),
             [{"x": 0, "y": 0, "length": 1}, {"x": 0, "y": 2, "length": 2}], 1),
            (("--max-difference-column-runs", "4"),
             [{"x": 0, "y": 0, "length": 1}, {"x": 0, "y": 2, "length": 2},
              {"x": 0, "y": 5, "length": 3}, {"x": 1, "y": 0, "length": 4}], 1),
            (("--min-difference-column-run-length", "9", "--max-difference-column-runs", "2"), [], 0),
        ):
            actual = json.loads(self._run_png_pair(candidate, reference, *base, *args).stdout)
            self.assertEqual(actual["difference_column_runs"], expected)
            self.assertEqual(actual["omitted_difference_column_runs"], omitted)
            self.assertEqual(actual["difference_column_run_count"], full["difference_column_run_count"])
            self.assertEqual(actual["longest_difference_column_run"], full["longest_difference_column_run"])
            self.assertEqual(actual["metrics"], full["metrics"])

    def test_capped_cli_consumes_one_shot_vertical_stream_with_bounded_retention(self):
        candidate, reference = self._pair()
        class TrackedRun(dict):
            live = peak = 0
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                type(self).live += 1
                type(self).peak = max(type(self).peak, type(self).live)
            def __del__(self):
                type(self).live -= 1
        def stream(*args, **kwargs):
            for i in range(5000):
                yield TrackedRun(x=i, y=0, length=(i % 7) + 1)
        TrackedRun.live = TrackedRun.peak = 0
        with mock.patch.object(fidelity, "iter_difference_column_runs", side_effect=stream):
            result = self._run_png_pair(
                candidate, reference, "--difference-column-runs",
                "--difference-column-run-count", "--longest-difference-column-run",
                "--max-difference-column-runs", "2",
                "--difference-column-run-offset", "4990", "--json")
        report = json.loads(result.stdout)
        self.assertEqual(report["difference_column_runs"], [
            {"x": 4990, "y": 0, "length": 7},
            {"x": 4991, "y": 0, "length": 1},
        ])
        self.assertEqual(report["omitted_difference_column_runs"], 4998)
        self.assertEqual(report["difference_column_run_count"], 5000)
        self.assertEqual(report["longest_difference_column_run"],
                         {"x": 6, "y": 0, "length": 7})
        self.assertLessEqual(TrackedRun.peak, 5)

    def test_zero_omissions_text_empty_images_and_independent_horizontal_cap(self):
        candidate, reference = self._pair()
        uncapped = json.loads(self._run_png_pair(candidate, reference,
                            "--difference-column-runs", "--json").stdout)
        self.assertNotIn("omitted_difference_column_runs", uncapped)
        result = self._run_png_pair(candidate, reference, "--difference-column-runs",
                                    "--max-difference-column-runs", "8", "--json")
        self.assertIn('"omitted_difference_column_runs": 0', result.stdout)
        complete = json.loads(self._run_png_pair(
            candidate, reference, "--difference-column-runs", "--max-difference-column-runs",
            "5", "--json").stdout)
        self.assertEqual(complete["difference_column_runs"], uncapped["difference_column_runs"])
        self.assertEqual(complete["omitted_difference_column_runs"], 0)
        tolerated = json.loads(self._run_png_pair(
            candidate, reference, "--difference-column-runs", "--max-difference-column-runs",
            "2", "--tolerance", "20", "--json").stdout)
        self.assertEqual(tolerated["difference_column_runs"], [])
        self.assertEqual(tolerated["omitted_difference_column_runs"], 0)
        cropped = json.loads(self._run_png_pair(
            candidate, reference, "--difference-column-runs", "--max-difference-column-runs",
            "2", "--json", "--candidate-crop", "0,1,2,8", "--crop", "0,1,2,8").stdout)
        self.assertEqual(cropped["difference_column_runs"], [
            {"x": 0, "y": 1, "length": 2}, {"x": 0, "y": 4, "length": 3},
        ])
        self.assertEqual(cropped["omitted_difference_column_runs"], 2)
        text = self._run_png_pair(candidate, reference, "--difference-column-runs",
                                  "--max-difference-column-runs", "2")
        self.assertIn("omitted difference column runs: 3", text.stdout)
        empty = make_png(2, 9, [bytes(6) for _ in range(9)])
        same = json.loads(self._run_png_pair(empty, empty, "--difference-column-runs",
                                             "--max-difference-column-runs", "2", "--json").stdout)
        self.assertEqual(same["difference_column_runs"], [])
        self.assertEqual(same["omitted_difference_column_runs"], 0)
        combined = json.loads(self._run_png_pair(
            candidate, reference, "--difference-runs", "--max-difference-runs", "1",
            "--difference-column-runs", "--max-difference-column-runs", "1", "--json").stdout)
        self.assertEqual(combined["omitted_difference_runs"], 7)
        self.assertEqual(combined["omitted_difference_column_runs"], 4)

    def test_dependency_and_invalid_cap_fail_before_read(self):
        for value in ("0", "-1", "١", "1.5", "bad"):
            result = self._run("missing.png", "missing.png", "--difference-column-runs",
                               "--max-difference-column-runs", value)
            self._assert_usage_error(result, "--max-difference-column-runs")
            self.assertEqual(result.stdout, "")
        missing = self._run("missing.png", "missing.png", "--difference-column-runs",
                            "--max-difference-column-runs")
        self._assert_usage_error(missing, "expected one argument")
        self.assertEqual(missing.stdout, "")
        self._assert_usage_error(self._run("missing.png", "missing.png",
                                           "--max-difference-column-runs", "2"),
                                 "requires --difference-column-runs")
        with mock.patch.object(fidelity, "_read_source", side_effect=AssertionError("read")):
            result = self._run("missing.png", "missing.png", "--max-difference-column-runs", "2")
        self._assert_usage_error(result, "requires --difference-column-runs")


if __name__ == "__main__":
    unittest.main()
