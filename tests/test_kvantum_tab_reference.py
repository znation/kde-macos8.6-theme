"""Ground the Kvantum tab face in the reference's System Profiler tabs.

`TestSvg` pins the tab state ids to the Platinum palette and
`TestSurfaceBevelPixels` pins their painted arrangement, but no test ties that
palette to a screenshot. The retail Japanese 8.6 System Profiler window
(`systemprofiler_betawiki.png`) shows two Platinum tab palettes: an unselected
tab is a #CCCCCC face with a #DDDDDD highlight, and the selected tab an
#EEEEEE face with a #FFFFFF highlight, both inside a #000000 outline. This test
re-derives both palettes from the image and asserts the shipped `tab-normal`,
`tab-focused` and `tab-toggled` centre tiles and raised top/left bands paint
them. It skips when the image is not materialized.

The reference tab's top edge is three bands -- the #000000 outline, a #CCCCCC
mid-tone and then the highlight -- because its highlight is inset one pixel;
the shipped two-band bevel skips the mid-tone (recorded deviation in
PLANS-DONE.md).
"""

from __future__ import annotations

import unittest

from support.aurorae_fixtures import PROFILER_REFERENCE, PROFILER_ROWS
from support.kvantum_fixtures import SVG
from support.platinum_palette import hex_colour
from support.reference_image import ReferenceScreenshotMixin
from support.svg_case import parse_svg
from svg_assertions import edge_map, pixel_map, render_slices

TAB_SIZE = 30

# The System Profiler window's tab row runs y=54..70. The first tab
# "システム情報" (selected) is at x=260; the second "環境とボリューム"
# (unselected) at x=450. One pixel per colour: the top outline, the #CCCCCC
# mid-tone, the highlight, the face and the bottom edge. The selected tab's
# bottom edge is open (#EEEEEE, no outline); the unselected one closes with a
# #000000 outline at y=70.
UNSELECTED_X = 450
SELECTED_X = 260
UNSELECTED_ANCHORS = {
    "outline": (UNSELECTED_X, 54),
    "midtone": (UNSELECTED_X, 55),
    "highlight": (UNSELECTED_X, 56),
    "face": (UNSELECTED_X, 58),
    "bottom_outline": (UNSELECTED_X, 70),
}
SELECTED_ANCHORS = {
    "outline": (SELECTED_X, 54),
    "midtone": (SELECTED_X, 55),
    "highlight": (SELECTED_X, 56),
    "face": (SELECTED_X, 57),
    "open_bottom": (SELECTED_X, 72),
}


class TestTabReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The tab palette is the reference System Profiler tabs'.

    `TestSvg` and `TestSurfaceBevelPixels` pin the shipped art to the palette,
    so a tab that keeps the button's #DDDDDD face and #FFFFFF highlight passes
    them. This derives the unselected and selected palettes from the
    screenshot and requires the shipped tab slices to paint them.
    """

    REFERENCE = PROFILER_REFERENCE
    MAX_ROWS = PROFILER_ROWS

    def test_unselected_tab_is_the_cccccc_palette(self):
        # Re-derive the unselected tab's five pixels: a #000000 outline, a
        # #CCCCCC mid-tone, a #DDDDDD highlight, a #CCCCCC face and a #000000
        # bottom outline.
        expected = {
            "outline": "#000000",
            "midtone": "#CCCCCC",
            "highlight": "#DDDDDD",
            "face": "#CCCCCC",
            "bottom_outline": "#000000",
        }
        for name, (x, y) in UNSELECTED_ANCHORS.items():
            self.assertEqual(
                hex_colour(self.pixel(x, y)), expected[name], (name, x, y)
            )

    def test_selected_tab_is_the_eeeeee_palette(self):
        # The selected tab swaps the face to #EEEEEE and the highlight to
        # #FFFFFF, and its bottom edge is open (#EEEEEE, no outline).
        expected = {
            "outline": "#000000",
            "midtone": "#CCCCCC",
            "highlight": "#FFFFFF",
            "face": "#EEEEEE",
            "open_bottom": "#EEEEEE",
        }
        for name, (x, y) in SELECTED_ANCHORS.items():
            self.assertEqual(
                hex_colour(self.pixel(x, y)), expected[name], (name, x, y)
            )

    def test_shipped_tabs_paint_the_reference_palette(self):
        # Derive the face, highlight and outline from one reference pixel each,
        # then require the shipped tab slices to paint them: a tab left
        # #DDDDDD (the old face) or with a #FFFFFF unselected highlight fails
        # the centre or band comparison.
        unselected_face = hex_colour(self.pixel(*UNSELECTED_ANCHORS["face"]))
        unselected_highlight = hex_colour(
            self.pixel(*UNSELECTED_ANCHORS["highlight"])
        )
        selected_face = hex_colour(self.pixel(*SELECTED_ANCHORS["face"]))
        selected_highlight = hex_colour(
            self.pixel(*SELECTED_ANCHORS["highlight"])
        )
        outline = hex_colour(self.pixel(*UNSELECTED_ANCHORS["outline"]))
        self.assertEqual(unselected_face, "#CCCCCC")
        self.assertEqual(unselected_highlight, "#DDDDDD")
        self.assertEqual(selected_face, "#EEEEEE")
        self.assertEqual(selected_highlight, "#FFFFFF")
        self.assertEqual(outline, "#000000")
        slices = render_slices(parse_svg(SVG))
        for prefix, face, highlight in (
            ("tab-normal", unselected_face, unselected_highlight),
            ("tab-focused", unselected_face, unselected_highlight),
            ("tab-toggled", selected_face, selected_highlight),
        ):
            with self.subTest(state=prefix):
                self.assertEqual(
                    slices[prefix],
                    pixel_map(
                        (face,) * (TAB_SIZE * TAB_SIZE), TAB_SIZE, TAB_SIZE
                    ),
                )
                self.assertEqual(
                    slices[f"{prefix}-top"],
                    edge_map(TAB_SIZE, "top", outline, highlight),
                )
                self.assertEqual(
                    slices[f"{prefix}-left"],
                    edge_map(TAB_SIZE, "left", outline, highlight),
                )


if __name__ == "__main__":
    unittest.main()
