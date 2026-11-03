"""Tests per-column enclosing spans in reference color searches."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample, sample_report_search


class TestSampleMatchColumnBounds(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_offset_disconnected_spans_and_combined_diagnostics(self):
        target = (10, 20, 30)
        columns = [[target, (0, 0, 0), (11, 20, 30), target],
                   [(0, 0, 0)] * 4,
                   [(0, 0, 0), target, (0, 0, 0), (0, 0, 0)]]
        _, encoded = rgb_image(5, 6, lambda x, y: columns[x - 1][y - 1]
                               if 1 <= x <= 3 and 1 <= y <= 4 else (99, 99, 99))
        path = self._write(self._tmp_dir(), "spans.png", encoded)
        args = (path, "1", "1", "--width", "3", "--height", "4",
                "--find-color", "0a141e", "--color-tolerance", "1",
                "--match-column-bounds")
        with mock.patch.object(sample_report_search, "_positioned_region_pixels",
                               wraps=sample_report_search._positioned_region_pixels) as pixels, \
                mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(*args, "--match-pixels", "1", "--match-rows",
                               "--match-columns", "--match-runs", "--match-column-runs",
                               "--match-row-bounds", "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        self.assertEqual(match["column_bounds"], [
            {"y": 1, "height": 4}, None, {"y": 2, "height": 1}])
        self.assertEqual(match["pixels"], [{"x": 1, "y": 1}])
        pixels.assert_called_once()
        self.assertEqual(read.call_args.kwargs["max_rows"], 5)
        text = self._run(*args)
        self._assert_success(text)
        self.assertIn('matching column bounds: [{"y":1,"height":4},null,{"y":2,"height":1}]', text.stdout)

    def test_full_empty_narrow_crops_alpha_and_default_omission(self):
        _, encoded = rgb_image(3, 2, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "coverage.png", encoded)
        full = self._run(path, "0", "0", "--width", "3", "--height", "2",
                         "--find-color", "010203", "--match-column-bounds", "--json")
        self.assertEqual(json.loads(full.stdout)["match"]["column_bounds"],
                         [{"y": 0, "height": 2}] * 3)
        empty = self._run(path, "0", "0", "--width", "3", "--height", "2",
                          "--find-color", "ffffff", "--match-column-bounds", "--json")
        self.assertEqual(json.loads(empty.stdout)["match"]["column_bounds"], [None] * 3)
        single = self._run(path, "2", "1", "--find-color", "010203",
                           "--match-column-bounds", "--json")
        self.assertEqual(json.loads(single.stdout)["match"]["column_bounds"],
                         [{"y": 1, "height": 1}])
        one_row = self._run(path, "0", "1", "--width", "3", "--find-color", "010203",
                            "--match-column-bounds", "--json")
        self.assertEqual(json.loads(one_row.stdout)["match"]["column_bounds"],
                         [{"y": 1, "height": 1}] * 3)
        one_column = self._run(path, "2", "0", "--height", "2", "--find-color", "010203",
                               "--match-column-bounds", "--json")
        self.assertEqual(json.loads(one_column.stdout)["match"]["column_bounds"],
                         [{"y": 0, "height": 2}])
        ordinary = self._run(path, "0", "0", "--width", "3", "--height", "2",
                             "--find-color", "010203", "--json")
        self.assertNotIn("column_bounds", json.loads(ordinary.stdout)["match"])

        alpha = self._write(self._tmp_dir(), "alpha.png", make_png(1, 2,
            [bytes((10, 20, 30, 0)), bytes((11, 20, 30, 255))], color_type=6))
        exact = self._run(alpha, "0", "0", "--height", "2", "--find-color", "0a141e",
                          "--color-tolerance", "1", "--match-alpha", "0",
                          "--match-column-bounds", "--json")
        self.assertEqual(json.loads(exact.stdout)["match"]["column_bounds"],
                         [{"y": 0, "height": 1}])
        opaque = self._run(path, "0", "0", "--width", "3", "--height", "2",
                           "--find-color", "010203", "--match-alpha", "255",
                           "--match-column-bounds", "--json")
        self.assertEqual(json.loads(opaque.stdout)["match"]["column_bounds"],
                         [{"y": 0, "height": 2}] * 3)

    def test_requires_find_color_help_and_direct_script(self):
        _, encoded = rgb_image(1, 1, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "one.png", encoded)
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            invalid = self._run(path, "0", "0", "--match-column-bounds")
        self._assert_usage_error(invalid, "requires --find-color")
        self.assertEqual(invalid.stdout, "")
        self.assertIn("--match-column-bounds", self._run("--help").stdout)
        direct = self._run_script(path, "0", "0", "--find-color", "010203",
                                  "--match-column-bounds", "--json")
        self._assert_success(direct)
        self.assertEqual(json.loads(direct.stdout)["match"]["column_bounds"],
                         [{"y": 0, "height": 1}])


if __name__ == "__main__":
    import unittest

    unittest.main()
