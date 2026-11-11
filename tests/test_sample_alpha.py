"""Alpha reporting for individual reference-pixel samples."""

from __future__ import annotations

import json
from unittest import mock

from support.cli_fixtures import CliTestCase
from support import repo_root  # noqa: F401
from support.png_fixtures import control_named_png, make_png
from tools import sample


class TestSampleAlpha(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _rgba(self):
        rows = [bytes((10, 20, 30, 0, 10, 20, 30, 128)),
                bytes((40, 50, 60, 255, 70, 80, 90, 255))]
        return self._write(self._tmp_dir(), "alpha.png", make_png(2, 2, rows, color_type=6))

    def test_json_pixel_and_offset_rectangle_keep_rgb_and_alpha(self):
        path = self._rgba()
        pixel = self._run(path, "0", "0", "--alpha", "--json")
        self._assert_success(pixel)
        self.assertEqual(json.loads(pixel.stdout)["pixels"], [
            {"x": 0, "y": 0, "rgb": [10, 20, 30], "hex": "#0A141E", "alpha": 0}
        ])
        rect = self._run(path, "1", "0", "--width", "1", "--height", "2", "--alpha", "--json")
        self._assert_success(rect)
        result = json.loads(rect.stdout)
        self.assertEqual((result["image_width"], result["image_height"]), (2, 2))
        self.assertEqual(result["pixels"], [
            {"x": 1, "y": 0, "rgb": [10, 20, 30], "hex": "#0A141E", "alpha": 128},
            {"x": 1, "y": 1, "rgb": [70, 80, 90], "hex": "#46505A", "alpha": 255},
        ])

    def test_exact_singleton_and_rectangle_output_and_script_parity(self):
        path = self._rgba()
        singleton = self._run(path, "0", "0", "--alpha")
        self._assert_success(singleton)
        self.assertEqual(singleton.stdout,
                         f"image: {path}  2x2\npixel (0, 0): 10,20,30  #0A141E  alpha=0\n")
        rectangle_args = (path, "1", "0", "--width", "1", "--height", "2", "--alpha")
        rectangle = self._run(*rectangle_args)
        self._assert_success(rectangle)
        self.assertEqual(rectangle.stdout,
                         f"image: {path}  2x2\nregion (1, 0) 1x2:\n"
                         "(1, 0): 10,20,30  #0A141E  alpha=128\n"
                         "(1, 1): 70,80,90  #46505A  alpha=255\n")
        json_args = (path, "1", "0", "--width", "1", "--height", "2", "--alpha", "--json")
        package = self._run(*json_args)
        direct = self._run_script(*json_args)
        self.assertEqual((direct.stdout, direct.stderr, direct.returncode),
                         (package.stdout, package.stderr, package.returncode))
        self.assertEqual(package.stdout,
                         json.dumps({"image": path, "image_width": 2, "image_height": 2,
                             "region": {"x": 1, "y": 0, "width": 1, "height": 2},
                             "pixels": [
                                 {"x": 1, "y": 0, "rgb": [10, 20, 30],
                                  "hex": "#0A141E", "alpha": 128},
                                 {"x": 1, "y": 1, "rgb": [70, 80, 90],
                                  "hex": "#46505A", "alpha": 255},
                             ]}, ensure_ascii=True) + "\n")

    def test_text_and_default_output(self):
        path = self._rgba()
        result = self._run(path, "0", "0", "--alpha")
        self._assert_success(result)
        self.assertIn("pixel (0, 0): 10,20,30  #0A141E  alpha=0", result.stdout)
        ordinary = self._run(path, "0", "0", "--json")
        self._assert_success(ordinary)
        self.assertNotIn("alpha", json.loads(ordinary.stdout)["pixels"][0])

    def test_text_rectangle_reports_alpha_in_row_major_order(self):
        path = self._rgba()
        result = self._run(path, "0", "0", "--width", "2", "--height", "2", "--alpha")
        self._assert_success(result)
        self.assertIn("region (0, 0) 2x2:", result.stdout)
        self.assertIn("(0, 0): 10,20,30  #0A141E  alpha=0", result.stdout)
        self.assertIn("(1, 0): 10,20,30  #0A141E  alpha=128", result.stdout)
        self.assertIn("(0, 1): 40,50,60  #28323C  alpha=255", result.stdout)
        self.assertIn("(1, 1): 70,80,90  #46505A  alpha=255", result.stdout)

    def test_script_json_and_control_path(self):
        with control_named_png() as path:
            result = self._run_script(path, "0", "0", "--alpha", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["pixels"][0]["alpha"], 255)
        self.assertNotIn("\x1b", result.stdout)

    def test_opaque_and_trns_alpha(self):
        opaque = self._write(self._tmp_dir(), "opaque.png", make_png(1, 1, [bytes((4, 5, 6))]))
        result = self._run(opaque, "0", "0", "--alpha", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["pixels"][0]["alpha"], 255)
        transparent = self._write(self._tmp_dir(), "trns.png", make_png(
            1, 1, [bytes((4, 5, 6))], color_type=2, trns=b"\x00\x04\x00\x05\x00\x06"))
        result = self._run(transparent, "0", "0", "--alpha", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["pixels"][0],
                         {"x": 0, "y": 0, "rgb": [4, 5, 6], "hex": "#040506", "alpha": 0})

    def test_opaque_rectangle_reports_255_alpha_in_row_major_order(self):
        opaque = self._write(self._tmp_dir(), "opaque-rect.png", make_png(
            2, 2, [bytes((4, 5, 6, 7, 8, 9)), bytes((10, 11, 12, 13, 14, 15))]))
        result = self._run(opaque, "0", "0", "--width", "2", "--height", "2", "--alpha", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["pixels"], [
            {"x": 0, "y": 0, "rgb": [4, 5, 6], "hex": "#040506", "alpha": 255},
            {"x": 1, "y": 0, "rgb": [7, 8, 9], "hex": "#070809", "alpha": 255},
            {"x": 0, "y": 1, "rgb": [10, 11, 12], "hex": "#0A0B0C", "alpha": 255},
            {"x": 1, "y": 1, "rgb": [13, 14, 15], "hex": "#0D0E0F", "alpha": 255},
        ])

    def test_opaque_text_rectangle_reports_255_alpha_in_row_major_order(self):
        opaque = self._write(self._tmp_dir(), "opaque-text-rect.png", make_png(
            2, 2, [bytes((4, 5, 6, 7, 8, 9)), bytes((10, 11, 12, 13, 14, 15))]))
        result = self._run(opaque, "0", "0", "--width", "2", "--height", "2", "--alpha")
        self._assert_success(result)
        self.assertIn("(0, 0): 4,5,6  #040506  alpha=255", result.stdout)
        self.assertIn("(1, 0): 7,8,9  #070809  alpha=255", result.stdout)
        self.assertIn("(0, 1): 10,11,12  #0A0B0C  alpha=255", result.stdout)
        self.assertIn("(1, 1): 13,14,15  #0D0E0F  alpha=255", result.stdout)

    def test_alpha_read_is_bounded_and_mode_conflicts_skip_decode(self):
        path = self._rgba()
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(path, "1", "0", "--height", "2", "--alpha")
            self._assert_success(result)
            read.assert_called_once_with(path, max_rows=2, alpha=True)
        for mode in ("--find-color", "000000"):
            args = (path, "0", "0", "--alpha", mode) if mode != "000000" else (path, "0", "0", "--alpha", "--find-color", mode)
            with mock.patch.object(sample, "read_png", side_effect=AssertionError("decoded")):
                result = self._run(*args)
            self._assert_usage_error(result, "--alpha")

    def test_bad_and_out_of_bounds_inputs_do_not_print_pixels(self):
        path = self._rgba()
        with mock.patch.object(sample, "read_png", side_effect=AssertionError("decoded")):
            result = self._run(path, "2", "0", "--alpha")
        self._assert_usage_error(result, "outside")
        missing = self._run(str(self._tmp_dir() / "missing.png"), "0", "0", "--alpha")
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(missing.stdout, "")
        corrupt = self._write(self._tmp_dir(), "corrupt.png", b"not a png")
        broken = self._run(corrupt, "0", "0", "--alpha")
        self.assertEqual(broken.returncode, 2)
        self.assertEqual(broken.stdout, "")


if __name__ == "__main__":
    import unittest
    unittest.main()
