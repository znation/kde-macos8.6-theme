"""Direct result assembly tests for reference-pixel histograms."""

from __future__ import annotations

import contextlib
import copy
import io
import json
from argparse import Namespace
from unittest import TestCase

from support import repo_root  # noqa: F401
from support.cli_fixtures import CliTestCase
from support.png_fixtures import make_png
from tools import sample, sample_report_histogram
from tools.png import Image


def options(**overrides):
    values = dict(x=0, y=0, width=1, height=1, alpha=False, top_colors=None,
                  color_bounds=False, color_positions=False, color_fractions=False,
                  json=False, image="fixture.png")
    values.update(overrides)
    return Namespace(**values)


class TestHistogramResult(TestCase):
    def test_rgb_ties_order_and_no_output_or_namespace_mutation(self):
        args = options(width=3)
        original = copy.copy(vars(args))
        image = Image(3, 1, bytes((9, 0, 0, 1, 0, 0, 5, 0, 0)))
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = sample_report_histogram._histogram_result(args, image, 3, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(vars(args), original)
        self.assertEqual(result, {
            "image": "fixture.png", "image_width": 3, "image_height": 1,
            "region": {"x": 0, "y": 0, "width": 3, "height": 1},
            "colors": [
                {"rgb": [1, 0, 0], "hex": "#010000", "count": 1},
                {"rgb": [5, 0, 0], "hex": "#050000", "count": 1},
                {"rgb": [9, 0, 0], "hex": "#090000", "count": 1},
            ],
        })

    def test_cropped_rgba_result_and_opaque_fallback(self):
        args = options(x=1, width=3, height=2, alpha=True, top_colors=1,
                       color_bounds=True, color_positions=True, color_fractions=True)
        image = Image(5, 2,
            bytes((99, 0, 0, 1, 2, 3, 8, 8, 8, 1, 2, 3, 99, 0, 0,
                  99, 0, 0, 1, 2, 3, 4, 5, 6, 1, 2, 3, 99, 0, 0)),
            bytes((255, 0, 128, 0, 255, 255, 0, 255, 0, 255)))
        self.assertEqual(sample_report_histogram._histogram_result(args, image, 5, 2), {
            "image": "fixture.png", "image_width": 5, "image_height": 2,
            "region": {"x": 1, "y": 0, "width": 3, "height": 2},
            "colors": [{"rgb": [1, 2, 3], "hex": "#010203", "count": 4,
                        "alpha": 0, "fraction": 4 / 6, "position": {"x": 1, "y": 0},
                        "bounds": {"x": 1, "y": 0, "width": 3, "height": 2}}],
            "total_colors": 3, "omitted_pixels": 2,
        })
        opaque = Image(1, 1, bytes((4, 5, 6)))
        self.assertEqual(sample_report_histogram._histogram_result(
            options(alpha=True), opaque, 1, 1)["colors"][0]["alpha"], 255)


class TestHistogramResultCli(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def test_combined_text_json_field_order_and_script_parity(self):
        rows = [bytes((0, 0, 0, 1, 2, 3, 8, 8, 8, 4, 5, 6, 1, 2, 3)),
                bytes((0, 0, 0, 1, 2, 3, 8, 8, 8, 4, 5, 6, 1, 2, 3))]
        path = self._write(self._tmp_dir(), "result.png", make_png(5, 2, rows, color_type=2))
        args = (path, "1", "0", "--width", "3", "--height", "2", "--histogram",
                "--top-colors", "1", "--color-fractions", "--color-bounds", "--color-positions")
        text = self._run(*args)
        self._assert_success(text)
        self.assertEqual(text.stdout.splitlines(), [
            f"image: {path}  5x2", "region (1, 0) 3x2:",
            "1,2,3  #010203  count=2  bounds=1,0,1,2  fraction=0.3333333333333333  position=1,0",
            "total colors: 3", "omitted pixels: 4",
        ])
        json_args = (*args, "--json")
        direct = self._run(*json_args)
        script = self._run_script(*json_args)
        self._assert_success(direct)
        self._assert_success(script)
        self.assertEqual((direct.stdout, direct.stderr, direct.returncode),
                         (script.stdout, script.stderr, script.returncode))
        payload = json.loads(direct.stdout)
        self.assertEqual(list(payload), ["image", "image_width", "image_height", "region",
                                         "colors", "total_colors", "omitted_pixels"])
        self.assertNotIn("omitted_pixels", sample_report_histogram._histogram_result(
            options(width=1, top_colors=None), Image(1, 1, bytes((1, 2, 3))), 1, 1))


if __name__ == "__main__":
    import unittest

    unittest.main()
