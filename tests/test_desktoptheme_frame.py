"""Tests for the desktop theme's frame.svg Platinum frame artwork."""

from __future__ import annotations

import os
import tempfile
import unittest
import xml.etree.ElementTree as ET

from desktoptheme_paths import DTHEME_ID, FRAME_SVG
from svg_assertions import (
    assert_center_tile_is,
    assert_corner_pixels,
    assert_edge_band_pixels,
    assert_no_script_elements,
    assert_slice_ids_present,
    assert_slices_stay_within_their_tiles,
    assert_tiles_placed_by_margins,
    nine_slice_margins,
    rect_geometry,
    render_slices,
)
from theme_install import assert_files_identical, install, installed_package


FRAME_PREFIXES = ("plain", "raised", "sunken")


# Every pixel of each raised/sunken 3x3 corner slice, row-major in slice-local
# coordinates. The bevel must turn the corner: the edge bevel colours continue
# into the corner and meet there. A corner that stops the bevel one pixel short
# leaves a face-coloured (#DDDDDD) notch where the side tile shows highlight or
# shadow, so pinning the pixels makes that defect fail the suite.
CORNER_PIXELS = {
    "raised": {
        "topleft": (
            "#000000", "#000000", "#000000",
            "#000000", "#FFFFFF", "#FFFFFF",
            "#000000", "#FFFFFF", "#DDDDDD",
        ),
        "topright": (
            "#000000", "#000000", "#000000",
            "#FFFFFF", "#999999", "#000000",
            "#DDDDDD", "#999999", "#000000",
        ),
        "bottomleft": (
            "#000000", "#FFFFFF", "#DDDDDD",
            "#000000", "#999999", "#999999",
            "#000000", "#000000", "#000000",
        ),
        "bottomright": (
            "#DDDDDD", "#999999", "#000000",
            "#999999", "#999999", "#000000",
            "#000000", "#000000", "#000000",
        ),
    },
    "sunken": {
        "topleft": (
            "#000000", "#000000", "#000000",
            "#000000", "#999999", "#999999",
            "#000000", "#999999", "#DDDDDD",
        ),
        "topright": (
            "#000000", "#000000", "#000000",
            "#999999", "#FFFFFF", "#000000",
            "#DDDDDD", "#FFFFFF", "#000000",
        ),
        "bottomleft": (
            "#000000", "#999999", "#DDDDDD",
            "#000000", "#FFFFFF", "#FFFFFF",
            "#000000", "#000000", "#000000",
        ),
        "bottomright": (
            "#DDDDDD", "#FFFFFF", "#000000",
            "#FFFFFF", "#FFFFFF", "#000000",
            "#000000", "#000000", "#000000",
        ),
    },
}


