"""Minimum-frequency filtering for reference color histograms."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image, solid_rgb
from tools import sample


class TestSampleHistogramMinimumCount(CliTestCase):
    """The histogram's ``--min-color-count`` filter against the other palette filters."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _image(self):
        # Crop has counts 3, 2, 2, 1; surrounding pixels are excluded.
        colors = ((0, 0, 1), (0, 0, 1), (0, 0, 1), (1, 0, 0),
                  (0, 1, 0), (1, 0, 0), (0, 1, 0), (2, 0, 0))
        _, data = rgb_image(10, 1, lambda x, y: (200, x, 0) if x in (0, 9) else colors[x - 1])
        return self._write(self._tmp_dir(), "minimum.png", data)

    def test_filtering_and_composition(self):
        path = self._image()
        base = (path, "1", "0", "--width", "8", "--histogram")
        result = self._run(*base, "--min-color-count", "2", "--json")
        self._assert_success(result)
        payload = json.loads(result.stdout)
        self.assertEqual([(c["rgb"], c["count"]) for c in payload["colors"]],
                         [([0, 0, 1], 3), ([0, 1, 0], 2), ([1, 0, 0], 2)])
        self.assertEqual((payload["total_colors"], payload["omitted_pixels"]), (4, 1))
        self.assertEqual(payload["colors"][0]["count"] / 8, 3 / 8)

        limited = self._run(*base, "--min-color-count", "2", "--top-colors", "1", "--json")
        self._assert_success(limited)
        data = json.loads(limited.stdout)
        self.assertEqual([(c["rgb"], c["count"]) for c in data["colors"]], [([0, 0, 1], 3)])
        self.assertEqual((data["total_colors"], data["omitted_pixels"]), (4, 5))

        all_colors = self._run(*base, "--min-color-count", "1", "--json")
        self._assert_success(all_colors)
        self.assertEqual(json.loads(all_colors.stdout)["omitted_pixels"], 0)
        none = self._run(*base, "--min-color-count", "9", "--json")
        self._assert_success(none)
        self.assertEqual(json.loads(none.stdout)["colors"], [])
        self.assertEqual(json.loads(none.stdout)["omitted_pixels"], 8)

    def test_spatial_diagnostics_apply_after_filtering_and_direct_script_matches(self):
        path = self._image()
        args = (path, "1", "0", "--width", "8", "--histogram", "--min-color-count", "3",
                "--color-bounds", "--color-positions", "--color-centroids", "--color-fractions", "--json")
        result = self._run(*args)
        direct = self._run_script(*args)
        self._assert_success(result)
        self._assert_success(direct)
        payload = json.loads(result.stdout)
        self.assertEqual(payload, json.loads(direct.stdout))
        self.assertEqual(payload["colors"][0]["bounds"], {"x": 1, "y": 0, "width": 3, "height": 1})
        self.assertEqual(payload["colors"][0]["position"], {"x": 1, "y": 0})
        self.assertEqual(payload["colors"][0]["centroid"], {"x": 2.0, "y": 0.0})
        self.assertEqual(payload["colors"][0]["fraction"], 3 / 8)

    def test_alpha_grouping_separation_and_opaque_fallback_honor_the_cutoff(self):
        # Crop pixels: (1,2,3) at alpha 0 and twice at alpha 128, plus (7,8,9) at alpha 128.
        rows = [bytes((9, 9, 9, 255, 1, 2, 3, 0, 7, 8, 9, 128)),
                bytes((8, 8, 8, 255, 1, 2, 3, 128, 1, 2, 3, 128))]
        path = self._write(self._tmp_dir(), "rgba-min.png", make_png(3, 2, rows, color_type=6))
        crop = (path, "1", "0", "--width", "2", "--height", "2", "--histogram")
        grouped = self._run(*crop, "--min-color-count", "3", "--json")
        self._assert_success(grouped)
        payload = json.loads(grouped.stdout)
        self.assertEqual([(c["rgb"], c["count"]) for c in payload["colors"]],
                         [([1, 2, 3], 3)])
        self.assertEqual((payload["total_colors"], payload["omitted_pixels"]), (2, 1))
        separated = self._run(*crop, "--alpha", "--min-color-count", "2", "--json")
        self._assert_success(separated)
        payload = json.loads(separated.stdout)
        self.assertEqual(payload["colors"],
                         [{"rgb": [1, 2, 3], "hex": "#010203", "count": 2, "alpha": 128}])
        self.assertEqual((payload["total_colors"], payload["omitted_pixels"]), (3, 2))
        _, opaque = solid_rgb(1, 1, (4, 5, 6))
        opaque_path = self._write(self._tmp_dir(), "opaque-min.png", opaque)
        fallback = self._run(opaque_path, "0", "0", "--histogram", "--alpha",
                             "--min-color-count", "1", "--json")
        self._assert_success(fallback)
        self.assertEqual(json.loads(fallback.stdout)["colors"],
                         [{"rgb": [4, 5, 6], "hex": "#040506", "count": 1, "alpha": 255}])

    def test_invalid_values_and_modes_are_rejected_before_image_access(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
             mock.patch.object(sample, "read_png", side_effect=AssertionError("decode")):
            for value in ("0", "-1", "1.5", "١"):
                result = self._run("missing.png", "0", "0", "--histogram", "--min-color-count", value)
                self._assert_usage_error(result)
                self.assertEqual(result.stdout, "")
            missing = self._run("missing.png", "0", "0", "--histogram", "--min-color-count")
            self._assert_usage_error(missing)
            self.assertEqual(missing.stdout, "")
            for mode in ((), ("--runs",), ("--find-color", "010203")):
                invalid = self._run("missing.png", "0", "0", "--min-color-count", "1", *mode)
                self._assert_usage_error(invalid, "requires --histogram")
                self.assertEqual(invalid.stdout, "")


if __name__ == "__main__":
    import unittest

    unittest.main()

