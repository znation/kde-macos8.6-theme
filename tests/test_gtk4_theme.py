"""Validate the standalone GTK 4 Platinum stylesheet.

The sheet is one standalone ``gtk.css`` under ``gtk-4.0``. The palette is
reference-grounded through ``support.platinum_palette``; no reference
screenshot shows a GTK widget, so the GTK geometry is this theme's adaptation
rather than a reference crop.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from support import gtk_css
from support.gtk_css import HEX, parse_css, strip_comments
from support.gtk_theme_spec import (
    BASE_DEFINED_COLOURS,
    ETCH_DARK,
    GtkSheetRuleCases,
    RAISED_BEVEL,
)
from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    GREY,
    SELECTION,
    TOOLTIP_FACE,
    TROUGH,
    WHITE,
)
from support.repo_root import ROOT

THEME_ID = "org.macos8.desktop"
THEME_DIR = Path(ROOT) / "theme" / "gtk" / THEME_ID
CSS = THEME_DIR / "gtk-4.0" / "gtk.css"

DEFINED_COLOURS = {
    **BASE_DEFINED_COLOURS,
    "accent_bg_color": SELECTION,
    "accent_fg_color": BLACK,
    "window_bg_color": FACE,
    "window_fg_color": BLACK,
    "view_bg_color": WHITE,
    "view_fg_color": BLACK,
    "headerbar_bg_color": FACE,
    "headerbar_fg_color": BLACK,
    "headerbar_border_color": BLACK,
    "headerbar_backdrop_color": FACE,
    "popover_bg_color": FACE,
    "popover_fg_color": BLACK,
    "card_bg_color": FACE,
    "card_fg_color": BLACK,
    "dialog_bg_color": FACE,
    "dialog_fg_color": BLACK,
    "sidebar_bg_color": FACE,
    "sidebar_fg_color": BLACK,
    "sidebar_backdrop_color": FACE,
    "sidebar_border_color": BLACK,
    "secondary_sidebar_bg_color": FACE,
    "secondary_sidebar_fg_color": BLACK,
    "secondary_sidebar_backdrop_color": FACE,
    "secondary_sidebar_border_color": BLACK,
    "thumbnail_bg_color": WHITE,
    "thumbnail_fg_color": BLACK,
    "scrollbar_outline_color": BLACK,
}

class TestGtk4Theme(GtkSheetRuleCases, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = gtk_css.read_theme_text(CSS)
        cls.colours, cls.rules, cls.selectors = parse_css(
            cls.css, source=str(CSS.relative_to(ROOT))
        )

    def test_theme_colours(self):
        self.assertEqual(self.colours, DEFINED_COLOURS)

    def test_stands_alone(self):
        self.assertNotIn("@import", self.css)
        self.assertNotIn("url(", self.css)
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
            TOOLTIP_FACE,
        }
        self.assertEqual(set(HEX.findall(strip_comments(self.css))), palette)

    def test_no_status_or_translucent_shade_roles(self):
        # Scan the raw declarations, not the parsed hex map, so a status or
        # shade role declared with a non-hex value (for example rgba(...))
        # cannot escape this check.
        names = re.findall(
            r"@define-color\s+([-A-Za-z0-9_]+)", strip_comments(self.css)
        )
        for name in names:
            with self.subTest(colour=name):
                self.assertFalse(
                    name.startswith(
                        ("success_", "warning_", "error_", "destructive_")
                    ),
                )
                self.assertFalse(
                    name == "shade_color" or name.endswith("_shade_color")
                )

    def test_no_universal_selector(self):
        for selector in self.selectors:
            self.assertNotIn("*", selector)

    def test_window_and_background(self):
        for selector in ("window", ".background"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "color": BLACK,
                    "border-radius": "0",
                },
            )

    def test_notebook_header(self):
        self.assert_rule(
            "notebook > header",
            {
                "background-color": FACE,
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
            },
        )

    def test_popover(self):
        for selector in ("popover > contents", "popover > arrow"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "border": f"1px solid {BLACK}",
                    "border-radius": "0",
                    "box-shadow": "none",
                },
            )
        for selector in (
            "popover.menu modelbutton:hover",
            "popover.menu modelbutton:selected",
        ):
            self.assert_rule(selector, {"background-color": SELECTION})

    def test_menu_separator(self):
        self.assert_menu_separator(
            ("popover separator", "popover.background separator")
        )

    def test_frame(self):
        self.assert_frame(("frame > border", ".frame"))

    def test_scrollbar(self):
        self.assert_rule(
            "scrollbar > range > trough",
            {
                "background-color": TROUGH,
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
            },
        )
        self.assert_rule(
            "scrollbar > range > trough > slider",
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "margin": "0",
                "box-shadow": RAISED_BEVEL,
            },
        )

    def test_progressbar(self):
        self.assert_progressbar(
            trough="progressbar > trough",
            progress="progressbar > trough > progress",
            disabled="progressbar > trough > progress:disabled",
        )

    def test_scale(self):
        self.assert_scale(
            trough="scale > trough",
            fill=("scale > trough > fill", "scale > trough > highlight"),
            slider="scale > trough > slider",
            horizontal="scale.horizontal > trough > slider",
            vertical="scale.vertical > trough > slider",
            disabled="scale > trough > slider:disabled",
        )

    def test_toolbar(self):
        self.assert_rule(
            ".toolbar",
            {
                "background-color": FACE,
                "border-bottom": f"1px solid {ETCH_DARK}",
                "box-shadow": f"inset 0 -1px {WHITE}",
            },
        )


if __name__ == "__main__":
    unittest.main()
