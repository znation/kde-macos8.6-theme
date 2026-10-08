"""Tests for the desktop theme's radiobutton.svg radio-face artwork."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from desktoptheme_paths import RADIOBUTTON_SVG
from svg_assertions import (
    assert_no_script_elements,
    attribute_values,
    local_name,
)


class TestRadioButton(unittest.TestCase):
    def test_radiobutton_contract(self):
        tree = ET.parse(RADIOBUTTON_SVG)
        ids = attribute_values(tree, "id")
        for name in ("normal", "symbol", "hint-size"):
            self.assertIn(name, ids, name)
        fills = attribute_values(tree, "fill")
        self.assertEqual(fills, {"#FFFFFF", "#000000"})
        assert_no_script_elements(self, tree)

    def test_radiobutton_geometry(self):
        # The black ring is a filled circle under the white face, so the two
        # normal circles must stay concentric at (8, 8) with r=8 over r=7 (a
        # 1px outline), and the selected dot must stay at (40, 8) with r=3 (a
        # 6x6 symbol). Pin each circle's centre with its fill and radius: the
        # contract test only checks the fill set, so a swap of the two faces
        # (black face, white ring) or a circle nudged off-centre would
        # otherwise pass.
        tree = ET.parse(RADIOBUTTON_SVG)
        by_id = {el.get("id"): el for el in tree.iter() if el.get("id")}
        circles = [
            el for el in by_id["normal"]
            if local_name(el) == "circle"
        ]
        self.assertEqual(
            [
                (float(el.get("cx")), float(el.get("cy")),
                 float(el.get("r")), el.get("fill"))
                for el in circles
            ],
            [(8, 8, 8, "#000000"), (8, 8, 7, "#FFFFFF")],
        )
        symbol = by_id["symbol"]
        self.assertEqual(
            (float(symbol.get("cx")), float(symbol.get("cy")),
             float(symbol.get("r")), symbol.get("fill")),
            (40, 8, 3, "#000000"),
        )
        # KSvg reads the hint circle's size (not its colour) to size the
        # widget, so its centre and radius are part of the contract too.
        hint = by_id["hint-size"]
        self.assertEqual(
            (float(hint.get("cx")), float(hint.get("cy")), float(hint.get("r"))),
            (24, 8, 8),
        )


if __name__ == "__main__":
    unittest.main()
