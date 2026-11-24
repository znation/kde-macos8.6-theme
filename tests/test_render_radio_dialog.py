"""The radio-list dialog gate's rendered pixels, pinned band by band.

The ``--radiolist-dialog`` mode opens kdialog's fixed radio list; this module
pins its selection face, indicators and sunken list field.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.render.gates import DialogGate
from support.render.skip_guards import (
    assert_gate_skips_only_when_a_tool_is_absent,
    dialog_gate_guard,
)
from support.platinum_palette import hex_colour
from tools.png import pixel_at


# The clear part of the first selected row, away from its radio indicator and
# label glyphs; measured on two byte-identical radio-list captures on
# 2026-11-11.
RADIO_DIALOG_SELECTION_BAND = (200, 97, 164, 16)
# Dark core pixels in the selected radio dot and an unchecked radio ring.
RADIO_DIALOG_CHECKED_DOT = (121, 106)
RADIO_DIALOG_UNCHECKED_RING = (119, 120)
# The sunken list field's top-left outer and inner frame pixels; the viewport
# sample is below the selected row, clear of text and indicator art.
RADIO_DIALOG_FIELD_FRAME = ((112, 93), (113, 94))
RADIO_DIALOG_VIEW_FACE = (200, 140)


@dialog_gate_guard()
class TestRadioDialogRender(DialogGate, unittest.TestCase):
    """The radio-list selection, indicators and sunken field keep their paint."""

    KIND = "radiolist"

    def test_selected_row_keeps_its_flat_selection_face(self):
        image = self.candidate_image()
        x, y, width, height = RADIO_DIALOG_SELECTION_BAND
        for yy in range(y, y + height):
            for xx in range(x, x + width):
                self.assertEqual("#CCCCFF", hex_colour(pixel_at(image, xx, yy)), (xx, yy))

    def test_checked_radio_keeps_its_dark_dot_core(self):
        self.assert_pixel(*RADIO_DIALOG_CHECKED_DOT, "#0C0C0F")

    def test_unchecked_radio_keeps_its_dark_ring_on_white(self):
        self.assert_pixel(*RADIO_DIALOG_UNCHECKED_RING, "#000000")
        self.assert_pixel(117, 120, "#FFFFFF")

    def test_list_field_keeps_its_sunken_frame_and_white_viewport(self):
        outer, inner = RADIO_DIALOG_FIELD_FRAME
        self.assert_pixel(*outer, "#999999")
        self.assert_pixel(*inner, "#000000")
        self.assert_pixel(*RADIO_DIALOG_VIEW_FACE, "#FFFFFF")


class TestRadioDialogGateSkipGuards(unittest.TestCase):
    """The radio gate skips only when a required tool is absent."""

    def test_the_radio_dialog_gate_skips_only_when_a_tool_is_absent(self):
        assert_gate_skips_only_when_a_tool_is_absent(self, TestRadioDialogRender)


if __name__ == "__main__":
    unittest.main()
