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

import os
import unittest

from support.kvantum_fixtures import SVG
from support.platinum_palette import hex_colour
from support.reference_image import ReferenceScreenshotMixin
from support.svg_case import parse_svg
from support.theme_install import ROOT
from svg_assertions import pixel_map, render_slices
from svg_assertions.faces import sunken_outside_face_corners

# The Setup Assistant body text field in firstboot_betawiki.png (retail Mac OS
# 8.6). Its 2px border is a #999999/#FFFFFF bevel outside a 1px #000000
# outline, over the #FFFFFF face. Only the field's bottom row is a constant,
# to bound the decode; the runs and corners below pin its other edges.
REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "firstboot_betawiki.png"
)
FIELD_BOTTOM = 351
MAX_ROWS = FIELD_BOTTOM + 1

# The field's border runs, read from the outside in: the bevel's outer pixel,
# the #000000 outline and the #FFFFFF face. One run per side, away from the
# corners.
FIELD_BORDER_RUNS = (
    # left border, left to right at y=95
    ((28, 95), "#999999"),
    ((29, 95), "#000000"),
    ((30, 95), "#FFFFFF"),
    # top border, top to bottom at x=100
    ((100, 58), "#999999"),
    ((100, 59), "#000000"),
    ((100, 60), "#FFFFFF"),
    # right border at y=150: face, outline, outer highlight
    ((429, 150), "#FFFFFF"),
    ((430, 150), "#000000"),
    ((431, 150), "#FFFFFF"),
    # bottom border at x=100: face, outline, outer highlight
    ((100, 349), "#FFFFFF"),
    ((100, 350), "#000000"),
    ((100, 351), "#FFFFFF"),
)

# The field's four 2x2 corners, row-major from the field's top-left pixel.
# The top-right outer pixel (431,58) is the window face #CCCCCC: the top
# shadow stops one pixel short of the outer highlight, so that corner leaves
# it unpainted, and the shipped corner tile does too.
FIELD_CORNER_PIXELS = (
    ((28, 58), "#999999"),
    ((29, 58), "#999999"),
    ((28, 59), "#999999"),
    ((29, 59), "#000000"),
    ((430, 58), "#999999"),
    ((431, 58), "#CCCCCC"),
    ((430, 59), "#000000"),
    ((431, 59), "#FFFFFF"),
    ((28, 350), "#999999"),
    ((29, 350), "#000000"),
    ((28, 351), "#999999"),
    ((29, 351), "#000000"),
    ((430, 350), "#000000"),
    ((431, 350), "#FFFFFF"),
    ((430, 351), "#000000"),
    ((431, 351), "#FFFFFF"),
)

# One reference pixel per colour: the top-left shadow, the #000000 outline
# inside it, the #FFFFFF face, and the right edge's outer #FFFFFF highlight.
FIELD_ANCHORS = {
    "shadow": (28, 95),
    "outline": (29, 95),
    "face": (30, 95),
    "highlight": (431, 150),
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

LINEEDIT_SIZE = 30


def _edge_map(side, outer, inner):
    """Return the 2px *side* edge slice, reading *outer* then *inner*."""
    if side == "top":
        rows = (outer,) * LINEEDIT_SIZE + (inner,) * LINEEDIT_SIZE
    elif side == "bottom":
        rows = (inner,) * LINEEDIT_SIZE + (outer,) * LINEEDIT_SIZE
    elif side == "left":
        return {(0, y): outer for y in range(LINEEDIT_SIZE)} | {
            (1, y): inner for y in range(LINEEDIT_SIZE)
        }
    else:
        return {(0, y): inner for y in range(LINEEDIT_SIZE)} | {
            (1, y): outer for y in range(LINEEDIT_SIZE)
        }
    return pixel_map(rows, LINEEDIT_SIZE, 2)


def _corner_map(colours):
    """Return the 2x2 corner map for *colours*, dropping the unpainted None."""
    return {
        (index % 2, index // 2): colour
        for index, colour in enumerate(colours)
        if colour is not None
    }


class TestLineEditReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The line edit is the reference field's sunken-outside arrangement.

    `TestLineEditBevelPixels` pins the shipped tiles, so a field whose bevel
    and outline are swapped fails there only if the expected art is written
    the other way; this derives the four colours from the reference and
    requires both the reference field and the shipped `lineedit-normal` tiles
    to paint the arrangement they describe.
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
        # The corners are easy to get subtly wrong: the top-right outer pixel
        # is the window face, not the shadow, and both bottom corners carry
        # the #000000 outline to their bottom row. Re-derive each pixel.
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
        prefix = "lineedit-normal"
        self.assertEqual(
            slices[prefix],
            pixel_map(
                (colours["face"],) * (LINEEDIT_SIZE * LINEEDIT_SIZE),
                LINEEDIT_SIZE,
                LINEEDIT_SIZE,
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
                _edge_map(side, outer, inner),
                side,
            )
        table = sunken_outside_face_corners(colours["face"])
        for name, indices in _OUTER_BLOCK_INDICES.items():
            expected = _corner_map(tuple(table[name][index] for index in indices))
            self.assertEqual(slices[f"{prefix}-{name}"], expected, name)


if __name__ == "__main__":
    unittest.main()
