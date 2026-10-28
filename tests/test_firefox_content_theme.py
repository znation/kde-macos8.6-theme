"""Validate the standalone Firefox Platinum ``userContent.css`` sheet.

No reference screenshot shows Firefox's content-area downloads page, its
about:config page, its about:preferences panes or its about:support and
about:networking pages, so the palette is the shared Platinum palette and
the geometry adapts this theme's line-edit field, list-item row, push
button, check box and radio circle. The opt-in profile install copies the
sheet beside userChrome.css through make install-firefox.
"""

from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree
from pathlib import Path
from urllib.parse import unquote

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
from support.selector_matching import element, matches

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
        escaped = False
        index = start = match.end()
        while index < len(stripped) and depth:
            char = stripped[index]
            if escaped:
                escaped = False
            elif char == "\\":
                # A backslash keeps the character after it inside the string,
                # so an escaped quote does not end it early and a quoted
                # ``\"`` or ``\\`` cannot swallow the block's closing brace.
                escaped = True
            elif quote is not None:
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


def decodes_to_the_shipped_checkmark(value):
    """Assert *value* is the data URI of the shipped checkmarks.svg glyph."""
    match = re.search(r'url\("([^"]+)"\)', value)
    assert match is not None, value
    payload = match.group(1)
    prefix = "data:image/svg+xml,"
    assert payload.startswith(prefix), payload
    svg = unquote(payload[len(prefix):])
    root = xml.etree.ElementTree.fromstring(svg)
    assert root.get("width") == "16"
    assert root.get("height") == "16"
    paths = list(root)
    assert len(paths) == 1
    assert paths[0].get("d") == "M 3.5 8.5 L 6.5 11.5 L 12.5 5.5"
    assert paths[0].get("fill") == "none"
    assert paths[0].get("stroke") == "rgb(0, 0, 0)"
    assert paths[0].get("stroke-width") == "2"
    assert paths[0].get("stroke-linecap") == "square"
    assert paths[0].get("stroke-linejoin") == "miter"
    assert "#" not in svg


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
CHECKBOX_FACE = "#mainPrefPane checkbox:not([disabled]) .checkbox-check"
CHECKBOX_GLYPH = "#mainPrefPane checkbox:not([disabled])[checked] .checkbox-check"
RADIO_FACE = "#mainPrefPane radio:not([disabled]) .radio-check"
RADIO_DOT = "#mainPrefPane radio:not([disabled])[selected] .radio-check"
PANEFIELD = '#mainPrefPane input[type="text"]:not([disabled])'
PANE_MENULIST = "#mainPrefPane menulist:not([disabled])"
PANE_MENULIST_HOVER = "#mainPrefPane menulist:not([disabled]):hover"
PANE_MENULIST_OPEN = '#mainPrefPane menulist[open="true"]:not([disabled])'

# The checkbox glyph, inlined as a data-URI SVG (single quotes inside the
# quoted url(), %3C/%3E for the angle brackets, space-separated path
# coordinates, and rgb(0, 0, 0) for the black so the sheet gains no new hex
# literal). The URI is byte-pinned by test_checked_glyph_uri_pins_the_checkmarks_glyph.
CHECKBOX_GLYPH_URI = (
    'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' '
    "width='16' height='16' viewBox='0 0 16 16'%3E%3Cpath d='M 3.5 8.5 "
    "L 6.5 11.5 L 12.5 5.5' fill='none' stroke='rgb(0, 0, 0)' "
    "stroke-width='2' stroke-linecap='square' "
    "stroke-linejoin='miter'/%3E%3C/svg%3E\") !important"
)

CHECKBOX_FACE_RULE = {
    "appearance": "none !important",
    "background-color": f"{FACE} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": f"inset 1px 1px {WHITE}, inset -1px -1px {ETCH_DARK} !important",
}

CHECKBOX_GLYPH_RULE = {
    "background-image": CHECKBOX_GLYPH_URI,
    "background-repeat": "no-repeat !important",
    "background-position": "center !important",
}

# The selected radio's dot, inlined as a data-URI SVG (single quotes inside
# the quoted url(), %3C/%3E for the angle brackets, and rgb(0, 0, 0) for the
# black so the sheet gains no new hex literal). The URI is byte-pinned by
# test_selected_dot_uri_pins_the_radiobutton_dot.
RADIO_DOT_URI = (
    'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' '
    "width='16' height='16' viewBox='0 0 16 16'%3E%3Ccircle cx='8' cy='8' "
    "r='3' fill='rgb(0, 0, 0)'/%3E%3C/svg%3E\") !important"
)

