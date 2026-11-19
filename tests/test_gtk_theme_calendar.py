"""Validate GTK 3 calendar declarations in the Platinum sheet."""

from __future__ import annotations

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import DISABLED_TEXT, ETCH_DARK
from support.platinum_palette import BLACK
from support.repo_root import ROOT


class TestGtkThemeCalendar(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_calendar(self):
        self.assert_calendar(("calendar:selected",), ("calendar:indeterminate",))

    def test_calendar_outer_border(self):
        self.assert_rule("calendar", {"border": f"1px solid {BLACK}"})
        for selector in ("frame > border", ".frame"):
            self.assertEqual(
                self.rules["calendar"]["border"],
                self.rules[selector]["border"],
            )

    def test_calendar_focus_outline(self):
        self.assert_dotted_focus_outline("calendar:focus")

    def test_calendar_state_arms(self):
        # No reference screenshot shows a GTK calendar header, navigation
        # button, day highlight or backdrop state, so the nine stock arms
        # rest on existing faces: ETCH_DARK for the header rule and day
        # highlights, BLACK for the navigation glyphs (the erase
        # precedents, with no hover motion) and the disabled grey, and the
        # existing button:backdrop keep-the-existing-face policy for the
        # backdrop window.
        expected = {
            "calendar.header": {"border-bottom-color": ETCH_DARK},
            "calendar.header:backdrop": {"border-bottom-color": ETCH_DARK},
            "calendar.button": {"color": BLACK},
            "calendar.button:hover": {"color": BLACK},
            "calendar.button:backdrop": {"color": BLACK},
            "calendar.button:disabled": {"color": DISABLED_TEXT["color"]},
            "calendar.highlight": {"color": ETCH_DARK},
            "calendar.highlight:backdrop": {"color": ETCH_DARK},
            "calendar:backdrop": {"color": BLACK, "border-color": BLACK},
        }
        for selector, rule in expected.items():
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], rule, selector)
        self.assertEqual(
            {s for s in self.rules if s.startswith("calendar")},
            {
                "calendar",
                "calendar:selected",
                "calendar:indeterminate",
                "calendar:focus",
                *expected,
            },
        )
        self.assert_rule_after("calendar.header {", "calendar:focus {")


if __name__ == "__main__":
    unittest.main()
