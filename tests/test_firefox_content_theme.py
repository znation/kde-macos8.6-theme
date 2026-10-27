"""Validate the standalone Firefox Platinum ``userContent.css`` sheet.

No reference screenshot shows Firefox's content-area downloads page or its
about:config page, so the palette is the shared Platinum palette and the
geometry adapts this theme's line-edit field, list-item row and push button.
The opt-in profile install copies the sheet beside userChrome.css through
make install-firefox.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from support import containment
from support.gtk_css import HEX, parse_css, strip_comments
from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
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


class SheetCase(unittest.TestCase):
    """Shared fixture for the two classes testing ``userContent.css``.

    Both read the shipped sheet, split it into ``@-moz-document`` bodies and
    parse exactly one of them; the class attribute ``AT_RULE_URL`` names which.
    :meth:`assert_header_names` serves the two provenance tests.
    """

    AT_RULE_URL: str

    @classmethod
    def setUpClass(cls):
        cls.text = containment.read_text(SHEET, ROOT, encoding="utf-8")
        cls.bodies = at_rule_bodies(cls.text)
        cls.colours, cls.rules, cls.selectors = parse_css(
            cls.bodies.get(cls.AT_RULE_URL, ""), source=SHEET_PATH
        )

    def assert_header_names(self, provenances):
        """Assert the comment header before the first ``*/`` names each entry."""
        header = self.text.split("*/", 1)[0]
        for provenance in provenances:
            with self.subTest(provenance=provenance):
                self.assertIn(provenance, header)


class TestFirefoxContentTheme(SheetCase):
    AT_RULE_URL = "about:downloads"

    def test_first_line_is_the_marker(self):
        first_line = self.text.removeprefix("\ufeff").splitlines()[0]
        self.assertEqual(first_line, MARKER)

    def test_sheet_has_the_downloads_and_config_at_rules(self):
        stripped = strip_comments(self.text).strip()
        self.assertEqual(set(self.bodies), {"about:downloads", "about:config"})
        self.assertEqual(stripped.count("@"), 2)
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

    def test_palette_is_exact(self):
        self.assertEqual(
            set(HEX.findall(self.text)),
            {WHITE, BLACK, GREY, SELECTION, FACE, TROUGH, BUTTON_SHADOW},
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
