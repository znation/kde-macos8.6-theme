"""Validate the ``userContent.css`` sheet's ``about:preferences`` paint.

The sidebar's category rows, the pane search field, push buttons, check
boxes, radio circles, entry fields and menulists are the shared Platinum
recipe set; the panes' other controls stay Firefox's. The shared spec
values and base case live in ``tests/support/firefox_content_cases.py``.
"""

from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree
from urllib.parse import unquote

from support.firefox_content_cases import (
    BUTTON_HOVER_RULE,
    BUTTON_RULE,
    CHECKBOX_FACE,
    CONFIG_PREFS,
    CHECKBOX_FACE_RULE,
    CHECKBOX_GLYPH,
    CHECKBOX_GLYPH_RULE,
    decodes_to_the_shipped_checkmark,
    FORBIDDEN_PAGE_CHROME,
    HEADING,
    HOST,
    LIST,
    NAV,
    PANE_BUTTON,
    PANE_BUTTON_HOVER,
    PANE_MENULIST,
    PANE_MENULIST_HOVER,
    PANE_MENULIST_HOVER_RULE,
    PANE_MENULIST_OPEN,
    PANE_MENULIST_RULE,
    PANEFIELD,
    PANEFIELD_RULE,
    RADIO_DOT,
    RADIO_DOT_RULE,
    RADIO_FACE,
    RADIO_FACE_RULE,
    REQUIRED_CONFIG_RULES,
    REQUIRED_PREFERENCES_RULES,
    REQUIRED_RULES,
    ROOT,
    SEPARATOR,
    SEARCH,
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
    WHITE,
)
from support.selector_matching import element, matches


class TestFirefoxPreferencesNavTheme(FirefoxContentTestCase):
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
class TestFirefoxPreferencesSearchTheme(FirefoxContentTestCase):
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
class TestFirefoxPreferencesPushButtonsTheme(FirefoxContentTestCase):
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
class TestFirefoxPreferencesCheckboxTheme(FirefoxContentTestCase):
    AT_RULE_URL = "about:preferences"

    def test_checkbox_rules_are_the_sheet_recipe(self):
        """Both checkbox rules equal the pinned face and glyph recipes."""
        self.assertEqual(self.rules[CHECKBOX_FACE], CHECKBOX_FACE_RULE)
        self.assertEqual(self.rules[CHECKBOX_FACE], REQUIRED_PREFERENCES_RULES[CHECKBOX_FACE])
        self.assertEqual(self.rules[CHECKBOX_GLYPH], CHECKBOX_GLYPH_RULE)
        self.assertEqual(
            self.rules[CHECKBOX_GLYPH], REQUIRED_PREFERENCES_RULES[CHECKBOX_GLYPH]
        )

    def test_checkbox_rules_scope_to_the_pane(self):
        for selector in (CHECKBOX_FACE, CHECKBOX_GLYPH):
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith("#mainPrefPane checkbox"))
                self.assertIn(":not([disabled])", selector)
        self.assertNotIn("[checked]", CHECKBOX_FACE)
        self.assertIn("[checked]", CHECKBOX_GLYPH)
        for token in ("moz-checkbox", "radio", "#dialogTemplate"):
            with self.subTest(token=token):
                self.assertNotIn(token, CHECKBOX_FACE)
                self.assertNotIn(token, CHECKBOX_GLYPH)

    def test_checkbox_rules_use_the_pinned_palette(self):
        for selector in (CHECKBOX_FACE, CHECKBOX_GLYPH):
            declarations = self.rules[selector]
            with self.subTest(selector=selector):
                self.assertTrue(declarations)
            for name, value in declarations.items():
                with self.subTest(property=name):
                    if name in ("background-color", "border", "box-shadow"):
                        self.assertIn("!important", value)
                    for token in HEX.findall(value):
                        self.assertIn(token, {WHITE, BLACK, FACE, ETCH_DARK})

    def test_checked_glyph_uri_pins_the_checkmarks_glyph(self):
        """Decoding the data URI yields the shipped checkmarks.svg glyph."""
        decodes_to_the_shipped_checkmark(
            self.rules[CHECKBOX_GLYPH]["background-image"]
        )

    def test_header_names_checkbox_provenance(self):
        self.assert_header_names(
            (
                "checkbox.css",
                "checkbox.js",
                "common-shared.css",
                "--checkbox-size",
                "tokens-shared.css",
                "preferences.css",
                "checkbox-normal",
                "checkbox-checked-normal",
                "org.macos8.desktop.svg",
                "widgets/checkmarks.svg",
                "tests/test_desktoptheme_checkmarks.py::TestCheckmarks",
                "rgb(0, 0, 0)",
                ":not([disabled])",
                "moz-checkbox",
                "radio",
                "platform colour adaptation 2026-10-27",
            )
        )
