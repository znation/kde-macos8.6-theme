"""Tests for the desktop theme's dialogs/background.svg Platinum window body."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from desktoptheme_paths import DIALOG_BACKGROUND_SVG
from svg_assertions import (
    assert_center_tile_is,
    assert_corner_pixels,
    assert_edge_band_pixels,
    assert_no_script_elements,
    assert_slice_ids_present,
    assert_tiles_placed_by_margins,
    attribute_values,
    nine_slice_hint_geometry,
    rect_geometry,
    render_slices,
)


PREFIXES = ("",)

BLACK = "#000000"
WHITE = "#FFFFFF"
GREY = "#999999"
FACE = "#DDDDDD"


class TestDialogBackground(unittest.TestCase):
    def test_dialog_slice_ids(self):
        assert_slice_ids_present(self, ET.parse(DIALOG_BACKGROUND_SVG), [""])

    def test_dialog_hint_geometry(self):
        # `test_dialog_slice_ids` pins only the hint ids, so a margin hint with
        # the wrong position or size passes it while KSvg lays the body out
        # wrong. Pin every hint: a 3px border around a 10px centre tile on the
        # 16x16 canvas.
        self.assertEqual(
            rect_geometry(ET.parse(DIALOG_BACKGROUND_SVG)),
            nine_slice_hint_geometry([""], 3, 10),
        )

    def test_dialog_tiles_placed_by_margins(self):
        assert_tiles_placed_by_margins(
            self, ET.parse(DIALOG_BACKGROUND_SVG), [""]
        )

    def test_dialog_frame_bevel(self):
        # The body is a raised #DDDDDD face: a 1px #000000 outline with a 1px
        # bevel inside it (#FFFFFF top/left, #999999 bottom/right), the same
        # rule as button.svg's normal state and scrollbar.svg's thumb. The
        # bottom/right bands are the mirrored top/left ones.
        slices = render_slices(ET.parse(DIALOG_BACKGROUND_SVG))
        assert_center_tile_is(self, slices, "center", FACE, size=10)
        outward = (BLACK, WHITE, FACE)
        mirrored = (FACE, GREY, BLACK)
        for side in ("top", "bottom", "left", "right"):
            band = outward if side in ("top", "left") else mirrored
            assert_edge_band_pixels(self, slices, side, side, band, size=10)
        assert_corner_pixels(
            self, slices, "topleft",
            (BLACK, BLACK, BLACK, BLACK, WHITE, WHITE, BLACK, WHITE, FACE),
        )
        assert_corner_pixels(
            self, slices, "topright",
            (BLACK, BLACK, BLACK, WHITE, GREY, BLACK, FACE, GREY, BLACK),
        )
        assert_corner_pixels(
            self, slices, "bottomleft",
            (BLACK, WHITE, FACE, BLACK, WHITE, GREY, BLACK, BLACK, BLACK),
        )
        assert_corner_pixels(
            self, slices, "bottomright",
            (FACE, GREY, BLACK, GREY, GREY, BLACK, BLACK, BLACK, BLACK),
        )

    def test_dialog_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the
        # artwork palette: face, outline, bevel highlight and bevel shadow.
        self.assertEqual(
            attribute_values(ET.parse(DIALOG_BACKGROUND_SVG), "fill"),
            {BLACK, WHITE, GREY, FACE},
        )

    def test_no_script_elements(self):
        assert_no_script_elements(self, ET.parse(DIALOG_BACKGROUND_SVG))


if __name__ == "__main__":
    unittest.main()
