"""Validate GTK 3 disabled-view declarations."""

from __future__ import annotations

import unittest

from support import gtk_css
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import DISABLED_TEXT
from support.platinum_palette import WHITE
from support.repo_root import ROOT


class TestGtkThemeDisabledViews(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_disabled_view_face_and_ink(self):
        """Pin the restated disabled view field and ink stock-twins."""
        # 2026-11-11: an insensitive view's stock arms out-specify the existing
        # `.view, textview text, list` view-field group, so stock would wash
        # each member with the toolkit's warm near-white field and grey ink
        # without the restatements; see the dated block beside the rules.
        group_members = (
            ".view:disabled",
            "iconview:disabled",
            ".view text:disabled",
            "iconview text:disabled",
            "textview text:disabled",
        )
        expected = {**DISABLED_TEXT, "background-color": WHITE}
        for selector in group_members:
            with self.subTest(selector=selector):
                self.assert_rule(selector, expected)
                self.assertEqual(self.rules[selector], expected, selector)
                self.assertEqual(self.selectors.count(selector), 1, selector)
        for selector in ("treeview.view:disabled", "treeview.view:disabled:backdrop"):
            with self.subTest(selector=selector):
                self.assert_rule(selector, DISABLED_TEXT)
                self.assertEqual(self.rules[selector], {**DISABLED_TEXT}, selector)
                self.assertEqual(self.selectors.count(selector), 1, selector)
        # Token sweeps keyed on substrings no other existing selector carries,
        # so a stray state twin, a renamed spelling or a dropped member
        # fails; the treeview family sweep pins the existing disabled-selected
        # pair as the only other treeview disabled spellings.
        self.assertEqual(
            {s for s in self.rules if "iconview:disabled" in s},
            {"iconview:disabled"},
        )
        self.assertEqual(
            {s for s in self.rules if "iconview text:disabled" in s},
            {"iconview text:disabled"},
        )
        # The ".view:disabled" substring is also inside the four treeview
        # disabled spellings, so the sweep names the whole five-key family.
        self.assertEqual(
            {s for s in self.rules if ".view:disabled" in s},
            {
                ".view:disabled",
                "treeview.view:disabled",
                "treeview.view:disabled:backdrop",
                "treeview.view:disabled:selected",
                "treeview.view:disabled:selected:backdrop",
            },
        )
        self.assertEqual(
            {s for s in self.rules if ".view text:disabled" in s},
            {".view text:disabled", ".view text:disabled:selected"},
        )
        self.assertEqual(
            {s for s in self.rules if "textview text:disabled" in s},
            {
                "textview text:disabled",
                "textview text:disabled:selected",
                "textview text:disabled:selected:focus",
            },
        )
        self.assertEqual(
            {s for s in self.rules if "treeview.view:disabled" in s},
            {
                "treeview.view:disabled",
                "treeview.view:disabled:backdrop",
                "treeview.view:disabled:selected",
                "treeview.view:disabled:selected:backdrop",
            },
        )
        # The restatements sit after the existing disabled-selected groups in
        # the sheet, the source-order position the cascade tie needs. The
        # order pin runs on the comment-stripped sheet because the dated
        # comment quotes the comma group's own spelling.
        stripped = gtk_css.strip_comments(self.css)
        self.assertGreater(
            stripped.index(".view:disabled,"),
            stripped.index("label:backdrop selection:disabled,"),
            "the disabled view restatements do not follow the disabled-selected groups",
        )


if __name__ == "__main__":
    unittest.main()
