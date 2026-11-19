"""GTK 3 link-button label declarations."""

from __future__ import annotations

import unittest

from support import gtk_css
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import DISABLED_TEXT
from support.repo_root import ROOT

CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"


class TestGtkThemeLinkButtons(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS_PATH

    def test_disabled_link_button_labels(self):
        selectors = ("button:link:disabled > label", "button:visited:disabled > label")
        self.assert_disabled_text(selectors)
        uncommented = gtk_css.strip_comments(self.css)
        disabled_rule = uncommented.index(selectors[0] + ", " + selectors[1] + " {")
        self.assertGreater(disabled_rule, uncommented.index("button:link > label {"))
        self.assertGreater(disabled_rule, uncommented.index("button:visited > label {"))

    def test_disabled_child_link_button_labels(self):
        selectors = (
            "button:link > label:disabled",
            "button:visited > label:disabled",
            "button:link > label:disabled:backdrop",
            "button:visited > label:disabled:backdrop",
        )
        self.assert_disabled_text(selectors)
        for selector in selectors:
            self.assertEqual(self.rules[selector], DISABLED_TEXT)
            self.assertEqual(self.selectors.count(selector), 1)
        uncommented = gtk_css.strip_comments(self.css)
        disabled_child_rule = uncommented.index(selectors[0] + ",")
        self.assertGreater(disabled_child_rule, uncommented.index("button:link > label {"))
        self.assertGreater(disabled_child_rule, uncommented.index("button:visited > label {"))
        self.assertGreater(disabled_child_rule, uncommented.index(
            "button:link:disabled > label, button:visited:disabled > label {"
        ))
        self.assertGreater(disabled_child_rule, uncommented.index(
            "button:visited:not(:disabled) > label:active:not(:disabled) {"
        ))
        self.assertGreater(disabled_child_rule, uncommented.index(
            "button:visited:not(:disabled) > label:backdrop:active:not(:disabled) {"
        ))

    def test_link_button_label_interaction_colours(self):
        blue = (
            "button:link:not(:disabled) > label:hover:not(:disabled)",
            "button:link:not(:disabled) > label:active:not(:disabled)",
        )
        visited = (
            "button:visited:not(:disabled) > label:hover:not(:disabled)",
            "button:visited:not(:disabled) > label:active:not(:disabled)",
        )
        for selectors, expected in ((blue, "#0000EE"), (visited, "#551A8B")):
            for selector in selectors:
                self.assertEqual(self.rules[selector], {"color": expected})
                self.assertEqual(self.selectors.count(selector), 1)
        self.assert_scheme_link_colours()
        uncommented = gtk_css.strip_comments(self.css)
        disabled = uncommented.index(
            "button:link:disabled > label, button:visited:disabled > label {"
        )
        blue_rule = uncommented.index(blue[0] + ",")
        visited_rule = uncommented.index(visited[0] + ",")
        self.assertGreater(blue_rule, disabled)
        self.assertGreater(visited_rule, blue_rule)

    def test_enabled_backdrop_link_button_label_colours(self):
        blue = (
            "button:link:not(:disabled) > label:backdrop:not(:disabled)",
            "button:link:not(:disabled) > label:backdrop:hover:not(:disabled)",
            "button:link:not(:disabled) > label:backdrop:active:not(:disabled)",
        )
        visited = tuple(selector.replace("button:link:", "button:visited:") for selector in blue)
        for selectors, expected in ((blue, "#0000EE"), (visited, "#551A8B")):
            for selector in selectors:
                self.assertEqual(self.rules[selector], {"color": expected})
                self.assertEqual(self.selectors.count(selector), 1)
        self.assert_scheme_link_colours()
        uncommented = gtk_css.strip_comments(self.css)
        blue_rule = uncommented.index(blue[0] + ",")
        visited_rule = uncommented.index(visited[0] + ",")
        self.assertGreater(blue_rule, uncommented.index("button:visited > label {"))
        self.assertGreater(blue_rule, uncommented.index(
            "button:link:disabled > label, button:visited:disabled > label {"
        ))
        self.assertLess(blue_rule, visited_rule)


if __name__ == "__main__":
    unittest.main()
