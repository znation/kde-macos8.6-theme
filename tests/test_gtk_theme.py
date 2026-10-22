"""Validate the standalone GTK 3 Platinum theme.

The theme is one ``index.theme`` descriptor and one standalone ``gtk.css``.
The palette is reference-grounded through ``support.platinum_palette``; no
reference screenshot shows a GTK widget, so the GTK geometry is this theme's
adaptation rather than a reference crop.
"""

from __future__ import annotations

import configparser
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import gtk_css
from support.gtk_css import HEX, parse_css
from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    GREY,
    SELECTION,
    TROUGH,
    WHITE,
)
from support.repo_root import ROOT

THEME_ID = "org.macos8.desktop"
THEME_DIR = Path(ROOT) / "theme" / "gtk" / THEME_ID
INDEX = THEME_DIR / "index.theme"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"

# The etched separator's dark half, pinned to the reference by
# tests/test_desktoptheme_line.py's DARK value.
ETCH_DARK = "#888888"

DEFINED_COLOURS = {
    "theme_bg_color": FACE,
    "theme_fg_color": BLACK,
    "theme_base_color": WHITE,
    "theme_text_color": BLACK,
    "theme_selected_bg_color": SELECTION,
    "theme_selected_fg_color": BLACK,
    "borders": BLACK,
    "unfocused_borders": GREY,
}

RAISED_BEVEL = f"inset 1px 1px {WHITE}, inset -1px -1px {GREY}"
BUTTON_BEVEL = f"inset 1px 1px {WHITE}, inset -1px -1px {BUTTON_SHADOW}"
INVERTED_BUTTON_BEVEL = f"inset 1px 1px {BUTTON_SHADOW}, inset -1px -1px {WHITE}"

# Every tab state covers both the plain and the notebook-scoped selectors, in
# the plain and `.reorderable-page` forms. A checked state also names the third
# member: whether its bevel and bottom border must be dropped.
TAB_STATES = (
    (
        "base",
        (
            "tab",
            "tab.reorderable-page",
            "notebook > header > tabs > tab",
            "notebook > header > tabs > tab.reorderable-page",
        ),
        False,
    ),
    (
        "hover",
        (
            "tab:hover",
            "tab.reorderable-page:hover",
            "notebook > header > tabs > tab:hover",
            "notebook > header > tabs > tab.reorderable-page:hover",
        ),
        False,
    ),
    (
        "checked",
        (
            "tab:checked",
            "tab.reorderable-page:checked",
            "notebook > header > tabs > tab:checked",
            "notebook > header > tabs > tab.reorderable-page:checked",
        ),
        True,
    ),
    (
        "checked+hover",
        (
            "tab:checked:hover",
            "tab.reorderable-page:checked:hover",
            "notebook > header > tabs > tab:checked:hover",
            "notebook > header > tabs > tab.reorderable-page:checked:hover",
        ),
        True,
    ),
    (
        "backdrop",
        (
            "tab:backdrop",
            "tab.reorderable-page:backdrop",
            "notebook > header > tabs > tab:backdrop",
            "notebook > header > tabs > tab.reorderable-page:backdrop",
        ),
        False,
    ),
    (
        "backdrop+checked",
        (
            "tab:backdrop:checked",
            "tab.reorderable-page:backdrop:checked",
            "notebook > header > tabs > tab:backdrop:checked",
            "notebook > header > tabs > tab.reorderable-page:backdrop:checked",
        ),
        True,
    ),
)


class TestGtkTheme(unittest.TestCase):
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
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            secret = tmp / "secret"
            secret.write_text("PRIVATE-LINE\n", encoding="utf-8")
            link = root / "index.theme"
            link.symlink_to(secret)
            with mock.patch.object(gtk_css, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "symlink escape"):
                    gtk_css.read_theme_text(link)

    def assert_rule(self, selector, expected):
        """Assert *selector* exists and carries each declaration in *expected*."""
        self.assertIn(selector, self.rules, f"missing rule for {selector}")
        for name, value in expected.items():
            self.assertEqual(
                self.rules[selector].get(name),
                value,
                f"{selector}: expected {name}: {value}",
            )

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

    def test_headerbar(self):
        for selector in ("headerbar", ".titlebar"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "background-image": "none",
                    "border": f"1px solid {BLACK}",
                    "border-radius": "0",
                    "box-shadow": "none",
                },
            )
        self.assert_rule("headerbar", {"border-width": "0 0 1px 0"})

    def test_button(self):
        self.assert_rule(
            "button",
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": BUTTON_BEVEL,
            },
        )
        self.assert_rule("button:hover", {"background-color": FACE})
        for selector in ("button:active", "button:checked"):
            self.assert_rule(selector, {"box-shadow": INVERTED_BUTTON_BEVEL})

    def test_entry(self):
        self.assert_rule(
            "entry",
            {
                "background-color": WHITE,
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": f"inset 1px 1px {GREY}",
                "color": BLACK,
            },
        )

    def test_notebook_header(self):
        self.assert_rule(
            "notebook > header",
            {"background-color": FACE, "border": f"1px solid {BLACK}"},
        )

    def test_tab_states(self):
        for state, selectors, checked in TAB_STATES:
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
            for selector in selectors:
                with self.subTest(state=state, selector=selector):
                    self.assert_rule(selector, expected)

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
        for selector in ("menuitem:hover", ".menuitem:hover"):
            self.assert_rule(selector, {"background-color": SELECTION})

    def test_scrollbar(self):
        self.assert_rule(
            "scrollbar",
            {"background-color": TROUGH, "border": f"1px solid {BLACK}"},
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


if __name__ == "__main__":
    unittest.main()
