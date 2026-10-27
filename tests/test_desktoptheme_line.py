"""Tests for the desktop theme's line.svg etched separator artwork."""

from __future__ import annotations

import unittest

from support.aurorae_fixtures import PROFILER_REFERENCE, PROFILER_ROWS
from support.desktoptheme_paths import LINE_SVG
from support.platinum_palette import hex_colour
from support.reference_image import ReferenceScreenshotMixin
from support.svg_case import SvgCase
from svg_assertions import (
    assert_ids_present,
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_unique_ids,
    attribute_values,
    elements_by_id,
    groups_with_id,
    pixel_map,
    render_slices,
)

DARK = "#888888"
LIGHT = "#FFFFFF"

REFERENCE = PROFILER_REFERENCE
BODY = (0xEE, 0xEE, 0xEE)


class TestLine(SvgCase, unittest.TestCase):
    SVG_PATH = LINE_SVG

    def test_line_contract(self):
        ids = ("horizontal-line", "vertical-line")
        assert_ids_present(self, self.tree, ids)
        self.assertEqual({g.get("id") for g in groups_with_id(self.tree)}, set(ids))
        assert_unique_ids(self, self.tree)
        assert_no_script_elements(self, self.tree)
        assert_no_style_elements(self, self.tree)
        assert_no_external_references(self, self.tree)
        self.assertEqual(attribute_values(self.tree, "fill"), {DARK, LIGHT})

    def test_line_pixels(self):
        slices = render_slices(self.tree)
        self.assertEqual(slices["horizontal-line"], pixel_map((DARK, LIGHT), 1, 2))
        self.assertEqual(slices["vertical-line"], pixel_map((DARK, LIGHT), 2, 1))

    def test_line_placement(self):
        by_id = elements_by_id(self.tree)
        self.assertIsNone(by_id["vertical-line"].get("transform"))
        self.assertEqual(by_id["horizontal-line"].get("transform"), "translate(3,0)")


class TestLineReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = REFERENCE
    MAX_ROWS = PROFILER_ROWS

    def assert_rule(self, dark_at, light_at, before, after):
        """Assert the reference's rule: a dark/light pair with body either side."""
        self.assertEqual(self.pixel(*dark_at), (0x88, 0x88, 0x88))
        self.assertEqual(self.pixel(*light_at), (0xFF, 0xFF, 0xFF))
        self.assertEqual(hex_colour(self.pixel(*dark_at)), DARK)
        self.assertEqual(hex_colour(self.pixel(*light_at)), LIGHT)
        self.assertEqual(self.pixel(*before), BODY)
        self.assertEqual(self.pixel(*after), BODY)

    def test_horizontal_rule_matches_reference(self):
        self.assert_rule((260, 153), (260, 154), (260, 152), (260, 155))

    def test_vertical_rule_matches_reference(self):
        self.assert_rule((241, 128), (242, 128), (240, 128), (243, 128))

    def test_group_box_top_rule_matches_reference(self):
        self.assert_rule((400, 103), (400, 104), (400, 102), (400, 105))

    def test_group_box_right_rule_matches_reference(self):
        self.assert_rule((678, 110), (679, 110), (677, 110), (680, 110))

    def test_group_box_corners_match_reference(self):
        DARK_PIXEL = (0x88, 0x88, 0x88)
        LIGHT_PIXEL = (0xFF, 0xFF, 0xFF)
        cases = (
            # Top-left corner: dark rectangle pixels plus the light copy
            # inside the top row and left column.
            ((241, 103), DARK_PIXEL), ((242, 103), DARK_PIXEL),
            ((241, 104), DARK_PIXEL), ((242, 104), LIGHT_PIXEL),
            # Top-right corner, with the body outside the light right
            # column.
            ((678, 103), DARK_PIXEL), ((678, 104), DARK_PIXEL),
            ((679, 104), LIGHT_PIXEL), ((677, 104), LIGHT_PIXEL),
            ((679, 103), BODY),
            # Bottom-left corner, with the body outside the light bottom
            # row.
            ((241, 153), DARK_PIXEL), ((242, 153), DARK_PIXEL),
            ((242, 154), LIGHT_PIXEL), ((241, 154), BODY),
            # Bottom-right corner: the light copies fill both the bottom
            # row and the right column.
            ((678, 153), DARK_PIXEL), ((679, 153), LIGHT_PIXEL),
            ((678, 154), LIGHT_PIXEL), ((679, 154), LIGHT_PIXEL),
        )
        for coordinates, expected in cases:
            with self.subTest(coordinates=coordinates):
                self.assertEqual(self.pixel(*coordinates), expected)


if __name__ == "__main__":
    unittest.main()
