"""GTK 4 toggle-group, indicator-bin and container corner checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases


class TestGtk4ControlCorners(Gtk4SheetRuleCases, unittest.TestCase):
    def test_toggle_group_corners(self):
        # The 2026-11-04 toggle-family corner row adds four stock-spelling
        # members at the sheet's switch seam.
        expected = {
            "toggle-group",
            "toggle-group > toggle",
            "toggle-group.round",
            "toggle-group.round toggle",
        }
        self.assertEqual(
            {selector for selector in self.rules if "toggle-group" in selector},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_square_corner(selector)
        for selector in sorted(expected):
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("switch > image"),
            )
            self.assertLess(
                self.selectors.index(selector),
                self.selectors.index(".toolbar"),
            )

    def test_indicator_bin_corners(self):
        # Stock cuts the indicator bin's badge dot and its reveal mask into
        # circles; the square-corner policy squares both nodes together —
        # squaring one alone would leave them disagreeing. The two
        # descendants of this comma group are the sheet's whole
        # indicatorbin family.
        selectors = {"indicatorbin > indicator", "indicatorbin > mask"}
        self.assertEqual(
            {selector for selector in self.rules if "indicatorbin" in selector},
            selectors,
        )
        for selector in sorted(selectors):
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_square_corner(selector)
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("floating-sheet > sheet"),
                )

    def test_color_button_and_menubutton_container_corners(self):
        # The 2026-11-04 container group squares the colour button's inner
        # swatch face and its overlay plus the plain, suggested-action and
        # opaque menu-button containers; the coloured container paints its
        # own rounding (its background arm rests on the container node
        # while the covered child buttons declare transparent
        # backgrounds), so the six face groups join them in one comma
        # group. The two .pill container spellings stay excluded: the
        # existing pill record already squares them byte-for-byte.
        selectors = {
            "button.color > colorswatch:only-child",
            "button.color > colorswatch:only-child > overlay",
            "menubutton.suggested-action",
            "menubutton.opaque",
            "menubutton.suggested-action.circular",
            "menubutton.opaque.circular",
        }
        for selector in sorted(selectors):
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_square_corner(selector)
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("indicatorbin > mask"),
                )
        # The distinctive button colour token is new to the sheet, so the
        # scan is its whole contract; a stray state twin would carry it
        # into the set. (The menu-button tokens cannot be swept by
        # substring: existing band focus and covered-button spellings name
        # them too, so those faces guard by count-1 and whole-rule above.)
        self.assertEqual(
            {selector for selector in self.rules if "button.color" in selector},
            {
                "button.color > colorswatch:only-child",
                "button.color > colorswatch:only-child > overlay",
            },
        )

if __name__ == "__main__":
    unittest.main()
