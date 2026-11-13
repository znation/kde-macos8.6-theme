"""Shared spec values and base case for the Firefox content sheet tests.

The standalone Firefox Platinum ``userContent.css`` has no reference
screenshot: its palette is the shared Platinum palette and its geometry
adapts this theme's Platinum controls, so every page module pins the same
required-rules table against the sheet's ``@-moz-document`` body. The
page modules live in ``tests/test_firefox_content_theme.py`` (the
sheet-wide and about:downloads checks plus the body scanner's own tests),
``tests/test_firefox_content_config.py``,
``tests/test_firefox_content_preferences.py`` and
``tests/test_firefox_content_support.py``,
``tests/test_firefox_content_networking.py`` and
``tests/test_firefox_content_telemetry.py``. The sheet
ships as a standalone file installed beside ``userChrome.css`` by
``make install-firefox``, pinned by ``tests/test_install_firefox.py``.
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


def _at_rule_end(text, start):
    """Return the index just past the ``}`` that closes the body at *start*.

    A quoted string is a token, and a backslash keeps the character after it
    inside the string, so an escaped quote does not end it early and a quoted
    ``\"`` or ``\\`` cannot swallow the block's closing brace; braces nest.
    An unterminated body scans to the end of the text.
    """
    depth = 1
    quote = None
    escaped = False
    index = start
    while index < len(text) and depth:
        char = text[index]
        if escaped:
            escaped = False
        elif char == "\\":
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
    return index


def at_rule_bodies(text):
    """Return each ``@-moz-document url("...")`` body, keyed by its URL."""
    stripped = strip_comments(text)
    bodies = {}
    for match in AT_RULE.finditer(stripped):
        start = match.end()
        end = _at_rule_end(stripped, start)
        bodies[match.group("url")] = stripped[start : end - 1]
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
# byte-recipe of this module's FIELD_RULE (the existing about:config search
# field), and the menulist rules the byte-recipes of BUTTON_RULE and
# BUTTON_HOVER_RULE (the existing pane push buttons), spelled explicitly so a
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

# The about:networking rules. The sheet's arms are the existing about:support
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
# The existing about:preferences checked-arm glyph, byte-for-byte (the
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

TELEMETRY_ROW = "#categories > .category"
TELEMETRY_ROW_HOVER = (
    "#categories > .category:hover",
    "#categories > .category:hover:active",
)
TELEMETRY_ROW_SELECTED = (
    "#categories > .category.selected",
    "#categories > .category.selected:hover",
    "#categories > .category.selected:hover:active",
)
TELEMETRY_SUBSECTION = "#categories .category-subsection"
TELEMETRY_SUBSECTION_SELECTED = TELEMETRY_SUBSECTION + ".selected"
TELEMETRY_SEARCH = "#search"
TELEMETRY_STORES = "#stores"
TELEMETRY_STORES_HOVER = TELEMETRY_STORES + ":hover"
TELEMETRY_PING_PANEL = "#ping-picker"

# The payload arms reuse the existing support/networking table byte-recipes
# (FIELD_RULE, the #EEEEEE zebra of TROUGH, SUPPORT_TH_RULE,
# SUPPORT_CELL_RULE and BUTTON_HOVER_RULE) and the existing push-button
# recipes over this page's selectors (.main-content table, the histogram
# boxes, their bars and copy buttons and the raw-JSON viewer); the register
# keys the parsed selectors, which are the comma-list cell and button arms
# split per arm by parse_css.
TELEMETRY_TABLE = ".main-content table"
TELEMETRY_ZEBRA = TELEMETRY_TABLE + " tr:nth-child(2n)"
TELEMETRY_TH = TELEMETRY_TABLE + " th"
TELEMETRY_TD = TELEMETRY_TABLE + " td"
TELEMETRY_HEADER_HOVER = TELEMETRY_TH + ":hover"
TELEMETRY_HISTOGRAM = ".histogram"
TELEMETRY_BAR_INNER = ".bar-inner"
TELEMETRY_COPY = ".copy-node"
TELEMETRY_COPY_HOVER = TELEMETRY_COPY + ":hover"
TELEMETRY_JSON_BUTTON = "#payload-json-viewer"
TELEMETRY_JSON_BUTTON_HOVER = TELEMETRY_JSON_BUTTON + ":hover"

TELEMETRY_ROW_RULE = {
    "background-color": "transparent !important",
    "color": f"{BLACK} !important",
    "border-radius": "0 !important",
}
TELEMETRY_ROW_HIGHLIGHT = {
    "background-color": f"{SELECTION} !important",
    "color": f"{BLACK} !important",
}
TELEMETRY_SUBSECTION_RULE = {"color": f"{BLACK} !important"}
TELEMETRY_PING_PANEL_RULE = {
    "background-color": f"{WHITE} !important",
    "color": f"{BLACK} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": "none !important",
}
# Flat histogram adaptation (2026-10-28) of the ten-row progress gradient;
# the selection colour is pinned by TestReferenceAnchors.test_selection_background.
TELEMETRY_BAR_INNER_RULE = {
    "background-color": f"{SELECTION} !important",
    "border": "0 !important",
    "border-radius": "0 !important",
}

REQUIRED_TELEMETRY_RULES = {
    TELEMETRY_ROW: TELEMETRY_ROW_RULE,
    **{selector: TELEMETRY_ROW_HIGHLIGHT for selector in TELEMETRY_ROW_HOVER},
    **{
        selector: TELEMETRY_ROW_HIGHLIGHT
        for selector in TELEMETRY_ROW_SELECTED
    },
    TELEMETRY_SUBSECTION: TELEMETRY_SUBSECTION_RULE,
    TELEMETRY_SUBSECTION_SELECTED: TELEMETRY_ROW_HIGHLIGHT,
    TELEMETRY_SEARCH: FIELD_RULE,
    TELEMETRY_STORES: PANE_MENULIST_RULE,
    TELEMETRY_STORES_HOVER: PANE_MENULIST_HOVER_RULE,
    TELEMETRY_PING_PANEL: TELEMETRY_PING_PANEL_RULE,
    TELEMETRY_TABLE: FIELD_RULE,
    TELEMETRY_ZEBRA: {"background-color": f"{TROUGH} !important"},
    TELEMETRY_TH: SUPPORT_TH_RULE,
    TELEMETRY_TD: SUPPORT_CELL_RULE,
    TELEMETRY_HEADER_HOVER: BUTTON_HOVER_RULE,
    TELEMETRY_HISTOGRAM: TELEMETRY_PING_PANEL_RULE,
    TELEMETRY_BAR_INNER: TELEMETRY_BAR_INNER_RULE,
    TELEMETRY_COPY: BUTTON_RULE,
    TELEMETRY_COPY_HOVER: BUTTON_HOVER_RULE,
    TELEMETRY_JSON_BUTTON: BUTTON_RULE,
    TELEMETRY_JSON_BUTTON_HOVER: BUTTON_HOVER_RULE,
}

TELEMETRY_SELECTORS = (
    TELEMETRY_ROW,
    *TELEMETRY_ROW_HOVER,
    *TELEMETRY_ROW_SELECTED,
    TELEMETRY_SUBSECTION,
    TELEMETRY_SUBSECTION_SELECTED,
    TELEMETRY_SEARCH,
    TELEMETRY_STORES,
    TELEMETRY_STORES_HOVER,
    TELEMETRY_PING_PANEL,
    TELEMETRY_TABLE,
    TELEMETRY_ZEBRA,
    TELEMETRY_TH,
    TELEMETRY_TD,
    TELEMETRY_TH,
    TELEMETRY_HEADER_HOVER,
    TELEMETRY_HISTOGRAM,
    TELEMETRY_BAR_INNER,
    TELEMETRY_COPY,
    TELEMETRY_JSON_BUTTON,
    TELEMETRY_COPY_HOVER,
    TELEMETRY_JSON_BUTTON_HOVER,
)

FORBIDDEN_PAGE_CHROME = ("body", "h1", "hgroup", "main-content-title")


_content_fixture = None


class FirefoxContentTestCase(CommentHeaderAssertions, unittest.TestCase):
    """Shared fixture for the content page modules testing ``userContent.css``.

    Each reads the shipped sheet, splits it into ``@-moz-document`` bodies
    and parses exactly one of them; the class attribute ``AT_RULE_URL``
    names which.
    The inherited :meth:`CommentHeaderAssertions.assert_header_names` serves
    the provenance tests.

    Because every derived class reads the same shipped sheet, the read and
    the ``@-moz-document`` split are memoized per worker process in
    ``_content_fixture`` after the first ``setUpClass``: classes that run
    in the same module share one read and split and parse only their own
    body. The fixture tuple must stay read-only -- no test may assign into
    ``cls.text`` or ``cls.bodies``.
    """

    AT_RULE_URL: str

    @classmethod
    def setUpClass(cls):
        global _content_fixture
        if _content_fixture is None:
            text = containment.read_text(SHEET, ROOT, encoding="utf-8")
            _content_fixture = text, at_rule_bodies(text)
        cls.text, cls.bodies = _content_fixture
        cls.colours, cls.rules, cls.selectors = parse_css(
            cls.bodies.get(cls.AT_RULE_URL, ""), source=SHEET_PATH
        )

    def pin_declaration_tokens(self, selector, declarations, allowed):
        """Pin *declarations* each important; return their allowed tokens."""
        tokens = set()
        for name, value in declarations.items():
            with self.subTest(selector=selector, property=name):
                self.assertIn("!important", value)
                for token in HEX.findall(value):
                    self.assertIn(token, allowed)
                    tokens.add(token)
        return tokens

    def assert_pinned_palette_rules(self, rules, allowed):
        """Pin a whole required-rules recipe against the shipped sheet.

        For every ``selector -> expected`` pair in *rules*, the sheet's
        parsed declaration block must equal *expected*, be non-empty, and
        use only *allowed* hex tokens, each ``!important``; at least one
        token must be seen. The suite keeps its own body-hex check.

        Exactly three call sites today: ``test_firefox_content_support.py``,
        ``test_firefox_content_networking.py`` and
        ``test_firefox_content_telemetry.py``. The about:preferences suites
        pin selector lists with ``assert_palette_declarations`` in
        ``test_firefox_content_preferences.py`` instead -- a different
        shape, without the recipe comparison.
        """
        seen = set()
        for selector, expected in rules.items():
            declarations = self.rules[selector]
            with self.subTest(selector=selector):
                self.assertEqual(declarations, expected)
                self.assertTrue(declarations)
            seen.update(
                self.pin_declaration_tokens(selector, declarations, allowed)
            )
        self.assertTrue(seen)


if __name__ == "__main__":
    unittest.main()
