"""Validate GTK 3 Platinum OSD suggested-action declarations."""

import unittest

from support.gtk.osd_cases import OsdSelectorAssertions
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import BUTTON_BEVEL, INVERTED_BUTTON_BEVEL, ETCH_DARK
from support.platinum_palette import BLACK, FACE
from support.repo_root import ROOT


class TestGtkThemeOsdSuggested(
    OsdSelectorAssertions, GtkSheetRuleCases, unittest.TestCase
):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_osd_suggested_action(self):
        """Pin the nine restated stock OSD suggested-action arms.

        No collected reference screenshot shows a GTK OSD overlay or a
        suggested-action button inside one, so the sheet restates the
        toolkit resource's ``.osd button.suggested-action`` arms with
        the existing plain push-button recipe (the base ``button``
        dictionary ``test_osd_button`` pins), with one clearance stock's
        own arms force: every one of the five stock arms claims
        ``background-clip: padding-box``, which left standing under the
        equal-specificity restatement would clip the restated face to
        the padding box, so every restated arm declares
        ``background-clip: border-box`` and the face paints exactly like
        the existing plain and flat restatements'. The restated arms are
        the raised ``#DDDDDD`` face with its 1px black border and zero
        radius, ``BUTTON_BEVEL``, and black labels; the ``:hover`` and
        ``:backdrop`` arms repeat the base recipe byte-equal, recipe
        ``outline-color`` included, as the existing plain and flat
        backdrop restatements do; the active and checked arms swap only
        ``box-shadow`` to ``INVERTED_BUTTON_BEVEL``; the disabled arms
        keep ``BUTTON_BEVEL`` with the Inactive grey (``ETCH_DARK``) and
        no ``outline-color``, as the existing disabled arms claim none.
        The arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); no
        restated arm sets on-disk geometry, so the stock ``button.osd``
        minimums and the ``button.osd.image-button`` minimum-width arm
        keep governing; the restated blocks keep the stock arm order, so
        the active/checked arm keeps stock's sheet-order win over the
        hover arm.
        """
        base = {
            "background-color": FACE,
            "background-image": "none",
            "background-clip": "border-box",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        active = {**base, "box-shadow": INVERTED_BUTTON_BEVEL}
        disabled = {**base, "color": ETCH_DARK}
        del disabled["outline-color"]
        expected = [
            (base, (
                ".osd button.suggested-action",
                ".osd button.suggested-action:hover",
                ".osd button.suggested-action:backdrop",
            )),
            (active, (
                ".osd button.suggested-action:active:backdrop",
                ".osd button.suggested-action:active",
                ".osd button.suggested-action:checked:backdrop",
                ".osd button.suggested-action:checked",
            )),
            (disabled, (
                ".osd button.suggested-action:disabled:backdrop",
                ".osd button.suggested-action:disabled",
            )),
        ]
        enumerated = self.assert_osd_selector_count(expected, 9)
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        self.assertEqual(
            {selector for selector in self.rules
             if "button" in selector
             and ".osd" in selector
             and "suggested-action" in selector},
            enumerated,
        )


if __name__ == "__main__":
    unittest.main()
