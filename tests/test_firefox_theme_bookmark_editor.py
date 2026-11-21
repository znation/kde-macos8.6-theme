"""Validate the Firefox Platinum sheet's bookmark-editor paints.

The ``#editBookmarkPanel`` fields, folder dropdown and footer buttons, for
the standalone ``userChrome.css``.
"""

from __future__ import annotations

import unittest

from support.firefox_chrome_cases import (
    BUTTON_REFERENCES,
    VIEWITEM_REFERENCES,
    FirefoxChromeTestCase,
)
from support.selector_matching import element, matches


class TestFirefoxBookmarkEditor(FirefoxChromeTestCase):
    """Section of the Firefox chrome sheet under test."""

    def test_bookmark_panel_control_paint_is_scoped_to_the_bookmark_panel(self):
        field_ids = (
            "editBMPanel_namePicker",
            "editBMPanel_locationField",
            "editBMPanel_tagsField",
            "editBMPanel_keywordField",
        )
        normal_ids = (
            "editBMPanel_folderMenuList",
            "editBookmarkPanelDoneButton",
            "editBookmarkPanelRemoveButton",
        )
        field_selectors = tuple(
            f"#editBookmarkPanel #{field_id}" for field_id in field_ids
        )
        normal_selectors = tuple(
            f"#editBookmarkPanel #{normal_id}" for normal_id in normal_ids
        )
        hover_selectors = tuple(
            selector + ":hover:not([disabled])"
            for selector in normal_selectors
        )
        selectors = field_selectors + normal_selectors + hover_selectors
        self.assert_rule_names_scoped_to("editBookmark", set(selectors))
        self.assert_rules_match_required(selectors)
        for selector in field_selectors + normal_selectors:
            self.assertNotIn(":hover", selector)
        for selector in hover_selectors:
            self.assertIn(":hover", selector)
            self.assertIn(":not([disabled])", selector)
        self.assertEqual(
            {name for name in selectors
             if "--button-border-radius" in self.rules[name]},
            set(),
        )
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if any(token in declarations for token in (
                 "--input-border-color",
                 "--input-text-background-color",
                 "--border-radius-medium",
             ))
             # The Library window's search box sets the shadow
             # moz-input-text tokens on its own host element; the
             # custom properties inherit into that host's shadow tree
             # only, so they cannot reach the bookmark panel's fields.
             and name != "moz-input-search#searchFilter"},
            set(),
        )

        panel = element(
            "panel", "editBookmarkPanel", ("panel-no-padding",),
            attrs={"type": "arrow"},
        )
        header = element(
            "box", "editBookmarkPanelHeader", ("panel-header",), parent=panel
        )
        heading = element("h1", parent=header)
        title = element("span", "editBookmarkPanelTitle", parent=heading)
        separator = element(
            "toolbarseparator", "editBookmarkHeaderSeparator", parent=panel
        )
        body = element(
            "vbox", "editBookmarkPanelBody", ("panel-subview-body",),
            parent=panel,
        )
        content = element(
            "div", "editBookmarkPanelContent", parent=body
        )
        folder_row = element(
            "hbox", classes=("editBMPanel_folderRow",), parent=content
        )
        folder_menu = element(
            "menulist", "editBMPanel_folderMenuList", ("folder-icon",),
            parent=folder_row,
        )
        folders_expander = element(
            "button", "editBMPanel_foldersExpander",
            ("expander-down", "panel-button"), parent=folder_row,
        )
        folder_tree_row = element(
            "vbox", "editBMPanel_folderTreeRow", parent=content
        )
        new_folder = element(
            "button", "editBMPanel_newFolderButton", parent=folder_tree_row
        )
        tags_row = element(
            "hbox", classes=("editBMPanel_tagsRow",), parent=content
        )
        tags_selector_expander = element(
            "button", "editBMPanel_tagsSelectorExpander",
            ("expander-down", "panel-button"), parent=tags_row,
        )
        tags_selector_row = element(
            "div", "editBMPanel_tagsSelectorRow", parent=content
        )
        tags_selector = element(
            "richlistbox", "editBMPanel_tagsSelector",
            parent=tags_selector_row,
        )
        tags_autocomplete = element(
            "panel", "editBMPanel_tagsAutocomplete", parent=content
        )
        checkbox = element(
            "checkbox", "editBookmarkPanel_showForNewBookmarks",
            parent=content,
        )
        footer = element(
            "moz-button-group", classes=("panel-footer",), parent=panel
        )
        done_button = element(
            "button", "editBookmarkPanelDoneButton", ("footer-button",),
            attrs={"default": ""}, parent=footer,
        )
        remove_button = element(
            "button", "editBookmarkPanelRemoveButton", ("footer-button",),
            parent=footer,
        )

        fields = {
            "editBMPanel_namePicker": element(
                "input", "editBMPanel_namePicker", parent=content
            ),
            "editBMPanel_locationField": element(
                "input", "editBMPanel_locationField", parent=content
            ),
            "editBMPanel_tagsField": element(
                "input", "editBMPanel_tagsField", parent=tags_row
            ),
            "editBMPanel_keywordField": element(
                "input", "editBMPanel_keywordField", parent=content
            ),
        }

        for field_id, selector in zip(field_ids, field_selectors):
            control = fields[field_id]
            with self.subTest(field=field_id):
                self.assertTrue(matches(selector, control))
                self.assertTrue(matches(selector, {**control, "hover": True}))

        for name, control, normal, hover in (
            ("folder_menu", folder_menu, normal_selectors[0],
             hover_selectors[0]),
            ("done_button", done_button, normal_selectors[1],
             hover_selectors[1]),
            ("remove_button", remove_button, normal_selectors[2],
             hover_selectors[2]),
        ):
            with self.subTest(control=name):
                self.assertTrue(matches(normal, control))
                self.assertTrue(matches(normal, {**control, "hover": True}))
                self.assertTrue(matches(hover, {**control, "hover": True}))
                self.assertFalse(matches(hover, control))
                disabled = {
                    **control,
                    "attrs": {**control["attrs"], "disabled": ""},
                    "hover": True,
                }
                self.assertTrue(matches(normal, disabled))
                self.assertFalse(matches(hover, disabled))

        for name, control in (
            ("header", header),
            ("title", title),
            ("separator", separator),
            ("content", content),
            ("folder_row", folder_row),
            ("folders_expander", folders_expander),
            ("folder_tree_row", folder_tree_row),
            ("new_folder", new_folder),
            ("tags_row", tags_row),
            ("tags_selector_expander", tags_selector_expander),
            ("tags_selector_row", tags_selector_row),
            ("tags_selector", tags_selector),
            ("tags_autocomplete", tags_autocomplete),
            ("checkbox", checkbox),
        ):
            with self.subTest(unthemed=name):
                for selector in selectors:
                    self.assertFalse(matches(selector, control))
                    self.assertFalse(
                        matches(selector, {**control, "hover": True})
                    )

        nav_bar = element("toolbar", "nav-bar")
        nav_button = element(
            "toolbarbutton", classes=("subviewbutton",), parent=nav_bar
        )
        for selector in selectors:
            self.assertFalse(matches(selector, nav_button))
            self.assertFalse(
                matches(selector, {**nav_button, "hover": True})
            )

        dialog = element("dialog", "bookmarkpropertiesdialog")
        dialog_content = element(
            "div", "editBookmarkPanelContent", parent=dialog
        )
        for field_id in field_ids:
            dialog_field = element(
                "input", field_id, parent=dialog_content
            )
            with self.subTest(dialog_field=field_id):
                for selector in selectors:
                    self.assertFalse(matches(selector, dialog_field))
                    self.assertFalse(
                        matches(selector, {**dialog_field, "hover": True})
                    )
        dialog_menulist = element(
            "menulist", "editBMPanel_folderMenuList", parent=dialog_content
        )
        for selector in selectors:
            self.assertFalse(matches(selector, dialog_menulist))
            self.assertFalse(
                matches(selector, {**dialog_menulist, "hover": True})
            )

    def test_bookmark_panel_provenance(self):
        self.assert_header_names((
            "No reference shows Firefox's bookmark editor",
            "widgets/lineedit.svg",
            "tests/test_desktoptheme_lineedit.py::TestLineEdit",
            *BUTTON_REFERENCES,
            *VIEWITEM_REFERENCES,
            "test_selection_background",
            "#editBookmarkPanel",
            "editBookmarkPanelTemplate",
            "editBMPanel_namePicker",
            "editBMPanel_locationField",
            "editBMPanel_tagsField",
            "editBMPanel_keywordField",
            "editBMPanel_folderMenuList",
            "editBookmarkPanelDoneButton",
            "editBookmarkPanelRemoveButton",
            "chrome/browser/content/browser/browser-places.js",
            "chrome/browser/content/browser/places/editBookmark.js",
            "chrome/browser/skin/classic/browser/places/editBookmarkPanel.css",
            "chrome/browser/skin/classic/browser/places/editBookmark.css",
            "chrome/toolkit/skin/classic/global/global-shared.css",
            "chrome/toolkit/skin/classic/global/button.css",
            "chrome/toolkit/skin/classic/global/menulist.css",
            "#bookmarkpropertiesdialog",
            "platform adaptation 2026-10-26",
        ))

if __name__ == "__main__":
    unittest.main()
