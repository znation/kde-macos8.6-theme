"""Validate the standalone Firefox Platinum ``userContent.css`` sheet.

No reference screenshot shows Firefox's content-area downloads page, its
about:config page or its about:preferences navigation, so the palette is the
shared Platinum palette and the geometry adapts this theme's line-edit field,
list-item row and push button. The opt-in profile install copies the sheet
beside userChrome.css through make install-firefox.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from support import containment
from support.css_header import CommentHeaderAssertions
from support.gtk_css import HEX, parse_css, strip_comments
from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    ETCH_DARK,
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
    / "userContent.css"
)
SHEET_PATH = "theme/firefox/org.macos8.desktop/chrome/userContent.css"
MARKER = "/* org.macos8.desktop Firefox content, standalone userContent.css"

LIST = "#contentAreaDownloadsView #downloadsListBox:not(:empty)"
ROW = "#contentAreaDownloadsView #downloadsListBox > richlistitem"
SELECTED = ROW + "[selected]"

REQUIRED_RULES = {
    LIST: {
        "appearance": "none !important",
        "background-color": f"{WHITE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"inset 1px 1px {GREY} !important",
    },
    ROW: {
        "border-radius": "0 !important",
    },
    SELECTED: {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
    },
}

AT_RULE = re.compile(r'@-moz-document\s+url\("(?P<url>[^"]+)"\)\s*\{')

CONFIG_PREFS = "#prefs:not(:empty)"
CONFIG_ODD = "#prefs > tr.odd"
CONFIG_HOVER = "#prefs > tr:hover"
CONFIG_ODD_HOVER = "#prefs > tr.odd:hover"
CONFIG_SEARCH = "#about-config-search"
CONFIG_SHOW_ALL = "#show-all"
CONFIG_WARNING = "#warningButton"
CONFIG_SHOW_ALL_HOVER = "#show-all:hover:not(:disabled)"
CONFIG_WARNING_HOVER = "#warningButton:hover:not(:disabled)"

FIELD_RULE = {
    "background-color": f"{WHITE} !important",
    "color": f"{BLACK} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": f"inset 1px 1px {GREY} !important",
}

BUTTON_RULE = {
    "background-color": f"{FACE} !important",
    "color": f"{BLACK} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": (
        f"inset 1px 1px {WHITE}, inset -1px -1px {BUTTON_SHADOW} !important"
    ),
}

BUTTON_HOVER_RULE = {
    "background-color": f"{SELECTION} !important",
    "color": f"{BLACK} !important",
    "box-shadow": "none !important",
}

REQUIRED_CONFIG_RULES = {
    CONFIG_PREFS: FIELD_RULE,
    CONFIG_ODD: {"background-color": f"{TROUGH} !important"},
    CONFIG_HOVER: {
        "background-color": "transparent !important",
        "color": f"{BLACK} !important",
    },
    CONFIG_ODD_HOVER: {"background-color": f"{TROUGH} !important"},
    CONFIG_SEARCH: FIELD_RULE,
    CONFIG_SHOW_ALL: BUTTON_RULE,
    CONFIG_WARNING: BUTTON_RULE,
    CONFIG_SHOW_ALL_HOVER: BUTTON_HOVER_RULE,
    CONFIG_WARNING_HOVER: BUTTON_HOVER_RULE,
}

CONFIG_CONTROL_PREFIXES = (
    "#prefs",
    "#about-config-search",
    "#show-all",
    "#warningButton",
)

CONFIG_UNTOUCHED = (
    ".config-background",
    ".config-help-text",
    "#about-config-show-only-modified",
    ".cell-edit",
    ".cell-reset",
    ".button-",
)


def at_rule_bodies(text):
    """Return each ``@-moz-document url("...")`` body, keyed by its URL."""
    stripped = strip_comments(text)
    bodies = {}
    for match in AT_RULE.finditer(stripped):
        depth = 1
        quote = None
        index = start = match.end()
        while index < len(stripped) and depth:
            char = stripped[index]
            if quote is not None:
                if char == quote:
                    quote = None
            elif char in "\"'":
                quote = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            index += 1
        bodies[match.group("url")] = stripped[start : index - 1]
    return bodies

PAGE_CHROME = (
    "downloadButton",
    "downloadsHistory",
    "downloadsListEmptyDescription",
    "downloadsContextMenu",
    "hover",
)

NAV = "moz-page-nav-button"
HOST = "moz-page-nav"
SEPARATOR = "#nav-separator"
ROOT = ":root"
HEADING = ".subcategory"

SEARCH = "moz-input-search#searchInput"
PANE_BUTTON = "#mainPrefPane button:not(.arrowhead):not([disabled])"
PANE_BUTTON_HOVER = PANE_BUTTON + ":hover"

REQUIRED_PREFERENCES_RULES = {
    NAV: {
        "--page-nav-button-background-color": "transparent !important",
        "--page-nav-button-background-color-hover": f"{SELECTION} !important",
        "--page-nav-button-background-color-active": f"{SELECTION} !important",
        "--page-nav-button-background-color-selected": f"{SELECTION} !important",
        "--page-nav-button-text-color": f"{BLACK} !important",
        "--page-nav-button-text-color-hover": f"{BLACK} !important",
        "--page-nav-button-text-color-active": f"{BLACK} !important",
        "--page-nav-button-border-radius": "0 !important",
        "--page-nav-button-indicator-color": f"{BLACK} !important",
        "--page-nav-button-indicator-width": "0 !important",
        "--border-radius-small": "0 !important",
    },
    HOST: {
        "--page-nav-border-color": f"{ETCH_DARK} !important",
        "--page-nav-hr-background-color": f"{ETCH_DARK} !important",
    },
    SEPARATOR: {
        "border": "0 !important",
        "border-top": f"1px solid {ETCH_DARK} !important",
        "border-bottom": f"1px solid {WHITE} !important",
    },
    ROOT: {
        "background-color": f"{WHITE} !important",
    },
    HEADING: {
        "border-top-color": f"{ETCH_DARK} !important",
        "box-shadow": f"inset 0 1px 0 {WHITE} !important",
        "color": f"{BLACK} !important",
    },
    SEARCH: {
        "--input-text-border": f"1px solid {BLACK} !important",
        "--input-text-border-radius": "0 !important",
        "--input-text-background-color": f"{WHITE} !important",
        "--input-text-color": f"{BLACK} !important",
        "--icon-color": f"{BLACK} !important",
    },
    PANE_BUTTON: {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": (
            f"inset 1px 1px {WHITE}, inset -1px -1px {BUTTON_SHADOW} !important"
        ),
    },
    PANE_BUTTON_HOVER: {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
}

FORBIDDEN_PAGE_CHROME = ("body", "h1", "hgroup", "main-content-title")


class SheetCase(CommentHeaderAssertions, unittest.TestCase):
    """Shared fixture for the three classes testing ``userContent.css``.

    Each reads the shipped sheet, splits it into ``@-moz-document`` bodies and
    parses exactly one of them; the class attribute ``AT_RULE_URL`` names
    which.
    The inherited :meth:`CommentHeaderAssertions.assert_header_names` serves
    the provenance tests.
    """

    AT_RULE_URL: str

    @classmethod
    def setUpClass(cls):
        cls.text = containment.read_text(SHEET, ROOT, encoding="utf-8")
        cls.bodies = at_rule_bodies(cls.text)
        cls.colours, cls.rules, cls.selectors = parse_css(
            cls.bodies.get(cls.AT_RULE_URL, ""), source=SHEET_PATH
        )


class TestFirefoxContentTheme(SheetCase):
    AT_RULE_URL = "about:downloads"

    def test_first_line_is_the_marker(self):
        first_line = self.text.removeprefix("\ufeff").splitlines()[0]
        self.assertEqual(first_line, MARKER)

    def test_sheet_has_the_downloads_config_and_preferences_at_rules(self):
        stripped = strip_comments(self.text).strip()
        self.assertEqual(
            set(self.bodies),
            {"about:downloads", "about:config", "about:preferences"},
        )
        self.assertEqual(stripped.count("@"), 3)
        for selector in REQUIRED_RULES:
            with self.subTest(selector=selector):
                self.assertIn(selector, self.bodies["about:downloads"])
        self.assertEqual(len(self.selectors), len(REQUIRED_RULES))

    def test_required_rules(self):
        for selector, expected in REQUIRED_RULES.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)

    def test_downloads_rules_are_exactly_the_three_list_rules(self):
        self.assertEqual(set(self.rules), set(REQUIRED_RULES))
        self.assertEqual(self.selectors, [LIST, ROW, SELECTED])

    def test_list_selector_guards_the_empty_state_and_squares_the_rows(self):
        self.assertIn(":not(:empty)", LIST)
        self.assertEqual(self.rules[LIST]["border-radius"], "0 !important")
        self.assertEqual(self.rules[ROW], {"border-radius": "0 !important"})

    def test_no_rule_paints_page_chrome(self):
        for selector in self.selectors:
            with self.subTest(selector=selector):
                self.assertTrue(
                    selector.startswith(
                        "#contentAreaDownloadsView #downloadsListBox"
                    )
                )
                for token in PAGE_CHROME:
                    self.assertNotIn(token, selector)
        for url, body in self.bodies.items():
            _, _, selectors = parse_css(body, source=SHEET_PATH)
            for selector in selectors:
                with self.subTest(url=url, selector=selector):
                    for token in FORBIDDEN_PAGE_CHROME:
                        self.assertNotIn(token, selector)

    def test_palette_is_exact(self):
        self.assertEqual(
            set(HEX.findall(self.text)),
            {
                WHITE,
                BLACK,
                GREY,
                ETCH_DARK,
                SELECTION,
                FACE,
                TROUGH,
                BUTTON_SHADOW,
            },
        )

    def test_sheet_does_not_import_or_name_adwaita(self):
        self.assertNotIn("@import", self.text)
        self.assertNotIn("adwaita", self.text.lower())

    def test_selectors_are_not_universal(self):
        for selector in self.selectors:
            self.assertNotIn("*", selector)

    def test_header_names_provenance(self):
        self.assert_header_names(
            (
                "No reference shows Firefox's",
                "widgets/lineedit.svg",
                "tests/test_desktoptheme_lineedit.py::TestLineEdit",
                "widgets/listitem.svg",
                "tests/test_desktoptheme_listitem.py::TestListItem",
                "test_selection_background",
                "chrome/browser/content/browser/downloads/contentAreaDownloadsView.xhtml",
                "contentAreaDownloadsView",
                "contentAreaDownloadsView.css",
                "richlistbox.css",
                "browser.tabs.remote.separatePrivilegedContentProcess",
                "@-moz-document",
                "platform colour adaptation 2026-10-26",
                "make install-firefox",
                "make remove-firefox",
            )
        )


class TestFirefoxPreferencesNavTheme(SheetCase):
    AT_RULE_URL = "about:preferences"

    ROOT = ":root"
    HEADING = ".subcategory"

    def test_required_rules(self):
        for selector, expected in REQUIRED_PREFERENCES_RULES.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)

    def test_parsed_rules_are_exactly_the_nav_rules(self):
        self.assertEqual(set(self.rules), set(REQUIRED_PREFERENCES_RULES))
        self.assertEqual(self.selectors, list(REQUIRED_PREFERENCES_RULES))

    def test_nav_rule_sets_only_custom_properties(self):
        declarations = self.rules[NAV]
        self.assertTrue(declarations)
        for name in declarations:
            with self.subTest(property=name):
                self.assertTrue(
                    name.startswith("--page-nav-")
                    or name == "--border-radius-small"
                )

    def test_host_rule_sets_only_custom_properties(self):
        declarations = self.rules[HOST]
        self.assertTrue(declarations)
        for name in declarations:
            with self.subTest(property=name):
                self.assertTrue(name.startswith("--page-nav-"))

    def test_nav_separator_rule_is_the_etched_pair(self):
        self.assertEqual(
            self.rules[SEPARATOR],
            REQUIRED_PREFERENCES_RULES[SEPARATOR],
        )
        for name, value in self.rules[SEPARATOR].items():
            with self.subTest(property=name):
                for token in HEX.findall(value):
                    self.assertIn(token, {ETCH_DARK, WHITE})

    def test_root_rule_is_the_white_page(self):
        self.assertEqual(self.rules[ROOT], REQUIRED_PREFERENCES_RULES[ROOT])
        self.assertEqual(
            self.rules[ROOT]["background-color"],
            REQUIRED_RULES[LIST]["background-color"],
        )
        self.assertEqual(
            self.rules[ROOT]["background-color"],
            REQUIRED_CONFIG_RULES[CONFIG_PREFS]["background-color"],
        )

    def test_heading_band_is_the_etched_rule_with_black_text(self):
        self.assertEqual(
            self.rules[HEADING],
            REQUIRED_PREFERENCES_RULES[HEADING],
        )
        for name, value in self.rules[HEADING].items():
            with self.subTest(property=name):
                for token in HEX.findall(value):
                    self.assertIn(token, {ETCH_DARK, WHITE, BLACK})

    def test_heading_selector_avoids_page_chrome(self):
        for selector in (self.ROOT, self.HEADING):
            with self.subTest(selector=selector):
                for token in FORBIDDEN_PAGE_CHROME:
                    self.assertNotIn(token, selector)

    def test_header_names_preferences_provenance(self):
        self.assert_header_names(
            (
                "No reference shows Firefox's about:preferences",
                "widgets/listitem.svg",
                "widgets/viewitem.svg",
                "test_selection_background",
                "moz-page-nav#categories",
                "moz-page-nav-button.css",
                "::part",
                "preferences.xhtml",
                "2026-10-27",
                "platform colour adaptation 2026-10-27",
                "nav-separator",
                "moz-page-nav.css",
                "widgets/line.svg",
                "test_desktoptheme_line.py",
                "common-shared.css",
                "preferences.css",
                "test_window_view_background",
                "#mainPrefPane",
            )
        )


class TestFirefoxPreferencesSearchTheme(SheetCase):
    AT_RULE_URL = "about:preferences"

    def test_search_field_rule_sets_only_custom_properties(self):
        declarations = self.rules[SEARCH]
        self.assertTrue(declarations)
        for name in declarations:
            with self.subTest(property=name):
                self.assertTrue(
                    name.startswith("--input-text-") or name == "--icon-color"
                )

    def test_search_field_is_the_line_edit(self):
        self.assertEqual(self.rules[SEARCH], REQUIRED_PREFERENCES_RULES[SEARCH])
        for name, value in self.rules[SEARCH].items():
            with self.subTest(property=name):
                for token in HEX.findall(value):
                    self.assertIn(token, {WHITE, BLACK})

    def test_search_field_selector_avoids_page_chrome(self):
        for token in FORBIDDEN_PAGE_CHROME:
            self.assertNotIn(token, SEARCH)
        self.assertIn("moz-input-search", SEARCH)
        self.assertIn("#searchInput", SEARCH)

    def test_header_names_search_provenance(self):
        self.assert_header_names(
            (
                "html:moz-input-search#searchInput",
                "preferences.xhtml",
                "moz-input-text.css",
                "tokens-shared.css",
                "--icon-color",
                "::part",
                "sunken bevel",
                "2026-10-27",
                "platform colour adaptation 2026-10-27",
            )
        )


class TestFirefoxPreferencesPushButtonsTheme(SheetCase):
    AT_RULE_URL = "about:preferences"

    def test_push_button_rules_are_the_sheet_recipe(self):
        """Both pane-button rules equal the userChrome push-button recipe."""
        self.assertEqual(self.rules[PANE_BUTTON], REQUIRED_PREFERENCES_RULES[PANE_BUTTON])
        self.assertEqual(self.rules[PANE_BUTTON], BUTTON_RULE)
        self.assertEqual(
            self.rules[PANE_BUTTON_HOVER],
            REQUIRED_PREFERENCES_RULES[PANE_BUTTON_HOVER],
        )
        self.assertEqual(self.rules[PANE_BUTTON_HOVER], BUTTON_HOVER_RULE)

    def test_push_button_rules_scope_to_the_pane(self):
        for selector in (PANE_BUTTON, PANE_BUTTON_HOVER):
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith("#mainPrefPane button"))
                self.assertIn(":not(.arrowhead)", selector)
        self.assertIn(":not([disabled])", PANE_BUTTON)
        self.assertIn(":not([disabled])", PANE_BUTTON_HOVER)
        for token in ("#dialogTemplate", "dialogClose", "sidebar-", "categories"):
            with self.subTest(token=token):
                self.assertNotIn(token, PANE_BUTTON)
                self.assertNotIn(token, PANE_BUTTON_HOVER)

    def test_push_button_rules_use_the_pinned_palette(self):
        for selector in (PANE_BUTTON, PANE_BUTTON_HOVER):
            declarations = self.rules[selector]
            with self.subTest(selector=selector):
                self.assertTrue(declarations)
            for name, value in declarations.items():
                with self.subTest(property=name):
                    if name in ("background-color", "color", "border", "box-shadow"):
                        self.assertIn("!important", value)
                    for token in HEX.findall(value):
                        self.assertIn(token, {WHITE, BLACK, FACE, BUTTON_SHADOW, SELECTION})

    def test_header_names_buttons_provenance(self):
        self.assert_header_names(
            (
                "#mainPrefPane",
                ".arrowhead",
                "#dialogTemplate",
                "in-content/common-shared.css",
                "tokens-shared.css",
                "tokens-brand.css",
                "preferences.css",
                "widgets/button.svg",
                "tests/test_desktoptheme_button.py",
                "widgets/viewitem.svg",
                "platform colour adaptation 2026-10-27",
                "2026-10-27",
            )
        )


class TestFirefoxConfigTheme(SheetCase):
    AT_RULE_URL = "about:config"

    def test_required_rules(self):
        for selector, expected in REQUIRED_CONFIG_RULES.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)

    def test_parsed_rules_are_exactly_the_config_rules(self):
        self.assertEqual(set(self.rules), set(REQUIRED_CONFIG_RULES))
        self.assertEqual(self.selectors, list(REQUIRED_CONFIG_RULES))

    def test_config_rules_are_scoped_to_the_prefs_table_and_controls(self):
        for selector in self.selectors:
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith(CONFIG_CONTROL_PREFIXES))
                for token in CONFIG_UNTOUCHED:
                    self.assertNotIn(token, selector)

    def test_config_selector_guards_the_empty_table(self):
        self.assertIn(":not(:empty)", CONFIG_PREFS)
        self.assertIn(CONFIG_PREFS, self.selectors)
        self.assertEqual(self.rules[CONFIG_PREFS], FIELD_RULE)

    def test_header_names_config_provenance(self):
        self.assert_header_names(
            (
                "No reference shows Firefox's about:config",
                "widgets/lineedit.svg",
                "widgets/listitem.svg",
                "widgets/button.svg",
                "tests/test_desktoptheme_button_reference.py::TestButtonReference",
                "test_view_background_alternate",
                "test_selection_background",
                "aboutconfig.html",
                "aboutconfig.js",
                "aboutconfig.css",
                "common-shared.css",
                "#prefs",
                "#about-config-search",
                "#show-all",
                "#warningButton",
                "platform colour adaptation 2026-10-26",
            )
        )


if __name__ == "__main__":
    unittest.main()
