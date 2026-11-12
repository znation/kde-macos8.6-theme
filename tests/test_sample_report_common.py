"""Tests for metadata shared by sampler report modes."""

from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from argparse import Namespace

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.sample_report_common import (  # noqa: E402
    compact_json, format_image_header, positioned_region_column_alpha,
    positioned_region_column_pixels, print_report_header, region_alpha,
    report_context,
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


class TestCompactJson(unittest.TestCase):
    """Compact JSON, the format embedded in the reports' plain-text lines."""

    def test_uses_no_spaces_after_separators(self):
        self.assertEqual(compact_json({"a": [1, 2], "b": {"c": 3}}),
                         '{"a":[1,2],"b":{"c":3}}')


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
