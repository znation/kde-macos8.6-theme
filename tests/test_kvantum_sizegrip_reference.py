"""Ground the Kvantum size grip in the reference's window grow box.

No reference screenshot shows a KDE/Qt size grip, so the `.kvconfig` section
and its key name are Kvantum-required and the element id is a chosen value;
the shipped art adapts the grow box in the retail Japanese 8.6 System
Profiler window (`systemprofiler_betawiki.png`). This test re-derives that
12x11 region --
mostly the window-frame `#CCCCCC`, with the white/`#777777` checker diamond
and its three `#AAAAAA` lower-left edge pixels -- and requires both shipped
size-grip states to paint exactly those non-background pixels. It skips when
the image is not materialized.
"""

from __future__ import annotations

from collections import Counter
import unittest

from support.aurorae_fixtures import PROFILER_REFERENCE
from support.kvantum_fixtures import SVG
from support.platinum_palette import (
    BUTTON_SHADOW,
    SIZEGRIP_DARK,
    WHITE,
    hex_colour,
)
from support.reference_image import ReferenceScreenshotMixin
from support.svg_case import parse_svg
from svg_assertions import pixel_map, render_slices

# The grow box occupies x=796..807, y=748..758 on the window frame. The
# reference rows are the region's six-digit colours, left to right, top to
# bottom, so the test pins the whole sampled pattern rather than one corner.
X0 = 796
Y0 = 748
WIDTH = 12
HEIGHT = 11
BACKGROUND = "#CCCCCC"
REFERENCE_ROWS = (
    "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCFFFFFFFFFFFFCCCCCCCCCCCCCCCCCCCCCCCC",
    "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCFFFFFFCCCCCC777777CCCCCCCCCCCCCCCCCCCCCCCC",
    "CCCCCCCCCCCCCCCCCCCCCCCCFFFFFFCCCCCC777777CCCCCCFFFFFFFFFFFFCCCCCCCCCCCC",
    "CCCCCCCCCCCCCCCCCCFFFFFFCCCCCC777777CCCCCCFFFFFFCCCCCC777777CCCCCCCCCCCC",
    "CCCCCCCCCCCCFFFFFFCCCCCC777777CCCCCCFFFFFFCCCCCC777777CCCCCCFFFFFFFFFFFF",
    "CCCCCCFFFFFFCCCCCC777777CCCCCCFFFFFFCCCCCC777777CCCCCCFFFFFFCCCCCC777777",
    "CCCCCCAAAAAA777777CCCCCCFFFFFFCCCCCC777777CCCCCCFFFFFFCCCCCC777777CCCCCC",
    "CCCCCCCCCCCCCCCCCCFFFFFFCCCCCC777777CCCCCCFFFFFFCCCCCC777777CCCCCCCCCCCC",
    "CCCCCCCCCCCCCCCCCCAAAAAA777777CCCCCCFFFFFFCCCCCC777777CCCCCCCCCCCCCCCCCC",
    "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCFFFFFFCCCCCC777777CCCCCCCCCCCCCCCCCCCCCCCC",
    "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCAAAAAA777777CCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
)


def _expected_map():
    """Return the pinned reference rows as a {(x, y): colour} map."""
    colours = [
        "#" + row[offset : offset + 6]
        for row in REFERENCE_ROWS
        for offset in range(0, len(row), 6)
    ]
    return pixel_map(colours, WIDTH, HEIGHT)


class TestSizeGripReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The size grip paints the reference window's grow box."""

    REFERENCE = PROFILER_REFERENCE
    # The grow box sits below the tab-row bound other profiler readers use.
    MAX_ROWS = 760

    def _sampled_map(self):
        return {
            (x, y): hex_colour(self.pixel(X0 + x, Y0 + y))
            for y in range(HEIGHT)
            for x in range(WIDTH)
        }

    def test_reference_grow_box_pattern(self):
        sampled = self._sampled_map()
        self.assertEqual(sampled, _expected_map())
        self.assertEqual(
            Counter(sampled.values()),
            {
                BACKGROUND: 90,
                WHITE: 21,
                SIZEGRIP_DARK: 18,
                BUTTON_SHADOW: 3,
            },
        )
        # The three #AAAAAA pixels along the diamond's lower-left edge.
        self.assertEqual(sampled[(1, 6)], BUTTON_SHADOW)
        self.assertEqual(sampled[(3, 8)], BUTTON_SHADOW)
        self.assertEqual(sampled[(5, 10)], BUTTON_SHADOW)
        self.assertEqual(sampled[(0, 0)], BACKGROUND)

    def test_shipped_size_grip_paints_the_reference_pattern(self):
        slices = render_slices(parse_svg(SVG))
        sampled = self._sampled_map()
        for element in ("sizegrip-normal", "sizegrip-focused"):
            with self.subTest(element=element):
                self.assertIn(element, slices)
                composed = {
                    (x, y): BACKGROUND
                    for y in range(HEIGHT)
                    for x in range(WIDTH)
                }
                # The groups' invisible bounds rect paints no pixel; compose
                # only the coloured 1x1 rects onto the sampled background.
                composed.update(
                    {
                        point: fill
                        for point, fill in slices[element].items()
                        if fill != "none"
                    }
                )
                self.assertEqual(composed, sampled)


if __name__ == "__main__":
    unittest.main()
