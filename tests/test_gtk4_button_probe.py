"""Rendered GTK 4 button probe."""

import os
import subprocess
import sys
import unittest

from support.gtk4_sheet import THEME_DIR, _rgb
from support.gui_tests import require_gui_opt_in
from support.platinum_palette import BLACK, BUTTON_SHADOW, FACE, WHITE


class TestGtk4ButtonProbe(unittest.TestCase):
    def test_button_faces_render(self):
        require_gui_opt_in()
        # The plain push button's raised face, black border and white/#AAAAAA
        # bevel are pinned from rendered pixels, with the pressed button's
        # inverted twin: a button rule that never matches the rendered node
        # tree, a bevel arm that never paints or a pressed state that leaks
        # the resting bevel would otherwise ship green under the declaration
        # tests alone. Pins measured 2026-11-11 in child renders; a dropped
        # face, border, raised arm or inverted active twin leaves a pinned
        # pixel wrong and fails. The disabled state stays out: the landed
        # button:disabled group keeps the resting face, border and raised
        # bevel byte-equal and dims only the label ink to #888888, so a
        # childless disabled button pins nothing new; the spelling stays
        # held by test_button_disabled_and_backdrop.
        # The child's literal expectations are formatted from the same
        # palette constants this suite imports, so a palette change cannot
        # desynchronize the probe's tuples from the sheet's inks.
        palette = (
            f"FACE, BLACK, WHITE, SHADOW = {_rgb(FACE)}, {_rgb(BLACK)}, "
            f"{_rgb(WHITE)}, {_rgb(BUTTON_SHADOW)}"
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
window.set_default_size(160, 120)
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
box.set_spacing(12)
window.set_child(box)
buttons = []
for active in (False, True):
    button = Gtk.Button()
    # Childless: no label child, so no glyph row becomes a fixture.
    button.set_size_request(24, 24)
    button.set_focusable(False)
    if active:
        button.set_state_flags(Gtk.StateFlags.ACTIVE, True)
    box.append(button)
    buttons.append(button)
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

# Every position derives from the button's fresh allocation, which is its
# painted border box 1:1 (checked against a window-level capture when the
# pins were measured): the interior centre reads the #DDDDDD face, the top
# row the #000000 border, and each inset arm sits one pixel inside its
# border row or column — the raised bevel's white top arm and #AAAAAA
# bottom-right arm, swapped for the pressed button's inverted twin.
def pins(w, h, active):
    top_arm, bottom_arm = (WHITE, SHADOW) if not active else (SHADOW, WHITE)
    return [((w // 2, h // 2), FACE),
            ((w // 2, 0), BLACK),
            ((w // 2, 1), top_arm),
            ((w - 2, h - 2), bottom_arm)]

deadline = time.monotonic() + 30
while True:
    while GLib.MainContext.default().pending():
        GLib.MainContext.default().iteration(False)
    mismatches = []
    ready = True
    for button, active in zip(buttons, (False, True)):
        # Snapshot at the allocation, not the width/height getters: as the
        # landed spin probe records, the getters exclude the margin box and
        # snapshotting at them would resample the render.
        alloc = button.get_allocation()
        w, h = alloc.width, alloc.height
        if w < 12 or h < 12:
            ready = False
            mismatches.append(("active" if active else "resting",
                               "unallocated", w, h))
            continue
        at = painted(button, w, h)
        if at is None:
            ready = False
            mismatches.append(("active" if active else "resting",
                               "no paintable"))
            continue
        # A pressed capture only exercises the inverted twin once the
        # ACTIVE state flag really applied; it settles within the deadline
        # or the capture fails there.
        if active and not bool(button.get_state_flags() & Gtk.StateFlags.ACTIVE):
            ready = False
            mismatches.append(("active", "state not applied"))
            continue
        want = pins(w, h, active)
        got = [((x, y), at(x, y), c) for (x, y), c in want if at(x, y) != c]
        mismatches.extend(("active" if active else "resting",) + g for g in got)
    if ready and not mismatches:
        break
    if time.monotonic() >= deadline:
        raise SystemExit(f"button pins did not settle: {mismatches}")
    time.sleep(0.01)
print("button pins settled")
''', str(THEME_DIR)],
            env={**os.environ, "GDK_BACKEND": "x11", "GSK_RENDERER": "cairo"},
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 77:
            self.skipTest("GTK 4 introspection or an X11 display is missing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
