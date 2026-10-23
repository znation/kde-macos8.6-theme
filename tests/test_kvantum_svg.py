"""Validate the org.macos8.desktop Kvantum style's SVG structure.

The ids, palette and safety guards of
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: every frame element
ships its centre and eight slices, the interior and indicator elements ship
their state ids, every element the `.kvconfig` names has art, the fill set is
exactly the Platinum palette, and the four SVG safety guards pass. The painted
bevels are pinned separately in `test_kvantum_bevel_pixels`.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import svg_case
from support.kde_config import read as read_kde_config
from support.kvantum_fixtures import KVCONFIG, SVG
from support.platinum_palette import (
    SELECTION,
    TOOLTIP_FACE,
    TROUGH,
    assert_fill_palette,
)
from support.svg_case import parse_svg
from support.symlink_fixtures import symlinked_repo
from svg_assertions import (
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_unique_ids,
    attribute_values,
    children_named,
    elements_by_id,
    local_name,
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
# whole, so they carry a state id, not a nine-slice. `comboarrow` is the
# [ComboBox] indicator: the reference popup's double up/down arrow in a 12x12
# cell. `menuitem` and `menubaritem` are the menu-item interiors; their centre
# ids also serve as the frame art above, so both are frames and interiors at
# once.
INTERIOR_STATES = {
    "checkbox": ("normal", "focused", "checked-normal", "checked-focused"),
    "radio": ("normal", "focused", "checked-normal", "checked-focused"),
    "slidercursor": ("normal", "focused", "pressed", "disabled"),
    "progress-pattern": ("normal", "focused", "toggled", "disabled"),
    "splitter-grip": ("normal", "focused", "pressed"),
    "grip": ("normal", "focused", "pressed"),
    "comboarrow": ("normal", "focused", "pressed", "toggled", "disabled"),
    "menuitem": ("normal", "pressed", "toggled"),
    "menubaritem": ("normal", "pressed", "toggled"),
}
ARROW_DIRECTIONS = ("up", "down", "left", "right")
ARROW_STATES = ("normal", "focused", "pressed", "disabled")

# Each indicator arrow is one 9x9 triangle whose `d` is the same in every
# state; only the disabled state greys its fill. The four `d` values are the
# up/down/left/right triangles, so pinning them by direction catches a path
# rotated or mirrored onto the wrong direction, which the id-only check above
# passes. The fills are pinned by state because #000000 and #999999 are both
# in the palette, so a disabled arrow painted black still passes the palette
# test.
ARROW_PATH_D = {
    "up": "M4.5,0 L9,9 L0,9 Z",
    "down": "M0,0 L9,0 L4.5,9 Z",
    "left": "M9,0 L9,9 L0,4.5 Z",
    "right": "M0,0 L9,4.5 L0,9 Z",
}
ARROW_FILL = {
    "normal": "#000000",
    "focused": "#000000",
    "pressed": "#000000",
    "disabled": "#999999",
}


def _rect(x, y, width, height, fill):
    return ("rect", {"x": x, "y": y, "width": width, "height": height, "fill": fill})


def _circle(cx, cy, r, fill):
    return ("circle", {"cx": cx, "cy": cy, "r": r, "fill": fill})


def _drawing_elements(element):
    """Return *element*'s child drawing elements as ``(tag, attributes)``.

    In document order, so an added, removed, reordered or re-drawn child
    changes the tuple. Check box and radio button interiors hold only drawing
    elements (rects and circles) directly under their state group.
    """
    return tuple(
        (local_name(child), dict(child.attrib)) for child in element
    )


# The check box and radio button interiors are multi-element groups that the
# tests above read only by id: a wrong dot radius, a wrong inner-face size or a
# black/white fill swap (both are in the palette, so `assert_fill_palette`
# cannot see it) would pass. Pin each state's child drawing elements (tag and
# attributes) in document order, the way `TestIconGeometry` pins the icon art.
# The check box face is the reference's raised Platinum square: a 1px
# #000000 outline, a #FFFFFF top/left highlight, a #DDDDDD face and a 1px
# #888888 bottom/right shadow, with the top-right and bottom-left corners
# left the face colour (the reference's bevel shadow is #888888, darker than
# the #999999 the other raised faces use, so it is a named extra below rather
# than part of PLATINUM_FILLS).
CHECKBOX_SHADOW = "#888888"
# The button bevel's shadow is the reference popup buttons' #AAAAAA
# (test_kvantum_button_reference), lighter than the #999999 the other raised
# faces use, so it too is a named extra rather than part of PLATINUM_FILLS.
BUTTON_SHADOW = "#AAAAAA"
# The unselected tab face is the reference System Profiler tabs' #CCCCCC
# (test_kvantum_tab_reference), darker than the #DDDDDD the other raised faces
# use, so it too is a named extra rather than part of PLATINUM_FILLS.
TAB_FACE = "#CCCCCC"
_CHECKBOX_FACE = (
    _rect("0", "0", "14", "14", "#000000"),
    _rect("1", "1", "12", "12", "#DDDDDD"),
    _rect("1", "1", "11", "1", "#FFFFFF"),
    _rect("1", "1", "1", "11", "#FFFFFF"),
    _rect("12", "2", "1", "11", CHECKBOX_SHADOW),
    _rect("2", "12", "11", "1", CHECKBOX_SHADOW),
)
_CHECKBOX_CHECK = (
    _rect("3", "7", "2", "2", "#000000"),
    _rect("5", "9", "2", "2", "#000000"),
    _rect("7", "7", "2", "2", "#000000"),
    _rect("9", "5", "2", "2", "#000000"),
    _rect("11", "3", "2", "2", "#000000"),
)
_RADIO_FACE = (
    _circle("7", "7", "6.5", "#000000"),
    _circle("7", "7", "5.5", "#FFFFFF"),
)
_RADIO_DOT = (_circle("7", "7", "2.5", "#000000"),)
INTERIOR_SHAPES = {
    "checkbox-normal": _CHECKBOX_FACE,
    "checkbox-focused": _CHECKBOX_FACE,
    "checkbox-checked-normal": _CHECKBOX_FACE + _CHECKBOX_CHECK,
    "checkbox-checked-focused": _CHECKBOX_FACE + _CHECKBOX_CHECK,
    "radio-normal": _RADIO_FACE,
    "radio-focused": _RADIO_FACE,
    "radio-checked-normal": _RADIO_FACE + _RADIO_DOT,
    "radio-checked-focused": _RADIO_FACE + _RADIO_DOT,
}

# The remaining multi-element interiors are also read only by id: the slider
# cursor, the progress-bar pattern, the two grip indicators and the combo box
# arrow. A wrong rect size or offset, or a swapped fill (every colour here is
# in the palette, so `assert_fill_palette` cannot see it) would pass. The
# slider cursor is the one interior whose pressed state swaps the raised
# bevel's highlight and shadow (#FFFFFF top/left, #999999 bottom/right) for
# the sunken one, so pinning only `slidercursor-normal` would miss a pressed
# state repeating the resting art.
_SLIDER_RAISED = (
    _rect("0", "0", "16", "16", "#DDDDDD"),
    _rect("0", "1", "16", "1", "#FFFFFF"),
    _rect("0", "14", "16", "1", "#999999"),
    _rect("1", "0", "1", "16", "#FFFFFF"),
    _rect("14", "0", "1", "16", "#999999"),
    _rect("0", "0", "16", "1", "#000000"),
    _rect("0", "15", "16", "1", "#000000"),
    _rect("0", "0", "1", "16", "#000000"),
    _rect("15", "0", "1", "16", "#000000"),
)
_SLIDER_SUNKEN = (
    _rect("0", "0", "16", "16", "#DDDDDD"),
    _rect("0", "1", "16", "1", "#999999"),
    _rect("0", "14", "16", "1", "#FFFFFF"),
    _rect("1", "0", "1", "16", "#999999"),
    _rect("14", "0", "1", "16", "#FFFFFF"),
    _rect("0", "0", "16", "1", "#000000"),
    _rect("0", "15", "16", "1", "#000000"),
    _rect("0", "0", "1", "16", "#000000"),
    _rect("15", "0", "1", "16", "#000000"),
)
_SLIDER_DISABLED = (
    _rect("0", "0", "16", "16", "#999999"),
    _rect("0", "0", "16", "1", "#000000"),
    _rect("0", "15", "16", "1", "#000000"),
    _rect("0", "0", "1", "16", "#000000"),
    _rect("15", "0", "1", "16", "#000000"),
)
_PROGRESS_PATTERN = (
    _rect("0", "0", "4", "4", "#EEEEEE"),
    _rect("0", "1", "4", "2", "#000000"),
)
_PROGRESS_PATTERN_DISABLED = (
    _rect("0", "0", "4", "4", "#EEEEEE"),
    _rect("0", "1", "4", "2", "#999999"),
)
_SPLITTER_GRIP = (
    _rect("7", "3", "2", "2", "#000000"),
    _rect("7", "7", "2", "2", "#000000"),
    _rect("7", "11", "2", "2", "#000000"),
)
_GRIP = (
    _rect("4", "3", "1", "7", "#000000"),
    _rect("6", "3", "1", "7", "#000000"),
    _rect("8", "3", "1", "7", "#000000"),
)
# The combo box indicator's eight one-row arrow bands, cell-relative: the two
# triangles widen from one row of width 1 to width 7 and narrow back, with the
# 12x12 #DDDDDD face showing through the two gap rows between them.
_COMBOARROW_ROWS = (
    ("5", "1", "1"),
    ("4", "2", "3"),
    ("3", "3", "5"),
    ("2", "4", "7"),
    ("2", "7", "7"),
    ("3", "8", "5"),
    ("4", "9", "3"),
    ("5", "10", "1"),
)
_COMBOARROW_FACE = (_rect("0", "0", "12", "12", "#DDDDDD"),)
_COMBOARROW = _COMBOARROW_FACE + tuple(
    _rect(x, y, width, "1", "#000000")
    for x, y, width in _COMBOARROW_ROWS
)
_COMBOARROW_DISABLED = _COMBOARROW_FACE + tuple(
    _rect(x, y, width, "1", "#999999")
    for x, y, width in _COMBOARROW_ROWS
)
INTERIOR_GROUP_SHAPES = {
    "slidercursor-normal": _SLIDER_RAISED,
    "slidercursor-focused": _SLIDER_RAISED,
    "slidercursor-pressed": _SLIDER_SUNKEN,
    "slidercursor-disabled": _SLIDER_DISABLED,
    "progress-pattern-normal": _PROGRESS_PATTERN,
    "progress-pattern-focused": _PROGRESS_PATTERN,
    "progress-pattern-toggled": _PROGRESS_PATTERN,
    "progress-pattern-disabled": _PROGRESS_PATTERN_DISABLED,
    "splitter-grip-normal": _SPLITTER_GRIP,
    "splitter-grip-focused": _SPLITTER_GRIP,
    "splitter-grip-pressed": _SPLITTER_GRIP,
    "grip-normal": _GRIP,
    "grip-focused": _GRIP,
    "grip-pressed": _GRIP,
    "comboarrow-normal": _COMBOARROW,
    "comboarrow-focused": _COMBOARROW,
    "comboarrow-pressed": _COMBOARROW,
    "comboarrow-toggled": _COMBOARROW,
    "comboarrow-disabled": _COMBOARROW_DISABLED,
}


def _interior_state_ids(*elements):
    """Return every ``<element>-<state>`` id *elements* ship, from the table."""
    return {
        f"{element}-{state}"
        for element in elements
        for state in INTERIOR_STATES[element]
    }


class TestSvg(unittest.TestCase):
    def setUp(self):
        self.tree = parse_svg(SVG)
        self.ids = attribute_values(self.tree, "id")

    def _assert_frame_element_slices(self, element, state):
        """Assert one frame state's centre and each nine-slice id exist."""
        prefix = f"{element}-{state}"
        self.assertIn(prefix, self.ids)
        for slice_name in SLICE_NAMES:
            self.assertIn(f"{prefix}-{slice_name}", self.ids)

    def test_every_frame_element_ships_its_centre_and_eight_slices(self):
        for element, states in FRAME_STATES.items():
            for state in states:
                with self.subTest(element=element, state=state):
                    self._assert_frame_element_slices(element, state)

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

    def test_indicator_arrows_draw_the_pinned_triangle_and_fill(self):
        by_id = elements_by_id(self.tree)
        for direction in ARROW_DIRECTIONS:
            for state in ARROW_STATES:
                paths = children_named(
                    by_id[f"arrow-{direction}-{state}"], "path"
                )
                with self.subTest(direction=direction, state=state):
                    self.assertEqual(len(paths), 1)
                    self.assertEqual(paths[0].get("d"), ARROW_PATH_D[direction])
                    self.assertEqual(paths[0].get("fill"), ARROW_FILL[state])

    def test_checkbox_and_radio_interiors_draw_the_pinned_shapes(self):
        by_id = elements_by_id(self.tree)
        # Every check box and radio button state must have a pinned shape, so a
        # newly shipped state cannot escape the per-state pins below.
        self.assertEqual(
            set(INTERIOR_SHAPES), _interior_state_ids("checkbox", "radio")
        )
        for element, expected in INTERIOR_SHAPES.items():
            with self.subTest(element=element):
                self.assertEqual(_drawing_elements(by_id[element]), expected)

    def test_remaining_interiors_draw_the_pinned_shapes(self):
        by_id = elements_by_id(self.tree)
        elements = (
            "slidercursor",
            "progress-pattern",
            "splitter-grip",
            "grip",
            "comboarrow",
        )
        # Every remaining multi-element interior state must have a pinned
        # shape, so a newly shipped state cannot escape the pins below.
        self.assertEqual(
            set(INTERIOR_GROUP_SHAPES), _interior_state_ids(*elements)
        )
        for element, expected in INTERIOR_GROUP_SHAPES.items():
            with self.subTest(element=element):
                self.assertEqual(_drawing_elements(by_id[element]), expected)

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
            extra=frozenset(
                {
                    TROUGH,
                    TOOLTIP_FACE,
                    SELECTION,
                    CHECKBOX_SHADOW,
                    BUTTON_SHADOW,
                    TAB_FACE,
                }
            ),
        )

    def test_has_no_scripts_styles_external_refs_or_duplicate_ids(self):
        assert_no_script_elements(self, self.tree)
        assert_no_style_elements(self, self.tree)
        assert_no_external_references(self, self.tree)
        assert_unique_ids(self, self.tree)


class TestSvgContainment(unittest.TestCase):
    """The Kvantum SVG parse must refuse a symlink that escapes the repository."""

    def test_setup_rejects_a_symlinked_svg_that_escapes_the_repository(self):
        # The shipped SVG is contributor-supplied, and a checked-in symlink at
        # its path can point at a private file; `ET.parse` reads the target
        # and the widget assertions echo attribute values into a failing
        # test's diagnostic, so `setUp` must refuse the escape before it
        # parses. This drives the real `TestSvg.setUp` (not `parse_svg`
        # directly), so it fails if the Kvantum test stops routing through the
        # guard. The target is a valid SVG so a bare `ET.parse` would succeed
        # and the escape would go unnoticed.
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp,
                "org.macos8.desktop.svg",
                "<svg><g id='secret'><rect width='1' height='1'/></g></svg>\n",
            )
            module = sys.modules[__name__]
            with mock.patch.object(svg_case, "ROOT", root), mock.patch.object(
                module, "SVG", str(link)
            ):
                with self.assertRaises(ValueError) as caught:
                    TestSvg().setUp()
        self.assertIn(str(link), str(caught.exception))


if __name__ == "__main__":
    unittest.main()
