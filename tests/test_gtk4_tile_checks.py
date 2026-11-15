"""GTK 4 content-view tile-check face checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import (
    CHECK,
    CHECK_GLYPH,
    MIXED_GLYPH,
    RADIO,
    RADIO_GLYPH,
    SELECTION_CHECK_STATES,
    TILE_CHECK_FACE,
    VIEW_BACKGROUND,
)
from support.platinum_palette import BLACK, FACE


class TestGtk4TileChecks(Gtk4SheetRuleCases, unittest.TestCase):
    def test_tile_check_faces(self):
        """Pin the eight 32px content-view tile-check state faces.

        The 2026-11-05 sheet-tail record restates the toolkit resource's
        eight class-armed comma triples (probed verbatim in the sheet
        comment and docs/invariants.md) with the existing check face under
        every state: the four unchecked spellings carry the raised
        etched face with the zero radius and hard black outline, the
        four checked ones the same under the shipped checkmark glyph.
        Stock's 32px geometry, margins, residual colour and 200ms
        transition and the unchecked none icon source stay inherited
        per-property (no declaration here), so this dictionary is the
        whole group.
        """
        states = SELECTION_CHECK_STATES
        class_armed = tuple(
            f"{head}{state}:not(list)"
            for state in states
            for head in (
                ".view.content-view.check",
                "iconview.content-view.check",
            )
        )
        tile_members = tuple(
            f".content-view .tile check{state}:not(list)" for state in states
        )
        unchecked = dict(TILE_CHECK_FACE)
        checked = {**unchecked, "-gtk-icon-source": CHECK_GLYPH["-gtk-icon-source"]}
        expected = {
            selector: dict(unchecked) for selector in class_armed + tile_members
        }
        for state in states[4:]:
            for head in (
                ".view.content-view.check",
                "iconview.content-view.check",
            ):
                expected[f"{head}{state}:not(list)"] = dict(checked)
            expected[f".content-view .tile check{state}:not(list)"] = dict(
                checked
            )
        self.assert_rule_group(expected)
        # The class-armed sweep: every rule carrying the content-view.check
        # token is one of the sixteen `.view`/`iconview` spellings, and the
        # `.tile check` token reaches exactly the eight third members.
        self.assertEqual(
            {s for s in self.rules if "content-view.check" in s},
            set(class_armed),
        )
        self.assertEqual(
            {s for s in self.rules if ".tile check" in s},
            set(tile_members),
        )
        # Provenance guards: the existing `.content-view` field and hover
        # arms, the existing element `check`/`radio` recipes, the four merged
        # checked and indeterminate glyph unions the plain-state record
        # pins and the merged zero-radius `check` key stay byte-equal, so
        # the tile record added no declaration to any existing key.
        self.assert_rule(".content-view", VIEW_BACKGROUND)
        self.assert_rule(".content-view:hover", {"-gtk-icon-filter": "none"})
        self.assert_rule("check", CHECK)
        self.assertEqual(self.selectors.count("check"), 2)
        self.assert_rule("radio", RADIO)
        check_face = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": CHECK["box-shadow"],
        }
        check_checked_face = {**check_face, "background-color": FACE}
        radio_face = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": "none",
        }
        self.assert_rule("check:checked", {**CHECK_GLYPH, **check_checked_face})
        self.assert_rule("radio:checked", {**RADIO_GLYPH, **radio_face})
        self.assert_rule(
            "check:indeterminate", {**MIXED_GLYPH, **check_checked_face}
        )
        self.assert_rule(
            "radio:indeterminate", {**MIXED_GLYPH, **radio_face}
        )


if __name__ == "__main__":
    unittest.main()
