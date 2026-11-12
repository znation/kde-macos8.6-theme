"""Tests for ``tools/cursor_vector.py``: the antialiased polygon rasterizer.

Every expected pixel below is worked out from the face geometry by hand (the
sample centres, the even-odd rule and the edge distances), never by running the
renderer. The committed cursor files do not use this module yet, so these tests
are the only pin on its output.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import cursor_vector  # noqa: E402
from tools.cursor_vector import VectorCursor  # noqa: E402
from tools.xcursor import MAX_IMAGE_SIZE  # noqa: E402

SQUARE = ((8, 8), (24, 8), (24, 24), (8, 24))
HALF_SQUARE = ((8, 8), (24.5, 8), (24.5, 24), (8, 24))


def _pixel(buf, size, x, y):
    offset = (y * size + x) * 4
    return tuple(buf[offset:offset + 4])


class TestRenderFace(unittest.TestCase):
    def test_square_face_is_opaque_black_on_its_pixels_and_clear_elsewhere(self):
        art = VectorCursor(face=SQUARE, outline_width=0, design_size=32)
        buf = cursor_vector.render_vector_rgba(art, 32)
        self.assertEqual(len(buf), 32 * 32 * 4)
        for y in range(32):
            for x in range(32):
                inside = 8 <= x <= 23 and 8 <= y <= 23
                expected = (0, 0, 0, 255) if inside else (0, 0, 0, 0)
                self.assertEqual(_pixel(buf, 32, x, y), expected, (x, y))

    def test_square_face_at_size_16_covers_pixels_four_to_eleven(self):
        art = VectorCursor(face=SQUARE, outline_width=0, design_size=32)
        buf = cursor_vector.render_vector_rgba(art, 16)
        for y in range(16):
            for x in range(16):
                inside = 4 <= x <= 11 and 4 <= y <= 11
                expected = (0, 0, 0, 255) if inside else (0, 0, 0, 0)
                self.assertEqual(_pixel(buf, 16, x, y), expected, (x, y))

    def test_half_covered_edge_pixel_has_half_alpha(self):
        # The face's right edge is at x = 24.5, so pixel column 24 has samples
        # at x = 24.125 and 24.375 inside and the other two columns outside.
        art = VectorCursor(face=HALF_SQUARE, outline_width=0, design_size=32)
        buf = cursor_vector.render_vector_rgba(art, 32)
        self.assertEqual(_pixel(buf, 32, 24, 16), (0, 0, 0, 128))


class TestRenderOutline(unittest.TestCase):
    def setUp(self):
        art = VectorCursor(face=HALF_SQUARE, outline_width=2, design_size=32)
        self.buf = cursor_vector.render_vector_rgba(art, 32)

    def test_pixel_half_face_half_outline_is_mid_grey(self):
        # Eight samples are inside and eight lie 0.125 and 0.375 outside the
        # right edge, all within the width of 2: grey is half of 255.
        self.assertEqual(_pixel(self.buf, 32, 24, 16), (128, 128, 128, 255))

    def test_outline_band_is_white_out_to_its_width(self):
        self.assertEqual(_pixel(self.buf, 32, 6, 16), (255, 255, 255, 255))
        self.assertEqual(_pixel(self.buf, 32, 7, 16), (255, 255, 255, 255))

    def test_pixel_beyond_the_outline_width_is_clear(self):
        # Pixel column 5 samples lie 2.125 to 2.875 from the edge at x = 8.
        self.assertEqual(_pixel(self.buf, 32, 5, 16), (0, 0, 0, 0))

    def test_corner_pixel_is_white_and_partly_covered(self):
        # Some samples of pixel (6, 6) lie within 2 of the corner (8, 8), others
        # do not, so alpha is strictly between 0 and 255 and the grey is white.
        r, g, b, a = _pixel(self.buf, 32, 6, 6)
        self.assertEqual((r, g, b), (255, 255, 255))
        self.assertTrue(0 < a < 255, a)


class TestRenderValidation(unittest.TestCase):
    def test_rejects_a_size_below_one(self):
        art = VectorCursor(face=SQUARE)
        with self.assertRaisesRegex(ValueError, "size"):
            cursor_vector.render_vector_rgba(art, 0)

    def test_rejects_a_bool_size(self):
        art = VectorCursor(face=SQUARE)
        with self.assertRaisesRegex(ValueError, "size"):
            cursor_vector.render_vector_rgba(art, True)

    def test_rejects_a_size_above_the_frame_limit_naming_it(self):
        art = VectorCursor(face=SQUARE)
        with self.assertRaisesRegex(ValueError, str(MAX_IMAGE_SIZE)):
            cursor_vector.render_vector_rgba(art, MAX_IMAGE_SIZE + 1)

    def test_rejects_a_non_positive_sample_count(self):
        art = VectorCursor(face=SQUARE)
        with self.assertRaisesRegex(ValueError, "samples"):
            cursor_vector.render_vector_rgba(art, 16, samples=0)

    def test_rejects_something_that_is_not_a_vector_cursor(self):
        with self.assertRaisesRegex(ValueError, "VectorCursor"):
            cursor_vector.render_vector_rgba(SQUARE, 16)

    def test_two_renders_of_one_input_are_identical(self):
        art = VectorCursor(face=HALF_SQUARE, outline_width=2)
        first = cursor_vector.render_vector_rgba(art, 24)
        second = cursor_vector.render_vector_rgba(art, 24)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 24 * 24 * 4)


class TestVectorCursorFields(unittest.TestCase):
    def test_default_design_size_is_thirty_two(self):
        self.assertEqual(VectorCursor(face=SQUARE).design_size, 32)

    def test_face_is_stored_as_a_hashable_tuple(self):
        art = VectorCursor(face=[[8, 8], [24, 8], [24, 24]])
        self.assertEqual(art.face, ((8, 8), (24, 8), (24, 24)))
        hash(art)

    def test_rejects_fewer_than_three_vertices(self):
        with self.assertRaisesRegex(ValueError, "face"):
            VectorCursor(face=((8, 8), (24, 24)))

    def test_rejects_a_vertex_that_is_not_a_pair(self):
        with self.assertRaisesRegex(ValueError, "face"):
            VectorCursor(face=((8, 8), (24, 8), (24,)))

    def test_rejects_a_non_numeric_coordinate_naming_the_field(self):
        with self.assertRaisesRegex(ValueError, "face vertex 1 x"):
            VectorCursor(face=((8, 8), ("24", 8), (24, 24)))

    def test_rejects_a_bool_coordinate(self):
        with self.assertRaisesRegex(ValueError, "face vertex 0 y"):
            VectorCursor(face=((8, True), (24, 8), (24, 24)))

    def test_rejects_a_coordinate_outside_the_design_grid(self):
        with self.assertRaisesRegex(ValueError, "face vertex 2 x"):
            VectorCursor(face=((8, 8), (24, 8), (33, 24)))

    def test_rejects_a_negative_outline_width(self):
        with self.assertRaisesRegex(ValueError, "outline_width"):
            VectorCursor(face=SQUARE, outline_width=-1)

    def test_rejects_an_infinite_outline_width(self):
        with self.assertRaisesRegex(ValueError, "outline_width"):
            VectorCursor(face=SQUARE, outline_width=float("inf"))

    def test_rejects_a_design_size_that_is_not_a_positive_int(self):
        for bad in (0, -4, 32.0, True):
            with self.subTest(design_size=bad):
                with self.assertRaisesRegex(ValueError, "design_size"):
                    VectorCursor(face=SQUARE, design_size=bad)


class TestVectorHotspot(unittest.TestCase):
    def setUp(self):
        self.art = VectorCursor(face=SQUARE, design_size=32)

    def test_design_hotspot_maps_to_each_nominal_size(self):
        self.assertEqual(
            cursor_vector.vector_hotspot((3, 3), self.art, 16), (1, 1))
        self.assertEqual(
            cursor_vector.vector_hotspot((3, 3), self.art, 24), (2, 2))
        self.assertEqual(
            cursor_vector.vector_hotspot((3, 3), self.art, 32), (3, 3))

    def test_fractional_hotspot_floors_and_stays_inside_the_frame(self):
        self.assertEqual(
            cursor_vector.vector_hotspot((31.9, 31.9), self.art, 16), (15, 15))

    def test_rejects_a_hotspot_at_or_beyond_the_design_size(self):
        with self.assertRaisesRegex(ValueError, "hotspot x"):
            cursor_vector.vector_hotspot((32, 0), self.art, 16)

    def test_rejects_a_hotspot_that_is_not_a_pair_of_numbers(self):
        with self.assertRaisesRegex(ValueError, "hotspot"):
            cursor_vector.vector_hotspot((3,), self.art, 16)
        with self.assertRaisesRegex(ValueError, "hotspot y"):
            cursor_vector.vector_hotspot((3, "3"), self.art, 16)


if __name__ == "__main__":
    unittest.main()
