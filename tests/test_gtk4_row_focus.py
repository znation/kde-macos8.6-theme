"""GTK 4 row focus and attention checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.platinum_palette import BLACK


class TestGtk4RowFocus(Gtk4SheetRuleCases, unittest.TestCase):
    def test_list_row_focus_outlines(self):
        """Keyboard-focused rows paint the existing black focus colour."""
        spellings = (
            "row:focus:focus-visible",
            ".boxed-list > row:focus:focus-visible",
            "stacksidebar row:focus:focus-visible",
            ".navigation-sidebar > row:focus-visible:focus-within",
            "list.boxed-list > row:focus:focus-visible",
            "list.content > row:focus:focus-visible",
            "list.boxed-list > row.expander row.header:focus:focus-visible",
            "list.content > row.expander row.header:focus:focus-visible",
            "row.expander list.nested > row:focus:focus-visible",
            "list.boxed-list-separate > row:focus:focus-visible",
            "list.boxed-list-separate > row.expander row.header:focus:focus-visible",
        )
        for selector in spellings:
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, {"outline-color": BLACK})
        # The restated spellings are the only row focus arms the sheet
        # declares: the scan kills renamed and stray variants. A row arm
        # must start the selector or follow a space, so the notebook
        # overflow arrow's own focus arm (its node name ends in "row")
        # does not join this family.
        suffixes = (
            "row:focus:focus-visible",
            "row.header:focus:focus-visible",
            "row:focus-visible:focus-within",
        )
        self.assertEqual(
            {selector for selector in self.rules
             if any(
                 selector.endswith(suffix)
                 and (len(selector) == len(suffix)
                      or selector[-len(suffix) - 1] == " ")
                 for suffix in suffixes)},
            set(spellings),
        )
        # Stock's generic 300 ms outline-motion arm is removed.
        self.assert_exact_rule_once("row", {"transition": "none"})
        # Source order: the focus group sits after the existing
        # disabled-selected backdrop group and before the existing tab-close
        # block.
        self.assertGreater(
            self.selectors.index("row:focus:focus-visible"),
            self.selectors.index("columnview.view:disabled:selected:backdrop"),
        )
        self.assertLess(
            self.selectors.index("row:focus:focus-visible"),
            self.selectors.index(
                "notebook > header > tabs > tab button.flat:disabled"),
        )

    def test_needs_attention_badges(self):
        """Needs-attention labels and images keep no stock accent pulse."""
        spellings = (
            "stacksidebar row.needs-attention > label",
            "stackswitcher > button.needs-attention > label",
            "stackswitcher > button.needs-attention > image",
        )
        for selector in spellings:
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, {"animation": "none", "background-image": "none"})
        # Source order: the restated group sits after the existing row-focus
        # outline rule and before the existing tab-close block.
        self.assertGreater(
            self.selectors.index("stacksidebar row.needs-attention > label"),
            self.selectors.index("row:focus:focus-visible"),
        )
        self.assertLess(
            self.selectors.index("stacksidebar row.needs-attention > label"),
            self.selectors.index("notebook > header > tabs > tab button.flat"),
        )
        # The restated spellings are the only needs-attention arms the sheet
        # declares: the scan kills renamed and stray variants.
        # The restated spellings are the only needs-attention arms the sheet
        # declares beside the 2026-11-04 tab-thumbnail badge cap: the scan
        # kills renamed and stray variants.
        self.assertEqual(
            {selector for selector in self.rules
             if "needs-attention" in selector},
            set(spellings) | {"tabthumbnail .needs-attention > widget"},
        )
        # The badge cap states only the corner radius; the label spellings'
        # animation and dot-image clears do not apply to it.
        self.assert_rule("tabthumbnail .needs-attention > widget",
                         {"border-radius": "0"})
        self.assertEqual(
            self.selectors.count("tabthumbnail .needs-attention > widget"), 1)
        self.assert_matches_frame("tabthumbnail .needs-attention > widget",
                                  "border-radius")


if __name__ == "__main__":
    unittest.main()
