"""Validate the GTK 3 Platinum sheet's scrollbar band.

This module owns the scrollbar slice of ``tests/test_gtk_theme.py``'s
split: the bar band and its overlay and ordinary thumbs, the overshoot
glows the stock toolkit repaints, the steppers, and the junction box. The
stepper box face and thumb minimums pin the reference screenshot's own
scroll bar, so the reference screenshot mixin and its keys live with them.
"""

import unittest
from pathlib import Path

from support.desktoptheme_paths import SETUP_MAX_ROWS, SETUP_REFERENCE
from support import gtk_css
from support.gtk_css import parse_css
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    RAISED_BEVEL,
    SCROLLBAR_STEPPER,
    SCROLLBAR_STEPPER_ACTIVE,
    SCROLLBAR_STEPPER_ARROWS,
)
from support.platinum_palette import (
    BLACK,
    FACE,
    INACTIVE_OUTLINE,
    TROUGH,
    hex_colour,
)
from support.reference_image import ReferenceScreenshotMixin
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"


class TestGtkThemeScrollbars(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS



    def test_scrollbar(self):
        self.assert_rule(
            "scrollbar",
            {
                "background-color": TROUGH,
                "border": f"1px solid {BLACK}",
                "padding": "0",
            },
        )
        self.assert_rule(
            "scrollbar slider",
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": RAISED_BEVEL,
            },
        )

    def test_scrollbar_steppers(self):
        self.assert_rule(
            "scrollbar:not(.overlay-indicator)",
            {
                "-gtkscrollbar-has-backward-stepper": "true",
                "-gtkscrollbar-has-forward-stepper": "true",
            },
        )
        self.assert_rule(
            "scrollbar.overlay-indicator",
            {
                "-gtkscrollbar-has-backward-stepper": "false",
                "-gtkscrollbar-has-forward-stepper": "false",
            },
        )
        self.assert_rule("scrollbar button", SCROLLBAR_STEPPER)
        self.assert_rule("scrollbar button:hover", {"background-color": TROUGH})
        self.assert_rule("scrollbar button:active", SCROLLBAR_STEPPER_ACTIVE)
        for selector, expected in SCROLLBAR_STEPPER_ARROWS.items():
            with self.subTest(selector=selector):
                self.assert_rule(selector, expected)

    def test_scrollbar_thumb_state_faces(self):
        """The thumb keeps the existing face through hover, drag and disabled.

        Stock repaints the thumb in three states whose arms each carry more
        pseudo-classes than the existing bare group, so each restated rule
        spells its stock twin byte-equal and wins the equal-specificity tie
        by later user-sheet source order, declaring only the existing face.
        """
        self.assert_rule_group(
            {
                "scrollbar slider:hover": {"background-color": FACE},
                "scrollbar slider:hover:active": {"background-color": FACE},
                "scrollbar slider:disabled": {"background-color": FACE},
            }
        )
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("scrollbar slider")
                and (":hover" in s or ":disabled" in s)
            },
            {
                "scrollbar slider:hover",
                "scrollbar slider:hover:active",
                "scrollbar slider:disabled",
            },
        )
        self.assertGreater(
            self.selectors.index("scrollbar slider:hover"),
            self.selectors.index("scrollbar slider"),
        )
        self.assertLess(
            self.selectors.index("scrollbar slider:hover"),
            self.selectors.index("scrollbar:not(.overlay-indicator) slider"),
        )

    def test_overlay_scrollbar_thumb_minimum(self):
        self.assert_rule(
            "scrollbar.overlay-indicator slider",
            {"min-width": "12px", "min-height": "12px"},
        )

    def test_ordinary_scrollbar_thumb_minimum(self):
        self.assert_rule(
            "scrollbar:not(.overlay-indicator) slider",
            {"min-width": "12px", "min-height": "12px"},
        )

    def test_overshoot_glows_cleared(self):
        """The stock radial over-scroll glows render nothing in normal state.

        The stock GTK 3 resource paints two radial ``-gtk-gradient`` images
        on each of the four ``scrolledwindow overshoot`` nodes; no collected
        reference screenshot shows a GTK over-scroll glow, and Platinum
        scroll fields run flat to the sunken frame.
        """
        for selector in (
            "scrolledwindow overshoot.top",
            "scrolledwindow overshoot.bottom",
            "scrolledwindow overshoot.left",
            "scrolledwindow overshoot.right",
        ):
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"background-image": "none"})

    def test_overshoot_backdrop_glows_cleared(self):
        """The stock radial over-scroll glows stay cleared in backdrop."""
        for selector in (
            "scrolledwindow overshoot.top:backdrop",
            "scrolledwindow overshoot.bottom:backdrop",
            "scrolledwindow overshoot.left:backdrop",
            "scrolledwindow overshoot.right:backdrop",
        ):
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"background-image": "none"})

    def test_junction_shares_the_scrollbar_band(self):
        """The scrollbar corner paints the flat trough band, nothing else.

        The stock GTK 3 resource fills the junction node where a scrolled
        window's two scrollbars meet with its own grey and draws a trough
        line through one edge of the band; no collected reference screenshot
        shows a GTK scrollbar corner, and the junction reads as the same
        flat band the existing scrollbar rule pins. The stock left-to-right
        mirror arm only re-slices the now-empty border-image, so the sheet
        must stop at the two rules and carry no such arm.
        """
        self.assertEqual(
            self.rules["scrolledwindow junction"],
            {
                "background-color": TROUGH,
                "border-color": "transparent",
                "border-image": "none",
            },
        )
        self.assertNotIn("junction:dir", self.css)

    def test_scrollbar_backdrop_faces(self):
        """The scrollbar band and thumb keep the existing faces in backdrop.

        The stock toolkit resource repaints a scrollbar's band and thumb
        through its own backdrop arms in an unfocused window; no collected
        reference screenshot shows a GTK scrollbar in an unfocused window,
        so the sheet restates the existing TROUGH band and FACE thumb through
        byte-equal stock twins and erases the bare bar's and thumb's 300ms
        repaint ease with the existing no-transition policy.
        """
        self.assert_rule_group(
            {
                "scrollbar:backdrop": {
                    "background-color": TROUGH,
                    "border-color": BLACK,
                    "transition": "none",
                },
                "scrollbar slider:backdrop": {"background-color": FACE},
            },
        )
        self.assert_rule("scrollbar", {"transition": "none"})
        self.assert_rule("scrollbar slider", {"transition": "none"})
        # The parser merges same-spelling groups into one declared rule, so
        # a sweep catches copy or variant spellings instead: exactly these
        # two scrollbar-rooted backdrop spellings exist in the sheet and none
        # carries foreign paint (the bare `scrollbar` selectors above use
        # assert_rule because the parser merges their existing group with the
        # transition restate; the slider spelling starts with "scrollbar"
        # too, so one combined sweep covers both root and descendant roots).
        self.assertEqual(
            {
                s
                for s in self.selectors
                if "scrollbar" in s and ":backdrop" in s
            },
            {"scrollbar:backdrop", "scrollbar slider:backdrop"},
        )
        # Both new groups sit at the sheet tail, after the junction's
        # backdrop restate and the existing places-view link-button arm.
        self.assertLess(
            self.selectors.index("scrolledwindow junction:backdrop"),
            self.selectors.index("scrollbar:backdrop"),
        )
        self.assertLess(
            self.selectors.index("infobar > revealer > box button:link"),
            self.selectors.index("scrollbar:backdrop"),
        )

    def test_junction_backdrop_shares_the_scrollbar_band(self):
        """The scrollbar corner stays the flat trough band in backdrop."""
        self.assertEqual(
            self.rules["scrolledwindow junction:backdrop"],
            {
                "background-color": TROUGH,
                "border-color": "transparent",
                "border-image": "none",
            },
        )


class TestScrollbarStepperReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The stepper box face and divider must match the reference screenshot.

    The installer CD window's left stepper is a 14x14 #EEEEEE face between the
    bar's 1px #000000 border (x=23, y=462 and y=477) and a 1px #555555
    divider at x=38, so the visible box is 16x16. ``TestGtkThemeScrollbars`` pins the
    sheet to ``SCROLLBAR_STEPPER`` and its direction rules, so this ties that
    14px face and divider to a screenshot.
    """

    REFERENCE = SETUP_REFERENCE
    MAX_ROWS = SETUP_MAX_ROWS

    def test_stepper_box_matches_reference(self):
        face_left, face_right = 24, 37
        face_top, face_bottom = 463, 476
        for x, y in ((face_left, face_top), (face_right, face_bottom)):
            with self.subTest(x=x, y=y):
                self.assertEqual(hex_colour(self.pixel(x, y)), TROUGH)
        for x, y in ((23, 468), (30, 462), (30, 477)):
            with self.subTest(x=x, y=y):
                self.assertEqual(hex_colour(self.pixel(x, y)), BLACK)
        self.assertEqual(hex_colour(self.pixel(38, 468)), INACTIVE_OUTLINE)
        face_width = face_right - face_left + 1
        face_height = face_bottom - face_top + 1
        self.assertEqual(face_width, 14)
        self.assertEqual(face_height, 14)
        self.assertEqual(SCROLLBAR_STEPPER["min-width"], f"{face_width}px")
        self.assertEqual(SCROLLBAR_STEPPER["min-height"], f"{face_height}px")
        self.assertEqual(
            SCROLLBAR_STEPPER_ARROWS["scrollbar.horizontal button.up"][
                "border-right"
            ],
            f"1px solid {INACTIVE_OUTLINE}",
        )

    def test_overlay_thumb_minimum_matches_reference(self):
        top, bottom = 462, 477
        for y in (top, bottom):
            self.assertEqual(hex_colour(self.pixel(200, y)), BLACK)
        for y in range(top + 1, bottom):
            with self.subTest(y=y):
                self.assertEqual(hex_colour(self.pixel(200, y)), TROUGH)
        band = bottom - top + 1
        css = gtk_css.read_theme_text(CSS)
        _, rules, _ = parse_css(css, source=str(CSS.relative_to(ROOT)))
        self.assertEqual(rules["scrollbar"]["border"], f"1px solid {BLACK}")
        self.assertEqual(rules["scrollbar slider"]["border"], f"1px solid {BLACK}")
        for dimension in ("min-width", "min-height"):
            with self.subTest(dimension=dimension):
                self.assertEqual(
                    rules["scrollbar.overlay-indicator slider"][dimension],
                    f"{band - 4}px",
                )

    def test_ordinary_thumb_minimum_matches_reference(self):
        top, bottom = 462, 477
        for y in (top, bottom):
            self.assertEqual(hex_colour(self.pixel(200, y)), BLACK)
        for y in range(top + 1, bottom):
            with self.subTest(y=y):
                self.assertEqual(hex_colour(self.pixel(200, y)), TROUGH)
        band = bottom - top + 1
        css = gtk_css.read_theme_text(CSS)
        _, rules, _ = parse_css(css, source=str(CSS.relative_to(ROOT)))
        self.assertEqual(rules["scrollbar"]["border"], f"1px solid {BLACK}")
        self.assertEqual(rules["scrollbar slider"]["border"], f"1px solid {BLACK}")
        for dimension in ("min-width", "min-height"):
            with self.subTest(dimension=dimension):
                self.assertEqual(
                    rules["scrollbar:not(.overlay-indicator) slider"][dimension],
                    f"{band - 4}px",
                )


if __name__ == "__main__":
    unittest.main()
