"""GTK 4 emoji declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import ETCH_DARK
from support.platinum_palette import WHITE


class TestGtk4Emoji(Gtk4SheetRuleCases, unittest.TestCase):
    def test_emoji_section_button_focus_outline_color(self):
        selector = "button.emoji-section.image-button:focus:focus-visible:not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque)"
        self.assert_black_focus_outline((selector,))
        # The 2026-11-04 residual radii record adds the section button's
        # own byte-equal zero-radius spelling to this token sweep; the
        # focus spelling stays the sweep's other member.
        self.assertEqual(
            {item for item in self.selectors if "emoji-section" in item},
            {
                selector,
                "button.emoji-section.image-button:not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque)",
            },
        )

    def test_emoji_strip_rims(self):
        # An emoji picker's own strips draw stock's greige rims around the
        # picker's band of sections: the search strip paints a bottom rim
        # and the section toolbar paints a top rim. No collected reference
        # screenshot shows a GTK emoji picker, so the bottom rim joins the
        # landed etched band and the top rim takes the landed dark
        # separator ink as a flat rim.
        searchbar = ".emoji-searchbar"
        toolbar = ".emoji-toolbar"
        expected = {
            "border-bottom": f"1px solid {ETCH_DARK}",
            "box-shadow": f"inset 0 -1px {WHITE}",
        }
        self.assert_rule(searchbar, expected)
        self.assert_exact_rule_once(searchbar, expected)
        self.assert_rule(toolbar, {"border-top": f"1px solid {ETCH_DARK}"})
        self.assertEqual(self.selectors.count(toolbar), 1)
        for prop in ("border-bottom", "box-shadow"):
            self.assertEqual(
                self.rules[searchbar][prop],
                self.rules["infobar > revealer > box"][prop],
            )
        self.assertEqual(
            self.rules[toolbar]["border-top"],
            f"1px solid {self.rules['popover separator']['background-color']}",
        )
        # The spellings are new to the sheet, so a stray member, colour,
        # padding or second rule shows up in the sweep.
        self.assertEqual(
            {s for s in self.rules if "emoji-searchbar" in s},
            {searchbar},
        )
        self.assertEqual(
            {s for s in self.rules if "emoji-toolbar" in s},
            {toolbar},
        )
        # Both strips sit beside the landed statusbar band group, ahead of
        # the landed path-bar group.
        for selector in (searchbar, toolbar):
            with self.subTest(selector=selector):
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("statusbar"),
                )
                self.assertLess(
                    self.selectors.index(selector),
                    self.selectors.index(
                        "pathbar > scrolledwindow > viewport > box > button"
                    ),
                )

    def test_emoji_completion_row_corners(self):
        expected = {"emoji-completion-row"}
        self.assertEqual(
            {selector for selector in self.rules if "emoji-completion-row" in selector},
            expected,
        )
        self.assert_square_corner("emoji-completion-row")

    def test_emoji_picker_cell_corners(self):
        expected = {
            "popover.emoji-picker emoji",
            # The undershoot mirrors name the same picker substring.
            "popover.emoji-picker scrolledwindow.view:not(.undershoot-top) > undershoot.top",
            "popover.emoji-picker window.print:not(.ssd-frame) "
            "scrolledwindow.dialog-action-box:not(.undershoot-top) > undershoot.top",
            "window.print:not(.ssd-frame) popover.emoji-picker "
            "scrolledwindow.dialog-action-box:not(.undershoot-top) > undershoot.top",
            "popover.emoji-picker scrolledwindow.view:not(.undershoot-bottom) > undershoot.bottom",
            "popover.emoji-picker window.print:not(.ssd-frame) "
            "scrolledwindow.dialog-action-box:not(.undershoot-bottom) > undershoot.bottom",
            "window.print:not(.ssd-frame) popover.emoji-picker "
            "scrolledwindow.dialog-action-box:not(.undershoot-bottom) > undershoot.bottom",
        }
        self.assertEqual(
            {selector for selector in self.rules if "emoji-picker" in selector},
            expected,
        )
        self.assert_square_corner("popover.emoji-picker emoji")

    def test_emoji_section_button_corners(self):
        """Pin the restated emoji picker's section-button radius arm.

        No collected reference screenshot shows an emoji picker's section
        row, so the sheet restates stock's 34px-minimum section-button arm
        byte-equal with exactly the zero radius: the landed emoji-section
        record squares the picker's emoji-completion-row corners and owns
        only this button's focus outline, so stock keeps this button's own
        face round today.
        """
        selector = (
            "button.emoji-section.image-button:not(.raised):not(.suggested-action)"
            ":not(.destructive-action):not(.opaque)"
        )
        self.assert_rule(selector, {"border-radius": "0"})
        self.assertEqual(self.selectors.count(selector), 1)
        self.assert_matches_frame(selector, "border-radius")



if __name__ == "__main__":
    unittest.main()
