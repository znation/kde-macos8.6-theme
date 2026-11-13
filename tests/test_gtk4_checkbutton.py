"""GTK 4 check-button declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases


class TestGtk4Checkbutton(Gtk4SheetRuleCases, unittest.TestCase):
    def test_checkbutton_focus_outline_color(self):
        self.assert_scale_focus_outline("checkbutton:focus:focus-visible")

    def test_checkbutton_focus_transition(self):
        self.assert_scale_slider_transition("checkbutton")

    def test_checkbutton_corners(self):
        # The 2026-11-04 wrapper-corner restatement squares the
        # check-button wrapper under the existing square-corner policy: the
        # base arm on the existing no-transition group and two byte-equal
        # stock twin spellings at the checked-indicator seam.
        self.assertEqual(
            {selector for selector in self.rules if "checkbutton" in selector},
            {
                "checkbutton",
                "checkbutton:focus:focus-visible",
                "checkbutton.grouped",
                "checkbutton.selection-mode",
            },
        )
        for selector in ("checkbutton.grouped", "checkbutton.selection-mode"):
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1, selector)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_square_corner(selector)
        self.assert_rule(
            "checkbutton", {"transition": "none", "border-radius": "0"}
        )
        self.assertEqual(
            self.rules["checkbutton"], {"transition": "none", "border-radius": "0"}
        )
        self.assert_matches_frame("checkbutton", "border-radius")
        # The parser splits the `check, radio` comma group, so the first
        # "check" selector is that group's first member, before the
        # extended `checkbutton` group, and the standalone `check` face
        # group is the next "check" spelling.
        self.assertGreater(
            self.selectors.index("checkbutton"),
            self.selectors.index("check"),
        )
        face = self.selectors.index(
            "check", self.selectors.index("checkbutton:focus:focus-visible") + 1
        )
        for selector in ("checkbutton.grouped", "checkbutton.selection-mode"):
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("checkbutton:focus:focus-visible"),
            )
            self.assertLess(
                self.selectors.index(selector),
                face,
            )


if __name__ == "__main__":
    unittest.main()
