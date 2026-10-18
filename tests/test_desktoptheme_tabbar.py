"""Tests for the desktop theme's tabbar.svg Platinum tab-bar artwork."""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import TABBAR_SVG
from support.nine_slice_case import NineSliceCase
from support.platinum_palette import assert_fill_palette
from svg_assertions import (
    assert_center_tile_is,
    assert_edge_band_pixels,
    assert_face_corners,
    assert_hint_geometry,
    face_corners,
    face_edge_bands,
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

FACE = "#DDDDDD"
FLAT_BAND = (FACE,) * 3
TOP_LEFT_BAND, BOTTOM_RIGHT_BAND = face_edge_bands(FACE, "raised")
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


def tab_corners(open_edge):
    """The four 3x3 corners of a tab whose *open_edge* is left open.

    A corner between two raised edges is the raised-face corner. A corner
    where the open edge meets a raised edge extends that raised edge's band
    across its whole tile, because the open side contributes only face.
    """
    corners = dict(face_corners(FACE, "raised"))
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
        for colour in ("#DDDDDD", "#FFFFFF", "#999999", "#000000"):
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
        assert_fill_palette(self, self.tree)


if __name__ == "__main__":
    unittest.main()
