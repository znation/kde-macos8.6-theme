"""Validate GTK 3 expander and disclosure-arrow declarations."""

from __future__ import annotations

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT


class TestGtkThemeExpander(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_expander_arrows(self):
        self.assert_expander_arrows(
            ("treeview.view.expander", "expander title > arrow"),
            ("treeview.view.expander:checked", "expander title > arrow:checked"),
        )

    def test_rtl_collapsed_expander_arrows(self):
        selectors = (
            "treeview.view.expander:not(:checked):dir(rtl)",
            "expander title > arrow:not(:checked):dir(rtl)",
        )
        self.assertEqual(
            {selector: self.rules[selector] for selector in selectors},
            {selector: {"-gtk-icon-transform": "scaleX(-1)"} for selector in selectors},
        )
        for selector in selectors:
            self.assertEqual(self.selectors.count(selector), 1)
        self.assert_expander_arrows(
            ("treeview.view.expander", "expander title > arrow"),
            ("treeview.view.expander:checked", "expander title > arrow:checked"),
        )

    def test_expander_title_focus_outline(self):
        self.assert_dotted_focus_outline("expander > title:focus")


if __name__ == "__main__":
    unittest.main()
