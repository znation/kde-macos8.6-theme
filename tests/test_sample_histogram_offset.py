"""Paged selection for reference color histograms."""

from __future__ import annotations

import json
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from tools import sample
from tools.sample_arguments import build_parser


class TestSampleHistogramOffset(CliTestCase):
    """The histogram's ``--color-offset`` paging of the ranked color list."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_offset_pages_and_filtering(self):
        colors = ((0, 0, 0),) * 3 + ((0, 1, 0),) * 2 + ((1, 0, 0),) * 2 + ((2, 0, 0),)
        _, data = rgb_image(10, 1, lambda x, y: (9, 9, 9) if x in (0, 9) else colors[x - 1])
        path = self._write(self._tmp_dir(), "page.png", data)
        base = (path, "1", "0", "--width", "8", "--histogram", "--top-colors", "2", "--color-fractions", "--json")
        page = json.loads(self._run(*base, "--color-offset", "1").stdout)
        self.assertEqual([(c["rgb"], c["count"], c["fraction"]) for c in page["colors"]],
                         [([0, 1, 0], 2, 0.25), ([1, 0, 0], 2, 0.25)])
        self.assertEqual((page["color_offset"], page["total_colors"], page["omitted_pixels"]), (1, 4, 4))
        tail = json.loads(self._run(*base, "--color-offset", "3").stdout)
        self.assertEqual([(c["rgb"], c["count"]) for c in tail["colors"]], [([2, 0, 0], 1)])
        empty = json.loads(self._run(*base, "--color-offset", "999999999999999999999").stdout)
        self.assertEqual(empty["colors"], [])
        self.assertEqual(empty["omitted_pixels"], 8)
        filtered = json.loads(self._run(*base, "--exclude-color", "000000", "--color-offset", "1").stdout)
        self.assertEqual([(c["rgb"], c["count"]) for c in filtered["colors"]],
                         [([1, 0, 0], 2), ([2, 0, 0], 1)])
        text = self._run(path, "1", "0", "--width", "8", "--histogram", "--top-colors", "2", "--color-offset", "1")
        self.assertIn("color offset: 1", text.stdout)

    def test_parser_default_and_option_help(self):
        args = build_parser().parse_args(("image.png", "0", "0"))
        self.assertIsNone(args.color_offset)
        self.assertIn("--color-offset K", build_parser().format_help())

    def test_ranked_pages_filters_metadata_and_text(self):
        pixels = ((0, 0, 0),) * 3 + ((0, 1, 0),) * 2 + ((1, 0, 0),) * 2 + ((2, 0, 0),)
        path = self._write(self._tmp_dir(), "page.png", rgb_image(8, 1, lambda x, y: pixels[x])[1])
        base = (path, "0", "0", "--width", "8", "--histogram", "--top-colors", "2")
        first = json.loads(self._run(*base, "--color-offset", "1", "--color-fractions", "--json").stdout)
        self.assertEqual([c["rgb"] for c in first["colors"]], [[0, 1, 0], [1, 0, 0]])
        self.assertEqual([c["fraction"] for c in first["colors"]], [0.25, 0.25])
        self.assertEqual((first["total_colors"], first["omitted_pixels"], first["color_offset"]), (4, 4, 1))
        later = json.loads(self._run(*base, "--color-offset", "3", "--json").stdout)
        self.assertEqual([c["rgb"] for c in later["colors"]], [[2, 0, 0]])
        self.assertEqual(later["omitted_pixels"], 7)
        empty = json.loads(self._run(*base, "--color-offset", "100000", "--json").stdout)
        self.assertEqual((empty["colors"], empty["omitted_pixels"]), ([], 8))
        excluded = json.loads(self._run(*base, "--exclude-color", "000000", "--color-offset", "1", "--top-colors", "1", "--json").stdout)
        self.assertEqual(excluded["colors"][0]["rgb"], [1, 0, 0])
        text = self._run(*base, "--color-offset", "1")
        self.assertIn("color offset: 1", text.stdout)
        self.assertIn("omitted pixels: 4", text.stdout)
        self.assertEqual(json.loads(self._run(*base, "--color-offset", "0", "--json").stdout)["colors"],
                         json.loads(self._run(*base, "--json").stdout)["colors"])
        self.assertIsNone(build_parser().parse_args(("x", "0", "0")).color_offset)
        self.assertIn("--color-offset", build_parser().format_help())

    def test_invalid_offset_and_missing_limit_fail_before_reads(self):
        with mock.patch.object(sample, "read_png_size", side_effect=AssertionError("read")):
            for value in ("-1", "1.2", "1e2", "1_0", " 1", "١", "x", "9" * 5000):
                result = self._run("missing.png", "0", "0", "--histogram", "--top-colors", "1", "--color-offset", value)
                self.assertEqual((result.returncode, result.stdout), (2, ""))
                self.assertNotIn("Traceback", result.stderr)
            for mode in (("--histogram",), (), ("--runs",), ("--find-color", "000000")):
                result = self._run("missing.png", "0", "0", "--color-offset", "0", *mode)
                self.assertEqual(result.returncode, 2)
                self.assertIn("--color-offset requires --top-colors", result.stderr)


if __name__ == "__main__":
    import unittest

    unittest.main()
