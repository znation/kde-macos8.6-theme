"""Validate the Firefox Platinum sheet's Library window tree paints.

The two places trees that frame the Library window's folder list and
content list for the standalone ``userChrome.css``.
"""

from __future__ import annotations

from support.firefox_chrome_cases import (
    REQUIRED_RULES,
    FirefoxChromeTestCase,
)
from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    SELECTION,
    WHITE,
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

# The Library toolbar's search box, painted as the Platinum line edit
# through the moz-input-search tokens.
SEARCH_RULE = ("moz-input-search#searchFilter",)

# The content tree's column-header arms, in sheet order: the two
# face arms then the four hover arms.
HEADER_FACE_ARMS = (
    "treecols#placeContentColumns > treecol",
    "treecols#placeContentColumns .tree-columnpicker-button",
)
HEADER_HOVER_ARMS = (
    "treecols#placeContentColumns > treecol:hover",
    "treecols#placeContentColumns > treecol:hover:active",
    "treecols#placeContentColumns .tree-columnpicker-button:hover",
    "treecols#placeContentColumns .tree-columnpicker-button:hover:active",
)


class TestFirefoxLibraryChrome(FirefoxChromeTestCase):
    """Section of the Firefox chrome sheet under test."""

    def test_library_tree_paint_is_scoped_to_the_places_trees(self):
        # The rule names naming either places tree are exactly the nine
        # selector names; each equals its REQUIRED_RULES entry (the
        # declarations test pins the values). The column-header arms
        # under treecols#placeContentColumns name the header row, not
        # the trees, and are pinned further down.
        named = [
            name for name in self.rules
            if ("placesList" in name or "placeContent" in name)
            and not name.startswith("treecols#placeContentColumns")
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

        # The twisties, cell icons and between-column grippies stay
        # Firefox's: no rule in the sheet names a twisty or splitter
        # (the column headers now carry their own rules under
        # TestFirefoxLibraryHeaderChrome, whose six arms are exactly
        # the sheet's treecols-prefixed names).
        for name in self.rules:
            with self.subTest(rule=name):
                for stock in ("twisty", "splitter"):
                    self.assertNotIn(stock, name)
        self.assertEqual(
            [name for name in self.rules if name.startswith("treecols")],
            list(HEADER_FACE_ARMS + HEADER_HOVER_ARMS),
        )



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
            "The toolbar buttons and the Organize, View",
            "downloads rich list and details pane stay Firefox's",
            "Declaration checks do not establish rendered pixels",
            "platform colour adaptation 2026-10-27",
        ))


class TestFirefoxLibrarySearchChrome(FirefoxChromeTestCase):
    """Section of the Firefox chrome sheet under test."""

    def test_search_field_rule_sets_only_custom_properties(self):
        # The host rule reaches the shadow #input only through the
        # tokens, so every property is a custom property.
        declarations = self.rules[SEARCH_RULE[0]]
        self.assertTrue(declarations)
        for name in declarations:
            with self.subTest(property=name):
                self.assertTrue(
                    name.startswith("--input-text-")
                    or name == "--icon-color"
                )

    def test_search_field_is_the_line_edit(self):
        self.assertEqual(
            self.rules[SEARCH_RULE[0]],
            REQUIRED_RULES[SEARCH_RULE[0]],
        )
        for name, value in self.rules[SEARCH_RULE[0]].items():
            with self.subTest(property=name):
                self.assertTrue(value.endswith("!important"))

    def test_search_field_selector_scopes_to_the_library_box(self):
        search = element("moz-input-search", "searchFilter")
        strain = element("moz-input-search", "someOtherSearchField")
        plain = element("moz-input-search", None)

        self.assertTrue(matches(SEARCH_RULE[0], search))
        self.assertFalse(matches(SEARCH_RULE[0], strain))
        self.assertFalse(matches(SEARCH_RULE[0], plain))

        # No rule in the sheet names a chrome moz-input-search host
        # other than the Library's, so other chrome windows' search
        # boxes keep Firefox's paint.
        named = [
            name for name in self.rules if "moz-input-search" in name
        ]
        self.assertEqual(named, list(SEARCH_RULE))

    def test_header_names_search_provenance(self):
        self.assert_header_names((
            "moz-input-search#searchFilter",
            "places.xhtml",
            "moz-input-text.css",
            "tokens-shared.css",
            "--icon-color",
            "search-textbox.svg",
            "no ::part()",
            "the sunken bevel is absent",
            "Declaration checks do not establish rendered pixels",
            "platform colour adaptation 2026-10-27",
            "2026-10-27",
        ))


