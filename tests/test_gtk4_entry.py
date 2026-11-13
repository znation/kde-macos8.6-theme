"""GTK 4 entry declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import ENTRY_PROGRESS_GTK4
from support.platinum_palette import BLACK


class TestGtk4Entry(Gtk4SheetRuleCases, unittest.TestCase):
    def test_entry_focus_outline_color(self):
        self.assert_scale_focus_outline("entry:focus-within")

    def test_entry_focus_transition(self):
        self.assert_scale_slider_transition("entry")

    def test_entry_colour_classes(self):
        # The landed entry policy takes no colour class: the sheet restates
        # the four stock error/warning colour-class arms with byte-equal
        # twins declaring the landed black text, the immediate motion
        # policy and the black focus outline, so an entry carrying the
        # `error` or `warning` class paints the raised field recipe instead
        # of stock's red or orange.
        bases = (
            "spinbutton.vertical > text.error",
            "spinbutton.error:not(.vertical)",
            "entry.error",
            "spinbutton.vertical > text.warning",
            "spinbutton.warning:not(.vertical)",
            "entry.warning",
        )
        focus = (
            "spinbutton.vertical > text.error:focus-within",
            "spinbutton.error:focus-within:not(.vertical)",
            "entry.error:focus-within",
            "spinbutton.vertical > text.warning:focus-within",
            "spinbutton.warning:focus-within:not(.vertical)",
            "entry.warning:focus-within",
        )
        for selector in bases:
            self.assert_exact_rule_once(selector, {"color": BLACK, "transition": "none"})
        for selector in focus:
            self.assert_exact_rule_once(selector, {"outline-color": BLACK})
        # No other error or warning selector exists in the sheet: the
        # family scan kills renamed, dropped and stray class spellings
        # alike (including the stock '> selection' arms, out of scope).
        # The landed `label.error` label colour-class twins share the
        # `.error` spelling, so the scan covers them too.
        self.assertEqual(
            {s for s in self.rules if ".error" in s or ".warning" in s},
            set(bases + focus) | {"label.error", "label.error:disabled"},
        )

    def test_entry_image_inks(self):
        # The landed entry recipe never names the icon child GTK embeds
        # inside entries and spin buttons (the magnifier, clear-button and
        # stepper glyphs), so two toolkit resources paint their own look on
        # them. The sheet tail restates the ten stock arms: the embedded
        # icons take the landed field's black ink at full opacity in every
        # state (the landed button:hover erase precedent), and the two
        # margin twins keep stock's own 6px values byte-equal, so later
        # user-sheet source order wins every equal-specificity tie under
        # either cascade reading.
        colour = (
            "spinbutton.vertical > text > image",
            "spinbutton.vertical > text > image:hover",
            "spinbutton.vertical > text > image:active",
            "spinbutton:not(.vertical) > image",
            "spinbutton:not(.vertical) > image:hover",
            "spinbutton:not(.vertical) > image:active",
        )
        for selector in colour:
            self.assert_rule(selector, {"color": BLACK})
            self.assertEqual(self.selectors.count(selector), 1, selector)
        # The bare `entry > image:hover`/`.:active` twins arise in both
        # resources' resources' grouped hover and active arms, so each
        # merges the theme resource's colour twin and the base stylesheet
        # resource's opacity twin, like `entry > image` itself.
        for selector in ("entry > image:hover", "entry > image:active"):
            self.assert_rule(selector, {"color": BLACK, "opacity": "1"})
            self.assertEqual(self.selectors.count(selector), 2, selector)
        opacity = (
            "spinbutton > image",
            "spinbutton > image:hover",
            "spinbutton > image:active",
        )
        for selector in opacity:
            self.assert_rule(selector, {"opacity": "1"})
            self.assertEqual(self.selectors.count(selector), 1, selector)
        # The bare `entry > image` spelling merges both resources'
        # declarations on one key: the theme resource's colour twin and
        # the base stylesheet resource's opacity twin.
        self.assert_rule("entry > image", {"color": BLACK, "opacity": "1"})
        self.assertEqual(self.selectors.count("entry > image"), 2)
        for selector, side in (
            ("spinbutton.vertical > text > image.left", "margin-right"),
            ("spinbutton.vertical > text > image.right", "margin-left"),
            ("spinbutton:not(.vertical) > image.left", "margin-right"),
            ("spinbutton:not(.vertical) > image.right", "margin-left"),
            ("spinbutton > image.left", "margin-right"),
            ("spinbutton > image.right", "margin-left"),
        ):
            self.assert_rule(selector, {side: "6px"})
            self.assertEqual(self.selectors.count(selector), 1, selector)
        # The `entry > image.left`/`.right` twins merge the identical 6px
        # margin restated once per resource on each key.
        for selector, side in (
            ("entry > image.left", "margin-right"),
            ("entry > image.right", "margin-left"),
        ):
            self.assert_rule(selector, {side: "6px"})
            self.assertEqual(self.selectors.count(selector), 2, selector)
        self.assertEqual(
            {s for s in self.rules if s.startswith("entry > image")}
            | {
                s
                for s in self.rules
                if s.startswith("spinbutton") and "> image" in s
            },
            set(colour)
            | {
                "entry > image:hover",
                "entry > image:active",
            }
            | set(opacity)
            | {
                "spinbutton.vertical > text > image.left",
                "spinbutton.vertical > text > image.right",
                "spinbutton:not(.vertical) > image.left",
                "spinbutton:not(.vertical) > image.right",
                "spinbutton > image.left",
                "spinbutton > image.right",
                "entry > image",
                "entry > image.left",
                "entry > image.right",
            },
        )
        self.assert_rule_after(
            "spinbutton.vertical > text > image.left",
            "entry, spinbutton:not(.vertical), spinbutton.vertical > text {",
        )

    def test_entry_progress(self):
        self.assert_rule("entry > progress > trough > progress", ENTRY_PROGRESS_GTK4)
        self.assert_rule("entry > progress > trough", {"min-height": "2px"})
        self.assert_rule("entry > progress", {"margin-bottom": "1px"})



if __name__ == "__main__":
    unittest.main()
