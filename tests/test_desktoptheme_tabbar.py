"""Tests for the desktop theme's tabbar.svg Platinum tab-bar artwork."""

from __future__ import annotations

import unittest

from support.aurorae_fixtures import PROFILER_REFERENCE, PROFILER_ROWS
from support.desktoptheme_paths import TABBAR_SVG
from support.nine_slice_case import NineSliceCase
from support.platinum_palette import hex_colour
from support.reference_image import ReferenceScreenshotMixin
from svg_assertions import (
    assert_center_tile_is,
    assert_edge_band_pixels,
    assert_face_corners,
    assert_hint_geometry,
    attribute_values,
    render_slices,
)


TABBAR_PREFIXES = ("north-active-tab", "south-active-tab", "east-active-tab", "west-active-tab")

# The edge that faces the panel content is open (face only) so the tab merges
# with it; the other three edges carry the raised bevel.
OPEN_EDGE = {
    "north-active-tab": "bottom",
    "south-active-tab": "top",
    "east-active-tab": "left",
    "west-active-tab": "right",
}

FACE = "#EEEEEE"
MIDTONE = "#CCCCCC"
HIGHLIGHT = "#FFFFFF"
FLAT_BAND = (FACE,) * 3
TOP_LEFT_BAND = ("#000000", MIDTONE, HIGHLIGHT)
BOTTOM_RIGHT_BAND = (FACE, "#999999", "#000000")
EDGE_BANDS = {
    "top": TOP_LEFT_BAND,
    "left": TOP_LEFT_BAND,
    "bottom": BOTTOM_RIGHT_BAND,
    "right": BOTTOM_RIGHT_BAND,
}


def band_rows(band):
    """The 3x3 corner whose rows are each the colour of *band* in turn."""
    return tuple(colour for colour in band for _ in range(3))


def band_columns(band):
    """The 3x3 corner whose rows each repeat *band* left to right."""
    return band * 3


def raised_tab_corners(face, midtone, highlight):
    """The four 3x3 fully-raised tab corners for *face*, *midtone*, *highlight*.

    `svg_assertions.face_corners` hard-codes the #DDDDDD/#FFFFFF button
    raised face, but the selected tab's face is #EEEEEE with a #CCCCCC
    mid-tone and a #FFFFFF highlight, so the tab's raised corners are built
    here instead. The top/left band is three deep (outline, mid-tone,
    highlight), so the corner carries all three.
    """
    return {
        "topleft": (
            "#000000", "#000000", "#000000",
            "#000000", midtone, midtone,
            "#000000", midtone, highlight,
        ),
        "topright": (
            "#000000", "#000000", "#000000",
            midtone, "#999999", "#000000",
            highlight, "#999999", "#000000",
        ),
        "bottomleft": (
            "#000000", midtone, highlight,
            "#000000", midtone, "#999999",
            "#000000", "#000000", "#000000",
        ),
        "bottomright": (
            face, "#999999", "#000000",
            "#999999", "#999999", "#000000",
            "#000000", "#000000", "#000000",
        ),
    }


def tab_corners(open_edge):
    """The four 3x3 corners of a tab whose *open_edge* is left open.

    A corner between two raised edges is the raised-face corner. A corner
    where the open edge meets a raised edge extends that raised edge's band
    across its whole tile, because the open side contributes only face.
    """
    corners = raised_tab_corners(FACE, MIDTONE, HIGHLIGHT)
    mixed = {
        "bottom": {
            "bottomleft": band_columns(EDGE_BANDS["left"]),
            "bottomright": band_columns(EDGE_BANDS["right"]),
        },
        "top": {
            "topleft": band_columns(EDGE_BANDS["left"]),
            "topright": band_columns(EDGE_BANDS["right"]),
        },
        "left": {
            "topleft": band_rows(EDGE_BANDS["top"]),
            "bottomleft": band_rows(EDGE_BANDS["bottom"]),
        },
        "right": {
            "topright": band_rows(EDGE_BANDS["top"]),
            "bottomright": band_rows(EDGE_BANDS["bottom"]),
        },
    }
    corners.update(mixed[open_edge])
    return corners


