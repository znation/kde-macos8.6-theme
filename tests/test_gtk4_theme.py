"""Validate the standalone GTK 4 Platinum stylesheet.

The sheet is one standalone ``gtk.css`` under ``gtk-4.0``. The palette is
reference-grounded through ``support.platinum_palette``; no reference
screenshot shows a GTK widget, so the GTK geometry is this theme's adaptation
rather than a reference crop.
"""

from __future__ import annotations

import re
import tempfile
import unittest
from unittest import mock

from support import gtk_css
from support.gtk_css import HEX, parse_css, strip_comments
from support.gtk4_sheet import (
    CSS, DEFINED_COLOURS, SCALE_SLIDER, Gtk4SheetRuleCases,
)
from support.gtk_rule_cases import (
    ROW_SELECTED_BUTTON_ARM_SIDEBAR,
    ROW_SELECTED_BUTTON_ARM_SIDEBAR_BACKDROP,
)
from support.gtk_theme_spec import (
    BUTTON_BEVEL,
    CHECK,
    CHECK_GLYPH,
    COMBO_ARROW,
    DISABLED_TEXT,
    ENTRY_FIELD,
    ETCH_DARK,
    LINK,
    MENUBUTTON_ARROWS,
    MENU_CHECK,
    SHEET_PALETTE,
    INVERTED_BUTTON_BEVEL,
    MIXED_GLYPH,
    PROGRESSBAR_TROUGH,
    RAISED_BEVEL,
    RADIO,
    RADIO_GLYPH,
    ROW_HOVER,
    ROW_SELECTED,
    SELECTION_CHECK_STATES,
    TEXT_SELECTION,
    TILE_CHECK_FACE,
    TITLE_BUTTON_ASSETS,
    TITLE_BUTTON_IMAGE,
    TITLE_BUTTON_IMAGE_STATE,
    VIEW_BACKGROUND,
)
from support.desktoptheme_paths import SETUP_MAX_ROWS, SETUP_REFERENCE
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    INACTIVE_OUTLINE,
    SELECTION,
    TROUGH,
    WHITE,
    hex_colour,
)
from support.reference_image import ReferenceScreenshotMixin
from support.symlink_fixtures import symlinked_repo
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
        for ref in re.findall(r'url\("([^"]*)"\)', self.css):
            self.assertTrue((CSS.parent / ref).resolve().is_file(), ref)

    def test_stands_alone(self):
        self.assertNotIn("@import", self.css)
        self.assertEqual(
            set(re.findall(r"url\(([^)]*)\)", self.css)),
            {
                '"../assets/checkmark.svg"',
                '"../assets/bullet.svg"',
                '"../assets/check-mixed.svg"',
                '"../assets/arrow-down.svg"',
                '"../assets/arrow-up.svg"',
                '"../assets/arrow-right.svg"',
                '"../assets/submenu-arrow.svg"',
                '"../assets/window-close.svg"',
                '"../assets/window-maximize.svg"',
                '"../assets/window-minimize.svg"',
            },
        )
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
        # or the landed message-dialog body squaring, and none beyond them.
        family = {
            selector
            for selector in self.selectors
            if selector == "tooltip.csd" or re.fullmatch(r"window\.[\w:.-]+", selector)
        }
        self.assertEqual(family, {*expected, "window.dialog.message.csd.background"})

        # Each appended arm sits after the landed window group it out-ranks,
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

    def test_expander_arrows(self):
        self.assert_expander_arrows(
            ("treeview.view.expander", "expander"),
            ("treeview.view.expander:checked", "expander:checked"),
        )

    def test_rtl_collapsed_expander_arrows(self):
        selectors = (
            "treeview.view.expander:not(:checked):dir(rtl)",
            "expander:not(:checked):dir(rtl)",
        )
        for selector in selectors:
            self.assert_rule(selector, {"-gtk-icon-transform": "scaleX(-1)"})
            self.assertEqual(self.selectors.count(selector), 1)
        self.assertEqual(
            {selector for selector, declarations in self.rules.items()
             if "-gtk-icon-transform" in declarations},
            set(selectors),
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

    def test_selected_text_arms(self):
        focus = (
            "label > selection:focus-within",
            "textview > text > selection:focus-within",
            "entry > text > selection:focus-within",
            "spinbutton:not(.vertical) > text > selection:focus-within",
            "spinbutton.vertical > text > text > selection:focus-within",
            "spinbutton.vertical > text > selection:focus-within",
            "editablelabel > stack > text > selection:focus-within",
        )
        disabled = (
            "label:disabled > selection",
            "label:disabled:selected",
            "textview > text:disabled:selected",
            "textview > text:disabled:selected:focus",
        )
        for selector in focus:
            self.assert_rule(selector, TEXT_SELECTION)
        self.assert_disabled_text(disabled)
        self.assertEqual(
            {s for s in self.rules if s in focus or s in disabled},
            set(focus) | set(disabled),
        )

    def test_label_error_colour_class(self):
        # The landed label policy takes no colour class: the sheet restates
        # the two stock error colour-class arms with byte-equal twins
        # declaring the landed inherited black text and the landed
        # insensitive grey, so an error-classed label paints the landed
        # policy instead of stock's red, and its disabled twin paints the
        # landed grey instead of stock's translucent red. Stock ships no
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

    def test_view_background(self):
        self.assert_view_background((".view", "list"))

    def test_content_view_field_and_hover(self):
        self.assert_rule(".content-view", VIEW_BACKGROUND)
        self.assert_rule(".content-view:hover", {"-gtk-icon-filter": "none"})

    def test_tile_check_faces(self):
        """Pin the eight 32px content-view tile-check state faces.

        The 2026-11-05 sheet-tail record restates the toolkit resource's
        eight class-armed comma triples (probed verbatim in the sheet
        comment and docs/invariants.md) with the landed check face under
        every state: the four unchecked spellings carry the raised
        etched face with the zero radius and hard black outline, the
        four checked ones the same under the shipped checkmark glyph.
        Stock's 32px geometry, margins, residual colour and 200ms
        transition and the unchecked none icon source stay inherited
        per-property (no declaration here), so this dictionary is the
        whole group.
        """
        states = SELECTION_CHECK_STATES
        class_armed = tuple(
            f"{head}{state}:not(list)"
            for state in states
            for head in (
                ".view.content-view.check",
                "iconview.content-view.check",
            )
        )
        tile_members = tuple(
            f".content-view .tile check{state}:not(list)" for state in states
        )
        unchecked = dict(TILE_CHECK_FACE)
        checked = {**unchecked, "-gtk-icon-source": CHECK_GLYPH["-gtk-icon-source"]}
        expected = {
            selector: dict(unchecked) for selector in class_armed + tile_members
        }
        for state in states[4:]:
            for head in (
                ".view.content-view.check",
                "iconview.content-view.check",
            ):
                expected[f"{head}{state}:not(list)"] = dict(checked)
            expected[f".content-view .tile check{state}:not(list)"] = dict(
                checked
            )
        self.assert_rule_group(expected)
        # The class-armed sweep: every rule carrying the content-view.check
        # token is one of the sixteen `.view`/`iconview` spellings, and the
        # `.tile check` token reaches exactly the eight third members.
        self.assertEqual(
            {s for s in self.rules if "content-view.check" in s},
            set(class_armed),
        )
        self.assertEqual(
            {s for s in self.rules if ".tile check" in s},
            set(tile_members),
        )
        # Provenance guards: the landed `.content-view` field and hover
        # arms, the landed element `check`/`radio` recipes, the four merged
        # checked and indeterminate glyph unions the plain-state record
        # pins and the merged zero-radius `check` key stay byte-equal, so
        # the tile record added no declaration to any landed key.
        self.assert_rule(".content-view", VIEW_BACKGROUND)
        self.assert_rule(".content-view:hover", {"-gtk-icon-filter": "none"})
        self.assert_rule("check", CHECK)
        self.assertEqual(self.selectors.count("check"), 2)
        self.assert_rule("radio", RADIO)
        check_face = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": CHECK["box-shadow"],
        }
        check_checked_face = {**check_face, "background-color": FACE}
        radio_face = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": "none",
        }
        self.assert_rule("check:checked", {**CHECK_GLYPH, **check_checked_face})
        self.assert_rule("radio:checked", {**RADIO_GLYPH, **radio_face})
        self.assert_rule(
            "check:indeterminate", {**MIXED_GLYPH, **check_checked_face}
        )
        self.assert_rule(
            "radio:indeterminate", {**MIXED_GLYPH, **radio_face}
        )

    def test_treeview_selected_check_radio_faces(self):
        """Pin the selected-row check and radio restated off the landed faces.

        The 2026-11-06 sheet-tail record answers the Default-light
        resource's four treeview-class-armed selected-row arms (probed
        verbatim in the sheet comment and docs/invariants.md) per-property:
        the colour arm's ink and border return to the landed check recipe's
        hard black, the checked and indeterminate glyph arms swap the
        toolkit's recoloured symbolic dot and dash for the landed black-ink
        shipped assets, and stock's radius and 14px-size arm restates
        nothing. No landing here adds a face declaration beyond the two
        answers per member spelling.
        """
        seal = {"color": BLACK, "border-color": BLACK}
        expected = {
            "treeview.view check:selected:focus": dict(seal),
            "treeview.view check:selected": dict(seal),
            "treeview.view radio:selected:focus": dict(seal),
            "treeview.view radio:selected": dict(seal),
            "treeview.view radio:checked:selected": dict(RADIO_GLYPH),
            "treeview.view radio:indeterminate:selected": dict(MIXED_GLYPH),
        }
        self.assert_rule_group(expected)
        # The family sweep: every rule carrying one of the two
        # treeview-class-armed control tokens is one of the six spellings
        # above, so no stock arm of either group survives unrepresented.
        self.assertEqual(
            {
                s
                for s in self.rules
                if "treeview.view check" in s or "treeview.view radio" in s
            },
            set(expected),
        )
        # Source order: each restated spelling lands after the landed
        # plain-state `radio:checked` glyph rule's parsed position.
        for selector in expected:
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("radio:checked"),
                selector,
            )

    def test_links(self):
        self.assert_links(
            ("button.link",),
            ("link", "button.link > label"),
            ("link:visited", "button.link:visited > label"),
            {"text-decoration": "underline"},
        )

    def test_inline_link_interaction_colours(self):
        css = strip_comments(self.css)
        self.assert_rule("link:hover", {"color": LINK})
        self.assert_rule("link:active", {"color": LINK})
        self.assert_disabled_text(("link:disabled",))
        hover = css.index("link:hover")
        active = css.index("link:active")
        visited = css.index("link:visited")
        disabled = css.index("link:disabled")
        self.assertLess(hover, visited)
        self.assertLess(active, visited)
        self.assertGreater(disabled, visited)

    def test_selected_inline_link_foregrounds(self):
        roots = ("link:selected:not(:disabled)", "link:visited:selected:not(:disabled)")
        selectors = gtk_css.inline_link_state_selectors(roots)
        css = strip_comments(self.css)
        for selector in selectors:
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], {"color": TEXT_SELECTION["color"]}, selector)
            for ordinary in ("link:visited", "link:hover", "link:active"):
                self.assertGreater(css.index(selector), css.index(ordinary), selector)

    def test_selected_ancestor_inline_link_foregrounds(self):
        roots = (":selected link:not(:disabled)", ":selected link:visited:not(:disabled)")
        selectors = gtk_css.inline_link_state_selectors(roots)
        css = strip_comments(self.css)
        selected_links = css.index("link:selected:not(:disabled)")
        for selector in selectors:
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assert_rule(selector, {"color": TEXT_SELECTION["color"]})
            self.assertEqual(self.rules[selector], {"color": TEXT_SELECTION["color"]})
            for earlier in ("link:visited", "link:hover", "link:active"):
                self.assertGreater(css.index(selector), css.index(earlier), selector)
            self.assertGreater(css.index(selector), selected_links, selector)

    def test_link_button_follows_the_button_state_rules(self):
        # button.link ties button:hover and :active on specificity, so only
        # coming later keeps the link button faceless while hovered or pressed.
        link = self.css.index("button.link {")
        for rule in ("button {", "button:hover {", "button:active, button:checked {"):
            self.assertGreater(link, self.css.index("\n" + rule), rule)






    def test_button_focus_outline_color(self):
        self.assert_scale_focus_outline("button:focus:focus-visible")

    def test_headerbar_button_focus_outline_color(self):
        self.assert_bar_family_focus("headerbar ", "headerbar ")

    def test_toolbar_button_focus_outline_color(self):
        self.assert_bar_family_focus(".toolbar ", ".toolbar")

    def test_actionbar_button_focus_outline_color(self):
        self.assert_bar_family_focus("actionbar > revealer > box ", "actionbar")

    def test_searchbar_button_focus_outline_color(self):
        self.assert_bar_family_focus(
            "searchbar > revealer > box ",
            "searchbar",
            extra=(".close:focus:focus-visible",),
        )

    def test_filechooser_breadcrumb_focus_outline_color(self):
        selectors = {
            "filechooser #pathbarbox > stack > box > button:focus:focus-visible",
            "filechooser #pathbarbox > stack > box > box > button:focus:focus-visible",
            "filechooser #pathbarbox > stack > box > menubutton > button:focus:focus-visible",
        }
        self.assertEqual(
            {selector for selector in self.selectors if "pathbarbox" in selector},
            selectors,
        )
        self.assert_black_focus_outline(selectors)

    def test_sidebar_button_focus_outline_color(self):
        self.assert_black_focus_outline(("button.sidebar-button:focus:focus-visible",))

    def test_checkbutton_focus_outline_color(self):
        self.assert_scale_focus_outline("checkbutton:focus:focus-visible")

    def test_button_focus_transition(self):
        self.assert_scale_slider_transition("button")

    def test_button_disabled_and_backdrop(self):
        self.assert_button_disabled_and_backdrop()

    def test_button_checked_hover_and_active(self):
        expected = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
        }
        for selector in ("button:checked:hover", "button:checked:active"):
            self.assert_rule(selector, expected)

    def test_button_hover_icon_filter(self):
        # No reference screenshot shows a hovered GTK push button; stock
        # brightens every icon inside one, so the tail arm clears the filter
        # while the landed `button:hover` face group stays the face source.
        self.assert_rule(
            "button:hover",
            {"background-color": FACE, "-gtk-icon-filter": "none"},
        )


    def test_suggested_action_plain_arms(self):
        self.assert_plain_action_arms("button.suggested-action")

    def test_destructive_action_plain_arms(self):
        self.assert_plain_action_arms("button.destructive-action")

    def test_action_class_flat_arms(self):
        # No reference screenshot shows a GTK flat action button; the tail
        # arms restate the landed push-button recipe over the stock
        # transparent colour-class flat family, so every checked
        # relationship below anchors the landed face constants and the two
        # family inventories keep the arms to stock's own spellings.
        face = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
        }
        sunken = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
        }
        insensitive = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        for prefix in ("button.suggested-action", "button.destructive-action"):
            with self.subTest(action_class=prefix):
                self.assert_rule(f"{prefix}.flat", face)
                for state in (":active", ":checked", ".keyboard-activating"):
                    self.assert_rule(f"{prefix}.flat{state}", sunken)
                self.assert_rule(f"{prefix}.flat:disabled", insensitive)
                self.assertEqual(
                    {s for s in self.rules if s.startswith(f"{prefix}.flat")},
                    {
                        f"{prefix}.flat",
                        f"{prefix}.flat:active",
                        f"{prefix}.flat:checked",
                        f"{prefix}.flat.keyboard-activating",
                        f"{prefix}.flat:disabled",
                    },
                )

    def test_flat_button_arms(self):
        # No reference screenshot shows a GTK flat button; the tail arms
        # restate the landed plain push-button recipe over the stock
        # transparent flat family, so every checked relationship below
        # anchors the landed face constants and the family inventory keeps
        # the arms to stock's own spellings.
        raised = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "transition": "none",
        }
        for selector in ("button.flat", "button.flat:hover"):
            self.assertEqual(self.rules[selector], raised)
        sunken = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "transition": "none",
        }
        for selector in ("button.flat:active", "button.flat:checked", "button.flat.keyboard-activating"):
            self.assertEqual(self.rules[selector], sunken)
        insensitive = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        backdrop = {**raised, "color": BLACK}
        backdrop_sunken = {
            **sunken,
            "color": BLACK,
        }
        for selector in (
            "button.flat:backdrop",
            "button.flat:disabled",
            "button.flat:backdrop:disabled",
            "button:backdrop.flat:disabled",
            "button:backdrop.flat:disabled:active",
            "button:backdrop.flat:disabled:checked",
        ):
            self.assertEqual(self.rules[selector], insensitive)
        self.assertEqual(self.rules["button:backdrop.flat"], backdrop)
        for selector in ("button:backdrop.flat:active", "button:backdrop.flat:checked"):
            self.assertEqual(self.rules[selector], backdrop_sunken)
        expected_selectors = {
            "button.flat",
            "button.flat:hover",
            "button.flat:active",
            "button.flat:checked",
            "button.flat.keyboard-activating",
            "button.flat:backdrop",
            "button.flat:disabled",
            "button.flat:backdrop:disabled",
            "button:backdrop.flat",
            "button:backdrop.flat:active",
            "button:backdrop.flat:checked",
            "button:backdrop.flat:disabled",
            "button:backdrop.flat:disabled:active",
            "button:backdrop.flat:disabled:checked",
        }
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith("button.flat") or selector.startswith("button:backdrop.flat")
            },
            expected_selectors,
        )

    def test_checkbutton_focus_transition(self):
        self.assert_scale_slider_transition("checkbutton")

    def test_checkbutton_corners(self):
        # The 2026-11-04 wrapper-corner restatement squares the
        # check-button wrapper under the landed square-corner policy: the
        # base arm on the landed no-transition group and two byte-equal
        # stock twin spellings at the checked-indicator seam.
        self.assertEqual(
            {selector for selector in self.rules if "checkbutton" in selector},
            {
                "checkbutton",
                "checkbutton:focus:focus-visible",
                "checkbutton.grouped",
                "checkbutton.selection-mode",
            },
        )
        for selector in ("checkbutton.grouped", "checkbutton.selection-mode"):
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1, selector)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_square_corner(selector)
        self.assert_rule(
            "checkbutton", {"transition": "none", "border-radius": "0"}
        )
        self.assertEqual(
            self.rules["checkbutton"], {"transition": "none", "border-radius": "0"}
        )
        self.assert_matches_frame("checkbutton", "border-radius")
        # The parser splits the `check, radio` comma group, so the first
        # "check" selector is that group's first member, before the
        # extended `checkbutton` group, and the standalone `check` face
        # group is the next "check" spelling.
        self.assertGreater(
            self.selectors.index("checkbutton"),
            self.selectors.index("check"),
        )
        face = self.selectors.index(
            "check", self.selectors.index("checkbutton:focus:focus-visible") + 1
        )
        for selector in ("checkbutton.grouped", "checkbutton.selection-mode"):
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("checkbutton:focus:focus-visible"),
            )
            self.assertLess(
                self.selectors.index(selector),
                face,
            )

    def test_expander_row_arrow_transition_motion(self):
        # An expander row's disclosure arrow keeps stock's two
        # orientations (half a turn at rest, upright while checked) while
        # the 200ms icon-transform ease is erased: the byte-equal stock
        # twin spelling declares only `transition: none`, sitting after
        # the landed caps-lock groups at the sheet tail.
        selector = "row.expander image.expander-row-arrow"
        self.assertEqual(self.selectors.count(selector), 1, selector)
        self.assert_rule(selector, {"transition": "none"})
        # Exact-dict, not the per-property subset: a stray rotation,
        # transform, colour or geometry declaration must fail, per the
        # entry's guarantee.
        self.assertEqual(self.rules[selector], {"transition": "none"}, selector)
        # The spelling is new to the sheet, so a stray state twin, a
        # second rule or a wrongly-spelled selector fails this sweep.
        self.assertEqual(
            {s for s in self.rules if "expander-row-arrow" in s}, {selector}
        )
        self.assertGreater(
            self.selectors.index(selector),
            self.selectors.index("entry.password image.caps-lock-indicator"),
        )

    def test_server_list_button_rotation_motion(self):
        # The places view's server-button icon keeps stock's two
        # orientations (upright at rest, half a turn while checked) while
        # the 200ms rotation ease is erased: the two byte-equal stock twin
        # spellings declare only `transition: none`, sitting after the
        # landed caps-lock groups at the sheet tail.
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

    def test_notebook_focus_transition(self):
        self.assert_scale_slider_transition(
            "notebook > header > tabs > tab:checked"
        )

    def test_notebook_tab_close_button_arms(self):
        for selector in (
            "notebook > header > tabs > tab button.flat",
            "notebook > header > tabs > tab button.flat:backdrop",
        ):
            self.assert_rule(selector, {"color": BLACK})
        for selector in (
            "notebook > header > tabs > tab button.flat:disabled",
            "notebook > header > tabs > tab button.flat:backdrop:disabled",
        ):
            self.assert_rule(selector, {"color": DISABLED_TEXT["color"]})

    def test_notebook_tab_scroll_arrow_faces(self):
        """Pin the 2026-11-11 notebook overflow-arrow restatement."""
        # 2026-11-11: stock paints the notebook header's overflow arrows
        # with the plain button family — rounded grey-gradient bevels and a
        # brightness-boosted hover glyph — and no collected reference
        # screenshot shows the arrows, so each state arm below restates the
        # landed same-sheet button arm at the arrow's own exact stock
        # spelling, later source order winning the tie per-property.
        raised = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "transition": "none",
        }
        sunken = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "transition": "none",
        }
        arrow = "notebook > header > tabs > arrow"
        self.assert_rule_group({
            arrow: raised,
            f"{arrow}:hover": {**raised, "-gtk-icon-filter": "none"},
            f"{arrow}:hover:not(:active):not(:backdrop)": {
                **raised, "-gtk-icon-filter": "none"},
            **dict.fromkeys((
                f"{arrow}.keyboard-activating",
                f"{arrow}:active",
                f"{arrow}:checked",
            ), sunken),
            **dict.fromkeys((
                f"{arrow}:checked:hover",
                f"{arrow}:checked:active",
            ), sunken),
            f"{arrow}:focus:focus-visible": {"outline-color": BLACK},
            **dict.fromkeys((
                f"{arrow}:disabled",
                f"{arrow}:disabled:active",
                f"{arrow}:disabled:checked",
                f"{arrow}:backdrop:disabled",
                f"{arrow}:backdrop:disabled:active",
                f"{arrow}:backdrop:disabled:checked",
            ), {
                "background-color": FACE,
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": BUTTON_BEVEL,
                "color": DISABLED_TEXT["color"],
            }),
            f"{arrow}:backdrop": {
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": BUTTON_BEVEL,
                "color": BLACK,
                "transition": "none",
            },
            **dict.fromkeys((
                f"{arrow}:backdrop:active",
                f"{arrow}:backdrop:checked",
            ), {
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": INVERTED_BUTTON_BEVEL,
                "color": BLACK,
                "transition": "none",
            }),
        })
        # Source order: the base arrow group files after the landed
        # `button.flat` family's tail block, so every arrow twin decides
        # the equal-specificity race against the stock arms.
        self.assertGreater(
            self.selectors.index(arrow),
            self.selectors.index("button.flat:backdrop"),
        )
        # The token sweep keys on a substring no other landed selector
        # carries: a dropped twin, a renamed spelling, a lost comma member
        # or a stray extra rule fails.
        self.assertEqual(
            {selector for selector in self.selectors if arrow in selector},
            {
                arrow,
                f"{arrow}:hover",
                f"{arrow}:hover:not(:active):not(:backdrop)",
                f"{arrow}.keyboard-activating",
                f"{arrow}:active",
                f"{arrow}:checked",
                f"{arrow}:checked:hover",
                f"{arrow}:checked:active",
                f"{arrow}:focus:focus-visible",
                f"{arrow}:disabled",
                f"{arrow}:disabled:active",
                f"{arrow}:disabled:checked",
                f"{arrow}:backdrop:disabled",
                f"{arrow}:backdrop:disabled:active",
                f"{arrow}:backdrop:disabled:checked",
                f"{arrow}:backdrop",
                f"{arrow}:backdrop:active",
                f"{arrow}:backdrop:checked",
            },
        )

    def test_notebook_focus_outline_color(self):
        self.assert_scale_focus_outline(
            "notebook:focus:focus-visible > header > tabs > tab:checked"
        )

    def test_infobar(self):
        self.assert_infobar(("infobar > revealer > box",))
        # No infobar-family rule names a message type; the ban's provenance
        # lives on the shared sweep helper.
        self.assert_infobar_message_type_ban()

    # The 2026-11-09 face extension gives the corner pair the whole landed
    # `button.flat` face recipe beside the radius, so the exact-dict checks
    # below assert the merged dict instead of the radius alone.
    CLOSE_CORNER_PAIR_RULE = {
        "background-color": FACE,
        "background-image": "none",
        "border": f"1px solid {BLACK}",
        "border-radius": "0",
        "box-shadow": BUTTON_BEVEL,
        "transition": "none",
    }

    def test_close_button_corners(self):
        # Stock circles the infobar and search-bar close buttons; the
        # square-corner policy squares both faces, and the added
        # 2026-11-09 face extension paints the landed `button.flat` recipe
        # on them. The landed window-controls close pair is the sibling
        # this test's radius sweep expects beside them.
        selectors = ("infobar .close", "searchbar > revealer > box .close")
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, self.CLOSE_CORNER_PAIR_RULE)
                self.assert_matches_frame(selector, "border-radius")
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("floating-sheet > sheet"),
                )
        self.assertEqual(
            {
                selector
                for selector, declarations in self.rules.items()
                if "close" in selector and "border-radius" in declarations
            },
            {
                "infobar .close",
                "searchbar > revealer > box .close",
                "headerbar windowcontrols button.close",
                ".titlebar windowcontrols button.close",
            },
        )

    def test_close_button_family(self):
        # The 2026-11-09 family restates every stock flat-band face the
        # close class carries except the typed-band twins (the landed
        # message-type ban needs no type token) and the `:drop(active)`
        # ring (nothing landed governs a button drop arm). The four
        # raised-hover recipe faces share the landed `button.flat:hover`
        # recipe minus its radius declaration (the corner pair keeps the
        # radius ownership alone), with the stock ink claim re-landed
        # black; the pressed and checked faces share the landed inverted
        # bevel; the disabled face keeps the landed `button:disabled`
        # shape and clears the stock dim filter under the landed
        # preserve-the-palette policy.
        hover = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "box-shadow": BUTTON_BEVEL,
            "transition": "none",
            "color": BLACK,
        }
        pressed = {
            "background-color": FACE,
            "background-image": "none",
            "box-shadow": INVERTED_BUTTON_BEVEL,
        }
        disabled = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
            "filter": "none",
        }
        expected = {
            "infobar.action:hover > revealer > box": {"background-color": FACE},
            "infobar .close:hover": hover,
            "searchbar .close:hover": hover,
            "searchbar > revealer > box .close:hover": hover,
            "infobar .keyboard-activating.close": pressed,
            "infobar .close:active": pressed,
            "searchbar > revealer > box .keyboard-activating.close": pressed,
            "searchbar > revealer > box .close:active": pressed,
            "infobar .close:checked": pressed,
            "searchbar > revealer > box .close:checked": pressed,
            "infobar .close:checked:hover": pressed,
            "searchbar > revealer > box .close:checked:hover": pressed,
            "infobar .close:checked.keyboard-activating": pressed,
            "infobar .close:checked:active": pressed,
            "searchbar > revealer > box .close:checked.keyboard-activating": pressed,
            "searchbar > revealer > box .close:checked:active": pressed,
            "infobar .close:disabled:not(:checked)": disabled,
            "searchbar > revealer > box .close:disabled:not(:checked)": disabled,
            "infobar .close:focus:focus-visible": {"outline-color": BLACK},
        }
        self.assert_rule_group(expected)
        # The family sweep: every sheet selector naming a close class against
        # an infobar or a search bar is exactly the landed corner pair, the
        # landed searchbar close focus spelling and this family.
        self.assertEqual(
            {
                selector
                for selector in self.selectors
                if ".close" in selector
                and ("infobar" in selector or selector.startswith("searchbar"))
            },
            {
                "infobar .close",
                "searchbar > revealer > box .close",
                "searchbar > revealer > box .close:focus:focus-visible",
                *{s for s in expected if ".close" in s},
            },
        )
        # Each family selector sits after the corner groups' index, so the
        # source-order win over the stock arms stays honest.
        corner_index = max(
            self.selectors.index("infobar .close"),
            self.selectors.index("searchbar > revealer > box .close"),
        )
        for selector in expected:
            with self.subTest(selector=selector):
                self.assertGreater(self.selectors.index(selector), corner_index)
        # The landed message-type ban already reads every infobar carrier
        # through test_infobar; restate it over the family's own members so
        # a future edit cannot add a type token inside this group.
        self.assert_infobar_message_type_ban(expected)

    def test_banner_surface(self):
        selectors = {
            "banner > revealer > widget",
            "banner > revealer > widget:backdrop",
        }
        self.assertEqual(
            {selector for selector in self.selectors if "banner" in selector},
            selectors,
        )
        expected = {"background-color": FACE, "color": BLACK}
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)
                for prop in expected:
                    self.assertEqual(
                        self.rules[selector][prop],
                        self.rules["infobar > revealer > box"][prop],
                    )

    def test_search_bar(self):
        self.assert_infobar(("searchbar > revealer > box",))

    def test_action_bar(self):
        self.assert_infobar(("actionbar > revealer > box",))

    def test_search_bar_backdrop(self):
        # An unfocused window keeps the landed band face: the
        # backdrop record spells its stock twin byte-equal and wins the tie
        # by later user-sheet source order.
        declarations = {
            "background-color": FACE,
            "border-bottom-color": ETCH_DARK,
            "box-shadow": f"inset 0 -1px {WHITE}",
            "transition": "none",
        }
        self.assert_rule_group(
            {"searchbar > revealer > box:backdrop": declarations}
        )
        self.assertEqual(
            {s for s in self.rules if s.startswith("searchbar") and ":backdrop" in s},
            {"searchbar > revealer > box:backdrop"},
        )
        # Stock GTK 4 declares neither an action-bar backdrop arm nor a
        # location strip, so no such spelling belongs here.
        self.assertNotIn("actionbar > revealer > box:backdrop", self.rules)
        self.assertFalse([s for s in self.rules if "location-bar" in s])
        self.assert_rule_after(
            "searchbar > revealer > box:backdrop",
            "actionbar > revealer > box {",
        )
        self.assert_rule_after(
            "statusbar {",
            "searchbar > revealer > box:backdrop",
        )

    def test_status_bar(self):
        self.assert_infobar(("statusbar",))

    def test_dropdown_searchbar_rim(self):
        # A dropdown's or combobox's searchable list popover draws the
        # search strip's own stock rim beneath the band edge the strip's
        # inner search box paints; the landed band group answers the inner
        # box, so this rim restates the strip itself with the landed etched
        # band edge.
        expected = {
            "border-bottom": f"1px solid {ETCH_DARK}",
            "box-shadow": f"inset 0 -1px {WHITE}",
        }
        for selector in (
            "dropdown popover .dropdown-searchbar",
            "combobox popover .dropdown-searchbar",
        ):
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, expected)
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("actionbar > revealer > box"),
                )
                self.assertLess(
                    self.selectors.index(selector),
                    self.selectors.index("statusbar"),
                )
                for prop in expected:
                    self.assertEqual(
                        self.rules[selector][prop],
                        self.rules["infobar > revealer > box"][prop],
                    )
        # The landed scroll-edge spellings end with undershoot.top /
        # undershoot.bottom and stay out of this suffix family.
        self.assertEqual(
            {s for s in self.rules if s.endswith("dropdown-searchbar")},
            {
                "dropdown popover .dropdown-searchbar",
                "combobox popover .dropdown-searchbar",
            },
        )
        # The strip's arm inventory must not grow a .combo-searchbar rule:
        # stock's margin arm and the landed undershoot twins (which contain
        # the token but end with an undershoot suffix) stay the only ones.
        self.assertEqual(
            {s for s in self.rules if s.endswith("combo-searchbar")},
            set(),
        )

    def test_path_bar_tabs(self):
        forms = {
            "base": ("pathbar > scrolledwindow > viewport > box > button",),
            "hover": ("pathbar > scrolledwindow > viewport > box > button:hover",),
            "checked": ("pathbar > scrolledwindow > viewport > box > button:checked",),
            "checked+hover": (
                "pathbar > scrolledwindow > viewport > box > button:checked:hover",
            ),
        }
        self.assert_tab_faces(forms)

    def test_row_selection_backdrop(self):
        self.assert_row_selection_backdrop((
            "treeview.view:selected:backdrop",
            "list row.activatable:selected:backdrop",
            "columnview.view:selected:backdrop",
            "listview > row.activatable:selected:backdrop",
        ))
        self.assert_rule_after(
            "list row.activatable:selected:backdrop",
            "list row.activatable:selected:",
        )

    def test_list_row_press_and_popup_faces(self):
        # The pressed and popup-holding row states restate the landed
        # faces: stock's toolkit resource and the integration library's
        # base.css resource would paint a tinted hover-wash, pressed
        # insets-wash-or-an-accent fill on rows the landed records paint
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
        # The landed row spellings are all list-, listview-, columnview-
        # or popover-armed, and the landed bare-row groups spell `row` and
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

    def test_selected_row_button_arms(self):
        # The selected-row button arms restate the landed black: see
        # assert_selected_row_button_arms in support.gtk_rule_cases.
        self.assert_selected_row_button_arms("button:backdrop.flat")

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
        # row twins on the landed selection lavender with black ink;
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

    def test_row_drop_borders(self):
        expected = {
            "border-style": "solid none",
            "border-width": "1px",
            "border-color": SELECTION,
        }
        for selector in (
            "columnview.view > dndtarget:drop(active)",
            "treeview.view > dndtarget:drop(active)",
            "window.print:not(.ssd-frame) treeview.dialog-action-box > dndtarget:drop(active)",
        ):
            with self.subTest(selector=selector):
                self.assert_rule(selector, expected)

    def test_view_row_separators(self):
        """Asked-for view separators paint the etched separator's dark half."""
        horizontal = ("listview.horizontal row.separator",
                      "listview.separators.horizontal > row:not(.separator)",
                      "list.horizontal row.separator",
                      "list.separators.horizontal > row:not(.separator)")
        vertical = ("listview:not(.horizontal) row.separator",
                    "listview.separators:not(.horizontal) > row:not(.separator)",
                    "list:not(.horizontal) row.separator",
                    "list.separators:not(.horizontal) > row:not(.separator)")
        view_spelling = {"columnview.view.separator", "treeview.view.separator"}
        cell_spelling = "columnview.column-separators > listview > row > cell"
        expected = [
            (selector, {"color": ETCH_DARK}) for selector in sorted(view_spelling)
        ]
        expected += [(selector, {"border-left": f"1px solid {ETCH_DARK}"})
                     for selector in horizontal]
        expected += [(selector, {"border-bottom": f"1px solid {ETCH_DARK}"})
                     for selector in vertical]
        expected.append((cell_spelling, {"border-left-color": ETCH_DARK}))
        backdrop_order = self.selectors.index("columnview.view:selected:backdrop")
        drop_order = self.selectors.index("columnview.view > dndtarget:drop(active)")
        for selector, expected_rule in expected:
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, expected_rule)
                self.assertGreater(self.selectors.index(selector), backdrop_order)
                self.assertLess(self.selectors.index(selector), drop_order)
        # The restated tone is the only separator paint at these view spellings:
        # no landed selector carries any of the stock arm's tokens, and every
        # selector ending on one of them is one of the restated spellings.
        self.assertEqual(
            {selector for selector in self.rules
             if selector.endswith("view.separator")},
            view_spelling,
        )
        self.assertEqual(
            {selector for selector in self.rules
             if "row:not(.separator)" in selector},
            {"listview.separators.horizontal > row:not(.separator)",
             "list.separators.horizontal > row:not(.separator)",
             "listview.separators:not(.horizontal) > row:not(.separator)",
             "list.separators:not(.horizontal) > row:not(.separator)"},
        )
        self.assertEqual(
            {selector for selector in self.rules
             if selector.endswith("row.separator")},
            {"listview.horizontal row.separator",
             "list.horizontal row.separator",
             "listview:not(.horizontal) row.separator",
             "list:not(.horizontal) row.separator"},
        )
        self.assertEqual(
            {selector for selector in self.rules if "column-separators" in selector},
            {cell_spelling},
        )

    def test_dropdown_list_rows(self):
        """Open dropdown and combobox popover lists use the landed row recipes."""
        padding_spellings = (
            "dropdown popover listview > row.activatable",
            "combobox popover listview > row.activatable",
        )
        selected_spellings = (
            "dropdown popover listview > row.activatable:selected",
            "dropdown popover listview > row.activatable:selected:hover",
            "combobox popover listview > row.activatable:selected",
            "combobox popover listview > row.activatable:selected:hover",
        )
        backlog_order = self.selectors.index("columnview.view:selected:backdrop")
        separator_order = self.selectors.index("listview.horizontal row.separator")
        for selector, expected_rule in (
            [(selector, {"padding": "2px"}) for selector in padding_spellings]
            + [(selector, ROW_SELECTED) for selector in selected_spellings]
        ):
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, expected_rule)
                self.assertGreater(self.selectors.index(selector), backlog_order)
                self.assertLess(self.selectors.index(selector), separator_order)
        # Exactly the stocked dropdown twin spellings exist and nothing else:
        # no landed rule elsewhere in the sheet names a popover listview, so the
        # family scan kills renamed and stray variants.
        self.assertEqual(
            {selector for selector in self.rules if "popover listview" in selector},
            set(padding_spellings) | set(selected_spellings),
        )
        self.assertEqual(
            {selector for selector in self.rules
             if selector.endswith("popover listview > row.activatable")},
            set(padding_spellings),
        )

    def test_list_row_focus_outlines(self):
        """Keyboard-focused rows paint the landed black focus colour."""
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
        # Source order: the focus group sits after the landed
        # disabled-selected backdrop group and before the landed tab-close
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
        # Source order: the restated group sits after the landed row-focus
        # outline rule and before the landed tab-close block.
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

    def test_row_drop_directional_arms_undeclared(self):
        # The stock directional arms only hide one of the two row drop
        # lines; neither carries a colour the selection replaces, so the
        # sheet keeps them undeclared. This pin fails if a rule ever
        # claims one of them by name.
        self.assertNotIn("drop(active).after", self.css)
        self.assertNotIn("drop(active).before", self.css)

    def test_view_accelerator_editor(self):
        # The stock label face tints the view family's on-screen
        # accelerator editor -- the overlay label a header button shows
        # while it captures a key -- with its accent. No collected
        # reference screenshot shows accelerator editing, so the pinned
        # selection fill answers it, as for the selected rows and the
        # drop header arm (see the sheet's adaptation
        # comment). The three stock arms were probed fresh 2026-11-09
        # with gresource extract of Default-light.css and Default-dark.css
        # in /usr/lib/x86_64-linux-gnu/libgtk-4.so.1 (libgtk-4 4.18.6,
        # light 726 / dark 718) and of the desktop integration library's
        # base stylesheet resource (the library name and resource path
        # recorded in docs/invariants.md, base 716): none claims any
        # member beyond background-color.
        expected = {"background-color": SELECTION}
        spellings = (
            "columnview.view acceleditor > label",
            "treeview.view acceleditor > label",
            "window.print:not(.ssd-frame) treeview.dialog-action-box acceleditor > label",
        )
        self.assert_rule_group({spelling: expected for spelling in spellings})
        # The sweep kills renamed and stray accelerator-editor spellings
        # alike; comment mentions are not selectors.
        self.assertEqual(
            {s for s in self.rules if "acceleditor" in s},
            set(spellings),
        )
        # Order pin: the restated group sits directly after the landed
        # drag-drop header-button group and before the expander group.
        self.assertGreater(
            self.selectors.index("columnview.view acceleditor > label"),
            self.selectors.index(
                "window.print:not(.ssd-frame) treeview.dialog-action-box > header > button.dnd"
            ),
        )
        self.assertLess(
            self.selectors.index("columnview.view acceleditor > label"),
            self.selectors.index("treeview.view.expander"),
        )

    def test_spin_button_field(self):
        self.assert_spin_button_field(
            ("spinbutton:not(.vertical)", "spinbutton.vertical > text")
        )

    def test_flat_entry_fields(self):
        # The landed entry recipe governs the stock flat entry family: the
        # sheet restates the stock grouped transparent-face arm with one
        # byte-equal six-selector twin declaring ENTRY_FIELD, so a resting,
        # focused, backdrop or disabled flat entry (and a spin button's flat
        # field) paints the raised field instead of stock's transparency.
        selectors = (
            "spinbutton.vertical > text.flat",
            "spinbutton.flat:not(.vertical)",
            "entry.flat:focus-within",
            "entry.flat:backdrop",
            "entry.flat:disabled",
            "entry.flat",
        )
        for selector in selectors:
            self.assert_exact_rule_once(selector, ENTRY_FIELD)
        # No other flat entry or spinbutton spelling exists beyond the
        # treeview-embedded flat twins the treeview entry restatement adds:
        # the family scan kills renamed and stray variants alike. The stock
        # `.osd` stepper spellings carry `:not(.flat)` (a not-flat
        # exclusion, not a flat field); the landed OSD stepper record adds
        # them byte-equal to stock, so the scan holds them out.
        self.assertEqual(
            {
                s
                for s in self.rules
                if "flat" in s
                and ("entry" in s or "spinbutton" in s)
                and ":not(.flat)" not in s
            },
            set(selectors) | {"treeview entry.flat", "treeview entry.flat:focus-within"},
        )

    def test_spin_field_mirrors_the_etch_in_rtl(self):
        # GTK does not mirror box-shadow for text direction, so a horizontal
        # RTL spin field kept the landed etch's horizontal top arm only: the
        # landed :dir(rtl) stepper arms cover the etch's vertical arm at the
        # field's left edge, leaving the exposed right edge half-etched
        # where the LTR field shows the full L (measured 2026-11-11 in a
        # child render before the fix). The sheet mirrors the arm onto the
        # exposed edge — the landed GTK 3 spinbutton:dir(rtl) record — with
        # one plain mirror directly after the plain field rule and one twin
        # directly after each of the three landed `.osd` state groups, each
        # declaring exactly the mirrored arm. Each mirror out-ranks its
        # base group by one class (the `:dir(rtl)` pseudo-class), so the
        # win does not depend on source position; the focused and disabled
        # twins also out-rank the plain OSD mirror the same way. Excluded:
        # vertical spinbutton.vertical > text fields (no horizontal stepper
        # covers the arm), plain entry fields (no steppers) and the
        # treeview-embedded entry group (an entry, not a spin field); the
        # OSD record declares no :backdrop field twin, so none is mirrored.
        mirror = "inset -1px 1px #999999"
        plain = "spinbutton:dir(rtl):not(.vertical)"
        twins = (
            ".osd spinbutton:dir(rtl):not(.vertical)",
            ".osd spinbutton:dir(rtl):focus-within:not(.vertical)",
            ".osd spinbutton:dir(rtl):disabled:not(.vertical)",
        )
        for selector in (plain, *twins):
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, {"box-shadow": mirror})
        # Each mirror sits directly after its base group in the sheet text.
        self.assert_rule_after(
            "\nspinbutton:dir(rtl):not(.vertical) {",
            "entry, spinbutton:not(.vertical), spinbutton.vertical > text {",
        )
        self.assert_rule_after(
            ".osd spinbutton:dir(rtl):not(.vertical) {",
            ".osd spinbutton.vertical > text, .osd spinbutton:not(.vertical), .osd entry {",
        )
        self.assert_rule_after(
            ".osd spinbutton:dir(rtl):focus-within:not(.vertical) {",
            ".osd spinbutton.vertical > text:focus-within, "
            ".osd spinbutton:focus-within:not(.vertical), .osd entry:focus-within {",
        )
        self.assert_rule_after(
            ".osd spinbutton:dir(rtl):disabled:not(.vertical) {",
            ".osd spinbutton.vertical > text:disabled, "
            ".osd spinbutton:disabled:not(.vertical), .osd entry:disabled {",
        )
        # Token sweeps keyed on substrings no other landed selector
        # carries: the plain token matches the plain mirror and its OSD
        # twin (the twin is a superstring), the two state tokens match
        # exactly their own twin, so a dropped mirror, a lost twin, a
        # renamed spelling or a stray extra selector fails.
        self.assertEqual(
            {s for s in self.rules if "spinbutton:dir(rtl):not(.vertical)" in s},
            {plain, twins[0]},
        )
        self.assertEqual(
            {s for s in self.rules if ".osd spinbutton:dir(rtl):focus-within" in s},
            {twins[1]},
        )
        self.assertEqual(
            {s for s in self.rules if ".osd spinbutton:dir(rtl):disabled" in s},
            {twins[2]},
        )

    def test_caps_lock_indicator(self):
        # The landed entry recipe never names the `caps-lock-indicator`
        # image child GTK stacks inside a password entry, so the two toolkit
        # tiers paint their own look on it even though the landed `entry >
        # image` family reaches the node: each stock arm carries the extra
        # `password` classes that out-specify the landed element pair, so
        # the toolkit's tint and the base tier's 30% dim stay in force.
        # The sheet tail restates both stock arms byte-equal: the
        # indicator takes the landed field's black ink (the family's own
        # pinned source) at the landed button:hover erase precedent's full
        # strength, so later user-sheet source order wins every
        # equal-specificity tie under either cascade reading.
        for selector in (
            "spinbutton.vertical > text.password image.caps-lock-indicator",
            "spinbutton.password:not(.vertical) image.caps-lock-indicator",
        ):
            self.assert_rule(selector, {"color": BLACK})
            self.assertEqual(self.selectors.count(selector), 1, selector)
        self.assert_rule("spinbutton.password image.caps-lock-indicator", {"opacity": "1"})
        self.assertEqual(
            self.selectors.count("spinbutton.password image.caps-lock-indicator"),
            1,
        )
        # The `entry.password image.caps-lock-indicator` spelling merges
        # one declaration from both restated rules on one key, like the
        # landed `entry > image` merge keys: the colour rule's landed
        # black and the opacity rule's full strength, asserted with
        # occurrence count two.
        self.assert_rule(
            "entry.password image.caps-lock-indicator",
            {"color": BLACK, "opacity": "1"},
        )
        self.assertEqual(
            self.selectors.count("entry.password image.caps-lock-indicator"), 2
        )
        # No other selector names the token: the family sweep kills a
        # renamed, dropped or stray spelling, a second colour or opacity
        # rule, a hover or active twin, or a restored stock value alike.
        self.assertEqual(
            {s for s in self.rules if "caps-lock-indicator" in s},
            {
                "spinbutton.vertical > text.password image.caps-lock-indicator",
                "spinbutton.password:not(.vertical) image.caps-lock-indicator",
                "spinbutton.password image.caps-lock-indicator",
                "entry.password image.caps-lock-indicator",
            },
        )
        # The restated pair holds the entry-image family tail, not a
        # detached sheet head: the colour arm sits after the landed
        # margin twin that ends the family and its own comment group.
        self.assertGreater(
            self.selectors.index(
                "spinbutton.vertical > text.password image.caps-lock-indicator"
            ),
            self.selectors.index("spinbutton > image.right"),
        )

    def test_treeview_entry_fields(self):
        # The landed entry recipe governs the stock treeview-embedded entry
        # family too: the sheet restates the three stock grouped arms with
        # byte-equal twins declaring ENTRY_FIELD, a black focus border and
        # the landed no-motion policy, so a resting, focused, flat or
        # plain editable cell paints the raised field instead of stock's
        # blue focus border and stock's color/background focus transition.
        fields = ("treeview entry.flat", "treeview entry")
        focus = (
            "treeview entry.flat:focus-within",
            "treeview entry:focus-within",
        )
        motion = (
            "treeview entry:focus-within:dir(rtl)",
            "treeview entry:focus-within:dir(ltr)",
        )
        for selector in fields:
            self.assert_exact_rule_once(selector, ENTRY_FIELD)
        for selector in focus:
            self.assert_exact_rule_once(selector, {"border-color": BLACK})
        for selector in motion:
            self.assert_exact_rule_once(selector, {"transition": "none"})
        # No other treeview entry spelling exists in the sheet: the family
        # scan kills renamed and stray variants alike.
        self.assertEqual(
            {s for s in self.rules if s.startswith("treeview entry")},
            set(fields + focus + motion),
        )

    def test_editable_label_cells(self):
        # The landed entry recipe governs the stock editable-label family:
        # the sheet restates the stock field arm and the four column-view
        # cell-editing arms with byte-equal twins declaring ENTRY_FIELD, the
        # landed focus-black outline and TEXT_SELECTION, so an editable
        # label and a column view's cell being edited paint the raised
        # field, the black focus ring and the landed selection fill instead
        # of stock's warm-grey border and blue accent tints.
        field = "editablelabel > stack > text"
        focus = (
            "columnview row:not(:selected) cell"
            " editablelabel:not(.editing):focus-within",
            "columnview row:not(:selected) cell"
            " editablelabel.editing:focus-within",
        )
        selection = (
            "columnview row:not(:selected) cell"
            " editablelabel.editing text selection",
            "columnview row:not(:selected) cell"
            " editablelabel.editing text selection:focus-within",
        )
        self.assert_exact_rule_once(field, ENTRY_FIELD)
        for selector in focus:
            self.assert_rule(selector, {"outline-color": BLACK})
            self.assert_exact_rule_once(selector, {"outline-color": BLACK})
        for selector in selection:
            self.assert_rule(selector, TEXT_SELECTION)
            self.assert_exact_rule_once(selector, TEXT_SELECTION)
        # No other editablelabel spelling exists beyond the landed selection
        # restatement and the five new spellings, and no other columnview row
        # spelling exists at all: the family scans kill renamed and stray
        # variants alike.
        self.assertEqual(
            {s for s in self.rules if "editablelabel" in s},
            {
                field,
                "editablelabel > stack > text > selection",
                "editablelabel > stack > text > selection:focus-within",
                *focus,
                *selection,
            },
        )
        self.assertEqual(
            {s for s in self.rules if s.startswith("columnview row")},
            set(focus + selection),
        )
        # The restatements sit between the landed selected-text groups and
        # the landed calendar disabled-selected day group: source order is
        # part of what lets the restatements govern the cell arms, which
        # outrank the landed editable-label selection twins by specificity.
        landed_tail = self.selectors.index(
            "editablelabel > stack > text > selection:focus-within"
        )
        calendar = self.selectors.index(
            "calendar > grid > label.day-number:disabled:selected"
        )
        for selector in (field, *focus, *selection):
            self.assertGreater(self.selectors.index(selector), landed_tail)
            self.assertGreater(calendar, self.selectors.index(selector))

    def test_title_buttons(self):
        for scope in ("headerbar", ".titlebar"):
            for control, asset in TITLE_BUTTON_ASSETS:
                self.assert_title_button(
                    f"{scope} windowcontrols button.{control}", asset
                )
            self.assert_rule(
                f"{scope} windowcontrols button image", TITLE_BUTTON_IMAGE
            )
            for state in ("hover", "active", "checked"):
                self.assert_rule(
                    f"{scope} windowcontrols button:{state} > image",
                    TITLE_BUTTON_IMAGE_STATE,
                )

    def test_message_dialog_header_band(self):
        # The message dialog's title band repaints the landed headerbar.
        # The band restates the landed headerbar, .titlebar group plus its
        # headerbar-only 1px bottom border, the backdrop band restates the
        # landed headerbar:backdrop, .titlebar:backdrop group, and the
        # dialog body corners go square; tying through the landed groups'
        # dictionaries keeps the bands in step with any future header
        # change.
        self.assert_rule(
            "window.dialog.message .titlebar",
            {**self.rules["headerbar"], "border-width": "0 0 1px 0"},
        )
        self.assert_rule(
            "window.dialog.message .titlebar:backdrop",
            self.rules["headerbar:backdrop"],
        )
        self.assert_rule(
            "window.dialog.message.csd.background",
            {"border-radius": "0"},
        )

    def test_message_dialog_action_area(self):
        # The stock toolkit resource re-pads the message dialog's action
        # buttons to 10px 14px and rounds the end buttons' bottom corners
        # to 7px; the sheet restates the stock button base padding and
        # square corners on both end arms.
        self.assert_rule(
            "window.dialog.message.csd .dialog-action-area button",
            {"padding": "4px 9px"},
        )
        for arm in ("first-child", "last-child"):
            self.assert_rule(
                f"window.dialog.message.csd .dialog-action-area button:{arm}",
                {"border-radius": "0"},
            )

    def test_notebook_header(self):
        self.assert_rule(
            "notebook > header",
            {
                "background-color": FACE,
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
            },
        )

    def test_popover(self):
        for selector in ("popover > contents", "popover > arrow"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "border": f"1px solid {BLACK}",
                    "border-radius": "0",
                    "box-shadow": "none",
                },
            )
        for selector in (
            "popover.menu modelbutton:hover",
            "popover.menu modelbutton:selected",
        ):
            self.assert_rule(selector, {"background-color": SELECTION})
        # Stock's popover-menu modelbutton arms declare a 5px corner
        # (Default-light.css in libgtk-4 4.18.6, probed 2026-11-03); the
        # restated byte-twin arms square the row like the square popover
        # contents shell above.
        for selector in ("popover.menu modelbutton", "modelbutton.flat"):
            self.assertEqual(self.rules[selector], {"border-radius": "0"})
            self.assertEqual(
                self.rules[selector]["border-radius"],
                self.rules["popover > contents"]["border-radius"],
            )
        # Stock's grey colour arms still govern the hover, disabled and
        # pressed-selected states of a standalone flat modelbutton and the
        # pressed-selected state inside a popover menu; the byte-twin
        # restatements paint the landed selection fill and disabled text
        # there (Default-light.css in libgtk-4 4.18.6, probed 2026-11-03).
        for selector in (
            "popover.menu modelbutton:selected:active",
            "modelbutton.flat:hover",
        ):
            self.assertEqual(self.rules[selector], {"background-color": SELECTION})
            self.assertEqual(
                self.rules[selector]["background-color"],
                self.rules["popover.menu modelbutton:hover"]["background-color"],
            )
        self.assertEqual(self.rules["modelbutton.flat:disabled"], {"color": ETCH_DARK})
        # The landed sheet carries no other modelbutton arm: any stray,
        # renamed or removed kind fails the family bound.
        self.assertEqual(
            {selector for selector in self.rules if "modelbutton" in selector},
            {
                "popover.menu modelbutton:hover",
                "popover.menu modelbutton:selected",
                "popover.menu modelbutton:selected:active",
                "popover modelbutton check",
                "popover modelbutton radio",
                "popover.background modelbutton check",
                "popover.background modelbutton radio",
                "popover.menu modelbutton > arrow.right",
                "popover.menu modelbutton",
                "modelbutton.flat",
                "modelbutton.flat:hover",
                "modelbutton.flat:disabled",
            },
        )
        # Both squaring arms sit after the landed hover/select block, the
        # source position that beats any same-theme arm on the corner.
        for selector in ("popover.menu modelbutton", "modelbutton.flat"):
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("popover.menu modelbutton:hover"),
            )
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("popover.menu modelbutton:selected"),
            )
        # Each colour arm sits after the landed hover/select blocks and the
        # squaring radius arms, the source position that beats stock's
        # equal-specificity grey arms and keeps the family together.
        for selector in (
            "popover.menu modelbutton:selected:active",
            "modelbutton.flat:hover",
            "modelbutton.flat:disabled",
        ):
            for earlier in (
                "popover.menu modelbutton:hover",
                "popover.menu modelbutton:selected",
                "popover.menu modelbutton",
                "modelbutton.flat",
            ):
                self.assertGreater(
                    self.selectors.index(selector), self.selectors.index(earlier)
                )

    def test_popover_menu_accelerator_foreground(self):
        selector = "popover.menu accelerator"
        self.assert_disabled_text((selector,))
        self.assert_rule(selector, {**DISABLED_TEXT})
        # Stock dims the accelerator inside the color declaration alone, so
        # the restatement carries the opacity-free, shadow-free dict whole.
        self.assert_exact_rule_once(selector, {**DISABLED_TEXT})
        # The stock-twin spelling lands after the landed popover-menu
        # modelbutton faces, the source position that beats either toolkit
        # arm on the tie.
        self.assertGreater(
            self.selectors.index(selector),
            self.selectors.index("popover.menu modelbutton"),
        )

    def test_toast_surface(self):
        selectors = {"toast", "toast:backdrop"}
        self.assertEqual(
            {selector for selector in self.selectors if "toast" in selector},
            selectors,
        )
        expected = {
            "background-color": FACE,
            "background-image": "none",
            "color": BLACK,
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": "none",
            "text-shadow": "none",
        }
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)
                self._assert_toast_matches_popover(selector)


    def test_dropdown_arrow(self):
        self.assert_rule("dropdown arrow", COMBO_ARROW)

    def test_menubutton_arrows(self):
        for selector, expected in MENUBUTTON_ARROWS.items():
            self.assert_rule(selector, expected)

    def test_menu_check_and_radio_are_boxless(self):
        for selector in (
            "popover modelbutton check",
            "popover modelbutton radio",
            "popover.background modelbutton check",
            "popover.background modelbutton radio",
        ):
            self.assert_rule(selector, MENU_CHECK)

    def test_menu_separator(self):
        self.assert_menu_separator(
            ("popover separator", "popover.background separator")
        )

    def test_separator(self):
        self.assert_separators()

    def test_paned_handle(self):
        self.assert_paned_handles()

    def test_paned_handle_stock_clearances(self):
        # Exact stock twins from Default-light.css (libgtk-4 4.18.6, probed
        # 2026-10-31) so sheet order decides every tie like the landed
        # image clearances do, plus the :dir margins the landed orientation
        # rules cannot outrank because each :dir arm carries one class more.
        for selector in (
            "paned > separator",
            "paned > separator:selected",
            "paned > separator.wide",
        ):
            self.assert_rule(selector, {"background-image": "none"})
        for selector in (
            "paned.horizontal > separator:dir(ltr)",
            "paned.horizontal > separator:dir(rtl)",
        ):
            self.assert_rule(selector, {"margin": "0", "padding": "0"})

    def test_frame(self):
        self.assert_frame(("frame > border", ".frame"))

    def test_shortcut_keycap_corners(self):
        self.assertEqual(
            {selector for selector in self.rules if "keycap" in selector},
            {"shortcut > .keycap"},
        )
        self.assert_square_corner("shortcut > .keycap")

    def test_card_corners(self):
        expected = {
            ".card",
            "menubutton.card > button",
            # The card focus arms restate the stock focus
            # colour, not radius, and test_card_focus_outline_color pins
            # them; they join this scan because they carry ``.card``.
            "tabthumbnail .card picture",
            "tabgrid > tabgridchild .card",
            "tabgrid > tabgridchild:focus:focus-visible .card",
            "button.card:focus:focus-visible",
            ".card:focus:focus-visible",
        }
        self.assertEqual(
            {selector for selector in self.rules if ".card" in selector},
            expected,
        )
        for selector in (".card", "menubutton.card > button"):
            with self.subTest(selector=selector):
                self.assert_square_corner(selector)

    def test_flowbox_item_corners(self):
        expected = {
            "flowbox > flowboxchild",
            # The selected view-child restatement names the same node.
            # The disabled-selected restatement names it again.
            "flowbox > flowboxchild:selected",
            "flowbox > flowboxchild:disabled:selected",
            "flowbox > flowboxchild:focus:focus-visible",
            # The rubberband view-specific recipe names this node.
            "flowbox > rubberband",
            # The disabled-view ink arm names the view class.
            "flowbox.view:disabled",
        }
        self.assertEqual(
            {selector for selector in self.rules if selector.startswith("flowbox")},
            expected,
        )
        self.assertEqual(
            self.rules["flowbox > flowboxchild"],
            {"border-radius": "0", "transition": "none"},
        )
        self.assert_matches_frame("flowbox > flowboxchild", "border-radius")

    def test_view_child_selected_arms(self):
        """Pin the view children restated off the landed row selection."""
        self.assert_rule(
            "flowbox > flowboxchild:selected",
            {
                "background-color": SELECTION,
                "color": BLACK,
                "outline-color": BLACK,
                "border-radius": "0",
            },
        )
        self.assert_rule(
            "gridview > child:selected",
            {
                "background-color": SELECTION,
                "color": BLACK,
                "outline-color": BLACK,
                "border-radius": "0",
            },
        )
        # Base selection already covers unfocused windows. An extra backdrop
        # state would outrank the chooser's base tint and tie stock's disabled
        # label. Pin its absence as well as the base declarations above.
        for selector in (
            "flowbox > flowboxchild:selected:backdrop",
            "gridview > child:selected:backdrop",
        ):
            with self.subTest(selector=selector):
                self.assertNotIn(selector, self.rules)
        for selector, alpha in (
            ("filechooser gridview child:selected", "0.15"),
            ("filechooser gridview child:selected:hover", "0.20"),
            ("filechooser gridview child:selected:active", "0.25"),
        ):
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {"background-color": f"rgba(204, 204, 255, {alpha})"},
                )

    def test_gridview_item_corners(self):
        expected = {
            "gridview > child",
            "filechooser gridview > child",
            "gridview > child:focus:focus-visible",
            # The filechooser undershoot mirror names the same view substring.
            "filechooser gridview ~ undershoot.top",
            # The selected view-child restatement names the same nodes.
            # The disabled-selected restatement names it again.
            "gridview > child:selected",
            "gridview > child:disabled:selected",
            # The rubberband view-specific recipe names this node.
            "gridview > rubberband",
            "filechooser gridview child:selected",
            "filechooser gridview child:selected:hover",
            "filechooser gridview child:selected:active",
            # The disabled-view ink arms name the view class and
            # the print action box.
            "gridview.view:disabled",
            "window.print:not(.ssd-frame) gridview.dialog-action-box:disabled",
        }
        self.assertEqual(
            {selector for selector in self.rules if "gridview" in selector},
            expected,
        )
        for selector in sorted(
            {"gridview > child", "filechooser gridview > child"}
        ):
            with self.subTest(selector=selector):
                self.assertEqual(
                    self.rules[selector],
                    {"border-radius": "0", "transition": "none"},
                )
                self.assert_matches_frame(selector, "border-radius")

    def test_iconview_selected_arms(self):
        """Pin the selected icon view restated off the landed row selection."""
        for selector in (
            "iconview.view:not(:disabled):selected",
            "iconview.view:not(:disabled):selected:focus",
            "iconview.view:not(:disabled):backdrop:selected",
        ):
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {
                        "background-color": SELECTION,
                        "color": BLACK,
                        "border-radius": "0",
                    },
                )
        self.assert_matches_frame("iconview.view:not(:disabled):selected", "border-radius")
        # Exact guarded spellings also prevent overriding disabled selections.
        # The family keeps the landed DND drop border as its only other
        # icon-view rule: a renamed restated arm leaves exactly its successor.
        # 2026-11-05: the tile-check face record restates eight more
        # iconview arms -- the selection-check state faces
        # `iconview.content-view.check…:not(list)` -- all pinned with the
        # other content-view check spellings by test_tile_check_faces.
        states = SELECTION_CHECK_STATES
        self.assertEqual(
            {selector for selector in self.rules if "iconview" in selector},
            {
                "iconview > dndtarget:drop(active)",
                "iconview",
                "iconview:focus:focus-visible",
                "iconview.view:not(:disabled):selected",
                "iconview.view:not(:disabled):selected:focus",
                "iconview.view:not(:disabled):backdrop:selected",
                *(
                    f"iconview.content-view.check{state}:not(list)"
                    for state in states
                ),
            },
        )

    def test_view_child_focus_outlines(self):
        selectors = (
            "iconview:focus:focus-visible",
            "flowbox > flowboxchild:focus:focus-visible",
            "gridview > child:focus:focus-visible",
        )
        self.assert_scale_anchored_focus_outline(selectors)
        self.assertEqual(self.selectors.count("iconview"), 1)
        self.assert_rule("iconview", {"transition": "none"})
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.endswith("child:focus:focus-visible")
            },
            set(selectors[1:]),
        )
        self.assertGreater(
            self.selectors.index("iconview:focus:focus-visible"),
            self.selectors.index("iconview.view:not(:disabled):backdrop:selected"),
        )
        self.assertLess(
            self.selectors.index("iconview:focus:focus-visible"),
            self.selectors.index("row:disabled:selected"),
        )

    def test_residual_focus_outline_color(self):
        selectors = (
            "label:focus:focus-visible",
            "link:focus:focus-visible",
            "expander-widget:focus:focus-visible > box > title",
            "colorswatch:focus:focus-visible",
            "plane:focus:focus-visible",
            "shortcut:focus:focus-visible",
        )
        self.assert_scale_anchored_focus_outline(selectors)
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"outline-color": BLACK})
        # The landed calendar label arm sits under ``calendar``, the link
        # state arms carry no focus twin, and the label selection arm is a
        # ``:focus-within`` selection rule, so matching ``:focus-visible``
        # pins exactly the six stock twins and rejects renames or strays.
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith(
                    ("label", "link", "colorswatch", "plane", "shortcut",
                     "expander-widget")
                )
                and ":focus-visible" in selector
            },
            set(selectors),
        )

    def test_card_focus_outline_color(self):
        """Pin the card focus arms to the landed black focus colour."""
        selectors = (
            "button.card:focus:focus-visible",
            ".card:focus:focus-visible",
        )
        self.assert_scale_anchored_focus_outline(selectors)
        # The landed tabgrid card arm ends with ``.card``, not
        # ``:focus-visible``, so the two ``:focus-visible``-ending card
        # spellings pin exactly the two stock twins and reject renames,
        # strays or a dropped arm.
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if "card" in selector and selector.endswith(":focus-visible")
            },
            set(selectors),
        )
        # The group closes the sheet after the residual focus group, so the
        # later source order wins every equal-specificity cascade tie.
        self.assertGreater(
            self.selectors.index("button.card:focus:focus-visible"),
            self.selectors.index("shortcut:focus:focus-visible"),
        )

    def test_cursor_handle_corners(self):
        """Pin the cursor-handle contents arm to the square-corner policy."""
        selector = "cursor-handle > contents"
        self.assert_rule(selector, {"border-radius": "0"})
        # The exact whole-rule dictionary catches stray restated geometry,
        # for example a mis-sized replay carrying stock's padding or
        # min-width/min-height into the user group.
        self.assert_square_corner(selector)
        self.assertEqual(self.selectors.count(selector), 1)
        # Stock's base arm and its three orientation twins stay
        # un-replayed: the squared whole-radius declaration makes their
        # per-corner radius cuts no-ops and later user-sheet source order
        # wins the equal-specificity tie, so exactly one cursor-handle
        # group exists and a renamed or orientated replay fails the scan.
        self.assertEqual(
            {s for s in self.rules if "cursor-handle" in s},
            {selector},
        )
        # The group closes the sheet's landed cursor-handle comment block
        # after the residual focus group and the landed card focus colour
        # group, so the later source order wins the equal-specificity
        # cascade tie against the stock resource: the 2026-11-04 alert-dialog
        # comment and corner groups follow it without speaking to any
        # cursor-handle node, so the tie keeps its winner.
        self.assertGreater(
            self.selectors.index("cursor-handle > contents"),
            self.selectors.index("label:focus:focus-visible"),
        )
        self.assertGreater(
            self.selectors.index("cursor-handle > contents"),
            self.selectors.index(".card:focus:focus-visible"),
        )
        self.assertLess(
            self.selectors.index("cursor-handle > contents"),
            self.selectors.index("window.dialog.message.csd:not(.solid-csd)"),
        )

    def test_generic_view_selected_arms(self):
        """Pin the generic view class fallback selection declarations."""
        for selector in (".view:selected", ".view:selected:focus"):
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {
                        "background-color": SELECTION,
                        "color": BLACK,
                        "border-radius": "0",
                    },
                )
        self.assert_matches_frame(".view:selected", "border-radius")
        self.assert_disabled_text((".view:disabled:selected",))
        self.assert_rule(".view:disabled:selected", {"color": "#888888"})

    def test_assistant_step_label_corners(self):
        expected = {"window.assistant .sidebar > label"}
        self.assertEqual(
            {selector for selector in self.rules if "assistant" in selector},
            expected,
        )
        self.assert_square_corner("window.assistant .sidebar > label")

    def test_pill_button_corners(self):
        expected = {
            "menubutton.pill > button",
            "button.pill",
            "menubutton.suggested-action.pill",
            "menubutton.opaque.pill",
        }
        self.assertEqual(
            {selector for selector in self.rules if ".pill" in selector},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                for reference in ("button", "frame > border", ".frame"):
                    self.assertEqual(
                        self.rules[selector]["border-radius"],
                        self.rules[reference]["border-radius"],
                    )

    def test_circular_button_corners(self):
        # The landed circular record squares the two children the toolkit
        # arms name; the 2026-11-04 container entry adds the two .circular
        # container members stock groups with the pill pair, so the
        # .circular sweep covers all four spellings.
        expected = {
            "menubutton.circular button",
            "button.circular",
            "menubutton.suggested-action.circular",
            "menubutton.opaque.circular",
        }
        self.assertEqual(
            {selector for selector in self.rules if ".circular" in selector},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, {"border-radius": "0"})
                for reference in ("button", "frame > border", ".frame"):
                    self.assertEqual(
                        self.rules[selector]["border-radius"],
                        self.rules[reference]["border-radius"],
                    )

    def test_row_spin_stepper_corners(self):
        """Pin the six restated preference-row spin stepper arms.

        No collected reference screenshot shows a preference-row spin
        stepper, so the sheet restates the six row-spin members stock's
        34px-minimum arm (and its earlier 9px arm) declares byte-equal,
        each carrying exactly the zero radius: the landed generic button
        restate names the one element and loses the compound row.spin tie,
        and the landed plain horizontal stepper groups name
        spinbutton:not(.vertical), so stock paints these steppers 9px and
        9999px round today. The six spellings sit in one comma group at the
        sheet tail with their dated comment.
        """
        expected = (
            "row.spin spinbutton > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):last-child",
            "row.spin spinbutton > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):last-child:dir(ltr):last-child",
            "row.spin spinbutton > button.image-button.up:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):last-child:dir(rtl):first-child",
            "row.spin spinbutton > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque)",
            "row.spin spinbutton > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(ltr):last-child",
            "row.spin spinbutton > button.image-button.down:not(.flat):not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque):dir(rtl):first-child",
        )
        for selector in expected:
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"border-radius": "0"})
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_matches_frame(selector, "border-radius")
        self.assertEqual(
            {selector for selector in self.rules if "row.spin" in selector},
            set(expected),
        )

    def test_sidebar_button_corners(self):
        """Pin the restated sidebar navigation-button radius arm.

        No collected reference screenshot shows a sidebar navigation
        button, so the sheet restates stock's 16px-minimum 100%-radius arm
        byte-equal with exactly the zero radius: the landed sidebar records
        own the focus outline colour and the selection-tint colours only,
        so stock keeps this button's face round today.
        """
        selector = "button.sidebar-button"
        self.assert_rule(selector, {"border-radius": "0"})
        self.assertEqual(self.selectors.count(selector), 1)
        self.assert_matches_frame(selector, "border-radius")
        self.assertEqual(
            {selector for selector in self.rules if "sidebar-button" in selector},
            {
                "button.sidebar-button",
                "button.sidebar-button:focus:focus-visible",
                ROW_SELECTED_BUTTON_ARM_SIDEBAR,
                ROW_SELECTED_BUTTON_ARM_SIDEBAR_BACKDROP,
            },
        )

    def test_video_osd_image_corners(self):
        self.assertEqual(
            {selector for selector in self.rules if "video" in selector},
            {"video image.osd"},
        )
        video_image = self.rules["video image.osd"]
        self.assertEqual(video_image, {"border-radius": "0"})
        for selector in ("frame > border", ".frame"):
            with self.subTest(selector=selector):
                self.assertEqual(
                    video_image["border-radius"],
                    self.rules[selector]["border-radius"],
                )

    def test_tab_thumbnail_corners(self):
        # The 2026-11-04 tab-family corner row adds three stock-spelling
        # tab-overview members beside the landed tab-preview shell spellings.
        expected = {
            "tabthumbnail",
            "tabthumbnail .card picture",
            "tabthumbnail button",
            "tabthumbnail button > image",
            "tabthumbnail .needs-attention > widget",
        }
        self.assertEqual(
            {selector for selector in self.rules if "tabthumbnail" in selector},
            expected,
        )
        for selector in expected:
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_matches_frame(selector, "border-radius")

    def test_split_button_container_corners(self):
        container = "splitbutton"
        band = [
            "actionbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            "searchbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            ".toolbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            "headerbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            "actionbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            "searchbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            ".toolbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            "headerbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            "splitbutton.flat > button",
            "splitbutton.flat > menubutton > button",
        ]
        self.assertEqual(
            {
                selector
                for selector, declarations in self.rules.items()
                if "splitbutton" in selector and "border-radius" in declarations
            },
            {container} | set(band),
        )
        splitbutton = self.rules[container]
        # The landed container record keeps its frame-equal radius; the
        # 2026-11-04 band group squares the absolute-band and .flat faces
        # beside it, and test_splitbutton_band_corners pins their spellings.
        self.assertEqual(splitbutton, {"border-radius": "0"})
        for selector in ("frame > border", ".frame", "button"):
            with self.subTest(selector=selector):
                self.assertEqual(
                    splitbutton["border-radius"],
                    self.rules[selector]["border-radius"],
                )
        for selector in band:
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, {"border-radius": "0"})

    def test_splitbutton_band_corners(self):
        """Pin the toolbar-band and flat split-button face corners.

        The band arm carries four :not() classes behind every band prefix,
        so the landed generic button radius restate loses on it; the group
        restates every spelling byte-equal to stock so later user-sheet
        source order wins the equal-specificity cascade tie.
        """
        band = [
            "actionbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            "searchbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            ".toolbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            "headerbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > button",
            "actionbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            "searchbar > revealer > box splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            ".toolbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            "headerbar splitbutton:"
            "not(.raised):not(.suggested-action):not(.destructive-action):"
            "not(.opaque) > menubutton > button",
            "splitbutton.flat > button",
            "splitbutton.flat > menubutton > button",
        ]
        # The landed band focus twins end with :focus:focus-visible, so
        # they stay out of this suffix scan, and the bare container key
        # never ends with these suffixes either. Exactly ten face spellings
        # square to the policy; nothing else in the sheet touches a
        # split-button face.
        self.assertEqual(
            {
                s
                for s in self.rules
                if "splitbutton" in s
                and (s.endswith("> button") or s.endswith("> menubutton > button"))
            },
            set(band),
        )
        for selector in band:
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_square_corner(selector)
                # The group sits between the landed searchbar band focus
                # group and the residual focus group: after the landed
                # splitbutton container key, before label:focus:focus-visible.
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("splitbutton"),
                )
                self.assertLess(
                    self.selectors.index(selector),
                    self.selectors.index("label:focus:focus-visible"),
                )

    def test_navigation_sidebar_item_corners(self):
        expected = {
            ".navigation-sidebar > row",
            ".navigation-sidebar > child",
            ".navigation-sidebar > flowboxchild",
        }
        # The row-focus restate adds one stock focus twin
        # under the same prefix; it states the focus outline, not the corner
        # radius, and test_list_row_focus_outlines pins its spelling.
        focus = {".navigation-sidebar > row:focus-visible:focus-within"}
        self.assertEqual(
            {selector for selector in self.rules
             if selector.startswith(".navigation-sidebar > ")},
            expected | focus,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assert_square_corner(selector)
        self.assert_rule(
            ".navigation-sidebar > row:focus-visible:focus-within",
            {"outline-color": BLACK},
        )

    def test_sidebar_row_icon_opacity(self):
        # The sheet restates the toolkit resource's 0.7 veil
        # arm, which is state-independent, so no hover, active, selected or
        # backdrop twin exists and the family holds exactly this one rule.
        self.assertEqual(
            {selector for selector in self.rules if "sidebar-icon" in selector},
            {"row image.sidebar-icon"},
        )
        self.assert_rule("row image.sidebar-icon", {"opacity": "1"})
        self.assertEqual(self.selectors.count("row image.sidebar-icon"), 1)
        # Held in the landed sidebar neighbourhood, not a detached tail.
        self.assertGreater(
            self.selectors.index("row image.sidebar-icon"),
            self.selectors.index(
                "placessidebar .navigation-sidebar > row:drop(active)"
                ":not(:disabled):selected"),
        )

    def test_boxed_list_corners(self):
        roots = ("list.boxed-list", "list.content")
        suffixes = (
            "",
            " > row:first-child",
            " > row:last-child",
            " > row:first-child.expander row.header",
            " > row:last-child.expander:not(:checked)",
            " > row:last-child.expander:not(:checked) row.header",
            " > row:last-child.expander:checked list.nested",
            " > row:last-child.expander:checked list.nested > row:last-child",
        )
        expected = {root + suffix for root in roots for suffix in suffixes}
        # The row-focus restate adds two stock focus twins
        # under each root; they state the focus outline, not the corner
        # radius, and test_list_row_focus_outlines pins their spelling.
        focus = {
            "list.boxed-list > row:focus:focus-visible",
            "list.boxed-list > row.expander row.header:focus:focus-visible",
            "list.content > row:focus:focus-visible",
            "list.content > row.expander row.header:focus:focus-visible",
        }
        self.assertEqual(
            {selector for selector in self.rules
             if any(selector == root or selector.startswith(root + " ")
                    for root in roots)},
            expected | focus,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assert_square_corner(selector)
        for selector in sorted(focus):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"outline-color": BLACK})

    def test_separate_boxed_row_corners(self):
        expected = {
            "list.boxed-list-separate > row",
            "list.boxed-list-separate > row.expander row.header",
            "list.boxed-list-separate > row.expander:not(:checked) row.header",
            "list.boxed-list-separate > row.expander.expander:checked list.nested",
            "list.boxed-list-separate > row.expander.expander:checked list.nested > row:last-child",
        }
        # The row-focus restate adds two stock focus twins
        # under the same root; they state the focus outline, not the corner
        # radius, and test_list_row_focus_outlines pins their spelling.
        focus = {
            "list.boxed-list-separate > row:focus:focus-visible",
            "list.boxed-list-separate > row.expander row.header:focus:focus-visible",
        }
        self.assertEqual(
            {selector for selector in self.rules
             if "list.boxed-list-separate" in selector},
            expected | focus,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assert_square_corner(selector)
        for selector in sorted(focus):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"outline-color": BLACK})

    def test_color_swatch_corners(self):
        # The residual focus restate adds the focus twin
        # under the same root; it states the focus outline colour, not a
        # corner radius, and test_residual_focus_outline_color pins its
        # spelling.
        self.assert_color_swatch_corners(
            " > overlay",
            extra_declarations={
                "colorswatch:focus:focus-visible": {"outline-color": BLACK},
                # The 2026-11-04 container entry squares the colour
                # button's two higher-specificity swatch spellings stock
                # groups before the integration library's own arm; they
                # carry the corner radius and nothing else.
                "button.color > colorswatch:only-child": {"border-radius": "0"},
                "button.color > colorswatch:only-child > overlay": {
                    "border-radius": "0"
                },
            },
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

    def test_scrollbar(self):
        self.assert_rule(
            "scrollbar > range > trough",
            {
                "background-color": TROUGH,
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
            },
        )
        self.assert_rule(
            "scrollbar > range > trough > slider",
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "margin": "0",
                "min-width": "12px",
                "min-height": "12px",
                "box-shadow": RAISED_BEVEL,
            },
        )

    def test_scrollbar_ordinary_trough_margins(self):
        for selector in (
            "scrollbar.horizontal:not(.overlay-indicator) > range > trough",
            "scrollbar.vertical:not(.overlay-indicator) > range > trough",
        ):
            self.assert_rule(selector, {"margin": "0"})

    def test_scrollbar_overlay_trough_margins(self):
        for selector in (
            "scrollbar.overlay-indicator.horizontal.hovering > range > trough",
            "scrollbar.overlay-indicator.horizontal:not(.hovering) > range > trough",
            "scrollbar.overlay-indicator.vertical.hovering > range > trough",
            "scrollbar.overlay-indicator.vertical:not(.hovering) > range > trough",
        ):
            self.assert_rule(selector, {"margin": "0"})

    def test_scrollbar_overlay_hover_trough_face(self):
        base_face = self.rules["scrollbar > range > trough"]["background-color"]
        self.assertEqual(base_face, TROUGH)
        self.assert_rule(
            "scrollbar.overlay-indicator.hovering > range > trough",
            {"background-color": base_face},
        )

    def test_scrollbar_overlay_thumb_outline(self):
        self.assert_rule(
            "scrollbar.overlay-indicator > range > trough > slider",
            {"outline": "none"},
        )

    def test_scrollbar_overlay_thumb_breadth(self):
        slider = self.rules["scrollbar > range > trough > slider"]
        for selector in (
            "scrollbar.overlay-indicator.horizontal.hovering > range > trough > slider",
            "scrollbar.overlay-indicator.horizontal:not(.hovering) > range > trough > slider",
        ):
            self.assert_rule(selector, {"min-height": slider["min-height"]})
        for selector in (
            "scrollbar.overlay-indicator.vertical.hovering > range > trough > slider",
            "scrollbar.overlay-indicator.vertical:not(.hovering) > range > trough > slider",
        ):
            self.assert_rule(selector, {"min-width": slider["min-width"]})

    def test_scrollbar_disabled_thumb_opacity(self):
        self.assert_rule(
            "scrollbar > range > trough > slider:disabled",
            {"opacity": "1"},
        )

    def test_scrollbar_fine_tune_thumb_face(self):
        base_face = self.rules["scrollbar > range > trough > slider"]["background-color"]
        self.assertEqual(base_face, FACE)
        for selector in (
            "scrollbar > range.fine-tune > trough > slider",
            "scrollbar > range.fine-tune > trough > slider:hover",
            "scrollbar > range.fine-tune > trough > slider:active",
        ):
            self.assert_rule(selector, {"background-color": base_face})

    def test_scrollbar_thumb_interaction_face(self):
        base_face = self.rules["scrollbar > range > trough > slider"]["background-color"]
        self.assertEqual(base_face, FACE)
        for selector in (
            "scrollbar > range > trough > slider:hover",
            "scrollbar > range > trough > slider:active",
        ):
            self.assert_rule(selector, {"background-color": base_face})

    def test_scrollbar_thumb_transition(self):
        self.assert_rule(
            "scrollbar > range > trough > slider",
            {"transition": "none"},
        )

    def test_scrollbar_trough_transition(self):
        self.assert_rule(
            "scrollbar > range > trough",
            {"transition": "none"},
        )

    def test_undershoot_bands_cleared(self):
        """Every stock undershoot context is mirrored, clearing its paint."""
        self.assert_rule(
            "scrolledwindow.undershoot-top > undershoot.top",
            {"background": "none", "box-shadow": "none"},
        )
        self.assert_rule(
            "scrolledwindow.undershoot-bottom > undershoot.bottom",
            {"background": "none", "box-shadow": "none"},
        )
        self.assert_rule(
            "scrolledwindow.undershoot-start:dir(ltr) > undershoot.left",
            {"background": "none", "box-shadow": "none"},
        )
        self.assert_rule(
            "scrolledwindow.undershoot-start:dir(rtl) > undershoot.right",
            {"background": "none", "box-shadow": "none"},
        )
        self.assert_rule(
            "scrolledwindow.undershoot-end:dir(ltr) > undershoot.right",
            {"background": "none", "box-shadow": "none"},
        )
        self.assert_rule(
            "scrolledwindow.undershoot-end:dir(rtl) > undershoot.left",
            {"background": "none", "box-shadow": "none"},
        )
        for selector in (
            "columnview ~ undershoot.top",
            "treeview.view ~ undershoot.top",
            "window.print:not(.ssd-frame) treeview.dialog-action-box ~ undershoot.top",
            "dropdown popover.menu .dropdown-searchbar "
            "+ scrolledwindow:not(.undershoot-top) > undershoot.top",
            "combobox popover.menu .dropdown-searchbar "
            "+ scrolledwindow:not(.undershoot-top) > undershoot.top",
            "popover.emoji-picker scrolledwindow.view:not(.undershoot-top) > undershoot.top",
            "popover.emoji-picker scrolledwindow.view:not(.undershoot-bottom) > undershoot.bottom",
            "filechooser gridview ~ undershoot.top",
            "filechooser placesview > stack > scrolledwindow > undershoot.bottom",
            "row.combo popover > contents .combo-searchbar + scrolledwindow > undershoot.top",
            "toolbarview.undershoot-top scrolledwindow > undershoot.top",
            "toolbarview.undershoot-bottom scrolledwindow > undershoot.bottom",
        ):
            self.assert_rule(selector, {"background": "none", "box-shadow": "none"})

    def test_overshoot_fades_cleared(self):
        """Each overshoot direction is mirrored, clearing its radial glows."""
        for selector in (
            "scrolledwindow > overshoot.top",
            "scrolledwindow > overshoot.bottom",
            "scrolledwindow > overshoot.left",
            "scrolledwindow > overshoot.right",
        ):
            self.assert_rule(selector, {"background-image": "none"})

    def test_scrolled_corner_junction_shares_the_scrollbar_band(self):
        """Both scrollbar-corner junction arms paint the landed trough band."""
        expected = {"background-color": TROUGH, "background-image": "none"}
        for selector in (
            "scrolledwindow > junction",
            "scrolledwindow > junction:dir(rtl)",
        ):
            self.assert_rule(selector, expected)
            self.assert_exact_rule_once(selector, expected)
            self.assertLess(
                self.selectors.index("scrolledwindow > overshoot.right"),
                self.selectors.index(selector),
            )
            self.assertLess(
                self.selectors.index(selector),
                self.selectors.index(
                    "scrollbar.overlay-indicator.hovering > range > trough"
                ),
            )
        self.assertEqual(
            {s for s in self.rules if "junction" in s},
            {
                "scrolledwindow > junction",
                "scrolledwindow > junction:dir(rtl)",
            },
        )

    def test_progressbar(self):
        self.assert_progressbar(
            trough="progressbar > trough",
            progress="progressbar > trough > progress",
            disabled="progressbar > trough > progress:disabled",
        )

    def test_progressbar_label_ink(self):
        """A meter's show-text percentage label keeps the landed window ink."""
        self.assert_rule_group({"progressbar": {"color": BLACK}})
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("progressbar")
                and ">" not in s
                and "." not in s
            },
            {"progressbar", "progressbar:disabled"},
        )
        self.assert_rule_after("progressbar > trough {", "progressbar {")

    def test_treeview_progress_cell_faces(self):
        """A view row's progress cell keeps the landed meter faces."""
        selected_cell = (
            "columnview.view.progressbar:selected:focus",
            "columnview.view.progressbar:selected",
            "treeview.view.progressbar:selected:focus",
            "treeview.view.progressbar:selected",
        )
        selected_backdrop_cell = (
            "columnview.view.progressbar:selected:focus:backdrop",
            "columnview.view.progressbar:selected:backdrop",
            "treeview.view.progressbar:selected:focus:backdrop",
            "treeview.view.progressbar:selected:backdrop",
        )
        selected_cell_trough = (
            "columnview.view.trough:selected:focus",
            "columnview.view.trough:selected",
            "treeview.view.trough:selected:focus",
            "treeview.view.trough:selected",
        )
        expected = {
            "columnview.view.progressbar": {
                "color": BLACK,
                "background-color": SELECTION,
                "background-image": "none",
                "box-shadow": "none",
            },
            "treeview.view.progressbar": {
                "color": BLACK,
                "background-color": SELECTION,
                "background-image": "none",
                "box-shadow": "none",
            },
            "columnview.view.trough": {
                "background-color": TROUGH,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": f"inset 1px 1px {GREY}",
            },
            "treeview.view.trough": {
                "background-color": TROUGH,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": f"inset 1px 1px {GREY}",
            },
        }
        for selector in selected_cell + selected_backdrop_cell:
            expected[selector] = {
                "color": BLACK,
                "background-color": WHITE,
                "background-image": "none",
                "box-shadow": "none",
            }
        for selector in selected_cell_trough:
            expected[selector] = {"background-color": TROUGH}
        self.assert_rule_group(expected)
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith(("columnview.view", "treeview.view"))
                and ("progressbar" in s or "trough" in s)
            },
            set(expected),
        )
        self.assertNotIn("min-height", self.rules["columnview.view.trough"])
        self.assertNotIn("min-height", self.rules["treeview.view.trough"])
        self.assertNotIn("min-width", self.rules["columnview.view.trough"])
        self.assertNotIn("min-width", self.rules["treeview.view.trough"])
        self.assertGreater(
            self.selectors.index("columnview.view.progressbar"),
            self.selectors.index("progressbar"),
        )
        self.assertLess(
            self.selectors.index("treeview.view.trough"),
            self.selectors.index("progressbar > trough"),
        )

    def test_progressbar_osd_trough_paint(self):
        selector = "progressbar.osd > trough"
        expected = {
            "background-color": TROUGH,
            "border": f"1px solid {BLACK}",
            "box-shadow": f"inset 1px 1px {GREY}",
        }
        self.assert_rule(selector, expected)
        self.assertEqual(self.rules[selector], expected)
        base = self.rules["progressbar > trough"]
        self.assertEqual(
            {name: self.rules[selector][name] for name in expected},
            {name: base[name] for name in expected},
        )

    def test_headerbar_meter_faces(self):
        """A meter embedded in the title band keeps the landed faces.

        Stock's one headerbar-descended meter arm repaints troughs and
        scale fills inside a headerbar with the stock band face; the
        sheet restates the arm's spellings split by landed value so a
        headerbar progress bar or scale keeps the landed `#EEEEEE`
        trough face and the landed transparent fill and highlight
        faces under either loading reading. The whole-dict reads kill
        a stock band value, a dropped or added spelling, a merged
        single group carrying one value and any value drift; the
        occurrence sweep kills a stray twin or per-state split; the
        order pin fixes the block between the landed fill/highlight
        and hover/active highlight groups.
        """
        trough_expected = {"background-color": TROUGH}
        fill_expected = {"background-color": "transparent"}
        self.assert_rule_group(
            {
                "headerbar progressbar > trough": trough_expected,
                "headerbar scale > trough": trough_expected,
                "headerbar scale > trough > fill": fill_expected,
                "headerbar scale > trough > highlight": fill_expected,
            }
        )
        # The whole-sheet sweep: no other headerbar-descended trough,
        # progressbar or scale spelling parses anywhere in the sheet.
        def headerbar_meter_selector(selector):
            tokens = set(selector.replace(">", " ").split())
            return "headerbar" in tokens and tokens & {
                "trough",
                "progressbar",
                "scale",
            }

        self.assertEqual(
            {s for s in self.selectors if headerbar_meter_selector(s)},
            {
                "headerbar progressbar > trough",
                "headerbar scale > trough",
                "headerbar scale > trough > fill",
                "headerbar scale > trough > highlight",
            },
        )
        self.assert_rule_after(
            "headerbar progressbar > trough, headerbar scale > trough {",
            "scale > trough > fill, scale > trough > highlight {",
        )
        self.assert_rule_after(
            "scale:hover > trough > highlight, scale:active > trough > highlight {",
            "headerbar scale > trough > fill, headerbar scale > trough > highlight {",
        )

    def test_progressbar_osd_trough_thickness(self):
        horizontal = "progressbar.osd.horizontal > trough"
        vertical = "progressbar.osd.vertical > trough"
        expected = {
            horizontal: {"min-height": self.rules["progressbar > trough"]["min-height"]},
            vertical: {"min-width": self.rules["progressbar > trough"]["min-width"]},
        }
        self.assertEqual(expected[horizontal]["min-height"], PROGRESSBAR_TROUGH["min-height"])
        self.assertEqual(expected[vertical]["min-width"], PROGRESSBAR_TROUGH["min-width"])
        self.assert_rule_group(expected)

    def test_progressbar_oriented_trough_thickness(self):
        horizontal = "progressbar.horizontal > trough"
        vertical = "progressbar.vertical > trough"
        expected = {
            horizontal: {"min-height": self.rules["progressbar > trough"]["min-height"]},
            vertical: {"min-width": self.rules["progressbar > trough"]["min-width"]},
        }
        self.assertEqual(expected[horizontal]["min-height"], PROGRESSBAR_TROUGH["min-height"])
        self.assertEqual(expected[vertical]["min-width"], PROGRESSBAR_TROUGH["min-width"])
        self.assert_rule_group(expected)

    def test_progressbar_directional_corners(self):
        self.assert_rule("progressbar > trough > progress", {"border-radius": "0"})
        for direction in ("left", "right", "top", "bottom"):
            with self.subTest(direction=direction):
                selector = f"progressbar > trough > progress.{direction}"
                self.assert_rule(
                    selector,
                    {"border-radius": "0"},
                )
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                self.assertEqual(
                    self.rules[selector]["border-radius"],
                    self.rules["progressbar > trough > progress"]["border-radius"],
                )

    def test_progressbar_disabled_filter(self):
        self.assertEqual(self.rules["progressbar:disabled"], {"filter": "none"})
        self.assertEqual(
            self.rules["progressbar > trough > progress:disabled"],
            {"background-color": GREY},
        )

    def test_selected_row_meter_rims(self):
        """A meter in a selected row keeps the landed rims over the selection.

        Stock's selected-row meter arms (libgtk-4 light resource lines
        1085, 1095 and 1133, dark twins at 1073, 1083 and 1121) repaint
        the trough rim with the stock accent-deep ink under the stock
        translucent white selection outline and both thumb states with
        the accent-deep ink, and the `row:selected` prefix out-specifies
        the landed plain meter groups, so inside the landed lavender
        selection a meter's rims repaint stock's ink today. The restated
        groups repeat the landed trough rim #000000 and the landed thumb
        rims — #000000 enabled, flat #999999 disabled — as byte-equal
        stock spellings that sit later, so under lower-sheet riding they
        win the per-property tie at stock's own specificity; under the
        replacement reading these rules are the only holders of the
        spellings. Stock's one thumb comma group is split by landed state
        into two single-spelling rules, since a comma group shares its
        declarations across every member and one group cannot carry the
        disabled thumb's flat grey rim and the enabled thumb's black rim;
        the disabled spelling out-specifies the bare thumb spelling, so
        each state keeps its landed rim. The sweep and order pins kill a
        merged comma group, a renamed spelling and a stray selected-row
        meter rule.
        """
        self.assert_rule_group(
            {
                "row:selected progressbar > trough": {"border-color": BLACK},
                "row:selected scale > trough": {"border-color": BLACK},
                "row:selected scale > trough > slider:disabled": {
                    "border-color": GREY
                },
                "row:selected scale > trough > slider": {
                    "border-color": BLACK
                },
            }
        )
        self.assertEqual(
            {
                selector
                for selector in self.selectors
                if selector.startswith("row:selected")
                and ("trough" in selector or "slider" in selector)
            },
            {
                "row:selected progressbar > trough",
                "row:selected scale > trough",
                "row:selected scale > trough > slider:disabled",
                "row:selected scale > trough > slider",
            },
        )
        # The restated rims sit inside the landed disabled-meter
        # neighbourhood on the raw sheet: after the landed disabled
        # trough group and before the landed opaque disabled policy.
        self.assert_rule_after(
            "row:selected progressbar > trough,",
            "scale > trough:disabled",
        )
        self.assert_rule_after(
            "progressbar:disabled",
            "row:selected scale > trough > slider:disabled",
        )

    def test_spinner(self):
        self.assert_spinner("transform")

    def test_levelbar(self):
        self.assert_levelbar(
            trough="levelbar > trough",
            filled="levelbar > trough > block.filled",
            empty="levelbar > trough > block.empty",
            disabled="levelbar > trough > block.filled:disabled",
            horizontal="levelbar.horizontal > trough > block",
            vertical="levelbar.vertical > trough > block",
        )

    def test_levelbar_disabled_filter(self):
        self.assert_rule("levelbar:disabled", {"filter": "none"})
        self.assert_rule(
            "levelbar > trough > block.filled:disabled",
            {"background-color": GREY},
        )

    def test_levelbar_discrete_cross_size(self):
        cases = (
            (
                "levelbar.horizontal.discrete > trough > block",
                "min-height",
                "levelbar.horizontal > trough > block",
            ),
            (
                "levelbar.vertical.discrete > trough > block",
                "min-width",
                "levelbar.vertical > trough > block",
            ),
        )
        for selector, dimension, continuous_selector in cases:
            with self.subTest(selector=selector):
                expected = {dimension: self.rules[continuous_selector][dimension]}
                self.assert_rule(selector, expected)
                self.assertEqual(self.rules[selector], expected)

    def test_levelbar_block_corners(self):
        selectors = (
            "levelbar.horizontal trough > block",
            "levelbar.vertical trough > block",
            "levelbar.horizontal trough > block.empty",
            "levelbar.horizontal trough > block.full",
            "levelbar.vertical trough > block.empty",
            "levelbar.vertical trough > block.full",
            "levelbar.horizontal.discrete > trough > block:first-child",
            "levelbar.horizontal.discrete > trough > block:last-child",
            "levelbar.vertical.discrete > trough > block:first-child",
            "levelbar.vertical.discrete > trough > block:last-child",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"border-radius": "0"})

    def test_levelbar_directional_block_corners(self):
        for selector in (
            "levelbar.horizontal trough > block:dir(ltr)",
            "levelbar.horizontal trough > block:dir(rtl)",
        ):
            with self.subTest(selector=selector):
                expected = {"border-radius": "0"}
                self.assert_rule(selector, expected)
                self.assertEqual(self.rules[selector], expected)
                self.assertEqual(
                    self.rules[selector]["border-radius"],
                    self.rules["levelbar.horizontal trough > block"]["border-radius"],
                )

    def test_switch(self):
        self.assert_switch(
            slider="switch > slider",
            disabled_slider="switch:disabled > slider",
            glyph="switch > image",
        )

    def test_switch_osd_checked_track_color(self):
        selector = ".osd switch:checked"
        self.assert_rule(selector, {"background-color": WHITE})
        self.assertEqual(
            self.rules[selector]["background-color"],
            self.rules["switch:checked"]["background-color"],
        )

    def test_switch_track_transition(self):
        self.assert_rule("switch", {"transition": "none"})

    def test_switch_focus_outline_color(self):
        self.assert_scale_focus_outline("switch:focus:focus-visible")

    def test_switch_interaction_track_faces(self):
        for selector in ("switch:hover", "switch:active"):
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {"background-color": "#EEEEEE", "background-image": "none"},
                )
        for selector in ("switch:checked:hover", "switch:checked:active"):
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {"background-color": "#FFFFFF", "background-image": "none"},
                )

    def test_switch_checked_thumb_face(self):
        self.assert_rule(
            "switch:checked > slider", {"background-color": "#DDDDDD"}
        )

    def test_switch_interaction_thumb_face(self):
        for selector in ("switch:hover > slider", "switch:active > slider"):
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"background-color": "#DDDDDD"})

    def test_switch_disabled_filter(self):
        self.assert_rule("switch:disabled", {"filter": "none"})

    def test_tabbar_backdrop_filter(self):
        value = self.rules["switch:disabled"]["filter"]
        for selector in (
            "tabbar .box:backdrop > scrolledwindow",
            "tabbar .box:backdrop > .start-action",
            "tabbar .box:backdrop > .end-action",
        ):
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"filter": "none"})
                self.assertEqual(self.rules[selector]["filter"], value)

    def test_tabbar_tab_and_indicator_corners(self):
        """The stock tab-family radii answer the square-corner policy.

        The sheet restates ten byte-equal stock spellings plus
        the extended tab-box base: eleven border-radius-zero selectors, each
        counted once, each matching both frame arms' radius, with the two
        family scans and the source-order span killing renamed and stray
        variants.
        """
        selectors = (
            "tabbar tab",
            "dnd tab",
            "tabbar tab button.image-button",
            "dnd tab button.image-button",
            "tabbar tab indicator",
            "dnd tab indicator",
            "tabbar tabbox > revealer > indicator",
            "tabthumbnail button",
            "tabthumbnail button > image",
            "tabthumbnail .needs-attention > widget",
            # The extended base group also keeps its landed no-transition.
            "tabbar tabbox > tabboxchild",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_matches_frame(selector, "border-radius")
        self.assertEqual(
            self.rules["tabbar tabbox > tabboxchild"],
            {"border-radius": "0", "transition": "none"},
        )
        # Family scans kill renamed and stray variants. The parsed sheet
        # splits every comma group into per-member selector keys, so the
        # "dnd tab" substring scan reaches only the three dnd members and the
        # exact "tabbar tab" token scans reach the three tabbar members;
        # together the two scans cover all six pair members.
        self.assertEqual(
            {selector for selector in self.rules if "dnd tab" in selector},
            {
                "dnd tab",
                "dnd tab button.image-button",
                "dnd tab indicator",
            },
        )
        self.assertEqual(
            {selector for selector in self.rules
             if selector == "tabbar tab"
             or selector.startswith("tabbar tab ")},
            {
                "tabbar tab",
                "tabbar tab button.image-button",
                "tabbar tab indicator",
            },
        )
        self.assertEqual(
            {selector for selector in self.rules
             if "tabthumbnail button" in selector},
            {"tabthumbnail button", "tabthumbnail button > image"},
        )
        self.assertEqual(
            {selector for selector in self.rules
             if "revealer > indicator" in selector},
            {"tabbar tabbox > revealer > indicator"},
        )
        # Source order: the tab seam restatements sit after the landed tabgrid
        # focus arm and before the stack switcher face.
        self.assertGreater(
            self.selectors.index("dnd tab"),
            self.selectors.index(
                "tabgrid > tabgridchild:focus:focus-visible .card"),
        )
        self.assertLess(
            self.selectors.index("dnd tab"),
            self.selectors.index("stackswitcher > button"),
        )

    def test_tabbar_tabboxchild_focus(self):
        base = "tabbar tabbox > tabboxchild"
        focus = "tabbar tabbox > tabboxchild:focus-within:focus-visible"
        self.assertEqual(
            self.rules[base], {"border-radius": "0", "transition": "none"})
        self.assertEqual(
            self.rules[base]["transition"],
            self.rules[SCALE_SLIDER]["transition"],
        )
        self.assert_scale_focus_outline(focus)
        for selector in (base, focus):
            self.assertEqual(self.selectors.count(selector), 1)
        self.assertEqual(
            {selector for selector in self.rules if "tabboxchild" in selector},
            {base, focus},
        )
        self.assertGreater(
            self.selectors.index(focus),
            self.selectors.index("tabbar .box:backdrop > scrolledwindow"),
        )
        self.assertLess(
            self.selectors.index(focus),
            self.selectors.index("stackswitcher > button"),
        )

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

    def test_switch_track_padding(self):
        self.assert_rule("switch", {"padding": "0"})

    def test_toggle_group_corners(self):
        # The 2026-11-04 toggle-family corner row adds four stock-spelling
        # members at the sheet's switch seam.
        expected = {
            "toggle-group",
            "toggle-group > toggle",
            "toggle-group.round",
            "toggle-group.round toggle",
        }
        self.assertEqual(
            {selector for selector in self.rules if "toggle-group" in selector},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_square_corner(selector)
        for selector in sorted(expected):
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("switch > image"),
            )
            self.assertLess(
                self.selectors.index(selector),
                self.selectors.index(".toolbar"),
            )

    def test_indicator_bin_corners(self):
        # Stock cuts the indicator bin's badge dot and its reveal mask into
        # circles; the square-corner policy squares both nodes together —
        # squaring one alone would leave them disagreeing. The two
        # descendants of this comma group are the sheet's whole
        # indicatorbin family.
        selectors = {"indicatorbin > indicator", "indicatorbin > mask"}
        self.assertEqual(
            {selector for selector in self.rules if "indicatorbin" in selector},
            selectors,
        )
        for selector in sorted(selectors):
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_square_corner(selector)
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("floating-sheet > sheet"),
                )

    def test_color_button_and_menubutton_container_corners(self):
        # The 2026-11-04 container group squares the colour button's inner
        # swatch face and its overlay plus the plain, suggested-action and
        # opaque menu-button containers; the coloured container paints its
        # own rounding (its background arm rests on the container node
        # while the covered child buttons declare transparent
        # backgrounds), so the six face groups join them in one comma
        # group. The two .pill container spellings stay excluded: the
        # landed pill record already squares them byte-for-byte.
        selectors = {
            "button.color > colorswatch:only-child",
            "button.color > colorswatch:only-child > overlay",
            "menubutton.suggested-action",
            "menubutton.opaque",
            "menubutton.suggested-action.circular",
            "menubutton.opaque.circular",
        }
        for selector in sorted(selectors):
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_square_corner(selector)
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("indicatorbin > mask"),
                )
        # The distinctive button colour token is new to the sheet, so the
        # scan is its whole contract; a stray state twin would carry it
        # into the set. (The menu-button tokens cannot be swept by
        # substring: landed band focus and covered-button spellings name
        # them too, so those faces guard by count-1 and whole-rule above.)
        self.assertEqual(
            {selector for selector in self.rules if "button.color" in selector},
            {
                "button.color > colorswatch:only-child",
                "button.color > colorswatch:only-child > overlay",
            },
        )

    def test_residual_radius_corners(self):
        # The 2026-11-04 residual-corner row squares the last seven
        # radius-bearing stock widget faces no landed restatement reaches:
        # the eight byte-equal spellings in one tail comma group (the
        # about-dialog version pill carries two node arms stock splits in
        # its own comma group, so eight selectors serve seven faces).
        selectors = {
            "avatar",
            "scale.horizontal.marks-before.marks-after > trough > slider",
            "scale.color > trough",
            "colorchooser .popover.osd",
            "shortcut",
            "window.about .main-page .app-version",
            "dialog.about .main-page .app-version",
            ".accent-color-row color",
        }
        for selector in sorted(selectors):
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, {"border-radius": "0"})
                self.assert_matches_frame(selector, "border-radius")
                self.assertGreater(
                    self.selectors.index(selector),
                    self.selectors.index("indicatorbin > mask"),
                )
        # Family sweeps on the distinctive tokens no landed selector
        # carries; the shortcut shell settles for the whole-dict and
        # count-1 guard above because the token already names the landed
        # keycap and focus spellings.
        self.assertEqual(
            {selector for selector in self.rules if "avatar" in selector},
            {"avatar"},
        )
        self.assertEqual(
            {selector for selector in self.rules if "app-version" in selector},
            {
                "window.about .main-page .app-version",
                "dialog.about .main-page .app-version",
            },
        )
        self.assertEqual(
            {selector for selector in self.rules if "scale.color" in selector},
            {"scale.color > trough"},
        )
        self.assertEqual(
            {selector for selector in self.rules if "popover.osd" in selector},
            {"colorchooser .popover.osd"},
        )
        self.assertEqual(
            {selector for selector in self.rules if "accent-color-row" in selector},
            {".accent-color-row color"},
        )
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if "marks-before.marks-after" in selector
            },
            {"scale.horizontal.marks-before.marks-after > trough > slider"},
        )

    def test_alert_dialog_corners(self):
        # The 2026-11-04 alert-dialog comment block appends six
        # stock-comma groups after the landed cursor-handle tail group;
        # the sheet parser splits each comma group into per-selector keys,
        # nine in all (the legacy .dialog-action-area keys from the landed
        # message-dialog records join the action-area prefix scan below).
        members = {
            "window.dialog.message.csd:not(.solid-csd)": {"border-radius": "0"},
            "window.dialog.message.csd .dialog-action-area > button": {
                "border-radius": "0"
            },
            "window.messagedialog .response-area > button": {"border-radius": "0"},
            "dialog.alert .response-area > button": {"border-radius": "0"},
            "dialog-host > dialog.alert sheet": {"border-radius": "0"},
            "window.messagedialog.csd:not(.solid-csd)": {"border-radius": "0"},
            "window.dialog-window.alert.csd:not(.solid-csd)": {"border-radius": "0"},
            "dialog-host > dialog.alert sheet .body-scrolled-window > viewport": {
                "border-top-left-radius": "0",
                "border-top-right-radius": "0",
            },
            "window.dialog-window.alert .body-scrolled-window > viewport": {
                "border-top-left-radius": "0",
                "border-top-right-radius": "0",
            },
        }
        self.assertEqual(
            {s for s in self.rules if s.startswith("window.messagedialog")},
            {
                "window.messagedialog .response-area > button",
                "window.messagedialog.csd:not(.solid-csd)",
            },
        )
        self.assertEqual(
            {s for s in self.rules if "dialog.alert" in s},
            {
                "dialog.alert .response-area > button",
                "dialog-host > dialog.alert sheet",
                "dialog-host > dialog.alert sheet .body-scrolled-window > viewport",
            },
        )
        self.assertEqual(
            {s for s in self.rules if "dialog-window" in s},
            {
                "window.dialog-window.alert.csd:not(.solid-csd)",
                "window.dialog-window.alert .body-scrolled-window > viewport",
            },
        )
        # The 2026-11-04 selection-surface record's two compound dialog-host
        # spellings joined this family scan, and the same-day disabled-view
        # record's two sheet spellings join them beside it.
        self.assertEqual(
            {s for s in self.rules if "dialog-host" in s},
            {
                "dialog-host > dialog.alert sheet",
                "dialog-host > dialog.alert sheet .body-scrolled-window > viewport",
                "dialog-host > dialog.view sheet:selected",
                "window.print:not(.ssd-frame) dialog-host > "
                "dialog.dialog-action-box sheet:selected",
                "dialog-host > dialog.view sheet:disabled",
                "window.print:not(.ssd-frame) dialog-host > "
                "dialog.dialog-action-box sheet:disabled",
            },
        )
        self.assertEqual(
            {
                s
                for s in self.rules
                if s.startswith("window.dialog.message.csd .dialog-action-area")
            },
            {
                "window.dialog.message.csd .dialog-action-area button",
                "window.dialog.message.csd .dialog-action-area button:first-child",
                "window.dialog.message.csd .dialog-action-area button:last-child",
                "window.dialog.message.csd .dialog-action-area > button",
            },
        )
        # The frame rule states the corner through the radius shorthand, so
        # the viewport longhand members match the frame's border-radius
        # value per corner against that shared zero instead of against a
        # longhand the frame rule never declares.
        for selector, rule in members.items():
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, rule)
                if "border-radius" in rule:
                    self.assert_matches_frame(selector, "border-radius")
                for prop in rule:
                    self.assertEqual(
                        self.rules[selector][prop],
                        self.rules["frame > border"]["border-radius"],
                    )
        for selector in members:
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("cursor-handle > contents"),
            )

    def test_selection_surface_corners(self):
        # The 2026-11-04 selection-surface comment block appends one
        # three-selector comma group after the landed spin-button axis
        # chains at the sheet tail; the sheet parser splits it into
        # per-selector keys. These three compound spellings are the
        # members of stock's selected-view comma arm that the landed
        # class-only .view:selected restatement, the icon-view group and
        # the row groups lose the specificity tie against, so stock's
        # 9px-rounded selected face paints them until this group restates
        # the zero the landed square-corner policy carries everywhere but
        # the radio circle. The 2026-11-04 palette half extends the same
        # group in place: each member's block carries the flat opaque
        # #CCCCFF selection fill above the zero radius, so stock's
        # accent-tinted quarter-accent mix — fed the shipped
        # accent_bg_color — no longer leaves 75% of the underlying view
        # field showing through, and the parse union keeps both keys.
        members = {
            "window.print:not(.ssd-frame) .dialog-action-box:selected": {
                "background-color": "#CCCCFF",
                "border-radius": "0",
            },
            "dialog-host > dialog.view sheet:selected": {
                "background-color": "#CCCCFF",
                "border-radius": "0",
            },
            "window.print:not(.ssd-frame) dialog-host > "
            "dialog.dialog-action-box sheet:selected": {
                "background-color": "#CCCCFF",
                "border-radius": "0",
            },
        }
        # The token sweeps key on substrings no landed selector carries:
        # both sheet spellings alone carry "sheet:selected", and the print
        # action-box spelling alone carries "dialog-action-box:selected".
        self.assertEqual(
            {s for s in self.rules if "sheet:selected" in s},
            {
                "dialog-host > dialog.view sheet:selected",
                "window.print:not(.ssd-frame) dialog-host > "
                "dialog.dialog-action-box sheet:selected",
            },
        )
        self.assertEqual(
            {s for s in self.rules if "dialog-action-box:selected" in s},
            {"window.print:not(.ssd-frame) .dialog-action-box:selected"},
        )
        for selector, rule in members.items():
            with self.subTest(selector=selector):
                self.assert_exact_rule_once(selector, rule)
                self.assert_matches_frame(selector, "border-radius")
                # The landed frame pair declares no background-color, so
                # the fill anchors to the pinned SELECTION constant the
                # landed .view, row and icon-view selection tests use.
                self.assertEqual(rule["background-color"], SELECTION)
        for selector in members:
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index(
                    "spinbutton.vertical > button.image-button.down"
                    ":not(.flat):not(.raised):not(.suggested-action)"
                    ":not(.destructive-action):not(.opaque):first-child"
                ),
            )

    def test_expander_widget_title_corners(self):
        # The 2026-11-04 expander-title comment block appends one group
        # after the landed alert-dialog groups at the sheet tail; stock's
        # two radius arms (integration 6px, toolkit 5px) share one selector
        # string, so one byte-equal restatement squares both.
        self.assertEqual(
            {s for s in self.rules if s.startswith("expander-widget > box > title")},
            {"expander-widget > box > title"},
        )
        self.assertEqual(
            {s for s in self.rules if "expander-widget" in s},
            {
                "expander-widget > box > title",
                "expander-widget:focus:focus-visible > box > title",
            },
        )
        self.assertEqual(self.selectors.count("expander-widget > box > title"), 1)
        self.assert_square_corner("expander-widget > box > title")
        self.assertGreater(
            self.selectors.index("expander-widget > box > title"),
            self.selectors.index("cursor-handle > contents"),
        )

    def test_sheet_widget_corners(self):
        # The 2026-11-04 sheet-widget comment block appends three groups
        # after the landed expander-title tail group; stock's three radius
        # arms share these six selector strings across the two sheet
        # widget families, so byte-equal restatements square them all while
        # stock's transitions, shadows, outline, fill, min sizes and
        # margins stay inherited per-property.
        bottom_sheet = {
            "bottom-sheet > sheet",
            "bottom-sheet > sheet > outline",
            "bottom-sheet > sheet > stack > widget",
            "bottom-sheet > sheet > stack > button",
            "bottom-sheet > sheet > stack > button > widget",
            "bottom-sheet > sheet > stack > widget > drag-handle",
        }
        self.assertEqual(
            {s for s in self.rules if s.startswith("bottom-sheet")},
            bottom_sheet,
        )
        self.assertEqual(
            {s for s in self.rules if s.startswith("floating-sheet")},
            {"floating-sheet > sheet"},
        )
        for selector in bottom_sheet | {"floating-sheet > sheet"}:
            self.assertEqual(self.selectors.count(selector), 1)
        for selector in (
            "bottom-sheet > sheet",
            "bottom-sheet > sheet > outline",
            "bottom-sheet > sheet > stack > widget",
            "bottom-sheet > sheet > stack > button",
            "bottom-sheet > sheet > stack > button > widget",
        ):
            with self.subTest(selector=selector):
                self.assertEqual(
                    self.rules[selector],
                    {
                        "border-top-left-radius": "0",
                        "border-top-right-radius": "0",
                    },
                )
                # The frame rule states the corner through the radius
                # shorthand, so each longhand member matches the frame's
                # shared zero instead of a longhand the frame rule never
                # declares.
                for corner in (
                    "border-top-left-radius",
                    "border-top-right-radius",
                ):
                    self.assertEqual(
                        self.rules[selector][corner],
                        self.rules["frame > border"]["border-radius"],
                    )
        for selector in (
            "bottom-sheet > sheet > stack > widget > drag-handle",
            "floating-sheet > sheet",
        ):
            with self.subTest(selector=selector):
                self.assert_square_corner(selector)
        for selector in sorted(bottom_sheet | {"floating-sheet > sheet"}):
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("expander-widget > box > title"),
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

    def test_menubar_titles(self):
        self.assert_menubar_titles("menubar > item")
        self.assert_rule(
            "menubar > item:selected", {"background-color": SELECTION}
        )

    def test_menu_selection_corners(self):
        # The 2026-11-04 menu-selection corner row squares the landed
        # menubar item beside its padding pin and adds the two stock
        # twins at the modelbutton-to-tooltip seam.
        self.assert_rule("menubar > item", {"border-radius": "0"})
        self.assertEqual(self.selectors.count("menubar > item"), 1)
        rows = {"popover.menu list > row", "popover.menu listview > row"}
        nested = "menubar > item popover.menu popover.menu > contents"
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if "popover.menu list > row" in selector
                or "popover.menu listview > row" in selector
            },
            rows,
        )
        for selector in rows | {nested}:
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assert_rule(selector, {"border-radius": "0"})
                self.assert_square_corner(selector)
        for selector in sorted(rows | {nested}):
            self.assertGreater(
                self.selectors.index(selector),
                self.selectors.index("modelbutton.flat:disabled"),
            )
            self.assertLess(
                self.selectors.index(selector),
                self.selectors.index("tooltip"),
            )
        self.assertGreater(
            self.selectors.index("menubar > item"),
            self.selectors.index(".toolbar"),
        )

    def test_linked_members_strip_their_trailing_border(self):
        for css_class, side in ((".linked:not(.vertical)", "border-right-style"),
                                (".linked.vertical", "border-bottom-style")):
            for member in ("button", "entry", "spinbutton:not(.vertical)",
                           "dropdown > button", "menubutton > button",
                           "colorbutton > button", "fontbutton > button",
                           "tabbutton > button"):
                self.assert_rule(
                    f"{css_class} > {member}",
                    {side: "none"},
                )

    def test_linked_last_member_restores_the_border(self):
        for css_class, side in ((".linked:not(.vertical)", "border-right-style"),
                                (".linked.vertical", "border-bottom-style")):
            for member in ("button:last-child", "entry:last-child",
                           "spinbutton:not(.vertical):last-child",
                           "dropdown > button:last-child",
                           "menubutton > button:last-child",
                           "colorbutton > button:last-child",
                           "fontbutton > button:last-child",
                           "tabbutton > button:last-child"):
                self.assert_rule(
                    f"{css_class} > {member}",
                    {side: "solid"},
                )

    def test_linked_protection_keeps_the_path_bar_and_stack_switcher_outlines(self):
        self.assert_rule(
            "pathbar > scrolledwindow > viewport > box.linked >"
            " button:not(:last-child)",
            {
                "border-right-style": "solid",
                "border-bottom-style": "solid",
            },
        )
        self.assert_rule(
            "stackswitcher.linked > button:not(:last-child)",
            {
                "border-right-style": "solid",
                "border-bottom-style": "solid",
            },
        )
        self.assert_rule(
            "pathbar > scrolledwindow > viewport > box > button",
            {
                "border": f"1px solid {BLACK}",
            },
        )


