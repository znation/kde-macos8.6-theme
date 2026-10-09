"""Tests for the desktop theme's dialogs/background.svg Platinum window body."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from desktoptheme_paths import DIALOG_BACKGROUND_SVG
from platinum_palette import FACE, PLATINUM_FILLS
from svg_assertions import (
    assert_face_bevel,
    assert_hint_geometry,
    assert_no_script_elements,
    assert_slice_ids_present,
    assert_tiles_placed_by_margins,
    attribute_values,
    render_slices,
)


PREFIXES = ("",)


class TestDialogBackground(unittest.TestCase):
    def test_dialog_slice_ids(self):
        assert_slice_ids_present(self, ET.parse(DIALOG_BACKGROUND_SVG), [""])

    def test_dialog_hint_geometry(self):
        # `test_dialog_slice_ids` pins only the hint ids, so a margin hint with
        # the wrong position or size passes it while KSvg lays the body out
        # wrong. Pin every hint: a 3px border around a 10px centre tile on the
        # 16x16 canvas.
        assert_hint_geometry(
            self, ET.parse(DIALOG_BACKGROUND_SVG), [""], 3, 10
        )

    def test_dialog_tiles_placed_by_margins(self):
        assert_tiles_placed_by_margins(
            self, ET.parse(DIALOG_BACKGROUND_SVG), [""]
        )

    def test_dialog_frame_bevel(self):
        # The body is a raised #DDDDDD face: a 1px #000000 outline with a 1px
        # bevel inside it (#FFFFFF top/left, #999999 bottom/right), the same
        # bevel direction as button.svg's normal state and scrollbar.svg's
        # thumb; `assert_face_bevel` pins the centre tile, the four edge bands
        # and the four corners.
        slices = render_slices(ET.parse(DIALOG_BACKGROUND_SVG))
        assert_face_bevel(self, slices, "", FACE, "raised", size=10)

    def test_dialog_colours(self):
        # The hints use `style`, so the parsed `fill` set is exactly the
        # artwork palette: face, outline, bevel highlight and bevel shadow.
        self.assertEqual(
            attribute_values(ET.parse(DIALOG_BACKGROUND_SVG), "fill"),
            PLATINUM_FILLS,
        )

    def test_no_script_elements(self):
        assert_no_script_elements(self, ET.parse(DIALOG_BACKGROUND_SVG))


if __name__ == "__main__":
    unittest.main()
