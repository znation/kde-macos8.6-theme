"""Validate the GTK 3 Platinum sheet's view field, viewport and frame borders.

This module owns the frame slice split out of the former GTK 3 controls suite:
the disabled view's white field and grey ink, the scrolled viewport's frame
(the declaration and the drawn frame), and the flat frame's border and drawn
frame. The declaration tests read the stripped CSS through ``GtkSheetRuleCases``;
the drawn probes render with a real GTK 3 in a child interpreter (see
``_run_gtk_child``), so the suite process itself imports no GTK.
"""

import unittest
from pathlib import Path

from support.gtk_child_probe import (
    _GTK3_PIXEL_HEAD,
    _GTK3_SHEET_AND_WINDOW,
    _GTK3_SHEET_PROLOGUE,
    _GTK3_SHEET_PROVIDER,
    Gtk3ChildProbeCases,
)
from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"


class TestGtkThemeFrames(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
