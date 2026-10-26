"""Validate the standalone Firefox Platinum ``userChrome.css`` sheet.

No reference screenshot shows Firefox chrome, so the palette is the shared
Platinum palette and the geometry adapts this theme's Platinum controls. The
sheet ships as a standalone file; ``make install-firefox`` copies it into one
Firefox profile, and ``tests/test_firefox_install.py`` pins that install and
its removal.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from support import containment
from support.gtk_css import HEX, parse_css
from support.gtk_rule_cases import SheetRuleAssertions
from support.gtk_theme_spec import ETCH_DARK, RAISED_BEVEL
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
    "#toolbar-menubar menubar > menu[open]": {
        "background-color": f"{SELECTION} !important",
        "border-bottom-color": f"{SELECTION} !important",
    },
    "#sidebar-box": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
    },
    "#sidebar-header": {
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
    ".tabbrowser-tab:is([selected], [multiselected]) .tab-background": {
        "background-color": f"{TROUGH} !important",
        "border-bottom-color": f"{TROUGH} !important",
    },
    (
        ".tabbrowser-tab:hover > .tab-stack > .tab-background"
        ":not([selected]):not([multiselected])"
    ): {
        "background-color": f"{TROUGH} !important",
    },
    "#urlbar-background": {
        "background-color": f"{WHITE} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": "none !important",
    },
    "#searchbar:not(:focus-within)": {
        "background-color": f"{WHITE} !important",
        "color": f"{BLACK} !important",
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
        "color": f"{BLACK} !important",
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

    def test_search_field_paint_is_scoped_to_the_unfocused_classic_field(self):
        selector = "#searchbar:not(:focus-within)"
        self.assertEqual(
            {name for name in self.rules if "searchbar" in name},
            {selector},
        )
        self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])

    def test_tab_hover_paint_is_scoped_to_unselected_tabs(self):
        hover = (
            ".tabbrowser-tab:hover > .tab-stack > .tab-background"
            ":not([selected]):not([multiselected])"
        )
        selected = ".tabbrowser-tab:is([selected], [multiselected]) .tab-background"
        self.assertEqual(
            {name for name in self.rules if "tab-background" in name},
            {
                ".tab-background",
                selected,
                hover,
            },
        )
        for selector in (
            ".tab-background",
            selected,
            hover,
        ):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        for part in (":hover", ":not([selected])", ":not([multiselected])"):
            with self.subTest(part=part):
                self.assertIn(part, hover)

    def test_selected_face_covers_multiselected_tabs(self):
        selected = ".tabbrowser-tab:is([selected], [multiselected]) .tab-background"
        hover = (
            ".tabbrowser-tab:hover > .tab-stack > .tab-background"
            ":not([selected]):not([multiselected])"
        )
        self.assertIn("[selected]", selected)
        self.assertIn("[multiselected]", selected)
        self.assertEqual(self.rules[selected], REQUIRED_RULES[selected])
        self.assertEqual(self.rules[selected]["background-color"],
                         f"{TROUGH} !important")
        self.assertEqual(self.rules[selected]["border-bottom-color"],
                         f"{TROUGH} !important")
        for name in self.rules:
            if ("tab-background" in name and "[selected]" in name
                    and "[multiselected]" not in name):
                with self.subTest(selected_only=name):
                    self.assertNotIn("background-color", self.rules[name])
        self.assertEqual(
            {name for name in self.rules if "multiselected" in name},
            {selected, hover},
        )

    def test_menubar_open_title_paint_is_scoped_to_the_open_title(self):
        selector = "#toolbar-menubar menubar > menu[open]"
        # A menu-bar title is a ``menu`` element outside a popup, so catch a
        # rule that targets one without naming #toolbar-menubar, such as a
        # bare ``menu[open]:hover``, rather than only selectors spelled
        # ``menubar``.
        title_rules = {
            name for name in self.rules
            if "menubar" in name
            or ("menu" in re.findall(r"[-\w]+", name)
                and "menupopup" not in name)
        }
        self.assertEqual(title_rules, {"#toolbar-menubar", selector})
        for name in ("#toolbar-menubar", selector):
            with self.subTest(selector=name):
                self.assertEqual(self.rules[name], REQUIRED_RULES[name])
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if declarations == REQUIRED_RULES[selector]},
            {selector},
        )

    def test_sidebar_frame_is_scoped_to_the_box_and_header(self):
        self.assertEqual(
            {name for name in self.rules if "sidebar" in name},
            {"#sidebar-box", "#sidebar-header"},
        )
        for selector in ("#sidebar-box", "#sidebar-header"):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        self.assertEqual(self.rules["#sidebar-box"]["background-color"],
                         f"{FACE} !important")
        self.assertEqual(self.rules["#sidebar-box"]["color"],
                         f"{BLACK} !important")
        self.assertEqual(self.rules["#sidebar-header"]["border-bottom"],
                         f"1px solid {ETCH_DARK} !important")
        self.assertEqual(self.rules["#sidebar-header"]["box-shadow"],
                         f"inset 0 -1px {WHITE} !important")

    def test_find_field_foreground_is_guarded(self):
        selector = (
            'findbar .findbar-textbox:not([status="notfound"])'
            ':not([flash="true"]):not(:focus)'
        )
        self.assertEqual(
            {name for name in self.rules if "findbar-textbox" in name},
            {selector},
        )
        self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        self.assertEqual(self.rules["findbar"], REQUIRED_RULES["findbar"])

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
            "No reference shows Firefox tab hover",
            "tests/test_desktoptheme_scrollbar.py::TestScrollbarReference",
            "No reference shows Firefox tooltips or a Balloon Help balloon",
            "platform adaptation 2026-10-25",
            "[Colors:Tooltip] BackgroundNormal",
            "TOOLTIP_FACE", "classic-palette exception accepted in QUESTIONS.md",
            "not a screenshot sample", "widgets/tooltip.svg",
            "tests/test_desktoptheme_tooltip.py::TestTooltip.test_tooltip_pixels",
            "chrome/toolkit/content/global/xul.css",
            "selector; default native anonymous tooltips require UA styling",
            "outside this sheet's guarantee",
            "No reference shows Firefox's optional classic search field",
            "chrome/browser/skin/classic/browser/urlbar-searchbar.css",
            "and owns the focused appearance",
            "#searchbar-new stays Firefox's",
            "No reference shows Firefox's find field",
            "chrome/toolkit/skin/classic/global/findbar.css",
            "not-found and flash states stay",
            "No reference shows Firefox multi-selected tabs",
            "selected=visuallyselected",
            "platform colour adaptation 2026-10-26",
            "No reference shows Firefox's menu bar",
            "TestMenuBarItem.test_menubaritem_pressed_is_flat_selection_colour",
            "TestReferenceAnchors.test_selection_background",
            "No reference shows a Firefox sidebar",
            "chrome/browser/skin/classic/browser/sidebar.css",
            "--sidebar-background-color",
            "modules/ThemeVariableMap.sys.mjs",
            "the sidebar's inner document is not userChrome territory",
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
