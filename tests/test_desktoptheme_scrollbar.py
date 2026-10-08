"""Tests for the desktop theme's scrollbar.svg Platinum scroll bar artwork."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from desktoptheme_paths import SCROLLBAR_SVG
from svg_assertions import (
    assert_corner_pixels,
    assert_no_script_elements,
    assert_slice_ids_present,
    assert_tiles_placed_by_margins,
    attribute_values,
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
        expected = {
            "hint-tile-center": ("3", "3", "10", "10"),
            "hint-scrollbar-size": ("0", "0", "16", "16"),
        }
        for prefix in PREFIXES:
            expected.update({
                f"{prefix}-hint-top-margin": ("3", "0", "10", "3"),
                f"{prefix}-hint-bottom-margin": ("3", "13", "10", "3"),
                f"{prefix}-hint-left-margin": ("0", "3", "3", "10"),
                f"{prefix}-hint-right-margin": ("13", "3", "3", "10"),
            })
        self.assertEqual(rect_geometry(ET.parse(SCROLLBAR_SVG)), expected)

    def test_scrollbar_tiles_placed_by_margins(self):
        assert_tiles_placed_by_margins(self, ET.parse(SCROLLBAR_SVG), list(PREFIXES))

    def test_scrollbar_trough_outline(self):
        # The trough is a flat #EEEEEE bar with a 1px #000000 outline: every
        # centre pixel is the trough fill, every edge slice's outer row/column
        # is black, and each square corner carries the two black outer edges.
        slices = render_slices(ET.parse(SCROLLBAR_SVG))
        for prefix in TROUGH_PREFIXES:
            centre = slices[f"{prefix}-center"]
            self.assertEqual(set(centre.values()), {TROUGH})
            self.assertEqual(len(centre), 100)
            top = slices[f"{prefix}-top"]
            bottom = slices[f"{prefix}-bottom"]
            left = slices[f"{prefix}-left"]
            right = slices[f"{prefix}-right"]
            for x in range(10):
                self.assertEqual(top[(x, 0)], BLACK, f"{prefix}-top ({x},0)")
                self.assertEqual(top[(x, 1)], TROUGH, f"{prefix}-top ({x},1)")
                self.assertEqual(top[(x, 2)], TROUGH, f"{prefix}-top ({x},2)")
                self.assertEqual(bottom[(x, 0)], TROUGH, f"{prefix}-bottom ({x},0)")
                self.assertEqual(bottom[(x, 1)], TROUGH, f"{prefix}-bottom ({x},1)")
                self.assertEqual(bottom[(x, 2)], BLACK, f"{prefix}-bottom ({x},2)")
            for y in range(10):
                self.assertEqual(left[(0, y)], BLACK, f"{prefix}-left (0,{y})")
                self.assertEqual(left[(1, y)], TROUGH, f"{prefix}-left (1,{y})")
                self.assertEqual(left[(2, y)], TROUGH, f"{prefix}-left (2,{y})")
                self.assertEqual(right[(0, y)], TROUGH, f"{prefix}-right (0,{y})")
                self.assertEqual(right[(1, y)], TROUGH, f"{prefix}-right (1,{y})")
                self.assertEqual(right[(2, y)], BLACK, f"{prefix}-right (2,{y})")
            assert_corner_pixels(
                self, slices, f"{prefix}-topleft",
                (BLACK, BLACK, BLACK, BLACK, TROUGH, TROUGH, BLACK, TROUGH, TROUGH),
            )
            assert_corner_pixels(
                self, slices, f"{prefix}-topright",
                (BLACK, BLACK, BLACK, TROUGH, TROUGH, BLACK, TROUGH, TROUGH, BLACK),
            )
            assert_corner_pixels(
                self, slices, f"{prefix}-bottomleft",
                (BLACK, TROUGH, TROUGH, BLACK, TROUGH, TROUGH, BLACK, BLACK, BLACK),
            )
            assert_corner_pixels(
                self, slices, f"{prefix}-bottomright",
                (TROUGH, TROUGH, BLACK, TROUGH, TROUGH, BLACK, BLACK, BLACK, BLACK),
            )

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
            centre = slices[f"{prefix}-center"]
            self.assertEqual(set(centre.values()), {FACE})
            self.assertEqual(len(centre), 100)
            top = slices[f"{prefix}-top"]
            bottom = slices[f"{prefix}-bottom"]
            left = slices[f"{prefix}-left"]
            right = slices[f"{prefix}-right"]
            for x in range(10):
                self.assertEqual(top[(x, 0)], BLACK, f"{prefix}-top ({x},0)")
                self.assertEqual(top[(x, 1)], WHITE, f"{prefix}-top ({x},1)")
                self.assertEqual(top[(x, 2)], FACE, f"{prefix}-top ({x},2)")
                self.assertEqual(bottom[(x, 0)], FACE, f"{prefix}-bottom ({x},0)")
                self.assertEqual(bottom[(x, 1)], GREY, f"{prefix}-bottom ({x},1)")
                self.assertEqual(bottom[(x, 2)], BLACK, f"{prefix}-bottom ({x},2)")
            for y in range(10):
                self.assertEqual(left[(0, y)], BLACK, f"{prefix}-left (0,{y})")
                self.assertEqual(left[(1, y)], WHITE, f"{prefix}-left (1,{y})")
                self.assertEqual(left[(2, y)], FACE, f"{prefix}-left (2,{y})")
                self.assertEqual(right[(0, y)], FACE, f"{prefix}-right (0,{y})")
                self.assertEqual(right[(1, y)], GREY, f"{prefix}-right (1,{y})")
                self.assertEqual(right[(2, y)], BLACK, f"{prefix}-right (2,{y})")
            assert_corner_pixels(
                self, slices, f"{prefix}-topleft",
                (BLACK, BLACK, BLACK, BLACK, WHITE, WHITE, BLACK, WHITE, FACE),
            )
            assert_corner_pixels(
                self, slices, f"{prefix}-topright",
                (BLACK, BLACK, BLACK, WHITE, GREY, BLACK, FACE, GREY, BLACK),
            )
            assert_corner_pixels(
                self, slices, f"{prefix}-bottomleft",
                (BLACK, WHITE, FACE, BLACK, WHITE, GREY, BLACK, BLACK, BLACK),
            )
            assert_corner_pixels(
                self, slices, f"{prefix}-bottomright",
                (FACE, GREY, BLACK, GREY, GREY, BLACK, BLACK, BLACK, BLACK),
            )

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
