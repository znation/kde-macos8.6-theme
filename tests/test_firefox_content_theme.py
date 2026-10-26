"""Validate the standalone Firefox Platinum ``userContent.css`` sheet.

No reference screenshot shows Firefox's content-area downloads page, so the
palette is the shared Platinum palette and the geometry adapts this theme's
line-edit field and list-item row. The opt-in profile install copies it
beside userChrome.css through make install-firefox.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from support import containment
from support.gtk_css import HEX, parse_css, strip_comments
from support.platinum_palette import BLACK, GREY, SELECTION, WHITE
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

AT_RULE = re.compile(
    r'@-moz-document\s+url\("about:downloads"\)\s*\{(?P<body>.*)\}',
    re.DOTALL,
)

PAGE_CHROME = (
    "downloadButton",
    "downloadsHistory",
    "downloadsListEmptyDescription",
    "downloadsContextMenu",
    "hover",
)


class TestFirefoxContentTheme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = containment.read_text(SHEET, ROOT, encoding="utf-8")
        cls.colours, cls.rules, cls.selectors = parse_css(
            cls.text, source=SHEET_PATH
        )

    def test_first_line_is_the_marker(self):
        first_line = self.text.removeprefix("\ufeff").splitlines()[0]
        self.assertEqual(first_line, MARKER)

    def test_sheet_is_one_about_downloads_at_rule(self):
        stripped = strip_comments(self.text).strip()
        self.assertEqual(stripped.count("@"), 1)
        match = AT_RULE.fullmatch(stripped)
        self.assertIsNotNone(match)
        body = match.group("body")
        for selector in REQUIRED_RULES:
            with self.subTest(selector=selector):
                self.assertIn(selector, body)
        self.assertEqual(len(self.selectors), len(REQUIRED_RULES))

    def test_required_rules(self):
        for selector, expected in REQUIRED_RULES.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)

    def test_parsed_rules_are_exactly_the_three_list_rules(self):
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
            {WHITE, BLACK, GREY, SELECTION},
        )

    def test_sheet_does_not_import_or_name_adwaita(self):
        self.assertNotIn("@import", self.text)
        self.assertNotIn("adwaita", self.text.lower())

    def test_selectors_are_not_universal(self):
        for selector in self.selectors:
            self.assertNotIn("*", selector)

    def test_header_names_provenance(self):
        header = self.text.split("*/", 1)[0]
        for provenance in (
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
            "part 2/2",
        ):
            with self.subTest(provenance=provenance):
                self.assertIn(provenance, header)


if __name__ == "__main__":
    unittest.main()
