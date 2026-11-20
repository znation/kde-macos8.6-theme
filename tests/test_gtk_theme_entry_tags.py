"""Validate GTK 3 Platinum entry-tag declarations."""

import unittest

from support.gtk_css import strip_comments
from support.gtk_rule_cases import GtkSheetRuleCases
from support.platinum_palette import BLACK, SELECTION
from support.repo_root import ROOT


class TestGtkThemeEntryTags(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_entry_tag_faces(self):
        # The existing entry recipe never names the tag chips a tagged
        # entry embeds at its tail, so the toolkit resource paints its
        # own chip: a foreign accent-blue fill with white ink at rest,
        # a lighter accent under hover, a pale-repeat twin inside an
        # unfocused window and a dimmed translucent white close-button
        # ink with an accent ring and fill under hover and press. The
        # chip restates the palette's flat selection fill with the
        # existing field's black ink (no collected reference screenshot
        # shows an entry tag, so the selection-surface and text-ink
        # records stand in; the backdrop twin keeps that face per the
        # existing button:backdrop policy since Platinum's model is
        # active=frontmost, and the dimmed close-button inks rise to
        # full strength per the existing hover-erase precedents), keeps
        # stock's own padding, vertical margins and border and keeps
        # the two direction margin twins byte-equal and mirrored.
        expected = {
            ".entry-tag": {
                "padding": "5px",
                "margin-top": "2px",
                "margin-bottom": "2px",
                "border-style": "none",
                "color": BLACK,
                "background-color": SELECTION,
            },
            ":dir(ltr) .entry-tag": {"margin-left": "8px", "margin-right": "-5px"},
            ":dir(rtl) .entry-tag": {"margin-left": "-5px", "margin-right": "8px"},
            ".entry-tag:hover": {"background-color": SELECTION},
            ":backdrop .entry-tag": {"color": BLACK, "background-color": SELECTION},
            ".entry-tag.button": {"background-color": "transparent", "color": BLACK},
            ":not(:backdrop) .entry-tag.button:hover": {
                "border": f"1px solid {BLACK}",
                "color": BLACK,
            },
            ":not(:backdrop) .entry-tag.button:active": {
                "background-color": SELECTION,
                "color": BLACK,
            },
        }
        for selector, declarations in expected.items():
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], declarations, selector)
        # No other spelling in the family exists: the token sweep kills
        # renamed, stray and dropped twins alike.
        self.assertEqual(
            {s for s in self.rules if "entry-tag" in s}, set(expected)
        )
        # The whole chip block sits after the existing entry-image block's
        # opener, so the equal-specificity ties resolve the existing
        # face's way under either cascade reading.
        uncommented = strip_comments(self.css)
        anchor = uncommented.index("spinbutton:not(.vertical) image, entry image {")
        for selector in expected:
            self.assertGreater(uncommented.index(selector), anchor, selector)


if __name__ == "__main__":
    unittest.main()
