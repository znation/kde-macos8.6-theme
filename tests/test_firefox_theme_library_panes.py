"""Validate the Firefox Platinum sheet's Library window downloads and details panes.

The downloads list with its Clear Downloads button, and the details pane's
bookmark fields, folder dropdown and tag selector, for the standalone
``userChrome.css``. The Library window's trees, search box, column headers
and toolbar are validated by ``test_firefox_theme_library.py``.
"""

from __future__ import annotations

import unittest

from support.firefox.chrome_cases import FirefoxChromeTestCase
from support.firefox.selector_matching import element, matches

# The Library downloads view's list-field and row arms, in sheet order.
DOWNLOADS_RULES = (
    "#placesViewsBox richlistbox#downloadsListBox",
    "#placesViewsBox richlistbox#downloadsListBox > richlistitem",
    "#placesViewsBox richlistbox#downloadsListBox > richlistitem[selected]",
)

# The Library toolbar's Clear Downloads button arms, in sheet order.
CLEAR_BUTTON_RULES = (
    "toolbar#placesToolbar toolbarbutton#clearDownloadsButton:not([disabled])",
    "toolbar#placesToolbar toolbarbutton#clearDownloadsButton"
    ":not([disabled]):hover",
)

# The Library details pane's four bookmark fields, in sheet order.
DETAILS_FIELD_RULES = (
    "#detailsPane #editBMPanel_namePicker",
    "#detailsPane #editBMPanel_locationField",
    "#detailsPane #editBMPanel_tagsField",
    "#detailsPane #editBMPanel_keywordField",
)

# The details pane's folder dropdown arms, in sheet order.
DETAILS_MENULIST_RULES = (
    "#detailsPane #editBMPanel_folderMenuList",
    "#detailsPane #editBMPanel_folderMenuList:hover:not([disabled])",
)

# The details pane's tag selector arms, in sheet order.
DETAILS_TAGS_RULES = (
    "#detailsPane richlistbox#editBMPanel_tagsSelector",
    "#detailsPane richlistbox#editBMPanel_tagsSelector > richlistitem",
    "#detailsPane richlistbox#editBMPanel_tagsSelector"
    " > richlistitem[selected]",
)

# All nine details-pane arms, in sheet order.
DETAILS_RULES = DETAILS_FIELD_RULES + DETAILS_MENULIST_RULES + DETAILS_TAGS_RULES


