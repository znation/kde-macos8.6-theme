"""Tests for tools/png.py -- the PNG reader behind the fidelity tool.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import struct
import sys
import tempfile
import unittest
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

    def test_grayscale_and_rgba(self):
        gray = make_png(2, 1, [bytes([7, 200])], color_type=0)
        self.assertEqual(png.decode_png(gray).rgb, bytes([7, 7, 7, 200, 200, 200]))
        # Two pixels so dropping the alpha byte is checked across a stride
        # rather than only at the first pixel.
        rgba = make_png(2, 1, [bytes([1, 2, 3, 4, 5, 6, 7, 8])], color_type=6)
        self.assertEqual(png.decode_png(rgba).rgb, bytes([1, 2, 3, 5, 6, 7]))

    def test_rejects_non_png(self):
        with self.assertRaises(png.PngError):
            png.decode_png(b"not a png")

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

    def test_read_png_names_undecodable_file(self):
        # A decode failure must name the file it came from, so a two-input
        # invocation can tell which of the candidate/reference was bad.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.png"
            path.write_bytes(b"not a png")
            with self.assertRaises(png.PngError) as ctx:
                png.read_png(path)
            self.assertIn(str(path), str(ctx.exception))

