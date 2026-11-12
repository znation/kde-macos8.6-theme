"""Rendered GTK 4 scale probe."""

import os
import subprocess
import sys
import unittest

from support.gtk4_sheet import THEME_DIR, _rgb
from support.gui_tests import require_gui_opt_in
from support.platinum_palette import BLACK, FACE, GREY, TROUGH, WHITE


class TestGtk4ScaleProbe(unittest.TestCase):
    def test_scale_faces_render(self):
        require_gui_opt_in()
        # The plain slider's trough band, black rim, inset shadow arm,
        # transparent fill/highlight and raised #DDDDDD thumb are pinned
        # from rendered pixels, with the disabled thumb's flat grey twin:
        # a trough rule that never matches the rendered node tree, a thumb
        # that never paints or loses its bevel, or stock's accent-coloured
        # fill or highlight leaking through the existing transparent faces
        # would otherwise ship green under the declaration tests alone.
        # Pins measured 2026-11-11 in child renders; a dropped band, rim
        # or bevel arm, a leaked fill or a disabled twin keeping the raised
        # bevel or the black rim leaves a pinned pixel wrong and fails.
        # The pressed state stays out: the existing hover/active group
        # repaints the same face, border and raised bevel as the resting
        # thumb, so pressed pins would be byte-identical and add nothing
        # discriminating; the spelling stays held by test_scale. The
        # disabled trough keeps the existing band, black rim and inset arm
        # (the `scale > trough:disabled` group repaints only the face and
        # border colour byte-equal), so its pins repeat the resting ones.
        # The child's literal expectations are formatted from the same
        # palette constants this suite imports, so a palette change cannot
        # desynchronize the probe's tuples from the sheet's inks.
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
window.set_default_size(160, 140)
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
box.set_spacing(12)
window.set_child(box)
built = []
for disabled in (False, True):
    scale = Gtk.Scale.new(Gtk.Orientation.HORIZONTAL,
                          Gtk.Adjustment(value=50, lower=0, upper=100,
                                         step_increment=1, page_increment=10,
                                         page_size=0))
    scale.set_draw_value(False)
    scale.set_size_request(120, -1)
    scale.set_halign(Gtk.Align.CENTER)
    scale.set_valign(Gtk.Align.CENTER)
    if disabled:
        # The parent carries the state, as a real insensitive container
        # does: the trough's nodes must match :disabled through
        # propagation.
        holder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        holder.set_sensitive(False)
        holder.append(scale)
        box.append(holder)
    else:
        box.append(scale)
    trough = scale.get_first_child()
    assert trough.get_css_name() == "trough", trough.get_css_name()
    slider = None
    child = trough.get_first_child()
    while child is not None:
        if child.get_css_name() == "slider":
            slider = child
        child = child.get_next_sibling()
    assert slider is not None, "the trough has no slider node"
    built.append((scale, trough, slider, disabled))
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

# Every position derives from the fresh allocations. The scale's content
# origin is the sheet's bare `scale` group's 12px padding, and a child
# widget's allocation reads relative to its parent's content-box origin,
# so the trough's painted border box is the content origin plus the
# trough's allocation. The thumb's allocation is its margin box — the
# existing `-5px` thumb margin shrinks it — so its painted border box sits
# 5px outside that box on every side and measures 10px more each way,
# overhanging the trough's band the way the existing recipe states. Each
# pin sits clear of every border row and antialiasing edge, positions
# unchanged from the allocations the capture itself used.
CONTENT = 12  # the sheet's bare `scale` padding
MARGIN = 5    # the existing thumb margin's -5px magnitude

def pins(t, s, disabled):
    tx, ty = CONTENT + t.x, CONTENT + t.y
    tw, th = t.width, t.height
    sx = tx + 1 + s.x - MARGIN
    sy = ty + 1 + s.y - MARGIN
    sw, sh = s.width + 2 * MARGIN, s.height + 2 * MARGIN
    cx = sx + sw // 2
    rim, top_arm, bottom_arm = (
        (GREY, FACE, FACE) if disabled else (BLACK, WHITE, GREY))
    return [((cx, sy + sh // 2), FACE),
            ((cx, sy), rim),
            ((cx, sy + 1), top_arm),
            ((cx, sy + sh - 2), bottom_arm),
            ((tx + 3, ty + th // 2), TROUGH),
            ((tx + tw - 3, ty + th // 2), TROUGH),
            ((tx + tw - 3, ty), BLACK),
            ((tx + tw - 3, ty + 1), GREY)]

deadline = time.monotonic() + 30
while True:
    while GLib.MainContext.default().pending():
        GLib.MainContext.default().iteration(False)
    mismatches = []
    ready = True
    for scale, trough, slider, disabled in built:
        if disabled and not bool(
                scale.get_state_flags() & Gtk.StateFlags.INSENSITIVE):
            ready = False
            mismatches.append(("disabled", "state not applied"))
            continue
        alloc = scale.get_allocation()
        w, h = alloc.width, alloc.height
        t, s = trough.get_allocation(), slider.get_allocation()
        if w < 40 or h < 10 or t.width < 8 or t.height < 6 or s.width < 4:
            ready = False
            mismatches.append(("disabled" if disabled else "resting",
                               "unallocated", w, h, t.width, t.height,
                               s.width, s.height))
            continue
        at = painted(scale, w, h)
        if at is None:
            ready = False
            mismatches.append(("disabled" if disabled else "resting",
                               "no paintable"))
            continue
        want = pins(t, s, disabled)
        got = [((x, y), at(x, y), c) for (x, y), c in want if at(x, y) != c]
        mismatches.extend(("disabled" if disabled else "resting",) + g
                          for g in got)
    if ready and not mismatches:
        break
    if time.monotonic() >= deadline:
        raise SystemExit(f"scale pins did not settle: {mismatches}")
    time.sleep(0.01)
print("scale pins settled")
''', str(THEME_DIR)],
            env={**os.environ, "GDK_BACKEND": "x11", "GSK_RENDERER": "cairo"},
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 77:
            self.skipTest("GTK 4 introspection or an X11 display is missing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
