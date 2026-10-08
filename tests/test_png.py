"""Tests for tools/png.py -- the PNG reader behind the fidelity tool.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import os
import random
import struct
import subprocess
import sys
import tempfile
import tracemalloc
import unittest
import zlib
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import png  # noqa: E402
from png_fixtures import (  # noqa: E402
    _PNG_SIGNATURE,
    _chunk,
    _paeth,
    make_png,
    png_with_idat,
    rgb_image,
    with_ihdr_byte,
)


class TestImage(unittest.TestCase):
    def test_rejects_rgb_length_that_does_not_match_dimensions(self):
        # Image promises tightly packed width*height*3 bytes, but nothing
        # checked it: compare() slices rgb by channel and divides by the
        # declared pixel count, so a short or long buffer mis-measures and can
        # report a wrong MAE instead of failing. The invariant is enforced at
        # construction and the error names the actual and expected byte counts.
        for width, height, size in ((2, 2, 11), (2, 2, 13), (1, 1, 0)):
            with self.subTest(width=width, height=height, size=size):
                with self.assertRaises(png.PngError) as ctx:
                    png.Image(width, height, bytes(size))
                message = str(ctx.exception)
                self.assertIn(str(size), message)
                self.assertIn(str(width * height * 3), message)
                self.assertIn(f"{width}x{height}", message)

    def test_accepts_rgb_length_matching_dimensions(self):
        image = png.Image(2, 2, bytes(12))
        self.assertEqual(len(image.rgb), 12)

    def test_rejects_non_positive_dimensions(self):
        # decode_png rejects a zero-dimension PNG, but a directly constructed
        # Image accepted one: 0 * height * 3 == 0 bytes, so the byte-count
        # check passed and compare() later raised an opaque ValueError from
        # _max_byte_index. A negative dimension was worse still, reporting a
        # nonsensical negative "needs" byte count. The invariant belongs at
        # construction, named with the offending dimensions.
        for width, height in ((0, 1), (1, 0), (0, 0), (-2, 3), (3, -1)):
            with self.subTest(width=width, height=height):
                with self.assertRaises(png.PngError) as ctx:
                    png.Image(width, height, b"")
                self.assertIn(f"{width}x{height}", str(ctx.exception))


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


class TestDecode(unittest.TestCase):
    def _decode_error(self, data):
        """Assert decode_png rejects *data* and return the PngError message."""
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(data)
        return str(ctx.exception)

    def test_rgb_roundtrip(self):
        image, data = rgb_image(3, 2, lambda x, y: (x * 10, y * 20, 30))
        self.assertEqual(png.decode_png(data), image)

    def test_multiple_idat_chunks_are_concatenated(self):
        # An encoder splits the zlib stream across several IDAT chunks once it
        # exceeds its output buffer, so a real screenshot's image data arrives
        # in more than one chunk. decode_png must concatenate every IDAT
        # payload in order before inflating; keeping only one would fail to
        # decode any large reference image.
        image, data = rgb_image(3, 2, lambda x, y: (x * 10, y * 20, 30))
        marker = data.index(b"IDAT")
        length = struct.unpack(">I", data[marker - 4 : marker])[0]
        compressed = data[marker + 4 : marker + 4 + length]
        tail = data[marker + 4 + length + 4 :]
        split = len(compressed) // 2
        two_chunks = (
            data[: marker - 4]
            + _chunk(b"IDAT", compressed[:split])
            + _chunk(b"IDAT", compressed[split:])
            + tail
        )
        self.assertEqual(png.decode_png(two_chunks), image)

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
        expected = b"".join(
            bytes(b for g in row for b in (g, g, g)) for row in rows
        )
        self.assertEqual(png.decode_png(data).rgb, expected)

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

    def test_palette_index_outside_plte_names_index_and_size(self):
        # A palette image whose pixel index has no PLTE entry must name the
        # offending index and the palette size, or the user cannot tell which
        # pixel is bad or how short the palette is. The size is named both as
        # entries and as bytes, matching the PLTE-length error.
        palette = bytes([255, 0, 0])  # one entry: index 0 only
        data = make_png(1, 1, [bytes([1])], color_type=3, palette=palette)
        message = self._decode_error(data)
        self.assertIn("index 1", message)
        self.assertIn("1 entry", message)
        self.assertIn("3 bytes", message)

    def test_palette_index_outside_multi_entry_plte_counts_entries(self):
        # The same out-of-range diagnostic on a palette with more than one
        # entry must say "entries", not the singular "entry": the message
        # counts the palette so the user can see how short it is.
        palette = bytes([255, 0, 0, 0, 255, 0])  # two entries: indices 0 and 1
        data = make_png(1, 1, [bytes([2])], color_type=3, palette=palette)
        message = self._decode_error(data)
        self.assertIn("index 2", message)
        self.assertIn("2 entries", message)
        self.assertIn("6 bytes", message)

    def test_palette_length_not_multiple_of_three(self):
        # A PLTE whose length is not a multiple of 3 ends in a partial RGB
        # entry. Index 0 would still decode, so without this check a malformed
        # palette passes silently as long as no pixel uses the bad entry.
        palette = bytes([255, 0, 0, 0])  # 4 bytes: index 1 is a partial entry
        data = make_png(1, 1, [bytes([0])], color_type=3, palette=palette)
        message = self._decode_error(data)
        self.assertIn("4 bytes", message)
        self.assertIn("multiple of 3", message)

    def test_palette_longer_than_256_entries(self):
        # The PNG spec caps PLTE at 256 entries (768 bytes); 771 bytes is 257
        # entries (a whole multiple of 3, so the length check cannot reject it
        # on the modulo alone) and must be reported with its actual size.
        palette = bytes(771)
        data = make_png(1, 1, [bytes([0])], color_type=3, palette=palette)
        message = self._decode_error(data)
        self.assertIn("771 bytes", message)
        self.assertIn("768", message)

    def test_truncated_image_data_names_actual_and_expected(self):
        # An IDAT that decompresses to fewer scanlines than IHDR's height
        # declares must name how many bytes arrived and how many were needed,
        # so a truncated file is distinguishable from other corruption.
        data = make_png(3, 3, [bytes(9)])
        self.assertIn(
            "got 10 bytes, expected 30 for a 3x3 image",
            self._decode_error(data),
        )

    def test_rejects_png_without_image_data(self):
        # A PNG truncated before its IDAT chunk, or one whose IDAT is empty,
        # must be named as missing image data rather than surfacing zlib's
        # opaque "incomplete or truncated stream".
        ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        cases = {
            "no IDAT": _PNG_SIGNATURE + ihdr + _chunk(b"IEND", b""),
            "empty IDAT": (
                _PNG_SIGNATURE
                + ihdr
                + _chunk(b"IDAT", b"")
                + _chunk(b"IEND", b"")
            ),
        }
        for label, data in cases.items():
            with self.subTest(label=label):
                self.assertIn("no IDAT image data", self._decode_error(data))

    def test_rejects_decompression_bomb_without_expanding_it(self):
        # A few KB of IDAT can expand to far more scanlines than the header
        # declares. Decoding must stop at the declared size instead of
        # materializing the whole stream (a decompression bomb).
        declared = 4  # 1x1 RGB: one filter byte + three channels
        bomb = bytes(declared) + bytes(16 * 1024 * 1024)
        data = png_with_idat(zlib.compress(bomb))
        tracemalloc.start()
        try:
            message = self._decode_error(data)
            peak = tracemalloc.get_traced_memory()[1]
        finally:
            tracemalloc.stop()
        self.assertIn("more than the 4 bytes", message)
        self.assertLess(peak, 4 * 1024 * 1024)

    def test_rejects_truncated_stream_that_hits_declared_size(self):
        # A stream cut before its end marker can still yield exactly the
        # declared byte count. Accepting it would silently drop the adler32
        # check that zlib.decompress performed before this change.
        raw = bytes([0, 1, 2, 3])  # 1x1 RGB: filter byte + three channels
        truncated = zlib.compress(raw)[:-4]  # drop the trailing adler32
        data = png_with_idat(truncated)
        self.assertIn("truncated", self._decode_error(data))

    def test_rejects_corrupt_deflate_stream(self):
        # The IDAT CRC covers the chunk bytes but says nothing about whether
        # they are a valid deflate stream, so a download corrupted inside the
        # chunk reaches zlib.decompressobj and raises zlib.error. That must
        # become a PngError naming the corruption, not leak a raw zlib.error
        # past decode_png and read_png (which would print a traceback from the
        # CLI instead of a clean "fidelity: error:" line).
        data = png_with_idat(b"\xff\xff\xff\xff")
        self.assertIn("corrupt PNG image data", self._decode_error(data))

    def test_rejects_declared_image_over_pixel_limit(self):
        # A header may declare dimensions far larger than any screenshot; the
        # pixel limit must reject it before zlib decompresses anything.
        data = png_with_idat(
            zlib.compress(bytes(4)), width=100_000, height=100_000
        )
        message = self._decode_error(data)
        self.assertIn("100000x100000", message)
        self.assertIn(str(png._MAX_PIXELS), message)

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
        expected = b"".join(
            bytes(b for i, b in enumerate(row) if i % 4 != 3) for row in rows
        )
        self.assertEqual(png.decode_png(data).rgb, expected)

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

    def test_rejects_unknown_scanline_filter_type(self):
        # IHDR's filter method byte is separate from the filter type byte that
        # precedes each scanline. A corrupt row filter (5-255) must be named
        # rather than silently decoded with a wrong predictor, and the error
        # must name the row so the corrupt scanline can be located.
        data = make_png(
            1,
            3,
            [bytes([1, 2, 3]), bytes([4, 5, 6]), bytes([7, 8, 9])],
            filter_types=[0, 0, 5],
        )
        message = self._decode_error(data)
        self.assertIn("unsupported PNG filter type 5", message)
        self.assertIn("row 2", message)

    def test_rejects_non_png(self):
        with self.assertRaises(png.PngError):
            png.decode_png(b"not a png")

    def test_rejects_png_without_ihdr(self):
        # A chunk stream that reaches IDAT/IEND with no IHDR leaves decode_png
        # with no dimensions or colour type; it must name the missing chunk
        # rather than unpacking None or decoding against defaults.
        data = (
            _PNG_SIGNATURE
            + _chunk(b"IDAT", zlib.compress(b"\x00"))
            + _chunk(b"IEND", b"")
        )
        self.assertIn("no IHDR", self._decode_error(data))

    def test_rejects_ihdr_with_wrong_length(self):
        # IHDR is fixed at 13 bytes; any other length cannot be unpacked as
        # width/height/depth/colour/compression/filter/interlace, so it must be
        # rejected by length, naming the actual and expected sizes. The CLI test
        # test_fidelity_cli.TestCli.test_malformed_png_is_error already drives
        # this guard end-to-end; this test pins the message it does not assert.
        data = (
            _PNG_SIGNATURE
            + _chunk(b"IHDR", b"\x00" * 12)
            + _chunk(b"IEND", b"")
        )
        message = self._decode_error(data)
        self.assertIn("12 bytes", message)
        self.assertIn("expected 13", message)

    def test_palette_color_type_without_plte_names_missing_chunk(self):
        # Color type 3 indexes a PLTE table; without one there is no colour to
        # map an index to, so the failure must name the missing chunk instead
        # of indexing a None palette.
        data = make_png(1, 1, [bytes([0])], color_type=3, palette=None)
        self.assertIn("no PLTE", self._decode_error(data))

    def test_rejects_bad_chunk_crc(self):
        # Every PNG chunk carries a CRC over its type and payload; a mismatch
        # means a corrupted header or palette, which would otherwise decode to
        # silently wrong pixels and poison the comparison. The failure must
        # name the chunk, its offset, and both CRC values, so the corruption
        # can be located without re-deriving them by hand.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        corrupted = bytearray(data)
        (ihdr_length,) = struct.unpack(">I", data[8:12])
        crc_offset = data.rindex(b"IHDR") + 4 + ihdr_length
        corrupted[crc_offset] ^= 0xFF
        message = self._decode_error(bytes(corrupted))
        self.assertIn("IHDR", message)
        self.assertIn("CRC", message)
        self.assertIn(f"offset {data.rindex(b'IHDR') - 4}", message)
        self.assertIn(
            f"stored 0x{int.from_bytes(corrupted[crc_offset:crc_offset + 4], 'big'):08x}",
            message,
        )
        self.assertIn(
            f"computed 0x{int.from_bytes(data[crc_offset:crc_offset + 4], 'big'):08x}",
            message,
        )

    def test_rejects_truncated_chunk_crc(self):
        # Cutting the final CRC byte must name the chunk and the offset of the
        # missing CRC, so the user can find the truncation point.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        message = self._decode_error(data[:-1])
        self.assertIn("truncated PNG chunk 'IEND' CRC", message)
        self.assertIn(f"offset {data.rindex(b'IEND') + 4}", message)
        self.assertIn("expected 4 bytes, got 3", message)

    def test_rejects_truncated_chunk_payload(self):
        # A chunk header declaring more payload than the file holds must name
        # the chunk, its offset, and the byte counts, not just say "truncated".
        ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        data = _PNG_SIGNATURE + ihdr + struct.pack(">I", 100) + b"IDAT" + b"\x00\x01"
        message = self._decode_error(data)
        self.assertIn("truncated PNG chunk 'IDAT'", message)
        self.assertIn("offset 33", message)
        self.assertIn("declared 100 payload bytes, only 2 present", message)

    def test_rejects_unknown_compression_method(self):
        # The IHDR compression and filter methods are separate fields; naming
        # the offending value tells the user which one to fix.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        broken = with_ihdr_byte(data, 10, 1)
        self.assertIn("compression method 1", self._decode_error(broken))

    def test_rejects_unknown_filter_method(self):
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        broken = with_ihdr_byte(data, 11, 1)
        self.assertIn("filter method 1", self._decode_error(broken))

    def test_rejects_unsupported_ihdr_fields(self):
        # IHDR's bit depth, color type, interlace flag and dimensions each
        # change how scanlines are interpreted. If a guard regressed, a 16-bit
        # or interlaced image would be silently decoded as 8-bit non-interlaced
        # (wrong pixels), an unknown color type would KeyError in _CHANNELS, and
        # a zero dimension would produce a degenerate image. Each must be
        # rejected by name before any scanline work.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        cases = {
            # offset 8 is the bit-depth field.
            "bit depth 16": (with_ihdr_byte(data, 8, 16), "bit depth 16"),
            # offset 9 is the color-type field; 5 is outside the supported set.
            "color type 5": (with_ihdr_byte(data, 9, 5), "color type 5"),
            # offset 12 is the interlace field.
            "interlaced": (with_ihdr_byte(data, 12, 1), "interlaced"),
            # offset 3 is the last width byte; the 1x1 image's width becomes 0.
            "zero width": (with_ihdr_byte(data, 3, 0), "zero width or height"),
            # offset 7 is the last height byte.
            "zero height": (with_ihdr_byte(data, 7, 0), "zero width or height"),
        }
        for label, (broken, expected) in cases.items():
            with self.subTest(label=label):
                self.assertIn(expected, self._decode_error(broken))

    def test_read_png_rejects_oversize_file_without_reading_it_all(self):
        # read_png reads the whole file before decode_png sees its header, so
        # an oversize file would be loaded into memory first. The read must
        # stop at the cap. Patch the cap down so the fixture stays small.
        limit = 4096
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oversize.png"
            path.write_bytes(b"\x00" * (limit + 1))
            with mock.patch.object(png, "_MAX_FILE_BYTES", limit):
                tracemalloc.start()
                try:
                    with self.assertRaises(png.PngError) as ctx:
                        png.read_png(path)
                    peak = tracemalloc.get_traced_memory()[1]
                finally:
                    tracemalloc.stop()
        self.assertIn(str(limit), str(ctx.exception))
        self.assertLess(peak, limit + 1024 * 1024)

    def test_read_png_names_undecodable_file(self):
        # A decode failure must name the file it came from, so a two-input
        # invocation can tell which of the candidate/reference was bad.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.png"
            path.write_bytes(b"not a png")
            with self.assertRaises(png.PngError) as ctx:
                png.read_png(path)
            self.assertIn(str(path), str(ctx.exception))

    def test_read_png_rejects_a_fifo_instead_of_blocking(self):
        # open() on a FIFO blocks until a writer appears, and read() on a pipe
        # whose writer never sends or closes blocks forever; the byte cap
        # bounds neither wait. read_png must reject a non-regular file. Run it
        # in a child, since a direct call would hang this test, and require it
        # to exit before the timeout.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        with tempfile.TemporaryDirectory() as tmp:
            fifo = Path(tmp) / "pipe.png"
            os.mkfifo(fifo)
            child = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.path.insert(0, sys.argv[1]); import png; "
                    "png.read_png(sys.argv[2])",
                    str(REPO_ROOT / "tools"),
                    str(fifo),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
        self.assertNotEqual(child.returncode, 0)
        self.assertIn("not a regular file", child.stderr)


class TestUnfilterLanes(unittest.TestCase):
    """The Sub and Up scanline filters reconstruct rows with big-integer lane
    operations; pin those against a per-byte oracle and an encode/decode
    round-trip so a carry or a truncated scan step cannot slip through."""

    def test_byte_add_matches_oracle(self):
        rng = random.Random(0x86)
        for length in (0, 1, 2, 3, 7, 8, 255, 256, 1024):
            with self.subTest(length=length):
                a = bytes(rng.randrange(256) for _ in range(length))
                b = bytes(rng.randrange(256) for _ in range(length))
                expected = bytes((x + y) & 0xFF for x, y in zip(a, b))
                self.assertEqual(png._byte_add(a, b), expected)

    def test_byte_add_wraps_without_carrying_between_bytes(self):
        # 0xFF + 0x01 must wrap to 0x00 without carrying into the next byte;
        # a leaked carry would turn the following byte into 0x01 instead.
        self.assertEqual(
            png._byte_add(bytes([0xFF, 0x00, 0xFF]), bytes([0x01, 0x00, 0x01])),
            bytes([0x00, 0x00, 0x00]),
        )

    def test_prefix_sum_matches_oracle(self):
        rng = random.Random(0x1999)
        for length in (0, 1, 2, 3, 7, 8, 100, 255, 256, 1024):
            with self.subTest(length=length):
                channel = bytes(rng.randrange(256) for _ in range(length))
                out = bytearray(channel)
                for i in range(1, len(out)):
                    out[i] = (out[i] + out[i - 1]) & 0xFF
                self.assertEqual(png._prefix_sum(channel), bytes(out))

    def test_sub_and_up_filters_roundtrip_random_rows(self):
        # Encode random rows using only Sub and Up filters and decode them
        # back; any per-byte carry or truncated scan step shows up as a
        # mismatched pixel. Widths include 1 so the scan length is 1.
        rng = random.Random(0x8_6)
        for width, color_type in (
            (1, 0),
            (2, 2),
            (3, 2),
            (5, 2),
            (3, 4),
            (4, 6),
            (9, 6),
        ):
            channels = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
            rows = [
                bytes(rng.randrange(256) for _ in range(width * channels))
                for _ in range(6)
            ]
            data = make_png(
                width,
                len(rows),
                rows,
                color_type=color_type,
                filter_types=[1, 2, 1, 2, 1, 2],
            )
            if color_type == 6:
                expected = b"".join(
                    bytes(b for i, b in enumerate(row) if i % 4 != 3)
                    for row in rows
                )
            elif color_type == 0:
                expected = b"".join(
                    bytes(b for g in row for b in (g, g, g)) for row in rows
                )
            elif color_type == 4:
                expected = b"".join(
                    bytes(b for i in range(0, len(row), 2) for b in (row[i],) * 3)
                    for row in rows
                )
            else:
                expected = b"".join(rows)
            with self.subTest(width=width, color_type=color_type):
                self.assertEqual(png.decode_png(data).rgb, expected)


class TestPaethDeltaTable(unittest.TestCase):
    """The Paeth delta table is filled from a closed-form block layout rather
    than a predictor call per cell; pin every cell against the per-entry
    predictor so a wrong block boundary cannot decode a row to a plausible but
    wrong value."""

    def test_table_matches_per_entry_oracle(self):
        expected = bytearray(511 * 512)
        for da in range(-255, 256):
            base = (da + 255) << 9
            for db in range(-255, 256):
                expected[base + db + 255] = _paeth(da, db, 0) & 0xFF
        original = png._PAETH_DELTA
        png._PAETH_DELTA = None
        try:
            table = png._paeth_delta_table()
        finally:
            png._PAETH_DELTA = original
        self.assertEqual(table, bytes(expected))

    def test_table_is_built_once_and_reused(self):
        original = png._PAETH_DELTA
        png._PAETH_DELTA = None
        try:
            first = png._paeth_delta_table()
            self.assertIs(png._paeth_delta_table(), first)
        finally:
            png._PAETH_DELTA = original

