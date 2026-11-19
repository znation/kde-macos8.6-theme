"""Check GTK 3 inline-link declarations in selected contexts."""

from __future__ import annotations

import unittest

from support import gtk_css
from support.colorscheme_fixtures import load_scheme
from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT

LINK_ROOTS = ("label:link", "label:visited", "label:link:visited")


class TestGtkThemeSelectedLinks(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def assert_selected_link_rules(self, selectors, earlier=(), color=None):
        """Check selected-link declarations and precedence over earlier rules."""
        if color is None:
            rgb = load_scheme().get("Colors:Selection", "ForegroundNormal")
            color = "#" + "".join(f"{int(part):02X}" for part in rgb.split(","))
            self.assertEqual(color, "#000000")
        self.assert_rule_group(dict.fromkeys(selectors, {"color": color}))
        css = gtk_css.strip_comments(self.css)
        selected_rule = css.index(selectors[0] + ",")
        for rule in earlier:
            self.assertGreater(selected_rule, css.index(rule))

    def test_selected_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":selected:not(:disabled):not(:backdrop)"
        )
        self.assert_selected_link_rules(
            selectors,
            (
                "label:visited, button:visited > label {",
                "label > link:link:active:not(:disabled) {",
                "label > link:visited:active:not(:disabled) {",
                "label:link:visited:backdrop:active:not(:disabled) {",
            ),
        )

    def test_disabled_selected_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":selected:disabled:not(:backdrop)"
        )
        self.assert_disabled_text(selectors)
        self.assert_selected_link_rules(
            selectors,
            (
                "label:link:disabled, label:visited:disabled {",
                "label:link:selected:not(:disabled):not(:backdrop),",
            ),
            color="#888888",
        )

    def test_selected_ancestor_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":not(:disabled):not(:backdrop)", prefix=":selected "
        )
        self.assert_selected_link_rules(
            selectors,
            (
                "label:visited, button:visited > label {",
                "label > link:link:hover:not(:disabled),",
                "label > link:visited:hover:not(:disabled),",
                "label:link:selected:not(:disabled):not(:backdrop),",
            ),
        )

    def test_disabled_selected_ancestor_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":disabled:not(:backdrop)", prefix=":selected "
        )
        self.assert_disabled_text(selectors)
        self.assert_selected_link_rules(
            selectors,
            (
                "label:link:disabled, label:visited:disabled {",
                ":selected label:link:not(:disabled):not(:backdrop),",
            ),
            color="#888888",
        )

    def test_selected_backdrop_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":selected:backdrop:not(:disabled)"
        )
        self.assert_selected_link_rules(
            selectors,
            (
                "label:link:backdrop:not(:disabled),",
                "label:link:visited:backdrop:not(:disabled),",
                "label:link:selected:not(:disabled):not(:backdrop),",
            ),
        )

    def test_disabled_selected_backdrop_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":selected:disabled:backdrop"
        )
        self.assert_disabled_text(selectors)
        for selector in selectors:
            self.assertEqual(self.rules[selector], {"color": "#888888"})
            self.assertEqual(self.selectors.count(selector), 1)
        uncommented = gtk_css.strip_comments(self.css)
        rule = uncommented.index(selectors[0] + ",")
        self.assertGreater(rule, uncommented.index("label:link:disabled:backdrop,"))
        self.assertGreater(
            rule,
            uncommented.index("label:link:selected:backdrop:not(:disabled),"),
        )

    def test_selected_ancestor_backdrop_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":backdrop:not(:disabled)", prefix=":selected "
        )
        self.assert_selected_link_rules(
            selectors,
            (
                "label:link:backdrop:not(:disabled),",
                "label:link:visited:backdrop:not(:disabled),",
                "label > link:link:hover:not(:disabled),",
                "label > link:visited:hover:not(:disabled),",
                "label:link:selected:backdrop:not(:disabled),",
            ),
        )

    def test_disabled_selected_ancestor_backdrop_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":disabled:backdrop", prefix=":selected "
        )
        self.assert_disabled_text(selectors)
        for selector in selectors:
            self.assertEqual(self.rules[selector], {"color": "#888888"})
            self.assertEqual(self.selectors.count(selector), 1)
        uncommented = gtk_css.strip_comments(self.css)
        rule = uncommented.index(selectors[0] + ",")
        self.assertGreater(
            rule,
            uncommented.index("label:link:disabled:backdrop,"),
        )
        self.assertGreater(
            rule,
            uncommented.index(":selected label:link:backdrop:not(:disabled),"),
        )


if __name__ == "__main__":
    unittest.main()
