"""Tests for the desktop theme's listitem.svg selection-row artwork."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from desktoptheme_paths import LISTITEM_SVG
from svg_assertions import (
    SLICE_IDS,
    assert_no_script_elements,
    assert_tiles_placed_by_margins,
    attribute_values,
    rect_geometry,
    render_slices,
)


class TestListItem(unittest.TestCase):
    def test_listitem_slice_ids(self):
        tree = ET.parse(LISTITEM_SVG)
        ids = attribute_values(tree, "id")
        for prefix in ("normal", "pressed"):
            for name in SLICE_IDS:
                self.assertIn(f"{prefix}-{name}", ids, name)
            for side in ("top", "bottom", "left", "right"):
                self.assertIn(f"{prefix}-hint-{side}-margin", ids, side)
        self.assertIn("hint-tile-center", ids)

    def test_listitem_hint_geometry(self):
        # `test_listitem_slice_ids` pins only the hint ids, so a margin or
        # centre hint with the wrong position or size passes it while KSvg
        # lays the row out wrong. Pin every hint: normal and pressed share a
        # 3px border around a 6px centre tile on the 12x12 canvas.
        expected = {"hint-tile-center": ("3", "3", "6", "6")}
        for prefix in ("normal", "pressed"):
            expected.update({
                f"{prefix}-hint-top-margin": ("3", "0", "6", "3"),
                f"{prefix}-hint-bottom-margin": ("3", "9", "6", "3"),
                f"{prefix}-hint-left-margin": ("0", "3", "3", "6"),
                f"{prefix}-hint-right-margin": ("9", "3", "3", "6"),
            })
        self.assertEqual(rect_geometry(ET.parse(LISTITEM_SVG)), expected)

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
