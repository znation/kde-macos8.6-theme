"""Validate GTK 3 Platinum embedded entry-icon declarations."""

import unittest

from support.gtk_css import strip_comments
from support.gtk_rule_cases import GtkSheetRuleCases
from support.platinum_palette import BLACK
from support.repo_root import ROOT


class TestGtkThemeEntryImages(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_entry_image_inks(self):
        # The existing entry recipe never names the icon child GTK embeds
        # inside a field or spin button, so the toolkit resource paints
        # its own inks on it: a foreign grey-green at rest, a dark grey
        # under hover, the accent hue while pressed or keyboard-active
        # and a pale grey inside an unfocused window, plus a 6px gap
        # between each side icon and the field's text that the existing
        # sheet owns nowhere. Every colour arm restates its stock twin
        # with the existing field's black ink (no collected reference
        # screenshot shows an embedded icon, so the existing text-ink
        # record stands in; the backdrop twin keeps that face per the
        # existing button:backdrop policy since Platinum's model is
        # active=frontmost), and the two margin twins keep stock's own
        # spacing byte-equal.
        expected = {
            "spinbutton:not(.vertical) image.left": {"margin-right": "6px"},
            "entry image.left": {"margin-right": "6px"},
            "spinbutton:not(.vertical) image.right": {"margin-left": "6px"},
            "entry image.right": {"margin-left": "6px"},
            "spinbutton:not(.vertical) image": {"color": BLACK},
            "entry image": {"color": BLACK},
            "spinbutton:not(.vertical) image:hover": {"color": BLACK},
            "entry image:hover": {"color": BLACK},
            "spinbutton:not(.vertical) image:active": {"color": BLACK},
            "entry image:active": {"color": BLACK},
            "spinbutton:not(.vertical) image:backdrop": {"color": BLACK},
            "entry image:backdrop": {"color": BLACK},
        }
        for selector, declarations in expected.items():
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], declarations, selector)
        # No other spelling in the family exists: the token sweep kills
        # renamed, stray and dropped twins alike.
        self.assertEqual(
            {
                s
                for s in self.rules
                if s.startswith("spinbutton:not(.vertical) image")
                or s.startswith("entry image")
            },
            set(expected),
        )
        # Every restated spelling sits after the existing field rule, so
        # the equal-specificity ties resolve the existing face's way under
        # either cascade reading.
        uncommented = strip_comments(self.css)
        anchor = uncommented.index("entry, spinbutton:not(.vertical) {")
        for selector in expected:
            self.assertGreater(uncommented.index(selector), anchor, selector)


if __name__ == "__main__":
    unittest.main()
