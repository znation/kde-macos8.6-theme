"""Tests for vertical contiguous color-search matches."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from tools import sample


class TestSampleMatchColumnRuns(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_column_runs_are_absolute_sorted_and_cover_tolerance_matches(self):
        rows = [
            [(10, 20, 30), (0, 0, 0), (10, 20, 30)],
            [(11, 20, 30), (10, 20, 30), (0, 0, 0)],
            [(0, 0, 0), (11, 20, 30), (10, 20, 30)],
            [(10, 20, 30), (0, 0, 0), (10, 20, 30)],
        ]
        _, encoded = rgb_image(5, 6, lambda x, y: rows[y - 1][x - 2]
                               if 2 <= x <= 4 and 1 <= y <= 4 else (99, 99, 99))
        path = self._write(self._tmp_dir(), "columns.png", encoded)
        args = (path, "2", "1", "--width", "3", "--height", "4", "--find-color", "0a141e",
                "--color-tolerance", "1", "--match-column-runs")
        result = self._run(*args, "--match-runs", "--match-pixels", "1", "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        expected = [
            {"x": 2, "y": 1, "length": 2}, {"x": 2, "y": 4, "length": 1},
            {"x": 3, "y": 2, "length": 2}, {"x": 4, "y": 1, "length": 1},
            {"x": 4, "y": 3, "length": 2},
        ]
        self.assertEqual(match["column_runs"], expected)
        self.assertEqual(sum(run["length"] for run in expected), match["count"])
        self.assertEqual(match["runs"], [
            {"x": 2, "y": 1, "length": 1}, {"x": 4, "y": 1, "length": 1},
            {"x": 2, "y": 2, "length": 2},
            {"x": 3, "y": 3, "length": 2},
            {"x": 2, "y": 4, "length": 1}, {"x": 4, "y": 4, "length": 1},
        ])
        self.assertEqual(len(match["pixels"]), 1)

    def test_empty_and_fully_matching_regions(self):
        _, encoded = rgb_image(2, 3, lambda x, y: (10, 20, 30) if x == 1 else (0, 0, 0))
        path = self._write(self._tmp_dir(), "coverage.png", encoded)
        empty = self._run(path, "0", "0", "--width", "2", "--height", "3",
                          "--find-color", "ffffff", "--match-column-runs", "--json")
        self.assertEqual(json.loads(empty.stdout)["match"]["column_runs"], [])
        full = self._run(path, "1", "1", "--find-color", "0a141e", "--match-column-runs", "--json")
        self.assertEqual(json.loads(full.stdout)["match"]["column_runs"],
                         [{"x": 1, "y": 1, "length": 1}])

    def test_option_requires_find_color_and_is_omitted_by_default(self):
        rejected = self._run("missing.png", "0", "0", "--match-column-runs")
        self._assert_usage_error(rejected)
        self.assertEqual(rejected.stdout, "")
        _, encoded = rgb_image(1, 1, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "plain.png", encoded)
        ordinary = self._run(path, "0", "0", "--find-color", "010203", "--json")
        self.assertNotIn("column_runs", json.loads(ordinary.stdout)["match"])


if __name__ == "__main__":
    import unittest

    unittest.main()
