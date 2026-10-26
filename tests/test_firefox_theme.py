"""Validate the standalone Firefox Platinum ``userChrome.css`` sheet.

No reference screenshot shows Firefox chrome, so the palette is the shared
Platinum palette and the geometry adapts this theme's Platinum controls. The
sheet ships as a standalone file; ``make install-firefox`` copies it into one
Firefox profile, and ``tests/test_firefox_install.py`` pins that install and
its removal.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from support import containment
from support.gtk_css import HEX, parse_css
from support.gtk_theme_spec import ETCH_DARK, RAISED_BEVEL, SheetRuleAssertions
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    SELECTION,
    TOOLTIP_FACE,
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
    "tooltip": {
        "appearance": "none !important",
        "background-color": f"{TOOLTIP_FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": "none !important",
    },
    ":root": {
        "--lwt-accent-color": f"{FACE} !important",
        "--lwt-text-color": f"{BLACK} !important",
        "--toolbar-bgcolor": f"{FACE} !important",
        "--toolbar-color": f"{BLACK} !important",
        "--tab-selected-bgcolor": f"{TROUGH} !important",
        "--tab-selected-textcolor": f"{BLACK} !important",
        "--toolbarbutton-border-radius": "0 !important",
        "--toolbarbutton-background-color-hover": f"{TROUGH} !important",
        "--toolbarbutton-background-color-active": f"{SELECTION} !important",
        "--urlbar-box-background-color-hover": f"{TROUGH} !important",
        "--urlbar-box-background-color-active": f"{SELECTION} !important",
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
    ".urlbarView-row": {
        "border-radius": "0 !important",
    },
    ".urlbarView-row[row-selectable]:not([selected]):hover": {
        "background-color": f"{TROUGH} !important",
    },
    ".urlbarView-row[selected]": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
    },
    ".urlbarView-body-inner": {
        "border-top-color": f"{ETCH_DARK} !important",
    },
    "#statuspanel-label": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
    },
    'panel[type="arrow"]': {
        "--panel-border-radius": "0 !important",
        "--panel-background-color": f"{FACE} !important",
        "--panel-text-color": f"{BLACK} !important",
        "--panel-border-color": f"{BLACK} !important",
    },
    "menupopup": {
        "--panel-border-radius": "0 !important",
        "--panel-background-color": f"{FACE} !important",
        "--panel-text-color": f"{BLACK} !important",
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
    "#PersonalToolbar .bookmark-item:hover": {
        "background-color": f"{SELECTION} !important",
        "border-radius": "0 !important",
        "box-shadow": f"inset 1px 1px {WHITE} !important",
    },
    "#PersonalToolbar .bookmark-item[open]": {
        "background-color": f"{SELECTION} !important",
        "border-radius": "0 !important",
        "box-shadow": f"inset 1px 1px {WHITE} !important",
    },
    "toolbarbutton:hover:not([disabled=\"true\"])": {
        "box-shadow": f"{RAISED_BEVEL} !important",
    },
    "toolbarbutton:hover:active:not([disabled=\"true\"])": {
        "box-shadow": f"inset 1px 1px {GREY} !important",
    },
    "menupopup > menuseparator": {
        "padding": "0 !important",
        "margin": "2px 0 !important",
    },
    "menupopup > menuseparator::before": {
        "border-top": f"1px solid {ETCH_DARK} !important",
        "border-bottom": f"1px solid {WHITE} !important",
    },
    "findbar": {
        "background-color": f"{FACE} !important",
        "border-top": f"1px solid {BLACK} !important",
    },
    "findbar .findbar-textbox:not([status=\"notfound\"]):not([flash=\"true\"]):not(:focus)": {
        "background-color": f"{WHITE} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"inset 1px 1px {GREY} !important",
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

    def test_panel_radius_override_is_scoped_to_menus_and_arrow_panels(self):
        self.assertEqual(
            {selector for selector, declarations in self.rules.items()
             if "--panel-border-radius" in declarations},
            {"menupopup", 'panel[type="arrow"]'},
        )

    def test_consumed_popup_colour_tokens_are_scoped_to_menus_and_arrow_panels(self):
        for token in ("--panel-background-color", "--panel-text-color",
                      "--panel-border-color"):
            with self.subTest(token=token):
                self.assertEqual(
                    {selector for selector, declarations in self.rules.items()
                     if token in declarations},
                    {"menupopup", 'panel[type="arrow"]'},
                )
        for token in ("--panel-background", "--panel-color"):
            with self.subTest(obsolete_token=token):
                self.assertNotIn(token, self.rules["menupopup"])
        for selector, declarations in self.rules.items():
            for token in ("--arrowpanel-background", "--arrowpanel-color",
                          "--arrowpanel-border-color"):
                with self.subTest(selector=selector, obsolete_token=token):
                    self.assertNotIn(token, declarations)

    def test_palette_is_exact(self):
        self.assertEqual(
            set(HEX.findall(self.text)),
            {BLACK, WHITE, GREY, FACE, TROUGH, SELECTION, ETCH_DARK, TOOLTIP_FACE},
        )

    def test_tooltip_face_is_scoped_to_explicit_tooltips(self):
        self.assertEqual(
            {selector for selector, declarations in self.rules.items()
             if any(TOOLTIP_FACE in value.upper()
                    for value in declarations.values())},
            {"tooltip"},
        )
        self.assertEqual(self.rules["tooltip"], REQUIRED_RULES["tooltip"])

    def test_results_paint_does_not_override_shared_tokens(self):
        # Firefox also consumes these tokens on realtime sub-items and one-offs.
        for selector, declarations in self.rules.items():
            with self.subTest(selector=selector):
                self.assertFalse(any(
                    name.startswith("--urlbarview-") for name in declarations
                ))
                if "urlbarView" in selector:
                    self.assertIn(selector, REQUIRED_RULES)
                    self.assertEqual(declarations, REQUIRED_RULES[selector])

    def test_sheet_has_no_at_rule_or_import(self):
        self.assertNotIn("@", self.text)

    def test_sheet_does_not_name_adwaita(self):
        self.assertNotIn("adwaita", self.text.lower())

    def test_selectors_are_not_universal(self):
        for selector in self.selectors:
            self.assertNotIn("*", selector)

    def test_header_names_provenance_and_preference(self):
        self.assertIn("Provenance exception", self.text)
        header = self.text.split("*/", 1)[0]
        for provenance in (
            "No reference shows Firefox tooltips or a Balloon Help balloon",
            "platform adaptation 2026-10-25",
            "[Colors:Tooltip] BackgroundNormal",
            "TOOLTIP_FACE", "classic-palette exception accepted in QUESTIONS.md",
            "not a screenshot sample", "widgets/tooltip.svg",
            "tests/test_desktoptheme_tooltip.py::TestTooltip.test_tooltip_pixels",
            "chrome/toolkit/content/global/xul.css",
            "selector; default native anonymous tooltips require UA styling",
            "outside this sheet's guarantee",
        ):
            with self.subTest(provenance=provenance):
                self.assertIn(provenance, header)
        self.assertIn(
            "toolkit.legacyUserProfileCustomizations.stylesheets",
            self.text,
        )

    def test_readme_names_the_sheet(self):
        self.assertIn(SHEET_PATH, self.readme)


if __name__ == "__main__":
    unittest.main()
