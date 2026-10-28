"""Validate the whole ``userContent.css`` sheet and its about:downloads paint.

This module holds the sheet's global checks — the ``@-moz-document`` body
scanner's own tests, the marker first line, the at-rule enumeration, the
exact whole-sheet palette and the no-@import/Adwaita and
non-universal-selector hygiene — and the content-area downloads page's
rules, adapted from the shared Platinum palette and the lineedit/listitem
art. The other pages live in ``tests/test_firefox_content_config.py``,
``tests/test_firefox_content_preferences.py``,
``tests/test_firefox_content_support.py``,
``tests/test_firefox_content_networking.py`` and
``tests/test_firefox_content_telemetry.py``; the shared spec values and
base case live in ``tests/support/firefox_content_cases.py``. The opt-in
profile install copies the sheet beside userChrome.css through
make install-firefox.
"""

from __future__ import annotations

import unittest

from support.firefox_content_cases import (
    FORBIDDEN_PAGE_CHROME,
    LIST,
    MARKER,
    PAGE_CHROME,
    REQUIRED_RULES,
    ROW,
    SELECTED,
    SHEET_PATH,
    FirefoxContentTestCase,
    at_rule_bodies,
)
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


class TestAtRuleBodies(unittest.TestCase):
    """Pin the ``@-moz-document`` body scanner's token handling."""

    def test_escaped_quote_in_a_body_value_ends_at_the_at_rule_brace(self):
        # ``content: "\""`` holds an escaped quote: it must not end the
        # string, or the run-away string swallows every later brace and the
        # scanner merges the following rules into the first body and reports
        # the at-rule's own closing brace as part of it.
        text = (
            '@-moz-document url("about:downloads") {\n'
            '  #a::before { content: "\\""; color: red; }\n'
            "  #b { color: green; }\n"
            "}\n"
        )
        bodies = at_rule_bodies(text)
        self.assertEqual(set(bodies), {"about:downloads"})
        self.assertEqual(
            bodies["about:downloads"],
            '\n  #a::before { content: "\\""; color: red; }\n'
            "  #b { color: green; }\n",
        )

    def test_body_ends_at_the_at_rules_own_closing_brace(self):
        text = '@-moz-document url("about:config") {\n  #a { color: red; }\n}\n'
        self.assertEqual(
            at_rule_bodies(text)["about:config"], "\n  #a { color: red; }\n"
        )


class TestFirefoxContentTheme(FirefoxContentTestCase):
    AT_RULE_URL = "about:downloads"

    def test_first_line_is_the_marker(self):
        first_line = self.text.removeprefix("\ufeff").splitlines()[0]
        self.assertEqual(first_line, MARKER)

    def test_sheet_has_the_downloads_config_preferences_support_networking_and_telemetry_at_rules(
        self,
    ):
        stripped = strip_comments(self.text).strip()
        self.assertEqual(
            set(self.bodies),
            {
                "about:downloads",
                "about:config",
                "about:preferences",
                "about:support",
                "about:networking",
                "about:telemetry",
            },
        )
        self.assertEqual(stripped.count("@"), 6)
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

if __name__ == "__main__":
    unittest.main()
