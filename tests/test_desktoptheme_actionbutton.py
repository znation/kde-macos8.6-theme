"""Tests for the desktop theme's actionbutton.svg round action button."""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import ACTIONBUTTON_SVG
from support.platinum_palette import BLACK, FACE, GREY, PLATINUM_FILLS, WHITE
from support.svg_case import SvgCase
from svg_assertions import (
    arc_center,
    assert_ids_present,
    assert_no_script_elements,
    attribute_values,
    children_named,
    circle_geometry_and_fill,
    elements_by_id,
    local_name,
    path_arcs,
)


CENTER = (18.0, 18.0)
# The bevel half-discs are radius 16: the outline is r=17 and the face r=15, so
# the bevel is the 1px annulus between them.
BEVEL_RADIUS = 16
# Each state's face circles in document order: the #000000 outline under the
# #DDDDDD face.
FACE_CIRCLES = ((18, 18, 17, BLACK), (18, 18, 15, FACE))
# The two bevel fills in document order. The first half-disc is the top-left
# half, so a raised button paints #FFFFFF then #999999; a pressed button swaps
# them.
NORMAL_BEVEL_FILLS = (WHITE, GREY)
PRESSED_BEVEL_FILLS = (GREY, WHITE)
# The hover/focus ring is one donut path in the outermost pixel: a full r=18
# outer circle (sweep 1) and a full r=17 inner circle wound the other way
# (sweep 0), so the nonzero fill rule leaves the interior transparent and the
# ring sits just outside the r=17 outline. `path_arcs` reads four 180-degree
# arcs, outer radii first: (radius, large_arc, sweep).
RING_ARCS = ((18, 1, 1), (18, 1, 1), (17, 1, 0), (17, 1, 0))
# Every group's invisible bounding rect: KSvg scales an element by its bounds,
# so all four groups must span the same canvas or the ring lands on the
# outline instead of outside it.
BOUNDS_RECT = ["0", "0", "36", "36", "none"]


class TestActionButton(SvgCase, unittest.TestCase):
    SVG_PATH = ACTIONBUTTON_SVG

    def test_actionbutton_contract(self):
        assert_ids_present(
            self, self.tree, ("normal", "pressed", "hover", "focus")
        )
        self.assertEqual(
            attribute_values(self.tree, "fill"), PLATINUM_FILLS | {"none"}
        )
        assert_no_script_elements(self, self.tree)

    def test_actionbutton_geometry(self):
        # RoundButton/Dial draw `pressed` while down or checked else `normal`,
        # and RoundShadow draws `hover`/`focus`; a state missing its face, or a
        # bevel swapped between the two halves, changes the widget. Pin each
        # state's circles and both bevel half-discs by name: the contract test
        # only checks the fill set, so a swapped bevel order or a half-disc
        # nudged off-centre would otherwise pass.
        by_id = elements_by_id(self.tree)
        for state in ("normal", "pressed", "hover", "focus"):
            with self.subTest(state=state):
                group = by_id[state]
                self.assertEqual(local_name(group), "g")
                rects = children_named(group, "rect")
                self.assertEqual(len(rects), 1)
                self.assertEqual(
                    [rects[0].get(k) for k in ("x", "y", "width", "height", "fill")],
                    BOUNDS_RECT,
                )
        for state, bevel_fills in (
            ("normal", NORMAL_BEVEL_FILLS),
            ("pressed", PRESSED_BEVEL_FILLS),
        ):
            with self.subTest(state=state):
                group = by_id[state]
                self.assertEqual(
                    [circle_geometry_and_fill(el) for el in children_named(group, "circle")],
                    list(FACE_CIRCLES),
                )
                paths = children_named(group, "path")
                self.assertEqual(len(paths), 2)
                for path, fill in zip(paths, bevel_fills):
                    entries = list(path_arcs(path.get("d")))
                    self.assertEqual(len(entries), 1)
                    start, arc, end = entries[0]
                    self.assertEqual((arc[0], arc[1]), (BEVEL_RADIUS, BEVEL_RADIUS))
                    self.assertEqual(path.get("fill"), fill)
                    centre = arc_center(start, arc, end)
                    self.assertAlmostEqual(centre[0], CENTER[0], places=2)
                    self.assertAlmostEqual(centre[1], CENTER[1], places=2)
        for state in ("hover", "focus"):
            with self.subTest(state=state):
                group = by_id[state]
                # A ring, not a disc: the group holds no filled circle, only
                # the donut path, so its interior is transparent. Its outer
                # radius sits one pixel outside the r=17 outline, so it paints
                # a visible ring instead of landing on the outline itself.
                self.assertEqual(children_named(group, "circle"), [])
                paths = children_named(group, "path")
                self.assertEqual(len(paths), 1)
                ring = paths[0]
                self.assertEqual(ring.get("fill"), BLACK)
                entries = list(path_arcs(ring.get("d")))
                # The inner circle's opposite sweep is what turns the two
                # concentric arcs into a hole; a same-winding path renders a
                # solid disc even though both radii are present.
                self.assertEqual(
                    [(arc[0], arc[2], arc[3]) for _, arc, _ in entries],
                    list(RING_ARCS),
                )
                for start, arc, end in entries:
                    self.assertEqual(arc[0], arc[1])
                    centre = arc_center(start, arc, end)
                    self.assertAlmostEqual(centre[0], CENTER[0], places=2)
                    self.assertAlmostEqual(centre[1], CENTER[1], places=2)


if __name__ == "__main__":
    unittest.main()
