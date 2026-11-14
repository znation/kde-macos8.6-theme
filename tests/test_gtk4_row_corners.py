"""GTK 4 navigation-sidebar, boxed-list, separate-row and colour-swatch corner checks moved out of ``test_gtk4_theme``."""


from __future__ import annotations

import unittest

from support.gtk4_sheet import Gtk4SheetRuleCases
from support.platinum_palette import BLACK


class TestGtk4RowCorners(Gtk4SheetRuleCases, unittest.TestCase):
    def test_navigation_sidebar_item_corners(self):
        expected = {
            ".navigation-sidebar > row",
            ".navigation-sidebar > child",
            ".navigation-sidebar > flowboxchild",
        }
        # The row-focus restate adds one stock focus twin
        # under the same prefix; it states the focus outline, not the corner
        # radius, and test_list_row_focus_outlines pins its spelling.
        focus = {".navigation-sidebar > row:focus-visible:focus-within"}
        self.assertEqual(
            {selector for selector in self.rules
             if selector.startswith(".navigation-sidebar > ")},
            expected | focus,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assert_square_corner(selector)
        self.assert_rule(
            ".navigation-sidebar > row:focus-visible:focus-within",
            {"outline-color": BLACK},
        )

    def test_boxed_list_corners(self):
        roots = ("list.boxed-list", "list.content")
        suffixes = (
            "",
            " > row:first-child",
            " > row:last-child",
            " > row:first-child.expander row.header",
            " > row:last-child.expander:not(:checked)",
            " > row:last-child.expander:not(:checked) row.header",
            " > row:last-child.expander:checked list.nested",
            " > row:last-child.expander:checked list.nested > row:last-child",
        )
        expected = {root + suffix for root in roots for suffix in suffixes}
        # The row-focus restate adds two stock focus twins
        # under each root; they state the focus outline, not the corner
        # radius, and test_list_row_focus_outlines pins their spelling.
        focus = {
            "list.boxed-list > row:focus:focus-visible",
            "list.boxed-list > row.expander row.header:focus:focus-visible",
            "list.content > row:focus:focus-visible",
            "list.content > row.expander row.header:focus:focus-visible",
        }
        self.assertEqual(
            {selector for selector in self.rules
             if any(selector == root or selector.startswith(root + " ")
                    for root in roots)},
            expected | focus,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assert_square_corner(selector)
        for selector in sorted(focus):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"outline-color": BLACK})

    def test_separate_boxed_row_corners(self):
        expected = {
            "list.boxed-list-separate > row",
            "list.boxed-list-separate > row.expander row.header",
            "list.boxed-list-separate > row.expander:not(:checked) row.header",
            "list.boxed-list-separate > row.expander.expander:checked list.nested",
            "list.boxed-list-separate > row.expander.expander:checked list.nested > row:last-child",
        }
        # The row-focus restate adds two stock focus twins
        # under the same root; they state the focus outline, not the corner
        # radius, and test_list_row_focus_outlines pins their spelling.
        focus = {
            "list.boxed-list-separate > row:focus:focus-visible",
            "list.boxed-list-separate > row.expander row.header:focus:focus-visible",
        }
        self.assertEqual(
            {selector for selector in self.rules
             if "list.boxed-list-separate" in selector},
            expected | focus,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assert_square_corner(selector)
        for selector in sorted(focus):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"outline-color": BLACK})

    def test_color_swatch_corners(self):
        # The residual focus restate adds the focus twin
        # under the same root; it states the focus outline colour, not a
        # corner radius, and test_residual_focus_outline_color pins its
        # spelling.
        self.assert_color_swatch_corners(
            " > overlay",
            extra_declarations={
                "colorswatch:focus:focus-visible": {"outline-color": BLACK},
                # The 2026-11-04 container entry squares the colour
                # button's two higher-specificity swatch spellings stock
                # groups before the integration library's own arm; they
                # carry the corner radius and nothing else.
                "button.color > colorswatch:only-child": {"border-radius": "0"},
                "button.color > colorswatch:only-child > overlay": {
                    "border-radius": "0"
                },
            },
        )


if __name__ == "__main__":
    unittest.main()
