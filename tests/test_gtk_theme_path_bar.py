"""Validate the GTK 3 Platinum file-chooser path-bar declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT


class TestGtkThemePathBar(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_path_bar_tabs(self):
        forms = {
            "base": (".path-bar > button",),
            "hover": (".path-bar > button:hover",),
            "checked": (".path-bar > button:checked",),
            "checked+hover": (".path-bar > button:checked:hover",),
        }
        self.assert_tab_faces(forms)


if __name__ == "__main__":
    unittest.main()
