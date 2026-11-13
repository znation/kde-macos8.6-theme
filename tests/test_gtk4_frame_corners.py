"""GTK 4 structural-etch and square-corner declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases


class TestGtk4FrameCorners(Gtk4SheetRuleCases, unittest.TestCase):
    def test_separator(self):
        self.assert_separators()

    def test_paned_handle(self):
        self.assert_paned_handles()

    def test_paned_handle_stock_clearances(self):
        # Exact stock twins from Default-light.css (libgtk-4 4.18.6, probed
        # 2026-10-31) so sheet order decides every tie like the existing
        # image clearances do, plus the :dir margins the existing orientation
        # rules cannot outrank because each :dir arm carries one class more.
        for selector in (
            "paned > separator",
            "paned > separator:selected",
            "paned > separator.wide",
        ):
            self.assert_rule(selector, {"background-image": "none"})
        for selector in (
            "paned.horizontal > separator:dir(ltr)",
            "paned.horizontal > separator:dir(rtl)",
        ):
            self.assert_rule(selector, {"margin": "0", "padding": "0"})

    def test_frame(self):
        self.assert_frame(("frame > border", ".frame"))

    def test_shortcut_keycap_corners(self):
        self.assertEqual(
            {selector for selector in self.rules if "keycap" in selector},
            {"shortcut > .keycap"},
        )
        self.assert_square_corner("shortcut > .keycap")

    def test_card_corners(self):
        expected = {
            ".card",
            "menubutton.card > button",
            # The card focus arms restate the stock focus
            # colour, not radius, and test_card_focus_outline_color pins
            # them; they join this scan because they carry ``.card``.
            "tabthumbnail .card picture",
            "tabgrid > tabgridchild .card",
            "tabgrid > tabgridchild:focus:focus-visible .card",
            "button.card:focus:focus-visible",
            ".card:focus:focus-visible",
        }
        self.assertEqual(
            {selector for selector in self.rules if ".card" in selector},
            expected,
        )
        for selector in (".card", "menubutton.card > button"):
            with self.subTest(selector=selector):
                self.assert_square_corner(selector)

    def test_flowbox_item_corners(self):
        expected = {
            "flowbox > flowboxchild",
            # The selected view-child restatement names the same node.
            # The disabled-selected restatement names it again.
            "flowbox > flowboxchild:selected",
            "flowbox > flowboxchild:disabled:selected",
            "flowbox > flowboxchild:focus:focus-visible",
            # The rubberband view-specific recipe names this node.
            "flowbox > rubberband",
            # The disabled-view ink arm names the view class.
            "flowbox.view:disabled",
        }
        self.assertEqual(
            {selector for selector in self.rules if selector.startswith("flowbox")},
            expected,
        )
        self.assertEqual(
            self.rules["flowbox > flowboxchild"],
            {"border-radius": "0", "transition": "none"},
        )
        self.assert_matches_frame("flowbox > flowboxchild", "border-radius")

    def test_gridview_item_corners(self):
        expected = {
            "gridview > child",
            "filechooser gridview > child",
            "gridview > child:focus:focus-visible",
            # The filechooser undershoot mirror names the same view substring.
            "filechooser gridview ~ undershoot.top",
            # The selected view-child restatement names the same nodes.
            # The disabled-selected restatement names it again.
            "gridview > child:selected",
            "gridview > child:disabled:selected",
            # The rubberband view-specific recipe names this node.
            "gridview > rubberband",
            "filechooser gridview child:selected",
            "filechooser gridview child:selected:hover",
            "filechooser gridview child:selected:active",
            # The disabled-view ink arms name the view class and
            # the print action box.
            "gridview.view:disabled",
            "window.print:not(.ssd-frame) gridview.dialog-action-box:disabled",
        }
        self.assertEqual(
            {selector for selector in self.rules if "gridview" in selector},
            expected,
        )
        for selector in sorted(
            {"gridview > child", "filechooser gridview > child"}
        ):
            with self.subTest(selector=selector):
                self.assertEqual(
                    self.rules[selector],
                    {"border-radius": "0", "transition": "none"},
                )
                self.assert_matches_frame(selector, "border-radius")



if __name__ == "__main__":
    unittest.main()
