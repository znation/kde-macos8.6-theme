"""Validate the GTK 3 Platinum sheet's views and dialogs.

This module owns the views-and-dialogs slice of
``tests/test_gtk_theme.py``'s split: selected views.
Stack-switcher tab declarations are in ``tests/test_gtk_theme_notebook.py``.
The spin-button field declaration is in ``tests/test_gtk_theme_spinbutton.py``.
Title-button declarations are in
``tests/test_gtk_theme_title_band.py``. Rubberband declarations are in
``tests/test_gtk_theme_rubberband.py``. Header drag-and-drop declarations are in
``tests/test_gtk_theme_drag_drop.py``. Accelerator-editor declarations are in
``tests/test_gtk_theme_accelerator_editor.py``.
List, tree, icon and flow-box focus outlines are in
``tests/test_gtk_theme_view_focus.py``. Places-view server-button motion declarations are in
``tests/test_gtk_theme_server_button.py``. List-row pressed and popup-holding
face declarations are in ``tests/test_gtk_theme_row_interactions.py``.
Vertical-stepper and content-view check corner declarations are in
``tests/test_gtk_theme_stepper_check_corners.py``.
Selected icon-view fill and selected treeview check and radio faces are in
``tests/test_gtk_theme_selected_views.py``.
Path-bar declarations are in ``tests/test_gtk_theme_path_bar.py``.
Needs-attention declarations are in ``tests/test_gtk_theme_attention.py``.
Message-dialog declarations are in ``tests/test_gtk_theme_message_dialog.py``.
Paned declarations
are in ``tests/test_gtk_theme_paned.py``. Menu declarations
are in ``tests/test_gtk_theme_menu.py``; inline-toolbar, keycap, fine-tune and
emoji-picker corners are in ``tests/test_gtk_theme_corners.py``; CSD container corners are in
``tests/test_gtk_theme_csd_containers.py``; shipped icon-source checks stay here. The
sheet's comment blocks carry each value's provenance.
"""

import unittest
from support.gtk_rule_cases import GtkSheetRuleCases
from support.platinum_palette import (
    BLACK,
    SELECTION,
)
from support.repo_root import ROOT

CSS = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

class TestGtkThemeViews(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_row_selection_backdrop(self):
        self.assert_row_selection_backdrop((
            "treeview.view:selected:backdrop",
            "list row.activatable:selected:backdrop",
        ))
        self.assert_rule_after(
            "list row.activatable:selected:backdrop",
            "list row.activatable:selected:",
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

    def test_disabled_selected_row_and_child_arms(self):
        """Pin the disabled selected rows and children restated stock-twin."""
        self.assert_disabled_text((
            "row:disabled:selected",
            "list row.activatable:disabled:selected",
            "list row.activatable:disabled:selected:backdrop",
            "flowbox flowboxchild:disabled:selected",
            "treeview.view:disabled:selected",
            "row:backdrop:disabled:selected",
            "flowbox flowboxchild:backdrop:disabled:selected",
            "treeview.view:disabled:selected:backdrop",
        ))
        # The family keeps stock's member set: nothing else in the sheet
        # names the state pair. Selected-text restatements add
        # their seven stock twins to this sweep.
        # More-specific disabled activatable-row overrides also belong
        # to this inventory and preserve grey against enabled row rules.
        self.assertEqual(
            {s for s in self.rules if ":disabled:selected" in s},
            {
                "row:disabled:selected",
                "list row.activatable:disabled:selected",
                "list row.activatable:disabled:selected:backdrop",
                "flowbox flowboxchild:disabled:selected",
                "treeview.view:disabled:selected",
                "row:backdrop:disabled:selected",
                "flowbox flowboxchild:backdrop:disabled:selected",
                "treeview.view:disabled:selected:backdrop",
                "label:disabled:selected",
                "label:backdrop:disabled:selected",
                "textview text:disabled:selected",
                "textview text:disabled:selected:focus",
                ".view text:disabled:selected",
                "textview text:backdrop:disabled:selected",
                ".view text:backdrop:disabled:selected",
            },
        )

    def test_icon_sources_resolve_to_shipped_files(self):
        self.assert_icon_sources_resolve()

    def test_icon_sources_point_at_shipped_assets(self):
        self.assert_shipped_asset_urls()

    def test_separator(self):
        self.assert_separators()

    def test_frame(self):
        self.assert_frame(("frame > border", ".frame"))


if __name__ == "__main__":
    unittest.main()
