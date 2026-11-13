"""GTK 4 switch declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.platinum_palette import WHITE


class TestGtk4Switch(Gtk4SheetRuleCases, unittest.TestCase):
    def test_switch(self):
        self.assert_switch(
            slider="switch > slider",
            disabled_slider="switch:disabled > slider",
            glyph="switch > image",
        )

    def test_switch_osd_checked_track_color(self):
        selector = ".osd switch:checked"
        self.assert_rule(selector, {"background-color": WHITE})
        self.assertEqual(
            self.rules[selector]["background-color"],
            self.rules["switch:checked"]["background-color"],
        )

    def test_switch_track_transition(self):
        self.assert_rule("switch", {"transition": "none"})

    def test_switch_focus_outline_color(self):
        self.assert_scale_focus_outline("switch:focus:focus-visible")

    def test_switch_interaction_track_faces(self):
        for selector in ("switch:hover", "switch:active"):
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {"background-color": "#EEEEEE", "background-image": "none"},
                )
        for selector in ("switch:checked:hover", "switch:checked:active"):
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {"background-color": "#FFFFFF", "background-image": "none"},
                )

    def test_switch_checked_thumb_face(self):
        self.assert_rule(
            "switch:checked > slider", {"background-color": "#DDDDDD"}
        )

    def test_switch_interaction_thumb_face(self):
        for selector in ("switch:hover > slider", "switch:active > slider"):
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"background-color": "#DDDDDD"})

    def test_switch_disabled_filter(self):
        self.assert_rule("switch:disabled", {"filter": "none"})

    def test_switch_track_padding(self):
        self.assert_rule("switch", {"padding": "0"})
if __name__ == "__main__":
    unittest.main()
