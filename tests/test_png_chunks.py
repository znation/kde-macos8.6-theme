"""Tests for tools/png.py's decode_png -- chunk framing.

The PNG stream is a sequence of length/type/payload/CRC chunks. These tests
pin the container layer: that a valid image may split its zlib stream across
several IDAT chunks or carry unknown ancillary chunks, and that the decoder
rejects malformed framing -- unknown critical chunks, bad chunk types,
oversized lengths, bad or truncated CRCs, a missing IHDR/PLTE/IEND and
unsupported IHDR fields. Scanline decoding lives in ``test_png_decode``; the
malformed-image-data and resource-limit rejections live in
``test_png_malformed``.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import struct
import unittest
import zlib

import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import png
from png_fixtures import (  # noqa: E402
    _PNG_SIGNATURE,
    _chunk,
    decode_error,
    ihdr_chunk,
    ihdr_end,
    make_png,
    rgb_image,
    solid_rgb,
    splice_after_ihdr,
    with_ihdr_byte,
)


class TestChunkFraming(unittest.TestCase):
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
        ancillary = (
            _chunk(b"gAMA", struct.pack(">I", 45455))
            + _chunk(b"tEXt", b"Software\x00Mac OS 8.6")
            + _chunk(b"pHYs", struct.pack(">IIB", 2835, 2835, 1))
        )
        augmented = splice_after_ihdr(data, ancillary)
        self.assertEqual(png.decode_png(augmented), image)

    def test_rejects_unknown_critical_chunk(self):
        # A chunk whose first byte is uppercase is critical: the decoder does
        # not model it, so it cannot know whether the chunk changes the
        # pixels. Silently ignoring it, as unknown ancillary chunks are
        # ignored, could decode the image wrong with no sign of a skipped
        # chunk; the error names the offending type.
        _, data = solid_rgb(1, 1)
        unknown = _chunk(b"XYZW", b"\x00\x01")
        message = decode_error(self, splice_after_ihdr(data, unknown))
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
        for ctype in (b"ab1d", b"a bd", b"ab\xffd"):
            with self.subTest(ctype=ctype):
                message = decode_error(
                    self, splice_after_ihdr(data, _chunk(ctype, b"\x00"))
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
        message = decode_error(self, data[:boundary] + oversized)
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
        text = _chunk(b"tEXt", b"note")
        corrupt = text[:-1] + bytes([text[-1] ^ 0xFF])
        message = decode_error(self, splice_after_ihdr(data, corrupt))
        self.assertIn("tEXt", message)
        self.assertIn("CRC", message)

    def test_rejects_png_without_ihdr(self):
        # A chunk stream that reaches IDAT/IEND with no IHDR leaves decode_png
        # with no dimensions or colour type; it must name the missing chunk
        # rather than unpacking None or decoding against defaults.
        data = (
            _PNG_SIGNATURE
            + _chunk(b"IDAT", zlib.compress(b"\x00"))
            + _chunk(b"IEND", b"")
        )
        self.assertIn("no IHDR", decode_error(self, data))

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
        message = decode_error(self, data)
        self.assertIn("12 bytes", message)
        self.assertIn("expected 13", message)

    def test_palette_color_type_without_plte_names_missing_chunk(self):
        # Color type 3 indexes a PLTE table; without one there is no colour to
        # map an index to, so the failure must name the missing chunk instead
        # of indexing a None palette.
        data = make_png(1, 1, [bytes([0])], color_type=3, palette=None)
        self.assertIn("no PLTE", decode_error(self, data))

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
        message = decode_error(self, bytes(corrupted))
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
        message = decode_error(self, data[:-1])
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
        self.assertIn("no IEND chunk", decode_error(self, stripped))

    def test_rejects_truncated_chunk_payload(self):
        # A chunk header declaring more payload than the file holds must name
        # the chunk, its offset, and the byte counts, not just say "truncated".
        ihdr = ihdr_chunk(1, 1, 2)
        data = _PNG_SIGNATURE + ihdr + struct.pack(">I", 100) + b"IDAT" + b"\x00\x01"
        message = decode_error(self, data)
        self.assertIn("truncated PNG chunk 'IDAT'", message)
        self.assertIn("offset 33", message)
        self.assertIn("declared 100 payload bytes, only 2 present", message)

    def test_rejects_unknown_compression_method(self):
        # The IHDR compression and filter methods are separate fields; naming
        # the offending value tells the user which one to fix.
        _, data = solid_rgb(1, 1)
        broken = with_ihdr_byte(data, 10, 1)
        self.assertIn("compression method 1", decode_error(self, broken))

    def test_rejects_unknown_filter_method(self):
        _, data = solid_rgb(1, 1)
        broken = with_ihdr_byte(data, 11, 1)
        self.assertIn("filter method 1", decode_error(self, broken))

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
                self.assertIn(expected, decode_error(self, broken))
