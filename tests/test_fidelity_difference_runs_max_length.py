"""Maximum length filtering for horizontal fidelity mismatch runs."""

from __future__ import annotations

import json
import unittest

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import (  # noqa: E402
    difference_pair,
    make_png,
)


class TestDifferenceRunsMaximumLength(FidelityCliTestCase):
    def _pair(self):
        return difference_pair(
            9, 2, ({0, 2, 3, 5, 6, 7}, {0, 1, 2, 3, 8}), vertical=False)

    def test_inclusive_filter_and_minimum_combine_after_segmentation(self):
        candidate, reference = self._pair()
        args = ("--difference-runs", "--longest-difference-run", "--json")
        expected = [
            {"x": 0, "y": 0, "length": 1},
            {"x": 2, "y": 0, "length": 2},
            {"x": 8, "y": 1, "length": 1},
        ]
        limited = json.loads(self._run_png_pair(
            candidate, reference, *args, "--max-difference-run-length", "2").stdout)
        self.assertEqual(limited["difference_runs"], expected)
        singletons = json.loads(self._run_png_pair(
            candidate, reference, *args, "--max-difference-run-length", "1").stdout)
        self.assertEqual(singletons["difference_runs"], [expected[0], expected[2]])
        combined = json.loads(self._run_png_pair(
            candidate, reference, *args, "--min-difference-run-length", "2",
            "--max-difference-run-length", "2").stdout)
        self.assertEqual(combined["difference_runs"], [expected[1]])
        empty = json.loads(self._run_png_pair(
            candidate, reference, *args, "--min-difference-run-length", "3",
            "--max-difference-run-length", "2").stdout)
        self.assertEqual(empty["difference_runs"], [])
        self.assertEqual(empty["longest_difference_run"], {"x": 0, "y": 1, "length": 4})
        self.assertEqual(empty["metrics"], limited["metrics"])
        self.assertEqual(empty["passed"], limited["passed"])
        boundary = json.loads(self._run_png_pair(
            candidate, reference, *args, "--tolerance", "20",
            "--max-difference-run-length", "2").stdout)
        self.assertEqual(boundary["difference_runs"], [])
        same = make_png(2, 1, [bytes(6)])
        identical = json.loads(self._run_png_pair(
            same, same, *args, "--max-difference-run-length", "1").stdout)
        self.assertEqual(identical["difference_runs"], [])

    def test_unfiltered_equivalence_text_and_direct_script(self):
        candidate, reference = self._pair()
        base = ("--difference-runs", "--json")
        plain = json.loads(self._run_png_pair(candidate, reference, *base).stdout)
        maximum = json.loads(self._run_png_pair(
            candidate, reference, *base, "--max-difference-run-length", "9").stdout)
        self.assertEqual(maximum["difference_runs"], plain["difference_runs"])
        self.assertEqual(maximum["metrics"], plain["metrics"])
        tmp = self._tmp_dir()
        a = self._write(tmp, "candidate.png", candidate)
        b = self._write(tmp, "reference.png", reference)
        direct = self._run_script(a, b, *base, "--max-difference-run-length", "2")
        expected = [
            {"x": 0, "y": 0, "length": 1},
            {"x": 2, "y": 0, "length": 2},
            {"x": 8, "y": 1, "length": 1},
        ]
        self.assertEqual(json.loads(direct.stdout)["difference_runs"], expected)
        text_result = self._run_png_pair(candidate, reference, "--difference-runs",
                                         "--max-difference-run-length", "2")
        self.assertIn('difference runs: ' + json.dumps(expected), text_result.stdout)

    def test_invalid_and_dependent_values_fail_before_reads(self):
        for value in ("0", "-1", "1.5", "1e2", " 2", "2_0", "٢", "bad"):
            result = self._run(
                "missing.png", "missing.png", "--difference-runs",
                "--max-difference-run-length", value)
            self._assert_usage_error(result, "--max-difference-run-length")
            self.assertEqual(result.stdout, "")
        missing = self._run(
            "missing.png", "missing.png", "--difference-runs",
            "--max-difference-run-length")
        self._assert_usage_error(missing, "expected one argument")
        self.assertEqual(missing.stdout, "")
        dependent = self._run(
            "missing.png", "missing.png", "--max-difference-run-length", "2")
        self._assert_usage_error(dependent, "--max-difference-run-length requires --difference-runs")
        self.assertEqual(dependent.stdout, "")


if __name__ == "__main__":
    unittest.main()
