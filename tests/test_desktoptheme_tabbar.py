"""Tests for the desktop theme's tabbar.svg Platinum tab-bar artwork."""

from __future__ import annotations

import os
import unittest

from desktoptheme_paths import TABBAR_SVG
from nine_slice_case import NineSliceCase
from process_assertions import assert_succeeded
from svg_assertions import (
    assert_center_tile_is,
    assert_corner_pixels,
    assert_edge_bevels,
    assert_face_corners,
    assert_hint_geometry,
    assert_no_script_elements,
    face_edge_bands,
    render_slices,
    RAISED_FACE_CORNERS,
)
from theme_install import installed_destdir, installed_package


TABBAR_PREFIXES = ("north-active-tab", "south-active-tab", "east-active-tab", "west-active-tab")

# Every pixel of each raised 3x3 corner slice, row-major in slice-local
# coordinates. The bevel must turn the corner: the edge bevel colours continue
# into the corner and meet there. A corner that stops the bevel one pixel short
# leaves a face-coloured (#DDDDDD) notch where the side tile shows highlight or
# shadow, so pinning the pixels makes that defect fail the suite.
#
# The raised state reuses `RAISED_FACE_CORNERS`' top-left, top-right and
# bottom-right corners; only its bottom-left corner turns differently, with a
# #999999 shadow where the scroll-bar thumb and dialog body show a #FFFFFF
# highlight.
CORNER_PIXELS = {
    "raised": {
        **RAISED_FACE_CORNERS,
        "bottomleft": (
            "#000000", "#FFFFFF", "#DDDDDD",
            "#000000", "#999999", "#999999",
            "#000000", "#000000", "#000000",
        ),
    },
}


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
            assert_center_tile_is(self, slices, f"{prefix}-center", "#DDDDDD", size=6)

    def test_tabbar_closed_edges_are_raised(self):
        slices = render_slices(self.tree)
        for prefix in TABBAR_PREFIXES:
            # Determine which edges are closed (have bevel) and which are open
            # (face only)
            if prefix == "north-active-tab":
                # bottom is open
                edges = {
                    "top": "raised",
                    "left": "raised",
                    "right": "raised",
                    "bottom": ("#DDDDDD",) * 3,
                }
            elif prefix == "south-active-tab":
                # top is open
                edges = {
                    "top": ("#DDDDDD",) * 3,
                    "left": "raised",
                    "right": "raised",
                    "bottom": "raised",
                }
            elif prefix == "east-active-tab":
                # left is open
                edges = {
                    "top": "raised",
                    "left": ("#DDDDDD",) * 3,
                    "right": "raised",
                    "bottom": "raised",
                }
            else:  # west-active-tab
                # right is open
                edges = {
                    "top": "raised",
                    "left": "raised",
                    "right": ("#DDDDDD",) * 3,
                    "bottom": "raised",
                }
            for edge, band in edges.items():
                if isinstance(band, tuple):
                    # Face-only edge: both outward and mirrored are the face band
                    assert_edge_bevels(self, slices, prefix, band, band, size=3)
                else:
                    # Raised edge: outward is the raised bevel, mirrored is the mirrored bevel
                    outward, mirrored = face_edge_bands("#DDDDDD", "raised")
                    assert_edge_bevels(self, slices, prefix, outward, mirrored, size=3)

    def test_tabbar_corners(self):
        slices = render_slices(self.tree)
        for prefix in TABBAR_PREFIXES:
            if prefix == "north-active-tab":
                corners = {
                    "topleft": RAISED_FACE_CORNERS["raised"]["topleft"],
                    "topright": RAISED_FACE_CORNERS["raised"]["topright"],
                    "bottomleft": CORNER_PIXELS["raised"]["bottomleft"],
                    "bottomright": RAISED_FACE_CORNERS["raised"]["bottomright"],
                }
            elif prefix == "south-active-tab":
                corners = {
                    "topleft": RAISED_FACE_CORNERS["raised"]["topleft"],
                    "topright": RAISED_FACE_CORNERS["raised"]["topright"],
                    "bottomleft": RAISED_FACE_CORNERS["raised"]["bottomleft"],
                    "bottomright": CORNER_PIXELS["raised"]["bottomright"],
                }
            elif prefix == "east-active-tab":
                corners = {
                    "topleft": RAISED_FACE_CORNERS["raised"]["topleft"],
                    "topright": RAISED_FACE_CORNERS["raised"]["topright"],
                    "bottomleft": RAISED_FACE_CORNERS["raised"]["bottomleft"],
                    "bottomright": RAISED_FACE_CORNERS["raised"]["bottomright"],
                }
            else:  # west-active-tab
                corners = {
                    "topleft": RAISED_FACE_CORNERS["raised"]["topleft"],
                    "topright": RAISED_FACE_CORNERS["raised"]["topright"],
                    "bottomleft": RAISED_FACE_CORNERS["raised"]["bottomleft"],
                    "bottomright": RAISED_FACE_CORNERS["raised"]["bottomright"],
                }
            assert_corner_pixels(self, slices, prefix, corners)

    def test_tabbar_colours(self):
        slices = render_slices(self.tree)
        assert self.attribute_values(slices, "fill") == {
            "#000000",
            "#FFFFFF",
            "#999999",
            "#DDDDDD",
        }

    def test_tabbar_no_script_elements(self):
        assert_no_script_elements(self, self.tree)

    def test_tabbar_installed(self):
        with installed_destdir(self) as tmp:
            target = os.path.join(
                installed_package(tmp, "desktoptheme", "org.macos8.desktop"),
                "widgets", "tabbar.svg",
            )
            assert_files_identical(self, TABBAR_SVG, target)
            again = install(tmp)
            assert_succeeded(self, again)


if __name__ == "__main__":
    unittest.main()
