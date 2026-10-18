"""Direct tests for ``svg_assertions.elements``'s helpers.

The rect and circle readers turn an SVG's id-bearing rects and its circles
into the geometry every widget layout test compares against.
"""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from support.error_assertions import assert_error_names, error_message
from svg_assertions import (
    circle_geometry,
    circle_geometry_and_fill,
    rect_geometry,
)
from support.svg_fixtures import _svg_tree


class TestCircleGeometry(unittest.TestCase):
    def test_reads_centre_and_radius_as_floats(self):
        # The radiobutton and checkmarks tests compare this against float
        # tuples, so a string passthrough would fail there; pin the conversion
        # (a decimal cx) and the argument order directly.
        element = ET.fromstring(
            '<circle cx="7.5" cy="24" r="3" fill="#000000"/>'
        )
        self.assertEqual(circle_geometry(element), (7.5, 24.0, 3.0))

    def test_geometry_and_fill_appends_the_raw_fill_attribute(self):
        # The radiobutton and checkmarks tests compare this against tuples of
        # geometry plus fill, so pin that the fill is appended after the
        # three floats -- and that an absent fill is the raw None, not
        # dropped or stringified.
        element = ET.fromstring(
            '<circle cx="8" cy="8" r="3" fill="#000000"/>'
        )
        self.assertEqual(
            circle_geometry_and_fill(element), (8.0, 8.0, 3.0, "#000000")
        )
        bare = ET.fromstring('<circle cx="8" cy="8" r="3"/>')
        self.assertEqual(circle_geometry_and_fill(bare), (8.0, 8.0, 3.0, None))

    def test_missing_dimension_names_the_circle_and_the_attribute(self):
        # ElementTree hands an absent attribute back as None, and
        # circle_geometry converts each value with float(); the error must
        # name the circle and the attribute rather than surfacing as a bare
        # TypeError.
        element = ET.fromstring('<circle id="symbol" cy="8" r="3"/>')
        assert_error_names(
            self, ValueError, circle_geometry, element,
            needles=("symbol", "'cx'"),
        )

    def test_anonymous_missing_dimension_still_names_the_attribute(self):
        # The radiobutton face and checkmarks dot carry no id of their own, so
        # the diagnostic must still name the attribute when it cannot name the
        # element.
        element = ET.fromstring('<circle cy="8" r="3"/>')
        self.assertIn(
            "'cx'", error_message(self, ValueError, circle_geometry, element)
        )

    def test_non_numeric_dimension_names_the_circle_attribute_and_value(self):
        # A present but non-numeric value (r="3px") would reach float() and
        # surface as a bare ValueError naming no circle or attribute; name
        # the circle, the attribute and the value instead.
        element = ET.fromstring(
            '<circle id="symbol" cx="8" cy="8" r="3px"/>'
        )
        assert_error_names(
            self, ValueError, circle_geometry, element,
            needles=("symbol", "'r'", "'3px'"),
        )

    def test_anonymous_non_numeric_dimension_still_names_the_attribute(self):
        element = ET.fromstring('<circle cx="8" cy="8" r="3px"/>')
        assert_error_names(
            self, ValueError, circle_geometry, element,
            needles=("'r'", "'3px'"),
        )


class TestRectGeometry(unittest.TestCase):
    def test_reads_the_four_dimensions_of_each_id_bearing_rect(self):
        # The layout guards and the per-widget hint tests read geometry
        # through this map, so a missing or reordered value would mispin the
        # nine-slice layout. Pin the order and that a rect without an id is
        # left out.
        tree = _svg_tree(
            '<rect id="a" x="1" y="2" width="3" height="4"/>'
            '<rect x="9" y="9" width="9" height="9"/>'
        )
        self.assertEqual(rect_geometry(tree), {"a": ("1", "2", "3", "4")})

    def test_missing_dimension_names_the_rect_and_the_attribute(self):
        # ElementTree hands an absent attribute back as None, and the layout
        # guards convert each value with int(); the error must name the rect
        # and the attribute rather than surfacing as a bare TypeError.
        tree = _svg_tree(
            '<rect id="hint-top-margin" y="0" width="4" height="4"/>'
        )
        assert_error_names(
            self, ValueError, rect_geometry, tree,
            needles=("hint-top-margin", "'x'"),
        )

    def test_non_integer_dimension_names_the_rect_attribute_and_value(self):
        # A hint rect is never rendered by render_slices (it lives outside
        # the id-bearing <g> groups), so rect_geometry is the only reader of
        # its x/y/width/height. A present but non-integer value (x="4px")
        # would reach the layout guards' int() and surface as a bare
        # ValueError naming no rect; name the rect, attribute and value.
        tree = _svg_tree(
            '<rect id="hint-top-margin" x="4px" y="0" width="4" '
            'height="4"/>'
        )
        assert_error_names(
            self, ValueError, rect_geometry, tree,
            needles=("hint-top-margin", "'x'", "'4px'"),
        )
