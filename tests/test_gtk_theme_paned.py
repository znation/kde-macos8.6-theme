"""Validate GTK 3 Platinum paned-handle declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT


class TestGtkThemePaned(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_paned_handle(self):
        self.assert_paned_handles()

    def test_paned_handle_background_images(self):
        for selector in (
            "paned > separator",
            "paned > separator:selected",
            "paned > separator:backdrop",
            "paned > separator.wide",
            "paned > separator.wide:backdrop",
        ):
            self.assert_rule(selector, {"background-image": "none"})

    def test_paned_handle_direction_margins(self):
        # Exact stock twins from the libgtk-3 theme CSS (libgtk-3 3.24.49,
        # probed 2026-10-31): each :dir arm carries one class more than the
        # existing orientation rules, so only a restatement clears their 8px
        # margins and paddings.
        for selector in (
            "paned.horizontal > separator:dir(ltr)",
            "paned.horizontal > separator:dir(rtl)",
        ):
            self.assert_rule(selector, {"margin": "0", "padding": "0"})


if __name__ == "__main__":
    unittest.main()
