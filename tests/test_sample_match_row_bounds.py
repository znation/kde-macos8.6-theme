"""Tests per-row enclosing spans in reference color searches."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample, sample_report_search


class TestSampleMatchRowBounds(CliTestCase):
    """The find-color search's ``--match-row-bounds`` per-row spans."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_offset_disconnected_spans_and_combined_diagnostics(self):
        target = (10, 20, 30)
        rows = [[target, (0, 0, 0), (11, 20, 30), target],
                [(0, 0, 0)] * 4,
                [(0, 0, 0), target, (0, 0, 0), (0, 0, 0)]]
        _, encoded = rgb_image(6, 5, lambda x, y: rows[y - 1][x - 1]
                               if 1 <= x <= 4 and 1 <= y <= 3 else (99, 99, 99))
        path = self._write(self._tmp_dir(), "spans.png", encoded)
        args = (path, "1", "1", "--width", "4", "--height", "3",
                "--find-color", "0a141e", "--color-tolerance", "1",
                "--match-row-bounds")
        with mock.patch.object(sample_report_search, "positioned_region_pixels",
                               wraps=sample_report_search.positioned_region_pixels) as pixels, \
                mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(*args, "--match-pixels", "1", "--match-rows",
                               "--match-columns", "--match-runs", "--match-column-runs", "--json")
        self._assert_success(result)
        match = json.loads(result.stdout)["match"]
        self.assertEqual(match["row_bounds"], [
            {"x": 1, "width": 4}, None, {"x": 2, "width": 1}])
        self.assertEqual(match["pixels"], [{"x": 1, "y": 1}])
        pixels.assert_called_once()
        self.assertEqual(read.call_args.kwargs["max_rows"], 4)
        text = self._run(*args)
        self._assert_success(text)
        self.assertIn('matching row bounds: [{"x":1,"width":4},null,{"x":2,"width":1}]', text.stdout)

    def test_full_empty_narrow_crops_alpha_and_default_omission(self):
        _, encoded = rgb_image(3, 2, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "coverage.png", encoded)
        full = self._run(path, "0", "0", "--width", "3", "--height", "2",
                         "--find-color", "010203", "--match-row-bounds", "--json")
        self.assertEqual(json.loads(full.stdout)["match"]["row_bounds"],
                         [{"x": 0, "width": 3}, {"x": 0, "width": 3}])
        empty = self._run(path, "0", "0", "--width", "3", "--height", "2",
                          "--find-color", "ffffff", "--match-row-bounds", "--json")
        self.assertEqual(json.loads(empty.stdout)["match"]["row_bounds"], [None, None])
        single = self._run(path, "2", "1", "--find-color", "010203",
                           "--match-row-bounds", "--json")
        self.assertEqual(json.loads(single.stdout)["match"]["row_bounds"],
                         [{"x": 2, "width": 1}])
        one_row = self._run(path, "1", "0", "--width", "2", "--find-color", "010203",
                            "--match-row-bounds", "--json")
        self.assertEqual(json.loads(one_row.stdout)["match"]["row_bounds"],
                         [{"x": 1, "width": 2}])
        one_column = self._run(path, "2", "0", "--height", "2", "--find-color", "010203",
                               "--match-row-bounds", "--json")
        self.assertEqual(json.loads(one_column.stdout)["match"]["row_bounds"],
                         [{"x": 2, "width": 1}, {"x": 2, "width": 1}])
        ordinary = self._run(path, "0", "0", "--width", "3", "--height", "2",
                             "--find-color", "010203", "--json")
        self.assertNotIn("row_bounds", json.loads(ordinary.stdout)["match"])

        alpha = self._write(self._tmp_dir(), "alpha.png", make_png(2, 1,
            [bytes((10, 20, 30, 0, 11, 20, 30, 255))], color_type=6))
        exact = self._run(alpha, "0", "0", "--width", "2", "--find-color", "0a141e",
                          "--color-tolerance", "1", "--match-alpha", "0",
                          "--match-row-bounds", "--json")
        self.assertEqual(json.loads(exact.stdout)["match"]["row_bounds"],
                         [{"x": 0, "width": 1}])
        opaque = self._run(path, "0", "0", "--width", "3", "--height", "2",
                           "--find-color", "010203", "--match-alpha", "255",
                           "--match-row-bounds", "--json")
        self.assertEqual(json.loads(opaque.stdout)["match"]["row_bounds"],
                         [{"x": 0, "width": 3}, {"x": 0, "width": 3}])

    def test_requires_find_color_help_and_direct_script(self):
        _, encoded = rgb_image(1, 1, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "one.png", encoded)
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            invalid = self._run(path, "0", "0", "--match-row-bounds")
        self._assert_usage_error(invalid, "requires --find-color")
        self.assertEqual(invalid.stdout, "")
        self.assertIn("--match-row-bounds", self._run("--help").stdout)
        direct = self._run_script(path, "0", "0", "--find-color", "010203",
                                  "--match-row-bounds", "--json")
        self._assert_success(direct)
        self.assertEqual(json.loads(direct.stdout)["match"]["row_bounds"],
                         [{"x": 0, "width": 1}])


if __name__ == "__main__":
    import unittest

    unittest.main()
