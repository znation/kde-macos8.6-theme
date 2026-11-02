"""Tests bounded coordinate output for reference-color matches."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample


class TestSampleMatchPixels(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _image(self):
        matches = {(1, 1), (3, 1), (2, 2), (4, 3)}
        _, data = rgb_image(6, 4, lambda x, y: (9, 8, 7) if (x, y) in matches else (0, 0, 0))
        return self._write(self._tmp_dir(), "matches.png", data)

    def test_prefix_order_region_bounds_and_omitted_count(self):
        path = self._image()
        args = (path, "1", "1", "--width", "3", "--height", "2", "--find-color", "090807")
        limited = self._run(*args, "--match-pixels", "2", "--json")
        self._assert_success(limited)
        match = json.loads(limited.stdout)["match"]
        self.assertEqual(match["count"], 3)
        self.assertEqual(match["bounds"], {"x": 1, "y": 1, "width": 3, "height": 2})
        self.assertEqual(match["pixels"], [{"x": 1, "y": 1}, {"x": 3, "y": 1}])
        self.assertEqual(match["omitted_pixels"], 1)
        for limit, expected, omitted in ((1, [(1, 1)], 2), (3, [(1, 1), (3, 1), (2, 2)], 0),
                                         (8, [(1, 1), (3, 1), (2, 2)], 0)):
            result = self._run(*args, "--match-pixels", str(limit), "--json")
            self._assert_success(result)
            report = json.loads(result.stdout)["match"]
            self.assertEqual([(p["x"], p["y"]) for p in report["pixels"]], expected)
            self.assertEqual(report["omitted_pixels"], omitted)

    def test_text_absent_and_tolerance_alpha_predicates(self):
        path = self._image()
        result = self._run(path, "1", "1", "--width", "3", "--height", "2",
                           "--find-color", "090807", "--match-pixels", "1")
        self._assert_success(result)
        self.assertIn("matching pixels: 1\npixel (1, 1)\nomitted pixels: 2", result.stdout)
        absent = self._run(path, "0", "0", "--find-color", "ffffff", "--match-pixels", "1", "--json")
        self._assert_success(absent)
        self.assertEqual(json.loads(absent.stdout)["match"]["pixels"], [])
        self.assertEqual(json.loads(absent.stdout)["match"]["omitted_pixels"], 0)
        row = bytes((9, 8, 7, 0, 10, 8, 7, 255, 9, 8, 7, 255))
        alpha_path = self._write(self._tmp_dir(), "alpha.png", make_png(3, 1, [row], color_type=6))
        found = self._run(alpha_path, "0", "0", "--width", "3", "--find-color", "090807",
                          "--color-tolerance", "1", "--match-alpha", "255", "--match-pixels", "5", "--json")
        self._assert_success(found)
        self.assertEqual(json.loads(found.stdout)["match"]["pixels"], [{"x": 1, "y": 0}, {"x": 2, "y": 0}])
        opaque_path = self._write(self._tmp_dir(), "opaque.png", rgb_image(2, 2, lambda x, y: (9, 8, 7))[1])
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            opaque = self._run(opaque_path, "0", "1", "--width", "2", "--find-color", "090807",
                               "--match-alpha", "255", "--match-pixels", "1", "--json")
        self._assert_success(opaque)
        self.assertEqual(json.loads(opaque.stdout)["match"]["pixels"], [{"x": 0, "y": 1}])
        self.assertTrue(read.call_args.kwargs["alpha"])
        self.assertEqual(read.call_args.kwargs["max_rows"], 2)

    def test_validation_precedes_reads_and_default_schema_is_unchanged(self):
        path = self._image()
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            for value in ("0", "-1", "1001", "1.5", "١", ""):
                invalid = self._run(path, "0", "0", "--find-color", "090807", "--match-pixels", value)
                self._assert_usage_error(invalid)
                self.assertEqual(invalid.stdout, "")
            missing = self._run(path, "0", "0", "--find-color", "090807", "--match-pixels")
            self._assert_usage_error(missing)
            self.assertEqual(missing.stdout, "")
            unused = self._run(path, "0", "0", "--match-pixels", "1")
            self._assert_usage_error(unused, "requires --find-color")
        default = self._run(path, "0", "0", "--find-color", "090807", "--json")
        self._assert_success(default)
        self.assertNotIn("pixels", json.loads(default.stdout)["match"])
        self.assertNotIn("omitted_pixels", json.loads(default.stdout)["match"])
        script = self._run_script(path, "1", "1", "--find-color", "090807", "--match-pixels", "1", "--json")
        self._assert_success(script)
        self.assertEqual(json.loads(script.stdout)["match"]["pixels"], [{"x": 1, "y": 1}])


if __name__ == "__main__":
    import unittest

    unittest.main()
