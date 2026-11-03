"""Named RGB inclusion filters for reference color histograms."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample


class TestSampleHistogramInclusions(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _image(self):
        colors = ((0, 0, 0),) * 4 + ((255, 0, 0),) * 2 + ((0, 255, 0), (0, 0, 255))
        _, data = rgb_image(8, 1, lambda x, y: colors[x])
        return self._write(self._tmp_dir(), "include.png", data)

    def test_inclusion_precedes_filters_and_pagination(self):
        path = self._image()
        base = (path, "0", "0", "--width", "8", "--histogram", "--json")
        result = self._run(*base, "--include-color", "#ff0000", "--include-color", "00ff00",
                           "--color-fractions")
        self._assert_success(result)
        payload = json.loads(result.stdout)
        self.assertEqual([(c["rgb"], c["count"], c["fraction"]) for c in payload["colors"]],
                         [([255, 0, 0], 2, 2 / 8), ([0, 255, 0], 1, 1 / 8)])
        self.assertEqual((payload["total_colors"], payload["omitted_pixels"]), (4, 5))
        repeated = self._run(*base, "--include-color", "ff0000", "--include-color", "#FF0000")
        self._assert_success(repeated)
        self.assertEqual([(c["rgb"], c["count"]) for c in json.loads(repeated.stdout)["colors"]],
                         [([255, 0, 0], 2)])

        excluded = self._run(*base, "--include-color", "ff0000", "--include-color", "00ff00",
                             "--exclude-color", "#FF0000")
        self._assert_success(excluded)
        self.assertEqual([c["rgb"] for c in json.loads(excluded.stdout)["colors"]], [[0, 255, 0]])
        self.assertEqual(json.loads(excluded.stdout)["omitted_pixels"], 7)

        page = self._run(*base, "--include-color", "0000ff", "--include-color", "00ff00",
                         "--top-colors", "1", "--color-offset", "1")
        self._assert_success(page)
        self.assertEqual([c["rgb"] for c in json.loads(page.stdout)["colors"]], [[0, 255, 0]])
        self.assertEqual(json.loads(page.stdout)["omitted_pixels"], 7)

        filtered = self._run(*base, "--include-color", "ff0000", "--include-color", "00ff00",
                             "--min-color-count", "2", "--max-color-fraction", "0.25")
        self._assert_success(filtered)
        self.assertEqual([c["rgb"] for c in json.loads(filtered.stdout)["colors"]], [[255, 0, 0]])
        fraction_filtered = self._run(*base, "--include-color", "ff0000", "--include-color", "00ff00",
                                      "--min-color-fraction", "0.25")
        self._assert_success(fraction_filtered)
        self.assertEqual([c["rgb"] for c in json.loads(fraction_filtered.stdout)["colors"]],
                         [[255, 0, 0]])
        empty_intersection = self._run(*base, "--include-color", "ff0000",
                                       "--min-color-count", "3")
        self._assert_success(empty_intersection)
        self.assertEqual(json.loads(empty_intersection.stdout)["colors"], [])
        self.assertEqual(json.loads(empty_intersection.stdout)["omitted_pixels"], 8)

    def test_crop_spatial_fields_cover_full_emitted_color_occurrences(self):
        path = self._image()
        result = self._run(path, "2", "0", "--width", "6", "--histogram", "--json",
                           "--include-color", "000000", "--include-color", "00ff00",
                           "--color-positions", "--color-bounds", "--color-centroids")
        self._assert_success(result)
        payload = json.loads(result.stdout)
        records = {tuple(color["rgb"]): color for color in payload["colors"]}
        self.assertEqual(records[(0, 0, 0)]["position"], {"x": 2, "y": 0})
        self.assertEqual(records[(0, 0, 0)]["bounds"], {"x": 2, "y": 0, "width": 2, "height": 1})
        self.assertEqual(records[(0, 0, 0)]["centroid"], {"x": 2.5, "y": 0.0})
        self.assertEqual(records[(0, 255, 0)]["position"], {"x": 6, "y": 0})

    def test_empty_full_palette_alpha_and_text_totals(self):
        path = self._image()
        base = (path, "0", "0", "--width", "8", "--histogram")
        empty = self._run(*base, "--include-color", "abcdef", "--json")
        self._assert_success(empty)
        self.assertEqual((json.loads(empty.stdout)["colors"], json.loads(empty.stdout)["omitted_pixels"]),
                         ([], 8))
        full = self._run(*base, "--include-color", "000000", "--include-color", "ff0000",
                         "--include-color", "00ff00", "--include-color", "0000ff", "--json")
        self._assert_success(full)
        self.assertEqual((json.loads(full.stdout)["total_colors"], json.loads(full.stdout)["omitted_pixels"]),
                         (4, 0))
        text = self._run(*base, "--include-color", "#ff0000")
        self._assert_success(text)
        self.assertIn("total colors: 4\nomitted pixels: 6", text.stdout)
        json_result = self._run(*base, "--include-color", "#ff0000", "--json")
        self._assert_success(json_result)
        text_color = next(line for line in text.stdout.splitlines() if "count=" in line)
        self.assertIn(f"count={json.loads(json_result.stdout)['colors'][0]['count']}", text_color)

        rgba = make_png(3, 1, [bytes((1, 2, 3, 0, 1, 2, 3, 128, 4, 5, 6, 255))], color_type=6)
        rgba_path = self._write(self._tmp_dir(), "rgba.png", rgba)
        result = self._run(rgba_path, "0", "0", "--width", "3", "--histogram", "--alpha",
                           "--include-color", "010203", "--json")
        self._assert_success(result)
        payload = json.loads(result.stdout)
        self.assertEqual([(c["rgb"], c["alpha"], c["count"]) for c in payload["colors"]],
                         [([1, 2, 3], 0, 1), ([1, 2, 3], 128, 1)])
        self.assertEqual(payload["omitted_pixels"], 1)

    def test_invalid_values_and_modes_fail_before_image_access(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
             mock.patch.object(sample, "read_png", side_effect=AssertionError("decode")):
            for value in ("12345", "gggggg"):
                result = self._run("missing.png", "0", "0", "--histogram", "--include-color", value)
                self._assert_usage_error(result)
                self.assertEqual(result.stdout, "")
            for mode in ((), ("--runs",), ("--find-color", "010203")):
                result = self._run("missing.png", "0", "0", "--include-color", "010203", *mode)
                self._assert_usage_error(result, "requires --histogram")
                self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    import unittest

    unittest.main()
