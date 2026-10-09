"""Tests for tests/png_fixtures.py -- the PNG encoder the image tests share.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import struct
import sys
import unittest
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import png  # noqa: E402
from png_fixtures import (  # noqa: E402
    _chunk,
    ihdr_chunk,
    ihdr_end,
    make_png,
    png_with_idat,
    rgb_image,
    with_ihdr_byte,
)


class TestMakePng(unittest.TestCase):
    def test_rejects_row_with_wrong_length(self):
        # make_png's rows are raw scanlines: a row that is not width*channels
        # bytes shifts every later scanline, and the fixture decodes with a
        # length error that points at the decoder rather than the bad row. The
        # helper must name the offending row and the expected length.
        with self.assertRaises(ValueError) as ctx:
            make_png(2, 1, [bytes([1, 2, 3])])
        message = str(ctx.exception)
        self.assertIn("row 0", message)
        self.assertIn("3 bytes", message)
        self.assertIn("needs 6", message)

    def test_rejects_filter_types_length_mismatch(self):
        # There is one filter type per row, so listing the wrong number is a
        # fixture bug: a short list used to raise a bare IndexError and a long
        # one was silently ignored.
        with self.assertRaises(ValueError) as ctx:
            make_png(1, 1, [bytes([0])], filter_types=[0, 0])
        message = str(ctx.exception)
        self.assertIn("2 entries", message)
        self.assertIn("for 1 rows", message)

    def test_rejects_unsupported_color_type(self):
        # An unknown color type is a fixture bug too; the dict lookup used to
        # escape as a bare KeyError that named only the number.
        with self.assertRaises(ValueError) as ctx:
            make_png(1, 1, [bytes([0])], color_type=5)
        message = str(ctx.exception)
        self.assertIn("color_type 5", message)
        self.assertIn("[0, 2, 3, 4, 6]", message)

    def test_rejects_non_positive_dimensions(self):
        # A negative dimension used to escape as a bare struct.error naming
        # neither the argument nor the requirement, and a zero width silently
        # built a degenerate PNG. Both are fixture bugs and must be named.
        for width, height in ((0, 1), (1, 0), (-1, 1), (1, -1), (0, 0)):
            with self.subTest(width=width, height=height):
                with self.assertRaises(ValueError) as ctx:
                    make_png(width, height, [])
                message = str(ctx.exception)
                self.assertIn("make_png", message)
                self.assertIn(f"{width}x{height}", message)

    def test_accepts_exact_row_and_matching_filters(self):
        data = make_png(1, 1, [bytes([7, 8, 9])], filter_types=[0])
        self.assertEqual(png.decode_png(data).rgb, bytes([7, 8, 9]))


class TestWithIhdrByte(unittest.TestCase):
    def test_rejects_out_of_range_offset(self):
        # A negative offset indexes from the end of the IHDR payload and would
        # silently edit a different field; one past the end raised a bare
        # IndexError. Both must name the offset and the payload's size.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        for offset in (-1, 13, 100):
            with self.subTest(offset=offset):
                with self.assertRaises(ValueError) as ctx:
                    with_ihdr_byte(data, offset, 0)
                message = str(ctx.exception)
                self.assertIn(f"offset {offset}", message)
                self.assertIn("0 <= offset < 13", message)

    def test_rejects_value_out_of_byte_range(self):
        # A value above 255 raised a bare bytearray ValueError that named the
        # range but not the argument; a negative value did the same.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        for value in (-1, 256, 1000):
            with self.subTest(value=value):
                with self.assertRaises(ValueError) as ctx:
                    with_ihdr_byte(data, 8, value)
                message = str(ctx.exception)
                self.assertIn(f"value {value}", message)
                self.assertIn("0 <= value <= 255", message)

    def test_accepts_the_last_ihdr_byte(self):
        # offset 12 is the interlace field, the last valid offset; the bound
        # must not reject it.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        broken = with_ihdr_byte(data, 12, 1)
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(broken)
        self.assertIn("interlaced", str(ctx.exception))


class TestIhdrEnd(unittest.TestCase):
    def test_returns_the_offset_where_the_next_chunk_begins(self):
        # The decode tests splice chunks in at this boundary. Splicing must
        # leave the pixels unchanged: an offset inside IHDR would corrupt it,
        # and one inside the following chunk would split that chunk.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        boundary = ihdr_end(data)
        self.assertEqual(data[12:16], b"IHDR")
        spliced = data[:boundary] + _chunk(b"tEXt", b"note") + data[boundary:]
        self.assertEqual(png.decode_png(spliced), png.decode_png(data))


class TestIhdrChunk(unittest.TestCase):
    def test_builds_the_fixed_8_bit_non_interlaced_header(self):
        # The header's fixed defaults (8-bit depth, zero compression, filter
        # and interlace methods) are easy to get subtly wrong when written by
        # hand; pin them and the big-endian width/height so a bad change fails
        # here instead of as an opaque decode error downstream.
        chunk = ihdr_chunk(3, 5, 2)
        self.assertEqual(chunk[:8], struct.pack(">I", 13) + b"IHDR")
        self.assertEqual(
            chunk[8:21], struct.pack(">IIBBBBB", 3, 5, 8, 2, 0, 0, 0)
        )
        self.assertEqual(
            chunk[21:],
            struct.pack(">I", zlib.crc32(chunk[4:21]) & 0xFFFFFFFF),
        )


class TestPngWithIdat(unittest.TestCase):
    def test_rejects_non_positive_dimensions(self):
        # Same fixture-bug class as make_png: the declared dimensions go
        # straight into struct.pack, so a negative one escaped as a bare
        # struct.error instead of naming the argument.
        for width, height in ((0, 1), (1, 0), (-1, 1), (1, -1)):
            with self.subTest(width=width, height=height):
                with self.assertRaises(ValueError) as ctx:
                    png_with_idat(b"", width=width, height=height)
                message = str(ctx.exception)
                self.assertIn("png_with_idat", message)
                self.assertIn(f"{width}x{height}", message)


class TestRgbImage(unittest.TestCase):
    def test_rejects_a_non_triple_pixel_result(self):
        # bytes() accepts a plain int as a length, so a callback returning 3
        # used to build three zero bytes silently -- a wrong image that every
        # later assertion would read as valid. It must name the coordinate.
        for value in (3, None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError) as ctx:
                    rgb_image(1, 1, lambda x, y: value)
                message = str(ctx.exception)
                self.assertIn("pixel(0, 0)", message)
                self.assertIn("(r, g, b)", message)

    def test_rejects_wrong_channel_count(self):
        for value in ((1, 2), (1, 2, 3, 4)):
            with self.subTest(value=value):
                with self.assertRaises(ValueError) as ctx:
                    rgb_image(1, 1, lambda x, y: value)
                message = str(ctx.exception)
                self.assertIn(f"{len(value)} channels", message)
                self.assertIn("expected 3", message)

    def test_rejects_a_non_integer_channel(self):
        with self.assertRaises(ValueError) as ctx:
            rgb_image(1, 1, lambda x, y: (1, "2", 3))
        message = str(ctx.exception)
        self.assertIn("channel g", message)
        self.assertIn("not an integer", message)

    def test_rejects_an_out_of_range_channel(self):
        for value in ((1, 2, 256), (-1, 2, 3)):
            with self.subTest(value=value):
                with self.assertRaises(ValueError) as ctx:
                    rgb_image(1, 1, lambda x, y: value)
                message = str(ctx.exception)
                self.assertIn("outside 0-255", message)

    def test_accepts_a_valid_triple(self):
        image, data = rgb_image(2, 1, lambda x, y: (x * 100, 50, 200))
        self.assertEqual(image.rgb, bytes([0, 50, 200, 100, 50, 200]))
        self.assertEqual(png.decode_png(data).rgb, image.rgb)
