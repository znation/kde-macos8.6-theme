"""Validate GTK 3 CSD container corner declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT


class TestGtkThemeCsdContainers(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_csd_container_corners(self):
        """Pin the CSD container and decoration corner restatements.

        The five appended groups rest stock's class-armed popup-menu,
        generic popover-background and decoration-shell radius arms at
        zero; the existing name-level `menu`, `popover`, `tooltip` and
        messagedialog groups match none of these spellings.
        """
        selectors = (
            ".csd menu",
            ".csd .menu",
            ".csd .context-menu",
            ".csd popover.background",
            "popover.background",
            ".csd.popup decoration",
            "tooltip.csd decoration",
            "messagedialog.csd decoration",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                self.assertEqual(self.selectors.count(selector), 1, selector)
        # The class-armed menu spellings have no existing or future neighbour:
        # the existing scroll-arrow and row spellings carry `context-menu` with
        # a space but never `csd menu`, `csd .menu` or `csd .context-menu`.
        self.assertEqual(
            {s for s in self.rules if "csd menu" in s}, {".csd menu"}
        )
        self.assertEqual(
            {s for s in self.rules if "csd .menu" in s}, {".csd .menu"}
        )
        self.assertEqual(
            {s for s in self.rules if "csd .context-menu" in s},
            {".csd .context-menu"},
        )
        # No existing or unrelated decoration selector exists: the sheet names
        # `text-decoration-line` only as a property, never as a selector.
        self.assertEqual(
            {s for s in self.rules if "decoration" in s},
            {
                ".csd.popup decoration",
                "tooltip.csd decoration",
                "messagedialog.csd decoration",
            },
        )
        # Source order: every appended spelling sits after the existing
        # menu, popover and messagedialog restatements, so the byte-equal
        # stock twins win the equal-specificity ties under the lower-sheet
        # reading of how the toolkit resource competes.
        for selector in selectors:
            for anchor in ("menu", "popover", "messagedialog.csd.background"):
                with self.subTest(selector=selector, after=anchor):
                    self.assertGreater(
                        self.selectors.index(selector),
                        self.selectors.index(anchor),
                    )


if __name__ == "__main__":
    unittest.main()
