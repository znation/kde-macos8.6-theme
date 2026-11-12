"""Shared spec values and base case for the Firefox chrome sheet tests.

The standalone Firefox Platinum ``userChrome.css`` has no reference
screenshot: its palette is the shared Platinum palette and its geometry
adapts this theme's Platinum controls, so every section module pins the
same ``REQUIRED_RULES`` table against the sheet text. The sections live in
``tests/test_firefox_theme_shell.py``, ``tests/test_firefox_theme_panels.py``,
``tests/test_firefox_theme_popups.py``,
``tests/test_firefox_theme_page_info.py`` and
``tests/test_firefox_theme_library.py``; the sheet ships as a standalone
file, and ``tests/test_install_firefox.py`` pins its install and removal.
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
    BUTTON_SHADOW,
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

# Provenance names repeated across the section suites' comment headers: a
# themed section that borrows the viewitem artwork names both the artwork
# and the desktoptheme tests pinning it, and the same two entries recur in
# every such header. Twelve call sites: eight in the shell suite's
# provenance header (the downloads-panel buttons, app menu, toolbar
# overflow panel, unified extensions panel, site-information panel,
# protections panel, permission popup and trust panel), one in the panels
# suite (the bookmark editor), one in the popups suite (the notification
# popup) and two in the page-info suite (the window and its tree).
VIEWITEM_REFERENCES = (
    "widgets/viewitem.svg",
    "tests/test_desktoptheme_viewitem.py::TestViewItem",
)

# The same bundle for a section that draws a real button artwork: three
# header entries name the button artwork, its implementing test and its
# reference-screenshot test together. Four call sites, one per button-derived
# section header (the page-info window, the bookmark editor panel, the
# downloads panel and the permission popup in the shell suite).
BUTTON_REFERENCES = (
    "widgets/button.svg",
    "tests/test_desktoptheme_button.py::TestButton",
    "tests/test_desktoptheme_button_reference.py::TestButtonReference",
)

# The declaration recipes the sheet restates across its themed controls:
# a raised push button draws the panel face on a black keyline with the
# button bevel, its hover and pressed arms flush to the selection ink
# with no shadow, and a themed field draws the white face on a black
# keyline with the pressed inset. BUTTON_FACE is required by 18 rules,
# BUTTON_HOVER by 31 (the Page Info deck's eight button arms and eight
# hover arms through the comprehension loops, and the library's hovered
# and pressed column headers through the HEADER_HOVER alias below), and
# FIELD_FACE by 18; the field rules that layer the browser skin's
# ``appearance: none`` over the recipe spread FIELD_FACE under that one
# declaration. The section suites compare rule text against the table
# and never mutate an entry; the tooltip, urlbar and viewGroup radio
# variants (different faces or a flat white field) stay spelled out.
BUTTON_FACE = {
    "background-color": f"{FACE} !important",
    "color": f"{BLACK} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": f"{BUTTON_BEVEL} !important",
}
BUTTON_HOVER = {
    "background-color": f"{SELECTION} !important",
    "color": f"{BLACK} !important",
    "box-shadow": "none !important",
}
FIELD_FACE = {
    "background-color": f"{WHITE} !important",
    "color": f"{BLACK} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": f"inset 1px 1px {GREY} !important",
}

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
        "scrollbar-color": f"{FACE} {TROUGH} !important",
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
    "#downloadsPanel .downloadsPanelFooterButton:not([disabled])": BUTTON_FACE,
    "#downloadsPanel .downloadButton:not([disabled])": BUTTON_FACE,
    "#downloadsPanel .footer-button:not([disabled])": BUTTON_FACE,
    "#downloadsPanel .downloadsPanelFooterButton:not([disabled]):hover": (
        BUTTON_HOVER
    ),
    "#downloadsPanel .downloadButton:not([disabled]):hover": BUTTON_HOVER,
    "#downloadsPanel .footer-button:not([disabled]):hover": BUTTON_HOVER,
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
    "#urlbar:not([focused], [open]) > .urlbar-background": {
        "background-color": f"{WHITE} !important",
        "border": f"1px solid {BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow": "none !important",
    },
    "#searchbar-new:not([focused], [open]) > .urlbar-background": {
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
    ): BUTTON_HOVER,
    "#appMenu-popup .subviewbutton:not(.panel-header .subviewbutton)": {
        "border-radius": "0 !important",
    },
    "#appMenu-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled])": (
        BUTTON_HOVER
    ),
    "#widget-overflow .subviewbutton:not(.panel-header .subviewbutton)": {
        "border-radius": "0 !important",
    },
    "#widget-overflow .widget-overflow-list .toolbarbutton-1": {
        "border-radius": "0 !important",
    },
    (
        "#widget-overflow .subviewbutton:not(.panel-header .subviewbutton)"
        ":hover:not([disabled])"
    ): BUTTON_HOVER,
    (
        "#widget-overflow .widget-overflow-list .toolbarbutton-1"
        ":hover:not([disabled])"
    ): BUTTON_HOVER,
    "#unified-extensions-panel .subviewbutton:not(.panel-header .subviewbutton):not(.unified-extensions-item-menu-button):not(#unified-extensions-discover-extensions)": {
        "border-radius": "0 !important",
    },
    "#unified-extensions-panel .subviewbutton:not(.panel-header .subviewbutton):not(.unified-extensions-item-menu-button):not(#unified-extensions-discover-extensions):hover:not([disabled])": (
        BUTTON_HOVER
    ),
    "#unified-extensions-panel .unified-extensions-item-menu-button:hover": {
        "box-shadow": "none !important",
    },
    "#identity-popup .subviewbutton:not(.panel-header .subviewbutton)": {
        "border-radius": "0 !important",
    },
    "#identity-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled])": (
        BUTTON_HOVER
    ),
    "#protections-popup .subviewbutton:not(.panel-header .subviewbutton)": {
        "border-radius": "0 !important",
    },
    "#protections-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled])": (
        BUTTON_HOVER
    ),
    "#protections-popup-show-report-stack:hover > .protections-popup-footer-button:not([disabled])": (
        BUTTON_HOVER
    ),
    "#trustpanel-popup .subviewbutton:not(.panel-header .subviewbutton)": {
        "border-radius": "0 !important",
    },
    "#trustpanel-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled])": (
        BUTTON_HOVER
    ),
    "#permission-popup .permission-popup-permission-remove-button": BUTTON_FACE,
    "#permission-popup .permission-popup-permission-remove-button:hover:not([disabled])": (
        BUTTON_HOVER
    ),
    "#permission-popup-menulist": BUTTON_FACE,
    "#permission-popup-menulist:hover:not([disabled])": BUTTON_HOVER,
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
    "findbar .findbar-textbox:not([status=\"notfound\"]):not([flash=\"true\"]):not(:focus)": (
        FIELD_FACE
    ),
    "#editBookmarkPanel #editBMPanel_namePicker": FIELD_FACE,
    "#editBookmarkPanel #editBMPanel_locationField": FIELD_FACE,
    "#editBookmarkPanel #editBMPanel_tagsField": FIELD_FACE,
    "#editBookmarkPanel #editBMPanel_keywordField": FIELD_FACE,
    "#editBookmarkPanel #editBMPanel_folderMenuList": BUTTON_FACE,
    "#editBookmarkPanel #editBookmarkPanelDoneButton": BUTTON_FACE,
    "#editBookmarkPanel #editBookmarkPanelRemoveButton": BUTTON_FACE,
    "#editBookmarkPanel #editBMPanel_folderMenuList:hover:not([disabled])": BUTTON_HOVER,
    "#editBookmarkPanel #editBookmarkPanelDoneButton:hover:not([disabled])": (
        BUTTON_HOVER
    ),
    "#editBookmarkPanel #editBookmarkPanelRemoveButton:hover:not([disabled])": (
        BUTTON_HOVER
    ),
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
        "box-shadow": "none !important",
    },
    "#viewGroup > radio:not([selected]):hover": {
        "background-color": f"{TROUGH} !important",
        "box-shadow": "none !important",
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
    f"#mainDeck {control}:not([disabled])": BUTTON_FACE
    for control in PAGE_INFO_CONTROL_IDS
})
REQUIRED_RULES.update({
    f"#mainDeck {control}:not([disabled]):hover": BUTTON_HOVER
    for control in PAGE_INFO_CONTROL_IDS
})

# The Page Info window's display fields: one rule recolours every input in
# the deck, which pageInfo.xhtml defines readonly, with no hover or focus
# variant (a focused readonly field keeps Firefox's focus ring).
REQUIRED_RULES["#mainDeck input"] = FIELD_FACE

# The Page Info media panel's preview pane: the Platinum sunken field
# (see the header's provenance paragraph), a static preview surface with
# no hover or focus variant.
REQUIRED_RULES["#imagecontainerbox"] = FIELD_FACE

# The Page Info permissions panel's permission list: the Platinum sunken
# list field (see the header's provenance paragraph), with the native
# listbox frame dropped and a hovered row keeping the field's face.
REQUIRED_RULES["#permList"] = {
    "appearance": "none !important",
    **FIELD_FACE,
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
REQUIRED_RULES["#metatree"] = FIELD_FACE
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

# The Page Info security panel's group frames: the reference's etched
# group box (see the header's provenance paragraph) — the dark border
# carrying the offset highlight copy while the interiors stay transparent
# over the dialog body face, stacked frames separated by a 1em margin, and
# each frame's header taking the shared black text. A groupbox and its
# header are static, so there is no hover, focus, active or disabled
# variant.
REQUIRED_RULES["#securityPanel > groupbox"] = {
    "border": f"1px solid {ETCH_DARK} !important",
    "border-radius": "0 !important",
    "padding": "2px 8px !important",
    "box-shadow": f"1px 1px {WHITE}, inset 1px 1px {WHITE} !important",
}
REQUIRED_RULES["#securityPanel > groupbox + groupbox"] = {
    "margin-top": "1em !important",
}
REQUIRED_RULES["#securityPanel > groupbox > label.header"] = {
    "color": f"{BLACK} !important",
}

# The Library window's two places trees: the Platinum sunken list field
# (see the header's provenance paragraph), reusing the Page Info tree
# recipes' field declarations and going through the plain tree
# selectors the Page Info trees already establish. The rows are
# transparent over the field so no skin hover wash paints, the
# selected row is flat #CCCCFF and the multicol odd-row stripe is
# floated back onto the field face; a single-column tree (#placesList)
# draws no multicol odd stripe, so the stripe rule is written only
# against tree#placeContent.
REQUIRED_RULES["#placesList"] = FIELD_FACE
REQUIRED_RULES["#placeContent"] = REQUIRED_RULES["#placesList"]
for _tree in ("placesList", "placeContent"):
    REQUIRED_RULES[
        f"tree#{_tree} treechildren::-moz-tree-row(hover)"
    ] = {"background-color": "transparent !important"}
    REQUIRED_RULES[
        f"tree#{_tree} treechildren::-moz-tree-row(selected)"
    ] = {"background-color": f"{SELECTION} !important"}
    REQUIRED_RULES[
        f"tree#{_tree} treechildren::-moz-tree-cell-text"
    ] = {"color": f"{BLACK} !important"}
REQUIRED_RULES[
    "tree#placeContent treechildren::-moz-tree-row(multicol, odd)"
] = {"background-color": "transparent !important"}

# The Library window's search box: the Platinum line edit through the
# moz-input-search tokens, the byte-twin of the existing
# moz-input-search#searchInput recipe (see the header's provenance
# paragraph). A static line edit from the token route's point of view,
# so there is no hover, focus or disabled variant here.
REQUIRED_RULES["moz-input-search#searchFilter"] = {
    "--input-text-border": f"1px solid {BLACK} !important",
    "--input-text-border-radius": "0 !important",
    "--input-text-background-color": f"{WHITE} !important",
    "--input-text-color": f"{BLACK} !important",
    "--icon-color": f"{BLACK} !important",
}

# The Library content tree's column headers: the Platinum raised
# header buttons, the byte-recipe of the existing edit-bookmark footer
# buttons, with the flat #CCCCFF hover/pressed fill and no bevel (see
# the header's provenance paragraph).
HEADER_FACE = {
    "background-color": f"{FACE} !important",
    "color": f"{BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow":
        f"inset 1px 1px {WHITE}, inset -1px -1px {BUTTON_SHADOW} !important",
}
# The hovered and pressed header arms take the shared BUTTON_HOVER flush.
HEADER_HOVER = BUTTON_HOVER
for _header_arm in (
    "treecols#placeContentColumns > treecol",
    "treecols#placeContentColumns .tree-columnpicker-button",
):
    REQUIRED_RULES[_header_arm] = HEADER_FACE
for _header_arm in (
    "treecols#placeContentColumns > treecol:hover",
    "treecols#placeContentColumns > treecol:hover:active",
    "treecols#placeContentColumns .tree-columnpicker-button:hover",
    "treecols#placeContentColumns .tree-columnpicker-button:hover:active",
):
    REQUIRED_RULES[_header_arm] = HEADER_HOVER

# The Library window's toolbar band and menu titles: the byte-recipes of
# the existing #toolbar-menubar band, its menu-title padding and its open
# title, spelled explicitly with the shared palette constants rather
# than aliased (the band entry adds the black text #toolbar-menubar
# inherits, see the header's provenance paragraph).
REQUIRED_RULES["toolbar#placesToolbar"] = {
    "background-color": f"{FACE} !important",
    "color": f"{BLACK} !important",
    "border-bottom": f"1px solid {ETCH_DARK} !important",
    "box-shadow": f"inset 0 -1px {WHITE} !important",
}
REQUIRED_RULES["menubar#placesMenu > menu"] = {
    "padding": "3px 7px 0 !important",
}
REQUIRED_RULES["menubar#placesMenu > menu[open]"] = {
    "background-color": f"{SELECTION} !important",
    "border-bottom-color": f"{SELECTION} !important",
}

# The Library window's downloads view: the Platinum sunken list field
# and its square rows, the byte-recipes of the existing #placesList
# field (plus the appearance: none the browser skin needs) and of the
# existing #downloadsPanel row entries (see the header's provenance
# paragraph), spelled explicitly with the shared palette constants
# rather than aliased.
REQUIRED_RULES["#placesViewsBox richlistbox#downloadsListBox"] = {
    "appearance": "none !important",
    **FIELD_FACE,
}
REQUIRED_RULES[
    "#placesViewsBox richlistbox#downloadsListBox > richlistitem"
] = {
    "border-radius": "0 !important",
}
REQUIRED_RULES[
    "#placesViewsBox richlistbox#downloadsListBox > richlistitem[selected]"
] = {
    "background-color": f"{SELECTION} !important",
    "color": f"{BLACK} !important",
}

# The Library's Clear Downloads button: the byte-recipes of the existing
# #downloadsPanel push button and its hover arm; disabled ones keep
# Firefox's paint (see the header's provenance paragraph).
REQUIRED_RULES[
    "toolbar#placesToolbar toolbarbutton#clearDownloadsButton:not([disabled])"
] = BUTTON_FACE
REQUIRED_RULES[
    "toolbar#placesToolbar toolbarbutton#clearDownloadsButton"
    ":not([disabled]):hover"
] = BUTTON_HOVER

# The Library details pane's four bookmark fields: the byte-recipes of
# the existing #editBookmarkPanel field entries (see the header's
# provenance paragraph), spelled explicitly with the shared palette
# constants rather than aliased.
REQUIRED_RULES["#detailsPane #editBMPanel_namePicker"] = FIELD_FACE
REQUIRED_RULES["#detailsPane #editBMPanel_locationField"] = FIELD_FACE
REQUIRED_RULES["#detailsPane #editBMPanel_tagsField"] = FIELD_FACE
REQUIRED_RULES["#detailsPane #editBMPanel_keywordField"] = FIELD_FACE

# The details pane's folder dropdown: the byte-recipes of the existing
# #editBookmarkPanel folder menulist entries; disabled ones keep
# Firefox's paint.
REQUIRED_RULES["#detailsPane #editBMPanel_folderMenuList"] = BUTTON_FACE
REQUIRED_RULES[
    "#detailsPane #editBMPanel_folderMenuList:hover:not([disabled])"
] = BUTTON_HOVER

# The details pane's tag selector: the existing #placesList mapping plus
# the appearance: none the browser skin needs, with square rows and the
# existing downloads selected-row byte-recipe.
REQUIRED_RULES["#detailsPane richlistbox#editBMPanel_tagsSelector"] = {
    "appearance": "none !important",
    **FIELD_FACE,
}
REQUIRED_RULES[
    "#detailsPane richlistbox#editBMPanel_tagsSelector > richlistitem"
] = {
    "border-radius": "0 !important",
}
REQUIRED_RULES[
    "#detailsPane richlistbox#editBMPanel_tagsSelector"
    " > richlistitem[selected]"
] = {
    "background-color": f"{SELECTION} !important",
    "color": f"{BLACK} !important",
}


_chrome_fixture = None


class FirefoxChromeTestCase(
    CommentHeaderAssertions, SheetRuleAssertions, unittest.TestCase
):
    """Base case loading the sheet text, README and parsed rules once.

    The ``CommentHeaderAssertions`` mixin serves the section modules'
    header-provenance tests.

    Because every derived class reads the same shipped sheet, the read and
    parse are memoized per worker process in ``_chrome_fixture`` after the
    first ``setUpClass``: classes that run in the same module share the
    one read and parse instead of re-deriving them per class. The fixture
    tuple must stay read-only -- no test may assign into ``cls.text``,
    ``cls.readme`` or the parsed mappings.
    """

    @classmethod
    def setUpClass(cls):
        global _chrome_fixture
        if _chrome_fixture is None:
            text = containment.read_text(SHEET, ROOT, encoding="utf-8")
            readme = containment.read_text(README, ROOT, encoding="utf-8")
            colours, rules, selectors = parse_css(text, source=SHEET_PATH)
            _chrome_fixture = (text, readme, colours, rules, selectors)
        (cls.text, cls.readme,
         cls.colours, cls.rules, cls.selectors) = _chrome_fixture

    def assert_arms_match_required(self, arms):
        """Assert each selector in *arms* equals its REQUIRED_RULES entry.

        The four Library chrome suites that pin a byte-recipe group call
        this once per group with the group's selectors: each arm must
        match the shared REQUIRED_RULES table byte-for-byte and every
        declaration value must be ``!important``-pinned, one subTest per
        arm.
        """
        for arm in arms:
            with self.subTest(selector=arm):
                self.assertEqual(self.rules[arm], REQUIRED_RULES[arm])
                for value in self.rules[arm].values():
                    self.assertTrue(value.endswith("!important"))

    def assert_rules_match_required(self, selectors):
        """Assert each selector matches its shared declaration recipe."""
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])

    def assert_rule_only_has(self, selector, property_name):
        """Assert that *selector* declares only *property_name*."""
        self.assertEqual(set(self.rules[selector]), {property_name})

    def assert_rule_names_scoped_to(self, token, expected):
        """Assert the rules whose selector names *token* are just *expected*.

        The Firefox chrome suites use this sweep to pin a block of rules
        to one UI region: every selector name carrying *token* must
        appear in *expected* (any set-able collection) and nothing
        outside it may match. Twenty-one call sites across the popup,
        panel, shell and library suites replace the identical three-line
        ``assertEqual`` sweep. Compound predicates -- multi-token,
        ``startswith``-anchored or exclusion conditions -- and the sorted
        or list-form variants keep their bespoke sweeps.
        """
        self.assertEqual(
            {name for name in self.rules if token in name},
            set(expected),
        )

    def assert_token_scoped_to(self, token, expected=()):
        """Assert the rules whose declarations carry *token* are just *expected*.

        The Firefox chrome suites use this sweep to pin the scoping of a CSS
        variable override: *token* is matched against every rule's
        declaration values, and the override must not leak outside the
        selectors in *expected*. Eleven call sites in the popup, panel and
        shell suites replace the identical four-line ``assertEqual`` sweep,
        eight of them expecting no rule at all.
        """
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if token in declarations},
            set(expected),
        )
