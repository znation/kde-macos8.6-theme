"""Rendered GTK 4 scrollbar probe."""

import os
import subprocess
import sys
import unittest

from support.gtk4_sheet import THEME_DIR, _rgb
from support.gui_tests import require_gui_opt_in
from support.platinum_palette import BLACK, FACE, GREY, TROUGH, WHITE


class TestGtk4ScrollbarProbe(unittest.TestCase):
    def test_scrollbar_faces_render(self):
        require_gui_opt_in()
        # The plain scrollbar's #EEEEEE trough band, black rim and raised
        # #DDDDDD thumb with its white/#999999 bevel are pinned from
        # rendered pixels, with the disabled scrollbar's still-opaque
        # thumb face: a trough or slider rule that never matches the
        # rendered node tree, a thumb that never paints or loses its
        # bevel, stock's beige trough or rounded thumb leaking through
        # would otherwise ship green under the declaration tests alone.
        # Pins measured 2026-11-11 in child renders; a dropped band, rim,
        # thumb face or bevel arm, or a state fade on the disabled thumb
        # leaves a pinned pixel wrong and fails. The pressed and
        # fine-tune states stay out: the landed hover/active and
        # fine-tune groups repaint the same face and raised bevel as the
        # resting thumb, so those pins would be byte-identical and add
        # nothing discriminating — the declaration tests hold the
        # spellings. Overlay scrollbars stay out: the probe builds no
        # scrolled window and no overlay-indicator widget (asserted in
        # the child), the landed overlay groups restate the same faces,
        # and the overlay declaration tests hold their margins,
        # breadths and outline. The child's literal expectations are
        # formatted from the same palette constants this suite imports,
        # so a palette change cannot desynchronize the probe's tuples
        # from the sheet's inks.
        palette = (
            f"GREY, BLACK, FACE, WHITE, TROUGH = {_rgb(GREY)}, {_rgb(BLACK)}, "
            f"{_rgb(FACE)}, {_rgb(WHITE)}, {_rgb(TROUGH)}"
        )
        result = subprocess.run(
            [sys.executable, "-c", palette + '''
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

window = Gtk.Window()
window.set_default_size(160, 320)
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
box.set_spacing(12)
window.set_child(box)
built = []
for disabled in (False, True):
    adjustment = Gtk.Adjustment.new(0, 0, 100, 1, 10, 50)
    # The thumb rides the value: at the resting value 0 it sits against
    # the trough's top border and no interior row exists above it, so
    # the value moves to 25 to leave a trough band on both sides — the
    # same 0..100/50-page adjustment the plan names.
    adjustment.set_value(25)
    scrollbar = Gtk.Scrollbar.new(Gtk.Orientation.VERTICAL, adjustment)
    scrollbar.set_size_request(24, 120)
    scrollbar.set_halign(Gtk.Align.CENTER)
    scrollbar.set_valign(Gtk.Align.CENTER)
    # A standalone scrollbar built outside a scrolled window takes no
    # overlay class, so the plain recipe is what the probe pins.
    assert not scrollbar.has_css_class("overlay-indicator"), (
        scrollbar.get_css_classes())
    if disabled:
        # The parent carries the state, as a real insensitive container
        # does: the trough's nodes must match :disabled through
        # propagation.
        holder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        holder.set_sensitive(False)
        holder.append(scrollbar)
        box.append(holder)
    else:
        box.append(scrollbar)
    assert scrollbar.get_css_name() == "scrollbar", scrollbar.get_css_name()
    rng = scrollbar.get_first_child()
    assert rng.get_css_name() == "range", rng.get_css_name()
    trough = rng.get_first_child()
    assert trough.get_css_name() == "trough", trough.get_css_name()
    slider = None
    child = trough.get_first_child()
    while child is not None:
        if child.get_css_name() == "slider":
            slider = child
        child = child.get_next_sibling()
    assert slider is not None, "the trough has no slider node"
    built.append((scrollbar, trough, slider, disabled))
window.present()

def painted(widget, w, h):
    snapshot = Gtk.Snapshot()
    Gtk.WidgetPaintable.new(widget).snapshot(snapshot, w, h)
    node = snapshot.to_node()
    renderer = window.get_renderer()
    if node is None or renderer is None or w <= 0 or h <= 0:
        return None
    viewport = Graphene.Rect()
    viewport.init(0, 0, w, h)
    texture = renderer.render_texture(node, viewport)
    pixbuf = Gdk.pixbuf_get_from_texture(texture)
    data, stride = pixbuf.get_pixels(), pixbuf.get_rowstride()
    channels = pixbuf.get_n_channels()
    def at(x, y):
        start = y * stride + x * channels
        return tuple(data[start:start + 3])
    return at

# Every position derives from the fresh allocations, in the child
# frame the landed probes record: a child widget's allocation reads
# relative to its parent's content-box origin. The scrollbar widget's
# own allocation is its painted box 1:1 (checked against a window-level
# capture when the pins were measured); the trough's painted border box
# is the range's allocation plus the trough's allocation, and the
# thumb's allocation is its painted border box — the landed thumb
# margin is 0, so the slider node's allocation paints 1:1 inside the
# trough's content box. Each pin sits clear of every border row and
# antialiasing edge; the two band pins take the middle of the trough
# interior above and below the thumb, so a thumb that drifts out of
# the middle band still reads its own face and the band pins its own
# ink on the surviving side.
def pins(r, t, s):
    tx, ty = r.x + t.x, r.y + t.y
    tw, th = t.width, t.height
    sx, sy = tx + 1 + s.x, ty + 1 + s.y
    sw, sh = s.width, s.height
    cx = sx + sw // 2
    top = (ty + 1 + sy) // 2
    bottom = (sy + sh + ty + th - 1) // 2
    assert sy - (ty + 1) >= 2 and (ty + th - 1) - (sy + sh) >= 2, (
        "the thumb leaves no trough band on both sides")
    return [((cx, sy + sh // 2), FACE),
            ((cx, sy), BLACK),
            ((cx, sy + 1), WHITE),
            ((cx, sy + sh - 2), GREY),
            ((cx, top), TROUGH),
            ((cx, bottom), TROUGH),
            ((tx, ty + th // 2), BLACK)]

disabled_pins = [0, 4, 5, 6]  # face centre, both bands, trough rim

deadline = time.monotonic() + 30
while True:
    while GLib.MainContext.default().pending():
        GLib.MainContext.default().iteration(False)
    mismatches = []
    ready = True
    for scrollbar, trough, slider, disabled in built:
        if disabled and not bool(
                scrollbar.get_state_flags() & Gtk.StateFlags.INSENSITIVE):
            ready = False
            mismatches.append(("disabled", "state not applied"))
            continue
        alloc = scrollbar.get_allocation()
        r = scrollbar.get_first_child().get_allocation()
        t, s = trough.get_allocation(), slider.get_allocation()
        w, h = alloc.width, alloc.height
        if w < 20 or h < 40 or s.width < 4 or s.height < 4:
            ready = False
            mismatches.append(("disabled" if disabled else "resting",
                               "unallocated", w, h, t.width, t.height,
                               s.width, s.height))
            continue
        at = painted(scrollbar, w, h)
        if at is None:
            ready = False
            mismatches.append(("disabled" if disabled else "resting",
                               "no paintable"))
            continue
        want = pins(r, t, s)
        if disabled:
            # The landed :disabled group keeps opacity 1, so the band,
            # rim and thumb face stay byte-equal to the resting ones;
            # any state fade leaves a pinned pixel wrong.
            want = [want[i] for i in disabled_pins]
        got = [((x, y), at(x, y), c) for (x, y), c in want if at(x, y) != c]
        mismatches.extend(("disabled" if disabled else "resting",) + g
                          for g in got)
    if ready and not mismatches:
        break
    if time.monotonic() >= deadline:
        raise SystemExit(f"scrollbar pins did not settle: {mismatches}")
    time.sleep(0.01)
print("scrollbar pins settled")
''', str(THEME_DIR)],
            env={**os.environ, "GDK_BACKEND": "x11", "GSK_RENDERER": "cairo"},
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 77:
            self.skipTest("GTK 4 introspection or an X11 display is missing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

