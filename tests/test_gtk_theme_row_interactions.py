"""Validate GTK 3 list-row pressed and popup-holding face declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import ROW_HOVER
from support.platinum_palette import SELECTION
from support.repo_root import ROOT


class TestGtkThemeRowInteractions(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_list_row_press_and_popup_faces(self):
        # The pressed and popup-holding row states restate the existing
        # faces: stock's four element-level row arms would paint a tinted
        # hover-wash, pressed insets and a selection-accent fill on rows
        # the existing records paint transparent or with the flat lavender
        # selection.
        expected = {
            "row.activatable.has-open-popup": dict(ROW_HOVER),
            "row.activatable:hover": dict(ROW_HOVER),
            "row.activatable:active": {"box-shadow": "none"},
            "row.activatable:selected:active": {"box-shadow": "none"},
            "row.activatable:selected.has-open-popup": {"background-color": SELECTION},
            "row.activatable:selected:hover": {"background-color": SELECTION},
        }
        self.assert_rule_group(expected)
        # The existing row spellings are all list-, listview- or
        # treeview-armed, so this element-level family is exactly six.
        self.assertEqual(
            {s for s in self.rules if s.startswith("row.activatable")},
            set(expected),
        )
        self.assertGreater(
            self.selectors.index("row.activatable:active"),
            self.selectors.index("list row.activatable:selected"),
        )


if __name__ == "__main__":
    unittest.main()
