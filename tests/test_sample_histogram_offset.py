"""Paged selection for reference color histograms."""

from __future__ import annotations

import json

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import rgb_image
from tools import sample
from tools.sample_arguments import build_parser


class TestSampleHistogramOffset(CliTestCase):
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


if __name__ == "__main__":
    import unittest

    unittest.main()
