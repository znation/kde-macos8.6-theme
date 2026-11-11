"""Maximum-frequency filtering for reference color histograms."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png, rgb_image
from tools import sample
from tools.sample_arguments import build_parser


class TestSampleHistogramMaximumCount(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _image(self):
        # Offset crop contains four RGB values with counts 3, 2, 2 and 1.
        colors = ((0, 0, 1), (0, 0, 1), (0, 0, 1), (1, 0, 0),
                  (0, 1, 0), (1, 0, 0), (0, 1, 0), (2, 0, 0))
        _, data = rgb_image(10, 1, lambda x, y: (99, 99, 99) if x in (0, 9) else colors[x - 1])
        return self._write(self._tmp_dir(), "maximum.png", data)

    def test_limit_composition_spatial_fields_and_report_forms(self):
        path = self._image()
        base = (path, "1", "0", "--width", "8", "--histogram")
        result = self._run(*base, "--max-color-count", "2", "--json")
        payload = json.loads(result.stdout)
        self.assertEqual([(c["rgb"], c["count"]) for c in payload["colors"]],
                         [([0, 1, 0], 2), ([1, 0, 0], 2), ([2, 0, 0], 1)])
        self.assertEqual((payload["total_colors"], payload["omitted_pixels"]), (4, 3))

        top = self._run(*base, "--max-color-count", "2", "--top-colors", "1",
                        "--color-fractions", "--color-positions", "--json")
        limited = json.loads(top.stdout)
        self.assertEqual(limited["colors"], [{"rgb": [0, 1, 0], "hex": "#000100", "count": 2,
            "fraction": 0.25, "position": {"x": 5, "y": 0}}])
        self.assertEqual((limited["total_colors"], limited["omitted_pixels"]), (4, 6))

        exact = self._run(*base, "--min-color-count", "2", "--max-color-count", "2", "--json")
        self.assertEqual([c["count"] for c in json.loads(exact.stdout)["colors"]], [2, 2])
        empty = self._run(*base, "--min-color-count", "4", "--max-color-count", "9", "--json")
        self.assertEqual(json.loads(empty.stdout)["colors"], [])
        self.assertEqual(json.loads(empty.stdout)["omitted_pixels"], 8)

        all_colors = self._run(*base, "--max-color-count", "8", "--json")
        self.assertEqual(json.loads(all_colors.stdout)["omitted_pixels"], 0)
        self.assertNotIn("total_colors", json.loads(self._run(*base, "--json").stdout))
        text = self._run(*base, "--max-color-count", "2")
        self.assertIn("total colors: 4", text.stdout)
        self.assertIn("omitted pixels: 3", text.stdout)

        direct = self._run_script(*base, "--max-color-count", "2", "--json")
        self.assertEqual(json.loads(direct.stdout), payload)

    def test_filters_intersect_and_alpha_counts_are_separate(self):
        path = self._image()
        base = (path, "1", "0", "--width", "8", "--histogram", "--json")
        combined = self._run(*base, "--max-color-count", "2", "--min-color-fraction", "0.25",
                             "--exclude-color", "000100")
        data = json.loads(combined.stdout)
        self.assertEqual([(c["rgb"], c["count"]) for c in data["colors"]],
                         [([1, 0, 0], 2)])
        self.assertEqual(data["omitted_pixels"], 6)

        rgba = self._write(self._tmp_dir(), "alpha.png", make_png(5, 1,
            [bytes((1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 255,
                    1, 2, 3, 255, 1, 2, 3, 255))], color_type=6))
        separate = self._run(rgba, "0", "0", "--width", "5", "--histogram", "--alpha",
                             "--max-color-count", "2", "--json")
        self.assertEqual([(c["rgb"], c["count"], c["alpha"])
                          for c in json.loads(separate.stdout)["colors"]],
                         [([1, 2, 3], 2, 0)])
        merged = self._run(rgba, "0", "0", "--width", "5", "--histogram",
                           "--max-color-count", "2", "--json")
        self.assertEqual(json.loads(merged.stdout)["colors"], [])

    def test_invalid_values_and_mode_usage_precede_png_reads(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")), \
             mock.patch.object(sample, "read_png", side_effect=AssertionError("decode")):
            for value in ("0", "-1", "1.5", "١"):
                result = self._run("missing.png", "0", "0", "--max-color-count", value)
                self.assertEqual((result.returncode, result.stdout), (2, ""))
            missing = self._run("missing.png", "0", "0", "--max-color-count")
            self.assertEqual((missing.returncode, missing.stdout), (2, ""))
            for mode in ((), ("--runs",), ("--find-color", "010203")):
                result = self._run("missing.png", "0", "0", "--max-color-count", "2", *mode)
                self.assertEqual((result.returncode, result.stdout), (2, ""))
                self.assertIn("--max-color-count requires --histogram", result.stderr)
        args = build_parser().parse_args(("image.png", "0", "0"))
        self.assertIsNone(args.max_color_count)


if __name__ == "__main__":
    import unittest

    unittest.main()
