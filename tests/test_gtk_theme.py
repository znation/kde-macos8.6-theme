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
    LINK,
    VISITED_LINK,
)
from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    GREY,
    INACTIVE_OUTLINE,
    SELECTION,
    TOOLTIP_FACE,
    TROUGH,
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


class TestGtkTheme(GtkSharedControlCases, unittest.TestCase):
    CSS_PATH = CSS

    @classmethod
    def setUpClass(cls):
        cls.index_text = gtk_css.read_theme_text(INDEX)
        super().setUpClass()




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
        palette = {
            BLACK,
            WHITE,
            GREY,
            FACE,
            BUTTON_SHADOW,
            TROUGH,
            SELECTION,
            ETCH_DARK,
            LINK,
            VISITED_LINK,
            TOOLTIP_FACE,
            INACTIVE_OUTLINE,
        }
        self.assertEqual(set(HEX.findall(self.css)), palette)

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
            "textview text:backdrop:selected", ".view text:backdrop:selected",
            "textview text selection:backdrop", ".view text selection:backdrop",
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

    def test_separator_label_foreground(self):
        selector = "label.separator"
        self.assert_disabled_text((selector,))
        self.assertEqual(
            self.rules[selector],
            {**DISABLED_TEXT, "opacity": "1", "text-shadow": "none"},
        )
        self.assertEqual(self.selectors.count(selector), 1)

    def test_dim_label_foreground(self):
        selector = ".dim-label"
        self.assert_disabled_text((selector,))
        self.assertEqual(
            self.rules[selector],
            {**DISABLED_TEXT, "opacity": "1", "text-shadow": "none"},
        )
        self.assertEqual(self.selectors.count(selector), 1)

    def test_header_subtitle_foreground(self):
        selectors = (".titlebar:not(headerbar) .subtitle", "headerbar .subtitle")
        self.assert_disabled_text(selectors)
        expected = {**DISABLED_TEXT, "opacity": "1", "text-shadow": "none"}
        for selector in selectors:
            self.assertEqual(self.rules[selector], expected)
            self.assertEqual(self.selectors.count(selector), 1)

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
            uncommented.index("label:link:visited:hover:not(:disabled),"),
        )

    def test_inline_link_interaction_colours(self):
        blue = (
            "label:link:hover:not(:disabled)",
            "label:link:active:not(:disabled)",
        )
        visited = (
            "label:link:visited:hover:not(:disabled)",
            "label:link:visited:active:not(:disabled)",
        )
        for selector in blue:
            self.assertEqual(self.rules[selector], {"color": "#0000EE"})
            self.assertEqual(self.selectors.count(selector), 1)
        for selector in visited:
            self.assertEqual(self.rules[selector], {"color": "#551A8B"})
            self.assertEqual(self.selectors.count(selector), 1)
        scheme = load_scheme()
        for role, expected in (("ForegroundLink", "#0000EE"),
                               ("ForegroundVisited", "#551A8B")):
            rgb = scheme.get("Colors:Window", role)
            self.assertEqual(
                "#" + "".join(f"{int(part):02X}" for part in rgb.split(",")),
                expected,
            )
        uncommented = gtk_css.strip_comments(self.css)
        self.assertLess(
            uncommented.index(blue[0] + ","),
            uncommented.index(visited[0] + ","),
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
        scheme = load_scheme()
        for role, expected in (("ForegroundLink", "#0000EE"),
                               ("ForegroundVisited", "#551A8B")):
            rgb = scheme.get("Colors:Window", role)
            self.assertEqual(
                "#" + "".join(f"{int(part):02X}" for part in rgb.split(",")),
                expected,
            )
        uncommented = gtk_css.strip_comments(self.css)
        blue_rule = uncommented.index(blue[0] + ",")
        visited_rule = uncommented.index(visited[0] + ",")
        self.assertGreater(
            blue_rule,
            uncommented.index("label:link:visited:active:not(:disabled) {"),
        )
        self.assertLess(blue_rule, visited_rule)

    def test_disabled_link_button_labels(self):
        selectors = ("button:link:disabled > label", "button:visited:disabled > label")
        self.assert_disabled_text(selectors)
        uncommented = gtk_css.strip_comments(self.css)
        disabled_rule = uncommented.index(selectors[0] + ", " + selectors[1] + " {")
        self.assertGreater(disabled_rule, uncommented.index("button:link > label {"))
        self.assertGreater(disabled_rule, uncommented.index("button:visited > label {"))

    def test_disabled_text_follows_the_entry_text_rule(self):
        # spinbutton:disabled ties spinbutton:not(.vertical) on specificity, so
        # only coming later greys a disabled spin button's text.
        self.assertGreater(
            self.css.index("label:disabled, entry:disabled, spinbutton:disabled {"),
            self.css.index("entry, spinbutton:not(.vertical) {"),
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

    def test_infobar(self):
        self.assert_infobar(("infobar > revealer > box",))
        for message_type in (".info", ".question", ".warning", ".error"):
            self.assertNotIn(message_type, self.css, message_type)

    def test_search_bar(self):
        self.assert_infobar(("searchbar > revealer > box",))

    def test_action_bar(self):
        self.assert_infobar(("actionbar > revealer > box",))

    def test_status_bar(self):
        self.assert_infobar(("statusbar",))

    def test_status_bar_frame_border_is_flat(self):
        self.assert_rule(
            "statusbar > frame > border", {"border-style": "none", "box-shadow": "none"}
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


if __name__ == "__main__":
    unittest.main()

