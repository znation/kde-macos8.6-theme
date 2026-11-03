"""Tests for cumulative displayed-palette coverage in reference histograms."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image, solid_rgb
from tools import sample
from tools.sample_arguments import build_parser


class TestSampleHistogramCumulativeFractions(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _page_fixture(self):
        # The selected 4x2 crop holds ordered color counts 3, 2, 2 and 1:
        # (10,0,0) three times, then the two count-2 colors in ascending
        # tuple order, then (10,10,0) once. Surrounding pixels have an
        # unrelated color they must not contribute.
        grid = (((10, 0, 0), (10, 0, 0), (0, 0, 10), (0, 10, 0), (9, 9, 9), (9, 9, 9)),
                ((10, 0, 0), (0, 0, 10), (0, 10, 0), (10, 10, 0), (9, 9, 9), (9, 9, 9)))
        _, data = rgb_image(6, 2, lambda x, y: grid[y][x])
        return self._write(self._tmp_dir(), "cumulative.png", data)

    _BASE = ("0", "0", "--width", "4", "--height", "2", "--histogram", "--json")

    def test_full_page_top_colors_offset_and_exclusion(self):
        path = self._page_fixture()
        args = (path,) + self._BASE
        result = self._run(*args, "--color-cumulative-fractions")
        self._assert_success(result)
        payload = json.loads(result.stdout)
        self.assertEqual([(color["count"], color["cumulative_fraction"]) for color in payload["colors"]],
                         [(3, 0.375), (2, 0.625), (2, 0.875), (1, 1.0)])
        self.assertNotIn("fraction", payload["colors"][0])

        top = json.loads(self._run(*args, "--top-colors", "2", "--color-cumulative-fractions").stdout)
        self.assertEqual([(c["rgb"], c["count"], c["cumulative_fraction"]) for c in top["colors"]],
                         [([10, 0, 0], 3, 0.375), ([0, 0, 10], 2, 0.625)])
        self.assertEqual((top["total_colors"], top["omitted_pixels"]), (4, 3))
        paged = json.loads(self._run(*args, "--top-colors", "2", "--color-offset", "1",
                                     "--color-cumulative-fractions").stdout)
        self.assertEqual([(c["rgb"], c["count"], c["cumulative_fraction"]) for c in paged["colors"]],
                         [([0, 0, 10], 2, 0.25), ([0, 10, 0], 2, 0.5)])
        self.assertEqual((paged["color_offset"], paged["total_colors"], paged["omitted_pixels"]), (1, 4, 4))
        excluded = json.loads(self._run(*args, "--exclude-color", "0a0000",
                                        "--color-cumulative-fractions").stdout)
        self.assertEqual([(c["rgb"], c["count"], c["cumulative_fraction"]) for c in excluded["colors"]],
                         [([0, 0, 10], 2, 0.25), ([0, 10, 0], 2, 0.5), ([10, 10, 0], 1, 0.625)])
        capped = json.loads(self._run(*args, "--max-color-count", "2",
                                      "--color-cumulative-fractions").stdout)
        self.assertEqual([c["cumulative_fraction"] for c in capped["colors"]],
                         [0.25, 0.5, 0.625])
        empty = json.loads(self._run(*args, "--min-color-count", "9",
                                     "--color-cumulative-fractions").stdout)
        self.assertEqual(empty["colors"], [])

    def test_text_orders_cumulative_after_fraction_and_before_position(self):
        path = self._write(self._tmp_dir(), "text.png", make_png(
            3, 2,
            [bytes((1, 2, 3, 0, 1, 2, 3, 255, 1, 2, 3, 0)),
             bytes((9, 8, 7, 255, 1, 2, 3, 255, 9, 8, 7, 255))],
            color_type=6))
        result = self._run(path, "1", "0", "--width", "2", "--height", "2", "--histogram",
                           "--alpha", "--color-fractions", "--color-cumulative-fractions",
                           "--color-positions")
        self._assert_success(result)
        self.assertEqual(result.stdout.splitlines(), [
            f"image: {path}  3x2",
            "region (1, 0) 2x2:",
            "1,2,3  #010203  count=2  alpha=255  fraction=0.5  cumulative_fraction=0.5  position=1,0",
            "1,2,3  #010203  count=1  alpha=0  fraction=0.25  cumulative_fraction=0.75  position=2,0",
            "9,8,7  #090807  count=1  alpha=255  fraction=0.25  cumulative_fraction=1.0  position=2,1",
        ])

    def test_integer_prefix_reaches_exactly_one_and_single_color(self):
        _, data = rgb_image(3, 1, lambda x, y: (5 + x, 0, 0))
        path = self._write(self._tmp_dir(), "thirds.png", data)
        result = self._run(path, "0", "0", "--width", "3", "--height", "1", "--histogram",
                           "--color-cumulative-fractions", "--json")
        self._assert_success(result)
        self.assertEqual([c["cumulative_fraction"] for c in json.loads(result.stdout)["colors"]],
                         [1 / 3, 2 / 3, 1.0])
        _, opaque = solid_rgb(2, 1, (4, 5, 6))
        solid_path = self._write(self._tmp_dir(), "opaque.png", opaque)
        solid = self._run(solid_path, "0", "0", "--width", "2", "--height", "1", "--histogram",
                          "--alpha", "--color-cumulative-fractions", "--json")
        self._assert_success(solid)
        self.assertEqual(json.loads(solid.stdout)["colors"], [
            {"rgb": [4, 5, 6], "hex": "#040506", "count": 2, "alpha": 255, "cumulative_fraction": 1.0}
        ])

    def test_rgba_grouping_matches_existing_counts_and_order(self):
        rgba = self._write(self._tmp_dir(), "rgba.png", make_png(
            3, 1, [bytes((1, 2, 3, 0, 1, 2, 3, 255, 9, 9, 9, 255))], color_type=6))
        revenge = self._run(rgba, "0", "0", "--width", "3", "--height", "1", "--histogram",
                            "--alpha", "--color-cumulative-fractions", "--json")
        self._assert_success(revenge)
        self.assertEqual([(c["count"], c["cumulative_fraction"], c.get("alpha"))
                          for c in json.loads(revenge.stdout)["colors"]],
                         [(1, 1 / 3, 0), (1, 2 / 3, 255), (1, 1.0, 255)])
        merged = self._run(rgba, "0", "0", "--width", "3", "--height", "1", "--histogram",
                           "--color-cumulative-fractions", "--json")
        self._assert_success(merged)
        self.assertEqual([(c["rgb"], c["count"], c["cumulative_fraction"]) for c in json.loads(merged.stdout)["colors"]],
                         [([1, 2, 3], 2, 2 / 3), ([9, 9, 9], 1, 1.0)])

    def test_flag_off_omits_fields_and_spatial_combinations_stay_independent(self):
        path = self._page_fixture()
        args = (path,) + self._BASE
        plain = self._run(*args)
        self._assert_success(plain)
        self.assertNotIn("cumulative_fraction", json.loads(plain.stdout).get("colors", [])[0])
        alone = self._run(*args, "--color-cumulative-fractions")
        self._assert_success(alone)
        alone_payload = json.loads(alone.stdout)
        self.assertNotIn("fraction", alone_payload["colors"][0])
        self.assertNotIn("total_colors", alone_payload)
        self.assertNotIn("omitted_pixels", alone_payload)
        text = self._run(path, "0", "0", "--width", "4", "--height", "2", "--histogram",
                         "--color-cumulative-fractions")
        self._assert_success(text)
        self.assertEqual([line for line in text.stdout.splitlines()
                          if line.startswith("cumulative")], [])
        self.assertEqual(sum(line.count("cumulative_fraction=0.375") for line in text.stdout.splitlines()), 1)
        self.assertEqual(sum(line.count("cumulative_fraction=0.625") for line in text.stdout.splitlines()), 1)
        self.assertEqual(sum(line.count("cumulative_fraction=0.875") for line in text.stdout.splitlines()), 1)
        self.assertEqual(sum(line.count("cumulative_fraction=1.0") for line in text.stdout.splitlines()), 1)
        spatial = json.loads(self._run(*args, "--color-cumulative-fractions",
                                       "--color-bounds", "--json").stdout)
        self.assertTrue(all(set(color) >= {"cumulative_fraction", "bounds"}
                            for color in spatial["colors"]))

    def test_requires_histogram_before_image_reads_and_scripts_agree(self):
        path = self._page_fixture()
        for mode in ((), ("--runs",), ("--find-color", "010203")):
            with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
                 mock.patch.object(sample, "read_png", side_effect=AssertionError("decode")):
                result = self._run(path, "0", "0", "--color-cumulative-fractions", *mode)
            self._assert_usage_error(result, "--color-cumulative-fractions requires --histogram")
            self.assertEqual(result.stdout, "")
        with mock.patch.object(sample, "read_png_size") as size, \
                mock.patch.object(sample, "read_png") as read, \
                mock.patch.object(sample.os, "open") as open_image:
            result = self._run(path, "0", "0", "--color-cumulative-fractions", "--find-color", "010203")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        size.assert_not_called()
        read.assert_not_called()
        open_image.assert_not_called()
        args = (path, "0", "0", "--width", "4", "--height", "2", "--histogram",
                "--color-cumulative-fractions", "--json")
        packaged = self._run(*args)
        self._assert_success(packaged)
        direct = self._run_script(*args)
        self._assert_success(direct)
        self.assertEqual(json.loads(packaged.stdout), json.loads(direct.stdout))

    def test_parser_default_and_option_help(self):
        args = build_parser().parse_args(("image.png", "0", "0"))
        self.assertIs(args.color_cumulative_fractions, False)
        self.assertIn("--color-cumulative-fractions", build_parser().format_help())


if __name__ == "__main__":
    import unittest

    unittest.main()
