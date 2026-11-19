"""Validate GTK 3 Platinum accelerator-editor declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.platinum_palette import SELECTION
from support.repo_root import ROOT


class TestGtkThemeAcceleratorEditor(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_view_accelerator_editor(self):
        # The stock label face tints the view family's on-screen
        # accelerator editor -- the overlay label a header button shows
        # while it captures a key -- with its accent. No collected
        # reference screenshot shows accelerator editing, so the pinned
        # selection fill answers it, as for the selected rows and the
        # drop header arm (see the sheet's adaptation
        # comment); the one stock arm was probed fresh 2026-11-09 with
        # gresource extract of the toolkit resource in
        # /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (its resource path is
        # recorded in docs/invariants.md, the GTK accelerator-editor
        # invariant); it has no ink, geometry or state member beyond
        # background-color.
        spelling = "treeview.view acceleditor > label"
        self.assertEqual(self.selectors.count(spelling), 1, spelling)
        self.assertEqual(self.rules[spelling], {"background-color": SELECTION})
        self.assertEqual(
            {s for s in self.rules if "acceleditor" in s},
            {spelling},
        )
        # Keep the rule after header-drop and before list-row focus; the
        # comma group's members are split selectors in the parsed sheet.
        self.assertGreater(
            self.css.index(spelling),
            self.css.index("treeview.view header button.dnd:selected {"),
        )
        self.assertLess(
            self.css.index(spelling),
            self.css.index("list row:focus {"),
        )


if __name__ == "__main__":
    unittest.main()
