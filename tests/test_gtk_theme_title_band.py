"""Validate GTK 3 Platinum title-button declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import TITLE_BUTTON_ASSETS, TITLE_BUTTON_IMAGE
from support.repo_root import ROOT


class TestGtkThemeTitleBand(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_title_buttons(self):
        for scope in ("headerbar", ".titlebar"):
            for control, asset in TITLE_BUTTON_ASSETS:
                self.assert_title_button(
                    f"{scope} button.titlebutton.{control}", asset
                )
            self.assert_rule(
                f"{scope} button.titlebutton image", TITLE_BUTTON_IMAGE
            )

    def test_titlebutton_separator_hidden(self):
        for selector in (
            "headerbar separator.titlebutton",
            ".titlebar separator.titlebutton",
        ):
            self.assert_rule(selector, {"opacity": "0"})


if __name__ == "__main__":
    unittest.main()
