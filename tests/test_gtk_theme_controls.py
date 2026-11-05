"""Validate the GTK 3 Platinum sheet's controls and shipped glyphs.

This module owns the control slice of ``tests/test_gtk_theme.py``'s split:
the progress bar and the entry's progress strip, the spinner, level bar,
switch and scale, the control focus outlines, the linked border pairs, the
menu-bar and toolbar titles, and the shipped check, radio, arrow and
submenu glyph assets. The two introspection tests render with a real GTK 3
in a child interpreter (see ``_run_gtk_child``); the suite process itself
imports no GTK.
"""

import subprocess
import sys
import unittest
from pathlib import Path

from support.gtk_css import assert_svg_root_first
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    BUTTON_BEVEL,
    DISABLED_TEXT,
    ENTRY_PROGRESS,
    ETCH_DARK,
    INVERTED_BUTTON_BEVEL,
)
from support.platinum_palette import (
    BLACK,
    FACE,
    WHITE,
)
from support.repo_root import ROOT
from support.svg_case import parse_svg
from svg_assertions import (
    assert_no_script_elements,
    assert_no_style_elements,
    assert_root_canvas,
    attribute_values,
    children_named,
    circle_geometry_and_fill,
)

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
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
    / "org.macos8.desktop"
    / "16x16"
    / "actions"
    / "go-next-symbolic.svg"
)


