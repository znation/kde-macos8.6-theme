"""Tests for the desktop theme's switch.svg Platinum toggle artwork."""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import SWITCH_SVG
from support.nine_slice_case import NineSliceCase
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    TROUGH,
    WHITE,
    assert_fill_palette,
)
from svg_assertions import (
    assert_face_bevel,
    assert_hint_geometry,
    assert_slice_pixels,
    assert_unique_ids,
    render_slices,
)


INACTIVE = "inactive"
ACTIVE = "active"

# The four thumb groups are id-bearing but are not nine-slice tiles, so they
# sit outside the margin-hint layout and must be pinned at the origin.
THUMBS = {
    "handle": (0, 0),
    "handle-hover": (0, 0),
    "handle-pressed": (0, 0),
    "handle-focus": (0, 0),
}

# `hint-bar-size` is the track SwitchIndicator sizes the inactive FrameSvg to;
# it is not a nine-slice tile, so it is merged into the hint geometry.
BAR_SIZE = {"hint-bar-size": ("0", "0", "30", "16")}


def thumb_pixels(width, height, top_left, bottom_right):
    """Return the {(x, y): fill} map of a 1px-outlined beveled Platinum thumb.

    The 1px #000000 outline is the outer ring; inside it a 1px bevel runs
    *top_left* on the top/left edges and *bottom_right* on the bottom/right
    ones, and the vertical bevel is painted over the horizontal so the two
    edges turn the corners the way the slider thumb's do. Every remaining
    pixel is the #DDDDDD face. *top_left* and *bottom_right* are #FFFFFF and
    #999999 for the raised thumb, swapped for the pressed one.
    """
    pixels = {}
    for y in range(height):
        for x in range(width):
            if x in (0, width - 1) or y in (0, height - 1):
                colour = BLACK
            elif x == 1:
                colour = top_left
            elif x == width - 2:
                colour = bottom_right
            elif y == 1:
                colour = top_left
            elif y == height - 2:
                colour = bottom_right
            else:
                colour = FACE
            pixels[(x, y)] = colour
    return pixels


def raised_thumb_pixels(width, height):
    """Return the raised thumb: white highlight top/left, grey shadow bottom/right."""
    return thumb_pixels(width, height, WHITE, GREY)


def sunken_thumb_pixels(width, height):
    """Return the pressed thumb: grey shadow top/left, white highlight bottom/right."""
    return thumb_pixels(width, height, GREY, WHITE)


def ring_pixels(width, height):
    """Return only the 1px #000000 outer ring of a *width* x *height* thumb.

    The focus ring's inside is transparent, so the map carries no interior
    points; `render_slices` records only the painted ring rects.
    """
    return {
        (x, y): BLACK
        for y in range(height)
        for x in range(width)
        if x in (0, width - 1) or y in (0, height - 1)
    }


class TestSwitch(NineSliceCase, unittest.TestCase):
    SVG_PATH = SWITCH_SVG
    PREFIXES = (INACTIVE, ACTIVE)
    EXTRA_GROUPS = THUMBS

    def test_switch_ids_are_unique(self):
        # The thumb groups sit outside the nine-slice layout, so the
        # inherited structural checks never key them; pin that no id in the
        # file collides before any id-keyed map reads it.
        assert_unique_ids(self, self.tree)

    def test_switch_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin or
        # centre hint with the wrong position or size passes it while KSvg
        # lays the track out wrong. Pin all five of each state: a 3px border
        # around a 10px centre tile, plus the 30x16 track size.
        assert_hint_geometry(
            self, self.tree, [INACTIVE, ACTIVE], 3, 10, BAR_SIZE
        )

    def test_switch_tracks(self):
        # Both tracks are flat faces with a 1px #000000 outline: the inactive
        # the #EEEEEE trough, the active the #FFFFFF field, each with the
        # black outer edge on every slice and the two black corner edges.
        slices = render_slices(self.tree)
        assert_face_bevel(self, slices, INACTIVE, TROUGH, "flat", size=10)
        assert_face_bevel(self, slices, ACTIVE, WHITE, "flat", size=10)

    def test_switch_thumb_bevel(self):
        # The thumbs are 12x18 raised/pressed faces plus a focus ring, not
        # nine-slice tiles, so render_slices composites each whole group: pin
        # every pixel of each, including that handle-hover matches handle and
        # that handle-focus is a ring with a transparent inside.
        slices = render_slices(self.tree)
        assert_slice_pixels(self, slices, "handle", raised_thumb_pixels(12, 18))
        assert_slice_pixels(
            self, slices, "handle-hover", raised_thumb_pixels(12, 18)
        )
        assert_slice_pixels(
            self, slices, "handle-pressed", sunken_thumb_pixels(12, 18)
        )
        assert_slice_pixels(
            self, slices, "handle-focus", ring_pixels(12, 18)
        )

    def test_switch_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the
        # artwork palette: the two track faces, the thumb face, the outline,
        # the bevel highlight and the bevel shadow.
        assert_fill_palette(self, self.tree, {TROUGH})


if __name__ == "__main__":
    unittest.main()
