"""Pin the painted bevel of each org.macos8.desktop Kvantum SVG state.

`TestSvg` checks that the state ids and the palette exist, which a pressed
state repeating the raised art passes; these tests render each state's nine
slices and compare them pixel for pixel, so a raised `button-pressed`, a
`menubaritem-pressed` repeating the flat `normal` art, or a wrong frame element
fails here.
"""

from __future__ import annotations

import unittest

from support.kvantum_fixtures import SVG
from support.platinum_palette import (
    FACE,
    SELECTION,
    TOOLTIP_FACE,
    WHITE,
)
from support.svg_case import parse_svg
from svg_assertions import (
    assert_slice_pixels,
    assert_sunken_outside_field,
    bevel_corner_maps,
    bevel_edge_maps,
    edge_map,
    pixel_map,
    render_slices,
)

# Each button state's bevel direction. Kvantum draws the `button-pressed` and
# `button-toggled` ids for a sunken and an on (toggled) button, so those
# states must paint the sunken bevel -- a #999999 shadow inside the top/left
# outline and a #FFFFFF highlight inside the bottom/right one -- rather than
# repeat the raised art of the resting and focused button.
BUTTON_BEVELS = {
    "normal": "raised",
    "focused": "raised",
    "pressed": "sunken",
    "toggled": "sunken",
}
BUTTON_FACE = FACE
BUTTON_SIZE = 30

# The four 2px corner slices of a button, per bevel, row-major in
# slice-local coordinates. The raised button's bevel shadow is the reference
# popup buttons' #AAAAAA (test_kvantum_button_reference); every other raised
# frame element (tab, menu, group, toolbar, ...) keeps the #999999 the
# desktop theme paints.
BUTTON_SHADOW = "#AAAAAA"
SURFACE_SHADOW = "#999999"
# The raised top/left highlight the other raised faces paint. The tab's
# normal/focused states use the reference's #DDDDDD (test_kvantum_tab_reference)
# and its selected state the #FFFFFF below.
SURFACE_HIGHLIGHT = "#FFFFFF"
# The tab states' face/highlight palette from the reference System Profiler
# tabs: an unselected tab is a #CCCCCC face with a #DDDDDD highlight, the
# selected tab an #EEEEEE face with a #FFFFFF highlight.
TAB_FACE = "#CCCCCC"
TAB_HIGHLIGHT = "#DDDDDD"
TAB_SELECTED_FACE = "#EEEEEE"


def _button_corners(bevel, shadow, highlight=SURFACE_HIGHLIGHT):
    """Return each 2x2 corner pixel map a *bevel* paints, keyed by name.

    The raised corners carry the *shadow* where the bottom/right band turns,
    and the sunken ones where the top/left band turns; the opposite corners
    carry the *highlight*.
    """
    return bevel_corner_maps(bevel, "#000000", highlight, shadow)

# Part 3's frame elements, the bevel each state paints and the colour of its
# centre. `raised` and `sunken` paint the eight bevel slices and four corners
# `_button_edge_maps`/`_button_corners` describe; `flat` paints every slice as
# a solid fill with no outline or bevel, the project's flat-selection art for
# a highlighted item. The pixel test renders each state's nine slices, so a
# `menubaritem-pressed` that gains a bevel, or a `menu` drawn with a sunken
# bevel, fails here rather than passing on ids alone. The selected tab keeps
# the raised bevel the desktop theme's active tab paints.
SURFACE_STATES = {
    "tab": {
        "normal": ("raised", TAB_FACE),
        "focused": ("raised", TAB_FACE),
        "toggled": ("raised", TAB_SELECTED_FACE),
    },
    "tabframe": {"normal": ("raised", FACE)},
    "menu": {"normal": ("raised", FACE)},
    "group": {"normal": ("raised", FACE)},
    "tooltip": {"normal": ("raised", TOOLTIP_FACE)},
    "itemview": {
        "pressed": ("flat", SELECTION),
        "toggled": ("flat", SELECTION),
    },
    "toolbar": {"normal": ("raised", FACE)},
    "menuitem": {
        "normal": ("raised", FACE),
        "pressed": ("flat", SELECTION),
        "toggled": ("flat", SELECTION),
    },
    "menubaritem": {
        "pressed": ("flat", SELECTION),
        "toggled": ("flat", SELECTION),
    },
}

# The nine slices of a Kvantum frame element and their size in the 30px test
# tile: the centre id carries no suffix, the eight slices do. A `flat` state
# paints every one of these as a solid rectangle.
SURFACE_SLICE_SIZES = {
    "": (BUTTON_SIZE, BUTTON_SIZE),
    "top": (BUTTON_SIZE, 2),
    "bottom": (BUTTON_SIZE, 2),
    "left": (2, BUTTON_SIZE),
    "right": (2, BUTTON_SIZE),
    "topleft": (2, 2),
    "topright": (2, 2),
    "bottomleft": (2, 2),
    "bottomright": (2, 2),
}


def _button_edge_maps(bevel, shadow, highlight=SURFACE_HIGHLIGHT):
    """Return the four 2px edge slices a *bevel* paints, keyed by slice name.

    Each edge is the outer 1px #000000 outline with the bevel's 1px band
    inside it: a raised bevel highlights the top/left and shadows the
    bottom/right, and a sunken one swaps those two colours. *shadow* is the
    bevel shadow the element paints (the button's #AAAAAA, the other raised
    faces' #999999); *highlight* is the raised band's colour.
    """
    return bevel_edge_maps(
        BUTTON_SIZE, bevel, "#000000", highlight, shadow
    )


