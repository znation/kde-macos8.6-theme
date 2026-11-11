"""Region-share filtering for reference color histograms."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample
from tools.sample_arguments import build_parser


class TestSampleHistogramMinimumFraction(CliTestCase):
    """The histogram's ``--min-color-fraction`` filter against the other palette filters."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _fixture(self):
        # Offset 3x2 crop: counts are 3, 2 and 1; exterior colors are excluded.
        pixels = ((1, 0, 0), (1, 0, 0), (1, 0, 0),
                  (0, 1, 0), (0, 1, 0), (0, 0, 1))
        _, data = rgb_image(5, 4, lambda x, y: pixels[(y - 1) * 3 + x - 1]
                            if 1 <= x <= 3 and 1 <= y <= 2 else (99, 99, 99))
        return self._write(self._tmp_dir(), "fraction.png", data)

    def test_crop_cutoff_boundaries_and_proportional_regions(self):
        path = self._fixture()
        base = (path, "1", "1", "--width", "3", "--height", "2", "--histogram")
        result = self._run(*base, "--min-color-fraction", "0.3333333333333333", "--json")
        self._assert_success(result)
        data = json.loads(result.stdout)
        self.assertEqual([(c["rgb"], c["count"]) for c in data["colors"]],
                         [([1, 0, 0], 3), ([0, 1, 0], 2)])
        self.assertEqual((data["total_colors"], data["omitted_pixels"]), (3, 1))
        below = self._run(*base, "--min-color-fraction", "0.34", "--json")
        self.assertEqual([c["count"] for c in json.loads(below.stdout)["colors"]], [3])

        half, half_data = rgb_image(4, 1,
            lambda x, y: ((1, 0, 0) if x < 2 else (0, 1, 0)))
        half = self._write(self._tmp_dir(), "half.png", half_data)
        doubled = self._write(self._tmp_dir(), "doubled.png", rgb_image(8, 1,
            lambda x, y: ((1, 0, 0) if x < 4 else (0, 1, 0)))[1])
        one = self._run(half, "0", "0", "--width", "4", "--histogram",
                        "--min-color-fraction", "0.5", "--json")
        two = self._run(doubled, "0", "0", "--width", "8", "--histogram",
                        "--min-color-fraction", "0.5", "--json")
        self.assertEqual([c["rgb"] for c in json.loads(one.stdout)["colors"]],
                         [c["rgb"] for c in json.loads(two.stdout)["colors"]])

    def test_zero_one_joint_filters_and_spatial_fields(self):
        path = self._fixture()
        base = (path, "1", "1", "--width", "3", "--height", "2", "--histogram")
        zero = self._run(*base, "--min-color-fraction", "0", "--json")
        ordinary = self._run(*base, "--json")
        self.assertEqual(json.loads(zero.stdout)["colors"], json.loads(ordinary.stdout)["colors"])
        self.assertEqual(json.loads(zero.stdout)["total_colors"], 3)
        all_pixels = self._run(path, "1", "1", "--width", "3", "--height", "2",
                               "--histogram", "--min-color-fraction", "1", "--json")
        self.assertEqual(json.loads(all_pixels.stdout)["colors"], [])
        self.assertEqual(json.loads(all_pixels.stdout)["omitted_pixels"], 6)
        combined = self._run(*base, "--min-color-count", "2", "--min-color-fraction", "0.5",
                             "--top-colors", "1", "--color-fractions", "--color-bounds",
                             "--color-positions", "--color-centroids", "--json")
        payload = json.loads(combined.stdout)
        self.assertEqual((payload["total_colors"], payload["omitted_pixels"]), (3, 3))
        self.assertEqual(payload["colors"], [{"rgb": [1, 0, 0], "hex": "#010000", "count": 3,
            "fraction": 0.5, "bounds": {"x": 1, "y": 1, "width": 3, "height": 1},
            "position": {"x": 1, "y": 1}, "centroid": {"x": 2.0, "y": 1.0}}])
        text = self._run(*base, "--min-color-fraction", "0.5")
        self.assertIn("total colors: 3", text.stdout)
        self.assertIn("omitted pixels: 3", text.stdout)

    def test_rgba_and_opaque_fallback_and_parser_default(self):
        rgba = self._write(self._tmp_dir(), "rgba.png", make_png(3, 1,
            [bytes((1, 2, 3, 0, 1, 2, 3, 255, 9, 9, 9, 255))], color_type=6))
        result = self._run(rgba, "0", "0", "--width", "2", "--histogram", "--alpha",
                           "--min-color-fraction", "0.5", "--json")
        self.assertEqual([c["alpha"] for c in json.loads(result.stdout)["colors"]], [0, 255])
        opaque, data = rgb_image(2, 1, lambda x, y: (4, 5, 6))
        opaque_path = self._write(self._tmp_dir(), "opaque.png", data)
        fallback = self._run(opaque_path, "0", "0", "--width", "2", "--histogram", "--alpha",
                             "--min-color-fraction", "1", "--json")
        self.assertEqual(json.loads(fallback.stdout)["colors"][0]["alpha"], 255)
        self.assertIsNone(build_parser().parse_args(("x", "0", "0")).min_color_fraction)

    def test_bad_values_fail_before_reads_and_direct_script_matches(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
                mock.patch.object(sample, "read_png", side_effect=AssertionError("decode")):
            for value in ("-0.1", "1.01", "nan", "inf", "1_0", " 0.5", "١", "x"):
                result = self._run("missing.png", "0", "0", "--histogram",
                                   "--min-color-fraction", value)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
            missing = self._run("missing.png", "0", "0", "--histogram", "--min-color-fraction")
            self.assertEqual(missing.returncode, 2)
        path = self._fixture()
        args = (path, "1", "1", "--width", "3", "--height", "2", "--histogram",
                "--min-color-fraction", "5e-1", "--json")
        package, direct = self._run(*args), self._run_script(*args)
        self._assert_success(package)
        self._assert_success(direct)
        self.assertEqual(json.loads(package.stdout), json.loads(direct.stdout))


if __name__ == "__main__":
    import unittest

    unittest.main()
