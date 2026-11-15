"""Validate the standalone GTK 4 Platinum stylesheet.

The sheet is one standalone ``gtk.css`` under ``gtk-4.0``. The palette is
reference-grounded through ``support.platinum_palette``; no reference
screenshot shows a GTK widget, so the GTK geometry is this theme's adaptation
rather than a reference crop.
"""

from __future__ import annotations

import re
import unittest

from support.gtk_css import HEX, strip_comments
from support.gtk4_sheet import (
    DEFINED_COLOURS, Gtk4SheetRuleCases,
)
from support.gtk_theme_spec import (
    DISABLED_TEXT,
    ETCH_DARK,
    SHEET_PALETTE,
    ROW_HOVER,
    ROW_SELECTED,
    VIEW_BACKGROUND,
)
from support.platinum_palette import (
    BLACK,
    FACE,
    INACTIVE_OUTLINE,
    SELECTION,
    WHITE,
)
class TestGtk4Theme(Gtk4SheetRuleCases, unittest.TestCase):
    def test_header_subtitle_foreground(self):
        selectors = ("headerbar .subtitle", "windowtitle .subtitle")
        self.assert_disabled_text(selectors)
        expected = {**DISABLED_TEXT, "opacity": "1"}
        self.assert_rule_group(dict.fromkeys(selectors, expected))

    def test_separator_label_foreground(self):
        self.assert_separator_label_foreground()

    def test_placeholder_foreground(self):
        selectors = (
            "entry > text > placeholder",
            "spinbutton > text > placeholder",
            "spinbutton.vertical > text > text > placeholder",
        )
        self.assert_disabled_text(selectors)
        expected = {**DISABLED_TEXT, "opacity": "1"}
        for selector in selectors:
            self.assertEqual(self.rules[selector], expected)
            self.assertEqual(self.css.count(selector), 1)

    def test_dimmed_label_foreground(self):
        selector = "label.dimmed"
        self.assert_disabled_text((selector,))
        self.assert_rule(selector, {**DISABLED_TEXT, "opacity": "1"})
        self.assertEqual(self.selectors.count(selector), 1)
        self.assertNotIn(".dimmed", self.selectors)

    def test_theme_colours(self):
        self.assertEqual(self.colours, DEFINED_COLOURS)

    def test_icon_sources_resolve_to_shipped_files(self):
        self.assert_icon_sources_resolve()

    def test_stands_alone(self):
        self.assertNotIn("@import", self.css)
        self.assert_shipped_asset_urls()
        self.assertNotIn("adwaita", self.css.lower())

    def test_only_palette_hex_literals(self):
        self.assertEqual(set(HEX.findall(strip_comments(self.css))), SHEET_PALETTE)

    def test_no_status_or_translucent_shade_roles(self):
        # Scan the raw declarations, not the parsed hex map, so a status or
        # shade role declared with a non-hex value (for example rgba(...))
        # cannot escape this check.
        names = re.findall(
            r"@define-color\s+([-A-Za-z0-9_]+)", strip_comments(self.css)
        )
        for name in names:
            with self.subTest(colour=name):
                self.assertFalse(
                    name.startswith(
                        ("success_", "warning_", "error_", "destructive_")
                    ),
                )
                self.assertFalse(
                    name == "shade_color" or name.endswith("_shade_color")
                )

    def test_no_universal_selector(self):
        for selector in self.selectors:
            self.assertNotIn("*", selector)

    def test_window_and_background(self):
        for selector in ("window", ".background"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "color": BLACK,
                    "border-radius": "0",
                },
            )

    def test_csd_window_shell(self):
        """The CSD top levels draw the shipped Aurorae frame, not stock's blur."""
        active = {"border-radius": "0", "box-shadow": f"0 0 0 1px {BLACK}"}
        backdrop = {"box-shadow": f"0 0 0 1px {INACTIVE_OUTLINE}"}
        flat = {"border-radius": "0", "box-shadow": "none"}
        solid = {"padding": "0", "border": f"solid 1px {BLACK}",
                 "box-shadow": "none"}
        solid_backdrop = {"border-color": INACTIVE_OUTLINE,
                          "box-shadow": "none"}
        expected = {
            "window.csd": active,
            "window.csd:backdrop": {**backdrop, "transition": "none"},
            "window.csd.popup": active,
            "window.csd.popup:backdrop": backdrop,
            "window.csd.dialog.message": active,
            "window.csd.dialog.message:backdrop": backdrop,
            "window.maximized": flat,
            "window.fullscreen": flat,
            "window.maximized:backdrop": flat,
            "window.fullscreen:backdrop": flat,
            "window.tiled": active,
            "window.tiled-top": active,
            "window.tiled-left": active,
            "window.tiled-right": active,
            "window.tiled-bottom": active,
            "window.tiled:backdrop": backdrop,
            "window.tiled-top:backdrop": backdrop,
            "window.tiled-left:backdrop": backdrop,
            "window.tiled-right:backdrop": backdrop,
            "window.tiled-bottom:backdrop": backdrop,
            "window.ssd": {"box-shadow": "none"},
            "window.solid-csd": solid,
            "window.solid-csd:backdrop": solid_backdrop,
            "tooltip.csd": flat,
        }
        self.assert_rule_group(expected)

        # The appended tail block is a family bound: every shell top-level
        # selector (a window.-prefixed node selector without descendant
        # combinators, plus tooltip.csd) is one of the restated twinned arms
        # or the existing message-dialog body squaring, and none beyond them.
        family = {
            selector
            for selector in self.selectors
            if selector == "tooltip.csd" or re.fullmatch(r"window\.[\w:.-]+", selector)
        }
        self.assertEqual(family, {*expected, "window.dialog.message.csd.background"})

        # Each appended arm sits after the existing window group it out-ranks,
        # and the backdrop arms sit after window.csd:backdrop, which otherwise
        # ties them on specificity: without that order an unfocused maximized
        # or tiled window would paint the active outline. The solid-csd arms
        # follow the stock "Window Decorations" order: after the window.csd
        # arms they beat on source position and before window.maximized to
        # preserve stock shadow ordering. These shadow rules do not clear
        # the solid-csd border. The backdrop arm follows its base arm.
        self.assertGreater(
            self.selectors.index("window.solid-csd"),
            self.selectors.index("window.csd"),
        )
        self.assertGreater(
            self.selectors.index("window.maximized"),
            self.selectors.index("window.solid-csd"),
        )
        self.assertGreater(
            self.selectors.index("window.solid-csd:backdrop"),
            self.selectors.index("window.solid-csd"),
        )
        for selector in "window.csd", "window.csd:backdrop", "window.maximized":
            self.assertGreater(
                self.selectors.index(selector), self.selectors.index("window")
            )
        self.assertGreater(
            self.selectors.index("tooltip.csd"), self.selectors.index("tooltip")
        )
        self.assertGreater(
            self.selectors.index("window.maximized:backdrop"),
            self.selectors.index("window.csd:backdrop"),
        )
        self.assertGreater(
            self.selectors.index("window.tiled:backdrop"),
            self.selectors.index("window.csd:backdrop"),
        )
        # The compositor-less solid-csd arms rest after the window.csd arms
        # they out-rank and before the maximized group, so a maximized or
        # tiled solid-csd window keeps its state-specific shadow rule.
        self.assertGreater(
            self.selectors.index("window.solid-csd"),
            self.selectors.index("window.csd.dialog.message:backdrop"),
        )
        self.assertGreater(
            self.selectors.index("window.solid-csd:backdrop"),
            self.selectors.index("window.solid-csd"),
        )
        self.assertGreater(
            self.selectors.index("window.solid-csd:backdrop"),
            self.selectors.index("window.csd:backdrop"),
        )
        self.assertGreater(
            self.selectors.index("window.maximized"),
            self.selectors.index("window.solid-csd"),
        )
        self.assertGreater(
            self.selectors.index("window.maximized"),
            self.selectors.index("window.solid-csd:backdrop"),
        )

    def test_csd_window_shell_state_cascade(self):
        """Resolve overlapping shell arms, including popup/backdrop ties."""
        cases = [
            ("window.csd", f"0 0 0 1px {BLACK}"),
            ("window.csd:backdrop", f"0 0 0 1px {INACTIVE_OUTLINE}"),
            ("window.csd.popup", f"0 0 0 1px {BLACK}"),
            ("window.csd.popup:backdrop", f"0 0 0 1px {INACTIVE_OUTLINE}"),
            ("window.csd.dialog.message:backdrop", f"0 0 0 1px {INACTIVE_OUTLINE}"),
            ("window.csd.maximized:backdrop", "none"),
            ("window.csd.fullscreen:backdrop", "none"),
            ("window.ssd", "none"),
            ("tooltip.csd", "none"),
        ]
        for tiled in ("tiled", "tiled-top", "tiled-left", "tiled-right", "tiled-bottom"):
            cases.append((f"window.csd.{tiled}:backdrop", f"0 0 0 1px {INACTIVE_OUTLINE}"))
        for node, expected in cases:
            with self.subTest(node=node):
                # This family contains only a type, classes and :backdrop.
                # CSS ranks class/pseudo-class count before source order.
                tokens = set(re.findall(r"[.:][\w-]+", node))
                element = re.match(r"\w+", node).group()
                candidates = []
                for order, selector in enumerate(self.selectors):
                    if not re.fullmatch(r"(?:window|tooltip)(?:[.:][\w-]+)*", selector):
                        continue
                    required = set(re.findall(r"[.:][\w-]+", selector))
                    rule = self.rules[selector]
                    if (selector.split(".")[0].split(":")[0] == element
                            and required <= tokens and "box-shadow" in rule):
                        candidates.append((len(required), order, rule["box-shadow"]))
                self.assertTrue(candidates)
                self.assertEqual(max(candidates)[2], expected)

        # Solid shells must not reintroduce a frame on maximized/fullscreen
        # windows or override the tiled state arms (including backdrop ties).
        for state in ("maximized", "fullscreen", "tiled", "tiled-top",
                      "tiled-left", "tiled-right", "tiled-bottom"):
            for suffix in ("", ":backdrop"):
                with self.subTest(state=state, suffix=suffix):
                    self.assertLess(
                        self.selectors.index("window.solid-csd" + suffix),
                        self.selectors.index("window." + state + suffix),
                    )

    def test_submenu_arrow(self):
        self.assert_submenu_arrow(
            ("popover.menu modelbutton > arrow.right",), sized=False
        )

    def test_tree_and_column_headers(self):
        selectors = (
            "columnview.view > header > button",
            "treeview.view > header > button",
        )
        self.assert_tree_header(selectors)
        for selector in selectors:
            self.assert_rule(
                f"{selector} sort-indicator.ascending",
                {"-gtk-icon-source": 'url("../assets/arrow-up.svg")'},
            )
            self.assert_rule(
                f"{selector} sort-indicator.descending",
                {"-gtk-icon-source": 'url("../assets/arrow-down.svg")'},
            )

    def test_text_selection(self):
        self.assert_text_selection(
            (
                "text > selection", "label > selection",
                "entry > text > selection",
                "spinbutton:not(.vertical) > text > selection",
                "spinbutton.vertical > text > text > selection",
                "spinbutton.vertical > text > selection",
                "editablelabel > stack > text > selection",
                "textview > text > selection",
            )
        )

    def test_label_error_colour_class(self):
        # The existing label policy takes no colour class: the sheet restates
        # the two stock error colour-class arms with byte-equal twins
        # declaring the existing inherited black text and the existing
        # insensitive grey, so an error-classed label paints the existing
        # policy instead of stock's red, and its disabled twin paints the
        # existing grey instead of stock's translucent red. Stock ships no
        # `label.warning` arm, so there is nothing to restate there.
        for selector in ("label.error", "label.error:disabled"):
            self.assertEqual(self.selectors.count(selector), 1)
        self.assertEqual(self.rules["label.error"], {"color": BLACK})
        self.assertEqual(self.rules["label.error:disabled"], {"color": ETCH_DARK})

    def test_dim_label_foreground(self):
        selector = ".dim-label"
        self.assert_disabled_text((selector,))
        self.assert_rule(selector, {**DISABLED_TEXT, "opacity": "1"})
        self.assertEqual(strip_comments(self.css).count(selector), 1)

    def test_content_view_field_and_hover(self):
        self.assert_rule(".content-view", VIEW_BACKGROUND)
        self.assert_rule(".content-view:hover", {"-gtk-icon-filter": "none"})

    def test_server_list_button_rotation_motion(self):
        # The places view's server-button icon keeps stock's two
        # orientations (upright at rest, half a turn while checked) while
        # the 200ms rotation ease is erased: the two byte-equal stock twin
        # spellings declare only `transition: none`, sitting after the
        # existing caps-lock groups at the sheet tail.
        selectors = (
            "placesview .server-list-button > image",
            "placesview .server-list-button:checked > image",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1, selector)
                self.assert_rule(selector, {"transition": "none"})
                # Exact-dict, not the per-property subset: a stray
                # rotation, transform, colour or geometry declaration on
                # either twin must fail, per the entry's guarantee.
                self.assertEqual(self.rules[selector], {"transition": "none"}, selector)
        self.assertEqual(
            {s for s in self.rules if "server-list-button" in s},
            set(selectors),
        )
        self.assertGreater(
            self.selectors.index("placesview .server-list-button > image"),
            self.selectors.index("entry.password image.caps-lock-indicator"),
        )
    def test_list_row_press_and_popup_faces(self):
        # The pressed and popup-holding row states restate the existing
        # faces: stock's toolkit resource and the integration library's
        # base.css resource would paint a tinted hover-wash, pressed
        # insets-wash-or-an-accent fill on rows the existing records paint
        # transparent or with the flat lavender selection, and the
        # integration library paints background colors on the pressed
        # spellings as well as the toolkit's insets.
        expected = {
            "row.activatable.has-open-popup": dict(ROW_HOVER),
            "row.activatable:hover": dict(ROW_HOVER),
            "row.activatable:active": {"background-color": "transparent", "box-shadow": "none"},
            "row.activatable:selected:active": {"background-color": SELECTION, "box-shadow": "none"},
            "row.activatable:selected.has-open-popup": {"background-color": SELECTION},
            "row.activatable:selected:hover": {"background-color": SELECTION},
        }
        self.assert_rule_group(expected)
        # The existing row spellings are all list-, listview-, columnview-
        # or popover-armed, and the existing bare-row groups spell `row` and
        # `row:focus:focus-visible`, so this element-level family is
        # exactly six.
        self.assertEqual(
            {s for s in self.rules if s.startswith("row.activatable")},
            set(expected),
        )
        self.assertGreater(
            self.selectors.index("row.activatable:active"),
            self.selectors.index("list row.activatable:selected"),
        )

    def test_places_sidebar(self):
        self.assert_rule(".sidebar", {"background-color": FACE, "color": BLACK})
        self.assert_rule(".sidebar:backdrop", {"background-color": FACE, "color": BLACK})
        self.assert_rule(
            "placessidebar.sidebar:not(separator):dir(ltr)", {"border": "none"}
        )
        self.assert_rule(
            "placessidebar.sidebar:not(separator):dir(rtl)", {"border": "none"}
        )
        self.assert_rule(
            "placessidebar .navigation-sidebar > row.sidebar-new-bookmark-row",
            {"color": BLACK},
        )
        # The drag-session arms restate the stock drop strip and drag-over
        # row twins on the existing selection lavender with black ink;
        # each keeps stock's own
        # geometry members so the byte-equal spelling wins the cascade by
        # later user-sheet source order.
        expected_drop = {
            "placessidebar .navigation-sidebar > row.sidebar-placeholder-row": {
                "padding": "0 8px",
                "min-height": "2px",
                "background-image": f"image({SELECTION})",
                "background-clip": "content-box",
            },
            "placessidebar .navigation-sidebar > row:drop(active):not(:disabled)": {
                "color": BLACK,
                "box-shadow":
                    f"inset 0 1px {SELECTION}, inset 0 -1px {SELECTION}",
            },
            "placessidebar .navigation-sidebar > row:drop(active):not(:disabled):selected": {
                "color": BLACK,
                "background-color": SELECTION,
            },
        }
        self.assert_rule_group(expected_drop)
        # The drag-over family is exactly these two arms: the sweep kills a
        # renamed spelling or a stray twin.
        self.assertEqual(
            {s for s in self.rules
             if s.startswith("placessidebar .navigation-sidebar > row:drop")},
            {
                "placessidebar .navigation-sidebar > row:drop(active):not(:disabled)",
                "placessidebar .navigation-sidebar > row:drop(active):not(:disabled):selected",
            },
        )

    def test_stack_switcher_tabs(self):
        forms = {
            "base": ("stackswitcher > button",),
            "hover": ("stackswitcher > button:hover",),
            "checked": ("stackswitcher > button:checked",),
            "checked+hover": ("stackswitcher > button:checked:hover",),
        }
        self.assert_tab_faces(forms)

    def test_rubberband(self):
        selectors = {
            "rubberband",
            ".content-view > rubberband",
            "columnview.view > rubberband",
            "treeview.view > rubberband",
            "gridview > rubberband",
            "flowbox > rubberband",
        }
        self.assert_rubberband(tuple(selectors))
        self.assertEqual(
            {selector for selector in self.rules if "rubberband" in selector},
            selectors,
        )

    def test_iconview_drop_border(self):
        self.assert_rule(
            "iconview > dndtarget:drop(active)",
            {"border": f"1px solid {SELECTION}"},
        )

    def test_list_row_focus_outlines(self):
        """Keyboard-focused rows paint the existing black focus colour."""
        spellings = (
            "row:focus:focus-visible",
            ".boxed-list > row:focus:focus-visible",
            "stacksidebar row:focus:focus-visible",
            ".navigation-sidebar > row:focus-visible:focus-within",
            "list.boxed-list > row:focus:focus-visible",
            "list.content > row:focus:focus-visible",
            "list.boxed-list > row.expander row.header:focus:focus-visible",
            "list.content > row.expander row.header:focus:focus-visible",
            "row.expander list.nested > row:focus:focus-visible",
            "list.boxed-list-separate > row:focus:focus-visible",
            "list.boxed-list-separate > row.expander row.header:focus:focus-visible",
        )
        for selector in spellings:
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, {"outline-color": BLACK})
        # The restated spellings are the only row focus arms the sheet
        # declares: the scan kills renamed and stray variants. A row arm
        # must start the selector or follow a space, so the notebook
        # overflow arrow's own focus arm (its node name ends in "row")
        # does not join this family.
        suffixes = (
            "row:focus:focus-visible",
            "row.header:focus:focus-visible",
            "row:focus-visible:focus-within",
        )
        self.assertEqual(
            {selector for selector in self.rules
             if any(
                 selector.endswith(suffix)
                 and (len(selector) == len(suffix)
                      or selector[-len(suffix) - 1] == " ")
                 for suffix in suffixes)},
            set(spellings),
        )
        # Stock's generic 300 ms outline-motion arm is removed.
        self.assert_exact_rule_once("row", {"transition": "none"})
        # Source order: the focus group sits after the existing
        # disabled-selected backdrop group and before the existing tab-close
        # block.
        self.assertGreater(
            self.selectors.index("row:focus:focus-visible"),
            self.selectors.index("columnview.view:disabled:selected:backdrop"),
        )
        self.assertLess(
            self.selectors.index("row:focus:focus-visible"),
            self.selectors.index(
                "notebook > header > tabs > tab button.flat:disabled"),
        )

    def test_needs_attention_badges(self):
        """Needs-attention labels and images keep no stock accent pulse."""
        spellings = (
            "stacksidebar row.needs-attention > label",
            "stackswitcher > button.needs-attention > label",
            "stackswitcher > button.needs-attention > image",
        )
        for selector in spellings:
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, {"animation": "none", "background-image": "none"})
        # Source order: the restated group sits after the existing row-focus
        # outline rule and before the existing tab-close block.
        self.assertGreater(
            self.selectors.index("stacksidebar row.needs-attention > label"),
            self.selectors.index("row:focus:focus-visible"),
        )
        self.assertLess(
            self.selectors.index("stacksidebar row.needs-attention > label"),
            self.selectors.index("notebook > header > tabs > tab button.flat"),
        )
        # The restated spellings are the only needs-attention arms the sheet
        # declares: the scan kills renamed and stray variants.
        # The restated spellings are the only needs-attention arms the sheet
        # declares beside the 2026-11-04 tab-thumbnail badge cap: the scan
        # kills renamed and stray variants.
        self.assertEqual(
            {selector for selector in self.rules
             if "needs-attention" in selector},
            set(spellings) | {"tabthumbnail .needs-attention > widget"},
        )
        # The badge cap states only the corner radius; the label spellings'
        # animation and dot-image clears do not apply to it.
        self.assert_rule("tabthumbnail .needs-attention > widget",
                         {"border-radius": "0"})
        self.assertEqual(
            self.selectors.count("tabthumbnail .needs-attention > widget"), 1)
        self.assert_matches_frame("tabthumbnail .needs-attention > widget",
                                  "border-radius")

    def test_header_drop_indicator(self):
        expected = {
            "background-color": SELECTION,
            "background-image": "none",
            "color": BLACK,
            "text-shadow": "none",
            "box-shadow": "none",
            "border-style": "none",
            "border-radius": "0",
        }
        for scope in ("columnview.view > header", "treeview.view > header"):
            for state in ("", ":hover", ":active", ":selected"):
                with self.subTest(scope=scope, state=state):
                    self.assert_rule(f"{scope} > button.dnd{state}", expected)
        self.assert_rule(
            "window.print:not(.ssd-frame) treeview.dialog-action-box > header > button.dnd",
            expected,
        )

    def test_columnview_and_listview_rows(self):
        self.assert_rule("listview > row.activatable:hover", ROW_HOVER)
        for selector in (
            "columnview.view:selected",
            "columnview.view:selected:hover",
            "listview > row.activatable:selected",
            "listview > row.activatable:selected:hover",
        ):
            self.assert_rule(selector, ROW_SELECTED)

    def test_spinner(self):
        self.assert_spinner("transform")

    def test_tabgrid_card_focus(self):
        base = "tabgrid > tabgridchild .card"
        focus = "tabgrid > tabgridchild:focus:focus-visible .card"
        self.assert_scale_slider_transition(base)
        self.assert_scale_focus_outline(focus)
        for selector in (base, focus):
            self.assertEqual(self.selectors.count(selector), 1)
        self.assertEqual(
            {selector for selector in self.rules if "tabgridchild" in selector},
            {base, focus},
        )

    def test_toolbar_and_menubar(self):
        for selector in (".toolbar", "menubar"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "border-bottom": f"1px solid {ETCH_DARK}",
                    "box-shadow": f"inset 0 -1px {WHITE}",
                },
            )

if __name__ == "__main__":
    unittest.main()
