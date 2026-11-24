"""Validate the GTK 3 Platinum sheet's views and dialogs.

This module owns the views-and-dialogs slice of ``tests/test_gtk_theme.py``'s
split: selected views. Stack-switcher tab declarations are in
``tests/test_gtk_theme_notebook.py``. The spin-button field declaration is in
``tests/test_gtk_theme_spinbutton.py``. Title-button declarations are in
``tests/test_gtk_theme_title_band.py``. Rubberband declarations are in
``tests/test_gtk_theme_rubberband.py``. Header drag-and-drop declarations are
in ``tests/test_gtk_theme_drag_drop.py``. Accelerator-editor declarations are
in ``tests/test_gtk_theme_accelerator_editor.py``. List, tree, icon and
flow-box focus outlines are in ``tests/test_gtk_theme_view_focus.py``.
Places-view server-button motion declarations are in
``tests/test_gtk_theme_server_button.py``. List-row pressed and popup-holding
face declarations are in ``tests/test_gtk_theme_row_interactions.py``.
Vertical-stepper and content-view check corner declarations are in
``tests/test_gtk_theme_stepper_check_corners.py``. Separator and frame
declarations are in ``tests/test_gtk_theme_frames.py``. Selected icon-view
fill, selected flow-box children, and selected treeview check and radio faces
are in ``tests/test_gtk_theme_selected_views.py``. Path-bar declarations are in
``tests/test_gtk_theme_path_bar.py``. Needs-attention declarations are in
``tests/test_gtk_theme_attention.py``. Message-dialog declarations are in
``tests/test_gtk_theme_message_dialog.py``. Paned declarations are in
``tests/test_gtk_theme_paned.py``. Menu declarations are in
``tests/test_gtk_theme_menu.py``; inline-toolbar, keycap, fine-tune and
emoji-picker corners are in ``tests/test_gtk_theme_corners.py``; CSD container
corners are in ``tests/test_gtk_theme_csd_containers.py``; shipped icon-source
checks stay here. Disabled-selected row, child and tree-view declarations are
in ``tests/test_gtk_theme_disabled_views.py``. The sheet's comment blocks carry
each value's provenance.
"""

import unittest
from support.gtk_rule_cases import GtkSheetRuleCases
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

    def test_icon_sources_resolve_to_shipped_files(self):
        self.assert_icon_sources_resolve()

    def test_icon_sources_point_at_shipped_assets(self):
        self.assert_shipped_asset_urls()


if __name__ == "__main__":
    unittest.main()
