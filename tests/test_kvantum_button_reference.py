"""Ground the Kvantum button bevel's shadow in the reference's popup buttons.

`TestSvg` pins each button state's rects to the Platinum palette and
`TestButtonBevelPixels` pins their painted arrangement, but no test ties that
arrangement to a screenshot. The Get Info window's two popup buttons in
`aboutsystem_betawiki.png` are raised Platinum bars: a 1px #000000 outline, a
1px #FFFFFF top/left highlight, a #DDDDDD face and a 1px #AAAAAA bottom/right
shadow. `[ComboBox]` inherits `PanelButtonCommand` and renders through the
`button` element, so the screenshot grounds the button's bevel. This test
re-derives the four colours from the image and asserts the shipped
`button-normal` slices paint the raised arrangement and the `button-pressed`
slices the sunken one, both with the reference's #AAAAAA shadow. The
reference is a beta build (`aboutsystem_betawiki.png`).
"""

from __future__ import annotations

import unittest

from support.aurorae_fixtures import REFERENCE, REFERENCE_ROWS
from support.kvantum_fixtures import SVG
from support.platinum_palette import hex_colour
from support.reference_image import ReferenceScreenshotMixin
from support.svg_case import parse_svg
from svg_assertions import (
    bevel_corner_maps,
    bevel_edge_maps,
    pixel_map,
    render_slices,
)

# The Get Info window's "表示" popup button in aboutsystem_betawiki.png: a
# raised bar at x=80..249, y=103..122. The "ラベル" popup button repeats it at
# y=275..292. The path and decode bound come from `aurorae_fixtures`, whose
# readers decode the same screenshot, so the reference cache unfilters it once
# per run.
BUTTON_X = 150
BUTTON_Y = 103
BUTTON_SIZE = 30

# One pixel of the reference button per colour, button-relative: the top
# outline, the top highlight, the face and the bottom shadow.
_REFERENCE_ANCHORS = {
    "outline": (0, 0),
    "highlight": (0, 1),
    "face": (0, 5),
    "shadow": (0, 18),
}


def _button_edges(bevel, outline, highlight, shadow):
    """Return the four 2px edge slices a *bevel* paints, keyed by slice name.

    Each edge is the outer 1px *outline* with the bevel's 1px band inside it:
    a raised bevel highlights the top/left and shadows the bottom/right, and a
    sunken one swaps those two colours.
    """
    return bevel_edge_maps(
        BUTTON_SIZE, bevel, outline, highlight, shadow
    )


def _button_corners(bevel, outline, highlight, shadow):
    """Return each 2x2 corner pixel map a *bevel* paints, keyed by name."""
    return bevel_corner_maps(bevel, outline, highlight, shadow)


class TestButtonReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The button bevel shadow is the reference popup buttons' #AAAAAA.

    `TestSvg` and `TestButtonBevelPixels` pin the shipped art to the palette,
    so a button that keeps the other raised faces' #999999 shadow passes them.
    This derives the popup buttons' four colours from the screenshot and
    requires the shipped `button-normal` and `button-pressed` slices to paint
    the arrangement they describe.
    """

    REFERENCE = REFERENCE
    MAX_ROWS = REFERENCE_ROWS

    def _reference_colours(self):
        """Return the reference button's four colours, sampled at their anchors."""
        return {
            name: hex_colour(self.pixel(BUTTON_X + dx, BUTTON_Y + dy))
            for name, (dx, dy) in _REFERENCE_ANCHORS.items()
        }

    def test_reference_popup_button_is_the_raised_arrangement(self):
        # Derive the colours from one pixel each, then pin the values: the
        # shadow is the #AAAAAA that distinguishes the button from the other
        # raised faces' #999999. The second popup button repeats it, six rows
        # shallower (y=275..292), and the left bevel repeats the highlight.
        colours = self._reference_colours()
        self.assertEqual(colours["outline"], "#000000")
        self.assertEqual(colours["highlight"], "#FFFFFF")
        self.assertEqual(colours["face"], "#DDDDDD")
        self.assertEqual(colours["shadow"], "#AAAAAA")
        self.assertEqual(hex_colour(self.pixel(BUTTON_X, 291)), "#AAAAAA")
        self.assertEqual(hex_colour(self.pixel(80, 108)), "#000000")
        self.assertEqual(hex_colour(self.pixel(81, 108)), "#FFFFFF")

    def test_shipped_button_paints_the_reference_arrangement(self):
        # The reference colours, not the SVG's own literals, describe both the
        # raised resting button and the sunken pressed one: a #999999 shadow
        # or a swapped bevel fails here.
        colours = self._reference_colours()
        slices = render_slices(parse_svg(SVG))
        for state, bevel in (("normal", "raised"), ("pressed", "sunken")):
            prefix = f"button-{state}"
            with self.subTest(state=state):
                self.assertEqual(
                    slices[prefix],
                    pixel_map(
                        (colours["face"],) * (BUTTON_SIZE * BUTTON_SIZE),
                        BUTTON_SIZE,
                        BUTTON_SIZE,
                    ),
                )
                edges = _button_edges(
                    bevel,
                    colours["outline"],
                    colours["highlight"],
                    colours["shadow"],
                )
                for name, expected in edges.items():
                    self.assertEqual(slices[f"{prefix}-{name}"], expected, name)
                corners = _button_corners(
                    bevel,
                    colours["outline"],
                    colours["highlight"],
                    colours["shadow"],
                )
                for name, expected in corners.items():
                    self.assertEqual(
                        slices[f"{prefix}-{name}"], expected, name
                    )


if __name__ == "__main__":
    unittest.main()
