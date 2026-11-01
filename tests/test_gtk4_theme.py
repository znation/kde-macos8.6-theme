"""Validate the standalone GTK 4 Platinum stylesheet.

The sheet is one standalone ``gtk.css`` under ``gtk-4.0``. The palette is
reference-grounded through ``support.platinum_palette``; no reference
screenshot shows a GTK widget, so the GTK geometry is this theme's adaptation
rather than a reference crop.
"""

from __future__ import annotations

import re
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import gtk_css
from support.gtk_css import HEX, parse_css, strip_comments
from support.gtk_rule_cases import GtkSharedControlCases
from support.gtk_theme_spec import (
    BASE_DEFINED_COLOURS,
    BUTTON_BEVEL,
    CALENDAR_SELECTED_DAY,
    CHECK,
    COMBO_ARROW,
    DISABLED_TEXT,
    ENTRY_PROGRESS_GTK4,
    ETCH_DARK,
    INFOBAR,
    LINK,
    MENUBUTTON_ARROWS,
    VISITED_LINK,
    MENU_CHECK,
    INVERTED_BUTTON_BEVEL,
    PROGRESSBAR_PROGRESS,
    PROGRESSBAR_TROUGH,
    RAISED_BEVEL,
    RADIO,
    ROW_HOVER,
    ROW_SELECTED,
    SCALE_EMPTY_FILL,
    SCALE_THUMB,
    SCALE_TROUGH,
    TEXT_SELECTION,
    TITLE_BUTTON_ASSETS,
    TITLE_BUTTON_IMAGE,
    TITLE_BUTTON_IMAGE_STATE,
    VIEW_BACKGROUND,
)
from support.desktoptheme_paths import SETUP_MAX_ROWS, SETUP_REFERENCE
from support.aurorae_fixtures import PROFILER_REFERENCE, PROFILER_ROWS
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
from support.symlink_fixtures import symlinked_repo

THEME_ID = "org.macos8.desktop"
THEME_DIR = Path(ROOT) / "theme" / "gtk" / THEME_ID
CSS = THEME_DIR / "gtk-4.0" / "gtk.css"

DEFINED_COLOURS = {
    **BASE_DEFINED_COLOURS,
    "accent_bg_color": SELECTION,
    "accent_fg_color": BLACK,
    "theme_unfocused_selected_bg_color": SELECTION,
    "theme_unfocused_selected_fg_color": BLACK,
    "theme_unfocused_bg_color": FACE,
    "theme_unfocused_fg_color": BLACK,
    "theme_unfocused_base_color": WHITE,
    "theme_unfocused_text_color": BLACK,
    "window_bg_color": FACE,
    "window_fg_color": BLACK,
    "view_bg_color": WHITE,
    "view_fg_color": BLACK,
    "headerbar_bg_color": FACE,
    "headerbar_fg_color": BLACK,
    "headerbar_border_color": BLACK,
    "headerbar_backdrop_color": FACE,
    "popover_bg_color": FACE,
    "popover_fg_color": BLACK,
    "card_bg_color": FACE,
    "card_fg_color": BLACK,
    "dialog_bg_color": FACE,
    "dialog_fg_color": BLACK,
    "sidebar_bg_color": FACE,
    "sidebar_fg_color": BLACK,
    "sidebar_backdrop_color": FACE,
    "sidebar_border_color": BLACK,
    "secondary_sidebar_bg_color": FACE,
    "secondary_sidebar_fg_color": BLACK,
    "secondary_sidebar_backdrop_color": FACE,
    "secondary_sidebar_border_color": BLACK,
    "thumbnail_bg_color": WHITE,
    "thumbnail_fg_color": BLACK,
    "scrollbar_outline_color": BLACK,
}

# The scale slider anchors the sheet's focus colour and its transition policy:
# every control that states an outline colour or a transition repeats the
# value the scale states, and these suites keep those two selectors as one.
SCALE_FOCUS = "scale:focus:focus-visible > trough > slider"
SCALE_SLIDER = "scale > trough > slider"


