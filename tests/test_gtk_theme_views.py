"""Validate the GTK 3 Platinum sheet's views and dialogs.

This module owns the views-and-dialogs slice of
``tests/test_gtk_theme.py``'s split: the stack switcher, the list and
icon-view focus outlines, the spin-button
field and title-button boxes. Rubberband declarations are in
``tests/test_gtk_theme_rubberband.py``. Header drag-and-drop declarations are in
``tests/test_gtk_theme_drag_drop.py``. Accelerator-editor declarations are in
``tests/test_gtk_theme_accelerator_editor.py``.
Places-view server-button motion declarations are in
``tests/test_gtk_theme_server_button.py``.
Path-bar declarations are in ``tests/test_gtk_theme_path_bar.py``.
Message-dialog declarations are in ``tests/test_gtk_theme_message_dialog.py``.
Paned declarations
are in ``tests/test_gtk_theme_paned.py``. Menu declarations
are in ``tests/test_gtk_theme_menu.py``; shipped icon-source checks stay here. The
sheet's comment blocks carry each value's provenance.
"""

import unittest
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    CHECK_GLYPH,
    ROW_HOVER,
    MIXED_GLYPH,
    RADIO_GLYPH,
    SELECTION_CHECK_STATES,
    TILE_CHECK_FACE,
    TITLE_BUTTON_ASSETS,
    TITLE_BUTTON_IMAGE,
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

    def test_list_row_press_and_popup_faces(self):
        # The pressed and popup-holding row states restate the existing
        # faces: stock's four element-level row arms would paint a tinted
        # hover-wash, pressed insets and a selection-accent fill on rows
        # the existing records paint transparent or with the flat lavender
        # selection.
        expected = {
            "row.activatable.has-open-popup": dict(ROW_HOVER),
            "row.activatable:hover": dict(ROW_HOVER),
            "row.activatable:active": {"box-shadow": "none"},
            "row.activatable:selected:active": {"box-shadow": "none"},
            "row.activatable:selected.has-open-popup": {"background-color": SELECTION},
            "row.activatable:selected:hover": {"background-color": SELECTION},
        }
        self.assert_rule_group(expected)
        # The existing row spellings are all list-, listview- or
        # treeview-armed, so this element-level family is exactly six.
        self.assertEqual(
            {s for s in self.rules if s.startswith("row.activatable")},
            set(expected),
        )
        self.assertGreater(
            self.selectors.index("row.activatable:active"),
            self.selectors.index("list row.activatable:selected"),
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

    def test_list_row_focus_outline(self):
        self.assert_dotted_focus_outline("list row:focus")

    def test_treeview_focus_outline(self):
        self.assert_dotted_focus_outline("treeview.view:focus")

    def test_iconview_focus_outline(self):
        self.assert_dotted_focus_outline("iconview:focus")

    def test_flowbox_child_focus_outline(self):
        self.assert_dotted_focus_outline("flowbox > flowboxchild:focus")

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

    def test_needs_attention_badges(self):
        """Needs-attention labels and images keep no stock accent pulse."""
        spellings = (
            "stacksidebar row.needs-attention > label",
            ".stack-switcher > button.needs-attention > label",
            ".stack-switcher > button.needs-attention > image",
        )
        self.assert_rule_group(
            {selector: {"animation": "none", "background-image": "none"}
             for selector in spellings}
        )
        # Source order: the restated group sits after the existing
        # stack-switcher checked face group. Stock spells the switcher as
        # the .stack-switcher class, so the restatement must be the same
        # byte-equal spelling to win the cascade.
        self.assertGreater(
            self.selectors.index(".stack-switcher > button.needs-attention"
                                 " > label"),
            self.selectors.index("stackswitcher > button:checked:hover"),
        )
        # The restated spellings are the only needs-attention arms the sheet
        # declares: the scan kills renamed and stray variants.
        self.assertEqual(
            {selector for selector in self.rules
             if "needs-attention" in selector},
            set(spellings),
        )

    def test_spin_button_field(self):
        self.assert_spin_button_field(("spinbutton:not(.vertical)",))
        self.assertNotIn("spinbutton.vertical > text", self.rules)

    def test_title_buttons(self):
        for scope in ("headerbar", ".titlebar"):
            for control, asset in TITLE_BUTTON_ASSETS:
                self.assert_title_button(
                    f"{scope} button.titlebutton.{control}", asset
                )
            self.assert_rule(
                f"{scope} button.titlebutton image", TITLE_BUTTON_IMAGE
            )

    def test_csd_container_corners(self):
        """Pin the CSD container and decoration corner restatements.

        The five appended groups rest stock's class-armed popup-menu,
        generic popover-background and decoration-shell radius arms at
        zero; the existing name-level `menu`, `popover`, `tooltip` and
        messagedialog groups match none of these spellings.
        """
        selectors = (
            ".csd menu",
            ".csd .menu",
            ".csd .context-menu",
            ".csd popover.background",
            "popover.background",
            ".csd.popup decoration",
            "tooltip.csd decoration",
            "messagedialog.csd decoration",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                self.assertEqual(self.selectors.count(selector), 1, selector)
        # The class-armed menu spellings have no existing or future neighbour:
        # the existing scroll-arrow and row spellings carry `context-menu` with
        # a space but never `csd menu`, `csd .menu` or `csd .context-menu`.
        self.assertEqual(
            {s for s in self.rules if "csd menu" in s}, {".csd menu"}
        )
        self.assertEqual(
            {s for s in self.rules if "csd .menu" in s}, {".csd .menu"}
        )
        self.assertEqual(
            {s for s in self.rules if "csd .context-menu" in s},
            {".csd .context-menu"},
        )
        # No existing or unrelated decoration selector exists: the sheet names
        # `text-decoration-line` only as a property, never as a selector.
        self.assertEqual(
            {s for s in self.rules if "decoration" in s},
            {
                ".csd.popup decoration",
                "tooltip.csd decoration",
                "messagedialog.csd decoration",
            },
        )
        # Source order: every appended spelling sits after the existing
        # menu, popover and messagedialog restatements, so the byte-equal
        # stock twins win the equal-specificity ties under the lower-sheet
        # reading of how the toolkit resource competes.
        for selector in selectors:
            for anchor in ("menu", "popover", "messagedialog.csd.background"):
                with self.subTest(selector=selector, after=anchor):
                    self.assertGreater(
                        self.selectors.index(selector),
                        self.selectors.index(anchor),
                    )

    def test_inline_toolbar_keycap_finetune_emoji_corners(self):
        """Pin inline-toolbar, keycap, fine-tune trough and emoji corners.

        The four appended groups rest stock's inline-toolbar container,
        shortcut keycap, fine-tuned scale trough family and emoji-picker
        hover radius arms at zero; the emoji section labels also have explicit
        opacity arms tested with their own declarations.
        """
        selectors = (
            ".inline-toolbar",
            ".keycap",
            "scale.fine-tune fill",
            "scale.fine-tune highlight",
            "scale.fine-tune trough",
            "popover.emoji-picker .emoji :hover",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                self.assertEqual(self.selectors.count(selector), 1, selector)
                self.assert_rule(selector, {"border-radius": "0"})
        # The four tokens have no existing or unrelated neighbours: the existing
        # keycap corner record is the GTK 4 `shortcut > .keycap` spelling,
        # and the emoji-label rules are the only additional emoji selectors.
        # The linked-field end-corner record restates six more
        # linked arm members naming the inline-toolbar token — the three
        # `.inline-toolbar button…` end members and the three
        # `toolbar.inline-toolbar toolbutton…` end members — all pinned
        # with the other linked-field spellings by
        # test_gtk_theme_linked.TestGtkThemeLinked::
        # test_linked_end_field_corners.
        self.assertEqual(
            {s for s in self.rules if "inline-toolbar" in s},
            {".inline-toolbar",
             ".inline-toolbar button:first-child",
             ".inline-toolbar button:last-child",
             ".inline-toolbar button:only-child",
             "toolbar.inline-toolbar toolbutton:first-child > button.flat",
             "toolbar.inline-toolbar toolbutton:last-child > button.flat",
             "toolbar.inline-toolbar toolbutton:only-child > button.flat"},
        )
        self.assertEqual({s for s in self.rules if "keycap" in s}, {".keycap"})
        # The four marked-scale fine-tune thumb arms also name
        # the token and are pinned with the marked-scale thumbs by
        # test_gtk_theme.TestGtkTheme.test_marked_scale_thumb_arms; the
        # fine-tuned container geometry restatement adds the
        # two orientation container spellings, pinned by
        # test_gtk_theme_scale.TestGtkThemeScale::
        # test_scale_fine_tune_container_geometry; and the
        # marked-node geometry restatement adds the six fine-tuned tick
        # margin and minimum spellings, pinned by
        # test_gtk_theme_scale.TestGtkThemeScale::
        # test_scale_marks_indicator_geometry.
        self.assertEqual(
            {s for s in self.rules if "fine-tune" in s},
            {
                "scale.fine-tune fill",
                "scale.fine-tune highlight",
                "scale.fine-tune trough",
                "scale.fine-tune.horizontal",
                "scale.fine-tune.vertical",
                "scale.horizontal.marks-before:not(.marks-after).fine-tune slider",
                "scale.horizontal.marks-after:not(.marks-before).fine-tune slider",
                "scale.vertical.marks-before:not(.marks-after).fine-tune slider",
                "scale.vertical.marks-after:not(.marks-before).fine-tune slider",
                "scale.horizontal.fine-tune marks.top",
                "scale.horizontal.fine-tune marks.bottom",
                "scale.vertical.fine-tune marks.top",
                "scale.vertical.fine-tune marks.bottom",
                "scale.horizontal.fine-tune indicator",
                "scale.vertical.fine-tune indicator",
            },
        )
        self.assertEqual(
            {s for s in self.rules if "emoji" in s},
            {
                "popover.emoji-picker .emoji :hover",
                "button.emoji-section label",
                "button.emoji-section:hover label",
            },
        )
        for selector in (
            "button.emoji-section label",
            "button.emoji-section:hover label",
        ):
            with self.subTest(selector=selector, after="modelbutton.flat"):
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("modelbutton.flat"),
                )
        # Source order: every appended spelling sits after the existing
        # modelbutton restatement near the sheet tail, so the byte-equal
        # stock twins win the equal-specificity ties under the lower-sheet
        # reading of how the toolkit resource competes.
        for selector in selectors:
            with self.subTest(selector=selector, after="modelbutton.flat"):
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("modelbutton.flat"),
                )

    def test_vertical_stepper_and_content_view_check_corners(self):
        """Pin the vertical steppers and content-view check faces square.

        The two appended stepper groups rest stock's vertical stepper
        end halves at zero and restate stock's per-stepper border-style
        halves so each field/stepper join draws one 1px line, and the
        eight content-view check state groups rest the eight
        selection-check state faces at zero and
        take the existing check face under every state: the
        tile-check face record extends the existing radius-only groups
        in place, so the scanned parser reads the merged dictionaries
        in this suite, and the suite's parser leaves each spelling
        once in the selector list -- repeating the spellings in new
        blocks would break the once-per-selector pin. Nothing else in
        the sheet names any of the three tokens.
        """
        stepper_up = "spinbutton.vertical button.up"
        stepper_down = "spinbutton.vertical button.down"
        states = SELECTION_CHECK_STATES
        check_spellings = (
            *[f".view.content-view.check{state}:not(list)" for state in states],
            *[f"iconview.content-view.check{state}:not(list)" for state in states],
            *[f".content-view:not(list) check{state}" for state in states],
        )
        spellings = (stepper_up, stepper_down) + check_spellings
        # The docstring comment above the groups names both probes and
        # the face source, and the realized dictionaries merge this
        # record's zero radius with the face record's existing
        # check face under every state: the four unchecked spellings
        # carry the raised etched face, the four checked ones the same
        # five declarations under the shipped checkmark glyph.
        tile_face = dict(TILE_CHECK_FACE)
        tile_rules = {}
        for state_index in range(len(states)):
            declarations = (
                tile_face
                if state_index < 4
                else {**tile_face, **CHECK_GLYPH}
            )
            for member_index in range(3):
                tile_rules[
                    check_spellings[member_index * len(states) + state_index]
                ] = dict(declarations)
        self.assert_rule_group(
            {
                stepper_up: {
                    "border-radius": "0",
                    "border-style": "solid solid none solid",
                },
                stepper_down: {
                    "border-radius": "0",
                    "border-style": "none solid solid solid",
                },
                **tile_rules,
            }
        )
        # The three tokens have no existing or unrelated neighbours: the
        # existing `.content-view` rules name no check node or `:not(list)`
        # guard and the existing `.osd spinbutton.vertical button:first-child`
        # groups name the stacked OSD twins only, so the scan kills renamed
        # variants, a folded or dropped `:not(list)` guard and stray
        # neighbours. The class-armed members take the `content-view.check`
        # token; the bare compound takes the `.content-view:not(list)`
        # token, which no other rule carries.
        view_and_iconview = {
            s
            for s in self.rules
            if "content-view.check" in s
        }
        self.assertEqual(
            view_and_iconview,
            set(check_spellings[:16]),
        )
        bare_compound = {
            s for s in self.rules if ".content-view:not(list)" in s
        }
        self.assertEqual(bare_compound, set(check_spellings[16:]))
        self.assertEqual(view_and_iconview | bare_compound, set(check_spellings))
        # One sweep further: every rule naming both tokens is one of the
        # twenty-four tile spellings, so the face record leaves no stray
        # check-and-content-view neighbour and the existing `.content-view`
        # field, hover and rubberband arms (which name no check node)
        # stay outside the family.
        self.assertEqual(
            {s for s in self.rules if "check" in s and "content-view" in s},
            set(check_spellings),
        )
        self.assertEqual(
            {s for s in self.rules if "spinbutton.vertical button.up" in s},
            {stepper_up},
        )
        self.assertEqual(
            {s for s in self.rules if "spinbutton.vertical button.down" in s},
            {stepper_down},
        )
        # Source order: every appended spelling sits after the existing bare
        # `check` recipe and the existing `popover.emoji-picker .emoji
        # :hover` tail group, so the byte-equal stock twins win the
        # equal-specificity ties under the lower-sheet reading of how the
        # toolkit resource competes.
        for selector in spellings:
            with self.subTest(selector=selector, after="check"):
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("check"),
                )
            with self.subTest(selector=selector, after="emoji"):
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("popover.emoji-picker .emoji :hover"),
                )

    def test_icon_sources_resolve_to_shipped_files(self):
        self.assert_icon_sources_resolve()

    def test_icon_sources_point_at_shipped_assets(self):
        self.assert_shipped_asset_urls()

    def test_titlebutton_separator_hidden(self):
        for selector in (
            "headerbar separator.titlebutton",
            ".titlebar separator.titlebutton",
        ):
            self.assert_rule(selector, {"opacity": "0"})

    def test_separator(self):
        self.assert_separators()

    def test_frame(self):
        self.assert_frame(("frame > border", ".frame"))


if __name__ == "__main__":
    unittest.main()
