"""Tests for maximum lengths on vertical color-search match segments."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from tools import sample
from tools.sample_arguments import build_parser


class TestSampleMatchColumnRunsMaxLength(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_maximum_filters_only_vertical_list_and_combines_with_minimum(self):
        target = (10, 20, 30)
        positions = {(0, 0), (0, 2), (0, 3), (0, 5), (0, 6), (0, 7), (1, 8)}
        _, encoded = rgb_image(6, 12, lambda x, y: target if (x - 2, y - 1) in positions else (0, 0, 0))
        path = self._write(self._tmp_dir(), "columns.png", encoded)
        base = (path, "2", "1", "--width", "2", "--height", "9", "--find-color",
                "0a141e", "--match-column-runs", "--longest-match-column-run",
                "--match-pixels", "1", "--match-columns", "--match-runs",
                "--longest-match-run", "--match-rows")
        full = self._run(*base, "--json")
        self._assert_success(full)
        result = self._run(*base, "--max-match-column-run-length", "2", "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        self.assertEqual(match["column_runs"], [
            {"x": 2, "y": 1, "length": 1}, {"x": 2, "y": 3, "length": 2},
            {"x": 3, "y": 9, "length": 1},
        ])
        self.assertEqual(match["longest_column_run"], {"x": 2, "y": 6, "length": 3})
        self.assertEqual(match["count"], 7)
        self.assertEqual(match["pixels"], [{"x": 2, "y": 1}])
        self.assertEqual(match["columns"], [6, 1])
        for key in ("runs", "longest_run", "rows"):
            self.assertEqual(match[key], json.loads(full.stdout)["match"][key], key)
        generous = self._run(*base, "--max-match-column-run-length", "9", "--json")
        self._assert_success(generous)
        self.assertEqual(json.loads(generous.stdout)["match"],
                         json.loads(full.stdout)["match"])

        combined = self._run(*base, "--min-match-column-run-length", "2",
                             "--max-match-column-run-length", "2", "--json")
        self._assert_success(combined)
        self.assertEqual(json.loads(combined.stdout)["match"]["column_runs"],
                         [{"x": 2, "y": 3, "length": 2}])
        beyond = self._run(*base, "--min-match-column-run-length", "4",
                           "--max-match-column-run-length", "9", "--json")
        self._assert_success(beyond)
        self.assertEqual(json.loads(beyond.stdout)["match"]["column_runs"], [])
        text = self._run(*base, "--max-match-column-run-length", "2")
        self._assert_success(text)
        self.assertIn("matching column runs: [{\"x\":2,\"y\":1,\"length\":1}", text.stdout)

    def test_no_matches_default_script_parity_and_validation(self):
        _, encoded = rgb_image(3, 4, lambda x, y: (0, 0, 0))
        path = self._write(self._tmp_dir(), "empty.png", encoded)
        base = (path, "0", "0", "--width", "3", "--height", "4", "--find-color",
                "010203", "--match-column-runs")
        empty = self._run(*base, "--max-match-column-run-length", "2", "--json")
        self._assert_success(empty)
        self.assertEqual(json.loads(empty.stdout)["match"]["column_runs"], [])
        self.assertIsNone(build_parser().parse_args(
            ("image.png", "0", "0", "--find-color", "010203")
        ).max_match_column_run_length)
        direct = self._run_script(*base, "--max-match-column-run-length", "2", "--json")
        self._assert_success(direct)
        self.assertEqual(direct.stdout, empty.stdout)
        for value in ("0", "-1", "1.5", "１", "bad"):
            result = self._run("missing.png", "0", "0", "--find-color", "010203",
                               "--match-column-runs", "--max-match-column-run-length", value)
            self.assertEqual((result.returncode, result.stdout), (2, ""))
        missing = self._run("missing.png", "0", "0", "--find-color", "010203",
                            "--match-column-runs", "--max-match-column-run-length")
        self.assertEqual((missing.returncode, missing.stdout), (2, ""))
        help_result = self._run("--help")
        self.assertIn("--max-match-column-run-length N", help_result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
