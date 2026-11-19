"""Validate GTK 3 Platinum message-dialog declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT

CSS = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"


class TestGtkThemeMessageDialog(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_message_dialog_header_band(self):
        # The message dialog's title band repaints the existing headerbar.
        # The band restates the existing headerbar, .titlebar group plus its
        # headerbar-only 1px bottom border, the backdrop band restates the
        # existing headerbar:backdrop, .titlebar:backdrop group, and the
        # dialog body corners go square; tying through the existing groups'
        # dictionaries keeps the bands in step with any future header
        # change.
        self.assert_rule(
            "messagedialog .titlebar",
            {**self.rules["headerbar"], "border-width": "0 0 1px 0"},
        )
        self.assert_rule(
            "messagedialog .titlebar:backdrop",
            self.rules["headerbar:backdrop"],
        )
        self.assert_rule(
            "messagedialog.csd.background",
            {"border-radius": "0"},
        )

    def test_message_dialog_action_area(self):
        # The stock toolkit resource re-pads the message dialog's action
        # buttons to 10px 14px and rounds the end buttons' bottom corners
        # to 7px with -gtk-outline-radius; the sheet restates the stock
        # button base padding and square corners on both end arms.
        self.assert_rule(
            "messagedialog.csd .dialog-action-area button",
            {"padding": "4px 9px"},
        )
        for arm in ("first-child", "last-child"):
            self.assert_rule(
                f"messagedialog.csd .dialog-action-area button:{arm}",
                {"border-radius": "0", "-gtk-outline-radius": "0"},
            )


if __name__ == "__main__":
    unittest.main()
