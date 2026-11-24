"""GTK 4 bar-family checks (infobar, search, action, status and path bars)
moved out of ``test_gtk4_theme``.
"""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import ETCH_DARK
from support.platinum_palette import BLACK, FACE, WHITE


class TestGtk4Bars(Gtk4SheetRuleCases, unittest.TestCase):
    def test_infobar(self):
        self.assert_infobar(("infobar > revealer > box",))
        # No infobar-family rule names a message type; the ban's provenance
        # lives on the shared sweep helper.
        self.assert_infobar_message_type_ban()

    def test_banner_surface(self):
        selectors = {
            "banner > revealer > widget",
            "banner > revealer > widget:backdrop",
        }
        self.assertEqual(
            {selector for selector in self.selectors if "banner" in selector},
            selectors,
        )
        expected = {"background-color": FACE, "color": BLACK}
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)
                for prop in expected:
                    self.assertEqual(
                        self.rules[selector][prop],
                        self.rules["infobar > revealer > box"][prop],
                    )

    def test_search_bar(self):
        self.assert_infobar(("searchbar > revealer > box",))

    def test_action_bar(self):
        self.assert_infobar(("actionbar > revealer > box",))

    def test_search_bar_backdrop(self):
        # An unfocused window keeps the existing band face: the
        # backdrop record spells its stock twin byte-equal and wins the tie
        # by later user-sheet source order.
        declarations = {
            "background-color": FACE,
            "border-bottom-color": ETCH_DARK,
            "box-shadow": f"inset 0 -1px {WHITE}",
            "transition": "none",
        }
        self.assert_rule_group(
            {"searchbar > revealer > box:backdrop": declarations}
        )
        self.assertEqual(
            {s for s in self.rules if s.startswith("searchbar") and ":backdrop" in s},
            {"searchbar > revealer > box:backdrop"},
        )
        # Stock GTK 4 declares neither an action-bar backdrop arm nor a
        # location strip, so no such spelling belongs here.
        self.assertNotIn("actionbar > revealer > box:backdrop", self.rules)
        self.assertFalse([s for s in self.rules if "location-bar" in s])
        self.assert_rule_after(
            "searchbar > revealer > box:backdrop",
            "actionbar > revealer > box {",
        )
        self.assert_rule_after(
            "statusbar {",
            "searchbar > revealer > box:backdrop",
        )

    def test_status_bar(self):
        self.assert_infobar(("statusbar",))

    def test_path_bar_tabs(self):
        forms = {
            "base": ("pathbar > scrolledwindow > viewport > box > button",),
            "hover": ("pathbar > scrolledwindow > viewport > box > button:hover",),
            "checked": ("pathbar > scrolledwindow > viewport > box > button:checked",),
            "checked+hover": (
                "pathbar > scrolledwindow > viewport > box > button:checked:hover",
            ),
        }
        self.assert_tab_faces(forms)


if __name__ == "__main__":
    unittest.main()
