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
from support.reference_image import ReferenceScreenshotMixin
from support.sunken_field_reference import (
    ShippedSunkenFieldMixin,
    SunkenFieldReferenceMixin,
)

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


class TestItemViewReference(
    ShippedSunkenFieldMixin,
    SunkenFieldReferenceMixin,
    ReferenceScreenshotMixin,
    unittest.TestCase,
):
    """The item view is the reference field's sunken-outside arrangement.

    `TestItemViewBevelPixels` pins the shipped tiles, so an item view whose
    bevel and outline are swapped fails there only if the expected art is
    written the other way; this derives the four colours from the reference
    and requires both the reference field and the shipped `itemview-normal`
    tiles to paint the arrangement they describe.
    """

    REFERENCE = REFERENCE
    MAX_ROWS = MAX_ROWS
    BORDER_RUNS = FIELD_BORDER_RUNS
    CORNER_PIXELS = FIELD_CORNER_PIXELS
    ANCHORS = FIELD_ANCHORS
    SLICE_SVG = SVG
    SLICE_NAME = "itemview-normal"
    SLICE_SIZE = 30


if __name__ == "__main__":
    unittest.main()
