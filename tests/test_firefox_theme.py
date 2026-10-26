"""Validate the standalone Firefox Platinum ``userChrome.css`` sheet.

No reference screenshot shows Firefox chrome, so the palette is the shared
Platinum palette and the geometry adapts this theme's Platinum controls. The
sheet ships as a standalone file; ``make install-firefox`` copies it into one
Firefox profile, and ``tests/test_firefox_install.py`` pins that install and
its removal.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from support import containment
from support.desktoptheme_paths import MENUBARITEM_SVG
from support.gtk_css import HEX, parse_css
from support.gtk_rule_cases import SheetRuleAssertions
from support.gtk_theme_spec import ETCH_DARK, RAISED_BEVEL
from support.svg_case import parse_svg
from svg_assertions import rect_geometry
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
from support.selector_matching import matches

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
}


class TestFirefoxChrome(SheetRuleAssertions, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = containment.read_text(SHEET, ROOT, encoding="utf-8")
        cls.readme = containment.read_text(README, ROOT, encoding="utf-8")
        cls.colours, cls.rules, cls.selectors = parse_css(
            cls.text, source=SHEET_PATH
        )

    def test_required_rules(self):
        for selector, expected in REQUIRED_RULES.items():
            with self.subTest(selector=selector):
                self.assert_rule(selector, expected)

    def test_panel_radius_override_is_scoped_to_menus_and_arrow_panels(self):
        self.assertEqual(
            {selector for selector, declarations in self.rules.items()
             if "--panel-border-radius" in declarations},
            {"menupopup", 'panel[type="arrow"]'},
        )

    def test_consumed_popup_colour_tokens_are_scoped_to_menus_and_arrow_panels(self):
        for token in ("--panel-background-color", "--panel-text-color",
                      "--panel-border-color"):
            with self.subTest(token=token):
                self.assertEqual(
                    {selector for selector, declarations in self.rules.items()
                     if token in declarations},
                    {"menupopup", 'panel[type="arrow"]'},
                )
        for token in ("--panel-background", "--panel-color"):
            with self.subTest(obsolete_token=token):
                self.assertNotIn(token, self.rules["menupopup"])
        for selector, declarations in self.rules.items():
            for token in ("--arrowpanel-background", "--arrowpanel-color",
                          "--arrowpanel-border-color"):
                with self.subTest(selector=selector, obsolete_token=token):
                    self.assertNotIn(token, declarations)

    def test_palette_is_exact(self):
        self.assertEqual(
            set(HEX.findall(self.text)),
            {BLACK, WHITE, GREY, FACE, TROUGH, SELECTION, ETCH_DARK, TOOLTIP_FACE},
        )

    def test_search_field_paint_is_scoped_to_the_unfocused_classic_field(self):
        selector = "#searchbar:not(:focus-within)"
        self.assertEqual(
            {name for name in self.rules if "searchbar" in name},
            {selector},
        )
        self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])

    def test_tab_hover_paint_is_scoped_to_unselected_tabs(self):
        hover = (
            ".tabbrowser-tab:hover > .tab-stack > .tab-background"
            ":not([selected]):not([multiselected])"
        )
        selected = ".tabbrowser-tab:is([selected], [multiselected]) .tab-background"
        self.assertEqual(
            {name for name in self.rules if "tab-background" in name},
            {
                ".tab-background",
                selected,
                hover,
            },
        )
        for selector in (
            ".tab-background",
            selected,
            hover,
        ):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        for part in (":hover", ":not([selected])", ":not([multiselected])"):
            with self.subTest(part=part):
                self.assertIn(part, hover)

    def test_selected_face_covers_multiselected_tabs(self):
        selected = ".tabbrowser-tab:is([selected], [multiselected]) .tab-background"
        hover = (
            ".tabbrowser-tab:hover > .tab-stack > .tab-background"
            ":not([selected]):not([multiselected])"
        )
        self.assertIn("[selected]", selected)
        self.assertIn("[multiselected]", selected)
        self.assertEqual(self.rules[selected], REQUIRED_RULES[selected])
        self.assertEqual(self.rules[selected]["background-color"],
                         f"{TROUGH} !important")
        self.assertEqual(self.rules[selected]["border-bottom-color"],
                         f"{TROUGH} !important")
        for name in self.rules:
            if ("tab-background" in name and "[selected]" in name
                    and "[multiselected]" not in name):
                with self.subTest(selected_only=name):
                    self.assertNotIn("background-color", self.rules[name])
        self.assertEqual(
            {name for name in self.rules if "multiselected" in name},
            {selected, hover},
        )

    def test_menubar_title_geometry_matches_the_menubaritem_margins(self):
        selector = "#toolbar-menubar menubar > menu"
        geometry = rect_geometry(parse_svg(MENUBARITEM_SVG))
        top = int(geometry["normal-hint-top-margin"][3])
        bottom = int(geometry["normal-hint-bottom-margin"][3])
        left = int(geometry["normal-hint-left-margin"][2])
        right = int(geometry["normal-hint-right-margin"][2])
        self.assertEqual((top, bottom), (3, 3))
        self.assertEqual((left, right), (7, 7))
        # The retained stock bottom border completes the bottom margin, so
        # the sheet's bottom pad is the margin minus that border.
        bottom_pad = bottom - MENU_STOCK_BOTTOM_BORDER
        bottom_value = f"{bottom_pad}px" if bottom_pad else "0"
        self.assertEqual(
            self.rules[selector],
            {"padding": f"{top}px {left}px {bottom_value} !important"},
        )
        pad_top, pad_right, pad_bottom = (
            int(value.removesuffix("px"))
            for value in self.rules[selector]["padding"]
            .removesuffix(" !important").split()
        )
        self.assertEqual(
            (pad_top, pad_right, pad_bottom),
            (top, left, bottom_pad),
        )
        self.assertEqual(pad_bottom + MENU_STOCK_BOTTOM_BORDER, bottom)

    def test_menubar_open_title_paint_is_scoped_to_the_open_title(self):
        selector = "#toolbar-menubar menubar > menu[open]"
        base = "#toolbar-menubar menubar > menu"
        # A menu-bar title is a ``menu`` element outside a popup, so catch a
        # rule that targets one without naming #toolbar-menubar, such as a
        # bare ``menu[open]:hover``, rather than only selectors spelled
        # ``menubar``.
        title_rules = {
            name for name in self.rules
            if "menubar" in name
            or ("menu" in re.findall(r"[-\w]+", name)
                and "menupopup" not in name)
        }
        self.assertEqual(title_rules, {"#toolbar-menubar", base, selector})
        for name in ("#toolbar-menubar", base, selector):
            with self.subTest(selector=name):
                self.assertEqual(self.rules[name], REQUIRED_RULES[name])
        self.assertEqual(set(self.rules[base]), {"padding"})
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if declarations == REQUIRED_RULES[selector]},
            {selector},
        )

    def test_sidebar_frame_is_scoped_to_the_box_and_header(self):
        self.assertEqual(
            {name for name in self.rules if "sidebar" in name},
            {"#sidebar-box", "#sidebar-header"},
        )
        for selector in ("#sidebar-box", "#sidebar-header"):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        self.assertEqual(self.rules["#sidebar-box"]["background-color"],
                         f"{FACE} !important")
        self.assertEqual(self.rules["#sidebar-box"]["color"],
                         f"{BLACK} !important")
        self.assertEqual(self.rules["#sidebar-header"]["border-bottom"],
                         f"1px solid {ETCH_DARK} !important")
        self.assertEqual(self.rules["#sidebar-header"]["box-shadow"],
                         f"inset 0 -1px {WHITE} !important")

    def test_downloads_panel_row_paint_is_scoped_to_the_panel_list(self):
        row = "#downloadsPanel #downloadsListBox > richlistitem"
        hover = row + ":not([selected]):hover"
        selected = row + "[selected]"
        self.assertEqual(
            {name for name in self.rules if "downloadsListBox" in name},
            {row, hover, selected},
        )
        for selector in (row, hover, selected):
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith(row))
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        self.assertIn(":not([selected])", hover)
        self.assertIn(":hover", hover)
        self.assertEqual(self.rules[hover]["background-color"],
                         f"{FACE} !important")
        self.assertEqual(self.rules[selected]["background-color"],
                         f"{SELECTION} !important")
        self.assertLess(
            self.selectors.index(hover),
            self.selectors.index(selected),
        )

    def test_all_tabs_row_paint_is_scoped_to_the_all_tabs_view(self):
        row = "#allTabsMenu-allTabsView .all-tabs-item"
        button = "#allTabsMenu-allTabsView .all-tabs-item > .all-tabs-button"
        hover = (
            "#allTabsMenu-allTabsView .all-tabs-item:not([selected])"
            " > .all-tabs-button:hover"
        )
        selected = (
            "#allTabsMenu-allTabsView .all-tabs-item[selected]"
            " > .all-tabs-button"
        )
        self.assertEqual(
            {name for name in self.rules
             if "allTabsMenu" in name or "all-tabs" in name},
            {row, button, hover, selected},
        )
        for selector in (row, button, hover, selected):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "--panel-menuitem-border-radius" in declarations},
            set(),
        )
        self.assertIn(":not([selected])", hover)
        self.assertIn(":hover", hover)
        self.assertEqual(self.rules[hover]["background-color"],
                         f"{FACE} !important")
        self.assertEqual(self.rules[selected]["background-color"],
                         f"{SELECTION} !important")
        self.assertLess(
            self.selectors.index(hover),
            self.selectors.index(selected),
        )

    def test_app_menu_row_paint_is_scoped_to_the_app_menu(self):
        radius = "#appMenu-popup .subviewbutton:not(.panel-header .subviewbutton)"
        hover = radius + ":hover:not([disabled])"
        self.assertEqual(
            {name for name in self.rules if "appMenu" in name},
            {radius, hover},
        )
        for selector in (radius, hover):
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith(radius))
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        self.assertIn(":not([disabled])", hover)
        self.assertIn(":hover", hover)
        self.assertIn(":not(.panel-header .subviewbutton)", radius)
        self.assertEqual(set(self.rules[radius]), {"border-radius"})
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "--panel-menuitem-border-radius" in declarations},
            set(),
        )

        def element(tag, identifier=None, classes=(), attrs=None,
                    hover=False, parent=None):
            return {
                "tag": tag,
                "id": identifier,
                "classes": set(classes),
                "attrs": dict(attrs or {}),
                "hover": hover,
                "parent": parent,
            }

        panel = element("panel", "appMenu-popup")
        main_view = element(
            "panelview", "appMenu-mainView", ("PanelUI-subView",),
            parent=panel,
        )
        body = element(
            "vbox", classes=("panel-subview-body",), parent=main_view
        )
        row = element(
            "toolbarbutton", "appMenu-settings-button", ("subviewbutton",),
            parent=body,
        )
        footer_rows = {
            "history": element(
                "toolbarbutton", "PanelUI-historyMore",
                ("subviewbutton", "panel-subview-footer-button"),
                parent=element("panelview", "PanelUI-history", parent=panel),
            ),
            "bookmarks": element(
                "toolbarbutton", "panelMenu_showAllBookmarks",
                ("subviewbutton", "panel-subview-footer-button"),
                parent=element("panelview", "PanelUI-bookmarks", parent=panel),
            ),
        }
        header = element(
            "box", "PanelUI-profiles-header", ("panel-header",),
            parent=element("panelview", "PanelUI-profiles", parent=panel),
        )
        header_buttons = {
            "back": element(
                "toolbarbutton", "profiles-appmenu-back-button",
                ("subviewbutton", "subviewbutton-iconic", "subviewbutton-back"),
                parent=header,
            ),
            "edit": element(
                "toolbarbutton", "profiles-edit-this-profile-button",
                ("subviewbutton", "subviewbutton-iconic"),
                parent=header,
            ),
        }
        self.assertTrue(matches(radius, row))
        self.assertTrue(matches(hover, {**row, "hover": True}))
        self.assertFalse(matches(hover, row))
        self.assertFalse(
            matches(hover, {**row, "hover": True, "attrs": {"disabled": ""}})
        )
        for name, button in footer_rows.items():
            with self.subTest(footer_row=name):
                self.assertTrue(matches(radius, button))
                self.assertTrue(matches(hover, {**button, "hover": True}))
        for name, button in header_buttons.items():
            with self.subTest(header_button=name):
                self.assertFalse(matches(radius, button))
                self.assertFalse(matches(hover, {**button, "hover": True}))

    def test_overflow_panel_row_paint_is_scoped_to_the_overflow_panel(self):
        radius_rows = (
            "#widget-overflow .subviewbutton:not(.panel-header .subviewbutton)",
            "#widget-overflow .widget-overflow-list .toolbarbutton-1",
        )
        hover_rows = (
            radius_rows[0] + ":hover:not([disabled])",
            radius_rows[1] + ":hover:not([disabled])",
        )
        self.assertEqual(
            {name for name in self.rules if "widget-overflow" in name},
            set(radius_rows + hover_rows),
        )
        for selector in radius_rows + hover_rows:
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith("#widget-overflow"))
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        for selector in radius_rows:
            self.assertEqual(set(self.rules[selector]), {"border-radius"})
        for selector in hover_rows:
            self.assertIn(":hover", selector)
            self.assertIn(":not([disabled])", selector)
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "--panel-menuitem-border-radius" in declarations},
            set(),
        )

        def element(tag, identifier=None, classes=(), attrs=None,
                    hover=False, parent=None):
            return {
                "tag": tag,
                "id": identifier,
                "classes": set(classes),
                "attrs": dict(attrs or {}),
                "hover": hover,
                "parent": parent,
            }

        panel = element("panel", "widget-overflow")
        main_view = element(
            "panelmultiview", "widget-overflow-mainView", parent=panel
        )
        body = element(
            "vbox", classes=("panel-subview-body",), parent=main_view
        )
        overflow_lists = {
            "main": element(
                "vbox", "widget-overflow-list", ("widget-overflow-list",),
                parent=body,
            ),
            "fixed": element(
                "vbox", "widget-overflow-fixed-list",
                ("widget-overflow-list",), parent=body,
            ),
        }
        overflowed_rows = {
            name: element(
                "toolbarbutton", classes=("toolbarbutton-1",), parent=row_list
            )
            for name, row_list in overflow_lists.items()
        }
        footer = element(
            "toolbarbutton", "overflowMenu-customize-button",
            ("subviewbutton", "panel-subview-footer-button"), parent=body,
        )
        header = element("box", classes=("panel-header",), parent=main_view)
        header_button = element(
            "toolbarbutton", "overflow-panel-back-button",
            ("subviewbutton", "subviewbutton-back"), parent=header,
        )
        nav_bar_button = element(
            "toolbarbutton", "nav-bar-button", ("toolbarbutton-1",),
            parent=element("toolbar", "nav-bar"),
        )

        for name, row in overflowed_rows.items():
            with self.subTest(overflowed_row=name):
                self.assertTrue(matches(radius_rows[1], row))
                self.assertTrue(matches(hover_rows[1], {**row, "hover": True}))
                self.assertFalse(matches(hover_rows[1], row))

        self.assertTrue(matches(radius_rows[0], footer))
        self.assertTrue(matches(hover_rows[0], {**footer, "hover": True}))
        self.assertFalse(matches(hover_rows[0], footer))

        disabled = {
            **overflowed_rows["main"], "attrs": {"disabled": ""},
            "hover": True,
        }
        for selector in hover_rows:
            self.assertFalse(matches(selector, disabled))

        for selector in radius_rows + hover_rows:
            with self.subTest(selector=selector):
                self.assertFalse(matches(selector, header_button))
                self.assertFalse(
                    matches(selector, {**header_button, "hover": True})
                )
                self.assertFalse(matches(selector, nav_bar_button))
                self.assertFalse(
                    matches(selector, {**nav_bar_button, "hover": True})
                )

    def test_unified_extensions_panel_row_paint_is_scoped_to_the_panel(self):
        radius = (
            "#unified-extensions-panel .subviewbutton"
            ":not(.panel-header .subviewbutton)"
            ":not(.unified-extensions-item-menu-button)"
            ":not(#unified-extensions-discover-extensions)"
        )
        hover = radius + ":hover:not([disabled])"
        gear_hover = (
            "#unified-extensions-panel "
            ".unified-extensions-item-menu-button:hover"
        )
        selectors = (radius, hover, gear_hover)
        self.assertEqual(
            {name for name in self.rules if "unified-extensions" in name},
            set(selectors),
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith("#unified-extensions-panel"))
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        self.assertEqual(set(self.rules[radius]), {"border-radius"})
        self.assertEqual(set(self.rules[gear_hover]), {"box-shadow"})
        self.assertIn(":hover", hover)
        self.assertIn(":not([disabled])", hover)
        for selector in (radius, hover):
            self.assertIn(
                ":not(.unified-extensions-item-menu-button)", selector
            )
            self.assertIn(":not(.panel-header .subviewbutton)", selector)
            self.assertIn(
                ":not(#unified-extensions-discover-extensions)", selector
            )
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "--panel-menuitem-border-radius" in declarations},
            set(),
        )

        def element(tag, identifier=None, classes=(), attrs=None,
                    hover=False, parent=None):
            return {
                "tag": tag,
                "id": identifier,
                "classes": set(classes),
                "attrs": dict(attrs or {}),
                "hover": hover,
                "parent": parent,
            }

        panel = element("panel", "unified-extensions-panel")
        view = element(
            "panelview", "unified-extensions-view",
            ("cui-widget-panelview",), parent=panel,
        )
        body = element(
            "vbox", classes=("panel-subview-body",), parent=view
        )
        extensions_list = element(
            "vbox", classes=("unified-extensions-list",), parent=body
        )
        item = element("unified-extensions-item", parent=extensions_list)
        row = element(
            "box", classes=("unified-extensions-item-row-wrapper",),
            parent=item,
        )
        action = element(
            "toolbarbutton",
            classes=(
                "unified-extensions-item-action-button", "subviewbutton",
            ),
            parent=row,
        )
        gear = element(
            "toolbarbutton",
            classes=(
                "unified-extensions-item-menu-button", "subviewbutton",
                "subviewbutton-iconic",
            ),
            parent=row,
        )
        area = element("vbox", "unified-extensions-area", parent=body)
        extension_btn = element(
            "toolbarbutton",
            classes=("webextension-browser-action", "subviewbutton"),
            parent=area,
        )
        footer = element(
            "toolbarbutton", "unified-extensions-manage-extensions",
            ("subviewbutton", "panel-subview-footer-button"), parent=body,
        )
        discover = element(
            "moz-button", "unified-extensions-discover-extensions",
            ("subviewbutton", "panel-subview-footer-button"), parent=body,
        )
        header = element("box", classes=("panel-header",), parent=view)
        header_button = element(
            "toolbarbutton", "unified-extensions-header-button",
            ("subviewbutton",), parent=header,
        )
        nav_bar_button = element(
            "toolbarbutton", "nav-bar-button", ("toolbarbutton-1",),
            parent=element("toolbar", "nav-bar"),
        )

        for name, row_button in (
            ("action", action),
            ("webextension", extension_btn),
            ("footer", footer),
        ):
            with self.subTest(row=name):
                self.assertTrue(matches(radius, row_button))
                self.assertTrue(
                    matches(hover, {**row_button, "hover": True})
                )
                self.assertFalse(matches(hover, row_button))

        disabled = {
            **action, "attrs": {"disabled": ""}, "hover": True,
        }
        self.assertFalse(matches(hover, disabled))

        for name, unthemed in (
            ("gear", gear),
            ("header", header_button),
            ("nav_bar", nav_bar_button),
            ("discover", discover),
        ):
            with self.subTest(unthemed=name):
                self.assertFalse(matches(radius, unthemed))
                self.assertFalse(
                    matches(hover, {**unthemed, "hover": True})
                )
        self.assertTrue(matches(gear_hover, {**gear, "hover": True}))

    def test_find_field_foreground_is_guarded(self):
        selector = (
            'findbar .findbar-textbox:not([status="notfound"])'
            ':not([flash="true"]):not(:focus)'
        )
        self.assertEqual(
            {name for name in self.rules if "findbar-textbox" in name},
            {selector},
        )
        self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        self.assertEqual(self.rules["findbar"], REQUIRED_RULES["findbar"])

    def test_tooltip_face_is_scoped_to_explicit_tooltips(self):
        self.assertEqual(
            {selector for selector, declarations in self.rules.items()
             if any(TOOLTIP_FACE in value.upper()
                    for value in declarations.values())},
            {"tooltip"},
        )
        self.assertEqual(self.rules["tooltip"], REQUIRED_RULES["tooltip"])

    def test_results_paint_does_not_override_shared_tokens(self):
        # Firefox also consumes these tokens on realtime sub-items and one-offs.
        for selector, declarations in self.rules.items():
            with self.subTest(selector=selector):
                self.assertFalse(any(
                    name.startswith("--urlbarview-") for name in declarations
                ))
                if "urlbarView" in selector:
                    self.assertIn(selector, REQUIRED_RULES)
                    self.assertEqual(declarations, REQUIRED_RULES[selector])

    def test_sheet_has_no_at_rule_or_import(self):
        self.assertNotIn("@", self.text)

    def test_sheet_does_not_name_adwaita(self):
        self.assertNotIn("adwaita", self.text.lower())

    def test_selectors_are_not_universal(self):
        for selector in self.selectors:
            self.assertNotIn("*", selector)

    def test_header_names_provenance_and_preference(self):
        self.assertIn("Provenance exception", self.text)
        header = self.text.split("*/", 1)[0]
        for provenance in (
            "No reference shows Firefox tab hover",
            "tests/test_desktoptheme_scrollbar.py::TestScrollbarReference",
            "No reference shows Firefox tooltips or a Balloon Help balloon",
            "platform adaptation 2026-10-25",
            "[Colors:Tooltip] BackgroundNormal",
            "TOOLTIP_FACE", "classic-palette exception accepted in QUESTIONS.md",
            "not a screenshot sample", "widgets/tooltip.svg",
            "tests/test_desktoptheme_tooltip.py::TestTooltip.test_tooltip_pixels",
            "chrome/toolkit/content/global/xul.css",
            "selector; default native anonymous tooltips require UA styling",
            "outside this sheet's guarantee",
            "No reference shows Firefox's optional classic search field",
            "chrome/browser/skin/classic/browser/urlbar-searchbar.css",
            "and owns the focused appearance",
            "#searchbar-new stays Firefox's",
            "No reference shows Firefox's find field",
            "chrome/toolkit/skin/classic/global/findbar.css",
            "not-found and flash states stay",
            "No reference shows Firefox's menu bar titles",
            "TestMenuBarItem.test_menubaritem_hint_geometry",
            "TestMenuTitleSpacingMatchesReference",
            "padding: 0.25em 0.5em",
            "zero bottom pad",
            "retained stock border",
            "chrome/toolkit/skin/classic/global/menu.css",
            "platform geometry adaptation 2026-10-26",
            "No reference shows Firefox multi-selected tabs",
            "selected=visuallyselected",
            "platform colour adaptation 2026-10-26",
            "No reference shows Firefox's menu bar",
            "TestMenuBarItem.test_menubaritem_pressed_is_flat_selection_colour",
            "TestReferenceAnchors.test_selection_background",
            "No reference shows a Firefox sidebar",
            "chrome/browser/skin/classic/browser/sidebar.css",
            "--sidebar-background-color",
            "modules/ThemeVariableMap.sys.mjs",
            "No reference shows Firefox's downloads panel",
            "widgets/listitem.svg",
            "tests/test_desktoptheme_listitem.py::TestListItem",
            "chrome/browser/skin/classic/browser/downloads/downloads.inc.css",
            "chrome/toolkit/skin/classic/global/richlistbox.css",
            "chrome/browser/content/browser/browser.xhtml",
            "moz-src/browser/components/downloads/DownloadsViewUI.sys.mjs",
            "--button-background-color-ghost-hover",
            "richlistitem[selected=\"true\"]",
            "platform colour adaptation 2026-10-26",
            "the sidebar's inner document is not userChrome territory",
            "No reference shows Firefox's all-tabs panel",
            "widgets/listitem.svg",
            "tests/test_desktoptheme_listitem.py::TestListItem",
            "allTabsMenu-allTabsView",
            "all-tabs-item",
            "chrome/browser/skin/classic/browser/tabbrowser/tabs.css",
            "chrome/toolkit/skin/classic/global/design-system/tokens-shared.css",
            "chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css",
            "moz-src/browser/components/tabbrowser/TabsList.sys.mjs",
            "--button-background-color-ghost-hover",
            "--panel-menuitem-border-radius",
            "--border-radius-small",
            "platform colour adaptation 2026-10-26",
            "No reference shows Firefox's app menu",
            "widgets/viewitem.svg",
            "tests/test_desktoptheme_viewitem.py::TestViewItem",
            "chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css",
            "#appMenu-popup",
            "panel-subview-body",
            "panel-subview-footer-button",
            "panel-header",
            "toolbarbutton.subviewbutton",
            "--panel-menuitem-border-radius",
            "--button-background-color-ghost-hover",
            "platform colour adaptation 2026-10-26",
            "No reference shows Firefox's toolbar overflow panel",
            "widgets/viewitem.svg",
            "tests/test_desktoptheme_viewitem.py::TestViewItem",
            "test_selection_background",
            "chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css",
            "chrome/browser/content/browser/browser.xhtml",
            "#widget-overflow",
            "widget-overflow-list",
            "widget-overflow-fixed-list",
            "#overflowMenu-customize-button",
            "--panel-menuitem-border-radius",
            "--button-background-color-ghost-hover",
            "platform colour adaptation 2026-10-26",
            "No reference shows Firefox's unified extensions panel",
            "widgets/viewitem.svg",
            "tests/test_desktoptheme_viewitem.py::TestViewItem",
            "test_selection_background",
            "chrome/browser/skin/classic/browser/addons/unified-extensions.css",
            "chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css",
            "chrome/browser/content/browser/browser.xhtml",
            "chrome/browser/content/browser/browser-addons.js",
            "#unified-extensions-discover-extensions",
            "#unified-extensions-panel",
            "#unified-extensions-view",
            "unified-extensions-item-action-button",
            "unified-extensions-item-menu-button",
            "#unified-extensions-manage-extensions",
            "--panel-menuitem-border-radius",
            "--button-background-color-ghost-hover",
            "platform colour adaptation 2026-10-26",
        ):
            with self.subTest(provenance=provenance):
                self.assertIn(provenance, header)
        self.assertIn(
            "toolkit.legacyUserProfileCustomizations.stylesheets",
            self.text,
        )

    def test_readme_names_the_sheet(self):
        self.assertIn(SHEET_PATH, self.readme)


if __name__ == "__main__":
    unittest.main()
