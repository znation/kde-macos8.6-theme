"""Validate GTK 3 button keyboard-focus declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.platinum_palette import BLACK
from support.repo_root import ROOT


class TestGtkThemeButtonFocus(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_button_focus_outline(self):
        self.assert_rule(
            "button:focus",
            {
                "outline": f"1px dotted {BLACK}",
                "outline-offset": "0",
                "-gtk-outline-radius": "0",
            },
        )
        self.assertEqual(
            self.rules["button:focus"]["outline"], self.rules["scale:focus"]["outline"]
        )
        self.assertEqual(
            self.rules["button:focus"]["outline-offset"],
            self.rules["scale:focus"]["outline-offset"],
        )
        self.assertEqual(
            self.rules["button:focus"]["-gtk-outline-radius"],
            self.rules["button"]["border-radius"],
        )


if __name__ == "__main__":
    unittest.main()
