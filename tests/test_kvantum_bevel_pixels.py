"""Pin the painted bevel of each org.macos8.desktop Kvantum SVG state.

`TestSvg` checks that the state ids and the palette exist, which a pressed
state repeating the raised art passes; these tests render each state's nine
slices and compare them pixel for pixel, so a raised `button-pressed`, a
`menubaritem-pressed` repeating the flat `normal` art, or a wrong frame element
fails here.
"""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from support.kvantum_fixtures import SVG
from support.platinum_palette import (
    FACE,
    SELECTION,
    TOOLTIP_FACE,
    WHITE,
)
from svg_assertions import assert_slice_pixels, pixel_map, render_slices

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
# slice-local coordinates.
BUTTON_CORNERS = {
    "raised": {
        "topleft": ("#000000", "#000000", "#000000", "#FFFFFF"),
        "topright": ("#000000", "#000000", "#999999", "#000000"),
        "bottomleft": ("#000000", "#FFFFFF", "#000000", "#000000"),
        "bottomright": ("#999999", "#000000", "#000000", "#000000"),
    },
    "sunken": {
        "topleft": ("#000000", "#000000", "#000000", "#999999"),
        "topright": ("#000000", "#000000", "#FFFFFF", "#000000"),
        "bottomleft": ("#000000", "#999999", "#000000", "#000000"),
        "bottomright": ("#FFFFFF", "#000000", "#000000", "#000000"),
    },
}

# Part 3's frame elements, the bevel each state paints and the colour of its
# centre. `raised` and `sunken` paint the eight bevel slices and four corners
# `_button_edge_maps`/`BUTTON_CORNERS` describe; `flat` paints every slice as
# a solid fill with no outline or bevel, the project's flat-selection art for
# a highlighted item. The pixel test renders each state's nine slices, so a
# `menubaritem-pressed` that gains a bevel, or a `menu` drawn with a sunken
# bevel, fails here rather than passing on ids alone. The selected tab keeps
# the raised bevel the desktop theme's active tab paints.
SURFACE_STATES = {
    "tab": {
        "normal": ("raised", FACE),
        "focused": ("raised", FACE),
        "toggled": ("raised", FACE),
    },
    "tabframe": {"normal": ("raised", FACE)},
    "menu": {"normal": ("raised", FACE)},
    "group": {"normal": ("raised", FACE)},
    "tooltip": {"normal": ("raised", TOOLTIP_FACE)},
    "itemview": {
        "normal": ("sunken", WHITE),
        "focused": ("sunken", WHITE),
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


def _button_edge_maps(bevel):
    """Return the four 2px edge slices a *bevel* paints, keyed by slice name.

    Each edge is the outer 1px #000000 outline with the bevel's 1px band
    inside it: a raised bevel highlights the top/left and shadows the
    bottom/right, and a sunken one swaps those two colours.
    """
    if bevel == "raised":
        top, bottom = ("#000000", "#FFFFFF"), ("#999999", "#000000")
        left, right = ("#000000", "#FFFFFF"), ("#999999", "#000000")
    else:
        top, bottom = ("#000000", "#999999"), ("#FFFFFF", "#000000")
        left, right = ("#000000", "#999999"), ("#FFFFFF", "#000000")
    return {
        "top": pixel_map(
            (top[0],) * BUTTON_SIZE + (top[1],) * BUTTON_SIZE, BUTTON_SIZE, 2
        ),
        "bottom": pixel_map(
            (bottom[0],) * BUTTON_SIZE + (bottom[1],) * BUTTON_SIZE, BUTTON_SIZE, 2
        ),
        "left": pixel_map(left * BUTTON_SIZE, 2, BUTTON_SIZE),
        "right": pixel_map(right * BUTTON_SIZE, 2, BUTTON_SIZE),
    }


class TestButtonBevelPixels(unittest.TestCase):
    """Pin the painted bevel of each button state, not just its ids.

    `TestSvg` checks that the state ids and the palette exist, which a pressed
    state repeating the raised art passes; these tests render each state's
    nine slices and compare them pixel for pixel, so a raised `button-pressed`
    or `button-toggled` fails here.
    """

    def setUp(self):
        self.slices = render_slices(ET.parse(SVG))

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
                for name, expected in _button_edge_maps(bevel).items():
                    assert_slice_pixels(
                        self, self.slices, f"{prefix}-{name}", expected
                    )
                for name, colours in BUTTON_CORNERS[bevel].items():
                    assert_slice_pixels(
                        self, self.slices, f"{prefix}-{name}", pixel_map(colours, 2, 2)
                    )


class TestSurfaceBevelPixels(unittest.TestCase):
    """Pin the painted bevel of each part-3 surface state, not just its ids.

    `TestSvg` checks that the state ids and the palette exist, which a
    `menubaritem-pressed` repeating the flat `normal` art passes; these tests
    render each state's nine slices and compare them pixel for pixel, so a
    wrong frame element or a wrong bevel fails here.
    """

    def setUp(self):
        self.slices = render_slices(ET.parse(SVG))

    def test_every_surface_state_paints_its_bevel(self):
        for element, states in SURFACE_STATES.items():
            for state, (bevel, face) in states.items():
                prefix = f"{element}-{state}"
                with self.subTest(element=element, state=state):
                    if bevel == "flat":
                        self._assert_flat_state(prefix, face)
                    else:
                        self._assert_bevel_state(prefix, bevel, face)

    def _assert_flat_state(self, prefix, face):
        for name, (width, height) in SURFACE_SLICE_SIZES.items():
            slice_id = prefix if not name else f"{prefix}-{name}"
            assert_slice_pixels(
                self,
                self.slices,
                slice_id,
                pixel_map((face,) * (width * height), width, height),
            )

    def _assert_bevel_state(self, prefix, bevel, face):
        assert_slice_pixels(
            self,
            self.slices,
            prefix,
            pixel_map(
                (face,) * (BUTTON_SIZE * BUTTON_SIZE), BUTTON_SIZE, BUTTON_SIZE
            ),
        )
        for name, expected in _button_edge_maps(bevel).items():
            assert_slice_pixels(self, self.slices, f"{prefix}-{name}", expected)
        for name, colours in BUTTON_CORNERS[bevel].items():
            assert_slice_pixels(
                self, self.slices, f"{prefix}-{name}", pixel_map(colours, 2, 2)
            )


if __name__ == "__main__":
    unittest.main()
