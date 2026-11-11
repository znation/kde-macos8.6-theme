"""First row-major positions in reference-pixel histograms."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample
from tools import sample_report_histogram


class TestSampleHistogramPositions(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _fixture(self):
        _, data = rgb_image(5, 4, lambda x, y: (
            (8, 8, 8) if x == 0 or x == 4 or y == 0 or y == 3 else
            ((1, 2, 3), (4, 5, 6), (1, 2, 3))[x - 1]
        ))
        return self._write(self._tmp_dir(), "positions.png", data)

    def test_json_text_crop_order_and_combined_bounds_and_fraction(self):
        path = self._fixture()
        result = self._run(path, "1", "1", "--width", "3", "--height", "2",
                           "--histogram", "--color-positions", "--json")
        self._assert_success(result)
        data = json.loads(result.stdout)
        self.assertEqual(data["colors"], [
            {"rgb": [1, 2, 3], "hex": "#010203", "count": 4, "position": {"x": 1, "y": 1}},
            {"rgb": [4, 5, 6], "hex": "#040506", "count": 2, "position": {"x": 2, "y": 1}},
        ])
        text = self._run(path, "1", "1", "--width", "3", "--height", "2",
                         "--histogram", "--color-positions")
        self._assert_success(text)
        self.assertIn("count=4  position=1,1", text.stdout)
        self.assertIn("count=2  position=2,1", text.stdout)

        combined = self._run(path, "1", "1", "--width", "3", "--height", "2",
                             "--histogram", "--color-positions", "--color-bounds",
                             "--color-fractions", "--top-colors", "1", "--json")
        self._assert_success(combined)
        color = json.loads(combined.stdout)["colors"][0]
        self.assertEqual((color["count"], color["fraction"], color["position"], color["bounds"]),
                         (4, 4 / 6, {"x": 1, "y": 1}, {"x": 1, "y": 1, "width": 3, "height": 2}))

    def test_alpha_keys_and_one_positioned_traversal_shared_with_bounds(self):
        rows = [bytes((1, 2, 3, 0, 1, 2, 3, 128, 1, 2, 3, 0))]
        path = self._write(self._tmp_dir(), "rgba.png", make_png(3, 1, rows, color_type=6))
        with mock.patch.object(sample_report_histogram, "_positioned_region_pixels",
                               wraps=sample_report_histogram._positioned_region_pixels) as positioned:
            result = self._run(path, "0", "0", "--width", "3", "--histogram", "--alpha",
                               "--color-positions", "--color-bounds", "--json")
        self._assert_success(result)
        colors = json.loads(result.stdout)["colors"]
        self.assertEqual([item["position"] for item in colors],
                         [{"x": 0, "y": 0}, {"x": 1, "y": 0}])
        self.assertEqual([item["alpha"] for item in colors], [0, 128])
        positioned.assert_called_once()

    def test_disconnected_first_occurrence_differs_from_bounds_corner(self):
        _, data = rgb_image(6, 6, lambda x, y: (
            (9, 9, 9) if (x, y) in ((5, 0), (0, 5)) else (0, 0, 0)))
        path = self._write(self._tmp_dir(), "disconnected.png", data)
        result = self._run(path, "0", "0", "--width", "6", "--height", "6",
                           "--histogram", "--color-positions", "--color-bounds", "--json")
        self._assert_success(result)
        colors = json.loads(result.stdout)["colors"]
        self.assertEqual(colors[1], {
            "rgb": [9, 9, 9], "hex": "#090909", "count": 2,
            "position": {"x": 5, "y": 0},
            "bounds": {"x": 0, "y": 0, "width": 6, "height": 6},
        })

    def test_single_pixel_and_uniform_region(self):
        _, data = rgb_image(6, 6, lambda x, y: (
            (9, 9, 9) if (x, y) in ((5, 0), (0, 5)) else (0, 0, 0)))
        path = self._write(self._tmp_dir(), "anchors.png", data)
        single = self._run(path, "5", "0", "--width", "1", "--height", "1",
                           "--histogram", "--color-positions", "--json")
        self._assert_success(single)
        self.assertEqual(json.loads(single.stdout)["colors"], [
            {"rgb": [9, 9, 9], "hex": "#090909", "count": 1, "position": {"x": 5, "y": 0}},
        ])
        uniform = self._run(path, "1", "1", "--width", "4", "--height", "4",
                            "--histogram", "--color-positions", "--json")
        self._assert_success(uniform)
        self.assertEqual(json.loads(uniform.stdout)["colors"], [
            {"rgb": [0, 0, 0], "hex": "#000000", "count": 16, "position": {"x": 1, "y": 1}},
        ])

    def test_option_requires_histogram_before_reads_and_script_parity(self):
        path = self._fixture()
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            for mode in ((), ("--runs",), ("--find-color", "010203")):
                result = self._run(path, "0", "0", "--color-positions", *mode)
                self._assert_usage_error(result, "requires --histogram")
                self.assertEqual(result.stdout, "")
        args = (path, "1", "1", "--width", "3", "--height", "2", "--histogram",
                "--color-positions", "--json")
        direct = self._run(*args)
        script = self._run_script(*args)
        self._assert_success(direct)
        self._assert_success(script)
        self.assertEqual(json.loads(direct.stdout), json.loads(script.stdout))
        help_result = self._run("--help")
        self.assertIn("--color-positions", help_result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()

