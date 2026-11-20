"""Validate the GTK 3 Platinum sheet's views and dialogs.

This module owns the views-and-dialogs slice of
``tests/test_gtk_theme.py``'s split: the stack switcher, selected views,
the spin-button field. Title-button declarations are in
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
        # The vertical-stepper and content-view-check corner
        # record restates eight more iconview arms — the selection-check
        # state faces `iconview.content-view.check…:not(list)` — all pinned
        # with the other content-view check spellings by
        # test_vertical_stepper_and_content_view_check_corners.
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

    def test_stack_switcher_tabs(self):
        forms = {
            "base": ("stackswitcher > button",),
            "hover": ("stackswitcher > button:hover",),
            "checked": ("stackswitcher > button:checked",),
            "checked+hover": ("stackswitcher > button:checked:hover",),
        }
        self.assert_tab_faces(forms)

    def test_spin_button_field(self):
        self.assert_spin_button_field(("spinbutton:not(.vertical)",))
        self.assertNotIn("spinbutton.vertical > text", self.rules)

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
