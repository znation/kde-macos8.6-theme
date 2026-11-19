"""Validate the GTK 3 Platinum sheet's selection marquee declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT


class TestGtkThemeRubberband(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_rubberband(self):
        selectors = (
            ".rubberband",
            "rubberband",
            ".content-view rubberband",
            ".content-view .rubberband",
            "treeview.view rubberband",
            "flowbox rubberband",
        )
        self.assert_rubberband(selectors)
        self.assertEqual(
            {selector for selector in self.rules if "rubberband" in selector},
            set(selectors),
        )
        # A later .view rule would win the cascade again.
        self.assert_rule_after(
            ".rubberband, rubberband,\n.content-view rubberband,",
            ".view, textview text, list {",
        )


if __name__ == "__main__":
    unittest.main()
