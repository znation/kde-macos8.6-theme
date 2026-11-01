"""Tests for reference-pixel region color counts."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import control_named_png, rgb_image, solid_rgb
from support.symlink_fixtures import symlinked_repo
from tools import sample


class TestSampleHistogram(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _fixture(self):
        # Outside the selected rectangle, colors are unique and must not count.
        _, data = rgb_image(5, 3, lambda x, y: (
            (250, x, y) if x == 0 or y == 2 else
            ((1, 2, 3), (1, 2, 3), (0, 0, 1), (0, 0, 1))[x - 1]
        ))
        return self._write(self._tmp_dir(), "hist.png", data)

    def test_json_rectangle_counts_sorted_colors_within_bounds(self):
        path = self._fixture()
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(path, "1", "0", "--width", "4", "--height", "2", "--histogram", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout), {
            "image": path, "image_width": 5, "image_height": 3,
            "region": {"x": 1, "y": 0, "width": 4, "height": 2},
            "colors": [
                {"rgb": [0, 0, 1], "hex": "#000001", "count": 4},
                {"rgb": [1, 2, 3], "hex": "#010203", "count": 4},
            ],
        })
        self.assertEqual(sum(c["count"] for c in json.loads(result.stdout)["colors"]), 8)
        self.assertEqual(read.call_args.kwargs["max_rows"], 2)

    def test_text_output_and_single_pixel_json_schema(self):
        path = self._fixture()
        text = self._run(path, "1", "0", "--width", "4", "--height", "2", "--histogram")
        self._assert_success(text)
        self.assertEqual(text.stdout.splitlines(), [
            f"image: {path}  5x3", "region (1, 0) 4x2:",
            "0,0,1  #000001  count=4", "1,2,3  #010203  count=4",
        ])
        pixel = self._run(path, "2", "1", "--histogram", "--json")
        self._assert_success(pixel)
        self.assertEqual(json.loads(pixel.stdout), {
            "image": path, "image_width": 5, "image_height": 3,
            "region": {"x": 2, "y": 1, "width": 1, "height": 1},
            "colors": [{"rgb": [1, 2, 3], "hex": "#010203", "count": 1}],
        })

    def test_script_control_path_and_errors(self):
        with control_named_png() as path:
            result = self._run_script(path, "0", "0", "--histogram", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["image"], path)
        self.assertNotIn("\x1b", result.stdout)

        path = self._fixture()
        with mock.patch.object(sample, "read_png", side_effect=AssertionError("decoded")):
            outside = self._run(path, "4", "0", "--width", "2", "--histogram")
        self._assert_usage_error(outside, "outside the 5x3 image")
        self.assertEqual(outside.stdout, "")

        bad = self._write(self._tmp_dir(), "bad.png", b"not png")
        malformed = self._run(bad, "0", "0", "--histogram")
        self._assert_usage_error(malformed)
        self.assertEqual(malformed.stdout, "")

        _, data = solid_rgb(1, 1)
        root, link = symlinked_repo(self._tmp_dir(), "reference.png", data)
        with mock.patch.object(sample, "ROOT", str(root)):
            escaped = self._run(str(link), "0", "0", "--histogram")
        self._assert_usage_error(escaped, "resolves outside")
        self.assertEqual(escaped.stdout, "")

    def test_top_colors_reports_cutoff_ties_and_omitted_summary(self):
        path = self._fixture()
        result = self._run(
            path, "1", "0", "--width", "4", "--height", "2",
            "--histogram", "--top-colors", "1", "--json",
        )
        self._assert_success(result)
        data = json.loads(result.stdout)
        self.assertEqual(data["colors"], [
            {"rgb": [0, 0, 1], "hex": "#000001", "count": 4},
        ])
        self.assertEqual(data["total_colors"], 2)
        self.assertEqual(data["omitted_pixels"], 4)
        self.assertEqual(sum(c["count"] for c in data["colors"]) + data["omitted_pixels"], 8)

        text = self._run(
            path, "1", "0", "--width", "4", "--height", "2",
            "--histogram", "--top-colors", "1",
        )
        self._assert_success(text)
        self.assertEqual(text.stdout.splitlines()[-3:], [
            "0,0,1  #000001  count=4", "total colors: 2", "omitted pixels: 4",
        ])

    def test_top_colors_at_or_above_distinct_count_and_single_color(self):
        path = self._fixture()
        for limit in (2, 5):
            result = self._run(path, "1", "0", "--width", "4", "--height", "2",
                               "--histogram", "--top-colors", str(limit), "--json")
            self._assert_success(result)
            data = json.loads(result.stdout)
            self.assertEqual(data["total_colors"], 2)
            self.assertEqual(len(data["colors"]), 2)
            self.assertEqual(data["omitted_pixels"], 0)

        _, data = solid_rgb(2, 2, (3, 4, 5))
        single = self._write(self._tmp_dir(), "single.png", data)
        result = self._run(single, "0", "0", "--width", "2", "--height", "2",
                           "--histogram", "--top-colors", "1", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["total_colors"], 1)
        self.assertEqual(json.loads(result.stdout)["omitted_pixels"], 0)

    def test_top_colors_validation_precedes_image_reads_and_is_histogram_only(self):
        path = self._fixture()
        for value in ("0", "-1", "1.5", "١"):
            with self.subTest(value=value):
                result = self._run(path, "0", "0", "--histogram", "--top-colors", value)
                self._assert_usage_error(result)
                self.assertEqual(result.stdout, "")
        for mode in ((), ("--runs",), ("--find-color", "#000001")):
            with self.subTest(mode=mode), mock.patch.object(
                sample, "read_png_size", side_effect=AssertionError("read")
            ):
                result = self._run(path, "0", "0", "--top-colors", "1", *mode)
                self._assert_usage_error(result, "requires --histogram")
                self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    import unittest

    unittest.main()
