"""Validate the ``userContent.css`` sheet's ``about:support`` paint.

The troubleshooting page's ``#contents`` tables are the sunken list field
with the raised column-header face and the page's ten buttons the
Platinum push button; the body, headings and the ``.action-box`` card
stay Firefox's. The shared spec values and base case live in
``tests/support/firefox_content_cases.py``.
"""

from __future__ import annotations

import unittest

from support.firefox_content_cases import (
    FORBIDDEN_PAGE_CHROME,
    REQUIRED_SUPPORT_RULES,
    SUPPORT_BUTTONS,
    SUPPORT_HEADER_HOVER,
    SUPPORT_LIST,
    SUPPORT_SELECTORS,
    SUPPORT_TD,
    SUPPORT_TH,
    SUPPORT_ZEBRA,
    FirefoxContentTestCase,
)
from support.gtk_css import HEX
from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    GREY,
    SELECTION,
    TROUGH,
    WHITE,
)
from support.selector_matching import element, matches


class TestFirefoxSupportTheme(FirefoxContentTestCase):
    AT_RULE_URL = "about:support"

    def test_support_rules_match_the_required_rules(self):
        for selector, expected in REQUIRED_SUPPORT_RULES.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)

    def test_parsed_rules_are_exactly_the_support_rules(self):
        self.assertEqual(set(self.rules), set(REQUIRED_SUPPORT_RULES))
        self.assertEqual(self.selectors, list(SUPPORT_SELECTORS))

    def test_support_table_rules_scope_to_the_contents_div(self):
        """The field, header and hover arms match nodes inside #contents.

        The zebra arm's ``:nth-child(2n)`` and the comma-list cell arm are
        outside the matcher's subset, so they are pinned by their selector
        text and by ``test_parsed_rules_are_exactly_the_support_rules``
        instead of a fixture match.
        """
        contents = element("div", "contents")
        table = element("table", None, parent=contents)
        header = element("th", None, classes=("column",), parent=table)
        self.assertTrue(matches(SUPPORT_LIST, table))
        self.assertFalse(
            matches(
                SUPPORT_LIST,
                element("table", None, parent=element("div", "other")),
            )
        )
        self.assertTrue(matches(SUPPORT_TH, header))
        self.assertTrue(
            matches(
                SUPPORT_HEADER_HOVER,
                element(
                    "th", None, classes=("column",), hover=True, parent=table,
                ),
            )
        )
        self.assertFalse(matches(SUPPORT_HEADER_HOVER, header))
        self.assertIn(":nth-child(2n)", SUPPORT_ZEBRA)
        self.assertIn(SUPPORT_TH, self.text)
        self.assertIn(SUPPORT_TD, self.text)
        for selector in self.selectors:
            with self.subTest(selector=selector):
                for token in FORBIDDEN_PAGE_CHROME:
                    self.assertNotIn(token, selector)

    def test_support_buttons_scope_to_the_page_ids(self):
        """The button arms name the page's ten ids and the .action-box arm.

        The comma-list face selector is outside the matcher's subset, so the
        scope check matches each arm's own compound and pins the hover's
        ``:not(:disabled)`` guard by text.
        """
        for arm in SUPPORT_BUTTONS:
            with self.subTest(arm=arm):
                self.assertIn(arm, self.text)
                self.assertIn(arm + ":hover:not(:disabled)", self.text)
        action_box = element("div", "box-container", classes=("action-box",))
        self.assertTrue(matches(
            ".action-box button", element("button", None, parent=action_box)
        ))
        self.assertTrue(matches(
            "#copy-to-clipboard", element("button", "copy-to-clipboard")
        ))
        self.assertFalse(matches(
            "#copy-raw-data-to-clipboard", element("button", "copy-to-clipboard")
        ))
        chrome_button = element("button", "PlacesToolbar")
        self.assertFalse(matches("#copy-to-clipboard", chrome_button))
        self.assertFalse(
            matches(".action-box button", element("button", None))
        )

    def test_support_rules_use_the_pinned_palette(self):
        allowed = {
            BLACK,
            WHITE,
            GREY,
            FACE,
            TROUGH,
            SELECTION,
            BUTTON_SHADOW,
        }
        seen = set()
        for selector, expected in REQUIRED_SUPPORT_RULES.items():
            declarations = self.rules[selector]
            with self.subTest(selector=selector):
                self.assertEqual(declarations, expected)
                self.assertTrue(declarations)
            for name, value in declarations.items():
                with self.subTest(selector=selector, property=name):
                    self.assertIn("!important", value)
                    for token in HEX.findall(value):
                        seen.add(token)
                        self.assertIn(token, allowed)
        self.assertTrue(seen)
        body = self.bodies["about:support"]
        self.assertEqual(
            set(HEX.findall(body)),
            {WHITE, BLACK, GREY, FACE, TROUGH, SELECTION, BUTTON_SHADOW},
        )

    def test_header_names_support_provenance(self):
        self.assert_header_names(
            (
                "No reference shows Firefox's about:support",
                "aboutSupport.xhtml",
                "aboutSupport.js",
                "attachShadow",
                "#copy-raw-data-to-clipboard",
                "#clear-startup-cache-button",
                "#place-database-stats-toggle",
                ".action-box",
                "th class=\"column\"",
                "th class=\"name\"",
                "#codec-table",
                "widgets/lineedit.svg",
                "tests/test_desktoptheme_lineedit.py::TestLineEdit",
                "test_view_background_alternate",
                "widgets/tabbar.svg",
                "tests/test_desktoptheme_tabbar.py::TestTabBar",
                "TestTabBarReference",
                "test_selection_background",
                "widgets/button.svg",
                "tests/test_desktoptheme_button_reference.py::TestButtonReference",
                ":disabled",
                "about:logins",
                "about:addons",
                "::part",
                "top-level in a tab",
                "headless",
                "@-moz-document url(\"about:support\")",
                "declaration checks do",
                "platform colour adaptation 2026-10-27",
            )
        )


if __name__ == "__main__":
    unittest.main()