class TestFirefoxLibraryDownloadsChrome(FirefoxChromeTestCase):
    """Section of the Firefox chrome sheet under test."""

    def test_downloads_rules_match_the_required_rules(self):
        # Each of the five arms equals its REQUIRED_RULES entry
        # byte-for-byte, and every declaration ends !important.
        self.assert_arms_match_required(DOWNLOADS_RULES + CLEAR_BUTTON_RULES)

    def test_downloads_list_rules_scoped_to_the_places_views_box(self):
        views_box = element(
            "vbox", "placesViewsBox",
            parent=element("vbox", None,
                           parent=element("vbox", "contentView")),
        )
        downloads = element("richlistbox", "downloadsListBox",
                            parent=views_box)
        panel_list = element(
            "richlistbox", "downloadsListBox",
            parent=element("vbox", None,
                           parent=element("panelview",
                                          "downloadsPanel-mainView")),
        )
        content_area_list = element(
            "richlistbox", "downloadsListBox",
            parent=element("vbox", None,
                           parent=element("hbox",
                                          "contentAreaDownloadsView")),
        )
        row = element("richlistitem", None, parent=downloads)
        selected_row = element(
            "richlistitem", None, attrs={"selected": "true"},
            parent=downloads,
        )

        # The face arm matches the Library's list and never the
        # #downloadsPanel or content-area copies; the row arm matches a
        # plain richlistitem child and the selected arm only with the
        # selected attribute.
        self.assertTrue(matches(DOWNLOADS_RULES[0], downloads))
        self.assertFalse(matches(DOWNLOADS_RULES[0], panel_list))
        self.assertFalse(matches(DOWNLOADS_RULES[0], content_area_list))
        self.assertTrue(matches(DOWNLOADS_RULES[1], row))
        self.assertTrue(matches(DOWNLOADS_RULES[2], selected_row))
        self.assertFalse(matches(DOWNLOADS_RULES[2], row))

        # The sheet's whole set of downloadsListBox-naming rules is
        # exactly the existing #downloadsPanel arms plus this section's.
        self.assert_rule_names_scoped_to(
            "downloadsListBox",
            {
                "#downloadsPanel #downloadsListBox > richlistitem",
                "#downloadsPanel #downloadsListBox > richlistitem"
                ":not([selected]):hover",
                "#downloadsPanel #downloadsListBox > richlistitem[selected]",
                *DOWNLOADS_RULES,
            },
        )

    def test_clear_button_rules_scoped_to_the_library_toolbar(self):
        toolbar = element("toolbar", "placesToolbar")
        button = element("toolbarbutton", "clearDownloadsButton",
                         parent=toolbar)
        hovered = element("toolbarbutton", "clearDownloadsButton",
                          hover=True, parent=toolbar)
        other_button = element("toolbarbutton", "back-button",
                               parent=toolbar)
        other_toolbar = element(
            "toolbarbutton", "clearDownloadsButton",
            parent=element("toolbar", "nav-bar"),
        )

        # The base arm matches the Library's button wherever it is
        # hovered or not; the hover arm only with hover=True; and
        # neither arm reaches another toolbarbutton in the toolbar,
        # the same button under another toolbar included.
        self.assertTrue(matches(CLEAR_BUTTON_RULES[0], button))
        self.assertTrue(matches(CLEAR_BUTTON_RULES[0], hovered))
        self.assertFalse(matches(CLEAR_BUTTON_RULES[1], button))
        self.assertTrue(matches(CLEAR_BUTTON_RULES[1], hovered))
        for arm in CLEAR_BUTTON_RULES:
            with self.subTest(selector=arm):
                self.assertFalse(matches(arm, other_button))
                self.assertFalse(matches(arm, other_toolbar))

        # The sheet's whole set of clearDownloadsButton-naming rules is
        # exactly this section's, and the whole set of placesToolbar-
        # naming rules is exactly the existing band rule plus them.
        self.assert_rule_names_scoped_to(
            "clearDownloadsButton",
            set(CLEAR_BUTTON_RULES),
        )
        self.assert_rule_names_scoped_to(
            "placesToolbar",
            {"toolbar#placesToolbar", *CLEAR_BUTTON_RULES},
        )

    def test_header_names_downloads_provenance(self):
        self.assert_header_names((
            "No reference screenshot shows the Firefox Library window",
            "sunken list-field recipe",
            "square 1px",
            "inset 1px 1px #999999",
            "#contentAreaDownloadsView #downloadsListBox:not(:empty)",
            "widgets/lineedit.svg",
            "widgets/viewitem.svg",
            "tests/test_desktoptheme_lineedit.py::TestLineEdit",
            "tests/test_desktoptheme_viewitem.py::TestViewItem",
            "tests/test_colorscheme_reference.py::TestReferenceAnchors",
            "test_selection_background",
            "existing #downloadsPanel push-button recipe",
            "widgets/button.svg",
            "tests/test_desktoptheme_button.py::TestButton",
            "tests/test_desktoptheme_button_reference.py::TestButtonReference",
            "platform colour adaptation 2026-10-27",
            "no row hover rule exists",
            "widgets/listitem.svg",
            "ships no hover state",
            "#downloadsListBox id also occurring on",
            "scope through #placesViewsBox and toolbar#placesToolbar",
            "anatomy is read 2026-10-27",
            "vbox#placesViewsBox holding",
            "richlistbox#downloadsListBox.allDownloadsListBox",
            "seltype=\"multiple\"",
            "hidden=\"true\"",
            "#downloadsContextMenu",
            "toolbarbutton#clearDownloadsButton.tabbable",
            "downloadsCmd_clearDownloads",
            "#libraryToolbarSpacer",
            "richlistbox.css",
            "appearance: auto",
            "ThreeDShadow",
            "margin: 2px 4px",
            "richlistitem[selected=\"true\"]",
            "-moz-cellhighlight",
            "--default-focusring",
            "allDownloadsView.css",
            "allDownloadsView.inc.css",
            "min-height: 4.5em",
            ".downloadTypeIcon",
            ".downloadTarget",
            ".downloadDetails",
            ".downloadButton",
            "The intentionally unchanged",
            "progress",
            "Declaration checks do not establish rendered pixels",
        ))

