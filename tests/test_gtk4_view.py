"""GTK 4 view declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import ETCH_DARK
from support.platinum_palette import BLACK, SELECTION


class TestGtk4View(Gtk4SheetRuleCases, unittest.TestCase):
    def test_view_background(self):
        self.assert_view_background((".view", "list"))

    def test_view_row_separators(self):
        """Asked-for view separators paint the etched separator's dark half."""
        horizontal = ("listview.horizontal row.separator",
                      "listview.separators.horizontal > row:not(.separator)",
                      "list.horizontal row.separator",
                      "list.separators.horizontal > row:not(.separator)")
        vertical = ("listview:not(.horizontal) row.separator",
                    "listview.separators:not(.horizontal) > row:not(.separator)",
                    "list:not(.horizontal) row.separator",
                    "list.separators:not(.horizontal) > row:not(.separator)")
        view_spelling = {"columnview.view.separator", "treeview.view.separator"}
        cell_spelling = "columnview.column-separators > listview > row > cell"
        expected = [
            (selector, {"color": ETCH_DARK}) for selector in sorted(view_spelling)
        ]
        expected += [(selector, {"border-left": f"1px solid {ETCH_DARK}"})
                     for selector in horizontal]
        expected += [(selector, {"border-bottom": f"1px solid {ETCH_DARK}"})
                     for selector in vertical]
        expected.append((cell_spelling, {"border-left-color": ETCH_DARK}))
        backdrop_order = self.selectors.index("columnview.view:selected:backdrop")
        drop_order = self.selectors.index("columnview.view > dndtarget:drop(active)")
        for selector, expected_rule in expected:
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, expected_rule)
                self.assertGreater(self.selectors.index(selector), backdrop_order)
                self.assertLess(self.selectors.index(selector), drop_order)
        # The restated tone is the only separator paint at these view spellings:
        # no existing selector carries any of the stock arm's tokens, and every
        # selector ending on one of them is one of the restated spellings.
        self.assertEqual(
            {selector for selector in self.rules
             if selector.endswith("view.separator")},
            view_spelling,
        )
        self.assertEqual(
            {selector for selector in self.rules
             if "row:not(.separator)" in selector},
            {"listview.separators.horizontal > row:not(.separator)",
             "list.separators.horizontal > row:not(.separator)",
             "listview.separators:not(.horizontal) > row:not(.separator)",
             "list.separators:not(.horizontal) > row:not(.separator)"},
        )
        self.assertEqual(
            {selector for selector in self.rules
             if selector.endswith("row.separator")},
            {"listview.horizontal row.separator",
             "list.horizontal row.separator",
             "listview:not(.horizontal) row.separator",
             "list:not(.horizontal) row.separator"},
        )
        self.assertEqual(
            {selector for selector in self.rules if "column-separators" in selector},
            {cell_spelling},
        )

    def test_view_accelerator_editor(self):
        # The stock label face tints the view family's on-screen
        # accelerator editor -- the overlay label a header button shows
        # while it captures a key -- with its accent. No collected
        # reference screenshot shows accelerator editing, so the pinned
        # selection fill answers it, as for the selected rows and the
        # drop header arm (see the sheet's adaptation
        # comment). The three stock arms were probed fresh 2026-11-09
        # with gresource extract of Default-light.css and Default-dark.css
        # in /usr/lib/x86_64-linux-gnu/libgtk-4.so.1 (libgtk-4 4.18.6,
        # light 726 / dark 718) and of the desktop integration library's
        # base stylesheet resource (the library name and resource path
        # recorded in docs/invariants.md, base 716): none claims any
        # member beyond background-color.
        expected = {"background-color": SELECTION}
        spellings = (
            "columnview.view acceleditor > label",
            "treeview.view acceleditor > label",
            "window.print:not(.ssd-frame) treeview.dialog-action-box acceleditor > label",
        )
        self.assert_rule_group({spelling: expected for spelling in spellings})
        # The sweep kills renamed and stray accelerator-editor spellings
        # alike; comment mentions are not selectors.
        self.assertEqual(
            {s for s in self.rules if "acceleditor" in s},
            set(spellings),
        )
        # Order pin: the restated group sits directly after the existing
        # drag-drop header-button group and before the expander group.
        self.assertGreater(
            self.selectors.index("columnview.view acceleditor > label"),
            self.selectors.index(
                "window.print:not(.ssd-frame) treeview.dialog-action-box > header > button.dnd"
            ),
        )
        self.assertLess(
            self.selectors.index("columnview.view acceleditor > label"),
            self.selectors.index("treeview.view.expander"),
        )

    def test_view_child_selected_arms(self):
        """Pin the view children restated off the existing row selection."""
        self.assert_rule(
            "flowbox > flowboxchild:selected",
            {
                "background-color": SELECTION,
                "color": BLACK,
                "outline-color": BLACK,
                "border-radius": "0",
            },
        )
        self.assert_rule(
            "gridview > child:selected",
            {
                "background-color": SELECTION,
                "color": BLACK,
                "outline-color": BLACK,
                "border-radius": "0",
            },
        )
        # Base selection already covers unfocused windows. An extra backdrop
        # state would outrank the chooser's base tint and tie stock's disabled
        # label. Pin its absence as well as the base declarations above.
        for selector in (
            "flowbox > flowboxchild:selected:backdrop",
            "gridview > child:selected:backdrop",
        ):
            with self.subTest(selector=selector):
                self.assertNotIn(selector, self.rules)
        for selector, alpha in (
            ("filechooser gridview child:selected", "0.15"),
            ("filechooser gridview child:selected:hover", "0.20"),
            ("filechooser gridview child:selected:active", "0.25"),
        ):
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {"background-color": f"rgba(204, 204, 255, {alpha})"},
                )

    def test_view_child_focus_outlines(self):
        selectors = (
            "iconview:focus:focus-visible",
            "flowbox > flowboxchild:focus:focus-visible",
            "gridview > child:focus:focus-visible",
        )
        self.assert_scale_anchored_focus_outline(selectors)
        self.assertEqual(self.selectors.count("iconview"), 1)
        self.assert_rule("iconview", {"transition": "none"})
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.endswith("child:focus:focus-visible")
            },
            set(selectors[1:]),
        )
        self.assertGreater(
            self.selectors.index("iconview:focus:focus-visible"),
            self.selectors.index("iconview.view:not(:disabled):backdrop:selected"),
        )
        self.assertLess(
            self.selectors.index("iconview:focus:focus-visible"),
            self.selectors.index("row:disabled:selected"),
        )


if __name__ == "__main__":
    unittest.main()
