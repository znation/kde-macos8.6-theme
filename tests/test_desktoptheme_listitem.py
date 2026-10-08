"""Tests for the desktop theme's listitem.svg selection-row artwork."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from desktoptheme_paths import LISTITEM_SVG
from svg_assertions import (
    SLICE_IDS,
    assert_no_script_elements,
    assert_slice_ids_present,
    assert_slice_pixels,
    assert_tiles_placed_by_margins,
    attribute_values,
    nine_slice_hint_geometry,
    pixel_map,
    rect_geometry,
    render_slices,
)


class TestListItem(unittest.TestCase):
    def test_listitem_slice_ids(self):
        assert_slice_ids_present(self, ET.parse(LISTITEM_SVG), ("normal", "pressed"))

    def test_listitem_hint_geometry(self):
        # `test_listitem_slice_ids` pins only the hint ids, so a margin or
        # centre hint with the wrong position or size passes it while KSvg
        # lays the row out wrong. Pin every hint: normal and pressed share a
        # 3px border around a 6px centre tile on the 12x12 canvas.
        self.assertEqual(
            rect_geometry(ET.parse(LISTITEM_SVG)),
            nine_slice_hint_geometry(("normal", "pressed"), 3, 6),
        )

    def test_listitem_selection_is_flat_selection_colour(self):
        # Every pressed slice must be the flat selection fill, so the
        # selection cannot silently gain a bevel or the grey button face.
        slices = render_slices(ET.parse(LISTITEM_SVG))
        for name in SLICE_IDS:
            for point, colour in slices[f"pressed-{name}"].items():
                self.assertEqual(colour, "#CCCCFF", f"pressed-{name} {point}")

    def test_listitem_normal_has_no_fill(self):
        # An unselected row paints nothing perceptible: the normal rects carry
        # no `fill` attribute and a 0.01 opacity, so only their margins apply.
        tree = ET.parse(LISTITEM_SVG)
        slices = render_slices(tree)
        for name in SLICE_IDS:
            for point, colour in slices[f"normal-{name}"].items():
                self.assertIsNone(colour, f"normal-{name} {point}")
        self.assertEqual(attribute_values(tree, "fill-opacity"), {"0.01"})

    def test_listitem_slices_fill_their_tiles(self):
        # The colour tests above iterate each slice's pixels, so a rect one
        # pixel short (or long) passes while KSvg leaves a transparent stripe
        # in the stretched tile. Pin every slice to its exact tile region:
        # pressed is flat #CCCCFF, normal carries no `fill` attribute (only a
        # 0.01-opacity style), so render_slices reads it as None.
        slices = render_slices(ET.parse(LISTITEM_SVG))
        border, tile = 3, 6
        sizes = {
            "center": (tile, tile),
            "top": (tile, border), "bottom": (tile, border),
            "left": (border, tile), "right": (border, tile),
            "topleft": (border, border), "topright": (border, border),
            "bottomleft": (border, border), "bottomright": (border, border),
        }
        for prefix, colour in (("pressed", "#CCCCFF"), ("normal", None)):
            for name, (width, height) in sizes.items():
                expected = pixel_map((colour,) * (width * height), width, height)
                assert_slice_pixels(self, slices, f"{prefix}-{name}", expected)

    def test_listitem_colours(self):
        # The hints and normal slices use `style`, so the parsed `fill` set is
        # exactly the selection fill.
        tree = ET.parse(LISTITEM_SVG)
        self.assertEqual(attribute_values(tree, "fill"), {"#CCCCFF"})

    def test_listitem_tiles_placed_by_margins(self):
        assert_tiles_placed_by_margins(
            self, ET.parse(LISTITEM_SVG), ["normal", "pressed"]
        )

    def test_no_script_elements(self):
        assert_no_script_elements(self, ET.parse(LISTITEM_SVG))


if __name__ == "__main__":
    unittest.main()
