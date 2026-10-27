"""Validate the Firefox Platinum sheet's chrome shell and whole-sheet rules.

The menubar, tab strip, search field, sidebar, find bar and tooltip paints,
the exact palette and the whole-sheet hygiene checks (required rules, no
``@``-rule or import, no Adwaita fallback, no universal selectors, the
header's provenance and preference note, and the README's pointer) for the
standalone ``userChrome.css``.
"""

from __future__ import annotations

import re
import unittest

from support.desktoptheme_paths import MENUBARITEM_SVG
from support.css_header import comment_header
from support.firefox_chrome_cases import (
    BUTTON_REFERENCES,
    MENU_STOCK_BOTTOM_BORDER,
    REQUIRED_RULES,
    SHEET_PATH,
    VIEWITEM_REFERENCES,
    FirefoxChromeTestCase,
)
from support.gtk_css import HEX
from support.gtk_theme_spec import ETCH_DARK
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
from support.svg_case import parse_svg
from svg_assertions import rect_geometry


class TestFirefoxChromeShell(FirefoxChromeTestCase):
    """Section of the Firefox chrome sheet under test."""

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
            {
                BLACK, WHITE, GREY, FACE, TROUGH, SELECTION, ETCH_DARK,
                TOOLTIP_FACE, BUTTON_SHADOW,
            },
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
        header = comment_header(self.text)
        self.assert_header_names((
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
            "No reference shows Firefox's downloads panel buttons",
            *BUTTON_REFERENCES,
            *VIEWITEM_REFERENCES,
            "test_selection_background",
            "downloadsPanelFooterButton",
            "downloadButton",
            "footer-button",
            "DownloadsViewUI.sys.mjs",
            "panelUI-shared.css",
            "global-shared.css",
            "disabled buttons keep Firefox's paint",
            "platform colour adaptation 2026-10-26",
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
            *VIEWITEM_REFERENCES,
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
            *VIEWITEM_REFERENCES,
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
            *VIEWITEM_REFERENCES,
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
            "No reference shows Firefox's site-information panel",
            *VIEWITEM_REFERENCES,
            "test_selection_background",
            "chrome/browser/skin/classic/browser/controlcenter/panel.css",
            "chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css",
            "chrome/browser/content/browser/browser.xhtml",
            "moz-src/browser/components/customizableui/PanelMultiView.sys.mjs",
            "#identity-popup",
            "identity-popup-mainView-panel-header",
            "identity-popup-security-button",
            "identity-popup-clear-sitedata-button",
            "identity-popup-more-info",
            "subviewbutton-back",
            "--panel-menuitem-border-radius",
            "--button-background-color-ghost-hover",
            "platform colour adaptation 2026-10-26",
            "No reference shows Firefox's protections panel",
            *VIEWITEM_REFERENCES,
            "test_selection_background",
            "chrome/browser/skin/classic/browser/controlcenter/panel.css",
            "chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css",
            "chrome/browser/content/browser/browser.xhtml",
            "chrome/browser/content/browser/browser-siteProtections.js",
            "moz-src/browser/components/customizableui/PanelMultiView.sys.mjs",
            "#protections-popup",
            "protections-popup-mainView-panel-header",
            "protections-popup-main-body",
            "protections-popup-category-trackers",
            "protections-popup-report-broken-site-button",
            "protections-popup-settings-button",
            "protections-popup-show-report-stack",
            "protections-popup-trackers-blocked-counter-box",
            "protections-popup-milestones-content",
            "protections-popup-cookie-banner-switch",
            "protections-popup-list-item",
            "subviewbutton-back",
            "--panel-menuitem-border-radius",
            "--button-background-color-ghost-hover",
            "platform colour adaptation 2026-10-26",
            "No reference shows Firefox's permission popup",
            *BUTTON_REFERENCES,
            *VIEWITEM_REFERENCES,
            "test_selection_background",
            "chrome/browser/content/browser/browser.xhtml",
            "template-permission-popup",
            "chrome/browser/content/browser/browser-sitePermissionPanel.js",
            "_createPermissionItem",
            "_createPermissionClearButton",
            "chrome/browser/skin/classic/browser/controlcenter/panel.css",
            "permission-popup-permission-remove-button",
            "permission-popup-menulist",
            "chrome/toolkit/skin/classic/global/button.css",
            "chrome/toolkit/skin/classic/global/menulist.css",
            "chrome/toolkit/skin/classic/global/design-system/tokens-shared.css",
            "--button-background-color",
            "--button-border-radius",
            "platform colour adaptation 2026-10-26",
            "No reference shows Firefox's trust panel",
            *VIEWITEM_REFERENCES,
            "test_selection_background",
            "chrome/browser/content/browser/navigator-toolbox.js",
            "browser.urlbar.trustPanel.featureGate",
            "defaults/preferences/firefox.js",
            "chrome/browser/content/browser/browser-siteProtections.js",
            "showProtectionsPopup",
            "chrome/browser/content/browser/browser.xhtml",
            "template-trustpanel-popup",
            "trustpanel-popup-connection",
            "trustpanel-clear-cookies-button",
            "trustpanel-privacy-link",
            "trustpanel-siteinformation-morelink",
            "trustpanel-toggle",
            "chrome/browser/content/browser/browser-trustPanel.js",
            "moz-button-subviewbutton-nav",
            "chrome/browser/skin/classic/browser/controlcenter/panel.css",
            "chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css",
            "chrome/toolkit/skin/classic/global/design-system/tokens-shared.css",
            "platform colour adaptation 2026-10-26",
        ))
        trust_provenance = header.split(
            "No reference shows Firefox's trust panel", 1
        )[1]
        self.assertIn(
            "moz-src/browser/components/customizableui/PanelMultiView.sys.mjs"
            " creates the trust panel's .panel-header back button",
            " ".join(trust_provenance.split()),
        )
        self.assertIn(
            "toolkit.legacyUserProfileCustomizations.stylesheets",
            self.text,
        )

    def test_readme_names_the_sheet(self):
        self.assertIn(SHEET_PATH, self.readme)



if __name__ == "__main__":
    unittest.main()
