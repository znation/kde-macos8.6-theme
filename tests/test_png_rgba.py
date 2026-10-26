"""Tests for the RGBA PNG codec (encode_rgba_png / decode_rgba / read_rgba)."""

from __future__ import annotations

import struct
import unittest

from support import repo_root  # noqa: F401
from support.error_assertions import assert_error_names  # noqa: E402
from support.png_fixtures import make_png  # noqa: E402
from support.tmp_dir import make_tmp_dir  # noqa: E402
from tools import png  # noqa: E402
from tools.png.write import encode_rgba_png  # noqa: E402

# The exact bytes encode_png returns for a 2x1 RGB image of (1, 2, 3) and
# (4, 5, 6): adding the RGBA encoder must leave the RGB encoder's framing
# (chunk order, filter byte, compression) byte-identical.
_ENCODE_PNG_2X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000002000000010802000000"
    "7b40e8dd0000000f4944415478da636064626661650300003f001698c1"
    "68130000000049454e44ae426082"
)


class TestRgbaPng(unittest.TestCase):
    def test_alpha_round_trip_zero_to_255(self):
        # 16x16 = 256 pixels, one for each alpha value.
        pixels = bytes(
            x for i in range(256) for x in (i, (i * 3) % 256, (i * 7) % 256, i)
        )
        blob = encode_rgba_png(16, 16, pixels)
        w, h, out = png.decode_rgba(blob)
        self.assertEqual((w, h), (16, 16))
        self.assertEqual(out, pixels)

    def test_read_rgba_round_trip(self):
        tmp = make_tmp_dir(self)
        pixels = bytes([1, 2, 3, 4, 5, 6, 7, 8])
        blob = encode_rgba_png(2, 1, pixels)
        path = tmp / "rgba.png"
        path.write_bytes(blob)
        self.assertEqual(png.read_rgba(path), (2, 1, pixels))
        self.assertEqual(png.read_rgba(path), png.decode_rgba(blob))

    def test_read_png_alpha_splits_rgb_and_alpha_planes(self):
        # The fidelity CLI asks read_png for alpha so it can compare
        # transparency; the returned Image must keep both the colour bytes and
        # one alpha byte per pixel, while the default stays RGB-only.
        tmp = make_tmp_dir(self)
        path = tmp / "rgba.png"
        path.write_bytes(
            make_png(2, 1, [bytes([1, 2, 3, 4, 5, 6, 7, 8])], color_type=6)
        )
        image = png.read_png(path, alpha=True)
        self.assertEqual((image.width, image.height), (2, 1))
        self.assertEqual(image.rgb, bytes([1, 2, 3, 5, 6, 7]))
        self.assertEqual(image.alpha, bytes([4, 8]))
        self.assertIsNone(png.read_png(path).alpha)

    def test_read_rgba_forwards_max_rows(self):
        # read_rgba's second argument is the only way a caller bounds a decode
        # to the top rows; pin that it reaches decode_rgba instead of being
        # dropped, which would decode the whole image and return every row.
        tmp = make_tmp_dir(self)
        rows = [bytes([1, 2, 3, 4]), bytes([5, 6, 7, 8])]
        path = tmp / "rgba.png"
        path.write_bytes(make_png(1, 2, rows, color_type=6))
        self.assertEqual(png.read_rgba(path, max_rows=1), (1, 1, rows[0]))

    def test_read_rgba_forwards_max_cols(self):
        # The column bound must reach decode_rgba too: dropping it would
        # return the full width a prefix reader asked to skip.
        tmp = make_tmp_dir(self)
        rows = [bytes([1, 2, 3, 4, 5, 6, 7, 8])]
        path = tmp / "rgba.png"
        path.write_bytes(make_png(2, 1, rows, color_type=6))
        self.assertEqual(
            png.read_rgba(path, max_cols=1), (1, 1, bytes([1, 2, 3, 4]))
        )

    def test_read_rgba_names_an_undecodable_file(self):
        # A two-input caller must be able to tell which file failed, so the
        # loader names the path it wraps decode_rgba's error with.
        tmp = make_tmp_dir(self)
        path = tmp / "not-an-image.png"
        path.write_bytes(b"not a png")
        assert_error_names(
            self,
            png.PngError,
            png.read_rgba,
            path,
            needles=(str(path), "not a PNG file"),
        )

    def test_ihdr_colour_type_is_6(self):
        blob = encode_rgba_png(1, 1, bytes([1, 2, 3, 4]))
        data_start = blob.index(b"IHDR") + 4
        width, height, depth, color_type = struct.unpack(
            ">IIBB", blob[data_start:data_start + 10]
        )
        self.assertEqual((width, height, depth, color_type), (1, 1, 8, 6))

    def test_output_is_deterministic(self):
        rgba = bytes(range(4)) * 4
        self.assertEqual(encode_rgba_png(2, 2, rgba), encode_rgba_png(2, 2, rgba))

    def test_wrong_length_rejected(self):
        for rgba in (b"", bytes(3), bytes(5)):
            with self.subTest(length=len(rgba)):
                assert_error_names(
                    self,
                    ValueError,
                    encode_rgba_png,
                    1,
                    1,
                    rgba,
                    needles=(f"{len(rgba)} RGBA bytes", "width*height*4"),
                )

    def test_three_bytes_per_pixel_rejected(self):
        # 12 bytes is a 2x2 RGB image, not a 2x2 RGBA one.
        message = assert_error_names(
            self,
            ValueError,
            encode_rgba_png,
            2,
            2,
            bytes(12),
            needles=("12 RGBA bytes", "16", "width*height*4"),
        )
        self.assertIn("2x2", message)

    def test_non_bytes_rejected(self):
        assert_error_names(
            self,
            ValueError,
            encode_rgba_png,
            1,
            1,
            "abc",
            needles=("PNG rgba must be bytes or bytearray", "str"),
        )

    def test_zero_dimension_rejected(self):
        with self.assertRaises(ValueError):
            encode_rgba_png(0, 1, b"")
        with self.assertRaises(ValueError):
            encode_rgba_png(1, 0, b"")

    def test_bool_dimension_rejected(self):
        with self.assertRaises(ValueError):
            encode_rgba_png(True, 1, bytes(4))
        with self.assertRaises(ValueError):
            encode_rgba_png(1, True, bytes(4))

    def test_negative_dimension_names_field(self):
        for name, w, h in (("width", -1, 1), ("height", 1, -1)):
            val = w if name == "width" else h
            with self.subTest(name=name):
                with self.assertRaises(ValueError) as c:
                    encode_rgba_png(w, h, bytes(4))
                self.assertIn(f"PNG {name} must be a positive integer", str(c.exception))
                self.assertIn(f"{name}={val!r}", str(c.exception))

    def test_colour_type_2_and_3_decode_to_alpha_255(self):
        rgba = bytes([10, 20, 30, 255, 40, 50, 60, 255])

        blob = png.encode_png(2, 1, bytes([10, 20, 30, 40, 50, 60]))
        self.assertEqual(png.decode_rgba(blob), (2, 1, rgba))

        palette = bytes([10, 20, 30, 40, 50, 60])
        blob = make_png(2, 1, [bytes([0, 1])], color_type=3, palette=palette)
        self.assertEqual(png.decode_rgba(blob), (2, 1, rgba))

    def test_greyscale_types_expand_to_rgba(self):
        grey = make_png(2, 1, [bytes([7, 8])], color_type=0)
        self.assertEqual(
            png.decode_rgba(grey),
            (2, 1, bytes([7, 7, 7, 255, 8, 8, 8, 255])),
        )
        grey_alpha = make_png(2, 1, [bytes([7, 200, 8, 100])], color_type=4)
        self.assertEqual(
            png.decode_rgba(grey_alpha),
            (2, 1, bytes([7, 7, 7, 200, 8, 8, 8, 100])),
        )

    def test_max_rows_returns_only_the_top_rows(self):
        rows = [bytes([1, 2, 3, 4, 5, 6]), bytes([7, 8, 9, 10, 11, 12])]
        blob = make_png(2, 2, rows, color_type=2)
        self.assertEqual(
            png.decode_rgba(blob, max_rows=1),
            (2, 1, bytes([1, 2, 3, 255, 4, 5, 6, 255])),
        )

    def test_max_cols_returns_only_the_left_columns(self):
        rows = [bytes([1, 2, 3, 4, 5, 6]), bytes([7, 8, 9, 10, 11, 12])]
        blob = make_png(2, 2, rows, color_type=2)
        self.assertEqual(
            png.decode_rgba(blob, max_cols=1),
            (1, 2, bytes([1, 2, 3, 255, 7, 8, 9, 255])),
        )

    def test_palette_max_cols_crops_the_expanded_rows(self):
        palette = bytes([10, 20, 30, 40, 50, 60])
        blob = make_png(2, 1, [bytes([0, 1])], color_type=3, palette=palette)
        self.assertEqual(
            png.decode_rgba(blob, max_cols=1), (1, 1, bytes([10, 20, 30, 255]))
        )

    def test_palette_index_past_the_column_bound_is_rejected(self):
        blob = make_png(
            2,
            1,
            [bytes([0, 5])],
            color_type=3,
            palette=bytes([10, 20, 30]),
        )
        assert_error_names(
            self,
            png.PngError,
            png.decode_rgba,
            blob,
            max_cols=1,
            needles=("index 5", "1 entry"),
        )

    def test_palette_index_past_the_row_bound_is_rejected(self):
        blob = make_png(
            1,
            2,
            [bytes([0]), bytes([5])],
            color_type=3,
            palette=bytes([10, 20, 30]),
        )
        assert_error_names(
            self,
            png.PngError,
            png.decode_rgba,
            blob,
            max_rows=1,
            needles=("index 5", "1 entry"),
        )

    def test_palette_without_plte_is_rejected(self):
        # decode_rgba expands a color-type-3 image through its own palette
        # branch, which no decode_png test reaches. Without the explicit
        # guard, a PLTE-less palette PNG would hand None to palette_rgba and
        # raise a TypeError instead of the decoder's PngError.
        blob = make_png(1, 1, [bytes([0])], color_type=3, palette=None)
        assert_error_names(
            self,
            png.PngError,
            png.decode_rgba,
            blob,
            needles=("no PLTE",),
        )

    def test_palette_trns_sets_alpha(self):
        palette = bytes([10, 20, 30, 40, 50, 60])
        blob = make_png(
            2,
            1,
            [bytes([0, 1])],
            color_type=3,
            palette=palette,
            trns=bytes([0, 255]),
        )
        self.assertEqual(
            png.decode_rgba(blob),
            (2, 1, bytes([10, 20, 30, 0, 40, 50, 60, 255])),
        )
        # The RGB decoder's contract is still RGB: it ignores transparency.
        self.assertEqual(
            png.decode_png(blob).rgb, bytes([10, 20, 30, 40, 50, 60])
        )

    def test_palette_trns_shorter_than_palette_leaves_rest_opaque(self):
        palette = bytes([10, 20, 30, 40, 50, 60])
        blob = make_png(
            2,
            1,
            [bytes([0, 1])],
            color_type=3,
            palette=palette,
            trns=bytes([7]),
        )
        self.assertEqual(
            png.decode_rgba(blob),
            (2, 1, bytes([10, 20, 30, 7, 40, 50, 60, 255])),
        )

    def test_greyscale_and_truecolor_trns_make_matching_pixels_transparent(self):
        grey = make_png(
            2, 1, [bytes([7, 8])], color_type=0, trns=struct.pack(">H", 7)
        )
        self.assertEqual(
            png.decode_rgba(grey),
            (2, 1, bytes([7, 7, 7, 0, 8, 8, 8, 255])),
        )
        truecolor = make_png(
            2,
            1,
            [bytes([1, 2, 3, 4, 5, 6])],
            color_type=2,
            trns=struct.pack(">HHH", 1, 2, 3),
        )
        self.assertEqual(
            png.decode_rgba(truecolor),
            (2, 1, bytes([1, 2, 3, 0, 4, 5, 6, 255])),
        )

    def test_trns_key_matches_only_whole_pixels(self):
        # A key that straddles a pixel boundary is not a match, and a 16-bit
        # key above 255 cannot equal an 8-bit sample.
        opaque = (2, 1, bytes([1, 2, 3, 255, 4, 5, 6, 255]))
        crossing = make_png(
            2,
            1,
            [bytes([1, 2, 3, 4, 5, 6])],
            color_type=2,
            trns=struct.pack(">HHH", 2, 3, 4),
        )
        self.assertEqual(png.decode_rgba(crossing), opaque)
        high = make_png(
            2,
            1,
            [bytes([1, 2, 3, 4, 5, 6])],
            color_type=2,
            trns=struct.pack(">HHH", 1, 2, 0x0103),
        )
        self.assertEqual(png.decode_rgba(high), opaque)

    def test_dense_truecolor_trns_key_marks_every_matching_pixel(self):
        # Three key pixels in every four take the bulk-match path, so this
        # pins its alpha against the same whole-pixel rule the sparse path
        # applies.
        width = height = 64
        key = bytes([1, 2, 3])
        other = bytes([4, 5, 6])
        rows = []
        expected = bytearray()
        for y in range(height):
            row = bytearray()
            for x in range(width):
                if (x + y) % 4 == 0:
                    row += other
                    expected += other + b"\xff"
                else:
                    row += key
                    expected += key + b"\x00"
            rows.append(bytes(row))
        blob = make_png(
            width,
            height,
            rows,
            color_type=2,
            trns=struct.pack(">HHH", 1, 2, 3),
        )
        self.assertEqual(
            png.decode_rgba(blob), (width, height, bytes(expected))
        )

    def test_sparse_truecolor_trns_key_marks_only_its_pixel(self):
        # One match in a 64-pixel row stays under the bulk-match threshold.
        width = 64
        key = bytes([1, 2, 3])
        other = bytes([4, 5, 6])
        row = key + other * (width - 1)
        blob = make_png(
            width, 1, [row], color_type=2, trns=struct.pack(">HHH", 1, 2, 3)
        )
        expected = key + b"\x00" + (other + b"\xff") * (width - 1)
        self.assertEqual(png.decode_rgba(blob), (width, 1, expected))

    def test_absent_truecolor_trns_key_leaves_every_pixel_opaque(self):
        row = bytes([4, 5, 6]) * 64
        blob = make_png(
            64, 1, [row], color_type=2, trns=struct.pack(">HHH", 1, 2, 3)
        )
        self.assertEqual(
            png.decode_rgba(blob), (64, 1, bytes([4, 5, 6, 255]) * 64)
        )

    def test_malformed_trns_length_rejected(self):
        grey = make_png(
            1, 1, [bytes([7])], color_type=0, trns=b"\x00\x07\x00"
        )
        assert_error_names(
            self,
            png.PngError,
            png.decode_rgba,
            grey,
            needles=("tRNS chunk has 3 bytes", "exactly 2"),
        )
        truecolor = make_png(
            1, 1, [bytes([1, 2, 3])], color_type=2, trns=bytes(5)
        )
        assert_error_names(
            self,
            png.PngError,
            png.decode_rgba,
            truecolor,
            needles=("tRNS chunk has 5 bytes", "exactly 6"),
        )
        palette = bytes([10, 20, 30, 40, 50, 60])
        for trns in (b"", bytes(3)):
            blob = make_png(
                1,
                1,
                [bytes([0])],
                color_type=3,
                palette=palette,
                trns=trns,
            )
            with self.subTest(length=len(trns)):
                assert_error_names(
                    self,
                    png.PngError,
                    png.decode_rgba,
                    blob,
                    needles=(f"has {len(trns)} bytes", "1 to 2"),
                )

    def test_encode_png_unchanged(self):
        blob = png.encode_png(2, 1, bytes([1, 2, 3, 4, 5, 6]))
        self.assertEqual(blob, _ENCODE_PNG_2X1)
        self.assertEqual(png.decode_png(blob).rgb, bytes([1, 2, 3, 4, 5, 6]))


if __name__ == "__main__":
    unittest.main()
