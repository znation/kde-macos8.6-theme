"""Unit tests for pixel iteration used by the sampler's report modules."""

from __future__ import annotations

import json
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.sample_report_pixels import _pixel_records, report_pixels  # noqa: E402
from tools.sample_report_common import positioned_region_pixels  # noqa: E402


class _TwoByTwoImage:
    """A 2x2 image: row-major RGB and an optional alpha plane."""

    width = 2
    rgb = bytes((
        1, 2, 3, 10, 11, 12,
        20, 21, 22, 255, 0, 16,
    ))
    alpha = bytes((0, 64, 128, 255))


class TestReportPixels(unittest.TestCase):
    """The ordinary pixel report's text and JSON output shapes."""

    def _run(self, **fields):
        defaults = {"x": 0, "y": 0, "width": 1, "height": 1, "alpha": False}
        defaults.update(fields)
        args = Namespace(image="reference.png", json=False, **defaults)
        output = StringIO()
        with redirect_stdout(output):
            report_pixels(args, _TwoByTwoImage(), 2, 2, "reference.png: 2x2")
        return output.getvalue()

    def test_single_pixel_text_prints_header_then_one_pixel_line(self):
        self.assertEqual(
            self._run(x=1, y=0),
            "reference.png: 2x2\n"
            "pixel (1, 0): 10,11,12  #0A0B0C\n",
        )

    def test_single_pixel_text_appends_alpha_when_requested(self):
        self.assertEqual(
            self._run(x=1, y=0, alpha=True),
            "reference.png: 2x2\n"
            "pixel (1, 0): 10,11,12  #0A0B0C  alpha=64\n",
        )

    def test_one_wide_rectangle_is_a_region_report_not_a_single_pixel(self):
        self.assertEqual(
            self._run(x=1, y=0, width=1, height=2),
            "reference.png: 2x2\n"
            "region (1, 0) 1x2:\n"
            "(1, 0): 10,11,12  #0A0B0C\n"
            "(1, 1): 255,0,16  #FF0010\n",
        )

    def test_rectangle_text_lists_rows_row_major_with_alpha_suffix(self):
        self.assertEqual(
            self._run(width=2, height=2, alpha=True),
            "reference.png: 2x2\n"
            "region (0, 0) 2x2:\n"
            "(0, 0): 1,2,3  #010203  alpha=0\n"
            "(1, 0): 10,11,12  #0A0B0C  alpha=64\n"
            "(0, 1): 20,21,22  #141516  alpha=128\n"
            "(1, 1): 255,0,16  #FF0010  alpha=255\n",
        )

    def test_json_document_carries_context_region_and_pixel_records(self):
        args = Namespace(image="reference.png", json=True, alpha=True,
                         x=0, y=0, width=2, height=2)
        output = StringIO()
        with redirect_stdout(output):
            report_pixels(args, _TwoByTwoImage(), 2, 2, "reference.png: 2x2")

        self.assertEqual(json.loads(output.getvalue()), {
            "image": "reference.png",
            "image_width": 2,
            "image_height": 2,
            "region": {"x": 0, "y": 0, "width": 2, "height": 2},
            "pixels": [
                {"x": 0, "y": 0, "rgb": [1, 2, 3], "hex": "#010203", "alpha": 0},
                {"x": 1, "y": 0, "rgb": [10, 11, 12], "hex": "#0A0B0C", "alpha": 64},
                {"x": 0, "y": 1, "rgb": [20, 21, 22], "hex": "#141516", "alpha": 128},
                {"x": 1, "y": 1, "rgb": [255, 0, 16], "hex": "#FF0010", "alpha": 255},
            ],
        })


