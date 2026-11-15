"""GTK 4 navigation-surface checks moved out of ``test_gtk4_theme``."""

from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.gtk_theme_spec import ROW_HOVER
from support.platinum_palette import BLACK, FACE, SELECTION


class TestGtk4Navigation(Gtk4SheetRuleCases, unittest.TestCase):
    def test_list_row_press_and_popup_faces(self):
        # The pressed and popup-holding row states restate the existing
        # faces: stock's toolkit resource and the integration library's
        # base.css resource would paint a tinted hover-wash, pressed
        # insets-wash-or-an-accent fill on rows the existing records paint
        # transparent or with the flat lavender selection, and the
        # integration library paints background colors on the pressed
        # spellings as well as the toolkit's insets.
        expected = {
            "row.activatable.has-open-popup": dict(ROW_HOVER),
            "row.activatable:hover": dict(ROW_HOVER),
            "row.activatable:active": {"background-color": "transparent", "box-shadow": "none"},
            "row.activatable:selected:active": {"background-color": SELECTION, "box-shadow": "none"},
            "row.activatable:selected.has-open-popup": {"background-color": SELECTION},
            "row.activatable:selected:hover": {"background-color": SELECTION},
        }
        self.assert_rule_group(expected)
        # The existing row spellings are all list-, listview-, columnview-
        # or popover-armed, and the existing bare-row groups spell `row` and
        # `row:focus:focus-visible`, so this element-level family is
        # exactly six.
        self.assertEqual(
            {s for s in self.rules if s.startswith("row.activatable")},
            set(expected),
        )
        self.assertGreater(
            self.selectors.index("row.activatable:active"),
            self.selectors.index("list row.activatable:selected"),
        )

    def test_places_sidebar(self):
        self.assert_rule(".sidebar", {"background-color": FACE, "color": BLACK})
        self.assert_rule(".sidebar:backdrop", {"background-color": FACE, "color": BLACK})
        self.assert_rule(
            "placessidebar.sidebar:not(separator):dir(ltr)", {"border": "none"}
        )
        self.assert_rule(
            "placessidebar.sidebar:not(separator):dir(rtl)", {"border": "none"}
        )
        self.assert_rule(
            "placessidebar .navigation-sidebar > row.sidebar-new-bookmark-row",
            {"color": BLACK},
        )
        # The drag-session arms restate the stock drop strip and drag-over
        # row twins on the existing selection lavender with black ink;
        # each keeps stock's own
        # geometry members so the byte-equal spelling wins the cascade by
        # later user-sheet source order.
        expected_drop = {
            "placessidebar .navigation-sidebar > row.sidebar-placeholder-row": {
                "padding": "0 8px",
                "min-height": "2px",
                "background-image": f"image({SELECTION})",
                "background-clip": "content-box",
            },
            "placessidebar .navigation-sidebar > row:drop(active):not(:disabled)": {
                "color": BLACK,
                "box-shadow":
                    f"inset 0 1px {SELECTION}, inset 0 -1px {SELECTION}",
            },
            "placessidebar .navigation-sidebar > row:drop(active):not(:disabled):selected": {
                "color": BLACK,
                "background-color": SELECTION,
            },
        }
        self.assert_rule_group(expected_drop)
        # The drag-over family is exactly these two arms: the sweep kills a
        # renamed spelling or a stray twin.
        self.assertEqual(
            {s for s in self.rules
             if s.startswith("placessidebar .navigation-sidebar > row:drop")},
            {
                "placessidebar .navigation-sidebar > row:drop(active):not(:disabled)",
                "placessidebar .navigation-sidebar > row:drop(active):not(:disabled):selected",
            },
        )

    def test_stack_switcher_tabs(self):
        forms = {
            "base": ("stackswitcher > button",),
            "hover": ("stackswitcher > button:hover",),
            "checked": ("stackswitcher > button:checked",),
            "checked+hover": ("stackswitcher > button:checked:hover",),
        }
        self.assert_tab_faces(forms)


if __name__ == "__main__":
    unittest.main()
