"""Validate GTK 3 Platinum OSD check and radio indicator declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import CHECK, RADIO
from support.platinum_palette import BLACK
from support.repo_root import ROOT


class TestGtkThemeOsdIndicators(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_osd_check_radio(self):
        """Pin the ten restated stock OSD indicator arms.

        No collected reference screenshot shows a check or radio inside a GTK
        OSD overlay, so the sheet restates the toolkit resource's five `.osd`
        indicator arms with the existing plain check and radio recipes (CHECK
        and RADIO in ``support.gtk_theme_spec.py``) plus two clearances the
        stock arms claim: the white-on-dark text and icon shadows, cleared,
        and a black focus-outline colour in place of the stock
        rgba(238,238,236,0.3). The arm selectors and states come from
        gtk-contained.css in /usr/lib/x86_64-linux-gnu/libgtk-3.so.0
        (libgtk-3 3.24.49); each arm is byte-for-byte the recipe in every
        state, because the armed spellings set no geometry, glyph source or
        checked spelling stock could override.
        """
        clearance = {
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        check = {**CHECK, **clearance}
        radio = {**RADIO, **clearance}
        states = ("", ":hover", ":active", ":backdrop", ":disabled")
        expected = {}
        for state in states:
            expected[f".osd check{state}"] = check
            expected[f".osd radio{state}"] = radio
        parsed = {}
        for selector in expected:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected[selector])
            parsed[selector] = self.rules[selector]
        self.assertEqual(
            [dict(parsed[f".osd check{state}"]) for state in states],
            [check] * 5,
        )
        self.assertEqual(
            [dict(parsed[f".osd radio{state}"]) for state in states],
            [radio] * 5,
        )
        self.assertEqual(
            {selector for selector in self.rules
             if ".osd check" in selector or ".osd radio" in selector},
            set(expected),
        )


if __name__ == "__main__":
    unittest.main()
