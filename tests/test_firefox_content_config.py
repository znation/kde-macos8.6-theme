"""Validate the ``userContent.css`` sheet's ``about:config`` paint.

The preference table is the Platinum sunken list field with the pinned
alternate rows, its search field is the sunken line edit and Show All and
the warning page's primary button are the Platinum push buttons; the
warning copy, the row buttons and the page background stay Firefox's.
The shared spec values and base case live in
``tests/support/firefox_content_cases.py``.
"""

from __future__ import annotations

import unittest

from support.firefox_content_cases import (
    CONFIG_CONTROL_PREFIXES,
    CONFIG_PREFS,
    CONFIG_UNTOUCHED,
    FIELD_RULE,
    REQUIRED_CONFIG_RULES,
    FirefoxContentTestCase,
)


class TestFirefoxConfigTheme(FirefoxContentTestCase):
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