class TestTabBar(NineSliceCase, unittest.TestCase):
    SVG_PATH = TABBAR_SVG
    PREFIXES = TABBAR_PREFIXES

    def test_tabbar_palette(self):
        # Read the raw file for the palette: the tab's hints deliberately
        # avoid the Platinum colours, so every hit here comes from the artwork.
        with open(TABBAR_SVG, encoding="utf-8") as handle:
            text = handle.read()
        for colour in ("#CCCCCC", "#EEEEEE", "#FFFFFF", "#999999", "#000000"):
            self.assertIn(colour, text)

    def test_tabbar_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin hint
        # naming the wrong tile size or border passes it. KSvg reads this
        # geometry to lay out the nine-slice, so pin each state's margins and
        # the shared centre tile.
        assert_hint_geometry(self, self.tree, TABBAR_PREFIXES, 3, 6)

    def test_tabbar_centres_are_the_face(self):
        slices = render_slices(self.tree)
        for prefix in TABBAR_PREFIXES:
            assert_center_tile_is(self, slices, f"{prefix}-center", FACE, size=6)

    def test_tabbar_closed_edges_are_raised(self):
        slices = render_slices(self.tree)
        for prefix in TABBAR_PREFIXES:
            for side, band in EDGE_BANDS.items():
                if side != OPEN_EDGE[prefix]:
                    assert_edge_band_pixels(
                        self, slices, f"{prefix}-{side}", side, band
                    )

    def test_tabbar_inner_edges_are_open(self):
        slices = render_slices(self.tree)
        for prefix in TABBAR_PREFIXES:
            side = OPEN_EDGE[prefix]
            assert_edge_band_pixels(
                self, slices, f"{prefix}-{side}", side, FLAT_BAND
            )

    def test_tabbar_corners(self):
        slices = render_slices(self.tree)
        for prefix in TABBAR_PREFIXES:
            assert_face_corners(self, slices, prefix, tab_corners(OPEN_EDGE[prefix]))

    def test_tabbar_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the
        # artwork palette: the #EEEEEE selected-tab face, the #CCCCCC
        # mid-tone, the #FFFFFF highlight, the #999999 shadow and the
        # #000000 outline.
        self.assertEqual(
            attribute_values(self.tree, "fill"),
            {"#000000", "#CCCCCC", "#EEEEEE", "#FFFFFF", "#999999"},
        )


# The retail 8.6 System Profiler window's selected first tab
# ("システム情報"): at its column x=260 the top edge is the three-band bevel
# over the face, and at its row y=60 the left edge is the same three bands.
# Its bottom (y=72) is open, i.e. face only. The reference is a lossless
# 1x screenshot, so the sampled pixels are the shipped nine-slice's bands.
SELECTED_COLUMN = 260
SELECTED_ROW = 60
TOP_BAND_Y = (54, 55, 56, 57)
TOP_BAND = ("#000000", MIDTONE, HIGHLIGHT, FACE)
OPEN_BOTTOM_Y = 72
LEFT_BAND_X = (225, 226, 227, 228)
LEFT_BAND = ("#000000", MIDTONE, HIGHLIGHT, FACE)


class TestTabBarReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = PROFILER_REFERENCE
    MAX_ROWS = PROFILER_ROWS

    def test_selected_tab_top_band(self):
        # The selected tab's top edge is #000000 outline, #CCCCCC mid-tone,
        # #FFFFFF highlight over the #EEEEEE face, re-derived here rather
        # than trusted from the artwork's constants.
        for y, colour in zip(TOP_BAND_Y, TOP_BAND):
            with self.subTest(y=y):
                self.assertEqual(
                    hex_colour(self.pixel(SELECTED_COLUMN, y)),
                    colour,
                    (SELECTED_COLUMN, y),
                )

    def test_selected_tab_left_edge(self):
        for x, colour in zip(LEFT_BAND_X, LEFT_BAND):
            with self.subTest(x=x):
                self.assertEqual(
                    hex_colour(self.pixel(x, SELECTED_ROW)),
                    colour,
                    (x, SELECTED_ROW),
                )

    def test_selected_tab_bottom_is_open(self):
        self.assertEqual(
            hex_colour(self.pixel(SELECTED_COLUMN, OPEN_BOTTOM_Y)), FACE
        )


if __name__ == "__main__":
    unittest.main()
