"""Validate the org.macos8.desktop Kvantum style's SVG structure.

The ids, palette and safety guards of
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: every frame element
ships its centre and eight slices, the interior and indicator elements ship
their state ids, every element the `.kvconfig` names has art, the fill set is
exactly the Platinum palette, and the four SVG safety guards pass. The painted
bevels are pinned separately in `test_kvantum_bevel_pixels`.
"""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from support.kde_config import read as read_kde_config
from support.kvantum_fixtures import KVCONFIG, SVG
from support.platinum_palette import (
    SELECTION,
    TOOLTIP_FACE,
    TROUGH,
    assert_fill_palette,
)
from svg_assertions import (
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_unique_ids,
    attribute_values,
)

# The nine-sliced frame elements and the states the SVG ships. Kvantum names
# the centre `<element>-<state>` and each slice `<element>-<state>-<slice>`.
# `menuitem` is a frame here because `[MenuBar]` names it as its frame element
# and an interior because `[MenuItem]` names it as its interior; its centre id
# serves both. `menubaritem` is the same: `[MenuBarItem]` names it as both its
# frame and its interior, and Kvantum draws that frame only in the pressed and
# toggled states, so those are the states it ships slices for.
FRAME_STATES = {
    "button": ("normal", "pressed", "focused", "toggled"),
    "lineedit": ("normal", "focused"),
    "common": ("normal", "focused"),
    "scrollbarslider": ("normal", "focused", "pressed"),
    "slider": ("normal", "toggled"),
    "progress": ("normal",),
    "spin": ("normal", "focused", "pressed"),
    "splitter": ("normal", "focused", "pressed"),
    "tab": ("normal", "focused", "toggled"),
    "tabframe": ("normal",),
    "menu": ("normal",),
    "group": ("normal",),
    "tooltip": ("normal",),
    "itemview": ("normal", "focused", "pressed", "toggled"),
    "toolbar": ("normal",),
    "menuitem": ("normal", "pressed", "toggled"),
    "menubaritem": ("pressed", "toggled"),
}
SLICE_NAMES = (
    "top", "bottom", "left", "right",
    "topleft", "topright", "bottomleft", "bottomright",
)

# Check boxes and radio buttons are single interior elements Kvantum renders
# whole, so they carry a state id, not a nine-slice. `menuitem` and
# `menubaritem` are the menu-item interiors; their centre ids also serve as the
# frame art above, so both are frames and interiors at once.
INTERIOR_STATES = {
    "checkbox": ("normal", "focused", "checked-normal", "checked-focused"),
    "radio": ("normal", "focused", "checked-normal", "checked-focused"),
    "slidercursor": ("normal", "focused", "pressed", "disabled"),
    "progress-pattern": ("normal", "focused", "toggled", "disabled"),
    "splitter-grip": ("normal", "focused", "pressed"),
    "grip": ("normal", "focused", "pressed"),
    "menuitem": ("normal", "pressed", "toggled"),
    "menubaritem": ("normal", "pressed", "toggled"),
}
ARROW_DIRECTIONS = ("up", "down", "left", "right")
ARROW_STATES = ("normal", "focused", "pressed", "disabled")


class TestSvg(unittest.TestCase):
    def setUp(self):
        self.tree = ET.parse(SVG)
        self.ids = attribute_values(self.tree, "id")

    def test_every_frame_element_ships_its_centre_and_eight_slices(self):
        for element, states in FRAME_STATES.items():
            for state in states:
                prefix = f"{element}-{state}"
                with self.subTest(element=element, state=state):
                    self.assertIn(prefix, self.ids)
                    for slice_name in SLICE_NAMES:
                        self.assertIn(f"{prefix}-{slice_name}", self.ids)

    def test_the_focus_ring_ships_its_centre_and_eight_slices(self):
        self.assertIn("focus", self.ids)
        for slice_name in SLICE_NAMES:
            self.assertIn(f"focus-{slice_name}", self.ids)

    def test_interior_elements_ship_every_state(self):
        for element, states in INTERIOR_STATES.items():
            for state in states:
                with self.subTest(element=element, state=state):
                    self.assertIn(f"{element}-{state}", self.ids)

    def test_indicator_arrows_ship_every_direction_and_state(self):
        for direction in ARROW_DIRECTIONS:
            for state in ARROW_STATES:
                with self.subTest(direction=direction, state=state):
                    self.assertIn(f"arrow-{direction}-{state}", self.ids)

    def test_every_element_the_config_names_has_art(self):
        parser = read_kde_config(KVCONFIG)
        names = set()
        for section in parser.sections():
            for key, value in parser.items(section):
                if key.endswith(".element"):
                    names.add(value)
        for name in names:
            with self.subTest(element=name):
                self.assertTrue(
                    any(i == name or i.startswith(name + "-") for i in self.ids),
                    f"no SVG id for config element {name!r}",
                )

    def test_uses_exactly_the_platinum_palette(self):
        assert_fill_palette(
            self,
            self.tree,
            extra=frozenset({TROUGH, TOOLTIP_FACE, SELECTION}),
        )

    def test_has_no_scripts_styles_external_refs_or_duplicate_ids(self):
        assert_no_script_elements(self, self.tree)
        assert_no_style_elements(self, self.tree)
        assert_no_external_references(self, self.tree)
        assert_unique_ids(self, self.tree)


if __name__ == "__main__":
    unittest.main()
