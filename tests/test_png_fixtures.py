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

from error_assertions import error_message

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import png  # noqa: E402
from png_fixtures import (  # noqa: E402
    _chunk,
    control_named_png,
    ihdr_chunk,
    ihdr_end,
    make_png,
    png_with_idat,
    rgb_from_rows,
    rgb_image,
    splice_after_ihdr,
    with_ihdr_byte,
)


def _value_error(case, func, *args, **kwargs):
    """Call *func* and return the ``ValueError`` message it raises.

    Every fixture guard tested here reports a malformed argument by raising
    ``ValueError``; this pins that type once on top of the shared
    ``error_assertions.error_message``. *case* is the calling
    ``unittest.TestCase``, so a failure is reported against the right test.
    """
    return error_message(case, ValueError, func, *args, **kwargs)


class TestMakePng(unittest.TestCase):
    def test_rejects_row_with_wrong_length(self):
        # make_png's rows are raw scanlines: a row that is not width*channels
        # bytes shifts every later scanline, and the fixture decodes with a
        # length error that points at the decoder rather than the bad row. The
        # helper must name the offending row and the expected length.
        message = _value_error(self, make_png, 2, 1, [bytes([1, 2, 3])])
        self.assertIn("row 0", message)
        self.assertIn("3 bytes", message)
        self.assertIn("needs 6", message)

    def test_rejects_filter_types_length_mismatch(self):
        # There is one filter type per row, so listing the wrong number is a
        # fixture bug: a short list used to raise a bare IndexError and a long
        # one was silently ignored.
        message = _value_error(
            self, make_png, 1, 1, [bytes([0])], filter_types=[0, 0]
        )
        self.assertIn("2 entries", message)
        self.assertIn("for 1 rows", message)

    def test_rejects_unsupported_color_type(self):
        # An unknown color type is a fixture bug too; the dict lookup used to
        # escape as a bare KeyError that named only the number.
        message = _value_error(
            self, make_png, 1, 1, [bytes([0])], color_type=5
        )
        self.assertIn("color_type 5", message)
        self.assertIn("[0, 2, 3, 4, 6]", message)

    def test_rejects_non_positive_dimensions(self):
        # A negative dimension used to escape as a bare struct.error naming
        # neither the argument nor the requirement, and a zero width silently
        # built a degenerate PNG. Both are fixture bugs and must be named.
        for width, height in ((0, 1), (1, 0), (-1, 1), (1, -1), (0, 0)):
            with self.subTest(width=width, height=height):
                message = _value_error(self, make_png, width, height, [])
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
                message = _value_error(
                    self, with_ihdr_byte, data, offset, 0
                )
                self.assertIn(f"offset {offset}", message)
                self.assertIn("0 <= offset < 13", message)

    def test_rejects_value_out_of_byte_range(self):
        # A value above 255 raised a bare bytearray ValueError that named the
        # range but not the argument; a negative value did the same.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        for value in (-1, 256, 1000):
            with self.subTest(value=value):
                message = _value_error(self, with_ihdr_byte, data, 8, value)
                self.assertIn(f"value {value}", message)
                self.assertIn("0 <= value <= 255", message)

    def test_accepts_the_last_ihdr_byte(self):
        # offset 12 is the interlace field, the last valid offset; the bound
        # must not reject it.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        broken = with_ihdr_byte(data, 12, 1)
        self.assertIn(
            "interlaced", error_message(self, png.PngError, png.decode_png, broken)
        )


class TestIhdrEnd(unittest.TestCase):
    def test_returns_the_offset_where_the_next_chunk_begins(self):
        # The decode tests splice chunks in at this boundary. An offset inside
        # IHDR would corrupt it, and one inside the following chunk would
        # split that chunk, so pin the boundary to the next chunk's type.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        boundary = ihdr_end(data)
        self.assertEqual(data[12:16], b"IHDR")
        self.assertEqual(data[boundary + 4 : boundary + 8], b"IDAT")


class TestSpliceAfterIhdr(unittest.TestCase):
    def test_inserts_at_the_ihdr_boundary_without_changing_the_pixels(self):
        # A chunk spliced in here must sit between IHDR and IDAT; the decode
        # tests rely on this to inject framing without touching the image.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        boundary = ihdr_end(data)
        chunk = _chunk(b"tEXt", b"note")
        spliced = splice_after_ihdr(data, chunk)
        self.assertEqual(spliced[boundary : boundary + len(chunk)], chunk)
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


