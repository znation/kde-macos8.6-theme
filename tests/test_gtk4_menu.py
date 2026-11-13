"""GTK 4 menu declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import MENUBUTTON_ARROWS, MENU_CHECK
from support.platinum_palette import SELECTION


class TestGtk4Menu(Gtk4SheetRuleCases, unittest.TestCase):
    def test_menubutton_arrows(self):
        for selector, expected in MENUBUTTON_ARROWS.items():
            self.assert_rule(selector, expected)

    def test_menu_check_and_radio_are_boxless(self):
        for selector in (
            "popover modelbutton check",
            "popover modelbutton radio",
            "popover.background modelbutton check",
            "popover.background modelbutton radio",
        ):
            self.assert_rule(selector, MENU_CHECK)

    def test_menu_separator(self):
        self.assert_menu_separator(
            ("popover separator", "popover.background separator")
        )

    def test_menubar_titles(self):
        self.assert_menubar_titles("menubar > item")
        self.assert_rule(
            "menubar > item:selected", {"background-color": SELECTION}
        )

    def test_menu_selection_corners(self):
        # The 2026-11-04 menu-selection corner row squares the existing
        # menubar item beside its padding pin and adds the two stock
        # twins at the modelbutton-to-tooltip seam.
        self.assert_rule("menubar > item", {"border-radius": "0"})
        self.assertEqual(self.selectors.count("menubar > item"), 1)
        rows = {"popover.menu list > row", "popover.menu listview > row"}
        nested = "menubar > item popover.menu popover.menu > contents"
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if "popover.menu list > row" in selector
                or "popover.menu listview > row" in selector
            },
            rows,
        )
        for selector in rows | {nested}:
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_square_corner(selector)
        for selector in sorted(rows | {nested}):
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("modelbutton.flat:disabled"),
            )
            self.assertLess(
                self.selectors.index(selector),
                self.selectors.index("tooltip"),
            )
        self.assertGreater(
            self.selectors.index("menubar > item"),
            self.selectors.index(".toolbar"),
        )


if __name__ == "__main__":
    unittest.main()
