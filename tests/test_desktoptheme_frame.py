"""Tests for the desktop theme's frame.svg Platinum frame artwork."""

from __future__ import annotations

import os
import tempfile
import unittest

from desktoptheme_paths import DTHEME_ID, FRAME_SVG
from nine_slice_case import NineSliceCase
from svg_assertions import (
    assert_center_tile_is,
    assert_edge_bevels,
    assert_face_corners,
    assert_hint_geometry,
    face_edge_bands,
    flat_face_corners,
    RAISED_FACE_CORNERS,
    render_slices,
    sunken_face_corners,
)
from theme_install import assert_files_identical, install, installed_package


FRAME_PREFIXES = ("plain", "raised", "sunken")


# Every pixel of each raised/sunken 3x3 corner slice, row-major in slice-local
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
    "sunken": sunken_face_corners("#DDDDDD"),
}


class TestFrame(NineSliceCase, unittest.TestCase):
    SVG_PATH = FRAME_SVG
    PREFIXES = FRAME_PREFIXES

    def test_frame_palette(self):
        # Read the raw file for the palette: the frame's hints deliberately
        # avoid the Platinum colours, so every hit here comes from the artwork.
        with open(FRAME_SVG, encoding="utf-8") as handle:
            text = handle.read()
        for colour in ("#DDDDDD", "#FFFFFF", "#999999", "#000000"):
            self.assertIn(colour, text)

    def test_frame_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin hint
        # naming the wrong tile size or border passes it. KSvg reads this
        # geometry to lay out the nine-slice, so pin each state's margins and
        # the shared centre tile.
        assert_hint_geometry(self, self.tree, FRAME_PREFIXES, 3, 6)

    def test_frame_corner_bevels_turn_the_corner(self):
        slices = render_slices(self.tree)
        for prefix, corners in CORNER_PIXELS.items():
            assert_face_corners(self, slices, prefix, corners)

    def test_frame_plain_corners_are_flat(self):
        # `test_frame_corner_bevels_turn_the_corner` pins only the raised and
        # sunken corners, and `test_frame_edge_bevels` does not reach the
        # corners, so a plain corner that copy-pasted a bevel from a
        # neighbouring state leaves a #FFFFFF or #999999 pixel where the face
        # should be and passes every existing test. Pin every plain-corner
        # pixel: the face plus the 1px black outline on the two outer edges,
        # with no bevel.
        slices = render_slices(self.tree)
        assert_face_corners(self, slices, "plain", flat_face_corners("#DDDDDD"))

    def test_frame_edge_bevels(self):
        # `test_frame_corner_bevels_turn_the_corner` pins only the raised and
        # sunken corners; the edge slices carry the same bevel along the frame
        # and are otherwise checked by id alone, so a raised top painted with
        # the shadow colour (or a plain edge that grew a bevel) passes every
        # existing test. Pin each edge's pixels from its outer edge in, and
        # each state's centre tile to the face.
        slices = render_slices(self.tree)
        # (outer outline, bevel, inner face) read from the slice's outer edge
        # inward; plain has no bevel, so its middle band is the face.
        directions = {"plain": "flat", "raised": "raised", "sunken": "sunken"}
        for prefix in FRAME_PREFIXES:
            outward, mirrored = face_edge_bands("#DDDDDD", directions[prefix])
            assert_edge_bevels(self, slices, prefix, outward, mirrored)
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
