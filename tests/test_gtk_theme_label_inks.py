"""Validate GTK 3 secondary-label ink and opacity declarations."""

from __future__ import annotations

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import DISABLED_TEXT
from support.repo_root import ROOT


class TestGtkThemeLabelInks(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_separator_label_foreground(self):
        selector = "label.separator"
        self.assert_disabled_text((selector,))
        self.assertEqual(
            self.rules[selector],
            {**DISABLED_TEXT, "opacity": "1", "text-shadow": "none"},
        )
        self.assertEqual(self.selectors.count(selector), 1)

    def test_dim_label_foreground(self):
        selector = ".dim-label"
        self.assert_disabled_text((selector,))
        self.assertEqual(
            self.rules[selector],
            {**DISABLED_TEXT, "opacity": "1", "text-shadow": "none"},
        )
        self.assertEqual(self.selectors.count(selector), 1)

    def test_menu_accelerator_foreground(self):
        selector = "menuitem accelerator"
        self.assert_disabled_text((selector,))
        self.assert_rule(selector, {**DISABLED_TEXT})
        # Stock dims the accelerator inside the color declaration alone, so
        # the restatement carries the opacity-free, shadow-free dict whole.
        self.assertEqual(self.rules[selector], {**DISABLED_TEXT})
        self.assertEqual(self.selectors.count(selector), 1)
        # The stock-twin spelling lands after the existing menu-row hover
        # face, the source position that beats the toolkit arm on the tie.
        self.assertGreater(
            self.selectors.index(selector),
            self.selectors.index("menu menuitem:hover"),
        )

    def test_header_subtitle_foreground(self):
        selectors = (".titlebar:not(headerbar) .subtitle", "headerbar .subtitle")
        self.assert_disabled_text(selectors)
        expected = {**DISABLED_TEXT, "opacity": "1", "text-shadow": "none"}
        self.assert_rule_group(dict.fromkeys(selectors, expected))

    def test_emoji_section_label_opacity(self):
        selectors = (
            "button.emoji-section label",
            "button.emoji-section:hover label",
        )
        self.assert_rule_group(dict.fromkeys(selectors, {"opacity": "1"}))
        self.assertEqual(
            {selector for selector in self.rules if "emoji-section" in selector},
            set(selectors),
        )


if __name__ == "__main__":
    unittest.main()
