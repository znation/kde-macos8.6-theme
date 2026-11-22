"""Tests pinning the bounded, non-decoding PNG declared-size read.

The tests cover the header-prefix allocation, inclusive file-size cap,
refusal to decode, and parity with the decoder's diagnosis for malformed
streams. The whole-file input guards for ``read_png`` stay in
``tests/test_png_read.py``.
"""

from __future__ import annotations

import unittest
import zlib
from pathlib import Path
from unittest import mock

from support.allocation_fixtures import peak_allocation
from support.error_assertions import error_message
from support.png_fixtures import (
    _chunk,
    ihdr_chunk,
    input_file,
    png_stream,
    rgb_image,
    with_ihdr_byte,
)
from tools import png
from tools.png import header, loader


class TestReadPngSize(unittest.TestCase):
    def _file(self, name: str, data: bytes) -> Path:
        return input_file(self, name, data)

    def test_read_png_size_reports_declared_dimensions_without_decoding(self):
        # The sampler needs the full image size to report and validate a
        # coordinate, but must not pay to unfilter rows it will not read.
        _, data = rgb_image(3, 4, lambda x, y: (x, y, 0))
        path = self._file("image.png", data)
        with mock.patch.object(loader, "decode_png") as decode:
            self.assertEqual(png.read_png_size(path), (3, 4))
        decode.assert_not_called()

    def test_read_png_size_reads_only_the_header_prefix(self):
        # The sampler reads a large reference twice: once for the sampled rows
        # and once for the declared size. A size read must not load the whole
        # file for the second pass. A megabyte after IEND keeps the header
        # valid, so both the old and new reads report 3x4; only a bounded
        # prefix read keeps the allocation small.
        _, data = rgb_image(3, 4, lambda x, y: (x, y, 0))
        path = self._file("padded.png", data + b"\x00" * (1 << 20))
        size, peak = peak_allocation(lambda: png.read_png_size(path))
        self.assertEqual(size, (3, 4))
        self.assertLess(peak, 64 * 1024)

    def test_read_png_size_still_rejects_an_oversize_file(self):
        # Reading only a prefix must not bypass the file-size cap: a file over
        # the cap whose first chunk is a valid IHDR is refused by name, with
        # the size an operator needs, just as the whole-file reader does.
        limit = 4096
        _, data = rgb_image(3, 4, lambda x, y: (x, y, 0))
        path = self._file("oversize.png", data + b"\x00" * (limit + 1 - len(data)))
        with mock.patch.object(loader, "_MAX_FILE_BYTES", limit):
            message = error_message(self, png.PngError, png.read_png_size, path)
        self.assertIn(str(path), message)
        self.assertIn(str(limit), message)
        self.assertIn(f"{limit + 1} bytes", message)

    def test_read_png_size_accepts_a_file_exactly_at_the_cap(self):
        # The prefix read checks the stat size against the cap, inclusively:
        # a file of exactly _MAX_FILE_BYTES bytes still reports its size.
        _, data = rgb_image(3, 4, lambda x, y: (x, y, 0))
        path = self._file("at_cap.png", data)
        with mock.patch.object(loader, "_MAX_FILE_BYTES", len(data)):
            self.assertEqual(png.read_png_size(path), (3, 4))

    def test_read_png_size_names_undecodable_file(self):
        path = self._file("broken.png", b"not a png")
        message = error_message(self, png.PngError, png.read_png_size, path)
        self.assertIn(str(path), message)

    def _assert_size_matches_decode(self, data: bytes, needle: str) -> None:
        """Assert read_png_size rejects *data* exactly as read_png does."""
        path = self._file("malformed.png", data)
        decode_message = error_message(self, png.PngError, png.read_png, path)
        self.assertEqual(
            error_message(self, png.PngError, png.read_png_size, path),
            decode_message,
        )
        self.assertIn(needle, decode_message)

    def test_read_png_size_rejects_a_corrupt_ihdr_crc(self):
        # A header byte changed without fixing the CRC makes the declared
        # dimensions untrustworthy; the size read must use the framing check.
        _, data = rgb_image(3, 4, lambda x, y: (x, y, 0))
        broken = bytearray(data)
        broken[23] ^= 0xFF  # last height byte, inside the IHDR payload
        self._assert_size_matches_decode(bytes(broken), "bad CRC")

    def test_read_png_size_rejects_unsupported_ihdr_fields(self):
        # A valid-CRC header can still declare a format the decoder refuses;
        # the size read must not report dimensions for it.
        _, data = rgb_image(3, 4, lambda x, y: (x, y, 0))
        self._assert_size_matches_decode(
            with_ihdr_byte(data, 8, 16), "bit depth 16"
        )

    def test_read_png_size_rejects_an_image_over_the_pixel_limit(self):
        # read_png_size must apply decode_png's decompression-bomb guard: a
        # header declaring more than the cap must not hand dimensions to a
        # caller that would then try to decode them.
        width, height = 8001, 8000  # 64,008,000 pixels, above the cap
        path = self._file(
            "huge.png", png_stream(ihdr_chunk(width, height, 2))
        )
        with mock.patch.object(loader, "decode_png") as decode:
            message = error_message(
                self, png.PngError, png.read_png_size, path
            )
        decode.assert_not_called()
        self.assertIn(str(path), message)
        self.assertIn(str(header.MAX_PIXELS), message)

    def test_read_png_size_rejects_a_png_whose_ihdr_is_not_first(self):
        # The size read trusts the first chunk only when it is IHDR. With an
        # IDAT first it must fall back to the decoder's framing check rather
        # than scanning ahead and accepting a header the decoder refuses.
        misordered = png_stream(
            _chunk(b"IDAT", zlib.compress(b"\x00\x01\x02\x03")),
            ihdr_chunk(1, 1, 2),
            _chunk(b"IEND", b""),
        )
        self._assert_size_matches_decode(misordered, "first chunk")

    def test_read_png_size_falls_back_when_the_prefix_cuts_off_the_first_chunk(self):
        # The size read inspects a 33-byte prefix, which cannot frame a first
        # chunk whose payload is longer than 13 bytes. A misordered stream with
        # such an IDAT first must still be refused with the decoder's canonical
        # diagnosis, not the prefix's "truncated chunk" one.
        misordered = png_stream(
            _chunk(b"IDAT", zlib.compress(bytes(range(100)))),
            ihdr_chunk(1, 1, 2),
            _chunk(b"IEND", b""),
        )
        self._assert_size_matches_decode(misordered, "must be the first chunk")


if __name__ == "__main__":
    unittest.main()
