"""GTK 4 row declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.platinum_palette import SELECTION


class TestGtk4Row(Gtk4SheetRuleCases, unittest.TestCase):
    def test_row_selection_backdrop(self):
        self.assert_row_selection_backdrop((
            "treeview.view:selected:backdrop",
            "list row.activatable:selected:backdrop",
            "columnview.view:selected:backdrop",
            "listview > row.activatable:selected:backdrop",
        ))
        self.assert_rule_after(
            "list row.activatable:selected:backdrop",
            "list row.activatable:selected:",
        )

    def test_row_drop_borders(self):
        expected = {
            "border-style": "solid none",
            "border-width": "1px",
            "border-color": SELECTION,
        }
        for selector in (
            "columnview.view > dndtarget:drop(active)",
            "treeview.view > dndtarget:drop(active)",
            "window.print:not(.ssd-frame) treeview.dialog-action-box > dndtarget:drop(active)",
        ):
            with self.subTest(selector=selector):
                self.assert_rule(selector, expected)

    def test_row_drop_directional_arms_undeclared(self):
        # The stock directional arms only hide one of the two row drop
        # lines; neither carries a colour the selection replaces, so the
        # sheet keeps them undeclared. This pin fails if a rule ever
        # claims one of them by name.
        self.assertNotIn("drop(active).after", self.css)
        self.assertNotIn("drop(active).before", self.css)

    def test_row_spin_stepper_corners(self):
        """Pin the six restated preference-row spin stepper arms.

        No collected reference screenshot shows a preference-row spin
        stepper, so the sheet restates the six row-spin members stock's
        34px-minimum arm (and its earlier 9px arm) declares byte-equal,
        each carrying exactly the zero radius: the existing generic button
        restate names the one element and loses the compound row.spin tie,
        and the existing plain horizontal stepper groups name
        spinbutton:not(.vertical), so stock paints these steppers 9px and
        9999px round today. The six spellings sit in one comma group at the
        sheet tail with their dated comment.
        """
        expected = (
            "row.spin spinbutton > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):last-child",
            "row.spin spinbutton > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):last-child:dir(ltr):last-child",
            "row.spin spinbutton > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):last-child:dir(rtl):first-child",
            "row.spin spinbutton > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque)",
            "row.spin spinbutton > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(ltr):last-child",
            "row.spin spinbutton > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(rtl):first-child",
        )
        for selector in expected:
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"border-radius": "0"})
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_matches_frame(selector, "border-radius")
        self.assertEqual(
            {selector for selector in self.rules if "row.spin" in selector},
            set(expected),
        )


if __name__ == "__main__":
    unittest.main()
