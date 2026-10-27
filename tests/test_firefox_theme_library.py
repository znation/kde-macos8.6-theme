"""Validate the Firefox Platinum sheet's Library window tree paints.

The two places trees that frame the Library window's folder list and
content list for the standalone ``userChrome.css``.
"""

from __future__ import annotations

from support.firefox_chrome_cases import (
    REQUIRED_RULES,
    FirefoxChromeTestCase,
)
from support.selector_matching import element, matches

# The nine required selectors naming the two places trees, in sheet
# order: the two field selectors, then the per-tree row and cell-text
# rules for each tree, then the multicol odd-row stripe floated back
# onto the content tree's field.
TREE_RULES = (
    "#placesList",
    "#placeContent",
    "tree#placesList treechildren::-moz-tree-row(hover)",
    "tree#placeContent treechildren::-moz-tree-row(hover)",
    "tree#placesList treechildren::-moz-tree-row(selected)",
    "tree#placeContent treechildren::-moz-tree-row(selected)",
    "tree#placesList treechildren::-moz-tree-cell-text",
    "tree#placeContent treechildren::-moz-tree-cell-text",
    "tree#placeContent treechildren::-moz-tree-row(multicol, odd)",
)


class TestFirefoxLibraryChrome(FirefoxChromeTestCase):
    """Section of the Firefox chrome sheet under test."""

    def test_library_tree_paint_is_scoped_to_the_places_trees(self):
        # The rule names naming either places tree are exactly the nine
        # selector names; each equals its REQUIRED_RULES entry (the
        # declarations test pins the values).
        named = [
            name for name in self.rules
            if "placesList" in name or "placeContent" in name
        ]
        self.assertEqual(sorted(named), sorted(TREE_RULES))
        self.assertEqual(len(named), len(TREE_RULES))

        places = element("tree", "placesList", ("placesTree",))
        content = element("tree", "placeContent", ("placesTree",))

        # The container selectors match their own tree and not the
        # sibling's.
        self.assertTrue(matches("#placesList", places))
        self.assertFalse(matches("#placeContent", places))
        self.assertTrue(matches("#placeContent", content))
        self.assertFalse(matches("#placesList", content))

        # The row and cell-text selectors carry ::-moz-tree-*
        # pseudo-elements, which the shared matcher treats as
        # assertion-only: they use only supported pieces elsewhere and
        # their parent chain names tree#placesList or
        # tree#placeContent, but the matcher reports no match for any
        # element, so their paint is pinned by the declarations above
        # and their scoping by the selector text. A stray tree still
        # cannot match any of the nine selectors, wherever it appears.
        strays = (
            element("tree", None),
            element("tree", "editBMPanel_folderTree"),
            element(
                "treechildren", None,
                parent=element("tree", "editBMPanel_folderTree"),
            ),
            element(
                "treefindbar", "placesToolbarFindBar",
                parent=element("toolbar", "placesToolbar"),
            ),
            element("tree", "placeContentColumns"),
            element("treecols", "placeContentColumns"),
            element("splitter", "placeContentSplitter"),
            element("tree", "placesViewHeader"),
        )
        for stray in strays:
            with self.subTest(unthemed=stray["id"] or stray["tag"]):
                self.assertFalse(
                    any(matches(rule, stray) for rule in TREE_RULES)
                )

        # The twisties, cell icons, column headers and between-column
        # grippies stay Firefox's: no rule in the sheet names a
        # twisty, splitter, treecol or column picker.
        for name in self.rules:
            with self.subTest(rule=name):
                for stock in ("twisty", "splitter", "treecol",
                              "columnpicker"):
                    self.assertNotIn(stock, name)



    def test_library_tree_rules_match_the_required_rules(self):
        for selector in TREE_RULES:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        # The two field selectors carry the five Platinum field
        # declarations on the same dict, and no entry naming a places
        # tree carries appearance, font, margin, border-right or
        # outline declarations.
        for selector in TREE_RULES:
            for declaration in REQUIRED_RULES[selector]:
                with self.subTest(selector=selector,
                                  declaration=declaration):
                    self.assertNotIn(
                        declaration,
                        ("appearance", "font", "margin",
                         "border-right", "outline"),
                    )

    def test_library_tree_provenance(self):
        self.assert_header_names((
            "The Library window's two places trees",
            "#placesList",
            "#placeContent",
            "No reference screenshot shows the Firefox Library window",
            "widgets/lineedit.svg",
            "macos8.6-screenshots/firstboot_betawiki.png",
            "tests/test_desktoptheme_lineedit.py::TestLineEdit",
            "TestLineEditReference",
            "widgets/listitem.svg",
            "tests/test_desktoptheme_listitem.py::TestListItem",
            "no-hover-highlight",
            "widgets/viewitem.svg",
            "tests/test_desktoptheme_viewitem.py::TestViewItem",
            "tests/test_colorscheme_reference.py::TestReferenceAnchors",
            "test_selection_background",
            "chrome/browser/content/browser/places/places.xhtml",
            "tree#placesList",
            "tree#placeContent",
            "hbox #placesView",
            "chrome/browser/content/browser/places/places.css",
            ".placesTree",
            "chrome/browser/skin/classic/browser/places/organizer.css",
            "organizer-shared.css",
            "chrome/toolkit/skin/classic/global/tree/tree.css",
            "Field",
            "ThreeDShadow",
            "-moz-oddtreerow",
            "hsla(0, 0%, 50%, 0.15)",
            "-moz-cellhighlight",
            "SelectedItem",
            "tree-icons.css",
            "The toolbar, search filter, content-tree",
            "downloads rich list and details pane stay Firefox's",
            "Declaration checks do not establish rendered pixels",
            "platform colour adaptation 2026-10-27",
        ))


if __name__ == "__main__":
    unittest.main()