RADIO_FACE_RULE = {
    "appearance": "none !important",
    "background-color": f"{WHITE} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "50% !important",
}

RADIO_DOT_RULE = {
    "background-image": RADIO_DOT_URI,
    "background-repeat": "no-repeat !important",
    "background-position": "center !important",
}

# The enabled pane entry fields and menulists: the field rule is the
# byte-recipe of this module's FIELD_RULE (the landed about:config search
# field), and the menulist rules the byte-recipes of BUTTON_RULE and
# BUTTON_HOVER_RULE (the landed pane push buttons), spelled explicitly so a
# change to the config or button recipes cannot silently retarget the panes.
PANEFIELD_RULE = {
    "background-color": f"{WHITE} !important",
    "color": f"{BLACK} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": f"inset 1px 1px {GREY} !important",
}

PANE_MENULIST_RULE = {
    "background-color": f"{FACE} !important",
    "color": f"{BLACK} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": (
        f"inset 1px 1px {WHITE}, inset -1px -1px {BUTTON_SHADOW} !important"
    ),
}

PANE_MENULIST_HOVER_RULE = {
    "background-color": f"{SELECTION} !important",
    "color": f"{BLACK} !important",
    "box-shadow": "none !important",
}

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
    CHECKBOX_FACE: CHECKBOX_FACE_RULE,
    CHECKBOX_GLYPH: CHECKBOX_GLYPH_RULE,
    RADIO_FACE: RADIO_FACE_RULE,
    RADIO_DOT: RADIO_DOT_RULE,
    PANEFIELD: PANEFIELD_RULE,
    PANE_MENULIST: PANE_MENULIST_RULE,
    PANE_MENULIST_HOVER: PANE_MENULIST_HOVER_RULE,
    PANE_MENULIST_OPEN: PANE_MENULIST_HOVER_RULE,
}

# The about:support rules. The sheet's field, header and button arms are the
# byte-recipes of this module's shared arms (FIELD_RULE for the field,
# BUTTON_RULE and BUTTON_HOVER_RULE for the raised header and push-button
# faces); the register keys the parsed selectors, which are the comma-list
# cell and button arms split per arm by parse_css.
SUPPORT_LIST = "#contents table"
SUPPORT_ZEBRA = SUPPORT_LIST + " tr:nth-child(2n)"
SUPPORT_TH = SUPPORT_LIST + " th"
SUPPORT_TD = SUPPORT_LIST + " td"
SUPPORT_HEADER_HOVER = SUPPORT_TH + ":hover"
SUPPORT_BUTTONS = (
    "#copy-raw-data-to-clipboard",
    "#copy-to-clipboard",
    ".action-box button",
    "#profile-dir-button",
    "#enumerate-database-button",
    "#verify-place-integrity-button",
    "#place-database-stats-toggle",
    "#support-printing-clear-settings-button",
)
SUPPORT_BUTTONS_HOVER = tuple(
    arm + ":hover:not(:disabled)" for arm in SUPPORT_BUTTONS
)

# The sheet's comma-list cell rule restates th before the header rule
# repaints it, so parse_css merges both blocks into th's five declarations.
SUPPORT_CELL_RULE = {
    "border": "0 !important",
    "border-radius": "0 !important",
}
SUPPORT_TH_RULE = {
    "border": "0 !important",
    "border-radius": "0 !important",
    "background-color": f"{FACE} !important",
    "color": f"{BLACK} !important",
    "box-shadow": (
        f"inset 1px 1px {WHITE}, inset -1px -1px {BUTTON_SHADOW} !important"
    ),
}

REQUIRED_SUPPORT_RULES = {
    SUPPORT_LIST: FIELD_RULE,
    SUPPORT_ZEBRA: {"background-color": f"{TROUGH} !important"},
    SUPPORT_TH: SUPPORT_TH_RULE,
    SUPPORT_TD: SUPPORT_CELL_RULE,
    SUPPORT_HEADER_HOVER: BUTTON_HOVER_RULE,
    **{selector: BUTTON_RULE for selector in SUPPORT_BUTTONS},
    **{selector: BUTTON_HOVER_RULE for selector in SUPPORT_BUTTONS_HOVER},
}

SUPPORT_SELECTORS = (
    SUPPORT_LIST,
    SUPPORT_ZEBRA,
    SUPPORT_TH,
    SUPPORT_TD,
    SUPPORT_TH,
    SUPPORT_HEADER_HOVER,
    *SUPPORT_BUTTONS,
    *SUPPORT_BUTTONS_HOVER,
)

