"""Tests for the desktop theme's plasmoidheading.svg popup band artwork."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from desktoptheme_paths import LINE_SVG, PLASMOIDHEADING_SVG
from nine_slice_case import NineSliceCase
from svg_assertions import (
    assert_hint_geometry,
    assert_no_external_references,
    assert_no_style_elements,
    assert_unique_ids,
    attribute_values,
    nine_slice_tile_sizes,
    pixel_map,
    render_slices,
)

DARK = "#888888"
LIGHT = "#FFFFFF"
SIZES = nine_slice_tile_sizes(12, 12, 3, 3, 3, 3)
RULE_SLICES = {
    "header-bottom": (None,) * 6 + (DARK,) * 6 + (LIGHT,) * 6,
    "footer-top": (DARK,) * 6 + (LIGHT,) * 6 + (None,) * 6,
}


class TestPlasmoidHeading(NineSliceCase, unittest.TestCase):
    SVG_PATH = PLASMOIDHEADING_SVG
    PREFIXES = ("header", "footer")

    def test_hint_geometry(self):
        assert_hint_geometry(self, self.tree, ("header", "footer"), 3, 6)

    def test_rule_rows(self):
        slices = render_slices(self.tree)
        for name, pixels in RULE_SLICES.items():
            with self.subTest(slice=name):
                self.assertEqual(slices[name], pixel_map(pixels, 6, 3))

    def test_other_slices_paint_nothing(self):
        slices = render_slices(self.tree)
        for prefix in ("header", "footer"):
            for name, (w, h) in SIZES.items():
                slice_id = f"{prefix}-{name}"
                if slice_id in RULE_SLICES:
                    continue
                with self.subTest(slice=slice_id):
                    self.assertEqual(
                        slices[slice_id], pixel_map((None,) * (w * h), w, h)
                    )

    def test_colours(self):
        self.assertEqual(attribute_values(self.tree, "fill"), {DARK, LIGHT})
        self.assertEqual(attribute_values(self.tree, "fill-opacity"), {"0.01"})

    def test_rule_matches_line_svg(self):
        line = render_slices(ET.parse(LINE_SVG))["horizontal-line"]
        self.assertEqual(line, {(0, 0): DARK, (0, 1): LIGHT})
        rule = render_slices(self.tree)["header-bottom"]
        self.assertEqual((rule[(0, 1)], rule[(0, 2)]), (line[(0, 0)], line[(0, 1)]))

    def test_document_hygiene(self):
        assert_unique_ids(self, self.tree)
        assert_no_style_elements(self, self.tree)
        assert_no_external_references(self, self.tree)


if __name__ == "__main__":
    unittest.main()
