"""Tests for vertical contiguous color-search matches."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
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
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(*args, "--match-runs", "--match-pixels", "1",
                               "--match-fraction", "--json")
        self._assert_success(result)
        read.assert_called_once()
        self.assertEqual(read.call_args.kwargs["max_rows"], 5)
        match = json.loads(result.stdout)["match"]
        expected = [
            {"x": 2, "y": 1, "length": 2}, {"x": 2, "y": 4, "length": 1},
            {"x": 3, "y": 2, "length": 2}, {"x": 4, "y": 1, "length": 1},
            {"x": 4, "y": 3, "length": 2},
        ]
        self.assertEqual(match["column_runs"], expected)
        self.assertEqual(sum(run["length"] for run in expected), match["count"])
        self.assertEqual((match["count"], match["fraction"]), (8, 2 / 3))
        self.assertEqual(match["runs"], [
            {"x": 2, "y": 1, "length": 1}, {"x": 4, "y": 1, "length": 1},
            {"x": 2, "y": 2, "length": 2},
            {"x": 3, "y": 3, "length": 2},
            {"x": 2, "y": 4, "length": 1}, {"x": 4, "y": 4, "length": 1},
        ])
        self.assertEqual(len(match["pixels"]), 1)
        text = self._run(*args, "--match-runs")
        self._assert_success(text)
        self.assertIn('matching column runs: [{"x":2,"y":1,"length":2},{"x":2,"y":4,"length":1},'
                      '{"x":3,"y":2,"length":2},{"x":4,"y":1,"length":1},{"x":4,"y":3,"length":2}]',
                      text.stdout)
        self.assertLess(text.stdout.index("matching runs: "),
                        text.stdout.index("matching column runs: "))

    def test_empty_and_fully_matching_regions(self):
        _, encoded = rgb_image(2, 3, lambda x, y: (10, 20, 30) if x == 1 else (0, 0, 0))
        path = self._write(self._tmp_dir(), "coverage.png", encoded)
        empty = self._run(path, "0", "0", "--width", "2", "--height", "3",
                          "--find-color", "ffffff", "--match-column-runs", "--json")
        self.assertEqual(json.loads(empty.stdout)["match"]["column_runs"], [])
        full = self._run(path, "1", "1", "--find-color", "0a141e", "--match-column-runs", "--json")
        self.assertEqual(json.loads(full.stdout)["match"]["column_runs"],
                         [{"x": 1, "y": 1, "length": 1}])

    def test_alpha_filter_single_axes_and_opaque_fallback(self):
        rows = [
            bytes((1, 2, 3, 0, 1, 2, 3, 0)),
            bytes((1, 2, 3, 255, 1, 2, 3, 0)),
            bytes((1, 2, 3, 0, 1, 2, 3, 0)),
        ]
        path = self._write(self._tmp_dir(), "rgba.png", make_png(2, 3, rows, color_type=6))
        filtered = self._run(path, "0", "0", "--width", "2", "--height", "3",
                             "--find-color", "010203", "--match-alpha", "255",
                             "--match-column-runs", "--json")
        self._assert_success(filtered)
        # Only the one transparent-border-column pixel with alpha 255 matches;
        # stored RGB beneath zero alpha is rejected even though RGB matches.
        self.assertEqual(json.loads(filtered.stdout)["match"]["column_runs"],
                         [{"x": 0, "y": 1, "length": 1}])
        _, encoded = rgb_image(2, 2, lambda _x, _y: (1, 2, 3))
        opaque = self._write(self._tmp_dir(), "opaque.png", encoded)
        fallback = self._run(opaque, "0", "0", "--width", "2", "--height", "2",
                             "--find-color", "010203", "--match-alpha", "255",
                             "--match-column-runs", "--json")
        self._assert_success(fallback)
        self.assertEqual(json.loads(fallback.stdout)["match"]["column_runs"],
                         [{"x": 0, "y": 0, "length": 2}, {"x": 1, "y": 0, "length": 2}])
        row = self._run(opaque, "0", "0", "--width", "2", "--find-color", "010203",
                        "--match-column-runs", "--json")
        self._assert_success(row)
        self.assertEqual(json.loads(row.stdout)["match"]["column_runs"],
                         [{"x": 0, "y": 0, "length": 1}, {"x": 1, "y": 0, "length": 1}])
        column = self._run(opaque, "0", "0", "--height", "2", "--find-color", "010203",
                           "--match-column-runs", "--json")
        self._assert_success(column)
        self.assertEqual(json.loads(column.stdout)["match"]["column_runs"],
                         [{"x": 0, "y": 0, "length": 2}])

    def test_option_requires_find_color_and_is_omitted_by_default(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            rejected = self._run("missing.png", "0", "0", "--match-column-runs")
        self._assert_usage_error(rejected, "requires --find-color")
        self.assertEqual(rejected.stdout, "")
        _, encoded = rgb_image(1, 1, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "plain.png", encoded)
        ordinary = self._run(path, "0", "0", "--find-color", "010203", "--json")
        self.assertNotIn("column_runs", json.loads(ordinary.stdout)["match"])
        direct = self._run_script(path, "0", "0", "--find-color", "010203",
                                  "--match-column-runs", "--json")
        self._assert_success(direct)
        self.assertEqual(json.loads(direct.stdout)["match"]["column_runs"],
                         [{"x": 0, "y": 0, "length": 1}])
        help_text = self._run_script("--help")
        self.assertEqual(help_text.returncode, 0, help_text.stderr)
        self.assertIn("--match-column-runs", help_text.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