class TestButtonBevelPixels(unittest.TestCase):
    """Pin the painted bevel of each button state, not just its ids.

    `TestSvg` checks that the state ids and the palette exist, which a pressed
    state repeating the raised art passes; these tests render each state's
    nine slices and compare them pixel for pixel, so a raised `button-pressed`
    or `button-toggled` fails here.
    """

    def setUp(self):
        self.slices = render_slices(parse_svg(SVG))

    def test_every_button_state_paints_its_bevel(self):
        centre = pixel_map(
            (BUTTON_FACE,) * (BUTTON_SIZE * BUTTON_SIZE),
            BUTTON_SIZE,
            BUTTON_SIZE,
        )
        for state, bevel in BUTTON_BEVELS.items():
            prefix = f"button-{state}"
            with self.subTest(state=state):
                assert_slice_pixels(self, self.slices, prefix, centre)
                for name, expected in _button_edge_maps(bevel, BUTTON_SHADOW).items():
                    assert_slice_pixels(
                        self, self.slices, f"{prefix}-{name}", expected
                    )
                for name, colours in _button_corners(bevel, BUTTON_SHADOW).items():
                    assert_slice_pixels(
                        self, self.slices, f"{prefix}-{name}", colours
                    )


# The Kvantum line edit is the reference's sunken text field: a 2px border
# whose outer pixel is the #999999/#FFFFFF bevel and whose inner pixel is the
# #000000 outline, over the #FFFFFF face. Mac OS 8.6 text fields have no focus
# ring, so `normal` and `focused` paint the same field.
LINEEDIT_SIZE = 30
LINEEDIT_FACE = WHITE

# The field's four colours: the top/left outer shadow, the #000000 outline
# inside it, the #FFFFFF face and the bottom/right outer highlight.
LINEEDIT_COLOURS = {
    "shadow": "#999999",
    "outline": "#000000",
    "face": LINEEDIT_FACE,
    "highlight": WHITE,
}


class TestLineEditBevelPixels(unittest.TestCase):
    """Pin the line edit's sunken-outside field, not just its ids.

    `TestSvg` checks the state ids and the palette, which the old
    outline-outside art also passes; this renders each state's nine slices
    and compares them pixel for pixel, so a field that keeps the outline
    outside the bevel fails here.
    """

    def setUp(self):
        self.slices = render_slices(parse_svg(SVG))

    def test_every_lineedit_state_paints_the_sunken_outside_field(self):
        for state in ("normal", "focused"):
            with self.subTest(state=state):
                assert_sunken_outside_field(
                    self,
                    self.slices,
                    f"lineedit-{state}",
                    LINEEDIT_SIZE,
                    LINEEDIT_COLOURS,
                )


class TestItemViewBevelPixels(unittest.TestCase):
    """Pin the item view's sunken-outside field, not just its ids.

    `TestSvg` checks the state ids and the palette, which the old
    outline-outside art also passes; this renders each state's nine slices
    and compares them pixel for pixel, so an item view that keeps the outline
    outside the bevel fails here. The field shares the line edit's geometry,
    including the unpainted outer bottom-left pixel.
    """

    def setUp(self):
        self.slices = render_slices(parse_svg(SVG))

    def test_every_itemview_state_paints_the_sunken_outside_field(self):
        for state in ("normal", "focused"):
            with self.subTest(state=state):
                assert_sunken_outside_field(
                    self,
                    self.slices,
                    f"itemview-{state}",
                    LINEEDIT_SIZE,
                    LINEEDIT_COLOURS,
                )


class TestSurfaceBevelPixels(unittest.TestCase):
    """Pin the painted bevel of each part-3 surface state, not just its ids.

    `TestSvg` checks that the state ids and the palette exist, which a
    `menubaritem-pressed` repeating the flat `normal` art passes; these tests
    render each state's nine slices and compare them pixel for pixel, so a
    wrong frame element or a wrong bevel fails here.
    """

    def setUp(self):
        self.slices = render_slices(parse_svg(SVG))

    def _assert_surface_state(self, prefix, bevel, face, highlight):
        """Assert one surface state paints its flat or beveled art."""
        if bevel == "flat":
            self._assert_flat_state(prefix, face)
        else:
            self._assert_bevel_state(prefix, bevel, face, highlight)

    def test_every_surface_state_paints_its_bevel(self):
        for element, states in SURFACE_STATES.items():
            for state, (bevel, face) in states.items():
                prefix = f"{element}-{state}"
                highlight = (
                    TAB_HIGHLIGHT
                    if element == "tab" and state in ("normal", "focused")
                    else SURFACE_HIGHLIGHT
                )
                with self.subTest(element=element, state=state):
                    self._assert_surface_state(prefix, bevel, face, highlight)

    def _assert_flat_state(self, prefix, face):
        for name, (width, height) in SURFACE_SLICE_SIZES.items():
            slice_id = prefix if not name else f"{prefix}-{name}"
            assert_slice_pixels(
                self,
                self.slices,
                slice_id,
                pixel_map((face,) * (width * height), width, height),
            )

    def _assert_bevel_state(self, prefix, bevel, face, highlight):
        assert_slice_pixels(
            self,
            self.slices,
            prefix,
            pixel_map(
                (face,) * (BUTTON_SIZE * BUTTON_SIZE), BUTTON_SIZE, BUTTON_SIZE
            ),
        )
        for name, expected in _button_edge_maps(
            bevel, SURFACE_SHADOW, highlight
        ).items():
            assert_slice_pixels(self, self.slices, f"{prefix}-{name}", expected)
        for name, colours in _button_corners(
            bevel, SURFACE_SHADOW, highlight
        ).items():
            assert_slice_pixels(
                self, self.slices, f"{prefix}-{name}", colours
            )


if __name__ == "__main__":
    unittest.main()
