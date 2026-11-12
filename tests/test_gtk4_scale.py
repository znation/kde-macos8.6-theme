"""GTK 4 scale declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import SCALE_FOCUS, SCALE_SLIDER, Gtk4SheetRuleCases
from support.gtk_theme_spec import BUTTON_BEVEL, RAISED_BEVEL
from support.platinum_palette import BLACK, FACE, TROUGH


class TestGtk4Scale(Gtk4SheetRuleCases, unittest.TestCase):
    def test_scale_focus_outline_color(self):
        focus = SCALE_FOCUS
        self.assert_rule(focus, {"outline-color": BLACK})
        self.assertEqual(
            self.rules[focus]["outline-color"],
            self.rules["calendar > grid > label:focus"]["outline-color"],
        )

    def test_scale_focus_transition(self):
        self.assert_rule(SCALE_SLIDER, {"transition": "none"})

    def test_scale_popup_buttons(self):
        """Clear the stock rounded scale-popup button overrides.

        No collected reference screenshot shows a GTK scale popup, so the
        sheet restates the toolkit resource's stock arms (probed from
        Default-light.css in libgtk-4 4.18.6) with the existing plain
        push-button recipe (the base ``button`` dictionary pinned by
        ``support.gtk_rule_cases.py::GtkSheetRuleCases::test_button``).
        The recipe is restated in full at each arm because this sheet has
        no restated ``.osd button.flat`` family: the stock
        ``.osd button``/``button.flat`` arms claim a transparent face and
        border and no bevel at (0,2,1)/(0,1,1), outranking the existing
        base ``button`` group's (0,0,1) face, border and bevel.
        """
        recipe = {
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
        self.assertEqual(self.rules[".osd .scale-popup button.flat"], recipe)
        self.assertEqual(self.rules[".scale-popup button:hover"], recipe)
        self.assertEqual(
            {selector for selector in self.rules
             if "scale-popup" in selector and "button" in selector},
            {".osd .scale-popup button.flat", ".scale-popup button:hover"},
        )

    def test_scale_marks_value_ink(self):
        """Scale tick marks and the value label read the existing black ink.

        The toolkit dilutes both through `currentColor`-alpha arms; the
        restated comma group wins the per-property tie under lower-sheet
        riding, and the marks indicators follow their `currentColor` fill.
        """
        self.assert_rule_group(
            {
                "scale > value": {"color": BLACK},
                "scale.horizontal > marks": {"color": BLACK},
                "scale.vertical > marks": {"color": BLACK},
            }
        )
        self.assertEqual(
            {
                selector
                for selector in self.selectors
                if selector.startswith("scale")
                and (
                    "value" in selector
                    or (
                        "marks" in selector
                        and "marks-" not in selector
                        and "slider" not in selector
                    )
                )
            },
            {
                "scale > value",
                "scale.horizontal > marks",
                "scale.vertical > marks",
                "scale.horizontal > marks.top",
                "scale.horizontal > marks.bottom",
                "scale.horizontal > marks indicator",
                "scale.horizontal:not(.marks-before) > value.top",
                "scale.horizontal:not(.marks-after) > value.bottom",
                "scale.horizontal > value.left",
                "scale.horizontal > value.right",
                "scale.horizontal.fine-tune > marks.top",
                "scale.horizontal.fine-tune > marks.bottom",
                "scale.horizontal.fine-tune > marks indicator",
                "scale.vertical > marks.top",
                "scale.vertical > marks.bottom",
                "scale.vertical > marks indicator",
                "scale.vertical:not(.marks-before) > value.left",
                "scale.vertical:not(.marks-after) > value.right",
                "scale.vertical > value.top",
                "scale.vertical > value.bottom",
                "scale.vertical.fine-tune > marks.top",
                "scale.vertical.fine-tune > marks.bottom",
                "scale.vertical.fine-tune > marks indicator",
            },
        )
        self.assert_rule_after("switch {", "scale > value,")

    def test_scale_horizontal_marks_value_allocation(self):
        """A plain or fine-tuned horizontal marked scale keeps the toolkit's own allocation.

        The toolkit's ten horizontal arms (push-out margins, tick
        minimums, value-label orientation margins, fine-tune halves) are
        restated byte-equal behind this block, so both cascade loading
        readings carry the same spacing — the keep-both-readings parity
        restate the existing plain-container record set, with the indicator
        currentColor member carried byte-equal so the arm survives the
        replacement reading too.
        """
        self.assert_rule_group(
            {
                "scale.horizontal > marks.top": {"margin-bottom": "6px"},
                "scale.horizontal > marks.bottom": {"margin-top": "6px"},
                "scale.horizontal > marks indicator": {
                    "background-color": "currentColor",
                    "min-height": "6px",
                    "min-width": "1px",
                },
                "scale.horizontal:not(.marks-before) > value.top": {
                    "margin-bottom": "12px"
                },
                "scale.horizontal:not(.marks-after) > value.bottom": {
                    "margin-top": "12px"
                },
                "scale.horizontal > value.left": {"margin-right": "9px"},
                "scale.horizontal > value.right": {"margin-left": "9px"},
                "scale.horizontal.fine-tune > marks.top": {"margin-top": "3px"},
                "scale.horizontal.fine-tune > marks.bottom": {
                    "margin-bottom": "3px"
                },
                "scale.horizontal.fine-tune > marks indicator": {
                    "min-height": "3px"
                },
            }
        )
        self.assert_rule_after("scale.horizontal > marks.top {", "scale > value,")
        self.assert_rule_after(
            "switch {", "scale.horizontal.fine-tune > marks indicator {"
        )

    def test_scale_vertical_marks_value_allocation(self):
        """A plain or fine-tuned vertical marked scale keeps the toolkit's own allocation.

        The toolkit's ten vertical arms (push-out margins, tick
        minimums, value-label orientation margins, fine-tune halves) are
        restated byte-equal behind this block, so both cascade loading
        readings carry the same spacing — the keep-both-readings parity
        restate the existing plain-container record set, companion to the
        horizontal twin block above, with the indicator currentColor
        member carried byte-equal so the arm survives the replacement
        reading too.
        """
        self.assert_rule_group(
            {
                "scale.vertical > marks.top": {"margin-right": "6px"},
                "scale.vertical > marks.bottom": {"margin-left": "6px"},
                "scale.vertical > marks indicator": {
                    "background-color": "currentColor",
                    "min-height": "1px",
                    "min-width": "6px",
                },
                "scale.vertical:not(.marks-before) > value.left": {
                    "margin-right": "12px"
                },
                "scale.vertical:not(.marks-after) > value.right": {
                    "margin-left": "12px"
                },
                "scale.vertical > value.top": {"margin-bottom": "9px"},
                "scale.vertical > value.bottom": {"margin-top": "9px"},
                "scale.vertical.fine-tune > marks.top": {
                    "margin-left": "3px"
                },
                "scale.vertical.fine-tune > marks.bottom": {
                    "margin-right": "3px"
                },
                "scale.vertical.fine-tune > marks indicator": {
                    "min-width": "3px"
                },
            }
        )
        self.assert_rule_after(
            "scale.vertical > marks.top {",
            "scale.horizontal.fine-tune > marks indicator {",
        )
        self.assert_rule_after(
            "switch {", "scale.vertical.fine-tune > marks indicator {"
        )

    def test_scale(self):
        self.assert_scale(
            trough="scale > trough",
            fill=("scale > trough > fill", "scale > trough > highlight"),
            slider="scale > trough > slider",
            horizontal="scale.horizontal > trough > slider",
            vertical="scale.vertical > trough > slider",
            disabled="scale > trough > slider:disabled",
        )

    def test_scale_plain_container_geometry(self):
        """The plain (non-fine-tuned) scale node keeps stock's allocation.

        The toolkit's arm on the sheet's only bare `scale` spelling
        carries the 10px transverse node minimums, the 12px push-out
        padding and the stock outline-motion riders; the sheet restates
        the arm byte-equal so a plain scale's container allocation stays
        unchanged under either loading reading. The whole-dict read and
        the occurrence count kill a dropped or changed member, an added
        member, a split grouping and any second bare rule; the compound
        sweep kills a duplicate padding declaration hidden behind a
        descendant or state-armed `scale `-prefixed spelling.
        """
        expected = {
            "min-height": "10px",
            "min-width": "10px",
            "padding": "12px",
            "transition-property": (
                "outline, outline-width, outline-offset, outline-color"
            ),
            "transition-duration": "300ms",
            "animation-timing-function": "ease-in-out",
        }
        # (a) The bare spelling carries exactly the stock members,
        # appearing exactly once in the sheet.
        self.assert_rule_group({"scale": expected})
        # (b) The whole-sheet sweep: no second bare rule or a restate
        # split across groups can hold `scale` again.
        self.assertEqual(self.selectors.count("scale"), 1)
        # (c) The compound sweep: no descendant or state-armed spelling
        # starting `scale ` re-declares a container padding member.
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("scale ") and "padding" in self.rules.get(s, {})
            },
            set(),
        )

    def test_scale_fine_tune_thumb_margin(self):
        for selector in (
            "scale.horizontal.fine-tune > trough > slider",
            "scale.vertical.fine-tune > trough > slider",
        ):
            self.assert_rule(selector, {"margin": "-5px"})

    def test_scale_fine_tune_trough_margin(self):
        for selector in (
            "scale.horizontal.fine-tune > trough",
            "scale.vertical.fine-tune > trough",
        ):
            self.assert_rule(selector, {"margin": "0"})

    def test_scale_fine_tune_radius(self):
        """A held modifier never re-rounds the scale's existing square faces.

        The toolkit's `scale.fine-tune` radius arm re-rounds the trough,
        fill and highlight with border-radius: 5px while the modifier is
        held; the sheet restates the group byte-equal with a zero radius
        so a fine-tuned scale stays on the existing square-corner policy
        under either loading reading. The whole-dict read kills a restored
        stock 5px, a dropped or extra member and any second rule reusing a
        spelling; the family sweep kills renames, state-armed twins and
        strays; the raw-text order pins keep the restate between the
        existing fine-tune trough-margin group and the existing parent-state
        trough-face group.
        """
        radius_spellings = (
            "scale.fine-tune > trough > fill",
            "scale.fine-tune > trough > highlight",
            "scale.fine-tune > trough",
        )
        # (a) The three comma-group members each carry exactly the one
        # declaration, appearing exactly once in the sheet.
        self.assert_rule_group(
            dict.fromkeys(radius_spellings, {"border-radius": "0"})
        )
        # (b) The sweep: the bare `scale.fine-tune` prefix selects exactly
        # these three spellings — a restored state twin, an orientation
        # suffix (`scale.horizontal.fine-tune...` from the existing margin
        # groups does not satisfy the bare prefix) or a renamed spelling
        # fails before any value is read.
        self.assertEqual(
            {s for s in self.selectors if s.startswith("scale.fine-tune")},
            set(radius_spellings),
        )
        # (c) Order pins on raw sheet text: the restate sits directly
        # after the existing fine-tune trough-margin group and before the
        # existing parent-state trough-face comma-group start.
        self.assert_rule_after(
            "scale.fine-tune > trough > fill,\n"
            "scale.fine-tune > trough > highlight,\n"
            "scale.fine-tune > trough {",
            "scale.vertical.fine-tune > trough {",
        )
        self.assert_rule_after(
            "scale:hover > trough,",
            "scale.fine-tune > trough > highlight,\nscale.fine-tune > trough {",
        )

    def test_scale_marked_thumb_transform(self):
        for selector in (
            "scale.marks-before:not(.marks-after) > trough > slider",
            "scale.marks-after:not(.marks-before) > trough > slider",
        ):
            self.assert_rule(selector, {"transform": "none"})

    def test_scale_enabled_marked_thumb_shadow(self):
        for selector in (
            "scale.marks-before:not(.marks-after):not(:disabled) > trough > slider:not(:disabled)",
            "scale.marks-after:not(.marks-before):not(:disabled) > trough > slider:not(:disabled)",
        ):
            self.assert_rule(selector, {"box-shadow": RAISED_BEVEL})

    def test_scale_disabled_filter(self):
        self.assert_rule("scale:disabled", {"filter": "none"})
        self.assertEqual(self.rules["scale:disabled"], {"filter": "none"})

    def test_scale_disabled_parent_shadow(self):
        self.assert_rule("scale:disabled > trough > slider", {"box-shadow": "none"})

    def test_scale_disabled_marked_thumb_shadow(self):
        for selector in (
            "scale.marks-before:not(.marks-after) > trough > slider:disabled",
            "scale.marks-after:not(.marks-before) > trough > slider:disabled",
            "scale.marks-before:not(.marks-after):disabled > trough > slider",
            "scale.marks-after:not(.marks-before):disabled > trough > slider",
        ):
            self.assert_rule(selector, {"box-shadow": "none"})

    def test_scale_parent_interaction_face(self):
        for selector in (
            "scale:hover > trough > slider",
            "scale:active > trough > slider",
        ):
            self.assert_rule(selector, {"background-color": FACE})

    def test_scale_parent_interaction_trough_face(self):
        for selector in ("scale:hover > trough", "scale:active > trough"):
            self.assert_rule(selector, {"background-color": TROUGH})

    def test_scale_parent_interaction_highlight_image(self):
        for selector in (
            "scale:hover > trough > highlight",
            "scale:active > trough > highlight",
        ):
            self.assert_rule(selector, {"background-image": "none"})


if __name__ == "__main__":
    unittest.main()
