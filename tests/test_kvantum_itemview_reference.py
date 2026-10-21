"""Ground the Kvantum item view in the reference screenshot's sunken field.

`TestItemViewBevelPixels` pins the shipped tiles' pixels, but its expected
arrangement is written from the same palette, so an item view whose bevel and
outline are both swapped there would pass; no test ties the field to a
screenshot. The item view in `setup_emaculation.png` (retail Mac OS 8.6
installer CD Finder window) is the reference's sunken field: a #999999
top/left shadow and a #FFFFFF bottom/right highlight outside a 1px #000000
outline, the same field the desktop theme's lineedit.svg and the shipped
Kvantum line edit are grounded in. This test re-derives the field's border
runs and top-left corner from the image and asserts the shipped
`itemview-normal` tiles paint the same arrangement; it skips when the image is
not materialized. The field's top-right and bottom-right corners sit under
the status header and the scrollbars, so only the clean left/top/right/bottom
runs, the top-left corner and the bottom-left corner are derived.
"""

from __future__ import annotations

import unittest

from support.desktoptheme_paths import SETUP_MAX_ROWS, SETUP_REFERENCE
from support.kvantum_fixtures import SVG
from support.platinum_palette import hex_colour
from support.reference_image import ReferenceScreenshotMixin
from support.svg_case import parse_svg
from svg_assertions import corner_map, edge_map, pixel_map, render_slices
from svg_assertions.faces import sunken_outside_face_corners

# The installer CD Finder window's item view in setup_emaculation.png (retail
# Mac OS 8.6). Its 2px border is a #999999/#FFFFFF bevel outside a 1px #000000
# outline, over the #FFFFFF face. Only the field's bottom row is a constant,
# to bound the decode; the runs and corners below pin its other edges. The
# scroll-bar reader shares the bound, so the screenshot is decoded once.
REFERENCE = SETUP_REFERENCE
MAX_ROWS = SETUP_MAX_ROWS

# The field's border runs, read from the outside in: the bevel's outer pixel,
# the #000000 outline and the #FFFFFF face. One run per side, away from the
# corners. The right and bottom runs stop at the outer highlight: a scrollbar
# trough sits against those edges, so their face pixel is not the field's.
FIELD_BORDER_RUNS = (
    # left border, left to right at y=250
    ((22, 250), "#999999"),
    ((23, 250), "#000000"),
    ((24, 250), "#FFFFFF"),
    # top border, top to bottom at x=200
    ((200, 118), "#999999"),
    ((200, 119), "#000000"),
    ((200, 120), "#FFFFFF"),
    # right border at y=200: outline, outer highlight
    ((452, 200), "#000000"),
    ((453, 200), "#FFFFFF"),
    # bottom border at x=100: outline, outer highlight
    ((100, 477), "#000000"),
    ((100, 478), "#FFFFFF"),
)

# The field's clean 2x2 corners, row-major from the field's top-left pixel.
# The top-right and bottom-right corners sit under the status header and the
# scrollbars. The bottom-left corner's outer bottom pixel (22,478) is the
# window face #CCCCCC -- the bottom highlight starts one pixel in from the
# left -- so the shipped tile leaves it unpainted, as the line edit's
# top-right tile does.
FIELD_CORNER_PIXELS = (
    ((22, 118), "#999999"),
    ((23, 118), "#999999"),
    ((22, 119), "#999999"),
    ((23, 119), "#000000"),
    ((22, 477), "#999999"),
    ((23, 477), "#000000"),
    ((22, 478), "#CCCCCC"),
    ((23, 478), "#FFFFFF"),
)

# One reference pixel per colour: the top-left shadow, the #000000 outline
# inside it, the #FFFFFF face, and the right edge's outer #FFFFFF highlight.
FIELD_ANCHORS = {
    "shadow": (22, 250),
    "outline": (23, 250),
    "face": (24, 250),
    "highlight": (453, 200),
}

# The outer 2x2 block of each `sunken_outside` 3x3 corner table: the block
# holding the outer corner pixel, which never contains the table's face
# pixel. Row-major slice-local indices into the 3x3 table.
_OUTER_BLOCK_INDICES = {
    "topleft": (0, 1, 3, 4),
    "topright": (1, 2, 4, 5),
    "bottomleft": (3, 4, 6, 7),
    "bottomright": (4, 5, 7, 8),
}

ITEMVIEW_SIZE = 30


class TestItemViewReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The item view is the reference field's sunken-outside arrangement.

    `TestItemViewBevelPixels` pins the shipped tiles, so an item view whose
    bevel and outline are swapped fails there only if the expected art is
    written the other way; this derives the four colours from the reference
    and requires both the reference field and the shipped `itemview-normal`
    tiles to paint the arrangement they describe.
    """

    REFERENCE = REFERENCE
    MAX_ROWS = MAX_ROWS

    def test_borders_are_the_sunken_bevel_outside_the_outline(self):
        # Re-derive the field's four border runs from the reference rather
        # than trust the SVG comment: the outer pixel is the bevel, the inner
        # pixel the #000000 outline, and the face #FFFFFF.
        for (x, y), colour in FIELD_BORDER_RUNS:
            self.assertEqual(hex_colour(self.pixel(x, y)), colour, (x, y))

    def test_corners_match_the_reference(self):
        # The top-left corner is the #999999 bevel wrapping the #000000
        # outline's first pixel. The bottom-left corner leaves its outer
        # bottom pixel to the window face, with the highlight one pixel in.
        # Re-derive each pixel.
        for (x, y), colour in FIELD_CORNER_PIXELS:
            self.assertEqual(hex_colour(self.pixel(x, y)), colour, (x, y))

    def test_shipped_itemview_paints_the_reference_arrangement(self):
        # Derive the four field colours from one reference pixel each, then
        # require the shipped `itemview-normal` nine-slice to paint the
        # arrangement they describe: a white face, the bevel outside the
        # outline, and the corner blocks the reference's clean corners show.
        colours = {
            name: hex_colour(self.pixel(x, y))
            for name, (x, y) in FIELD_ANCHORS.items()
        }
        self.assertEqual(colours["shadow"], "#999999")
        self.assertEqual(colours["outline"], "#000000")
        self.assertEqual(colours["face"], "#FFFFFF")
        self.assertEqual(colours["highlight"], "#FFFFFF")
        slices = render_slices(parse_svg(SVG))
        prefix = "itemview-normal"
        self.assertEqual(
            slices[prefix],
            pixel_map(
                (colours["face"],) * (ITEMVIEW_SIZE * ITEMVIEW_SIZE),
                ITEMVIEW_SIZE,
                ITEMVIEW_SIZE,
            ),
        )
        edges = {
            "top": (colours["shadow"], colours["outline"]),
            "bottom": (colours["highlight"], colours["outline"]),
            "left": (colours["shadow"], colours["outline"]),
            "right": (colours["highlight"], colours["outline"]),
        }
        for side, (outer, inner) in edges.items():
            self.assertEqual(
                slices[f"{prefix}-{side}"],
                edge_map(ITEMVIEW_SIZE, side, outer, inner),
                side,
            )
        table = sunken_outside_face_corners(colours["face"])
        corners = {
            name: corner_map(tuple(table[name][index] for index in indices))
            for name, indices in _OUTER_BLOCK_INDICES.items()
        }
        for name, expected in corners.items():
            self.assertEqual(slices[f"{prefix}-{name}"], expected, name)


if __name__ == "__main__":
    unittest.main()
