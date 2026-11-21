"""Tests for ``tools/png/chunks.py``'s byte framing and iterator contract.

These tests pin how a byte stream is cut into chunks at all: that a chunk
type is four ASCII letters with an uppercase reserved third letter, that a
length stays at or under the spec maximum, that every chunk's CRC is checked
even when the chunk is ignored, and how truncation is named -- plus the
``iter_chunks`` iterator contract. The ordering, duplication and IEND rules
through ``decode_png`` stay in ``test_png_chunks.py``.
"""

from __future__ import annotations

import struct
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.png_fixtures import (
    _chunk, decode_error_message, ihdr_chunk, ihdr_end, png_stream, rgb_image,
    solid_rgb, splice_after_ihdr,
)
from tools import png
from tools.png import chunks


class TestChunkFramingRules(unittest.TestCase):
    def test_rejects_chunk_type_that_is_not_four_ascii_letters(self):
        _, data = solid_rgb(1, 1)
        for ctype in (b"ab1d", b"a bd", b"ab\xffd"):
            with self.subTest(ctype=ctype):
                message = decode_error_message(
                    self, splice_after_ihdr(data, _chunk(ctype, b"\x00"))
                )
                self.assertIn("invalid PNG chunk type", message)
                self.assertIn("four ASCII letters", message)
                if ctype.isascii():
                    self.assertIn(repr(ctype.decode("ascii")), message)

    def test_rejects_chunk_type_with_lowercase_reserved_bit(self):
        _, data = solid_rgb(1, 1)
        malformed = splice_after_ihdr(data, _chunk(b"abca", b""))
        message = decode_error_message(self, malformed)
        self.assertIn("invalid PNG chunk type", message)
        self.assertIn("reserved third letter must be uppercase", message)

    def test_rejects_chunk_length_above_the_spec_maximum(self):
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        boundary = ihdr_end(data)
        oversized = struct.pack(">I", 0x80000000) + b"IDAT"
        message = decode_error_message(self, data[:boundary] + oversized)
        self.assertIn("'IDAT'", message)
        self.assertIn("offset", message)
        self.assertIn("2147483648", message)
        self.assertIn("2147483647", message)

    def test_a_chunk_length_at_the_spec_maximum_is_not_refused_as_oversized(self):
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        boundary = ihdr_end(data)
        at_maximum = struct.pack(">I", 0x7FFFFFFF) + b"IDAT"
        message = decode_error_message(self, data[:boundary] + at_maximum)
        self.assertIn("truncated PNG chunk 'IDAT'", message)
        self.assertIn(f"offset {boundary}", message)
        self.assertIn("declared 2147483647 payload bytes", message)
        self.assertNotIn("above", message)

    def test_ignored_ancillary_chunk_still_has_its_crc_checked(self):
        _, data = solid_rgb(1, 1)
        text = _chunk(b"tEXt", b"note")
        corrupt = text[:-1] + bytes([text[-1] ^ 0xFF])
        message = decode_error_message(self, splice_after_ihdr(data, corrupt))
        self.assertIn("tEXt", message)
        self.assertIn("CRC", message)

    def test_rejects_bad_chunk_crc(self):
        _, data = solid_rgb(1, 1)
        corrupted = bytearray(data)
        (ihdr_length,) = struct.unpack(">I", data[8:12])
        crc_offset = data.rindex(b"IHDR") + 4 + ihdr_length
        corrupted[crc_offset] ^= 0xFF
        message = decode_error_message(self, bytes(corrupted))
        self.assertIn("IHDR", message)
        self.assertIn("CRC", message)
        self.assertIn(f"offset {data.rindex(b'IHDR') - 4}", message)
        self.assertIn(
            f"stored 0x{int.from_bytes(corrupted[crc_offset:crc_offset + 4], 'big'):08x}", message,
        )
        self.assertIn(
            f"computed 0x{int.from_bytes(data[crc_offset:crc_offset + 4], 'big'):08x}", message,
        )

    def test_rejects_truncated_chunk_crc(self):
        _, data = solid_rgb(1, 1)
        message = decode_error_message(self, data[:-1])
        self.assertIn("truncated PNG chunk 'IEND' CRC", message)
        self.assertIn(f"offset {data.rindex(b'IEND') + 4}", message)
        self.assertIn("expected 4 bytes, got 3", message)

    def test_rejects_truncated_chunk_payload(self):
        ihdr = ihdr_chunk(1, 1, 2)
        data = png_stream(ihdr, struct.pack(">I", 100) + b"IDAT" + b"\x00\x01")
        message = decode_error_message(self, data)
        self.assertIn("truncated PNG chunk 'IDAT'", message)
        self.assertIn("offset 33", message)
        self.assertIn("declared 100 payload bytes, only 2 present", message)


class TestIterChunks(unittest.TestCase):
    """tools/png/chunks.py's framing iterator, tested directly.

    collect_chunks keeps pulling the iterator past IEND so it can refuse a
    chunk after it, and the iterator itself refuses a trailing fragment after
    IEND. Before IEND its ``pos + 8 <= len(data)`` loop exit still ignores a
    fragment shorter than a chunk header, and collect_chunks then reports the
    missing IEND. These tests pin the iterator's contract that the decoder
    layer relies on.
    """

    def test_iter_chunks_rejects_non_bytes_input(self):
        with self.assertRaises(png.PngError) as caught:
            list(chunks.iter_chunks("not bytes"))
        self.assertIn("must be bytes or bytearray", str(caught.exception))
        self.assertIn("str", str(caught.exception))

    def test_yields_each_chunk_type_and_payload_in_order(self):
        data = png_stream(_chunk(b"tEXt", b"a"), _chunk(b"gAMA", b"bc"))
        self.assertEqual([(b"tEXt", b"a"), (b"gAMA", b"bc")], list(chunks.iter_chunks(data)))

    def test_does_not_stop_at_iend(self):
        data = png_stream(_chunk(b"IEND", b""), _chunk(b"tEXt", b"after"))
        self.assertEqual([(b"IEND", b""), (b"tEXt", b"after")], list(chunks.iter_chunks(data)))

    def test_a_trailing_fragment_shorter_than_a_header_is_ignored(self):
        _, data = solid_rgb(1, 1)
        without_iend = data[: data.rindex(b"IEND") - 4]
        truncated = without_iend + b"\x00\x00\x00\x01"
        self.assertEqual(list(chunks.iter_chunks(without_iend)), list(chunks.iter_chunks(truncated)))
        self.assertIn("no IEND", decode_error_message(self, truncated))


if __name__ == "__main__":
    unittest.main()
