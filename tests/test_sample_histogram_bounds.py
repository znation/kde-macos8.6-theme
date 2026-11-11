"""Tests for optional bounds on emitted histogram colors."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample, sample_report_histogram


class TestSampleHistogramBounds(CliTestCase):
    """The histogram's ``--color-bounds`` option: absolute rectangles per emitted color."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_json_bounds_are_absolute_and_enclose_disconnected_matches(self):
        _, data = rgb_image(5, 4, lambda x, y: (
            (9, 9, 9) if (x, y) in {(0, 0), (4, 3)} else
            (1, 2, 3) if (x, y) in {(1, 1), (3, 2)} else (4, 5, 6)
        ))
        path = self._write(self._tmp_dir(), "bounds.png", data)
        result = self._run(path, "1", "1", "--width", "3", "--height", "2",
                           "--histogram", "--color-bounds", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["colors"], [
            {"rgb": [4, 5, 6], "hex": "#040506", "count": 4,
             "bounds": {"x": 1, "y": 1, "width": 3, "height": 2}},
            {"rgb": [1, 2, 3], "hex": "#010203", "count": 2,
             "bounds": {"x": 1, "y": 1, "width": 3, "height": 2}},
        ])

    def test_text_and_top_colors_bound_only_emitted_color(self):
        _, data = rgb_image(3, 2, lambda x, y: (1, 1, 1) if x == 0 else (2, 2, 2))
        path = self._write(self._tmp_dir(), "top.png", data)
        result = self._run(path, "0", "0", "--width", "3", "--height", "2",
                           "--histogram", "--color-bounds", "--top-colors", "1")
        self._assert_success(result)
        self.assertIn("2,2,2  #020202  count=4  bounds=1,0,2,2", result.stdout)
        self.assertIn("total colors: 2", result.stdout)
        self.assertIn("omitted pixels: 2", result.stdout)

    def test_alpha_bounds_separate_transparent_rgb_and_opaque_fallback(self):
        path = self._write(self._tmp_dir(), "rgba.png", make_png(3, 2, [
            bytes((1, 2, 3, 0, 1, 2, 3, 128, 1, 2, 3, 255)),
            bytes((1, 2, 3, 0, 1, 2, 3, 128, 1, 2, 3, 255)),
        ], color_type=6))
        result = self._run(path, "0", "0", "--width", "3", "--height", "2",
                           "--histogram", "--alpha", "--color-bounds", "--json")
        self._assert_success(result)
        records = json.loads(result.stdout)["colors"]
        self.assertEqual([record["alpha"] for record in records], [0, 128, 255])
        self.assertTrue(all(record["bounds"] == {"x": i, "y": 0, "width": 1, "height": 2}
                            for i, record in enumerate(records)))

        _, rgb = rgb_image(1, 1, lambda _x, _y: (7, 8, 9))
        opaque = self._write(self._tmp_dir(), "opaque.png", rgb)
        fallback = self._run(opaque, "0", "0", "--histogram", "--alpha", "--color-bounds", "--json")
        self._assert_success(fallback)
        self.assertEqual(json.loads(fallback.stdout)["colors"][0]["alpha"], 255)

    def test_top_colors_alpha_bounds_cover_only_emitted_rgba_color(self):
        path = self._write(self._tmp_dir(), "rgba-top.png", make_png(3, 2, [
            bytes((1, 2, 3, 0, 1, 2, 3, 128, 1, 2, 3, 255)),
            bytes((1, 2, 3, 0, 1, 2, 3, 128, 1, 2, 3, 255)),
        ], color_type=6))
        result = self._run(path, "0", "0", "--width", "3", "--height", "2",
                           "--histogram", "--alpha", "--top-colors", "1",
                           "--color-bounds", "--json")
        self._assert_success(result)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["colors"], [{
            "rgb": [1, 2, 3], "hex": "#010203", "count": 2, "alpha": 0,
            "bounds": {"x": 0, "y": 0, "width": 1, "height": 2},
        }])
        self.assertEqual((payload["total_colors"], payload["omitted_pixels"]), (3, 4))

    def test_bounds_traversal_is_optional_and_uses_single_decode(self):
        _, data = rgb_image(2, 2, lambda _x, _y: (1, 2, 3))
        path = self._write(self._tmp_dir(), "small.png", data)
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read, \
             mock.patch.object(sample_report_histogram, "positioned_region_pixels",
                               wraps=sample_report_histogram.positioned_region_pixels) as positioned:
            plain = self._run(path, "0", "0", "--width", "2", "--height", "2", "--histogram")
            bounded = self._run(path, "0", "0", "--width", "2", "--height", "2",
                                "--histogram", "--color-bounds")
        self._assert_success(plain)
        self._assert_success(bounded)
        self.assertEqual(positioned.call_count, 1)
        self.assertEqual(read.call_count, 2)

    def test_misuse_rejected_before_reads_and_script_help_and_json_work(self):
        path = "not-read.png"
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
             mock.patch.object(sample, "read_png", side_effect=AssertionError("decode")):
            for mode in ((), ("--runs",), ("--find-color", "010203")):
                result = self._run(path, "0", "0", "--color-bounds", *mode)
                self._assert_usage_error(result, "requires --histogram")
                self.assertEqual(result.stdout, "")

        _, data = rgb_image(1, 1, lambda _x, _y: (3, 4, 5))
        image = self._write(self._tmp_dir(), "script.png", data)
        script = self._run_script(image, "0", "0", "--histogram", "--color-bounds", "--json")
        self._assert_success(script)
        self.assertEqual(json.loads(script.stdout)["colors"][0]["bounds"],
                         {"x": 0, "y": 0, "width": 1, "height": 1})
        help_result = self._run_script("--help")
        self.assertIn("--color-bounds", help_result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
