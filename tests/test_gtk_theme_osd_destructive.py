"""Validate GTK 3 Platinum OSD destructive-action declarations."""

import unittest

from support.gtk.osd_cases import OsdSelectorAssertions
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import osd_button_arms
from support.repo_root import ROOT


class TestGtkThemeOsdDestructive(
    OsdSelectorAssertions, GtkSheetRuleCases, unittest.TestCase
):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_osd_destructive_action(self):
        """Pin the nine restated stock OSD destructive-action arms.

        No collected reference screenshot shows a GTK OSD overlay or a
        destructive-action button inside one, so the sheet restates the
        toolkit resource's ``.osd button.destructive-action`` arms with
        the existing plain push-button recipe (the base ``button``
        dictionary ``test_osd_button`` pins), with one clearance stock's
        own arms force: every one of the five stock arms claims
        ``background-clip: padding-box``, which left standing under the
        equal-specificity restatement would clip the restated face to
        the padding box, so every restated arm declares
        ``background-clip: border-box`` and the face paints exactly like
        the existing plain, flat and suggested-action restatements'. The
        restated arms are the raised ``#DDDDDD`` face with its 1px black
        border and zero radius, ``BUTTON_BEVEL``, and black labels; the
        ``:hover`` and ``:backdrop`` arms repeat the base recipe
        byte-equal, recipe ``outline-color`` included, as the existing
        plain and suggested-action backdrop restatements do; the active
        and checked arms swap only ``box-shadow`` to
        ``INVERTED_BUTTON_BEVEL``; the disabled arms keep
        ``BUTTON_BEVEL`` with the Inactive grey (``ETCH_DARK``) and no
        ``outline-color``, as the existing disabled arms claim none. The
        arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); no
        restated arm sets on-disk geometry, so the stock ``button.osd``
        minimums and the ``button.osd.image-button`` minimum-width arm
        keep governing; the restated blocks keep the stock arm order, so
        the active/checked arm keeps stock's sheet-order win over the
        hover arm.
        """
        base, active, disabled = osd_button_arms(clip=True)
        expected = [
            (base, (
                ".osd button.destructive-action",
                ".osd button.destructive-action:hover",
                ".osd button.destructive-action:backdrop",
            )),
            (active, (
                ".osd button.destructive-action:active:backdrop",
                ".osd button.destructive-action:active",
                ".osd button.destructive-action:checked:backdrop",
                ".osd button.destructive-action:checked",
            )),
            (disabled, (
                ".osd button.destructive-action:disabled:backdrop",
                ".osd button.destructive-action:disabled",
            )),
        ]
        enumerated = self.assert_osd_selector_count(expected, 9)
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        self.assertEqual(
            # "button", ".osd" and "destructive-action" as bare tokens:
            # the shipped sheet's only .osd-scoped destructive-action
            # spellings are these nine restated arms. As of 2026-10-31
            # the generic opaque destructive-action family is restated
            # at the sheet-wide tail (pinned by
            # test_gtk_theme_buttons.TestGtkThemeButtons
            # .test_destructive_action_plain_arms), so the whole-sheet
            # destructive-action scan this assertion once made is gone;
            # the .flat colour-class members outside .osd still stay
            # undeclared, so the stock resource keeps governing them.
            {selector
             for selector in self.rules
             if "button" in selector
             and ".osd" in selector
             and "destructive-action" in selector},
            enumerated,
        )


if __name__ == "__main__":
    unittest.main()
