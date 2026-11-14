"""Validate the GTK 3 Platinum sheet's button arms and button focus outline.

This module owns the button slice split out of ``tests/test_gtk_theme_controls.py``:
the plain colour-class action arms, the flat, selected-row and destructive
arms, the button focus outline, and the disabled and backdrop faces. None of
these tests renders; the sheet rules are read from the stripped CSS through
``GtkSheetRuleCases``.
"""

import unittest
from pathlib import Path

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    BUTTON_BEVEL,
    DISABLED_TEXT,
    INVERTED_BUTTON_BEVEL,
)
from support.platinum_palette import (
    BLACK,
    FACE,
)
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"


class TestGtkThemeButtons(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def assert_plain_action_arms(self, prefix):
        """Assert a plain colour-class action's arms restate the existing face.

        The recipe behind both plain action families: only the opaque
        members of the stock family are restated; no restated selector
        carries `.flat`, so the stock transparent-face colour-class family
        keeps governing whole.
        (The colour-class members are restated by
        test_action_class_flat_arms.) Exactly two call sites: the
        suggested- and destructive-action plain families.
        """
        face = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        sunken = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        disabled = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        self.assert_rule(prefix, face)
        self.assert_rule(f"{prefix}:hover", face)
        self.assert_rule(f"{prefix}:active", sunken)
        self.assert_rule(f"{prefix}:checked", sunken)
        self.assert_rule(f"{prefix}:backdrop", face)
        self.assert_rule(f"{prefix}:backdrop:active", sunken)
        self.assert_rule(f"{prefix}:backdrop:checked", sunken)
        for selector in (
            f"{prefix}:backdrop:disabled",
            f"{prefix}:backdrop:disabled:active",
            f"{prefix}:backdrop:disabled:checked",
            f"{prefix}:disabled",
            f"{prefix}:disabled:active",
            f"{prefix}:disabled:checked",
        ):
            self.assert_rule(selector, disabled)
        expected = {
            prefix,
            f"{prefix}:hover",
            f"{prefix}:active",
            f"{prefix}:checked",
            f"{prefix}:backdrop",
            f"{prefix}:backdrop:active",
            f"{prefix}:backdrop:checked",
            f"{prefix}:backdrop:disabled",
            f"{prefix}:backdrop:disabled:active",
            f"{prefix}:backdrop:disabled:checked",
            f"{prefix}:disabled",
            f"{prefix}:disabled:active",
            f"{prefix}:disabled:checked",
        }
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith(prefix)
                # The colour-class members are restated
                # by test_action_class_flat_arms; the plain opaque keys
                # carry no flat token, so this filter stays inside this
                # family.
                and ".flat" not in selector
            },
            expected,
        )

    def test_suggested_action_plain_arms(self):
        """The plain `suggested-action` arms restate the existing face."""
        self.assert_plain_action_arms("button.suggested-action")

    def test_flat_button_plain_arms(self):
        """The plain `button.flat` arms restate the existing face.

        A GTK 3 push button carrying the `flat` class outside the existing
        overlays draws the existing push-button face in every armed state:
        every restated dictionary extends the existing plain recipe with the
        `background-color` claim the stock transparent faces force, and
        the base, hover and backdrop arms clear the stock motion claims
        with `transition: none`.
        """
        face = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
            "transition": "none",
        }
        sunken = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        disabled = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        self.assert_rule("button.flat", face)
        self.assert_rule("button.flat:hover", face)
        self.assert_rule("button.flat:backdrop", face)
        self.assert_rule("button.flat:hover:active", {"transition": "none"})
        for selector in (
            "button.flat:active",
            "button.flat:checked",
            "button.flat:backdrop:active",
            "button.flat:backdrop:checked",
        ):
            self.assert_rule(selector, sunken)
        for selector in (
            "button.flat:disabled",
            "button.flat:disabled:active",
            "button.flat:disabled:checked",
            "button.flat:backdrop:disabled",
            "button.flat:backdrop:disabled:active",
            "button.flat:backdrop:disabled:checked",
        ):
            self.assert_rule(selector, disabled)
        expected = {
            "button.flat",
            "button.flat:hover",
            "button.flat:hover:active",
            "button.flat:active",
            "button.flat:checked",
            "button.flat:backdrop",
            "button.flat:backdrop:active",
            "button.flat:backdrop:checked",
            "button.flat:backdrop:disabled",
            "button.flat:backdrop:disabled:active",
            "button.flat:backdrop:disabled:checked",
            "button.flat:disabled",
            "button.flat:disabled:active",
            "button.flat:disabled:checked",
        }
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith("button.flat")
            },
            expected,
        )

    def test_selected_row_button_arms(self):
        """The selected-row button arms restate the existing black."""
        self.assert_selected_row_button_arms("button.flat:backdrop")

    def test_destructive_action_plain_arms(self):
        """The plain `destructive-action` arms restate the existing face.

        The red mirror of `test_suggested_action_plain_arms`.
        """
        self.assert_plain_action_arms("button.destructive-action")

    def test_action_class_flat_arms(self):
        """The plain colour-class `.flat` arms restate the existing face.

        A GTK 3 push button carrying the `flat` class beside
        `suggested-action` or `destructive-action` outside an overlay
        draws the existing push-button face in every armed state, erasing
        the stock transparent face with its blue or red label: the
        twenty selectors extend the existing plain push-button recipes the
        same way `test_flat_button_plain_arms` extends the plain ones —
        every restated dictionary carries the `background-color` claim
        the stock transparent faces force, and the disabled arms
        re-declare the face colour beside the existing disabled dictionary
        and claim no `outline-color`. No `transition` is restated: the
        plain flat family's `transition: none` claims already hold at
        equal-or-higher class counts (probed from gtk-contained.css in
        libgtk-3 3.24.49 with gresource).
        """
        face = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        sunken = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        disabled = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        for action_class in ("suggested-action", "destructive-action"):
            with self.subTest(action_class=action_class):
                prefix = f"button.{action_class}.flat"
                self.assertEqual(self.rules[prefix], face)
                for state in (":active", ":checked"):
                    self.assertEqual(self.rules[f"{prefix}{state}"], sunken)
                self.assertEqual(self.rules[f"{prefix}:backdrop"], face)
                for state in (":backdrop:active", ":backdrop:checked"):
                    self.assertEqual(self.rules[f"{prefix}{state}"], sunken)
                for state in (
                    ":disabled",
                    ":backdrop:disabled",
                    ":backdrop:disabled:active",
                    ":backdrop:disabled:checked",
                ):
                    self.assertEqual(self.rules[f"{prefix}{state}"], disabled)
                expected = {
                    prefix,
                    f"{prefix}:active",
                    f"{prefix}:checked",
                    f"{prefix}:backdrop",
                    f"{prefix}:backdrop:active",
                    f"{prefix}:backdrop:checked",
                    f"{prefix}:disabled",
                    f"{prefix}:backdrop:disabled",
                    f"{prefix}:backdrop:disabled:active",
                    f"{prefix}:backdrop:disabled:checked",
                }
                self.assertEqual(
                    {
                        selector
                        for selector in self.rules
                        if selector.startswith(prefix)
                    },
                    expected,
                )

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

    def test_button_disabled_and_backdrop(self):
        self.assert_button_disabled_and_backdrop()


if __name__ == "__main__":
    unittest.main()
