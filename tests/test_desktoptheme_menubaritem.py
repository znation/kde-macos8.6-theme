"""Tests for the desktop theme's menubaritem.svg menu-bar title background."""

from __future__ import annotations

import unittest

from desktoptheme_paths import MENUBARITEM_SVG
from nine_slice_case import NineSliceCase
from svg_assertions import (
    assert_hint_geometry,
    assert_slices_fill_their_tiles,
    assert_slices_uniform,
    attribute_values,
    render_slices,
)


class TestMenuBarItem(NineSliceCase, unittest.TestCase):
    SVG_PATH = MENUBARITEM_SVG
    PREFIXES = ("normal", "hover", "pressed")

    def test_menubaritem_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin or
        # centre hint with the wrong position or size passes it while KSvg
        # lays the title out wrong. Pin every hint: all three prefixes share a
        # 3px border around a 6px centre tile on the 12x12 canvas.
        assert_hint_geometry(self, self.tree, self.PREFIXES, 3, 6)

    def test_menubaritem_normal_and_hover_have_no_fill(self):
        # An idle or merely hovered title paints nothing perceptible: the
        # normal and hover rects carry no `fill` attribute and a 0.01 opacity,
        # so only their margins apply.
        slices = render_slices(self.tree)
        for prefix in ("normal", "hover"):
            assert_slices_uniform(self, slices, prefix, None)
        self.assertEqual(attribute_values(self.tree, "fill-opacity"), {"0.01"})

    def test_menubaritem_pressed_is_flat_selection_colour(self):
        # Every pressed slice must be the flat selection fill, so the open-menu
        # title cannot silently gain a bevel or the grey button face.
        assert_slices_uniform(
            self, render_slices(self.tree), "pressed", "#CCCCFF"
        )

    def test_menubaritem_slices_fill_their_tiles(self):
        # The colour tests above iterate each slice's pixels, so a rect one
        # pixel short (or long) passes while KSvg leaves a transparent stripe
        # in the stretched tile. Pin every slice to its exact tile region:
        # pressed is flat #CCCCFF, normal and hover carry no `fill` attribute
        # (only a 0.01-opacity style), so render_slices reads them as None.
        assert_slices_fill_their_tiles(
            self,
            render_slices(self.tree),
            (
                ("normal", None),
                ("hover", None),
                ("pressed", "#CCCCFF"),
            ),
            3,
            6,
        )

    def test_menubaritem_colours(self):
        # The hints and the normal/hover slices use `style`, so the parsed
        # `fill` set is exactly the selection fill.
        self.assertEqual(attribute_values(self.tree, "fill"), {"#CCCCFF"})


if __name__ == "__main__":
    unittest.main()
