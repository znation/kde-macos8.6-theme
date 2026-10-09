"""Tests for the desktop theme's lineedit.svg text-field artwork."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from desktoptheme_paths import LINEEDIT_SVG
from svg_assertions import (
    assert_center_tile_is,
    assert_edge_bevels,
    assert_face_corners,
    assert_hint_geometry,
    assert_no_script_elements,
    assert_slice_ids_present,
    assert_slices_stay_within_their_tiles,
    assert_tiles_placed_by_margins,
    attribute_values,
    face_edge_bands,
    render_slices,
    sunken_face_corners,
)


class TestLineEdit(unittest.TestCase):
    def test_lineedit_slice_ids(self):
        assert_slice_ids_present(self, ET.parse(LINEEDIT_SVG), ["base"])

    def test_lineedit_hint_geometry(self):
        # `test_lineedit_slice_ids` pins only the hint ids, so a margin or
        # centre hint with the wrong position or size passes it while KSvg
        # lays the field out wrong. Pin every hint: a 3px border around a 6px
        # centre tile on the 12x12 canvas.
        assert_hint_geometry(self, ET.parse(LINEEDIT_SVG), ["base"], 3, 6)

    def test_lineedit_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the
        # artwork palette: white face/highlight, grey shadow, black outline.
        tree = ET.parse(LINEEDIT_SVG)
        fills = attribute_values(tree, "fill")
        self.assertEqual(fills, {"#FFFFFF", "#999999", "#000000"})

    def test_lineedit_face_is_white(self):
        # The field must not silently become the grey frame face: pin the
        # centre tile to #FFFFFF so a copy of frame.svg's sunken geometry
        # fails here.
        slices = render_slices(ET.parse(LINEEDIT_SVG))
        assert_center_tile_is(self, slices, "base-center", "#FFFFFF", size=6)

    def test_lineedit_edge_bevels_are_sunken(self):
        # `test_lineedit_colours` sees the same three fills whichever way the
        # bevel runs, so only the per-slice paint order pins the sunken
        # direction: the #999999 shadow sits inside the top/left outline and
        # the #FFFFFF highlight inside the bottom/right, with the white face
        # innermost. A swap (a raised field) passes every existing test.
        slices = render_slices(ET.parse(LINEEDIT_SVG))
        # (outer outline, bevel, inner face) read from the slice's outer edge
        # in; the bottom/right edges mirror the top/left.
        outward, mirrored = face_edge_bands("#FFFFFF", "sunken")
        assert_edge_bevels(self, slices, "base", outward, mirrored)

    def test_lineedit_corner_bevels_turn_the_corner(self):
        # The edge bevel must continue into the corner and meet there; a
        # corner that stops one pixel short leaves a white face-coloured
        # notch where the edge tile shows shadow or highlight. Pin every
        # pixel of each corner slice.
        slices = render_slices(ET.parse(LINEEDIT_SVG))
        assert_face_corners(
            self, slices, "base", sunken_face_corners("#FFFFFF")
        )

    def test_lineedit_tiles_placed_by_margins(self):
        # `test_lineedit_face_is_white` composites `base-center` slice-local,
        # so a `base-*` group translated off its slice would still pass. Pin
        # every tile's origin against the base margin hints.
        assert_tiles_placed_by_margins(self, ET.parse(LINEEDIT_SVG), ["base"])

    def test_lineedit_tiles_stay_within_their_margins(self):
        # The pixel tests read only points inside each tile, so an oversized
        # rect spilling into the neighbouring canvas region -- which KSvg
        # samples into that adjacent tile -- passes. Pin every slice to the
        # tile region its hints define.
        assert_slices_stay_within_their_tiles(
            self, ET.parse(LINEEDIT_SVG), ["base"]
        )

    def test_no_script_elements(self):
        assert_no_script_elements(self, ET.parse(LINEEDIT_SVG))


if __name__ == "__main__":
    unittest.main()
