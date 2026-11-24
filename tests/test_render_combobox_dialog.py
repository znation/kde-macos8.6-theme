"""The ``--combobox-dialog`` gate's rendered pixels and skip guard."""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.platinum_palette import hex_colour
from support.render.gates import DialogGate
from support.render.skip_guards import (
    assert_gate_skips_only_when_a_tool_is_absent,
    dialog_gate_guard,
)
from tools.png import pixel_at


# The rendered combo box indicator: the shipped 12x12 canvas at 1:1, measured
# against `tests/test_kvantum_combobox_reference.py`'s reference cell. The
# combo dialog is the session's only window like the checkbox dialog, so the
# crop is measured on the same 480x360 capture.
COMBOBOX_CROP = (316, 178, 12, 12)
# The rendered combo field: `[ComboBox] frame.element=combofield` draws its
# frame slices from the dedicated raised family, so the field bands are the
# reference's raised arrangement in every state the engine may select.
COMBOBOX_FIELD = (146, 172, 188, 24)
COMBOBOX_OK_BUTTON = (167, 199, 82, 24)
COMBOBOX_CANCEL_BUTTON = (252, 199, 82, 24)


@dialog_gate_guard()
class TestComboboxDialogRender(DialogGate, unittest.TestCase):
    """The engine-drawn combo box indicator the dialog render captures is 1:1.

    The combo render opens a real ``QComboBox`` (kdialog's ``--combobox``)
    drawn by the engine with this theme's ``comboarrow-*`` art through
    ``[ComboBox] indicator.size``, and byte-compares the rendered 12x12 cell
    with the shipped-art slice. The squashed 4px-wide arrow this gate guards
    against was the very render bug the check box cell alone could not see;
    the render pass found the combo arrow while the check box one was fixed,
    so the two gates must hold together.
    """

    KIND = "combobox"

    def test_draws_the_combo_arrow_cell_1_to_1(self):
        self.assert_cell_matches("comboarrow-normal", COMBOBOX_CROP)

    def test_combo_field_keeps_its_engine_drawn_raised_frame(self):
        self.assert_raised_frame(COMBOBOX_FIELD)

    def test_draws_the_combo_field_raised_bevel(self):
        """Pin the Kvantum field frame around the selected combo contents."""
        image = self.candidate_image()
        x, y, width, height = COMBOBOX_FIELD
        expected_top = ["#000000"] * width
        expected_upper = ["#000000", *(["#FFFFFF"] * (width - 3)), "#AAAAAA", "#000000"]
        expected_lower = ["#000000", "#FFFFFF", *(["#AAAAAA"] * (width - 3)), "#000000"]
        expected_bottom = ["#000000"] * width
        for row, expected in ((0, expected_top), (1, expected_upper),
                              (height - 2, expected_lower), (height - 1, expected_bottom)):
            with self.subTest(row=row):
                self.assertEqual(
                    expected,
                    [hex_colour(pixel_at(image, x + dx, y + row)) for dx in range(width)],
                )
        for dy in range(2, height - 2):
            with self.subTest(column="left", row=dy):
                self.assertEqual("#000000", hex_colour(pixel_at(image, x, y + dy)))
            with self.subTest(column="left-highlight", row=dy):
                self.assertEqual("#FFFFFF", hex_colour(pixel_at(image, x + 1, y + dy)))
            with self.subTest(column="right-shadow", row=dy):
                self.assertEqual("#AAAAAA", hex_colour(pixel_at(image, x + width - 2, y + dy)))
            with self.subTest(column="right-edge", row=dy):
                self.assertEqual("#000000", hex_colour(pixel_at(image, x + width - 1, y + dy)))
        for yy in range(y + 2, y + height - 2):
            self.assert_pixel(x + 2, yy, "#DDDDDD")
            self.assert_pixel(x + width - 3, yy, "#DDDDDD")

    def test_ok_and_cancel_buttons_keep_their_engine_drawn_frames(self):
        self.assert_raised_frame(COMBOBOX_OK_BUTTON, flat_rows=(201, 202, 203, 204))
        self.assert_raised_frame(COMBOBOX_CANCEL_BUTTON, flat_rows=(201, 202, 203, 204))


class TestComboboxDialogGateSkipGuards(unittest.TestCase):
    """Pin the combobox gate's tool and software-renderer skip condition."""

    def test_the_combobox_dialog_gate_skips_only_when_a_tool_is_absent(self):
        assert_gate_skips_only_when_a_tool_is_absent(self, TestComboboxDialogRender)


if __name__ == "__main__":
    unittest.main()
