"""Tests for tools/png.py's Image type -- the decoded-image container.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest

from error_assertions import error_message

import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import png


class TestImage(unittest.TestCase):
    def _image_error(self, width, height, rgb):
        """Assert Image construction rejects the arguments and return the message."""
        return error_message(self, png.PngError, png.Image, width, height, rgb)

    def test_rejects_rgb_length_that_does_not_match_dimensions(self):
        # Image promises tightly packed width*height*3 bytes, but nothing
        # checked it: compare() slices rgb by channel and divides by the
        # declared pixel count, so a short or long buffer mis-measures and can
        # report a wrong MAE instead of failing. The invariant is enforced at
        # construction and the error names the actual and expected byte counts.
        for width, height, size in ((2, 2, 11), (2, 2, 13), (1, 1, 0)):
            with self.subTest(width=width, height=height, size=size):
                message = self._image_error(width, height, bytes(size))
                self.assertIn(str(size), message)
                self.assertIn(str(width * height * 3), message)
                self.assertIn(f"{width}x{height}", message)

    def test_accepts_rgb_length_matching_dimensions(self):
        image = png.Image(2, 2, bytes(12))
        self.assertEqual(len(image.rgb), 12)

    def test_rejects_non_positive_dimensions(self):
        # decode_png rejects a zero-dimension PNG, but a directly constructed
        # Image accepted one: 0 * height * 3 == 0 bytes, so the byte-count
        # check passed and compare() later raised an opaque ValueError from
        # _max_byte_index. A negative dimension was worse still, reporting a
        # nonsensical negative "needs" byte count. The invariant belongs at
        # construction, named with the offending dimensions.
        for width, height in ((0, 1), (1, 0), (0, 0), (-2, 3), (3, -1)):
            with self.subTest(width=width, height=height):
                self.assertIn(
                    f"{width}x{height}",
                    self._image_error(width, height, b""),
                )

    def test_rejects_bool_dimensions_despite_being_an_int_subclass(self):
        # bool is an int subclass, so True/False would pass an isinstance
        # check as 1/0 and build a 1x1 image carrying width=True; require a
        # genuine integer and name the offending dimension.
        for width, height in ((True, 1), (1, False), (True, True)):
            with self.subTest(width=width, height=height):
                self.assertIn(
                    "must be an integer",
                    self._image_error(width, height, bytes(3)),
                )

    def test_rejects_non_bytes_rgb_naming_its_type(self):
        # Only the rgb length was checked, so a str or list of the right
        # length constructed an Image and then failed inside compare() with an
        # opaque TypeError ("can only concatenate str (not bytes) to str")
        # naming neither the field nor the offending type. Reject it at
        # construction, by type. memoryview is included because it also fails
        # later (_abs_diff cannot concatenate a memoryview with bytes).
        for rgb in ("abc", [1, 2, 3], memoryview(b"abc"), 1):
            with self.subTest(rgb=type(rgb).__name__):
                message = self._image_error(1, 1, rgb)
                self.assertIn("rgb", message)
                self.assertIn(type(rgb).__name__, message)

    def test_accepts_bytearray_rgb(self):
        # A bytearray supports every operation compare() and crop() perform on
        # rgb, so it stays a valid input alongside bytes.
        image = png.Image(1, 1, bytearray(b"abc"))
        self.assertEqual(image.rgb, bytearray(b"abc"))

    def test_rejects_non_integer_dimensions_naming_the_value(self):
        # A non-int dimension used to reach the positivity comparison as an
        # opaque TypeError (a str) or report a non-integral byte count (a
        # float); the invariant names the offending dimension and its value.
        for width, height in (("2", 2), (2, "2"), (2.5, 2), (2, 2.5)):
            with self.subTest(width=width, height=height):
                message = self._image_error(width, height, b"")
                self.assertIn("must be an integer", message)
                self.assertIn(repr(width), message)
                self.assertIn(repr(height), message)


class TestPixelAt(unittest.TestCase):
    def test_reads_the_pixel_at_a_coordinate(self):
        # Four distinct pixels, so a wrong offset or a row wrap reads a
        # different one instead of passing by coincidence.
        image = png.Image(2, 2, bytes(range(1, 13)))
        for x, y, expected in (
            (0, 0, (1, 2, 3)),
            (1, 0, (4, 5, 6)),
            (0, 1, (7, 8, 9)),
            (1, 1, (10, 11, 12)),
        ):
            with self.subTest(x=x, y=y):
                self.assertEqual(png.pixel_at(image, x, y), expected)

    def test_rejects_non_integer_coordinates_naming_the_value(self):
        # bool is an int subclass, so True/False passed the bounds comparison
        # as 1/0 and silently read a different pixel; a float, str or None
        # raised an opaque TypeError from the comparison ("'<=' not supported
        # between instances of 'int' and 'str'") or the RGB index ("byte
        # indices must be integers or slices, not float") that named neither
        # the coordinate nor pixel_at. Require a genuine integer, as the
        # Image dimensions already do, and name the offending value.
        image = png.Image(2, 2, bytes(range(1, 13)))
        for x, y, named in (
            (True, 0, "x"),
            (False, 0, "x"),
            (1.0, 0, "x"),
            ("1", 0, "x"),
            (None, 0, "x"),
            (0, True, "y"),
            (0, 1.0, "y"),
            (0, "0", "y"),
        ):
            with self.subTest(x=x, y=y):
                message = error_message(
                    self, ValueError, png.pixel_at, image, x, y
                )
                self.assertIn("must be an integer", message)
                value = x if named == "x" else y
                self.assertIn(f"{named}={value!r}", message)

    def test_rejects_coordinates_outside_the_image(self):
        # A coordinate outside the image must not be read: the RGB slice would
        # be empty, and an x past the row end would wrap to the next row and
        # return the wrong pixel. Pin that both the coordinate and the image
        # size are named.
        image = png.Image(2, 3, bytes(2 * 3 * 3))
        for x, y in ((2, 0), (0, 3), (-1, 0), (0, -1), (5, 5)):
            with self.subTest(x=x, y=y):
                message = error_message(
                    self, ValueError, png.pixel_at, image, x, y
                )
                self.assertIn(f"({x}, {y})", message)
                self.assertIn("2x3", message)
