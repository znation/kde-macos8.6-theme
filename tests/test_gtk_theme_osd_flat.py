"""Validate GTK 3 OSD flat-button declarations."""

import unittest

from support.gtk.osd_cases import OsdSelectorAssertions
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import BUTTON_BEVEL, INVERTED_BUTTON_BEVEL, ETCH_DARK
from support.platinum_palette import BLACK, FACE
from support.repo_root import ROOT


class TestGtkThemeOsdFlat(
    OsdSelectorAssertions, GtkSheetRuleCases, unittest.TestCase
):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_osd_flat_button(self):
        """Pin the 24 restated stock OSD flat-button arms.

        No collected reference screenshot shows a GTK OSD overlay or a
        flat button inside one, so the sheet restates the toolkit
        resource's grouped ``.app-notification button.flat, …, .osd
        button.flat`` arms with the existing plain push-button recipe (the
        base ``button`` dictionary ``test_osd_button`` pins):
        the raised ``#DDDDDD`` face with its 1px black border and zero
        radius, ``BUTTON_BEVEL``, and black labels; the ``:hover`` and
        ``:backdrop`` arms repeat the base recipe byte-equal; the active
        and checked arms swap only ``box-shadow`` to
        ``INVERTED_BUTTON_BEVEL``; the disabled arms keep
        ``BUTTON_BEVEL`` with the Inactive grey (``ETCH_DARK``) and no
        ``outline-color``, as the existing disabled arms also claim none.
        The arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); no
        restated arm sets on-disk geometry, so the stock
        ``button.osd`` minimums and the stock ``.osd .scale-popup
        button.flat`` pointer arm is restated by its dedicated test; the
        restated blocks put disabled after backdrop so inactive insensitive
        labels stay grey; active/checked keeps stock's sheet-order win over
        hover.
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
                ".app-notification button.flat",
                "popover.background.touch-selection button.flat",
                "popover.background.magnifier button.flat",
                ".osd button.flat",
                ".app-notification button.flat:hover",
                "popover.background.touch-selection button.flat:hover",
                "popover.background.magnifier button.flat:hover",
                ".osd button.flat:hover",
                ".app-notification button.flat:backdrop",
                "popover.background.touch-selection button.flat:backdrop",
                "popover.background.magnifier button.flat:backdrop",
                ".osd button.flat:backdrop",
            )),
            (disabled, (
                ".app-notification button.flat:disabled",
                "popover.background.touch-selection button.flat:disabled",
                "popover.background.magnifier button.flat:disabled",
                ".osd button.flat:disabled",
            )),
            (active, (
                ".app-notification button.flat:active",
                "popover.background.touch-selection button.flat:active",
                "popover.background.magnifier button.flat:active",
                ".app-notification button.flat:checked",
                "popover.background.touch-selection button.flat:checked",
                "popover.background.magnifier button.flat:checked",
                ".osd button.flat:active",
                ".osd button.flat:checked",
            )),
        ]
        enumerated = self.assert_osd_selector_count(expected, 24)
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        for family in (
            ".app-notification button.flat",
            "popover.background.touch-selection button.flat",
            "popover.background.magnifier button.flat",
            ".osd button.flat",
        ):
            candidates = {family + ":disabled", family + ":backdrop"}
            color = None
            for selector in self.selectors:
                if selector in candidates:
                    color = self.rules[selector]["color"]
            with self.subTest(disabled_backdrop=family):
                self.assertEqual(color, ETCH_DARK)
        self.assertEqual(
            {selector
             for selector in self.rules
             if "button" in selector and "flat" in selector
             and not selector.startswith("button")
             and not selector.startswith("row:selected button")
             and not selector.startswith("notebook > header tab")
             and selector not in
             ("modelbutton.flat", ".menuitem.button.flat",
              "toolbar.inline-toolbar toolbutton:first-child > button.flat",
              "toolbar.inline-toolbar toolbutton:last-child > button.flat",
              "toolbar.inline-toolbar toolbutton:only-child > button.flat")},
            enumerated | {".osd .scale-popup button.flat"},
        )


if __name__ == "__main__":
    unittest.main()
