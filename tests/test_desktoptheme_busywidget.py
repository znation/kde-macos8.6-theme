"""Tests for the desktop theme's busywidget.svg busy indicator artwork."""

from __future__ import annotations

import math
import unittest

from support.desktoptheme_paths import BUSYWIDGET_SVG
from support.platinum_palette import BLACK, FACE
from support.svg_case import SvgCase
from svg_assertions import (
    arc_center,
    assert_ids_present,
    assert_no_script_elements,
    attribute_values,
    children_named,
    elements_by_id,
    local_name,
    path_arcs,
)


CENTER = (18.0, 18.0)
# The two ring paths in document order: the #000000 outline under the #DDDDDD
# face, and each path's (outer, inner) radius. A swapped or concentric ring
# changes this.
RING_RADII = ((16, 11), (15, 12))
RING_FILLS = (BLACK, FACE)
# The 45-degree rays the gap's four endpoints sit on.
GAP_RAY = math.pi / 4


class TestBusyWidget(SvgCase, unittest.TestCase):
    SVG_PATH = BUSYWIDGET_SVG

    def test_busywidget_contract(self):
        assert_ids_present(self, self.tree, ("busywidget",))
        self.assertEqual(attribute_values(self.tree, "fill"), {"none", BLACK, FACE})
        assert_no_script_elements(self, self.tree)

    def test_busywidget_ring_geometry(self):
        # BusyIndicator rotates the element by its bounds, so the invisible
        # full-canvas rect must span the square and the two ring paths must be
        # 270-degree Cs sharing the same 90-degree gap: a full circle, a
        # smaller gap, or a gap on another axis would change how the spin
        # reads.
        by_id = elements_by_id(self.tree)
        group = by_id["busywidget"]
        self.assertEqual(local_name(group), "g")
        rects = children_named(group, "rect")
        paths = children_named(group, "path")
        self.assertEqual(len(rects), 1)
        self.assertEqual(len(paths), 2)
        self.assertEqual(
            [rects[0].get(k) for k in ("x", "y", "width", "height", "fill")],
            ["0", "0", "36", "36", "none"],
        )
        for path, radii, fill in zip(paths, RING_RADII, RING_FILLS):
            entries = list(path_arcs(path.get("d")))
            self.assertEqual([arc[0] for _, arc, _ in entries], list(radii))
            self.assertEqual(path.get("fill"), fill)
            angles = []
            for start, arc, end in entries:
                rx, ry, large_arc = arc[0], arc[1], arc[2]
                self.assertEqual(rx, ry)
                self.assertEqual(large_arc, 1)
                actual = arc_center(start, arc, end)
                self.assertAlmostEqual(actual[0], CENTER[0], places=2)
                self.assertAlmostEqual(actual[1], CENTER[1], places=2)
                angles.extend(
                    math.atan2(point[1] - CENTER[1], point[0] - CENTER[0])
                    for point in (start, end)
                )
            self.assertEqual(len(angles), 4)
            for angle in angles:
                self.assertAlmostEqual(abs(angle), GAP_RAY, places=4)


if __name__ == "__main__":
    unittest.main()
