"""Tests for the desktop theme's arrows.svg popup / dropdown arrow artwork."""

from __future__ import annotations

import unittest

from desktoptheme_paths import ARROWS_SVG
from svg_assertions import (
    assert_ids_present,
    assert_no_script_elements,
    attribute_values,
    children_named,
    elements_by_id,
    local_name,
)
from svg_case import SvgCase

TRIANGLES = {
    "down-arrow": "M 4,5 L 12,5 L 8,11 Z",
    "up-arrow": "M 4,11 L 12,11 L 8,5 Z",
    "left-arrow": "M 11,4 L 11,12 L 5,8 Z",
    "right-arrow": "M 5,4 L 5,12 L 11,8 Z",
}


class TestArrows(SvgCase, unittest.TestCase):
    SVG_PATH = ARROWS_SVG

    def test_arrows_contract(self):
        assert_ids_present(self, self.tree, tuple(TRIANGLES))
        self.assertEqual(attribute_values(self.tree, "fill"), {"none", "#000000"})
        assert_no_script_elements(self, self.tree)

    def test_arrows_geometry(self):
        # Both consumers scale the element by its bounds into a square
        # iconSizes.small item, so each group's invisible rect must span the
        # full 16x16 canvas and the triangle must keep its exact path.
        by_id = elements_by_id(self.tree)
        for element_id, path_d in TRIANGLES.items():
            with self.subTest(element=element_id):
                group = by_id[element_id]
                self.assertEqual(local_name(group), "g")
                rects = children_named(group, "rect")
                paths = children_named(group, "path")
                self.assertEqual(len(rects), 1)
                self.assertEqual(len(paths), 1)
                self.assertEqual(
                    [rects[0].get(k) for k in ("x", "y", "width", "height", "fill")],
                    ["0", "0", "16", "16", "none"],
                )
                self.assertEqual(paths[0].get("d"), path_d)
                self.assertEqual(paths[0].get("fill"), "#000000")


if __name__ == "__main__":
    unittest.main()
