"""Validate the ``userContent.css`` sheet's ``about:telemetry`` paint.

The page's furniture takes the landed paints: the sidebar rows and their
selected arm, the subsection label, the search field and the stores menu
button and ping-picker panel. Payload tables, histograms and their bars,
and copy and JSON-viewer buttons reuse the landed recipes; the body stays
Firefox's. The shared spec values and base case live in
``tests/support/firefox_content_cases.py``.
"""

from __future__ import annotations

import unittest

from support.firefox_content_cases import (
    FORBIDDEN_PAGE_CHROME,
    TELEMETRY_BAR_INNER,
    TELEMETRY_COPY,
    TELEMETRY_COPY_HOVER,
    TELEMETRY_HEADER_HOVER,
    TELEMETRY_HISTOGRAM,
    TELEMETRY_JSON_BUTTON,
    TELEMETRY_JSON_BUTTON_HOVER,
    TELEMETRY_TABLE,
    TELEMETRY_TD,
    TELEMETRY_TH,
    TELEMETRY_ZEBRA,

    REQUIRED_TELEMETRY_RULES,
    TELEMETRY_ROW,
    TELEMETRY_ROW_HOVER,
    TELEMETRY_ROW_SELECTED,
    TELEMETRY_SEARCH,
    TELEMETRY_SELECTORS,
    TELEMETRY_STORES,
    TELEMETRY_STORES_HOVER,
    TELEMETRY_SUBSECTION,
    TELEMETRY_SUBSECTION_SELECTED,
    FirefoxContentTestCase,
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


class TestFirefoxTelemetryTheme(FirefoxContentTestCase):
    AT_RULE_URL = "about:telemetry"

    def test_telemetry_rules_match_the_required_rules(self):
        for selector, expected in REQUIRED_TELEMETRY_RULES.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)

    def test_parsed_rules_are_exactly_the_telemetry_rules(self):
        self.assertEqual(set(self.rules), set(REQUIRED_TELEMETRY_RULES))
        self.assertEqual(self.selectors, list(TELEMETRY_SELECTORS))

    def test_telemetry_rules_scope_to_page_furniture(self):
        """The row, subsection, field, store, panel and payload arms match.

        ``:hover`` is the matcher's only pseudo-class, so the ``:hover:active``
        row arms are pinned by their selector text and by
        ``test_parsed_rules_are_exactly_the_telemetry_rules`` instead of a
        fixture match, as the networking scope test pins its
        ``:hover:active`` arm.
        """
        categories = element("div", "categories")
        row = element(
            "div",
            None,
            classes=("category", "category-no-icon"),
            parent=categories,
        )
        self.assertTrue(matches(TELEMETRY_ROW, row))
        self.assertFalse(matches(TELEMETRY_ROW_HOVER[0], row))
        self.assertTrue(
            matches(
                TELEMETRY_ROW_HOVER[0],
                element(
                    "div",
                    None,
                    classes=("category", "category-no-icon"),
                    hover=True,
                    parent=categories,
                ),
            )
        )
        self.assertIn(TELEMETRY_ROW_HOVER[1], self.text)
        selected_row = element(
            "div",
            None,
            classes=("category", "category-no-icon", "selected"),
            parent=categories,
        )
        self.assertTrue(matches(TELEMETRY_ROW_SELECTED[0], selected_row))
        self.assertTrue(
            matches(
                TELEMETRY_ROW_SELECTED[1],
                element(
                    "div",
                    None,
                    classes=("category", "category-no-icon", "selected"),
                    hover=True,
                    parent=categories,
                ),
            )
        )
        self.assertIn(TELEMETRY_ROW_SELECTED[2], self.text)
        self.assertFalse(matches(TELEMETRY_ROW_HOVER[0], selected_row))
        subsection = element(
            "div", None, classes=("category-subsection",), parent=selected_row
        )
        self.assertTrue(matches(TELEMETRY_SUBSECTION, subsection))
        self.assertFalse(matches(TELEMETRY_SUBSECTION_SELECTED, subsection))
        selected_subsection = element(
            "div",
            None,
            classes=("category-subsection", "selected"),
            parent=selected_row,
        )
        self.assertTrue(matches(TELEMETRY_SUBSECTION_SELECTED, selected_subsection))
        other_row = element(
            "div",
            None,
            classes=("category", "category-no-icon"),
            parent=element("div", "othersidebar"),
        )
        for selector in (
            TELEMETRY_ROW,
            *TELEMETRY_ROW_HOVER,
            *TELEMETRY_ROW_SELECTED,
            TELEMETRY_SUBSECTION,
            TELEMETRY_SUBSECTION_SELECTED,
        ):
            with self.subTest(selector=selector):
                self.assertFalse(matches(selector, other_row))
        span_row = element("span", None, classes=("category",))
        for selector in (
            TELEMETRY_ROW,
            *TELEMETRY_ROW_HOVER,
            *TELEMETRY_ROW_SELECTED,
        ):
            with self.subTest(selector=selector):
                self.assertFalse(matches(selector, span_row))
        search = element(
            "input",
            "search",
            attrs={"type": "text"},
            parent=element("div", "sectionFilters"),
        )
        self.assertTrue(matches(TELEMETRY_SEARCH, search))
        self.assertFalse(matches(TELEMETRY_SEARCH, element("input")))
        stores = element("select", "stores")
        self.assertTrue(matches(TELEMETRY_STORES, stores))
        self.assertTrue(
            matches(TELEMETRY_STORES_HOVER, element("select", "stores", hover=True))
        )
        self.assertFalse(matches(TELEMETRY_STORES_HOVER, stores))
        main = element("div", "main", classes=("main-content",))
        data = element("div", None, classes=("data",), parent=main)
        table = element("table", None, parent=data)
        self.assertTrue(matches(TELEMETRY_TABLE, table))
        self.assertFalse(
            matches(
                TELEMETRY_TABLE,
                element("table", None, parent=element("div", "other")),
            )
        )
        header = element("th", None, parent=table)
        self.assertTrue(matches(TELEMETRY_TH, header))
        self.assertTrue(matches(TELEMETRY_TD, element("td", None, parent=table)))
        self.assertTrue(
            matches(
                TELEMETRY_HEADER_HOVER,
                element("th", None, hover=True, parent=table),
            )
        )
        self.assertFalse(matches(TELEMETRY_HEADER_HOVER, header))
        # The zebra arm's :nth-child(2n) is outside the matcher's subset,
        # as the support scope test records, so it is pinned by text.
        self.assertIn(":nth-child(2n)", TELEMETRY_ZEBRA)
        histogram = element("div", None, classes=("histogram",))
        self.assertTrue(matches(TELEMETRY_HISTOGRAM, histogram))
        bar = element("div", None, classes=("bar",), parent=histogram)
        bar_inner = element("div", None, classes=("bar-inner",), parent=bar)
        for selector in (
            TELEMETRY_TABLE,
            TELEMETRY_ZEBRA,
            TELEMETRY_TH,
            TELEMETRY_TD,
            TELEMETRY_HEADER_HOVER,
            TELEMETRY_HISTOGRAM,
            TELEMETRY_BAR_INNER,
            TELEMETRY_COPY,
            TELEMETRY_COPY_HOVER,
            TELEMETRY_JSON_BUTTON,
            TELEMETRY_JSON_BUTTON_HOVER,
        ):
            with self.subTest(selector=selector):
                self.assertFalse(matches(selector, bar))
        self.assertTrue(matches(TELEMETRY_BAR_INNER, bar_inner))
        self.assertFalse(matches(TELEMETRY_BAR_INNER, bar))
        copy_button = element("button", None, classes=("copy-node",))
        self.assertTrue(matches(TELEMETRY_COPY, copy_button))
        self.assertFalse(matches(TELEMETRY_COPY_HOVER, copy_button))
        self.assertTrue(
            matches(
                TELEMETRY_COPY_HOVER,
                element("button", None, classes=("copy-node",), hover=True),
            )
        )
        self.assertTrue(matches(TELEMETRY_JSON_BUTTON, element("button", "payload-json-viewer")))
        other_button = element("button", "other")
        self.assertFalse(matches(TELEMETRY_JSON_BUTTON, other_button))
        self.assertFalse(matches(TELEMETRY_JSON_BUTTON_HOVER, other_button))
        self.assertFalse(matches(TELEMETRY_JSON_BUTTON, copy_button))
        for selector in self.selectors:
            with self.subTest(selector=selector):
                for token in FORBIDDEN_PAGE_CHROME:
                    self.assertNotIn(token, selector)

    def test_telemetry_rules_use_the_pinned_palette(self):
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
        for selector, expected in REQUIRED_TELEMETRY_RULES.items():
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
        body = self.bodies["about:telemetry"]
        self.assertLessEqual(set(HEX.findall(body)), allowed)

    def test_header_names_telemetry_provenance(self):
        self.assert_header_names(
            (
                "No reference shows Firefox's about:telemetry",
                "aboutTelemetry.js",
                ".category.selected",
                "common-shared.css",
                "#search",
                "#stores",
                "#ping-picker",
                "test_selection_background",
                "widgets/lineedit.svg",
                "tests/test_desktoptheme_lineedit.py::TestLineEdit",
                "TestLineEditReference",
                "PANE_MENULIST_RULE",
                "PANE_MENULIST_HOVER_RULE",
                "no reference",
                "#sectionTitle",
                ".main-content table",
                ".histogram",
                ".bar-inner",
                ".copy-node",
                "#payload-json-viewer",
                "widgets/bar_meter_horizontal.svg",
                "TestProgressBar",
                "BUTTON_RULE",
                "@-moz-document url(\"about:telemetry\")",
                "platform colour adaptation 2026-10-27",
            )
        )


if __name__ == "__main__":
    unittest.main()
