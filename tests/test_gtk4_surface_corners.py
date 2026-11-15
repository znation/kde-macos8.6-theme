"""GTK 4 surface-corner declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.platinum_palette import SELECTION


class TestGtk4SurfaceCorners(Gtk4SheetRuleCases, unittest.TestCase):
    def test_residual_radius_corners(self):
        # The 2026-11-04 residual-corner row squares the last seven
        # radius-bearing stock widget faces no existing restatement reaches:
        # the eight byte-equal spellings in one tail comma group (the
        # about-dialog version pill carries two node arms stock splits in
        # its own comma group, so eight selectors serve seven faces).
        selectors = {
            "avatar",
            "scale.horizontal.marks-before.marks-after > trough > slider",
            "scale.color > trough",
            "colorchooser .popover.osd",
            "shortcut",
            "window.about .main-page .app-version",
            "dialog.about .main-page .app-version",
            ".accent-color-row color",
        }
        for selector in sorted(selectors):
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, {"border-radius": "0"})
                self.assert_matches_frame(selector, "border-radius")
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("indicatorbin > mask"),
                )
        # Family sweeps on the distinctive tokens no existing selector
        # carries; the shortcut shell settles for the whole-dict and
        # count-1 guard above because the token already names the existing
        # keycap and focus spellings.
        self.assertEqual(
            {selector for selector in self.rules if "avatar" in selector},
            {"avatar"},
        )
        self.assertEqual(
            {selector for selector in self.rules if "app-version" in selector},
            {
                "window.about .main-page .app-version",
                "dialog.about .main-page .app-version",
            },
        )
        self.assertEqual(
            {selector for selector in self.rules if "scale.color" in selector},
            {"scale.color > trough"},
        )
        self.assertEqual(
            {selector for selector in self.rules if "popover.osd" in selector},
            {"colorchooser .popover.osd"},
        )
        self.assertEqual(
            {selector for selector in self.rules if "accent-color-row" in selector},
            {".accent-color-row color"},
        )
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if "marks-before.marks-after" in selector
            },
            {"scale.horizontal.marks-before.marks-after > trough > slider"},
        )

    def test_alert_dialog_corners(self):
        # The 2026-11-04 alert-dialog comment block appends six
        # stock-comma groups after the existing cursor-handle tail group;
        # the sheet parser splits each comma group into per-selector keys,
        # nine in all (the legacy .dialog-action-area keys from the existing
        # message-dialog records join the action-area prefix scan below).
        members = {
            "window.dialog.message.csd:not(.solid-csd)": {"border-radius": "0"},
            "window.dialog.message.csd .dialog-action-area > button": {
                "border-radius": "0"
            },
            "window.messagedialog .response-area > button": {"border-radius": "0"},
            "dialog.alert .response-area > button": {"border-radius": "0"},
            "dialog-host > dialog.alert sheet": {"border-radius": "0"},
            "window.messagedialog.csd:not(.solid-csd)": {"border-radius": "0"},
            "window.dialog-window.alert.csd:not(.solid-csd)": {"border-radius": "0"},
            "dialog-host > dialog.alert sheet .body-scrolled-window > viewport": {
                "border-top-left-radius": "0",
                "border-top-right-radius": "0",
            },
            "window.dialog-window.alert .body-scrolled-window > viewport": {
                "border-top-left-radius": "0",
                "border-top-right-radius": "0",
            },
        }
        self.assertEqual(
            {s for s in self.rules if s.startswith("window.messagedialog")},
            {
                "window.messagedialog .response-area > button",
                "window.messagedialog.csd:not(.solid-csd)",
            },
        )
        self.assertEqual(
            {s for s in self.rules if "dialog.alert" in s},
            {
                "dialog.alert .response-area > button",
                "dialog-host > dialog.alert sheet",
                "dialog-host > dialog.alert sheet .body-scrolled-window > viewport",
            },
        )
        self.assertEqual(
            {s for s in self.rules if "dialog-window" in s},
            {
                "window.dialog-window.alert.csd:not(.solid-csd)",
                "window.dialog-window.alert .body-scrolled-window > viewport",
            },
        )
        # The 2026-11-04 selection-surface record's two compound dialog-host
        # spellings joined this family scan, and the same-day disabled-view
        # record's two sheet spellings join them beside it.
        self.assertEqual(
            {s for s in self.rules if "dialog-host" in s},
            {
                "dialog-host > dialog.alert sheet",
                "dialog-host > dialog.alert sheet .body-scrolled-window > viewport",
                "dialog-host > dialog.view sheet:selected",
                "window.print:not(.ssd-frame) dialog-host > "
                "dialog.dialog-action-box sheet:selected",
                "dialog-host > dialog.view sheet:disabled",
                "window.print:not(.ssd-frame) dialog-host > "
                "dialog.dialog-action-box sheet:disabled",
            },
        )
        self.assertEqual(
            {
                s
                for s in self.rules
                if s.startswith("window.dialog.message.csd .dialog-action-area")
            },
            {
                "window.dialog.message.csd .dialog-action-area button",
                "window.dialog.message.csd .dialog-action-area button:first-child",
                "window.dialog.message.csd .dialog-action-area button:last-child",
                "window.dialog.message.csd .dialog-action-area > button",
            },
        )
        # The frame rule states the corner through the radius shorthand, so
        # the viewport longhand members match the frame's border-radius
        # value per corner against that shared zero instead of against a
        # longhand the frame rule never declares.
        for selector, rule in members.items():
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, rule)
                if "border-radius" in rule:
                    self.assert_matches_frame(selector, "border-radius")
                for prop in rule:
                    self.assertEqual(
                        self.rules[selector][prop],
                        self.rules["frame > border"]["border-radius"],
                    )
        for selector in members:
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("cursor-handle > contents"),
            )

    def test_selection_surface_corners(self):
        # The 2026-11-04 selection-surface comment block appends one
        # three-selector comma group after the existing spin-button axis
        # chains at the sheet tail; the sheet parser splits it into
        # per-selector keys. These three compound spellings are the
        # members of stock's selected-view comma arm that the existing
        # class-only .view:selected restatement, the icon-view group and
        # the row groups lose the specificity tie against, so stock's
        # 9px-rounded selected face paints them until this group restates
        # the zero the existing square-corner policy carries everywhere but
        # the radio circle. The 2026-11-04 palette half extends the same
        # group in place: each member's block carries the flat opaque
        # #CCCCFF selection fill above the zero radius, so stock's
        # accent-tinted quarter-accent mix — fed the shipped
        # accent_bg_color — no longer leaves 75% of the underlying view
        # field showing through, and the parse union keeps both keys.
        members = {
            "window.print:not(.ssd-frame) .dialog-action-box:selected": {
                "background-color": "#CCCCFF",
                "border-radius": "0",
            },
            "dialog-host > dialog.view sheet:selected": {
                "background-color": "#CCCCFF",
                "border-radius": "0",
            },
            "window.print:not(.ssd-frame) dialog-host > "
            "dialog.dialog-action-box sheet:selected": {
                "background-color": "#CCCCFF",
                "border-radius": "0",
            },
        }
        # The token sweeps key on substrings no existing selector carries:
        # both sheet spellings alone carry "sheet:selected", and the print
        # action-box spelling alone carries "dialog-action-box:selected".
        self.assertEqual(
            {s for s in self.rules if "sheet:selected" in s},
            {
                "dialog-host > dialog.view sheet:selected",
                "window.print:not(.ssd-frame) dialog-host > "
                "dialog.dialog-action-box sheet:selected",
            },
        )
        self.assertEqual(
            {s for s in self.rules if "dialog-action-box:selected" in s},
            {"window.print:not(.ssd-frame) .dialog-action-box:selected"},
        )
        for selector, rule in members.items():
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, rule)
                self.assert_matches_frame(selector, "border-radius")
                # The existing frame pair declares no background-color, so
                # the fill anchors to the pinned SELECTION constant the
                # existing .view, row and icon-view selection tests use.
                self.assertEqual(rule["background-color"], SELECTION)
        for selector in members:
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index(
                    "spinbutton.vertical > button.image-button.down"
                    ":not(.flat):not(.raised):not(.suggested-action)"
                    ":not(.destructive-action):not(.opaque):first-child"
                ),
            )

    def test_sheet_widget_corners(self):
        # The 2026-11-04 sheet-widget comment block appends three groups
        # after the existing expander-title tail group; stock's three radius
        # arms share these six selector strings across the two sheet
        # widget families, so byte-equal restatements square them all while
        # stock's transitions, shadows, outline, fill, min sizes and
        # margins stay inherited per-property.
        bottom_sheet = {
            "bottom-sheet > sheet",
            "bottom-sheet > sheet > outline",
            "bottom-sheet > sheet > stack > widget",
            "bottom-sheet > sheet > stack > button",
            "bottom-sheet > sheet > stack > button > widget",
            "bottom-sheet > sheet > stack > widget > drag-handle",
        }
        self.assertEqual(
            {s for s in self.rules if s.startswith("bottom-sheet")},
            bottom_sheet,
        )
        self.assertEqual(
            {s for s in self.rules if s.startswith("floating-sheet")},
            {"floating-sheet > sheet"},
        )
        for selector in bottom_sheet | {"floating-sheet > sheet"}:
            self.assertEqual(self.selectors.count(selector), 1)
        for selector in (
            "bottom-sheet > sheet",
            "bottom-sheet > sheet > outline",
            "bottom-sheet > sheet > stack > widget",
            "bottom-sheet > sheet > stack > button",
            "bottom-sheet > sheet > stack > button > widget",
        ):
            with self.subTest(selector=selector):
                self.assertEqual(
                    self.rules[selector],
                    {
                        "border-top-left-radius": "0",
                        "border-top-right-radius": "0",
                    },
                )
                # The frame rule states the corner through the radius
                # shorthand, so each longhand member matches the frame's
                # shared zero instead of a longhand the frame rule never
                # declares.
                for corner in (
                    "border-top-left-radius",
                    "border-top-right-radius",
                ):
                    self.assertEqual(
                        self.rules[selector][corner],
                        self.rules["frame > border"]["border-radius"],
                    )
        for selector in (
            "bottom-sheet > sheet > stack > widget > drag-handle",
            "floating-sheet > sheet",
        ):
            with self.subTest(selector=selector):
                self.assert_square_corner(selector)
        for selector in sorted(bottom_sheet | {"floating-sheet > sheet"}):
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("expander-widget > box > title"),
            )


if __name__ == "__main__":
    unittest.main()