class TestFirefoxLibraryHeaderChrome(FirefoxChromeTestCase):
    """Section of the Firefox chrome sheet under test."""

    def test_header_rules_are_the_sheet_recipe(self):
        # Each arm equals its REQUIRED_RULES entry byte-for-byte, and
        # every declaration is !important-pinned.
        for arm in HEADER_FACE_ARMS + HEADER_HOVER_ARMS:
            with self.subTest(selector=arm):
                self.assertEqual(self.rules[arm], REQUIRED_RULES[arm])
                for value in self.rules[arm].values():
                    self.assertTrue(value.endswith("!important"))

    def test_header_face_is_the_raised_button(self):
        # The face arms re-derive the landed raised push button's
        # byte-recipe from the shared palette constants; the hover
        # arms re-derive the flat no-bevel selection fill.
        face = {
            "background-color": f"{FACE} !important",
            "color": f"{BLACK} !important",
            "border-radius": "0 !important",
            "box-shadow":
                f"inset 1px 1px {WHITE}, "
                f"inset -1px -1px {BUTTON_SHADOW} !important",
        }
        hover = {
            "background-color": f"{SELECTION} !important",
            "color": f"{BLACK} !important",
            "box-shadow": "none !important",
        }
        for arm in HEADER_FACE_ARMS:
            with self.subTest(selector=arm):
                self.assertEqual(self.rules[arm], face)
        for arm in HEADER_HOVER_ARMS:
            with self.subTest(selector=arm):
                self.assertEqual(self.rules[arm], hover)

    def test_header_rules_scope_to_the_content_tree(self):
        columns = element(
            "treecols", "placeContentColumns",
            parent=element("tree", "placeContent", ("placesTree",)),
        )
        sidebar = element(
            "treecols", None,
            parent=element("tree", "placesList", ("placesTree",)),
        )
        column = element("treecol", "placesContentTitle", parent=columns)
        sidebar_column = element("treecol", None, parent=sidebar)
        picker = element(
            "button", None, ("tree-columnpicker-button",),
            parent=element("treecolpicker", None, parent=columns),
        )
        sidebar_picker = element(
            "button", None, ("tree-columnpicker-button",),
            parent=element("treecolpicker", None, parent=sidebar),
        )

        # The face arms match the content tree's columns and its
        # column-picker button, and never the placesList sidebar's
        # (its id-less treecols, hideheader="true", carries the one
        # column).
        self.assertTrue(matches(HEADER_FACE_ARMS[0], column))
        self.assertFalse(matches(HEADER_FACE_ARMS[0], sidebar_column))
        self.assertTrue(matches(HEADER_FACE_ARMS[1], picker))
        self.assertFalse(matches(HEADER_FACE_ARMS[1], sidebar_picker))

        # The hover arms match their fixtures with hover=True fixed
        # and nothing else; the matcher reads no :active, so the
        # hover:active arms stay pinned by the selector text alone.
        hovered_column = element(
            "treecol", "placesContentTitle", parent=columns, hover=True,
        )
        hovered_picker = element(
            "button", None, ("tree-columnpicker-button",), hover=True,
            parent=element("treecolpicker", None, parent=columns),
        )
        self.assertTrue(matches(HEADER_HOVER_ARMS[0], hovered_column))
        self.assertFalse(matches(HEADER_HOVER_ARMS[0], column))
        self.assertTrue(matches(HEADER_HOVER_ARMS[2], hovered_picker))
        self.assertFalse(matches(HEADER_HOVER_ARMS[2], picker))
        for arm in HEADER_HOVER_ARMS:
            with self.subTest(selector=arm):
                self.assertFalse(matches(arm, sidebar_column))
                self.assertFalse(matches(arm, sidebar_picker))

    def test_header_provenance(self):
        self.assert_header_names((
            "No reference screenshot shows the Firefox Library window",
            "widgets/button.svg",
            "tests/test_desktoptheme_button.py::TestButton",
            "TestButtonReference",
            "widgets/viewitem.svg",
            "test_selection_background",
            "treecols#placeContentColumns",
            "tree.js",
            "tree.css",
            "-moz-ColHeader",
            "ThreeDLightShadow",
            "-moz-ColHeaderHover",
            "sort-asc.svg",
            "columnpicker.svg",
            "Graytext",
            "hideheader",
            "Declaration checks do not establish rendered pixels",
            "platform colour adaptation 2026-10-27",
        ))


if __name__ == "__main__":
    unittest.main()
