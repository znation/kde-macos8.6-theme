"""Tests for the desktop theme's panel-background.svg menu-bar artwork."""

from __future__ import annotations

import unittest

from desktoptheme_paths import PANEL_SVG
from nine_slice_case import NineSliceCase
from platinum_palette import PLATINUM_FILLS
from svg_assertions import (
    assert_center_tile_is,
    assert_slice_ids_present,
    assert_slice_pixels,
    attribute_values,
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


class TestPanelBackground(NineSliceCase, unittest.TestCase):
    SVG_PATH = PANEL_SVG

    def test_nine_slice_ids_present(self):
        assert_slice_ids_present(self, self.tree, [""])

    def test_panel_background_hint_geometry(self):
        # `test_hint_ids_present` pins only the hint ids, so a margin or inset
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
            },
        )

    def test_platinum_colours_present(self):
        # Read the parsed artwork's fill attributes, not the raw file: the
        # header comment names all four colours, so a text search would pass
        # even if the artwork used none of them.
        fills = attribute_values(self.tree, "fill")
        self.assertEqual(fills, PLATINUM_FILLS)

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


if __name__ == "__main__":
    unittest.main()
