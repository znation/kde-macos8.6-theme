"""Validate the GTK 3 Platinum theme.

The theme is one ``index.theme`` descriptor and one standalone ``gtk.css``.
The palette is reference-grounded through ``support.platinum_palette``; no
reference screenshot shows a GTK widget, so most GTK geometry is this
theme's adaptation. This module holds the sheet-level invariants and the
windows, bands and text roles; the OSD overlays, views and menus,
color-chooser swatches, scrollbar band and controls live in their own
``test_gtk_theme_*.py`` suites.
"""

from __future__ import annotations

import configparser
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import gtk_css
from support.gtk_css import HEX, assert_svg_root_first
from support.colorscheme_fixtures import load_scheme
from support.gtk_rule_cases import GtkSharedControlCases
from support.gtk_theme_spec import (
    BASE_DEFINED_COLOURS,
    BUTTON_BEVEL,
    DISABLED_TEXT,
    ETCH_DARK,
    INVERTED_BUTTON_BEVEL,
    LINK,
    SCALE_THUMB,
    SHEET_PALETTE,
)
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    SELECTION,
    WHITE,
)
from support.repo_root import ROOT
from support.symlink_fixtures import symlinked_repo

DEFINED_COLOURS = {
    **BASE_DEFINED_COLOURS,
    "theme_unfocused_selected_bg_color": SELECTION,
    "theme_unfocused_selected_fg_color": BLACK,
}

THEME_ID = "org.macos8.desktop"
THEME_DIR = Path(ROOT) / "theme" / "gtk" / THEME_ID
INDEX = THEME_DIR / "index.theme"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"

# Every inline-link rule expands these roots over the base, hover and
# active states; the inline-link tests below all pin rules for that
# expansion via support.gtk_css.inline_link_state_selectors.
LINK_ROOTS = ("label:link", "label:visited", "label:link:visited")


