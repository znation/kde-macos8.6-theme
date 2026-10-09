"""Tests for the desktop theme's slider.svg Platinum slider artwork."""

from __future__ import annotations

import unittest

from desktoptheme_paths import SLIDER_SVG
from nine_slice_case import NineSliceCase
from platinum_palette import FACE, PLATINUM_FILLS
from svg_assertions import (
    assert_face_bevel,
    assert_hint_geometry,
    assert_slice_pixels,
    assert_unique_ids,
    attribute_values,
    render_slices,
)


GROOVE = "groove"
TROUGH = "#EEEEEE"

# The two handle groups are id-bearing but are not nine-slice tiles, so they
# sit outside the margin-hint layout and must be pinned at the origin.
HANDLES = {
    "horizontal-slider-handle": (0, 0),
    "vertical-slider-handle": (0, 0),
}


def raised_thumb_pixels(width, height):
    """Return the {(x, y): fill} map of a raised Platinum thumb.

    The 1px #000000 outline is the outer ring; inside it a 1px bevel runs
    #FFFFFF on the top/left edges and #999999 on the bottom/right ones, and
    the vertical bevel is painted over the horizontal so the two edges turn
    the corners the way the scroll bar thumb's corner slices do. Every
    remaining pixel is the #DDDDDD face.
    """
    pixels = {}
    for y in range(height):
        for x in range(width):
            if x in (0, width - 1) or y in (0, height - 1):
                colour = "#000000"
            elif x == 1:
                colour = "#FFFFFF"
            elif x == width - 2:
                colour = "#999999"
            elif y == 1:
                colour = "#FFFFFF"
            elif y == height - 2:
                colour = "#999999"
            else:
                colour = FACE
            pixels[(x, y)] = colour
    return pixels


class TestSlider(NineSliceCase, unittest.TestCase):
    SVG_PATH = SLIDER_SVG
    PREFIXES = (GROOVE,)
    EXTRA_GROUPS = HANDLES

    def test_slider_ids_are_unique(self):
        # The handle groups sit outside the nine-slice layout, so the
        # inherited structural checks never key them; pin that no id in the
        # file collides before any id-keyed map reads it.
        assert_unique_ids(self, self.tree)

    def test_slider_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin or
        # centre hint with the wrong position or size passes it while KSvg
        # lays the track out wrong. Pin all five: a 3px border around a 10px
        # centre tile on the 16x16 canvas, so the track is 6px thick.
        assert_hint_geometry(self, self.tree, [GROOVE], 3, 10)

    def test_slider_groove_outline(self):
        # The groove is a flat #EEEEEE bar with a 1px #000000 outline: every
        # centre pixel is the trough fill, every edge slice's outer row/column
        # is black, and each square corner carries the two black outer edges.
        slices = render_slices(self.tree)
        assert_face_bevel(self, slices, GROOVE, TROUGH, "flat", size=10)

    def test_slider_handles_are_raised_thumbs(self):
        # The handles are raised #DDDDDD thumbs, not nine-slice tiles, so
        # render_slices composites each whole group: pin every pixel of both
        # orientations, including that the vertical one is 16x12.
        slices = render_slices(self.tree)
        assert_slice_pixels(
            self,
            slices,
            "horizontal-slider-handle",
            raised_thumb_pixels(12, 16),
        )
        assert_slice_pixels(
            self,
            slices,
            "vertical-slider-handle",
            raised_thumb_pixels(16, 12),
        )

    def test_slider_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the
        # artwork palette: trough, thumb face, outline, bevel highlight and
        # bevel shadow.
        self.assertEqual(
            attribute_values(self.tree, "fill"),
            PLATINUM_FILLS | {TROUGH},
        )


if __name__ == "__main__":
    unittest.main()
