"""Tests pagination of bounded reference-color match coordinates."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample


class TestSampleMatchPixelOffset(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _image(self):
        matches = {(1, 1), (3, 1), (2, 2), (4, 3)}
        _, data = rgb_image(6, 4, lambda x, y: (9, 8, 7) if (x, y) in matches else (0, 0, 0))
        return self._write(self._tmp_dir(), "matches.png", data)

    def test_pages_offset_crop_and_preserves_full_search(self):
        path = self._image()
        args = (path, "1", "1", "--width", "4", "--height", "3",
                "--find-color", "090807", "--match-pixels", "2")
        all_coords = []
        for offset, expected, omitted in (
                (0, [(1, 1), (3, 1)], 2),
                (2, [(2, 2), (4, 3)], 2),
                (3, [(4, 3)], 3), (4, [], 4), (9, [], 4)):
            result = self._run(*args, "--match-pixel-offset", str(offset),
                               "--match-fraction", "--match-centroid", "--match-runs", "--json")
            self._assert_success(result)
            match = json.loads(result.stdout)["match"]
            self.assertEqual(match["pixels"], [{"x": x, "y": y} for x, y in expected])
            self.assertEqual(match["omitted_pixels"], omitted)
            self.assertEqual(match["pixel_offset"], offset)
            self.assertEqual((match["count"], match["bounds"], match["fraction"],
                              match["centroid"], match["runs"]),
                             (4, {"x": 1, "y": 1, "width": 4, "height": 3},
                              1 / 3, {"x": 2.5, "y": 1.75},
                              [{"x": 1, "y": 1, "length": 1},
                               {"x": 3, "y": 1, "length": 1},
                               {"x": 2, "y": 2, "length": 1},
                               {"x": 4, "y": 3, "length": 1}]))
            if offset in (0, 2):
                all_coords.extend(expected)
        self.assertEqual(all_coords, [(1, 1), (3, 1), (2, 2), (4, 3)])

    def test_zero_default_alpha_empty_and_text(self):
        path = self._image()
        args = (path, "1", "1", "--width", "3", "--height", "2",
                "--find-color", "090807", "--match-pixels", "1")
        default = self._run(*args, "--json")
        self._assert_success(default)
        self.assertNotIn("pixel_offset", json.loads(default.stdout)["match"])
        zero = self._run(*args, "--match-pixel-offset", "0")
        self._assert_success(zero)
        self.assertIn("pixel offset: 0\nmatching pixels: 1\npixel (1, 1)", zero.stdout)
        none = self._run(path, "0", "0", "--find-color", "ffffff", "--match-pixels", "1",
                         "--match-pixel-offset", "0", "--json")
        self._assert_success(none)
        self.assertEqual(json.loads(none.stdout)["match"]["pixels"], [])
        row = bytes((9, 8, 7, 0, 10, 8, 7, 255, 9, 8, 7, 255))
        alpha_path = self._write(self._tmp_dir(), "alpha.png", make_png(3, 1, [row], color_type=6))
        found = self._run(alpha_path, "0", "0", "--width", "3", "--find-color", "090807",
                          "--color-tolerance", "1", "--match-alpha", "255",
                          "--match-pixels", "1", "--match-pixel-offset", "1", "--json")
        self._assert_success(found)
        self.assertEqual(json.loads(found.stdout)["match"]["pixels"], [{"x": 2, "y": 0}])
        opaque_path = self._write(self._tmp_dir(), "opaque.png",
                                  rgb_image(2, 1, lambda x, y: (9, 8, 7))[1])
        opaque = self._run(opaque_path, "0", "0", "--width", "2", "--find-color", "090807",
                           "--match-alpha", "255", "--match-pixels", "1",
                           "--match-pixel-offset", "1", "--json")
        self._assert_success(opaque)
        self.assertEqual(json.loads(opaque.stdout)["match"]["pixels"], [{"x": 1, "y": 0}])
        pixel = self._run(opaque_path, "1", "0", "--find-color", "090807",
                          "--match-pixels", "1", "--match-pixel-offset", "1", "--json")
        self._assert_success(pixel)
        self.assertEqual(json.loads(pixel.stdout)["match"]["pixels"], [])

    def test_validation_before_reads_and_direct_script(self):
        path = self._image()
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            for value in ("-1", "1.5", "1e2", "1_0", "١", " 1", "x", "9" * 5000):
                bad = self._run(path, "0", "0", "--find-color", "090807", "--match-pixels", "1",
                                "--match-pixel-offset", value)
                self._assert_usage_error(bad)
                self.assertEqual(bad.stdout, "")
            missing = self._run(path, "0", "0", "--find-color", "090807", "--match-pixel-offset")
            self._assert_usage_error(missing)
            self.assertEqual(missing.stdout, "")
            for options in (("--match-pixel-offset", "0"),
                            ("--histogram", "--match-pixel-offset", "0"),
                            ("--runs", "--width", "2", "--match-pixel-offset", "0"),
                            ("--find-color", "090807", "--match-pixel-offset", "0")):
                bad = self._run(path, "0", "0", *options)
                self._assert_usage_error(bad, "requires --match-pixels")
                self.assertEqual(bad.stdout, "")
        script = self._run_script(path, "1", "1", "--find-color", "090807", "--match-pixels", "1",
                                  "--match-pixel-offset", "1", "--json")
        self._assert_success(script)
        self.assertEqual(json.loads(script.stdout)["match"]["pixel_offset"], 1)


if __name__ == "__main__":
    import unittest

    unittest.main()
