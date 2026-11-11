"""Tests dense per-column color-search match counts."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample, sample_report_search


class TestSampleMatchColumns(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_offset_region_columns_and_combined_diagnostics(self):
        target = (10, 20, 30)
        rows = [
            [target, (11, 20, 30), (0, 0, 0), target],
            [(0, 0, 0)] * 4,
            [target, (0, 0, 0), target, (0, 0, 0)],
        ]
        _, encoded = rgb_image(6, 5, lambda x, y: rows[y - 1][x - 1]
                               if 1 <= x <= 4 and 1 <= y <= 3 else (99, 99, 99))
        path = self._write(self._tmp_dir(), "columns.png", encoded)
        args = (path, "1", "1", "--width", "4", "--height", "3", "--find-color",
                "0a141e", "--color-tolerance", "1", "--match-columns")
        with mock.patch.object(sample_report_search, "positioned_region_pixels",
                               wraps=sample_report_search.positioned_region_pixels) as pixels, \
                mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(*args, "--match-pixels", "1", "--match-rows", "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        self.assertEqual(match["columns"], [2, 1, 1, 1])
        self.assertEqual(sum(match["columns"]), match["count"])
        self.assertEqual(match["rows"], [3, 0, 2])
        self.assertEqual(match["pixels"], [{"x": 1, "y": 1}])
        pixels.assert_called_once()
        self.assertEqual(read.call_args.kwargs["max_rows"], 4)
        text = self._run(*args)
        self._assert_success(text)
        self.assertIn("matching columns: [2,1,1,1]", text.stdout)
        ordinary = self._run(path, "1", "1", "--width", "4", "--height", "3",
                             "--find-color", "0a141e", "--json")
        self.assertNotIn("columns", json.loads(ordinary.stdout)["match"])
        ordinary_text = self._run(path, "1", "1", "--width", "4", "--height", "3",
                                  "--find-color", "0a141e")
        self.assertNotIn("matching columns:", ordinary_text.stdout)

    def test_empty_full_single_row_column_pixel_and_alpha(self):
        _, encoded = rgb_image(3, 2, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "coverage.png", encoded)
        full = self._run(path, "0", "0", "--width", "3", "--height", "2",
                         "--find-color", "010203", "--match-columns", "--json")
        self.assertEqual(json.loads(full.stdout)["match"]["columns"], [2, 2, 2])
        empty = self._run(path, "0", "0", "--width", "3", "--height", "2",
                          "--find-color", "ffffff", "--match-columns", "--json")
        self.assertEqual(json.loads(empty.stdout)["match"]["columns"], [0, 0, 0])
        row = self._run(path, "0", "1", "--width", "3", "--find-color", "010203",
                        "--match-columns", "--json")
        self.assertEqual(json.loads(row.stdout)["match"]["columns"], [1, 1, 1])
        column = self._run(path, "2", "0", "--height", "2", "--find-color", "010203",
                           "--match-columns", "--json")
        self.assertEqual(json.loads(column.stdout)["match"]["columns"], [2])
        one = self._run(path, "2", "1", "--find-color", "010203", "--match-columns", "--json")
        self.assertEqual(json.loads(one.stdout)["match"]["columns"], [1])

        transparent = self._write(self._tmp_dir(), "alpha.png", make_png(4, 2, [
            bytes((10, 20, 30, 0, 11, 20, 30, 255, 10, 20, 30, 255, 0, 0, 0, 255)),
            bytes((10, 20, 30, 255, 0, 0, 0, 255, 10, 20, 30, 0, 0, 0, 0, 255)),
        ], color_type=6))
        filtered = self._run(transparent, "0", "0", "--width", "4", "--height", "2",
                             "--find-color", "0a141e", "--color-tolerance", "1",
                             "--match-alpha", "0", "--match-columns", "--json")
        self.assertEqual(json.loads(filtered.stdout)["match"]["columns"], [1, 0, 1, 0])
        opaque = self._run(path, "0", "0", "--width", "3", "--height", "2",
                           "--find-color", "010203", "--match-alpha", "255",
                           "--match-columns", "--json")
        self.assertEqual(json.loads(opaque.stdout)["match"]["columns"], [2, 2, 2])

    def test_requires_find_color_before_reads_help_and_direct_script(self):
        _, encoded = rgb_image(1, 1, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "one.png", encoded)
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            invalid = self._run(path, "0", "0", "--match-columns")
        self._assert_usage_error(invalid, "requires --find-color")
        self.assertEqual(invalid.stdout, "")
        help_result = self._run("--help")
        self.assertIn("--match-columns", help_result.stdout)
        direct = self._run_script(path, "0", "0", "--find-color", "010203",
                                  "--match-columns", "--json")
        self._assert_success(direct)
        self.assertEqual(json.loads(direct.stdout)["match"]["columns"], [1])


if __name__ == "__main__":
    import unittest

    unittest.main()
