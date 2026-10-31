"""Validate the standalone GTK 3 Platinum theme.

The theme is one ``index.theme`` descriptor and one standalone ``gtk.css``.
The palette is reference-grounded through ``support.platinum_palette``; no
reference screenshot shows a GTK widget, so most GTK geometry is this theme's
adaptation, while the scroll-bar stepper box copies the reference's own scroll
bar.
"""

from __future__ import annotations

import configparser
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import gtk_css
from support.desktoptheme_paths import SETUP_MAX_ROWS, SETUP_REFERENCE
from support.gtk_css import HEX, parse_css
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    BASE_DEFINED_COLOURS as DEFINED_COLOURS,
    BUTTON_BEVEL,
    CHECK,
    DISABLED_TEXT,
    ENTRY_FIELD,
    ENTRY_PROGRESS,
    ETCH_DARK,
    INVERTED_BUTTON_BEVEL,
    LINK,
    VISITED_LINK,
    MENU_CHECK,
    PROGRESSBAR_PROGRESS,
    PROGRESSBAR_TROUGH,
    RAISED_BEVEL,
    SCALE_EMPTY_FILL,
    SCALE_TROUGH,
    SCALE_THUMB,
    SCROLLBAR_STEPPER,
    SCROLLBAR_STEPPER_ACTIVE,
    SCROLLBAR_STEPPER_ARROWS,
    TAB_STATES,
    RADIO,
    TITLE_BUTTON_IMAGE,
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
    hex_colour,
)
from support.reference_image import ReferenceScreenshotMixin
from support.repo_root import ROOT
from support.svg_case import parse_svg
from support.symlink_fixtures import symlinked_repo
from svg_assertions import (
    assert_no_script_elements,
    assert_no_style_elements,
    assert_root_canvas,
    attribute_values,
    children_named,
    circle_geometry_and_fill,
)

THEME_ID = "org.macos8.desktop"
THEME_DIR = Path(ROOT) / "theme" / "gtk" / THEME_ID
INDEX = THEME_DIR / "index.theme"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"
CHECKMARK = THEME_DIR / "assets" / "checkmark.svg"
BULLET = THEME_DIR / "assets" / "bullet.svg"
CHECK_MIXED = THEME_DIR / "assets" / "check-mixed.svg"
ARROW_DOWN = THEME_DIR / "assets" / "arrow-down.svg"
ARROW_UP = THEME_DIR / "assets" / "arrow-up.svg"
ARROW_RIGHT = THEME_DIR / "assets" / "arrow-right.svg"
SUBMENU_ARROW_SVG = THEME_DIR / "assets" / "submenu-arrow.svg"
ICON_GO_NEXT = (
    Path(ROOT)
    / "theme"
    / "icons"
    / THEME_ID
    / "16x16"
    / "actions"
    / "go-next-symbolic.svg"
)

MENU_SCROLL_UP = ("menu > arrow.top", ".menu > arrow.top", ".context-menu > arrow.top")
MENU_SCROLL_DOWN = (
    "menu > arrow.bottom",
    ".menu > arrow.bottom",
    ".context-menu > arrow.bottom",
)


def assert_svg_root_first(test, path):
    """Assert *path* puts its SVG root before any provenance comment.

    GTK loads a ``-gtk-icon-source`` SVG through gdk-pixbuf, whose sniffer
    only recognizes a file whose ``<svg`` root sits near the start; a comment
    before the root leaves the glyph blank. An XML declaration is optional
    and accepted, but the provenance comment belongs inside the root. The
    asset is contributor-supplied, and ``assertRegex`` echoes the text it was
    given when it fails, so the file is read through the shared guarded
    reader: a checked-in symlink that escapes the repository is refused
    before its private target's text reaches the diagnostic.
    """
    test.assertRegex(
        gtk_css.read_theme_text(path),
        r"^\s*(?:<\?xml[^>]*\?>\s*)?<svg\b",
    )


