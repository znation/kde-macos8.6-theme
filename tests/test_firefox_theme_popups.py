"""Validate the Firefox Platinum sheet's popup paints.

The identity, protections, trust, permission and notification popups for
the standalone ``userChrome.css``.
"""

from __future__ import annotations

import unittest

from support.firefox_chrome_cases import (
    REQUIRED_RULES,
    FirefoxChromeTestCase,
)
from support.selector_matching import element, matches


class TestFirefoxPopupRows(FirefoxChromeTestCase):
    """Section of the Firefox chrome sheet under test."""

    def test_identity_popup_row_paint_is_scoped_to_the_identity_popup(self):
        radius = (
            "#identity-popup .subviewbutton"
            ":not(.panel-header .subviewbutton)"
        )
        hover = radius + ":hover:not([disabled])"
        self.assertEqual(
            {name for name in self.rules if "identity-popup" in name},
            {radius, hover},
        )
        for selector in (radius, hover):
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith("#identity-popup"))
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
                self.assertIn(":not(.panel-header .subviewbutton)", selector)
        self.assertEqual(set(self.rules[radius]), {"border-radius"})
        self.assertIn(":hover", hover)
        self.assertIn(":not([disabled])", hover)
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "--panel-menuitem-border-radius" in declarations},
            set(),
        )

        panel = element("panel", "identity-popup")
        multi_view = element(
            "panelmultiview", "identity-popup-multiView", parent=panel
        )
        main_view = element(
            "panelview", "identity-popup-mainView", ("PanelUI-subView",),
            parent=multi_view,
        )
        header = element(
            "box", "identity-popup-mainView-panel-header",
            ("panel-header",), parent=main_view,
        )
        header_button = element(
            "toolbarbutton",
            classes=(
                "subviewbutton", "subviewbutton-iconic",
                "subviewbutton-back",
            ),
            parent=header,
        )
        body = element(
            "vbox", classes=("panel-subview-body",), parent=main_view
        )
        connection = element(
            "toolbarbutton", "identity-popup-security-button",
            (
                "identity-popup-security-connection", "subviewbutton",
                "subviewbutton-iconic",
            ),
            parent=body,
        )
        clear_footer = element(
            "vbox", "identity-popup-clear-sitedata-footer",
            ("panel-subview-footer-button",), parent=main_view,
        )
        clear_sitedata = element(
            "toolbarbutton", "identity-popup-clear-sitedata-button",
            ("subviewbutton",), parent=clear_footer,
        )
        security_view = element(
            "panelview", "identity-popup-securityView", ("PanelUI-subView",),
            parent=multi_view,
        )
        security_body = element(
            "vbox", classes=("panel-subview-body",), parent=security_view
        )
        cert_action = element(
            "button", "identity-popup-remove-cert-exception",
            ("panel-button",), parent=security_body,
        )
        more_info_footer = element(
            "vbox", "identity-popup-more-info-footer", parent=security_view
        )
        more_info = element(
            "toolbarbutton", "identity-popup-more-info",
            ("subviewbutton", "panel-subview-footer-button"),
            parent=more_info_footer,
        )
        nav_bar_button = element(
            "toolbarbutton", "nav-bar-button", ("toolbarbutton-1",),
            parent=element("toolbar", "nav-bar"),
        )

        for name, row in (
            ("connection", connection),
            ("clear-sitedata", clear_sitedata),
            ("more-info", more_info),
        ):
            with self.subTest(row=name):
                self.assertTrue(matches(radius, row))
                self.assertTrue(matches(hover, {**row, "hover": True}))
                self.assertFalse(matches(hover, row))

        disabled = {
            **connection, "attrs": {"disabled": ""}, "hover": True,
        }
        self.assertFalse(matches(hover, disabled))

        for name, unthemed in (
            ("header_back", header_button),
            ("cert_action", cert_action),
            ("nav_bar", nav_bar_button),
        ):
            with self.subTest(unthemed=name):
                self.assertFalse(matches(radius, unthemed))
                self.assertFalse(
                    matches(hover, {**unthemed, "hover": True})
                )

    def test_protections_popup_row_paint_is_scoped_to_the_protections_popup(self):
        radius = (
            "#protections-popup .subviewbutton"
            ":not(.panel-header .subviewbutton)"
        )
        hover = radius + ":hover:not([disabled])"
        stack_hover = (
            "#protections-popup-show-report-stack:hover > "
            ".protections-popup-footer-button:not([disabled])"
        )
        self.assertEqual(
            {name for name in self.rules if "protections-popup" in name},
            {radius, hover, stack_hover},
        )
        for selector in (radius, hover):
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith("#protections-popup"))
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
                self.assertIn(":not(.panel-header .subviewbutton)", selector)
        self.assertEqual(set(self.rules[radius]), {"border-radius"})
        for selector in (hover, stack_hover):
            with self.subTest(hover_selector=selector):
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
                self.assertIn(":hover", selector)
                self.assertIn(":not([disabled])", selector)
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "--panel-menuitem-border-radius" in declarations},
            set(),
        )

        panel = element("panel", "protections-popup")
        multi_view = element(
            "panelmultiview", "protections-popup-multiView", parent=panel
        )
        main_view = element(
            "panelview", "protections-popup-mainView", ("PanelUI-subView",),
            parent=multi_view,
        )
        header = element(
            "box", "protections-popup-mainView-panel-header",
            ("panel-header",), parent=main_view,
        )
        header_button = element(
            "toolbarbutton",
            classes=(
                "subviewbutton", "subviewbutton-iconic",
                "subviewbutton-back",
            ),
            parent=header,
        )
        info_button = element(
            "toolbarbutton", "protections-popup-info-button",
            ("panel-info-button",), parent=header,
        )
        body = element(
            "vbox", "protections-popup-main-body",
            ("panel-subview-body",), parent=main_view,
        )
        switch = element(
            "html:moz-toggle", "protections-popup-tp-switch", parent=body
        )
        report_broken = element(
            "toolbarbutton", "protections-popup-report-broken-site-button",
            ("subviewbutton", "subviewbutton-nav"), parent=body,
        )
        category = element(
            "toolbarbutton", "protections-popup-category-trackers",
            (
                "protections-popup-category", "subviewbutton",
                "subviewbutton-iconic",
            ),
            parent=body,
        )
        milestones = element(
            "toolbarbutton", "protections-popup-milestones-content",
            ("subviewbutton",), parent=body,
        )
        cookie_banner = element(
            "toolbarbutton", "protections-popup-cookie-banner-switch",
            ("subviewbutton", "subviewbutton-nav"), parent=body,
        )
        footer = element(
            "vbox", "protections-popup-footer",
            ("panel-subview-footer-button",), parent=main_view,
        )
        settings = element(
            "toolbarbutton", "protections-popup-settings-button",
            ("subviewbutton", "protections-popup-footer-button"),
            parent=footer,
        )
        show_report_stack = element(
            "stack", "protections-popup-show-report-stack", parent=footer
        )
        show_report = element(
            "toolbarbutton", "protections-popup-show-report-button",
            ("subviewbutton", "protections-popup-footer-button"),
            parent=show_report_stack,
        )
        blocked_counter = element(
            "hbox", "protections-popup-trackers-blocked-counter-box",
            parent=show_report_stack,
        )
        trackers_view = element(
            "panelview", "protections-popup-trackersView", ("PanelUI-subView",),
            parent=multi_view,
        )
        trackers_footer = element(
            "vbox", classes=("panel-subview-footer-button",),
            parent=trackers_view,
        )
        trackers_settings = element(
            "toolbarbutton", "protections-popup-trackersView-settings-button",
            ("subviewbutton", "panel-subview-footer-button"),
            parent=trackers_footer,
        )
        list_item = element(
            "div", classes=("protections-popup-list-item",), parent=body
        )
        nav_bar_button = element(
            "toolbarbutton", "nav-bar-button", ("toolbarbutton-1",),
            parent=element("toolbar", "nav-bar"),
        )

        for name, row in (
            ("category", category),
            ("report-broken-site", report_broken),
            ("settings", settings),
            ("show-report", show_report),
            ("milestones", milestones),
            ("cookie-banner", cookie_banner),
            ("trackers-settings", trackers_settings),
        ):
            with self.subTest(row=name):
                self.assertTrue(matches(radius, row))
                self.assertTrue(matches(hover, {**row, "hover": True}))
                self.assertFalse(matches(hover, row))

        disabled = {
            **category, "attrs": {"disabled": ""}, "hover": True,
        }
        self.assertFalse(matches(hover, disabled))

        under_stack_hover = {
            **show_report,
            "parent": {**show_report_stack, "hover": True},
        }
        self.assertTrue(matches(stack_hover, under_stack_hover))
        self.assertFalse(matches(stack_hover, show_report))
        self.assertFalse(matches(hover, under_stack_hover))

        for name, unthemed in (
            ("header_back", header_button),
            ("info_button", info_button),
            ("tracking_switch", switch),
            ("list_item", list_item),
            ("blocked_counter", blocked_counter),
            ("nav_bar", nav_bar_button),
        ):
            with self.subTest(unthemed=name):
                self.assertFalse(matches(radius, unthemed))
                for selector in (hover, stack_hover):
                    self.assertFalse(
                        matches(selector, {**unthemed, "hover": True})
                    )

    def test_trust_panel_row_paint_is_scoped_to_the_trust_panel(self):
        radius = (
            "#trustpanel-popup .subviewbutton"
            ":not(.panel-header .subviewbutton)"
        )
        hover = radius + ":hover:not([disabled])"
        self.assertEqual(
            {name for name in self.rules if "trustpanel-popup" in name},
            {radius, hover},
        )
        for selector in (radius, hover):
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith("#trustpanel-popup"))
                self.assertIn(":not(.panel-header .subviewbutton)", selector)
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        self.assertEqual(set(self.rules[radius]), {"border-radius"})
        self.assertIn(":hover", hover)
        self.assertIn(":not([disabled])", hover)
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "--panel-menuitem-border-radius" in declarations},
            set(),
        )

        panel = element("panel", "trustpanel-popup")
        multi_view = element(
            "panelmultiview", "trustpanel-popup-multiView", parent=panel
        )
        main_view = element(
            "panelview", "trustpanel-popup-mainView", ("PanelUI-subView",),
            parent=multi_view,
        )
        header = element(
            "box", "trustpanel-popup-mainView-panel-header",
            ("panel-header",), parent=main_view,
        )
        header_button = element(
            "toolbarbutton",
            classes=(
                "subviewbutton", "subviewbutton-iconic",
                "subviewbutton-back",
            ),
            parent=header,
        )
        connection = element(
            "toolbarbutton", "trustpanel-popup-connection",
            ("subviewbutton", "subviewbutton-nav"), parent=main_view,
        )
        clear_cookies = element(
            "toolbarbutton", "trustpanel-clear-cookies-button",
            ("subviewbutton", "subviewbutton-nav"), parent=main_view,
        )
        privacy_link = element(
            "toolbarbutton", "trustpanel-privacy-link",
            ("subviewbutton",), parent=main_view,
        )
        toggle = element(
            "html:moz-toggle", "trustpanel-toggle", parent=main_view
        )
        https_only = element(
            "menulist", "trustpanel-popup-security-httpsonlymode-menulist",
            parent=main_view,
        )
        blocker_see_all = element(
            "html:moz-button", "trustpanel-blocker-see-all", parent=main_view
        )
        blocker_row = element(
            "html:moz-button", classes=("moz-button-subviewbutton-nav",),
            parent=main_view,
        )
        morelink = element(
            "html:a", "trustpanel-siteinformation-morelink",
            ("trustpanel-section", "panel-subview-footer-button"),
            parent=main_view,
        )
        cert_action = element(
            "button", "identity-popup-remove-cert-exception",
            ("panel-button",), parent=main_view,
        )
        graphic = element(
            "vbox", "trustpanel-graphic-section", parent=main_view
        )
        nav_bar_button = element(
            "toolbarbutton", "nav-bar-button", ("subviewbutton",),
            parent=element("toolbar", "nav-bar"),
        )

        for name, row in (
            ("connection", connection),
            ("clear-cookies", clear_cookies),
            ("privacy-link", privacy_link),
        ):
            with self.subTest(row=name):
                self.assertTrue(matches(radius, row))
                self.assertTrue(matches(hover, {**row, "hover": True}))
                self.assertFalse(matches(hover, row))

        disabled = {
            **connection, "attrs": {"disabled": ""}, "hover": True,
        }
        self.assertTrue(matches(radius, disabled))
        self.assertFalse(matches(hover, disabled))

        for name, unthemed in (
            ("header_back", header_button),
            ("toggle", toggle),
            ("https_only", https_only),
            ("blocker_see_all", blocker_see_all),
            ("blocker_row", blocker_row),
            ("morelink", morelink),
            ("cert_action", cert_action),
            ("graphic", graphic),
            ("nav_bar", nav_bar_button),
        ):
            with self.subTest(unthemed=name):
                self.assertFalse(matches(radius, unthemed))
                self.assertFalse(
                    matches(hover, {**unthemed, "hover": True})
                )

    def test_permission_popup_control_paint_is_scoped_to_the_permission_popup(self):
        button = (
            "#permission-popup .permission-popup-permission-remove-button"
        )
        button_hover = button + ":hover:not([disabled])"
        menulist = "#permission-popup-menulist"
        menulist_hover = menulist + ":hover:not([disabled])"
        selectors = (button, button_hover, menulist, menulist_hover)
        self.assertEqual(
            {name for name in self.rules if "permission-popup" in name},
            set(selectors),
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith("#permission-popup"))
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        for normal in (button, menulist):
            self.assertNotIn(":hover", normal)
        for hover in (button_hover, menulist_hover):
            self.assertIn(":hover", hover)
            self.assertIn(":not([disabled])", hover)
        self.assertEqual(
            {name for name in selectors
             if any(token in self.rules[name] for token in (
                 "--button-background-color",
                 "--button-border-color",
                 "--button-border-radius",
             ))},
            set(),
        )

        panel = element("panel", "permission-popup", ("panel-no-padding",))
        multi_view = element(
            "panelmultiview", "permission-popup-multiView", parent=panel
        )
        main_view = element(
            "panelview", "permission-popup-mainView", ("PanelUI-subView",),
            parent=multi_view,
        )
        header = element(
            "box", "permission-popup-mainView-panel-header",
            ("panel-header",), parent=main_view,
        )
        header_span = element(
            "span", classes=("panel-header-label",), parent=header
        )
        separator = element("toolbarseparator", parent=main_view)
        body = element(
            "vbox", "permission-popup-main-body", ("panel-subview-body",),
            parent=main_view,
        )
        permission_list = element(
            "vbox", "permission-popup-permission-list", parent=body
        )
        row = element(
            "hbox", classes=("permission-popup-permission-item",),
            parent=permission_list,
        )
        icon = element(
            "image", classes=("permission-popup-permission-icon",), parent=row
        )
        label = element(
            "label", classes=("permission-popup-permission-label",), parent=row
        )
        state = element(
            "label", classes=("permission-popup-permission-state-label",),
            parent=row,
        )
        remove_button = element(
            "button", classes=("permission-popup-permission-remove-button",),
            parent=row,
        )
        permission_menulist = element(
            "menulist", "permission-popup-menulist", parent=row
        )
        learn_more = element(
            "moz-support-link",
            "permission-popup-storage-access-permission-learn-more",
            parent=permission_list,
        )
        outside_button = element(
            "button", classes=("permission-popup-permission-remove-button",),
            parent=element("panel", "identity-popup"),
        )
        other_menulist = element("menulist", "other-menulist", parent=row)

        for name, control, normal, hover in (
            ("remove_button", remove_button, button, button_hover),
            ("menulist", permission_menulist, menulist, menulist_hover),
        ):
            with self.subTest(control=name):
                self.assertTrue(matches(normal, control))
                self.assertTrue(matches(hover, {**control, "hover": True}))
                self.assertFalse(matches(hover, control))
                disabled = {
                    **control, "attrs": {"disabled": ""}, "hover": True,
                }
                self.assertTrue(matches(normal, disabled))
                self.assertFalse(matches(hover, disabled))

        for name, unthemed in (
            ("row", row),
            ("icon", icon),
            ("label", label),
            ("state_label", state),
            ("header", header),
            ("header_span", header_span),
            ("separator", separator),
            ("learn_more", learn_more),
        ):
            with self.subTest(unthemed=name):
                for selector in (button, menulist):
                    self.assertFalse(matches(selector, unthemed))
                for selector in (button_hover, menulist_hover):
                    self.assertFalse(
                        matches(selector, {**unthemed, "hover": True})
                    )

        for name, control in (
            ("outside_button", outside_button),
            ("other_menulist", other_menulist),
        ):
            with self.subTest(outside=name):
                for selector in selectors:
                    self.assertFalse(matches(selector, control))
                    self.assertFalse(
                        matches(selector, {**control, "hover": True})
                    )

    def test_notification_popup_primary_button_paint_is_scoped_to_the_notification_popup(self):
        primary = "#notification-popup .popup-notification-primary-button"
        self.assertEqual(
            {name for name in self.rules if "notification-popup" in name},
            {primary},
        )
        self.assertEqual(self.rules[primary], REQUIRED_RULES[primary])
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if any(token in declarations for token in (
                 "--button-background-color",
                 "--button-border-color",
             ))},
            set(),
        )
        for token in (
            "--button-border-color-primary-hover",
            "--button-border-color-primary-active",
            "--button-text-color-primary-hover",
            "--button-text-color-primary-active",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.rules[primary])
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "--button-border-radius" in declarations},
            {primary},
        )
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "--border-radius-medium" in declarations},
            set(),
        )

        panel = element(
            "panel", "notification-popup", attrs={"type": "arrow"}
        )
        footer = element(
            "moz-button-group", classes=("panel-footer",), parent=panel
        )
        primary_button = element(
            "moz-button",
            classes=("popup-notification-primary-button",),
            attrs={"type": "primary"},
            parent=footer,
        )
        secondary = element(
            "moz-button",
            classes=("popup-notification-secondary-button",),
            attrs={"type": "split"},
            parent=footer,
        )
        plain_button = element(
            "button",
            classes=("popup-notification-primary-button",),
            parent=element("panel", "identity-popup"),
        )
        other_primary = element(
            "moz-button",
            classes=("popup-notification-primary-button",),
            attrs={"type": "primary"},
            parent=element("panel", "trustpanel-popup"),
        )

        self.assertTrue(matches(primary, primary_button))
        self.assertTrue(matches(primary, {**primary_button, "hover": True}))
        for name, unthemed in (
            ("secondary", secondary),
            ("footer", footer),
            ("plain_button", plain_button),
            ("other_primary", other_primary),
        ):
            with self.subTest(unthemed=name):
                self.assertFalse(matches(primary, unthemed))
                self.assertFalse(
                    matches(primary, {**unthemed, "hover": True})
                )

    def test_notification_popup_provenance(self):
        self.assert_header_names((
            "No reference shows Firefox's notification doorhanger",
            "widgets/button.svg",
            "tests/test_desktoptheme_button.py::TestButton",
            "widgets/viewitem.svg",
            "tests/test_desktoptheme_viewitem.py::TestViewItem",
            "test_selection_background",
            "#notification-popup",
            "popup-notification-primary-button",
            "popup-notification-secondary-button",
            "popupnotification.js",
            "browser.xhtml",
            "browser-shared.css",
            "moz-button.css",
            "tokens-shared.css",
            "--button-border",
            "platform adaptation 2026-10-26",
        ))



if __name__ == "__main__":
    unittest.main()
