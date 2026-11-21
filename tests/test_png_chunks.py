"""Tests for ``tools/png/stream.py``'s chunk ordering, through ``decode_png``.

The PNG stream is a sequence of length/type/payload/CRC chunks. These tests
pin the container layer: that a valid image may split its zlib stream across
several IDAT chunks or carry unknown ancillary chunks, and that the decoder
rejects malformed chunk ordering -- unknown critical chunks, a missing,
duplicated or out-of-position IHDR, non-consecutive IDAT chunks, a PLTE or
tRNS chunk after the image data, a non-empty IEND payload and a missing
PLTE/IEND. Byte framing (chunk types, length caps, CRC checks and the
truncation diagnostics) and the ``iter_chunks`` iterator live in
``test_png_chunk_framing.py``; header-field validation keeps its tests here,
and the tRNS length rules in ``test_png_malformed``.
Scanline decoding lives in ``test_png_decode``; the malformed-image-data
and resource-limit rejections live in ``test_png_malformed``.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import struct
import unittest
import zlib

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.png_fixtures import (  # noqa: E402
    _chunk,
    decode_error_message,
    ihdr_chunk,
    make_png,
    png_stream,
    rgb_image,
    solid_rgb,
    splice_after_ihdr,
    with_ihdr_byte,
)
from tools import png


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

    def test_rejects_idat_chunks_that_are_not_consecutive(self):
        # PNG requires the IDAT chunks to be consecutive. An ancillary chunk
        # between two IDATs leaves a stream whose concatenated payload still
        # inflates, so without an ordering check the decoder accepts a file
        # that a conformant reader rejects.
        compressed = zlib.compress(b"\x00\x01\x02\x03")
        split = len(compressed) // 2
        data = png_stream(
            ihdr_chunk(1, 1, 2),
            _chunk(b"IDAT", compressed[:split]),
            _chunk(b"tEXt", b"Software\x00x"),
            _chunk(b"IDAT", compressed[split:]),
            _chunk(b"IEND", b""),
        )
        message = decode_error_message(self, data)
        self.assertIn("IDAT", message)
        self.assertIn("consecutive", message)

    def test_rejects_plte_after_idat(self):
        # PLTE must precede the image data. A palette arriving after IDAT
        # would still be used to expand the indices even though the PNG spec
        # puts it before the first IDAT.
        data = png_stream(
            ihdr_chunk(1, 1, 3),
            _chunk(b"IDAT", zlib.compress(b"\x00\x00")),
            _chunk(b"PLTE", bytes([1, 2, 3])),
            _chunk(b"IEND", b""),
        )
        message = decode_error_message(self, data)
        self.assertIn("PLTE", message)
        self.assertIn("precede IDAT", message)

    def test_rejects_trns_after_idat(self):
        # tRNS must also precede IDAT; accepted late, it would change the
        # decoded alpha of an otherwise conformant-looking image.
        data = png_stream(
            ihdr_chunk(1, 1, 0),
            _chunk(b"IDAT", zlib.compress(b"\x00\x07")),
            _chunk(b"tRNS", struct.pack(">H", 7)),
            _chunk(b"IEND", b""),
        )
        message = decode_error_message(self, data)
        self.assertIn("tRNS", message)
        self.assertIn("precede IDAT", message)

    def test_rejects_a_chunk_after_iend(self):
        # IEND marks the end of the PNG datastream and must be last. A complete
        # chunk after it would otherwise be silently ignored, so the decoder
        # would accept a file whose trailing data a conformant reader refuses.
        _, data = rgb_image(1, 1, lambda x, y: (1, 2, 3))
        trailing = data + _chunk(b"tEXt", b"Software\x00x")
        message = decode_error_message(self, trailing)
        self.assertIn("after IEND", message)
        self.assertIn("last chunk", message)

    def test_rejects_a_second_idat_after_iend(self):
        # A second IDAT after IEND is not image data: the first IEND already
        # ended the stream. Without the guard it is dropped silently, while a
        # conformant reader treats it as malformed trailing data.
        _, data = rgb_image(1, 1, lambda x, y: (1, 2, 3))
        trailing = data + _chunk(b"IDAT", zlib.compress(b"\x00\x04\x05\x06"))
        message = decode_error_message(self, trailing)
        self.assertIn("IDAT", message)
        self.assertIn("after IEND", message)

    def test_rejects_a_trailing_fragment_after_iend(self):
        # A file can also end part-way through a chunk after IEND: 1-7 bytes
        # are too short to carry a length and type, so the framing loop used
        # to exit and drop them, and decode_png returned the image. Those
        # bytes follow the datastream's end, so they are malformed trailing
        # data and must be refused just like a complete chunk after IEND.
        _, data = rgb_image(1, 1, lambda x, y: (1, 2, 3))
        chunk = _chunk(b"tEXt", b"Software\x00x")
        for length in range(1, 8):
            with self.subTest(length=length):
                message = decode_error_message(self, data + chunk[:length])
                self.assertIn("trailing", message)
                self.assertIn("after IEND", message)
                self.assertIn("last chunk", message)

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
        message = decode_error_message(self, splice_after_ihdr(data, unknown))
        self.assertIn("unknown critical PNG chunk", message)
        self.assertIn("'XYZW'", message)

    def test_rejects_png_without_ihdr(self):
        # A chunk stream that reaches IDAT/IEND with no IHDR leaves decode_png
        # with no dimensions or colour type; it must name the missing chunk
        # rather than unpacking None or decoding against defaults.
        data = png_stream(
            _chunk(b"IDAT", zlib.compress(b"\x00")),
            _chunk(b"IEND", b""),
        )
        self.assertIn("no IHDR", decode_error_message(self, data))

    def test_rejects_a_second_ihdr_chunk(self):
        # The image has one header. A second IHDR silently redefines the
        # dimensions and colour type the decoder uses -- here to a 2x2 image
        # whose 1x1 IDAT cannot satisfy it -- so a file that decodes
        # differently in a conformant viewer than here must be refused by
        # name instead of decoding against the later header.
        _, data = solid_rgb(1, 1)
        duplicated = splice_after_ihdr(data, ihdr_chunk(2, 2, 2))
        message = decode_error_message(self, duplicated)
        self.assertIn("more than one IHDR", message)

    def test_rejects_a_second_plte_chunk(self):
        # The palette is defined once. A second PLTE would silently replace
        # the table, so the same indices decode to pixels a conformant reader
        # never produces; refuse it by name.
        palette = bytes([10, 20, 30, 40, 50, 60])
        data = make_png(1, 1, [bytes([0])], color_type=3, palette=palette)
        duplicated = splice_after_ihdr(
            data, _chunk(b"PLTE", bytes([200, 0, 0]))
        )
        message = decode_error_message(self, duplicated)
        self.assertIn("more than one PLTE", message)

    def test_rejects_a_second_trns_chunk(self):
        # Likewise only one tRNS may define the out-of-band transparency. A
        # later chunk silently overriding an earlier one would change the
        # decoded alpha with no sign that the file is malformed.
        palette = bytes([10, 20, 30, 40, 50, 60])
        data = make_png(
            1, 1, [bytes([0])], color_type=3, palette=palette, trns=bytes([0])
        )
        duplicated = splice_after_ihdr(data, _chunk(b"tRNS", bytes([255])))
        message = decode_error_message(self, duplicated)
        self.assertIn("more than one tRNS", message)

    def test_rejects_ihdr_that_is_not_the_first_chunk(self):
        # The PNG spec puts IHDR first. A stream that reaches IDAT before its
        # header is malformed framing; without this check the header that
        # arrives later would be used and the file accepted, while a
        # conformant reader rejects it. The diagnostic names both the
        # requirement and the chunk that came first.
        misordered = png_stream(
            _chunk(b"IDAT", zlib.compress(b"\x00\x01\x02\x03")),
            ihdr_chunk(1, 1, 2),
            _chunk(b"IEND", b""),
        )
        message = decode_error_message(self, misordered)
        self.assertIn("IHDR", message)
        self.assertIn("first chunk", message)
        self.assertIn("IDAT", message)

    def test_rejects_ihdr_with_wrong_length(self):
        # IHDR is fixed at 13 bytes; any other length cannot be unpacked as
        # width/height/depth/colour/compression/filter/interlace, so it must be
        # rejected by length, naming the actual and expected sizes. The CLI test
        # test_fidelity_cli.TestCli.test_malformed_png_is_error already drives
        # this guard end-to-end; this test pins the message it does not assert.
        data = png_stream(
            _chunk(b"IHDR", b"\x00" * 12),
            _chunk(b"IEND", b""),
        )
        message = decode_error_message(self, data)
        self.assertIn("12 bytes", message)
        self.assertIn("expected 13", message)

    def test_palette_color_type_without_plte_names_missing_chunk(self):
        # Color type 3 indexes a PLTE table; without one there is no colour to
        # map an index to, so the failure must name the missing chunk instead
        # of indexing a None palette.
        data = make_png(1, 1, [bytes([0])], color_type=3, palette=None)
        self.assertIn("no PLTE", decode_error_message(self, data))

    def test_rejects_an_iend_with_a_payload(self):
        # The PNG spec gives IEND an empty data field. A non-empty one is
        # malformed framing, and dropping its payload silently would decode a
        # file a conformant reader refuses as if it were whole.
        _, data = rgb_image(2, 1, lambda x, y: (x * 10, y * 20, 30))
        head = data[: data.rindex(b"IEND") - 4]
        bad = head + _chunk(b"IEND", b"\x00")
        message = decode_error_message(self, bad)
        self.assertIn("IEND", message)
        self.assertIn("payload", message)

    def test_rejects_png_without_end_marker(self):
        # IEND terminates the chunk stream. A file cut at a chunk boundary
        # keeps a complete IHDR and IDAT but has no end marker; decoding it
        # as a whole image would hide the truncation, so it must be named.
        _, data = solid_rgb(1, 1)
        stripped = data[: data.rindex(b"IEND") - 4]
        self.assertNotIn(b"IEND", stripped)
        self.assertIn("no IEND chunk", decode_error_message(self, stripped))

    def test_rejects_unknown_compression_method(self):
        # The IHDR compression and filter methods are separate fields; naming
        # the offending value tells the user which one to fix.
        _, data = solid_rgb(1, 1)
        broken = with_ihdr_byte(data, 10, 1)
        self.assertIn("compression method 1", decode_error_message(self, broken))

    def test_rejects_unknown_filter_method(self):
        _, data = solid_rgb(1, 1)
        broken = with_ihdr_byte(data, 11, 1)
        self.assertIn("filter method 1", decode_error_message(self, broken))

    def test_rejects_unsupported_ihdr_fields(self):
        # IHDR's bit depth, color type, interlace flag and dimensions each
        # change how scanlines are interpreted. If a guard regressed, a 16-bit
        # or interlaced image would be silently decoded as 8-bit non-interlaced
        # (wrong pixels), an unknown color type would KeyError in CHANNELS, and
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
                self.assertIn(expected, decode_error_message(self, broken))

    def test_unsupported_color_type_names_the_supported_set(self):
        # The color type decides how scanlines are interpreted, so a rejected
        # value must name the types the decoder handles instead of leaving the
        # operator to look up which PNG color types are valid. The set is the
        # five the PNG spec defines; pin the literal text so a wrong set in
        # the diagnostic fails here rather than reading as plausible.
        _, data = solid_rgb(1, 1)
        broken = with_ihdr_byte(data, 9, 5)
        message = decode_error_message(self, broken)
        self.assertIn("unsupported PNG color type 5", message)
        self.assertIn("need one of 0, 2, 3, 4, 6", message)

    def test_interlaced_png_names_the_re_export_fix(self):
        # An interlaced PNG cannot be decoded here, and the operator's fix is
        # to re-export it without interlacing; name that fix the way the
        # wrong-format message names its conversion.
        _, data = solid_rgb(1, 1)
        broken = with_ihdr_byte(data, 12, 1)
        self.assertIn(
            "re-export it without interlacing", decode_error_message(self, broken)
        )


if __name__ == "__main__":
    unittest.main()