class TestFirefoxPreferencesRadioTheme(FirefoxContentTestCase):
    AT_RULE_URL = "about:preferences"

    def test_radio_rules_are_the_sheet_recipe(self):
        """Both radio rules equal the pinned face and dot recipes."""
        self.assertEqual(self.rules[RADIO_FACE], RADIO_FACE_RULE)
        self.assertEqual(
            self.rules[RADIO_FACE], REQUIRED_PREFERENCES_RULES[RADIO_FACE]
        )
        self.assertEqual(self.rules[RADIO_DOT], RADIO_DOT_RULE)
        self.assertEqual(
            self.rules[RADIO_DOT], REQUIRED_PREFERENCES_RULES[RADIO_DOT]
        )

    def test_radio_rules_scope_to_the_pane(self):
        for selector in (RADIO_FACE, RADIO_DOT):
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith("#mainPrefPane radio"))
                self.assertIn(":not([disabled])", selector)
        self.assertNotIn("[selected]", RADIO_FACE)
        self.assertIn("[selected]", RADIO_DOT)
        for token in ("checkbox", "moz-radio", "#dialogTemplate"):
            with self.subTest(token=token):
                self.assertNotIn(token, RADIO_FACE)
                self.assertNotIn(token, RADIO_DOT)

    def test_radio_rules_use_the_pinned_palette(self):
        for selector in (RADIO_FACE, RADIO_DOT):
            declarations = self.rules[selector]
            with self.subTest(selector=selector):
                self.assertTrue(declarations)
            for name, value in declarations.items():
                with self.subTest(property=name):
                    self.assertIn("!important", value)
                    for token in HEX.findall(value):
                        self.assertIn(token, {WHITE, BLACK})

    def test_selected_dot_uri_pins_the_radiobutton_dot(self):
        """Decoding the data URI yields the shipped checkmarks.svg dot."""
        value = self.rules[RADIO_DOT]["background-image"]
        match = re.search(r'url\("([^"]+)"\)', value)
        self.assertIsNotNone(match)
        payload = match.group(1)
        prefix = "data:image/svg+xml,"
        self.assertTrue(payload.startswith(prefix))
        svg = unquote(payload[len(prefix):])
        root = xml.etree.ElementTree.fromstring(svg)
        self.assertEqual(root.get("width"), "16")
        self.assertEqual(root.get("height"), "16")
        circles = list(root)
        self.assertEqual(len(circles), 1)
        self.assertEqual(circles[0].get("cx"), "8")
        self.assertEqual(circles[0].get("cy"), "8")
        self.assertEqual(circles[0].get("r"), "3")
        self.assertEqual(circles[0].get("fill"), "rgb(0, 0, 0)")
        self.assertNotIn("#", svg)

    def test_header_names_radio_provenance(self):
        self.assert_header_names(
            (
                "radio.css",
                "radio.js",
                "common-shared.css",
                "--checkbox-size",
                "radio-normal",
                "radio-checked-normal",
                "org.macos8.desktop.svg",
                "widgets/checkmarks.svg",
                "tests/test_desktoptheme_checkmarks.py::TestCheckmarks",
                "rgb(0, 0, 0)",
                ":not([disabled])",
                "[selected]",
                "moz-radio",
                "platform colour adaptation 2026-10-27",
            )
        )
