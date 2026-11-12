"""Validate the GTK 3 Platinum sheet's views, menus and dialogs.

This module owns the views-and-dialogs slice of
``tests/test_gtk_theme.py``'s split: the file chooser's path-bar tabs and
places sidebar, the stack switcher, the list and icon-view focus outlines,
the header's drop indicators, the spin-button field, the message dialog's
header band and action area, the title-button boxes, and the menus with
their scroll arrows, separators, checks and shipped icon sources. The
sheet's comment blocks carry each value's provenance.
"""

import re
import unittest
from pathlib import Path

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    CHECK_GLYPH,
    DISABLED_TEXT,
    BUTTON_BEVEL,
    MENU_CHECK,
    ROW_HOVER,
    MIXED_GLYPH,
    RADIO_GLYPH,
    SELECTION_CHECK_STATES,
    SUBMENU_ARROW,
    TILE_CHECK_FACE,
    TITLE_BUTTON_ASSETS,
    TITLE_BUTTON_IMAGE,
)
from support.platinum_palette import (
    BLACK,
    ETCH_DARK,
    FACE,
    SELECTION,
)
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"

MENU_SCROLL_UP = ("menu > arrow.top", ".menu > arrow.top", ".context-menu > arrow.top")
MENU_SCROLL_DOWN = (
    "menu > arrow.bottom",
    ".menu > arrow.bottom",
    ".context-menu > arrow.bottom",
)