class TestRgbFromRows(unittest.TestCase):
    def test_expands_each_supported_color_type(self):
        # The helper stands in for the decoder's per-color-type expansion, so
        # pin one row of each type: a wrong stride or a kept alpha byte would
        # otherwise make both a decode and its expected value wrong together.
        self.assertEqual(
            rgb_from_rows([bytes([1, 2])], 0),
            bytes([1, 1, 1, 2, 2, 2]),
        )
        self.assertEqual(rgb_from_rows([bytes([1, 2, 3])], 2), bytes([1, 2, 3]))
        self.assertEqual(
            rgb_from_rows([bytes([7, 200, 100, 50])], 4),
            bytes([7, 7, 7, 100, 100, 100]),
        )
        self.assertEqual(
            rgb_from_rows([bytes([1, 2, 3, 4, 5, 6, 7, 8])], 6),
            bytes([1, 2, 3, 5, 6, 7]),
        )

    def test_concatenates_rows_in_order(self):
        # A decode's rgb is the rows concatenated, so the helper must not
        # interleave or reverse them.
        self.assertEqual(
            rgb_from_rows([bytes([1]), bytes([2])], 0),
            bytes([1, 1, 1, 2, 2, 2]),
        )

    def test_rejects_an_unsupported_color_type(self):
        # Palette output depends on the PLTE table, which this helper does not
        # read; returning RGB for it would be bytes no decode could match.
        message = _value_error(self, rgb_from_rows, [bytes([0])], 3)
        self.assertIn("color_type 3", message)
        self.assertIn("[0, 2, 4, 6]", message)


class TestPngWithIdat(unittest.TestCase):
    def test_rejects_non_positive_dimensions(self):
        # Same fixture-bug class as make_png: the declared dimensions go
        # straight into struct.pack, so a negative one escaped as a bare
        # struct.error instead of naming the argument.
        for width, height in ((0, 1), (1, 0), (-1, 1), (1, -1)):
            with self.subTest(width=width, height=height):
                message = _value_error(
                    self, png_with_idat, b"", width=width, height=height
                )
                self.assertIn("png_with_idat", message)
                self.assertIn(f"{width}x{height}", message)


class TestRgbImage(unittest.TestCase):
    def _rgb_error(self, value):
        """Return the ``ValueError`` message ``rgb_image`` raises for *value*.

        Every guard in this case drives a 1x1 image whose pixel callback
        returns *value*, so this pins that call shape once.
        """
        return _value_error(self, rgb_image, 1, 1, lambda x, y: value)

    def test_rejects_a_non_triple_pixel_result(self):
        # bytes() accepts a plain int as a length, so a callback returning 3
        # used to build three zero bytes silently -- a wrong image that every
        # later assertion would read as valid. It must name the coordinate.
        for value in (3, None):
            with self.subTest(value=value):
                message = self._rgb_error(value)
                self.assertIn("pixel(0, 0)", message)
                self.assertIn("(r, g, b)", message)

    def test_rejects_wrong_channel_count(self):
        for value in ((1, 2), (1, 2, 3, 4)):
            with self.subTest(value=value):
                message = self._rgb_error(value)
                self.assertIn(f"{len(value)} channels", message)
                self.assertIn("expected 3", message)

    def test_rejects_a_non_integer_channel(self):
        message = self._rgb_error((1, "2", 3))
        self.assertIn("channel g", message)
        self.assertIn("not an integer", message)

    def test_rejects_an_out_of_range_channel(self):
        for value in ((1, 2, 256), (-1, 2, 3)):
            with self.subTest(value=value):
                message = self._rgb_error(value)
                self.assertIn("outside 0-255", message)

    def test_accepts_a_valid_triple(self):
        image, data = rgb_image(2, 1, lambda x, y: (x * 100, 50, 200))
        self.assertEqual(image.rgb, bytes([0, 50, 200, 100, 50, 200]))
        self.assertEqual(png.decode_png(data).rgb, image.rgb)


class TestValueError(unittest.TestCase):
    def test_returns_the_message_from_a_value_error(self):
        def reject():
            raise ValueError("row 0 needs 6 bytes")

        self.assertEqual(_value_error(self, reject), "row 0 needs 6 bytes")

    def test_lets_another_exception_type_propagate(self):
        # The helper names ValueError as the expected failure; a different
        # exception must reach the test rather than being swallowed as a pass.
        def reject():
            raise TypeError("not a ValueError")

        with self.assertRaises(TypeError):
            _value_error(self, reject)


class TestControlNamedPng(unittest.TestCase):
    def test_yields_a_valid_png_whose_name_carries_an_escape(self):
        # The CLI escaping tests read the path from this fixture; pin that it
        # really is a decodable 1x1 PNG and that the name still carries the
        # OSC title-setting escape those tests are about.
        with control_named_png() as path:
            self.assertTrue(path.endswith("evil\x1b]0;pwned\x07.png"))
            self.assertEqual(
                png.decode_png(Path(path).read_bytes()),
                png.Image(1, 1, b"\x00\x00\x00"),
            )
