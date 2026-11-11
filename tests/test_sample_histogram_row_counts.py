"""Tests for per-row distinct-color counts in the reference histogram."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample
from tools import sample_report_histogram

_PALETTE = {"A": (1, 1, 1), "B": (4, 5, 6), "C": (7, 8, 9)}
_RGB_ROWS = ("AAAA", "ABBA", "ABCC")
_EXPECTED_COLORS = [
    {"rgb": [1, 1, 1], "hex": "#010101", "count": 7},
    {"rgb": [4, 5, 6], "hex": "#040506", "count": 3},
    {"rgb": [7, 8, 9], "hex": "#070809", "count": 2},
]


def _rows_image():
    """Return the 4x3 RGB image whose palette-mapped rows the counts come from."""
    return rgb_image(4, 3, lambda x, y: _PALETTE[_RGB_ROWS[y][x]])


class TestSampleHistogramRowCounts(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_json_row_counts_cover_the_full_region_without_changing_the_palette(self):
        _, data = _rows_image()
        path = self._write(self._tmp_dir(), "rows.png", data)
        counts = self._run(path, "0", "0", "--width", "4", "--height", "3",
                           "--histogram", "--row-color-counts", "--json")
        self._assert_success(counts)
        payload = json.loads(counts.stdout)
        self.assertEqual(payload["colors"], _EXPECTED_COLORS)
        self.assertEqual(payload["row_color_counts"], [1, 2, 3])
        self.assertNotIn("column_color_counts", payload)
        plain = self._run(path, "0", "0", "--width", "4", "--height", "3",
                          "--histogram", "--json")
        self._assert_success(plain)
        self.assertEqual(json.loads(plain.stdout)["colors"], _EXPECTED_COLORS)
        self.assertNotIn("row_color_counts", json.loads(plain.stdout))

    def test_text_row_counts_follow_the_color_list_once(self):
        _, data = _rows_image()
        path = self._write(self._tmp_dir(), "rows.png", data)
        counts = self._run(path, "0", "0", "--width", "4", "--height", "3",
                           "--histogram", "--row-color-counts")
        self._assert_success(counts)
        self.assertEqual(counts.stdout.count("row color counts:"), 1)
        lines = counts.stdout.splitlines()
        self.assertEqual(lines[-1], "row color counts: [1,2,3]")
        self.assertIn("1,1,1  #010101  count=7", lines[2])

    def test_palette_filters_leave_track_lists_at_full_region_values(self):
        _, data = _rows_image()
        path = self._write(self._tmp_dir(), "rows.png", data)
        cases = (
            (("--top-colors", "1"), [_EXPECTED_COLORS[0]], 3, 5),
            (("--exclude-color", "010101"), _EXPECTED_COLORS[1:], 3, 7),
            (("--include-color", "010203"), [], 3, 12),
            (("--min-color-count", "6"), [_EXPECTED_COLORS[0]], 3, 5),
            (("--min-color-count", "10"), [], 3, 12),
            (("--max-color-count", "2"), [_EXPECTED_COLORS[2]], 3, 10),
            (("--min-color-fraction", "0.5"), [_EXPECTED_COLORS[0]], 3, 5),
            (("--max-color-fraction", "0.2"), [_EXPECTED_COLORS[2]], 3, 10),
        )
        for options, colors, total, omitted in cases:
            with self.subTest(options=options):
                result = self._run(path, "0", "0", "--width", "4", "--height", "3",
                                   "--histogram", "--row-color-counts", "--json", *options)
                self._assert_success(result)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["colors"], colors)
                self.assertEqual(payload["row_color_counts"], [1, 2, 3])
                self.assertEqual((payload["total_colors"], payload["omitted_pixels"]),
                                 (total, omitted))

    def test_shapes_of_one_row_wide_column_and_single_pixel_regions(self):
        _, data = _rows_image()
        path = self._write(self._tmp_dir(), "rows.png", data)
        single_row = self._run(path, "0", "1", "--width", "4", "--height", "1",
                               "--histogram", "--row-color-counts",
                               "--column-color-counts", "--json")
        self._assert_success(single_row)
        payload = json.loads(single_row.stdout)
        self.assertEqual(payload["row_color_counts"], [2])
        self.assertEqual(payload["column_color_counts"], [1, 1, 1, 1])
        single_pixel = self._run(path, "2", "0", "--histogram", "--row-color-counts",
                                 "--column-color-counts", "--json")
        self._assert_success(single_pixel)
        self.assertEqual(json.loads(single_pixel.stdout)["row_color_counts"], [1])
        self.assertEqual(json.loads(single_pixel.stdout)["column_color_counts"], [1])

    def test_alpha_grouping_counts_opacity_variants_and_stores_transparent_rgb(self):
        path = self._write(self._tmp_dir(), "rgba.png", make_png(4, 1, [
            bytes((1, 2, 3, 10, 1, 2, 3, 255, 1, 2, 3, 0, 4, 5, 6, 255)),
        ], color_type=6))
        alpha = self._run(path, "0", "0", "--width", "4", "--height", "1",
                          "--histogram", "--alpha", "--row-color-counts", "--json")
        self._assert_success(alpha)
        self.assertEqual(json.loads(alpha.stdout)["row_color_counts"], [4])
        self.assertEqual(len(json.loads(alpha.stdout)["colors"]), 4)
        plain = self._run(path, "0", "0", "--width", "4", "--height", "1",
                          "--histogram", "--row-color-counts", "--json")
        self._assert_success(plain)
        self.assertEqual(json.loads(plain.stdout)["row_color_counts"], [2])
        self.assertEqual(len(json.loads(plain.stdout)["colors"]), 2)

    def test_omitting_the_flags_skips_the_collection_pass_and_output(self):
        _, data = _rows_image()
        path = self._write(self._tmp_dir(), "rows.png", data)
        with mock.patch.object(sample_report_histogram, "_scanline_color_counts",
                               return_value=(None, None)) as scan:
            json_run = self._run(path, "0", "0", "--width", "4", "--height", "3",
                                 "--histogram", "--json")
            text_run = self._run(path, "0", "0", "--width", "4", "--height", "3",
                                 "--histogram")
            self._assert_success(json_run)
            self._assert_success(text_run)
        scan.assert_not_called()
        payload = json.loads(json_run.stdout)
        self.assertNotIn("row_color_counts", payload)
        self.assertNotIn("column_color_counts", payload)
        self.assertNotIn("color counts:", text_run.stdout)

    def test_misuse_rejection_script_entry_and_help(self):
        path = "not-read.png"
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
             mock.patch.object(sample, "read_png", side_effect=AssertionError("decode")):
            for flag in ("--row-color-counts", "--column-color-counts"):
                result = self._run(path, "0", "0", flag)
                self._assert_usage_error(result, f"{flag} requires --histogram")
                self.assertEqual(result.stdout, "")

        _, data = _rows_image()
        image = self._write(self._tmp_dir(), "script.png", data)
        direct = self._run(image, "0", "0", "--width", "4", "--height", "3",
                           "--histogram", "--row-color-counts", "--json")
        script = self._run_script(image, "0", "0", "--width", "4", "--height", "3",
                                  "--histogram", "--row-color-counts", "--json")
        self._assert_success(direct)
        self.assertEqual((script.stdout, script.returncode), (direct.stdout, 0))
        help_result = self._run_script("--help")
        self.assertIn("--row-color-counts", help_result.stdout)
        self.assertIn("--column-color-counts", help_result.stdout)


if __name__ == "__main__":
    import unittest

    unittest.main()
