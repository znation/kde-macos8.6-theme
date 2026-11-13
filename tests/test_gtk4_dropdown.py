"""GTK 4 dropdown declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import COMBO_ARROW, ETCH_DARK, ROW_SELECTED, WHITE


class TestGtk4Dropdown(Gtk4SheetRuleCases, unittest.TestCase):
    def test_dropdown_searchbar_rim(self):
        # A dropdown's or combobox's searchable list popover draws the
        # search strip's own stock rim beneath the band edge the strip's
        # inner search box paints; the existing band group answers the inner
        # box, so this rim restates the strip itself with the existing etched
        # band edge.
        expected = {
            "border-bottom": f"1px solid {ETCH_DARK}",
            "box-shadow": f"inset 0 -1px {WHITE}",
        }
        for selector in (
            "dropdown popover .dropdown-searchbar",
            "combobox popover .dropdown-searchbar",
        ):
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, expected)
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("actionbar > revealer > box"),
                )
                self.assertLess(
                    self.selectors.index(selector),
                    self.selectors.index("statusbar"),
                )
                for prop in expected:
                    self.assertEqual(
                        self.rules[selector][prop],
                        self.rules["infobar > revealer > box"][prop],
                    )
        # The existing scroll-edge spellings end with undershoot.top /
        # undershoot.bottom and stay out of this suffix family.
        self.assertEqual(
            {s for s in self.rules if s.endswith("dropdown-searchbar")},
            {
                "dropdown popover .dropdown-searchbar",
                "combobox popover .dropdown-searchbar",
            },
        )
        # The strip's arm inventory must not grow a .combo-searchbar rule:
        # stock's margin arm and the existing undershoot twins (which contain
        # the token but end with an undershoot suffix) stay the only ones.
        self.assertEqual(
            {s for s in self.rules if s.endswith("combo-searchbar")},
            set(),
        )

    def test_dropdown_list_rows(self):
        """Open dropdown and combobox popover lists use the existing row recipes."""
        padding_spellings = (
            "dropdown popover listview > row.activatable",
            "combobox popover listview > row.activatable",
        )
        selected_spellings = (
            "dropdown popover listview > row.activatable:selected",
            "dropdown popover listview > row.activatable:selected:hover",
            "combobox popover listview > row.activatable:selected",
            "combobox popover listview > row.activatable:selected:hover",
        )
        backlog_order = self.selectors.index("columnview.view:selected:backdrop")
        separator_order = self.selectors.index("listview.horizontal row.separator")
        for selector, expected_rule in (
            [(selector, {"padding": "2px"}) for selector in padding_spellings]
            + [(selector, ROW_SELECTED) for selector in selected_spellings]
        ):
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, expected_rule)
                self.assertGreater(self.selectors.index(selector), backlog_order)
                self.assertLess(self.selectors.index(selector), separator_order)
        # Exactly the stocked dropdown twin spellings exist and nothing else:
        # no existing rule elsewhere in the sheet names a popover listview, so the
        # family scan kills renamed and stray variants.
        self.assertEqual(
            {selector for selector in self.rules if "popover listview" in selector},
            set(padding_spellings) | set(selected_spellings),
        )
        self.assertEqual(
            {selector for selector in self.rules
             if selector.endswith("popover listview > row.activatable")},
            set(padding_spellings),
        )

    def test_dropdown_arrow(self):
        self.assert_rule("dropdown arrow", COMBO_ARROW)


if __name__ == "__main__":
    unittest.main()
