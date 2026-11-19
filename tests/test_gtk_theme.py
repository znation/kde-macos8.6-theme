"""Validate the GTK 3 Platinum theme.

The theme is one ``index.theme`` descriptor and one standalone ``gtk.css``.
The palette is reference-grounded through ``support.platinum_palette``; no
reference screenshot shows a GTK widget, so most GTK geometry is this
theme's adaptation. This module holds the sheet-level invariants and the
windows and text roles; expander arrows, OSD overlays, views and menus,
color-chooser swatches, scrollbar band and controls live in their own
``test_gtk_theme_*.py`` suites. Calendar, notebook, infobar, assistant
 sidebar, auxiliary band, application notification, round-button corner and disabled-view declarations live in focused suites.
Secondary-label ink and opacity declarations live in
``test_gtk_theme_label_inks.py``.
"""

from __future__ import annotations

import configparser
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
    SCALE_THUMB,
    SHEET_PALETTE,
)
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    SELECTION,
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

    def test_rtl_spin_field_mirrors_the_etch(self):
        # No reference shows a GTK spin button; the existing field rule etches
        # with `inset 1px 1px #999999`, and GTK 3 does not mirror box-shadow
        # for text direction. Measured 2026-11-11 in a GTK 3 offscreen child:
        # in a horizontal RTL spin button the steppers cover that arm at the
        # left edge, so this mirror pins the arm to the field's exposed right
        # edge. The rendered pixels are the horizontal-seam
        # probe's subject in tests/test_gtk_theme_spinbutton.py.
        self.assert_rule(
            "spinbutton:dir(rtl):not(.vertical)",
            {"box-shadow": "inset -1px 1px #999999"},
        )
        self.assertEqual(self.selectors.count("spinbutton:dir(rtl):not(.vertical)"), 1)
        self.assert_rule_after(
            "spinbutton:dir(rtl):not(.vertical) {",
            "entry, spinbutton:not(.vertical) {",
        )

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

    def test_link_button_follows_the_button_state_rules(self):
        # button:link ties button:hover and :active on specificity, so only
        # coming later keeps the link button faceless while hovered or pressed.
        link = self.css.index("button:link, button:visited {")
        for rule in ("button {", "button:hover {", "button:active, button:checked {"):
            self.assertGreater(link, self.css.index("\n" + rule), rule)

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

