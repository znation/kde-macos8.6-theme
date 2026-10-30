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
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    BASE_DEFINED_COLOURS,
    CALENDAR_SELECTED_DAY,
    COMBO_ARROW,
    ENTRY_PROGRESS_GTK4,
    ETCH_DARK,
    LINK,
    MENUBUTTON_ARROWS,
    VISITED_LINK,
    MENU_CHECK,
    PROGRESSBAR_TROUGH,
    RAISED_BEVEL,
    ROW_HOVER,
    ROW_SELECTED,
    TAB_STATES,
    TITLE_BUTTON_IMAGE,
    TITLE_BUTTON_IMAGE_STATE,
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

class TestGtk4Theme(GtkSheetRuleCases, unittest.TestCase):
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

    @classmethod
    def setUpClass(cls):
        cls.css = gtk_css.read_theme_text(CSS)
        cls.colours, cls.rules, cls.selectors = parse_css(
            cls.css, source=str(CSS.relative_to(ROOT))
        )

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
            ("text > selection", "label > selection")
        )

    def test_disabled_text(self):
        self.assert_disabled_text(
            ("label:disabled", "text:disabled", "spinbutton.vertical > text:disabled")
        )

    def test_view_background(self):
        self.assert_view_background((".view", "list"))

    def test_links(self):
        self.assert_links(
            ("button.link",),
            ("link", "button.link > label"),
            ("link:visited", "button.link:visited > label"),
            {"text-decoration": "underline"},
        )

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
        for frame in ("frame > border", ".frame"):
            with self.subTest(frame=frame):
                self.assertEqual(
                    self.rules[selected]["border-radius"],
                    self.rules[frame]["border-radius"],
                )

    def test_calendar_disabled_day_text(self):
        disabled = "calendar:disabled > grid > label.day-number"
        selected = "calendar > grid > label.day-number:selected"
        other_month = "calendar > grid > label.day-number.other-month"
        self.assert_rule(disabled, {"color": "#888888"})
        self.assertEqual(self.rules[disabled]["color"], self.rules["label:disabled"]["color"])
        self._assert_inactive_grey_from_scheme()
        self.assertGreater(self.css.index(disabled), self.css.index(selected))
        self.assertGreater(self.css.index(disabled), self.css.index(other_month))

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
        for frame in ("frame > border", ".frame"):
            with self.subTest(frame=frame):
                self.assertEqual(
                    self.rules[marked]["border-radius"],
                    self.rules[frame]["border-radius"],
                )

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
        for frame in ("frame > border", ".frame"):
            with self.subTest(frame=frame):
                self.assertEqual(
                    self.rules[calendar]["border"],
                    self.rules[frame]["border"],
                )

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

    def test_scale_focus_outline_color(self):
        focus = "scale:focus:focus-visible > trough > slider"
        self.assert_rule(focus, {"outline-color": BLACK})
        self.assertEqual(
            self.rules[focus]["outline-color"],
            self.rules["calendar > grid > label:focus"]["outline-color"],
        )

    def test_button_focus_outline_color(self):
        focus = "button:focus:focus-visible"
        scale_focus = "scale:focus:focus-visible > trough > slider"
        self.assert_rule(focus, {"outline-color": BLACK})
        self.assertEqual(
            self.rules[focus]["outline-color"],
            self.rules[scale_focus]["outline-color"],
        )

    def test_entry_focus_outline_color(self):
        focus = "entry:focus-within"
        scale_focus = "scale:focus:focus-visible > trough > slider"
        self.assert_rule(focus, {"outline-color": BLACK})
        self.assertEqual(
            self.rules[focus]["outline-color"],
            self.rules[scale_focus]["outline-color"],
        )

    def test_spinbutton_focus_outline_color(self):
        focus = "spinbutton:focus-within"
        scale_focus = "scale:focus:focus-visible > trough > slider"
        self.assert_rule(focus, {"outline-color": BLACK})
        self.assertEqual(
            self.rules[focus]["outline-color"],
            self.rules[scale_focus]["outline-color"],
        )

    def test_checkbutton_focus_outline_color(self):
        focus = "checkbutton:focus:focus-visible"
        scale_focus = "scale:focus:focus-visible > trough > slider"
        self.assert_rule(focus, {"outline-color": BLACK})
        self.assertEqual(
            self.rules[focus]["outline-color"],
            self.rules[scale_focus]["outline-color"],
        )

    def test_calendar_focus_transition(self):
        self.assert_rule("calendar > grid > label", {"transition": "none"})

    def test_scale_focus_transition(self):
        self.assert_rule("scale > trough > slider", {"transition": "none"})

    def test_button_focus_transition(self):
        self.assert_rule("button", {"transition": "none"})
        self.assertEqual(
            self.rules["button"]["transition"],
            self.rules["scale > trough > slider"]["transition"],
        )

    def test_entry_focus_transition(self):
        self.assert_rule("entry", {"transition": "none"})
        self.assertEqual(
            self.rules["entry"]["transition"],
            self.rules["scale > trough > slider"]["transition"],
        )

    def test_spinbutton_focus_transition(self):
        self.assert_rule("spinbutton", {"transition": "none"})
        self.assertEqual(
            self.rules["spinbutton"]["transition"],
            self.rules["scale > trough > slider"]["transition"],
        )

    def test_checkbutton_focus_transition(self):
        self.assert_rule("checkbutton", {"transition": "none"})
        self.assertEqual(
            self.rules["checkbutton"]["transition"],
            self.rules["scale > trough > slider"]["transition"],
        )

    def test_notebook_focus_transition(self):
        notebook_tab = "notebook > header > tabs > tab:checked"
        self.assert_rule(notebook_tab, {"transition": "none"})
        self.assertEqual(
            self.rules[notebook_tab]["transition"],
            self.rules["scale > trough > slider"]["transition"],
        )

    def test_notebook_focus_outline_color(self):
        focus = "notebook:focus:focus-visible > header > tabs > tab:checked"
        self.assert_rule(focus, {"outline-color": BLACK})
        self.assertEqual(
            self.rules[focus]["outline-color"],
            self.rules["scale:focus:focus-visible > trough > slider"]["outline-color"],
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
            "columnview.view:selected:backdrop",
            "listview > row.activatable:selected:backdrop",
        ))
        self.assertGreater(
            self.css.index("list row.activatable:selected:backdrop"),
            self.css.index("list row.activatable:selected:"),
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
        self.assert_rubberband(("rubberband",))

    def test_spin_button_field(self):
        self.assert_spin_button_field(
            ("spinbutton:not(.vertical)", "spinbutton.vertical > text")
        )

    def test_title_buttons(self):
        for scope in ("headerbar", ".titlebar"):
            for control, asset in (
                ("close", "window-close.svg"),
                ("maximize", "window-maximize.svg"),
                ("minimize", "window-minimize.svg"),
            ):
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

    def test_frame(self):
        self.assert_frame(("frame > border", ".frame"))

    def test_shortcut_keycap_corners(self):
        self.assertEqual(
            {selector for selector in self.rules if "keycap" in selector},
            {"shortcut > .keycap"},
        )
        keycap = self.rules["shortcut > .keycap"]
        self.assertEqual(keycap, {"border-radius": "0"})
        for frame in ("frame > border", ".frame"):
            with self.subTest(frame=frame):
                self.assertEqual(
                    keycap["border-radius"], self.rules[frame]["border-radius"]
                )

    def test_card_corners(self):
        expected = {".card", "menubutton.card > button"}
        self.assertEqual(
            {selector for selector in self.rules if ".card" in selector},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                for frame in ("frame > border", ".frame"):
                    self.assertEqual(
                        self.rules[selector]["border-radius"],
                        self.rules[frame]["border-radius"],
                    )

    def test_emoji_completion_row_corners(self):
        expected = {"emoji-completion-row"}
        self.assertEqual(
            {selector for selector in self.rules if "emoji-completion-row" in selector},
            expected,
        )
        row = self.rules["emoji-completion-row"]
        self.assertEqual(row, {"border-radius": "0"})
        for frame in ("frame > border", ".frame"):
            with self.subTest(frame=frame):
                self.assertEqual(row["border-radius"], self.rules[frame]["border-radius"])

    def test_flowbox_item_corners(self):
        expected = {"flowbox > flowboxchild"}
        self.assertEqual(
            {selector for selector in self.rules if selector.startswith("flowbox")},
            expected,
        )
        item = self.rules["flowbox > flowboxchild"]
        self.assertEqual(item, {"border-radius": "0"})
        for frame in ("frame > border", ".frame"):
            with self.subTest(frame=frame):
                self.assertEqual(item["border-radius"], self.rules[frame]["border-radius"])

    def test_gridview_item_corners(self):
        expected = {
            "gridview > child",
            "filechooser gridview > child",
            # The filechooser undershoot mirror names the same view substring.
            "filechooser gridview ~ undershoot.top",
        }
        self.assertEqual(
            {selector for selector in self.rules if "gridview" in selector},
            expected,
        )
        for selector in sorted(expected - {"filechooser gridview ~ undershoot.top"}):
            with self.subTest(selector=selector):
                item = self.rules[selector]
                self.assertEqual(item, {"border-radius": "0"})
                for frame in ("frame > border", ".frame"):
                    with self.subTest(frame=frame):
                        self.assertEqual(
                            item["border-radius"], self.rules[frame]["border-radius"]
                        )

    def test_assistant_step_label_corners(self):
        expected = {"window.assistant .sidebar > label"}
        self.assertEqual(
            {selector for selector in self.rules if "assistant" in selector},
            expected,
        )
        step_label = self.rules["window.assistant .sidebar > label"]
        self.assertEqual(step_label, {"border-radius": "0"})
        for frame in ("frame > border", ".frame"):
            with self.subTest(frame=frame):
                self.assertEqual(
                    step_label["border-radius"], self.rules[frame]["border-radius"]
                )

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
        cell = self.rules["popover.emoji-picker emoji"]
        self.assertEqual(cell, {"border-radius": "0"})
        for frame in ("frame > border", ".frame"):
            with self.subTest(frame=frame):
                self.assertEqual(cell["border-radius"], self.rules[frame]["border-radius"])

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
                for frame in ("frame > border", ".frame"):
                    self.assertEqual(
                        self.rules[selector]["border-radius"],
                        self.rules[frame]["border-radius"],
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
        self.assertEqual(
            {selector for selector in self.rules
             if any(selector == root or selector.startswith(root + " ")
                    for root in roots)},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], {"border-radius": "0"})
                for frame in ("frame > border", ".frame"):
                    self.assertEqual(
                        self.rules[selector]["border-radius"],
                        self.rules[frame]["border-radius"],
                    )

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
                for frame in ("frame > border", ".frame"):
                    self.assertEqual(
                        self.rules[selector]["border-radius"],
                        self.rules[frame]["border-radius"],
                    )

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
        focus = "switch:focus:focus-visible"
        self.assert_rule(focus, {"outline-color": BLACK})
        self.assertEqual(
            self.rules[focus]["outline-color"],
            self.rules["scale:focus:focus-visible > trough > slider"]["outline-color"],
        )

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
                           "dropdown > button"):
                self.assert_rule(
                    f"{css_class} > {member}",
                    {side: "none"},
                )

    def test_linked_last_member_restores_the_border(self):
        for css_class, side in ((".linked:not(.vertical)", "border-right-style"),
                                (".linked.vertical", "border-bottom-style")):
            for member in ("button:last-child", "entry:last-child",
                           "spinbutton:not(.vertical):last-child",
                           "dropdown > button:last-child"):
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
        self.assertEqual(rules["calendar:disabled > grid > label.day-number"]["color"],
                         hex_colour(self.pixel(241, 103)))


if __name__ == "__main__":
    unittest.main()
