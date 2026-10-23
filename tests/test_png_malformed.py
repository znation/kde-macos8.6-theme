"""Tests for the PNG decoder's malformed image data and limits.

``tools/png/read.py``'s inflate guards, ``tools/png/stream.py``'s header and
pixel-limit checks and ``tools/png/expand.py``'s palette guard all reject
malformed input; the decoders run them in pipeline order: stream validation,
then inflate, then expansion.

After the chunk stream is well-formed, the image data can still be
untrustworthy: a palette index can fall outside its table, the IDAT stream can
be truncated or corrupt, a few KB can expand to a decompression bomb, or the
header can declare more pixels than the decoder will allocate. These tests pin
each rejection and the resource limit that bounds it, plus the entry guards
for a non-PNG file and an unsupported colour type. Chunk framing lives in
``test_png_chunks``; successful decoding lives in ``test_png_decode``.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest
import zlib

from support.allocation_fixtures import peak_allocation
from support.error_assertions import assert_error_names, error_message

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.png_fixtures import (  # noqa: E402
    _PNG_SIGNATURE,
    _chunk,
    decode_error_message,
    ihdr_chunk,
    make_png,
    png_with_idat,
)
from tools import png
from tools.png import expand, stream


class TestMalformedImageData(unittest.TestCase):
    def test_palette_index_outside_plte_names_index_and_size(self):
        # A palette image whose pixel index has no PLTE entry must name the
        # offending index and the palette size, or the user cannot tell which
        # pixel is bad or how short the palette is. The size is named both as
        # entries and as bytes, matching the PLTE-length error.
        palette = bytes([255, 0, 0])  # one entry: index 0 only
        data = make_png(1, 1, [bytes([1])], color_type=3, palette=palette)
        message = decode_error_message(self, data)
        self.assertIn("index 1", message)
        self.assertIn("1 entry", message)
        self.assertIn("3 bytes", message)

    def test_palette_index_outside_multi_entry_plte_counts_entries(self):
        # The same out-of-range diagnostic on a palette with more than one
        # entry must say "entries", not the singular "entry": the message
        # counts the palette so the user can see how short it is.
        palette = bytes([255, 0, 0, 0, 255, 0])  # two entries: indices 0 and 1
        data = make_png(1, 1, [bytes([2])], color_type=3, palette=palette)
        message = decode_error_message(self, data)
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
        message = decode_error_message(self, data)
        self.assertIn("index 2", message)
        self.assertIn("2 entries", message)

    def test_palette_length_not_multiple_of_three(self):
        # A PLTE whose length is not a multiple of 3 ends in a partial RGB
        # entry. Index 0 would still decode, so without this check a malformed
        # palette passes silently as long as no pixel uses the bad entry.
        palette = bytes([255, 0, 0, 0])  # 4 bytes: index 1 is a partial entry
        data = make_png(1, 1, [bytes([0])], color_type=3, palette=palette)
        message = decode_error_message(self, data)
        self.assertIn("4 bytes", message)
        self.assertIn("multiple of 3", message)

    def test_palette_longer_than_256_entries(self):
        # The PNG spec caps PLTE at 256 entries (768 bytes); 771 bytes is 257
        # entries (a whole multiple of 3, so the length check cannot reject it
        # on the modulo alone) and must be reported with its actual size.
        palette = bytes(771)
        data = make_png(1, 1, [bytes([0])], color_type=3, palette=palette)
        message = decode_error_message(self, data)
        self.assertIn("771 bytes", message)
        self.assertIn("768", message)

    def test_truncated_image_data_names_actual_and_expected(self):
        # An IDAT that decompresses to fewer scanlines than IHDR's height
        # declares must name how many bytes arrived and how many were needed,
        # so a truncated file is distinguishable from other corruption.
        data = make_png(3, 3, [bytes(9)])
        self.assertIn(
            "got 10 bytes, expected 30 for a 3x3 image",
            decode_error_message(self, data),
        )

    def test_truncated_rgba_image_data_names_actual_and_expected(self):
        # Color-type-6 scanlines carry four channels per pixel, and decode
        # drops the alpha before unfiltering. That path has its own
        # declared-size check; without it the short buffer would be indexed
        # past its end as a bare IndexError instead of a PngError. The
        # expected count (39 = 3 rows * (3 px * 4 channels + 1 filter byte))
        # pins the four-channel declaration rather than RGB's 30, so this is
        # the drop_alpha call site and not the unfilter one.
        data = make_png(3, 3, [bytes(12)], color_type=6)
        self.assertIn(
            "got 13 bytes, expected 39 for a 3x3 image",
            decode_error_message(self, data),
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
                self.assertIn("no IDAT image data", decode_error_message(self, data))

    def test_rejects_decompression_bomb_without_expanding_it(self):
        # A few KB of IDAT can expand to far more scanlines than the header
        # declares. Decoding must stop at the declared size instead of
        # materializing the whole stream (a decompression bomb).
        declared = 4  # 1x1 RGB: one filter byte + three channels
        bomb = bytes(declared) + bytes(16 * 1024 * 1024)
        data = png_with_idat(zlib.compress(bomb))
        message, peak = peak_allocation(lambda: decode_error_message(self, data))
        self.assertIn("more than the 4 bytes", message)
        self.assertLess(peak, 4 * 1024 * 1024)

    def test_rejects_truncated_stream_that_hits_declared_size(self):
        # A stream cut before its end marker can still yield exactly the
        # declared byte count. Accepting it would silently drop the adler32
        # check that zlib.decompress performed before this change.
        raw = bytes([0, 1, 2, 3])  # 1x1 RGB: filter byte + three channels
        truncated = zlib.compress(raw)[:-4]  # drop the trailing adler32
        data = png_with_idat(truncated)
        self.assertIn("truncated", decode_error_message(self, data))

    def test_rejects_corrupt_deflate_stream(self):
        # The IDAT CRC covers the chunk bytes but says nothing about whether
        # they are a valid deflate stream, so a download corrupted inside the
        # chunk reaches zlib.decompressobj and raises zlib.error. That must
        # become a PngError naming the corruption, not leak a raw zlib.error
        # past decode_png and read_png (which would print a traceback from the
        # CLI instead of a clean "fidelity: error:" line).
        data = png_with_idat(b"\xff\xff\xff\xff")
        self.assertIn("corrupt PNG image data", decode_error_message(self, data))

    def test_rejects_trailing_bytes_after_the_zlib_stream(self):
        # IDAT holds exactly one zlib stream, which ends at its adler32
        # trailer. Bytes after that end are not image data; zlib reports them
        # as unused_data, and accepting them would let a malformed PNG carry
        # hidden payload the decoder silently drops.
        raw = bytes([0, 1, 2, 3])  # 1x1 RGB: filter byte + three channels
        data = png_with_idat(zlib.compress(raw) + b"trailing")
        message = decode_error_message(self, data)
        self.assertIn("trailing", message)
        self.assertIn("zlib stream", message)

    def test_rejects_declared_image_over_pixel_limit(self):
        # A header may declare dimensions far larger than any screenshot; the
        # pixel limit must reject it before zlib decompresses anything.
        data = png_with_idat(
            zlib.compress(bytes(4)), width=100_000, height=100_000
        )
        message = decode_error_message(self, data)
        self.assertIn("100000x100000", message)
        self.assertIn(str(stream.MAX_PIXELS), message)

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
                message = decode_error_message(self, data)
                self.assertIn("not a PNG file", message)
                self.assertIn(expected, message)
                self.assertIn("convert it to PNG", message)

    def test_unknown_bytes_keep_the_bare_not_a_png_message(self):
        # Only a known raster signature earns the format and fix hints;
        # arbitrary bytes must not be described as an image, nor told to
        # convert a format the decoder never identified.
        message = decode_error_message(self, b"not a png")
        self.assertIn("not a PNG file", message)
        self.assertNotIn("image", message)
        self.assertNotIn("convert", message)

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
        message = decode_error_message(self, data)
        self.assertIn("unsupported PNG filter type 5", message)
        self.assertIn("row 2", message)


class TestTrnsColorTypeValidation(unittest.TestCase):
    """Both decoders refuse a tRNS chunk the header cannot carry.

    ``decode_rgba`` is the only decoder that applies tRNS to pixels, but a
    malformed chunk still makes the file non-conformant: ``decode_png`` used
    to discard transparency without validating it, so the same bytes decoded
    as RGB and raised on the RGBA path.
    """

    def test_alpha_color_types_refuse_trns(self):
        for color_type, channels in ((4, 2), (6, 4)):
            blob = make_png(
                1,
                1,
                [bytes(range(channels))],
                color_type=color_type,
                trns=b"\x00\x01\x00\x02\x00\x03",
            )
            for decoder in (png.decode_png, png.decode_rgba):
                with self.subTest(
                    color_type=color_type, decoder=decoder.__name__
                ):
                    assert_error_names(
                        self,
                        png.PngError,
                        decoder,
                        blob,
                        needles=(
                            "tRNS chunk",
                            f"color type {color_type}",
                            "0, 2 and 3",
                        ),
                    )

    def test_rgb_path_refuses_wrong_length_sample_trns(self):
        cases = (
            (0, 2, bytes([7]), b"\x00\x07\x00", "exactly 2"),
            (2, 3, bytes([1, 2, 3]), bytes(5), "exactly 6"),
        )
        for color_type, channels, row, trns, length_needle in cases:
            blob = make_png(
                1, 1, [row], color_type=color_type, trns=trns
            )
            with self.subTest(color_type=color_type):
                assert_error_names(
                    self,
                    png.PngError,
                    png.decode_png,
                    blob,
                    needles=(f"has {len(trns)} bytes", length_needle),
                )

    def test_rgb_path_refuses_overlong_palette_trns(self):
        palette = bytes([10, 20, 30, 40, 50, 60])
        blob = make_png(
            1, 1, [bytes([0])], color_type=3, palette=palette, trns=bytes(3)
        )
        assert_error_names(
            self,
            png.PngError,
            png.decode_png,
            blob,
            needles=("tRNS chunk has 3 bytes", "needs 1 to 2"),
        )

    def test_palette_trns_before_plte_is_refused(self):
        # The PNG spec requires a color type 3 image's tRNS chunk to follow
        # the PLTE chunk whose entries it gives alpha. The chunk collector
        # used to accept the two payloads independently, so a file that gave
        # transparency to a palette appearing later still decoded.
        blob = (
            _PNG_SIGNATURE
            + ihdr_chunk(1, 1, 3)
            + _chunk(b"tRNS", bytes([0, 128]))
            + _chunk(b"PLTE", bytes([255, 0, 0, 0, 255, 0]))
            + _chunk(b"IDAT", zlib.compress(bytes([0, 0])))
            + _chunk(b"IEND", b"")
        )
        for decoder in (png.decode_png, png.decode_rgba):
            with self.subTest(decoder=decoder.__name__):
                assert_error_names(
                    self,
                    png.PngError,
                    decoder,
                    blob,
                    needles=("tRNS chunk before", "PLTE chunk", "follow"),
                )

    def test_palette_trns_without_any_plte_still_names_the_missing_palette(
        self,
    ):
        # An ordering guard must not swallow the diagnosis for a color type 3
        # image that has no palette at all: there is no PLTE for its tRNS to
        # precede, so the missing-palette error must still win.
        blob = make_png(1, 1, [bytes([0])], color_type=3, trns=b"\x00")
        for decoder in (png.decode_png, png.decode_rgba):
            with self.subTest(decoder=decoder.__name__):
                assert_error_names(
                    self,
                    png.PngError,
                    decoder,
                    blob,
                    needles=("palette PNG has no PLTE chunk",),
                )

    def test_valid_trns_still_decodes_as_rgb(self):
        # The new check must not reject the valid chunk the RGB path discards:
        # a conformant tRNS is still part of a decodable file.
        truecolor = make_png(
            1,
            1,
            [bytes([1, 2, 3])],
            color_type=2,
            trns=b"\x00\x01\x00\x02\x00\x03",
        )
        self.assertEqual(png.decode_png(truecolor).rgb, bytes([1, 2, 3]))
        palette = bytes([10, 20, 30, 40, 50, 60])
        indexed = make_png(
            1, 1, [bytes([1])], color_type=3, palette=palette, trns=b"\x00\x80"
        )
        self.assertEqual(png.decode_png(indexed).rgb, bytes([40, 50, 60]))


class TestPlteColorTypeValidation(unittest.TestCase):
    """Both decoders refuse a PLTE chunk the header's color type forbids.

    The PNG spec permits PLTE for color type 3 (required), color types 2 and
    6 (optional suggested palette) and prohibits it for the greyscale color
    types 0 and 4. The decoder used to ignore such a palette, so a
    non-conformant file decoded even though its palette could never affect a
    pixel.
    """

    def test_greyscale_color_types_refuse_plte(self):
        for color_type, channels in ((0, 1), (4, 2)):
            blob = make_png(
                1,
                1,
                [bytes(range(channels))],
                color_type=color_type,
                palette=bytes([10, 20, 30]),
            )
            for decoder in (png.decode_png, png.decode_rgba):
                with self.subTest(
                    color_type=color_type, decoder=decoder.__name__
                ):
                    assert_error_names(
                        self,
                        png.PngError,
                        decoder,
                        blob,
                        needles=(
                            "PLTE chunk",
                            f"color type {color_type}",
                            "prohibited for the greyscale color types 0 and 4",
                        ),
                    )

    def test_truecolor_color_types_still_accept_a_suggested_palette(self):
        # PLTE is optional for truecolor and truecolor with alpha, so the new
        # guard must not reject the suggested palette a conformant file may
        # carry.
        for color_type, channels in ((2, 3), (6, 4)):
            row = bytes(range(1, channels + 1))
            blob = make_png(
                1,
                1,
                [row],
                color_type=color_type,
                palette=bytes([10, 20, 30]),
            )
            with self.subTest(color_type=color_type):
                self.assertEqual(png.decode_png(blob).rgb, row[:3])
                rgba = row if channels == 4 else row + b"\xff"
                self.assertEqual(png.decode_rgba(blob), (1, 1, rgba))


class TestToRgbUnsupportedColorType(unittest.TestCase):
    """``to_rgb`` names a color type it has no expansion for.

    ``decode_png`` rejects a color type outside ``stream.CHANNELS`` before
    calling ``to_rgb``, so the four types it handles (0, 2, 3 and 4;
    ``decode_png`` expands type 6 itself) are the only ones a real PNG can
    reach it with. The helper's final guard is the contract that keeps a
    future ``CHANNELS`` entry from silently decoding with the wrong expansion:
    adding a color type there without a matching branch here must fail loudly,
    naming the type. No PNG can drive that branch through ``decode_png``, so
    call the helper directly with the color types the PNG spec does not
    define.
    """

    def test_unsupported_color_type_names_the_type(self):
        for color_type in (1, 5, 7):
            with self.subTest(color_type=color_type):
                self.assertEqual(
                    error_message(
                        self, png.PngError, expand.to_rgb, color_type, b"", None
                    ),
                    f"unsupported PNG color type {color_type}",
                )


if __name__ == "__main__":
    unittest.main()
