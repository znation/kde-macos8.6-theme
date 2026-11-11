"""Minimum length filtering for horizontal fidelity mismatch runs."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import (  # noqa: E402
    FidelityCliTestCase,
    patched_horizontal_calls,
)
from support.png_fixtures import (  # noqa: E402
    difference_pair,
    make_png,
)
from tools import fidelity  # noqa: E402


class TestDifferenceRunsMinimumLength(FidelityCliTestCase):
    def _pair(self):
        return difference_pair(
            7, 2, ({0, 2, 3, 5}, {0, 1, 2}), vertical=False)

    def test_filters_after_run_segmentation_with_offset_crops(self):
        candidate, reference = self._pair()
        base = ("--difference-runs", "--difference-column-runs",
                "--candidate-crop", "1,0,6,2", "--crop", "0,0,6,2", "--json")
        full = self._run_png_pair(candidate, reference, *base)
        filtered = self._run_png_pair(candidate, reference, *base,
                                      "--min-difference-run-length", "2")
        self.assertEqual(full.returncode, 1)
        self.assertEqual(filtered.returncode, full.returncode)
        original = json.loads(full.stdout)
        data = json.loads(filtered.stdout)
        self.assertEqual(original["difference_runs"], [
            {"x": 1, "y": 0, "length": 2},
            {"x": 4, "y": 0, "length": 1},
            {"x": 0, "y": 1, "length": 2},
        ])
        self.assertEqual(data["difference_runs"], [
            {"x": 1, "y": 0, "length": 2},
            {"x": 0, "y": 1, "length": 2},
        ])
        for key in ("metrics", "difference_column_runs", "candidate_difference_bounds",
                    "reference_difference_bounds"):
            self.assertEqual(data[key], original[key])
        self.assertEqual(data["candidate_difference_bounds"], [1, 0, 5, 2])
        passing_full = json.loads(self._run_png_pair(
            candidate, reference, *base, "--max-mae", "10").stdout)
        passing_filtered = json.loads(self._run_png_pair(
            candidate, reference, *base, "--max-mae", "10",
            "--min-difference-run-length", "2").stdout)
        self.assertEqual(passing_filtered["passed"], passing_full["passed"])
        self.assertEqual(passing_filtered["metrics"], passing_full["metrics"])

    def test_cutoff_one_and_empty_results_and_longest_summary(self):
        candidate, reference = self._pair()
        args = ("--difference-runs", "--longest-difference-run", "--json")
        plain = json.loads(self._run_png_pair(candidate, reference, *args).stdout)
        cutoff = json.loads(self._run_png_pair(candidate, reference, *args,
                                               "--min-difference-run-length", "1").stdout)
        self.assertEqual(cutoff["difference_runs"], plain["difference_runs"])
        self.assertEqual(cutoff["longest_difference_run"], plain["longest_difference_run"])
        empty = json.loads(self._run_png_pair(candidate, reference, *args,
                                              "--min-difference-run-length", "8").stdout)
        self.assertEqual(empty["difference_runs"], [])
        self.assertIsNotNone(empty["longest_difference_run"])
        same = make_png(2, 1, [bytes(6)])
        no_runs = json.loads(self._run_png_pair(same, same, "--difference-runs", "--json",
                                               "--min-difference-run-length", "1").stdout)
        self.assertEqual(no_runs["difference_runs"], [])

    def test_longest_summary_uses_unfiltered_run_list(self):
        candidate, reference = self._pair()
        with patched_horizontal_calls(runs=mock.Mock(return_value=[
            {"x": 0, "y": 0, "length": 1}, {"x": 2, "y": 0, "length": 3},
        ])) as patched:
            result = self._run_png_pair(candidate, reference, "--difference-runs",
                                        "--longest-difference-run", "--json",
                                        "--min-difference-run-length", "2")
        patched.runs.assert_called_once()
        data = json.loads(result.stdout)
        self.assertEqual(data["difference_runs"], [{"x": 2, "y": 0, "length": 3}])
        self.assertEqual(data["longest_difference_run"], {"x": 2, "y": 0, "length": 3})
        tmp = self._tmp_dir()
        a = self._write(tmp, "a.png", candidate)
        b = self._write(tmp, "b.png", reference)
        direct = self._run_script(a, b, "--difference-runs", "--json",
                                  "--min-difference-run-length", "2")
        self.assertEqual(json.loads(direct.stdout)["difference_runs"], [
            {"x": 2, "y": 0, "length": 2}, {"x": 0, "y": 1, "length": 3},
        ])

    def test_invalid_and_dependent_options_fail_before_read(self):
        for value in ("0", "-1", "١", "1.5", "oops"):
            result = self._run("missing.png", "missing.png", "--difference-runs",
                               "--min-difference-run-length", value)
            self._assert_usage_error(result, "--min-difference-run-length")
        result = self._run("missing.png", "missing.png", "--min-difference-run-length", "2")
        self._assert_usage_error(result, "requires --difference-runs")
        missing = self._run("missing.png", "missing.png", "--difference-runs",
                            "--min-difference-run-length")
        self._assert_usage_error(missing, "expected one argument")
        with mock.patch.object(fidelity, "_read_source", side_effect=AssertionError("read")):
            with self.assertRaises(SystemExit) as raised:
                fidelity.main(["missing.png", "missing.png", "--min-difference-run-length", "2"])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
