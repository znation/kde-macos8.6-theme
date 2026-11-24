"""Validate the GTK 3 Platinum sheet's selected icon-view and treeview faces.

This module owns the selected icon-view fill, the selected flow-box child
arms, and the selected treeview-row check and radio faces, split out of
``tests/test_gtk_theme_views.py``.
"""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
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

    def test_flowbox_child_selected_arms(self):
        """Pin the selected children restated off the existing row selection."""
        self.assert_rule(
            "flowbox flowboxchild:selected",
            {
                "background-color": SELECTION,
                "color": BLACK,
                "border-radius": "0",
            },
        )
        self.assert_rule(
            "flowbox flowboxchild:backdrop:selected",
            {
                "background-color": SELECTION,
                "color": BLACK,
                "border-radius": "0",
            },
        )

    def test_treeview_selected_check_radio_faces(self):
        """Pin the selected-row check and radio restated off the existing faces.

        The sheet-tail record answers the toolkit resource's
        four treeview-class-armed selected-row arms (probed verbatim in
        the sheet comment and docs/invariants.md) per-property, exactly as
        the shared assertion pins them for the GTK 4 sheet.
        """
        self.assert_treeview_selected_check_radio_faces()


if __name__ == "__main__":
    unittest.main()
