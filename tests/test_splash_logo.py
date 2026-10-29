"""Tests for the splash logo SVG's structure and geometry."""

from __future__ import annotations

import unittest

from support.splash_fixtures import LOGO
from support.placeholders import REGISTER, cross_check
from support.repo_root import ROOT
from support.svg_case import SvgCase

from svg_assertions import (  # noqa: E402
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_root_canvas,
    assert_unique_ids,
    attribute_values,
    elements_by_id,
    local_name,
)


class TestLogo(SvgCase, unittest.TestCase):
    SVG_PATH = LOGO

    def test_logo_is_tracked_as_a_placeholder(self):
        found, registered = cross_check(ROOT, REGISTER)
        relative = "theme/look-and-feel/org.macos8.desktop/contents/splash/images/macos-logo.svg"
        self.assertIn(relative, registered)
        self.assertIn(relative, found)

    def test_logo_svg(self):
        # The logo is the look-and-feel package's only shipped SVG, so it gets
        # the same structural guard the desktop-theme SVGs get centrally: a
        # pinned canvas (a width/height that drifts from the viewBox would
        # rescale the logo), no <style> element, and no reference to a file
        # the package does not ship. `attribute_values` reads fills only from
        # attributes, so a CSS-styled or externally-referenced logo could
        # otherwise pass this test while rendering wrong or blank.
        assert_root_canvas(self, self.tree, 26, 21)
        assert_no_script_elements(self, self.tree)
        assert_no_style_elements(self, self.tree)
        assert_no_external_references(self, self.tree)
        assert_unique_ids(self, self.tree)
        self.assertEqual(
            attribute_values(self.tree, "fill"), {"#4C65CB", "#7286D6"}
        )

    def test_logo_geometry(self):
        # `test_logo_svg` pins the root canvas and the set of fills, and
        # `test_logo_colours_match_reference` pins each fill to a reference
        # pixel, but neither fixes the drawn shape: the face rect could shrink
        # inside the 26x21 canvas or lose its 5px corner radius, or the
        # highlight path could move, and every existing test would still pass.
        # Pin each element's geometry and its own fill, so a drift in either
        # fails here instead of only looking wrong on screen.
        by_id = elements_by_id(self.tree)

        face = by_id["face"]
        self.assertEqual(local_name(face), "rect")
        self.assertEqual(
            [face.get(k) for k in ("x", "y", "width", "height", "rx", "fill")],
            ["0", "0", "26", "21", "5", "#4C65CB"],
        )

        highlight = by_id["highlight"]
        self.assertEqual(local_name(highlight), "path")
        self.assertEqual(highlight.get("fill"), "#7286D6")
        self.assertEqual(
            highlight.get("d"),
            "M 4 3 L 22 3 Q 24 3 24 5 L 24 9 Q 19 6 4 6 Z",
        )

        # The highlight is the lighter blue drawn over the face, and document
        # order is paint order: it must come after `face` or it is hidden.
        order = [
            element.get("id")
            for element in self.tree.iter()
            if element.get("id")
        ]
        self.assertLess(order.index("face"), order.index("highlight"))


if __name__ == "__main__":
    unittest.main()