class TestGtk4Theme(GtkSharedControlCases, unittest.TestCase):
    def test_header_subtitle_foreground(self):
        selectors = ("headerbar .subtitle", "windowtitle .subtitle")
        self.assert_disabled_text(selectors)
        expected = {**DISABLED_TEXT, "opacity": "1"}
        for selector in selectors:
            self.assertEqual(self.rules[selector], expected)
            self.assertEqual(self.selectors.count(selector), 1)

    def test_separator_label_foreground(self):
        selector = "label.separator"
        self.assert_disabled_text((selector,))
        self.assertEqual(
            self.rules[selector],
            {**DISABLED_TEXT, "opacity": "1", "text-shadow": "none"},
        )
        self.assertEqual(self.selectors.count(selector), 1)

    def test_placeholder_foreground(self):
        selectors = (
            "entry > text > placeholder",
            "spinbutton > text > placeholder",
            "spinbutton.vertical > text > text > placeholder",
        )
        self.assert_disabled_text(selectors)
        expected = {**DISABLED_TEXT, "opacity": "1"}
        for selector in selectors:
            self.assert_rule(selector, expected)
            self.assertEqual(self.css.count(selector), 1)

    def test_dim_label_foreground(self):
        selectors = (".dim-label",)
        self.assert_disabled_text(selectors)
        self.assert_rule(selectors[0], {**DISABLED_TEXT, "opacity": "1"})
        self.assertEqual(self.css.count(".dim-label {"), 1)

    def test_dimmed_label_foreground(self):
        selector = "label.dimmed"
        self.assert_disabled_text((selector,))
        self.assert_rule(selector, {**DISABLED_TEXT, "opacity": "1"})
        self.assertEqual(self.selectors.count(selector), 1)
        self.assertNotIn(".dimmed", self.selectors)

    def test_mixed_indicators_draw_black_dashes(self):
        # Isolate GTK 4 from the GTK 3 introspection used by the other suite.
        result = subprocess.run(
            [sys.executable, "-c", '''
import sys, time
from pathlib import Path
try:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, Gdk, GLib, Graphene
except (ImportError, ValueError):
    sys.exit(77)
Gtk.init()
if Gdk.Display.get_default() is None:
    sys.exit(77)
Gtk.Settings.get_default().set_property("gtk-theme-name", "Adwaita")
root = Path(sys.argv[1])
provider = Gtk.CssProvider()
provider.load_from_data((root / "gtk-4.0/gtk.css").read_bytes().replace(
    b"../assets/", (root / "assets").as_uri().encode() + b"/"))
Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider, 801)
for radio in (False, True):
    window = Gtk.Window()
    button = Gtk.CheckButton()
    peer = Gtk.CheckButton()
    if radio:
        button.set_group(peer)
    button.set_inconsistent(True)
    button.set_focusable(False)
    window.set_child(button)
    window.present()
    try:
        indicator = button.get_first_child()
        name = "radio" if radio else "check"
        assert indicator.get_css_name() == name
        face = (255, 255, 255) if radio else (221, 221, 221)
        dash = [(x, y) for x in range(4, 12) for y in (7, 8)]
        surround = [
            (x, y) for x in range(4, 12) for y in (6, 9)
        ] + [(3, 7), (12, 7)]

        def painted():
            snapshot = Gtk.Snapshot()
            Gtk.WidgetPaintable.new(indicator).snapshot(snapshot, 16, 16)
            node = snapshot.to_node()
            renderer = window.get_renderer()
            if node is None or renderer is None:
                # Not allocated or realized yet: no frame to inspect.
                return None
            viewport = Graphene.Rect()
            viewport.init(0, 0, 16, 16)
            texture = renderer.render_texture(node, viewport)
            pixbuf = Gdk.pixbuf_get_from_texture(texture)
            data, stride = pixbuf.get_pixels(), pixbuf.get_rowstride()
            channels = pixbuf.get_n_channels()
            def at(x, y):
                start = y * stride + x * channels
                return tuple(data[start:start + 3])
            return at

        # Wait for the indicator's first correctly painted frame instead of a
        # fixed wall-clock settle: under CPU load the toolkit's async style and
        # paint work can outlast a short settle, which made this test fail on a
        # busy machine. A sheet that never paints the dash still fails, after
        # the deadline, with the pixel tuple that is wrong.
        deadline = time.monotonic() + 30
        while True:
            while GLib.MainContext.default().pending():
                GLib.MainContext.default().iteration(False)
            at = painted()
            if at is not None and all(
                at(x, y) == (0, 0, 0) for x, y in dash
            ) and all(at(x, y) == face for x, y in surround):
                break
            if time.monotonic() >= deadline:
                if at is None:
                    raise AssertionError(
                        f"{name}: indicator produced no paintable node"
                    )
                for x, y in dash:
                    assert at(x, y) == (0, 0, 0), (name, x, y, at(x, y))
                for x, y in surround:
                    assert at(x, y) == face, (name, x, y, at(x, y))
                raise AssertionError(f"{name}: indicator did not settle")
            time.sleep(0.01)
        print(name + ": black dash at columns 4–11, rows 7–8; face surrounds it")
    finally:
        window.destroy()
''', str(THEME_DIR)],
            env={**os.environ, "GDK_BACKEND": "x11", "GSK_RENDERER": "cairo"},
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 77:
            self.skipTest("GTK 4 introspection or an X11 display is missing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    CSS_PATH = CSS

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
        self.assertEqual(set(HEX.findall(strip_comments(self.css))), palette)

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

    def test_expander_arrows(self):
        self.assert_expander_arrows(
            ("treeview.view.expander", "expander"),
            ("treeview.view.expander:checked", "expander:checked"),
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

    def test_disabled_text(self):
        self.assert_disabled_text(
            ("label:disabled", "text:disabled", "spinbutton.vertical > text:disabled")
        )

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

    def test_links(self):
        self.assert_links(
            ("button.link",),
            ("link", "button.link > label"),
            ("link:visited", "button.link:visited > label"),
            {"text-decoration": "underline"},
        )

    def test_disabled_link_button_labels(self):
        selectors = (
            "button.link:disabled > label",
            "button.link:visited:disabled > label",
        )
        self.assert_disabled_text(selectors)
        css = strip_comments(self.css)
        enabled = css.index("button.link > label")
        visited = css.index("button.link:visited > label")
        for selector in selectors:
            self.assertGreater(css.index(selector), enabled, selector)
            self.assertGreater(css.index(selector), visited, selector)

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

    def test_calendar(self):
        selected = "calendar > grid > label.day-number:selected"
        self.assert_rule(
            selected, {**CALENDAR_SELECTED_DAY, "border-radius": "0"}
        )
        self.assert_rule(
            "calendar > grid > label.day-number.other-month",
            {"color": "#888888"},
        )
        self._assert_inactive_grey_from_scheme()
        self.assert_matches_frame(selected, "border-radius")

    def test_calendar_disabled_day_text(self):
        disabled = "calendar:disabled > grid > label.day-number"
        selected = "calendar > grid > label.day-number:selected"
        other_month = "calendar > grid > label.day-number.other-month"
        self.assert_rule(disabled, {"color": "#888888"})
        self.assertEqual(self.rules[disabled]["color"], self.rules["label:disabled"]["color"])
        self._assert_inactive_grey_from_scheme()
        self.assertGreater(self.css.index(disabled), self.css.index(selected))
        self.assertGreater(self.css.index(disabled), self.css.index(other_month))

    def test_calendar_disabled_selected_day_text(self):
        disabled_selected = "calendar > grid > label.day-number:disabled:selected"
        disabled = "calendar:disabled > grid > label.day-number"
        selected = "calendar > grid > label.day-number:selected"
        self.assert_disabled_text((disabled_selected,))
        self.assertEqual(self.rules[disabled_selected], {"color": "#888888"})
        self.assertEqual(self.rules[disabled_selected]["color"],
                         self.rules[disabled]["color"])
        self.assertEqual(self.rules[selected]["background-color"], SELECTION)
        self.assertGreater(self.css.index(disabled_selected), self.css.index(selected))

    def test_calendar_today_underline(self):
        today = "calendar > grid > label.today"
        selected_today = "calendar > grid > label.today:selected"
        other_month = "calendar > grid > label.day-number.other-month"
        self.assert_rule(today, {"box-shadow": "inset 0 -2px #888888"})
        self.assert_rule(selected_today, {"box-shadow": "none"})
        self.assertEqual(self.rules[today]["box-shadow"].split()[-1],
                         self.rules[other_month]["color"])
        self._assert_inactive_grey_from_scheme()

    def test_calendar_marked_day_corners(self):
        marked = "calendar > grid > label.day-number:checked"
        self.assert_rule(marked, {"border-radius": "0", "background-color": TROUGH})
        self.assert_matches_frame(marked, "border-radius")

    def test_calendar_marked_day_fill(self):
        marked = "calendar > grid > label.day-number:checked"
        selected = "calendar > grid > label.day-number:selected"
        trough = "scrollbar > range > trough"
        self.assertEqual(self.rules[marked]["background-color"],
                         self.rules[trough]["background-color"])
        self.assertEqual(self.rules[selected]["background-color"], SELECTION)
        self.assertLess(self.css.index(marked), self.css.index(selected))

    def test_calendar_outer_border(self):
        calendar = "calendar"
        self.assert_rule(calendar, {"color": BLACK, "border": "1px solid #000000"})
        self.assert_matches_frame(calendar, "border")

    def test_calendar_foreground(self):
        self.assertEqual(self.rules["calendar"]["color"], BLACK)
        self.assertEqual(self.rules["calendar"]["color"], DEFINED_COLOURS["view_fg_color"])
        self.assertEqual(self.rules["calendar"]["color"], self.rules[".view"]["color"])

    def test_calendar_focus_outline(self):
        focus = "calendar > grid > label:focus"
        self.assert_rule(
            focus,
            {"outline-color": BLACK, "outline-width": "2px", "outline-offset": "-2px"},
        )
        self.assertEqual(self.rules[focus]["outline-color"], BLACK)
        self.assertTrue(self.rules["calendar"]["border"].endswith(BLACK))

    def assert_scale_focus_outline(self, focus):
        """Assert *focus* states the black outline the scale focus states."""
        self.assert_rule(focus, {"outline-color": BLACK})
        self.assertEqual(
            self.rules[focus]["outline-color"],
            self.rules[SCALE_FOCUS]["outline-color"],
        )

    def assert_scale_slider_transition(self, selector):
        """Assert *selector* keeps the no-transition the scale slider keeps."""
        self.assert_rule(selector, {"transition": "none"})
        self.assertEqual(
            self.rules[selector]["transition"],
            self.rules[SCALE_SLIDER]["transition"],
        )

    def assert_matches_frame(self, selector, prop):
        """Assert *selector*'s *prop* value matches each frame arm's.

        The square-corner tests anchor a container's paint to both spellings
        of the landed frame rule; this drives the paired assertion for each
        spelling in turn.
        """
        for frame in ("frame > border", ".frame"):
            with self.subTest(frame=frame):
                self.assertEqual(
                    self.rules[selector][prop],
                    self.rules[frame][prop],
                )

    def test_scale_focus_outline_color(self):
        focus = SCALE_FOCUS
        self.assert_rule(focus, {"outline-color": BLACK})
        self.assertEqual(
            self.rules[focus]["outline-color"],
            self.rules["calendar > grid > label:focus"]["outline-color"],
        )

    def test_button_focus_outline_color(self):
        self.assert_scale_focus_outline("button:focus:focus-visible")

    def test_entry_focus_outline_color(self):
        self.assert_scale_focus_outline("entry:focus-within")

    def test_spinbutton_focus_outline_color(self):
        self.assert_scale_focus_outline("spinbutton:focus-within")

    def test_checkbutton_focus_outline_color(self):
        self.assert_scale_focus_outline("checkbutton:focus:focus-visible")

    def test_calendar_focus_transition(self):
        self.assert_rule("calendar > grid > label", {"transition": "none"})

    def test_scale_focus_transition(self):
        self.assert_rule(SCALE_SLIDER, {"transition": "none"})

    def test_button_focus_transition(self):
        self.assert_scale_slider_transition("button")

    def test_button_disabled_and_backdrop(self):
        self.assert_rule(
            "button:backdrop",
            {
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": BUTTON_BEVEL,
                "color": BLACK,
                "transition": "none",
            },
        )
        for selector in ("button:backdrop:active", "button:backdrop:checked"):
            self.assert_rule(
                selector,
                {
                    "background-image": "none",
                    "border-color": BLACK,
                    "box-shadow": INVERTED_BUTTON_BEVEL,
                    "color": BLACK,
                    "transition": "none",
                },
            )
        for selector in (
            "button:disabled",
            "button:disabled:active",
            "button:disabled:checked",
            "button:backdrop:disabled",
            "button:backdrop:disabled:active",
            "button:backdrop:disabled:checked",
        ):
            self.assert_rule(
                selector,
                {
                    "background-image": "none",
                    "border-color": BLACK,
                    "box-shadow": BUTTON_BEVEL,
                    "color": DISABLED_TEXT["color"],
                },
            )

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
        # No reference screenshot shows a GTK suggested-action button; the
        # tail arms restate the landed plain push-button recipe, so every
        # checked relationship below anchors the landed face constants.
        # (2026-10-31: the colour-class members are since restated by
        # test_action_class_flat_arms.)
        self.assert_rule(
            "button.suggested-action",
            {
                "background-color": FACE,
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": BUTTON_BEVEL,
                "color": BLACK,
                "outline-color": BLACK,
                "transition": "none",
            },
        )
        self.assert_rule(
            "button.suggested-action:hover",
            {
                "background-color": FACE,
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": BUTTON_BEVEL,
                "color": BLACK,
                "outline-color": BLACK,
            },
        )
        sunken = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
        }
        for selector in ("button.suggested-action:active", "button.suggested-action:checked"):
            self.assert_rule(selector, sunken)
        insensitive = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        for selector in (
            "button.suggested-action:disabled",
            "button.suggested-action:disabled:active",
            "button.suggested-action:disabled:checked",
        ):
            self.assert_rule(selector, insensitive)
        self.assert_rule(
            "button.suggested-action:focus:focus-visible",
            {"outline-color": BLACK},
        )
        self.assertEqual(
            self.rules["button.suggested-action:focus:focus-visible"]["outline-color"],
            self.rules["button:focus:focus-visible"]["outline-color"],
        )
        expected_selectors = {
            "button.suggested-action",
            "button.suggested-action:hover",
            "button.suggested-action:active",
            "button.suggested-action:checked",
            "button.suggested-action:disabled",
            "button.suggested-action:disabled:active",
            "button.suggested-action:disabled:checked",
            "button.suggested-action:focus:focus-visible",
        }
        # The `.flat`-suffixed colour-class selectors land through
        # test_action_class_flat_arms, so they stay out of the plain family
        # bound here (2026-10-31).
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith("button.suggested-action") and ".flat" not in selector
            },
            expected_selectors,
        )

    def test_destructive_action_plain_arms(self):
        # No reference screenshot shows a GTK destructive-action button; the
        # tail arms restate the landed plain push-button recipe, so every
        # checked relationship below anchors the landed face constants.
        # (2026-10-31: the colour-class members are since restated by
        # test_action_class_flat_arms.)
        self.assert_rule(
            "button.destructive-action",
            {
                "background-color": FACE,
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": BUTTON_BEVEL,
                "color": BLACK,
                "outline-color": BLACK,
                "transition": "none",
            },
        )
        self.assert_rule(
            "button.destructive-action:hover",
            {
                "background-color": FACE,
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": BUTTON_BEVEL,
                "color": BLACK,
                "outline-color": BLACK,
            },
        )
        sunken = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
        }
        for selector in ("button.destructive-action:active", "button.destructive-action:checked"):
            self.assert_rule(selector, sunken)
        insensitive = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        for selector in (
            "button.destructive-action:disabled",
            "button.destructive-action:disabled:active",
            "button.destructive-action:disabled:checked",
        ):
            self.assert_rule(selector, insensitive)
        self.assert_rule(
            "button.destructive-action:focus:focus-visible",
            {"outline-color": BLACK},
        )
        self.assertEqual(
            self.rules["button.destructive-action:focus:focus-visible"]["outline-color"],
            self.rules["button:focus:focus-visible"]["outline-color"],
        )
        expected_selectors = {
            "button.destructive-action",
            "button.destructive-action:hover",
            "button.destructive-action:active",
            "button.destructive-action:checked",
            "button.destructive-action:disabled",
            "button.destructive-action:disabled:active",
            "button.destructive-action:disabled:checked",
            "button.destructive-action:focus:focus-visible",
        }
        # The `.flat`-suffixed colour-class selectors land through
        # test_action_class_flat_arms, so they stay out of the plain family
        # bound here (2026-10-31).
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith("button.destructive-action") and ".flat" not in selector
            },
            expected_selectors,
        )

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

    def test_entry_focus_transition(self):
        self.assert_scale_slider_transition("entry")

    def test_spinbutton_focus_transition(self):
        self.assert_scale_slider_transition("spinbutton")

    def test_checkbutton_focus_transition(self):
        self.assert_scale_slider_transition("checkbutton")

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

    def test_notebook_focus_outline_color(self):
        self.assert_scale_focus_outline(
            "notebook:focus:focus-visible > header > tabs > tab:checked"
        )

    def test_calendar_header_separator(self):
        header = "calendar > header"
        infobar = "infobar > revealer > box"
        self.assert_rule(
            header,
            {"border-bottom": "1px solid #888888", "box-shadow": "inset 0 -1px #FFFFFF"},
        )
        for prop in ("border-bottom", "box-shadow"):
            with self.subTest(property=prop):
                self.assertEqual(self.rules[header][prop], self.rules[infobar][prop])

    def test_infobar(self):
        self.assert_infobar(("infobar > revealer > box",))
        for message_type in (".info", ".question", ".warning", ".error"):
            self.assertNotIn(message_type, self.css, message_type)

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

    def test_row_selection_backdrop(self):
        self.assert_row_selection_backdrop((
            "treeview.view:selected:backdrop",
            "list row.activatable:selected:backdrop",
            "columnview.view:selected:backdrop",
            "listview > row.activatable:selected:backdrop",
        ))
        self.assertGreater(
            self.css.index("list row.activatable:selected:backdrop"),
            self.css.index("list row.activatable:selected:"),
        )

    def test_selected_row_button_arms(self):
        # The selected-row button arms restate the landed black: stock's
        # three selected-row arms would paint an opaque button with a
        # blue border and a flat button with a white label on the landed
        # light selection fill and recolour the flat label near white in
        # backdrop, so each appended selector is the exact stock twin at
        # the sheet tail, winning the tie by later source order with the
        # landed palette's black (recorded 2026-10-31 by the feature
        # role).
        self.assert_rule("row:selected button", {"border-color": BLACK})
        for selector in (
            "row:selected button.sidebar-button:not(:active):not(:checked):not(:hover):not(disabled)",
            "row:selected button.flat:not(:active):not(:checked):not(:hover):not(disabled)",
        ):
            self.assert_rule(selector, {"color": BLACK, "border-color": BLACK})
        for selector in (
            "row:selected button.sidebar-button:not(:active):not(:checked):not(:hover):not(disabled):backdrop",
            "row:selected button.flat:not(:active):not(:checked):not(:hover):not(disabled):backdrop",
        ):
            self.assert_rule(selector, {"color": BLACK})
        self.assertEqual(
            self.rules[
                "row:selected button.flat:not(:active):not(:checked):not(:hover):not(disabled):backdrop"
            ]["color"],
            self.rules["button:backdrop.flat"]["color"],
        )
        expected = {
            "row:selected button",
            "row:selected button.sidebar-button:not(:active):not(:checked):not(:hover):not(disabled)",
            "row:selected button.flat:not(:active):not(:checked):not(:hover):not(disabled)",
            "row:selected button.sidebar-button:not(:active):not(:checked):not(:hover):not(disabled):backdrop",
            "row:selected button.flat:not(:active):not(:checked):not(:hover):not(disabled):backdrop",
        }
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith("row:selected button")
            },
            expected,
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

    def test_stack_switcher_tabs(self):
        forms = {
            "base": ("stackswitcher > button",),
            "hover": ("stackswitcher > button:hover",),
            "checked": ("stackswitcher > button:checked",),
            "checked+hover": ("stackswitcher > button:checked:hover",),
        }
        self.assert_tab_faces(forms)

    def test_rubberband(self):
        self.assert_rubberband(("rubberband",))

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

    def test_spin_button_field(self):
        self.assert_spin_button_field(
            ("spinbutton:not(.vertical)", "spinbutton.vertical > text")
        )

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
                for popover in ("popover > contents", "popover > arrow"):
                    for prop in (
                        "background-color", "border", "border-radius", "box-shadow"
                    ):
                        self.assertEqual(
                            self.rules[selector][prop], self.rules[popover][prop]
                        )
                self.assertEqual(
                    self.rules[selector]["color"], self.rules["window"]["color"]
                )

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
        self.assertEqual(
            self.rules["shortcut > .keycap"], {"border-radius": "0"}
        )
        self.assert_matches_frame("shortcut > .keycap", "border-radius")

    def test_card_corners(self):
        expected = {".card", "menubutton.card > button"}
        self.assertEqual(
            {selector for selector in self.rules if ".card" in selector},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                self.assert_matches_frame(selector, "border-radius")

    def test_emoji_completion_row_corners(self):
        expected = {"emoji-completion-row"}
        self.assertEqual(
            {selector for selector in self.rules if "emoji-completion-row" in selector},
            expected,
        )
        self.assertEqual(
            self.rules["emoji-completion-row"], {"border-radius": "0"}
        )
        self.assert_matches_frame("emoji-completion-row", "border-radius")

    def test_flowbox_item_corners(self):
        expected = {
            "flowbox > flowboxchild",
            # The selected view-child restatement names the same node.
            # The disabled-selected restatement names it again (2026-10-31).
            "flowbox > flowboxchild:selected",
            "flowbox > flowboxchild:selected:backdrop",
            "flowbox > flowboxchild:disabled:selected",
        }
        self.assertEqual(
            {selector for selector in self.rules if selector.startswith("flowbox")},
            expected,
        )
        self.assertEqual(
            self.rules["flowbox > flowboxchild"], {"border-radius": "0"}
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
        for selector in (
            "flowbox > flowboxchild:selected:backdrop",
            "gridview > child:selected:backdrop",
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

    def test_disabled_selected_row_and_child_arms(self):
        """Pin the disabled selected rows and children restated stock-twin."""
        self.assert_disabled_text((
            "row:disabled:selected",
            "flowbox > flowboxchild:disabled:selected",
            "gridview > child:disabled:selected",
            "columnview.view:disabled:selected",
            "treeview.view:disabled:selected",
            "columnview.view:disabled:selected:backdrop",
            "treeview.view:disabled:selected:backdrop",
            "label:disabled:selected",
            "textview > text:disabled:selected",
            "textview > text:disabled:selected:focus",
        ))
        # The family adds the calendar stock twin alongside the row/view
        # arms; stock has no big :backdrop disabled group here, so backdrop
        # members are the dedicated view arms. The calendar member is pinned
        # against stock by this exact set assertion.
        # 2026-10-31: selected text arms and the generic .view disabled twin
        # are restated by their focused plan entries.
        self.assertEqual(
            {
                s for s in self.rules if ":disabled:selected" in s
            },
            {
                "row:disabled:selected",
                "flowbox > flowboxchild:disabled:selected",
                "gridview > child:disabled:selected",
                "columnview.view:disabled:selected",
                "treeview.view:disabled:selected",
                "columnview.view:disabled:selected:backdrop",
                "treeview.view:disabled:selected:backdrop",
                "calendar > grid > label.day-number:disabled:selected",
                ".view:disabled:selected",
                "label:disabled:selected",
                "textview > text:disabled:selected",
                "textview > text:disabled:selected:focus",
            },
        )

    def test_gridview_item_corners(self):
        expected = {
            "gridview > child",
            "filechooser gridview > child",
            # The filechooser undershoot mirror names the same view substring.
            "filechooser gridview ~ undershoot.top",
            # The selected view-child restatement names the same nodes.
            # The disabled-selected restatement names it again (2026-10-31).
            "gridview > child:selected",
            "gridview > child:selected:backdrop",
            "gridview > child:disabled:selected",
            "filechooser gridview child:selected",
            "filechooser gridview child:selected:hover",
            "filechooser gridview child:selected:active",
        }
        self.assertEqual(
            {selector for selector in self.rules if "gridview" in selector},
            expected,
        )
        for selector in sorted(
            {"gridview > child", "filechooser gridview > child"}
        ):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                self.assert_matches_frame(selector, "border-radius")

    def test_iconview_selected_arms(self):
        """Pin the selected icon view restated off the landed row selection."""
        for selector in (
            "iconview.view:selected",
            "iconview.view:selected:focus",
            "iconview.view:backdrop:selected",
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
        self.assert_matches_frame("iconview.view:selected", "border-radius")
        # The family keeps the landed DND drop border as its only other
        # icon-view rule: a renamed restated arm leaves exactly its successor.
        self.assertEqual(
            {selector for selector in self.rules if "iconview" in selector},
            {
                "iconview > dndtarget:drop(active)",
                "iconview.view:selected",
                "iconview.view:selected:focus",
                "iconview.view:backdrop:selected",
            },
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
        self.assertEqual(
            self.rules["window.assistant .sidebar > label"],
            {"border-radius": "0"},
        )
        self.assert_matches_frame("window.assistant .sidebar > label", "border-radius")

    def test_emoji_picker_cell_corners(self):
        expected = {
            "popover.emoji-picker emoji",
            # The undershoot mirrors name the same picker substring.
            "popover.emoji-picker scrolledwindow.view:not(.undershoot-top) > undershoot.top",
            "popover.emoji-picker window.print:not(.ssd-frame) "
            "scrolledwindow.dialog-action-box:not(.undershoot-top) > undershoot.top",
            "window.print:not(.ssd-frame) popover.emoji-picker "
            "scrolledwindow.dialog-action-box:not(.undershoot-top) > undershoot.top",
            "popover.emoji-picker scrolledwindow.view:not(.undershoot-bottom) > undershoot.bottom",
            "popover.emoji-picker window.print:not(.ssd-frame) "
            "scrolledwindow.dialog-action-box:not(.undershoot-bottom) > undershoot.bottom",
            "window.print:not(.ssd-frame) popover.emoji-picker "
            "scrolledwindow.dialog-action-box:not(.undershoot-bottom) > undershoot.bottom",
        }
        self.assertEqual(
            {selector for selector in self.rules if "emoji-picker" in selector},
            expected,
        )
        self.assertEqual(
            self.rules["popover.emoji-picker emoji"], {"border-radius": "0"}
        )
        self.assert_matches_frame("popover.emoji-picker emoji", "border-radius")

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

    def test_split_button_container_corners(self):
        self.assertEqual(
            {selector for selector in self.rules if "splitbutton" in selector},
            {"splitbutton"},
        )
        splitbutton = self.rules["splitbutton"]
        self.assertEqual(splitbutton, {"border-radius": "0"})
        for selector in ("frame > border", ".frame", "button"):
            with self.subTest(selector=selector):
                self.assertEqual(
                    splitbutton["border-radius"],
                    self.rules[selector]["border-radius"],
                )

    def test_navigation_sidebar_item_corners(self):
        expected = {
            ".navigation-sidebar > row",
            ".navigation-sidebar > child",
            ".navigation-sidebar > flowboxchild",
        }
        self.assertEqual(
            {selector for selector in self.rules
             if selector.startswith(".navigation-sidebar > ")},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                self.assert_matches_frame(selector, "border-radius")

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
        self.assertEqual(
            {selector for selector in self.rules
             if any(selector == root or selector.startswith(root + " ")
                    for root in roots)},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                self.assert_matches_frame(selector, "border-radius")

    def test_separate_boxed_row_corners(self):
        expected = {
            "list.boxed-list-separate > row",
            "list.boxed-list-separate > row.expander row.header",
            "list.boxed-list-separate > row.expander:not(:checked) row.header",
            "list.boxed-list-separate > row.expander.expander:checked list.nested",
            "list.boxed-list-separate > row.expander.expander:checked list.nested > row:last-child",
        }
        self.assertEqual(
            {selector for selector in self.rules
             if "list.boxed-list-separate" in selector},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                self.assert_matches_frame(selector, "border-radius")

    def test_color_swatch_corners(self):
        self.assert_color_swatch_corners(" > overlay")

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

    def test_progressbar(self):
        self.assert_progressbar(
            trough="progressbar > trough",
            progress="progressbar > trough > progress",
            disabled="progressbar > trough > progress:disabled",
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

    def test_osd_container_bands(self):
        selectors = (
            ".osd .scale-popup",
            ".app-notification",
            ".rich-list > header",
            ".osd popover.background > arrow",
            ".osd popover.background > contents",
            "popover.background.touch-selection > arrow",
            "popover.background.touch-selection > contents",
            "popover.background.magnifier > arrow",
            "popover.background.magnifier > contents",
            ".osd",
            ".osd popover.background",
            ".toolbar.osd",
            ".osd popover",
            "popover.touch-selection",
            "popover.magnifier",
            ".osd popover > arrow",
            ".osd popover > contents",
            "popover.touch-selection > arrow",
            "popover.touch-selection > contents",
            "popover.magnifier > arrow",
            "popover.magnifier > contents",
        )
        expected = {
            **INFOBAR,
            "background-image": "none",
            "border": "0",
            "border-radius": "0",
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], expected)
                infobar = self.rules["infobar > revealer > box"]
                for prop in INFOBAR:
                    self.assertEqual(self.rules[selector][prop], infobar[prop])

        arms = {
            f".osd {node}{state}"
            for node in ("check", "radio")
            for state in ("", ":hover", ":active", ":disabled")
        }
        landed = {
            "video image.osd",
            "progressbar.osd > trough",
            "progressbar.osd.horizontal > trough",
            "progressbar.osd.vertical > trough",
            ".osd switch:checked",
            ".osd progressbar > trough",
            ".osd scale > trough",
            ".osd scale > trough > fill",
            ".osd scale > trough > highlight",
            ".osd progressbar > trough > progress",
            ".osd progressbar > trough:disabled",
            ".osd scale > trough:disabled",
            ".osd scale > trough > fill:disabled",
            ".osd scale > trough > highlight:disabled",
            ".osd progressbar > trough > progress:disabled",
            ".osd scale > trough > slider",
            ".osd scale > trough > slider:hover",
            ".osd scale > trough > slider:active",
            ".osd scale > trough > slider:disabled",
        } | arms
        tokens = (
            "osd",
            "touch-selection",
            "magnifier",
            "scale-popup",
            "app-notification",
            "rich-list",
        )
        self.assertEqual(
            {
                selector
                for selector in self.selectors
                if "button" not in selector
                and any(token in selector for token in tokens)
            },
            set(selectors) | landed,
        )

    def test_osd_check_radio(self):
        """Pin the four restated stock OSD indicator arms.

        No collected reference screenshot shows a check or radio inside a
        GTK OSD overlay, so the sheet restates the toolkit resource's four
        `.osd check`/`.osd radio` arms with the landed plain check and radio
        recipes (CHECK and RADIO in ``support.gtk_theme_spec.py``) plus one
        clearance the stock arms claim: a black focus-outline colour in
        place of the toolkit's accent-tinted ring. The arm selectors and
        states come from /org/gtk/libgtk/theme/Default/Default-dark.css and
        Default-light.css in /usr/lib/x86_64-linux-gnu/libgtk-4.so.1
        (libgtk-4 4.18.6); each arm is byte-for-byte the recipe in every
        state, because the armed spellings set no geometry, glyph source or
        checked spelling stock could override.
        """
        check = {**CHECK, "outline-color": BLACK}
        radio = {**RADIO, "outline-color": BLACK}
        states = ("", ":hover", ":active", ":disabled")
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
            [check] * 4,
        )
        self.assertEqual(
            [dict(parsed[f".osd radio{state}"]) for state in states],
            [radio] * 4,
        )
        self.assertEqual(
            {selector for selector in self.rules
             if ".osd check" in selector or ".osd radio" in selector},
            set(expected),
        )

    def test_osd_progress_scale(self):
        progress_trough = PROGRESSBAR_TROUGH
        scale_trough = SCALE_TROUGH
        fill = SCALE_EMPTY_FILL
        progress = PROGRESSBAR_PROGRESS
        disabled_progress = {**PROGRESSBAR_PROGRESS, "background-color": GREY}
        expected = {
            ".osd progressbar > trough": progress_trough,
            ".osd scale > trough": scale_trough,
            ".osd scale > trough > fill": fill,
            ".osd scale > trough > highlight": fill,
            ".osd progressbar > trough > progress": progress,
            ".osd progressbar > trough:disabled": progress_trough,
            ".osd scale > trough:disabled": scale_trough,
            ".osd scale > trough > fill:disabled": fill,
            ".osd scale > trough > highlight:disabled": fill,
            ".osd progressbar > trough > progress:disabled": disabled_progress,
        }
        for selector, recipe in expected.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], recipe)
        self.assertEqual(
            self.rules[".osd scale > trough > fill"],
            self.rules[".osd scale > trough > highlight"],
        )
        self.assertEqual(
            self.rules[".osd progressbar > trough > progress:disabled"]["background-color"],
            self.rules["progressbar > trough > progress:disabled"]["background-color"],
        )
        node_names = ("trough", "fill", "highlight", "progress")
        self.assertEqual(
            {
                selector for selector in self.selectors
                if ".osd" in selector
                and "slider" not in selector
                and any(node in selector for node in node_names)
            } - {
                "progressbar.osd > trough",
                "progressbar.osd.horizontal > trough",
                "progressbar.osd.vertical > trough",
            },
            set(expected),
        )

    def test_osd_scale_thumbs(self):
        """Pin the four OSD scale-thumb arms to the ordinary thumb recipes."""
        enabled = {
            **SCALE_THUMB,
            "color": BLACK,
            "outline-color": BLACK,
            "background-clip": "border-box",
        }
        disabled = {
            **enabled,
            "border": f"1px solid {GREY}",
            "box-shadow": "none",
        }
        expected = {
            ".osd scale > trough > slider": enabled,
            ".osd scale > trough > slider:hover": enabled,
            ".osd scale > trough > slider:active": enabled,
            ".osd scale > trough > slider:disabled": disabled,
        }
        for selector, recipe in expected.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], recipe)
        plain_disabled = self.rules["scale > trough > slider:disabled"]
        self.assertEqual(disabled["border"], plain_disabled["border"])
        self.assertEqual(disabled["box-shadow"], plain_disabled["box-shadow"])
        self.assertEqual(
            {selector for selector in self.rules
             if ".osd" in selector and "slider" in selector},
            set(expected),
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
        for selector, declarations in expected.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], declarations)

    def test_progressbar_oriented_trough_thickness(self):
        horizontal = "progressbar.horizontal > trough"
        vertical = "progressbar.vertical > trough"
        expected = {
            horizontal: {"min-height": self.rules["progressbar > trough"]["min-height"]},
            vertical: {"min-width": self.rules["progressbar > trough"]["min-width"]},
        }
        self.assertEqual(expected[horizontal]["min-height"], PROGRESSBAR_TROUGH["min-height"])
        self.assertEqual(expected[vertical]["min-width"], PROGRESSBAR_TROUGH["min-width"])
        for selector, declarations in expected.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], declarations)

    def test_progressbar_directional_corners(self):
        self.assert_rule("progressbar > trough > progress", {"border-radius": "0"})
        for direction in ("left", "right", "top", "bottom"):
            with self.subTest(direction=direction):
                self.assert_rule(
                    f"progressbar > trough > progress.{direction}",
                    {"border-radius": "0"},
                )

    def test_progressbar_disabled_filter(self):
        self.assert_rule("progressbar:disabled", {"filter": "none"})
        self.assert_rule(
            "progressbar > trough > progress:disabled",
            {"background-color": GREY},
        )

    def test_entry_progress(self):
        self.assert_rule("entry > progress > trough > progress", ENTRY_PROGRESS_GTK4)
        self.assert_rule("entry > progress > trough", {"min-height": "2px"})
        self.assert_rule("entry > progress", {"margin-bottom": "1px"})

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

    def test_switch_track_padding(self):
        self.assert_rule("switch", {"padding": "0"})

    def test_scale(self):
        self.assert_scale(
            trough="scale > trough",
            fill=("scale > trough > fill", "scale > trough > highlight"),
            slider="scale > trough > slider",
            horizontal="scale.horizontal > trough > slider",
            vertical="scale.vertical > trough > slider",
            disabled="scale > trough > slider:disabled",
        )

    def test_scale_fine_tune_thumb_margin(self):
        for selector in (
            "scale.horizontal.fine-tune > trough > slider",
            "scale.vertical.fine-tune > trough > slider",
        ):
            self.assert_rule(selector, {"margin": "-5px"})

    def test_scale_fine_tune_trough_margin(self):
        for selector in (
            "scale.horizontal.fine-tune > trough",
            "scale.vertical.fine-tune > trough",
        ):
            self.assert_rule(selector, {"margin": "0"})

    def test_scale_marked_thumb_transform(self):
        for selector in (
            "scale.marks-before:not(.marks-after) > trough > slider",
            "scale.marks-after:not(.marks-before) > trough > slider",
        ):
            self.assert_rule(selector, {"transform": "none"})

    def test_scale_enabled_marked_thumb_shadow(self):
        for selector in (
            "scale.marks-before:not(.marks-after):not(:disabled) > trough > slider:not(:disabled)",
            "scale.marks-after:not(.marks-before):not(:disabled) > trough > slider:not(:disabled)",
        ):
            self.assert_rule(selector, {"box-shadow": RAISED_BEVEL})

    def test_scale_disabled_filter(self):
        self.assert_rule("scale:disabled", {"filter": "none"})

    def test_scale_disabled_parent_shadow(self):
        self.assert_rule("scale:disabled > trough > slider", {"box-shadow": "none"})

    def test_scale_disabled_marked_thumb_shadow(self):
        for selector in (
            "scale.marks-before:not(.marks-after) > trough > slider:disabled",
            "scale.marks-after:not(.marks-before) > trough > slider:disabled",
            "scale.marks-before:not(.marks-after):disabled > trough > slider",
            "scale.marks-after:not(.marks-before):disabled > trough > slider",
        ):
            self.assert_rule(selector, {"box-shadow": "none"})

    def test_scale_parent_interaction_face(self):
        for selector in (
            "scale:hover > trough > slider",
            "scale:active > trough > slider",
        ):
            self.assert_rule(selector, {"background-color": FACE})

    def test_scale_parent_interaction_trough_face(self):
        for selector in ("scale:hover > trough", "scale:active > trough"):
            self.assert_rule(selector, {"background-color": TROUGH})

    def test_scale_parent_interaction_highlight_image(self):
        for selector in (
            "scale:hover > trough > highlight",
            "scale:active > trough > highlight",
        ):
            self.assert_rule(selector, {"background-image": "none"})

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
                with mock.patch.object(gtk_css, "ROOT", root):
                    with self.assertRaisesRegex(
                        ValueError, "symlink escape"
                    ) as caught:
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

class TestCalendarDisabledGreyReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = PROFILER_REFERENCE
    MAX_ROWS = PROFILER_ROWS

    def test_disabled_day_grey_matches_reference_palette_pixel(self):
        _, rules, _ = parse_css(gtk_css.read_theme_text(CSS))
        sampled = hex_colour(self.pixel(241, 103))
        for selector in (
            "calendar:disabled > grid > label.day-number",
            "calendar > grid > label.day-number:disabled:selected",
        ):
            with self.subTest(selector=selector):
                self.assertEqual(rules[selector]["color"], sampled)


if __name__ == "__main__":
    unittest.main()