class TestPixelRecords(unittest.TestCase):
    """The pixel report's lazy, ordered record generation."""

    def test_records_are_lazy_ordered_and_do_not_mutate_or_print(self):
        class TrackingBytes:
            """Byte sequence that records the index of every element read."""

            def __init__(self, data):
                self._data = bytes(data)
                self.read = []

            def __getitem__(self, index):
                self.read.append(index)
                return self._data[index]

        rgb = TrackingBytes((1, 2, 3, 10, 11, 12, 20, 21, 22,
                             30, 31, 32, 40, 41, 42, 50, 51, 52))
        alpha = TrackingBytes((0, 64, 255, 128, 255, 7))

        class Image:
            width = 3

        image = Image()
        image.rgb = rgb
        image.alpha = alpha
        args = Namespace(x=1, y=0, width=2, height=2, alpha=True)
        snapshot = vars(args).copy()
        with mock.patch("builtins.print") as printed:
            records = _pixel_records(args, image)
            printed.assert_not_called()
            self.assertEqual(rgb.read, [], "iterator construction read pixels")
            self.assertEqual(alpha.read, [], "iterator construction read the alpha plane")
            self.assertEqual(next(records),
                             {"x": 1, "y": 0, "rgb": [10, 11, 12], "hex": "#0A0B0C", "alpha": 64})
            self.assertEqual(rgb.read, [3, 4, 5], "first record read one pixel")
            self.assertEqual(alpha.read, [1], "first record read one alpha byte")
            self.assertEqual(next(records),
                             {"x": 2, "y": 0, "rgb": [20, 21, 22], "hex": "#141516", "alpha": 255})
            self.assertEqual(rgb.read, [3, 4, 5, 6, 7, 8],
                             "second record read the next pixel, no further")
            self.assertEqual(alpha.read, [1, 2],
                             "second record read the next alpha byte, no further")
        self.assertEqual(vars(args), snapshot)

    def test_rgb_omits_alpha_and_opaque_rgba_alpha_uses_255(self):
        class RaisingAlpha:
            def __getitem__(self, index):
                raise AssertionError("alpha plane read without --alpha")

        class Image:
            width = 1
            rgb = bytes((255, 0, 16))
            alpha = RaisingAlpha()

        class OpaqueImage:
            width = 1
            rgb = bytes((255, 0, 16))
            alpha = None

        args = Namespace(x=0, y=0, width=1, height=1, alpha=False)
        self.assertEqual(list(_pixel_records(args, Image())),
                         [{"x": 0, "y": 0, "rgb": [255, 0, 16], "hex": "#FF0010"}])
        args.alpha = True
        self.assertEqual(list(_pixel_records(args, OpaqueImage()))[0]["alpha"], 255)


class TestPositionedRegionPixels(unittest.TestCase):
    """The positioned region helper's row-major pixel coordinates."""

    def test_positions_advance_across_rows_with_row_major_rgb_values(self):
        class Image:
            width = 3
            rgb = bytes((
                10, 11, 12, 20, 21, 22, 30, 31, 32,
                40, 41, 42, 50, 51, 52, 60, 61, 62,
            ))

        self.assertEqual(
            list(positioned_region_pixels(Image(), 1, 0, 2, 2)),
            [
                (1, 0, (20, 21, 22)),
                (2, 0, (30, 31, 32)),
                (1, 1, (50, 51, 52)),
                (2, 1, (60, 61, 62)),
            ],
        )

    def test_single_column_crop_advances_rows_without_neighbor_pixels(self):
        class Image:
            width = 4
            rgb = bytes((
                1, 0, 0, 2, 0, 0, 3, 0, 0, 4, 0, 0,
                5, 0, 0, 6, 0, 0, 7, 0, 0, 8, 0, 0,
                9, 0, 0, 10, 0, 0, 11, 0, 0, 12, 0, 0,
            ))

        self.assertEqual(
            list(positioned_region_pixels(Image(), 2, 0, 1, 3)),
            [(2, 0, (3, 0, 0)), (2, 1, (7, 0, 0)), (2, 2, (11, 0, 0))],
        )


if __name__ == "__main__":
    unittest.main()
