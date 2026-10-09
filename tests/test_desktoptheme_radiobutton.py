"""Tests for the desktop theme's radiobutton.svg radio-face artwork."""

from __future__ import annotations

import unittest

from desktoptheme_paths import RADIOBUTTON_SVG
from svg_assertions import (
    assert_ids_present,
    assert_no_script_elements,
    attribute_values,
    children_named,
    circle_geometry,
    elements_by_id,
)
from svg_case import SvgCase


class TestRadioButton(SvgCase, unittest.TestCase):
    SVG_PATH = RADIOBUTTON_SVG

    def test_radiobutton_contract(self):
        assert_ids_present(self, self.tree, ("normal", "symbol", "hint-size"))
        fills = attribute_values(self.tree, "fill")
        self.assertEqual(fills, {"#FFFFFF", "#000000"})
        assert_no_script_elements(self, self.tree)

    def test_radiobutton_geometry(self):
        # The black ring is a filled circle under the white face, so the two
        # normal circles must stay concentric at (8, 8) with r=8 over r=7 (a
        # 1px outline), and the selected dot must stay at (40, 8) with r=3 (a
        # 6x6 symbol). Pin each circle's centre with its fill and radius: the
        # contract test only checks the fill set, so a swap of the two faces
        # (black face, white ring) or a circle nudged off-centre would
        # otherwise pass.
        tree = self.tree
        by_id = elements_by_id(tree)
        circles = children_named(by_id["normal"], "circle")
        self.assertEqual(
            [circle_geometry(el) + (el.get("fill"),) for el in circles],
            [(8, 8, 8, "#000000"), (8, 8, 7, "#FFFFFF")],
        )
        symbol = by_id["symbol"]
        self.assertEqual(
            circle_geometry(symbol) + (symbol.get("fill"),),
            (40, 8, 3, "#000000"),
        )
        # KSvg reads the hint circle's size (not its colour) to size the
        # widget, so its centre and radius are part of the contract too.
        hint = by_id["hint-size"]
        self.assertEqual(circle_geometry(hint), (24, 8, 8))


if __name__ == "__main__":
    unittest.main()