class TestFirefoxPreferencesFieldsTheme(FirefoxContentTestCase):
    AT_RULE_URL = "about:preferences"

    def test_field_and_menulist_rules_are_the_sheet_recipe(self):
        """All five arms equal the pinned field and menulist recipes."""
        self.assertEqual(self.rules[PANEFIELD], PANEFIELD_RULE)
        self.assertEqual(
            self.rules[PANEFIELD], REQUIRED_PREFERENCES_RULES[PANEFIELD]
        )
        self.assertEqual(self.rules[PANE_MENULIST], PANE_MENULIST_RULE)
        self.assertEqual(
            self.rules[PANE_MENULIST], REQUIRED_PREFERENCES_RULES[PANE_MENULIST]
        )
        for selector in (PANE_MENULIST_HOVER, PANE_MENULIST_OPEN):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], PANE_MENULIST_HOVER_RULE)
                self.assertEqual(
                    self.rules[selector], REQUIRED_PREFERENCES_RULES[selector]
                )

    def test_field_and_menulist_rules_extend_the_ordered_rule_register(self):
        """The four new arms close the about:preferences register in order.

        The two assertions mirror TestFirefoxPreferencesNavTheme's
        register checks, which read the same extended dict; the tail
        assertion pins the new arms as the block's last, so no earlier
        rule moved.
        """
        self.assertEqual(set(self.rules), set(REQUIRED_PREFERENCES_RULES))
        self.assertEqual(self.selectors, list(REQUIRED_PREFERENCES_RULES))
        self.assertEqual(
            self.selectors[-4:],
            [PANEFIELD, PANE_MENULIST, PANE_MENULIST_HOVER, PANE_MENULIST_OPEN],
        )

    def test_field_and_menulist_rules_scope_to_the_pane(self):
        for selector in (PANEFIELD, PANE_MENULIST, PANE_MENULIST_HOVER,
                         PANE_MENULIST_OPEN):
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
        # The field arm matches the authored light-DOM text inputs and
        # never a disabled or non-text input; the menulist arms match the
        # pane's menulists and never one under #dialogTemplate.
        pane = element("vbox", "mainPrefPane")
        dialog = element("vbox", "dialogTemplate")
        self.assertTrue(
            matches(PANEFIELD, element(
                "input", "homePageUrl", attrs={"type": "text"}, parent=pane,
            ))
        )
        self.assertFalse(
            matches(PANEFIELD, element(
                "input", "homePageUrl",
                attrs={"type": "text", "disabled": "true"}, parent=pane,
            ))
        )
        self.assertFalse(
            matches(PANEFIELD, element(
                "input", "homePageUrl", attrs={"type": "range"}, parent=pane,
            ))
        )
        self.assertTrue(
            matches(PANE_MENULIST, element("menulist", "homeMode", parent=pane))
        )
        self.assertFalse(
            matches(
                PANE_MENULIST,
                element("menulist", "homeMode", parent=dialog),
            )
        )
        self.assertTrue(
            matches(
                PANE_MENULIST_HOVER,
                element("menulist", "homeMode", hover=True, parent=pane),
            )
        )
        self.assertFalse(
            matches(PANE_MENULIST_HOVER, element("menulist", "homeMode", parent=pane))
        )
        self.assertTrue(
            matches(
                PANE_MENULIST_OPEN,
                element("menulist", "homeMode", attrs={"open": "true"}, parent=pane),
            )
        )
        self.assertFalse(
            matches(PANE_MENULIST_OPEN, element("menulist", "homeMode", parent=pane))
        )

    def test_field_and_menulist_rules_use_the_pinned_palette(self):
        for selector, allowed in (
            (PANEFIELD, {WHITE, BLACK, GREY}),
            (PANE_MENULIST, {WHITE, BLACK, FACE, BUTTON_SHADOW}),
            (PANE_MENULIST_HOVER, {SELECTION, BLACK}),
            (PANE_MENULIST_OPEN, {SELECTION, BLACK}),
        ):
            declarations = self.rules[selector]
            with self.subTest(selector=selector):
                self.assertTrue(declarations)
            for name, value in declarations.items():
                with self.subTest(property=name):
                    self.assertIn("!important", value)
                    for token in HEX.findall(value):
                        self.assertIn(token, allowed)

    def test_header_names_field_provenance(self):
        self.assert_header_names(
            (
                "preferences.xhtml",
                "html:input[type=\"text\"]",
                "#homePageUrl",
                "#dohEnabledInputField",
                "#dohStrictInputField",
                "#fxaSyncComputerName",
                "#primaryBrowserLocale",
                "#homeMode",
                "#newTabMode",
                "#blockCookiesMenu",
                "#trackingProtectionMenu",
                "#fingerprintingProtectionMenu",
                "#dohEnabledResolverChoices",
                "#dohStrictResolverChoices",
                "menulist",
                "common-shared.css",
                "--border-radius-medium",
                "--background-color-box",
                "tokens-shared.css",
                "tokens-brand.css",
                "menulist.css",
                "dropmarker",
                "arrow-down-12.svg",
                "currentColor",
                "browser/omni.ja",
                "#about-config-search",
                "widgets/lineedit.svg",
                "tests/test_desktoptheme_lineedit.py::TestLineEdit",
                "TestLineEditReference",
                "widgets/button.svg",
                "tests/test_desktoptheme_button.py::TestButton",
                "tests/test_desktoptheme_button_reference.py::TestButtonReference",
                "widgets/viewitem.svg",
                "tests/test_desktoptheme_viewitem.py::TestViewItem",
                "test_selection_background",
                "[open=\"true\"]",
                "menupopup",
                ":not([disabled])",
                ":user-invalid",
                "sub-dialog",
                "platform colour adaptation 2026-10-27",
            )
        )

if __name__ == "__main__":
    unittest.main()
