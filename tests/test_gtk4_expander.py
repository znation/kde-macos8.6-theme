"""GTK 4 expander declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases


class TestGtk4Expander(Gtk4SheetRuleCases, unittest.TestCase):
    def test_expander_arrows(self):
        self.assert_expander_arrows(
            ("treeview.view.expander", "expander"),
            ("treeview.view.expander:checked", "expander:checked"),
        )

    def test_rtl_collapsed_expander_arrows(self):
        selectors = (
            "treeview.view.expander:not(:checked):dir(rtl)",
            "expander:not(:checked):dir(rtl)",
        )
        for selector in selectors:
            self.assert_rule(selector, {"-gtk-icon-transform": "scaleX(-1)"})
            self.assertEqual(self.selectors.count(selector), 1)
        self.assertEqual(
            {selector for selector, declarations in self.rules.items()
             if "-gtk-icon-transform" in declarations},
            set(selectors),
        )

    def test_expander_row_arrow_transition_motion(self):
        # An expander row's disclosure arrow keeps stock's two
        # orientations (half a turn at rest, upright while checked) while
        # the 200ms icon-transform ease is erased: the byte-equal stock
        # twin spelling declares only `transition: none`, sitting after
        # the existing caps-lock groups at the sheet tail.
        selector = "row.expander image.expander-row-arrow"
        self.assertEqual(self.selectors.count(selector), 1, selector)
        self.assert_rule(selector, {"transition": "none"})
        # Exact-dict, not the per-property subset: a stray rotation,
        # transform, colour or geometry declaration must fail, per the
        # entry's guarantee.
        self.assertEqual(self.rules[selector], {"transition": "none"}, selector)
        # The spelling is new to the sheet, so a stray state twin, a
        # second rule or a wrongly-spelled selector fails this sweep.
        self.assertEqual(
            {s for s in self.rules if "expander-row-arrow" in s}, {selector}
        )
        self.assertGreater(
            self.selectors.index(selector),
            self.selectors.index("entry.password image.caps-lock-indicator"),
        )

    def test_expander_widget_title_corners(self):
        # The 2026-11-04 expander-title comment block appends one group
        # after the existing alert-dialog groups at the sheet tail; stock's
        # two radius arms (integration 6px, toolkit 5px) share one selector
        # string, so one byte-equal restatement squares both.
        self.assertEqual(
            {s for s in self.rules if s.startswith("expander-widget > box > title")},
            {"expander-widget > box > title"},
        )
        self.assertEqual(
            {s for s in self.rules if "expander-widget" in s},
            {
                "expander-widget > box > title",
                "expander-widget:focus:focus-visible > box > title",
            },
        )
        self.assertEqual(self.selectors.count("expander-widget > box > title"), 1)
        self.assert_square_corner("expander-widget > box > title")
        self.assertGreater(
            self.selectors.index("expander-widget > box > title"),
            self.selectors.index("cursor-handle > contents"),
        )


if __name__ == "__main__":
    unittest.main()
