"""Validate GTK 3 list, tree, icon and flow-box focus declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT


class TestGtkThemeViewFocus(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_list_row_focus_outline(self):
        self.assert_dotted_focus_outline("list row:focus")

    def test_treeview_focus_outline(self):
        self.assert_dotted_focus_outline("treeview.view:focus")

    def test_iconview_focus_outline(self):
        self.assert_dotted_focus_outline("iconview:focus")

    def test_flowbox_child_focus_outline(self):
        self.assert_dotted_focus_outline("flowbox > flowboxchild:focus")


if __name__ == "__main__":
    unittest.main()
