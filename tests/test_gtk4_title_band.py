"""GTK 4 title-button, message-dialog band and headerbar meter checks moved out
of ``test_gtk4_theme``.
"""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import (
    TITLE_BUTTON_ASSETS,
    TITLE_BUTTON_IMAGE,
    TITLE_BUTTON_IMAGE_STATE,
)
from support.platinum_palette import TROUGH


class TestGtk4TitleBand(Gtk4SheetRuleCases, unittest.TestCase):
    def test_title_buttons(self):
        for scope in ("headerbar", ".titlebar"):
            for control, asset in TITLE_BUTTON_ASSETS:
                self.assert_title_button(
                    f"{scope} windowcontrols button.{control}", asset
                )
            self.assert_rule(
                f"{scope} windowcontrols button image", TITLE_BUTTON_IMAGE
            )
            for state in ("hover", "active", "checked"):
                self.assert_rule(
                    f"{scope} windowcontrols button:{state} > image",
                    TITLE_BUTTON_IMAGE_STATE,
                )

    def test_message_dialog_header_band(self):
        # The message dialog's title band repaints the existing headerbar.
        # The band restates the existing headerbar, .titlebar group plus its
        # headerbar-only 1px bottom border, the backdrop band restates the
        # existing headerbar:backdrop, .titlebar:backdrop group, and the
        # dialog body corners go square; tying through the existing groups'
        # dictionaries keeps the bands in step with any future header
        # change.
        self.assert_rule(
            "window.dialog.message .titlebar",
            {**self.rules["headerbar"], "border-width": "0 0 1px 0"},
        )
        self.assert_rule(
            "window.dialog.message .titlebar:backdrop",
            self.rules["headerbar:backdrop"],
        )
        self.assert_rule(
            "window.dialog.message.csd.background",
            {"border-radius": "0"},
        )

    def test_message_dialog_action_area(self):
        # The stock toolkit resource re-pads the message dialog's action
        # buttons to 10px 14px and rounds the end buttons' bottom corners
        # to 7px; the sheet restates the stock button base padding and
        # square corners on both end arms.
        self.assert_rule(
            "window.dialog.message.csd .dialog-action-area button",
            {"padding": "4px 9px"},
        )
        for arm in ("first-child", "last-child"):
            self.assert_rule(
                f"window.dialog.message.csd .dialog-action-area button:{arm}",
                {"border-radius": "0"},
            )

    def test_headerbar_meter_faces(self):
        """A meter embedded in the title band keeps the existing faces.

        Stock's one headerbar-descended meter arm repaints troughs and
        scale fills inside a headerbar with the stock band face; the
        sheet restates the arm's spellings split by existing value so a
        headerbar progress bar or scale keeps the existing `#EEEEEE`
        trough face and the existing transparent fill and highlight
        faces under either loading reading. The whole-dict reads kill
        a stock band value, a dropped or added spelling, a merged
        single group carrying one value and any value drift; the
        occurrence sweep kills a stray twin or per-state split; the
        order pin fixes the block between the existing fill/highlight
        and hover/active highlight groups.
        """
        trough_expected = {"background-color": TROUGH}
        fill_expected = {"background-color": "transparent"}
        self.assert_rule_group(
            {
                "headerbar progressbar > trough": trough_expected,
                "headerbar scale > trough": trough_expected,
                "headerbar scale > trough > fill": fill_expected,
                "headerbar scale > trough > highlight": fill_expected,
            }
        )
        # The whole-sheet sweep: no other headerbar-descended trough,
        # progressbar or scale spelling parses anywhere in the sheet.
        def headerbar_meter_selector(selector):
            tokens = set(selector.replace(">", " ").split())
            return "headerbar" in tokens and tokens & {
                "trough",
                "progressbar",
                "scale",
            }

        self.assertEqual(
            {s for s in self.selectors if headerbar_meter_selector(s)},
            {
                "headerbar progressbar > trough",
                "headerbar scale > trough",
                "headerbar scale > trough > fill",
                "headerbar scale > trough > highlight",
            },
        )
        self.assert_rule_after(
            "headerbar progressbar > trough, headerbar scale > trough {",
            "scale > trough > fill, scale > trough > highlight {",
        )
        self.assert_rule_after(
            "scale:hover > trough > highlight, scale:active > trough > highlight {",
            "headerbar scale > trough > fill, headerbar scale > trough > highlight {",
        )


if __name__ == "__main__":
    unittest.main()
