"""Tests for tools/png.py's decode_png -- scanline decoding, chunk framing,
and the resource limits that guard malformed input.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import struct
import sys
import tracemalloc
import unittest
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import png  # noqa: E402
from png_fixtures import (  # noqa: E402
    _PNG_SIGNATURE,
    _chunk,
    ihdr_chunk,
    ihdr_end,
    make_png,
    png_with_idat,
    rgb_from_rows,
    rgb_image,
    solid_rgb,
    with_ihdr_byte,
)


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

    def test_ignores_unknown_ancillary_chunks(self):
        # Real screenshots carry ancillary chunks (gAMA, sRGB, pHYs, tEXt,
        # iCCP) between IHDR and IDAT that decode_png does not model. The PNG
        # spec has a decoder ignore unknown ancillary chunks, so their presence
        # must not change the decoded pixels; a regression that rejected them
        # would refuse nearly every real reference image. Insert a gAMA, tEXt
        # and pHYs chunk after the fixed 25-byte IHDR chunk and compare to the
        # same PNG without them.
        image, data = rgb_image(2, 1, lambda x, y: (x * 40, 7, 200))
        boundary = ihdr_end(data)
        ancillary = (
            _chunk(b"gAMA", struct.pack(">I", 45455))
            + _chunk(b"tEXt", b"Software\x00Mac OS 8.6")
            + _chunk(b"pHYs", struct.pack(">IIB", 2835, 2835, 1))
        )
        augmented = data[:boundary] + ancillary + data[boundary:]
        self.assertEqual(png.decode_png(augmented), image)

    def test_rejects_unknown_critical_chunk(self):
        # A chunk whose first byte is uppercase is critical: the decoder does
        # not model it, so it cannot know whether the chunk changes the
        # pixels. Silently ignoring it, as unknown ancillary chunks are
        # ignored, could decode the image wrong with no sign of a skipped
        # chunk; the error names the offending type.
        _, data = solid_rgb(1, 1)
        boundary = ihdr_end(data)
        unknown = _chunk(b"XYZW", b"\x00\x01")
        message = self._decode_error(data[:boundary] + unknown + data[boundary:])
        self.assertIn("unknown critical PNG chunk", message)
        self.assertIn("'XYZW'", message)

    def test_rejects_chunk_type_that_is_not_four_ascii_letters(self):
        # A PNG chunk type must be four ASCII letters, and the first byte
        # alone decides criticality. A type carrying a digit, space or
        # non-ASCII byte is not a valid code; because its first byte is not an
        # uppercase letter it used to fall through as an unknown *ancillary*
        # chunk and be ignored. Reject it by name instead of silently skipping
        # malformed framing.
        _, data = solid_rgb(1, 1)
        boundary = ihdr_end(data)
        for ctype in (b"ab1d", b"a bd", b"ab\xffd"):
            with self.subTest(ctype=ctype):
                message = self._decode_error(
                    data[:boundary] + _chunk(ctype, b"\x00") + data[boundary:]
                )
                self.assertIn("invalid PNG chunk type", message)
                self.assertIn("four ASCII letters", message)
                if ctype.isascii():
                    self.assertIn(repr(ctype.decode("ascii")), message)

    def test_rejects_chunk_length_above_the_spec_maximum(self):
        # A chunk length is a 32-bit unsigned field, but the PNG spec caps it
        # at 2**31 - 1; a value with the high bit set cannot be a real payload.
        # Without the cap it is compared against the bytes present and reported
        # as a truncated chunk, which blames the file's tail instead of its
        # invalid length. The error names the chunk, offset and declared length.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        boundary = ihdr_end(data)
        oversized = struct.pack(">I", 0x80000000) + b"IDAT"
        message = self._decode_error(data[:boundary] + oversized)
        self.assertIn("'IDAT'", message)
        self.assertIn("offset", message)
        self.assertIn("2147483648", message)
        self.assertIn("2147483647", message)

    def test_ignored_ancillary_chunk_still_has_its_crc_checked(self):
        # Ignoring a chunk's contents must not skip its integrity check: a
        # corrupt ancillary chunk means the file is damaged and could hide a
        # damaged IHDR/IDAT region, so it must be rejected by name even though
        # decode_png would otherwise discard it.
        _, data = solid_rgb(1, 1)
        boundary = ihdr_end(data)
        text = _chunk(b"tEXt", b"note")
        corrupt = text[:-1] + bytes([text[-1] ^ 0xFF])
        message = self._decode_error(data[:boundary] + corrupt + data[boundary:])
        self.assertIn("tEXt", message)
        self.assertIn("CRC", message)

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

    def test_palette_names_first_out_of_range_index_after_valid_pixels(self):
        # The table lookup fails only at the offending pixel, so an image whose
        # valid prefix expands before the bad index must still report the first
        # bad index and the palette size, not a different one.
        palette = bytes([255, 0, 0, 0, 255, 0])  # two entries: indices 0 and 1
        rows = [bytes([0, 1, 0, 2, 1])]  # index 2 is the first bad one
        data = make_png(5, 1, rows, color_type=3, palette=palette)
        message = self._decode_error(data)
        self.assertIn("index 2", message)
        self.assertIn("2 entries", message)

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
        ihdr = ihdr_chunk(1, 1, 2)
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

    def test_names_the_format_and_fix_of_a_non_png_image(self):
        # A reference from the set is often a JPEG (and sherlock_fandom.jpg is
        # a WebP payload), so a user can hand decode_png the wrong file. "not
        # a PNG file" alone reads as a corrupt PNG; naming the actual format
        # says which input was wrong, and naming the fix says what to do with
        # it. The reference set is the reason a user hits this, and its
        # workflow (README's fidelity check) is to save the surface as PNG.
        cases = (
            (b"\xff\xd8\xff\xe0" + b"\x00" * 8, "JPEG"),
            (b"GIF89a" + b"\x00" * 6, "GIF"),
            (b"GIF87a" + b"\x00" * 6, "GIF"),
            (b"RIFF\x24\x00\x00\x00WEBPVP8 " + b"\x00" * 8, "WebP"),
        )
        for data, expected in cases:
            with self.subTest(expected=expected):
                message = self._decode_error(data)
                self.assertIn("not a PNG file", message)
                self.assertIn(expected, message)
                self.assertIn("convert it to PNG", message)

    def test_unknown_bytes_keep_the_bare_not_a_png_message(self):
        # Only a known raster signature earns the format and fix hints;
        # arbitrary bytes must not be described as an image, nor told to
        # convert a format the decoder never identified.
        message = self._decode_error(b"not a png")
        self.assertIn("not a PNG file", message)
        self.assertNotIn("image", message)
        self.assertNotIn("convert", message)

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
        _, data = solid_rgb(1, 1)
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
        _, data = solid_rgb(1, 1)
        message = self._decode_error(data[:-1])
        self.assertIn("truncated PNG chunk 'IEND' CRC", message)
        self.assertIn(f"offset {data.rindex(b'IEND') + 4}", message)
        self.assertIn("expected 4 bytes, got 3", message)

    def test_rejects_png_without_end_marker(self):
        # IEND terminates the chunk stream. A file cut at a chunk boundary
        # keeps a complete IHDR and IDAT but has no end marker; decoding it
        # as a whole image would hide the truncation, so it must be named.
        _, data = solid_rgb(1, 1)
        stripped = data[: data.rindex(b"IEND") - 4]
        self.assertNotIn(b"IEND", stripped)
        self.assertIn("no IEND chunk", self._decode_error(stripped))

    def test_rejects_truncated_chunk_payload(self):
        # A chunk header declaring more payload than the file holds must name
        # the chunk, its offset, and the byte counts, not just say "truncated".
        ihdr = ihdr_chunk(1, 1, 2)
        data = _PNG_SIGNATURE + ihdr + struct.pack(">I", 100) + b"IDAT" + b"\x00\x01"
        message = self._decode_error(data)
        self.assertIn("truncated PNG chunk 'IDAT'", message)
        self.assertIn("offset 33", message)
        self.assertIn("declared 100 payload bytes, only 2 present", message)

    def test_rejects_unknown_compression_method(self):
        # The IHDR compression and filter methods are separate fields; naming
        # the offending value tells the user which one to fix.
        _, data = solid_rgb(1, 1)
        broken = with_ihdr_byte(data, 10, 1)
        self.assertIn("compression method 1", self._decode_error(broken))

    def test_rejects_unknown_filter_method(self):
        _, data = solid_rgb(1, 1)
        broken = with_ihdr_byte(data, 11, 1)
        self.assertIn("filter method 1", self._decode_error(broken))

    def test_rejects_unsupported_ihdr_fields(self):
        # IHDR's bit depth, color type, interlace flag and dimensions each
        # change how scanlines are interpreted. If a guard regressed, a 16-bit
        # or interlaced image would be silently decoded as 8-bit non-interlaced
        # (wrong pixels), an unknown color type would KeyError in _CHANNELS, and
        # a zero dimension would produce a degenerate image. Each must be
        # rejected by name before any scanline work.
        _, data = solid_rgb(1, 1)
        cases = {
            # offset 8 is the bit-depth field.
            "bit depth 16": (with_ihdr_byte(data, 8, 16), "bit depth 16"),
            # offset 9 is the color-type field; 5 is outside the supported set.
            "color type 5": (with_ihdr_byte(data, 9, 5), "color type 5"),
            # offset 12 is the interlace field.
            "interlaced": (with_ihdr_byte(data, 12, 1), "interlaced"),
            # offset 3 is the last width byte; the 1x1 image's width becomes 0.
            "zero width": (with_ihdr_byte(data, 3, 0), "zero width or height: 0x1"),
            # offset 7 is the last height byte.
            "zero height": (with_ihdr_byte(data, 7, 0), "zero width or height: 1x0"),
        }
        for label, (broken, expected) in cases.items():
            with self.subTest(label=label):
                self.assertIn(expected, self._decode_error(broken))


class TestToRgbUnsupportedColorType(unittest.TestCase):
    """``_to_rgb`` names a color type it has no expansion for.

    ``decode_png`` rejects a color type outside ``_CHANNELS`` before calling
    ``_to_rgb``, so the five types it handles are the only ones a real PNG can
    present. The helper's final guard is the contract that keeps a future
    ``_CHANNELS`` entry from silently decoding with the wrong expansion: adding
    a color type there without a matching branch here must fail loudly, naming
    the type. No PNG can drive that branch through ``decode_png``, so call the
    helper directly with the color types the PNG spec does not define.
    """

    def test_unsupported_color_type_names_the_type(self):
        for color_type in (1, 5, 7):
            with self.subTest(color_type=color_type):
                with self.assertRaises(png.PngError) as ctx:
                    png._to_rgb(color_type, b"", None)
                self.assertEqual(
                    str(ctx.exception),
                    f"unsupported PNG color type {color_type}",
                )
