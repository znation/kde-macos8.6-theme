"""Validate the GTK 3 Platinum sheet's controls.

This module owns the control slice of ``tests/test_gtk_theme.py``'s split:
the spinner, level bar, switch, the control focus outlines
(the button arms and button focus outline are checked in
``tests/test_gtk_theme_buttons.py``, the spin-button focus outlines, stepper
seams and RTL etch in ``tests/test_gtk_theme_spinbutton.py``), the menu-bar and
toolbar titles, and the rendered notebook tab faces. The linked border pairs are
checked in ``tests/test_gtk_theme_linked.py``, the scale geometry and ink in
``tests/test_gtk_theme_scale.py`` and the entry fields in
``tests/test_gtk_theme_entry.py`` and the progress bar and meter faces in
``tests/test_gtk_theme_progress.py``. The shipped glyph assets are checked in
``tests/test_gtk_theme_glyphs.py``. The three
introspection tests render with a real GTK 3 in a child interpreter (see
``_run_gtk_child``); the suite process itself imports no GTK.
"""

import unittest
from pathlib import Path

from support.gtk_child_probe import (
    _GTK3_CHILD_HEAD,
    _GTK3_PIXEL_HEAD,
    _GTK3_SHEET_AND_WINDOW,
    _GTK3_SHEET_PROLOGUE,
    _GTK3_SHEET_PROVIDER,
    Gtk3ChildProbeCases,
)
from support.gtk_css import strip_comments
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    ETCH_DARK,
)
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    TROUGH,
    WHITE,
)
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"

class TestGtkThemeControls(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

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
            _GTK3_SHEET_PROLOGUE
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
            _GTK3_SHEET_PROLOGUE
            + _GTK3_SHEET_PROVIDER
            + r'''

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
            _GTK3_SHEET_PROLOGUE
            + _GTK3_SHEET_PROVIDER
            + r'''

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
            _GTK3_SHEET_PROLOGUE
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

    def test_checkbutton_focus_outline(self):
        self.assert_dotted_focus_outline("checkbutton:focus")

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


if __name__ == "__main__":
    unittest.main()
