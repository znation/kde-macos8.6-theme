"""Validate the Firefox Platinum sheet's panel and view row paints.

The downloads panel's rows and buttons, the all-tabs view, the app menu,
the overflow and unified-extensions panels and the bookmark panel for the
standalone ``userChrome.css``.
"""

from __future__ import annotations

import unittest

from support.firefox_chrome_cases import (
    BUTTON_REFERENCES,
    REQUIRED_RULES,
    VIEWITEM_REFERENCES,
    FirefoxChromeTestCase,
)
from support.platinum_palette import FACE, SELECTION
from support.selector_matching import element, matches


class TestFirefoxPanelRows(FirefoxChromeTestCase):
    """Section of the Firefox chrome sheet under test."""

    def test_downloads_panel_row_paint_is_scoped_to_the_panel_list(self):
        row = "#downloadsPanel #downloadsListBox > richlistitem"
        hover = row + ":not([selected]):hover"
        selected = row + "[selected]"
        self.assertEqual(
            {name for name in self.rules if "downloadsListBox" in name},
            {row, hover, selected},
        )
        for selector in (row, hover, selected):
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith(row))
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        self.assertIn(":not([selected])", hover)
        self.assertIn(":hover", hover)
        self.assertEqual(self.rules[hover]["background-color"],
                         f"{FACE} !important")
        self.assertEqual(self.rules[selected]["background-color"],
                         f"{SELECTION} !important")
        self.assertLess(
            self.selectors.index(hover),
            self.selectors.index(selected),
        )

    def test_downloads_panel_button_paint_is_scoped_to_the_panel(self):
        normal = (
            "#downloadsPanel .downloadsPanelFooterButton:not([disabled])",
            "#downloadsPanel .downloadButton:not([disabled])",
            "#downloadsPanel .footer-button:not([disabled])",
        )
        hover = tuple(selector + ":hover" for selector in normal)
        selectors = normal + hover
        self.assertEqual(
            {name for name in self.rules
             if name.startswith("#downloadsPanel ")
             and ("downloadButton" in name
                  or "downloadsPanelFooterButton" in name
                  or "footer-button" in name)},
            set(selectors),
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith("#downloadsPanel "))
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        for selector in normal:
            self.assertNotIn(":hover", selector)
            self.assertIn(":not([disabled])", selector)
        for selector in hover:
            self.assertIn(":not([disabled]):hover", selector)

        panel = element(
            "panel", "downloadsPanel", attrs={"type": "arrow"}
        )
        main_view = element(
            "panelview", "downloadsPanel-mainView", parent=panel
        )
        listbox = element(
            "richlistbox", "downloadsListBox", parent=main_view
        )
        row = element("richlistitem", parent=listbox)
        main_area = element(
            "hbox", classes=("downloadMainArea",), parent=row
        )
        download_button = element(
            "button", classes=("downloadButton",), parent=row
        )
        footer = element("vbox", "downloadsFooter", parent=panel)
        history = element(
            "button", "downloadsHistory",
            ("downloadsPanelFooterButton", "subviewbutton",
             "panel-subview-footer-button", "toolbarbutton-1"),
            parent=footer,
        )
        blocked = element(
            "panelview", "downloadsPanel-blockedSubview", parent=panel
        )
        blocked_buttons = element(
            "moz-button-group", "downloadsPanel-blockedSubview-buttons",
            ("panel-footer",), parent=blocked,
        )
        unblock = element(
            "button", "downloadsPanel-blockedSubview-unblockButton",
            ("footer-button",), parent=blocked_buttons,
        )
        delete = element(
            "button", "downloadsPanel-blockedSubview-deleteButton",
            ("footer-button",), attrs={"default": ""},
            parent=blocked_buttons,
        )
        private = element(
            "panelview", "downloadsPanel-privateBrowsing", parent=panel
        )
        secondary = element(
            "button", classes=("footer-button", "secondary"), parent=private
        )
        primary = element(
            "button", classes=("footer-button", "primary"), parent=private
        )

        for name, control, normal_selector, hover_selector in (
            ("downloads_history", history, normal[0], hover[0]),
            ("download_button", download_button, normal[1], hover[1]),
            ("blocked_unblock", unblock, normal[2], hover[2]),
            ("blocked_delete", delete, normal[2], hover[2]),
            ("private_secondary", secondary, normal[2], hover[2]),
            ("private_primary", primary, normal[2], hover[2]),
        ):
            with self.subTest(control=name):
                self.assertTrue(matches(normal_selector, control))
                self.assertTrue(
                    matches(normal_selector, {**control, "hover": True})
                )
                self.assertTrue(
                    matches(hover_selector, {**control, "hover": True})
                )
                self.assertFalse(matches(hover_selector, control))
                disabled = {
                    **control,
                    "attrs": {**control["attrs"], "disabled": ""},
                    "hover": True,
                }
                self.assertFalse(matches(normal_selector, disabled))
                self.assertFalse(matches(hover_selector, disabled))

        summary = element("label", "downloadsSummary", parent=footer)
        progress = element(
            "progress", "downloadsSummaryProgress", parent=footer
        )
        blocked_title = element(
            "span", "downloadsPanel-blockedSubview-title", parent=blocked
        )
        header = element(
            "box", "downloadsPanelHeader", ("panel-header",), parent=panel
        )
        for name, control in (
            ("summary", summary),
            ("progress", progress),
            ("main_area", main_area),
            ("blocked_title", blocked_title),
            ("header", header),
        ):
            with self.subTest(unthemed=name):
                for selector in selectors:
                    self.assertFalse(matches(selector, control))
                    self.assertFalse(
                        matches(selector, {**control, "hover": True})
                    )

        external_listbox = element("richlistbox", "downloadsListBox")
        external_row = element("richlistitem", parent=external_listbox)
        external_button = element(
            "button", classes=("downloadButton",), parent=external_row
        )
        for selector in selectors:
            self.assertFalse(matches(selector, external_button))
            self.assertFalse(
                matches(selector, {**external_button, "hover": True})
            )

        bookmark_panel = element("panel", "editBookmarkPanel")
        bookmark_done = element(
            "button", "editBookmarkPanelDoneButton", ("footer-button",),
            parent=bookmark_panel,
        )
        for selector in selectors:
            self.assertFalse(matches(selector, bookmark_done))
            self.assertFalse(
                matches(selector, {**bookmark_done, "hover": True})
            )

    def test_all_tabs_row_paint_is_scoped_to_the_all_tabs_view(self):
        row = "#allTabsMenu-allTabsView .all-tabs-item"
        button = "#allTabsMenu-allTabsView .all-tabs-item > .all-tabs-button"
        hover = (
            "#allTabsMenu-allTabsView .all-tabs-item:not([selected])"
            " > .all-tabs-button:hover"
        )
        selected = (
            "#allTabsMenu-allTabsView .all-tabs-item[selected]"
            " > .all-tabs-button"
        )
        self.assertEqual(
            {name for name in self.rules
             if "allTabsMenu" in name or "all-tabs" in name},
            {row, button, hover, selected},
        )
        for selector in (row, button, hover, selected):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "--panel-menuitem-border-radius" in declarations},
            set(),
        )
        self.assertIn(":not([selected])", hover)
        self.assertIn(":hover", hover)
        self.assertEqual(self.rules[hover]["background-color"],
                         f"{FACE} !important")
        self.assertEqual(self.rules[selected]["background-color"],
                         f"{SELECTION} !important")
        self.assertLess(
            self.selectors.index(hover),
            self.selectors.index(selected),
        )

    def test_app_menu_row_paint_is_scoped_to_the_app_menu(self):
        radius = "#appMenu-popup .subviewbutton:not(.panel-header .subviewbutton)"
        hover = radius + ":hover:not([disabled])"
        self.assertEqual(
            {name for name in self.rules if "appMenu" in name},
            {radius, hover},
        )
        for selector in (radius, hover):
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith(radius))
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        self.assertIn(":not([disabled])", hover)
        self.assertIn(":hover", hover)
        self.assertIn(":not(.panel-header .subviewbutton)", radius)
        self.assertEqual(set(self.rules[radius]), {"border-radius"})
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "--panel-menuitem-border-radius" in declarations},
            set(),
        )

        panel = element("panel", "appMenu-popup")
        main_view = element(
            "panelview", "appMenu-mainView", ("PanelUI-subView",),
            parent=panel,
        )
        body = element(
            "vbox", classes=("panel-subview-body",), parent=main_view
        )
        row = element(
            "toolbarbutton", "appMenu-settings-button", ("subviewbutton",),
            parent=body,
        )
        footer_rows = {
            "history": element(
                "toolbarbutton", "PanelUI-historyMore",
                ("subviewbutton", "panel-subview-footer-button"),
                parent=element("panelview", "PanelUI-history", parent=panel),
            ),
            "bookmarks": element(
                "toolbarbutton", "panelMenu_showAllBookmarks",
                ("subviewbutton", "panel-subview-footer-button"),
                parent=element("panelview", "PanelUI-bookmarks", parent=panel),
            ),
        }
        header = element(
            "box", "PanelUI-profiles-header", ("panel-header",),
            parent=element("panelview", "PanelUI-profiles", parent=panel),
        )
        header_buttons = {
            "back": element(
                "toolbarbutton", "profiles-appmenu-back-button",
                ("subviewbutton", "subviewbutton-iconic", "subviewbutton-back"),
                parent=header,
            ),
            "edit": element(
                "toolbarbutton", "profiles-edit-this-profile-button",
                ("subviewbutton", "subviewbutton-iconic"),
                parent=header,
            ),
        }
        self.assertTrue(matches(radius, row))
        self.assertTrue(matches(hover, {**row, "hover": True}))
        self.assertFalse(matches(hover, row))
        self.assertFalse(
            matches(hover, {**row, "hover": True, "attrs": {"disabled": ""}})
        )
        for name, button in footer_rows.items():
            with self.subTest(footer_row=name):
                self.assertTrue(matches(radius, button))
                self.assertTrue(matches(hover, {**button, "hover": True}))
        for name, button in header_buttons.items():
            with self.subTest(header_button=name):
                self.assertFalse(matches(radius, button))
                self.assertFalse(matches(hover, {**button, "hover": True}))

    def test_overflow_panel_row_paint_is_scoped_to_the_overflow_panel(self):
        radius_rows = (
            "#widget-overflow .subviewbutton:not(.panel-header .subviewbutton)",
            "#widget-overflow .widget-overflow-list .toolbarbutton-1",
        )
        hover_rows = (
            radius_rows[0] + ":hover:not([disabled])",
            radius_rows[1] + ":hover:not([disabled])",
        )
        self.assertEqual(
            {name for name in self.rules if "widget-overflow" in name},
            set(radius_rows + hover_rows),
        )
        for selector in radius_rows + hover_rows:
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith("#widget-overflow"))
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        for selector in radius_rows:
            self.assertEqual(set(self.rules[selector]), {"border-radius"})
        for selector in hover_rows:
            self.assertIn(":hover", selector)
            self.assertIn(":not([disabled])", selector)
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "--panel-menuitem-border-radius" in declarations},
            set(),
        )

        panel = element("panel", "widget-overflow")
        main_view = element(
            "panelmultiview", "widget-overflow-mainView", parent=panel
        )
        body = element(
            "vbox", classes=("panel-subview-body",), parent=main_view
        )
        overflow_lists = {
            "main": element(
                "vbox", "widget-overflow-list", ("widget-overflow-list",),
                parent=body,
            ),
            "fixed": element(
                "vbox", "widget-overflow-fixed-list",
                ("widget-overflow-list",), parent=body,
            ),
        }
        overflowed_rows = {
            name: element(
                "toolbarbutton", classes=("toolbarbutton-1",), parent=row_list
            )
            for name, row_list in overflow_lists.items()
        }
        footer = element(
            "toolbarbutton", "overflowMenu-customize-button",
            ("subviewbutton", "panel-subview-footer-button"), parent=body,
        )
        header = element("box", classes=("panel-header",), parent=main_view)
        header_button = element(
            "toolbarbutton", "overflow-panel-back-button",
            ("subviewbutton", "subviewbutton-back"), parent=header,
        )
        nav_bar_button = element(
            "toolbarbutton", "nav-bar-button", ("toolbarbutton-1",),
            parent=element("toolbar", "nav-bar"),
        )

        for name, row in overflowed_rows.items():
            with self.subTest(overflowed_row=name):
                self.assertTrue(matches(radius_rows[1], row))
                self.assertTrue(matches(hover_rows[1], {**row, "hover": True}))
                self.assertFalse(matches(hover_rows[1], row))

        self.assertTrue(matches(radius_rows[0], footer))
        self.assertTrue(matches(hover_rows[0], {**footer, "hover": True}))
        self.assertFalse(matches(hover_rows[0], footer))

        disabled = {
            **overflowed_rows["main"], "attrs": {"disabled": ""},
            "hover": True,
        }
        for selector in hover_rows:
            self.assertFalse(matches(selector, disabled))

        for selector in radius_rows + hover_rows:
            with self.subTest(selector=selector):
                self.assertFalse(matches(selector, header_button))
                self.assertFalse(
                    matches(selector, {**header_button, "hover": True})
                )
                self.assertFalse(matches(selector, nav_bar_button))
                self.assertFalse(
                    matches(selector, {**nav_bar_button, "hover": True})
                )

    def test_unified_extensions_panel_row_paint_is_scoped_to_the_panel(self):
        radius = (
            "#unified-extensions-panel .subviewbutton"
            ":not(.panel-header .subviewbutton)"
            ":not(.unified-extensions-item-menu-button)"
            ":not(#unified-extensions-discover-extensions)"
        )
        hover = radius + ":hover:not([disabled])"
        gear_hover = (
            "#unified-extensions-panel "
            ".unified-extensions-item-menu-button:hover"
        )
        selectors = (radius, hover, gear_hover)
        self.assertEqual(
            {name for name in self.rules if "unified-extensions" in name},
            set(selectors),
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertTrue(selector.startswith("#unified-extensions-panel"))
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
        self.assertEqual(set(self.rules[radius]), {"border-radius"})
        self.assertEqual(set(self.rules[gear_hover]), {"box-shadow"})
        self.assertIn(":hover", hover)
        self.assertIn(":not([disabled])", hover)
        for selector in (radius, hover):
            self.assertIn(
                ":not(.unified-extensions-item-menu-button)", selector
            )
            self.assertIn(":not(.panel-header .subviewbutton)", selector)
            self.assertIn(
                ":not(#unified-extensions-discover-extensions)", selector
            )
        self.assertEqual(
            {name for name, declarations in self.rules.items()
             if "--panel-menuitem-border-radius" in declarations},
            set(),
        )

        panel = element("panel", "unified-extensions-panel")
        view = element(
            "panelview", "unified-extensions-view",
            ("cui-widget-panelview",), parent=panel,
        )
        body = element(
            "vbox", classes=("panel-subview-body",), parent=view
        )
        extensions_list = element(
            "vbox", classes=("unified-extensions-list",), parent=body
        )
        item = element("unified-extensions-item", parent=extensions_list)
        row = element(
            "box", classes=("unified-extensions-item-row-wrapper",),
            parent=item,
        )
        action = element(
            "toolbarbutton",
            classes=(
                "unified-extensions-item-action-button", "subviewbutton",
            ),
            parent=row,
        )
        gear = element(
            "toolbarbutton",
            classes=(
                "unified-extensions-item-menu-button", "subviewbutton",
                "subviewbutton-iconic",
            ),
            parent=row,
        )
        area = element("vbox", "unified-extensions-area", parent=body)
        extension_btn = element(
            "toolbarbutton",
            classes=("webextension-browser-action", "subviewbutton"),
            parent=area,
        )
        footer = element(
            "toolbarbutton", "unified-extensions-manage-extensions",
            ("subviewbutton", "panel-subview-footer-button"), parent=body,
        )
        discover = element(
            "moz-button", "unified-extensions-discover-extensions",
            ("subviewbutton", "panel-subview-footer-button"), parent=body,
        )
        header = element("box", classes=("panel-header",), parent=view)
        header_button = element(
            "toolbarbutton", "unified-extensions-header-button",
            ("subviewbutton",), parent=header,
        )
        nav_bar_button = element(
            "toolbarbutton", "nav-bar-button", ("toolbarbutton-1",),
            parent=element("toolbar", "nav-bar"),
        )

        for name, row_button in (
            ("action", action),
            ("webextension", extension_btn),
            ("footer", footer),
        ):
            with self.subTest(row=name):
                self.assertTrue(matches(radius, row_button))
                self.assertTrue(
                    matches(hover, {**row_button, "hover": True})
                )
                self.assertFalse(matches(hover, row_button))

        disabled = {
            **action, "attrs": {"disabled": ""}, "hover": True,
        }
        self.assertFalse(matches(hover, disabled))

        for name, unthemed in (
            ("gear", gear),
            ("header", header_button),
            ("nav_bar", nav_bar_button),
            ("discover", discover),
        ):
            with self.subTest(unthemed=name):
                self.assertFalse(matches(radius, unthemed))
                self.assertFalse(
                    matches(hover, {**unthemed, "hover": True})
                )
        self.assertTrue(matches(gear_hover, {**gear, "hover": True}))

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
        self.assertEqual(
            {name for name in self.rules if "editBookmark" in name},
            set(selectors),
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])
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
