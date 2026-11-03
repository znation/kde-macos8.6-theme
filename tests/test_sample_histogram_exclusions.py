"""Explicit RGB exclusions for reference color histograms."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from support.png_fixtures import make_png
from tools import sample


class TestSampleHistogramExclusions(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _image(self):
        colors = ((9, 9, 9), (1, 0, 0), (9, 9, 9), (0, 1, 0),
                  (1, 0, 0), (0, 1, 0), (2, 0, 0), (9, 9, 9))
        _, data = rgb_image(10, 1, lambda x, y: (200, 0, 0) if x in (0, 9) else colors[x - 1])
        return self._write(self._tmp_dir(), "exclude.png", data)

    def test_exclusion_precedes_top_colors_and_combines_with_filters(self):
        path = self._image()
        base = (path, "1", "0", "--width", "8", "--histogram", "--json")
        result = self._run(*base, "--exclude-color", "#090909", "--exclude-color", "090909",
                           "--top-colors", "1", "--color-fractions", "--color-bounds")
        self._assert_success(result)
        payload = json.loads(result.stdout)
        self.assertEqual([(c["rgb"], c["count"]) for c in payload["colors"]], [([0, 1, 0], 2)])
        self.assertEqual((payload["total_colors"], payload["omitted_pixels"]), (4, 6))
        self.assertEqual(payload["colors"][0]["fraction"], 2 / 8)
        combined = self._run(*base, "--exclude-color", "090909", "--min-color-count", "2",
                             "--min-color-fraction", "0.25")
        self._assert_success(combined)
        self.assertEqual([c["rgb"] for c in json.loads(combined.stdout)["colors"]], [[0, 1, 0], [1, 0, 0]])

    def test_empty_and_absent_exclusions_keep_original_totals(self):
        path = self._image()
        base = (path, "1", "0", "--width", "8", "--histogram", "--json")
        absent = self._run(*base, "--exclude-color", "#abcdef")
        self._assert_success(absent)
        self.assertEqual(json.loads(absent.stdout)["omitted_pixels"], 0)
        empty = self._run(*base, "--exclude-color", "090909", "--exclude-color", "010000",
                          "--exclude-color", "000100", "--exclude-color", "020000")
        self._assert_success(empty)
        payload = json.loads(empty.stdout)
        self.assertEqual(payload["colors"], [])
        self.assertEqual((payload["total_colors"], payload["omitted_pixels"]), (4, 8))

    def test_alpha_excludes_all_opacity_variants_and_preserves_key_total(self):
        data = make_png(3, 1, [bytes((1, 2, 3, 0, 1, 2, 3, 128, 4, 5, 6, 255))], color_type=6)
        path = self._write(self._tmp_dir(), "rgba.png", data)
        result = self._run(path, "0", "0", "--width", "3", "--histogram", "--alpha",
                           "--exclude-color", "010203", "--json")
        self._assert_success(result)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["total_colors"], 3)
        self.assertEqual(payload["omitted_pixels"], 2)
        self.assertEqual(payload["colors"][0]["alpha"], 255)

    def test_invalid_values_and_modes_are_rejected_before_image_access(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
             mock.patch.object(sample, "read_png", side_effect=AssertionError("decode")):
            for value in ("12345", "gggggg"):
                result = self._run("missing.png", "0", "0", "--histogram", "--exclude-color", value)
                self._assert_usage_error(result)
                self.assertEqual(result.stdout, "")
            for mode in ((), ("--runs",), ("--find-color", "010203")):
                result = self._run("missing.png", "0", "0", "--exclude-color", "010203", *mode)
                self._assert_usage_error(result, "requires --histogram")
                self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    import unittest

    unittest.main()
