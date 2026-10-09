"""Shared structural checks for the flat nine-slice artwork tests.

`test_desktoptheme_panel` and `test_desktoptheme_background` each parse one
nine-slice SVG and assert the same structural invariants: every hint id is
present, each tile sits at the origin its margins imply, no slice spills into a
neighbouring tile, and the file carries no `<script>`. Each subclass sets
`SVG_PATH` and inherits those checks once.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from svg_assertions import (
    HINT_IDS,
    assert_no_script_elements,
    assert_slices_stay_within_their_tiles,
    assert_tiles_placed_by_margins,
    attribute_values,
)


class NineSliceCase:
    """Mixin: the structural checks shared by the flat nine-slice widgets.

    Subclasses set `SVG_PATH` to the widget SVG. It is a plain mixin, not a
    `TestCase`, so importing it does not collect an unconfigured base. The
    widget's own pixel test pins the painted result; the checks here guard the
    structure that pixel test does not read.
    """

    SVG_PATH = None

    def setUp(self):
        self.tree = ET.parse(self.SVG_PATH)
        self.ids = attribute_values(self.tree, "id")

    def test_hint_ids_present(self):
        for name in HINT_IDS:
            self.assertIn(name, self.ids, name)

    def test_tiles_placed_by_margins(self):
        # The widget's pixel test composites each slice from its rects but
        # ignores the group's translate, so a group moved off its slice draws
        # from the wrong canvas region and still passes. Pin each tile's origin
        # against the margins that size the nine-slice.
        assert_tiles_placed_by_margins(self, self.tree, [""])

    def test_tiles_stay_within_their_margins(self):
        # The widget's pixel test reads only points inside each tile, so an
        # oversized rect spilling into the neighbouring canvas region -- which
        # KSvg samples into that adjacent tile -- passes. Pin every slice to
        # the tile region its hints define.
        assert_slices_stay_within_their_tiles(self, self.tree, [""])

    def test_no_script_elements(self):
        assert_no_script_elements(self, self.tree)
