"""Tests for the desktop theme's scrollbar.svg Platinum scroll bar artwork."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from desktoptheme_paths import SCROLLBAR_SVG
from svg_assertions import (
    assert_face_bevel,
    assert_no_script_elements,
    assert_slice_ids_present,
    assert_tiles_placed_by_margins,
    attribute_values,
    nine_slice_hint_geometry,
    rect_geometry,
    render_slices,
)


TROUGH_PREFIXES = ("background-vertical", "background-horizontal")
THUMB_PREFIXES = ("slider", "mouseover-slider")
PREFIXES = TROUGH_PREFIXES + THUMB_PREFIXES

BLACK = "#000000"
WHITE = "#FFFFFF"
GREY = "#999999"
FACE = "#DDDDDD"
TROUGH = "#EEEEEE"


class TestScrollbar(unittest.TestCase):
    def test_scrollbar_slice_ids(self):
        assert_slice_ids_present(self, ET.parse(SCROLLBAR_SVG), PREFIXES)

    def test_scrollbar_hint_geometry(self):
        # `test_scrollbar_slice_ids` pins only the hint ids, so a margin or
        # track hint with the wrong position or size passes it while KSvg lays
        # the bar out wrong. Pin every hint: the four prefixes share a 3px
        # border around a 10px centre tile on the 16x16 canvas, and
        # `hint-scrollbar-size` names the 16px track.
        expected = nine_slice_hint_geometry(PREFIXES, 3, 10)
        expected["hint-scrollbar-size"] = ("0", "0", "16", "16")
        self.assertEqual(rect_geometry(ET.parse(SCROLLBAR_SVG)), expected)

    def test_scrollbar_tiles_placed_by_margins(self):
        assert_tiles_placed_by_margins(self, ET.parse(SCROLLBAR_SVG), list(PREFIXES))

    def test_scrollbar_trough_outline(self):
        # The trough is a flat #EEEEEE bar with a 1px #000000 outline: every
        # centre pixel is the trough fill, every edge slice's outer row/column
        # is black, and each square corner carries the two black outer edges.
        slices = render_slices(ET.parse(SCROLLBAR_SVG))
        for prefix in TROUGH_PREFIXES:
            assert_face_bevel(self, slices, prefix, TROUGH, "flat", size=10)

    def test_scrollbar_thumb_bevel(self):
        # The handle is a raised #DDDDDD thumb: a 1px #000000 outline with a
        # 1px bevel inside it (#FFFFFF top/left, #999999 bottom/right). The
        # hovered `mouseover-slider` state is pixel-identical to `slider`.
        slices = render_slices(ET.parse(SCROLLBAR_SVG))
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
        self.assertEqual(
            attribute_values(ET.parse(SCROLLBAR_SVG), "fill"),
            {BLACK, WHITE, GREY, FACE, TROUGH},
        )

    def test_no_script_elements(self):
        assert_no_script_elements(self, ET.parse(SCROLLBAR_SVG))


if __name__ == "__main__":
    unittest.main()
