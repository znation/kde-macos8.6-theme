"""Ground the Kvantum check box face in the reference screenshot.

`TestSvg` pins each check box interior's rects to the Platinum palette, which
a flat white square or a raised square with the wrong bevel shadow passes; no
test ties the face to a screenshot. The Get Info window's "Locked" check box
at `aboutsystem_betawiki.png` x=38..49, y=382..393 (the same face in
`systeminfo_betawiki.png` at the same pixels) is a 12x12 raised Platinum
square: a 1px #000000 outline, a 1px #FFFFFF top/left highlight, a #DDDDDD
face and a 1px #888888 bottom/right shadow, with the top-right and bottom-left
corners where a highlight meets a shadow left the face colour. This test
re-derives that arrangement from the image and asserts the shipped
`checkbox-normal` interior paints the same arrangement on its 14x14 canvas.
The reference is a beta build (`aboutsystem_betawiki.png`,
`systeminfo_betawiki.png`); no retail screenshot shows a check box.
"""

from __future__ import annotations

import os
import unittest
import xml.etree.ElementTree as ET

from support.kvantum_fixtures import SVG
from support.platinum_palette import hex_colour
from support.reference_image import ReferenceScreenshotMixin
from support.theme_install import ROOT
from svg_assertions import render_slices

# The Get Info window's "Locked" check box: a 12x12 raised Platinum square
# including its 1px outline.
REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "aboutsystem_betawiki.png"
)
CHECKBOX_X = 38
CHECKBOX_Y = 382
REFERENCE_SIZE = 12

# The shipped `checkbox-normal` element is a 14x14 canvas: the reference's
# 12x12 box with the same 1px outline, so its interior is 12x12 rather than
# the reference's 10x10. The extra interior pixels extend the face, not the
# 1px bevel bands.
SHIPPED_SIZE = 14

# One pixel of the reference box per colour, box-relative: the top-left
# outline, the top highlight row, the face and the right shadow column.
_REFERENCE_ANCHORS = {
    "outline": (0, 0),
    "highlight": (1, 1),
    "face": (2, 3),
    "shadow": (10, 3),
}


def _raised_box(size, outline, highlight, face, shadow):
    """Return the ``{(x, y): colour}`` raised Platinum square of *size* pixels.

    The outer 1px ring is *outline*; inside it the top row and left column are
    the *highlight* and the bottom row and right column are the *shadow*. The
    two diagonal corners where a highlight band meets a shadow band -- the
    top-right and the bottom-left -- stay *face*, as the reference's check box
    shows.
    """
    pixels = {}
    for x in range(size):
        for y in range(size):
            if x in (0, size - 1) or y in (0, size - 1):
                pixels[(x, y)] = outline
            elif y == 1 or x == 1:
                pixels[(x, y)] = highlight
            elif y == size - 2 or x == size - 2:
                pixels[(x, y)] = shadow
            else:
                pixels[(x, y)] = face
    pixels[(size - 2, 1)] = face
    pixels[(1, size - 2)] = face
    return pixels


class TestCheckBoxReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The check box face is the reference's raised Platinum square.

    `TestSvg` pins the shipped rects to the palette, so a flat white square or
    a raised square with the wrong bevel shadow passes it. The reference's
    check box is a raised square, so this derives its four colours and their
    arrangement from the screenshot and checks both the screenshot and the
    shipped `checkbox-normal` art against them.
    """

    REFERENCE = REFERENCE
    MAX_ROWS = CHECKBOX_Y + REFERENCE_SIZE

    def _reference_colours(self):
        """Return the reference box's four colours, sampled at their anchors."""
        return {
            name: hex_colour(
                self.pixel(CHECKBOX_X + dx, CHECKBOX_Y + dy)
            )
            for name, (dx, dy) in _REFERENCE_ANCHORS.items()
        }

    def test_reference_box_is_the_raised_arrangement(self):
        # Derive the colours from one pixel each, then require the whole 12x12
        # box to be the raised arrangement those colours describe. A flat
        # white box, a #999999 shadow or a face-coloured highlight fails here.
        colours = self._reference_colours()
        self.assertEqual(colours["outline"], "#000000")
        self.assertEqual(colours["highlight"], "#FFFFFF")
        self.assertEqual(colours["face"], "#DDDDDD")
        self.assertEqual(colours["shadow"], "#888888")
        actual = {
            (x, y): hex_colour(self.pixel(CHECKBOX_X + x, CHECKBOX_Y + y))
            for x in range(REFERENCE_SIZE)
            for y in range(REFERENCE_SIZE)
        }
        self.assertEqual(actual, _raised_box(REFERENCE_SIZE, **colours))

    def test_shipped_checkbox_paints_the_reference_arrangement(self):
        # The shipped art's canvas is larger than the reference box, but the
        # same raised arrangement with the reference's four colours must fill
        # it: a flat white interior or a black/white fill swap fails here.
        expected = _raised_box(SHIPPED_SIZE, **self._reference_colours())
        slices = render_slices(ET.parse(SVG))
        self.assertEqual(slices["checkbox-normal"], expected)


if __name__ == "__main__":
    unittest.main()
