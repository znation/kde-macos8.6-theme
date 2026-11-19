"""Validate GTK 3 Platinum places-sidebar declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.platinum_palette import BLACK, ETCH_DARK, FACE, SELECTION
from support.repo_root import ROOT

CSS = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"


class TestGtkThemeSidebar(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_places_sidebar(self):
        self.assert_rule(".sidebar", {"background-color": FACE, "color": BLACK})
        self.assert_rule(".sidebar:backdrop", {"background-color": FACE, "color": BLACK})
        self.assert_rule("placessidebar row:backdrop", {"color": BLACK})
        self.assert_rule(
            "placessidebar row.activatable:selected:backdrop",
            {"background-color": SELECTION, "color": BLACK},
        )
        self.assert_rule("placessidebar row.sidebar-new-bookmark-row", {"color": BLACK})
        # The drag-session arms restate the stock drop strip and drag-over
        # row twins on the existing selection lavender with black ink;
        # each keeps stock's own geometry members so the byte-equal spelling
        # wins the cascade by later user-sheet source order.
        expected_drop = {
            "placessidebar row.sidebar-placeholder-row": {
                "padding": "0 8px",
                "min-height": "2px",
                "background-image": f"image({SELECTION})",
                "background-clip": "content-box",
            },
            "placessidebar row:drop(active):not(:disabled)": {
                "color": BLACK,
                "box-shadow": f"inset 0 1px {SELECTION}, inset 0 -1px {SELECTION}",
            },
            "placessidebar row:drop(active):not(:disabled):selected": {
                "color": BLACK,
                "background-color": SELECTION,
            },
        }
        self.assert_rule_group(expected_drop)
        self.assertEqual(
            {s for s in self.rules if s.startswith("placessidebar row:drop")},
            {
                "placessidebar row:drop(active):not(:disabled)",
                "placessidebar row:drop(active):not(:disabled):selected",
            },
        )
        anchor = self.css.index(".sidebar {")
        for spelling in expected_drop:
            self.assertGreater(self.css.index(spelling), anchor)

    def test_sidebar_row_geometry(self):
        # No collected reference screenshot shows a GTK sidebar list,
        # places sidebar or stack sidebar, so the sheet restates the
        # stock sidebar seam and row geometry the existing .sidebar field
        # record leaves stock: the directional border twins and the
        # sidebar-direction separator take the existing etched dark half,
        # and every padding, the 36px row height, the viewport edge
        # drop and the paned border drop are stock's own shapes kept
        # byte-equal. The exact stock arms and the excluded faces live
        # in docs/invariants.md.
        seam = {
            "stacksidebar.sidebar:dir(ltr) list",
            "stacksidebar.sidebar.left list",
            "stacksidebar.sidebar.left:dir(rtl) list",
            ".sidebar:not(separator):dir(ltr)",
            ".sidebar:not(separator).left",
        }
        self.assert_rule_group({selector: {
            "border-right": "1px solid " + ETCH_DARK,
            "border-left-style": "none",
        } for selector in seam})
        self.assert_rule_group({selector: {
            "border-left": "1px solid " + ETCH_DARK,
            "border-right-style": "none",
        } for selector in (
            "stacksidebar.sidebar:dir(rtl) list",
            "stacksidebar.sidebar.right list",
            ".sidebar:not(separator):dir(rtl)",
            ".sidebar:not(separator).right",
        )})
        paned = {
            "paned .sidebar.left",
            "paned .sidebar.right",
            "paned .sidebar.left:dir(rtl)",
            "paned .sidebar:dir(rtl)",
            "paned .sidebar:dir(ltr)",
            "paned .sidebar",
        }
        self.assert_rule_group({key: {"border-style": "none"} for key in paned})
        self.assert_rule("stacksidebar row", {"padding": "10px 4px"})
        self.assert_rule("stacksidebar row > label", {
            "padding-left": "6px", "padding-right": "6px",
        })
        self.assert_rule("separator.sidebar", {"background-color": ETCH_DARK})
        selection_separator = "separator.sidebar.selection-mode"
        ancestor_selection_separator = ".selection-mode separator.sidebar"
        self.assert_rule(selection_separator, {"background-color": ETCH_DARK})
        self.assert_rule(ancestor_selection_separator, {"background-color": ETCH_DARK})
        self.assertEqual(self.selectors.count(selection_separator), 1)
        self.assertEqual(self.selectors.count(ancestor_selection_separator), 1)
        separator_family = {
            selector for selector in self.rules if "separator.sidebar" in selector
        }
        self.assertEqual(separator_family, {
            "separator.sidebar", selection_separator, ancestor_selection_separator,
        })
        self.assertLess(self.selectors.index("separator.sidebar"),
                        self.selectors.index(selection_separator))
        self.assertLess(self.selectors.index("separator.sidebar"),
                        self.selectors.index(ancestor_selection_separator))
        self.assert_rule("placessidebar > viewport.frame", {"border-style": "none"})
        self.assert_rule("placessidebar row", {"min-height": "36px", "padding": "0px"})
        self.assert_rule("placessidebar row > revealer", {"padding": "0 14px"})
        icon_ltr = "placessidebar row image.sidebar-icon:dir(ltr)"
        icon_rtl = "placessidebar row image.sidebar-icon:dir(rtl)"
        self.assert_rule(icon_ltr, {"padding-right": "8px"})
        self.assert_rule(icon_rtl, {"padding-left": "8px"})
        row_icon = "row image.sidebar-icon"
        self.assert_rule(row_icon, {"opacity": "1"})
        self.assertEqual(self.selectors.count(row_icon), 1)
        rtl_icon_position = self.css.index(icon_rtl)
        self.assertGreater(self.css.index(row_icon, rtl_icon_position + len(icon_rtl)),
                           rtl_icon_position)
        label_ltr = "placessidebar row label.sidebar-label:dir(ltr)"
        label_rtl = "placessidebar row label.sidebar-label:dir(rtl)"
        self.assert_rule(label_ltr, {"padding-right": "2px"})
        self.assert_rule(label_rtl, {"padding-left": "2px"})
        self.assertEqual({s for s in self.rules if s.startswith("paned .sidebar")}, paned)
        self.assertEqual({s for s in self.rules if "image.sidebar-icon" in s},
                         {icon_ltr, icon_rtl, row_icon})
        self.assertEqual({s for s in self.rules if "label.sidebar-label" in s},
                         {label_ltr, label_rtl})
        self.assertEqual({s for s in self.rules if s.startswith("stacksidebar")}, {
            "stacksidebar.sidebar:dir(ltr) list",
            "stacksidebar.sidebar.left list",
            "stacksidebar.sidebar.left:dir(rtl) list",
            "stacksidebar.sidebar:dir(rtl) list",
            "stacksidebar.sidebar.right list",
            "stacksidebar row",
            "stacksidebar row > label",
            "stacksidebar row.needs-attention > label",
        })
        self.assertNotIn("separator.sidebar:backdrop", self.selectors)
        self.assert_rule_after("stacksidebar.sidebar:dir(ltr) list", ".sidebar {")


if __name__ == "__main__":
    unittest.main()