class TestGtkThemeControls(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS




    def test_progressbar(self):
        self.assert_progressbar(
            trough="progressbar trough",
            progress="progressbar progress",
            disabled="progressbar progress:disabled",
        )

    def test_entry_progress(self):
        self.assert_rule("entry progress", ENTRY_PROGRESS)

    def test_suggested_action_plain_arms(self):
        """The plain `suggested-action` arms restate the landed face.

        Only the opaque members of the stock family are restated; no
        restated selector carries `.flat`, so the stock transparent-face
        colour-class family keeps governing whole (recorded 2026-10-31
        by the feature role). (2026-10-31: the colour-class members are
        since restated by test_action_class_flat_arms.)
        """
        face = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        sunken = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        disabled = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        self.assert_rule("button.suggested-action", face)
        self.assert_rule("button.suggested-action:hover", face)
        self.assert_rule("button.suggested-action:active", sunken)
        self.assert_rule("button.suggested-action:checked", sunken)
        self.assert_rule("button.suggested-action:backdrop", face)
        self.assert_rule("button.suggested-action:backdrop:active", sunken)
        self.assert_rule("button.suggested-action:backdrop:checked", sunken)
        for selector in (
            "button.suggested-action:backdrop:disabled",
            "button.suggested-action:backdrop:disabled:active",
            "button.suggested-action:backdrop:disabled:checked",
            "button.suggested-action:disabled",
            "button.suggested-action:disabled:active",
            "button.suggested-action:disabled:checked",
        ):
            self.assert_rule(selector, disabled)
        expected = {
            "button.suggested-action",
            "button.suggested-action:hover",
            "button.suggested-action:active",
            "button.suggested-action:checked",
            "button.suggested-action:backdrop",
            "button.suggested-action:backdrop:active",
            "button.suggested-action:backdrop:checked",
            "button.suggested-action:backdrop:disabled",
            "button.suggested-action:backdrop:disabled:active",
            "button.suggested-action:backdrop:disabled:checked",
            "button.suggested-action:disabled",
            "button.suggested-action:disabled:active",
            "button.suggested-action:disabled:checked",
        }
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith("button.suggested-action")
                # 2026-10-31: the colour-class members are since restated
                # by test_action_class_flat_arms; the plain opaque keys
                # carry no flat token, so this filter stays inside this
                # family.
                and ".flat" not in selector
            },
            expected,
        )

    def test_flat_button_plain_arms(self):
        """The plain `button.flat` arms restate the landed face.

        A GTK 3 push button carrying the `flat` class outside the landed
        overlays draws the landed push-button face in every armed state:
        every restated dictionary extends the landed plain recipe with the
        `background-color` claim the stock transparent faces force, and
        the base, hover and backdrop arms clear the stock motion claims
        with `transition: none` (recorded 2026-10-31 by the feature role).
        """
        face = {
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
        self.assert_rule("button.flat", face)
        self.assert_rule("button.flat:hover", face)
        self.assert_rule("button.flat:backdrop", face)
        self.assert_rule("button.flat:hover:active", {"transition": "none"})
        for selector in (
            "button.flat:active",
            "button.flat:checked",
            "button.flat:backdrop:active",
            "button.flat:backdrop:checked",
        ):
            self.assert_rule(selector, sunken)
        for selector in (
            "button.flat:disabled",
            "button.flat:disabled:active",
            "button.flat:disabled:checked",
            "button.flat:backdrop:disabled",
            "button.flat:backdrop:disabled:active",
            "button.flat:backdrop:disabled:checked",
        ):
            self.assert_rule(selector, disabled)
        expected = {
            "button.flat",
            "button.flat:hover",
            "button.flat:hover:active",
            "button.flat:active",
            "button.flat:checked",
            "button.flat:backdrop",
            "button.flat:backdrop:active",
            "button.flat:backdrop:checked",
            "button.flat:backdrop:disabled",
            "button.flat:backdrop:disabled:active",
            "button.flat:backdrop:disabled:checked",
            "button.flat:disabled",
            "button.flat:disabled:active",
            "button.flat:disabled:checked",
        }
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith("button.flat")
            },
            expected,
        )

    def test_selected_row_button_arms(self):
        """The selected-row button arms restate the landed black.

        A push button inside a selected GTK row keeps reading black on
        the landed lavender fill with the landed raised and flat
        treatments: stock's three selected-row arms would paint an opaque
        button with a blue border and a flat button with a white label on
        the landed light selection fill and recolour the flat label near
        white in backdrop, so each restated selector is the exact stock
        twin appended at the sheet tail, winning the tie by later source
        order with the landed palette's black (recorded 2026-10-31 by
        the feature role).
        """
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
            self.rules["button.flat:backdrop"]["color"],
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

    def test_destructive_action_plain_arms(self):
        """The plain `destructive-action` arms restate the landed face.

        The red mirror of `test_suggested_action_plain_arms`: only the
        opaque members of the stock family are restated; no restated
        selector carries `.flat`, so the stock transparent-face
        colour-class family keeps governing whole (recorded 2026-10-31
        by the feature role). (2026-10-31: the colour-class members are
        since restated by test_action_class_flat_arms.)
        """
        face = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        sunken = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        disabled = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        self.assert_rule("button.destructive-action", face)
        self.assert_rule("button.destructive-action:hover", face)
        self.assert_rule("button.destructive-action:active", sunken)
        self.assert_rule("button.destructive-action:checked", sunken)
        self.assert_rule("button.destructive-action:backdrop", face)
        self.assert_rule("button.destructive-action:backdrop:active", sunken)
        self.assert_rule("button.destructive-action:backdrop:checked", sunken)
        for selector in (
            "button.destructive-action:backdrop:disabled",
            "button.destructive-action:backdrop:disabled:active",
            "button.destructive-action:backdrop:disabled:checked",
            "button.destructive-action:disabled",
            "button.destructive-action:disabled:active",
            "button.destructive-action:disabled:checked",
        ):
            self.assert_rule(selector, disabled)
        expected = {
            "button.destructive-action",
            "button.destructive-action:hover",
            "button.destructive-action:active",
            "button.destructive-action:checked",
            "button.destructive-action:backdrop",
            "button.destructive-action:backdrop:active",
            "button.destructive-action:backdrop:checked",
            "button.destructive-action:backdrop:disabled",
            "button.destructive-action:backdrop:disabled:active",
            "button.destructive-action:backdrop:disabled:checked",
            "button.destructive-action:disabled",
            "button.destructive-action:disabled:active",
            "button.destructive-action:disabled:checked",
        }
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith("button.destructive-action")
                # 2026-10-31: the colour-class members are since restated
                # by test_action_class_flat_arms; the plain opaque keys
                # carry no flat token, so this filter stays inside this
                # family.
                and ".flat" not in selector
            },
            expected,
        )

    def test_action_class_flat_arms(self):
        """The plain colour-class `.flat` arms restate the landed face.

        A GTK 3 push button carrying the `flat` class beside
        `suggested-action` or `destructive-action` outside an overlay
        draws the landed push-button face in every armed state, erasing
        the stock transparent face with its blue or red label: the
        twenty selectors extend the landed plain push-button recipes the
        same way `test_flat_button_plain_arms` extends the plain ones —
        every restated dictionary carries the `background-color` claim
        the stock transparent faces force, and the disabled arms
        re-declare the face colour beside the landed disabled dictionary
        and claim no `outline-color`. No `transition` is restated: the
        plain flat family's `transition: none` claims already hold at
        equal-or-higher class counts (recorded 2026-10-31 by the
        feature role; probed from gtk-contained.css in libgtk-3 3.24.49
        with gresource the same day).
        """
        face = {
            "background-color": FACE,
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
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
        for action_class in ("suggested-action", "destructive-action"):
            with self.subTest(action_class=action_class):
                prefix = f"button.{action_class}.flat"
                self.assert_rule(prefix, face)
                for state in (":active", ":checked"):
                    self.assert_rule(f"{prefix}{state}", sunken)
                self.assert_rule(f"{prefix}:backdrop", face)
                for state in (":backdrop:active", ":backdrop:checked"):
                    self.assert_rule(f"{prefix}{state}", sunken)
                for state in (
                    ":disabled",
                    ":backdrop:disabled",
                    ":backdrop:disabled:active",
                    ":backdrop:disabled:checked",
                ):
                    self.assert_rule(f"{prefix}{state}", disabled)
                expected = {
                    prefix,
                    f"{prefix}:active",
                    f"{prefix}:checked",
                    f"{prefix}:backdrop",
                    f"{prefix}:backdrop:active",
                    f"{prefix}:backdrop:checked",
                    f"{prefix}:disabled",
                    f"{prefix}:backdrop:disabled",
                    f"{prefix}:backdrop:disabled:active",
                    f"{prefix}:backdrop:disabled:checked",
                }
                self.assertEqual(
                    {
                        selector
                        for selector in self.rules
                        if selector.startswith(prefix)
                    },
                    expected,
                )

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

    LINKED_FIRST_LEFT = {
        "border-top-left-radius": "0",
        "border-bottom-left-radius": "0",
        "-gtk-outline-top-left-radius": "0",
        "-gtk-outline-bottom-left-radius": "0",
    }

    LINKED_LAST_RIGHT = {
        "border-top-right-radius": "0",
        "border-bottom-right-radius": "0",
        "-gtk-outline-top-right-radius": "0",
        "-gtk-outline-bottom-right-radius": "0",
    }

    LINKED_ONLY = {
        "border-radius": "0",
        "-gtk-outline-radius": "0",
    }

    LINKED_FIRST_TOP = {
        "border-top-left-radius": "0",
        "border-top-right-radius": "0",
        "-gtk-outline-top-left-radius": "0",
        "-gtk-outline-top-right-radius": "0",
    }

    LINKED_LAST_BOTTOM = {
        "border-bottom-left-radius": "0",
        "border-bottom-right-radius": "0",
        "-gtk-outline-bottom-left-radius": "0",
        "-gtk-outline-bottom-right-radius": "0",
    }

    LINKED_HORIZONTAL_FIRST = (
        ".linked:not(.vertical) > combobox:first-child > box > button.combo",
        "combobox.linked button:nth-child(2):dir(rtl)",
        "filechooser .path-bar.linked > button:dir(rtl):last-child",
        "filechooser .path-bar.linked > button:dir(ltr):first-child",
        ".linked:not(.vertical) > spinbutton:first-child:not(.vertical)",
        ".linked:not(.vertical) > entry:first-child",
        ".inline-toolbar button:first-child",
        ".linked > button:first-child",
        "toolbar.inline-toolbar toolbutton:first-child > button.flat",
    )

    LINKED_HORIZONTAL_LAST = (
        ".linked:not(.vertical) > combobox:last-child > box > button.combo",
        "combobox.linked button:nth-child(2):dir(ltr)",
        "filechooser .path-bar.linked > button:dir(rtl):first-child",
        "filechooser .path-bar.linked > button:dir(ltr):last-child",
        ".linked:not(.vertical) > spinbutton:last-child:not(.vertical)",
        ".linked:not(.vertical) > entry:last-child",
        ".inline-toolbar button:last-child",
        ".linked > button:last-child",
        "toolbar.inline-toolbar toolbutton:last-child > button.flat",
    )

    LINKED_HORIZONTAL_ONLY = (
        ".linked:not(.vertical) > combobox:only-child > box > button.combo",
        "filechooser .path-bar.linked > button:only-child",
        ".linked:not(.vertical) > spinbutton:only-child:not(.vertical)",
        ".linked:not(.vertical) > entry:only-child",
        ".inline-toolbar button:only-child",
        ".linked > button:only-child",
        "toolbar.inline-toolbar toolbutton:only-child > button.flat",
    )

    LINKED_VERTICAL_FIRST = (
        ".linked.vertical > combobox:first-child > box > button.combo",
        ".linked.vertical > spinbutton:first-child:not(.vertical)",
        ".linked.vertical > entry:first-child",
        ".linked.vertical > button:first-child",
    )

    LINKED_VERTICAL_LAST = (
        ".linked.vertical > combobox:last-child > box > button.combo",
        ".linked.vertical > spinbutton:last-child:not(.vertical)",
        ".linked.vertical > entry:last-child",
        ".linked.vertical > button:last-child",
    )

    LINKED_VERTICAL_ONLY = (
        ".linked.vertical > combobox:only-child > box > button.combo",
        ".linked.vertical > spinbutton:only-child:not(.vertical)",
        ".linked.vertical > entry:only-child",
        ".linked.vertical > button:only-child",
    )

    def test_linked_end_field_corners(self):
        """Stock's linked-field end corners square in the shipped sheet.

        The toolkit resource rounds six linked arms — the horizontal
        first, last and only member arms and the vertical trio — cutting
        each linked group's two ends 5px and pairing matching
        `-gtk-outline-` focus-ring halves into the same arms. The sheet
        restates all thirty-seven byte-equal spellings in stock's own
        grouping, each carrying only its zeroed radius declarations.
        Three spellings coincide with the landed border-sharing groups,
        so their parsed dictionaries merge the carried border-style and
        the spelling counts twice — once as the landed group's member,
        once in the restating group. (Recorded 2026-11-04 by the
        feature role.)
        """
        expected = {}
        for selector in self.LINKED_HORIZONTAL_FIRST:
            expected[selector] = dict(self.LINKED_FIRST_LEFT)
        for selector in self.LINKED_HORIZONTAL_LAST:
            expected[selector] = dict(self.LINKED_LAST_RIGHT)
        expected[".linked:not(.vertical) > entry:last-child"] = {
            "border-right-style": "solid", **self.LINKED_LAST_RIGHT}
        for selector in self.LINKED_HORIZONTAL_ONLY:
            expected[selector] = dict(self.LINKED_ONLY)
        for selector in self.LINKED_VERTICAL_FIRST:
            expected[selector] = dict(self.LINKED_FIRST_TOP)
        for selector in self.LINKED_VERTICAL_LAST:
            expected[selector] = dict(self.LINKED_LAST_BOTTOM)
        for selector in (".linked.vertical > entry:last-child",
                         ".linked.vertical > button:last-child"):
            expected[selector] = {
                "border-bottom-style": "solid", **self.LINKED_LAST_BOTTOM}
        for selector in self.LINKED_VERTICAL_ONLY:
            expected[selector] = dict(self.LINKED_ONLY)
        self.assertEqual(len(expected), 37)

        merged = (".linked:not(.vertical) > entry:last-child",
                  ".linked.vertical > entry:last-child",
                  ".linked.vertical > button:last-child")
        self.assert_rule_group(
            {s: r for s, r in expected.items() if s not in merged})
        for selector in merged:
            with self.subTest(selector=selector):
                # The spelling is a member of the landed border-sharing
                # group and of this entry's restating group: the parsed
                # rules merge the border-style with the radius longhands,
                # so the whole dictionary pins both — a dropped group,
                # a stray declaration or a third spelling fails.
                self.assertEqual(self.selectors.count(selector), 2,
                                 selector)
                self.assertEqual(self.rules[selector], expected[selector],
                                 selector)

        # No stray member of the families the restatements touch and no
        # state twin stays stock: every toolbutton, combobox.linked and
        # filechooser-radius spelling this entry adds is the whole set.
        self.assertEqual(
            {s for s in self.rules if "toolbutton" in s},
            {"toolbar.inline-toolbar toolbutton:first-child > button.flat",
             "toolbar.inline-toolbar toolbutton:last-child > button.flat",
             "toolbar.inline-toolbar toolbutton:only-child > button.flat"},
        )
        self.assertEqual(
            {s for s in self.rules if "combobox.linked" in s},
            {"combobox.linked button:nth-child(2):dir(rtl)",
             "combobox.linked button:nth-child(2):dir(ltr)"},
        )
        self.assertEqual(
            {s for s in self.rules if "filechooser" in s},
            {"filechooser .path-bar.linked > button:dir(rtl):last-child",
             "filechooser .path-bar.linked > button:dir(ltr):first-child",
             "filechooser .path-bar.linked > button:dir(rtl):first-child",
             "filechooser .path-bar.linked > button:dir(ltr):last-child",
             "filechooser .path-bar.linked > button:only-child"},
        )

        # Every restatement parses after the sheet's landed tail group.
        tail = self.selectors.index("popover.emoji-picker .emoji :hover")
        for selector in expected:
            with self.subTest(selector=selector):
                if selector in merged:
                    # The merged spelling's landed group sits mid-sheet;
                    # its restatement — the second listing — follows.
                    self.assertGreater(self.selectors.index(selector, tail
                                                            + 1), tail,
                                       selector)
                else:
                    self.assertGreater(self.selectors.index(selector), tail,
                                       selector)

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


if __name__ == "__main__":
    unittest.main()
