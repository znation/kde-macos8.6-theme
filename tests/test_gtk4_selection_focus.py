"""GTK 4 selection, focus-outline and cursor-handle declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import SELECTION_CHECK_STATES
from support.platinum_palette import BLACK, SELECTION


class TestGtk4SelectionFocus(Gtk4SheetRuleCases, unittest.TestCase):
    def test_iconview_selected_arms(self):
        """Pin the selected icon view restated off the existing row selection."""
        for selector in (
            "iconview.view:not(:disabled):selected",
            "iconview.view:not(:disabled):selected:focus",
            "iconview.view:not(:disabled):backdrop:selected",
        ):
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {
                        "background-color": SELECTION,
                        "color": BLACK,
                        "border-radius": "0",
                    },
                )
        self.assert_matches_frame("iconview.view:not(:disabled):selected", "border-radius")
        # Exact guarded spellings also prevent overriding disabled selections.
        # The family keeps the existing DND drop border as its only other
        # icon-view rule: a renamed restated arm leaves exactly its successor.
        # 2026-11-05: the tile-check face record restates eight more
        # iconview arms -- the selection-check state faces
        # `iconview.content-view.check…:not(list)` -- all pinned with the
        # other content-view check spellings by test_tile_check_faces.
        states = SELECTION_CHECK_STATES
        self.assertEqual(
            {selector for selector in self.rules if "iconview" in selector},
            {
                "iconview > dndtarget:drop(active)",
                "iconview",
                "iconview:focus:focus-visible",
                "iconview.view:not(:disabled):selected",
                "iconview.view:not(:disabled):selected:focus",
                "iconview.view:not(:disabled):backdrop:selected",
                *(
                    f"iconview.content-view.check{state}:not(list)"
                    for state in states
                ),
            },
        )

    def test_residual_focus_outline_color(self):
        selectors = (
            "label:focus:focus-visible",
            "link:focus:focus-visible",
            "expander-widget:focus:focus-visible > box > title",
            "colorswatch:focus:focus-visible",
            "plane:focus:focus-visible",
            "shortcut:focus:focus-visible",
        )
        self.assert_scale_anchored_focus_outline(selectors)
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"outline-color": BLACK})
        # The existing calendar label arm sits under ``calendar``, the link
        # state arms carry no focus twin, and the label selection arm is a
        # ``:focus-within`` selection rule, so matching ``:focus-visible``
        # pins exactly the six stock twins and rejects renames or strays.
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith(
                    ("label", "link", "colorswatch", "plane", "shortcut",
                     "expander-widget")
                )
                and ":focus-visible" in selector
            },
            set(selectors),
        )

    def test_card_focus_outline_color(self):
        """Pin the card focus arms to the existing black focus colour."""
        selectors = (
            "button.card:focus:focus-visible",
            ".card:focus:focus-visible",
        )
        self.assert_scale_anchored_focus_outline(selectors)
        # The existing tabgrid card arm ends with ``.card``, not
        # ``:focus-visible``, so the two ``:focus-visible``-ending card
        # spellings pin exactly the two stock twins and reject renames,
        # strays or a dropped arm.
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if "card" in selector and selector.endswith(":focus-visible")
            },
            set(selectors),
        )
        # The group closes the sheet after the residual focus group, so the
        # later source order wins every equal-specificity cascade tie.
        self.assertGreater(
            self.selectors.index("button.card:focus:focus-visible"),
            self.selectors.index("shortcut:focus:focus-visible"),
        )

    def test_cursor_handle_corners(self):
        """Pin the cursor-handle contents arm to the square-corner policy."""
        selector = "cursor-handle > contents"
        self.assert_rule(selector, {"border-radius": "0"})
        # The exact whole-rule dictionary catches stray restated geometry,
        # for example a mis-sized replay carrying stock's padding or
        # min-width/min-height into the user group.
        self.assert_square_corner(selector)
        self.assertEqual(self.selectors.count(selector), 1)
        # Stock's base arm and its three orientation twins stay
        # un-replayed: the squared whole-radius declaration makes their
        # per-corner radius cuts no-ops and later user-sheet source order
        # wins the equal-specificity tie, so exactly one cursor-handle
        # group exists and a renamed or orientated replay fails the scan.
        self.assertEqual(
            {s for s in self.rules if "cursor-handle" in s},
            {selector},
        )
        # The group closes the sheet's existing cursor-handle comment block
        # after the residual focus group and the existing card focus colour
        # group, so the later source order wins the equal-specificity
        # cascade tie against the stock resource: the 2026-11-04 alert-dialog
        # comment and corner groups follow it without speaking to any
        # cursor-handle node, so the tie keeps its winner.
        self.assertGreater(
            self.selectors.index("cursor-handle > contents"),
            self.selectors.index("label:focus:focus-visible"),
        )
        self.assertGreater(
            self.selectors.index("cursor-handle > contents"),
            self.selectors.index(".card:focus:focus-visible"),
        )
        self.assertLess(
            self.selectors.index("cursor-handle > contents"),
            self.selectors.index("window.dialog.message.csd:not(.solid-csd)"),
        )

    def test_generic_view_selected_arms(self):
        """Pin the generic view class fallback selection declarations."""
        for selector in (".view:selected", ".view:selected:focus"):
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {
                        "background-color": SELECTION,
                        "color": BLACK,
                        "border-radius": "0",
                    },
                )
        self.assert_matches_frame(".view:selected", "border-radius")
        self.assert_disabled_text((".view:disabled:selected",))
        self.assert_rule(".view:disabled:selected", {"color": "#888888"})

if __name__ == "__main__":
    unittest.main()
