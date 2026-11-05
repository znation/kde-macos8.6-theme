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
    MENU_CHECK,
    TITLE_BUTTON_ASSETS,
    TITLE_BUTTON_IMAGE,
)
from support.platinum_palette import (
    BLACK,
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
        self.assertGreater(
            self.css.index("list row.activatable:selected:backdrop"),
            self.css.index("list row.activatable:selected:"),
        )

    def test_iconview_selected_arms(self):
        """Pin the selected icon view restated off the landed row selection."""
        for selector in (
            "iconview.view:selected",
            "iconview.view:selected:focus",
            "iconview.view:backdrop:selected",
            "iconview.view:backdrop:selected:focus",
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
        # The family keeps the landed dotted focus outline as its only other
        # icon-view rule: a renamed restated arm leaves exactly its successor.
        self.assertEqual(
            {selector for selector in self.rules if "iconview" in selector},
            {
                "iconview:focus",
                "iconview.view:selected",
                "iconview.view:selected:focus",
                "iconview.view:backdrop:selected",
                "iconview.view:backdrop:selected:focus",
            },
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
            "flowbox flowboxchild:disabled:selected",
            "treeview.view:disabled:selected",
            "row:backdrop:disabled:selected",
            "flowbox flowboxchild:backdrop:disabled:selected",
            "treeview.view:disabled:selected:backdrop",
        ))
        # The family keeps stock's member set: nothing else in the sheet
        # names the state pair. 2026-10-31: selected-text restatements add
        # their seven stock twins to this sweep.
        self.assertEqual(
            {s for s in self.rules if ":disabled:selected" in s},
            {
                "row:disabled:selected",
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
        self.assertGreater(
            self.css.index(
                ".rubberband, rubberband,\n.content-view rubberband,"
            ),
            self.css.index(".view, textview text, list {"),
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
        """Pin the inline-toolbar, keycap, fine-tune trough and emoji hover corners.

        The four appended groups rest stock's inline-toolbar container,
        shortcut keycap, fine-tuned scale trough family and emoji-picker
        hover radius arms at zero; nothing else in the sheet names any of
        the four tokens.
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
        # and the suite's other emoji sweeps name GTK 4 spellings only.
        self.assertEqual(
            {s for s in self.rules if "inline-toolbar" in s}, {".inline-toolbar"}
        )
        self.assertEqual({s for s in self.rules if "keycap" in s}, {".keycap"})
        self.assertEqual(
            {s for s in self.rules if "fine-tune" in s},
            {
                "scale.fine-tune fill",
                "scale.fine-tune highlight",
                "scale.fine-tune trough",
            },
        )
        self.assertEqual(
            {s for s in self.rules if "emoji" in s},
            {"popover.emoji-picker .emoji :hover"},
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

    def test_menu_scroll_arrows(self):
        for selector in MENU_SCROLL_UP:
            self.assert_rule(
                selector, {"-gtk-icon-source": 'url("../assets/arrow-up.svg")'}
            )
        for selector in MENU_SCROLL_DOWN:
            self.assert_rule(
                selector, {"-gtk-icon-source": 'url("../assets/arrow-down.svg")'}
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
