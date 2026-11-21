"""Validate GTK 3 Platinum OSD plain push-button declarations."""

import unittest

from support.gtk.osd_cases import OsdSelectorAssertions
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import BUTTON_BEVEL, ETCH_DARK, INVERTED_BUTTON_BEVEL
from support.platinum_palette import BLACK, FACE
from support.repo_root import ROOT


class TestGtkThemeOsdButtons(
    OsdSelectorAssertions, GtkSheetRuleCases, unittest.TestCase
):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_osd_button(self):
        """Pin the 37 restated stock OSD push-button arms.

        No collected reference screenshot shows a GTK OSD overlay or a
        push button inside one, so the sheet restates the toolkit
        resource's stock ``button.osd`` and grouped ``.app-notification
        button, …, .osd button`` arms with the existing plain push-button
        recipe (the base ``button`` dictionary pinned by
        ``support.gtk_rule_cases.py::GtkSheetRuleCases::test_button``):
        the raised ``#DDDDDD`` face with its 1px black border and zero
        radius, ``BUTTON_BEVEL``, and black labels; the active and checked
        arms swap only ``box-shadow`` to ``INVERTED_BUTTON_BEVEL``; the
        disabled arms keep ``BUTTON_BEVEL`` with the Inactive grey
        (``ETCH_DARK``); ``outline-color: #000000`` replaces the stock
        rgba(238,238,236,0.3) only in the arms whose stock counterparts
        claim an outline colour. The arm selectors and states come from
        gtk-contained.css in /usr/lib/x86_64-linux-gnu/libgtk-3.so.0
        (libgtk-3 3.24.49); no restated arm sets on-disk geometry, so the
        stock ``button.osd`` minimums and the ``button.osd.image-button``
        minimum-width arm keep governing.
        """
        recipe = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        active = {**recipe, "box-shadow": INVERTED_BUTTON_BEVEL}
        disabled = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": ETCH_DARK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        expected = [
            (recipe, (
                "button.osd", "button.osd:hover", "button.osd:backdrop",
                ".app-notification button", ".app-notification.frame button",
                ".csd popover.background.touch-selection button",
                ".csd popover.background.magnifier button",
                "popover.background.touch-selection button",
                "popover.background.magnifier button", ".osd button",
                ".app-notification button:hover",
                "popover.background.touch-selection button:hover",
                "popover.background.magnifier button:hover", ".osd button:hover",
                ".app-notification button:backdrop",
                "popover.background.touch-selection button:backdrop",
                "popover.background.magnifier button:backdrop",
                ".osd button:backdrop",
            )),
            (active, (
                "button.osd:active", "button.osd:checked",
                ".app-notification button:active",
                "popover.background.touch-selection button:active",
                "popover.background.magnifier button:active",
                ".app-notification button:checked",
                "popover.background.touch-selection button:checked",
                "popover.background.magnifier button:checked",
                ".osd button:active:backdrop", ".osd button:active",
                ".osd button:checked:backdrop", ".osd button:checked",
            )),
            (disabled, (
                "button.osd:disabled:backdrop", "button.osd:disabled",
                ".app-notification button:disabled",
                "popover.background.touch-selection button:disabled",
                "popover.background.magnifier button:disabled",
                ".osd button:disabled:backdrop", ".osd button:disabled",
            )),
        ]
        enumerated = self.assert_osd_selector_count(expected, 37)
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        osd_like = (".osd", "app-notification", "touch-selection", "magnifier")
        self.assertEqual(
            {selector for selector in self.rules
             # Match button as a token; spinbuttons are fields. Flat,
             # suggested and destructive buttons have separate recipes.
             if "button" in selector
             and "spinbutton" not in selector
             and "flat" not in selector
             and "suggested-action" not in selector
             and "destructive-action" not in selector
             and any(token in selector for token in osd_like)},
            enumerated,
        )


if __name__ == "__main__":
    unittest.main()
