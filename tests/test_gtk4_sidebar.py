"""GTK 4 sidebar declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_rule_cases import (
    ROW_SELECTED_BUTTON_ARM_SIDEBAR,
    ROW_SELECTED_BUTTON_ARM_SIDEBAR_BACKDROP,
)


class TestGtk4Sidebar(Gtk4SheetRuleCases, unittest.TestCase):
    def test_sidebar_button_focus_outline_color(self):
        self.assert_black_focus_outline(("button.sidebar-button:focus:focus-visible",))

    def test_sidebar_button_corners(self):
        """Pin the restated sidebar navigation-button radius arm.

        No collected reference screenshot shows a sidebar navigation
        button, so the sheet restates stock's 16px-minimum 100%-radius arm
        byte-equal with exactly the zero radius: the existing sidebar records
        own the focus outline colour and the selection-tint colours only,
        so stock keeps this button's face round today.
        """
        selector = "button.sidebar-button"
        self.assert_rule(selector, {"border-radius": "0"})
        self.assertEqual(self.selectors.count(selector), 1)
        self.assert_matches_frame(selector, "border-radius")
        self.assertEqual(
            {selector for selector in self.rules if "sidebar-button" in selector},
            {
                "button.sidebar-button",
                "button.sidebar-button:focus:focus-visible",
                ROW_SELECTED_BUTTON_ARM_SIDEBAR,
                ROW_SELECTED_BUTTON_ARM_SIDEBAR_BACKDROP,
            },
        )

    def test_sidebar_row_icon_opacity(self):
        # The sheet restates the toolkit resource's 0.7 veil
        # arm, which is state-independent, so no hover, active, selected or
        # backdrop twin exists and the family holds exactly this one rule.
        self.assertEqual(
            {selector for selector in self.rules if "sidebar-icon" in selector},
            {"row image.sidebar-icon"},
        )
        self.assert_rule("row image.sidebar-icon", {"opacity": "1"})
        self.assertEqual(self.selectors.count("row image.sidebar-icon"), 1)
        # Held in the existing sidebar neighbourhood, not a detached tail.
        self.assertGreater(
            self.selectors.index("row image.sidebar-icon"),
            self.selectors.index(
                "placessidebar .navigation-sidebar > row:drop(active)"
                ":not(:disabled):selected"),
        )


if __name__ == "__main__":
    unittest.main()
