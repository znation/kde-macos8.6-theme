"""Tests for tools/png_write.py's encode_png."""

from __future__ import annotations

import unittest

import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import png  # noqa: E402
from tools.png_write import encode_png  # noqa: E402


class TestEncodePng(unittest.TestCase):
    def test_one_pixel_round_trips(self):
        image = png.decode_png(encode_png(1, 1, bytes([1, 2, 3])))
        self.assertEqual((image.width, image.height), (1, 1))
        self.assertEqual(image.rgb, bytes([1, 2, 3]))

    def test_multi_row_image_of_distinct_pixels_round_trips(self):
        width, height = 5, 4
        rgb = bytes((i * 7 + 3) % 256 for i in range(width * height * 3))
        image = png.decode_png(encode_png(width, height, rgb))
        self.assertEqual((image.width, image.height), (width, height))
        self.assertEqual(image.rgb, rgb)

    def test_bytearray_input_is_accepted(self):
        rgb = bytearray([9, 8, 7, 6, 5, 4])
        image = png.decode_png(encode_png(2, 1, rgb))
        self.assertEqual(image.rgb, bytes(rgb))

    def test_output_is_deterministic(self):
        rgb = bytes(range(12))
        self.assertEqual(encode_png(2, 2, rgb), encode_png(2, 2, rgb))

    def test_wrong_length_rgb_is_rejected(self):
        for rgb in (b"", bytes(5), bytes(7)):
            with self.subTest(length=len(rgb)):
                with self.assertRaises(ValueError):
                    encode_png(1, 2, rgb)

    def test_non_bytes_rgb_is_rejected(self):
        with self.assertRaises(ValueError):
            encode_png(1, 1, "abc")

    def test_zero_dimension_is_rejected(self):
        with self.assertRaises(ValueError):
            encode_png(0, 1, b"")
        with self.assertRaises(ValueError):
            encode_png(1, 0, b"")

    def test_bool_dimension_is_rejected(self):
        with self.assertRaises(ValueError):
            encode_png(True, 1, bytes(3))
        with self.assertRaises(ValueError):
            encode_png(1, True, bytes(3))


if __name__ == "__main__":
    unittest.main()