# The about:networking rules. The sheet's arms are the landed about:support
# arms byte-for-byte over this page's selectors (.main-content table and the
# four button ids); the register keys the parsed selectors, which are the
# comma-list cell and button arms split per arm by parse_css.
NETWORKING_LIST = ".main-content table"
NETWORKING_ZEBRA = NETWORKING_LIST + " tr:nth-child(2n)"
NETWORKING_TH = NETWORKING_LIST + " th"
NETWORKING_TD = NETWORKING_LIST + " td"
NETWORKING_HEADER_HOVER = NETWORKING_TH + ":hover"
NETWORKING_BUTTONS = (
    "#refreshButton",
    "#clearHTTPCache",
    "#clearDNSCache",
    "#dnsLookupButton",
)
NETWORKING_BUTTONS_HOVER = tuple(
    arm + ":hover:not(:disabled)" for arm in NETWORKING_BUTTONS
)
NETWORKING_CATEGORY = "#categories > .category"
NETWORKING_CATEGORY_HOVER = (
    "#categories > .category:hover",
    "#categories > .category:hover:active",
)
NETWORKING_CATEGORY_SELECTED = (
    "#categories > .category[selected]",
    "#categories > .category[selected]:hover",
    "#categories > .category[selected]:hover:active",
)
NETWORKING_HOST = "#host"
NETWORKING_CHECK = "#autorefcheck"
NETWORKING_CHECK_CHECKED = NETWORKING_CHECK + ":checked"

NETWORKING_CATEGORY_RULE = {
    "background-color": "transparent !important",
    "color": f"{BLACK} !important",
    "border-radius": "0 !important",
}
NETWORKING_ROW_HIGHLIGHT = {
    "background-color": f"{SELECTION} !important",
    "color": f"{BLACK} !important",
}
NETWORKING_CHECK_RULE = {
    "appearance": "none !important",
    "background-color": f"{FACE} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": f"inset 1px 1px {WHITE}, inset -1px -1px {ETCH_DARK} !important",
}
# The landed about:preferences checked-arm glyph, byte-for-byte (the
# module's own CHECKBOX_GLYPH_URI): the plan spells the URI inline and this
# constant is its byte-equal spelling.
NETWORKING_CHECK_CHECKED_RULE = {
    "background-image": CHECKBOX_GLYPH_URI,
    "background-repeat": "no-repeat !important",
    "background-position": "center !important",
}

REQUIRED_NETWORKING_RULES = {
    NETWORKING_LIST: FIELD_RULE,
    NETWORKING_ZEBRA: {"background-color": f"{TROUGH} !important"},
    NETWORKING_TH: SUPPORT_TH_RULE,
    NETWORKING_TD: SUPPORT_CELL_RULE,
    NETWORKING_HEADER_HOVER: BUTTON_HOVER_RULE,
    **{selector: BUTTON_RULE for selector in NETWORKING_BUTTONS},
    **{selector: BUTTON_HOVER_RULE for selector in NETWORKING_BUTTONS_HOVER},
    NETWORKING_CATEGORY: NETWORKING_CATEGORY_RULE,
    **{
        selector: NETWORKING_ROW_HIGHLIGHT
        for selector in NETWORKING_CATEGORY_HOVER
    },
    **{
        selector: NETWORKING_ROW_HIGHLIGHT
        for selector in NETWORKING_CATEGORY_SELECTED
    },
    NETWORKING_HOST: FIELD_RULE,
    NETWORKING_CHECK: NETWORKING_CHECK_RULE,
    NETWORKING_CHECK_CHECKED: NETWORKING_CHECK_CHECKED_RULE,
}

NETWORKING_SELECTORS = (
    NETWORKING_LIST,
    NETWORKING_ZEBRA,
    NETWORKING_TH,
    NETWORKING_TD,
    NETWORKING_TH,
    NETWORKING_HEADER_HOVER,
    *NETWORKING_BUTTONS,
    *NETWORKING_BUTTONS_HOVER,
    NETWORKING_CATEGORY,
    *NETWORKING_CATEGORY_HOVER,
    *NETWORKING_CATEGORY_SELECTED,
    NETWORKING_HOST,
    NETWORKING_CHECK,
    NETWORKING_CHECK_CHECKED,
)

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

    def test_sheet_has_the_downloads_config_preferences_support_and_networking_at_rules(
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
            },
        )
        self.assertEqual(stripped.count("@"), 5)
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


class TestFirefoxPreferencesCheckboxTheme(SheetCase):
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


class TestFirefoxPreferencesRadioTheme(SheetCase):
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


class TestFirefoxPreferencesFieldsTheme(SheetCase):
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


class TestFirefoxSupportTheme(SheetCase):
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


class TestFirefoxNetworkingTheme(SheetCase):
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