class TestGtkTheme(GtkSheetRuleCases, unittest.TestCase):
    def assert_osd_selector_count(self, expected, count):
        """Check the flattened selector inventory for an OSD rule family."""
        enumerated = {
            selector for _, selectors in expected for selector in selectors
        }
        self.assertEqual(len(enumerated), count, enumerated)
        return enumerated

    @classmethod
    def setUpClass(cls):
        cls.index_text = gtk_css.read_theme_text(INDEX)
        cls.css = gtk_css.read_theme_text(CSS)
        cls.colours, cls.rules, cls.selectors = parse_css(
            cls.css, source=str(CSS.relative_to(ROOT))
        )

    def assert_dotted_focus_outline(self, selector, anchor="button:focus"):
        """Assert *selector* carries the sheet's dotted focus outline.

        The GTK 3 sheet gives every focusable control the same
        ``1px dotted`` outline; thirteen ``:focus`` selectors copy
        ``button:focus`` (or a sibling rule passed as *anchor*), and each
        test below pins the literal declarations and the copy through this
        helper. The scale and button focus tests stay inline because each
        ties additional properties to other rules.
        """
        self.assert_rule(
            selector,
            {
                "outline": f"1px dotted {BLACK}",
                "outline-offset": "0",
                "-gtk-outline-radius": "0",
            },
        )
        for property_name in ("outline", "outline-offset", "-gtk-outline-radius"):
            self.assertEqual(
                self.rules[selector][property_name],
                self.rules[anchor][property_name],
            )

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
            ("entry selection", "spinbutton selection", "label selection", "textview text selection")
        )

    def test_disabled_text(self):
        self.assert_disabled_text(("label:disabled", "entry:disabled", "spinbutton:disabled"))

    def test_view_background(self):
        self.assert_view_background((".view", "textview text", "list"))

    def test_links(self):
        self.assert_links(
            ("button:link", "button:visited"),
            ("label:link", "button:link > label"),
            ("label:visited", "button:visited > label"),
            {"text-decoration-line": "underline"},
        )

    def test_disabled_text_follows_the_entry_text_rule(self):
        # spinbutton:disabled ties spinbutton:not(.vertical) on specificity, so
        # only coming later greys a disabled spin button's text.
        self.assertGreater(
            self.css.index("label:disabled, entry:disabled, spinbutton:disabled {"),
            self.css.index("entry, spinbutton:not(.vertical) {"),
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

    def test_osd_overlay_bands(self):
        selectors = (
            ".osd .scale-popup",
            ".csd popover.background.osd",
            "popover.background.osd",
            ".csd popover.background.touch-selection",
            ".csd popover.background.magnifier",
            "popover.background.touch-selection",
            "popover.background.magnifier",
            ".osd",
            ".osd .scale-popup:backdrop",
            "popover.background.osd:backdrop",
            "popover.background.touch-selection:backdrop",
            "popover.background.magnifier:backdrop",
            ".osd:backdrop",
            "toolbar.osd",
        )
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
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector != "colorchooser .popover.osd"
                and "button" not in selector
                and ((".osd" in selector
                    and ".osd check" not in selector
                    and ".osd entry" not in selector
                    and "fill" not in selector
                    and "highlight" not in selector
                    and "progress" not in selector
                    and ".osd radio" not in selector
                    and ".osd scale slider" not in selector
                    and ".osd spinbutton" not in selector
                    and "trough" not in selector)
                or "magnifier" in selector
                or "touch-selection" in selector
                or "scale-popup" in selector)
            },
            set(selectors),
        )

    def test_colorchooser_osd_popover_corners(self):
        self.assertEqual(
            self.rules["colorchooser .popover.osd"], {"border-radius": "0"}
        )
        self.assertEqual(
            self.rules["colorchooser .popover.osd"]["border-radius"],
            self.rules[".popover"]["border-radius"],
        )

    def test_osd_entry_fields(self):
        """Pin the four restated stock OSD field arms.

        No collected reference screenshot shows a field inside a GTK OSD
        overlay, so the sheet restates the toolkit resource's four grouped
        `.osd spinbutton:not(.vertical), .osd entry` arms with the landed
        entry recipe (``ENTRY_FIELD`` in ``support.gtk_theme_spec.py``) plus
        the stock arms' own shadow claims, cleared. The arm selectors,
        states and shadow claims come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49).
        """
        field = {
            **ENTRY_FIELD,
            "background-image": "none",
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        focus = {
            **field,
            "outline": f"1px dotted {BLACK}",
            "outline-offset": "0",
            "-gtk-outline-radius": "0",
        }
        disabled = {**field, "color": DISABLED_TEXT["color"]}
        expected = {
            ".osd spinbutton:not(.vertical)": field,
            ".osd entry": field,
            ".osd spinbutton:focus:not(.vertical)": focus,
            ".osd entry:focus": focus,
            ".osd spinbutton:backdrop:not(.vertical)": field,
            ".osd entry:backdrop": field,
            ".osd spinbutton:disabled:not(.vertical)": disabled,
            ".osd entry:disabled": disabled,
        }
        for selector, declarations in expected.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], declarations)
        for property_name in ("outline", "outline-offset", "-gtk-outline-radius"):
            self.assertEqual(
                self.rules[".osd entry:focus"][property_name],
                self.rules["entry:focus"][property_name],
            )
        self.assertEqual(
            self.rules[".osd entry:disabled"]["color"],
            self.rules["entry:disabled"]["color"],
        )
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if (".osd entry" in selector or ".osd spinbutton" in selector)
                and " button" not in selector
            },
            set(expected),
        )

    def test_osd_spinbutton_buttons(self):
        """Pin the twelve OSD spinbutton stepper arms to push-button faces."""
        base = {
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
        active = {**base, "box-shadow": INVERTED_BUTTON_BEVEL}
        disabled = {**base, "color": ETCH_DARK}
        del disabled["outline-color"]
        horizontal = lambda declarations: declarations
        vertical = lambda declarations: {
            **declarations, "background-clip": "border-box"
        }
        expected = {
            ".osd spinbutton:not(.vertical) button": horizontal(base),
            ".osd spinbutton:not(.vertical) button:dir(rtl)": horizontal(base),
            ".osd spinbutton:not(.vertical) button:hover": horizontal(base),
            ".osd spinbutton:not(.vertical) button:backdrop": horizontal(base),
            ".osd spinbutton:not(.vertical) button:disabled": horizontal(disabled),
            ".osd spinbutton:not(.vertical) button:dir(ltr):last-child": horizontal(base),
            ".osd spinbutton:not(.vertical) button:dir(rtl):first-child": horizontal(base),
            ".osd spinbutton.vertical button:first-child": vertical(base),
            ".osd spinbutton.vertical button:first-child:hover": vertical(base),
            ".osd spinbutton.vertical button:first-child:active": vertical(active),
            ".osd spinbutton.vertical button:first-child:disabled": vertical(disabled),
            ".osd spinbutton.vertical button:first-child:backdrop": vertical(base),
        }
        self.assertEqual(len(expected), 12)
        for selector, declarations in expected.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], declarations)
        self.assertEqual(
            {selector for selector in self.rules
             if "spinbutton" in selector and " button" in selector
             and any(token in selector for token in (
                 ".osd", "app-notification", "touch-selection", "magnifier"
             ))},
            set(expected),
        )

    def test_osd_flat_button(self):
        """Pin the 24 restated stock OSD flat-button arms.

        No collected reference screenshot shows a GTK OSD overlay or a
        flat button inside one, so the sheet restates the toolkit
        resource's grouped ``.app-notification button.flat, …, .osd
        button.flat`` arms with the landed plain push-button recipe (the
        base ``button`` dictionary ``test_osd_button`` pins):
        the raised ``#DDDDDD`` face with its 1px black border and zero
        radius, ``BUTTON_BEVEL``, and black labels; the ``:hover`` and
        ``:backdrop`` arms repeat the base recipe byte-equal; the active
        and checked arms swap only ``box-shadow`` to
        ``INVERTED_BUTTON_BEVEL``; the disabled arms keep
        ``BUTTON_BEVEL`` with the Inactive grey (``ETCH_DARK``) and no
        ``outline-color``, as the landed disabled arms also claim none.
        The arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); no
        restated arm sets on-disk geometry, so the stock
            ``button.osd`` minimums and the stock ``.osd .scale-popup
            button.flat`` pointer arm is restated by its dedicated test;
            the restated blocks
        keep the stock arm order, so the active/checked arm keeps
        stock's sheet-order win over the hover arm.
        """
        recipe = {
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
        active = {**recipe, "box-shadow": INVERTED_BUTTON_BEVEL}
        disabled = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": ETCH_DARK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        expected = [
            (recipe, (
                ".app-notification button.flat",
                "popover.background.touch-selection button.flat",
                "popover.background.magnifier button.flat",
                ".osd button.flat",
                ".app-notification button.flat:hover",
                "popover.background.touch-selection button.flat:hover",
                "popover.background.magnifier button.flat:hover",
                ".osd button.flat:hover",
                ".app-notification button.flat:backdrop",
                "popover.background.touch-selection button.flat:backdrop",
                "popover.background.magnifier button.flat:backdrop",
                ".osd button.flat:backdrop",
            )),
            (disabled, (
                ".app-notification button.flat:disabled",
                "popover.background.touch-selection button.flat:disabled",
                "popover.background.magnifier button.flat:disabled",
                ".osd button.flat:disabled",
            )),
            (active, (
                ".app-notification button.flat:active",
                "popover.background.touch-selection button.flat:active",
                "popover.background.magnifier button.flat:active",
                ".app-notification button.flat:checked",
                "popover.background.touch-selection button.flat:checked",
                "popover.background.magnifier button.flat:checked",
                ".osd button.flat:active",
                ".osd button.flat:checked",
            )),
        ]
        enumerated = self.assert_osd_selector_count(expected, 24)
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        self.assertEqual(
            # "button" and "flat" as bare tokens: the shipped sheet's only
            # button.flat spellings are these 24 restated arms plus the
            # dedicated scale-popup flat-button arm.
            {selector
             for selector in self.rules
             if "button" in selector and "flat" in selector},
            enumerated | {".osd .scale-popup button.flat"},
        )

    def test_scale_popup_buttons(self):
        """Clear the stock rounded scale-popup button overrides."""
        self.assertEqual(
            self.rules[".osd .scale-popup button.flat"],
            {"border-style": "solid", "border-radius": "0"},
        )
        self.assertEqual(
            self.rules[".scale-popup button:hover"],
            {"background-color": FACE, "border-radius": "0"},
        )
        self.assertEqual(
            {selector for selector in self.rules
             if "scale-popup" in selector and "button" in selector},
            {".osd .scale-popup button.flat", ".scale-popup button:hover"},
        )

    def test_osd_button(self):
        """Pin the 37 restated stock OSD push-button arms.

        No collected reference screenshot shows a GTK OSD overlay or a
        push button inside one, so the sheet restates the toolkit
        resource's stock ``button.osd`` and grouped ``.app-notification
        button, …, .osd button`` arms with the landed plain push-button
        recipe (the base ``button`` dictionary pinned by
        ``support.gtk_rule_cases.py::GtkSheetRuleCases::test_button``):
        the raised ``#DDDDDD`` face with its 1px black border and zero
        radius, ``BUTTON_BEVEL``, and black labels; the active and checked
        arms swap only ``box-shadow`` to ``INVERTED_BUTTON_BEVEL``; the
        disabled arms keep ``BUTTON_BEVEL`` with the Inactive grey
        (``ETCH_DARK``); ``outline-color: #000000`` replaces the stock
        rgba(238,238,236,0.3) only in the arms whose stock counterparts
        claim an outline colour. The arm selectors and states come from
        gtk-contained.css in /usr/lib/x86_64-linux-gnu/libgtk-3.so.0
        (libgtk-3 3.24.49); no restated arm sets on-disk geometry, so the
        stock ``button.osd`` minimums and the ``button.osd.image-button``
        minimum-width arm keep governing.
        """
        recipe = {
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
        active = {**recipe, "box-shadow": INVERTED_BUTTON_BEVEL}
        disabled = {
            "background-color": FACE,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": ETCH_DARK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        expected = [
            (recipe, (
                "button.osd",
                "button.osd:hover",
                "button.osd:backdrop",
                ".app-notification button",
                ".app-notification.frame button",
                ".csd popover.background.touch-selection button",
                ".csd popover.background.magnifier button",
                "popover.background.touch-selection button",
                "popover.background.magnifier button",
                ".osd button",
                ".app-notification button:hover",
                "popover.background.touch-selection button:hover",
                "popover.background.magnifier button:hover",
                ".osd button:hover",
                ".app-notification button:backdrop",
                "popover.background.touch-selection button:backdrop",
                "popover.background.magnifier button:backdrop",
                ".osd button:backdrop",
            )),
            (active, (
                "button.osd:active",
                "button.osd:checked",
                ".app-notification button:active",
                "popover.background.touch-selection button:active",
                "popover.background.magnifier button:active",
                ".app-notification button:checked",
                "popover.background.touch-selection button:checked",
                "popover.background.magnifier button:checked",
                ".osd button:active:backdrop",
                ".osd button:active",
                ".osd button:checked:backdrop",
                ".osd button:checked",
            )),
            (disabled, (
                "button.osd:disabled:backdrop",
                "button.osd:disabled",
                ".app-notification button:disabled",
                "popover.background.touch-selection button:disabled",
                "popover.background.magnifier button:disabled",
                ".osd button:disabled:backdrop",
                ".osd button:disabled",
            )),
        ]
        enumerated = self.assert_osd_selector_count(expected, 37)
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        osd_like = (".osd", "app-notification", "touch-selection",
                    "magnifier")
        self.assertEqual(
            {selector
             for selector in self.rules
             # "button" as a bare token: a spinbutton is a field, not a
             # button, so its node spelling never counts toward the scan;
             # a flat button node carries the flat-style arms, not the
             # plain ones, and is pinned by test_osd_flat_button; a
             # suggested-action or destructive-action button node
             # carries its own restated arms, also not the plain ones,
             # and is pinned by test_osd_suggested_action and
             # test_osd_destructive_action.
             if "button" in selector
             and "spinbutton" not in selector
             and "flat" not in selector
             and "suggested-action" not in selector
             and "destructive-action" not in selector
             and any(token in selector for token in osd_like)},
            enumerated,
        )

    def test_osd_suggested_action(self):
        """Pin the nine restated stock OSD suggested-action arms.

        No collected reference screenshot shows a GTK OSD overlay or a
        suggested-action button inside one, so the sheet restates the
        toolkit resource's ``.osd button.suggested-action`` arms with
        the landed plain push-button recipe (the base ``button``
        dictionary ``test_osd_button`` pins), with one clearance stock's
        own arms force: every one of the five stock arms claims
        ``background-clip: padding-box``, which left standing under the
        equal-specificity restatement would clip the restated face to
        the padding box, so every restated arm declares
        ``background-clip: border-box`` and the face paints exactly like
        the landed plain and flat restatements'. The restated arms are
        the raised ``#DDDDDD`` face with its 1px black border and zero
        radius, ``BUTTON_BEVEL``, and black labels; the ``:hover`` and
        ``:backdrop`` arms repeat the base recipe byte-equal, recipe
        ``outline-color`` included, as the landed plain and flat
        backdrop restatements do; the active and checked arms swap only
        ``box-shadow`` to ``INVERTED_BUTTON_BEVEL``; the disabled arms
        keep ``BUTTON_BEVEL`` with the Inactive grey (``ETCH_DARK``) and
        no ``outline-color``, as the landed disabled arms claim none.
        The arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); no
        restated arm sets on-disk geometry, so the stock ``button.osd``
        minimums and the ``button.osd.image-button`` minimum-width arm
        keep governing; the restated blocks keep the stock arm order, so
        the active/checked arm keeps stock's sheet-order win over the
        hover arm.
        """
        base = {
            "background-color": FACE,
            "background-image": "none",
            "background-clip": "border-box",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        active = {**base, "box-shadow": INVERTED_BUTTON_BEVEL}
        disabled = {**base, "color": ETCH_DARK}
        del disabled["outline-color"]
        expected = [
            (base, (
                ".osd button.suggested-action",
                ".osd button.suggested-action:hover",
                ".osd button.suggested-action:backdrop",
            )),
            (active, (
                ".osd button.suggested-action:active:backdrop",
                ".osd button.suggested-action:active",
                ".osd button.suggested-action:checked:backdrop",
                ".osd button.suggested-action:checked",
            )),
            (disabled, (
                ".osd button.suggested-action:disabled:backdrop",
                ".osd button.suggested-action:disabled",
            )),
        ]
        enumerated = self.assert_osd_selector_count(expected, 9)
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        self.assertEqual(
            # "button" and "suggested-action" as bare tokens: the shipped
            # sheet's only suggested-action spellings are these nine
            # restated arms; the generic suggested-action arms outside
            # .osd stay undeclared in the sheet, so the stock resource
            # keeps governing outside overlays.
            {selector
             for selector in self.rules
             if "button" in selector and "suggested-action" in selector},
            enumerated,
        )

    def test_osd_destructive_action(self):
        """Pin the nine restated stock OSD destructive-action arms.

        No collected reference screenshot shows a GTK OSD overlay or a
        destructive-action button inside one, so the sheet restates the
        toolkit resource's ``.osd button.destructive-action`` arms with
        the landed plain push-button recipe (the base ``button``
        dictionary ``test_osd_button`` pins), with one clearance stock's
        own arms force: every one of the five stock arms claims
        ``background-clip: padding-box``, which left standing under the
        equal-specificity restatement would clip the restated face to
        the padding box, so every restated arm declares
        ``background-clip: border-box`` and the face paints exactly like
        the landed plain, flat and suggested-action restatements'. The
        restated arms are the raised ``#DDDDDD`` face with its 1px black
        border and zero radius, ``BUTTON_BEVEL``, and black labels; the
        ``:hover`` and ``:backdrop`` arms repeat the base recipe
        byte-equal, recipe ``outline-color`` included, as the landed
        plain and suggested-action backdrop restatements do; the active
        and checked arms swap only ``box-shadow`` to
        ``INVERTED_BUTTON_BEVEL``; the disabled arms keep
        ``BUTTON_BEVEL`` with the Inactive grey (``ETCH_DARK``) and no
        ``outline-color``, as the landed disabled arms claim none. The
        arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); no
        restated arm sets on-disk geometry, so the stock ``button.osd``
        minimums and the ``button.osd.image-button`` minimum-width arm
        keep governing; the restated blocks keep the stock arm order, so
        the active/checked arm keeps stock's sheet-order win over the
        hover arm.
        """
        base = {
            "background-color": FACE,
            "background-image": "none",
            "background-clip": "border-box",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        active = {**base, "box-shadow": INVERTED_BUTTON_BEVEL}
        disabled = {**base, "color": ETCH_DARK}
        del disabled["outline-color"]
        expected = [
            (base, (
                ".osd button.destructive-action",
                ".osd button.destructive-action:hover",
                ".osd button.destructive-action:backdrop",
            )),
            (active, (
                ".osd button.destructive-action:active:backdrop",
                ".osd button.destructive-action:active",
                ".osd button.destructive-action:checked:backdrop",
                ".osd button.destructive-action:checked",
            )),
            (disabled, (
                ".osd button.destructive-action:disabled:backdrop",
                ".osd button.destructive-action:disabled",
            )),
        ]
        enumerated = self.assert_osd_selector_count(expected, 9)
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        self.assertEqual(
            # "button" and "destructive-action" as bare tokens: the
            # shipped sheet's only destructive-action spellings are these
            # nine restated arms; the generic destructive-action arms
            # outside .osd stay undeclared in the sheet, so the stock
            # resource keeps governing outside overlays.
            {selector
             for selector in self.rules
             if "button" in selector and "destructive-action" in selector},
            enumerated,
        )

    def test_osd_check_radio(self):
        """Pin the ten restated stock OSD indicator arms.

        No collected reference screenshot shows a check or radio inside a GTK
        OSD overlay, so the sheet restates the toolkit resource's five `.osd`
        indicator arms with the landed plain check and radio recipes (CHECK
        and RADIO in ``support.gtk_theme_spec.py``) plus two clearances the
        stock arms claim: the white-on-dark text and icon shadows, cleared,
        and a black focus-outline colour in place of the stock
        rgba(238,238,236,0.3). The arm selectors and states come from
        gtk-contained.css in /usr/lib/x86_64-linux-gnu/libgtk-3.so.0
        (libgtk-3 3.24.49); each arm is byte-for-byte the recipe in every
        state, because the armed spellings set no geometry, glyph source or
        checked spelling stock could override.
        """
        clearance = {
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        check = {**CHECK, **clearance}
        radio = {**RADIO, **clearance}
        states = ("", ":hover", ":active", ":backdrop", ":disabled")
        expected = {}
        for state in states:
            expected[f".osd check{state}"] = check
            expected[f".osd radio{state}"] = radio
        parsed = {}
        for selector in expected:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected[selector])
            parsed[selector] = self.rules[selector]
        self.assertEqual(
            [dict(parsed[f".osd check{state}"]) for state in states],
            [check] * 5,
        )
        self.assertEqual(
            [dict(parsed[f".osd radio{state}"]) for state in states],
            [radio] * 5,
        )
        self.assertEqual(
            {selector for selector in self.rules
             if ".osd check" in selector or ".osd radio" in selector},
            set(expected),
        )

    def test_osd_progress_scale(self):
        """Pin the nine restated stock OSD trough, fill and progress arms.

        No collected reference screenshot shows a meter inside a GTK OSD
        overlay, so the sheet restates the toolkit resource's six `.osd`
        trough/fill/progress groups with the landed plain progress-bar and
        scale recipes (``PROGRESSBAR_TROUGH``, ``PROGRESSBAR_PROGRESS``,
        ``SCALE_TROUGH`` and ``SCALE_EMPTY_FILL`` in
        ``support.gtk_theme_spec.py``): the flat ``#EEEEEE`` trough face with
        its black border, zero radius and ``inset 1px 1px #999999`` etch at
        the landed minimums, the transparent scale fill and highlight face,
        and the landed ``#CCCCFF`` progress fill. The disabled groups repeat
        the landed paints byte-for-byte, and the disabled progress fill is
        the landed grey (``GREY`` from ``support.platinum_palette``). The
        arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); the
        stock arms claim no geometry, glyph source or box-shadow, so the
        landed plain meter rules keep governing size and every state an arm
        does not restate.
        """
        trough = PROGRESSBAR_TROUGH
        scale_trough = SCALE_TROUGH
        fill = SCALE_EMPTY_FILL
        progress = PROGRESSBAR_PROGRESS
        disabled_progress = {**PROGRESSBAR_PROGRESS, "background-color": GREY}
        expected = [
            (trough, (
                ".osd progressbar trough",
                "progressbar .osd trough",
                ".osd progressbar trough:disabled",
                "progressbar .osd trough:disabled",
            )),
            (scale_trough, (
                ".osd scale trough",
                "scale .osd trough",
                ".osd scale trough:disabled",
                "scale .osd trough:disabled",
            )),
            (fill, (
                ".osd scale fill",
                "scale .osd fill",
                ".osd scale highlight",
                "scale .osd highlight",
                ".osd scale fill:disabled:backdrop",
                ".osd scale fill:disabled",
                "scale .osd fill:disabled",
                ".osd scale highlight:disabled",
                "scale .osd highlight:disabled",
            )),
            (progress, (
                ".osd progressbar progress",
                "progressbar .osd progress",
            )),
            (disabled_progress, (
                ".osd progressbar progress:disabled",
                "progressbar .osd progress:disabled",
            )),
        ]
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        self.assertEqual(
            self.rules[".osd progressbar progress:disabled"]["background-color"],
            self.rules["progressbar progress:disabled"]["background-color"],
        )
        self.assertEqual(
            self.rules["progressbar progress:disabled"]["background-color"],
            GREY,
        )
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if ".osd" in selector
                and (
                    "trough" in selector
                    or "fill" in selector
                    or "highlight" in selector
                    or "progress" in selector
                )
            },
            {selector
             for _, selectors in expected
             for selector in selectors}
            | {"progressbar.osd trough", "progressbar.osd progress"},
        )

    def test_osd_thin_bar(self):
        """Pin the two restated stock self-class ``.osd`` thin-bar arms.

        No collected reference screenshot shows a GTK OSD overlay, a meter
        inside one or a self-class ``.osd`` thin bar (a ``progressbar.osd``,
        the thin Epiphany-style headerbar indicator), so the sheet restates
        the toolkit resource's stock ``progressbar.osd trough`` and
        ``progressbar.osd progress`` arms with the landed plain progress-bar
        recipes (``PROGRESSBAR_TROUGH`` and ``PROGRESSBAR_PROGRESS`` in
        ``support.gtk_theme_spec.py``), the same reuse the landed GTK 4
        sheet's ``progressbar.osd > trough`` face makes (pinned by
        ``TestGtk4Theme::test_progressbar_osd_trough_paint``). The equal
        specificity restatements append after the toolkit resource, so they
        pre-empt exactly the stock arms they restate, and the landed
        ``.osd progressbar trough, progressbar .osd trough`` ancestor arms
        stay disjoint. The bare ``progressbar.osd`` node arm stays
        undeclared: its ``3px`` minimum is dominated by the trough's
        ``10px`` minimum and its transparent node background stays beneath
        the trough face. The arm selectors and stock claims come from
        gtk-contained.css in /usr/lib/x86_64-linux-gnu/libgtk-3.so.0
        (libgtk-3 3.24.49); no stock arm claims geometry, so the landed
        plain rules keep governing every state an arm does not restate.
        """
        with self.subTest(selector="progressbar.osd trough"):
            self.assertEqual(self.rules["progressbar.osd trough"],
                             PROGRESSBAR_TROUGH)
        with self.subTest(selector="progressbar.osd progress"):
            self.assertEqual(self.rules["progressbar.osd progress"],
                             PROGRESSBAR_PROGRESS)

    def test_osd_scale_slider(self):
        """Pin the six restated stock OSD scale thumb arms.

        No collected reference screenshot shows a scale thumb inside a GTK
        OSD overlay, so the sheet restates the toolkit resource's six
        ``.osd scale slider`` arms with the landed plain scale-thumb recipes
        (``SCALE_THUMB`` in ``support.gtk_theme_spec.py``) plus two
        clearances the stock arms claim: the white-on-dark text and icon
        shadows, cleared, and a black focus-outline colour in place of the
        stock rgba(238,238,236,0.3). Stock's background-clip stays omitted
        and the stateless arms carry the plain thumb's ``-5px`` margin. The
        arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); the
        plain ``scale slider`` rules keep governing size and every state an
        arm does not restate.
        """
        face = {
            **SCALE_THUMB,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        base = {**face, "margin": "-5px"}
        disabled = {
            "background-color": FACE,
            "border": f"1px solid {GREY}",
            "box-shadow": "none",
        }
        raised_states = ("", ":hover", ":active", ":backdrop")
        for state in raised_states:
            with self.subTest(state=state):
                self.assertEqual(
                    self.rules[f".osd scale slider{state}"],
                    base if state in ("", ":backdrop") else face,
                )
        for state in (":disabled", ":backdrop:disabled"):
            with self.subTest(state=state):
                self.assertEqual(
                    self.rules[f".osd scale slider{state}"], disabled
                )
        self.assertEqual(
            self.rules[".osd scale slider:disabled"],
            self.rules["scale slider:disabled"],
        )
        self.assertEqual(
            self.rules[".osd scale slider"],
            {
                **self.rules["scale slider"],
                "outline-color": BLACK,
                "text-shadow": "none",
                "-gtk-icon-shadow": "none",
            },
        )
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if ".osd scale slider" in selector
            },
            {
                f".osd scale slider{state}"
                for state in raised_states + (":disabled", ":backdrop:disabled")
            },
        )

    def test_path_bar_tabs(self):
        forms = {
            "base": (".path-bar > button",),
            "hover": (".path-bar > button:hover",),
            "checked": (".path-bar > button:checked",),
            "checked+hover": (".path-bar > button:checked:hover",),
        }
        for state, _selectors, checked in TAB_STATES:
            if state not in forms:
                continue
            expected = {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
            }
            if checked:
                expected["border-bottom-color"] = FACE
                expected["box-shadow"] = "none"
            else:
                expected["box-shadow"] = RAISED_BEVEL
            for selector in forms[state]:
                with self.subTest(state=state, selector=selector):
                    self.assert_rule(selector, expected)

    def test_row_selection_backdrop(self):
        super().test_row_selection_backdrop((
            "treeview.view:selected:backdrop",
            "list row.activatable:selected:backdrop",
        ))
        self.assertGreater(
            self.css.index("list row.activatable:selected:backdrop"),
            self.css.index("list row.activatable:selected:"),
        )

    def test_header_drop_indicator(self):
        targets = ("", "header.", "header ")
        states = (
            "button.dnd",
            "button.dnd:hover",
            "button.dnd:active",
            "button.dnd:selected",
        )
        selectors = [
            f"treeview.view {target}{state}"
            for target in targets
            for state in states
        ]
        self.assertEqual(len(selectors), 12, selectors)
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assert_rule(
                    selector,
                    {
                        "background-color": SELECTION,
                        "background-image": "none",
                        "color": BLACK,
                        "text-shadow": "none",
                        "box-shadow": "none",
                        "border-style": "none",
                        "border-radius": "0",
                    },
                )

    def test_header_drop_arm_carries_no_padding(self):
        self.assertNotIn(
            "padding", self.rules["treeview.view button.dnd"]
        )

    def test_no_dndtarget_node_declared(self):
        self.assertNotIn("dndtarget", self.css)

    def test_list_row_focus_outline(self):
        self.assert_dotted_focus_outline("list row:focus")

    def test_treeview_focus_outline(self):
        self.assert_dotted_focus_outline("treeview.view:focus")

    def test_iconview_focus_outline(self):
        self.assert_dotted_focus_outline("iconview:focus")

    def test_flowbox_child_focus_outline(self):
        self.assert_dotted_focus_outline("flowbox > flowboxchild:focus")

    def test_places_sidebar(self):
        self.assert_rule(".sidebar", {"background-color": FACE, "color": BLACK})
        self.assert_rule(".sidebar:backdrop", {"background-color": FACE, "color": BLACK})
        self.assert_rule("placessidebar row:backdrop", {"color": BLACK})
        self.assert_rule(
            "placessidebar row.activatable:selected:backdrop",
            {"background-color": SELECTION, "color": BLACK},
        )
        self.assert_rule("placessidebar row.sidebar-new-bookmark-row", {"color": BLACK})

    def test_stack_switcher_tabs(self):
        forms = {
            "base": ("stackswitcher > button",),
            "hover": ("stackswitcher > button:hover",),
            "checked": ("stackswitcher > button:checked",),
            "checked+hover": ("stackswitcher > button:checked:hover",),
        }
        for state, _selectors, checked in TAB_STATES:
            if state not in forms:
                continue
            expected = {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
            }
            if checked:
                expected["border-bottom-color"] = FACE
                expected["box-shadow"] = "none"
            else:
                expected["box-shadow"] = RAISED_BEVEL
            for selector in forms[state]:
                with self.subTest(state=state, selector=selector):
                    self.assert_rule(selector, expected)

    def test_rubberband(self):
        self.assert_rubberband((".rubberband", "rubberband"))
        # A later .view rule would win the cascade again.
        self.assertGreater(
            self.css.index(".rubberband, rubberband {"),
            self.css.index(".view, textview text, list {"),
        )

    def test_spin_button_field(self):
        self.assert_spin_button_field(("spinbutton:not(.vertical)",))
        self.assertNotIn("spinbutton.vertical > text", self.rules)

    def test_title_buttons(self):
        for scope in ("headerbar", ".titlebar"):
            for control, asset in (
                ("close", "window-close.svg"),
                ("maximize", "window-maximize.svg"),
                ("minimize", "window-minimize.svg"),
            ):
                self.assert_title_button(
                    f"{scope} button.titlebutton.{control}", asset
                )
            self.assert_rule(
                f"{scope} button.titlebutton image", TITLE_BUTTON_IMAGE
            )

    def test_menu(self):
        for selector in ("menu", ".menu", "popover", ".popover"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "border": f"1px solid {BLACK}",
                    "border-radius": "0",
                },
            )
        for selector in (
            "menuitem:hover",
            ".menuitem:hover",
            "popover modelbutton:hover",
            "popover modelbutton:selected",
        ):
            self.assert_rule(selector, {"background-color": SELECTION})

    def test_menu_scroll_arrows(self):
        for selector in MENU_SCROLL_UP:
            self.assert_rule(
                selector, {"-gtk-icon-source": 'url("../assets/arrow-up.svg")'}
            )
        for selector in MENU_SCROLL_DOWN:
            self.assert_rule(
                selector, {"-gtk-icon-source": 'url("../assets/arrow-down.svg")'}
            )

    def test_icon_sources_resolve_to_shipped_files(self):
        for ref in re.findall(r'url\("([^"]*)"\)', self.css):
            self.assertTrue((CSS.parent / ref).resolve().is_file(), ref)

    def test_icon_sources_point_at_shipped_assets(self):
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

    def test_menu_check_and_radio_are_boxless(self):
        for selector in (
            "menu menuitem check",
            "menu menuitem radio",
            "popover modelbutton check",
            "popover modelbutton radio",
        ):
            self.assert_rule(selector, MENU_CHECK)

    def test_menu_separator(self):
        self.assert_menu_separator(("menu separator", ".menu separator"))

    def test_titlebutton_separator_hidden(self):
        for selector in (
            "headerbar separator.titlebutton",
            ".titlebar separator.titlebutton",
        ):
            self.assert_rule(selector, {"opacity": "0"})

    def test_separator(self):
        self.assert_separators()

    def test_paned_handle(self):
        self.assert_paned_handles()

    def test_paned_handle_background_images(self):
        for selector in (
            "paned > separator",
            "paned > separator:selected",
            "paned > separator:backdrop",
            "paned > separator.wide",
            "paned > separator.wide:backdrop",
        ):
            self.assert_rule(selector, {"background-image": "none"})

    def test_frame(self):
        self.assert_frame(("frame > border", ".frame"))

    def test_color_swatch_corners(self):
        selectors = (
            "colorswatch#add-color-button overlay",
            "colorswatch#add-color-button overlay:hover",
            "colorswatch#add-color-button overlay:backdrop",
            "colorswatch#add-color-button overlay:backdrop:hover",
        )
        self.assert_color_swatch_corners(
            " overlay",
            {
                **{
                    selector: {"background-image": "none", "box-shadow": "none", "color": BLACK}
                    for selector in selectors
                },
                "button.color colorswatch:only-child": {"box-shadow": "none"},
            },
        )

    def test_color_button_swatch_shadow(self):
        self.assert_rule(
            "button.color colorswatch:only-child", {"box-shadow": "none"}
        )

    def test_add_color_background_images(self):
        for selector in (
            "colorswatch#add-color-button overlay",
            "colorswatch#add-color-button overlay:hover",
            "colorswatch#add-color-button overlay:backdrop",
            "colorswatch#add-color-button overlay:backdrop:hover",
        ):
            self.assert_rule(
                selector, {"background-image": "none", "box-shadow": "none", "color": BLACK}
            )
        self.assertEqual(
            self.rules["colorswatch#add-color-button overlay"]["background-image"],
            self.rules["button"]["background-image"],
        )

    def test_add_color_box_shadows(self):
        for selector in (
            "colorswatch#add-color-button overlay",
            "colorswatch#add-color-button overlay:hover",
            "colorswatch#add-color-button overlay:backdrop",
            "colorswatch#add-color-button overlay:backdrop:hover",
        ):
            self.assert_rule(selector, {"box-shadow": "none"})

    def test_add_color_foregrounds(self):
        selectors = (
            "colorswatch#add-color-button overlay",
            "colorswatch#add-color-button overlay:hover",
            "colorswatch#add-color-button overlay:backdrop",
            "colorswatch#add-color-button overlay:backdrop:hover",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector]["color"], BLACK)
        self.assertEqual(self.rules[selectors[0]]["color"], self.rules["window"]["color"])

    def test_scrollbar(self):
        self.assert_rule(
            "scrollbar",
            {
                "background-color": TROUGH,
                "border": f"1px solid {BLACK}",
                "padding": "0",
            },
        )
        self.assert_rule(
            "scrollbar slider",
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": RAISED_BEVEL,
            },
        )

    def test_scrollbar_steppers(self):
        self.assert_rule(
            "scrollbar:not(.overlay-indicator)",
            {
                "-GtkScrollbar-has-backward-stepper": "true",
                "-GtkScrollbar-has-forward-stepper": "true",
            },
        )
        self.assert_rule(
            "scrollbar.overlay-indicator",
            {
                "-GtkScrollbar-has-backward-stepper": "false",
                "-GtkScrollbar-has-forward-stepper": "false",
            },
        )
        self.assert_rule("scrollbar button", SCROLLBAR_STEPPER)
        self.assert_rule("scrollbar button:hover", {"background-color": TROUGH})
        self.assert_rule("scrollbar button:active", SCROLLBAR_STEPPER_ACTIVE)
        for selector, expected in SCROLLBAR_STEPPER_ARROWS.items():
            with self.subTest(selector=selector):
                self.assert_rule(selector, expected)

    def test_overlay_scrollbar_thumb_minimum(self):
        self.assert_rule(
            "scrollbar.overlay-indicator slider",
            {"min-width": "12px", "min-height": "12px"},
        )

    def test_ordinary_scrollbar_thumb_minimum(self):
        self.assert_rule(
            "scrollbar:not(.overlay-indicator) slider",
            {"min-width": "12px", "min-height": "12px"},
        )

    def test_overshoot_glows_cleared(self):
        """The stock radial over-scroll glows render nothing in normal state.

        The stock GTK 3 resource paints two radial ``-gtk-gradient`` images
        on each of the four ``scrolledwindow overshoot`` nodes; no collected
        reference screenshot shows a GTK over-scroll glow, and Platinum
        scroll fields run flat to the sunken frame.
        """
        for selector in (
            "scrolledwindow overshoot.top",
            "scrolledwindow overshoot.bottom",
            "scrolledwindow overshoot.left",
            "scrolledwindow overshoot.right",
        ):
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"background-image": "none"})

    def test_overshoot_backdrop_glows_cleared(self):
        """The stock radial over-scroll glows stay cleared in backdrop."""
        for selector in (
            "scrolledwindow overshoot.top:backdrop",
            "scrolledwindow overshoot.bottom:backdrop",
            "scrolledwindow overshoot.left:backdrop",
            "scrolledwindow overshoot.right:backdrop",
        ):
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"background-image": "none"})

    def test_junction_shares_the_scrollbar_band(self):
        """The scrollbar corner paints the flat trough band, nothing else.

        The stock GTK 3 resource fills the junction node where a scrolled
        window's two scrollbars meet with its own grey and draws a trough
        line through one edge of the band; no collected reference screenshot
        shows a GTK scrollbar corner, and the junction reads as the same
        flat band the landed scrollbar rule pins. The stock left-to-right
        mirror arm only re-slices the now-empty border-image, so the sheet
        must stop at the two rules and carry no such arm.
        """
        self.assertEqual(
            self.rules["scrolledwindow junction"],
            {
                "background-color": TROUGH,
                "border-color": "transparent",
                "border-image": "none",
            },
        )
        self.assertNotIn("junction:dir", self.css)

    def test_junction_backdrop_shares_the_scrollbar_band(self):
        """The scrollbar corner stays the flat trough band in backdrop."""
        self.assertEqual(
            self.rules["scrolledwindow junction:backdrop"],
            {
                "background-color": TROUGH,
                "border-color": "transparent",
                "border-image": "none",
            },
        )

    def test_progressbar(self):
        self.assert_progressbar(
            trough="progressbar trough",
            progress="progressbar progress",
            disabled="progressbar progress:disabled",
        )

    def test_entry_progress(self):
        self.assert_rule("entry progress", ENTRY_PROGRESS)

    def _run_gtk_child(self, program, *paths):
        """Run the GTK 3 pixel *program* in a fresh child interpreter.

        *paths* are the child's ``sys.argv[1:]``. The child does the GTK
        introspection work and asserts on the pixels it draws; the parent
        only judges its exit status, attaching the child's output to the
        failure. Exit 77 is the skip marker tests/test_gtk4_theme.py
        established: introspection or a display is missing, so the child
        prints its own skip reason first.

        The child process is not only a sandbox: an in-process ``import gi``
        leaves GLib's C worker threads in the suite process, which
        ``threading.active_count()`` cannot see, so every later
        ``tests/support/snippet_child.py`` ``os.fork`` FIFO guard would run
        from a multi-threaded parent -- Python 3.12+ warns about that as a
        deadlock hazard in the child, and a future Python may refuse it
        outright. The suite therefore never imports ``gi`` in-process
        (``tests/test_no_gtk_introspection.py`` pins that).
        """
        result = subprocess.run(
            [sys.executable, "-c", program, *paths],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 77:
            self.skipTest(result.stdout.strip() or "GTK 3 is not available")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_entry_progress_draws_a_two_pixel_strip(self):
        # GTK 3 ignores min-height on this node, so pin the drawn pixels.
        # The GTK work runs in a child interpreter; see _run_gtk_child for
        # why it never runs in this one.
        program = r'''
import re
import sys
from pathlib import Path

try:
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, Gtk
except (ImportError, ValueError):
    print("GTK 3 introspection is not installed")
    sys.exit(77)
if Gdk.Screen.get_default() is None:
    print("no display for GTK 3")
    sys.exit(77)
css = re.sub(rb"url\([^)]*\)", b"none", Path(sys.argv[1]).read_bytes())
provider = Gtk.CssProvider()
provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), provider, 800
)
window = Gtk.OffscreenWindow()
entry = Gtk.Entry()
entry.set_progress_fraction(0.5)
window.add(entry)
window.set_default_size(120, 21)
window.show_all()
while Gtk.events_pending():
    Gtk.main_iteration()
pixbuf = window.get_pixbuf()
pixels, stride, n = pixbuf.get_pixels(), pixbuf.get_rowstride(), pixbuf.get_n_channels()

def at(x, y):
    return "#%02X%02X%02X" % tuple(pixels[y * stride + x * n:][:3])

bottom = pixbuf.get_height() - 1
assert at(90, bottom) == "#000000", at(90, bottom)
strip = [at(30, bottom - d) for d in (1, 2)]
assert strip == ["#CCCCFF"] * 2, strip
assert at(30, bottom - 3) == "#FFFFFF", at(30, bottom - 3)
assert at(90, bottom - 1) == "#FFFFFF", at(90, bottom - 1)
print("entry progress: the 0.5 fraction leaves the #CCCCFF strip one and two pixels above the bottom border, #FFFFFF below it")
'''
        self._run_gtk_child(program, str(CSS))

    def test_mixed_check_draws_a_black_dash(self):
        # The GTK work runs in a child interpreter; see _run_gtk_child for
        # why it never runs in this one.
        program = r'''
import sys
from pathlib import Path

try:
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, Gtk
except (ImportError, ValueError):
    print("GTK 3 introspection is not installed")
    sys.exit(77)
if Gdk.Screen.get_default() is None:
    print("no display for GTK 3")
    sys.exit(77)
assets = sys.argv[2]
css = Path(sys.argv[1]).read_bytes().replace(
    b'url("../assets/', b'url("' + assets.encode() + b"/")
provider = Gtk.CssProvider()
provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), provider, 800
)
window = Gtk.OffscreenWindow()
button = Gtk.CheckButton()
button.set_can_focus(False)
button.set_inconsistent(True)
window.add(button)
window.show_all()
while Gtk.events_pending():
    Gtk.main_iteration()
pixbuf = window.get_pixbuf()
pixels, stride, n = pixbuf.get_pixels(), pixbuf.get_rowstride(), pixbuf.get_n_channels()

def at(x, y):
    return "#%02X%02X%02X" % tuple(pixels[y * stride + x * n:][:3])

black = [
    (x, y)
    for y in range(pixbuf.get_height())
    for x in range(pixbuf.get_width())
    if at(x, y) == "#000000"
]
xs = sorted({x for x, _ in black})
ys = sorted({y for _, y in black})
# The dash is 8px wide and 2px tall; the face's own border is not
# inside the dash's columns and rows.
dash = [(x, y) for x, y in black if 0 < x - xs[0] < 12]
inner = [p for p in dash if p[1] not in (ys[0], ys[-1])]
inner_xs = sorted({x for x, _ in inner})
inner_ys = sorted({y for _, y in inner})
assert len(inner_ys) == 2, inner_ys
assert inner_ys[1] - inner_ys[0] == 1, inner_ys
row = inner_ys[0]
run = [x for x in inner_xs if at(x, row) == "#000000" and at(x, row + 1) == "#000000"]
assert len(run) == 8, run
assert run[-1] - run[0] == 7, run
assert at(run[3], row - 1) == "#DDDDDD", at(run[3], row - 1)
assert at(run[3], row + 2) == "#DDDDDD", at(run[3], row + 2)
assert at(run[0] - 1, row) == "#DDDDDD", at(run[0] - 1, row)
print("mixed check: the inconsistent dash is 8px by 2px on the #DDDDDD face")
'''
        self._run_gtk_child(program, str(CSS), str(THEME_DIR / "assets"))

    def test_spinner(self):
        self.assert_spinner("-gtk-icon-transform")

    def test_levelbar(self):
        self.assert_levelbar(
            trough="levelbar trough",
            filled="levelbar block.filled",
            empty="levelbar block.empty",
            disabled="levelbar block.filled:disabled",
            horizontal="levelbar.horizontal block",
            vertical="levelbar.vertical block",
        )

    def test_switch(self):
        self.assert_switch(
            slider="switch slider",
            disabled_slider="switch:disabled slider",
            glyph="switch image",
        )

    def test_switch_focus_outline(self):
        self.assert_dotted_focus_outline("switch:focus")

    def test_scale(self):
        self.assert_scale(
            trough="scale trough",
            fill=("scale fill", "scale highlight"),
            slider="scale slider",
            horizontal="scale.horizontal slider",
            vertical="scale.vertical slider",
            disabled="scale slider:disabled",
        )

    def test_scale_focus_outline(self):
        self.assert_rule(
            "scale:focus",
            {
                "outline": f"1px dotted {BLACK}",
                "outline-offset": "0",
                "-gtk-outline-radius": "0",
            },
        )
        width, style, color = self.rules[".rubberband"]["border"].split()
        self.assertEqual((width, style, color), ("1px", "dotted", BLACK))
        self.assertEqual(self.rules["scale trough"]["border-radius"], "0")

    def test_button_focus_outline(self):
        self.assert_rule(
            "button:focus",
            {
                "outline": f"1px dotted {BLACK}",
                "outline-offset": "0",
                "-gtk-outline-radius": "0",
            },
        )
        self.assertEqual(
            self.rules["button:focus"]["outline"], self.rules["scale:focus"]["outline"]
        )
        self.assertEqual(
            self.rules["button:focus"]["outline-offset"],
            self.rules["scale:focus"]["outline-offset"],
        )
        self.assertEqual(
            self.rules["button:focus"]["-gtk-outline-radius"],
            self.rules["button"]["border-radius"],
        )

    def test_checkbutton_focus_outline(self):
        self.assert_dotted_focus_outline("checkbutton:focus")

    def test_entry_focus_outline(self):
        self.assert_dotted_focus_outline("entry:focus")

    def test_horizontal_spinbutton_focus_outline(self):
        self.assert_dotted_focus_outline("spinbutton:focus:not(.vertical)")

    def test_vertical_spinbutton_focus_outline(self):
        self.assert_dotted_focus_outline(
            "spinbutton.vertical:focus", anchor="spinbutton:focus:not(.vertical)"
        )

    def test_linked_members_strip_their_trailing_border(self):
        for css_class, side in ((".linked:not(.vertical)", "border-right-style"),
                                (".linked.vertical", "border-bottom-style")):
            for member in ("button", "entry", "spinbutton:not(.vertical)",
                           "combobox > box > button.combo"):
                self.assert_rule(
                    f"{css_class} > {member}",
                    {side: "none"},
                )

    def test_linked_last_member_restores_the_border(self):
        for css_class, side in ((".linked:not(.vertical)", "border-right-style"),
                                (".linked.vertical", "border-bottom-style")):
            for member in ("button:last-child", "entry:last-child",
                           "spinbutton:not(.vertical):last-child",
                           "combobox > box > button.combo:last-child"):
                self.assert_rule(
                    f"{css_class} > {member}",
                    {side: "solid"},
                )

    def test_linked_protection_keeps_the_path_bar_and_stack_switcher_outlines(self):
        self.assert_rule(
            ".path-bar.linked > button:not(:last-child)",
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
            ".path-bar > button",
            {
                "border": f"1px solid {BLACK}",
            },
        )

    def test_radiobutton_focus_outline(self):
        self.assert_dotted_focus_outline(
            "radiobutton:focus", anchor="checkbutton:focus"
        )

    def test_menubar_titles(self):
        self.assert_menubar_titles("menubar > menuitem")

    def test_toolbar_and_menubar(self):
        for selector in ("toolbar", "menubar"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "border-bottom": f"1px solid {ETCH_DARK}",
                    "box-shadow": f"inset 0 -1px {WHITE}",
                },
            )


