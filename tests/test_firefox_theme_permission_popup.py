"""Validate permission-control paints in Firefox's Platinum chrome sheet."""

from __future__ import annotations

import unittest

from support.firefox_chrome_cases import REQUIRED_RULES, FirefoxChromeTestCase
from support.selector_matching import element, matches


class TestFirefoxPermissionPopup(FirefoxChromeTestCase):
    """Permission popup control declarations and selector scope."""

    def test_permission_popup_control_paint_is_scoped_to_the_permission_popup(self):
        button = (
            "#permission-popup .permission-popup-permission-remove-button"
        )
        button_hover = button + ":hover:not([disabled])"
        menulist = "#permission-popup-menulist"
        menulist_hover = menulist + ":hover:not([disabled])"
        selectors = (button, button_hover, menulist, menulist_hover)
        self.assert_rule_names_scoped_to("permission-popup", set(selectors))
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


if __name__ == "__main__":
    unittest.main()
