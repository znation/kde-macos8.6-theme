"""Validate GTK 3 assistant sidebar declarations."""

from __future__ import annotations

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import ETCH_DARK
from support.platinum_palette import FACE, WHITE
from support.repo_root import ROOT


class TestGtkThemeAssistant(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_assistant_sidebar_arms(self):
        # No reference screenshot shows a GTK assistant sidebar, so the
        # five stock sidebar arms rest on existing faces: WHITE for the
        # sidebar field, ETCH_DARK for the top edge (the existing etched
        # band edge the infobar reuses) and FACE for the active-step
        # label — a wizard's current page is not a selected row, so no
        # selection blue applies. Stock's own padding and csd shape stay
        # byte-equal, and the backdrop window keeps the existing face per
        # the existing button:backdrop keep-the-existing-face policy.
        expected = {
            "assistant .sidebar": {
                "background-color": WHITE,
                "border-top": "1px solid " + ETCH_DARK,
            },
            "assistant.csd .sidebar": {"border-top-style": "none"},
            "assistant .sidebar label": {"padding": "6px 12px"},
            "assistant .sidebar label.highlight": {"background-color": FACE},
        }
        for selector, rule in expected.items():
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], rule, selector)
        self.assertEqual(
            {s for s in self.rules if "assistant" in s}, set(expected)
        )
        self.assertNotIn("assistant .sidebar:backdrop", self.rules)
        self.assert_rule_after(
            "assistant .sidebar {",
            "infobar > revealer > box {",
        )


if __name__ == "__main__":
    unittest.main()
