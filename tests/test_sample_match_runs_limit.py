"""Tests for limiting horizontal color-search match intervals."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from tools import sample


class TestSampleMatchRunsLimit(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_cap_follows_length_filters_and_keeps_full_summaries(self):
        target = (1, 2, 3)
        matches = ({0, 2, 3, 5, 6, 7}, {0, 1, 2, 3, 8})
        _, encoded = rgb_image(13, 4, lambda x, y: target
                               if 1 <= y <= 2 and x - 2 in matches[y - 1]
                               else (0, 0, 0))
        path = self._write(self._tmp_dir(), "segments.png", encoded)
        base = (path, "2", "1", "--width", "9", "--height", "2",
                "--find-color", "010203", "--match-runs", "--match-run-count",
                "--longest-match-run", "--match-fraction", "--match-centroid",
                "--match-pixels", "3", "--match-column-runs", "--json")
        results = [self._run(*base, "--max-match-runs", n) for n in ("2", "4", "5")]
        full_result = self._run(*base)
        minimum = self._run(*base, "--min-match-run-length", "2", "--max-match-runs", "1")
        maximum = self._run(*base, "--max-match-run-length", "2", "--max-match-runs", "2")
        contradictory = self._run(*base, "--min-match-run-length", "3",
                                  "--max-match-run-length", "2", "--max-match-runs", "2")
        for result in (*results, full_result, minimum, maximum, contradictory):
            self._assert_success(result)
        reports = [json.loads(result.stdout)["match"] for result in results]
        expected = [
            {"x": 2, "y": 1, "length": 1},
            {"x": 4, "y": 1, "length": 2},
            {"x": 7, "y": 1, "length": 3},
            {"x": 2, "y": 2, "length": 4},
            {"x": 10, "y": 2, "length": 1},
        ]
        self.assertEqual(reports[0]["runs"], expected[:2])
        self.assertEqual(reports[0]["omitted_runs"], 3)
        self.assertEqual(reports[1]["runs"], expected[:4])
        self.assertEqual(reports[1]["omitted_runs"], 1)
        self.assertEqual(reports[2]["runs"], expected)
        self.assertEqual(reports[2]["omitted_runs"], 0)
        full = json.loads(full_result.stdout)["match"]
        self.assertEqual(full["runs"], expected)
        self.assertNotIn("omitted_runs", full)
        self.assertEqual(full["run_count"], 5)
        self.assertEqual(full["longest_run"], {"x": 2, "y": 2, "length": 4})
        for key in ("count", "bounds", "fraction", "centroid", "pixels", "omitted_pixels",
                    "column_runs", "run_count", "longest_run"):
            self.assertEqual(reports[0][key], full[key], key)
        min_match = json.loads(minimum.stdout)["match"]
        self.assertEqual(min_match["runs"], [{"x": 4, "y": 1, "length": 2}])
        self.assertEqual(min_match["omitted_runs"], 2)
        max_match = json.loads(maximum.stdout)["match"]
        self.assertEqual(max_match["runs"], expected[:2])
        self.assertEqual(max_match["omitted_runs"], 1)
        contradiction_match = json.loads(contradictory.stdout)["match"]
        self.assertEqual(contradiction_match["runs"], [])
        self.assertEqual(contradiction_match["omitted_runs"], 0)

    def test_empty_text_direct_script_and_validation(self):
        _, encoded = rgb_image(2, 1, lambda x, y: (0, 0, 0))
        path = self._write(self._tmp_dir(), "empty.png", encoded)
        args = (path, "0", "0", "--find-color", "010203", "--match-runs")
        empty = self._run(*args, "--max-match-runs", "2", "--json")
        text = self._run(*args, "--max-match-runs", "2")
        direct = self._run_script(*args, "--max-match-runs", "2", "--json")
        for result in (empty, text, direct):
            self._assert_success(result)
        self.assertEqual(json.loads(empty.stdout)["match"]["runs"], [])
        self.assertEqual(json.loads(empty.stdout)["match"]["omitted_runs"], 0)
        self.assertEqual(json.loads(direct.stdout)["match"], json.loads(empty.stdout)["match"])
        self.assertIn("matching runs: []\nomitted matching runs: 0", text.stdout)
        self.assertNotIn("omitted matching runs:", self._run(*args).stdout)
        for value in ("0", "-1", "1.5", "nope", "１"):
            result = self._run("missing.png", "0", "0", "--find-color", "010203",
                               "--match-runs", "--max-match-runs", value)
            self.assertEqual((result.returncode, result.stdout), (2, ""))
        missing = self._run("missing.png", "0", "0", "--find-color", "010203",
                            "--match-runs", "--max-match-runs")
        self.assertEqual((missing.returncode, missing.stdout), (2, ""))
        dependency = self._run("missing.png", "0", "0", "--find-color", "010203",
                               "--max-match-runs", "1")
        self.assertEqual(dependency.returncode, 2)
        self.assertEqual(dependency.stdout, "")
        self.assertIn("--max-match-runs requires --match-runs", dependency.stderr)
        help_result = self._run("--help")
        self.assertIn("--max-match-runs N", help_result.stdout)


if __name__ == "__main__":
    import unittest
    unittest.main()
