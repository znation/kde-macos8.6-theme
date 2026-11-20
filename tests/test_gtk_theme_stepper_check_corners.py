"""Validate GTK 3 vertical spin-button stepper and content-view check corners.

The vertical stepper end halves and the content-view tile-check state faces
square their corners and keep the existing check face; the views module
keeps the rest of the GTK 3 views and dialogs declarations.
"""

import unittest
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    CHECK_GLYPH,
    SELECTION_CHECK_STATES,
    TILE_CHECK_FACE,
)
from support.repo_root import ROOT


class TestGtkThemeStepperCheckCorners(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_vertical_stepper_and_content_view_check_corners(self):
        """Pin the vertical steppers and content-view check faces square.

        The two appended stepper groups rest stock's vertical stepper
        end halves at zero and restate stock's per-stepper border-style
        halves so each field/stepper join draws one 1px line, and the
        eight content-view check state groups rest the eight
        selection-check state faces at zero and
        take the existing check face under every state: the
        tile-check face record extends the existing radius-only groups
        in place, so the scanned parser reads the merged dictionaries
        in this suite, and the suite's parser leaves each spelling
        once in the selector list -- repeating the spellings in new
        blocks would break the once-per-selector pin. Nothing else in
        the sheet names any of the three tokens.
        """
        stepper_up = "spinbutton.vertical button.up"
        stepper_down = "spinbutton.vertical button.down"
        states = SELECTION_CHECK_STATES
        check_spellings = (
            *[f".view.content-view.check{state}:not(list)" for state in states],
            *[f"iconview.content-view.check{state}:not(list)" for state in states],
            *[f".content-view:not(list) check{state}" for state in states],
        )
        spellings = (stepper_up, stepper_down) + check_spellings
        # The docstring comment above the groups names both probes and
        # the face source, and the realized dictionaries merge this
        # record's zero radius with the face record's existing
        # check face under every state: the four unchecked spellings
        # carry the raised etched face, the four checked ones the same
        # five declarations under the shipped checkmark glyph.
        tile_face = dict(TILE_CHECK_FACE)
        tile_rules = {}
        for state_index in range(len(states)):
            declarations = (
                tile_face
                if state_index < 4
                else {**tile_face, **CHECK_GLYPH}
            )
            for member_index in range(3):
                tile_rules[
                    check_spellings[member_index * len(states) + state_index]
                ] = dict(declarations)
        self.assert_rule_group(
            {
                stepper_up: {
                    "border-radius": "0",
                    "border-style": "solid solid none solid",
                },
                stepper_down: {
                    "border-radius": "0",
                    "border-style": "none solid solid solid",
                },
                **tile_rules,
            }
        )
        # The three tokens have no existing or unrelated neighbours: the
        # existing `.content-view` rules name no check node or `:not(list)`
        # guard and the existing `.osd spinbutton.vertical button:first-child`
        # groups name the stacked OSD twins only, so the scan kills renamed
        # variants, a folded or dropped `:not(list)` guard and stray
        # neighbours. The class-armed members take the `content-view.check`
        # token; the bare compound takes the `.content-view:not(list)`
        # token, which no other rule carries.
        view_and_iconview = {
            s
            for s in self.rules
            if "content-view.check" in s
        }
        self.assertEqual(
            view_and_iconview,
            set(check_spellings[:16]),
        )
        bare_compound = {
            s for s in self.rules if ".content-view:not(list)" in s
        }
        self.assertEqual(bare_compound, set(check_spellings[16:]))
        self.assertEqual(view_and_iconview | bare_compound, set(check_spellings))
        # One sweep further: every rule naming both tokens is one of the
        # twenty-four tile spellings, so the face record leaves no stray
        # check-and-content-view neighbour and the existing `.content-view`
        # field, hover and rubberband arms (which name no check node)
        # stay outside the family.
        self.assertEqual(
            {s for s in self.rules if "check" in s and "content-view" in s},
            set(check_spellings),
        )
        self.assertEqual(
            {s for s in self.rules if "spinbutton.vertical button.up" in s},
            {stepper_up},
        )
        self.assertEqual(
            {s for s in self.rules if "spinbutton.vertical button.down" in s},
            {stepper_down},
        )
        # Source order: every appended spelling sits after the existing bare
        # `check` recipe and the existing `popover.emoji-picker .emoji
        # :hover` tail group, so the byte-equal stock twins win the
        # equal-specificity ties under the lower-sheet reading of how the
        # toolkit resource competes.
        for selector in spellings:
            with self.subTest(selector=selector, after="check"):
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("check"),
                )
            with self.subTest(selector=selector, after="emoji"):
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("popover.emoji-picker .emoji :hover"),
                )


if __name__ == "__main__":
    unittest.main()
