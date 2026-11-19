"""Validate GTK 3 menu declarations in the Platinum stylesheet."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import BUTTON_BEVEL, DISABLED_TEXT, MENU_CHECK, SUBMENU_ARROW
from support.platinum_palette import BLACK, FACE, SELECTION
from support.repo_root import ROOT

CSS = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"
MENU_SCROLL_UP = ("menu > arrow.top", ".menu > arrow.top", ".context-menu > arrow.top")
MENU_SCROLL_DOWN = (
    "menu > arrow.bottom",
    ".menu > arrow.bottom",
    ".context-menu > arrow.bottom",
)


class TestGtkThemeMenu(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_menu(self):
        for selector in ("menu", ".menu", "popover", ".popover"):
            self.assert_rule(selector, {
                "background-color": FACE,
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
            })
        for selector in ("menuitem:hover", ".menuitem:hover",
                         "popover modelbutton:hover", "popover modelbutton:selected"):
            self.assert_rule(selector, {"background-color": SELECTION})

    def test_menu_row_state_faces(self):
        """Pin the existing menu-row and menu-bar-title faces under every state.

        The nine appended arms rest the toolkit resource's
        higher-specificity classic-menu state spellings so a hovered row or
        hovered or open menu-bar title keeps the selection fill with black
        text, a disabled or backdropped row keeps black rest text and the
        inactive grey when disabled, and a `:dir` arrow keeps the shipped
        submenu triangle in both text directions; the exact stock arms live
        in docs/invariants.md.
        """
        hover = (
            "menu menuitem:hover", ".menu menuitem:hover",
            ".context-menu menuitem:hover", "menu menuitem:backdrop:hover",
            ".menu menuitem:backdrop:hover", ".context-menu menuitem:backdrop:hover",
        )
        self.assert_rule_group({s: {"color": BLACK, "background-color": SELECTION} for s in hover})
        backdrop = ("menu menuitem:backdrop", ".menu menuitem:backdrop", ".context-menu menuitem:backdrop")
        self.assert_rule_group({s: {"color": BLACK} for s in backdrop})
        menubar_hover = ("menubar > menuitem:hover", ".menubar > menuitem:hover")
        self.assert_rule_group({s: {"color": BLACK, "box-shadow": "none"} for s in menubar_hover})
        disabled = (
            "menu menuitem:disabled", ".menu menuitem:disabled", ".context-menu menuitem:disabled",
            "menu menuitem:disabled:backdrop", ".menu menuitem:disabled:backdrop",
            ".context-menu menuitem:disabled:backdrop", "menubar > menuitem:disabled",
            ".menubar > menuitem:disabled",
        )
        self.assert_rule_group({s: DISABLED_TEXT for s in disabled})
        # The inactive grey is re-derived from the colour scheme, as the
        # existing disabled-text callers do.
        self.assert_disabled_text(disabled)
        arrows = (
            "menu menuitem arrow:dir(ltr)", ".menu menuitem arrow:dir(ltr)",
            ".context-menu menuitem arrow:dir(ltr)", "menu menuitem arrow:dir(rtl)",
            ".menu menuitem arrow:dir(rtl)", ".context-menu menuitem arrow:dir(rtl)",
        )
        self.assert_rule_group({s: SUBMENU_ARROW for s in arrows})
        # Source order: every appended spelling sits after the existing
        # `menuitem:hover` and `menubar > menuitem` selectors, so the
        # byte-equal stock twins win the equal-specificity ties under the
        # lower-sheet reading of how the toolkit resource competes.
        for selector in hover + backdrop + disabled + arrows + menubar_hover:
            with self.subTest(selector=selector):
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("menuitem:hover"),
                )
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("menubar > menuitem"),
                )

    def test_menu_scroll_arrows(self):
        # Preserve the shipped up/down glyphs while closing the stock rounded
        # corners; the reference set has no scrolling-menu capture.
        for selectors, glyph in ((MENU_SCROLL_UP, "arrow-up.svg"), (MENU_SCROLL_DOWN, "arrow-down.svg")):
            for selector in selectors:
                self.assert_rule(selector, {
                    "-gtk-icon-source": f'url("../assets/{glyph}")',
                    "border-radius": "0",
                })

    def test_menu_scroll_arrow_faces(self):
        """Pin the menu scroll-arrow face restatement."""
        # Stock paints the menu's scroll arrows with an opaque white face, a
        # grey hover wash and a near-white backdrop tile. Each arm restates
        # the existing plain button.flat dictionary at the arrow's stock
        # spelling, with later source order winning ties per property.
        raised = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
            "transition": "none",
        }
        disabled = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        raised_selectors = tuple(
            f"{prefix} > arrow{state}"
            for prefix in ("menu", ".menu", ".context-menu")
            for state in ("", ":hover", ":backdrop")
        )
        disabled_selectors = tuple(
            f"{prefix} > arrow:disabled"
            for prefix in ("menu", ".menu", ".context-menu")
        )
        for selector in raised_selectors:
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], raised, selector)
        for selector in disabled_selectors:
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], disabled, selector)
        # The token sweep keys on a substring no other existing selector
        # carries: a dropped twin, renamed spelling or stray state fails.
        expected = set(MENU_SCROLL_UP) | set(MENU_SCROLL_DOWN) | set(raised_selectors) | set(disabled_selectors)
        self.assertEqual(
            {selector for selector in self.selectors if "menu > arrow" in selector},
            expected,
        )
        # Every appended face spelling follows the existing glyph group, so
        # the restated face wins the equal-specificity race against stock.
        for selector in raised_selectors + disabled_selectors:
            self.assertGreater(self.selectors.index(selector), self.selectors.index("menu > arrow.top"))

    def test_menu_check_and_radio_are_boxless(self):
        for selector in (
            "menu menuitem check",
            "menu menuitem radio",
            "popover modelbutton check",
            "popover modelbutton radio",
        ):
            self.assert_rule(selector, MENU_CHECK)

    def test_menu_separator(self):
        self.assert_menu_separator(("menu separator", ".menu separator"))


if __name__ == "__main__":
    unittest.main()
