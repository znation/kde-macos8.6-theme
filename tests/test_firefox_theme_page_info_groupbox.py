"""Validate the Firefox Page Info security groupbox declarations.

Other Page Info surfaces are covered by
``tests/test_firefox_theme_page_info.py``; meta and image trees are covered
by ``tests/test_firefox_theme_page_info_trees.py``.
"""

from __future__ import annotations

import unittest

from support.firefox_chrome_cases import REQUIRED_RULES, FirefoxChromeTestCase
from support.selector_matching import element, matches


class TestFirefoxPageInfoGroupbox(FirefoxChromeTestCase):
    """Security panel etched frame declarations and selector scope."""

    def test_page_info_groupbox_paint_is_scoped_to_page_info(self):
        selectors = (
            "#securityPanel > groupbox",
            "#securityPanel > groupbox + groupbox",
            "#securityPanel > groupbox > label.header",
        )
        # The rule names containing groupbox are exactly the three
        # selector names, each equal to its REQUIRED_RULES entry.
        self.assertEqual(
            sorted(name for name in self.rules if "groupbox" in name),
            sorted(selectors),
        )
        for name in selectors:
            with self.subTest(selector=name):
                self.assertEqual(self.rules[name], REQUIRED_RULES[name])

        window = element("window", "pageInfoWindow")
        main_deck = element("deck", "mainDeck", parent=window)
        security_panel = element("vbox", "securityPanel", parent=main_deck)
        boxes = []
        headers = []
        for section in ("identity", "privacy", "technical"):
            box = element("groupbox", None, parent=security_panel)
            headers.append(
                element(
                    "label", f"security-view-{section}", ("header",),
                    parent=box,
                )
            )
            boxes.append(box)
        other_panel = element("vbox", "otherPanel", parent=main_deck)
        stray_box = element("groupbox", "strayBox", parent=other_panel)
        stray_header = element(
            "label", "strayHeader", ("header",), parent=stray_box
        )
        for box in boxes:
            with self.subTest(security_groupbox=True):
                self.assertTrue(matches("#securityPanel > groupbox", box))
        # The `+` selector needs no element matching: the matcher subset
        # has no adjacent-sibling combinator, so it stays assertion-only.
        self.assertFalse(matches("#securityPanel > groupbox + groupbox",
                                 stray_box))
        for header in headers:
            with self.subTest(security_header=True):
                self.assertTrue(
                    matches("#securityPanel > groupbox > label.header", header)
                )
        self.assertFalse(matches("#securityPanel > groupbox", stray_box))
        self.assertFalse(matches("#securityPanel > groupbox", stray_header))
        self.assertFalse(
            matches("#securityPanel > groupbox > label.header", stray_header)
        )

    def test_page_info_groupbox_provenance(self):
        self.assert_header_names((
            "systemprofiler_betawiki.png",
            "x=241..679",
            "y=103..154",
            "#888888",
            "offset one pixel right and down",
            "tests/test_desktoptheme_line.py::TestLineReference",
            "pageInfo.xhtml",
            "label.header",
            "chrome/toolkit/content/global/xul.css",
            "flex-direction: column",
            "-moz-default-appearance",
            "#securityPanel",
            "pageInfo.css",
            "apps_macrumors8.6.jpg",
            "1em",
            "Declaration checks pin the sheet's declarations",
            "reference grounding 2026-10-27",
        ))


if __name__ == "__main__":
    unittest.main()
