"""Tests for reference-pixel histogram color fractions."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image, solid_rgb
from tools import sample


class TestSampleHistogramFractions(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _rgb_fixture(self):
        # The selected 3x2 crop has counts 2, 2 and 2; surrounding pixels
        # have unrelated colors so they cannot affect the denominator.
        _, data = rgb_image(5, 3, lambda x, y: (
            (90 + x, 80 + y, 70) if x == 0 or x == 4 or y == 2 else
            ((1, 0, 0), (2, 0, 0), (3, 0, 0))[x - 1]
        ))
        return self._write(self._tmp_dir(), "fractions.png", data)

    def test_region_fractions_text_json_bounds_and_truncation(self):
        path = self._rgb_fixture()
        args = (path, "1", "0", "--width", "3", "--height", "2", "--histogram")
        with mock.patch.object(sample, "read_png", wraps=sample.read_png) as read:
            result = self._run(*args, "--color-fractions", "--color-bounds", "--json")
        self._assert_success(result)
        payload = json.loads(result.stdout)
        self.assertEqual([color["fraction"] for color in payload["colors"]], [1 / 3] * 3)
        self.assertAlmostEqual(sum(color["fraction"] for color in payload["colors"]), 1)
        self.assertEqual([color["count"] for color in payload["colors"]], [2, 2, 2])
        self.assertTrue(all("bounds" in color for color in payload["colors"]))
        read.assert_called_once_with(path, max_rows=2)

        text = self._run(*args, "--color-fractions")
        self._assert_success(text)
        self.assertTrue(all("fraction=0.3333333333333333" in line
                            for line in text.stdout.splitlines()[2:]))
        truncated = self._run(*args, "--top-colors", "1", "--color-fractions", "--json")
        self._assert_success(truncated)
        data = json.loads(truncated.stdout)
        self.assertEqual(data["colors"][0]["fraction"], 1 / 3)
        self.assertEqual(data["omitted_pixels"], 4)
        self.assertLess(sum(color["fraction"] for color in data["colors"]), 1)
        bounded = self._run(*args, "--top-colors", "3", "--color-fractions",
                            "--color-bounds", "--json")
        self._assert_success(bounded)
        self.assertTrue(all("bounds" in color and "fraction" in color
                            for color in json.loads(bounded.stdout)["colors"]))

    def test_fractions_rgb_rgba_opaque_and_single_pixel(self):
        _, opaque_png = solid_rgb(2, 1, (4, 5, 6))
        path = self._write(self._tmp_dir(), "opaque.png", opaque_png)
        result = self._run(path, "0", "0", "--width", "2", "--histogram",
                           "--color-fractions", "--alpha", "--json")
        self._assert_success(result)
        self.assertEqual(json.loads(result.stdout)["colors"], [
            {"rgb": [4, 5, 6], "hex": "#040506", "count": 2, "alpha": 255, "fraction": 1.0}
        ])
        single = self._run(path, "1", "0", "--histogram", "--color-fractions", "--json")
        self._assert_success(single)
        self.assertEqual(json.loads(single.stdout)["colors"][0]["fraction"], 1.0)

        rgba = self._write(self._tmp_dir(), "rgba.png", make_png(
            3, 1, [bytes((1, 2, 3, 0, 1, 2, 3, 255, 9, 9, 9, 255))], color_type=6))
        rgb = self._run(rgba, "0", "0", "--width", "2", "--histogram",
                        "--color-fractions", "--json")
        self._assert_success(rgb)
        self.assertEqual(json.loads(rgb.stdout)["colors"][0]["fraction"], 1.0)
        separate = self._run(rgba, "0", "0", "--width", "2", "--histogram", "--alpha",
                              "--color-fractions", "--json")
        self._assert_success(separate)
        self.assertEqual([c["fraction"] for c in json.loads(separate.stdout)["colors"]], [0.5, 0.5])

    def test_text_combines_alpha_bounds_and_fractions(self):
        path = self._write(self._tmp_dir(), "combined.png", make_png(
            3, 2,
            [bytes((1, 2, 3, 0, 1, 2, 3, 255, 1, 2, 3, 0)),
             bytes((9, 8, 7, 255, 1, 2, 3, 255, 9, 8, 7, 255))],
            color_type=6))
        result = self._run(path, "1", "0", "--width", "2", "--height", "2",
                           "--histogram", "--alpha", "--color-bounds", "--color-fractions")
        self._assert_success(result)
        self.assertEqual(result.stdout.splitlines(), [
            f"image: {path}  3x2",
            "region (1, 0) 2x2:",
            "1,2,3  #010203  count=2  alpha=255  bounds=1,0,1,2  fraction=0.5",
            "1,2,3  #010203  count=1  alpha=0  bounds=2,0,1,1  fraction=0.25",
            "9,8,7  #090807  count=1  alpha=255  bounds=2,1,1,1  fraction=0.25",
        ])

    def test_option_requires_histogram_before_image_reads_and_direct_script_works(self):
        path = self._rgb_fixture()
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
             mock.patch.object(sample, "read_png", side_effect=AssertionError("decode")):
            for mode in ((), ("--runs",), ("--find-color", "010203")):
                result = self._run(path, "0", "0", "--color-fractions", *mode)
                self._assert_usage_error(result, "requires --histogram")
                self.assertEqual(result.stdout, "")
        direct = self._run_script(path, "1", "0", "--histogram", "--color-fractions", "--json")
        self._assert_success(direct)
        self.assertAlmostEqual(sum(c["fraction"] for c in json.loads(direct.stdout)["colors"]), 1)


if __name__ == "__main__":
    import unittest

    unittest.main()
