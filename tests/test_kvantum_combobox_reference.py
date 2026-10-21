"""Ground the Kvantum combo box indicator in the reference's double arrow.

`TestSvg` pins the ``comboarrow`` interior's rects to the Platinum palette and
their painted arrangement, but no test ties that arrangement to a screenshot.
The System Info window's "Show:" popup in `systeminfo_betawiki.png` (an 8.6a3c2
beta build) draws a double up/down arrow in a 12x12 #DDDDDD cell: two black
triangles of one-row bands whose widths run 1/3/5/7 and 7/5/3/1, separated by
two face rows. This test re-derives the cell from the image and asserts the
shipped ``comboarrow-*`` groups paint it. The cell's divider and right bevel
are frame art, not indicator art, so they are outside the sampled cell.
"""

from __future__ import annotations

import unittest

from support.kvantum_fixtures import (
    SVG,
    SYSTEMINFO_MAX_ROWS,
    SYSTEMINFO_REFERENCE,
)
from support.platinum_palette import BLACK, FACE, GREY, hex_colour
from support.reference_image import ReferenceScreenshotMixin
from support.svg_case import parse_svg
from svg_assertions import render_slices

# The "Show:" popup's 12x12 arrow region, top-left corner included, in
# systeminfo_betawiki.png.
COMBO_X = 233
COMBO_Y = 106
COMBO_SIZE = 12

# Each black band as (cell-relative y, left x, width), top to bottom: the
# upper triangle widens 1/3/5/7 and the lower one narrows 7/5/3/1.
_BLACK_ROWS = (
    (1, 5, 1),
    (2, 4, 3),
    (3, 3, 5),
    (4, 2, 7),
    (7, 2, 7),
    (8, 3, 5),
    (9, 4, 3),
    (10, 5, 1),
)


def _black_points():
    """Return the set of cell-relative ``(x, y)`` points the arrow paints black."""
    points = set()
    for y, x, width in _BLACK_ROWS:
        points.update((x + offset, y) for offset in range(width))
    return points


class TestComboBoxReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The combo box indicator is the reference popup's double arrow cell."""

    REFERENCE = SYSTEMINFO_REFERENCE
    MAX_ROWS = SYSTEMINFO_MAX_ROWS

    def _reference_cell(self):
        """Return the reference's 12x12 arrow cell as a cell-relative pixel map."""
        return {
            (dx, dy): hex_colour(self.pixel(COMBO_X + dx, COMBO_Y + dy))
            for dy in range(COMBO_SIZE)
            for dx in range(COMBO_SIZE)
        }

    def test_reference_popup_draws_the_double_arrow_cell(self):
        cell = self._reference_cell()
        # Derive every pixel, then pin the two colours and the exact black
        # bands: an arrow with one triangle, a shifted centre or a changed gap
        # fails here rather than only against the shipped SVG.
        self.assertEqual(set(cell.values()), {BLACK, FACE})
        self.assertEqual(
            {point for point, colour in cell.items() if colour == BLACK},
            _black_points(),
        )

    def test_shipped_comboarrow_paints_the_reference_cell(self):
        cell = self._reference_cell()
        slices = render_slices(parse_svg(SVG))
        self.assertEqual(slices["comboarrow-normal"], cell)
        for state in ("focused", "pressed", "toggled"):
            self.assertEqual(slices[f"comboarrow-{state}"], cell, state)
        # The disabled cell keeps the face and greys only the arrow, as the
        # shared arrow's disabled state does.
        disabled = {
            point: GREY if colour == BLACK else colour
            for point, colour in cell.items()
        }
        self.assertEqual(slices["comboarrow-disabled"], disabled)


if __name__ == "__main__":
    unittest.main()
