"""Validate the ``userContent.css`` sheet's ``about:networking`` paint.

The page's ten ``.main-content`` tables are the sunken list field with the
raised column-header face and the page's four buttons the Platinum push
button. The sidebar rows use the Platinum navigation paint, the ``#host``
input the sunken line edit, and the ``#autorefcheck`` checkbox the
preferences checkbox face and shipped check-mark glyph; the body stays
Firefox's. The shared spec values and base case live
in ``tests/support/firefox_content_cases.py``.
"""

from __future__ import annotations

import unittest

from support.firefox_content_cases import (
    FORBIDDEN_PAGE_CHROME,
    NETWORKING_BUTTONS,
    NETWORKING_CATEGORY,
    NETWORKING_CATEGORY_HOVER,
    NETWORKING_CATEGORY_SELECTED,
    NETWORKING_CHECK_CHECKED,
    NETWORKING_HEADER_HOVER,
    NETWORKING_HOST,
    NETWORKING_LIST,
    NETWORKING_SELECTORS,
    NETWORKING_TD,
    NETWORKING_TH,
    NETWORKING_ZEBRA,
    REQUIRED_NETWORKING_RULES,
    FirefoxContentTestCase,
    decodes_to_the_shipped_checkmark,
)
from support.gtk_css import HEX
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
from support.selector_matching import element, matches


class TestFirefoxNetworkingTheme(FirefoxContentTestCase):
    AT_RULE_URL = "about:networking"

    def test_networking_rules_match_the_required_rules(self):
        for selector, expected in REQUIRED_NETWORKING_RULES.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)

    def test_parsed_rules_are_exactly_the_networking_rules(self):
        self.assertEqual(set(self.rules), set(REQUIRED_NETWORKING_RULES))
        self.assertEqual(self.selectors, list(NETWORKING_SELECTORS))

    def test_networking_rules_scope_to_the_main_content_div(self):
        """The field, header, button, sidebar, host and check arms match.

        The zebra arm's ``:nth-child(2n)``, the comma-list cell and
        button arms and now the ``:checked`` and ``:hover:active`` arms
        are outside the matcher's subset, so they are pinned by their
        selector text and by
        ``test_parsed_rules_are_exactly_the_networking_rules`` instead of a
        fixture match.
        """
        main_content = element("div", None, classes=("main-content",))
        table = element("table", None, parent=main_content)
        header = element("th", None, parent=table)
        self.assertTrue(matches(NETWORKING_LIST, table))
        self.assertFalse(
            matches(
                NETWORKING_LIST,
                element("table", None, parent=element("div", "other")),
            )
        )
        self.assertTrue(matches(NETWORKING_TH, header))
        self.assertTrue(
            matches(
                NETWORKING_HEADER_HOVER,
                element("th", None, hover=True, parent=table),
            )
        )
        self.assertFalse(matches(NETWORKING_HEADER_HOVER, header))
        self.assertIn(":nth-child(2n)", NETWORKING_ZEBRA)
        self.assertIn(NETWORKING_TD, self.text)
        for arm in NETWORKING_BUTTONS:
            with self.subTest(arm=arm):
                self.assertTrue(matches(arm, element("button", arm[1:])))
                self.assertIn(arm + ":hover:not(:disabled)", self.text)
        chrome_button = element("button", "PlacesToolbar")
        for arm in NETWORKING_BUTTONS:
            with self.subTest(arm=arm):
                self.assertFalse(matches(arm, chrome_button))
        categories = element("div", "categories")
        row = element(
            "div",
            None,
            classes=("category", "category-no-icon"),
            parent=categories,
        )
        self.assertTrue(matches(NETWORKING_CATEGORY, row))
        self.assertTrue(
            matches(
                NETWORKING_CATEGORY_HOVER[0],
                element(
                    "div",
                    None,
                    classes=("category", "category-no-icon"),
                    hover=True,
                    parent=categories,
                ),
            )
        )
        self.assertFalse(matches(NETWORKING_CATEGORY_HOVER[0], row))
        self.assertTrue(
            matches(
                NETWORKING_CATEGORY_SELECTED[0],
                element(
                    "div",
                    None,
                    classes=("category", "category-no-icon"),
                    attrs={"selected": "true"},
                    parent=categories,
                ),
            )
        )
        self.assertFalse(matches(NETWORKING_CATEGORY_SELECTED[0], row))
        other_row = element(
            "div",
            None,
            classes=("category", "category-no-icon"),
            parent=element("div", "othersidebar"),
        )
        for selector in (
            NETWORKING_CATEGORY,
            *NETWORKING_CATEGORY_HOVER,
            *NETWORKING_CATEGORY_SELECTED,
        ):
            with self.subTest(selector=selector):
                self.assertFalse(matches(selector, other_row))
        orphan = element("button", "category-http")
        for selector in (
            NETWORKING_CATEGORY,
            *NETWORKING_CATEGORY_HOVER,
            *NETWORKING_CATEGORY_SELECTED,
        ):
            with self.subTest(selector=selector):
                self.assertFalse(matches(selector, orphan))
        host = element(
            "input",
            "host",
            attrs={"type": "text"},
            parent=element(
                "div", "dnslookuptool", parent=main_content
            ),
        )
        self.assertTrue(matches(NETWORKING_HOST, host))
        self.assertFalse(
            matches(
                NETWORKING_HOST,
                element("input", None, parent=main_content),
            )
        )
        for selector in self.selectors:
            with self.subTest(selector=selector):
                for token in FORBIDDEN_PAGE_CHROME:
                    self.assertNotIn(token, selector)

    def test_networking_rules_use_the_pinned_palette(self):
        allowed = {
            BLACK,
            WHITE,
            GREY,
            FACE,
            TROUGH,
            SELECTION,
            BUTTON_SHADOW,
            ETCH_DARK,
        }
        seen = set()
        for selector, expected in REQUIRED_NETWORKING_RULES.items():
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
        body = self.bodies["about:networking"]
        self.assertEqual(
            set(HEX.findall(body)),
            {
                WHITE,
                BLACK,
                GREY,
                FACE,
                TROUGH,
                SELECTION,
                BUTTON_SHADOW,
                ETCH_DARK,
            },
        )

    def test_checked_glyph_uri_pins_the_checkmarks_glyph(self):
        """Decoding the #autorefcheck data URI yields the shipped glyph."""
        decodes_to_the_shipped_checkmark(
            self.rules[NETWORKING_CHECK_CHECKED]["background-image"]
        )

    def test_header_names_networking_provenance(self):
        self.assert_header_names(
            (
                "No reference shows Firefox's about:networking",
                "aboutNetworking.html",
                "aboutNetworking.js",
                "attachShadow",
                "an .html document",
                ".main-content",
                "#refreshButton",
                "#clearHTTPCache",
                "#clearDNSCache",
                "#dnsLookupButton",
                "aboutNetworking.css",
                "in-content/common.css",
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
                "#categories",
                "#host",
                "#autorefcheck",
                "#autorefcheck:checked",
                "in-content/common-shared.css",
                "about:preferences",
                "aboutNetworking.js",
                "#sectionTitle",
                "a later plan",
                "top-level in a tab",
                "headless",
                "@-moz-document url(\"about:networking\")",
                "declaration checks do",
                "platform colour adaptation 2026-10-27",
            )
        )


if __name__ == "__main__":
    unittest.main()
