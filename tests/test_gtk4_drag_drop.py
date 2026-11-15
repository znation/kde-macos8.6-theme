"""GTK 4 selection marquee and drag-and-drop mark checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.platinum_palette import BLACK, SELECTION


class TestGtk4DragDrop(Gtk4SheetRuleCases, unittest.TestCase):
    def test_rubberband(self):
        selectors = {
            "rubberband",
            ".content-view > rubberband",
            "columnview.view > rubberband",
            "treeview.view > rubberband",
            "gridview > rubberband",
            "flowbox > rubberband",
        }
        self.assert_rubberband(tuple(selectors))
        self.assertEqual(
            {selector for selector in self.rules if "rubberband" in selector},
            selectors,
        )
    def test_iconview_drop_border(self):
        self.assert_rule(
            "iconview > dndtarget:drop(active)",
            {"border": f"1px solid {SELECTION}"},
        )
    def test_header_drop_indicator(self):
        expected = {
            "background-color": SELECTION,
            "background-image": "none",
            "color": BLACK,
            "text-shadow": "none",
            "box-shadow": "none",
            "border-style": "none",
            "border-radius": "0",
        }
        for scope in ("columnview.view > header", "treeview.view > header"):
            for state in ("", ":hover", ":active", ":selected"):
                with self.subTest(scope=scope, state=state):
                    self.assert_rule(f"{scope} > button.dnd{state}", expected)
        self.assert_rule(
            "window.print:not(.ssd-frame) treeview.dialog-action-box > header > button.dnd",
            expected,
        )


if __name__ == "__main__":
    unittest.main()