class TestScrollbarStepperReference(ReferenceScreenshotMixin, unittest.TestCase):
    """The stepper box face and divider must match the reference screenshot.

    The installer CD window's left stepper is a 14x14 #EEEEEE face between the
    bar's 1px #000000 border (x=23, y=462 and y=477) and a 1px #555555
    divider at x=38, so the visible box is 16x16. ``TestGtkTheme`` pins the
    sheet to ``SCROLLBAR_STEPPER`` and its direction rules, so this ties that
    14px face and divider to a screenshot.
    """

    REFERENCE = SETUP_REFERENCE
    MAX_ROWS = SETUP_MAX_ROWS

    def test_stepper_box_matches_reference(self):
        face_left, face_right = 24, 37
        face_top, face_bottom = 463, 476
        for x, y in ((face_left, face_top), (face_right, face_bottom)):
            with self.subTest(x=x, y=y):
                self.assertEqual(hex_colour(self.pixel(x, y)), TROUGH)
        for x, y in ((23, 468), (30, 462), (30, 477)):
            with self.subTest(x=x, y=y):
                self.assertEqual(hex_colour(self.pixel(x, y)), BLACK)
        self.assertEqual(hex_colour(self.pixel(38, 468)), INACTIVE_OUTLINE)
        face_width = face_right - face_left + 1
        face_height = face_bottom - face_top + 1
        self.assertEqual(face_width, 14)
        self.assertEqual(face_height, 14)
        self.assertEqual(SCROLLBAR_STEPPER["min-width"], f"{face_width}px")
        self.assertEqual(SCROLLBAR_STEPPER["min-height"], f"{face_height}px")
        self.assertEqual(
            SCROLLBAR_STEPPER_ARROWS["scrollbar.horizontal button.up"][
                "border-right"
            ],
            f"1px solid {INACTIVE_OUTLINE}",
        )

    def test_overlay_thumb_minimum_matches_reference(self):
        top, bottom = 462, 477
        for y in (top, bottom):
            self.assertEqual(hex_colour(self.pixel(200, y)), BLACK)
        for y in range(top + 1, bottom):
            with self.subTest(y=y):
                self.assertEqual(hex_colour(self.pixel(200, y)), TROUGH)
        band = bottom - top + 1
        css = gtk_css.read_theme_text(CSS)
        _, rules, _ = parse_css(css, source=str(CSS.relative_to(ROOT)))
        self.assertEqual(rules["scrollbar"]["border"], f"1px solid {BLACK}")
        self.assertEqual(rules["scrollbar slider"]["border"], f"1px solid {BLACK}")
        for dimension in ("min-width", "min-height"):
            with self.subTest(dimension=dimension):
                self.assertEqual(
                    rules["scrollbar.overlay-indicator slider"][dimension],
                    f"{band - 4}px",
                )

    def test_ordinary_thumb_minimum_matches_reference(self):
        top, bottom = 462, 477
        for y in (top, bottom):
            self.assertEqual(hex_colour(self.pixel(200, y)), BLACK)
        for y in range(top + 1, bottom):
            with self.subTest(y=y):
                self.assertEqual(hex_colour(self.pixel(200, y)), TROUGH)
        band = bottom - top + 1
        css = gtk_css.read_theme_text(CSS)
        _, rules, _ = parse_css(css, source=str(CSS.relative_to(ROOT)))
        self.assertEqual(rules["scrollbar"]["border"], f"1px solid {BLACK}")
        self.assertEqual(rules["scrollbar slider"]["border"], f"1px solid {BLACK}")
        for dimension in ("min-width", "min-height"):
            with self.subTest(dimension=dimension):
                self.assertEqual(
                    rules["scrollbar:not(.overlay-indicator) slider"][dimension],
                    f"{band - 4}px",
                )


