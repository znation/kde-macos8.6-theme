"""Ground the Kvantum line edit in the reference screenshot's sunken field.

`TestLineEditBevelPixels` pins the shipped tiles' pixels, but its expected
arrangement is written from the same palette, so a field whose bevel and
outline are both swapped there would pass; no test ties the field to a
screenshot. The Setup Assistant body text field in `firstboot_betawiki.png`
(retail Mac OS 8.6) is the reference's sunken field: a #999999 top/left
shadow and a #FFFFFF bottom/right highlight outside a 1px #000000 outline,
the same field the desktop theme's lineedit.svg is grounded in. This test
re-derives the field's border runs and corners from the image and asserts the
shipped `lineedit-normal` tiles paint the same arrangement; it skips when the
image is not materialized.
"""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import FIRSTBOOT_MAX_ROWS, FIRSTBOOT_REFERENCE
from support.firstboot_lineedit import FIELD_BORDER_RUNS, FIELD_CORNER_PIXELS
from support.kvantum_fixtures import SVG
from support.platinum_palette import hex_colour
from support.reference_image import ReferenceScreenshotMixin
from support.svg_case import parse_svg
from svg_assertions import assert_sunken_outside_field, render_slices

# One reference pixel per colour: the top-left shadow, the #000000 outline
# inside it, the #FFFFFF face, and the right edge's outer #FFFFFF highlight.
FIELD_ANCHORS = {
    "shadow": (28, 95),
    "outline": (29, 95),
    "face": (30, 95),
    "highlight": (431, 150),
}

LINEEDIT_SIZE = 30


class TestLineEditReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The line edit is the reference field's sunken-outside arrangement.

    `TestLineEditBevelPixels` pins the shipped tiles, so a field whose bevel
    and outline are swapped fails there only if the expected art is written
    the other way; this derives the four colours from the reference and
    requires both the reference field and the shipped `lineedit-normal` tiles
    to paint the arrangement they describe.
    """

    REFERENCE = FIRSTBOOT_REFERENCE
    MAX_ROWS = FIRSTBOOT_MAX_ROWS

    def test_borders_are_the_sunken_bevel_outside_the_outline(self):
        # Re-derive the field's four border runs from the reference rather
        # than trust the SVG comment: the outer pixel is the bevel, the inner
        # pixel the #000000 outline, and the face #FFFFFF.
        for (x, y), colour in FIELD_BORDER_RUNS:
            self.assertEqual(hex_colour(self.pixel(x, y)), colour, (x, y))

    def test_corners_match_the_reference(self):
        # The corners are easy to get subtly wrong: the top-right outer pixel
        # is the window face, not the shadow, and the #000000 outline stops
        # one row short of the bottom, whose outer row is the #FFFFFF
        # highlight. Re-derive each pixel.
        for (x, y), colour in FIELD_CORNER_PIXELS:
            self.assertEqual(hex_colour(self.pixel(x, y)), colour, (x, y))

    def test_shipped_lineedit_paints_the_reference_arrangement(self):
        # Derive the four field colours from one reference pixel each, then
        # require the shipped `lineedit-normal` nine-slice to paint the
        # arrangement they describe: a white face, the bevel outside the
        # outline, and the corner blocks the reference's corners show.
        colours = {
            name: hex_colour(self.pixel(x, y))
            for name, (x, y) in FIELD_ANCHORS.items()
        }
        self.assertEqual(colours["shadow"], "#999999")
        self.assertEqual(colours["outline"], "#000000")
        self.assertEqual(colours["face"], "#FFFFFF")
        self.assertEqual(colours["highlight"], "#FFFFFF")
        slices = render_slices(parse_svg(SVG))
        assert_sunken_outside_field(
            self, slices, "lineedit-normal", LINEEDIT_SIZE, colours
        )


if __name__ == "__main__":
    unittest.main()