class TestFrame(unittest.TestCase):
    def test_frame_svg_contract(self):
        tree = ET.parse(FRAME_SVG)
        assert_slice_ids_present(self, tree, FRAME_PREFIXES)
        # Read the raw file for the palette: the frame's hints deliberately
        # avoid the Platinum colours, so every hit here comes from the artwork.
        with open(FRAME_SVG, encoding="utf-8") as handle:
            text = handle.read()
        for colour in ("#DDDDDD", "#FFFFFF", "#999999", "#000000"):
            self.assertIn(colour, text)
        assert_no_script_elements(self, tree)

    def test_frame_hint_geometry(self):
        # `test_frame_svg_contract` pins only the hint ids, so a margin hint
        # naming the wrong tile size or border passes it. KSvg reads this
        # geometry to lay out the nine-slice, so pin each state's margins and
        # the shared centre tile.
        expected = {"hint-tile-center": ("3", "3", "6", "6")}
        for prefix in FRAME_PREFIXES:
            expected.update(nine_slice_margins(prefix, 3, 6))
        self.assertEqual(rect_geometry(ET.parse(FRAME_SVG)), expected)

    def test_frame_tiles_placed_by_margins(self):
        # The pixel tests composite each slice from its rects but ignore the
        # group's translate, so a tile translated off its slice draws from the
        # wrong canvas region and still passes. Pin every state's tile origins
        # against its margin hints.
        assert_tiles_placed_by_margins(self, ET.parse(FRAME_SVG), FRAME_PREFIXES)

    def test_frame_tiles_stay_within_their_margins(self):
        # The edge/corner pixel tests composite each slice but read only points
        # inside its tile, so an oversized rect spilling into the neighbouring
        # canvas region -- which KSvg samples into that adjacent tile --
        # passes. Pin every slice to the tile region its hints define.
        assert_slices_stay_within_their_tiles(
            self, ET.parse(FRAME_SVG), FRAME_PREFIXES
        )

    def test_frame_corner_bevels_turn_the_corner(self):
        slices = render_slices(ET.parse(FRAME_SVG))
        for prefix, corners in CORNER_PIXELS.items():
            for name, expected in corners.items():
                assert_corner_pixels(self, slices, f"{prefix}-{name}", expected)

    def test_frame_plain_corners_are_flat(self):
        # `test_frame_corner_bevels_turn_the_corner` pins only the raised and
        # sunken corners, and `test_frame_edge_bevels` does not reach the
        # corners, so a plain corner that copy-pasted a bevel from a
        # neighbouring state leaves a #FFFFFF or #999999 pixel where the face
        # should be and passes every existing test. Pin every plain-corner
        # pixel: the face plus the 1px black outline on the two outer edges,
        # with no bevel.
        slices = render_slices(ET.parse(FRAME_SVG))
        expected = {
            "plain-topleft": (
                "#000000", "#000000", "#000000",
                "#000000", "#DDDDDD", "#DDDDDD",
                "#000000", "#DDDDDD", "#DDDDDD",
            ),
            "plain-topright": (
                "#000000", "#000000", "#000000",
                "#DDDDDD", "#DDDDDD", "#000000",
                "#DDDDDD", "#DDDDDD", "#000000",
            ),
            "plain-bottomleft": (
                "#000000", "#DDDDDD", "#DDDDDD",
                "#000000", "#DDDDDD", "#DDDDDD",
                "#000000", "#000000", "#000000",
            ),
            "plain-bottomright": (
                "#DDDDDD", "#DDDDDD", "#000000",
                "#DDDDDD", "#DDDDDD", "#000000",
                "#000000", "#000000", "#000000",
            ),
        }
        for name, colours in expected.items():
            assert_corner_pixels(self, slices, name, colours)

    def test_frame_edge_bevels(self):
        # `test_frame_corner_bevels_turn_the_corner` pins only the raised and
        # sunken corners; the edge slices carry the same bevel along the frame
        # and are otherwise checked by id alone, so a raised top painted with
        # the shadow colour (or a plain edge that grew a bevel) passes every
        # existing test. Pin each edge's pixels from its outer edge in, and
        # each state's centre tile to the face.
        slices = render_slices(ET.parse(FRAME_SVG))
        # (outer outline, bevel, inner face) read from the slice's outer edge
        # inward; plain has no bevel, so its middle band is the face.
        outward = {
            "plain": ("#000000", "#DDDDDD", "#DDDDDD"),
            "raised": ("#000000", "#FFFFFF", "#DDDDDD"),
            "sunken": ("#000000", "#999999", "#DDDDDD"),
        }
        # The bottom/right edges mirror the top/left: the outline stays on the
        # outer edge while the bevel colour swaps sides.
        mirrored = {
            "plain": ("#DDDDDD", "#DDDDDD", "#000000"),
            "raised": ("#DDDDDD", "#999999", "#000000"),
            "sunken": ("#DDDDDD", "#FFFFFF", "#000000"),
        }
        for prefix in FRAME_PREFIXES:
            for side in ("top", "bottom", "left", "right"):
                band = (
                    outward if side in ("top", "left") else mirrored
                )[prefix]
                assert_edge_band_pixels(
                    self, slices, f"{prefix}-{side}", side, band
                )
            # The centre tile is one body rect, so every pixel is the face.
            assert_center_tile_is(self, slices, f"{prefix}-center", "#DDDDDD", size=6)

    def test_frame_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = install(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            target = os.path.join(
                installed_package(tmp, "desktoptheme", DTHEME_ID),
                "widgets", "frame.svg",
            )
            assert_files_identical(self, FRAME_SVG, target)
            again = install(tmp)
            self.assertEqual(again.returncode, 0, again.stderr)


if __name__ == "__main__":
    unittest.main()
