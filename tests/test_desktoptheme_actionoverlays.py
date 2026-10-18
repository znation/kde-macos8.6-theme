"""Tests for the desktop theme's action-overlays.svg desktop icon buttons."""

from __future__ import annotations

import math
import unittest

from support.desktoptheme_paths import ACTION_OVERLAYS_SVG
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


CENTER = (8.0, 8.0)
# The bevel half-discs are radius 6: the outline is r=7 and the face r=5, so
# the bevel is the 1px annulus between them.
BEVEL_RADIUS = 6
# The two half-disc endpoints on the top-right to bottom-left diagonal, in
# document order. The first half runs bottom-left -> top-right and the second
# top-right -> bottom-left, both swept (sweep 1) so the first covers the
# top-left half the raised bevel paints #FFFFFF.
_DIAGONAL = BEVEL_RADIUS / math.sqrt(2)
BEVEL_ENDPOINTS = (
    ((CENTER[0] - _DIAGONAL, CENTER[1] + _DIAGONAL),
     (CENTER[0] + _DIAGONAL, CENTER[1] - _DIAGONAL)),
    ((CENTER[0] + _DIAGONAL, CENTER[1] - _DIAGONAL),
     (CENTER[0] - _DIAGONAL, CENTER[1] + _DIAGONAL)),
)
# Every group's invisible bounding rect: KSvg scales an element by its bounds,
# so all nine groups must span the same canvas.
BOUNDS_RECT = ["0", "0", "16", "16", "none"]
KINDS = ("add", "open", "remove")
STATES = ("normal", "hover", "pressed")
# The two bevel fills in document order. The first half-disc is the top-left
# half, so a raised button paints #FFFFFF then #999999; a pressed button swaps
# them.
RAISED_BEVEL_FILLS = (WHITE, GREY)
PRESSED_BEVEL_FILLS = (GREY, WHITE)
# Each state's face circles in document order: the #000000 outline under the
# face. `hover` lights the face white; `normal` and `pressed` keep #DDDDDD.
FACE_CIRCLES = {
    "normal": ((8, 8, 7, BLACK), (8, 8, 5, FACE)),
    "hover": ((8, 8, 7, BLACK), (8, 8, 5, WHITE)),
    "pressed": ((8, 8, 7, BLACK), (8, 8, 5, FACE)),
}
BEVEL_FILLS = {
    "normal": RAISED_BEVEL_FILLS,
    "hover": RAISED_BEVEL_FILLS,
    "pressed": PRESSED_BEVEL_FILLS,
}
# Each kind's glyph over the face, pinned by its path and its paint. `add` and
# `remove` are stroked 1.5px black lines with no fill; `open` is a filled
# black triangle with no stroke.
GLYPHS = {
    "add": {
        "d": "M 5.5,8 L 10.5,8 M 8,5.5 L 8,10.5",
        "fill": "none",
        "stroke": BLACK,
        "stroke-width": "1.5",
    },
    "open": {
        "d": "M 6,5.5 L 6,10.5 L 10.5,8 Z",
        "fill": BLACK,
        "stroke": None,
        "stroke-width": None,
    },
    "remove": {
        "d": "M 5.5,8 L 10.5,8",
        "fill": "none",
        "stroke": BLACK,
        "stroke-width": "1.5",
    },
}


class TestActionOverlays(SvgCase, unittest.TestCase):
    SVG_PATH = ACTION_OVERLAYS_SVG

    def test_actionoverlays_contract(self):
        assert_ids_present(
            self,
            self.tree,
            tuple(f"{kind}-{state}" for kind in KINDS for state in STATES),
        )
        self.assertEqual(
            attribute_values(self.tree, "fill"), PLATINUM_FILLS | {"none"}
        )
        self.assertEqual(attribute_values(self.tree, "stroke"), {BLACK})
        assert_no_script_elements(self, self.tree)

    def test_actionoverlays_geometry(self):
        # FolderItemActionButton draws `normal` while the pointer is away,
        # `hover` while over it and `pressed` while down, for the `add`,
        # `open` and `remove` elements FolderItemDelegate names; a missing
        # state, a swapped bevel or a glyph on the wrong kind changes the
        # widget. Pin each group's circles, both bevel half-discs and its
        # glyph: the contract test only checks the fill/stroke sets, so a
        # swapped bevel order or a nudged glyph would otherwise pass.
        by_id = elements_by_id(self.tree)
        for kind in KINDS:
            for state in STATES:
                with self.subTest(element=f"{kind}-{state}"):
                    group = by_id[f"{kind}-{state}"]
                    self.assertEqual(local_name(group), "g")
                    rects = children_named(group, "rect")
                    self.assertEqual(len(rects), 1)
                    self.assertEqual(
                        [rects[0].get(k) for k in ("x", "y", "width", "height", "fill")],
                        BOUNDS_RECT,
                    )
                    self.assertEqual(
                        [
                            circle_geometry_and_fill(el)
                            for el in children_named(group, "circle")
                        ],
                        list(FACE_CIRCLES[state]),
                    )
                    paths = children_named(group, "path")
                    self.assertEqual(len(paths), 3)
                    for index, (path, fill) in enumerate(
                        zip(paths[:2], BEVEL_FILLS[state])
                    ):
                        entries = list(path_arcs(path.get("d")))
                        self.assertEqual(len(entries), 1)
                        start, arc, end = entries[0]
                        self.assertEqual(
                            (arc[0], arc[1]), (BEVEL_RADIUS, BEVEL_RADIUS)
                        )
                        # A half-disc rotated onto the other diagonal would
                        # still centre on (8,8) at r=6, so pin both endpoints
                        # and the sweep that picks the top-left side.
                        self.assertEqual((arc[2], arc[3]), (0, 1))
                        expected_start, expected_end = BEVEL_ENDPOINTS[index]
                        for got, want in ((start, expected_start), (end, expected_end)):
                            self.assertAlmostEqual(got[0], want[0], delta=1e-3)
                            self.assertAlmostEqual(got[1], want[1], delta=1e-3)
                        self.assertEqual(path.get("fill"), fill)
                        centre = arc_center(start, arc, end)
                        self.assertAlmostEqual(centre[0], CENTER[0], places=2)
                        self.assertAlmostEqual(centre[1], CENTER[1], places=2)
                    glyph = paths[2]
                    for attribute, expected in GLYPHS[kind].items():
                        self.assertEqual(glyph.get(attribute), expected)


if __name__ == "__main__":
    unittest.main()
