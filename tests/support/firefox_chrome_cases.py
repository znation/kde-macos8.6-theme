"""Shared spec values and base case for the Firefox chrome sheet tests.

The standalone Firefox Platinum ``userChrome.css`` has no reference
screenshot: its palette is the shared Platinum palette and its geometry
adapts this theme's Platinum controls, so every section module pins the
same ``REQUIRED_RULES`` table against the sheet text. The sections live in
``tests/test_firefox_theme_shell.py``, ``tests/test_firefox_theme_panels.py``,
``tests/test_firefox_theme_popups.py`` and
``tests/test_firefox_theme_page_info.py``; the sheet ships as a standalone
file, and ``tests/test_firefox_install.py`` pins its install and removal.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from support import containment
from support.css_header import CommentHeaderAssertions
from support.gtk_css import parse_css
from support.gtk_rule_cases import SheetRuleAssertions
from support.gtk_theme_spec import BUTTON_BEVEL, ETCH_DARK, RAISED_BEVEL
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    SELECTION,
    TOOLTIP_FACE,
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
    / "userChrome.css"
)
README = Path(ROOT) / "README.md"
SHEET_PATH = "theme/firefox/org.macos8.desktop/chrome/userChrome.css"

# Firefox's stock Linux menubar > menu rule keeps a 3px transparent bottom
# border; the sheet leaves it in place and the open-title rule recolours it.
MENU_STOCK_BOTTOM_BORDER = 3

REQUIRED_RULES = {
    "tooltip": {
        "appearance": "none !important",
        "background-color": f"{TOOLTIP_FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": "none !important",
    },
    ":root": {
        "--lwt-accent-color": f"{FACE} !important",
        "--lwt-text-color": f"{BLACK} !important",
        "--toolbar-bgcolor": f"{FACE} !important",
        "--toolbar-color": f"{BLACK} !important",
        "--tab-selected-bgcolor": f"{TROUGH} !important",
        "--tab-selected-textcolor": f"{BLACK} !important",
        "--toolbarbutton-border-radius": "0 !important",
        "--toolbarbutton-background-color-hover": f"{TROUGH} !important",
        "--toolbarbutton-background-color-active": f"{SELECTION} !important",
        "--urlbar-box-background-color-hover": f"{TROUGH} !important",
        "--urlbar-box-background-color-active": f"{SELECTION} !important",
    },
    "#navigator-toolbox": {
        "background-color": f"{FACE} !important",
        "border-bottom": f"1px solid {BLACK} !important",
    },
    "#TabsToolbar": {
        "background-color": f"{FACE} !important",
    },
    "#nav-bar": {
        "background-color": f"{FACE} !important",
        "border-bottom": f"1px solid {ETCH_DARK} !important",
        "box-shadow": f"inset 0 -1px {WHITE} !important",
    },
    "#PersonalToolbar": {
        "background-color": f"{FACE} !important",
        "border-bottom": f"1px solid {ETCH_DARK} !important",
        "box-shadow": f"inset 0 -1px {WHITE} !important",
    },
    "#toolbar-menubar": {
        "background-color": f"{FACE} !important",
        "border-bottom": f"1px solid {ETCH_DARK} !important",
        "box-shadow": f"inset 0 -1px {WHITE} !important",
    },
    "#toolbar-menubar menubar > menu": {
        "padding": "3px 7px 0 !important",
    },
    "#toolbar-menubar menubar > menu[open]": {
        "background-color": f"{SELECTION} !important",
        "border-bottom-color": f"{SELECTION} !important",
    },
    "#sidebar-box": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
    },
    "#sidebar-header": {
        "border-bottom": f"1px solid {ETCH_DARK} !important",
        "box-shadow": f"inset 0 -1px {WHITE} !important",
    },
    "#downloadsPanel #downloadsListBox > richlistitem": {
        "border-radius": "0 !important",
    },
    "#downloadsPanel #downloadsListBox > richlistitem:not([selected]):hover": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
    },
    "#downloadsPanel #downloadsListBox > richlistitem[selected]": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
    },
    "#downloadsPanel .downloadsPanelFooterButton:not([disabled])": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"{BUTTON_BEVEL} !important",
    },
    "#downloadsPanel .downloadButton:not([disabled])": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"{BUTTON_BEVEL} !important",
    },
    "#downloadsPanel .footer-button:not([disabled])": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"{BUTTON_BEVEL} !important",
    },
    "#downloadsPanel .downloadsPanelFooterButton:not([disabled]):hover": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#downloadsPanel .downloadButton:not([disabled]):hover": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#downloadsPanel .footer-button:not([disabled]):hover": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    ".tab-background": {
        "background-color": f"{FACE} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": (
            f"inset 1px 1px {WHITE}, inset -1px -1px {GREY} !important"
        ),
    },
    ".tabbrowser-tab:is([selected], [multiselected]) .tab-background": {
        "background-color": f"{TROUGH} !important",
        "border-bottom-color": f"{TROUGH} !important",
    },
    (
        ".tabbrowser-tab:hover > .tab-stack > .tab-background"
        ":not([selected]):not([multiselected])"
    ): {
        "background-color": f"{TROUGH} !important",
    },
    "#urlbar-background": {
        "background-color": f"{WHITE} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": "none !important",
    },
    "#searchbar:not(:focus-within)": {
        "background-color": f"{WHITE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": "none !important",
    },
    ".urlbarView-row": {
        "border-radius": "0 !important",
    },
    ".urlbarView-row[row-selectable]:not([selected]):hover": {
        "background-color": f"{TROUGH} !important",
    },
    ".urlbarView-row[selected]": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
    },
    ".urlbarView-body-inner": {
        "border-top-color": f"{ETCH_DARK} !important",
    },
    "#statuspanel-label": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
    },
    'panel[type="arrow"]': {
        "--panel-border-radius": "0 !important",
        "--panel-background-color": f"{FACE} !important",
        "--panel-text-color": f"{BLACK} !important",
        "--panel-border-color": f"{BLACK} !important",
    },
    "menupopup": {
        "--panel-border-radius": "0 !important",
        "--panel-background-color": f"{FACE} !important",
        "--panel-text-color": f"{BLACK} !important",
        "--panel-border-color": f"{BLACK} !important",
    },
    "menupopup > menuitem:hover": {
        "background-color": f"{SELECTION} !important",
    },
    "menupopup > menu:hover": {
        "background-color": f"{SELECTION} !important",
    },
    'menupopup > menuitem[_moz-menuactive="true"]': {
        "background-color": f"{SELECTION} !important",
    },
    'menupopup > menu[_moz-menuactive="true"]': {
        "background-color": f"{SELECTION} !important",
    },
    "#PersonalToolbar .bookmark-item:hover": {
        "background-color": f"{SELECTION} !important",
        "border-radius": "0 !important",
        "box-shadow": f"inset 1px 1px {WHITE} !important",
    },
    "#PersonalToolbar .bookmark-item[open]": {
        "background-color": f"{SELECTION} !important",
        "border-radius": "0 !important",
        "box-shadow": f"inset 1px 1px {WHITE} !important",
    },
    "toolbarbutton:hover:not([disabled=\"true\"])": {
        "box-shadow": f"{RAISED_BEVEL} !important",
    },
    "toolbarbutton:hover:active:not([disabled=\"true\"])": {
        "box-shadow": f"inset 1px 1px {GREY} !important",
    },
    "#allTabsMenu-allTabsView .all-tabs-item": {
        "border-radius": "0 !important",
    },
    "#allTabsMenu-allTabsView .all-tabs-item > .all-tabs-button": {
        "border-radius": "0 !important",
    },
    (
        "#allTabsMenu-allTabsView .all-tabs-item:not([selected])"
        " > .all-tabs-button:hover"
    ): {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    (
        "#allTabsMenu-allTabsView .all-tabs-item[selected]"
        " > .all-tabs-button"
    ): {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#appMenu-popup .subviewbutton:not(.panel-header .subviewbutton)": {
        "border-radius": "0 !important",
    },
    "#appMenu-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled])": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#widget-overflow .subviewbutton:not(.panel-header .subviewbutton)": {
        "border-radius": "0 !important",
    },
    "#widget-overflow .widget-overflow-list .toolbarbutton-1": {
        "border-radius": "0 !important",
    },
    (
        "#widget-overflow .subviewbutton:not(.panel-header .subviewbutton)"
        ":hover:not([disabled])"
    ): {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    (
        "#widget-overflow .widget-overflow-list .toolbarbutton-1"
        ":hover:not([disabled])"
    ): {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#unified-extensions-panel .subviewbutton:not(.panel-header .subviewbutton):not(.unified-extensions-item-menu-button):not(#unified-extensions-discover-extensions)": {
        "border-radius": "0 !important",
    },
    "#unified-extensions-panel .subviewbutton:not(.panel-header .subviewbutton):not(.unified-extensions-item-menu-button):not(#unified-extensions-discover-extensions):hover:not([disabled])": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#unified-extensions-panel .unified-extensions-item-menu-button:hover": {
        "box-shadow": "none !important",
    },
    "#identity-popup .subviewbutton:not(.panel-header .subviewbutton)": {
        "border-radius": "0 !important",
    },
    "#identity-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled])": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#protections-popup .subviewbutton:not(.panel-header .subviewbutton)": {
        "border-radius": "0 !important",
    },
    "#protections-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled])": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#protections-popup-show-report-stack:hover > .protections-popup-footer-button:not([disabled])": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#trustpanel-popup .subviewbutton:not(.panel-header .subviewbutton)": {
        "border-radius": "0 !important",
    },
    "#trustpanel-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled])": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#permission-popup .permission-popup-permission-remove-button": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"{BUTTON_BEVEL} !important",
    },
    "#permission-popup .permission-popup-permission-remove-button:hover:not([disabled])": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#permission-popup-menulist": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"{BUTTON_BEVEL} !important",
    },
    "#permission-popup-menulist:hover:not([disabled])": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#notification-popup .popup-notification-primary-button": {
        "--button-background-color-primary": f"{FACE} !important",
        "--button-background-color-primary-hover": f"{SELECTION} !important",
        "--button-background-color-primary-active": f"{SELECTION} !important",
        "--button-border": "1px solid !important",
        "--button-border-color-primary": f"{BLACK} !important",
        "--button-border-color-primary-hover": f"{BLACK} !important",
        "--button-border-color-primary-active": f"{BLACK} !important",
        "--button-text-color-primary": f"{BLACK} !important",
        "--button-text-color-primary-hover": f"{BLACK} !important",
        "--button-text-color-primary-active": f"{BLACK} !important",
        "--button-border-radius": "0 !important",
        "background-color": "transparent !important",
        "color": f"{BLACK} !important",
        "border-radius": "0 !important",
    },
    "menupopup > menuseparator": {
        "padding": "0 !important",
        "margin": "2px 0 !important",
    },
    "menupopup > menuseparator::before": {
        "border-top": f"1px solid {ETCH_DARK} !important",
        "border-bottom": f"1px solid {WHITE} !important",
    },
    "findbar": {
        "background-color": f"{FACE} !important",
        "border-top": f"1px solid {BLACK} !important",
    },
    "findbar .findbar-textbox:not([status=\"notfound\"]):not([flash=\"true\"]):not(:focus)": {
        "background-color": f"{WHITE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"inset 1px 1px {GREY} !important",
    },
    "#editBookmarkPanel #editBMPanel_namePicker": {
        "background-color": f"{WHITE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"inset 1px 1px {GREY} !important",
    },
    "#editBookmarkPanel #editBMPanel_locationField": {
        "background-color": f"{WHITE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"inset 1px 1px {GREY} !important",
    },
    "#editBookmarkPanel #editBMPanel_tagsField": {
        "background-color": f"{WHITE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"inset 1px 1px {GREY} !important",
    },
    "#editBookmarkPanel #editBMPanel_keywordField": {
        "background-color": f"{WHITE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"inset 1px 1px {GREY} !important",
    },
    "#editBookmarkPanel #editBMPanel_folderMenuList": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"{BUTTON_BEVEL} !important",
    },
    "#editBookmarkPanel #editBookmarkPanelDoneButton": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"{BUTTON_BEVEL} !important",
    },
    "#editBookmarkPanel #editBookmarkPanelRemoveButton": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"{BUTTON_BEVEL} !important",
    },
    "#editBookmarkPanel #editBMPanel_folderMenuList:hover:not([disabled])": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#editBookmarkPanel #editBookmarkPanelDoneButton:hover:not([disabled])": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#editBookmarkPanel #editBookmarkPanelRemoveButton:hover:not([disabled])": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    },
    "#topBar": {
        "background-color": f"{FACE} !important",
        "border-bottom": f"1px solid {ETCH_DARK} !important",
        "box-shadow": f"inset 0 -1px {WHITE} !important",
    },
    "#viewGroup > radio": {
        "appearance": "none !important",
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"{RAISED_BEVEL} !important",
    },
    "#viewGroup > radio[selected]": {
        "background-color": f"{TROUGH} !important",
        "border-bottom-color": f"{TROUGH} !important",
    },
    "#viewGroup > radio:not([selected]):hover": {
        "background-color": f"{TROUGH} !important",
    },
}

# The Page Info window's action buttons: each panel's help button plus the
# media panel's select-all and save buttons and the security panel's
# certificate and site-data buttons.
PAGE_INFO_CONTROL_IDS = (
    ".help-button",
    "#selectallbutton",
    "#imagesaveasbutton",
    "#mediasaveasbutton",
    "#security-view-qwac",
    "#security-view-cert",
    "#security-clear-sitedata",
    "#security-view-password",
)

REQUIRED_RULES.update({
    f"#mainDeck {control}:not([disabled])": {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": f"{BUTTON_BEVEL} !important",
    }
    for control in PAGE_INFO_CONTROL_IDS
})
REQUIRED_RULES.update({
    f"#mainDeck {control}:not([disabled]):hover": {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    }
    for control in PAGE_INFO_CONTROL_IDS
})

# The Page Info window's display fields: one rule recolours every input in
# the deck, which pageInfo.xhtml defines readonly, with no hover or focus
# variant (a focused readonly field keeps Firefox's focus ring).
REQUIRED_RULES["#mainDeck input"] = {
    "background-color": f"{WHITE} !important",
    "color": f"{BLACK} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": f"inset 1px 1px {GREY} !important",
}

# The Page Info media panel's preview pane: the Platinum sunken field
# (see the header's provenance paragraph), a static preview surface with
# no hover or focus variant.
REQUIRED_RULES["#imagecontainerbox"] = {
    "background-color": f"{WHITE} !important",
    "color": f"{BLACK} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": f"inset 1px 1px {GREY} !important",
}

# The Page Info permissions panel's permission list: the Platinum sunken
# list field (see the header's provenance paragraph), with the native
# listbox frame dropped and a hovered row keeping the field's face.
REQUIRED_RULES["#permList"] = {
    "appearance": "none !important",
    "background-color": f"{WHITE} !important",
    "color": f"{BLACK} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": f"inset 1px 1px {GREY} !important",
}
REQUIRED_RULES["#permList .permission:hover"] = {
    "background-color": "transparent !important",
    "color": f"{BLACK} !important",
}

# The Page Info dialog's meta and image trees: the Platinum sunken list
# field (see the header's provenance paragraph), with the rows transparent
# over the field, a flat #CCCCFF selected row and the broken image rows
# keeping their italic graytext. No appearance declaration: the trees are
# painted with plain declarations.
REQUIRED_RULES["#metatree"] = {
    "background-color": f"{WHITE} !important",
    "color": f"{BLACK} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": f"inset 1px 1px {GREY} !important",
}
REQUIRED_RULES["#imagetree"] = REQUIRED_RULES["#metatree"]
for _tree in ("metatree", "imagetree"):
    REQUIRED_RULES[
        f"tree#{_tree} treechildren::-moz-tree-row(hover)"
    ] = {"background-color": "transparent !important"}
    REQUIRED_RULES[
        f"tree#{_tree} treechildren::-moz-tree-row(selected)"
    ] = {"background-color": f"{SELECTION} !important"}
    REQUIRED_RULES[
        f"tree#{_tree} treechildren::-moz-tree-cell-text"
    ] = {"color": f"{BLACK} !important"}
REQUIRED_RULES["tree#imagetree treechildren::-moz-tree-cell-text(broken)"] = {
    "color": "graytext !important",
}


class FirefoxChromeTestCase(
    CommentHeaderAssertions, SheetRuleAssertions, unittest.TestCase
):
    """Base case loading the sheet text, README and parsed rules once.

    The ``CommentHeaderAssertions`` mixin serves the section modules'
    header-provenance tests.
    """

    @classmethod
    def setUpClass(cls):
        cls.text = containment.read_text(SHEET, ROOT, encoding="utf-8")
        cls.readme = containment.read_text(README, ROOT, encoding="utf-8")
        cls.colours, cls.rules, cls.selectors = parse_css(
            cls.text, source=SHEET_PATH
        )
