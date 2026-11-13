"""GTK 4 button declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import INVERTED_BUTTON_BEVEL
from support.platinum_palette import BLACK, FACE


class TestGtk4Button(Gtk4SheetRuleCases, unittest.TestCase):
    def test_button_focus_outline_color(self):
        self.assert_scale_focus_outline("button:focus:focus-visible")

    def test_button_focus_transition(self):
        self.assert_scale_slider_transition("button")

    def test_button_disabled_and_backdrop(self):
        self.assert_button_disabled_and_backdrop()

    def test_button_checked_hover_and_active(self):
        expected = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
        }
        for selector in ("button:checked:hover", "button:checked:active"):
            self.assert_rule(selector, expected)

    def test_button_hover_icon_filter(self):
        # No reference screenshot shows a hovered GTK push button; stock
        # brightens every icon inside one, so the tail arm clears the filter
        # while the existing `button:hover` face group stays the face source.
        self.assert_rule(
            "button:hover",
            {"background-color": FACE, "-gtk-icon-filter": "none"},
        )


if __name__ == "__main__":
    unittest.main()
