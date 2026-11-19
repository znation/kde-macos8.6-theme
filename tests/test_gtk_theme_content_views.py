"""Validate GTK 3 content-view declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT


class TestGtkThemeContentViews(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_content_view_background(self):
        selectors = (".content-view", ".content-view:backdrop")
        self.assert_view_background(selectors)
        expected = {"background-color": "#FFFFFF", "color": "#000000"}
        for selector in selectors:
            self.assertEqual(self.rules[selector], expected)
            self.assertEqual(self.selectors.count(selector), 1)

    def test_content_view_hover(self):
        self.assert_rule(".content-view:hover", {"-gtk-icon-effect": "none"})


if __name__ == "__main__":
    unittest.main()
