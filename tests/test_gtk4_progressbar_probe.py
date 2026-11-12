"""Rendered GTK 4 progressbar probe."""

import os
import subprocess
import sys
import unittest

from support.gtk4_sheet import THEME_DIR
from support.gui_tests import require_gui_opt_in


class TestGtk4ProgressbarProbe(unittest.TestCase):
    def test_progressbar_faces_render(self):
        require_gui_opt_in()
        # The plain meter's trough face, black rim, inset shadow arm, fill
        # and disabled twin are pinned from rendered pixels: a trough rule
        # that never matches the rendered node tree, a fill that never
        # paints or a disabled fill that loses its grey would otherwise
        # ship green under the declaration tests alone. Pins measured
        # 2026-11-11 in child renders; a dropped fill, a recoloured face,
        # a lost rim or arm, or a disabled twin repainting the selection
        # fill leaves a pinned pixel wrong and fails. One mask: the landed
        # opaque-disabled filter arm is pixel-invisible in the plain child
        # — the only competing meter filter arm lives in the integration
        # library's base.css resource (line 1860, recorded in the sheet),
        # which a plain toolkit child never loads — so the filter spelling
        # is held by test_progressbar_disabled_filter, and the disabled
        # bar's full-strength faces are what this probe establishes.
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

GREY, BLACK, FACE, SELECTION, TROUGH = (
    (153, 153, 153), (0, 0, 0), (221, 221, 221),
    (204, 204, 255), (238, 238, 238))

window = Gtk.Window()
window.set_default_size(160, 90)
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
box.set_spacing(12)
window.set_child(box)
built = []
for disabled in (False, True):
    bar = Gtk.ProgressBar()
    bar.set_fraction(0.5)
    bar.set_show_text(False)
    bar.set_size_request(120, -1)
    if disabled:
        # The parent carries the state, as a real insensitive container
        # does: the bar's nodes must match :disabled through propagation.
        holder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        holder.set_sensitive(False)
        holder.append(bar)
        box.append(holder)
    else:
        box.append(bar)
    trough = bar.get_first_child()
    assert trough.get_css_name() == "trough", trough.get_css_name()
    progress = trough.get_first_child()
    assert progress.get_css_name() == "progress", progress.get_css_name()
    built.append((bar, trough, progress, disabled))
window.present()

WANT = {"fill": SELECTION, "border": BLACK, "arm": GREY, "face": TROUGH}
WANT_DISABLED = {"fill": GREY, "border": BLACK, "arm": GREY, "face": TROUGH}

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

# Pins for one meter capture. The capture is the bar widget's own
# allocation, whose painted box it equals 1:1 (the trough fills the bar's
# box). The filled half spans the progress child's allocation width from
# the content box's leading edge, so every position derives from the fresh
# allocations; each pin sits clear of every border row and the 1px inset
# shadow arm. The fill paints a two-row band vertically centred in the
# trough's interior, so the interior row h//2 is inside it; a build that
# paints the fill at full interior height keeps that row inside it too.
def pins(w, h, pw):
    x = 1 + pw // 2
    return [((x, h // 2), "fill"),
            ((x, 0), "border"),
            ((w - 3, 1), "arm"),
            ((w - 3, h // 2), "face")]

deadline = time.monotonic() + 30
mismatches = []
settled = False
while not settled:
    while GLib.MainContext.default().pending():
        GLib.MainContext.default().iteration(False)
    mismatches = []
    bar_height = 0
    for bar, trough, progress, disabled in built:
        w, h = bar.get_width(), bar.get_height()
        if w < 12 or h < 12:
            mismatches.append(("disabled" if disabled else "enabled",
                               "unallocated", w, h))
            continue
        at = painted(bar, w, h)
        if at is None:
            mismatches.append(("disabled" if disabled else "enabled",
                               "no paintable"))
            continue
        pw = progress.get_allocation().width
        want = WANT_DISABLED if disabled else WANT
        got = [((x, y), at(x, y), want[label])
               for (x, y), label in pins(w, h, pw) if at(x, y) != want[label]]
        mismatches.extend(
            ("disabled" if disabled else "enabled",) + g for g in got)
        if not disabled:
            bar_height = h
    if len(mismatches) == 0 and bar_height > 0:
        atw = painted(window, window.get_width(), window.get_height())
        if atw is None:
            mismatches.append(("window", "no paintable"))
        else:
            balloc = built[0][0].get_allocation()
            calloc = built[0][0].get_parent().get_allocation()
            x = (calloc.x + balloc.x
                 + 1 + built[0][2].get_allocation().width // 2)
            y = calloc.y + balloc.y + bar_height
            got = atw(x, y)
            if got == FACE:
                settled = True
            else:
                mismatches.append(("window", (x, y), got, FACE))
    else:
        mismatches.append(("window", "bars not settled"))
    if settled:
        break
    if time.monotonic() >= deadline:
        raise AssertionError(f"meter pins did not settle: {mismatches}")
    time.sleep(0.01)
print("meter pins settled")
''', str(THEME_DIR)],
            env={**os.environ, "GDK_BACKEND": "x11", "GSK_RENDERER": "cairo"},
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 77:
            self.skipTest("GTK 4 introspection or an X11 display is missing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
