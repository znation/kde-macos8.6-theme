"""Validate the standalone GTK 3 Platinum theme.

The theme is one ``index.theme`` descriptor and one standalone ``gtk.css``.
The palette is reference-grounded through ``support.platinum_palette``; no
reference screenshot shows a GTK widget, so most GTK geometry is this theme's
adaptation, while the scroll-bar stepper box copies the reference's own scroll
bar.
"""

from __future__ import annotations

import configparser
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import gtk_css
from support.desktoptheme_paths import SETUP_MAX_ROWS, SETUP_REFERENCE
from support.gtk_css import HEX, parse_css
from support.gtk_theme_spec import (
    BASE_DEFINED_COLOURS as DEFINED_COLOURS,
    ETCH_DARK,
    LINK,
    VISITED_LINK,
    GtkSheetRuleCases,
    MENU_CHECK,
    RAISED_BEVEL,
    SCROLLBAR_STEPPER,
    SCROLLBAR_STEPPER_ACTIVE,
    SCROLLBAR_STEPPER_ARROWS,
    TITLE_BUTTON_IMAGE,
)
from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    GREY,
    INACTIVE_OUTLINE,
    SELECTION,
    TOOLTIP_FACE,
    TROUGH,
    WHITE,
    hex_colour,
)
from support.reference_image import ReferenceScreenshotMixin
from support.repo_root import ROOT
from support.svg_case import parse_svg
from support.symlink_fixtures import symlinked_repo
from svg_assertions import (
    assert_no_script_elements,
    assert_no_style_elements,
    assert_root_canvas,
    attribute_values,
    children_named,
    circle_geometry_and_fill,
)

THEME_ID = "org.macos8.desktop"
THEME_DIR = Path(ROOT) / "theme" / "gtk" / THEME_ID
INDEX = THEME_DIR / "index.theme"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"
CHECKMARK = THEME_DIR / "assets" / "checkmark.svg"
BULLET = THEME_DIR / "assets" / "bullet.svg"
ARROW_DOWN = THEME_DIR / "assets" / "arrow-down.svg"
ARROW_UP = THEME_DIR / "assets" / "arrow-up.svg"
ARROW_RIGHT = THEME_DIR / "assets" / "arrow-right.svg"
SUBMENU_ARROW_SVG = THEME_DIR / "assets" / "submenu-arrow.svg"
ICON_GO_NEXT = (
    Path(ROOT)
    / "theme"
    / "icons"
    / THEME_ID
    / "16x16"
    / "actions"
    / "go-next-symbolic.svg"
)

MENU_SCROLL_UP = ("menu > arrow.top", ".menu > arrow.top", ".context-menu > arrow.top")
MENU_SCROLL_DOWN = (
    "menu > arrow.bottom",
    ".menu > arrow.bottom",
    ".context-menu > arrow.bottom",
)


def assert_svg_root_first(test, path):
    """Assert *path* puts its SVG root before any provenance comment.

    GTK loads a ``-gtk-icon-source`` SVG through gdk-pixbuf, whose sniffer
    only recognizes a file whose ``<svg`` root sits near the start; a comment
    before the root leaves the glyph blank. An XML declaration is optional
    and accepted, but the provenance comment belongs inside the root.
    """
    test.assertRegex(
        path.read_text(encoding="utf-8"),
        r"^\s*(?:<\?xml[^>]*\?>\s*)?<svg\b",
    )


