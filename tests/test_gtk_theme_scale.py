"""Validate the GTK 3 Platinum sheet's scale geometry and ink.

This module owns the scale slice split out of the former GTK 3 controls suite:
the shared scale spec, the scale focus outline, the plain and fine-tuned
container geometry, the marks indicator geometry, and the tick-mark and
value-label ink. None of these tests renders; the sheet rules are read from
the stripped CSS through ``GtkSheetRuleCases``.
"""

import unittest
from pathlib import Path

from support.gtk_css import strip_comments
from support.gtk_rule_cases import GtkSheetRuleCases
from support.platinum_palette import BLACK
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"


class TestGtkThemeScale(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_scale(self):
        self.assert_scale(
            trough="scale trough",
            fill=("scale fill", "scale highlight"),
            slider="scale slider",
            horizontal="scale.horizontal slider",
            vertical="scale.vertical slider",
            disabled="scale slider:disabled",
        )

    def test_scale_decoration_ink(self):
        """A scale's tick marks and readout paint the existing window ink.

        The existing group sits directly after the existing backdrop-disabled
        slider twin and before the existing selected-row slider twin, so the
        single repainted member reads through the toolkit's stock ink arm
        in every state the bare pair reaches. Assert each spelling once,
        whole-driven, family-clean and in the existing group order.
        """
        # The parser stores comma-group members individually, so the
        # whole-dict assertion pins the two spellings the group declares,
        # each exactly once, and the stripped sheet's single comma-spelled
        # group kills a split into bare spelling blocks.
        self.assert_rule_group(
            {"scale marks": {"color": BLACK}, "scale value": {"color": BLACK}}
        )
        self.assertEqual(
            strip_comments(self.css).count("scale marks, scale value {"), 1
        )
        # Order pins: the pair group reads later than the backdrop-disabled
        # slider twin it follows and earlier than the selected-row slider
        # twin it precedes in the existing sheet order.
        self.assert_rule_after(
            "scale marks, scale value {", "scale slider:backdrop:disabled {"
        )
        self.assert_rule_after(
            "row:selected scale slider:disabled, row:selected scale slider {",
            "scale marks, scale value {",
        )
        # No renamed, stray or state-armed marks/value spelling exists: the
        # family sweeps admit only the group's two members.
        self.assertEqual(
            {s for s in self.selectors if s.startswith("scale marks")},
            {"scale marks"},
        )
        self.assertEqual(
            {s for s in self.selectors if s.startswith("scale value")},
            {"scale value"},
        )

    def test_scale_focus_outline(self):
        self.assert_rule(
            "scale:focus",
            {
                "outline": f"1px dotted {BLACK}",
                "outline-offset": "0",
                "-gtk-outline-radius": "0",
            },
        )
        width, style, color = self.rules[".rubberband"]["border"].split()
        self.assertEqual((width, style, color), ("1px", "dotted", BLACK))
        self.assertEqual(self.rules["scale trough"]["border-radius"], "0")

    def test_scale_plain_container_geometry(self):
        """A plain (non-fine-tuned) scale's container keeps stock's geometry.

        The restatement stands directly after the fine-tune radius group
        and directly before the fine-tuned container record, so the plain
        node keeps stock's 10px transverse minimums and its 12px push-out
        padding in both orientations under either loading reading; assert
        the spelling once, whole-driven, family-clean and in record order.
        """
        self.assert_rule_group(
            {
                "scale": {
                    "min-height": "10px",
                    "min-width": "10px",
                    "padding": "12px",
                }
            }
        )
        # Family sweep: no state twin, no rename and no split spelling (the
        # existing scale trough, fill/highlight and slider spellings fail the
        # equality and stay out); the state sweep admits only the existing
        # `scale:focus` record's spelling, so an added `scale:disabled` or
        # `scale:backdrop` bare-node twin dies here too.
        self.assertEqual({s for s in self.selectors if s == "scale"}, {"scale"})
        self.assertEqual(
            {s for s in self.selectors if s.startswith("scale:")},
            {"scale:focus"},
        )
        # Order pins: the container block sits after the fine-tune radius
        # group and the fine-tuned container record follows it, mirroring
        # stock's plain-before-fine-tuned order. The two-operand pins ride
        # first raw-text occurrence; the existing fine-tuned record's comment
        # quotes these spellings, which is why the second pin holds only
        # once this record's own rule exists.
        self.assert_rule_after("scale {", "scale.fine-tune trough {")
        self.assert_rule_after("scale.fine-tune.horizontal {", "scale {")

    def test_scale_fine_tune_container_geometry(self):
        """A fine-tuned scale's container keeps the toolkit's stock geometry.

        The existing restatement stands directly after the fine-tune radius
        group, so both orientations keep stock's 9px transverse paddings
        and 16px transverse minimum under either loading reading; assert
        each spelling once, whole-driven, family-clean and in radius-block
        order.
        """
        self.assert_rule_group(
            {
                "scale.fine-tune.horizontal": {
                    "padding-top": "9px",
                    "padding-bottom": "9px",
                    "min-height": "16px",
                },
                "scale.fine-tune.vertical": {
                    "padding-left": "9px",
                    "padding-right": "9px",
                    "min-width": "16px",
                },
            }
        )
        # Family sweeps: no state twin, no bare-class fallback, no split
        # spelling (the existing .fine-tune slider and fill/highlight/trough
        # spellings do not satisfy the prefixed equality and stay out).
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("scale.fine-tune.horizontal")
            },
            {"scale.fine-tune.horizontal"},
        )
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("scale.fine-tune.vertical")
            },
            {"scale.fine-tune.vertical"},
        )
        # The container block sits beside the existing fine-tune radius
        # group, so its equal-specificity ties win by later source order.
        self.assert_rule_after(
            "scale.fine-tune.horizontal {",
            "scale.fine-tune trough {",
        )

    def test_scale_marks_indicator_geometry(self):
        """A marked scale keeps the toolkit's tick spacing and line sizes.

        The twelve restated arms stand directly before the existing
        marked-scale record, so both orientations keep stock's 6px tick
        push-out with the -12px plain and -9px fine-tuned stop margins and
        the 6px-by-1px plain and 3px fine-tuned indicator minimums under
        either loading reading; assert each spelling once, whole-driven,
        family-clean and in record order.
        """
        self.assert_rule_group(
            {
                "scale.horizontal marks.top": {
                    "margin-bottom": "6px",
                    "margin-top": "-12px",
                },
                "scale.horizontal.fine-tune marks.top": {
                    "margin-bottom": "6px",
                    "margin-top": "-9px",
                },
                "scale.horizontal marks.bottom": {
                    "margin-top": "6px",
                    "margin-bottom": "-12px",
                },
                "scale.horizontal.fine-tune marks.bottom": {
                    "margin-top": "6px",
                    "margin-bottom": "-9px",
                },
                "scale.vertical marks.top": {
                    "margin-right": "6px",
                    "margin-left": "-12px",
                },
                "scale.vertical.fine-tune marks.top": {
                    "margin-right": "6px",
                    "margin-left": "-9px",
                },
                "scale.vertical marks.bottom": {
                    "margin-left": "6px",
                    "margin-right": "-12px",
                },
                "scale.vertical.fine-tune marks.bottom": {
                    "margin-left": "6px",
                    "margin-right": "-9px",
                },
                "scale.horizontal indicator": {
                    "min-height": "6px",
                    "min-width": "1px",
                },
                "scale.horizontal.fine-tune indicator": {
                    "min-height": "3px",
                },
                "scale.vertical indicator": {
                    "min-height": "1px",
                    "min-width": "6px",
                },
                "scale.vertical.fine-tune indicator": {
                    "min-width": "3px",
                },
            }
        )
        # Family sweeps: no renamed spelling, no stray or split member
        # (the existing has-marks slider spellings carry neither token and
        # stay out).
        for token, members in (
            (
                "marks.top",
                (
                    "scale.horizontal marks.top",
                    "scale.horizontal.fine-tune marks.top",
                    "scale.vertical marks.top",
                    "scale.vertical.fine-tune marks.top",
                ),
            ),
            (
                "marks.bottom",
                (
                    "scale.horizontal marks.bottom",
                    "scale.horizontal.fine-tune marks.bottom",
                    "scale.vertical marks.bottom",
                    "scale.vertical.fine-tune marks.bottom",
                ),
            ),
        ):
            self.assertEqual(
                {s for s in self.selectors if token in s}, set(members)
            )
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("scale.h") and s.endswith("indicator")
            },
            {
                "scale.horizontal indicator",
                "scale.horizontal.fine-tune indicator",
            },
        )
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("scale.v") and s.endswith("indicator")
            },
            {
                "scale.vertical indicator",
                "scale.vertical.fine-tune indicator",
            },
        )
        # The block sits after the existing trough group and before the
        # existing marked-scale record's closing group, so its
        # equal-specificity ties win by later source order.
        self.assert_rule_after(
            "scale.vertical.marks-after:not(.marks-before).fine-tune slider {",
            "scale.vertical.fine-tune indicator {",
        )
        self.assert_rule_after("scale.horizontal marks.top {", "scale trough {")


if __name__ == "__main__":
    unittest.main()
