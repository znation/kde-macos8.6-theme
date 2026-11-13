"""GTK 4 treeview declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import ENTRY_FIELD, MIXED_GLYPH, RADIO_GLYPH
from support.platinum_palette import BLACK, GREY, SELECTION, TROUGH, WHITE


class TestGtk4Treeview(Gtk4SheetRuleCases, unittest.TestCase):
    def test_treeview_selected_check_radio_faces(self):
        """Pin the selected-row check and radio restated off the existing faces.

        The 2026-11-06 sheet-tail record answers the Default-light
        resource's four treeview-class-armed selected-row arms (probed
        verbatim in the sheet comment and docs/invariants.md) per-property:
        the colour arm's ink and border return to the existing check recipe's
        hard black, the checked and indeterminate glyph arms swap the
        toolkit's recoloured symbolic dot and dash for the existing black-ink
        shipped assets, and stock's radius and 14px-size arm restates
        nothing. No merge here adds a face declaration beyond the two
        answers per member spelling.
        """
        seal = {"color": BLACK, "border-color": BLACK}
        expected = {
            "treeview.view check:selected:focus": dict(seal),
            "treeview.view check:selected": dict(seal),
            "treeview.view radio:selected:focus": dict(seal),
            "treeview.view radio:selected": dict(seal),
            "treeview.view radio:checked:selected": dict(RADIO_GLYPH),
            "treeview.view radio:indeterminate:selected": dict(MIXED_GLYPH),
        }
        self.assert_rule_group(expected)
        # The family sweep: every rule carrying one of the two
        # treeview-class-armed control tokens is one of the six spellings
        # above, so no stock arm of either group survives unrepresented.
        self.assertEqual(
            {
                s
                for s in self.rules
                if "treeview.view check" in s or "treeview.view radio" in s
            },
            set(expected),
        )
        # Source order: each restated spelling lands after the existing
        # plain-state `radio:checked` glyph rule's parsed position.
        for selector in expected:
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("radio:checked"),
                selector,
            )

    def test_treeview_entry_fields(self):
        # The existing entry recipe governs the stock treeview-embedded entry
        # family too: the sheet restates the three stock grouped arms with
        # byte-equal twins declaring ENTRY_FIELD, a black focus border and
        # the existing no-motion policy, so a resting, focused, flat or
        # plain editable cell paints the raised field instead of stock's
        # blue focus border and stock's color/background focus transition.
        fields = ("treeview entry.flat", "treeview entry")
        focus = (
            "treeview entry.flat:focus-within",
            "treeview entry:focus-within",
        )
        motion = (
            "treeview entry:focus-within:dir(rtl)",
            "treeview entry:focus-within:dir(ltr)",
        )
        for selector in fields:
            self.assert_exact_rule_once(selector, ENTRY_FIELD)
        for selector in focus:
            self.assert_exact_rule_once(selector, {"border-color": BLACK})
        for selector in motion:
            self.assert_exact_rule_once(selector, {"transition": "none"})
        # No other treeview entry spelling exists in the sheet: the family
        # scan kills renamed and stray variants alike.
        self.assertEqual(
            {s for s in self.rules if s.startswith("treeview entry")},
            set(fields + focus + motion),
        )

    def test_treeview_progress_cell_faces(self):
        """A view row's progress cell keeps the existing meter faces."""
        selected_cell = (
            "columnview.view.progressbar:selected:focus",
            "columnview.view.progressbar:selected",
            "treeview.view.progressbar:selected:focus",
            "treeview.view.progressbar:selected",
        )
        selected_backdrop_cell = (
            "columnview.view.progressbar:selected:focus:backdrop",
            "columnview.view.progressbar:selected:backdrop",
            "treeview.view.progressbar:selected:focus:backdrop",
            "treeview.view.progressbar:selected:backdrop",
        )
        selected_cell_trough = (
            "columnview.view.trough:selected:focus",
            "columnview.view.trough:selected",
            "treeview.view.trough:selected:focus",
            "treeview.view.trough:selected",
        )
        expected = {
            "columnview.view.progressbar": {
                "color": BLACK,
                "background-color": SELECTION,
                "background-image": "none",
                "box-shadow": "none",
            },
            "treeview.view.progressbar": {
                "color": BLACK,
                "background-color": SELECTION,
                "background-image": "none",
                "box-shadow": "none",
            },
            "columnview.view.trough": {
                "background-color": TROUGH,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": f"inset 1px 1px {GREY}",
            },
            "treeview.view.trough": {
                "background-color": TROUGH,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": f"inset 1px 1px {GREY}",
            },
        }
        for selector in selected_cell + selected_backdrop_cell:
            expected[selector] = {
                "color": BLACK,
                "background-color": WHITE,
                "background-image": "none",
                "box-shadow": "none",
            }
        for selector in selected_cell_trough:
            expected[selector] = {"background-color": TROUGH}
        self.assert_rule_group(expected)
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith(("columnview.view", "treeview.view"))
                and ("progressbar" in s or "trough" in s)
            },
            set(expected),
        )
        self.assertNotIn("min-height", self.rules["columnview.view.trough"])
        self.assertNotIn("min-height", self.rules["treeview.view.trough"])
        self.assertNotIn("min-width", self.rules["columnview.view.trough"])
        self.assertNotIn("min-width", self.rules["treeview.view.trough"])
        self.assertGreater(
            self.selectors.index("columnview.view.progressbar"),
            self.selectors.index("progressbar"),
        )
        self.assertLess(
            self.selectors.index("treeview.view.trough"),
            self.selectors.index("progressbar > trough"),
        )


if __name__ == "__main__":
    unittest.main()