class TestCheckGlyphs(unittest.TestCase):
    """The checked check and radio glyphs GTK loads from the shipped assets."""

    @classmethod
    def setUpClass(cls):
        cls.checkmark = parse_svg(CHECKMARK)
        cls.bullet = parse_svg(BULLET)
        cls.mixed = parse_svg(CHECK_MIXED)

    def test_assets_stand_alone(self):
        for tree in (self.checkmark, self.bullet, self.mixed):
            assert_no_script_elements(self, tree)
            assert_no_style_elements(self, tree)

    def test_assets_put_the_root_first(self):
        for path in (CHECKMARK, BULLET, CHECK_MIXED):
            with self.subTest(asset=path.name):
                assert_svg_root_first(self, path)

    def test_assets_span_a_14px_canvas(self):
        for tree in (self.checkmark, self.bullet, self.mixed):
            assert_root_canvas(self, tree, 14, 14)

    def test_assets_use_only_the_two_glyph_fills(self):
        self.assertEqual(
            attribute_values(self.checkmark, "fill")
            | attribute_values(self.bullet, "fill")
            | attribute_values(self.mixed, "fill"),
            {"none", BLACK},
        )

    def test_checkmark_geometry(self):
        paths = children_named(self.checkmark.getroot(), "path")
        self.assertEqual(len(paths), 1)
        path = paths[0]
        self.assertEqual(path.get("d"), "M 2.5,7.5 L 5.5,10.5 L 11.5,4.5")
        self.assertEqual(path.get("fill"), "none")
        self.assertEqual(path.get("stroke"), BLACK)
        self.assertEqual(path.get("stroke-width"), "2")
        self.assertEqual(path.get("stroke-linecap"), "square")
        self.assertEqual(path.get("stroke-linejoin"), "miter")

    def test_mixed_geometry(self):
        paths = children_named(self.mixed.getroot(), "path")
        self.assertEqual(len(paths), 1)
        path = paths[0]
        self.assertEqual(path.get("d"), "M 4,7 L 10,7")
        self.assertEqual(path.get("fill"), "none")
        self.assertEqual(path.get("stroke"), BLACK)
        self.assertEqual(path.get("stroke-width"), "2")
        self.assertEqual(path.get("stroke-linecap"), "square")

    def test_bullet_geometry(self):
        circles = children_named(self.bullet.getroot(), "circle")
        self.assertEqual(len(circles), 1)
        self.assertEqual(
            circle_geometry_and_fill(circles[0]),
            (7.0, 7.0, 2.5, BLACK),
        )


