"""Tests for the desktop theme's margins-highlight.svg panel edit-mode band."""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import MARGINS_HIGHLIGHT_SVG
from support.platinum_palette import SELECTION
from support.svg_case import SvgCase
from svg_assertions import (
    assert_ids_present,
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_unique_ids,
    elements_by_id,
    local_name,
    rect_geometry,
)


CANVAS = 4
OPACITY = "0.3"
IDS = ("fill", "topleft", "topright", "bottomleft", "bottomright")
# Each corner's exact path. Each is a right triangle whose two legs run the
# full 4 units along its two canvas edges, so it covers half of the 4x4
# canvas: top-left and top-right share the top edge, bottom-left and
# bottom-right the bottom edge.
CORNERS = {
    "topleft": "M 0,0 H 4 L 0,4 Z",
    "topright": "M 0,0 H 4 V 4 Z",
    "bottomleft": "M 0,0 V 4 H 4 Z",
    "bottomright": "M 4,0 V 4 H 0 Z",
}


class TestMarginsHighlight(SvgCase, unittest.TestCase):
    SVG_PATH = MARGINS_HIGHLIGHT_SVG

    def test_margins_highlight_contract(self):
        # SideMargin resolves `fill` and the four corner ids by name; a
        # missing id, a duplicate, a moved colour into a <style> or an
        # external reference would each leave the band wrong or invisible.
        assert_ids_present(self, self.tree, IDS)
        assert_unique_ids(self, self.tree)
        assert_no_script_elements(self, self.tree)
        assert_no_style_elements(self, self.tree)
        assert_no_external_references(self, self.tree)
        by_id = elements_by_id(self.tree)
        for element_id in IDS:
            with self.subTest(element=element_id):
                self.assertEqual(by_id[element_id].get("fill"), SELECTION)
                self.assertEqual(by_id[element_id].get("fill-opacity"), OPACITY)

    def test_fill_covers_the_whole_canvas(self):
        # The flat band is the full 4x4 tile SideMargin stretches over the
        # margin; a short rect leaves a transparent stripe.
        by_id = elements_by_id(self.tree)
        self.assertEqual(local_name(by_id["fill"]), "rect")
        self.assertEqual(
            rect_geometry(self.tree),
            {"fill": ("0", "0", str(CANVAS), str(CANVAS))},
        )

    def test_corners_match_the_pinned_paths(self):
        # Each corner is its pinned half-canvas right triangle: SideMargin
        # stretches it over the margin corner, so a nudged vertex would tilt
        # or shrink the wedge while the fill and opacity assertions still
        # passed.
        by_id = elements_by_id(self.tree)
        for corner, path_d in CORNERS.items():
            with self.subTest(corner=corner):
                path = by_id[corner]
                self.assertEqual(local_name(path), "path")
                self.assertEqual(path.get("d"), path_d)


if __name__ == "__main__":
    unittest.main()
