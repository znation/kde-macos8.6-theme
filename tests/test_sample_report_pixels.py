"""Unit tests for pixel iteration used by the sampler's report modules."""

from __future__ import annotations

import unittest
from argparse import Namespace
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.sample_report_pixels import _pixel_records  # noqa: E402
from tools.sample_report_common import positioned_region_pixels  # noqa: E402


class TestPixelRecords(unittest.TestCase):
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
