"""Validate GTK 3 Platinum treeview progress-cell declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.platinum_palette import BLACK, GREY, SELECTION, TROUGH, WHITE
from support.repo_root import ROOT


class TestGtkThemeTreeviewProgress(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_treeview_progress_bar(self):
        """A treeview row's progress cell restates the existing meter recipe."""
        plain_fill = {
            "color": BLACK,
            "background-color": SELECTION,
            "background-image": "none",
            "box-shadow": "none",
        }
        selected_fill = {
            "color": BLACK,
            "background-color": WHITE,
            "background-image": "none",
        }
        backdrop_fill = {
            "color": BLACK,
            "background-image": "none",
            "box-shadow": "none",
        }
        plain_trough = {
            "background-color": TROUGH,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": f"inset 1px 1px {GREY}",
        }
        self.assert_rule("treeview.view.progressbar", plain_fill)
        for selector in (
            "treeview.view.progressbar:selected:focus",
            "treeview.view.progressbar:selected",
            "treeview.view.progressbar:selected:focus:backdrop",
            "treeview.view.progressbar:selected:backdrop",
        ):
            self.assert_rule(selector, selected_fill)
        self.assert_rule("treeview.view.progressbar:backdrop", backdrop_fill)
        self.assert_rule("treeview.view.trough", plain_trough)
        for selector in (
            "treeview.view.trough:selected:focus",
            "treeview.view.trough:selected",
        ):
            self.assert_rule(selector, {"background-color": TROUGH})
        selectors = (
            "treeview.view.progressbar",
            "treeview.view.progressbar:selected:focus",
            "treeview.view.progressbar:selected",
            "treeview.view.progressbar:selected:focus:backdrop",
            "treeview.view.progressbar:selected:backdrop",
            "treeview.view.progressbar:backdrop",
            "treeview.view.trough",
            "treeview.view.trough:selected:focus",
            "treeview.view.trough:selected",
        )
        for selector in selectors:
            self.assertEqual(self.selectors.count(selector), 1, selector)
        self.assertNotIn("min-height", self.rules["treeview.view.trough"])
        self.assertNotIn("min-width", self.rules["treeview.view.trough"])
        self.assertEqual(
            {
                s
                for s in self.rules
                if "treeview.view.progressbar" in s or "treeview.view.trough" in s
            },
            set(selectors),
        )
        self.assertLess(
            self.selectors.index("entry progress"),
            self.selectors.index("treeview.view.progressbar"),
        )
        self.assertLess(
            self.selectors.index("treeview.view.trough"),
            self.selectors.index("levelbar trough"),
        )


if __name__ == "__main__":
    unittest.main()
