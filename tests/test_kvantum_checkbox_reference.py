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

import unittest

from support.aurorae_fixtures import REFERENCE, REFERENCE_ROWS
from support.kde_config import read as read_kde_config
from support.kvantum_config_spec import _resolved
from support.kvantum_fixtures import SVG, KVCONFIG
from support.platinum_palette import hex_colour
from support.reference_image import ReferenceScreenshotMixin
from support.svg_case import parse_svg
from svg_assertions import render_slices

# The Get Info window's "Locked" check box in the shared aboutsystem
# screenshot: a 12x12 raised Platinum square including its 1px outline. The
# path and decode bound come from `aurorae_fixtures`, whose readers decode the
# same screenshot, so the reference cache unfilters it once per run.
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


def _raised_box_colour(x, y, size, outline, highlight, face, shadow):
    """Return the fill of the raised square pixel at (*x*, *y*).

    The outline wins, then the highlight and shadow bands.
    """
    if x in (0, size - 1) or y in (0, size - 1):
        return outline
    if y == 1 or x == 1:
        return highlight
    if y == size - 2 or x == size - 2:
        return shadow
    return face


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
            pixels[(x, y)] = _raised_box_colour(
                x, y, size, outline, highlight, face, shadow
            )
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
    MAX_ROWS = REFERENCE_ROWS

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
        slices = render_slices(parse_svg(SVG))
        self.assertEqual(slices["checkbox-normal"], expected)

    def test_config_draws_the_indicator_at_the_canvas_size(self):
        # The engine renders `PE_IndicatorCheckBox`'s interior art into the
        # rect whose side is the global `%General` `check_size` and consults
        # no section-level size for it: `pixelMetric(PM_IndicatorWidth)` and
        # `PM_IndicatorHeight` return `tspec_.check_size` for checkbox
        # options, whose compiled-in default is 13 (upstream 1.1.4,
        # `styleproject` `PM_IndicatorWidth`/`PE_IndicatorCheckBox` and
        # `themeconfig/specs.h`). At 13 the 14x14 canvas is resampled and
        # its 1px bands blend (`000003`/`212121` edges instead of `#000000`,
        # `FEFEFE` instead of `#FFFFFF`, `949494` instead of `#888888`).
        # The rendered indicator equals this test's derived raised square
        # when `check_size` is the canvas side, so pin the config value to
        # the side re-derived here; the rendered check itself was made in
        # this run's throwaway `kwin_wayland` `kdialog --dontagain` render,
        # not in this suite, which has no Qt engine fake.
        slices = render_slices(parse_svg(SVG))
        side = 1 + max(x for x, _ in slices["checkbox-normal"])
        self.assertEqual(side, SHIPPED_SIZE)
        parser = read_kde_config(KVCONFIG)
        self.assertEqual(_resolved(parser, "%General", "check_size"), str(SHIPPED_SIZE))


if __name__ == "__main__":
    unittest.main()
