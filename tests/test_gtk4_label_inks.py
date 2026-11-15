"""GTK 4 label and text-hint foreground checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk_css import strip_comments
from support.gtk_theme_spec import DISABLED_TEXT, ETCH_DARK
from support.gtk4_sheet import Gtk4SheetRuleCases
from support.platinum_palette import BLACK


class TestGtk4LabelInks(Gtk4SheetRuleCases, unittest.TestCase):
    def test_header_subtitle_foreground(self):
        selectors = ("headerbar .subtitle", "windowtitle .subtitle")
        self.assert_disabled_text(selectors)
        expected = {**DISABLED_TEXT, "opacity": "1"}
        self.assert_rule_group(dict.fromkeys(selectors, expected))


    def test_separator_label_foreground(self):
        self.assert_separator_label_foreground()


    def test_placeholder_foreground(self):
        selectors = (
            "entry > text > placeholder",
            "spinbutton > text > placeholder",
            "spinbutton.vertical > text > text > placeholder",
        )
        self.assert_disabled_text(selectors)
        expected = {**DISABLED_TEXT, "opacity": "1"}
        for selector in selectors:
            self.assertEqual(self.rules[selector], expected)
            self.assertEqual(self.css.count(selector), 1)


    def test_dimmed_label_foreground(self):
        selector = "label.dimmed"
        self.assert_disabled_text((selector,))
        self.assert_rule(selector, {**DISABLED_TEXT, "opacity": "1"})
        self.assertEqual(self.selectors.count(selector), 1)
        self.assertNotIn(".dimmed", self.selectors)


    def test_label_error_colour_class(self):
        # The existing label policy takes no colour class: the sheet restates
        # the two stock error colour-class arms with byte-equal twins
        # declaring the existing inherited black text and the existing
        # insensitive grey, so an error-classed label paints the existing
        # policy instead of stock's red, and its disabled twin paints the
        # existing grey instead of stock's translucent red. Stock ships no
        # `label.warning` arm, so there is nothing to restate there.
        for selector in ("label.error", "label.error:disabled"):
            self.assertEqual(self.selectors.count(selector), 1)
        self.assertEqual(self.rules["label.error"], {"color": BLACK})
        self.assertEqual(self.rules["label.error:disabled"], {"color": ETCH_DARK})

    def test_dim_label_foreground(self):
        selector = ".dim-label"
        self.assert_disabled_text((selector,))
        self.assert_rule(selector, {**DISABLED_TEXT, "opacity": "1"})
        self.assertEqual(strip_comments(self.css).count(selector), 1)


if __name__ == "__main__":
    unittest.main()
