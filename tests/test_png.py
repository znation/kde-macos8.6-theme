"""Tests for tools/png.py -- the PNG reader behind the fidelity tool.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import struct
import sys
import tempfile
import tracemalloc
import unittest
import zlib
from unittest import mock
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import png  # noqa: E402
from png_fixtures import (  # noqa: E402
    _PNG_SIGNATURE,
    _chunk,
    make_png,
    rgb_image,
    with_ihdr_byte,
)


class TestDecode(unittest.TestCase):
    def test_rgb_roundtrip(self):
        image, data = rgb_image(3, 2, lambda x, y: (x * 10, y * 20, 30))
        self.assertEqual(png.decode_png(data), image)

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

    def test_palette(self):
        palette = bytes([255, 0, 0, 0, 255, 0])
        rows = [bytes([0, 1])]
        data = make_png(2, 1, rows, color_type=3, palette=palette)
        self.assertEqual(png.decode_png(data).rgb, bytes([255, 0, 0, 0, 255, 0]))

    def test_palette_index_outside_plte_names_index_and_size(self):
        # A palette image whose pixel index has no PLTE entry must name the
        # offending index and the palette size, or the user cannot tell which
        # pixel is bad or how short the palette is.
        palette = bytes([255, 0, 0])  # one entry: index 0 only
        data = make_png(1, 1, [bytes([1])], color_type=3, palette=palette)
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(data)
        message = str(ctx.exception)
        self.assertIn("index 1", message)
        self.assertIn("3 bytes", message)

    def test_palette_length_not_multiple_of_three(self):
        # A PLTE whose length is not a multiple of 3 ends in a partial RGB
        # entry. Index 0 would still decode, so without this check a malformed
        # palette passes silently as long as no pixel uses the bad entry.
        palette = bytes([255, 0, 0, 0])  # 4 bytes: index 1 is a partial entry
        data = make_png(1, 1, [bytes([0])], color_type=3, palette=palette)
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(data)
        message = str(ctx.exception)
        self.assertIn("4 bytes", message)
        self.assertIn("multiple of 3", message)

    def test_palette_longer_than_256_entries(self):
        # The PNG spec caps PLTE at 256 entries (768 bytes); 771 bytes is 257
        # entries (a whole multiple of 3, so the length check cannot reject it
        # on the modulo alone) and must be reported with its actual size.
        palette = bytes(771)
        data = make_png(1, 1, [bytes([0])], color_type=3, palette=palette)
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(data)
        message = str(ctx.exception)
        self.assertIn("771 bytes", message)
        self.assertIn("768", message)

    def test_truncated_image_data_names_actual_and_expected(self):
        # An IDAT that decompresses to fewer scanlines than IHDR's height
        # declares must name how many bytes arrived and how many were needed,
        # so a truncated file is distinguishable from other corruption.
        data = make_png(3, 3, [bytes(9)])
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(data)
        self.assertIn(
            "got 10 bytes, expected 30 for a 3x3 image", str(ctx.exception)
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
                with self.assertRaises(png.PngError) as ctx:
                    png.decode_png(data)
                self.assertIn("no IDAT image data", str(ctx.exception))

    def test_rejects_decompression_bomb_without_expanding_it(self):
        # A few KB of IDAT can expand to far more scanlines than the header
        # declares. Decoding must stop at the declared size instead of
        # materializing the whole stream (a decompression bomb).
        declared = 4  # 1x1 RGB: one filter byte + three channels
        bomb = bytes(declared) + bytes(16 * 1024 * 1024)
        ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
        data = (
            _PNG_SIGNATURE
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bomb))
            + _chunk(b"IEND", b"")
        )
        tracemalloc.start()
        try:
            with self.assertRaises(png.PngError) as ctx:
                png.decode_png(data)
            peak = tracemalloc.get_traced_memory()[1]
        finally:
            tracemalloc.stop()
        self.assertIn("more than the 4 bytes", str(ctx.exception))
        self.assertLess(peak, 4 * 1024 * 1024)

    def test_rejects_truncated_stream_that_hits_declared_size(self):
        # A stream cut before its end marker can still yield exactly the
        # declared byte count. Accepting it would silently drop the adler32
        # check that zlib.decompress performed before this change.
        raw = bytes([0, 1, 2, 3])  # 1x1 RGB: filter byte + three channels
        ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
        truncated = zlib.compress(raw)[:-4]  # drop the trailing adler32
        data = (
            _PNG_SIGNATURE
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", truncated)
            + _chunk(b"IEND", b"")
        )
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(data)
        self.assertIn("truncated", str(ctx.exception))

    def test_rejects_declared_image_over_pixel_limit(self):
        # A header may declare dimensions far larger than any screenshot; the
        # pixel limit must reject it before zlib decompresses anything.
        ihdr = struct.pack(">IIBBBBB", 100_000, 100_000, 8, 2, 0, 0, 0)
        data = (
            _PNG_SIGNATURE
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(4)))
            + _chunk(b"IEND", b"")
        )
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(data)
        message = str(ctx.exception)
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
        # rather than silently decoded with a wrong predictor.
        data = make_png(1, 1, [bytes([1, 2, 3])], filter_types=[5])
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(data)
        self.assertIn("unsupported PNG filter type 5", str(ctx.exception))

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
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(data)
        self.assertIn("no IHDR", str(ctx.exception))

    def test_rejects_ihdr_with_wrong_length(self):
        # IHDR is fixed at 13 bytes; any other length cannot be unpacked as
        # width/height/depth/colour/compression/filter/interlace, so it must be
        # rejected by length, naming the actual and expected sizes. The CLI test
        # test_fidelity.TestCli.test_malformed_png_is_error already drives this
        # guard end-to-end; this test pins the message it does not assert.
        data = (
            _PNG_SIGNATURE
            + _chunk(b"IHDR", b"\x00" * 12)
            + _chunk(b"IEND", b"")
        )
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(data)
        message = str(ctx.exception)
        self.assertIn("12 bytes", message)
        self.assertIn("expected 13", message)

    def test_palette_color_type_without_plte_names_missing_chunk(self):
        # Color type 3 indexes a PLTE table; without one there is no colour to
        # map an index to, so the failure must name the missing chunk instead
        # of indexing a None palette.
        data = make_png(1, 1, [bytes([0])], color_type=3, palette=None)
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(data)
        self.assertIn("no PLTE", str(ctx.exception))

    def test_rejects_bad_chunk_crc(self):
        # Every PNG chunk carries a CRC over its type and payload; a mismatch
        # means a corrupted header or palette, which would otherwise decode to
        # silently wrong pixels and poison the comparison.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        corrupted = bytearray(data)
        corrupted[29] ^= 0xFF  # first byte of the IHDR chunk's CRC
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(bytes(corrupted))
        self.assertIn("IHDR", str(ctx.exception))
        self.assertIn("CRC", str(ctx.exception))

    def test_rejects_truncated_chunk_crc(self):
        # Cutting the final CRC byte must name the chunk and the offset of the
        # missing CRC, so the user can find the truncation point.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(data[:-1])
        message = str(ctx.exception)
        self.assertIn("truncated PNG chunk 'IEND' CRC", message)
        self.assertIn(f"offset {data.rindex(b'IEND') + 4}", message)
        self.assertIn("expected 4 bytes, got 3", message)

    def test_rejects_truncated_chunk_payload(self):
        # A chunk header declaring more payload than the file holds must name
        # the chunk, its offset, and the byte counts, not just say "truncated".
        ihdr = _chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        data = _PNG_SIGNATURE + ihdr + struct.pack(">I", 100) + b"IDAT" + b"\x00\x01"
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(data)
        message = str(ctx.exception)
        self.assertIn("truncated PNG chunk 'IDAT'", message)
        self.assertIn("offset 33", message)
        self.assertIn("declared 100 payload bytes, only 2 present", message)

    def test_rejects_unknown_compression_method(self):
        # The IHDR compression and filter methods are separate fields; naming
        # the offending value tells the user which one to fix.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        broken = with_ihdr_byte(data, 10, 1)
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(broken)
        self.assertIn("compression method 1", str(ctx.exception))

    def test_rejects_unknown_filter_method(self):
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        broken = with_ihdr_byte(data, 11, 1)
        with self.assertRaises(png.PngError) as ctx:
            png.decode_png(broken)
        self.assertIn("filter method 1", str(ctx.exception))

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
                with self.assertRaises(png.PngError) as ctx:
                    png.decode_png(broken)
                self.assertIn(expected, str(ctx.exception))

    def test_read_png_rejects_oversize_file_without_reading_it_all(self):
        # read_png reads the whole file before decode_png sees its header, so
        # an oversize file (or an endless stream such as /dev/zero) would be
        # loaded into memory first. The read must stop at the cap. Patch the
        # cap down so the fixture stays small.
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

