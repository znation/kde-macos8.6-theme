"""Tests for the desktop theme's widgets/background.svg Platinum menu body."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from desktoptheme_paths import BACKGROUND_SVG
from svg_assertions import (
    HINT_IDS,
    assert_face_bevel,
    assert_no_script_elements,
    assert_slice_ids_present,
    assert_slices_stay_within_their_tiles,
    assert_tiles_placed_by_margins,
    attribute_values,
    nine_slice_hint_geometry,
    rect_geometry,
    render_slices,
)


BLACK = "#000000"
WHITE = "#FFFFFF"


class TestBackground(unittest.TestCase):
    def setUp(self):
        self.tree = ET.parse(BACKGROUND_SVG)
        self.ids = attribute_values(self.tree, "id")

    def test_background_slice_ids(self):
        assert_slice_ids_present(self, self.tree, [""])

    def test_hint_ids_present(self):
        for name in HINT_IDS:
            self.assertIn(name, self.ids, name)

    def test_background_hint_geometry(self):
        # `test_background_slice_ids` pins only the hint ids, so a margin or
        # inset rect with the wrong position or size passes it while KSvg lays
        # the menu body out wrong. Pin every hint: a 3px border around a 10px
        # centre tile on the 16x16 canvas, plus the zero-size inset rects.
        expected = nine_slice_hint_geometry([""], 3, 10)
        expected.update({
            "hint-top-inset": ("3", "0", "10", "0"),
            "hint-bottom-inset": ("3", "16", "10", "0"),
            "hint-left-inset": ("0", "3", "0", "10"),
            "hint-right-inset": ("16", "3", "0", "10"),
        })
        self.assertEqual(rect_geometry(self.tree), expected)

    def test_background_tiles_placed_by_margins(self):
        # `test_background_pixels` composites each slice from its rects but
        # ignores the group's translate, so a group moved off its slice draws
        # from the wrong canvas region and still passes. Pin each tile's origin
        # against the margins that size the menu body's nine-slice.
        assert_tiles_placed_by_margins(self, self.tree, [""])

    def test_background_tiles_stay_within_their_margins(self):
        # `test_background_pixels` reads only points inside each tile, so an
        # oversized rect spilling into the neighbouring canvas region -- which
        # KSvg samples into that adjacent tile -- passes. Pin every slice to
        # the tile region its hints define.
        assert_slices_stay_within_their_tiles(self, self.tree, [""])

    def test_background_pixels(self):
        # The body is a flat #FFFFFF face: a 1px #000000 outline on the outer
        # edge of each slice and no bevel. `assert_face_bevel` pins the 10x10
        # centre, the four edge tiles, and the four corners where the outline
        # turns.
        slices = render_slices(self.tree)
        assert_face_bevel(self, slices, "", WHITE, "flat", size=10)

    def test_background_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the
        # artwork palette: the white face and the black outline.
        self.assertEqual(
            attribute_values(self.tree, "fill"), {BLACK, WHITE}
        )

    def test_no_script_elements(self):
        assert_no_script_elements(self, self.tree)


if __name__ == "__main__":
    unittest.main()
