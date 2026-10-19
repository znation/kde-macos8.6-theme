"""Tests for the desktop theme's scrollbar.svg Platinum scroll bar artwork."""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import (
    SCROLLBAR_SVG,
    SETUP_MAX_ROWS,
    SETUP_REFERENCE,
)
from support.nine_slice_case import NineSliceCase
from support.platinum_palette import (
    BLACK,
    FACE,
    TROUGH,
    assert_fill_palette,
    hex_colour,
)
from support.reference_image import ReferenceScreenshotMixin
from svg_assertions import (
    assert_face_bevel,
    assert_hint_geometry,
    render_slices,
)


TROUGH_PREFIXES = ("background-vertical", "background-horizontal")
THUMB_PREFIXES = ("slider", "mouseover-slider")
PREFIXES = TROUGH_PREFIXES + THUMB_PREFIXES

# The installer CD window's horizontal scroll bar, sampled for
# `[Colors:View] BackgroundAlternate`; see
# `test_colorscheme_reference.REFERENCE_SCROLLBAR`. The shared bound covers
# that anchor and this module's bottom rule at y=477, so the screenshot
# decodes once per run.
REFERENCE = SETUP_REFERENCE


class TestScrollbar(NineSliceCase, unittest.TestCase):
    SVG_PATH = SCROLLBAR_SVG
    PREFIXES = PREFIXES

    def test_scrollbar_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin or
        # track hint with the wrong position or size passes it while KSvg lays
        # the bar out wrong. Pin every hint: the four prefixes share a 3px
        # border around a 10px centre tile on the 16x16 canvas, and
        # `hint-scrollbar-size` names the 16px track.
        assert_hint_geometry(
            self,
            self.tree,
            PREFIXES,
            3,
            10,
            {"hint-scrollbar-size": ("0", "0", "16", "16")},
        )

    def test_scrollbar_trough_outline(self):
        # The trough is a flat #EEEEEE bar with a 1px #000000 outline: every
        # centre pixel is the trough fill, every edge slice's outer row/column
        # is black, and each square corner carries the two black outer edges.
        slices = render_slices(self.tree)
        for prefix in TROUGH_PREFIXES:
            assert_face_bevel(self, slices, prefix, TROUGH, "flat", size=10)

    def test_scrollbar_thumb_bevel(self):
        # The handle is a raised #DDDDDD thumb: a 1px #000000 outline with a
        # 1px bevel inside it (#FFFFFF top/left, #999999 bottom/right). The
        # hovered `mouseover-slider` state is pixel-identical to `slider`.
        slices = render_slices(self.tree)
        for name, pixels in slices.items():
            if name.startswith("slider-"):
                self.assertEqual(
                    pixels, slices["mouseover-" + name], name
                )
        for prefix in THUMB_PREFIXES:
            assert_face_bevel(self, slices, prefix, FACE, "raised", size=10)

    def test_scrollbar_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the
        # artwork palette: trough, thumb face, outline, bevel highlight and
        # bevel shadow.
        assert_fill_palette(self, self.tree, {TROUGH})


class TestScrollbarReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The trough fill and its outline must match the reference screenshot.

    `TestScrollbar` pins the artwork to `platinum_palette`, so a wrong
    `TROUGH`/`BLACK` pair passes it. The retail installer CD window shows the
    same 16px horizontal scroll bar -- a flat #EEEEEE band between the #000000
    rules at y=462 and y=477 -- so this ties the pinned fills to a screenshot.
    """

    REFERENCE = REFERENCE
    MAX_ROWS = SETUP_MAX_ROWS

    def test_trough_matches_reference(self):
        self.assertEqual(hex_colour(self.pixel(200, 470)), TROUGH)
        self.assertEqual(hex_colour(self.pixel(200, 462)), BLACK)
        self.assertEqual(hex_colour(self.pixel(200, 477)), BLACK)
        # The band is flat across the window, not only at the anchor column.
        for x in (50, 300, 400):
            with self.subTest(x=x):
                self.assertEqual(hex_colour(self.pixel(x, 470)), TROUGH)


if __name__ == "__main__":
    unittest.main()
