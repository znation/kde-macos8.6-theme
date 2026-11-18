"""The ``--lineedit-dialog`` gate's rendered field and button pixels."""

from __future__ import annotations

import shutil
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.firstboot_lineedit import FIELD_BORDER_RUNS, FIELD_CORNER_PIXELS
from support.render_gates import (
    DIALOG_REAL_TOOLS,
    DialogGate,
    dialog_gate_guard,
    probe_gate_skip,
    software_renderer_skip_reason,
)
from support.platinum_palette import hex_colour
from tools.png import pixel_at


# The rendered line edit occupies (146,172)..(333,195), measured on two
# consecutive 480x360 captures on 2026-11-10 that agreed byte for byte under
# cmp; a third run in that batch reproduced them byte for byte.
LINEEDIT_DIALOG_FIELD = (146, 172, 188, 24)
# The caret blinks at x=154 in rows 176..191; this band starts at x=200.
LINEEDIT_DIALOG_FIELD_CROP = (200, 172, 120, 24)
# The OK button was measured on the same agreeing capture pair.
LINEEDIT_DIALOG_OK_BUTTON = (167, 199, 82, 24)


@dialog_gate_guard()
class TestLineInputDialogRender(DialogGate, unittest.TestCase):
    """Pin the rendered input field against its reference-derived roles."""

    KIND = "lineedit"

    def test_draws_the_field_sunken_bevel(self):
        width, height = LINEEDIT_DIALOG_FIELD_CROP[2:]
        self.assert_band(
            LINEEDIT_DIALOG_FIELD_CROP,
            (
                ["#999999"] * width,
                ["#000000"] * width,
                *( ["#FFFFFF"] * width for _ in range(height - 4) ),
                ["#000000"] * width,
                ["#FFFFFF"] * width,
            ),
        )

    def test_field_lands_keep_the_reference_corner_arrangement(self):
        image = self.candidate_image()
        x0, y0, width, height = LINEEDIT_DIALOG_FIELD
        ref_x0 = min(rx for (rx, _), _ in FIELD_BORDER_RUNS)
        ref_x1 = max(rx for (rx, _), _ in FIELD_BORDER_RUNS)
        ref_y0 = min(ry for (_, ry), _ in FIELD_BORDER_RUNS)
        ref_y1 = max(ry for (_, ry), _ in FIELD_BORDER_RUNS)

        def position(rx, ry):
            dx = rx - ref_x0 if rx <= ref_x0 + 1 else width - 2 + (rx - ref_x1 + 1)
            dy = ry - ref_y0 if ry <= ref_y0 + 1 else height - 2 + (ry - ref_y1 + 1)
            return x0 + dx, y0 + dy

        expected = {
            position(rx, ry): ("#DDDDDD" if colour == "#CCCCCC" else colour)
            for (rx, ry), colour in FIELD_CORNER_PIXELS
        }
        for yy in range(y0 + 2, y0 + height - 2):
            expected[x0, yy], expected[x0 + 1, yy] = "#999999", "#000000"
            expected[x0 + width - 3, yy] = "#FFFFFF"
            expected[x0 + width - 2, yy] = "#000000"
            expected[x0 + width - 1, yy] = "#FFFFFF"
        for xx in range(x0 + 2, x0 + width - 1):
            expected[xx, y0] = "#999999"
            expected[xx, y0 + 1] = "#000000"
            expected[xx, y0 + height - 2] = "#000000"
            expected[xx, y0 + height - 1] = "#FFFFFF"
        self.assertEqual(
            expected,
            {(xx, yy): hex_colour(pixel_at(image, xx, yy)) for xx, yy in sorted(expected)},
        )

    def test_ok_button_keeps_its_engine_drawn_frame(self):
        self.assert_raised_frame(LINEEDIT_DIALOG_OK_BUTTON, flat_rows=(201, 202, 203, 204))

    def test_draws_the_ok_button_face_at_the_existing_recipe(self):
        image = self.candidate_image()
        x, y, width, _height = LINEEDIT_DIALOG_OK_BUTTON
        self.assertEqual(
            ["#DDDDDD"] * (width - 4),
            [hex_colour(pixel_at(image, x + 2 + dx, y + 2)) for dx in range(width - 4)],
        )


class TestLineInputDialogGateSkipGuards(unittest.TestCase):
    """Pin the line-input gate's real skip flag without capturing a window."""

    def test_the_line_input_gate_skips_only_when_a_tool_is_absent(self):
        expected = software_renderer_skip_reason() is not None or not all(
            shutil.which(tool) for tool in DIALOG_REAL_TOOLS
        )
        self.assertEqual(expected, TestLineInputDialogRender.__unittest_skip__)
        for missing in (None, *DIALOG_REAL_TOOLS):
            with self.subTest(missing=missing):
                self.assertEqual(missing is not None, probe_gate_skip(dialog_gate_guard, missing))


if __name__ == "__main__":
    unittest.main()
