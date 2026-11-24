"""GTK 4 bar-family and file-chooser breadcrumb keyboard-focus outline checks
moved out of ``test_gtk4_theme``.
"""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases


class TestGtk4BarFocus(Gtk4SheetRuleCases, unittest.TestCase):
    def test_headerbar_button_focus_outline_color(self):
        self.assert_bar_family_focus("headerbar ", "headerbar ")

    def test_toolbar_button_focus_outline_color(self):
        self.assert_bar_family_focus(".toolbar ", ".toolbar")

    def test_actionbar_button_focus_outline_color(self):
        self.assert_bar_family_focus("actionbar > revealer > box ", "actionbar")

    def test_searchbar_button_focus_outline_color(self):
        self.assert_bar_family_focus(
            "searchbar > revealer > box ",
            "searchbar",
            extra=(".close:focus:focus-visible",),
        )

    def test_filechooser_breadcrumb_focus_outline_color(self):
        selectors = {
            "filechooser #pathbarbox > stack > box > button:focus:focus-visible",
            "filechooser #pathbarbox > stack > box > box > button:focus:focus-visible",
            "filechooser #pathbarbox > stack > box > menubutton > button:focus:focus-visible",
        }
        self.assertEqual(
            {selector for selector in self.selectors if "pathbarbox" in selector},
            selectors,
        )
        self.assert_black_focus_outline(selectors)


if __name__ == "__main__":
    unittest.main()
