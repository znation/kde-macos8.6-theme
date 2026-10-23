"""Ground the desktop theme push button's raised bevel shadow in the reference.

`TestButton` pins the button's arrangement to the Platinum palette and
`test_button_edge_pixels` pins its bands, but no test ties that arrangement to
a screenshot. The Get Info window's two popup buttons in
`aboutsystem_betawiki.png` are raised Platinum bars: a 1px #000000 outline, a
1px #FFFFFF top/left highlight, a #DDDDDD face and a 1px #AAAAAA bottom/right
shadow. The `[ComboBox]`-style popup and the desktop push button share that
raised bevel, so the screenshot grounds the button's shadow. This test
re-derives the four colours from the image and asserts the shipped `normal`
slices paint the raised arrangement and the `pressed` slices the sunken one,
both with the reference's #AAAAAA shadow. The reference is a beta build
(`aboutsystem_betawiki.png`).
"""

from __future__ import annotations

import unittest

from support.aurorae_fixtures import REFERENCE, REFERENCE_ROWS
from support.desktoptheme_paths import BUTTON_SVG
from support.reference_button import (
    assert_reference_button_is_raised,
    reference_button_colours,
)
from support.reference_image import ReferenceScreenshotMixin
from support.svg_case import parse_svg
from svg_assertions import (
    assert_edge_bevels,
    children_named,
    elements_by_id,
    face_edge_bands,
    render_slices,
)


def _corner_fills(bevel, outline, highlight, shadow, face):
    """Return each corner slice's path fills, in document order, for *bevel*.

    A raised corner paints the outline, the highlight and the face on the
    two same-side corners and adds the shadow on the two mixed corners, where
    the bevel turns; a sunken corner swaps the highlight and shadow. This is
    the desktop button's 3px-radius corner in the button's own colours.
    """
    if bevel == "raised":
        return {
            "topleft": (outline, highlight, face),
            "topright": (outline, highlight, shadow, face),
            "bottomleft": (outline, highlight, shadow, face),
            "bottomright": (outline, shadow, face),
        }
    return {
        "topleft": (outline, shadow, face),
        "topright": (outline, shadow, highlight, face),
        "bottomleft": (outline, shadow, highlight, face),
        "bottomright": (outline, highlight, face),
    }


class TestButtonReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The push button's bevel shadow is the reference popup buttons' #AAAAAA.

    `TestButton` pins the shipped art to the palette, so a button that keeps
    the other raised faces' #999999 shadow passes it. This derives the popup
    buttons' four colours from the screenshot and requires the shipped
    `normal` and `pressed` slices to paint the arrangement they describe.
    """

    REFERENCE = REFERENCE
    MAX_ROWS = REFERENCE_ROWS

    def _reference_colours(self):
        """Return the reference button's four colours, sampled at their anchors."""
        return reference_button_colours(self.pixel)

    def test_reference_popup_button_is_the_raised_arrangement(self):
        assert_reference_button_is_raised(self, self.pixel)

    def test_shipped_button_paints_the_reference_arrangement(self):
        # The reference colours, not the SVG's own literals, describe both the
        # raised resting button and the sunken pressed one: a #999999 shadow
        # or a swapped bevel fails here. The edge slices are rects, so
        # `render_slices` composites them; the corner slices are paths, so
        # read the order their fills are painted in.
        colours = self._reference_colours()
        tree = parse_svg(BUTTON_SVG)
        slices = render_slices(tree)
        by_id = elements_by_id(tree)
        for prefix, bevel in (("normal", "raised"), ("pressed", "sunken")):
            outward, mirrored = face_edge_bands(
                colours["face"], bevel, shadow=colours["shadow"]
            )
            assert_edge_bevels(self, slices, prefix, outward, mirrored)
            corners = _corner_fills(
                bevel,
                colours["outline"],
                colours["highlight"],
                colours["shadow"],
                colours["face"],
            )
            for corner, expected in corners.items():
                name = f"{prefix}-{corner}"
                actual = tuple(
                    child.get("fill")
                    for child in children_named(by_id[name], "path")
                )
                with self.subTest(corner=name):
                    self.assertEqual(actual, expected, name)


if __name__ == "__main__":
    unittest.main()