class TestFirefoxLibraryDetailsPaneChrome(FirefoxChromeTestCase):
    """Section of the Firefox chrome sheet under test."""

    def test_details_pane_rules_match_the_required_rules(self):
        # Each of the nine arms equals its REQUIRED_RULES entry
        # byte-for-byte, and every declaration ends !important.
        self.assert_arms_match_required(DETAILS_RULES)

    def test_details_pane_rules_scoped_to_the_details_pane(self):
        # The places.xhtml details pane: window#places > vbox#detailsPane
        # > vbox#infoBox > div#editBookmarkPanelContent, holding the
        # four fields, the folder and tags rows and the tag selector.
        details_pane = element(
            "vbox", "detailsPane",
            parent=element("window", "places"),
        )
        info_box = element("vbox", "infoBox", parent=details_pane)
        content = element(
            "div", "editBookmarkPanelContent", parent=info_box,
        )
        fields = tuple(
            element("input", field_id, parent=content)
            for field_id in (
                "editBMPanel_namePicker",
                "editBMPanel_locationField",
                "editBMPanel_tagsField",
                "editBMPanel_keywordField",
            )
        )
        folder_row = element(
            "hbox", classes=("editBMPanel_folderRow",), parent=content,
        )
        menulist = element(
            "menulist", "editBMPanel_folderMenuList", ("folder-icon",),
            parent=folder_row,
        )
        folders_expander = element(
            "button", "editBMPanel_foldersExpander",
            ("expander-down", "panel-button"), parent=folder_row,
        )
        tags_selector_expander = element(
            "button", "editBMPanel_tagsSelectorExpander",
            ("expander-down", "panel-button"), parent=content,
        )
        new_folder = element(
            "button", "editBMPanel_newFolderButton", parent=content,
        )
        tags_selector = element(
            "richlistbox", "editBMPanel_tagsSelector", parent=content,
        )
        row = element("richlistitem", None, parent=tags_selector)
        selected_row = element(
            "richlistitem", None, attrs={"selected": "true"},
            parent=tags_selector,
        )

        # Beside the pane in the same window: browser.xhtml's
        # #editBookmarkPanel with copies of the themed widgets, plus a
        # stray id-less input and richlistbox.
        panel = element(
            "panel", "editBookmarkPanel", attrs={"type": "arrow"},
            parent=element("window", "places"),
        )
        panel_content = element(
            "div", "editBookmarkPanelContent", parent=panel,
        )
        panel_fields = tuple(
            element("input", field_id, parent=panel_content)
            for field_id in (
                "editBMPanel_namePicker",
                "editBMPanel_locationField",
                "editBMPanel_tagsField",
                "editBMPanel_keywordField",
            )
        )
        panel_menulist = element(
            "menulist", "editBMPanel_folderMenuList", parent=panel_content,
        )
        panel_tags_selector = element(
            "richlistbox", "editBMPanel_tagsSelector", parent=panel_content,
        )
        stray_input = element("input", None, parent=details_pane)
        stray_list = element("richlistbox", None, parent=details_pane)

        # The four fields match their selectors hovered or not; the
        # menulist matches its normal arm idle and hovered but its
        # hover arm only with hover=True and never when disabled; the
        # tags selector matches its face arm, its rows the row arm and
        # only a selected row the selected arm.
        for index, field in enumerate(fields):
            with self.subTest(field=field.get("id")):
                self.assertTrue(matches(DETAILS_FIELD_RULES[index], field))
                self.assertTrue(
                    matches(DETAILS_FIELD_RULES[index], {**field, "hover": True})
                )
        self.assertTrue(matches(DETAILS_MENULIST_RULES[0], menulist))
        self.assertTrue(
            matches(DETAILS_MENULIST_RULES[0], {**menulist, "hover": True})
        )
        self.assertFalse(matches(DETAILS_MENULIST_RULES[1], menulist))
        self.assertTrue(
            matches(DETAILS_MENULIST_RULES[1], {**menulist, "hover": True})
        )
        disabled = {
            **menulist,
            "attrs": {"disabled": "true"},
            "hover": True,
        }
        self.assertFalse(matches(DETAILS_MENULIST_RULES[1], disabled))
        self.assertTrue(matches(DETAILS_TAGS_RULES[0], tags_selector))
        self.assertTrue(matches(DETAILS_TAGS_RULES[1], row))
        self.assertTrue(matches(DETAILS_TAGS_RULES[2], selected_row))
        self.assertFalse(matches(DETAILS_TAGS_RULES[2], row))

        # The #editBookmarkPanel copies, the two expander buttons, the
        # New Folder button, the stray input and the stray richlistbox
        # match none of the nine selectors: the details-pane scoping
        # keeps the panel's own existing paint intact.
        for name, control in (
            ("panel name field", panel_fields[0]),
            ("panel location field", panel_fields[1]),
            ("panel tags field", panel_fields[2]),
            ("panel keyword field", panel_fields[3]),
            ("panel menulist", panel_menulist),
            ("panel tags selector", panel_tags_selector),
            ("folders expander", folders_expander),
            ("tags selector expander", tags_selector_expander),
            ("new folder button", new_folder),
            ("stray input", stray_input),
            ("stray richlistbox", stray_list),
        ):
            with self.subTest(unthemed=name):
                for selector in DETAILS_RULES:
                    self.assertFalse(matches(selector, control))
                    self.assertFalse(
                        matches(selector, {**control, "hover": True})
                    )

    def test_details_pane_selector_set_is_exact(self):
        # The sheet's whole set of detailsPane-naming rules is exactly
        # this section's nine arms, and the whole set of editBMPanel-
        # naming rules is exactly them plus the existing ten
        # #editBookmarkPanel-prefixed bookmark editor's arms.
        self.assert_rule_names_scoped_to("detailsPane", set(DETAILS_RULES))
        # The sheet's whole set of editBMPanel-naming rules is exactly
        # this section's nine arms plus the existing six that name the
        # bookmark editor's field ids and folder menulist; the Done/
        # Remove buttons' names carry editBookmarkPanel but not
        # editBMPanel, and the panels suite pins their ten-rule set.
        self.assert_rule_names_scoped_to(
            "editBMPanel",
            {
                "#editBookmarkPanel #editBMPanel_namePicker",
                "#editBookmarkPanel #editBMPanel_locationField",
                "#editBookmarkPanel #editBMPanel_tagsField",
                "#editBookmarkPanel #editBMPanel_keywordField",
                "#editBookmarkPanel #editBMPanel_folderMenuList",
                "#editBookmarkPanel #editBMPanel_folderMenuList"
                ":hover:not([disabled])",
                *DETAILS_RULES,
            },
        )
        self.assert_rule_names_scoped_to(
            "editBookmark",
            {
                "#editBookmarkPanel #editBookmarkPanelDoneButton",
                "#editBookmarkPanel #editBookmarkPanelRemoveButton",
                "#editBookmarkPanel #editBookmarkPanelDoneButton"
                ":hover:not([disabled])",
                "#editBookmarkPanel #editBookmarkPanelRemoveButton"
                ":hover:not([disabled])",
                *[
                    name for name in self.rules
                    if "editBMPanel" in name
                    and name.startswith("#editBookmarkPanel")
                ],
            },
        )

    def test_header_names_details_pane_provenance(self):
        self.assert_header_names((
            "No reference screenshot shows the Firefox Library window",
            "details pane's bookmark fields reuse this sheet's existing",
            "#editBookmarkPanel line-edit recipe",
            "#FFFFFF face, black text,",
            "square 1px solid #000000 outline, inset 1px 1px #999999 shadow)",
            "push-button menulist recipe",
            "inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA raised bevel,",
            "flat #CCCCFF hover)",
            "grounded in widgets/lineedit.svg and",
            "widgets/button.svg and pinned by",
            "tests/test_desktoptheme_lineedit.py::TestLineEdit",
            "TestLineEditReference,",
            "tests/test_desktoptheme_button.py::TestButton",
            "tests/test_desktoptheme_button_reference.py::TestButtonReference",
            "tag selector reuses the existing #placesList sunken list-field",
            "selected row's widgets/viewitem.svg highlight",
            "tests/test_desktoptheme_viewitem.py::TestViewItem",
            "tests/test_colorscheme_reference.py::TestReferenceAnchors",
            ".test_selection_background",
            "no hover rule exists on the fields or",
            "the tag selector's rows because the existing recipes have none",
            "menulist's hover arm is the existing menulist recipe's own",
            "rules scope through #detailsPane because the same editBMPanel ids",
            "browser.xhtml's #editBookmarkPanel",
            "#bookmarkpropertiesdialog",
            "finds a detailsPane element only in places.xhtml",
            "read 2026-10-27 from the installed Firefox ESR 153.5.1",
            "vbox#detailsPane holding #itemsCountBox and",
            "#infoBox with the embedded #editBookmarkPanelContent markup",
            "html:input#editBMPanel_namePicker,",
            "hbox.editBMPanel_folderRow",
            "menulist#editBMPanel_folderMenuList.folder-icon and",
            "button#editBMPanel_foldersExpander.expander-down.panel-button,",
            "vbox#editBMPanel_folderTreeRow",
            "button#editBMPanel_newFolderButton,",
            "html:input#editBMPanel_tagsField with #editBMPanel_tagsAutocomplete",
            "button#editBMPanel_tagsSelectorExpander,",
            "div#editBMPanel_tagsSelectorRow",
            "richlistbox#editBMPanel_tagsSelector and",
            "html:input#editBMPanel_keywordField)",
            "organizer-shared.css owning",
            "min-height: 16em and padding: 5px",
            "#editBookmarkPanelContent grid and the #editBMPanel_tagsSelector",
            "margin: 4px",
            "editBookmarkPanel.css's expander and focus paints",
            "being #editBookmarkPanel-scoped",
            "global-shared.css, button.css, menulist.css and richlistbox.css",
            "The intentionally unchanged paint: the",
            "two expander buttons, the New Folder button, the folder tree, the",
            "labels and caption labels, #itemsCountBox and",
            "#editBMPanel_itemsCountText",
            "the tags autocomplete panel, the",
            "menulist's popup list and the stock margins",
            "Declaration checks",
        ))


if __name__ == "__main__":
    unittest.main()
