"""GTK 4 tabbar declaration checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases, SCALE_SLIDER


class TestGtk4Tabbar(Gtk4SheetRuleCases, unittest.TestCase):
    def test_tabbar_backdrop_filter(self):
        value = self.rules["switch:disabled"]["filter"]
        for selector in (
            "tabbar .box:backdrop > scrolledwindow",
            "tabbar .box:backdrop > .start-action",
            "tabbar .box:backdrop > .end-action",
        ):
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"filter": "none"})
                self.assertEqual(self.rules[selector]["filter"], value)

    def test_tabbar_tab_and_indicator_corners(self):
        """The stock tab-family radii answer the square-corner policy.

        The sheet restates ten byte-equal stock spellings plus
        the extended tab-box base: eleven border-radius-zero selectors, each
        counted once, each matching both frame arms' radius, with the two
        family scans and the source-order span killing renamed and stray
        variants.
        """
        selectors = (
            "tabbar tab",
            "dnd tab",
            "tabbar tab button.image-button",
            "dnd tab button.image-button",
            "tabbar tab indicator",
            "dnd tab indicator",
            "tabbar tabbox > revealer > indicator",
            "tabthumbnail button",
            "tabthumbnail button > image",
            "tabthumbnail .needs-attention > widget",
            # The extended base group also keeps its existing no-transition.
            "tabbar tabbox > tabboxchild",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_matches_frame(selector, "border-radius")
        self.assertEqual(
            self.rules["tabbar tabbox > tabboxchild"],
            {"border-radius": "0", "transition": "none"},
        )
        # Family scans kill renamed and stray variants. The parsed sheet
        # splits every comma group into per-member selector keys, so the
        # "dnd tab" substring scan reaches only the three dnd members and the
        # exact "tabbar tab" token scans reach the three tabbar members;
        # together the two scans cover all six pair members.
        self.assertEqual(
            {selector for selector in self.rules if "dnd tab" in selector},
            {
                "dnd tab",
                "dnd tab button.image-button",
                "dnd tab indicator",
            },
        )
        self.assertEqual(
            {selector for selector in self.rules
             if selector == "tabbar tab"
             or selector.startswith("tabbar tab ")},
            {
                "tabbar tab",
                "tabbar tab button.image-button",
                "tabbar tab indicator",
            },
        )
        self.assertEqual(
            {selector for selector in self.rules
             if "tabthumbnail button" in selector},
            {"tabthumbnail button", "tabthumbnail button > image"},
        )
        self.assertEqual(
            {selector for selector in self.rules
             if "revealer > indicator" in selector},
            {"tabbar tabbox > revealer > indicator"},
        )
        # Source order: the tab seam restatements sit after the existing tabgrid
        # focus arm and before the stack switcher face.
        self.assertGreater(
            self.selectors.index("dnd tab"),
            self.selectors.index(
                "tabgrid > tabgridchild:focus:focus-visible .card"),
        )
        self.assertLess(
            self.selectors.index("dnd tab"),
            self.selectors.index("stackswitcher > button"),
        )

    def test_tabbar_tabboxchild_focus(self):
        base = "tabbar tabbox > tabboxchild"
        focus = "tabbar tabbox > tabboxchild:focus-within:focus-visible"
        self.assertEqual(
            self.rules[base], {"border-radius": "0", "transition": "none"})
        self.assertEqual(
            self.rules[base]["transition"],
            self.rules[SCALE_SLIDER]["transition"],
        )
        self.assert_scale_focus_outline(focus)
        for selector in (base, focus):
            self.assertEqual(self.selectors.count(selector), 1)
        self.assertEqual(
            {selector for selector in self.rules if "tabboxchild" in selector},
            {base, focus},
        )
        self.assertGreater(
            self.selectors.index(focus),
            self.selectors.index("tabbar .box:backdrop > scrolledwindow"),
        )
        self.assertLess(
            self.selectors.index(focus),
            self.selectors.index("stackswitcher > button"),
        )

if __name__ == "__main__":
    unittest.main()
