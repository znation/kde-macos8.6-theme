"""Output cap for horizontal fidelity mismatch runs."""

from __future__ import annotations

import json
import unittest

from support import repo_root  # noqa: F401
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import difference_pair  # noqa: E402


class TestDifferenceRunsLimit(FidelityCliTestCase):
    def _pair(self):
        return difference_pair(
            9, 2, ({0, 2, 3, 5, 6, 7}, {0, 1, 2, 3, 8}), vertical=False)

    def test_cap_follows_length_filters_and_keeps_full_summaries(self):
        candidate, reference = self._pair()
        base = ("--difference-runs", "--difference-run-count",
                "--longest-difference-run", "--json")
        full_runs = [
            {"x": 0, "y": 0, "length": 1}, {"x": 2, "y": 0, "length": 2},
            {"x": 5, "y": 0, "length": 3}, {"x": 0, "y": 1, "length": 4},
            {"x": 8, "y": 1, "length": 1},
        ]
        limited = json.loads(self._run_png_pair(candidate, reference, *base,
                         "--max-difference-runs", "2").stdout)
        self.assertEqual(limited["difference_runs"], full_runs[:2])
        self.assertEqual(limited["omitted_difference_runs"], 3)
        self.assertEqual(limited["difference_run_count"], 5)
        self.assertEqual(limited["longest_difference_run"], {"x": 0, "y": 1, "length": 4})

        minimum = json.loads(self._run_png_pair(candidate, reference, *base,
                         "--min-difference-run-length", "2",
                         "--max-difference-runs", "1").stdout)
        self.assertEqual(minimum["difference_runs"], [full_runs[1]])
        self.assertEqual(minimum["omitted_difference_runs"], 2)
        maximum = json.loads(self._run_png_pair(candidate, reference, *base,
                         "--max-difference-run-length", "2",
                         "--max-difference-runs", "2").stdout)
        self.assertEqual(maximum["difference_runs"], full_runs[:2])
        self.assertEqual(maximum["omitted_difference_runs"], 1)

        # An empty requested window uses a minimum above the fixture's
        # longest run (4), kept legal against the paired maximum: a
        # contradictory window is refused before any image read.
        conflict = json.loads(self._run_png_pair(candidate, reference, *base,
                          "--min-difference-run-length", "5",
                          "--max-difference-run-length", "9",
                          "--max-difference-runs", "1").stdout)
        self.assertEqual(conflict["difference_runs"], [])
        self.assertEqual(conflict["omitted_difference_runs"], 0)
        self.assertEqual(conflict["metrics"], limited["metrics"])
        self.assertEqual(conflict["passed"], limited["passed"])

        paged = json.loads(self._run_png_pair(
            candidate, reference, *base, "--min-difference-run-length", "2",
            "--max-difference-run-length", "3", "--difference-run-offset", "1",
            "--max-difference-runs", "1").stdout)
        self.assertEqual(paged["difference_runs"], [full_runs[2]])
        self.assertEqual(paged["omitted_difference_runs"], 1)
        self.assertEqual(paged["difference_run_count"], 5)
        self.assertEqual(paged["longest_difference_run"], full_runs[3])

    def test_json_text_crop_and_no_option_schema(self):
        candidate, reference = self._pair()
        expected = [
            {"x": 0, "y": 0, "length": 1}, {"x": 2, "y": 0, "length": 2},
        ]
        uncapped = json.loads(self._run_png_pair(
            candidate, reference, "--difference-runs", "--json").stdout)
        self.assertNotIn("omitted_difference_runs", uncapped)
        text = self._run_png_pair(candidate, reference, "--difference-runs",
                                  "--max-difference-runs", "2")
        self.assertIn("difference runs: " + json.dumps(expected), text.stdout)
        self.assertIn("omitted difference runs: 3", text.stdout)
        cropped = json.loads(self._run_png_pair(
            candidate, reference, "--difference-runs", "--json",
            "--candidate-crop", "1,0,8,2", "--crop", "1,0,8,2",
            "--max-difference-runs", "2").stdout)
        self.assertEqual(cropped["difference_runs"], [
            {"x": 1, "y": 0, "length": 2}, {"x": 4, "y": 0, "length": 3},
        ])
        self.assertEqual(cropped["omitted_difference_runs"], 2)
        complete = json.loads(self._run_png_pair(
            candidate, reference, "--difference-runs", "--json",
            "--max-difference-runs", "5").stdout)
        self.assertEqual(complete["difference_runs"], uncapped["difference_runs"])
        self.assertEqual(complete["omitted_difference_runs"], 0)
        identical = json.loads(self._run_png_pair(
            reference, reference, "--difference-runs", "--json",
            "--max-difference-runs", "1").stdout)
        self.assertEqual(identical["difference_runs"], [])
        self.assertEqual(identical["omitted_difference_runs"], 0)

    def test_invalid_and_dependent_caps_fail_before_reads(self):
        for value in ("0", "-1", "1.5", "١"):
            result = self._run("missing.png", "missing.png", "--difference-runs",
                               "--max-difference-runs", value)
            self._assert_usage_error(result, "--max-difference-runs")
            self.assertEqual(result.stdout, "")
        missing = self._run("missing.png", "missing.png", "--difference-runs",
                            "--max-difference-runs")
        self._assert_usage_error(missing, "expected one argument")
        self.assertEqual(missing.stdout, "")
        dependent = self._run("missing.png", "missing.png", "--max-difference-runs", "2")
        self._assert_usage_error(dependent, "--max-difference-runs requires --difference-runs")
        self.assertEqual(dependent.stdout, "")


if __name__ == "__main__":
    unittest.main()
