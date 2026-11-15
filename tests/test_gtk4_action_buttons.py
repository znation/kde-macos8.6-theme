"""GTK 4 action and flat button checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import BUTTON_BEVEL, DISABLED_TEXT, INVERTED_BUTTON_BEVEL
from support.platinum_palette import BLACK, FACE


class TestGtk4ActionButtons(Gtk4SheetRuleCases, unittest.TestCase):
    def test_suggested_action_plain_arms(self):
        self.assert_plain_action_arms("button.suggested-action")

    def test_destructive_action_plain_arms(self):
        self.assert_plain_action_arms("button.destructive-action")

    def test_action_class_flat_arms(self):
        # No reference screenshot shows a GTK flat action button; the tail
        # arms restate the existing push-button recipe over the stock
        # transparent colour-class flat family, so every checked
        # relationship below anchors the existing face constants and the two
        # family inventories keep the arms to stock's own spellings.
        face = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
        }
        sunken = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
        }
        insensitive = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        for prefix in ("button.suggested-action", "button.destructive-action"):
            with self.subTest(action_class=prefix):
                self.assert_rule(f"{prefix}.flat", face)
                for state in (":active", ":checked", ".keyboard-activating"):
                    self.assert_rule(f"{prefix}.flat{state}", sunken)
                self.assert_rule(f"{prefix}.flat:disabled", insensitive)
                self.assertEqual(
                    {s for s in self.rules if s.startswith(f"{prefix}.flat")},
                    {
                        f"{prefix}.flat",
                        f"{prefix}.flat:active",
                        f"{prefix}.flat:checked",
                        f"{prefix}.flat.keyboard-activating",
                        f"{prefix}.flat:disabled",
                    },
                )

    def test_flat_button_arms(self):
        # No reference screenshot shows a GTK flat button; the tail arms
        # restate the existing plain push-button recipe over the stock
        # transparent flat family, so every checked relationship below
        # anchors the existing face constants and the family inventory keeps
        # the arms to stock's own spellings.
        raised = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "transition": "none",
        }
        for selector in ("button.flat", "button.flat:hover"):
            self.assertEqual(self.rules[selector], raised)
        sunken = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "transition": "none",
        }
        for selector in ("button.flat:active", "button.flat:checked", "button.flat.keyboard-activating"):
            self.assertEqual(self.rules[selector], sunken)
        insensitive = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        backdrop = {**raised, "color": BLACK}
        backdrop_sunken = {
            **sunken,
            "color": BLACK,
        }
        for selector in (
            "button.flat:backdrop",
            "button.flat:disabled",
            "button.flat:backdrop:disabled",
            "button:backdrop.flat:disabled",
            "button:backdrop.flat:disabled:active",
            "button:backdrop.flat:disabled:checked",
        ):
            self.assertEqual(self.rules[selector], insensitive)
        self.assertEqual(self.rules["button:backdrop.flat"], backdrop)
        for selector in ("button:backdrop.flat:active", "button:backdrop.flat:checked"):
            self.assertEqual(self.rules[selector], backdrop_sunken)
        expected_selectors = {
            "button.flat",
            "button.flat:hover",
            "button.flat:active",
            "button.flat:checked",
            "button.flat.keyboard-activating",
            "button.flat:backdrop",
            "button.flat:disabled",
            "button.flat:backdrop:disabled",
            "button:backdrop.flat",
            "button:backdrop.flat:active",
            "button:backdrop.flat:checked",
            "button:backdrop.flat:disabled",
            "button:backdrop.flat:disabled:active",
            "button:backdrop.flat:disabled:checked",
        }
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith("button.flat") or selector.startswith("button:backdrop.flat")
            },
            expected_selectors,
        )


if __name__ == "__main__":
    unittest.main()
