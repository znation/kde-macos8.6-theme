"""Validate the GTK 3 Platinum sheet's selected icon-view and treeview faces.

This module owns the selected icon-view fill and the selected treeview-row
check and radio faces, split out of ``tests/test_gtk_theme_views.py``.
"""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    MIXED_GLYPH,
    RADIO_GLYPH,
    SELECTION_CHECK_STATES,
)
from support.platinum_palette import (
    BLACK,
    SELECTION,
)
from support.repo_root import ROOT

CSS = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"


class TestGtkThemeSelectedViews(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_iconview_selected_arms(self):
        """Pin the selected icon view restated off the existing row selection."""
        for selector in (
            "iconview.view:not(:disabled):selected",
            "iconview.view:not(:disabled):selected:focus",
            "iconview.view:not(:disabled):backdrop:selected",
            "iconview.view:not(:disabled):backdrop:selected:focus",
        ):
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {
                        "background-color": SELECTION,
                        "color": BLACK,
                        "border-radius": "0",
                    },
                )
        # Exact guarded spellings also prevent overriding disabled selections.
        # The family keeps the existing dotted focus outline and the
        # disabled-view restatement's two arms as its only other icon-view
        # rules: a renamed restated arm leaves exactly its successor.
        # The vertical-stepper and content-view check corner
        # record restates eight more iconview arms — the selection-check
        # state faces `iconview.content-view.check…:not(list)` — all pinned
        # with the other content-view check spellings by
        # test_vertical_stepper_and_content_view_check_corners in
        # tests/test_gtk_theme_stepper_check_corners.py.
        check_states = SELECTION_CHECK_STATES
        self.assertEqual(
            {selector for selector in self.rules if "iconview" in selector},
            {
                "iconview:focus",
                "iconview:disabled",
                "iconview text:disabled",
                "iconview.view:not(:disabled):selected",
                "iconview.view:not(:disabled):selected:focus",
                "iconview.view:not(:disabled):backdrop:selected",
                "iconview.view:not(:disabled):backdrop:selected:focus",
                *(
                    f"iconview.content-view.check{state}:not(list)"
                    for state in check_states
                ),
            },
        )

    def test_treeview_selected_check_radio_faces(self):
        """Pin the selected-row check and radio restated off the existing faces."""
        # The sheet-tail record answers the toolkit resource's
        # four treeview-class-armed selected-row arms (probed verbatim in
        # the sheet comment and docs/invariants.md) per-property: the
        # colour arm's ink and border return to the existing check recipe's
        # hard black, the checked and indeterminate glyph arms swap the
        # toolkit's recoloured symbolic dot and dash for the existing
        # black-ink shipped assets, and stock's radius and 14px-size arm
        # restates nothing. No change here adds a face declaration beyond
        # the two answers per member spelling.
        seal = {"color": BLACK, "border-color": BLACK}
        expected = {
            "treeview.view check:selected:focus": dict(seal),
            "treeview.view check:selected": dict(seal),
            "treeview.view radio:selected:focus": dict(seal),
            "treeview.view radio:selected": dict(seal),
            "treeview.view radio:checked:selected": dict(RADIO_GLYPH),
            "treeview.view radio:indeterminate:selected": dict(MIXED_GLYPH),
        }
        self.assert_rule_group(expected)
        # The family sweep: every rule carrying one of the two
        # treeview-class-armed control tokens is one of the six spellings
        # above, so no stock arm of either group survives unrepresented.
        self.assertEqual(
            {
                s
                for s in self.rules
                if "treeview.view check" in s or "treeview.view radio" in s
            },
            set(expected),
        )
        # Source order: each restated spelling lands after the existing
        # plain-state `radio:checked` glyph rule's parsed position.
        for selector in expected:
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("radio:checked"),
                selector,
            )


if __name__ == "__main__":
    unittest.main()
