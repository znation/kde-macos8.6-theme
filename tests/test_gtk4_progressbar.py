"""GTK 4 progressbar declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import PROGRESSBAR_TROUGH
from support.platinum_palette import BLACK, GREY, TROUGH


class TestGtk4Progressbar(Gtk4SheetRuleCases, unittest.TestCase):
    def test_progressbar(self):
        self.assert_progressbar(
            trough="progressbar > trough",
            progress="progressbar > trough > progress",
            disabled="progressbar > trough > progress:disabled",
        )

    def test_progressbar_label_ink(self):
        """A meter's show-text percentage label keeps the existing window ink."""
        self.assert_rule_group({"progressbar": {"color": BLACK}})
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("progressbar")
                and ">" not in s
                and "." not in s
            },
            {"progressbar", "progressbar:disabled"},
        )
        self.assert_rule_after("progressbar > trough {", "progressbar {")

    def test_progressbar_osd_trough_paint(self):
        selector = "progressbar.osd > trough"
        expected = {
            "background-color": TROUGH,
            "border": f"1px solid {BLACK}",
            "box-shadow": f"inset 1px 1px {GREY}",
        }
        self.assert_rule(selector, expected)
        self.assertEqual(self.rules[selector], expected)
        base = self.rules["progressbar > trough"]
        self.assertEqual(
            {name: self.rules[selector][name] for name in expected},
            {name: base[name] for name in expected},
        )

    def test_progressbar_osd_trough_thickness(self):
        horizontal = "progressbar.osd.horizontal > trough"
        vertical = "progressbar.osd.vertical > trough"
        expected = {
            horizontal: {"min-height": self.rules["progressbar > trough"]["min-height"]},
            vertical: {"min-width": self.rules["progressbar > trough"]["min-width"]},
        }
        self.assertEqual(expected[horizontal]["min-height"], PROGRESSBAR_TROUGH["min-height"])
        self.assertEqual(expected[vertical]["min-width"], PROGRESSBAR_TROUGH["min-width"])
        self.assert_rule_group(expected)

    def test_progressbar_oriented_trough_thickness(self):
        horizontal = "progressbar.horizontal > trough"
        vertical = "progressbar.vertical > trough"
        expected = {
            horizontal: {"min-height": self.rules["progressbar > trough"]["min-height"]},
            vertical: {"min-width": self.rules["progressbar > trough"]["min-width"]},
        }
        self.assertEqual(expected[horizontal]["min-height"], PROGRESSBAR_TROUGH["min-height"])
        self.assertEqual(expected[vertical]["min-width"], PROGRESSBAR_TROUGH["min-width"])
        self.assert_rule_group(expected)

    def test_progressbar_directional_corners(self):
        self.assert_rule("progressbar > trough > progress", {"border-radius": "0"})
        for direction in ("left", "right", "top", "bottom"):
            with self.subTest(direction=direction):
                selector = f"progressbar > trough > progress.{direction}"
                self.assert_rule(
                    selector,
                    {"border-radius": "0"},
                )
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                self.assertEqual(
                    self.rules[selector]["border-radius"],
                    self.rules["progressbar > trough > progress"]["border-radius"],
                )

    def test_progressbar_disabled_filter(self):
        self.assertEqual(self.rules["progressbar:disabled"], {"filter": "none"})
        self.assertEqual(
            self.rules["progressbar > trough > progress:disabled"],
            {"background-color": GREY},
        )


if __name__ == "__main__":
    unittest.main()