class TestGtkThemeViews(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_path_bar_tabs(self):
        forms = {
            "base": (".path-bar > button",),
            "hover": (".path-bar > button:hover",),
            "checked": (".path-bar > button:checked",),
            "checked+hover": (".path-bar > button:checked:hover",),
        }
        self.assert_tab_faces(forms)

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
        # The pressed and popup-holding row states restate the landed
        # faces: stock's four element-level row arms would paint a tinted
        # hover-wash, pressed insets and a selection-accent fill on rows
        # the landed records paint transparent or with the flat lavender
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
        # The landed row spellings are all list-, listview- or
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
        """Pin the selected icon view restated off the landed row selection."""
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
        # The family keeps the landed dotted focus outline and the 2026-11-11
        # disabled-view restatement's two arms as its only other icon-view
        # rules: a renamed restated arm leaves exactly its successor.
        # 2026-11-04: the vertical-stepper and content-view-check corner
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
        """Pin the selected-row check and radio restated off the landed faces."""
        # The 2026-11-06 sheet-tail record answers the toolkit resource's
        # four treeview-class-armed selected-row arms (probed verbatim in
        # the sheet comment and docs/invariants.md) per-property: the
        # colour arm's ink and border return to the landed check recipe's
        # hard black, the checked and indeterminate glyph arms swap the
        # toolkit's recoloured symbolic dot and dash for the landed
        # black-ink shipped assets, and stock's radius and 14px-size arm
        # restates nothing. No landing here adds a face declaration beyond
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
        # Source order: each restated spelling lands after the landed
        # plain-state `radio:checked` glyph rule's parsed position.
        for selector in expected:
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("radio:checked"),
                selector,
            )

    def test_header_drop_indicator(self):
        targets = ("", "header.", "header ")
        states = (
            "button.dnd",
            "button.dnd:hover",
            "button.dnd:active",
            "button.dnd:selected",
        )
        selectors = [
            f"treeview.view {target}{state}"
            for target in targets
            for state in states
        ]
        self.assertEqual(len(selectors), 12, selectors)
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {
                        "background-color": SELECTION,
                        "background-image": "none",
                        "color": BLACK,
                        "text-shadow": "none",
                        "box-shadow": "none",
                        "border-style": "none",
                        "border-radius": "0",
                    },
                )

    def test_header_drop_arm_carries_no_padding(self):
        self.assertNotIn(
            "padding", self.rules["treeview.view button.dnd"]
        )

    def test_no_dndtarget_node_declared(self):
        self.assertNotIn("dndtarget", self.css)

    def test_view_accelerator_editor(self):
        # The stock label face tints the view family's on-screen
        # accelerator editor -- the overlay label a header button shows
        # while it captures a key -- with its accent. No collected
        # reference screenshot shows accelerator editing, so the pinned
        # selection fill answers it, as for the selected rows and the
        # drop header arm (see the sheet's 2026-11-09 adaptation
        # comment); the one stock arm was probed fresh 2026-11-09 with
        # gresource extract of the toolkit resource in
        # /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (its resource path is
        # recorded in docs/invariants.md, line 755), with no ink,
        # geometry or state member beyond background-color.
        spelling = "treeview.view acceleditor > label"
        self.assertEqual(self.selectors.count(spelling), 1, spelling)
        self.assertEqual(self.rules[spelling], {"background-color": SELECTION})
        self.assertEqual(
            {s for s in self.rules if "acceleditor" in s},
            {spelling},
        )
        # Order pin: the rule sits directly after the landed header-drop
        # group and before the landed list-row focus group (the comma
        # group's members are split selectors, so the pin read the sheet
        # text for the earlier operand).
        self.assertGreater(
            self.css.index(spelling),
            self.css.index("treeview.view header button.dnd:selected {"),
        )
        self.assertLess(
            self.css.index(spelling),
            self.css.index("list row:focus {"),
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
        """Pin the selected children restated off the landed row selection."""
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
        # names the state pair. 2026-10-31: selected-text restatements add
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

    def test_places_sidebar(self):
        self.assert_rule(".sidebar", {"background-color": FACE, "color": BLACK})
        self.assert_rule(".sidebar:backdrop", {"background-color": FACE, "color": BLACK})
        self.assert_rule("placessidebar row:backdrop", {"color": BLACK})
        self.assert_rule(
            "placessidebar row.activatable:selected:backdrop",
            {"background-color": SELECTION, "color": BLACK},
        )
        self.assert_rule("placessidebar row.sidebar-new-bookmark-row", {"color": BLACK})
        # The drag-session arms restate the stock drop strip and drag-over
        # row twins on the landed selection lavender with black ink;
        # each keeps stock's own
        # geometry members so the byte-equal spelling wins the cascade by
        # later user-sheet source order.
        expected_drop = {
            "placessidebar row.sidebar-placeholder-row": {
                "padding": "0 8px",
                "min-height": "2px",
                "background-image": f"image({SELECTION})",
                "background-clip": "content-box",
            },
            "placessidebar row:drop(active):not(:disabled)": {
                "color": BLACK,
                "box-shadow":
                    f"inset 0 1px {SELECTION}, inset 0 -1px {SELECTION}",
            },
            "placessidebar row:drop(active):not(:disabled):selected": {
                "color": BLACK,
                "background-color": SELECTION,
            },
        }
        self.assert_rule_group(expected_drop)
        # The element-level drag-over family is exactly these two arms: the
        # sweep kills a renamed spelling or a stray twin.
        self.assertEqual(
            {s for s in self.rules
             if s.startswith("placessidebar row:drop")},
            {
                "placessidebar row:drop(active):not(:disabled)",
                "placessidebar row:drop(active):not(:disabled):selected",
            },
        )
        anchor = self.css.index(".sidebar {")
        for spelling in expected_drop:
            self.assertGreater(self.css.index(spelling), anchor)

    def test_server_list_button_rotation_motion(self):
        selectors = (
            "placesview .server-list-button > image",
            "placesview .server-list-button:checked > image",
        )
        for selector in selectors:
            self.assert_rule(selector, {"transition": "none"})
            # Exact-dict, not the per-property subset: a stray rotation,
            # transform, colour or geometry declaration on either twin
            # must fail, per the entry's guarantee.
            self.assertEqual(self.rules[selector], {"transition": "none"}, selector)
            self.assertEqual(self.selectors.count(selector), 1, selector)
        # The element-level family is exactly these two stock arms: the
        # sweep kills a renamed spelling, a stray state twin or a second
        # rule.
        self.assertEqual(
            {s for s in self.rules if "server-list-button" in s},
            set(selectors),
        )
        # The rules hold the sheet tail, after the landed infobar band's
        # closing selection and link spellings (the parser splits a
        # comma group into its member selectors).
        tail_anchor = max(
            self.selectors.index("infobar > revealer > box selection"),
            self.selectors.index("infobar > revealer > box label:link"),
            self.selectors.index("infobar > revealer > box button:link"),
        )
        for selector in selectors:
            self.assertGreater(self.selectors.index(selector), tail_anchor)

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
        # Source order: the restated group sits after the landed
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

    def test_rubberband(self):
        selectors = (
            ".rubberband",
            "rubberband",
            ".content-view rubberband",
            ".content-view .rubberband",
            "treeview.view rubberband",
            "flowbox rubberband",
        )
        self.assert_rubberband(selectors)
        self.assertEqual(
            {selector for selector in self.rules if "rubberband" in selector},
            set(selectors),
        )
        # A later .view rule would win the cascade again.
        self.assert_rule_after(
            ".rubberband, rubberband,\n.content-view rubberband,",
            ".view, textview text, list {",
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

    def test_message_dialog_header_band(self):
        # The message dialog's title band repaints the landed headerbar.
        # The band restates the landed headerbar, .titlebar group plus its
        # headerbar-only 1px bottom border, the backdrop band restates the
        # landed headerbar:backdrop, .titlebar:backdrop group, and the
        # dialog body corners go square; tying through the landed groups'
        # dictionaries keeps the bands in step with any future header
        # change.
        self.assert_rule(
            "messagedialog .titlebar",
            {**self.rules["headerbar"], "border-width": "0 0 1px 0"},
        )
        self.assert_rule(
            "messagedialog .titlebar:backdrop",
            self.rules["headerbar:backdrop"],
        )
        self.assert_rule(
            "messagedialog.csd.background",
            {"border-radius": "0"},
        )

    def test_sidebar_row_geometry(self):
        # No collected reference screenshot shows a GTK sidebar list,
        # places sidebar or stack sidebar, so the sheet restates the
        # stock sidebar seam and row geometry the landed .sidebar field
        # record leaves stock: the directional border twins and the
        # sidebar-direction separator take the landed etched dark half,
        # and every padding, the 36px row height, the viewport edge
        # drop and the paned border drop are stock's own shapes kept
        # byte-equal. The exact stock arms and the excluded faces live
        # in docs/invariants.md.
        seam = {
            "stacksidebar.sidebar:dir(ltr) list",
            "stacksidebar.sidebar.left list",
            "stacksidebar.sidebar.left:dir(rtl) list",
            ".sidebar:not(separator):dir(ltr)",
            ".sidebar:not(separator).left",
        }
        self.assert_rule_group(
            {selector: {
                "border-right": "1px solid " + ETCH_DARK,
                "border-left-style": "none",
            } for selector in seam}
        )
        self.assert_rule_group(
            {selector: {
                "border-left": "1px solid " + ETCH_DARK,
                "border-right-style": "none",
            } for selector in (
                "stacksidebar.sidebar:dir(rtl) list",
                "stacksidebar.sidebar.right list",
                ".sidebar:not(separator):dir(rtl)",
                ".sidebar:not(separator).right",
            )}
        )
        paned = {
            "paned .sidebar.left",
            "paned .sidebar.right",
            "paned .sidebar.left:dir(rtl)",
            "paned .sidebar:dir(rtl)",
            "paned .sidebar:dir(ltr)",
            "paned .sidebar",
        }
        self.assert_rule_group({key: {"border-style": "none"} for key in paned})
        self.assert_rule("stacksidebar row", {"padding": "10px 4px"})
        self.assert_rule(
            "stacksidebar row > label",
            {"padding-left": "6px", "padding-right": "6px"},
        )
        self.assert_rule("separator.sidebar", {"background-color": ETCH_DARK})
        selection_separator = "separator.sidebar.selection-mode"
        ancestor_selection_separator = ".selection-mode separator.sidebar"
        self.assert_rule(selection_separator, {"background-color": ETCH_DARK})
        self.assert_rule(
            ancestor_selection_separator,
            {"background-color": ETCH_DARK},
        )
        self.assertEqual(self.selectors.count(selection_separator), 1)
        self.assertEqual(self.selectors.count(ancestor_selection_separator), 1)
        separator_family = {
            selector for selector in self.rules if "separator.sidebar" in selector
        }
        self.assertEqual(
            separator_family,
            {
                "separator.sidebar",
                selection_separator,
                ancestor_selection_separator,
            },
        )
        self.assertLess(
            self.selectors.index("separator.sidebar"),
            self.selectors.index(selection_separator),
        )
        self.assertLess(
            self.selectors.index("separator.sidebar"),
            self.selectors.index(ancestor_selection_separator),
        )
        self.assert_rule(
            "placessidebar > viewport.frame",
            {"border-style": "none"},
        )
        self.assert_rule(
            "placessidebar row",
            {"min-height": "36px", "padding": "0px"},
        )
        self.assert_rule("placessidebar row > revealer", {"padding": "0 14px"})
        icon_ltr = "placessidebar row image.sidebar-icon:dir(ltr)"
        icon_rtl = "placessidebar row image.sidebar-icon:dir(rtl)"
        self.assert_rule(icon_ltr, {"padding-right": "8px"})
        self.assert_rule(icon_rtl, {"padding-left": "8px"})
        row_icon = "row image.sidebar-icon"
        self.assert_rule(row_icon, {"opacity": "1"})
        self.assertEqual(self.selectors.count(row_icon), 1)
        rtl_icon_position = self.css.index(icon_rtl)
        self.assertGreater(
            self.css.index(row_icon, rtl_icon_position + len(icon_rtl)),
            rtl_icon_position,
        )
        label_ltr = "placessidebar row label.sidebar-label:dir(ltr)"
        label_rtl = "placessidebar row label.sidebar-label:dir(rtl)"
        self.assert_rule(label_ltr, {"padding-right": "2px"})
        self.assert_rule(label_rtl, {"padding-left": "2px"})
        # The whole sheet holds exactly these sides of the sidebar
        # family: a swapped border side, a dropped direction twin, a
        # stray stock restatement or a renamed restated arm fails the
        # sweep, and the pale separator twin stays owned by the backdrop
        # record.
        self.assertEqual(
            {s for s in self.rules if s.startswith("paned .sidebar")},
            paned,
        )
        self.assertEqual(
            {s for s in self.rules if "image.sidebar-icon" in s},
            {icon_ltr, icon_rtl, row_icon},
        )
        self.assertEqual(
            {s for s in self.rules if "label.sidebar-label" in s},
            {label_ltr, label_rtl},
        )
        self.assertEqual(
            {s for s in self.rules if s.startswith("stacksidebar")},
            {
                "stacksidebar.sidebar:dir(ltr) list",
                "stacksidebar.sidebar.left list",
                "stacksidebar.sidebar.left:dir(rtl) list",
                "stacksidebar.sidebar:dir(rtl) list",
                "stacksidebar.sidebar.right list",
                "stacksidebar row",
                "stacksidebar row > label",
                # The landed needs-attention record owns the badge twin.
                "stacksidebar row.needs-attention > label",
            },
        )
        self.assertNotIn("separator.sidebar:backdrop", self.selectors)
        # The seam complements the landed .sidebar field record in the
        # sheet, so the restated seam arms follow that block in source.
        self.assert_rule_after(
            "stacksidebar.sidebar:dir(ltr) list",
            ".sidebar {",
        )

    def test_message_dialog_action_area(self):
        # The stock toolkit resource re-pads the message dialog's action
        # buttons to 10px 14px and rounds the end buttons' bottom corners
        # to 7px with -gtk-outline-radius; the sheet restates the stock
        # button base padding and square corners on both end arms.
        self.assert_rule(
            "messagedialog.csd .dialog-action-area button",
            {"padding": "4px 9px"},
        )
        for arm in ("first-child", "last-child"):
            self.assert_rule(
                f"messagedialog.csd .dialog-action-area button:{arm}",
                {"border-radius": "0", "-gtk-outline-radius": "0"},
            )

    def test_menu(self):
        for selector in ("menu", ".menu", "popover", ".popover"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "border": f"1px solid {BLACK}",
                    "border-radius": "0",
                },
            )
        for selector in (
            "menuitem:hover",
            ".menuitem:hover",
            "popover modelbutton:hover",
            "popover modelbutton:selected",
        ):
            self.assert_rule(selector, {"background-color": SELECTION})

    def test_menu_row_state_faces(self):
        """Pin the landed menu-row and menu-bar-title faces under every state.

        The nine appended arms rest the toolkit resource's
        higher-specificity classic-menu state spellings so a hovered row or
        hovered or open menu-bar title keeps the selection fill with black
        text, a disabled or backdropped row keeps black rest text and the
        inactive grey when disabled, and a `:dir` arrow keeps the shipped
        submenu triangle in both text directions; the exact stock arms live
        in docs/invariants.md.
        """
        hover = (
            "menu menuitem:hover",
            ".menu menuitem:hover",
            ".context-menu menuitem:hover",
            "menu menuitem:backdrop:hover",
            ".menu menuitem:backdrop:hover",
            ".context-menu menuitem:backdrop:hover",
        )
        self.assert_rule_group(
            {selector: {"color": BLACK, "background-color": SELECTION}
             for selector in hover}
        )
        backdrop = (
            "menu menuitem:backdrop",
            ".menu menuitem:backdrop",
            ".context-menu menuitem:backdrop",
        )
        self.assert_rule_group(
            {selector: {"color": BLACK} for selector in backdrop}
        )
        self.assert_rule_group(
            {selector: {"color": BLACK, "box-shadow": "none"}
             for selector in ("menubar > menuitem:hover",
                              ".menubar > menuitem:hover")}
        )
        disabled = (
            "menu menuitem:disabled",
            ".menu menuitem:disabled",
            ".context-menu menuitem:disabled",
            "menu menuitem:disabled:backdrop",
            ".menu menuitem:disabled:backdrop",
            ".context-menu menuitem:disabled:backdrop",
            "menubar > menuitem:disabled",
            ".menubar > menuitem:disabled",
        )
        self.assert_rule_group(
            {selector: DISABLED_TEXT for selector in disabled}
        )
        # The inactive grey is re-derived from the colour scheme, as the
        # landed disabled-text callers do.
        self.assert_disabled_text(disabled)
        arrows = (
            "menu menuitem arrow:dir(ltr)",
            ".menu menuitem arrow:dir(ltr)",
            ".context-menu menuitem arrow:dir(ltr)",
            "menu menuitem arrow:dir(rtl)",
            ".menu menuitem arrow:dir(rtl)",
            ".context-menu menuitem arrow:dir(rtl)",
        )
        self.assert_rule_group(
            {selector: SUBMENU_ARROW for selector in arrows}
        )
        # Source order: every appended spelling sits after the landed
        # `menuitem:hover` and `menubar > menuitem` selectors, so the
        # byte-equal stock twins win the equal-specificity ties under the
        # lower-sheet reading of how the toolkit resource competes.
        for selector in hover + backdrop + disabled + arrows + (
            "menubar > menuitem:hover",
            ".menubar > menuitem:hover",
        ):
            with self.subTest(selector=selector):
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("menuitem:hover"),
                )
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("menubar > menuitem"),
                )

    def test_csd_container_corners(self):
        """Pin the CSD container and decoration corner restatements.

        The five appended groups rest stock's class-armed popup-menu,
        generic popover-background and decoration-shell radius arms at
        zero; the landed name-level `menu`, `popover`, `tooltip` and
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
        # The class-armed menu spellings have no landed or future neighbour:
        # the landed scroll-arrow and row spellings carry `context-menu` with
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
        # No landed or unrelated decoration selector exists: the sheet names
        # `text-decoration-line` only as a property, never as a selector.
        self.assertEqual(
            {s for s in self.rules if "decoration" in s},
            {
                ".csd.popup decoration",
                "tooltip.csd decoration",
                "messagedialog.csd decoration",
            },
        )
        # Source order: every appended spelling sits after the landed
        # menu, popover and messagedialog restatements, so the byte-equal
        # stock twins win the equal-specificity ties under the lower-sheet
        # reading of how the toolkit resource competes.
        for selector in selectors:
            for landed in ("menu", "popover", "messagedialog.csd.background"):
                with self.subTest(selector=selector, after=landed):
                    self.assertGreater(
                        self.selectors.index(selector),
                        self.selectors.index(landed),
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
        # The four tokens have no landed or unrelated neighbours: the landed
        # keycap corner record is the GTK 4 `shortcut > .keycap` spelling,
        # and the emoji-label rules are the only additional emoji selectors.
        # 2026-11-04: the linked-field end-corner record restates six more
        # linked arm members naming the inline-toolbar token — the three
        # `.inline-toolbar button…` end members and the three
        # `toolbar.inline-toolbar toolbutton…` end members — all pinned
        # with the other linked-field spellings by
        # test_gtk_theme_controls.TestGtkThemeControls::
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
        # 2026-11-09: the four marked-scale fine-tune thumb arms also name
        # the token and are pinned with the marked-scale thumbs by
        # test_gtk_theme.TestGtkTheme.test_marked_scale_thumb_arms; the
        # same date's fine-tuned container geometry restatement adds the
        # two orientation container spellings, pinned by
        # test_gtk_theme_controls.TestGtkThemeControls::
        # test_scale_fine_tune_container_geometry; and the same date's
        # marked-node geometry restatement adds the six fine-tuned tick
        # margin and minimum spellings, pinned by
        # test_gtk_theme_controls.TestGtkThemeControls::
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
        # Source order: every appended spelling sits after the landed
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
        take the landed check face under every state: the 2026-11-05
        tile-check face record extends the landed radius-only groups
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
        # record's zero radius with the 2026-11-05 face record's landed
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
        # The three tokens have no landed or unrelated neighbours: the
        # landed `.content-view` rules name no check node or `:not(list)`
        # guard and the landed `.osd spinbutton.vertical button:first-child`
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
        # check-and-content-view neighbour and the landed `.content-view`
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
        # Source order: every appended spelling sits after the landed bare
        # `check` recipe and the landed `popover.emoji-picker .emoji
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

    def test_menu_scroll_arrows(self):
        for selector in MENU_SCROLL_UP:
            self.assert_rule(
                selector,
                {
                    "-gtk-icon-source": 'url("../assets/arrow-up.svg")',
                    "border-radius": "0",
                },
            )
        for selector in MENU_SCROLL_DOWN:
            self.assert_rule(
                selector,
                {
                    "-gtk-icon-source": 'url("../assets/arrow-down.svg")',
                    "border-radius": "0",
                },
            )

    def test_menu_scroll_arrow_faces(self):
        """Pin the 2026-11-11 menu scroll-arrow face restatement."""
        # 2026-11-11: stock paints the menu's scroll arrows with an opaque
        # white face, a grey hover wash and a near-white backdrop tile, and
        # no collected reference screenshot shows the arrows, so each state
        # arm below restates the landed plain `button.flat` family's
        # dictionary at the arrow's own exact stock spelling, later source
        # order winning the tie per-property.
        raised = {
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
        disabled = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        for selector in (
            "menu > arrow",
            ".menu > arrow",
            ".context-menu > arrow",
            "menu > arrow:hover",
            ".menu > arrow:hover",
            ".context-menu > arrow:hover",
            "menu > arrow:backdrop",
            ".menu > arrow:backdrop",
            ".context-menu > arrow:backdrop",
        ):
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], raised, selector)
        for selector in (
            "menu > arrow:disabled",
            ".menu > arrow:disabled",
            ".context-menu > arrow:disabled",
        ):
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], disabled, selector)
        # The token sweep keys on a substring no other landed selector
        # carries: a dropped twin, a renamed spelling, a lost comma member
        # or a stray extra rule fails.
        self.assertEqual(
            {selector for selector in self.selectors if "menu > arrow" in selector},
            set(MENU_SCROLL_UP) | set(MENU_SCROLL_DOWN)
            | {
                "menu > arrow",
                ".menu > arrow",
                ".context-menu > arrow",
                "menu > arrow:hover",
                ".menu > arrow:hover",
                ".context-menu > arrow:hover",
                "menu > arrow:backdrop",
                ".menu > arrow:backdrop",
                ".context-menu > arrow:backdrop",
                "menu > arrow:disabled",
                ".menu > arrow:disabled",
                ".context-menu > arrow:disabled",
            },
        )
        # Source order: every appended spelling files after the landed
        # glyph group, so the restated faces decide the equal-specificity
        # race against the stock arms.
        for selector in (
            "menu > arrow",
            ".menu > arrow",
            ".context-menu > arrow",
            "menu > arrow:hover",
            ".menu > arrow:hover",
            ".context-menu > arrow:hover",
            "menu > arrow:backdrop",
            ".menu > arrow:backdrop",
            ".context-menu > arrow:backdrop",
            "menu > arrow:disabled",
            ".menu > arrow:disabled",
            ".context-menu > arrow:disabled",
        ):
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("menu > arrow.top"),
            )

    def test_icon_sources_resolve_to_shipped_files(self):
        for ref in re.findall(r'url\("([^"]*)"\)', self.css):
            self.assertTrue((CSS.parent / ref).resolve().is_file(), ref)

    def test_icon_sources_point_at_shipped_assets(self):
        self.assertEqual(
            set(re.findall(r"url\(([^)]*)\)", self.css)),
            {
                '"../assets/checkmark.svg"',
                '"../assets/bullet.svg"',
                '"../assets/check-mixed.svg"',
                '"../assets/arrow-down.svg"',
                '"../assets/arrow-up.svg"',
                '"../assets/arrow-right.svg"',
                '"../assets/submenu-arrow.svg"',
                '"../assets/window-close.svg"',
                '"../assets/window-maximize.svg"',
                '"../assets/window-minimize.svg"',
            },
        )

    def test_menu_check_and_radio_are_boxless(self):
        for selector in (
            "menu menuitem check",
            "menu menuitem radio",
            "popover modelbutton check",
            "popover modelbutton radio",
        ):
            self.assert_rule(selector, MENU_CHECK)

    def test_menu_separator(self):
        self.assert_menu_separator(("menu separator", ".menu separator"))

    def test_titlebutton_separator_hidden(self):
        for selector in (
            "headerbar separator.titlebutton",
            ".titlebar separator.titlebutton",
        ):
            self.assert_rule(selector, {"opacity": "0"})

    def test_separator(self):
        self.assert_separators()

    def test_paned_handle(self):
        self.assert_paned_handles()

    def test_paned_handle_background_images(self):
        for selector in (
            "paned > separator",
            "paned > separator:selected",
            "paned > separator:backdrop",
            "paned > separator.wide",
            "paned > separator.wide:backdrop",
        ):
            self.assert_rule(selector, {"background-image": "none"})

    def test_paned_handle_direction_margins(self):
        # Exact stock twins from the libgtk-3 theme CSS (libgtk-3 3.24.49,
        # probed 2026-10-31): each :dir arm carries one class more than the
        # landed orientation rules, so only a restatement clears their 8px
        # margins and paddings.
        for selector in (
            "paned.horizontal > separator:dir(ltr)",
            "paned.horizontal > separator:dir(rtl)",
        ):
            self.assert_rule(selector, {"margin": "0", "padding": "0"})

    def test_frame(self):
        self.assert_frame(("frame > border", ".frame"))


if __name__ == "__main__":
    unittest.main()
