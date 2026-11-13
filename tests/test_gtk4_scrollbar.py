"""GTK 4 scrollbar declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import RAISED_BEVEL
from support.platinum_palette import BLACK, FACE, TROUGH


class TestGtk4Scrollbar(Gtk4SheetRuleCases, unittest.TestCase):
    def test_scrollbar(self):
        self.assert_rule(
            "scrollbar > range > trough",
            {
                "background-color": TROUGH,
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
            },
        )
        self.assert_rule(
            "scrollbar > range > trough > slider",
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "margin": "0",
                "min-width": "12px",
                "min-height": "12px",
                "box-shadow": RAISED_BEVEL,
            },
        )

    def test_scrollbar_ordinary_trough_margins(self):
        for selector in (
            "scrollbar.horizontal:not(.overlay-indicator) > range > trough",
            "scrollbar.vertical:not(.overlay-indicator) > range > trough",
        ):
            self.assert_rule(selector, {"margin": "0"})

    def test_scrollbar_overlay_trough_margins(self):
        for selector in (
            "scrollbar.overlay-indicator.horizontal.hovering > range > trough",
            "scrollbar.overlay-indicator.horizontal:not(.hovering) > range > trough",
            "scrollbar.overlay-indicator.vertical.hovering > range > trough",
            "scrollbar.overlay-indicator.vertical:not(.hovering) > range > trough",
        ):
            self.assert_rule(selector, {"margin": "0"})

    def test_scrollbar_overlay_hover_trough_face(self):
        base_face = self.rules["scrollbar > range > trough"]["background-color"]
        self.assertEqual(base_face, TROUGH)
        self.assert_rule(
            "scrollbar.overlay-indicator.hovering > range > trough",
            {"background-color": base_face},
        )

    def test_scrollbar_overlay_thumb_outline(self):
        self.assert_rule(
            "scrollbar.overlay-indicator > range > trough > slider",
            {"outline": "none"},
        )

    def test_scrollbar_overlay_thumb_breadth(self):
        slider = self.rules["scrollbar > range > trough > slider"]
        for selector in (
            "scrollbar.overlay-indicator.horizontal.hovering > range > trough > slider",
            "scrollbar.overlay-indicator.horizontal:not(.hovering) > range > trough > slider",
        ):
            self.assert_rule(selector, {"min-height": slider["min-height"]})
        for selector in (
            "scrollbar.overlay-indicator.vertical.hovering > range > trough > slider",
            "scrollbar.overlay-indicator.vertical:not(.hovering) > range > trough > slider",
        ):
            self.assert_rule(selector, {"min-width": slider["min-width"]})

    def test_scrollbar_disabled_thumb_opacity(self):
        self.assert_rule(
            "scrollbar > range > trough > slider:disabled",
            {"opacity": "1"},
        )

    def test_scrollbar_fine_tune_thumb_face(self):
        base_face = self.rules["scrollbar > range > trough > slider"]["background-color"]
        self.assertEqual(base_face, FACE)
        for selector in (
            "scrollbar > range.fine-tune > trough > slider",
            "scrollbar > range.fine-tune > trough > slider:hover",
            "scrollbar > range.fine-tune > trough > slider:active",
        ):
            self.assert_rule(selector, {"background-color": base_face})

    def test_scrollbar_thumb_interaction_face(self):
        base_face = self.rules["scrollbar > range > trough > slider"]["background-color"]
        self.assertEqual(base_face, FACE)
        for selector in (
            "scrollbar > range > trough > slider:hover",
            "scrollbar > range > trough > slider:active",
        ):
            self.assert_rule(selector, {"background-color": base_face})

    def test_scrollbar_thumb_transition(self):
        self.assert_rule(
            "scrollbar > range > trough > slider",
            {"transition": "none"},
        )

    def test_scrollbar_trough_transition(self):
        self.assert_rule(
            "scrollbar > range > trough",
            {"transition": "none"},
        )


if __name__ == "__main__":
    unittest.main()
