"""Maximum region-share filtering for reference color histograms."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample
from tools.sample_arguments import build_parser


class TestSampleHistogramMaximumFraction(CliTestCase):
    """The histogram's ``--max-color-fraction`` filter against the other palette filters."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _fixture(self):
        pixels = (((1, 0, 0),) * 3 + ((0, 1, 0),) * 2 +
                  ((0, 0, 1),) * 2 + ((2, 2, 2),))
        _, data = rgb_image(6, 4, lambda x, y: pixels[(y - 1) * 4 + x - 1]
                            if 1 <= x <= 4 and 1 <= y <= 2 else (99, 99, 99))
        return self._write(self._tmp_dir(), "maximum-fraction.png", data)

    def test_cutoff_totals_top_colors_and_text(self):
        path = self._fixture()
        base = (path, "1", "1", "--width", "4", "--height", "2", "--histogram")
        result = self._run(*base, "--max-color-fraction", "0.25", "--color-fractions", "--json")
        data = json.loads(result.stdout)
        self.assertEqual([(c["rgb"], c["count"], c["fraction"]) for c in data["colors"]],
                         [([0, 0, 1], 2, 0.25), ([0, 1, 0], 2, 0.25), ([2, 2, 2], 1, 0.125)])
        self.assertEqual((data["total_colors"], data["omitted_pixels"]), (4, 3))
        limited = json.loads(self._run(*base, "--max-color-fraction", "0.25",
                                        "--top-colors", "1", "--json").stdout)
        self.assertEqual(limited["colors"][0]["rgb"], [0, 0, 1])
        self.assertEqual(limited["omitted_pixels"], 6)
        text = self._run(*base, "--max-color-fraction", "0.25")
        self.assertIn("total colors: 4", text.stdout)
        self.assertIn("omitted pixels: 3", text.stdout)

    def test_fraction_intersections_extremes_and_proportional_crop(self):
        path = self._fixture()
        base = (path, "1", "1", "--width", "4", "--height", "2", "--histogram")
        combined = json.loads(self._run(*base, "--min-color-fraction", "0.25",
                                        "--max-color-fraction", "0.25", "--json").stdout)
        self.assertEqual([c["count"] for c in combined["colors"]], [2, 2])
        empty = json.loads(self._run(*base, "--min-color-fraction", "0.5",
                                     "--max-color-fraction", "1", "--json").stdout)
        self.assertEqual(empty["colors"], [])
        self.assertEqual((empty["total_colors"], empty["omitted_pixels"]), (4, 8))
        zero = json.loads(self._run(*base, "--max-color-fraction", "0", "--json").stdout)
        self.assertEqual((zero["colors"], zero["omitted_pixels"]), ([], 8))
        one = json.loads(self._run(*base, "--max-color-fraction", "1", "--json").stdout)
        self.assertEqual((len(one["colors"]), one["total_colors"], one["omitted_pixels"]), (4, 4, 0))

        small = self._write(self._tmp_dir(), "small.png", rgb_image(4, 1,
            lambda x, y: ((1, 0, 0) if x < 2 else (0, 1, 0)))[1])
        large = self._write(self._tmp_dir(), "large.png", rgb_image(8, 1,
            lambda x, y: ((1, 0, 0) if x < 4 else (0, 1, 0)))[1])
        args = ("0", "0", "--histogram", "--max-color-fraction", "0.5", "--json")
        a = json.loads(self._run(small, *args, "--width", "4").stdout)
        b = json.loads(self._run(large, *args, "--width", "8").stdout)
        self.assertEqual([c["rgb"] for c in a["colors"]], [c["rgb"] for c in b["colors"]])

    def test_alpha_exclusions_spatial_fields_and_rgb_mode(self):
        path = self._write(self._tmp_dir(), "alpha.png", make_png(4, 1,
            [bytes((1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 255, 9, 9, 9, 255))], color_type=6))
        rgba = json.loads(self._run(path, "0", "0", "--width", "4", "--histogram", "--alpha",
                                    "--max-color-fraction", "0.25", "--color-positions",
                                    "--color-bounds", "--color-centroids", "--json").stdout)
        self.assertEqual([(c["rgb"], c["alpha"], c["count"]) for c in rgba["colors"]],
                         [([1, 2, 3], 255, 1), ([9, 9, 9], 255, 1)])
        self.assertEqual(rgba["colors"][0]["position"], {"x": 2, "y": 0})
        self.assertEqual(rgba["colors"][0]["bounds"], {"x": 2, "y": 0, "width": 1, "height": 1})
        self.assertEqual(rgba["colors"][0]["centroid"], {"x": 2.0, "y": 0.0})
        rgb = json.loads(self._run(path, "0", "0", "--width", "4", "--histogram",
                                   "--max-color-fraction", "0.25", "--json").stdout)
        self.assertEqual(rgb["colors"], [{"rgb": [9, 9, 9], "hex": "#090909", "count": 1}])
        excluded = json.loads(self._run(path, "0", "0", "--width", "4", "--histogram",
                                        "--alpha", "--max-color-fraction", "0.25",
                                        "--exclude-color", "090909", "--json").stdout)
        self.assertEqual([c["rgb"] for c in excluded["colors"]], [[1, 2, 3]])
        limited = json.loads(self._run(path, "0", "0", "--width", "4", "--histogram",
                                       "--max-color-fraction", "0.5", "--min-color-count", "2",
                                       "--max-color-count", "2", "--json").stdout)
        self.assertEqual(limited["colors"], [])
        self.assertEqual(limited["omitted_pixels"], 4)
        opaque = self._write(self._tmp_dir(), "opaque.png", rgb_image(1, 1,
            lambda x, y: (4, 5, 6))[1])
        fallback = json.loads(self._run(opaque, "0", "0", "--histogram", "--alpha",
                                        "--max-color-fraction", "1", "--json").stdout)
        self.assertEqual(fallback["colors"][0]["alpha"], 255)
        self.assertIsNone(build_parser().parse_args(("x", "0", "0")).max_color_fraction)

    def test_invalid_values_and_modes_fail_before_reads_and_script_matches(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
                mock.patch.object(sample, "read_png", side_effect=AssertionError("decode")):
            for value in ("-0.1", "1.01", "nan", "inf", "1_0", " 0.5", "١", "x"):
                result = self._run("missing.png", "0", "0", "--histogram",
                                   "--max-color-fraction", value)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
            missing = self._run("missing.png", "0", "0", "--histogram", "--max-color-fraction")
            self.assertEqual(missing.returncode, 2)
            for mode in ((), ("--runs",), ("--find-color", "010203")):
                result = self._run("missing.png", "0", "0", "--max-color-fraction", "0", *mode)
                self.assertEqual(result.returncode, 2)
                self.assertIn("--max-color-fraction requires --histogram", result.stderr)
        path = self._fixture()
        args = (path, "1", "1", "--width", "4", "--height", "2", "--histogram",
                "--max-color-fraction", "2.5e-1", "--json")
        self.assertEqual(json.loads(self._run(*args).stdout), json.loads(self._run_script(*args).stdout))


if __name__ == "__main__":
    import unittest

    unittest.main()
