"""Tests for the sampler's completed-run length filter."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample


class TestSampleRunsMinimumLength(CliTestCase):
    """The scanline runs report's ``--min-run-length`` cutoff."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_horizontal_rectangle_filters_without_joining_or_crossing_rows(self):
        rows = [[(1, 2, 3)] * 2 + [(9, 8, 7)] + [(1, 2, 3)] * 2,
                [(1, 2, 3)] * 2 + [(9, 8, 7)] + [(1, 2, 3)] * 2]
        _, data = rgb_image(7, 2, lambda x, y: rows[y][x - 1] if 1 <= x <= 5 else (0, 0, 0))
        path = self._write(self._tmp_dir(), "horizontal.png", data)
        result = self._run(path, "1", "0", "--width", "5", "--height", "2",
                           "--runs", "--run-axis", "horizontal", "--min-run-length", "2", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["runs"], [
            {"x": 1, "y": 0, "length": 2, "rgb": [1, 2, 3], "hex": "#010203"},
            {"x": 4, "y": 0, "length": 2, "rgb": [1, 2, 3], "hex": "#010203"},
            {"x": 1, "y": 1, "length": 2, "rgb": [1, 2, 3], "hex": "#010203"},
            {"x": 4, "y": 1, "length": 2, "rgb": [1, 2, 3], "hex": "#010203"},
        ])
        text = self._run(path, "1", "0", "--width", "5", "--height", "2", "--runs",
                         "--run-axis", "horizontal", "--min-run-length", "2")
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertEqual(text.stdout.splitlines(), [f"image: {path}  7x2", "region (1, 0) 5x2:",
                         "axis: horizontal", "(1, 0): 1,2,3  #010203  length=2",
                         "(4, 0): 1,2,3  #010203  length=2", "(1, 1): 1,2,3  #010203  length=2",
                         "(4, 1): 1,2,3  #010203  length=2"])

    def test_vertical_rectangle_singleton_inference_and_empty_output(self):
        _, data = rgb_image(3, 4, lambda x, y: (4, 5, 6) if y < 2 else (8, 9, 10))
        path = self._write(self._tmp_dir(), "vertical.png", data)
        vertical = self._run(path, "1", "1", "--height", "3", "--runs", "--min-run-length", "2", "--json")
        self.assertEqual(vertical.returncode, 0, vertical.stderr)
        self.assertEqual(json.loads(vertical.stdout)["runs"], [
            {"x": 1, "y": 2, "length": 2, "rgb": [8, 9, 10], "hex": "#08090A"},
        ])
        singleton = self._run(path, "1", "1", "--runs", "--run-axis", "vertical",
                              "--min-run-length", "2")
        self.assertEqual(singleton.returncode, 0, singleton.stderr)
        self.assertEqual(singleton.stdout.splitlines(), [f"image: {path}  3x4", "region (1, 1) 1x1:", "axis: vertical"])
        empty = self._run(path, "1", "1", "--height", "3", "--runs", "--min-run-length", "4", "--json")
        self.assertEqual(json.loads(empty.stdout)["runs"], [])
        empty_text = self._run(path, "1", "1", "--height", "3", "--runs", "--min-run-length", "4")
        self.assertEqual(empty_text.stdout.splitlines(), [f"image: {path}  3x4", "region (1, 1) 1x3:", "axis: vertical"])
        default = self._run(path, "1", "1", "--height", "3", "--runs", "--json")
        cutoff_one = self._run(path, "1", "1", "--height", "3", "--runs", "--min-run-length", "1", "--json")
        self.assertEqual((cutoff_one.returncode, cutoff_one.stdout, cutoff_one.stderr),
                         (default.returncode, default.stdout, default.stderr))

    def test_alpha_grouping_opaque_fallback_and_transparent_rgb(self):
        row = bytes((1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 255, 9, 8, 7, 255))
        path = self._write(self._tmp_dir(), "alpha.png", make_png(4, 1, [row], color_type=6))
        result = self._run(path, "0", "0", "--width", "4", "--runs", "--alpha",
                           "--min-run-length", "2", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["runs"], [
            {"x": 0, "y": 0, "length": 2, "rgb": [1, 2, 3], "hex": "#010203", "alpha": 0},
        ])
        _, opaque_data = rgb_image(2, 1, lambda x, y: (3, 4, 5))
        opaque = self._write(self._tmp_dir(), "opaque.png", opaque_data)
        fallback = self._run(opaque, "0", "0", "--width", "2", "--runs", "--alpha",
                             "--min-run-length", "2", "--json")
        self.assertEqual(json.loads(fallback.stdout)["runs"][0]["alpha"], 255)

    def test_bad_and_missing_cutoffs_and_direct_script_match(self):
        for value in ("0", "-1", "１２", "2x"):
            result = self._run("missing.png", "0", "0", "--runs", "--min-run-length", value)
            self.assertEqual(result.returncode, 2, value)
            self.assertEqual(result.stdout, "", value)
        missing = self._run("missing.png", "0", "0", "--runs", "--min-run-length")
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(missing.stdout, "")
        _, data = rgb_image(3, 1, lambda x, y: (1, 2, 3) if x < 2 else (4, 5, 6))
        path = self._write(self._tmp_dir(), "direct.png", data)
        args = (path, "0", "0", "--width", "3", "--runs", "--min-run-length", "2", "--json")
        package, direct = self._run(*args), self._run_script(*args)
        self.assertEqual((package.returncode, package.stdout, package.stderr),
                         (direct.returncode, direct.stdout, direct.stderr))


if __name__ == "__main__":
    import unittest

    unittest.main()
