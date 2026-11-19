"""Validate GTK 3 places-view server-button motion declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT


class TestGtkThemeServerButton(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_server_list_button_rotation_motion(self):
        selectors = (
            "placesview .server-list-button > image",
            "placesview .server-list-button:checked > image",
        )
        for selector in selectors:
            self.assert_rule(selector, {"transition": "none"})
            # Exact-dict, not the per-property subset: a stray rotation,
            # transform, colour or geometry declaration on either twin
            # must fail, per the entry's guarantee.
            self.assertEqual(self.rules[selector], {"transition": "none"}, selector)
            self.assertEqual(self.selectors.count(selector), 1, selector)
        # The element-level family is exactly these two stock arms: the
        # sweep kills a renamed spelling, a stray state twin or a second
        # rule.
        self.assertEqual(
            {s for s in self.rules if "server-list-button" in s},
            set(selectors),
        )
        # The rules hold the sheet tail, after the existing infobar band's
        # closing selection and link spellings (the parser splits a
        # comma group into its member selectors).
        tail_anchor = max(
            self.selectors.index("infobar > revealer > box selection"),
            self.selectors.index("infobar > revealer > box label:link"),
            self.selectors.index("infobar > revealer > box button:link"),
        )
        for selector in selectors:
            self.assertGreater(self.selectors.index(selector), tail_anchor)


if __name__ == "__main__":
    unittest.main()