class TestGtkTheme(GtkSheetRuleCases, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index_text = gtk_css.read_theme_text(INDEX)
        cls.css = gtk_css.read_theme_text(CSS)
        cls.colours, cls.rules, cls.selectors = parse_css(
            cls.css, source=str(CSS.relative_to(ROOT))
        )

    def test_theme_read_refuses_a_symlink_escape(self):
        """A checked-in symlink must not feed a private file to a diagnostic."""
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "index.theme", "PRIVATE-LINE\n"
            )
            with mock.patch.object(gtk_css, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "symlink escape"):
                    gtk_css.read_theme_text(link)

    def test_index_theme(self):
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str
        parser.read_string(self.index_text)

        entry = parser["Desktop Entry"]
        self.assertEqual(entry["Type"], "X-GNOME-Metatheme")
        self.assertEqual(entry["Name"], "Mac OS 8.6 Platinum")
        self.assertEqual(entry["Encoding"], "UTF-8")
        self.assertEqual(
            entry["Comment"],
            "Standalone Platinum controls for GTK 3 applications",
        )

        metatheme = parser["X-GNOME-Metatheme"]
        self.assertEqual(metatheme["Name"], "Mac OS 8.6 Platinum")
        self.assertEqual(metatheme["GtkTheme"], THEME_ID)

    def test_theme_colours(self):
        self.assertEqual(self.colours, DEFINED_COLOURS)

    def test_imports_nothing_and_does_not_mention_adwaita(self):
        self.assertNotIn("@import", self.css)
        self.assertNotIn("adwaita", self.css.lower())

    def test_only_palette_hex_literals(self):
        palette = {
            BLACK,
            WHITE,
            GREY,
            FACE,
            BUTTON_SHADOW,
            TROUGH,
            SELECTION,
            ETCH_DARK,
            LINK,
            VISITED_LINK,
            TOOLTIP_FACE,
            INACTIVE_OUTLINE,
        }
        self.assertEqual(set(HEX.findall(self.css)), palette)

    def test_no_universal_selector(self):
        for selector in self.selectors:
            self.assertNotIn("*", selector)

    def test_window_and_background(self):
        for selector in ("window", ".background"):
            self.assert_rule(
                selector,
                {"background-color": FACE, "color": BLACK},
            )

    def test_notebook_header(self):
        self.assert_rule(
            "notebook > header",
            {"background-color": FACE, "border": f"1px solid {BLACK}"},
        )

    def test_tree_header(self):
        self.assert_tree_header(("treeview.view header button",))

    def test_expander_arrows(self):
        self.assert_expander_arrows(
            ("treeview.view.expander", "expander title > arrow"),
            ("treeview.view.expander:checked", "expander title > arrow:checked"),
        )

    def test_submenu_arrow(self):
        self.assert_submenu_arrow(("menu menuitem arrow",), sized=True)

    def test_text_selection(self):
        self.assert_text_selection(
            ("entry selection", "spinbutton selection", "label selection", "textview text selection")
        )

    def test_disabled_text(self):
        self.assert_disabled_text(("label:disabled", "entry:disabled", "spinbutton:disabled"))

    def test_view_background(self):
        self.assert_view_background((".view", "textview text", "list"))

    def test_links(self):
        self.assert_links(
            ("button:link", "button:visited"),
            ("label:link", "button:link > label"),
            ("label:visited", "button:visited > label"),
            {"text-decoration-line": "underline"},
        )

    def test_disabled_text_follows_the_entry_text_rule(self):
        # spinbutton:disabled ties spinbutton:not(.vertical) on specificity, so
        # only coming later greys a disabled spin button's text.
        self.assertGreater(
            self.css.index("label:disabled, entry:disabled, spinbutton:disabled {"),
            self.css.index("entry, spinbutton:not(.vertical) {"),
        )

    def test_link_button_follows_the_button_state_rules(self):
        # button:link ties button:hover and :active on specificity, so only
        # coming later keeps the link button faceless while hovered or pressed.
        link = self.css.index("button:link, button:visited {")
        for rule in ("button {", "button:hover {", "button:active, button:checked {"):
            self.assertGreater(link, self.css.index("\n" + rule), rule)

    def test_calendar(self):
        self.assert_calendar(("calendar:selected",), ("calendar:indeterminate",))

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
            for control, asset in (
                ("close", "window-close.svg"),
                ("maximize", "window-maximize.svg"),
                ("minimize", "window-minimize.svg"),
            ):
                self.assert_title_button(
                    f"{scope} button.titlebutton.{control}", asset
                )
            self.assert_rule(
                f"{scope} button.titlebutton image", TITLE_BUTTON_IMAGE
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

    def test_icon_sources_point_at_shipped_assets(self):
        self.assertEqual(
            set(re.findall(r"url\(([^)]*)\)", self.css)),
            {
                '"../assets/checkmark.svg"',
                '"../assets/bullet.svg"',
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

    def test_frame(self):
        self.assert_frame(("frame > border", ".frame"))

    def test_scrollbar(self):
        self.assert_rule(
            "scrollbar",
            {
                "background-color": TROUGH,
                "border": f"1px solid {BLACK}",
                "padding": "0",
            },
        )
        self.assert_rule(
            "scrollbar slider",
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": RAISED_BEVEL,
            },
        )

    def test_scrollbar_steppers(self):
        self.assert_rule(
            "scrollbar:not(.overlay-indicator)",
            {
                "-GtkScrollbar-has-backward-stepper": "true",
                "-GtkScrollbar-has-forward-stepper": "true",
            },
        )
        self.assert_rule(
            "scrollbar.overlay-indicator",
            {
                "-GtkScrollbar-has-backward-stepper": "false",
                "-GtkScrollbar-has-forward-stepper": "false",
            },
        )
        self.assert_rule("scrollbar button", SCROLLBAR_STEPPER)
        self.assert_rule("scrollbar button:hover", {"background-color": TROUGH})
        self.assert_rule("scrollbar button:active", SCROLLBAR_STEPPER_ACTIVE)
        for selector, expected in SCROLLBAR_STEPPER_ARROWS.items():
            with self.subTest(selector=selector):
                self.assert_rule(selector, expected)

    def test_progressbar(self):
        self.assert_progressbar(
            trough="progressbar trough",
            progress="progressbar progress",
            disabled="progressbar progress:disabled",
        )

    def test_spinner(self):
        self.assert_spinner("-gtk-icon-transform")

    def test_levelbar(self):
        self.assert_levelbar(
            trough="levelbar trough",
            filled="levelbar block.filled",
            empty="levelbar block.empty",
            disabled="levelbar block.filled:disabled",
            horizontal="levelbar.horizontal block",
            vertical="levelbar.vertical block",
        )

    def test_switch(self):
        self.assert_switch(
            slider="switch slider",
            disabled_slider="switch:disabled slider",
            glyph="switch image",
        )

    def test_scale(self):
        self.assert_scale(
            trough="scale trough",
            fill=("scale fill", "scale highlight"),
            slider="scale slider",
            horizontal="scale.horizontal slider",
            vertical="scale.vertical slider",
            disabled="scale slider:disabled",
        )

    def test_menubar_titles(self):
        self.assert_menubar_titles("menubar > menuitem")

    def test_toolbar_and_menubar(self):
        for selector in ("toolbar", "menubar"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "border-bottom": f"1px solid {ETCH_DARK}",
                    "box-shadow": f"inset 0 -1px {WHITE}",
                },
            )


class TestScrollbarStepperReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The stepper box face and divider must match the reference screenshot.

    The installer CD window's left stepper is a 14x14 #EEEEEE face between the
    bar's 1px #000000 border (x=23, y=462 and y=477) and a 1px #555555
    divider at x=38, so the visible box is 16x16. ``TestGtkTheme`` pins the
    sheet to ``SCROLLBAR_STEPPER`` and its direction rules, so this ties that
    14px face and divider to a screenshot.
    """

    REFERENCE = SETUP_REFERENCE
    MAX_ROWS = SETUP_MAX_ROWS

    def test_stepper_box_matches_reference(self):
        face_left, face_right = 24, 37
        face_top, face_bottom = 463, 476
        for x, y in ((face_left, face_top), (face_right, face_bottom)):
            with self.subTest(x=x, y=y):
                self.assertEqual(hex_colour(self.pixel(x, y)), TROUGH)
        for x, y in ((23, 468), (30, 462), (30, 477)):
            with self.subTest(x=x, y=y):
                self.assertEqual(hex_colour(self.pixel(x, y)), BLACK)
        self.assertEqual(hex_colour(self.pixel(38, 468)), INACTIVE_OUTLINE)
        face_width = face_right - face_left + 1
        face_height = face_bottom - face_top + 1
        self.assertEqual(face_width, 14)
        self.assertEqual(face_height, 14)
        self.assertEqual(SCROLLBAR_STEPPER["min-width"], f"{face_width}px")
        self.assertEqual(SCROLLBAR_STEPPER["min-height"], f"{face_height}px")
        self.assertEqual(
            SCROLLBAR_STEPPER_ARROWS["scrollbar.horizontal button.up"][
                "border-right"
            ],
            f"1px solid {INACTIVE_OUTLINE}",
        )


class TestCheckGlyphs(unittest.TestCase):
    """The checked check and radio glyphs GTK loads from the shipped assets."""

    @classmethod
    def setUpClass(cls):
        cls.checkmark = parse_svg(CHECKMARK)
        cls.bullet = parse_svg(BULLET)

    def test_assets_stand_alone(self):
        for tree in (self.checkmark, self.bullet):
            assert_no_script_elements(self, tree)
            assert_no_style_elements(self, tree)

    def test_assets_put_the_root_first(self):
        for path in (CHECKMARK, BULLET):
            with self.subTest(asset=path.name):
                assert_svg_root_first(self, path)

    def test_assets_span_a_14px_canvas(self):
        for tree in (self.checkmark, self.bullet):
            assert_root_canvas(self, tree, 14, 14)

    def test_assets_use_only_the_two_glyph_fills(self):
        self.assertEqual(
            attribute_values(self.checkmark, "fill")
            | attribute_values(self.bullet, "fill"),
            {"none", BLACK},
        )

    def test_checkmark_geometry(self):
        paths = children_named(self.checkmark.getroot(), "path")
        self.assertEqual(len(paths), 1)
        path = paths[0]
        self.assertEqual(path.get("d"), "M 2.5,7.5 L 5.5,10.5 L 11.5,4.5")
        self.assertEqual(path.get("fill"), "none")
        self.assertEqual(path.get("stroke"), BLACK)
        self.assertEqual(path.get("stroke-width"), "2")
        self.assertEqual(path.get("stroke-linecap"), "square")
        self.assertEqual(path.get("stroke-linejoin"), "miter")

    def test_bullet_geometry(self):
        circles = children_named(self.bullet.getroot(), "circle")
        self.assertEqual(len(circles), 1)
        self.assertEqual(
            circle_geometry_and_fill(circles[0]),
            (7.0, 7.0, 2.5, BLACK),
        )


class TestArrowGlyphs(unittest.TestCase):
    """The combo box, menu scroll and disclosure arrow glyphs GTK loads from assets."""

    @classmethod
    def setUpClass(cls):
        cls.down = parse_svg(ARROW_DOWN)
        cls.up = parse_svg(ARROW_UP)
        cls.right = parse_svg(ARROW_RIGHT)
        cls.submenu = parse_svg(SUBMENU_ARROW_SVG)

    def test_assets_stand_alone(self):
        for tree in (self.down, self.up, self.right, self.submenu):
            assert_no_script_elements(self, tree)
            assert_no_style_elements(self, tree)

    def test_assets_put_the_root_first(self):
        for path in (ARROW_DOWN, ARROW_UP, ARROW_RIGHT, SUBMENU_ARROW_SVG):
            with self.subTest(asset=path.name):
                assert_svg_root_first(self, path)

    def test_assets_span_a_16px_canvas(self):
        for tree in (self.down, self.up, self.right, self.submenu):
            assert_root_canvas(self, tree, 16, 16)

    def test_assets_use_only_the_black_fill(self):
        self.assertEqual(
            attribute_values(self.down, "fill")
            | attribute_values(self.up, "fill")
            | attribute_values(self.right, "fill")
            | attribute_values(self.submenu, "fill"),
            {BLACK},
        )

    def test_arrow_geometry(self):
        expected = (
            (self.down, "M 4,5 L 12,5 L 8,11 Z"),
            (self.up, "M 4,11 L 12,11 L 8,5 Z"),
            (self.right, "M 5,4 L 5,12 L 11,8 Z"),
        )
        for tree, path_d in expected:
            with self.subTest(path=path_d):
                paths = children_named(tree.getroot(), "path")
                self.assertEqual(len(paths), 1)
                self.assertEqual(paths[0].get("d"), path_d)
                self.assertEqual(paths[0].get("fill"), BLACK)

    def test_submenu_arrow_copies_the_icon_theme_triangle(self):
        paths = []
        for tree in (self.submenu, parse_svg(ICON_GO_NEXT)):
            found = children_named(tree.getroot(), "path")
            self.assertEqual(len(found), 1)
            paths.append((found[0].get("d"), found[0].get("fill")))
        self.assertEqual(paths[0], paths[1])


if __name__ == "__main__":
    unittest.main()
