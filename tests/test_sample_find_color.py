"""Tests for locating a chosen RGB color in a sampled region."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import control_named_png, make_png, rgb_image, solid_rgb
from support.symlink_fixtures import symlinked_repo
from tools import sample


class TestSampleFindColor(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _image(self):
        _, data = rgb_image(6, 4, lambda x, y: (
            (1, 2, 3) if (x, y) in {(0, 0), (2, 1), (4, 3)} else
            (0, 0, 0) if x == 1 else (255, 255, 255)
        ))
        return self._write(self._tmp_dir(), "find.png", data)

    def test_json_disconnected_matches_are_counted_and_bounded_absolutely(self):
        path = self._image()
        result = self._run(path, "1", "0", "--width", "4", "--height", "4", "--find-color", "#010203", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout), {
            "image": path, "image_width": 6, "image_height": 4,
            "region": {"x": 1, "y": 0, "width": 4, "height": 4},
            "match": {"rgb": [1, 2, 3], "hex": "#010203", "count": 2,
                      "bounds": {"x": 2, "y": 1, "width": 3, "height": 3}},
        })

    def test_text_single_pixel_black_white_full_region_and_absence(self):
        path = self._write(self._tmp_dir(), "white.png", solid_rgb(2, 2, (255, 255, 255))[1])
        result = self._run(path, "1", "1", "--find-color", "ffffff")
        self._assert_success(result)
        self.assertEqual(result.stdout.splitlines(), [
            f"image: {path}  2x2", "region (1, 1) 1x1:", "color: #FFFFFF",
            "count: 1", "bounds: 1,1,1,1",
        ])
        full = self._run(path, "0", "0", "--width", "2", "--height", "2", "--find-color", "#FFFFFF", "--json")
        self._assert_success(full)
        self.assertEqual(json.loads(full.stdout)["match"]["bounds"], {"x": 0, "y": 0, "width": 2, "height": 2})
        absent = self._run(path, "0", "0", "--find-color", "000000", "--json")
        self._assert_success(absent)
        self.assertEqual(json.loads(absent.stdout)["match"], {"rgb": [0, 0, 0], "hex": "#000000", "count": 0, "bounds": None})
        absent_text = self._run(path, "0", "0", "--find-color", "000000")
        self._assert_success(absent_text)
        self.assertIn("count: 0", absent_text.stdout)
        self.assertIn("bounds: none", absent_text.stdout)

    def test_alpha_does_not_change_rgb_matching(self):
        data = make_png(2, 1, [bytes((9, 8, 7, 0, 9, 8, 7, 255))], color_type=6)
        path = self._write(self._tmp_dir(), "alpha.png", data)
        result = self._run(path, "0", "0", "--width", "2", "--find-color", "090807", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["match"]["count"], 2)

    def test_tolerance_threshold_channel_boundary_and_absolute_bounds(self):
        pixels = [(255, 0, 0), (10, 20, 30), (13, 20, 30), (12, 18, 32), (10, 23, 30), (255, 0, 0)]
        _, data = rgb_image(6, 1, lambda x, y: pixels[x])
        path = self._write(self._tmp_dir(), "tolerance.png", data)
        result = self._run(path, "1", "0", "--width", "4", "--find-color", "0a141e",
                           "--color-tolerance", "2", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["match"], {
            "rgb": [10, 20, 30], "hex": "#0A141E", "count": 2,
            "bounds": {"x": 1, "y": 0, "width": 3, "height": 1}, "tolerance": 2,
        })
        full = self._run(path, "0", "0", "--width", "6", "--find-color", "0a141e",
                         "--color-tolerance", "2", "--json")
        self._assert_success(full)
        self.assertEqual(json.loads(full.stdout)["match"]["count"], 2)
        maximum = self._run(path, "5", "0", "--find-color", "0a141e", "--color-tolerance", "255", "--json")
        self._assert_success(maximum)
        self.assertEqual(json.loads(maximum.stdout)["match"]["count"], 1)

    def test_explicit_zero_schema_text_and_invalid_tolerance(self):
        path = self._image()
        omitted = self._run(path, "0", "0", "--find-color", "010203", "--json")
        zero = self._run(path, "0", "0", "--find-color", "010203", "--color-tolerance", "0", "--json")
        self._assert_success(omitted)
        self._assert_success(zero)
        self.assertNotIn("tolerance", json.loads(omitted.stdout)["match"])
        self.assertEqual(json.loads(zero.stdout)["match"]["tolerance"], 0)
        text = self._run(path, "0", "0", "--find-color", "010203", "--color-tolerance", "0")
        self._assert_success(text)
        self.assertIn("tolerance: 0", text.stdout)
        self.assertEqual(next(line for line in text.stdout.splitlines() if line.startswith("count:")),
                         f"count: {json.loads(zero.stdout)['match']['count']}")
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            unused = self._run(path, "0", "0", "--color-tolerance", "0")
        self._assert_usage_error(unused, "requires --find-color")
        for invalid in ("-1", "256", "1.5", "١", "1_0", ""):
            bad = self._run(path, "0", "0", "--find-color", "010203", "--color-tolerance", invalid)
            self._assert_usage_error(bad)
            self.assertEqual(bad.stdout, "")

    def test_direct_script_tolerance(self):
        path = self._image()
        result = self._run_script(path, "0", "0", "--find-color", "010203", "--color-tolerance", "255", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["match"]["tolerance"], 255)

    def test_invalid_modes_bounds_decoder_and_path_safety(self):
        path = self._image()
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(path, "1", "1", "--width", "3", "--height", "2", "--find-color", "010203", "--json")
        self._assert_success(result)
        self.assertEqual(read.call_args.kwargs["max_rows"], 3)
        with mock.patch.object(sample, "read_png", side_effect=AssertionError("decoded")):
            outside = self._run(path, "5", "0", "--width", "2", "--find-color", "010203")
            malformed = self._run(path, "0", "0", "--find-color", "xyz")
            conflict = self._run(path, "0", "0", "--find-color", "010203", "--runs")
        self._assert_usage_error(outside, "outside")
        self._assert_usage_error(malformed, "six hexadecimal digits")
        self.assertIn("'xyz'", malformed.stderr)
        self._assert_usage_error(conflict)
        _, data = solid_rgb(1, 1)
        root, link = symlinked_repo(self._tmp_dir(), "reference.png", data)
        with mock.patch.object(sample, "ROOT", str(root)):
            escaped = self._run(str(link), "0", "0", "--find-color", "000000")
        self._assert_usage_error(escaped, "resolves outside")

    def test_control_path_round_trips_in_json(self):
        with control_named_png() as path:
            result = self._run(path, "0", "0", "--find-color", "000000", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["image"], path)
        self.assertNotIn("\x1b", result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
