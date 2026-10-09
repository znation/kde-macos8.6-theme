"""Tests for tools/png.py's decode_png -- scanline decoding.

Pins the successful decode path: the five PNG filter types, the supported
colour types, palette expansion and the ``max_rows`` bound. The chunk-framing
tests live in ``test_png_chunks``; the rejections for malformed image data and
the resource limits live in ``test_png_malformed``.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest

import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import png
from png_fixtures import (  # noqa: E402
    decode_error,
    make_png,
    rgb_from_rows,
    rgb_image,
)


class TestDecode(unittest.TestCase):
    def test_rgb_roundtrip(self):
        image, data = rgb_image(3, 2, lambda x, y: (x * 10, y * 20, 30))
        self.assertEqual(png.decode_png(data), image)

    def test_max_rows_returns_only_the_top_scanlines(self):
        image, data = rgb_image(3, 4, lambda x, y: (x * 10, y * 20, 30))
        top = png.decode_png(data, max_rows=2)
        self.assertEqual(top, png.Image(3, 2, image.rgb[: 3 * 2 * 3]))

    def test_max_rows_at_or_above_height_decodes_every_row(self):
        image, data = rgb_image(3, 4, lambda x, y: (x, y, 0))
        self.assertEqual(png.decode_png(data, max_rows=4), image)
        self.assertEqual(png.decode_png(data, max_rows=99), image)

    def test_max_rows_still_checks_every_scanline_filter_type(self):
        # The bound skips the predictor work, not the filter-type check: a bad
        # filter type in a row the caller did not ask for is still rejected.
        rows = [bytes(3), bytes(3), bytes(3)]
        data = make_png(1, 3, rows, filter_types=[0, 0, 7])
        message = decode_error(self, data, max_rows=1)
        self.assertIn("row 2", message)

    def test_max_rows_rejects_a_non_positive_or_non_integer_bound(self):
        _, data = rgb_image(1, 2, lambda x, y: (0, 0, 0))
        for bad in (0, -1, True, 1.5, "2"):
            with self.subTest(max_rows=bad):
                message = decode_error(self, data, max_rows=bad)
                self.assertIn("max_rows", message)

    def test_all_filter_types(self):
        rows = [
            bytes([1, 2, 3, 4, 5, 6, 7, 8, 9]),
            bytes([10, 20, 30, 40, 50, 60, 70, 80, 90]),
            bytes([200, 150, 100, 50, 25, 12, 6, 3, 1]),
            bytes([0, 255, 0, 255, 0, 255, 0, 255, 0]),
            bytes([17, 34, 51, 68, 85, 102, 119, 136, 153]),
        ]
        # One row per PNG filter type: 0 None, 1 Sub, 2 Up, 3 Average, 4 Paeth.
        data = make_png(3, 5, rows, filter_types=[0, 1, 2, 3, 4])
        image = png.decode_png(data)
        self.assertEqual(image.rgb, b"".join(rows))

    def test_grayscale_all_filter_types(self):
        # Color-type-0 grayscale is a single channel, so it exercises the
        # one-channel Paeth path: a wrong first-pixel or carried-left value
        # would scramble the row rather than fail loudly.
        rows = [
            bytes([1, 2, 3, 4, 5]),
            bytes([10, 20, 30, 40, 50]),
            bytes([200, 150, 100, 50, 25]),
            bytes([0, 255, 0, 255, 0]),
            bytes([17, 34, 51, 68, 85]),
        ]
        data = make_png(5, 5, rows, color_type=0, filter_types=[0, 1, 2, 3, 4])
        self.assertEqual(png.decode_png(data).rgb, rgb_from_rows(rows, 0))

    def test_palette(self):
        palette = bytes([255, 0, 0, 0, 255, 0])
        rows = [bytes([0, 1])]
        data = make_png(2, 1, rows, color_type=3, palette=palette)
        self.assertEqual(png.decode_png(data).rgb, bytes([255, 0, 0, 0, 255, 0]))

    def test_palette_full_table_expands_every_index(self):
        # The table-driven expansion must map each index to its PLTE entry,
        # including the last one (255).
        palette = bytes(v for i in range(256) for v in (i, i ^ 0xFF, (i * 7) & 0xFF))
        rows = [bytes([0, 1, 254, 255])]
        data = make_png(4, 1, rows, color_type=3, palette=palette)
        expected = b"".join(palette[i * 3 : i * 3 + 3] for i in (0, 1, 254, 255))
        self.assertEqual(png.decode_png(data).rgb, expected)

    def test_grayscale_and_rgba(self):
        gray = make_png(2, 1, [bytes([7, 200])], color_type=0)
        self.assertEqual(png.decode_png(gray).rgb, bytes([7, 7, 7, 200, 200, 200]))
        # Two pixels so dropping the alpha byte is checked across a stride
        # rather than only at the first pixel.
        rgba = make_png(2, 1, [bytes([1, 2, 3, 4, 5, 6, 7, 8])], color_type=6)
        self.assertEqual(png.decode_png(rgba).rgb, bytes([1, 2, 3, 5, 6, 7]))

    def test_rgba_all_filter_types_ignore_alpha(self):
        # Color-type-6 alpha is dropped before unfiltering. A filter that
        # references a same-channel neighbour must still reconstruct the
        # colour channels exactly, so decode must equal the alpha-stripped
        # pixels with one row per PNG filter type.
        rows = [
            bytes([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
            bytes([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]),
            bytes([200, 150, 100, 50, 25, 12, 6, 3, 1, 0, 255, 128]),
            bytes([0, 255, 0, 255, 0, 255, 0, 255, 0, 255, 0, 255]),
            bytes([17, 34, 51, 68, 85, 102, 119, 136, 153, 170, 187, 204]),
        ]
        data = make_png(3, 5, rows, color_type=6, filter_types=[0, 1, 2, 3, 4])
        self.assertEqual(png.decode_png(data).rgb, rgb_from_rows(rows, 6))

    def test_grayscale_alpha_ignores_alpha(self):
        # color_type 4 is grayscale + alpha (2 bytes per pixel). It is the only
        # supported color type with no decode test: the alpha byte must be
        # dropped and each gray sample repeated across R, G and B. A wrong
        # stride would silently emit scrambled pixels that poison a fidelity
        # score, so two pixels are used to exercise the stride.
        data = make_png(2, 1, [bytes([7, 200, 100, 50])], color_type=4)
        self.assertEqual(
            png.decode_png(data).rgb, bytes([7, 7, 7, 100, 100, 100])
        )
