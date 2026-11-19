"""Validate GTK 3 application notification declarations."""

from __future__ import annotations

import re
import unittest

from support import gtk_css
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import ETCH_DARK
from support.platinum_palette import BLACK, FACE, WHITE
from support.repo_root import ROOT


class TestGtkThemeNotification(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_app_notification_band(self):
        roots = (
            ".app-notification", ".app-notification.frame",
            ".app-notification:backdrop", ".app-notification.frame:backdrop",
        )
        self.assert_infobar(roots)
        expected = {
            "background-color": FACE, "background-image": "none", "color": BLACK,
            "border": "0", "border-bottom": f"1px solid {ETCH_DARK}",
            "border-radius": "0", "box-shadow": f"inset 0 -1px {WHITE}",
            "text-shadow": "none", "-gtk-icon-shadow": "none",
        }
        for selector in roots:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)
                sheet = gtk_css.strip_comments(self.css)
                block = next(
                    body for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", sheet)
                    if selector in {arm.strip() for arm in selectors.split(",")}
                )
                self.assertLess(block.index("border: 0;"), block.index("border-bottom:"))
        self.assertEqual(
            {selector for selector in self.rules if ".app-notification" in selector},
            set(roots) | {
                ".app-notification > border", ".app-notification.frame > border",
                ".app-notification button", ".app-notification.frame button",
                ".app-notification button:hover", ".app-notification button:active",
                ".app-notification button:checked", ".app-notification button:disabled",
                ".app-notification button:backdrop", ".app-notification button.flat",
                ".app-notification button.flat:hover", ".app-notification button.flat:active",
                ".app-notification button.flat:checked", ".app-notification button.flat:disabled",
                ".app-notification button.flat:backdrop",
            },
        )

    def test_app_notification_frame_border(self):
        for selector in (".app-notification > border", ".app-notification.frame > border"):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-style": "none", "box-shadow": "none"})


if __name__ == "__main__":
    unittest.main()
