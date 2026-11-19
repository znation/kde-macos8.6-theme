"""Validate GTK 3 infobar declarations in the Platinum sheet."""

from __future__ import annotations

import unittest

from support import gtk_css
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    BUTTON_BEVEL,
    DISABLED_TEXT,
    INVERTED_BUTTON_BEVEL,
    LINK,
)
from support.platinum_palette import BLACK, FACE, SELECTION
from support.repo_root import ROOT


class TestGtkThemeInfobar(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_infobar(self):
        self.assert_infobar(("infobar > revealer > box",))
        # No infobar-family rule may name a message type. Keep this whole
        # sheet sweep beside the GTK 3 band assertion without inheriting the
        # shared-control test cases from the source suite.
        for selector in self.selectors:
            if "infobar" in selector:
                for message_type in (".info", ".question", ".warning", ".error"):
                    self.assertNotIn(message_type, selector, message_type)

    def test_infobar_button_family(self):
        """The bar's typed stock button, selection and link arms restated.

        gtk-contained.css's four typed infobar button families out-token
        the existing plain ``button`` rule inside an infobar, and the bar's
        ``selection`` and ``*:link`` arms out-token the existing selection
        and link records, so the sheet restates them with the untyped
        band-chain spellings: the existing surface-button face/pressed/
        insensitive/backdrop recipes (the existing ``.app-notification``
        and ``.osd`` button groups), the existing selection fill and the
        existing link ink. All twelve spellings embed the existing measured
        chain ``infobar > revealer > box`` and name no message type, so
        ``test_infobar``'s ban stays green uncited here.
        """
        face = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        pressed = {**face, "box-shadow": INVERTED_BUTTON_BEVEL}
        # The existing `.osd button:disabled` shape: no ``outline-color``,
        # the Inactive grey (DISABLED_TEXT) label ink.
        disabled = {
            **{k: v for k, v in face.items() if k != "outline-color"},
            "color": DISABLED_TEXT["color"],
        }
        expected = {
            "infobar > revealer > box button": face,
            "infobar > revealer > box button:hover": face,
            "infobar > revealer > box button:active": pressed,
            "infobar > revealer > box button:checked": pressed,
            "infobar > revealer > box button:disabled": disabled,
            "infobar > revealer > box button:disabled:backdrop": disabled,
            "infobar > revealer > box button:backdrop": face,
            "infobar > revealer > box button label": {"color": BLACK},
            "infobar > revealer > box button:backdrop label": {"color": BLACK},
            "infobar > revealer > box selection": {"background-color": SELECTION},
            "infobar > revealer > box label:link": {"color": LINK},
            "infobar > revealer > box button:link": {"color": LINK},
        }
        for selector, declarations in expected.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1, selector)
                self.assertEqual(self.rules[selector], declarations, selector)
        # The family sweep: the existing band rule plus exactly these
        # twelve restatements — no respelling escapes the family.
        self.assertEqual(
            {s for s in self.selectors if "infobar" in s},
            {"infobar > revealer > box", *expected},
        )
        # Source order: every group follows the existing band rule at the
        # sheet tail (after the marked-scale thumb blocks).
        sheet = gtk_css.strip_comments(self.css)
        band = sheet.index("\ninfobar > revealer > box {")
        for selector in expected:
            positions = []
            start = 0
            while True:
                found = sheet.find(f"\n{selector}", start)
                if found == -1:
                    break
                positions.append(found)
                start = found + 1
            self.assertTrue(positions, selector)
            for position in positions:
                self.assertGreater(position, band, selector)


if __name__ == "__main__":
    unittest.main()
