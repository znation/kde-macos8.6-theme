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
from support.reference_image import ReferenceScreenshotMixin
from support.sunken_field_reference import (
    ShippedSunkenFieldMixin,
    SunkenFieldReferenceMixin,
)

# One reference pixel per colour: the top-left shadow, the #000000 outline
# inside it, the #FFFFFF face, and the right edge's outer #FFFFFF highlight.
FIELD_ANCHORS = {
    "shadow": (28, 95),
    "outline": (29, 95),
    "face": (30, 95),
    "highlight": (431, 150),
}


class TestLineEditReference(
    ShippedSunkenFieldMixin,
    SunkenFieldReferenceMixin,
    ReferenceScreenshotMixin,
    unittest.TestCase,
):
    """The line edit is the reference field's sunken-outside arrangement.

    `TestLineEditBevelPixels` pins the shipped tiles, so a field whose bevel
    and outline are swapped fails there only if the expected art is written
    the other way; this derives the four colours from the reference and
    requires both the reference field and the shipped `lineedit-normal` tiles
    to paint the arrangement they describe.
    """

    REFERENCE = FIRSTBOOT_REFERENCE
    MAX_ROWS = FIRSTBOOT_MAX_ROWS
    BORDER_RUNS = FIELD_BORDER_RUNS
    CORNER_PIXELS = FIELD_CORNER_PIXELS
    ANCHORS = FIELD_ANCHORS
    SLICE_SVG = SVG
    SLICE_NAME = "lineedit-normal"
    SLICE_SIZE = 30


if __name__ == "__main__":
    unittest.main()
