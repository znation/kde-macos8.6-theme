"""Tests for tools/png.py's Image type -- the decoded-image container.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import png  # noqa: E402


class TestImage(unittest.TestCase):
    def test_rejects_rgb_length_that_does_not_match_dimensions(self):
        # Image promises tightly packed width*height*3 bytes, but nothing
        # checked it: compare() slices rgb by channel and divides by the
        # declared pixel count, so a short or long buffer mis-measures and can
        # report a wrong MAE instead of failing. The invariant is enforced at
        # construction and the error names the actual and expected byte counts.
        for width, height, size in ((2, 2, 11), (2, 2, 13), (1, 1, 0)):
            with self.subTest(width=width, height=height, size=size):
                with self.assertRaises(png.PngError) as ctx:
                    png.Image(width, height, bytes(size))
                message = str(ctx.exception)
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
                with self.assertRaises(png.PngError) as ctx:
                    png.Image(width, height, b"")
                self.assertIn(f"{width}x{height}", str(ctx.exception))

    def test_rejects_bool_dimensions_despite_being_an_int_subclass(self):
        # bool is an int subclass, so True/False would pass an isinstance
        # check as 1/0 and build a 1x1 image carrying width=True; require a
        # genuine integer and name the offending dimension.
        for width, height in ((True, 1), (1, False), (True, True)):
            with self.subTest(width=width, height=height):
                with self.assertRaises(png.PngError) as ctx:
                    png.Image(width, height, bytes(3))
                self.assertIn("must be an integer", str(ctx.exception))

    def test_rejects_non_integer_dimensions_naming_the_value(self):
        # A non-int dimension used to reach the positivity comparison as an
        # opaque TypeError (a str) or report a non-integral byte count (a
        # float); the invariant names the offending dimension and its value.
        for width, height in (("2", 2), (2, "2"), (2.5, 2), (2, 2.5)):
            with self.subTest(width=width, height=height):
                with self.assertRaises(png.PngError) as ctx:
                    png.Image(width, height, b"")
                message = str(ctx.exception)
                self.assertIn("must be an integer", message)
                self.assertIn(repr(width), message)
                self.assertIn(repr(height), message)
