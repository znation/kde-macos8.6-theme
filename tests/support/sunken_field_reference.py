"""Re-derive a reference screenshot's sunken field and the tiles that paint it.

Three reference tests read a field whose #999999/#FFFFFF bevel sits outside a
1px #000000 outline: the desktop theme's line edit
(`test_desktoptheme_lineedit.py`), the Kvantum line edit and the Kvantum item
view (both under `test_kvantum_*_reference.py`). They carried the same
border-run and corner loops; the two Kvantum tests also derived the same four
anchor colours and asserted the shipped nine-slice against them. The mixins
here hold one copy of each.

A mixin deliberately does not subclass `unittest.TestCase`: each test module
combines it with that base, so discovery collects only the concrete classes.
`SunkenFieldReferenceMixin` needs `BORDER_RUNS` and `CORNER_PIXELS` on the
class; `ShippedSunkenFieldMixin` additionally needs `ANCHORS`, `SLICE_SVG`,
`SLICE_NAME` and `SLICE_SIZE`.
"""

from __future__ import annotations

from support.platinum_palette import hex_colour
from support.svg_case import parse_svg
from svg_assertions import assert_sunken_outside_field, render_slices


class SunkenFieldReferenceMixin:
    """Re-derive the reference field's border runs and clean corners."""

    def test_borders_are_the_sunken_bevel_outside_the_outline(self):
        # Re-derive the field's border runs from the reference rather than
        # trust the SVG comment: the outer pixel is the bevel, the inner
        # pixel the #000000 outline, and the face #FFFFFF.
        for (x, y), colour in self.BORDER_RUNS:
            self.assertEqual(hex_colour(self.pixel(x, y)), colour, (x, y))

    def test_corners_match_the_reference(self):
        # The corners are easy to get subtly wrong: an outer pixel can be the
        # window face rather than the shadow, and the outline can stop one
        # row short of the bottom. Re-derive each pixel.
        for (x, y), colour in self.CORNER_PIXELS:
            self.assertEqual(hex_colour(self.pixel(x, y)), colour, (x, y))


class ShippedSunkenFieldMixin:
    """Require a shipped nine-slice to paint the reference field's colours."""

    def test_shipped_slice_paints_the_reference_arrangement(self):
        # Derive the four field colours from one reference pixel each, then
        # require the shipped nine-slice to paint the arrangement they
        # describe: a white face, the bevel outside the outline, and the
        # corner blocks the reference's clean corners show.
        colours = {
            name: hex_colour(self.pixel(x, y))
            for name, (x, y) in self.ANCHORS.items()
        }
        self.assertEqual(colours["shadow"], "#999999")
        self.assertEqual(colours["outline"], "#000000")
        self.assertEqual(colours["face"], "#FFFFFF")
        self.assertEqual(colours["highlight"], "#FFFFFF")
        slices = render_slices(parse_svg(self.SLICE_SVG))
        assert_sunken_outside_field(
            self, slices, self.SLICE_NAME, self.SLICE_SIZE, colours
        )
