"""Rendered GTK 4 spin-field probe."""

import unittest

from support.gtk4_child_probe import run_gtk4_probe
from support.gui_tests import require_gui_opt_in


class TestGtk4SpinProbe(unittest.TestCase):
    def test_spin_field_renders_the_mirrored_etch_in_rtl(self):
        require_gui_opt_in()
        # The RTL spin field's exposed right edge must read the mirrored
        # etch arm in a plain and an .osd overlay capture alike, and the
        # existing `.osd spinbutton:dir(rtl)` state twins must govern their
        # own states: the probe captures the plain field, the resting .osd
        # field, the focused .osd field and the insensitive .osd field.
        # Pins measured 2026-11-11 in child renders on this host, after
        # the mirrors landed; a dropped plain, .osd or focused mirror, a
        # foreign value, a mirror that loses its specificity race or a
        # state twin spelled with the LTR arm leaves the exposed edge
        # field-white and fails. One mask: a dropped resting .osd twin is
        # pixel-invisible — the plain mirror restates the same arm over
        # the resting overlay state — so the declaration test's token
        # sweep and whole-dict pins hold that spelling.
        run_gtk4_probe(self, '''
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
root = Path(sys.argv[1])
provider = Gtk.CssProvider()
provider.load_from_data((root / "gtk-4.0/gtk.css").read_bytes().replace(
    b"../assets/", (root / "assets").as_uri().encode() + b"/"))
Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider, 801)

GREY, BLACK, WHITE = (153, 153, 153), (0, 0, 0), (255, 255, 255)

def pins(w, h):
    # The exposed right edge column reads the mirrored grey arm down its
    # interior rows, the top border row stays black, and the covered left
    # edge keeps the stepper button's white bevel highlight rather than
    # any etch grey; all positions are clear of glyph rows.
    return [((w - 2, 0), BLACK),
            ((w - 2, 1), GREY), ((w - 2, 2), GREY),
            ((w - 2, 3), GREY), ((w - 2, h - 2), GREY),
            ((2, 5), WHITE)]

def capture(osd, focus, disabled):
    window = Gtk.Window()
    spin = Gtk.SpinButton.new_with_range(0, 100, 1)
    assert spin.get_css_name() == "spinbutton"
    spin.set_focusable(focus or disabled)
    spin.set_size_request(160, -1)
    # Keep the spin field at its natural size whatever size the window
    # manager gives the presented window: a stretched field would both
    # change the pinned geometry and scale the render the paintable
    # produces, so aligning it to its own preferred box keeps the pins
    # about the sheet, not about the host's window management.
    spin.set_halign(Gtk.Align.CENTER)
    spin.set_valign(Gtk.Align.CENTER)
    spin.set_direction(Gtk.TextDirection.RTL)
    if disabled:
        spin.set_sensitive(False)
    if osd:
        box = Gtk.Box()
        box.add_css_class("osd")
        box.append(spin)
        window.set_child(box)
    else:
        window.set_child(spin)
    window.present()
    if focus:
        spin.grab_focus()
    deadline = time.monotonic() + 30
    while True:
        while GLib.MainContext.default().pending():
            GLib.MainContext.default().iteration(False)
        # The spin field carries a 1px stock margin, so its width/height
        # getters exclude the margin box and snapshotting at them would
        # resample the render; snapshot at the allocation instead.
        alloc = spin.get_allocation()
        w, h = alloc.width, alloc.height
        if w > 10 and h > 10:
            snapshot = Gtk.Snapshot()
            Gtk.WidgetPaintable.new(spin).snapshot(snapshot, w, h)
            node = snapshot.to_node()
            renderer = window.get_renderer()
            if node is not None and renderer is not None:
                viewport = Graphene.Rect()
                viewport.init(0, 0, w, h)
                texture = renderer.render_texture(node, viewport)
                pixbuf = Gdk.pixbuf_get_from_texture(texture)
                data, stride, n = (pixbuf.get_pixels(),
                                   pixbuf.get_rowstride(),
                                   pixbuf.get_n_channels())
                def at(x, y):
                    start = y * stride + x * n
                    return tuple(data[start:start + 3])
                # A focused capture only exercises its state twin once the
                # field really holds focus (the spin button delegates focus
                # to its inner text, so check the FOCUS_WITHIN state flag
                # rather than has_focus), and a disabled capture only once
                # the insensitive state really applied; both settle within
                # the deadline or the capture fails there.
                settled = (
                    not focus
                    or bool(spin.get_state_flags() & Gtk.StateFlags.FOCUS_WITHIN)
                ) and (
                    not disabled
                    or bool(spin.get_state_flags() & Gtk.StateFlags.INSENSITIVE)
                )
                want = pins(w, h)
                if settled and all(at(x, y) == c for (x, y), c in want):
                    window.destroy()
                    return
        if time.monotonic() >= deadline:
            got = ("unsettled" if w <= 10 or h <= 10 else
                   [((x, y), at(x, y), c)
                    for (x, y), c in pins(w, h) if at(x, y) != c])
            raise SystemExit(f"osd={osd}: pins did not settle: {got}")
        time.sleep(0.01)

capture(False, False, False)
capture(True, False, False)
capture(True, True, False)
capture(True, False, True)
print("spin field: the etch's mirrored arm reads down the exposed right edge in RTL, plain and .osd in the resting, focused and insensitive states")
''')


if __name__ == "__main__":
    unittest.main()
