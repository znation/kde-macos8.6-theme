"""Validate Firefox tab hover and multiselection declarations."""

from __future__ import annotations

import unittest

from support.firefox_chrome_cases import REQUIRED_RULES, FirefoxChromeTestCase
from support.platinum_palette import TROUGH


class TestFirefoxTabStates(FirefoxChromeTestCase):
    """Tab hover and selected-face declarations."""

    def test_tab_hover_paint_is_scoped_to_unselected_tabs(self):
        hover = (
            ".tabbrowser-tab:hover > .tab-stack > .tab-background"
            ":not([selected]):not([multiselected])"
        )
        selected = ".tabbrowser-tab:is([selected], [multiselected]) .tab-background"
        self.assert_rule_names_scoped_to(
            "tab-background",
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
        self.assert_rule_names_scoped_to("multiselected", {selected, hover})


if __name__ == "__main__":
    unittest.main()