def _scrollbar_rules(css=CSS):
    """Return the parsed GTK 4 rules for the scrollbar breadth assertion.

    The sheet is contributor-supplied and ``parse_css`` echoes a malformed
    declaration in its diagnostic, so a checked-in symlink must be refused
    before its target is read.
    """
    _, rules, _ = parse_css(gtk_css.read_theme_text(css))
    return rules


class TestScrollbarBreadthRules(unittest.TestCase):
    """The GTK 4 thumb minimum must fill the reference's 16px scroll bar."""

    # The reference class below re-derives this band from the screenshot.
    CSS_PATH = CSS

    def test_thumb_minimum_fills_reference_band(self):
        rules = _scrollbar_rules(self.CSS_PATH)
        slider = rules["scrollbar > range > trough > slider"]
        trough = rules["scrollbar > range > trough"]
        band = 16
        # The 4 is the trough's and thumb's 1px borders on each side.
        self.assertEqual(slider["min-width"], f"{band - 4}px")
        self.assertEqual(slider["min-height"], f"{band - 4}px")
        self.assertEqual(slider["border"], f"1px solid {BLACK}")
        self.assertEqual(trough["border"], f"1px solid {BLACK}")

    def test_scrollbar_rules_refuse_a_symlink_escape(self):
        """A checked-in symlink must not echo a private file's text."""
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "gtk.css", "x{PRIVATE-SECRET}\n"
            )
            self.CSS_PATH = link
            try:
                with (
                    mock.patch.object(gtk_css, "ROOT", root),
                    self.assertRaisesRegex(
                        ValueError, "symlink escape"
                    ) as caught,
                ):
                    # Run the rule test itself, so reverting its read to a
                    # raw read fails here and not only in the helper.
                    self.test_thumb_minimum_fills_reference_band()
            finally:
                self.CSS_PATH = CSS
        self.assertNotIn("PRIVATE-SECRET", str(caught.exception))


class TestScrollbarBreadthReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The reference scroll bar is 16px thick; the thumb must fill it."""

    REFERENCE = SETUP_REFERENCE
    MAX_ROWS = SETUP_MAX_ROWS

    def test_thumb_band_matches_reference(self):
        top, bottom = 462, 477
        x = 200
        for y in (top, bottom):
            with self.subTest(y=y):
                self.assertEqual(hex_colour(self.pixel(x, y)), BLACK)
        for y in range(top + 1, bottom):
            with self.subTest(y=y):
                self.assertEqual(hex_colour(self.pixel(x, y)), TROUGH)
        band = bottom - top + 1
        self.assertEqual(band, 16)
        _, rules, _ = parse_css(gtk_css.read_theme_text(CSS))
        slider = rules["scrollbar > range > trough > slider"]
        trough = rules["scrollbar > range > trough"]
        self.assertEqual(slider["border"], f"1px solid {BLACK}")
        self.assertEqual(trough["border"], f"1px solid {BLACK}")
        for selector in (
            "scrollbar.overlay-indicator.horizontal.hovering > range > trough > slider",
            "scrollbar.overlay-indicator.horizontal:not(.hovering) > range > trough > slider",
        ):
            self.assertEqual(rules[selector]["min-height"], f"{band - 4}px")
        for selector in (
            "scrollbar.overlay-indicator.vertical.hovering > range > trough > slider",
            "scrollbar.overlay-indicator.vertical:not(.hovering) > range > trough > slider",
        ):
            self.assertEqual(rules[selector]["min-width"], f"{band - 4}px")
        self.assertEqual(rules["calendar"]["color"], hex_colour(self.pixel(x, top)))

if __name__ == "__main__":
    unittest.main()
