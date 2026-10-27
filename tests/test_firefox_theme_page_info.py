"""Validate the Firefox Platinum sheet's Page Info dialog paints.

The Page Info view tabs and action buttons, the readonly display fields,
the permission list, the meta and image trees, the media preview and the
security groupboxes for the standalone ``userChrome.css``.
"""

from __future__ import annotations

import unittest

from support.firefox_chrome_cases import (
    BUTTON_REFERENCES,
    PAGE_INFO_CONTROL_IDS,
    REQUIRED_RULES,
    VIEWITEM_REFERENCES,
    FirefoxChromeTestCase,
)
from support.selector_matching import element, matches


class TestFirefoxPageInfo(FirefoxChromeTestCase):
    """Section of the Firefox chrome sheet under test."""

    def test_page_info_control_paint_is_scoped_to_page_info(self):
        tab_selectors = (
            "#viewGroup > radio",
            "#viewGroup > radio[selected]",
            "#viewGroup > radio:not([selected]):hover",
        )
        button_selectors = tuple(
            f"#mainDeck {control}:not([disabled])"
            for control in PAGE_INFO_CONTROL_IDS
        )
        hover_selectors = tuple(
            selector + ":hover" for selector in button_selectors
        )
        selectors = ("#topBar",) + tab_selectors + button_selectors \
            + hover_selectors
        field_selectors = ("#mainDeck input",)
        self.assertEqual(
            {name for name in self.rules
             if "#topBar" in name or "#viewGroup" in name
             or "#mainDeck" in name},
            set(selectors) | set(field_selectors),
        )
        for selector in selectors + field_selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], REQUIRED_RULES[selector])

        window = element("window", "pageInfoWindow")
        top_bar = element("vbox", "topBar", parent=window)
        view_group = element(
            "radiogroup", "viewGroup", ("chromeclass-toolbar",),
            parent=top_bar,
        )
        tabs = {
            "generalTab": element("radio", "generalTab", parent=view_group),
            "mediaTab": element(
                "radio", "mediaTab", attrs={"hidden": "true"},
                parent=view_group,
            ),
            "permTab": element("radio", "permTab", parent=view_group),
            "securityTab": element(
                "radio", "securityTab", parent=view_group
            ),
        }
        selected_tab = element(
            "radio", "generalTab", attrs={"selected": "true"},
            parent=view_group,
        )
        main_deck = element("deck", "mainDeck", parent=window)
        general_panel = element("vbox", "generalPanel", parent=main_deck)
        media_panel = element("vbox", "mediaPanel", parent=main_deck)
        perm_panel = element("vbox", "permPanel", parent=main_deck)
        security_panel = element("vbox", "securityPanel", parent=main_deck)
        buttons = {
            "general help-button": element(
                "button", "helpButton", ("help-button",),
                attrs={"command": "cmd_help"}, parent=general_panel,
            ),
            "media help-button": element(
                "button", "helpButton", ("help-button",),
                attrs={"command": "cmd_help"}, parent=media_panel,
            ),
            "perm help-button": element(
                "button", "helpButton", ("help-button",),
                attrs={"command": "cmd_help"}, parent=perm_panel,
            ),
            "security help-button": element(
                "button", "helpButton", ("help-button",),
                attrs={"command": "cmd_help"}, parent=security_panel,
            ),
            "selectallbutton": element(
                "button", "selectallbutton", ("small-button",),
                parent=media_panel,
            ),
            "imagesaveasbutton": element(
                "button", "imagesaveasbutton", parent=media_panel,
            ),
            "mediasaveasbutton": element(
                "button", "mediasaveasbutton", parent=media_panel,
            ),
            "security-view-qwac": element(
                "button", "security-view-qwac", parent=security_panel,
            ),
            "security-view-cert": element(
                "button", "security-view-cert", parent=security_panel,
            ),
            "security-clear-sitedata": element(
                "button", "security-clear-sitedata", parent=security_panel,
            ),
            "security-view-password": element(
                "button", "security-view-password", parent=security_panel,
            ),
        }

        unscoped = (
            element("input", "titletext", parent=general_panel),
            element("input", "urltext", parent=general_panel),
            element("tree", "metatree", parent=general_panel),
            element("tree", "imagetree", parent=media_panel),
            element("label", classes=("tooltip-label",),
                    parent=general_panel),
            element("listitem", "permList", ("perm-item",),
                    parent=perm_panel),
            element("row", "perm-row", parent=perm_panel),
            element("table", "security-technical", parent=security_panel),
            element("description", "security-technical-label",
                    parent=security_panel),
            element("preview", "mediaPreview", parent=media_panel),
            element("button", "selectallbutton", parent=top_bar),
            element("button", "helpButton", ("help-button",),
                    parent=view_group),
            element("toolbar", "navigator-toolbox", parent=top_bar),
        )

        for name, tab in tabs.items(): 
            with self.subTest(tab=name):
                self.assertTrue(matches(tab_selectors[0], tab))
                self.assertFalse(matches(tab_selectors[1], tab))
                self.assertFalse(matches(tab_selectors[2], tab))
                self.assertFalse(
                    matches(tab_selectors[1], {**tab, "hover": True})
                )
        with self.subTest(selected="selected_tab"):
            self.assertTrue(matches(tab_selectors[0], selected_tab))
            self.assertTrue(matches(tab_selectors[1], selected_tab))
            self.assertFalse(
                matches(tab_selectors[2], {**selected_tab, "hover": True})
            )
        with self.subTest(state="hovered_unselected_tab"):
            hovered = {**tabs["permTab"], "hover": True}
            self.assertTrue(matches(tab_selectors[2], hovered))

        for name, button in buttons.items():
            selector = (
                "#mainDeck #selectallbutton:not([disabled])"
                if name == "selectallbutton"
                else "#mainDeck .help-button:not([disabled])"
                if name.endswith("help-button")
                else f"#mainDeck #{name}:not([disabled])"
            )
            with self.subTest(button=name):
                self.assertTrue(matches(selector, button))
                self.assertTrue(matches(selector, {**button, "hover": True}))
                self.assertFalse(matches(selector + ":hover", button))
                self.assertTrue(
                    matches(selector + ":hover", {**button, "hover": True})
                )
                disabled = {
                    **button,
                    "attrs": {**button["attrs"], "disabled": ""},
                    "hover": True,
                }
                self.assertFalse(matches(selector, disabled))
                self.assertFalse(matches(selector + ":hover", disabled))

        for control in unscoped:
            with self.subTest(unthemed=control["id"] or control["tag"]):
                for selector in selectors:
                    self.assertFalse(matches(selector, control))
                    self.assertFalse(
                        matches(selector, {**control, "hover": True})
                    )

    def test_page_info_provenance(self):
        self.assert_header_names((
            "No reference shows Firefox's Page Info window",
            "widgets/tabbar.svg",
            "tests/test_desktoptheme_tabbar.py::TestTabBar",
            "tests/test_desktoptheme_tabbar.py::TestTabBarReference",
            "tests/test_desktoptheme_line.py::TestLineReference",
            "test_view_background_alternate",
            *BUTTON_REFERENCES,
            *VIEWITEM_REFERENCES,
            "test_selection_background",
            "pageInfo.xhtml",
            "pageInfo.js",
            "pageInfo.css",
            "#topBar",
            "#viewGroup",
            "#mainDeck",
            "#generalTab",
            "#selectallbutton",
            "#security-view-qwac",
            "platform adaptation 2026-10-26",
        ))

    def test_page_info_field_paint_is_scoped_to_page_info(self):
        self.assertIn("#mainDeck input", self.rules)
        self.assertEqual(
            self.rules["#mainDeck input"], REQUIRED_RULES["#mainDeck input"]
        )
        selector = "#mainDeck input"

        window = element("window", "pageInfoWindow")
        main_deck = element("deck", "mainDeck", parent=window)
        general_panel = element("vbox", "generalPanel", parent=main_deck)
        security_panel = element(
            "vbox", "securityPanel", parent=main_deck
        )
        fields = {
            "titletext": element(
                "input", "titletext", attrs={"readonly": "readonly"},
                parent=general_panel,
            ),
            "imagetypetext": element(
                "input", "imagetypetext", parent=general_panel
            ),
            "hostText": element(
                "input", "hostText", attrs={"readonly": "readonly"},
                parent=security_panel,
            ),
        }
        for name, field in fields.items():
            with self.subTest(field=name):
                self.assertTrue(matches(selector, field))
                # No hover or focus variant exists: a focused readonly
                # display field keeps the same paint (Firefox draws the
                # focus ring).
                self.assertTrue(matches(selector, {**field, "hover": True}))

        other_sheets = (
            element("textbox", None, ("findbar-textbox",),
                    parent=element("toolbar", "findbar")),
            element("input", "editBMPanel_locationField",
                    parent=element("vbox", "editBookmarkPanel")),
            element("input", "searchbar-textbox", classes=("searchbar-textbox",),
                    parent=element("toolbar", "searchbar")),
            element("input", "urltext",
                    parent=element("toolbar", "navigator-toolbox")),
        )
        for stray in other_sheets:
            with self.subTest(unthemed=stray["id"] or stray["classes"]):
                self.assertFalse(matches(selector, stray))
                self.assertFalse(matches(selector, {**stray, "hover": True}))

        self.assertNotIn(
            "#mainDeck input:not([readonly])", self.rules
        )
        self.assertNotIn("#mainDeck input:hover", self.rules)
        self.assertNotIn("#mainDeck input:focus", self.rules)
        self.assertEqual(
            [name for name in self.rules if "#mainDeck input" in name],
            ["#mainDeck input"],
        )

    def test_page_info_media_preview_paint_is_scoped_to_page_info(self):
        self.assertIn("#imagecontainerbox", self.rules)
        self.assertEqual(
            self.rules["#imagecontainerbox"],
            REQUIRED_RULES["#imagecontainerbox"],
        )
        selector = "#imagecontainerbox"

        window = element("window", "pageInfoWindow")
        main_deck = element("deck", "mainDeck", parent=window)
        media_preview_box = element(
            "vbox", "mediaPreviewBox", parent=main_deck
        )
        container = element(
            "vbox", "imagecontainerbox", parent=media_preview_box
        )
        theimagecontainer = element(
            "hbox", "theimagecontainer", parent=container
        )
        media_browser = element(
            "browser", "mediaBrowser", parent=theimagecontainer
        )
        broken_container = element(
            "hbox", "brokenimagecontainer", parent=theimagecontainer
        )
        broken_image = element(
            "image", "brokenimage", parent=broken_container
        )
        # The pane is a static preview surface: with and without hover it
        # keeps the same paint, and no hover or focus variant exists.
        for hover in (False, True):
            candidate = {**container, "hover": hover}
            with self.subTest(hover=hover):
                self.assertTrue(matches(selector, candidate))

        # The preview's children keep Firefox's own paint: they match no
        # selector whose name contains imagecontainerbox.
        preview_rules = [
            name for name in self.rules if "imagecontainerbox" in name
        ]
        for name, child in (
            ("#mediaBrowser", media_browser),
            ("#brokenimage", broken_image),
            ("brokenimagecontainer", broken_container),
            ("theimagecontainer", theimagecontainer),
        ):
            with self.subTest(unthemed=child["id"] or name):
                self.assertFalse(
                    any(matches(rule, child) for rule in preview_rules)
                )

        other_sheets = (
            element("textbox", None, ("findbar-textbox",),
                    parent=element("toolbar", "findbar")),
            element("input", "editBMPanel_locationField",
                    parent=element("vbox", "editBookmarkPanel")),
            element("input", "searchbar-textbox",
                    classes=("searchbar-textbox",),
                    parent=element("toolbar", "searchbar")),
            element("input", "urltext",
                    parent=element("toolbar", "navigator-toolbox")),
        )
        for stray in other_sheets:
            with self.subTest(unthemed=stray["id"] or stray["classes"]):
                self.assertFalse(
                    any(matches(rule, stray) for rule in preview_rules)
                )

        self.assertEqual(preview_rules, ["#imagecontainerbox"])
        self.assertNotIn("#imagecontainerbox:hover", self.rules)
        self.assertNotIn("#imagecontainerbox:focus", self.rules)
        self.assertNotIn("#mediaPreviewBox", self.rules)

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

    def test_page_info_field_provenance(self):
        self.assert_header_names((
            "No reference shows Firefox's Page Info window",
            "#mainDeck input",
            "#titletext",
            "#imagetypetext",
            "html:input#hostText",
            "widgets/lineedit.svg",
            "firstboot_betawiki.png",
            "tests/test_desktoptheme_lineedit.py::TestLineEdit",
            "TestLineEditReference",
            "pageInfo.xhtml",
            "pageInfo.css",
            "#FFFFFF face",
            "1px #000000 outline",
            "#999999 sunken",
            "no hover or focus variant",
            "platform adaptation 2026-10-26",
        ))

    def test_page_info_media_preview_provenance(self):
        header = self.text.split("*/", 1)[0]
        for provenance in (
            "No reference shows Firefox's Page Info media preview",
            "#imagecontainerbox",
            "widgets/lineedit.svg",
            "firstboot_betawiki.png",
            "tests/test_desktoptheme_lineedit.py::TestLineEdit",
            "TestLineEditReference",
            "#mainDeck input",
            "pageInfo.xhtml",
            "#mediaBrowser",
            "#brokenimagecontainer",
            "pageInfo.css",
            "Field",
            "ThreeDLightShadow",
            "no hover, focus or selected variant",
            "platform colour adaptation 2026-10-26",
            "Declaration checks do not establish rendered pixels",
        ):
            with self.subTest(provenance=provenance):
                self.assertIn(provenance, header)

    def test_page_info_permission_list_paint_is_scoped_to_page_info(self):
        perm_rules = [
            name for name in self.rules
            if "permList" in name
            or (".permission" in name and "permission-popup" not in name)
        ]
        self.assertEqual(
            sorted(perm_rules),
            ["#permList", "#permList .permission:hover"],
        )
        for name in perm_rules:
            with self.subTest(rule=name):
                self.assertEqual(self.rules[name], REQUIRED_RULES[name])
        # #permList paints the container, not its rows: the hover rule is the
        # only row rule, and it carries no bevel.
        self.assertEqual(
            [name for name in self.rules if ".permission" in name
             and "permission-popup" not in name],
            ["#permList .permission:hover"],
        )

        window = element("window", "pageInfoWindow")
        main_deck = element("deck", "mainDeck", parent=window)
        perm_panel = element("vbox", "permPanel", parent=main_deck)
        perm_list = element("vbox", "permList", parent=perm_panel)
        row = element("vbox", None, ("permission",), parent=perm_list)
        child_panel = element("vbox", "permPanel", parent=main_deck)
        container = element("vbox", "permList", parent=child_panel)
        for hover in (False, True):
            candidate = {**row, "hover": hover}
            with self.subTest(hover=hover):
                self.assertEqual(
                    matches("#permList .permission:hover", candidate), hover
                )
                # #permList is a container selector: a row is never the
                # list itself.
                self.assertFalse(matches("#permList", row))
        self.assertTrue(matches("#permList", container))

        security_panel = element("vbox", "securityPanel", parent=main_deck)
        host_text = element(
            "input", "hostText", attrs={"readonly": "readonly"},
            parent=security_panel,
        )
        self.assertTrue(matches("#mainDeck input", host_text))
        self.assertFalse(matches("#permList", host_text))
        self.assertFalse(
            matches("#permList .permission:hover", {**host_text, "hover": True})
        )

        other_list = element("vbox", "otherList")
        stray_row = element(
            "vbox", None, ("permission",), parent=other_list
        )
        self.assertFalse(matches("#permList", stray_row))
        self.assertFalse(
            matches("#permList .permission:hover", {**stray_row, "hover": True})
        )

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
            "label", "strayHeader", ("header",), parent=other_panel
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

    def test_page_info_permission_list_provenance(self):
        self.assert_header_names((
            "No reference shows Firefox's Page Info permission list",
            "widgets/lineedit.svg",
            "firstboot_betawiki.png",
            "tests/test_desktoptheme_lineedit.py::TestLineEdit",
            "TestLineEditReference",
            "#mainDeck input",
            "widgets/listitem.svg",
            "tests/test_desktoptheme_listitem.py::TestListItem",
            "no hover highlight",
            "#prefs > tr:hover",
            "permissions.js",
            "createRow",
            "pageInfo.css",
            "-moz-default-appearance: listbox",
            "-moz-dialog",
            "#permList",
            ".permission",
            "platform colour adaptation 2026-10-26",
        ))



if __name__ == "__main__":
    unittest.main()
