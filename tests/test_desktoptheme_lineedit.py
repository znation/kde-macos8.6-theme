"""Tests for the desktop theme's lineedit.svg text-field artwork."""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import (
    FIRSTBOOT_MAX_ROWS,
    FIRSTBOOT_REFERENCE,
    LINEEDIT_SVG,
)
from support.firstboot_lineedit import FIELD_BORDER_RUNS, FIELD_CORNER_PIXELS
from support.nine_slice_case import NineSliceCase
from support.platinum_palette import hex_colour
from support.reference_image import ReferenceScreenshotMixin
from svg_assertions import (
    assert_center_tile_is,
    assert_edge_bevels,
    assert_face_corners,
    assert_hint_geometry,
    attribute_values,
    face_edge_bands,
    render_slices,
    sunken_outside_face_corners,
)


class TestLineEdit(NineSliceCase, unittest.TestCase):
    SVG_PATH = LINEEDIT_SVG
    PREFIXES = ("base",)

    def test_lineedit_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin or
        # centre hint with the wrong position or size passes it while KSvg
        # lays the field out wrong. Pin every hint: a 3px border around a 6px
        # centre tile on the 12x12 canvas.
        assert_hint_geometry(self, self.tree, ["base"], 3, 6)

    def test_lineedit_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the
        # artwork palette: white face/highlight, grey shadow, black outline.
        fills = attribute_values(self.tree, "fill")
        self.assertEqual(fills, {"#FFFFFF", "#999999", "#000000"})

    def test_lineedit_face_is_white(self):
        # The field must not silently become the grey frame face: pin the
        # centre tile to #FFFFFF so a copy of frame.svg's sunken geometry
        # fails here.
        slices = render_slices(self.tree)
        assert_center_tile_is(self, slices, "base-center", "#FFFFFF", size=6)

    def test_lineedit_edge_bevels_are_sunken_outside(self):
        # `test_lineedit_colours` sees the same three fills whichever way the
        # bevel runs, so only the per-slice paint order pins the direction:
        # the #999999 shadow sits outside the top/left outline and the
        # #FFFFFF highlight outside the bottom/right, with the white face
        # innermost. A swap (the outline outside the bevel) passes every
        # existing test.
        slices = render_slices(self.tree)
        # (outer bevel, outline, inner face) read from the slice's outer edge
        # in; the bottom/right edges mirror the top/left.
        outward, mirrored = face_edge_bands("#FFFFFF", "sunken-outside")
        assert_edge_bevels(self, slices, "base", outward, mirrored)

    def test_lineedit_corner_bevels_turn_the_corner(self):
        # The edge bevel must continue into the corner and meet there; a
        # corner that stops one pixel short leaves a white face-coloured
        # notch where the edge tile shows shadow or highlight. Pin every
        # pixel of each corner slice.
        slices = render_slices(self.tree)
        assert_face_corners(
            self, slices, "base", sunken_outside_face_corners("#FFFFFF")
        )


class TestLineEditReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = FIRSTBOOT_REFERENCE
    MAX_ROWS = FIRSTBOOT_MAX_ROWS

    def test_borders_are_the_sunken_bevel_outside_the_outline(self):
        # Re-derive the field's border runs from the reference rather than
        # trust the SVG comment: the outer ring is the bevel, the inner ring
        # the #000000 outline, and the face #FFFFFF.
        for (x, y), colour in FIELD_BORDER_RUNS:
            self.assertEqual(hex_colour(self.pixel(x, y)), colour, (x, y))

    def test_corners_match_the_reference(self):
        # The corner tiles are easy to get subtly wrong: the #000000 outline
        # stops one row short of the bottom row, and the top-right outer pixel
        # is the window face, not the shadow. Re-derive each from the
        # reference.
        for (x, y), colour in FIELD_CORNER_PIXELS:
            self.assertEqual(hex_colour(self.pixel(x, y)), colour, (x, y))


if __name__ == "__main__":
    unittest.main()
