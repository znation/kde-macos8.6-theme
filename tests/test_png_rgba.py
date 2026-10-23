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

    def test_encode_png_unchanged(self):
        blob = png.encode_png(2, 1, bytes([1, 2, 3, 4, 5, 6]))
        self.assertEqual(blob, _ENCODE_PNG_2X1)
        self.assertEqual(png.decode_png(blob).rgb, bytes([1, 2, 3, 4, 5, 6]))


if __name__ == "__main__":
    unittest.main()
