"""Tests for reference-pixel scanline color runs."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import control_named_png, rgb_image, solid_rgb
from support.symlink_fixtures import symlinked_repo
from tools import sample


class TestSampleRuns(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _fixture(self):
        colors = [(1, 2, 3), (1, 2, 3), (9, 8, 7), (1, 2, 3), (4, 5, 6)]
        _, data = rgb_image(6, 5, lambda x, y: colors[x - 1] if y == 2 and 1 <= x <= 5 else (0, 0, 0))
        return self._write(self._tmp_dir(), "runs.png", data)

    def test_horizontal_json_and_text_keep_separated_runs(self):
        path = self._fixture()
        expected = {
            "image": path, "image_width": 6, "image_height": 5,
            "region": {"x": 1, "y": 2, "width": 5, "height": 1},
            "axis": "horizontal",
            "runs": [
                {"x": 1, "y": 2, "length": 2, "rgb": [1, 2, 3], "hex": "#010203"},
                {"x": 3, "y": 2, "length": 1, "rgb": [9, 8, 7], "hex": "#090807"},
                {"x": 4, "y": 2, "length": 1, "rgb": [1, 2, 3], "hex": "#010203"},
                {"x": 5, "y": 2, "length": 1, "rgb": [4, 5, 6], "hex": "#040506"},
            ],
        }
        result = self._run(path, "1", "2", "--width", "5", "--runs", "--json")
        self._assert_success(result)
        actual = json.loads(result.stdout)
        self.assertEqual(actual, expected)
        self.assertEqual(sum(run["length"] for run in actual["runs"]), 5)
        self.assertTrue(all(a["rgb"] != b["rgb"] for a, b in zip(actual["runs"], actual["runs"][1:])))
        text = self._run(path, "1", "2", "--width", "5", "--runs")
        self._assert_success(text)
        self.assertEqual(text.stdout.splitlines(), [
            f"image: {path}  6x5", "region (1, 2) 5x1:", "axis: horizontal",
            "(1, 2): 1,2,3  #010203  length=2", "(3, 2): 9,8,7  #090807  length=1",
            "(4, 2): 1,2,3  #010203  length=1", "(5, 2): 4,5,6  #040506  length=1",
        ])

    def test_vertical_uniform_and_single_pixel_scans(self):
        _, data = rgb_image(4, 4, lambda x, y: (7, 6, 5) if x == 2 else (x, y, 0))
        path = self._write(self._tmp_dir(), "vertical.png", data)
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(path, "2", "1", "--height", "3", "--runs", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["runs"], [
            {"x": 2, "y": 1, "length": 3, "rgb": [7, 6, 5], "hex": "#070605"},
        ])
        self.assertEqual(json.loads(result.stdout)["axis"], "vertical")
        self.assertEqual(read.call_args.kwargs["max_rows"], 4)
        vertical_text = self._run(path, "2", "1", "--height", "3", "--runs")
        self._assert_success(vertical_text)
        self.assertEqual(vertical_text.stdout.splitlines(), [
            f"image: {path}  4x4", "region (2, 1) 1x3:", "axis: vertical",
            "(2, 1): 7,6,5  #070605  length=3",
        ])
        single = self._run(path, "2", "2", "--runs", "--json")
        self._assert_success(single)
        data = json.loads(single.stdout)
        self.assertEqual(data["axis"], "horizontal")
        self.assertEqual(data["runs"][0]["length"], 1)

    def test_invalid_regions_and_reads_have_no_stdout(self):
        path = self._fixture()
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            two_dimensional = self._run(path, "0", "0", "--width", "2", "--height", "2", "--runs")
        self._assert_usage_error(two_dimensional, "single row or column")
        self.assertEqual(two_dimensional.stdout, "")
        conflict = self._run(path, "0", "0", "--runs", "--histogram")
        self._assert_usage_error(conflict)
        self.assertEqual(conflict.stdout, "")

        outside = self._run(path, "5", "2", "--width", "2", "--runs")
        self._assert_usage_error(outside, "outside the 6x5 image")
        self.assertEqual(outside.stdout, "")
        bad = self._write(self._tmp_dir(), "bad.png", b"not png")
        malformed = self._run(bad, "0", "0", "--runs")
        self._assert_usage_error(malformed)
        self.assertEqual(malformed.stdout, "")
        missing = self._run(str(self._tmp_dir() / "missing.png"), "0", "0", "--runs")
        self._assert_usage_error(missing)
        self.assertEqual(missing.stdout, "")
        _, data = solid_rgb(1, 1)
        root, link = symlinked_repo(self._tmp_dir(), "ref.png", data)
        with mock.patch.object(sample, "ROOT", str(root)):
            escaped = self._run(str(link), "0", "0", "--runs")
        self._assert_usage_error(escaped, "resolves outside")
        self.assertEqual(escaped.stdout, "")

    def test_script_control_path_round_trips_as_json(self):
        with control_named_png() as path:
            result = self._run_script(path, "0", "0", "--runs", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["image"], path)
        self.assertNotIn("\x1b", result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
