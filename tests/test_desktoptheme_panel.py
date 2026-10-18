"""Tests for the desktop theme's panel-background.svg menu-bar artwork."""

from __future__ import annotations

import os
import unittest
import xml.etree.ElementTree as ET

from support.desktoptheme_paths import PANEL_SVG
from support.nine_slice_case import NineSliceCase
from support.platinum_palette import assert_fill_palette, hex_colour
from support.reference_image import ReferenceScreenshotMixin
from support.repo_root import ROOT
from svg_assertions import (
    assert_center_tile_is,
    assert_slice_pixels,
    pixel_map,
    rect_geometry,
    render_slices,
)


# Every pixel of each panel-background edge/corner slice, row-major in
# slice-local coordinates (the centre tile is checked separately). The menu-bar
# bevel must run the right way: #FFFFFF on the outer top/left edge, #999999 on
# the inner bottom edge and the outer right edge, and the #000000 rule on the
# outer bottom edge. `test_platinum_colours_present` sees the same four fills
# whichever way the bevel runs, so only pinning the pixels catches a swapped
# highlight/shadow or the black rule moved to the wrong edge.
PANEL_EDGE_PIXELS = {
    "top": (8, 2, ("#FFFFFF",) * 8 + ("#DDDDDD",) * 8),
    "bottom": (8, 2, ("#999999",) * 8 + ("#000000",) * 8),
    "left": (2, 8, ("#FFFFFF", "#DDDDDD") * 8),
    "right": (2, 8, ("#DDDDDD", "#999999") * 8),
    "topleft": (2, 2, ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#DDDDDD")),
    "topright": (2, 2, ("#FFFFFF", "#999999", "#DDDDDD", "#999999")),
    "bottomleft": (2, 2, ("#999999", "#999999", "#000000", "#000000")),
    "bottomright": (2, 2, ("#999999", "#999999", "#000000", "#000000")),
}


# Every pixel of each `north-` slice (the top-edge panel state), row-major in
# slice-local coordinates. Row 0 of the 8x18 centre is the bar's white
# highlight, which Plasma never lets the top slices draw; rows 1..17 are the
# #DDDDDD body. The side slices continue that row 0 highlight.
NORTH_EDGE_PIXELS = {
    "north-top": (8, 2, ("#FFFFFF",) * 8 + ("#DDDDDD",) * 8),
    "north-bottom": (8, 2, ("#999999",) * 8 + ("#000000",) * 8),
    "north-left": (
        2, 18, ("#FFFFFF", "#FFFFFF") + ("#FFFFFF", "#DDDDDD") * 17
    ),
    "north-right": (
        2, 18, ("#FFFFFF", "#999999") + ("#DDDDDD", "#999999") * 17
    ),
    "north-center": (8, 18, ("#FFFFFF",) * 8 + ("#DDDDDD",) * 136),
    "north-topleft": (2, 2, ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#DDDDDD")),
    "north-topright": (2, 2, ("#FFFFFF", "#999999", "#DDDDDD", "#999999")),
    "north-bottomleft": (2, 2, ("#999999", "#999999", "#000000", "#000000")),
    "north-bottomright": (2, 2, ("#999999", "#999999", "#000000", "#000000")),
}


class TestPanelBackground(NineSliceCase, unittest.TestCase):
    SVG_PATH = PANEL_SVG
    PREFIXES = ("", "north")

    def test_panel_background_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin or inset
        # rect with the wrong position or size passes it. KSvg reads this
        # geometry to size the menu bar's nine-slice, so pin each hint.
        self.assertEqual(
            rect_geometry(self.tree),
            {
                "hint-tile-center": ("2", "2", "8", "8"),
                "hint-top-margin": ("2", "0", "2", "2"),
                "hint-bottom-margin": ("2", "10", "2", "2"),
                "hint-left-margin": ("0", "2", "2", "2"),
                "hint-right-margin": ("10", "2", "2", "2"),
                "hint-top-inset": ("2", "0", "8", "0"),
                "hint-bottom-inset": ("2", "12", "8", "0"),
                "hint-left-inset": ("0", "2", "0", "8"),
                "hint-right-inset": ("12", "2", "0", "8"),
                "north-hint-top-margin": ("2", "0", "2", "2"),
                "north-hint-bottom-margin": ("2", "20", "2", "2"),
                "north-hint-left-margin": ("0", "2", "2", "2"),
                "north-hint-right-margin": ("10", "2", "2", "2"),
                "north-hint-top-inset": ("2", "0", "8", "0"),
                "north-hint-bottom-inset": ("2", "22", "8", "0"),
                "north-hint-left-inset": ("0", "2", "0", "18"),
                "north-hint-right-inset": ("12", "2", "0", "18"),
            },
        )

    def test_platinum_colours_present(self):
        # Read the parsed artwork's fill attributes, not the raw file: the
        # header comment names all four colours, so a text search would pass
        # even if the artwork used none of them.
        assert_fill_palette(self, self.tree)

    def test_panel_background_pixels(self):
        # `test_platinum_colours_present` pins only the set of fills, so a
        # highlight/shadow swap or a rule on the wrong edge passes it. Read
        # each edge/corner slice's pixels in paint order instead.
        slices = render_slices(self.tree)
        for name, (width, height, expected) in PANEL_EDGE_PIXELS.items():
            assert_slice_pixels(
                self, slices, name, pixel_map(expected, width, height)
            )
        # The centre tile is one body rect, so every pixel is the same face.
        assert_center_tile_is(self, slices, "center", "#DDDDDD", size=8)

    def test_north_state_pixels(self):
        # A top-edge panel draws the `north-` state, and Plasma draws only its
        # centre and bottom slices on the full-width bar, so the white row 0
        # must be in the centre's first row. Pin every pixel of all nine.
        slices = render_slices(self.tree)
        for name, (width, height, expected) in NORTH_EDGE_PIXELS.items():
            assert_slice_pixels(
                self, slices, name, pixel_map(expected, width, height)
            )


class TestNorthStateMatchesReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = os.path.join(
        ROOT, "macos8.6-screenshots", "desktop_betawiki.png"
    )

    def test_bar_column_equals_north_center_and_bottom(self):
        # Column 10 is clear of the screen corners and the Apple menu: rows
        # 0..17 are the centre tile's rows and rows 18..19 the bottom slice's.
        tree = ET.parse(PANEL_SVG)
        slices = render_slices(tree)

        def hex_at(y):
            return hex_colour(self.pixel(10, y))

        for y in range(18):
            with self.subTest(row=y):
                self.assertEqual(hex_at(y), slices["north-center"][(0, y)])
        for y in (18, 19):
            with self.subTest(row=y):
                self.assertEqual(
                    hex_at(y), slices["north-bottom"][(0, y - 18)]
                )


if __name__ == "__main__":
    unittest.main()
