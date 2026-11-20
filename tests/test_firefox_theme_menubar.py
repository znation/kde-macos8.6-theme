"""Validate the main Firefox window's menubar title geometry and paint."""

from __future__ import annotations

import re
import unittest

from support.desktoptheme_paths import MENUBARITEM_SVG
from support.firefox_chrome_cases import (
    MENU_STOCK_BOTTOM_BORDER,
    REQUIRED_RULES,
    FirefoxChromeTestCase,
)
from support.svg_case import parse_svg
from svg_assertions import rect_geometry


class TestFirefoxMenubar(FirefoxChromeTestCase):
    """Main-window menubar title geometry and open-state paint."""

    def test_menubar_title_geometry_matches_the_menubaritem_margins(self):
        selector = "#toolbar-menubar menubar > menu"
        geometry = rect_geometry(parse_svg(MENUBARITEM_SVG))
        top = int(geometry["normal-hint-top-margin"][3])
        bottom = int(geometry["normal-hint-bottom-margin"][3])
        left = int(geometry["normal-hint-left-margin"][2])
        right = int(geometry["normal-hint-right-margin"][2])
        self.assertEqual((top, bottom), (3, 3))
        self.assertEqual((left, right), (7, 7))
        # The retained stock bottom border completes the bottom margin, so
        # the sheet's bottom pad is the margin minus that border.
        bottom_pad = bottom - MENU_STOCK_BOTTOM_BORDER
        bottom_value = f"{bottom_pad}px" if bottom_pad else "0"
        self.assertEqual(
            self.rules[selector],
            {"padding": f"{top}px {left}px {bottom_value} !important"},
        )
        pad_top, pad_right, pad_bottom = (
            int(value.removesuffix("px"))
            for value in self.rules[selector]["padding"]
            .removesuffix(" !important").split()
        )
        self.assertEqual(
            (pad_top, pad_right, pad_bottom),
            (top, left, bottom_pad),
        )
        self.assertEqual(pad_bottom + MENU_STOCK_BOTTOM_BORDER, bottom)

    def test_menubar_open_title_paint_is_scoped_to_the_open_title(self):
        selector = "#toolbar-menubar menubar > menu[open]"
        base = "#toolbar-menubar menubar > menu"
        # A menu-bar title is a ``menu`` element outside a popup, so catch a
        # rule that targets one without naming #toolbar-menubar, such as a
        # bare ``menu[open]:hover``, rather than only selectors spelled
        # ``menubar``. The Library window's menubar#placesMenu title rules
        # are scoped to their own menubar by id and have their own suite,
        # so they stay out of this main-window set; an unscoped bare rule
        # would still land here.
        title_rules = {
            name for name in self.rules
            if "placesMenu" not in name
            and ("menubar" in name
                 or ("menu" in re.findall(r"[-\w]+", name)
                     and "menupopup" not in name))
        }
        self.assertEqual(title_rules, {"#toolbar-menubar", base, selector})
        for name in ("#toolbar-menubar", base, selector):
            with self.subTest(selector=name):
                self.assertEqual(self.rules[name], REQUIRED_RULES[name])
        self.assertEqual(set(self.rules[base]), {"padding"})
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "placesMenu" not in name
             and declarations == REQUIRED_RULES[selector]},
            {selector},
        )


if __name__ == "__main__":
    unittest.main()
