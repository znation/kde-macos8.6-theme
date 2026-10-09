"""Tests for the desktop theme's viewitem.svg generic item highlight."""

from __future__ import annotations

import unittest

from desktoptheme_paths import VIEWITEM_SVG
from nine_slice_case import NineSliceCase
from svg_assertions import (
    assert_hint_geometry,
    assert_slices_fill_their_tiles,
    assert_slices_have_no_fill,
    assert_slices_uniform,
    attribute_values,
    render_slices,
)


class TestViewItem(NineSliceCase, unittest.TestCase):
    SVG_PATH = VIEWITEM_SVG
    PREFIXES = ("normal", "hover", "selected", "selected+hover")

    def test_viewitem_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin or
        # centre hint with the wrong position or size passes it while KSvg
        # lays the highlight out wrong. Pin every hint: all four prefixes
        # share a 3px border around a 6px centre tile on the 12x12 canvas.
        assert_hint_geometry(self, self.tree, self.PREFIXES, 3, 6)

    def test_viewitem_normal_has_no_fill(self):
        # An unhighlighted item paints nothing perceptible: the normal rects
        # carry no `fill` attribute and a 0.01 opacity, so only their margins
        # apply.
        assert_slices_have_no_fill(self, self.tree, "normal")

    def test_viewitem_highlights_are_flat_selection_colour(self):
        # Every highlight slice must be the flat selection fill, so the
        # highlight cannot silently gain a bevel or the grey button face.
        slices = render_slices(self.tree)
        for prefix in ("hover", "selected", "selected+hover"):
            assert_slices_uniform(self, slices, prefix, "#CCCCFF")

    def test_viewitem_slices_fill_their_tiles(self):
        # The colour tests above iterate each slice's pixels, so a rect one
        # pixel short (or long) passes while KSvg leaves a transparent stripe
        # in the stretched tile. Pin every slice to its exact tile region:
        # the three highlight prefixes are flat #CCCCFF, normal carries no
        # `fill` attribute (only a 0.01-opacity style), so render_slices
        # reads it as None.
        assert_slices_fill_their_tiles(
            self,
            render_slices(self.tree),
            (
                ("hover", "#CCCCFF"),
                ("selected", "#CCCCFF"),
                ("selected+hover", "#CCCCFF"),
                ("normal", None),
            ),
            3,
            6,
        )

    def test_viewitem_colours(self):
        # The hints and normal slices use `style`, so the parsed `fill` set is
        # exactly the selection fill.
        self.assertEqual(attribute_values(self.tree, "fill"), {"#CCCCFF"})


if __name__ == "__main__":
    unittest.main()
