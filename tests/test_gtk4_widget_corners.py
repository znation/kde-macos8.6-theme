"""GTK 4 assistant, pill, circular, video-OSD and tab-thumbnail corner checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases


class TestGtk4WidgetCorners(Gtk4SheetRuleCases, unittest.TestCase):
    def test_assistant_step_label_corners(self):
        expected = {"window.assistant .sidebar > label"}
        self.assertEqual(
            {selector for selector in self.rules if "assistant" in selector},
            expected,
        )
        self.assert_square_corner("window.assistant .sidebar > label")

    def test_pill_button_corners(self):
        expected = {
            "menubutton.pill > button",
            "button.pill",
            "menubutton.suggested-action.pill",
            "menubutton.opaque.pill",
        }
        self.assertEqual(
            {selector for selector in self.rules if ".pill" in selector},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                for reference in ("button", "frame > border", ".frame"):
                    self.assertEqual(
                        self.rules[selector]["border-radius"],
                        self.rules[reference]["border-radius"],
                    )

    def test_circular_button_corners(self):
        # The existing circular record squares the two children the toolkit
        # arms name; the 2026-11-04 container entry adds the two .circular
        # container members stock groups with the pill pair, so the
        # .circular sweep covers all four spellings.
        expected = {
            "menubutton.circular button",
            "button.circular",
            "menubutton.suggested-action.circular",
            "menubutton.opaque.circular",
        }
        self.assertEqual(
            {selector for selector in self.rules if ".circular" in selector},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, {"border-radius": "0"})
                for reference in ("button", "frame > border", ".frame"):
                    self.assertEqual(
                        self.rules[selector]["border-radius"],
                        self.rules[reference]["border-radius"],
                    )

    def test_video_osd_image_corners(self):
        self.assertEqual(
            {selector for selector in self.rules if "video" in selector},
            {"video image.osd"},
        )
        video_image = self.rules["video image.osd"]
        self.assertEqual(video_image, {"border-radius": "0"})
        for selector in ("frame > border", ".frame"):
            with self.subTest(selector=selector):
                self.assertEqual(
                    video_image["border-radius"],
                    self.rules[selector]["border-radius"],
                )

    def test_tab_thumbnail_corners(self):
        # The 2026-11-04 tab-family corner row adds three stock-spelling
        # tab-overview members beside the existing tab-preview shell spellings.
        expected = {
            "tabthumbnail",
            "tabthumbnail .card picture",
            "tabthumbnail button",
            "tabthumbnail button > image",
            "tabthumbnail .needs-attention > widget",
        }
        self.assertEqual(
            {selector for selector in self.rules if "tabthumbnail" in selector},
            expected,
        )
        for selector in expected:
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_matches_frame(selector, "border-radius")

if __name__ == "__main__":
    unittest.main()
