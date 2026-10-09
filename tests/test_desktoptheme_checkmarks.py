"""Tests for the desktop theme's checkmarks.svg checkbox overlay artwork."""

from __future__ import annotations

import unittest

from desktoptheme_paths import CHECKMARKS_SVG
from svg_assertions import (
    assert_ids_present,
    assert_no_script_elements,
    attribute_values,
    children_named,
    circle_geometry_and_fill,
    elements_by_id,
    local_name,
)
from svg_case import SvgCase


class TestCheckmarks(SvgCase, unittest.TestCase):
    SVG_PATH = CHECKMARKS_SVG

    def test_checkmarks_contract(self):
        assert_ids_present(self, self.tree, ("checkbox", "radiobutton"))
        strokes = attribute_values(self.tree, "stroke")
        self.assertEqual(strokes, {"#000000"})
        fills = attribute_values(self.tree, "fill")
        self.assertEqual(fills, {"none", "#000000"})
        assert_no_script_elements(self, self.tree)

    def test_checkmarks_geometry(self):
        # The consumers anchor the SvgItem with `anchors.fill`, so KSvg scales
        # each element by its bounds. Without the invisible full-cell bounding
        # rect the checkbox path's natural ~12x9 bounds (and the 6x6 dot)
        # would stretch to the 16x16 cell; pin the group, the rect, and the
        # glyph so that scaling cannot creep back in.
        tree = self.tree
        by_id = elements_by_id(tree)

        checkbox = by_id["checkbox"]
        self.assertEqual(local_name(checkbox), "g")
        check_rects = children_named(checkbox, "rect")
        check_paths = children_named(checkbox, "path")
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
        # `d` and stroke-width alone do not fix the drawn glyph. The 2px
        # square caps extend the stroke past the path endpoints: the drawn
        # check spans x ~ 2.09..13.91, beyond the path's 3.5..12.5, and the
        # miter join keeps the (6.5, 11.5) corner sharp. A change to either
        # attribute would silently resize or round the check while every
        # existing assertion still passed, so pin them with the rest of the
        # stroke.
        self.assertEqual(check_paths[0].get("stroke-linecap"), "square")
        self.assertEqual(check_paths[0].get("stroke-linejoin"), "miter")

        radiobutton = by_id["radiobutton"]
        self.assertEqual(local_name(radiobutton), "g")
        radio_rects = children_named(radiobutton, "rect")
        radio_circles = children_named(radiobutton, "circle")
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
            circle_geometry_and_fill(radio_circles[0]),
            (8, 24, 3, "#000000"),
        )


if __name__ == "__main__":
    unittest.main()
