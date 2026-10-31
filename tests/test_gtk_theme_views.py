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

from support import gtk_css
from support.gtk_css import parse_css
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    MENU_CHECK,
    RAISED_BEVEL,
    TAB_STATES,
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
    @classmethod
    def setUpClass(cls):
        cls.css = gtk_css.read_theme_text(CSS)
        cls.colours, cls.rules, cls.selectors = parse_css(
            cls.css, source=str(CSS.relative_to(ROOT))
        )

    def test_path_bar_tabs(self):
        forms = {
            "base": (".path-bar > button",),
            "hover": (".path-bar > button:hover",),
            "checked": (".path-bar > button:checked",),
            "checked+hover": (".path-bar > button:checked:hover",),
        }
        for state, _selectors, checked in TAB_STATES:
            if state not in forms:
                continue
            expected = {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
            }
            if checked:
                expected["border-bottom-color"] = FACE
                expected["box-shadow"] = "none"
            else:
                expected["box-shadow"] = RAISED_BEVEL
            for selector in forms[state]:
                with self.subTest(state=state, selector=selector):
                    self.assert_rule(selector, expected)

    def test_row_selection_backdrop(self):
        self.assert_row_selection_backdrop((
            "treeview.view:selected:backdrop",
            "list row.activatable:selected:backdrop",
        ))
        self.assertGreater(
            self.css.index("list row.activatable:selected:backdrop"),
            self.css.index("list row.activatable:selected:"),
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
        for state, _selectors, checked in TAB_STATES:
            if state not in forms:
                continue
            expected = {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
            }
            if checked:
                expected["border-bottom-color"] = FACE
                expected["box-shadow"] = "none"
            else:
                expected["box-shadow"] = RAISED_BEVEL
            for selector in forms[state]:
                with self.subTest(state=state, selector=selector):
                    self.assert_rule(selector, expected)

    def test_rubberband(self):
        self.assert_rubberband((".rubberband", "rubberband"))
        # A later .view rule would win the cascade again.
        self.assertGreater(
            self.css.index(".rubberband, rubberband {"),
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

    def test_frame(self):
        self.assert_frame(("frame > border", ".frame"))


if __name__ == "__main__":
    unittest.main()
