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
        by the feature role).
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