class TestArrowGlyphs(unittest.TestCase):
    """The combo box, menu scroll and disclosure arrow glyphs GTK loads from assets."""

    @classmethod
    def setUpClass(cls):
        cls.down = parse_svg(ARROW_DOWN)
        cls.up = parse_svg(ARROW_UP)
        cls.right = parse_svg(ARROW_RIGHT)
        cls.submenu = parse_svg(SUBMENU_ARROW_SVG)

    def test_assets_stand_alone(self):
        for tree in (self.down, self.up, self.right, self.submenu):
            assert_no_script_elements(self, tree)
            assert_no_style_elements(self, tree)

    def test_assets_put_the_root_first(self):
        for path in (ARROW_DOWN, ARROW_UP, ARROW_RIGHT, SUBMENU_ARROW_SVG):
            with self.subTest(asset=path.name):
                assert_svg_root_first(self, path)

    def test_assets_span_a_16px_canvas(self):
        for tree in (self.down, self.up, self.right, self.submenu):
            assert_root_canvas(self, tree, 16, 16)

    def test_assets_use_only_the_black_fill(self):
        self.assertEqual(
            attribute_values(self.down, "fill")
            | attribute_values(self.up, "fill")
            | attribute_values(self.right, "fill")
            | attribute_values(self.submenu, "fill"),
            {BLACK},
        )

    def test_arrow_geometry(self):
        expected = (
            (self.down, "M 4,5 L 12,5 L 8,11 Z"),
            (self.up, "M 4,11 L 12,11 L 8,5 Z"),
            (self.right, "M 5,4 L 5,12 L 11,8 Z"),
        )
        for tree, path_d in expected:
            with self.subTest(path=path_d):
                paths = children_named(tree.getroot(), "path")
                self.assertEqual(len(paths), 1)
                self.assertEqual(paths[0].get("d"), path_d)
                self.assertEqual(paths[0].get("fill"), BLACK)

    def test_submenu_arrow_copies_the_icon_theme_triangle(self):
        paths = []
        for tree in (self.submenu, parse_svg(ICON_GO_NEXT)):
            found = children_named(tree.getroot(), "path")
            self.assertEqual(len(found), 1)
            paths.append((found[0].get("d"), found[0].get("fill")))
        self.assertEqual(paths[0], paths[1])


if __name__ == "__main__":
    unittest.main()
