"""Validate GTK 3 Platinum drag-and-drop declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.platinum_palette import BLACK, SELECTION
from support.repo_root import ROOT


class TestGtkThemeDragDrop(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_header_drop_indicator(self):
        targets = ("", "header.", "header ")
        states = (
            "button.dnd",
            "button.dnd:hover",
            "button.dnd:active",
            "button.dnd:selected",
        )
        selectors = [
            f"treeview.view {target}{state}"
            for target in targets
            for state in states
        ]
        self.assertEqual(len(selectors), 12, selectors)
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {
                        "background-color": SELECTION,
                        "background-image": "none",
                        "color": BLACK,
                        "text-shadow": "none",
                        "box-shadow": "none",
                        "border-style": "none",
                        "border-radius": "0",
                    },
                )

    def test_header_drop_arm_carries_no_padding(self):
        self.assertNotIn("padding", self.rules["treeview.view button.dnd"])

    def test_no_dndtarget_node_declared(self):
        self.assertNotIn("dndtarget", self.css)


if __name__ == "__main__":
    unittest.main()
