"""Tests for metadata shared by sampler report modes."""

from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from argparse import Namespace

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.sample_lib.report_common import (  # noqa: E402
    compact_json, format_image_header, hex, positioned_region_column_alpha,
    positioned_region_column_pixels, positioned_region_pixels,
    print_json_report, print_report_header, region_alpha, region_from_args,
    region_pixels, report_context,
)


class _ThreeByTwoImage:
    """A 3x2 image whose pixel i (row-major) has RGB (i, 100 + i, 200 + i)
    and alpha 10 + i. The region used below covers columns 1-2 of both rows,
    so row-major and column-major order differ."""

    width = 3
    rgb = bytes(v for i in range(6) for v in (i, 100 + i, 200 + i))
    alpha = bytes(10 + i for i in range(6))


class _NoAlphaImage(_ThreeByTwoImage):
    alpha = None


REGION = (1, 0, 2, 2)  # x, y, width, height: pixel indices 1, 2, 4, 5


class TestRegionAlpha(unittest.TestCase):
    """Alpha iteration over a region, row-major and column-major."""

    def test_region_alpha_is_row_major(self):
        # Row 0: pixels 1, 2; row 1: pixels 4, 5 -> alpha 11, 12, 14, 15.
        self.assertEqual(list(region_alpha(_ThreeByTwoImage(), *REGION)),
                         [11, 12, 14, 15])

    def test_column_alpha_is_column_major(self):
        # Column 1: pixels 1, 4; column 2: pixels 2, 5 -> alpha 11, 14, 12, 15.
        self.assertEqual(
            list(positioned_region_column_alpha(_ThreeByTwoImage(), *REGION)),
            [11, 14, 12, 15])

    def test_image_without_alpha_yields_opaque_for_both_orders(self):
        image = _NoAlphaImage()
        self.assertEqual(list(region_alpha(image, *REGION)), [255] * 4)
        self.assertEqual(
            list(positioned_region_column_alpha(image, *REGION)), [255] * 4)


class TestRegionColumnPixels(unittest.TestCase):
    """Column-major pixel iteration with absolute positions."""

    def test_yields_column_major_positions_with_rgb(self):
        # Column 1 then column 2, rows 0 then 1 within each column.
        self.assertEqual(list(positioned_region_column_pixels(
            _ThreeByTwoImage(), *REGION)), [
                (1, 0, (1, 101, 201)),
                (1, 1, (4, 104, 204)),
                (2, 0, (2, 102, 202)),
                (2, 1, (5, 105, 205)),
            ])


class TestRegionPixels(unittest.TestCase):
    """Row-major pixel iteration, the order the runs and histogram reports scan."""

    def test_yields_row_major_rgb_for_the_region(self):
        # Row 0: pixels 1, 2; row 1: pixels 4, 5 (image is 3 wide).
        self.assertEqual(list(region_pixels(_ThreeByTwoImage(), *REGION)), [
            (1, 101, 201),
            (2, 102, 202),
            (4, 104, 204),
            (5, 105, 205),
        ])

    def test_positioned_pixels_carry_absolute_row_major_positions(self):
        self.assertEqual(list(positioned_region_pixels(
            _ThreeByTwoImage(), *REGION)), [
                (1, 0, (1, 101, 201)),
                (2, 0, (2, 102, 202)),
                (1, 1, (4, 104, 204)),
                (2, 1, (5, 105, 205)),
            ])


class TestHexFormat(unittest.TestCase):
    """The reports' ``#RRGGBB`` color text: uppercase, two digits per channel."""

    def test_formats_each_channel_as_two_uppercase_hex_digits(self):
        # 1 -> 01, 171 -> AB, 10 -> 0A: leading zero kept, letters uppercase.
        self.assertEqual(hex((1, 171, 10)), "#01AB0A")

    def test_black_and_white_are_zero_and_full_width(self):
        self.assertEqual(hex((0, 0, 0)), "#000000")
        self.assertEqual(hex((255, 255, 255)), "#FFFFFF")


class TestRegionFromArgs(unittest.TestCase):
    """The region dict every report result and JSON document carries."""

    def test_maps_the_four_region_arguments_to_named_fields(self):
        args = Namespace(x=3, y=5, width=7, height=2)
        self.assertEqual(region_from_args(args),
                         {"x": 3, "y": 5, "width": 7, "height": 2})


class TestCompactJson(unittest.TestCase):
    """Compact JSON, the format embedded in the reports' plain-text lines."""

    def test_uses_no_spaces_after_separators(self):
        self.assertEqual(compact_json({"a": [1, 2], "b": {"c": 3}}),
                         '{"a":[1,2],"b":{"c":3}}')


class TestPrintJsonReport(unittest.TestCase):
    """The --json line every sample report mode prints."""

    def test_prints_one_ascii_escaped_json_line(self):
        out = StringIO()
        with redirect_stdout(out):
            print_json_report({"image": "\u00e9", "n": 1})
        self.assertEqual(out.getvalue(), '{"image": "\\u00e9", "n": 1}\n')


class TestReportContext(unittest.TestCase):
    """The shared report context's source and region fields."""

    def test_context_contains_source_dimensions_and_requested_region(self):
        args = Namespace(image="reference.png", x=3, y=5, width=7, height=2)

        self.assertEqual(report_context(args, 40, 30), {
            "image": "reference.png",
            "image_width": 40,
            "image_height": 30,
            "region": {"x": 3, "y": 5, "width": 7, "height": 2},
        })

    def test_image_header_escapes_name_and_includes_decoded_dimensions(self):
        self.assertEqual(
            format_image_header("reference\n.png", 40, 30),
            r"image: reference\u000a.png  40x30",
        )

    def test_plain_text_header_includes_requested_region(self):
        args = Namespace(x=3, y=5, width=7, height=2)
        output = StringIO()

        with redirect_stdout(output):
            print_report_header("reference.png: 40x30", args)

        self.assertEqual(output.getvalue(),
                         "reference.png: 40x30\nregion (3, 5) 7x2:\n")


if __name__ == "__main__":
    unittest.main()
