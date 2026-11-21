"""Validate the GTK 3 Platinum sheet's spin-button focus outlines, stepper seams and RTL etch.

This module owns the spin-button slice split out of the former GTK 3 controls suite:
the spin-button field declaration, the horizontal and vertical focus outlines, the horizontal stepper seam rules,
the OSD spin field's RTL mirror, and the rendered stepper seams and vertical
joins. The rule checks read the stripped CSS through ``GtkSheetRuleCases``;
the three rendered probes run in a child interpreter (see ``_run_gtk_child``),
so the suite process itself imports no GTK.
"""

import unittest
from pathlib import Path

from support.gtk.child_probe import (
    _GTK3_SHEET_PROLOGUE,
    _GTK3_SHEET_PROVIDER,
    Gtk3ChildProbeCases,
)
from support.gtk_rule_cases import GtkSheetRuleCases
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"


class TestGtkThemeSpinbutton(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_spin_button_field(self):
        self.assert_spin_button_field(("spinbutton:not(.vertical)",))
        self.assertNotIn("spinbutton.vertical > text", self.rules)

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
            _GTK3_SHEET_PROLOGUE
            + _GTK3_SHEET_PROVIDER
            + r'''

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
        red, green, blue = pixels[y * stride + x * n:][:3]
        return f"#{red:02X}{green:02X}{blue:02X}"

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
            _GTK3_SHEET_PROLOGUE
            + _GTK3_SHEET_PROVIDER
            + r'''

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
        red, green, blue = pixels[y * stride + x * n:][:3]
        return f"#{red:02X}{green:02X}{blue:02X}"

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
            _GTK3_SHEET_PROLOGUE
            + _GTK3_SHEET_PROVIDER
            + r'''

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
        red, green, blue = pixels[y * stride + x * n:][:3]
        return f"#{red:02X}{green:02X}{blue:02X}"

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


if __name__ == "__main__":
    unittest.main()
