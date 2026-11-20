"""Validate GTK 3 Platinum OSD entry fields and spin-button declarations."""

import unittest

from support.gtk_css import strip_comments
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    BUTTON_BEVEL,
    DISABLED_TEXT,
    ENTRY_FIELD,
    ETCH_DARK,
    INVERTED_BUTTON_BEVEL,
)
from support.platinum_palette import BLACK, FACE
from support.repo_root import ROOT


class TestGtkThemeOsdFields(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_osd_entry_fields(self):
        """Pin the four restated stock OSD field arms and nested clearing."""
        field = {
            **ENTRY_FIELD,
            "background-image": "none",
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        focus = {
            **field,
            "outline": f"1px dotted {BLACK}",
            "outline-offset": "0",
            "-gtk-outline-radius": "0",
        }
        disabled = {**field, "color": DISABLED_TEXT["color"]}
        expected = {
            ".osd spinbutton:not(.vertical)": field,
            ".osd entry": field,
            ".osd spinbutton:focus:not(.vertical)": focus,
            ".osd entry:focus": focus,
            ".osd spinbutton:backdrop:not(.vertical)": field,
            ".osd entry:backdrop": field,
            ".osd spinbutton:disabled:not(.vertical)": disabled,
            ".osd entry:disabled": disabled,
            ".osd spinbutton:dir(rtl):not(.vertical)": {
                "box-shadow": "inset -1px 1px #999999"
            },
            ".osd spinbutton:dir(rtl):focus:not(.vertical)": {
                "box-shadow": "inset -1px 1px #999999"
            },
            ".osd spinbutton:dir(rtl):backdrop:not(.vertical)": {
                "box-shadow": "inset -1px 1px #999999"
            },
            ".osd spinbutton:dir(rtl):disabled:not(.vertical)": {
                "box-shadow": "inset -1px 1px #999999"
            },
            ".osd spinbutton:not(.vertical) entry": {
                "min-width": "28px", "margin": "0", "background": "none",
                "background-color": "transparent", "border": "none",
                "border-radius": "0", "box-shadow": "none",
            },
        }
        self.assert_rule_group(expected)
        for property_name in ("outline", "outline-offset", "-gtk-outline-radius"):
            self.assertEqual(
                self.rules[".osd entry:focus"][property_name],
                self.rules["entry:focus"][property_name],
            )
        self.assertEqual(
            self.rules[".osd entry:disabled"]["color"],
            self.rules["entry:disabled"]["color"],
        )
        self.assertEqual(
            {
                selector for selector in self.rules
                if (".osd entry" in selector or ".osd spinbutton" in selector)
                and " button" not in selector
            },
            set(expected),
        )

    def test_osd_spin_field_mirrors_the_etch_in_rtl(self):
        pairs = [
            (".osd spinbutton:not(.vertical),\n.osd entry {", ".osd spinbutton:dir(rtl):not(.vertical)"),
            (".osd spinbutton:focus:not(.vertical),\n.osd entry:focus {", ".osd spinbutton:dir(rtl):focus:not(.vertical)"),
            (".osd spinbutton:backdrop:not(.vertical),\n.osd entry:backdrop {", ".osd spinbutton:dir(rtl):backdrop:not(.vertical)"),
            (".osd spinbutton:disabled:not(.vertical),\n.osd entry:disabled {", ".osd spinbutton:dir(rtl):disabled:not(.vertical)"),
        ]
        stripped = strip_comments(self.css)
        for base, twin in pairs:
            with self.subTest(twin=twin):
                self.assertEqual(self.selectors.count(twin), 1, twin)
                self.assertEqual(self.rules[twin], {"box-shadow": "inset -1px 1px #999999"}, twin)
                self.assertEqual(stripped.count(twin), 1)
                between = stripped[stripped.index(base):stripped.index(twin)]
                self.assertEqual(between.count("{"), 1,
                                 f"{twin} does not sit directly after its base group")

    def test_osd_spinbutton_buttons(self):
        """Pin the twelve OSD spinbutton stepper arms to push-button faces."""
        base = {
            "background-color": FACE, "background-image": "none",
            "border": f"1px solid {BLACK}", "border-radius": "0",
            "box-shadow": BUTTON_BEVEL, "color": BLACK,
            "outline-color": BLACK, "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        active = {**base, "box-shadow": INVERTED_BUTTON_BEVEL}
        disabled = {**base, "color": ETCH_DARK}
        del disabled["outline-color"]
        horizontal = lambda declarations: declarations
        vertical = lambda declarations: {**declarations, "background-clip": "border-box"}
        expected = {
            ".osd spinbutton:not(.vertical) button": horizontal(base),
            ".osd spinbutton:not(.vertical) button:dir(rtl)": horizontal(base),
            ".osd spinbutton:not(.vertical) button:hover": horizontal(base),
            ".osd spinbutton:not(.vertical) button:backdrop": horizontal(base),
            ".osd spinbutton:not(.vertical) button:disabled": horizontal(disabled),
            ".osd spinbutton:not(.vertical) button:dir(ltr):last-child": horizontal(base),
            ".osd spinbutton:not(.vertical) button:dir(rtl):first-child": horizontal(base),
            ".osd spinbutton.vertical button:first-child": vertical(base),
            ".osd spinbutton.vertical button:first-child:hover": vertical(base),
            ".osd spinbutton.vertical button:first-child:active": vertical(active),
            ".osd spinbutton.vertical button:first-child:disabled": vertical(disabled),
            ".osd spinbutton.vertical button:first-child:backdrop": vertical(base),
        }
        self.assertEqual(len(expected), 12)
        self.assert_rule_group(expected)
        self.assertEqual(
            {selector for selector in self.rules
             if "spinbutton" in selector and " button" in selector
             and any(token in selector for token in (
                 ".osd", "app-notification", "touch-selection", "magnifier"
             ))},
            set(expected),
        )


if __name__ == "__main__":
    unittest.main()