class TestGtkTheme(GtkSharedControlCases, unittest.TestCase):
    CSS_PATH = CSS

    @classmethod
    def setUpClass(cls):
        cls.index_text = gtk_css.read_theme_text(INDEX)
        super().setUpClass()

    def assert_selected_link_rules(self, selectors, earlier=(), color=None):
        """Check selected-link declarations and precedence over earlier rules."""
        if color is None:
            rgb = load_scheme().get("Colors:Selection", "ForegroundNormal")
            color = "#" + "".join(f"{int(part):02X}" for part in rgb.split(","))
            self.assertEqual(color, "#000000")
        self.assert_rule_group(dict.fromkeys(selectors, {"color": color}))
        css = gtk_css.strip_comments(self.css)
        selected_rule = css.index(selectors[0] + ",")
        for rule in earlier:
            self.assertGreater(selected_rule, css.index(rule))




    def test_theme_read_refuses_a_symlink_escape(self):
        """A checked-in symlink must not feed a private file to a diagnostic."""
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "index.theme", "PRIVATE-LINE\n"
            )
            with mock.patch.object(gtk_css, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "symlink escape"):
                    gtk_css.read_theme_text(link)

    def test_svg_root_assertion_refuses_a_symlink_escape(self):
        """The root-first assertion must not echo a private file's text."""
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "checkmark.svg", "PRIVATE-SECRET\n"
            )
            with mock.patch.object(gtk_css, "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    assert_svg_root_first(self, link)
        self.assertIn(str(link), str(caught.exception))
        self.assertNotIn("PRIVATE-SECRET", str(caught.exception))

    def test_index_theme(self):
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str
        parser.read_string(self.index_text)

        entry = parser["Desktop Entry"]
        self.assertEqual(entry["Type"], "X-GNOME-Metatheme")
        self.assertEqual(entry["Name"], "Platinum")
        self.assertEqual(entry["Encoding"], "UTF-8")
        self.assertEqual(
            entry["Comment"],
            "Standalone Platinum controls for GTK 3 applications",
        )

        metatheme = parser["X-GNOME-Metatheme"]
        self.assertEqual(metatheme["Name"], "Platinum")
        self.assertEqual(metatheme["GtkTheme"], THEME_ID)

    def test_theme_colours(self):
        self.assertEqual(self.colours, DEFINED_COLOURS)

    def test_imports_nothing_and_does_not_mention_adwaita(self):
        self.assertNotIn("@import", self.css)
        self.assertNotIn("adwaita", self.css.lower())

    def test_only_palette_hex_literals(self):
        self.assertEqual(set(HEX.findall(self.css)), SHEET_PALETTE)

    def test_no_universal_selector(self):
        for selector in self.selectors:
            if selector != "tooltip *":
                self.assertNotIn("*", selector)

    def test_window_and_background(self):
        for selector in ("window", ".background"):
            self.assert_rule(
                selector,
                {"background-color": FACE, "color": BLACK},
            )

    def test_notebook_header(self):
        self.assert_rule(
            "notebook > header",
            {"background-color": FACE, "border": f"1px solid {BLACK}"},
        )

    def test_notebook_tab_close_button_arms(self):
        for selector in (
            "notebook > header tab button.flat",
            "notebook > header tab button.flat:backdrop",
        ):
            self.assert_rule(selector, {"color": BLACK})
        for selector in (
            "notebook > header tab button.flat:disabled",
            "notebook > header tab button.flat:backdrop:disabled",
        ):
            self.assert_rule(selector, {"color": DISABLED_TEXT["color"]})

    def test_notebook_tab_scroll_arrow_faces(self):
        """Pin the 2026-11-11 notebook overflow-arrow restatement."""
        # 2026-11-11: stock paints the notebook header's overflow arrows
        # with the flat-button family — transparent at rest, a toolkit
        # gradient plus a highlighted glyph on hover, 5px-rounded corners —
        # and no collected reference screenshot shows the arrows, so each
        # state arm below restates the existing plain `button.flat` family's
        # dictionary at the arrow's own exact stock spelling, later source
        # order winning the tie per-property.
        face = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
            "transition": "none",
        }
        hover = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
            "-gtk-icon-effect": "none",
            "transition": "none",
        }
        # The radius addition is the base twin's alone: in the hovered and
        # pressed states stock's own later re-square arm (line 912) already
        # squares the arrow, so the other twins carry the existing
        # `button.flat` dictionaries byte-equal.
        flat = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
            "transition": "none",
        }
        sunken = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        disabled = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        arrow = "notebook > header > tabs > arrow"
        self.assert_rule_group({
            arrow: face,
            f"{arrow}.flat": face,
            f"{arrow}:hover": hover,
            f"{arrow}.flat:hover": hover,
            f"{arrow}:hover:active": {"transition": "none"},
            f"{arrow}.flat:hover:active": {"transition": "none"},
            f"{arrow}:active": sunken,
            f"{arrow}:checked": sunken,
            f"{arrow}:backdrop": flat,
            f"{arrow}:backdrop:active": sunken,
            f"{arrow}:backdrop:checked": sunken,
            f"{arrow}:backdrop:disabled": disabled,
            f"{arrow}:backdrop:disabled:active": disabled,
            f"{arrow}:backdrop:disabled:checked": disabled,
            f"{arrow}:disabled": disabled,
            f"{arrow}:disabled:active": disabled,
            f"{arrow}:disabled:checked": disabled,
            f"{arrow}:hover:not(:active):not(:backdrop)": hover,
        })
        # Source order: the base arrow group files after the existing
        # plain `button.flat` family's tail group, so every arrow twin
        # decides the equal-specificity race against the stock arms.
        self.assert_rule_after(
            f"{arrow},\n{arrow}.flat {{",
            "button.flat:disabled:active, button.flat:disabled:checked {",
        )
        # The token sweep keys on a substring no other existing selector
        # carries: a dropped twin, a renamed spelling, a lost comma member
        # or a stray extra rule fails.
        self.assertEqual(
            {selector for selector in self.selectors if arrow in selector},
            {
                arrow,
                f"{arrow}.flat",
                f"{arrow}:hover",
                f"{arrow}.flat:hover",
                f"{arrow}:hover:active",
                f"{arrow}.flat:hover:active",
                f"{arrow}:active",
                f"{arrow}:checked",
                f"{arrow}:backdrop",
                f"{arrow}:backdrop:active",
                f"{arrow}:backdrop:checked",
                f"{arrow}:backdrop:disabled",
                f"{arrow}:backdrop:disabled:active",
                f"{arrow}:backdrop:disabled:checked",
                f"{arrow}:disabled",
                f"{arrow}:disabled:active",
                f"{arrow}:disabled:checked",
                f"{arrow}:hover:not(:active):not(:backdrop)",
            },
        )

    def test_notebook_tab_focus_outline(self):
        self.assert_dotted_focus_outline("notebook > header > tabs > tab:focus")

    def test_tree_header(self):
        self.assert_tree_header(("treeview.view header button",))

    def test_tooltip_descendant_text(self):
        selector = "tooltip *"
        self.assert_rule(selector, {
            "color": self.rules["tooltip"]["color"],
            "text-shadow": "none",
        })
        self.assertEqual(
            self.rules[selector]["text-shadow"],
            self.rules["treeview.view header button"]["text-shadow"],
        )

    def test_expander_arrows(self):
        self.assert_expander_arrows(
            ("treeview.view.expander", "expander title > arrow"),
            ("treeview.view.expander:checked", "expander title > arrow:checked"),
        )

    def test_rtl_collapsed_expander_arrows(self):
        selectors = (
            "treeview.view.expander:not(:checked):dir(rtl)",
            "expander title > arrow:not(:checked):dir(rtl)",
        )
        self.assertEqual(
            {selector: self.rules[selector] for selector in selectors},
            {selector: {"-gtk-icon-transform": "scaleX(-1)"} for selector in selectors},
        )
        for selector in selectors:
            self.assertEqual(self.selectors.count(selector), 1)
        self.assert_expander_arrows(
            ("treeview.view.expander", "expander title > arrow"),
            ("treeview.view.expander:checked", "expander title > arrow:checked"),
        )

    def test_rtl_spin_field_mirrors_the_etch(self):
        # No reference shows a GTK spin button; the existing field rule etches
        # with `inset 1px 1px #999999`, and GTK 3 does not mirror box-shadow
        # for text direction. Measured 2026-11-11 in a GTK 3 offscreen child:
        # in a horizontal RTL spin button the steppers cover that arm at the
        # left edge, so this mirror pins the arm to the field's exposed right
        # edge. The rendered pixels are the horizontal-seam
        # probe's subject in tests/test_gtk_theme_controls.py.
        self.assert_rule(
            "spinbutton:dir(rtl):not(.vertical)",
            {"box-shadow": "inset -1px 1px #999999"},
        )
        self.assertEqual(self.selectors.count("spinbutton:dir(rtl):not(.vertical)"), 1)
        self.assert_rule_after(
            "spinbutton:dir(rtl):not(.vertical) {",
            "entry, spinbutton:not(.vertical) {",
        )

    def test_expander_title_focus_outline(self):
        self.assert_dotted_focus_outline("expander > title:focus")

    def test_submenu_arrow(self):
        self.assert_submenu_arrow(("menu menuitem arrow",), sized=True)
        self.assert_submenu_arrow(("popover modelbutton arrow.right",), sized=False)

    def test_text_selection(self):
        self.assert_text_selection(
            ("entry selection", "spinbutton:not(.vertical) selection", "label selection", "textview text selection")
        )

    def test_selected_text_arms(self):
        black = (
            "label:selected", "textview text:selected", "textview text:selected:focus",
            ".view text:selected", ".view text:selected:focus",
            "textview text selection:focus", ".view text selection:focus",
            ".view text selection", "label:backdrop selection", "label:backdrop:selected",
            "entry selection:backdrop", "spinbutton:not(.vertical) selection:backdrop",
            "textview text:backdrop:selected", "textview text:backdrop:selected:focus",
            ".view text:backdrop:selected",
            "textview text selection:backdrop", "textview text selection:backdrop:focus",
            ".view text selection:backdrop",
        )
        disabled = (
            "label:disabled selection", "label:disabled:selected", "entry selection:disabled",
            "spinbutton:not(.vertical) selection:disabled", "textview text:disabled:selected",
            "textview text:disabled:selected:focus", ".view text:disabled:selected",
            "textview text selection:disabled", "textview text selection:disabled:focus",
            ".view text selection:disabled", "label:backdrop selection:disabled",
            "label:backdrop:disabled:selected", "entry selection:backdrop:disabled",
            "spinbutton:not(.vertical) selection:backdrop:disabled",
            "textview text:backdrop:disabled:selected", ".view text:backdrop:disabled:selected",
            "textview text selection:backdrop:disabled", ".view text selection:backdrop:disabled",
        )
        for selector in black:
            self.assert_rule(selector, {"color": BLACK})
        for selector in disabled:
            self.assert_rule(selector, {"color": DISABLED_TEXT["color"]})
        self.assertEqual(
            {selector for selector in self.rules if selector in set(black + disabled)},
            set(black + disabled),
        )

    def test_disabled_text(self):
        self.assert_disabled_text(("label:disabled", "entry:disabled", "spinbutton:disabled"))

    def test_disabled_view_face_and_ink(self):
        """Pin the restated disabled view field and ink stock-twins."""
        # 2026-11-11: an insensitive view's stock arms out-specify the existing
        # `.view, textview text, list` view-field group, so stock would wash
        # each member with the toolkit's warm near-white field and grey ink
        # without the restatements; see the dated block beside the rules.
        group_members = (
            ".view:disabled",
            "iconview:disabled",
            ".view text:disabled",
            "iconview text:disabled",
            "textview text:disabled",
        )
        expected = {**DISABLED_TEXT, "background-color": WHITE}
        for selector in group_members:
            with self.subTest(selector=selector):
                self.assert_rule(selector, expected)
                self.assertEqual(self.rules[selector], expected, selector)
                self.assertEqual(self.selectors.count(selector), 1, selector)
        for selector in ("treeview.view:disabled", "treeview.view:disabled:backdrop"):
            with self.subTest(selector=selector):
                self.assert_rule(selector, DISABLED_TEXT)
                self.assertEqual(self.rules[selector], {**DISABLED_TEXT}, selector)
                self.assertEqual(self.selectors.count(selector), 1, selector)
        # Token sweeps keyed on substrings no other existing selector carries,
        # so a stray state twin, a renamed spelling or a dropped member
        # fails; the treeview family sweep pins the existing disabled-selected
        # pair as the only other treeview disabled spellings.
        self.assertEqual(
            {s for s in self.rules if "iconview:disabled" in s},
            {"iconview:disabled"},
        )
        self.assertEqual(
            {s for s in self.rules if "iconview text:disabled" in s},
            {"iconview text:disabled"},
        )
        # The ".view:disabled" substring is also inside the four treeview
        # disabled spellings, so the sweep names the whole five-key family.
        self.assertEqual(
            {s for s in self.rules if ".view:disabled" in s},
            {
                ".view:disabled",
                "treeview.view:disabled",
                "treeview.view:disabled:backdrop",
                "treeview.view:disabled:selected",
                "treeview.view:disabled:selected:backdrop",
            },
        )
        self.assertEqual(
            {s for s in self.rules if ".view text:disabled" in s},
            {".view text:disabled", ".view text:disabled:selected"},
        )
        self.assertEqual(
            {s for s in self.rules if "textview text:disabled" in s},
            {
                "textview text:disabled",
                "textview text:disabled:selected",
                "textview text:disabled:selected:focus",
            },
        )
        self.assertEqual(
            {s for s in self.rules if "treeview.view:disabled" in s},
            {
                "treeview.view:disabled",
                "treeview.view:disabled:backdrop",
                "treeview.view:disabled:selected",
                "treeview.view:disabled:selected:backdrop",
            },
        )
        # The restatements sit after the existing disabled-selected groups in
        # the sheet, the source-order position the cascade tie needs. The
        # order pin runs on the comment-stripped sheet because the dated
        # comment quotes the comma group's own spelling.
        stripped = gtk_css.strip_comments(self.css)
        self.assertGreater(
            stripped.index(".view:disabled,"),
            stripped.index("label:backdrop selection:disabled,"),
            "the disabled view restatements do not follow the disabled-selected groups",
        )

    def test_separator_label_foreground(self):
        self.assert_separator_label_foreground()

    def test_dim_label_foreground(self):
        selector = ".dim-label"
        self.assert_disabled_text((selector,))
        self.assertEqual(
            self.rules[selector],
            {**DISABLED_TEXT, "opacity": "1", "text-shadow": "none"},
        )
        self.assertEqual(self.selectors.count(selector), 1)

    def test_menu_accelerator_foreground(self):
        selector = "menuitem accelerator"
        self.assert_disabled_text((selector,))
        self.assert_rule(selector, {**DISABLED_TEXT})
        # Stock dims the accelerator inside the color declaration alone, so
        # the restatement carries the opacity-free, shadow-free dict whole.
        self.assertEqual(self.rules[selector], {**DISABLED_TEXT})
        self.assertEqual(self.selectors.count(selector), 1)
        # The stock-twin spelling lands after the existing menu-row hover
        # face, the source position that beats the toolkit arm on the tie.
        self.assertGreater(
            self.selectors.index(selector),
            self.selectors.index("menu menuitem:hover"),
        )

    def test_header_subtitle_foreground(self):
        selectors = (".titlebar:not(headerbar) .subtitle", "headerbar .subtitle")
        self.assert_disabled_text(selectors)
        expected = {**DISABLED_TEXT, "opacity": "1", "text-shadow": "none"}
        self.assert_rule_group(dict.fromkeys(selectors, expected))

    def test_emoji_section_label_opacity(self):
        selectors = (
            "button.emoji-section label",
            "button.emoji-section:hover label",
        )
        self.assert_rule_group(dict.fromkeys(selectors, {"opacity": "1"}))
        self.assertEqual(
            {selector for selector in self.rules if "emoji-section" in selector},
            set(selectors),
        )

    def test_view_background(self):
        self.assert_view_background((".view", "textview text", "list"))

    def test_content_view_background(self):
        selectors = (".content-view", ".content-view:backdrop")
        self.assert_view_background(selectors)
        expected = {"background-color": "#FFFFFF", "color": "#000000"}
        for selector in selectors:
            self.assertEqual(self.rules[selector], expected)
            self.assertEqual(self.selectors.count(selector), 1)

    def test_content_view_hover(self):
        self.assert_rule(".content-view:hover", {"-gtk-icon-effect": "none"})

    def test_links(self):
        self.assert_links(
            ("button:link", "button:visited"),
            ("label:link", "button:link > label"),
            ("label:visited", "button:visited > label"),
            {"text-decoration-line": "underline"},
        )

    def test_disabled_inline_link_foregrounds(self):
        selectors = ("label:link:disabled", "label:visited:disabled")
        self.assert_disabled_text(selectors)
        for selector in selectors:
            self.assertEqual(self.rules[selector], {"color": "#888888"})
            self.assertEqual(self.selectors.count(selector), 1)
        uncommented = gtk_css.strip_comments(self.css)
        disabled_rule = uncommented.index(selectors[0] + ", " + selectors[1] + " {")
        self.assertGreater(disabled_rule, uncommented.index("label:link, button:link > label {"))
        self.assertGreater(disabled_rule, uncommented.index("label:visited, button:visited > label {"))

    def test_disabled_backdrop_inline_link_foregrounds(self):
        selectors = (
            "label:link:disabled:backdrop",
            "label:link:disabled:backdrop:hover",
            "label:link:disabled:backdrop:active",
            "label:visited:disabled:backdrop",
            "label:visited:disabled:backdrop:hover",
            "label:visited:disabled:backdrop:active",
        )
        self.assert_disabled_text(selectors)
        for selector in selectors:
            self.assertEqual(self.rules[selector], {"color": "#888888"})
            self.assertEqual(self.selectors.count(selector), 1)
        uncommented = gtk_css.strip_comments(self.css)
        rule = uncommented.index(selectors[0] + ",")
        self.assertGreater(rule, uncommented.index("label:link:disabled, label:visited:disabled {"))
        self.assertGreater(
            rule,
            uncommented.index("label > link:visited:hover:not(:disabled),"),
        )

    def test_inline_link_interaction_colours(self):
        # GTK 3 gtklabel.c creates child link nodes with either LINK or VISITED,
        # never both. Pin declarations for those actual node/state combinations.
        blue = (
            "label > link:link:hover:not(:disabled)",
            "label > link:link:active:not(:disabled)",
        )
        visited = (
            "label > link:visited:hover:not(:disabled)",
            "label > link:visited:active:not(:disabled)",
        )
        for selector in blue:
            self.assertEqual(self.rules[selector], {"color": "#0000EE"})
            self.assertEqual(self.selectors.count(selector), 1)
        for selector in visited:
            self.assertEqual(self.rules[selector], {"color": "#551A8B"})
            self.assertEqual(self.selectors.count(selector), 1)
        self.assert_scheme_link_colours()
        uncommented = gtk_css.strip_comments(self.css)
        self.assertLess(
            uncommented.index(blue[0] + ","),
            uncommented.index(visited[0] + ","),
        )

    def test_selected_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":selected:not(:disabled):not(:backdrop)"
        )
        self.assert_selected_link_rules(
            selectors,
            (
                "label:visited, button:visited > label {",
                "label > link:link:active:not(:disabled) {",
                "label > link:visited:active:not(:disabled) {",
                "label:link:visited:backdrop:active:not(:disabled) {",
            ),
        )

    def test_disabled_selected_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":selected:disabled:not(:backdrop)"
        )
        self.assert_disabled_text(selectors)
        self.assert_selected_link_rules(
            selectors,
            (
                "label:link:disabled, label:visited:disabled {",
                "label:link:selected:not(:disabled):not(:backdrop),",
            ),
            color="#888888",
        )

    def test_selected_ancestor_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":not(:disabled):not(:backdrop)", prefix=":selected "
        )
        self.assert_selected_link_rules(
            selectors,
            (
                "label:visited, button:visited > label {",
                "label > link:link:hover:not(:disabled),",
                "label > link:visited:hover:not(:disabled),",
                "label:link:selected:not(:disabled):not(:backdrop),",
            ),
        )

    def test_disabled_selected_ancestor_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":disabled:not(:backdrop)", prefix=":selected "
        )
        self.assert_disabled_text(selectors)
        self.assert_selected_link_rules(
            selectors,
            (
                "label:link:disabled, label:visited:disabled {",
                ":selected label:link:not(:disabled):not(:backdrop),",
            ),
            color="#888888",
        )

    def test_selected_backdrop_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":selected:backdrop:not(:disabled)"
        )
        self.assert_selected_link_rules(
            selectors,
            (
                "label:link:backdrop:not(:disabled),",
                "label:link:visited:backdrop:not(:disabled),",
                "label:link:selected:not(:disabled):not(:backdrop),",
            ),
        )

    def test_disabled_selected_backdrop_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":selected:disabled:backdrop"
        )
        self.assert_disabled_text(selectors)
        for selector in selectors:
            self.assertEqual(self.rules[selector], {"color": "#888888"})
            self.assertEqual(self.selectors.count(selector), 1)
        uncommented = gtk_css.strip_comments(self.css)
        rule = uncommented.index(selectors[0] + ",")
        self.assertGreater(rule, uncommented.index("label:link:disabled:backdrop,"))
        self.assertGreater(
            rule,
            uncommented.index("label:link:selected:backdrop:not(:disabled),"),
        )

    def test_selected_ancestor_backdrop_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":backdrop:not(:disabled)", prefix=":selected "
        )
        self.assert_selected_link_rules(
            selectors,
            (
                "label:link:backdrop:not(:disabled),",
                "label:link:visited:backdrop:not(:disabled),",
                "label > link:link:hover:not(:disabled),",
                "label > link:visited:hover:not(:disabled),",
                "label:link:selected:backdrop:not(:disabled),",
            ),
        )

    def test_disabled_selected_ancestor_backdrop_inline_link_foregrounds(self):
        selectors = gtk_css.inline_link_state_selectors(
            LINK_ROOTS, state=":disabled:backdrop", prefix=":selected "
        )
        self.assert_disabled_text(selectors)
        for selector in selectors:
            self.assertEqual(self.rules[selector], {"color": "#888888"})
            self.assertEqual(self.selectors.count(selector), 1)
        uncommented = gtk_css.strip_comments(self.css)
        rule = uncommented.index(selectors[0] + ",")
        self.assertGreater(
            rule,
            uncommented.index("label:link:disabled:backdrop,"),
        )
        self.assertGreater(
            rule,
            uncommented.index(":selected label:link:backdrop:not(:disabled),"),
        )

    def test_enabled_backdrop_inline_link_colours(self):
        blue = (
            "label:link:backdrop:not(:disabled)",
            "label:link:backdrop:hover:not(:disabled)",
            "label:link:backdrop:active:not(:disabled)",
        )
        visited = tuple(selector.replace("label:link:", "label:link:visited:") for selector in blue)
        for selectors, expected in ((blue, "#0000EE"), (visited, "#551A8B")):
            for selector in selectors:
                self.assertEqual(self.rules[selector], {"color": expected})
                self.assertEqual(self.selectors.count(selector), 1)
        self.assert_scheme_link_colours()
        uncommented = gtk_css.strip_comments(self.css)
        blue_rule = uncommented.index(blue[0] + ",")
        visited_rule = uncommented.index(visited[0] + ",")
        self.assertGreater(
            blue_rule,
            uncommented.index("label > link:visited:active:not(:disabled) {"),
        )
        self.assertLess(blue_rule, visited_rule)

    def test_disabled_link_button_labels(self):
        selectors = ("button:link:disabled > label", "button:visited:disabled > label")
        self.assert_disabled_text(selectors)
        uncommented = gtk_css.strip_comments(self.css)
        disabled_rule = uncommented.index(selectors[0] + ", " + selectors[1] + " {")
        self.assertGreater(disabled_rule, uncommented.index("button:link > label {"))
        self.assertGreater(disabled_rule, uncommented.index("button:visited > label {"))

    def test_disabled_child_link_button_labels(self):
        selectors = (
            "button:link > label:disabled",
            "button:visited > label:disabled",
            "button:link > label:disabled:backdrop",
            "button:visited > label:disabled:backdrop",
        )
        self.assert_disabled_text(selectors)
        for selector in selectors:
            self.assertEqual(self.rules[selector], DISABLED_TEXT)
            self.assertEqual(self.selectors.count(selector), 1)
        uncommented = gtk_css.strip_comments(self.css)
        disabled_child_rule = uncommented.index(selectors[0] + ",")
        self.assertGreater(disabled_child_rule, uncommented.index("button:link > label {"))
        self.assertGreater(disabled_child_rule, uncommented.index("button:visited > label {"))
        self.assertGreater(disabled_child_rule, uncommented.index(
            "button:link:disabled > label, button:visited:disabled > label {"
        ))
        self.assertGreater(disabled_child_rule, uncommented.index(
            "button:visited:not(:disabled) > label:active:not(:disabled) {"
        ))
        self.assertGreater(disabled_child_rule, uncommented.index(
            "button:visited:not(:disabled) > label:backdrop:active:not(:disabled) {"
        ))

    def test_link_button_label_interaction_colours(self):
        blue = (
            "button:link:not(:disabled) > label:hover:not(:disabled)",
            "button:link:not(:disabled) > label:active:not(:disabled)",
        )
        visited = (
            "button:visited:not(:disabled) > label:hover:not(:disabled)",
            "button:visited:not(:disabled) > label:active:not(:disabled)",
        )
        for selectors, expected in ((blue, "#0000EE"), (visited, "#551A8B")):
            for selector in selectors:
                self.assertEqual(self.rules[selector], {"color": expected})
                self.assertEqual(self.selectors.count(selector), 1)
        self.assert_scheme_link_colours()
        uncommented = gtk_css.strip_comments(self.css)
        disabled = uncommented.index(
            "button:link:disabled > label, button:visited:disabled > label {"
        )
        blue_rule = uncommented.index(blue[0] + ",")
        visited_rule = uncommented.index(visited[0] + ",")
        self.assertGreater(blue_rule, disabled)
        self.assertGreater(visited_rule, blue_rule)

    def test_enabled_backdrop_link_button_label_colours(self):
        blue = (
            "button:link:not(:disabled) > label:backdrop:not(:disabled)",
            "button:link:not(:disabled) > label:backdrop:hover:not(:disabled)",
            "button:link:not(:disabled) > label:backdrop:active:not(:disabled)",
        )
        visited = tuple(selector.replace("button:link:", "button:visited:") for selector in blue)
        for selectors, expected in ((blue, "#0000EE"), (visited, "#551A8B")):
            for selector in selectors:
                self.assertEqual(self.rules[selector], {"color": expected})
                self.assertEqual(self.selectors.count(selector), 1)
        self.assert_scheme_link_colours()
        uncommented = gtk_css.strip_comments(self.css)
        blue_rule = uncommented.index(blue[0] + ",")
        visited_rule = uncommented.index(visited[0] + ",")
        self.assertGreater(blue_rule, uncommented.index("button:visited > label {"))
        self.assertGreater(blue_rule, uncommented.index(
            "button:link:disabled > label, button:visited:disabled > label {"
        ))
        self.assertLess(blue_rule, visited_rule)

    def test_disabled_text_follows_the_entry_text_rule(self):
        # spinbutton:disabled ties spinbutton:not(.vertical) on specificity, so
        # only coming later greys a disabled spin button's text.
        self.assert_rule_after(
            "label:disabled, entry:disabled, spinbutton:disabled {",
            "entry, spinbutton:not(.vertical) {",
        )

    def test_button_text_and_icon_shadows(self):
        # button and button:hover append at the sheet tail, so the plain
        # enabled arms carry no stock label or icon emboss and the hovered
        # arm keeps no stock icon highlight; -gtk-icon-effect stays out of
        # the shared group so stock's *:disabled dim keeps greyed icons.
        self.assert_rule(
            "button",
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": BUTTON_BEVEL,
                "text-shadow": "none",
                "-gtk-icon-shadow": "none",
            },
        )
        self.assert_rule(
            "button:hover",
            {
                "background-color": FACE,
                "text-shadow": "none",
                "-gtk-icon-shadow": "none",
                "-gtk-icon-effect": "none",
            },
        )
        self.assertNotIn("-gtk-icon-effect", self.rules["button"])

    def test_sidebar_button_image_opacity(self):
        self.assert_rule_group(
            {
                "button.sidebar-button:not(:hover):not(:active) > image": {
                    "opacity": "1"
                },
                "button.sidebar-button:backdrop > image": {"opacity": "1"},
            }
        )

    def test_round_button_face_corners(self):
        # The five class-qualified stock arms sit later in source order than
        # the existing unclassed `button`, window-control and `scrollbar button`
        # restatements, so the exact stock twins appended at the sheet tail
        # win every radius tie: square faces, and for the two arms stock
        # rounds with an equal outline radius, square keyboard focus rings.
        self.assert_rule_group(
            {
                "button.circular": {
                    "border-radius": "0",
                    "-gtk-outline-radius": "0",
                },
                # Joined 2026-11-08: the five byte-equal stock geometry
                # declarations (probe of the toolkit resource, libgtk-3
                # 3.24.49, arm at resource line 1687) joined the existing
                # corner record's bare sidebar-button rule to pin the
                # button's box geometry against upstream drift; the radius
                # pair is the existing pair.
                "button.sidebar-button": {
                    "border-radius": "0",
                    "-gtk-outline-radius": "0",
                    "min-height": "26px",
                    "min-width": "26px",
                    "margin-top": "3px",
                    "margin-bottom": "3px",
                    "padding": "0",
                },
                "button.titlebutton:not(.appmenu)": {"border-radius": "0"},
                "modelbutton.flat": {"border-radius": "0"},
                ".menuitem.button.flat": {"border-radius": "0"},
                "scrollbar.overlay-indicator:not(.dragging):not(.hovering) button": {
                    "border-radius": "0"
                },
            },
        )
        # A stray twin under one of the corner-bearing tokens would steal a
        # tie from the exact spellings above; the existing selected-row
        # sidebar-button arms are excluded because they begin with
        # `row:selected` and own colours only.
        for token, expected in (
            ("button.circular", {"button.circular"}),
            (
                "button.sidebar-button",
                {
                    "button.sidebar-button",
                    "button.sidebar-button:not(:hover):not(:active) > image",
                    "button.sidebar-button:backdrop > image",
                },
            ),
            ("modelbutton.flat", {"modelbutton.flat"}),
            ("menuitem.button.flat", {".menuitem.button.flat"}),
        ):
            sweep = {
                selector
                for selector in self.rules
                if token in selector and "row:selected" not in selector
            }
            self.assertEqual(sweep, expected, token)
        # Source order: after the existing plain `button` and `scrollbar button`
        # groups and at the sheet tail behind the backdrop link block.
        uncommented = gtk_css.strip_comments(self.css)
        circular = uncommented.index("button.circular {")
        for rule in ("button {", "scrollbar button {"):
            self.assertGreater(circular, uncommented.index("\n" + rule), rule)
        self.assertGreater(
            circular,
            uncommented.index(
                "label:link:visited:selected:disabled:backdrop:active {"
            ),
            "circular must follow the sheet-tail backdrop link block",
        )

    def test_link_button_follows_the_button_state_rules(self):
        # button:link ties button:hover and :active on specificity, so only
        # coming later keeps the link button faceless while hovered or pressed.
        link = self.css.index("button:link, button:visited {")
        for rule in ("button {", "button:hover {", "button:active, button:checked {"):
            self.assertGreater(link, self.css.index("\n" + rule), rule)

    def test_calendar(self):
        self.assert_calendar(("calendar:selected",), ("calendar:indeterminate",))

    def test_calendar_outer_border(self):
        self.assert_rule("calendar", {"border": f"1px solid {BLACK}"})
        for selector in ("frame > border", ".frame"):
            self.assertEqual(
                self.rules["calendar"]["border"],
                self.rules[selector]["border"],
            )

    def test_calendar_focus_outline(self):
        self.assert_dotted_focus_outline("calendar:focus")

    def test_calendar_state_arms(self):
        # No reference screenshot shows a GTK calendar header, navigation
        # button, day highlight or backdrop state, so the nine stock arms
        # rest on existing faces: ETCH_DARK for the header rule and day
        # highlights, BLACK for the navigation glyphs (the erase
        # precedents, with no hover motion) and the disabled grey, and the
        # existing button:backdrop keep-the-existing-face policy for the
        # backdrop window.
        expected = {
            "calendar.header": {"border-bottom-color": ETCH_DARK},
            "calendar.header:backdrop": {"border-bottom-color": ETCH_DARK},
            "calendar.button": {"color": BLACK},
            "calendar.button:hover": {"color": BLACK},
            "calendar.button:backdrop": {"color": BLACK},
            "calendar.button:disabled": {"color": DISABLED_TEXT["color"]},
            "calendar.highlight": {"color": ETCH_DARK},
            "calendar.highlight:backdrop": {"color": ETCH_DARK},
            "calendar:backdrop": {"color": BLACK, "border-color": BLACK},
        }
        for selector, rule in expected.items():
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], rule, selector)
        self.assertEqual(
            {s for s in self.rules if s.startswith("calendar")},
            {
                "calendar",
                "calendar:selected",
                "calendar:indeterminate",
                "calendar:focus",
                *expected,
            },
        )
        self.assert_rule_after(
            "calendar.header {",
            "calendar:focus {",
        )

    def test_infobar(self):
        self.assert_infobar(("infobar > revealer > box",))
        # No infobar-family rule names a message type; the ban's provenance
        # lives on the shared sweep helper.
        self.assert_infobar_message_type_ban()

    def test_infobar_button_family(self):
        """The bar's typed stock button, selection and link arms restated.

        gtk-contained.css's four typed infobar button families out-token
        the existing plain ``button`` rule inside an infobar, and the bar's
        ``selection`` and ``*:link`` arms out-token the existing selection
        and link records, so the sheet restates them with the untyped
        band-chain spellings: the existing surface-button face/pressed/
        insensitive/backdrop recipes (the existing ``.app-notification``
        and ``.osd`` button groups), the existing selection fill and the
        existing link ink. All twelve spellings embed the existing measured
        chain ``infobar > revealer > box`` and name no message type, so
        ``test_infobar``'s ban stays green uncited here.
        """
        face = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        pressed = {**face, "box-shadow": INVERTED_BUTTON_BEVEL}
        # The existing `.osd button:disabled` shape: no ``outline-color``,
        # the Inactive grey (DISABLED_TEXT) label ink.
        disabled = {
            **{k: v for k, v in face.items() if k != "outline-color"},
            "color": DISABLED_TEXT["color"],
        }
        expected = {
            "infobar > revealer > box button": face,
            "infobar > revealer > box button:hover": face,
            "infobar > revealer > box button:active": pressed,
            "infobar > revealer > box button:checked": pressed,
            "infobar > revealer > box button:disabled": disabled,
            "infobar > revealer > box button:disabled:backdrop": disabled,
            "infobar > revealer > box button:backdrop": face,
            "infobar > revealer > box button label": {"color": BLACK},
            "infobar > revealer > box button:backdrop label": {"color": BLACK},
            "infobar > revealer > box selection": {"background-color": SELECTION},
            "infobar > revealer > box label:link": {"color": LINK},
            "infobar > revealer > box button:link": {"color": LINK},
        }
        for selector, declarations in expected.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1, selector)
                self.assertEqual(self.rules[selector], declarations, selector)
        # The family sweep: the existing band rule plus exactly these
        # twelve restatements — no respelling escapes the family.
        self.assertEqual(
            {s for s in self.selectors if "infobar" in s},
            {"infobar > revealer > box", *expected},
        )
        # Source order: every group follows the existing band rule at the
        # sheet tail (after the marked-scale thumb blocks).
        sheet = gtk_css.strip_comments(self.css)
        band = sheet.index("\ninfobar > revealer > box {")
        for selector in expected:
            positions = []
            start = 0
            while True:
                found = sheet.find(f"\n{selector}", start)
                if found == -1:
                    break
                positions.append(found)
                start = found + 1
            self.assertTrue(positions, selector)
            for position in positions:
                self.assertGreater(position, band, selector)

    def test_assistant_sidebar_arms(self):
        # No reference screenshot shows a GTK assistant sidebar, so the
        # five stock sidebar arms rest on existing faces: WHITE for the
        # sidebar field, ETCH_DARK for the top edge (the existing etched
        # band edge the infobar reuses) and FACE for the active-step
        # label — a wizard's current page is not a selected row, so no
        # selection blue applies. Stock's own padding and csd shape stay
        # byte-equal, and the backdrop window keeps the existing face per
        # the existing button:backdrop keep-the-existing-face policy.
        expected = {
            "assistant .sidebar": {
                "background-color": WHITE,
                "border-top": "1px solid " + ETCH_DARK,
            },
            "assistant.csd .sidebar": {"border-top-style": "none"},
            "assistant .sidebar label": {"padding": "6px 12px"},
            "assistant .sidebar label.highlight": {"background-color": FACE},
        }
        for selector, rule in expected.items():
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], rule, selector)
        self.assertEqual(
            {s for s in self.rules if "assistant" in s}, set(expected)
        )
        self.assertNotIn("assistant .sidebar:backdrop", self.rules)
        self.assert_rule_after(
            "assistant .sidebar {",
            "infobar > revealer > box {",
        )

    def test_search_bar(self):
        self.assert_infobar(("searchbar > revealer > box",))

    def test_location_bar(self):
        self.assert_infobar((".location-bar",))
        self.assertEqual(self.selectors.count(".location-bar"), 1)
        self.assertEqual(
            {s for s in self.rules if "location-bar" in s},
            {".location-bar", ".location-bar:backdrop"},
        )
        self.assert_rule_after(
            "statusbar {",
            ".location-bar",
        )

    def test_action_bar(self):
        self.assert_infobar(("actionbar > revealer > box",))

    def test_status_bar(self):
        self.assert_infobar(("statusbar",))

    def test_status_bar_frame_border_is_flat(self):
        self.assert_rule(
            "statusbar > frame > border", {"border-style": "none", "box-shadow": "none"}
        )

    def test_band_backdrop_faces(self):
        # An unfocused window keeps the existing band face: the grouped
        # backdrop record spells each stock backdrop twin byte-equal and
        # wins every tie by later user-sheet source order.
        declarations = {
            "background-color": FACE,
            "border-bottom-color": ETCH_DARK,
            "box-shadow": f"inset 0 -1px {WHITE}",
            "transition": "none",
        }
        self.assert_rule_group(
            {
                "searchbar > revealer > box:backdrop": declarations,
                ".location-bar:backdrop": declarations,
                "actionbar > revealer > box:backdrop": declarations,
            }
        )
        self.assertEqual(
            {s for s in self.rules if s.startswith("searchbar") and ":backdrop" in s},
            {"searchbar > revealer > box:backdrop"},
        )
        self.assertEqual(
            {s for s in self.rules if s.startswith("actionbar") and ":backdrop" in s},
            {"actionbar > revealer > box:backdrop"},
        )
        # The existing inline-toolbar record keeps stock's own face in
        # focused and unfocused windows alike, so stock's grouped
        # `.inline-toolbar:backdrop` membership stays stock.
        self.assertNotIn(".inline-toolbar:backdrop", self.rules)
        self.assert_rule_after(
            "searchbar > revealer > box:backdrop",
            "searchbar > revealer > box,",
        )
        self.assert_rule_after(
            "statusbar {",
            "searchbar > revealer > box:backdrop",
        )

    def test_app_notification_band(self):
        roots = (
            ".app-notification",
            ".app-notification.frame",
            ".app-notification:backdrop",
            ".app-notification.frame:backdrop",
        )
        self.assert_infobar(roots)
        expected = {
            "background-color": FACE,
            "background-image": "none",
            "color": BLACK,
            "border": "0",
            "border-bottom": f"1px solid {ETCH_DARK}",
            "border-radius": "0",
            "box-shadow": f"inset 0 -1px {WHITE}",
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        for selector in roots:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)
                sheet = gtk_css.strip_comments(self.css)
                block = next(
                    body for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", sheet)
                    if selector in {arm.strip() for arm in selectors.split(",")}
                )
                self.assertLess(block.index("border: 0;"), block.index("border-bottom:"))
        self.assertEqual(
            {selector for selector in self.rules if ".app-notification" in selector},
            set(roots)
            | {
                ".app-notification > border",
                ".app-notification.frame > border",
                ".app-notification button",
                ".app-notification.frame button",
                ".app-notification button:hover",
                ".app-notification button:active",
                ".app-notification button:checked",
                ".app-notification button:disabled",
                ".app-notification button:backdrop",
                ".app-notification button.flat",
                ".app-notification button.flat:hover",
                ".app-notification button.flat:active",
                ".app-notification button.flat:checked",
                ".app-notification button.flat:disabled",
                ".app-notification button.flat:backdrop",
            },
        )

    def test_app_notification_frame_border(self):
        for selector in (".app-notification > border", ".app-notification.frame > border"):
            with self.subTest(selector=selector):
                self.assertEqual(
                    self.rules[selector], {"border-style": "none", "box-shadow": "none"}
                )

    def test_osd_button_states_follow_backdrop(self):
        # These pairs tie on specificity. When both states match, the
        # interactive state must win: checked/active keeps the inverted
        # bevel, and disabled keeps its grey label in an inactive window.
        for root in ("button.osd", ".app-notification button",
                     "popover.background.touch-selection button",
                     "popover.background.magnifier button", ".osd button"):
            for state in ("hover", "active", "checked", "disabled"):
                with self.subTest(root=root, state=state):
                    self.assertLess(
                        self.selectors.index(root + ":backdrop"),
                        self.selectors.index(root + ":" + state),
                    )

    def test_marked_scale_thumb_arms(self):
        """One-sided marked scales restated to the plain thumb recipe."""
        faces = {
            "scale.horizontal.marks-before:not(.marks-after) slider": {
                "min-width": "12px",
                "min-height": "16px",
            },
            "scale.horizontal.marks-after:not(.marks-before) slider": {
                "min-width": "12px",
                "min-height": "16px",
            },
            "scale.vertical.marks-before:not(.marks-after) slider": {
                "min-width": "16px",
                "min-height": "12px",
            },
            "scale.vertical.marks-after:not(.marks-before) slider": {
                "min-width": "16px",
                "min-height": "12px",
            },
        }
        expected = {}
        for base, minima in faces.items():
            raised = {**SCALE_THUMB, "margin": "-5px", **minima}
            greyed = {
                "background-color": FACE,
                "border": f"1px solid {GREY}",
                "box-shadow": "none",
                "margin": "-5px",
                **minima,
            }
            expected.update(
                {
                    base: raised,
                    f"{base}:hover": raised,
                    f"{base}:active": raised,
                    f"{base}:disabled": greyed,
                    f"{base}:backdrop": greyed,
                    f"{base}:backdrop:disabled": greyed,
                    base.replace(" slider", ".fine-tune slider"): {"margin": "-5px"},
                }
            )
        self.assert_rule_group(expected)
        self.assertEqual(
            {s for s in self.selectors if "marks-" in s}, set(expected)
        )


if __name__ == "__main__":
    unittest.main()

