"""Validate about:preferences entry-field and menulist declarations."""

from __future__ import annotations

import unittest

from support.firefox.content_cases import (
    BUTTON_SHADOW,
    FACE,
    GREY,
    PANEFIELD,
    PANEFIELD_RULE,
    PANE_MENULIST,
    PANE_MENULIST_HOVER,
    PANE_MENULIST_HOVER_RULE,
    PANE_MENULIST_OPEN,
    PANE_MENULIST_RULE,
    REQUIRED_PREFERENCES_RULES,
    SELECTION,
    FirefoxContentTestCase,
)
from support.firefox_content_palette import assert_palette_declarations
from support.platinum_palette import BLACK, WHITE
from support.firefox.selector_matching import element, matches


class TestFirefoxPreferencesFieldsTheme(FirefoxContentTestCase):
    AT_RULE_URL = "about:preferences"

    def test_field_and_menulist_rules_are_the_sheet_recipe(self):
        """All five arms equal the pinned field and menulist recipes."""
        self.assertEqual(self.rules[PANEFIELD], PANEFIELD_RULE)
        self.assertEqual(self.rules[PANEFIELD], REQUIRED_PREFERENCES_RULES[PANEFIELD])
        self.assertEqual(self.rules[PANE_MENULIST], PANE_MENULIST_RULE)
        self.assertEqual(self.rules[PANE_MENULIST], REQUIRED_PREFERENCES_RULES[PANE_MENULIST])
        for selector in (PANE_MENULIST_HOVER, PANE_MENULIST_OPEN):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], PANE_MENULIST_HOVER_RULE)
                self.assertEqual(self.rules[selector], REQUIRED_PREFERENCES_RULES[selector])

    def test_field_and_menulist_rules_extend_the_ordered_rule_register(self):
        """The four new arms close the about:preferences register in order.

        The two assertions mirror TestFirefoxPreferencesNavTheme's
        register checks, which read the same extended dict; the tail
        assertion pins the new arms as the block's last, so no earlier
        rule moved.
        """
        self.assertEqual(set(self.rules), set(REQUIRED_PREFERENCES_RULES))
        self.assertEqual(self.selectors, list(REQUIRED_PREFERENCES_RULES))
        self.assertEqual(self.selectors[-4:], [PANEFIELD, PANE_MENULIST, PANE_MENULIST_HOVER, PANE_MENULIST_OPEN])

    def test_field_and_menulist_rules_scope_to_the_pane(self):
        for selector in (PANEFIELD, PANE_MENULIST, PANE_MENULIST_HOVER, PANE_MENULIST_OPEN):
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith("#mainPrefPane"))
                for token in ("menupopup", "#dialogTemplate", "subdialog"):
                    self.assertNotIn(token, selector)
        self.assertIn('[type="text"]', PANEFIELD)
        self.assertIn(":not([disabled])", PANEFIELD)
        self.assertNotIn("moz-input-search", PANEFIELD)
        self.assertIn(":not([disabled])", PANE_MENULIST)
        self.assertTrue(PANE_MENULIST_HOVER.endswith(":hover"))
        self.assertIn('[open="true"]', PANE_MENULIST_OPEN)
        pane = element("vbox", "mainPrefPane")
        dialog = element("vbox", "dialogTemplate")
        self.assertTrue(matches(PANEFIELD, element("input", "homePageUrl", attrs={"type": "text"}, parent=pane)))
        self.assertFalse(matches(PANEFIELD, element("input", "homePageUrl", attrs={"type": "text", "disabled": "true"}, parent=pane)))
        self.assertFalse(matches(PANEFIELD, element("input", "homePageUrl", attrs={"type": "range"}, parent=pane)))
        self.assertTrue(matches(PANE_MENULIST, element("menulist", "homeMode", parent=pane)))
        self.assertFalse(matches(PANE_MENULIST, element("menulist", "homeMode", parent=dialog)))
        self.assertTrue(matches(PANE_MENULIST_HOVER, element("menulist", "homeMode", hover=True, parent=pane)))
        self.assertFalse(matches(PANE_MENULIST_HOVER, element("menulist", "homeMode", parent=pane)))
        self.assertTrue(matches(PANE_MENULIST_OPEN, element("menulist", "homeMode", attrs={"open": "true"}, parent=pane)))
        self.assertFalse(matches(PANE_MENULIST_OPEN, element("menulist", "homeMode", parent=pane)))

    def test_field_and_menulist_rules_use_the_pinned_palette(self):
        for selector, allowed in (
            (PANEFIELD, {WHITE, BLACK, GREY}),
            (PANE_MENULIST, {WHITE, BLACK, FACE, BUTTON_SHADOW}),
            (PANE_MENULIST_HOVER, {SELECTION, BLACK}),
            (PANE_MENULIST_OPEN, {SELECTION, BLACK}),
        ):
            assert_palette_declarations(self, (selector,), allowed)

    def test_header_names_field_provenance(self):
        self.assert_header_names((
            "preferences.xhtml", 'html:input[type="text"]', "#homePageUrl",
            "#dohEnabledInputField", "#dohStrictInputField", "#fxaSyncComputerName",
            "#primaryBrowserLocale", "#homeMode", "#newTabMode", "#blockCookiesMenu",
            "#trackingProtectionMenu", "#fingerprintingProtectionMenu", "#dohEnabledResolverChoices",
            "#dohStrictResolverChoices", "menulist", "common-shared.css",
            "--border-radius-medium", "--background-color-box", "tokens-shared.css",
            "tokens-brand.css", "menulist.css", "dropmarker", "arrow-down-12.svg",
            "currentColor", "browser/omni.ja", "#about-config-search", "widgets/lineedit.svg",
            "tests/test_desktoptheme_lineedit.py::TestLineEdit", "TestLineEditReference",
            "widgets/button.svg", "tests/test_desktoptheme_button.py::TestButton",
            "tests/test_desktoptheme_button_reference.py::TestButtonReference", "widgets/viewitem.svg",
            "tests/test_desktoptheme_viewitem.py::TestViewItem", "test_selection_background",
            '[open="true"]', "menupopup", ":not([disabled])", ":user-invalid", "sub-dialog",
            "platform colour adaptation 2026-10-27",
        ))


if __name__ == "__main__":
    unittest.main()
