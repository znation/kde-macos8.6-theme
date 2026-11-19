"""Validate GTK 3 round-button corner declarations."""

from __future__ import annotations

import unittest

from support import gtk_css
from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT


class TestGtkThemeCorners(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_round_button_face_corners(self):
        # The five class-qualified stock arms sit later in source order than
        # the existing unclassed `button`, window-control and `scrollbar button`
        # restatements, so the exact stock twins appended at the sheet tail
        # win every radius tie: square faces, and for the two arms stock
        # rounds with an equal outline radius, square keyboard focus rings.
        self.assert_rule_group(
            {
                "button.circular": {
                    "border-radius": "0",
                    "-gtk-outline-radius": "0",
                },
                # Joined 2026-11-08: the five byte-equal stock geometry
                # declarations (probe of the toolkit resource, libgtk-3
                # 3.24.49, arm at resource line 1687) joined the existing
                # corner record's bare sidebar-button rule to pin the
                # button's box geometry against upstream drift; the radius
                # pair is the existing pair.
                "button.sidebar-button": {
                    "border-radius": "0",
                    "-gtk-outline-radius": "0",
                    "min-height": "26px",
                    "min-width": "26px",
                    "margin-top": "3px",
                    "margin-bottom": "3px",
                    "padding": "0",
                },
                "button.titlebutton:not(.appmenu)": {"border-radius": "0"},
                "modelbutton.flat": {"border-radius": "0"},
                ".menuitem.button.flat": {"border-radius": "0"},
                "scrollbar.overlay-indicator:not(.dragging):not(.hovering) button": {
                    "border-radius": "0"
                },
            },
        )
        # A stray twin under one of the corner-bearing tokens would steal a
        # tie from the exact spellings above; the existing selected-row
        # sidebar-button arms are excluded because they begin with
        # `row:selected` and own colours only.
        for token, expected in (
            ("button.circular", {"button.circular"}),
            (
                "button.sidebar-button",
                {
                    "button.sidebar-button",
                    "button.sidebar-button:not(:hover):not(:active) > image",
                    "button.sidebar-button:backdrop > image",
                },
            ),
            ("modelbutton.flat", {"modelbutton.flat"}),
            ("menuitem.button.flat", {".menuitem.button.flat"}),
        ):
            sweep = {
                selector
                for selector in self.rules
                if token in selector and "row:selected" not in selector
            }
            self.assertEqual(sweep, expected, token)
        # Source order: after the existing plain `button` and `scrollbar button`
        # groups and at the sheet tail behind the backdrop link block.
        uncommented = gtk_css.strip_comments(self.css)
        circular = uncommented.index("button.circular {")
        for rule in ("button {", "scrollbar button {"):
            self.assertGreater(circular, uncommented.index("\n" + rule), rule)
        self.assertGreater(
            circular,
            uncommented.index(
                "label:link:visited:selected:disabled:backdrop:active {"
            ),
            "circular must follow the sheet-tail backdrop link block",
        )


if __name__ == "__main__":
    unittest.main()
