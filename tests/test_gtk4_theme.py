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
    CSS, DEFINED_COLOURS, Gtk4SheetRuleCases,
)
from support.gtk_theme_spec import (
    BUTTON_BEVEL,
    CHECK,
    CHECK_GLYPH,
    DISABLED_TEXT,
    ENTRY_FIELD,
    ETCH_DARK,
    LINK,
    SHEET_PALETTE,
    INVERTED_BUTTON_BEVEL,
    MIXED_GLYPH,
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

    def test_tile_check_faces(self):
        """Pin the eight 32px content-view tile-check state faces.

        The 2026-11-05 sheet-tail record restates the toolkit resource's
        eight class-armed comma triples (probed verbatim in the sheet
        comment and docs/invariants.md) with the existing check face under
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
        # Provenance guards: the existing `.content-view` field and hover
        # arms, the existing element `check`/`radio` recipes, the four merged
        # checked and indeterminate glyph unions the plain-state record
        # pins and the merged zero-radius `check` key stay byte-equal, so
        # the tile record added no declaration to any existing key.
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

    def test_link_button_follows_the_button_state_rules(self):
        # button.link ties button:hover and :active on specificity, so only
        # coming later keeps the link button faceless while hovered or pressed.
        link = self.css.index("button.link {")
        for rule in ("button {", "button:hover {", "button:active, button:checked {"):
            self.assertGreater(link, self.css.index("\n" + rule), rule)

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

    def test_suggested_action_plain_arms(self):
        self.assert_plain_action_arms("button.suggested-action")

    def test_destructive_action_plain_arms(self):
        self.assert_plain_action_arms("button.destructive-action")

    def test_action_class_flat_arms(self):
        # No reference screenshot shows a GTK flat action button; the tail
        # arms restate the existing push-button recipe over the stock
        # transparent colour-class flat family, so every checked
        # relationship below anchors the existing face constants and the two
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
        # restate the existing plain push-button recipe over the stock
        # transparent flat family, so every checked relationship below
        # anchors the existing face constants and the family inventory keeps
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

    def test_infobar(self):
        self.assert_infobar(("infobar > revealer > box",))
        # No infobar-family rule names a message type; the ban's provenance
        # lives on the shared sweep helper.
        self.assert_infobar_message_type_ban()

    # The 2026-11-09 face extension gives the corner pair the whole existing
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
        # 2026-11-09 face extension paints the existing `button.flat` recipe
        # on them. The existing window-controls close pair is the sibling
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
        # close class carries except the typed-band twins (the existing
        # message-type ban needs no type token) and the `:drop(active)`
        # ring (nothing existing governs a button drop arm). The four
        # raised-hover recipe faces share the existing `button.flat:hover`
        # recipe minus its radius declaration (the corner pair keeps the
        # radius ownership alone), with the stock ink claim re-pinned
        # black; the pressed and checked faces share the existing inverted
        # bevel; the disabled face keeps the existing `button:disabled`
        # shape and clears the stock dim filter under the existing
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
        # an infobar or a search bar is exactly the existing corner pair, the
        # existing searchbar close focus spelling and this family.
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
        # The existing message-type ban already reads every infobar carrier
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
        # An unfocused window keeps the existing band face: the
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

    def test_spin_button_field(self):
        self.assert_spin_button_field(
            ("spinbutton:not(.vertical)", "spinbutton.vertical > text")
        )

    def test_flat_entry_fields(self):
        # The existing entry recipe governs the stock flat entry family: the
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
        # exclusion, not a flat field); the existing OSD stepper record adds
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
        # RTL spin field kept the existing etch's horizontal top arm only: the
        # existing :dir(rtl) stepper arms cover the etch's vertical arm at the
        # field's left edge, leaving the exposed right edge half-etched
        # where the LTR field shows the full L (measured 2026-11-11 in a
        # child render before the fix). The sheet mirrors the arm onto the
        # exposed edge — the existing GTK 3 spinbutton:dir(rtl) record — with
        # one plain mirror directly after the plain field rule and one twin
        # directly after each of the three existing `.osd` state groups, each
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
        # Token sweeps keyed on substrings no other existing selector
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
        # The existing entry recipe never names the `caps-lock-indicator`
        # image child GTK stacks inside a password entry, so the two toolkit
        # tiers paint their own look on it even though the existing `entry >
        # image` family reaches the node: each stock arm carries the extra
        # `password` classes that out-specify the existing element pair, so
        # the toolkit's tint and the base tier's 30% dim stay in force.
        # The sheet tail restates both stock arms byte-equal: the
        # indicator takes the existing field's black ink (the family's own
        # pinned source) at the existing button:hover erase precedent's full
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
        # existing `entry > image` merge keys: the colour rule's existing
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
        # detached sheet head: the colour arm sits after the existing
        # margin twin that ends the family and its own comment group.
        self.assertGreater(
            self.selectors.index(
                "spinbutton.vertical > text.password image.caps-lock-indicator"
            ),
            self.selectors.index("spinbutton > image.right"),
        )

    def test_editable_label_cells(self):
        # The existing entry recipe governs the stock editable-label family:
        # the sheet restates the stock field arm and the four column-view
        # cell-editing arms with byte-equal twins declaring ENTRY_FIELD, the
        # existing focus-black outline and TEXT_SELECTION, so an editable
        # label and a column view's cell being edited paint the raised
        # field, the black focus ring and the existing selection fill instead
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
        # No other editablelabel spelling exists beyond the existing selection
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
        # The restatements sit between the existing selected-text groups and
        # the existing calendar disabled-selected day group: source order is
        # part of what lets the restatements govern the cell arms, which
        # outrank the existing editable-label selection twins by specificity.
        existing_tail = self.selectors.index(
            "editablelabel > stack > text > selection:focus-within"
        )
        calendar = self.selectors.index(
            "calendar > grid > label.day-number:disabled:selected"
        )
        for selector in (field, *focus, *selection):
            self.assertGreater(self.selectors.index(selector), existing_tail)
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
        # The message dialog's title band repaints the existing headerbar.
        # The band restates the existing headerbar, .titlebar group plus its
        # headerbar-only 1px bottom border, the backdrop band restates the
        # existing headerbar:backdrop, .titlebar:backdrop group, and the
        # dialog body corners go square; tying through the existing groups'
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
        # The existing container record keeps its frame-equal radius; the
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
        so the existing generic button radius restate loses on it; the group
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
        # The existing band focus twins end with :focus:focus-visible, so
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
                # The group sits between the existing searchbar band focus
                # group and the residual focus group: after the existing
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
        """Both scrollbar-corner junction arms paint the existing trough band."""
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

    def test_headerbar_meter_faces(self):
        """A meter embedded in the title band keeps the existing faces.

        Stock's one headerbar-descended meter arm repaints troughs and
        scale fills inside a headerbar with the stock band face; the
        sheet restates the arm's spellings split by existing value so a
        headerbar progress bar or scale keeps the existing `#EEEEEE`
        trough face and the existing transparent fill and highlight
        faces under either loading reading. The whole-dict reads kill
        a stock band value, a dropped or added spelling, a merged
        single group carrying one value and any value drift; the
        occurrence sweep kills a stray twin or per-state split; the
        order pin fixes the block between the existing fill/highlight
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
        # existing pill record already squares them byte-for-byte.
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
        # substring: existing band focus and covered-button spellings name
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
        # radius-bearing stock widget faces no existing restatement reaches:
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
        # Family sweeps on the distinctive tokens no existing selector
        # carries; the shortcut shell settles for the whole-dict and
        # count-1 guard above because the token already names the existing
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
        # stock-comma groups after the existing cursor-handle tail group;
        # the sheet parser splits each comma group into per-selector keys,
        # nine in all (the legacy .dialog-action-area keys from the existing
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
        # three-selector comma group after the existing spin-button axis
        # chains at the sheet tail; the sheet parser splits it into
        # per-selector keys. These three compound spellings are the
        # members of stock's selected-view comma arm that the existing
        # class-only .view:selected restatement, the icon-view group and
        # the row groups lose the specificity tie against, so stock's
        # 9px-rounded selected face paints them until this group restates
        # the zero the existing square-corner policy carries everywhere but
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
        # The token sweeps key on substrings no existing selector carries:
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
                # The existing frame pair declares no background-color, so
                # the fill anchors to the pinned SELECTION constant the
                # existing .view, row and icon-view selection tests use.
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

    def test_sheet_widget_corners(self):
        # The 2026-11-04 sheet-widget comment block appends three groups
        # after the existing expander-title tail group; stock's three radius
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
