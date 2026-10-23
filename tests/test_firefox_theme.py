"""Validate the standalone Firefox Platinum ``userChrome.css`` sheet.

No reference screenshot shows Firefox chrome, so the palette is the shared
Platinum palette and the geometry adapts this theme's Platinum controls. The
sheet ships alone; a later part installs it into a Firefox profile.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from support import containment
from support.gtk_css import HEX, parse_css
from support.gtk_theme_spec import ETCH_DARK, SheetRuleAssertions
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    SELECTION,
    TROUGH,
    WHITE,
)
from support.repo_root import ROOT

THEME_ID = "org.macos8.desktop"
SHEET = (
    Path(ROOT)
    / "theme"
    / "firefox"
    / THEME_ID
    / "chrome"
    / "userChrome.css"
)
README = Path(ROOT) / "README.md"
SHEET_PATH = "theme/firefox/org.macos8.desktop/chrome/userChrome.css"

REQUIRED_RULES = {
    ":root": {
        "--lwt-accent-color": f"{FACE} !important",
        "--lwt-text-color": f"{BLACK} !important",
        "--toolbar-bgcolor": f"{FACE} !important",
        "--toolbar-color": f"{BLACK} !important",
        "--tab-selected-bgcolor": f"{TROUGH} !important",
        "--tab-selected-textcolor": f"{BLACK} !important",
        "--arrowpanel-background": f"{FACE} !important",
        "--arrowpanel-color": f"{BLACK} !important",
        "--arrowpanel-border-color": f"{BLACK} !important",
    },
    "#navigator-toolbox": {
        "background-color": f"{FACE} !important",
        "border-bottom": f"1px solid {BLACK} !important",
    },
    "#TabsToolbar": {
        "background-color": f"{FACE} !important",
    },
    "#nav-bar": {
        "background-color": f"{FACE} !important",
        "border-bottom": f"1px solid {ETCH_DARK} !important",
        "box-shadow": f"inset 0 -1px {WHITE} !important",
    },
    "#PersonalToolbar": {
        "background-color": f"{FACE} !important",
        "border-bottom": f"1px solid {ETCH_DARK} !important",
        "box-shadow": f"inset 0 -1px {WHITE} !important",
    },
    "#toolbar-menubar": {
        "background-color": f"{FACE} !important",
        "border-bottom": f"1px solid {ETCH_DARK} !important",
        "box-shadow": f"inset 0 -1px {WHITE} !important",
    },
    ".tab-background": {
        "background-color": f"{FACE} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": (
            f"inset 1px 1px {WHITE}, inset -1px -1px {GREY} !important"
        ),
    },
    ".tabbrowser-tab[selected] .tab-background": {
        "background-color": f"{TROUGH} !important",
        "border-bottom-color": f"{TROUGH} !important",
    },
    "#urlbar-background": {
        "background-color": f"{WHITE} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": "none !important",
    },
    "#statuspanel-label": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
    },
    "menupopup": {
        "--panel-background": f"{FACE} !important",
        "--panel-color": f"{BLACK} !important",
        "--panel-border-color": f"{BLACK} !important",
    },
    "menupopup > menuitem:hover": {
        "background-color": f"{SELECTION} !important",
    },
    "menupopup > menu:hover": {
        "background-color": f"{SELECTION} !important",
    },
    'menupopup > menuitem[_moz-menuactive="true"]': {
        "background-color": f"{SELECTION} !important",
    },
    'menupopup > menu[_moz-menuactive="true"]': {
        "background-color": f"{SELECTION} !important",
    },
}


class TestFirefoxChrome(SheetRuleAssertions, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = containment.read_text(SHEET, ROOT, encoding="utf-8")
        cls.readme = containment.read_text(README, ROOT, encoding="utf-8")
        cls.colours, cls.rules, cls.selectors = parse_css(
            cls.text, source=SHEET_PATH
        )

    def test_required_rules(self):
        for selector, expected in REQUIRED_RULES.items():
            with self.subTest(selector=selector):
                self.assert_rule(selector, expected)

    def test_palette_is_exact(self):
        self.assertEqual(
            set(HEX.findall(self.text)),
            {BLACK, WHITE, GREY, FACE, TROUGH, SELECTION, ETCH_DARK},
        )

    def test_sheet_has_no_at_rule_or_import(self):
        self.assertNotIn("@", self.text)

    def test_sheet_does_not_name_adwaita(self):
        self.assertNotIn("adwaita", self.text.lower())

    def test_selectors_are_not_universal(self):
        for selector in self.selectors:
            self.assertNotIn("*", selector)

    def test_header_names_provenance_and_preference(self):
        self.assertIn("Provenance exception", self.text)
        self.assertIn(
            "toolkit.legacyUserProfileCustomizations.stylesheets",
            self.text,
        )

    def test_readme_names_the_sheet(self):
        self.assertIn(SHEET_PATH, self.readme)


if __name__ == "__main__":
    unittest.main()
