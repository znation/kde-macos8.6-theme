"""Validate GTK 3 round-button and residual widget corner declarations.

This module covers two corner families: the round-button faces, and the
residual inline-toolbar, keycap, fine-tuned scale trough and emoji-picker
hover corners, which are pinned by
``test_inline_toolbar_keycap_finetune_emoji_corners``. The views-and-dialogs
module no longer carries that check.
"""

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

    def test_inline_toolbar_keycap_finetune_emoji_corners(self):
        """Pin inline-toolbar, keycap, fine-tune trough and emoji corners.

        The four appended groups rest stock's inline-toolbar container,
        shortcut keycap, fine-tuned scale trough family and emoji-picker
        hover radius arms at zero; the emoji section labels also have explicit
        opacity arms tested with their own declarations.
        """
        selectors = (
            ".inline-toolbar",
            ".keycap",
            "scale.fine-tune fill",
            "scale.fine-tune highlight",
            "scale.fine-tune trough",
            "popover.emoji-picker .emoji :hover",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                self.assertEqual(self.selectors.count(selector), 1, selector)
                self.assert_rule(selector, {"border-radius": "0"})
        # The four tokens have no existing or unrelated neighbours: the existing
        # keycap corner record is the GTK 4 `shortcut > .keycap` spelling,
        # and the emoji-label rules are the only additional emoji selectors.
        # The linked-field end-corner record restates six more
        # linked arm members naming the inline-toolbar token — the three
        # `.inline-toolbar button…` end members and the three
        # `toolbar.inline-toolbar toolbutton…` end members — all pinned
        # with the other linked-field spellings by
        # test_gtk_theme_linked.TestGtkThemeLinked::
        # test_linked_end_field_corners.
        self.assertEqual(
            {s for s in self.rules if "inline-toolbar" in s},
            {".inline-toolbar",
             ".inline-toolbar button:first-child",
             ".inline-toolbar button:last-child",
             ".inline-toolbar button:only-child",
             "toolbar.inline-toolbar toolbutton:first-child > button.flat",
             "toolbar.inline-toolbar toolbutton:last-child > button.flat",
             "toolbar.inline-toolbar toolbutton:only-child > button.flat"},
        )
        self.assertEqual({s for s in self.rules if "keycap" in s}, {".keycap"})
        # The four marked-scale fine-tune thumb arms also name
        # the token and are pinned with the marked-scale thumbs by
        # test_gtk_theme.TestGtkTheme.test_marked_scale_thumb_arms; the
        # fine-tuned container geometry restatement adds the
        # two orientation container spellings, pinned by
        # test_gtk_theme_scale.TestGtkThemeScale::
        # test_scale_fine_tune_container_geometry; and the
        # marked-node geometry restatement adds the six fine-tuned tick
        # margin and minimum spellings, pinned by
        # test_gtk_theme_scale.TestGtkThemeScale::
        # test_scale_marks_indicator_geometry.
        self.assertEqual(
            {s for s in self.rules if "fine-tune" in s},
            {
                "scale.fine-tune fill",
                "scale.fine-tune highlight",
                "scale.fine-tune trough",
                "scale.fine-tune.horizontal",
                "scale.fine-tune.vertical",
                "scale.horizontal.marks-before:not(.marks-after).fine-tune slider",
                "scale.horizontal.marks-after:not(.marks-before).fine-tune slider",
                "scale.vertical.marks-before:not(.marks-after).fine-tune slider",
                "scale.vertical.marks-after:not(.marks-before).fine-tune slider",
                "scale.horizontal.fine-tune marks.top",
                "scale.horizontal.fine-tune marks.bottom",
                "scale.vertical.fine-tune marks.top",
                "scale.vertical.fine-tune marks.bottom",
                "scale.horizontal.fine-tune indicator",
                "scale.vertical.fine-tune indicator",
            },
        )
        self.assertEqual(
            {s for s in self.rules if "emoji" in s},
            {
                "popover.emoji-picker .emoji :hover",
                "button.emoji-section label",
                "button.emoji-section:hover label",
            },
        )
        for selector in (
            "button.emoji-section label",
            "button.emoji-section:hover label",
        ):
            with self.subTest(selector=selector, after="modelbutton.flat"):
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("modelbutton.flat"),
                )
        # Source order: every appended spelling sits after the existing
        # modelbutton restatement near the sheet tail, so the byte-equal
        # stock twins win the equal-specificity ties under the lower-sheet
        # reading of how the toolkit resource competes.
        for selector in selectors:
            with self.subTest(selector=selector, after="modelbutton.flat"):
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("modelbutton.flat"),
                )


if __name__ == "__main__":
    unittest.main()
