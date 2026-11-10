"""Direct tests for assembled reference scanline results."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest import TestCase

from support import repo_root  # noqa: F401
from tools.sample_arguments import build_parser
from tools.sample_report_runs import _runs_result, report_runs


class TestSampleRunsResult(TestCase):
    def test_report_runs_prints_json_result(self):
        args = build_parser().parse_args([
            "fixture.png", "0", "0", "--width", "2", "--runs", "--json",
        ])
        image = SimpleNamespace(width=2, rgb=bytes((1, 2, 3, 1, 2, 3)), alpha=None)
        output = StringIO()
        with redirect_stdout(output):
            report_runs(args, image, 2, 1, "header")
        self.assertEqual(output.getvalue(), (
            '{"image": "fixture.png", "image_width": 2, "image_height": 1, '
            '"region": {"x": 0, "y": 0, "width": 2, "height": 1}, '
            '"axis": "horizontal", "runs": [{"x": 0, "y": 0, "length": 2, '
            '"rgb": [1, 2, 3], "hex": "#010203"}]}\n'
        ))

    def test_report_runs_prints_text_header_region_and_run(self):
        args = build_parser().parse_args([
            "fixture.png", "0", "0", "--width", "2", "--runs",
        ])
        image = SimpleNamespace(width=2, rgb=bytes((1, 2, 3, 1, 2, 3)), alpha=None)
        output = StringIO()
        with redirect_stdout(output):
            report_runs(args, image, 2, 1, "sample header")
        self.assertEqual(output.getvalue(), (
            "sample header\n"
            "region (0, 0) 2x1:\n"
            "axis: horizontal\n"
            "(0, 0): 1,2,3  #010203  length=2\n"
        ))

    def test_cropped_horizontal_result_keeps_scanlines_separate(self):
        args = build_parser().parse_args([
            "fixture.png", "1", "0", "--width", "3", "--height", "2",
            "--runs", "--run-axis", "horizontal", "--json",
        ])
        before = vars(args).copy()
        colors = [(9, 9, 9), (10, 20, 30), (10, 20, 30), (9, 9, 9), (9, 9, 9),
                  (9, 9, 9), (10, 20, 30), (10, 20, 30), (40, 50, 60), (9, 9, 9)]
        pixels = bytes(channel for color in colors for channel in color)
        image = SimpleNamespace(width=5, rgb=pixels, alpha=None)
        output = StringIO()
        with redirect_stdout(output):
            result = _runs_result(args, image, 5, 2)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(vars(args), before)
        self.assertEqual(image.rgb, pixels)
        self.maxDiff = None
        self.assertEqual(result, {
            "image": "fixture.png", "image_width": 5, "image_height": 2,
            "region": {"x": 1, "y": 0, "width": 3, "height": 2},
            "axis": "horizontal",
            "runs": [
                {"x": 1, "y": 0, "length": 2, "rgb": [10, 20, 30], "hex": "#0A141E"},
                {"x": 3, "y": 0, "length": 1, "rgb": [9, 9, 9], "hex": "#090909"},
                {"x": 1, "y": 1, "length": 2, "rgb": [10, 20, 30], "hex": "#0A141E"},
                {"x": 3, "y": 1, "length": 1, "rgb": [40, 50, 60], "hex": "#28323C"},
            ],
        })

    def test_vertical_alpha_result_preserves_transparent_rgb(self):
        args = build_parser().parse_args([
            "fixture.png", "0", "0", "--height", "3", "--runs", "--alpha",
        ])
        rgb = bytes((1, 2, 3, 1, 2, 3, 1, 2, 3))
        alpha = bytes((0, 128, 0))
        result = _runs_result(args, SimpleNamespace(width=1, rgb=rgb, alpha=alpha), 1, 3)
        self.assertEqual(result["axis"], "vertical")
        self.assertEqual(result["runs"], [
            {"x": 0, "y": 0, "length": 1, "rgb": [1, 2, 3], "alpha": 0, "hex": "#010203"},
            {"x": 0, "y": 1, "length": 1, "rgb": [1, 2, 3], "alpha": 128, "hex": "#010203"},
            {"x": 0, "y": 2, "length": 1, "rgb": [1, 2, 3], "alpha": 0, "hex": "#010203"},
        ])

    def test_rectangle_defaults_to_vertical_scanlines(self):
        args = build_parser().parse_args([
            "fixture.png", "0", "0", "--width", "2", "--height", "2", "--runs", "--json",
        ])
        image = SimpleNamespace(
            width=2,
            rgb=bytes((1, 2, 3, 9, 8, 7, 1, 2, 3, 9, 8, 7)),
            alpha=None,
        )

        result = _runs_result(args, image, 2, 2)

        self.assertEqual(result["axis"], "vertical")
        self.assertEqual(result["runs"], [
            {"x": 0, "y": 0, "length": 2, "rgb": [1, 2, 3], "hex": "#010203"},
            {"x": 1, "y": 0, "length": 2, "rgb": [9, 8, 7], "hex": "#090807"},
        ])


if __name__ == "__main__":
    import unittest

    unittest.main()
