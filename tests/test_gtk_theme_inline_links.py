"""Validate ordinary GTK 3 inline-link declarations."""

import unittest

from support import gtk_css
from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT


class TestGtkThemeInlineLinks(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_disabled_inline_link_foregrounds(self):
        selectors = ("label:link:disabled", "label:visited:disabled")
        self.assert_disabled_text(selectors)
        for selector in selectors:
            self.assertEqual(self.rules[selector], {"color": "#888888"})
            self.assertEqual(self.selectors.count(selector), 1)
        uncommented = gtk_css.strip_comments(self.css)
        disabled_rule = uncommented.index(selectors[0] + ", " + selectors[1] + " {")
        self.assertGreater(disabled_rule, uncommented.index("label:link, button:link > label {"))
        self.assertGreater(disabled_rule, uncommented.index("label:visited, button:visited > label {"))

    def test_disabled_backdrop_inline_link_foregrounds(self):
        selectors = (
            "label:link:disabled:backdrop",
            "label:link:disabled:backdrop:hover",
            "label:link:disabled:backdrop:active",
            "label:visited:disabled:backdrop",
            "label:visited:disabled:backdrop:hover",
            "label:visited:disabled:backdrop:active",
        )
        self.assert_disabled_text(selectors)
        for selector in selectors:
            self.assertEqual(self.rules[selector], {"color": "#888888"})
            self.assertEqual(self.selectors.count(selector), 1)
        uncommented = gtk_css.strip_comments(self.css)
        rule = uncommented.index(selectors[0] + ",")
        self.assertGreater(rule, uncommented.index("label:link:disabled, label:visited:disabled {"))
        self.assertGreater(rule, uncommented.index("label > link:visited:hover:not(:disabled),"))

    def test_inline_link_interaction_colours(self):
        # GTK 3 gtklabel.c creates child link nodes with either LINK or VISITED,
        # never both. Pin declarations for those actual node/state combinations.
        blue = (
            "label > link:link:hover:not(:disabled)",
            "label > link:link:active:not(:disabled)",
        )
        visited = (
            "label > link:visited:hover:not(:disabled)",
            "label > link:visited:active:not(:disabled)",
        )
        for selector in blue:
            self.assertEqual(self.rules[selector], {"color": "#0000EE"})
            self.assertEqual(self.selectors.count(selector), 1)
        for selector in visited:
            self.assertEqual(self.rules[selector], {"color": "#551A8B"})
            self.assertEqual(self.selectors.count(selector), 1)
        self.assert_scheme_link_colours()
        uncommented = gtk_css.strip_comments(self.css)
        self.assertLess(uncommented.index(blue[0] + ","), uncommented.index(visited[0] + ","))

    def test_enabled_backdrop_inline_link_colours(self):
        blue = (
            "label:link:backdrop:not(:disabled)",
            "label:link:backdrop:hover:not(:disabled)",
            "label:link:backdrop:active:not(:disabled)",
        )
        visited = tuple(selector.replace("label:link:", "label:link:visited:") for selector in blue)
        for selectors, expected in ((blue, "#0000EE"), (visited, "#551A8B")):
            for selector in selectors:
                self.assertEqual(self.rules[selector], {"color": expected})
                self.assertEqual(self.selectors.count(selector), 1)
        self.assert_scheme_link_colours()
        uncommented = gtk_css.strip_comments(self.css)
        blue_rule = uncommented.index(blue[0] + ",")
        visited_rule = uncommented.index(visited[0] + ",")
        self.assertGreater(blue_rule, uncommented.index("label > link:visited:active:not(:disabled) {"))
        self.assertLess(blue_rule, visited_rule)


if __name__ == "__main__":
    unittest.main()
