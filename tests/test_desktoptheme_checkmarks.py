"""Tests for the desktop theme's checkmarks.svg checkbox overlay artwork."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from desktoptheme_paths import CHECKMARKS_SVG
from svg_assertions import (
    assert_no_script_elements,
    attribute_values,
    local_name,
)


class TestCheckmarks(unittest.TestCase):
    def test_checkmarks_contract(self):
        tree = ET.parse(CHECKMARKS_SVG)
        ids = attribute_values(tree, "id")
        for name in ("checkbox", "radiobutton"):
            self.assertIn(name, ids, name)
        strokes = attribute_values(tree, "stroke")
        self.assertEqual(strokes, {"#000000"})
        fills = attribute_values(tree, "fill")
        self.assertEqual(fills, {"none", "#000000"})
        assert_no_script_elements(self, tree)

    def test_checkmarks_geometry(self):
        # The consumers anchor the SvgItem with `anchors.fill`, so KSvg scales
        # each element by its bounds. Without the invisible full-cell bounding
        # rect the checkbox path's natural ~12x9 bounds (and the 6x6 dot)
        # would stretch to the 16x16 cell; pin the group, the rect, and the
        # glyph so that scaling cannot creep back in.
        tree = ET.parse(CHECKMARKS_SVG)
        by_id = {el.get("id"): el for el in tree.iter() if el.get("id")}

        checkbox = by_id["checkbox"]
        self.assertEqual(local_name(checkbox), "g")
        check_rects = [el for el in checkbox if local_name(el) == "rect"]
        check_paths = [el for el in checkbox if local_name(el) == "path"]
        self.assertEqual(len(check_rects), 1)
        self.assertEqual(len(check_paths), 1)
        self.assertEqual(
            [check_rects[0].get(k) for k in ("x", "y", "width", "height", "fill")],
            ["0", "0", "16", "16", "none"],
        )
        self.assertEqual(
            check_paths[0].get("d"),
            "M 3.5,8.5 L 6.5,11.5 L 12.5,5.5",
        )
        self.assertEqual(check_paths[0].get("stroke-width"), "2")
        self.assertEqual(check_paths[0].get("fill"), "none")

        radiobutton = by_id["radiobutton"]
        self.assertEqual(local_name(radiobutton), "g")
        radio_rects = [el for el in radiobutton if local_name(el) == "rect"]
        radio_circles = [el for el in radiobutton if local_name(el) == "circle"]
        self.assertEqual(len(radio_rects), 1)
        self.assertEqual(len(radio_circles), 1)
        self.assertEqual(
            [radio_rects[0].get(k) for k in ("x", "y", "width", "height", "fill")],
            ["0", "16", "16", "16", "none"],
        )
        # The dot must stay centred in the bottom 16x16 cell at (8, 24) so
        # the fallback indicator draws concentric with the radio face; the
        # contract test only checks the fill set, so a dot nudged off-centre
        # would otherwise pass. Pin its centre with its radius and fill.
        self.assertEqual(
            (float(radio_circles[0].get("cx")),
             float(radio_circles[0].get("cy")),
             float(radio_circles[0].get("r")),
             radio_circles[0].get("fill")),
            (8, 24, 3, "#000000"),
        )


if __name__ == "__main__":
    unittest.main()
