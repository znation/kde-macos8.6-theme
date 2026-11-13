"""Validate the GTK 3 Platinum sheet's controls and shipped glyphs.

This module owns the control slice of ``tests/test_gtk_theme.py``'s split:
the progress bar and the entry's progress strip, the spinner, level bar,
switch and scale, the control focus outlines, the linked border pairs, the
menu-bar and toolbar titles, the rendered notebook tab faces, and the
shipped check, radio, arrow and submenu glyph assets. The three
introspection tests render with a real GTK 3 in a child interpreter (see
``_run_gtk_child``); the suite process itself imports no GTK.
"""

import unittest
from pathlib import Path

from support.gtk_child_probe import (
    _GTK3_CHILD_HEAD,
    _GTK3_PIXEL_HEAD,
    _GTK3_SHEET_AND_WINDOW,
    run_gtk_child,
)
from support.gtk_css import assert_svg_root_first, strip_comments
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    BUTTON_BEVEL,
    DISABLED_TEXT,
    ENTRY_FIELD,
    ENTRY_PROGRESS,
    ETCH_DARK,
    INVERTED_BUTTON_BEVEL,
    RAISED_BEVEL,
)
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    SELECTION,
    TROUGH,
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

    def test_meter_geometry(self):
        """A meter's class-armed and corner-armed geometry keeps the existing values,
        and the scale trough carries the existing scale:focus focus shape."""
        self.assert_rule_group(
            {
                "progressbar.horizontal trough": {"min-height": "10px"},
                "progressbar.vertical trough": {"min-width": "10px"},
                "progressbar.horizontal progress": {"margin": "0", "min-height": "10px"},
                "progressbar.vertical progress": {"margin": "0", "min-width": "10px"},
                "progressbar progress.left": {"border-radius": "0"},
                "progressbar progress.right": {"border-radius": "0"},
                "progressbar progress.top": {"border-radius": "0"},
                "progressbar progress.bottom": {"border-radius": "0"},
            }
        )
        self.assert_rule(
            "scale trough",
            {
                "outline": f"1px dotted {BLACK}",
                "outline-offset": "0",
                "-gtk-outline-radius": "0",
            },
        )
        self.assertEqual(self.selectors.count("scale trough"), 1)
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith(("progressbar.horizontal", "progressbar.vertical"))
            },
            {
                "progressbar.horizontal trough",
                "progressbar.vertical trough",
                "progressbar.horizontal progress",
                "progressbar.vertical progress",
            },
        )
        self.assertEqual(
            {s for s in self.selectors if s.startswith("progressbar progress.")},
            {
                "progressbar progress.left",
                "progressbar progress.right",
                "progressbar progress.top",
                "progressbar progress.bottom",
            },
        )
        top = self.css.index("progressbar progress:disabled {")
        bottom = self.css.index("entry progress {")
        for spelling in (
            "progressbar.horizontal trough",
            "progressbar.vertical trough",
            "progressbar.horizontal progress",
            "progressbar.vertical progress",
            "progressbar progress.left",
            "progressbar progress.right",
            "progressbar progress.top",
            "progressbar progress.bottom",
        ):
            position = self.css.index(spelling + " {")
            self.assertGreater(position, top, spelling)
            self.assertLess(position, bottom, spelling)

    def test_treeview_progress_bar(self):
        """A treeview row's progress cell restates the existing meter recipe."""
        plain_fill = {
            "color": BLACK,
            "background-color": SELECTION,
            "background-image": "none",
            "box-shadow": "none",
        }
        selected_fill = {
            "color": BLACK,
            "background-color": WHITE,
            "background-image": "none",
        }
        backdrop_fill = {
            "color": BLACK,
            "background-image": "none",
            "box-shadow": "none",
        }
        plain_trough = {
            "background-color": TROUGH,
            "background-image": "none",
            "border": f"1px solid {BLACK}",
            "border-radius": "0",
            "box-shadow": f"inset 1px 1px {GREY}",
        }
        self.assert_rule("treeview.view.progressbar", plain_fill)
        for selector in (
            "treeview.view.progressbar:selected:focus",
            "treeview.view.progressbar:selected",
            "treeview.view.progressbar:selected:focus:backdrop",
            "treeview.view.progressbar:selected:backdrop",
        ):
            self.assert_rule(selector, selected_fill)
        self.assert_rule("treeview.view.progressbar:backdrop", backdrop_fill)
        self.assert_rule("treeview.view.trough", plain_trough)
        for selector in (
            "treeview.view.trough:selected:focus",
            "treeview.view.trough:selected",
        ):
            self.assert_rule(selector, {"background-color": TROUGH})
        selectors = (
            "treeview.view.progressbar",
            "treeview.view.progressbar:selected:focus",
            "treeview.view.progressbar:selected",
            "treeview.view.progressbar:selected:focus:backdrop",
            "treeview.view.progressbar:selected:backdrop",
            "treeview.view.progressbar:backdrop",
            "treeview.view.trough",
            "treeview.view.trough:selected:focus",
            "treeview.view.trough:selected",
        )
        for selector in selectors:
            self.assertEqual(self.selectors.count(selector), 1, selector)
        self.assertNotIn("min-height", self.rules["treeview.view.trough"])
        self.assertNotIn("min-width", self.rules["treeview.view.trough"])
        self.assertEqual(
            {
                s
                for s in self.rules
                if "treeview.view.progressbar" in s or "treeview.view.trough" in s
            },
            set(selectors),
        )
        self.assertLess(
            self.selectors.index("entry progress"),
            self.selectors.index("treeview.view.progressbar"),
        )
        self.assertLess(
            self.selectors.index("treeview.view.trough"),
            self.selectors.index("levelbar trough"),
        )

    def test_meter_label_ink(self):
        """A meter's show-text percentage label keeps the existing window ink."""
        self.assert_rule_group({"progressbar": {"color": BLACK}})
        self.assert_rule_after("progressbar trough {", "progressbar {")
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("progressbar")
                and not s.startswith(("progressbar ", "progressbar.", "progressbar:"))
            },
            {"progressbar"},
        )

    def test_entry_progress(self):
        self.assert_rule("entry progress", ENTRY_PROGRESS)

    def assert_plain_action_arms(self, prefix):
        """Assert a plain colour-class action's arms restate the existing face.

        The recipe behind both plain action families: only the opaque
        members of the stock family are restated; no restated selector
        carries `.flat`, so the stock transparent-face colour-class family
        keeps governing whole.
        (The colour-class members are restated by
        test_action_class_flat_arms.) Exactly two call sites: the
        suggested- and destructive-action plain families.
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
        self.assert_rule(prefix, face)
        self.assert_rule(f"{prefix}:hover", face)
        self.assert_rule(f"{prefix}:active", sunken)
        self.assert_rule(f"{prefix}:checked", sunken)
        self.assert_rule(f"{prefix}:backdrop", face)
        self.assert_rule(f"{prefix}:backdrop:active", sunken)
        self.assert_rule(f"{prefix}:backdrop:checked", sunken)
        for selector in (
            f"{prefix}:backdrop:disabled",
            f"{prefix}:backdrop:disabled:active",
            f"{prefix}:backdrop:disabled:checked",
            f"{prefix}:disabled",
            f"{prefix}:disabled:active",
            f"{prefix}:disabled:checked",
        ):
            self.assert_rule(selector, disabled)
        expected = {
            prefix,
            f"{prefix}:hover",
            f"{prefix}:active",
            f"{prefix}:checked",
            f"{prefix}:backdrop",
            f"{prefix}:backdrop:active",
            f"{prefix}:backdrop:checked",
            f"{prefix}:backdrop:disabled",
            f"{prefix}:backdrop:disabled:active",
            f"{prefix}:backdrop:disabled:checked",
            f"{prefix}:disabled",
            f"{prefix}:disabled:active",
            f"{prefix}:disabled:checked",
        }
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith(prefix)
                # The colour-class members are restated
                # by test_action_class_flat_arms; the plain opaque keys
                # carry no flat token, so this filter stays inside this
                # family.
                and ".flat" not in selector
            },
            expected,
        )

    def test_suggested_action_plain_arms(self):
        """The plain `suggested-action` arms restate the existing face."""
        self.assert_plain_action_arms("button.suggested-action")

    def test_flat_button_plain_arms(self):
        """The plain `button.flat` arms restate the existing face.

        A GTK 3 push button carrying the `flat` class outside the existing
        overlays draws the existing push-button face in every armed state:
        every restated dictionary extends the existing plain recipe with the
        `background-color` claim the stock transparent faces force, and
        the base, hover and backdrop arms clear the stock motion claims
        with `transition: none`.
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
        """The selected-row button arms restate the existing black."""
        self.assert_selected_row_button_arms("button.flat:backdrop")

    def test_destructive_action_plain_arms(self):
        """The plain `destructive-action` arms restate the existing face.

        The red mirror of `test_suggested_action_plain_arms`.
        """
        self.assert_plain_action_arms("button.destructive-action")

    def test_action_class_flat_arms(self):
        """The plain colour-class `.flat` arms restate the existing face.

        A GTK 3 push button carrying the `flat` class beside
        `suggested-action` or `destructive-action` outside an overlay
        draws the existing push-button face in every armed state, erasing
        the stock transparent face with its blue or red label: the
        twenty selectors extend the existing plain push-button recipes the
        same way `test_flat_button_plain_arms` extends the plain ones —
        every restated dictionary carries the `background-color` claim
        the stock transparent faces force, and the disabled arms
        re-declare the face colour beside the existing disabled dictionary
        and claim no `outline-color`. No `transition` is restated: the
        plain flat family's `transition: none` claims already hold at
        equal-or-higher class counts (probed from gtk-contained.css in
        libgtk-3 3.24.49 with gresource).
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
                self.assertEqual(self.rules[prefix], face)
                for state in (":active", ":checked"):
                    self.assertEqual(self.rules[f"{prefix}{state}"], sunken)
                self.assertEqual(self.rules[f"{prefix}:backdrop"], face)
                for state in (":backdrop:active", ":backdrop:checked"):
                    self.assertEqual(self.rules[f"{prefix}{state}"], sunken)
                for state in (
                    ":disabled",
                    ":backdrop:disabled",
                    ":backdrop:disabled:active",
                    ":backdrop:disabled:checked",
                ):
                    self.assertEqual(self.rules[f"{prefix}{state}"], disabled)
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
        """Run the GTK 3 pixel *program* in a child interpreter.

        A delegate to ``support.gtk_child_probe.run_gtk_child``, which
        holds the harness this module's offscreen pixel probes share.
        """
        return run_gtk_child(self, program, *paths)

    def test_entry_progress_draws_a_two_pixel_strip(self):
        # GTK 3 ignores min-height on this node, so pin the drawn pixels.
        # The GTK work runs in a child interpreter; see _run_gtk_child for
        # why it never runs in this one.
        program = (
            "\nimport re\n"
            + _GTK3_CHILD_HEAD
            + r'''css = re.sub(rb"url\([^)]*\)", b"none", Path(sys.argv[1]).read_bytes())
'''
            + _GTK3_SHEET_AND_WINDOW
            + '''entry = Gtk.Entry()
entry.set_progress_fraction(0.5)
window.add(entry)
window.set_default_size(120, 21)
'''
            + _GTK3_PIXEL_HEAD
            + '''bottom = pixbuf.get_height() - 1
assert at(90, bottom) == "#000000", at(90, bottom)
strip = [at(30, bottom - d) for d in (1, 2)]
assert strip == ["#CCCCFF"] * 2, strip
assert at(30, bottom - 3) == "#FFFFFF", at(30, bottom - 3)
assert at(90, bottom - 1) == "#FFFFFF", at(90, bottom - 1)
print("entry progress: the 0.5 fraction leaves the #CCCCFF strip one and two pixels above the bottom border, #FFFFFF below it")
'''
        )
        self._run_gtk_child(program, str(CSS))

    def test_progressbar_fill_spans_the_trough(self):
        # GTK 3 centres a fill of its own preferred size in the trough, so
        # the oriented fill rules' min-height/min-width is what makes the
        # fill span the trough interior. Each bar renders in its own
        # offscreen window; see _run_gtk_child for why this runs in a child.
        program = (
            "\nimport re\n"
            + _GTK3_CHILD_HEAD
            + r'''css = re.sub(rb"url\([^)]*\)", b"none", Path(sys.argv[1]).read_bytes())
provider = Gtk.CssProvider()
provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), provider, 800
)

def render(bar, width, height, sensitive=True):
    window = Gtk.OffscreenWindow()
    bar.set_fraction(0.5)
    bar.set_sensitive(sensitive)
    window.add(bar)
    window.set_default_size(width, height)
    window.show_all()
    while Gtk.events_pending():
        Gtk.main_iteration()
    pixbuf = window.get_pixbuf()
    pixels, stride, n = pixbuf.get_pixels(), pixbuf.get_rowstride(), pixbuf.get_n_channels()
    window.destroy()

    def at(x, y):
        return "#%02X%02X%02X" % tuple(pixels[y * stride + x * n:][:3])

    return at

def column(at, x, ys):
    return [at(x, y) for y in ys]

def row(at, y, xs):
    return [at(x, y) for x in xs]

BLACK, FILL, GREY, FACE = "#000000", "#CCCCFF", "#999999", "#EEEEEE"

at = render(Gtk.ProgressBar(), 100, 10)
assert column(at, 25, range(12)) == [BLACK] + [FILL] * 10 + [BLACK], column(at, 25, range(12))
assert column(at, 75, range(12)) == [BLACK, GREY] + [FACE] * 9 + [BLACK], column(at, 75, range(12))

at = render(Gtk.ProgressBar(), 100, 10, sensitive=False)
assert column(at, 25, range(1, 11)) == [GREY] * 10, column(at, 25, range(1, 11))
assert column(at, 75, range(12)) == [BLACK, GREY] + [FACE] * 9 + [BLACK], column(at, 75, range(12))

at = render(Gtk.ProgressBar(orientation=Gtk.Orientation.VERTICAL), 12, 100)
assert row(at, 25, range(1, 11)) == [FILL] * 10, row(at, 25, range(1, 11))
assert row(at, 75, range(1, 11)) == [GREY] + [FACE] * 9, row(at, 75, range(1, 11))
print("progress bar: the 0.5 fill spans trough rows 1-10 and columns 1-10 on the horizontal and vertical bars")
'''
        )
        self._run_gtk_child(program, str(CSS))

    def test_disabled_view_renders_the_white_field_and_grey_ink(self):
        # An insensitive view's stock arms out-specify the existing
        # `.view, textview text, list` group, so the pixels show whether the
        # restated disabled view group actually reaches the text window. The
        # buffer's underscores are scaled 3x with a TextTag: at the default
        # font the underscore stroke is a sub-pixel hairline and no pixel
        # reaches full ink coverage, so only a scaled stroke offers the
        # solid run the restated ink is pinned through. The GTK work runs in
        # a child interpreter; see _run_gtk_child for why it never runs in
        # this one.
        program = (
            "\nimport re\n"
            + _GTK3_CHILD_HEAD
            + r'''css = re.sub(rb"url\([^)]*\)", b"none", Path(sys.argv[1]).read_bytes())
'''
            + _GTK3_SHEET_AND_WINDOW
            + '''box = Gtk.Box()
box.set_border_width(5)
view = Gtk.TextView()
view.set_sensitive(False)
view.set_can_focus(False)
buf = view.get_buffer()
tag = buf.create_tag("scaled", scale=3.0)
buf.set_text("_" * 60, -1)
buf.apply_tag(tag, buf.get_start_iter(), buf.get_end_iter())
box.pack_start(view, True, True, 0)
window.add(box)
window.set_default_size(240, 96)
'''
            + _GTK3_PIXEL_HEAD
            + '''alloc = view.get_allocation()
left, top = alloc.x, alloc.y
right, bottom = alloc.x + alloc.width - 1, alloc.y + alloc.height - 1
assert (right - left + 1) * (bottom - top + 1) > 400, (left, top, right, bottom)

FIELD, INK = "#FFFFFF", "#888888"
STOCK = ("#929595", "#faf9f8")

corners = [at(left, top), at(right, top), at(left, bottom), at(right, bottom)]
assert corners == [FIELD] * 4, corners

for y in range(top, bottom + 1):
    for x in range(left, right + 1):
        pixel = at(x, y)
        assert pixel not in STOCK, (x, y, pixel)

best = 0
for y in range(top, bottom + 1):
    run = 0
    for x in range(left, right + 1):
        if at(x, y) == INK:
            run += 1
            best = max(best, run)
        else:
            run = 0
assert best >= 8, best
print("disabled text view: the allocation corners read the white field, no pixel inside the allocation reads a stock disabled literal, and one row carries a >=8px #888888 underscore run")
'''
        )
        self._run_gtk_child(program, str(CSS))

    def test_scrolled_viewport_draws_no_frame(self):
        self.assert_rule(
            "scrolledwindow viewport.frame",
            {"border-style": "none", "box-shadow": "none"},
        )

    def test_scrolled_viewport_renders_one_frame(self):
        # A scrolled window wrapping a child that cannot scroll itself gets a
        # Gtk.Viewport with the frame class. The probe measures the scrolled
        # window's own allocation, so it does not hard-code its position, and
        # checks the frame drawn at its middle column and row. Each render
        # gets a fresh offscreen window; see _run_gtk_child for why this runs
        # in a child.
        program = (
            "\nimport re\n"
            + _GTK3_CHILD_HEAD
            + r'''css = re.sub(rb"url\([^)]*\)", b"none", Path(sys.argv[1]).read_bytes())
provider = Gtk.CssProvider()
provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), provider, 800
)

def render(shadow, rtl):
    window = Gtk.OffscreenWindow()
    box = Gtk.Box()
    box.set_border_width(5)
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
    scrolled.set_size_request(30, 30)
    scrolled.set_shadow_type(shadow)
    scrolled.add(Gtk.Box())
    if rtl:
        scrolled.set_direction(Gtk.TextDirection.RTL)
    box.pack_start(scrolled, False, False, 0)
    window.add(box)
    window.show_all()
    while Gtk.events_pending():
        Gtk.main_iteration()
    alloc = scrolled.get_allocation()
    pixbuf = window.get_pixbuf()
    pixels, stride, n = pixbuf.get_pixels(), pixbuf.get_rowstride(), pixbuf.get_n_channels()
    window.destroy()

    def at(x, y):
        return "#%02X%02X%02X" % tuple(pixels[y * stride + x * n:][:3])

    left, top = alloc.x, alloc.y
    right, bottom = alloc.x + alloc.width - 1, alloc.y + alloc.height - 1
    mid_x, mid_y = (left + right) // 2, (top + bottom) // 2
    column = [at(mid_x, y) for y in range(top, top + 3)]
    column_bottom = [at(mid_x, y) for y in range(bottom - 2, bottom + 1)]
    row = [at(x, mid_y) for x in range(left, left + 3)]
    row_right = [at(x, mid_y) for x in range(right - 2, right + 1)]
    return column, column_bottom, row, row_right

BLACK, GREY, FACE = "#000000", "#999999", "#DDDDDD"

for rtl in (False, True):
    column, column_bottom, row, row_right = render(Gtk.ShadowType.IN, rtl)
    assert column == [BLACK, GREY, FACE], (rtl, column)
    assert column_bottom == [FACE, FACE, BLACK], (rtl, column_bottom)
    assert row == [BLACK, GREY, FACE], (rtl, row)
    assert row_right == [FACE, FACE, BLACK], (rtl, row_right)

    column, column_bottom, row, row_right = render(Gtk.ShadowType.NONE, rtl)
    assert column == [FACE] * 3, (rtl, column)
    assert column_bottom == [FACE] * 3, (rtl, column_bottom)
    assert row == [FACE] * 3, (rtl, row)
    assert row_right == [FACE] * 3, (rtl, row_right)
print("scrolled viewport: the IN frame is 1px black with a grey inset and no second frame; NONE draws no black edge, in LTR and RTL")
'''
        )
        self._run_gtk_child(program, str(CSS))

    def test_flat_frame_draws_no_border(self):
        self.assert_rule(
            "frame > border.flat",
            {"border-style": "none", "box-shadow": "none"},
        )
        self.assert_rule(
            ".frame.flat",
            {"border-style": "none", "box-shadow": "none"},
        )

    def test_flat_frame_renders_no_frame(self):
        # A Gtk.Frame with shadow NONE asks GTK to put the flat style class
        # on its border node, so the frame > border, .frame recipe above must
        # not reach it. The probe measures the frame's own allocation, so it
        # does not hard-code its position, and checks the frame drawn at its
        # middle column and row. Each render gets a fresh offscreen window;
        # see _run_gtk_child for why this runs in a child.
        program = (
            "\nimport re\n"
            + _GTK3_CHILD_HEAD
            + r'''css = re.sub(rb"url\([^)]*\)", b"none", Path(sys.argv[1]).read_bytes())
provider = Gtk.CssProvider()
provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), provider, 800
)

def render(shadow, rtl):
    window = Gtk.OffscreenWindow()
    box = Gtk.Box()
    box.set_border_width(5)
    frame = Gtk.Frame()
    frame.set_size_request(40, 30)
    frame.set_shadow_type(shadow)
    if rtl:
        frame.set_direction(Gtk.TextDirection.RTL)
    box.pack_start(frame, False, False, 0)
    window.add(box)
    window.show_all()
    while Gtk.events_pending():
        Gtk.main_iteration()
    alloc = frame.get_allocation()
    pixbuf = window.get_pixbuf()
    pixels, stride, n = pixbuf.get_pixels(), pixbuf.get_rowstride(), pixbuf.get_n_channels()
    window.destroy()

    def at(x, y):
        return "#%02X%02X%02X" % tuple(pixels[y * stride + x * n:][:3])

    left, top = alloc.x, alloc.y
    right, bottom = alloc.x + alloc.width - 1, alloc.y + alloc.height - 1
    mid_x, mid_y = (left + right) // 2, (top + bottom) // 2
    column = [at(mid_x, y) for y in range(top, top + 3)]
    column_bottom = [at(mid_x, y) for y in range(bottom - 2, bottom + 1)]
    row = [at(x, mid_y) for x in range(left, left + 3)]
    row_right = [at(x, mid_y) for x in range(right - 2, right + 1)]
    return column, column_bottom, row, row_right

BLACK, GREY, FACE = "#000000", "#999999", "#DDDDDD"

for rtl in (False, True):
    column, column_bottom, row, row_right = render(Gtk.ShadowType.IN, rtl)
    assert column == [BLACK, GREY, FACE], (rtl, column)
    assert column_bottom == [FACE, FACE, BLACK], (rtl, column_bottom)
    assert row == [BLACK, GREY, FACE], (rtl, row)
    assert row_right == [FACE, FACE, BLACK], (rtl, row_right)

    column, column_bottom, row, row_right = render(Gtk.ShadowType.NONE, rtl)
    assert column == [FACE] * 3, (rtl, column)
    assert column_bottom == [FACE] * 3, (rtl, column_bottom)
    assert row == [FACE] * 3, (rtl, row)
    assert row_right == [FACE] * 3, (rtl, row_right)
print("flat frame: the IN frame is 1px black with a grey inset; NONE draws no border or inset shadow, in LTR and RTL")
'''
        )
        self._run_gtk_child(program, str(CSS))

    def test_mixed_check_draws_a_black_dash(self):
        # The GTK work runs in a child interpreter; see _run_gtk_child for
        # why it never runs in this one.
        program = (
            "\n" + _GTK3_CHILD_HEAD
            + '''assets = sys.argv[2]
css = Path(sys.argv[1]).read_bytes().replace(
    b'url("../assets/', b'url("' + assets.encode() + b"/")
'''
            + _GTK3_SHEET_AND_WINDOW
            + '''button = Gtk.CheckButton()
button.set_can_focus(False)
button.set_inconsistent(True)
window.add(button)
'''
            + _GTK3_PIXEL_HEAD
            + '''black = [
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
        )
        self._run_gtk_child(program, str(CSS), str(THEME_DIR / "assets"))

    def test_notebook_tab_faces_render(self):
        # The tab recipe is matched by a live GTK paint only; pin the
        # rendered pixels of a two-page notebook's tab faces. The GTK work
        # runs in a child interpreter; see _run_gtk_child for why it never
        # runs in this one.
        program = (
            "\nimport re\n"
            + _GTK3_CHILD_HEAD
            + r'''css = re.sub(rb"url\([^)]*\)", b"none", Path(sys.argv[1]).read_bytes())
'''
            + _GTK3_SHEET_AND_WINDOW
            + '''window.set_default_size(160, 60)
notebook = Gtk.Notebook()
notebook.append_page(Gtk.Label(label=" "), Gtk.Label(label=" "))
notebook.append_page(Gtk.Label(label=" "), Gtk.Label(label=" "))
window.add(notebook)
'''
            + _GTK3_PIXEL_HEAD
            + r'''# Geometry measured 2026-11-10 on this host from this very render:
# the notebook is flush with the window, whose pixbuf it fills, and the
# toolkit's own notebook frame paints the 1px black line at row 0 and the
# columns at x 0 and 159; the band's own 1px black top border sits at
# y = 1 and its interior spans x 30-157 down to y = 32, with blend rows
# (y = 33) beneath and the page area from y = 35. The first tab is
# checked and the second is not; the tabs' shared black edge and each
# face's x are located at render time so the pin is not a transcription
# of tab widths, whose left edges depend on the tab-label metrics.
border = next(x for x in range(6, pixbuf.get_width() - 1) if at(x, 20) == "#000000")
# (a) The band interior beyond the tabs keeps the flat #DDDDDD face.
assert at(130, 20) == "#DDDDDD", at(130, 20)
# (b) The band's top border row is the toolkit frame's black under the
# header's own 1px black border.
assert at(130, 1) == "#000000", at(130, 1)
# (c) The unselected tab carries the raised bevel: the #FFFFFF top arm
# just below its top border row and the #999999 bottom arm symmetric
# above its bottom border row, with the tab's own #DDDDDD face between.
b1 = border + 6
assert at(b1, 3) == "#FFFFFF", at(b1, 3)
assert at(b1, 8) == "#DDDDDD", at(b1, 8)
assert at(b1, 32) == "#999999", at(b1, 32)
# (d) The checked tab is flattened in place: the very same rows carry
# the flat #DDDDDD face with neither bevel arm.
b0 = border - 5
assert at(b0, 3) == "#DDDDDD", at(b0, 3)
assert at(b0, 32) == "#DDDDDD", at(b0, 32)
print("notebook tab faces: the band interior and the flat checked tab read #DDDDDD, the band's top border #000000, the unselected tab's bevel #FFFFFF over #DDDDDD over #999999")
'''
        )
        self._run_gtk_child(program, str(CSS))

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

    def test_switch_state_and_backdrop_faces(self):
        """The existing switch faces hold through every toolkit repaint.

        The toolkit's state, backdrop and selected-row switch arms
        out-specify the existing groups (see the
        sheet), so each stock spelling is restated byte-equal and wins by
        later user-sheet source order. Each spelling counts exactly once,
        the three existing groups carry exactly one added member each, and
        the family sweeps admit no stray or renamed spelling.
        """
        # The restated knob arms: the raised bevel face, no fade.
        for selector in ("switch:hover slider", "switch:backdrop slider"):
            self.assert_rule(
                selector,
                {
                    "border-color": BLACK,
                    "background-image": "none",
                    "box-shadow": "inset 1px 1px #FFFFFF,"
                    " inset -1px -1px #999999",
                    "transition": "none",
                },
            )
        self.assert_rule("switch:checked > slider", {"border-color": BLACK})
        self.assert_rule(
            "switch:backdrop",
            {
                "background-color": TROUGH,
                "border-color": BLACK,
                "transition": "none",
            },
        )
        self.assert_rule(
            "switch:backdrop:checked",
            {"background-color": WHITE, "border-color": BLACK},
        )
        self.assert_rule(
            "switch:backdrop:disabled",
            {"background-color": TROUGH, "border-color": GREY},
        )
        self.assert_rule(
            "switch:backdrop:disabled slider",
            {
                "border-color": GREY,
                "background-image": "none",
                "box-shadow": "none",
                "transition": "none",
            },
        )
        # The selected-row twins of the existing `row:selected button` record.
        for selector in (
            "row:selected switch",
            "row:selected switch:backdrop",
            "row:selected switch > slider:checked",
            "row:selected switch > slider",
        ):
            self.assert_rule(selector, {"border-color": BLACK})

        # The three amended existing groups: one added member each, no more.
        self.assert_rule("switch:checked", {"border-color": BLACK})
        self.assert_rule("switch:disabled", {"background-color": TROUGH})
        self.assert_rule("switch slider", {"transition": "none"})
        self.assertEqual(
            self.rules["switch:checked"],
            {
                "background-color": WHITE,
                "background-image": "none",
                "border-color": BLACK,
            },
        )
        self.assertEqual(
            self.rules["switch:disabled"],
            {"background-color": TROUGH, "border-color": GREY},
        )
        self.assertEqual(
            self.rules["switch slider"],
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": "inset 1px 1px #FFFFFF,"
                " inset -1px -1px #999999",
                "margin": "-1px",
                "min-width": "12px",
                "min-height": "16px",
                "transition": "none",
            },
        )
        for selector in ("switch:checked", "switch:disabled", "switch slider"):
            self.assertEqual(self.selectors.count(selector), 1, selector)

        # Family sweeps: no stray or renamed spelling survives.
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("switch") and ":backdrop" in s
            },
            {
                "switch:backdrop",
                "switch:backdrop:checked",
                "switch:backdrop:disabled",
                "switch:backdrop slider",
                "switch:backdrop:checked > slider",
                "switch:backdrop:disabled slider",
            },
        )
        self.assertEqual(
            {s for s in self.selectors if "row:selected switch" in s},
            {
                "row:selected switch",
                "row:selected switch:backdrop",
                "row:selected switch > slider:checked",
                "row:selected switch > slider",
            },
        )
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("switch")
                and ":backdrop" not in s
                and (
                    ":hover" in s
                    or ":active" in s
                    or ":checked" in s
                    or ":disabled" in s
                )
            },
            {
                "switch:checked",
                "switch:disabled",
                "switch:disabled slider",
                "switch:hover slider",
                "switch:checked > slider",
            },
        )

        # Order: the restated block sits between the existing `switch image`
        # group and the existing toolbar band group.
        self.assertGreater(
            self.css.index("switch:hover slider"),
            self.css.index("switch image {"),
        )
        self.assertLess(
            self.css.index("switch:hover slider"),
            self.css.index("toolbar, menubar {"),
        )

    def test_scale(self):
        self.assert_scale(
            trough="scale trough",
            fill=("scale fill", "scale highlight"),
            slider="scale slider",
            horizontal="scale.horizontal slider",
            vertical="scale.vertical slider",
            disabled="scale slider:disabled",
        )

    def test_meter_state_and_backdrop_faces(self):
        """Disabled, selected-row and unfocused-window meters keep the existing
        faces, and no meter repaint fades over the stock 200ms."""
        self.assert_rule_group(
            {
                "progressbar trough:disabled": {"background-color": TROUGH},
                "scale trough:disabled": {"background-color": TROUGH},
                "progressbar trough:backdrop": {
                    "background-color": TROUGH,
                    "border-color": BLACK,
                    "transition": "none",
                },
                "scale trough:backdrop": {
                    "background-color": TROUGH,
                    "border-color": BLACK,
                    "transition": "none",
                },
                "progressbar trough:backdrop:disabled": {
                    "background-color": TROUGH,
                },
                "scale trough:backdrop:disabled": {
                    "background-color": TROUGH,
                },
                "row:selected progressbar trough": {"border-color": BLACK},
                "progressbar row:selected trough": {"border-color": BLACK},
                "row:selected scale trough": {"border-color": BLACK},
                "scale row:selected trough": {"border-color": BLACK},
                "scale fill:backdrop": {"background-color": "transparent"},
                "scale slider:backdrop": {
                    "background-color": FACE,
                    "background-image": "none",
                    "border-color": BLACK,
                    "box-shadow": RAISED_BEVEL,
                    "transition": "none",
                },
                "scale slider:backdrop:disabled": {
                    "background-color": FACE,
                    "background-image": "none",
                    "border-color": GREY,
                    "box-shadow": "none",
                    "transition": "none",
                },
                "row:selected scale slider:disabled": {"border-color": BLACK},
                "row:selected scale slider": {"border-color": BLACK},
            }
        )
        # The single amendment to the existing bare knob group: the existing
        # assert_scale reads that group per-property, so only an added,
        # altered or duplicated transition member dies here.
        self.assert_rule("scale slider", {"transition": "none"})
        self.assertEqual(self.selectors.count("scale slider"), 1)
        # Family sweep: the trough keeps the existing face in exactly the six
        # stock state spellings. A stray state trough spelling, a renamed
        # member or a pale trough face leaking onto a disabled fill dies.
        self.assertEqual(
            {
                s
                for s in self.selectors
                if (s.startswith("progressbar trough")
                    or s.startswith("scale trough"))
                and (":disabled" in s or ":backdrop" in s)
            },
            {
                "progressbar trough:disabled",
                "scale trough:disabled",
                "progressbar trough:backdrop",
                "scale trough:backdrop",
                "progressbar trough:backdrop:disabled",
                "scale trough:backdrop:disabled",
            },
        )
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("scale slider:backdrop")
            },
            {"scale slider:backdrop", "scale slider:backdrop:disabled"},
        )
        # Exactly the six selected-row meter members restated: no selected-row
        # fill or highlight rim (inert over the zero-width border), and no
        # spelling drift on the odd disabled-first slider group.
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith(
                    (
                        "row:selected scale",
                        "row:selected progressbar",
                        "scale row:selected",
                        "progressbar row:selected",
                    )
                )
            },
            {
                "row:selected progressbar trough",
                "progressbar row:selected trough",
                "row:selected scale trough",
                "scale row:selected trough",
                "row:selected scale slider:disabled",
                "row:selected scale slider",
            },
        )
        # Every non-.osd meter backdrop spelling is accounted for: a dropped
        # rule or a stray twin outside the state block dies. The existing .osd
        # and treeview progressbar backdrop spellings carry a prefix neither
        # a scale nor a progressbar root, so neither joins; the existing one-sided
        # marked-scale record (test_marked_scale_thumb_arms) contributes its
        # eight backdropped slider spellings, verbatim from the fresh parse.
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith(("scale", "progressbar"))
                and ":backdrop" in s
                and ".osd" not in s
            },
            {
                "scale fill:backdrop",
                "progressbar trough:backdrop",
                "scale trough:backdrop",
                "progressbar trough:backdrop:disabled",
                "scale trough:backdrop:disabled",
                "scale slider:backdrop",
                "scale slider:backdrop:disabled",
                "progressbar:backdrop",
                "scale.horizontal.marks-after:not(.marks-before) slider:backdrop",
                "scale.horizontal.marks-after:not(.marks-before) slider:backdrop:disabled",
                "scale.horizontal.marks-before:not(.marks-after) slider:backdrop",
                "scale.horizontal.marks-before:not(.marks-after) slider:backdrop:disabled",
                "scale.vertical.marks-after:not(.marks-before) slider:backdrop",
                "scale.vertical.marks-after:not(.marks-before) slider:backdrop:disabled",
                "scale.vertical.marks-before:not(.marks-after) slider:backdrop",
                "scale.vertical.marks-before:not(.marks-after) slider:backdrop:disabled",
            },
        )
        # Source-order pin: the nine rules sit between the existing
        # scale fill/highlight and bare knob groups, so each wins its
        # equal-specificity tie by later user-sheet source order.
        # Both anchors get a line-start bolt: the new row:selected slider
        # group's "row:selected scale slider {" spelling would otherwise
        # satisfy the bare "scale slider {" substring.
        top = self.css.index("\nscale fill, scale highlight {")
        bottom = self.css.index("\nscale slider {")
        # Comma groups pin by their full byte-equal spelling (the parser
        # stores each member individually); solo rules by their selector.
        for spelling in (
            "progressbar trough:disabled, scale trough:disabled",
            "progressbar trough:backdrop, scale trough:backdrop",
            "progressbar trough:backdrop:disabled, scale trough:backdrop:disabled",
            "row:selected progressbar trough, progressbar row:selected trough,"
            " row:selected scale trough, scale row:selected trough",
            "scale fill:backdrop",
            "scale slider:backdrop",
            "scale slider:backdrop:disabled",
            "row:selected scale slider:disabled, row:selected scale slider",
            "progressbar:backdrop",
        ):
            # A line-start bolt keeps treeview's existing
            # treeview.view.progressbar:backdrop spelling out of this search.
            position = self.css.index(
                ("\n" + spelling if spelling == "progressbar:backdrop"
                 else spelling) + " {"
            )
            self.assertGreater(position, top, spelling)
            self.assertLess(position, bottom, spelling)

    def test_scale_decoration_ink(self):
        """A scale's tick marks and readout paint the existing window ink.

        The existing group sits directly after the existing backdrop-disabled
        slider twin and before the existing selected-row slider twin, so the
        single repainted member reads through the toolkit's stock ink arm
        in every state the bare pair reaches. Assert each spelling once,
        whole-driven, family-clean and in the existing group order.
        """
        # The parser stores comma-group members individually, so the
        # whole-dict assertion pins the two spellings the group declares,
        # each exactly once, and the stripped sheet's single comma-spelled
        # group kills a split into bare spelling blocks.
        self.assert_rule_group(
            {"scale marks": {"color": BLACK}, "scale value": {"color": BLACK}}
        )
        self.assertEqual(
            strip_comments(self.css).count("scale marks, scale value {"), 1
        )
        # Order pins: the pair group reads later than the backdrop-disabled
        # slider twin it follows and earlier than the selected-row slider
        # twin it precedes in the existing sheet order.
        self.assert_rule_after(
            "scale marks, scale value {", "scale slider:backdrop:disabled {"
        )
        self.assert_rule_after(
            "row:selected scale slider:disabled, row:selected scale slider {",
            "scale marks, scale value {",
        )
        # No renamed, stray or state-armed marks/value spelling exists: the
        # family sweeps admit only the group's two members.
        self.assertEqual(
            {s for s in self.selectors if s.startswith("scale marks")},
            {"scale marks"},
        )
        self.assertEqual(
            {s for s in self.selectors if s.startswith("scale value")},
            {"scale value"},
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

    def test_scale_plain_container_geometry(self):
        """A plain (non-fine-tuned) scale's container keeps stock's geometry.

        The restatement stands directly after the fine-tune radius group
        and directly before the fine-tuned container record, so the plain
        node keeps stock's 10px transverse minimums and its 12px push-out
        padding in both orientations under either loading reading; assert
        the spelling once, whole-driven, family-clean and in record order.
        """
        self.assert_rule_group(
            {
                "scale": {
                    "min-height": "10px",
                    "min-width": "10px",
                    "padding": "12px",
                }
            }
        )
        # Family sweep: no state twin, no rename and no split spelling (the
        # existing scale trough, fill/highlight and slider spellings fail the
        # equality and stay out); the state sweep admits only the existing
        # `scale:focus` record's spelling, so an added `scale:disabled` or
        # `scale:backdrop` bare-node twin dies here too.
        self.assertEqual({s for s in self.selectors if s == "scale"}, {"scale"})
        self.assertEqual(
            {s for s in self.selectors if s.startswith("scale:")},
            {"scale:focus"},
        )
        # Order pins: the container block sits after the fine-tune radius
        # group and the fine-tuned container record follows it, mirroring
        # stock's plain-before-fine-tuned order. The two-operand pins ride
        # first raw-text occurrence; the existing fine-tuned record's comment
        # quotes these spellings, which is why the second pin holds only
        # once this record's own rule exists.
        self.assert_rule_after("scale {", "scale.fine-tune trough {")
        self.assert_rule_after("scale.fine-tune.horizontal {", "scale {")

    def test_scale_fine_tune_container_geometry(self):
        """A fine-tuned scale's container keeps the toolkit's stock geometry.

        The existing restatement stands directly after the fine-tune radius
        group, so both orientations keep stock's 9px transverse paddings
        and 16px transverse minimum under either loading reading; assert
        each spelling once, whole-driven, family-clean and in radius-block
        order.
        """
        self.assert_rule_group(
            {
                "scale.fine-tune.horizontal": {
                    "padding-top": "9px",
                    "padding-bottom": "9px",
                    "min-height": "16px",
                },
                "scale.fine-tune.vertical": {
                    "padding-left": "9px",
                    "padding-right": "9px",
                    "min-width": "16px",
                },
            }
        )
        # Family sweeps: no state twin, no bare-class fallback, no split
        # spelling (the existing .fine-tune slider and fill/highlight/trough
        # spellings do not satisfy the prefixed equality and stay out).
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("scale.fine-tune.horizontal")
            },
            {"scale.fine-tune.horizontal"},
        )
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("scale.fine-tune.vertical")
            },
            {"scale.fine-tune.vertical"},
        )
        # The container block sits beside the existing fine-tune radius
        # group, so its equal-specificity ties win by later source order.
        self.assert_rule_after(
            "scale.fine-tune.horizontal {",
            "scale.fine-tune trough {",
        )

    def test_scale_marks_indicator_geometry(self):
        """A marked scale keeps the toolkit's tick spacing and line sizes.

        The twelve restated arms stand directly before the existing
        marked-scale record, so both orientations keep stock's 6px tick
        push-out with the -12px plain and -9px fine-tuned stop margins and
        the 6px-by-1px plain and 3px fine-tuned indicator minimums under
        either loading reading; assert each spelling once, whole-driven,
        family-clean and in record order.
        """
        self.assert_rule_group(
            {
                "scale.horizontal marks.top": {
                    "margin-bottom": "6px",
                    "margin-top": "-12px",
                },
                "scale.horizontal.fine-tune marks.top": {
                    "margin-bottom": "6px",
                    "margin-top": "-9px",
                },
                "scale.horizontal marks.bottom": {
                    "margin-top": "6px",
                    "margin-bottom": "-12px",
                },
                "scale.horizontal.fine-tune marks.bottom": {
                    "margin-top": "6px",
                    "margin-bottom": "-9px",
                },
                "scale.vertical marks.top": {
                    "margin-right": "6px",
                    "margin-left": "-12px",
                },
                "scale.vertical.fine-tune marks.top": {
                    "margin-right": "6px",
                    "margin-left": "-9px",
                },
                "scale.vertical marks.bottom": {
                    "margin-left": "6px",
                    "margin-right": "-12px",
                },
                "scale.vertical.fine-tune marks.bottom": {
                    "margin-left": "6px",
                    "margin-right": "-9px",
                },
                "scale.horizontal indicator": {
                    "min-height": "6px",
                    "min-width": "1px",
                },
                "scale.horizontal.fine-tune indicator": {
                    "min-height": "3px",
                },
                "scale.vertical indicator": {
                    "min-height": "1px",
                    "min-width": "6px",
                },
                "scale.vertical.fine-tune indicator": {
                    "min-width": "3px",
                },
            }
        )
        # Family sweeps: no renamed spelling, no stray or split member
        # (the existing has-marks slider spellings carry neither token and
        # stay out).
        for token, members in (
            (
                "marks.top",
                (
                    "scale.horizontal marks.top",
                    "scale.horizontal.fine-tune marks.top",
                    "scale.vertical marks.top",
                    "scale.vertical.fine-tune marks.top",
                ),
            ),
            (
                "marks.bottom",
                (
                    "scale.horizontal marks.bottom",
                    "scale.horizontal.fine-tune marks.bottom",
                    "scale.vertical marks.bottom",
                    "scale.vertical.fine-tune marks.bottom",
                ),
            ),
        ):
            self.assertEqual(
                {s for s in self.selectors if token in s}, set(members)
            )
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("scale.h") and s.endswith("indicator")
            },
            {
                "scale.horizontal indicator",
                "scale.horizontal.fine-tune indicator",
            },
        )
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("scale.v") and s.endswith("indicator")
            },
            {
                "scale.vertical indicator",
                "scale.vertical.fine-tune indicator",
            },
        )
        # The block sits after the existing trough group and before the
        # existing marked-scale record's closing group, so its
        # equal-specificity ties win by later source order.
        self.assert_rule_after(
            "scale.vertical.marks-after:not(.marks-before).fine-tune slider {",
            "scale.vertical.fine-tune indicator {",
        )
        self.assert_rule_after("scale.horizontal marks.top {", "scale trough {")

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
        self.assert_button_disabled_and_backdrop()

    def test_checkbutton_focus_outline(self):
        self.assert_dotted_focus_outline("checkbutton:focus")

    def test_entry_focus_outline(self):
        self.assert_dotted_focus_outline("entry:focus")

    def test_entry_error_warning_colour_classes(self):
        # The existing entry policy takes no colour class: the sheet
        # restates the stock colour-class arms with byte-equal twins
        # declaring the existing faces, so an entry, spin-button field or
        # label carrying the `error` or `warning` class paints the existing
        # recipe instead of the toolkit resource's red or orange. The
        # label's disabled twins both take the existing insensitive grey
        # with no backdrop dim (the existing sheet carries no label backdrop
        # dim, matching the existing GTK 4 label colour-class record); the
        # selection arms restate only the fill, the existing element-level
        # selection groups owning the ink; the focus arms restate only the
        # etch and the border colour, the existing dotted outlines cascading
        # unchanged; and stock's late colour-only repeat of the error
        # field base arm needs no twin of its own.
        expected = {
            "label.error": {"color": BLACK},
            "label.error:disabled": DISABLED_TEXT,
            "label.error:disabled:backdrop": DISABLED_TEXT,
            "spinbutton.error:not(.vertical)": {
                "color": BLACK,
                "border-color": BLACK,
            },
            "entry.error": {"color": BLACK, "border-color": BLACK},
            "spinbutton.error:focus:not(.vertical)": {
                "box-shadow": ENTRY_FIELD["box-shadow"],
                "border-color": BLACK,
            },
            "entry.error:focus": {
                "box-shadow": ENTRY_FIELD["box-shadow"],
                "border-color": BLACK,
            },
            "spinbutton.error:not(.vertical) selection": {
                "background-color": SELECTION,
            },
            "entry.error selection": {"background-color": SELECTION},
            "spinbutton.warning:not(.vertical)": {
                "color": BLACK,
                "border-color": BLACK,
            },
            "entry.warning": {"color": BLACK, "border-color": BLACK},
            "spinbutton.warning:focus:not(.vertical)": {
                "box-shadow": ENTRY_FIELD["box-shadow"],
                "border-color": BLACK,
            },
            "entry.warning:focus": {
                "box-shadow": ENTRY_FIELD["box-shadow"],
                "border-color": BLACK,
            },
            "spinbutton.warning:not(.vertical) selection": {
                "background-color": SELECTION,
            },
            "entry.warning selection": {"background-color": SELECTION},
        }
        self.assert_rule_group(expected)
        # No other error or warning selector exists in the sheet: the
        # family sweep kills renamed, dropped and stray class spellings
        # alike.
        self.assertEqual(
            {s for s in self.rules if ".error" in s or ".warning" in s},
            set(expected),
        )
        # Every restated spelling sits after the existing field rule, so the
        # equal-specificity ties resolve the existing face's way under either
        # cascade reading the existing records accept.
        uncommented = strip_comments(self.css)
        anchor = uncommented.index("entry, spinbutton:not(.vertical) {")
        for selector in expected:
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertGreater(uncommented.index(selector), anchor, selector)

    def test_entry_state_faces(self):
        # The toolkit resource's own plain entry and spin-button state arms
        # (focus, disabled, backdrop, backdrop-disabled, drop-active, the
        # vertical spin button's colour-only twins, the nested horizontal
        # spin-button field and the treeview editable cell) otherwise paint
        # foreign faces on the existing spellings: an accent ring on focus,
        # greige borders and off-white fills with no etch on the insensitive
        # and unfocused-window states, a green drag rim, an accent border on
        # focused editable cells, and a duplicate existing etch on the nested
        # field the resource itself clears. Each rule restates its stock
        # twin's declarations with the existing faces (the field etch and hard
        # border, the insensitive grey, the no-motion backdrop policy the
        # existing button:backdrop record states) in place of the foreign
        # inks, so the later user-sheet spellings win every equal-specificity
        # tie.
        etch = ENTRY_FIELD["box-shadow"]
        expected = {
            "entry:focus": {
                "outline": "1px dotted #000000",
                "outline-offset": "0",
                "-gtk-outline-radius": "0",
                "box-shadow": etch,
                "border-color": BLACK,
            },
            "spinbutton:focus:not(.vertical)": {
                "outline": "1px dotted #000000",
                "outline-offset": "0",
                "-gtk-outline-radius": "0",
                "box-shadow": etch,
                "border-color": BLACK,
            },
            "entry:disabled": {
                "color": DISABLED_TEXT["color"],
                "border-color": BLACK,
                "background-color": WHITE,
                "box-shadow": etch,
            },
            "spinbutton:disabled:not(.vertical)": {
                "color": DISABLED_TEXT["color"],
                "border-color": BLACK,
                "background-color": WHITE,
                "box-shadow": etch,
            },
            "entry:backdrop": {
                "color": BLACK,
                "border-color": BLACK,
                "background-color": WHITE,
                "box-shadow": etch,
                "transition": "none",
            },
            "spinbutton:backdrop:not(.vertical)": {
                "color": BLACK,
                "border-color": BLACK,
                "background-color": WHITE,
                "box-shadow": etch,
                "transition": "none",
            },
            "entry:backdrop:disabled": {
                "color": DISABLED_TEXT["color"],
                "border-color": BLACK,
                "background-color": WHITE,
                "box-shadow": etch,
            },
            "spinbutton:backdrop:disabled:not(.vertical)": {
                "color": DISABLED_TEXT["color"],
                "border-color": BLACK,
                "background-color": WHITE,
                "box-shadow": etch,
            },
            "spinbutton.vertical:disabled": {
                "color": DISABLED_TEXT["color"],
            },
            "spinbutton.vertical:backdrop:disabled": {
                "color": DISABLED_TEXT["color"],
            },
            "spinbutton:drop(active):not(.vertical)": {
                "border-color": BLACK,
                "box-shadow": etch,
            },
            "entry:drop(active):focus": {
                "border-color": BLACK,
                "box-shadow": etch,
            },
            "entry:drop(active)": {
                "border-color": BLACK,
                "box-shadow": etch,
            },
            "spinbutton.vertical:drop(active)": {
                "border-color": "transparent",
                "box-shadow": "none",
            },
            ".osd spinbutton:not(.vertical) entry": {
                "min-width": "28px",
                "margin": "0",
                "background": "none",
                "background-color": "transparent",
                "border": "none",
                "border-radius": "0",
                "box-shadow": "none",
            },
            "spinbutton:not(.vertical) entry": {
                "min-width": "28px",
                "margin": "0",
                "background": "none",
                "background-color": "transparent",
                "border": "none",
                "border-radius": "0",
                "box-shadow": "none",
            },
            "spinbutton:not(.vertical) entry:backdrop:disabled": {
                "background-color": "transparent",
            },
            "treeview entry": {
                "background-color": WHITE,
                "background-image": "none",
                "border-radius": "0",
            },
            "treeview entry.flat": {
                "background-color": WHITE,
                "background-image": "none",
                "border-radius": "0",
            },
            "treeview entry:focus:dir(rtl)": {
                "background-color": WHITE,
                "transition-property": "none",
            },
            "treeview entry:focus:dir(ltr)": {
                "background-color": WHITE,
                "transition-property": "none",
            },
            "treeview entry.flat:focus": {
                "border-color": BLACK,
            },
            "treeview entry:focus": {
                "border-color": BLACK,
            },
        }
        # Three spellings pre-exist in the existing sheet — the existing focus
        # rules and the existing label/entry/spin-button insensitive group —
        # so each lands with exactly two declarations in the sheet (count 2)
        # and the rest with exactly one.
        existing_counts = {
            "entry:focus": 2,
            "spinbutton:focus:not(.vertical)": 2,
            "entry:disabled": 2,
        }
        for selector, declarations in expected.items():
            self.assertEqual(
                self.selectors.count(selector),
                existing_counts.get(selector, 1),
                selector,
            )
            self.assertEqual(self.rules[selector], declarations, selector)
        # No other unlinked entry or spin-button drop-active selector exists:
        # the family sweep kills renamed, stray and linked leftovers alike.
        self.assertEqual(
            {
                s
                for s in self.rules
                if ":drop(active)" in s
                and ("entry" in s or "spinbutton" in s)
                and ".linked" not in s
            },
            {
                "spinbutton:drop(active):not(.vertical)",
                "entry:drop(active):focus",
                "entry:drop(active)",
                "spinbutton.vertical:drop(active)",
            },
        )
        # Every restated spelling sits after the existing field rule, so the
        # equal-specificity ties resolve the existing face's way under either
        # cascade reading the existing records accept.
        uncommented = strip_comments(self.css)
        anchor = uncommented.index("entry, spinbutton:not(.vertical) {")
        for selector in expected:
            self.assertGreater(uncommented.index(selector), anchor, selector)

    def test_entry_image_inks(self):
        # The existing entry recipe never names the icon child GTK embeds
        # inside a field or spin button, so the toolkit resource paints
        # its own inks on it: a foreign grey-green at rest, a dark grey
        # under hover, the accent hue while pressed or keyboard-active
        # and a pale grey inside an unfocused window, plus a 6px gap
        # between each side icon and the field's text that the existing
        # sheet owns nowhere. Every colour arm restates its stock twin
        # with the existing field's black ink (no collected reference
        # screenshot shows an embedded icon, so the existing text-ink
        # record stands in; the backdrop twin keeps that face per the
        # existing button:backdrop policy since Platinum's model is
        # active=frontmost), and the two margin twins keep stock's own
        # spacing byte-equal.
        expected = {
            "spinbutton:not(.vertical) image.left": {"margin-right": "6px"},
            "entry image.left": {"margin-right": "6px"},
            "spinbutton:not(.vertical) image.right": {"margin-left": "6px"},
            "entry image.right": {"margin-left": "6px"},
            "spinbutton:not(.vertical) image": {"color": BLACK},
            "entry image": {"color": BLACK},
            "spinbutton:not(.vertical) image:hover": {"color": BLACK},
            "entry image:hover": {"color": BLACK},
            "spinbutton:not(.vertical) image:active": {"color": BLACK},
            "entry image:active": {"color": BLACK},
            "spinbutton:not(.vertical) image:backdrop": {"color": BLACK},
            "entry image:backdrop": {"color": BLACK},
        }
        for selector, declarations in expected.items():
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], declarations, selector)
        # No other spelling in the family exists: the token sweep kills
        # renamed, stray and dropped twins alike.
        self.assertEqual(
            {
                s
                for s in self.rules
                if s.startswith("spinbutton:not(.vertical) image")
                or s.startswith("entry image")
            },
            set(expected),
        )
        # Every restated spelling sits after the existing field rule, so
        # the equal-specificity ties resolve the existing face's way under
        # either cascade reading.
        uncommented = strip_comments(self.css)
        anchor = uncommented.index("entry, spinbutton:not(.vertical) {")
        for selector in expected:
            self.assertGreater(uncommented.index(selector), anchor, selector)

    def test_entry_tag_faces(self):
        # The existing entry recipe never names the tag chips a tagged
        # entry embeds at its tail, so the toolkit resource paints its
        # own chip: a foreign accent-blue fill with white ink at rest,
        # a lighter accent under hover, a pale-repeat twin inside an
        # unfocused window and a dimmed translucent white close-button
        # ink with an accent ring and fill under hover and press. The
        # chip restates the palette's flat selection fill with the
        # existing field's black ink (no collected reference screenshot
        # shows an entry tag, so the selection-surface and text-ink
        # records stand in; the backdrop twin keeps that face per the
        # existing button:backdrop policy since Platinum's model is
        # active=frontmost, and the dimmed close-button inks rise to
        # full strength per the existing hover-erase precedents), keeps
        # stock's own padding, vertical margins and border and keeps
        # the two direction margin twins byte-equal and mirrored.
        expected = {
            ".entry-tag": {
                "padding": "5px",
                "margin-top": "2px",
                "margin-bottom": "2px",
                "border-style": "none",
                "color": BLACK,
                "background-color": SELECTION,
            },
            ":dir(ltr) .entry-tag": {"margin-left": "8px", "margin-right": "-5px"},
            ":dir(rtl) .entry-tag": {"margin-left": "-5px", "margin-right": "8px"},
            ".entry-tag:hover": {"background-color": SELECTION},
            ":backdrop .entry-tag": {"color": BLACK, "background-color": SELECTION},
            ".entry-tag.button": {"background-color": "transparent", "color": BLACK},
            ":not(:backdrop) .entry-tag.button:hover": {
                "border": f"1px solid {BLACK}",
                "color": BLACK,
            },
            ":not(:backdrop) .entry-tag.button:active": {
                "background-color": SELECTION,
                "color": BLACK,
            },
        }
        for selector, declarations in expected.items():
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], declarations, selector)
        # No other spelling in the family exists: the token sweep kills
        # renamed, stray and dropped twins alike.
        self.assertEqual(
            {s for s in self.rules if "entry-tag" in s}, set(expected)
        )
        # The whole chip block sits after the existing entry-image block's
        # opener, so the equal-specificity ties resolve the existing
        # face's way under either cascade reading.
        uncommented = strip_comments(self.css)
        anchor = uncommented.index("spinbutton:not(.vertical) image, entry image {")
        for selector in expected:
            self.assertGreater(uncommented.index(selector), anchor, selector)

    def test_horizontal_spinbutton_focus_outline(self):
        self.assert_dotted_focus_outline("spinbutton:focus:not(.vertical)")

    def test_vertical_spinbutton_focus_outline(self):
        self.assert_dotted_focus_outline(
            "spinbutton.vertical:focus", anchor="spinbutton:focus:not(.vertical)"
        )

    def test_horizontal_spinbutton_steppers_share_one_seam(self):
        self.assert_rule(
            "spinbutton:not(.vertical) button",
            {"border-style": "none none none solid"},
        )
        self.assert_rule(
            "spinbutton:not(.vertical) button:dir(rtl)",
            {"border-style": "none solid none none"},
        )

    def test_horizontal_spinbutton_steppers_render_one_pixel_seams(self):
        # The spin button is measured from its own allocation, so the probe
        # does not hard-code stepper widths: it finds the black columns on
        # row T+4 and checks that they are the left edge, two non-adjacent
        # seams and the right edge. Each render gets a fresh offscreen window;
        # see _run_gtk_child for why this runs in a child.
        program = (
            "\nimport re\n"
            + _GTK3_CHILD_HEAD
            + r'''css = re.sub(rb"url\([^)]*\)", b"none", Path(sys.argv[1]).read_bytes())
provider = Gtk.CssProvider()
provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), provider, 800
)

def render(rtl):
    window = Gtk.OffscreenWindow()
    box = Gtk.Box()
    box.set_border_width(5)
    spin = Gtk.SpinButton.new_with_range(0, 100, 1)
    spin.set_can_focus(False)
    if rtl:
        spin.set_direction(Gtk.TextDirection.RTL)
    box.pack_start(spin, False, False, 0)
    window.add(box)
    window.show_all()
    while Gtk.events_pending():
        Gtk.main_iteration()
    alloc = spin.get_allocation()
    pixbuf = window.get_pixbuf()
    pixels, stride, n = pixbuf.get_pixels(), pixbuf.get_rowstride(), pixbuf.get_n_channels()
    window.destroy()

    def at(x, y):
        return "#%02X%02X%02X" % tuple(pixels[y * stride + x * n:][:3])

    left, top = alloc.x, alloc.y
    right, bottom = alloc.x + alloc.width - 1, alloc.y + alloc.height - 1
    return at, left, top, right, bottom

BLACK, WHITE, GREY, LIGHT, SHADE = "#000000", "#FFFFFF", "#999999", "#DDDDDD", "#AAAAAA"

def check_field(at, x, top, bottom):
    got = [at(x, top), at(x, top + 1), at(x, top + 2), at(x, bottom)]
    assert got == [BLACK, GREY, WHITE, BLACK], got

def check_stepper(at, x, top, bottom):
    got = [at(x, top), at(x, top + 1), at(x, top + 2), at(x, bottom - 1), at(x, bottom)]
    assert got == [BLACK, WHITE, LIGHT, SHADE, BLACK], got

for rtl in (False, True):
    at, left, top, right, bottom = render(rtl)
    cols = [x for x in range(left, right + 1) if at(x, top + 4) == BLACK]
    assert len(cols) == 4, (rtl, cols)
    assert cols[0] == left and cols[3] == right, (rtl, cols, left, right)
    assert all(b - a > 1 for a, b in zip(cols, cols[1:])), (rtl, cols)
    if rtl:
        field, steppers = (cols[2] + cols[3]) // 2, (cols[0] + 3, cols[1] + 3)
    else:
        field, steppers = (cols[0] + cols[1]) // 2, (cols[1] + 3, cols[2] + 3)
    check_field(at, field, top, bottom)
    for x in steppers:
        check_stepper(at, x, top, bottom)
    # The RTL mirror rule moves the etch's vertical arm to the field's
    # exposed right edge: measured 2026-11-11, the shipped sheet left the
    # RTL field with no vertical arm at either exposed edge (GTK 3 does
    # not mirror box-shadow for direction, and the steppers cover the
    # arm at the left edge), reading white at R-1 below the top arm and
    # stepper face over the covered arm at L+1. A mirror spelled
    # `inset 1px 1px #999999` would keep RTL R-1 white at T+2 and B-1,
    # and a mirror on the wrong side would read grey at RTL L+1.
    rows = (top + 1, top + 2, top + 3, bottom - 1)
    if rtl:
        assert [at(right - 1, y) for y in rows] == [GREY] * 4, (rtl, rows)
        assert [at(left + 1, y) for y in rows] == [WHITE, WHITE, WHITE, SHADE], (rtl, rows)
    else:
        assert [at(left + 1, y) for y in rows] == [GREY] * 4, (rtl, rows)
        assert [at(right - 1, y) for y in rows] == [SHADE] * 4, (rtl, rows)
print("horizontal spin button: one 1px black seam per stepper edge in LTR and RTL, with the field and stepper faces unchanged")
'''
        )
        self._run_gtk_child(program, str(CSS))

    def test_osd_spin_field_renders_the_mirrored_etch_in_rtl(self):
        # The four OSD field groups restate the etch at equal-or-higher
        # specificity than the existing plain RTL mirror, so the OSD record
        # carries its own RTL twins. The probe renders the spin button
        # under an .osd-classed box and measures the field's edge columns
        # from its own allocation in both directions; see _run_gtk_child
        # for why this runs in a child.
        program = (
            "\nimport re\n"
            + _GTK3_CHILD_HEAD
            + r'''css = re.sub(rb"url\([^)]*\)", b"none", Path(sys.argv[1]).read_bytes())
provider = Gtk.CssProvider()
provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), provider, 800
)

def render(rtl):
    window = Gtk.OffscreenWindow()
    box = Gtk.Box()
    box.set_border_width(5)
    box.get_style_context().add_class("osd")
    spin = Gtk.SpinButton.new_with_range(0, 100, 1)
    spin.set_can_focus(False)
    if rtl:
        spin.set_direction(Gtk.TextDirection.RTL)
    box.pack_start(spin, False, False, 0)
    window.add(box)
    window.show_all()
    while Gtk.events_pending():
        Gtk.main_iteration()
    alloc = spin.get_allocation()
    pixbuf = window.get_pixbuf()
    pixels, stride, n = pixbuf.get_pixels(), pixbuf.get_rowstride(), pixbuf.get_n_channels()
    window.destroy()

    def at(x, y):
        return "#%02X%02X%02X" % tuple(pixels[y * stride + x * n:][:3])

    left, top = alloc.x, alloc.y
    right, bottom = alloc.x + alloc.width - 1, alloc.y + alloc.height - 1
    return at, left, top, right, bottom

BLACK, GREY = "#000000", "#999999"

# The etch's vertical arm reads down the field's exposed edge column at
# rows T+1, T+2, T+3 and B-1; the covered edge stays black in both
# directions. A twin spelled `inset 1px 1px #999999` would leave the RTL
# exposed edge white below the top arm, and a dropped twin would too.
for rtl in (False, True):
    at, left, top, right, bottom = render(rtl)
    rows = (top + 1, top + 2, top + 3, bottom - 1)
    if rtl:
        assert [at(left + 1, y) for y in rows] == [BLACK] * 4, (rtl, "left", rows)
        assert [at(right - 1, y) for y in rows] == [GREY] * 4, (rtl, "right", rows)
    else:
        assert [at(left + 1, y) for y in rows] == [GREY] * 4, (rtl, "left", rows)
        assert [at(right - 1, y) for y in rows] == [BLACK] * 4, (rtl, "right", rows)
print("OSD spin field: the etch's vertical arm reads at the exposed edge column in LTR and RTL, the covered edge staying black")
'''
        )
        self._run_gtk_child(program, str(CSS))

    def test_vertical_spinbutton_renders_one_pixel_joins(self):
        # The vertical spin button stacks its up stepper, the field and
        # the down stepper, and each member paints its own full 1px black
        # border, so before the border-style halves were added, both
        # field/stepper joins drew two adjacent black rows. The probe
        # measures from the widget's own allocation and finds the
        # fully-black rows, so it does not hard-code the layout: each
        # render gets a fresh offscreen window; see _run_gtk_child for
        # why this runs in a child.
        program = (
            "\nimport re\n"
            + _GTK3_CHILD_HEAD
            + r'''css = re.sub(rb"url\([^)]*\)", b"none", Path(sys.argv[1]).read_bytes())
provider = Gtk.CssProvider()
provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), provider, 800
)

def render(rtl):
    window = Gtk.OffscreenWindow()
    box = Gtk.Box()
    box.set_border_width(5)
    spin = Gtk.SpinButton.new_with_range(0, 100, 1)
    spin.set_orientation(Gtk.Orientation.VERTICAL)
    spin.set_can_focus(False)
    if rtl:
        spin.set_direction(Gtk.TextDirection.RTL)
    box.pack_start(spin, False, False, 0)
    window.add(box)
    window.show_all()
    while Gtk.events_pending():
        Gtk.main_iteration()
    alloc = spin.get_allocation()
    pixbuf = window.get_pixbuf()
    pixels, stride, n = pixbuf.get_pixels(), pixbuf.get_rowstride(), pixbuf.get_n_channels()
    window.destroy()

    def at(x, y):
        return "#%02X%02X%02X" % tuple(pixels[y * stride + x * n:][:3])

    left, top = alloc.x, alloc.y
    right, bottom = alloc.x + alloc.width - 1, alloc.y + alloc.height - 1
    return at, left, top, right, bottom

BLACK, WHITE, GREY, LIGHT, SHADE = "#000000", "#FFFFFF", "#999999", "#DDDDDD", "#AAAAAA"

for rtl in (False, True):
    at, left, top, right, bottom = render(rtl)
    rows = [y for y in range(top, bottom + 1)
            if all(at(x, y) == BLACK for x in range(left, right + 1))]
    # Measured 2026-11-11: exactly four fully-black rows — the top edge,
    # the two field/stepper joins and the bottom edge — each one row,
    # never an adjacent pair, and the 27-row stepper pitch measured that
    # day; the doubled joins the sheet painted before the halves were added
    # made two adjacent rows black at each join and the render two rows
    # taller.
    assert rows == [top, top + 27, top + 54, bottom], (rtl, rows, top, bottom)
    join1, join2 = rows[1], rows[2]
    # The column beside the left border keeps the raised up-stepper head
    # (black border row, white highlight, light face, shade above its
    # removed bottom border), the field's etched face (grey, then white
    # to its bottom border) and the down stepper's tail (white highlight
    # below its removed top border, light face, shade, black edge).
    x = left + 3
    got = [at(x, top), at(x, top + 1), at(x, top + 2),
           at(x, join1 - 1), at(x, join1), at(x, join1 + 1), at(x, join1 + 2)]
    assert got == [BLACK, WHITE, LIGHT, SHADE, BLACK, GREY, WHITE], (rtl, got)
    assert all(at(x, y) == WHITE for y in range(join1 + 2, join2)), \
        (rtl, "field face rows", [y for y in range(join1 + 2, join2)
                                  if at(x, y) != WHITE])
    assert at(x, join2) == BLACK and at(x, join2 + 1) == WHITE, (rtl,)
    lit = [y for y in range(join2 + 2, bottom - 1) if at(x, y) != LIGHT]
    assert not lit, (rtl, "down stepper face rows", lit)
    assert at(x, bottom - 1) == SHADE and at(x, bottom) == BLACK, \
        (rtl, at(x, bottom - 1), at(x, bottom))
print("vertical spin button: one 1px black line per field/stepper join in LTR and RTL, with the stepper and field faces unchanged")
'''
        )
        self._run_gtk_child(program, str(CSS))

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
        Three spellings coincide with the existing border-sharing groups,
        so their parsed dictionaries merge the carried border-style and
        the spelling counts twice — once as the existing group's member,
        once in the restating group.
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
                # The spelling is a member of the existing border-sharing
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

        # Every restatement parses after the sheet's existing tail group.
        tail = self.selectors.index("popover.emoji-picker .emoji :hover")
        for selector in expected:
            with self.subTest(selector=selector):
                if selector in merged:
                    # The merged spelling's existing group sits mid-sheet;
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

    def test_check_radio_tick_motion(self):
        """The checked and mixed marks flip with no stock transition."""
        group = (
            "radio:checked:not(:backdrop)",
            "radio:indeterminate:not(:backdrop)",
            "check:checked:not(:backdrop)",
            "check:indeterminate:not(:backdrop)",
        )
        self.assert_rule_group(dict.fromkeys(group, {"transition": "none"}))
        # The parser stores a comma group's members individually, so the
        # raw sheet pins the one byte-equal stock group: a second rule,
        # a wrongly split four-rule spelling or a stray state twin dies.
        sheet = strip_comments(self.css)
        self.assertEqual(sheet.count(", ".join(group) + " {"), 1)
        for spelling in group:
            self.assertEqual(sheet.count(spelling), 1, spelling)
        self.assertEqual(
            {s for s in self.selectors if "indeterminate:not(:backdrop)" in s},
            {"radio:indeterminate:not(:backdrop)",
             "check:indeterminate:not(:backdrop)"},
        )
        self.assertEqual(
            {s for s in self.selectors if s in group}, set(group)
        )
        # One existing tail group holds the rule last: a later append
        # keeps it behind every existing spelling it follows today.
        tail = self.selectors.index(
            "infobar > revealer > box label:link"
        )
        for spelling in group:
            self.assertGreater(
                self.selectors.index(spelling), tail, spelling
            )

    def test_check_radio_backdrop_motion_disabled_and_selected_row(self):
        """Disabled and selected-row indicators keep the existing face unfocused,
        and no ``:backdrop`` indicator repaint fades over the stock 200ms."""
        etch = "inset 1px 1px #FFFFFF, inset -1px -1px #888888"
        self.assert_rule_group(
            {
                "check:backdrop": {
                    "background-image": "none",
                    "border-color": BLACK,
                    "box-shadow": etch,
                    "transition": "none",
                },
                "radio:backdrop": {
                    "background-image": "none",
                    "border-color": BLACK,
                    "box-shadow": "none",
                    "transition": "none",
                },
            }
        )
        disabled_face = {"box-shadow": etch}
        self.assert_rule_group(
            {
                "check:backdrop:disabled": disabled_face,
                "check:checked:backdrop:disabled": disabled_face,
                "check:indeterminate:backdrop:disabled": disabled_face,
                "row:selected check": {"border-color": BLACK},
                "row:selected radio": {"border-color": BLACK},
            }
        )
        # The residue block answers the check twins only: stock's shadow
        # clear matches the existing radio face's own none, so no radio
        # backdrop-disabled spelling lands (a stray twin dies here).
        self.assertEqual(
            {s for s in self.selectors
             if ":backdrop:disabled" in s
             and (s.startswith("check") or s.startswith("radio"))},
            {"check:backdrop:disabled",
             "check:checked:backdrop:disabled",
             "check:indeterminate:backdrop:disabled"},
        )
        self.assertEqual(
            {s for s in self.selectors
             if s.startswith("row:selected check")
             or s.startswith("row:selected radio")},
            {"row:selected check", "row:selected radio"},
        )
        # The fade erasure stays bound to the two amended bare :backdrop
        # groups and the existing no-fade mark group: a stray fade on any
        # other check or radio state, a dropped amendment or a transition
        # leaking onto the existing hover, active, disabled or glyph faces
        # dies here.
        self.assertEqual(
            {s for s in self.selectors
             if (s.startswith("check") or s.startswith("radio"))
             and "transition" in self.rules[s]},
            {"check:backdrop", "radio:backdrop",
             "radio:checked:not(:backdrop)",
             "radio:indeterminate:not(:backdrop)",
             "check:checked:not(:backdrop)",
             "check:indeterminate:not(:backdrop)"},
        )
        # One existing tail block holds the five residue spellings, after
        # the amended :backdrop groups' block and before the menu record.
        top = self.css.index("radio:indeterminate:backdrop")
        bottom = self.css.index("hovered menu row")
        for spelling in (
            "check:backdrop:disabled",
            "check:checked:backdrop:disabled",
            "check:indeterminate:backdrop:disabled",
            "row:selected check, row:selected radio",
        ):
            position = self.css.index(spelling + " {")
            self.assertGreater(position, top, spelling)
            self.assertLess(position, bottom, spelling)

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
        self.assertEqual(paths[0], paths[1])


if __name__ == "__main__":
    unittest.main()
