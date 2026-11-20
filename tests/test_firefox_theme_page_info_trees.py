"""Validate Firefox Page Info meta and image tree declarations."""

from __future__ import annotations

import unittest

from support.firefox_chrome_cases import (
    REQUIRED_RULES,
    VIEWITEM_REFERENCES,
    FirefoxChromeTestCase,
)
from support.selector_matching import element, matches


class TestFirefoxPageInfoTrees(FirefoxChromeTestCase):
    """Meta and image tree paint declarations and selector scope."""

    def test_page_info_tree_paint_is_scoped_to_page_info(self):
        tree_rules = [
            name for name in self.rules
            if "metatree" in name or "imagetree" in name
        ]
        self.assertEqual(sorted(tree_rules), sorted([
            "#metatree",
            "#imagetree",
            "tree#metatree treechildren::-moz-tree-row(hover)",
            "tree#imagetree treechildren::-moz-tree-row(hover)",
            "tree#metatree treechildren::-moz-tree-row(selected)",
            "tree#imagetree treechildren::-moz-tree-row(selected)",
            "tree#metatree treechildren::-moz-tree-cell-text",
            "tree#imagetree treechildren::-moz-tree-cell-text",
            "tree#imagetree treechildren::-moz-tree-cell-text(broken)",
        ]))
        self.assertEqual(len(tree_rules), 9)
        for name in tree_rules:
            with self.subTest(rule=name):
                self.assertEqual(self.rules[name], REQUIRED_RULES[name])
        self.assertIn("::-moz-tree-row(hover)", " ".join(tree_rules))
        self.assertIn("::-moz-tree-row(selected)", " ".join(tree_rules))
        self.assertIn("::-moz-tree-cell-text", " ".join(tree_rules))
        # The page-info trees' column headers keep Firefox's paint:
        # the sheet's only treecol and column-picker rules are the
        # Library window's six header arms under
        # TestFirefoxLibraryHeaderChrome.
        for name in self.rules:
            if name.startswith("treecols#placeContentColumns"):
                continue
            with self.subTest(rule=name):
                self.assertNotIn("treecol", name)
                self.assertNotIn("tree-columnpicker", name)

        window = element("window", "pageInfoWindow")
        main_deck = element("deck", "mainDeck", parent=window)
        meta_tags = element("vbox", "metaTags", parent=main_deck)
        metatree = element("tree", "metatree", parent=meta_tags)
        media_panel = element("vbox", "mediaPanel", parent=main_deck)
        imagetree = element("tree", "imagetree", parent=media_panel)
        # The containers match their own id selector and not the other's.
        self.assertTrue(matches("#metatree", metatree))
        self.assertFalse(matches("#imagetree", metatree))
        self.assertTrue(matches("#imagetree", imagetree))
        self.assertFalse(matches("#metatree", imagetree))

        other_panel = element("vbox", "otherPanel", parent=main_deck)
        stray_tree = element("tree", None, parent=other_panel)
        bookmark_tree = element(
            "tree", "editBMPanel_folderTree",
            parent=element("vbox", "editBookmarkPanel"),
        )
        for stray in (stray_tree, bookmark_tree):
            with self.subTest(unthemed=stray["id"]):
                for name in tree_rules:
                    self.assertFalse(matches(name, stray))

    def test_page_info_tree_provenance(self):
        self.assert_header_names((
            "No reference shows Firefox's Page Info trees",
            "widgets/lineedit.svg",
            "firstboot_betawiki.png",
            "tests/test_desktoptheme_lineedit.py::TestLineEdit",
            "TestLineEditReference",
            "#mainDeck input",
            "#permList",
            "widgets/listitem.svg",
            "tests/test_desktoptheme_listitem.py::TestListItem",
            "no hover highlight",
            *VIEWITEM_REFERENCES,
            "test_selection_background",
            "pageInfo.xhtml",
            "multicol",
            "chrome/toolkit/skin/classic/global/tree/tree.css",
            "pageInfo.css",
            "Field",
            "ThreeDShadow",
            "-moz-cellhighlight",
            "SelectedItem",
            "-moz-cellhighlighttext",
            "SelectedItemText",
            "graytext",
            "column headers stay Firefox's",
            "Declaration checks do not establish rendered pixels",
            "platform colour adaptation 2026-10-27",
        ))


if __name__ == "__main__":
    unittest.main()
