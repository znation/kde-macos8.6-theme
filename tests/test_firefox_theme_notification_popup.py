"""Validate Firefox notification doorhanger button paint and provenance."""

from __future__ import annotations

import unittest

from support.firefox_chrome_cases import (
    REQUIRED_RULES,
    VIEWITEM_REFERENCES,
    FirefoxChromeTestCase,
)
from support.selector_matching import element, matches


class TestFirefoxNotificationPopup(FirefoxChromeTestCase):
    """Notification doorhanger primary button paint and provenance."""

    def test_notification_popup_primary_button_paint_is_scoped_to_the_notification_popup(self):
        primary = "#notification-popup .popup-notification-primary-button"
        self.assert_rule_names_scoped_to("notification-popup", {primary})
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
        self.assert_token_scoped_to("--button-border-radius", {primary})
        self.assert_token_scoped_to("--border-radius-medium")

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
            *VIEWITEM_REFERENCES,
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
