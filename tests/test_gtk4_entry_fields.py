"""GTK 4 entry-field, spin-field, caps-lock and editable-label checks moved out
of ``test_gtk4_theme``.
"""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import ENTRY_FIELD, TEXT_SELECTION
from support.platinum_palette import BLACK


class TestGtk4EntryFields(Gtk4SheetRuleCases, unittest.TestCase):
    def test_spin_button_field(self):
        self.assert_spin_button_field(
            ("spinbutton:not(.vertical)", "spinbutton.vertical > text")
        )

    def test_flat_entry_fields(self):
        # The existing entry recipe governs the stock flat entry family: the
        # sheet restates the stock grouped transparent-face arm with one
        # byte-equal six-selector twin declaring ENTRY_FIELD, so a resting,
        # focused, backdrop or disabled flat entry (and a spin button's flat
        # field) paints the raised field instead of stock's transparency.
        selectors = (
            "spinbutton.vertical > text.flat",
            "spinbutton.flat:not(.vertical)",
            "entry.flat:focus-within",
            "entry.flat:backdrop",
            "entry.flat:disabled",
            "entry.flat",
        )
        for selector in selectors:
            self.assert_exact_rule_once(selector, ENTRY_FIELD)
        # No other flat entry or spinbutton spelling exists beyond the
        # treeview-embedded flat twins the treeview entry restatement adds:
        # the family scan kills renamed and stray variants alike. The stock
        # `.osd` stepper spellings carry `:not(.flat)` (a not-flat
        # exclusion, not a flat field); the existing OSD stepper record adds
        # them byte-equal to stock, so the scan holds them out.
        self.assertEqual(
            {
                s
                for s in self.rules
                if "flat" in s
                and ("entry" in s or "spinbutton" in s)
                and ":not(.flat)" not in s
            },
            set(selectors) | {"treeview entry.flat", "treeview entry.flat:focus-within"},
        )

    def test_spin_field_mirrors_the_etch_in_rtl(self):
        # GTK does not mirror box-shadow for text direction, so a horizontal
        # RTL spin field kept the existing etch's horizontal top arm only: the
        # existing :dir(rtl) stepper arms cover the etch's vertical arm at the
        # field's left edge, leaving the exposed right edge half-etched
        # where the LTR field shows the full L (measured 2026-11-11 in a
        # child render before the fix). The sheet mirrors the arm onto the
        # exposed edge — the existing GTK 3 spinbutton:dir(rtl) record — with
        # one plain mirror directly after the plain field rule and one twin
        # directly after each of the three existing `.osd` state groups, each
        # declaring exactly the mirrored arm. Each mirror out-ranks its
        # base group by one class (the `:dir(rtl)` pseudo-class), so the
        # win does not depend on source position; the focused and disabled
        # twins also out-rank the plain OSD mirror the same way. Excluded:
        # vertical spinbutton.vertical > text fields (no horizontal stepper
        # covers the arm), plain entry fields (no steppers) and the
        # treeview-embedded entry group (an entry, not a spin field); the
        # OSD record declares no :backdrop field twin, so none is mirrored.
        mirror = "inset -1px 1px #999999"
        plain = "spinbutton:dir(rtl):not(.vertical)"
        twins = (
            ".osd spinbutton:dir(rtl):not(.vertical)",
            ".osd spinbutton:dir(rtl):focus-within:not(.vertical)",
            ".osd spinbutton:dir(rtl):disabled:not(.vertical)",
        )
        for selector in (plain, *twins):
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, {"box-shadow": mirror})
        # Each mirror sits directly after its base group in the sheet text.
        self.assert_rule_after(
            "\nspinbutton:dir(rtl):not(.vertical) {",
            "entry, spinbutton:not(.vertical), spinbutton.vertical > text {",
        )
        self.assert_rule_after(
            ".osd spinbutton:dir(rtl):not(.vertical) {",
            ".osd spinbutton.vertical > text, .osd spinbutton:not(.vertical), .osd entry {",
        )
        self.assert_rule_after(
            ".osd spinbutton:dir(rtl):focus-within:not(.vertical) {",
            ".osd spinbutton.vertical > text:focus-within, "
            ".osd spinbutton:focus-within:not(.vertical), .osd entry:focus-within {",
        )
        self.assert_rule_after(
            ".osd spinbutton:dir(rtl):disabled:not(.vertical) {",
            ".osd spinbutton.vertical > text:disabled, "
            ".osd spinbutton:disabled:not(.vertical), .osd entry:disabled {",
        )
        # Token sweeps keyed on substrings no other existing selector
        # carries: the plain token matches the plain mirror and its OSD
        # twin (the twin is a superstring), the two state tokens match
        # exactly their own twin, so a dropped mirror, a lost twin, a
        # renamed spelling or a stray extra selector fails.
        self.assertEqual(
            {s for s in self.rules if "spinbutton:dir(rtl):not(.vertical)" in s},
            {plain, twins[0]},
        )
        self.assertEqual(
            {s for s in self.rules if ".osd spinbutton:dir(rtl):focus-within" in s},
            {twins[1]},
        )
        self.assertEqual(
            {s for s in self.rules if ".osd spinbutton:dir(rtl):disabled" in s},
            {twins[2]},
        )

    def test_caps_lock_indicator(self):
        # The existing entry recipe never names the `caps-lock-indicator`
        # image child GTK stacks inside a password entry, so the two toolkit
        # tiers paint their own look on it even though the existing `entry >
        # image` family reaches the node: each stock arm carries the extra
        # `password` classes that out-specify the existing element pair, so
        # the toolkit's tint and the base tier's 30% dim stay in force.
        # The sheet tail restates both stock arms byte-equal: the
        # indicator takes the existing field's black ink (the family's own
        # pinned source) at the existing button:hover erase precedent's full
        # strength, so later user-sheet source order wins every
        # equal-specificity tie under either cascade reading.
        for selector in (
            "spinbutton.vertical > text.password image.caps-lock-indicator",
            "spinbutton.password:not(.vertical) image.caps-lock-indicator",
        ):
            self.assert_rule(selector, {"color": BLACK})
            self.assertEqual(self.selectors.count(selector), 1, selector)
        self.assert_rule("spinbutton.password image.caps-lock-indicator", {"opacity": "1"})
        self.assertEqual(
            self.selectors.count("spinbutton.password image.caps-lock-indicator"),
            1,
        )
        # The `entry.password image.caps-lock-indicator` spelling merges
        # one declaration from both restated rules on one key, like the
        # existing `entry > image` merge keys: the colour rule's existing
        # black and the opacity rule's full strength, asserted with
        # occurrence count two.
        self.assert_rule(
            "entry.password image.caps-lock-indicator",
            {"color": BLACK, "opacity": "1"},
        )
        self.assertEqual(
            self.selectors.count("entry.password image.caps-lock-indicator"), 2
        )
        # No other selector names the token: the family sweep kills a
        # renamed, dropped or stray spelling, a second colour or opacity
        # rule, a hover or active twin, or a restored stock value alike.
        self.assertEqual(
            {s for s in self.rules if "caps-lock-indicator" in s},
            {
                "spinbutton.vertical > text.password image.caps-lock-indicator",
                "spinbutton.password:not(.vertical) image.caps-lock-indicator",
                "spinbutton.password image.caps-lock-indicator",
                "entry.password image.caps-lock-indicator",
            },
        )
        # The restated pair holds the entry-image family tail, not a
        # detached sheet head: the colour arm sits after the existing
        # margin twin that ends the family and its own comment group.
        self.assertGreater(
            self.selectors.index(
                "spinbutton.vertical > text.password image.caps-lock-indicator"
            ),
            self.selectors.index("spinbutton > image.right"),
        )

    def test_editable_label_cells(self):
        # The existing entry recipe governs the stock editable-label family:
        # the sheet restates the stock field arm and the four column-view
        # cell-editing arms with byte-equal twins declaring ENTRY_FIELD, the
        # existing focus-black outline and TEXT_SELECTION, so an editable
        # label and a column view's cell being edited paint the raised
        # field, the black focus ring and the existing selection fill instead
        # of stock's warm-grey border and blue accent tints.
        field = "editablelabel > stack > text"
        focus = (
            "columnview row:not(:selected) cell"
            " editablelabel:not(.editing):focus-within",
            "columnview row:not(:selected) cell"
            " editablelabel.editing:focus-within",
        )
        selection = (
            "columnview row:not(:selected) cell"
            " editablelabel.editing text selection",
            "columnview row:not(:selected) cell"
            " editablelabel.editing text selection:focus-within",
        )
        self.assert_exact_rule_once(field, ENTRY_FIELD)
        for selector in focus:
            self.assert_rule(selector, {"outline-color": BLACK})
            self.assert_exact_rule_once(selector, {"outline-color": BLACK})
        for selector in selection:
            self.assert_rule(selector, TEXT_SELECTION)
            self.assert_exact_rule_once(selector, TEXT_SELECTION)
        # No other editablelabel spelling exists beyond the existing selection
        # restatement and the five new spellings, and no other columnview row
        # spelling exists at all: the family scans kill renamed and stray
        # variants alike.
        self.assertEqual(
            {s for s in self.rules if "editablelabel" in s},
            {
                field,
                "editablelabel > stack > text > selection",
                "editablelabel > stack > text > selection:focus-within",
                *focus,
                *selection,
            },
        )
        self.assertEqual(
            {s for s in self.rules if s.startswith("columnview row")},
            set(focus + selection),
        )
        # The restatements sit between the existing selected-text groups and
        # the existing calendar disabled-selected day group: source order is
        # part of what lets the restatements govern the cell arms, which
        # outrank the existing editable-label selection twins by specificity.
        existing_tail = self.selectors.index(
            "editablelabel > stack > text > selection:focus-within"
        )
        calendar = self.selectors.index(
            "calendar > grid > label.day-number:disabled:selected"
        )
        for selector in (field, *focus, *selection):
            self.assertGreater(self.selectors.index(selector), existing_tail)
            self.assertGreater(calendar, self.selectors.index(selector))


if __name__ == "__main__":
    unittest.main()
