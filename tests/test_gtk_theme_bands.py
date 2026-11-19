"""Validate GTK 3 auxiliary band declarations."""

from __future__ import annotations

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import ETCH_DARK
from support.platinum_palette import FACE, WHITE
from support.repo_root import ROOT


class TestGtkThemeBands(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_search_bar(self):
        self.assert_infobar(("searchbar > revealer > box",))

    def test_location_bar(self):
        self.assert_infobar((".location-bar",))
        self.assertEqual(self.selectors.count(".location-bar"), 1)
        self.assertEqual(
            {s for s in self.rules if "location-bar" in s},
            {".location-bar", ".location-bar:backdrop"},
        )
        self.assert_rule_after(
            "statusbar {",
            ".location-bar",
        )

    def test_action_bar(self):
        self.assert_infobar(("actionbar > revealer > box",))

    def test_status_bar(self):
        self.assert_infobar(("statusbar",))

    def test_status_bar_frame_border_is_flat(self):
        self.assert_rule(
            "statusbar > frame > border", {"border-style": "none", "box-shadow": "none"}
        )

    def test_band_backdrop_faces(self):
        # An unfocused window keeps the existing band face: the grouped
        # backdrop record spells each stock backdrop twin byte-equal and
        # wins every tie by later user-sheet source order.
        declarations = {
            "background-color": FACE,
            "border-bottom-color": ETCH_DARK,
            "box-shadow": f"inset 0 -1px {WHITE}",
            "transition": "none",
        }
        self.assert_rule_group(
            {
                "searchbar > revealer > box:backdrop": declarations,
                ".location-bar:backdrop": declarations,
                "actionbar > revealer > box:backdrop": declarations,
            }
        )
        self.assertEqual(
            {s for s in self.rules if s.startswith("searchbar") and ":backdrop" in s},
            {"searchbar > revealer > box:backdrop"},
        )
        self.assertEqual(
            {s for s in self.rules if s.startswith("actionbar") and ":backdrop" in s},
            {"actionbar > revealer > box:backdrop"},
        )
        # The existing inline-toolbar record keeps stock's own face in
        # focused and unfocused windows alike, so stock's grouped
        # `.inline-toolbar:backdrop` membership stays stock.
        self.assertNotIn(".inline-toolbar:backdrop", self.rules)
        self.assert_rule_after(
            "searchbar > revealer > box:backdrop",
            "searchbar > revealer > box,",
        )

        self.assert_rule_after(
            "statusbar {",
            "searchbar > revealer > box:backdrop",
        )


if __name__ == "__main__":
    unittest.main()
