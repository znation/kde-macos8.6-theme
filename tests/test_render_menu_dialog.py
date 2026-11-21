"""The menu dialog's item-view gate and its isolated skip guard."""

from __future__ import annotations

import shutil
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.render.gates import (
    DIALOG_REAL_TOOLS,
    DialogGate,
    dialog_gate_guard,
    probe_gate_skip,
    software_renderer_skip_reason,
)
from tools.png import pixel_at  # noqa: E402
from support.platinum_palette import hex_colour


# The rendered menu's item view at the measured 480x360 capture geometry.
MENU_ITEM_VIEW = (112, 93, 256, 182)


@dialog_gate_guard()
class TestMenuDialogRender(DialogGate, unittest.TestCase):
    """The menu dialog's item view keeps its engine-drawn sunken frame."""

    KIND = "menu"

    def test_item_view_frame_matches_its_measured_border_runs(self):
        x, y, width, height = MENU_ITEM_VIEW
        for xx in range(x, x + width - 1):
            self.assert_pixel(xx, y, "#999999")
        for xx in range(x + 1, x + width):
            self.assert_pixel(xx, y + height - 1, "#FFFFFF")
        for xx in range(x + 1, x + width - 1):
            self.assert_pixel(xx, y + height - 2, "#000000")
        for yy in range(y, y + height - 1):
            self.assert_pixel(x, yy, "#999999")
        for yy in range(y + 1, y + height - 1):
            self.assert_pixel(x + 1, yy, "#000000")
            self.assert_pixel(x + width - 2, yy, "#000000")
            self.assert_pixel(x + width - 1, yy, "#FFFFFF")
        self.assert_pixel(x + width - 1, y, "#DDDDDD")
        self.assert_pixel(x, y + height - 1, "#DDDDDD")
        for yy in range(y + 2, y + height - 2):
            self.assert_pixel(x + 2, yy, "#FFFFFF")
            self.assert_pixel(x + width - 3, yy, "#FFFFFF")
        for xx in range(x + 2, x + width - 2):
            self.assert_pixel(xx, y + 2, "#FFFFFF")

    def test_current_item_focus_ring_is_pinned_inside_the_field(self):
        for xx in range(115, 365):
            self.assert_pixel(xx, 96, "#000000")
            self.assert_pixel(xx, 113, "#000000")
        for yy in range(96, 114):
            self.assert_pixel(115, yy, "#000000")
            self.assert_pixel(364, yy, "#000000")

    def test_draws_the_item_view_frame_and_white_interior(self):
        image = self.candidate_image()
        x0, y0, width, height = MENU_ITEM_VIEW
        self.assertEqual("#999999", hex_colour(pixel_at(image, x0, y0)))
        for x in range(x0, x0 + width - 1):
            with self.subTest(edge="top", x=x):
                self.assertEqual("#999999", hex_colour(pixel_at(image, x, y0)))
        for x in range(x0 + 1, x0 + width - 1):
            with self.subTest(edge="bottom", x=x):
                self.assertEqual("#000000", hex_colour(pixel_at(image, x, y0 + height - 2)))
        self.assertEqual("#999999", hex_colour(pixel_at(image, x0, y0 + height - 2)))
        self.assertEqual("#FFFFFF", hex_colour(pixel_at(image, x0 + width - 1, y0 + height - 2)))
        for y in range(y0 + 1, y0 + height - 1):
            with self.subTest(edge="left", y=y):
                self.assertEqual("#999999", hex_colour(pixel_at(image, x0, y)))
            with self.subTest(edge="right", y=y):
                self.assertEqual("#FFFFFF", hex_colour(pixel_at(image, x0 + width - 1, y)))
        self.assertEqual("#DDDDDD", hex_colour(pixel_at(image, x0 + width - 1, y0)))
        self.assertEqual("#DDDDDD", hex_colour(pixel_at(image, x0, y0 + height - 1)))
        for x in range(x0 + 1, x0 + width):
            with self.subTest(edge="lower-white", x=x):
                self.assertEqual("#FFFFFF", hex_colour(pixel_at(image, x, y0 + height - 1)))
        for point in ((114, 120), (200, 120), (365, 272)):
            with self.subTest(point=point):
                self.assertEqual("#FFFFFF", hex_colour(pixel_at(image, *point)))


class TestMenuDialogGateSkipGuards(unittest.TestCase):
    """Pin this gate's real skip flag and its shared missing-tool guard."""

    def test_the_menu_dialog_gate_skips_only_when_a_tool_is_absent(self):
        expected = software_renderer_skip_reason() is not None or not all(
            shutil.which(tool) for tool in DIALOG_REAL_TOOLS
        )
        self.assertEqual(expected, TestMenuDialogRender.__unittest_skip__)
        for missing in (None, *DIALOG_REAL_TOOLS):
            with self.subTest(missing=missing):
                self.assertEqual(
                    missing is not None,
                    probe_gate_skip(dialog_gate_guard, missing),
                )


if __name__ == "__main__":
    unittest.main()
