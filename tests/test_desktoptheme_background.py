"""Tests for the desktop theme's widgets/background.svg Platinum menu body."""

from __future__ import annotations

import unittest

from desktoptheme_paths import BACKGROUND_SVG
from nine_slice_case import NineSliceCase
from platinum_palette import BLACK, WHITE
from svg_assertions import (
    assert_face_bevel,
    assert_hint_geometry,
    attribute_values,
    render_slices,
)


class TestBackground(NineSliceCase, unittest.TestCase):
    SVG_PATH = BACKGROUND_SVG

    def test_background_hint_geometry(self):
        # `test_slice_ids_present` pins only the hint ids, so a margin or
        # inset rect with the wrong position or size passes it while KSvg lays
        # the menu body out wrong. Pin every hint: a 3px border around a 10px
        # centre tile on the 16x16 canvas, plus the zero-size inset rects.
        assert_hint_geometry(self, self.tree, [""], 3, 10, {
            "hint-top-inset": ("3", "0", "10", "0"),
            "hint-bottom-inset": ("3", "16", "10", "0"),
            "hint-left-inset": ("0", "3", "0", "10"),
            "hint-right-inset": ("16", "3", "0", "10"),
        })

    def test_background_pixels(self):
        # The body is a flat #FFFFFF face: a 1px #000000 outline on the outer
        # edge of each slice and no bevel. `assert_face_bevel` pins the 10x10
        # centre, the four edge tiles, and the four corners where the outline
        # turns.
        slices = render_slices(self.tree)
        assert_face_bevel(self, slices, "", WHITE, "flat", size=10)

    def test_background_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the
        # artwork palette: the white face and the black outline.
        self.assertEqual(
            attribute_values(self.tree, "fill"), {BLACK, WHITE}
        )


if __name__ == "__main__":
    unittest.main()
