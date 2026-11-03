"""Tests for filtering short vertical color-search match segments."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from tools import sample
from tools.sample_arguments import build_parser


class TestSampleMatchColumnRunsMinLength(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_cutoff_filters_vertical_list_and_preserves_full_region_diagnostics(self):
        target = (10, 20, 30)
        rows = [
            [target, (0, 0, 0), target, target],
            [(11, 20, 30), target, (0, 0, 0), target],
            [(0, 0, 0), (0, 0, 0), target, target],
            [target, (0, 0, 0), (0, 0, 0), (0, 0, 0)],
            [target, target, (0, 0, 0), target],
        ]
        _, encoded = rgb_image(6, 7, lambda x, y: rows[y - 1][x - 2]
                               if 2 <= x <= 5 and 1 <= y <= 5 else (90, 90, 90))
        path = self._write(self._tmp_dir(), "columns.png", encoded)
        base = (path, "2", "1", "--width", "4", "--height", "5", "--find-color",
                "0a141e", "--color-tolerance", "1", "--match-runs", "--match-column-runs",
                "--longest-match-run", "--longest-match-column-run", "--match-pixels", "1",
                "--match-fraction", "--match-rows", "--match-columns")
        full_result = self._run(*base, "--json")
        filtered_result = self._run(*base, "--min-match-run-length", "2",
                                    "--min-match-column-run-length", "3", "--json")
        self._assert_success(full_result)
        self._assert_success(filtered_result)
        full = json.loads(full_result.stdout)["match"]
        result = json.loads(filtered_result.stdout)["match"]
        self.assertEqual(result["column_runs"], [{"x": 5, "y": 1, "length": 3}])
        self.assertEqual(result["runs"], [run for run in full["runs"] if run["length"] >= 2])
        for key in ("count", "bounds", "pixels", "longest_run", "longest_column_run",
                    "fraction", "rows", "columns"):
            self.assertEqual(result[key], full[key], key)
        self.assertEqual(result["longest_column_run"], {"x": 5, "y": 1, "length": 3})

        empty = self._run(*base, "--min-match-column-run-length", "6", "--json")
        self._assert_success(empty)
        empty_match = json.loads(empty.stdout)["match"]
        self.assertEqual(empty_match["column_runs"], [])
        self.assertEqual(empty_match["longest_column_run"], full["longest_column_run"])
        text = self._run(*base, "--min-match-column-run-length", "6")
        self._assert_success(text)
        self.assertIn("matching column runs: []", text.stdout)

    def test_cutoff_one_no_matches_parser_default_and_script_parity(self):
        _, encoded = rgb_image(3, 4, lambda x, y: (1, 2, 3) if x == 1 else (0, 0, 0))
        path = self._write(self._tmp_dir(), "matches.png", encoded)
        base = (path, "0", "0", "--width", "3", "--height", "4", "--find-color",
                "010203", "--match-column-runs")
        ordinary = self._run(*base, "--json")
        cutoff = self._run(*base, "--min-match-column-run-length", "1", "--json")
        self._assert_success(ordinary)
        self._assert_success(cutoff)
        expected = json.loads(ordinary.stdout)["match"]["column_runs"]
        self.assertEqual(json.loads(cutoff.stdout)["match"]["column_runs"], expected)
        self.assertEqual(expected, [{"x": 1, "y": 0, "length": 4}])
        none = self._run(path, "0", "0", "--width", "3", "--height", "4", "--find-color",
                         "ffffff", "--match-column-runs", "--min-match-column-run-length", "2", "--json")
        self._assert_success(none)
        self.assertEqual(json.loads(none.stdout)["match"]["column_runs"], [])
        direct = self._run_script(*base, "--min-match-column-run-length", "2", "--json")
        self._assert_success(direct)
        self.assertEqual(json.loads(direct.stdout)["match"]["column_runs"], expected)
        self.assertIsNone(build_parser().parse_args(
            ("image.png", "0", "0", "--find-color", "010203")
        ).min_match_column_run_length)

    def test_invalid_values_and_help(self):
        for value in ("0", "-1", "1.5", "１", "nope"):
            with self.subTest(value=value):
                result = self._run("missing.png", "0", "0", "--find-color", "010203",
                                   "--match-column-runs", "--min-match-column-run-length", value)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
        missing = self._run("missing.png", "0", "0", "--find-color", "010203",
                            "--match-column-runs", "--min-match-column-run-length")
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(missing.stdout, "")
        help_result = self._run("--help")
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("--min-match-column-run-length N", help_result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
