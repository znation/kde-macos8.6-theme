"""Rendered GTK 4 indicator probe."""

import os
import subprocess
import sys
import unittest

from support.gtk4_sheet import THEME_DIR
from support.gui_tests import require_gui_opt_in


class TestGtk4IndicatorsProbe(unittest.TestCase):
    def test_mixed_indicators_draw_black_dashes(self):
        require_gui_opt_in()
        # Isolate GTK 4 from the GTK 3 introspection used by the other suite.
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
for radio in (False, True):
    window = Gtk.Window()
    button = Gtk.CheckButton()
    peer = Gtk.CheckButton()
    if radio:
        button.set_group(peer)
    button.set_inconsistent(True)
    button.set_focusable(False)
    window.set_child(button)
    window.present()
    try:
        indicator = button.get_first_child()
        name = "radio" if radio else "check"
        assert indicator.get_css_name() == name
        face = (255, 255, 255) if radio else (221, 221, 221)
        dash = [(x, y) for x in range(4, 12) for y in (7, 8)]
        surround = [
            (x, y) for x in range(4, 12) for y in (6, 9)
        ] + [(3, 7), (12, 7)]

        def painted():
            snapshot = Gtk.Snapshot()
            Gtk.WidgetPaintable.new(indicator).snapshot(snapshot, 16, 16)
            node = snapshot.to_node()
            renderer = window.get_renderer()
            if node is None or renderer is None:
                # Not allocated or realized yet: no frame to inspect.
                return None
            viewport = Graphene.Rect()
            viewport.init(0, 0, 16, 16)
            texture = renderer.render_texture(node, viewport)
            pixbuf = Gdk.pixbuf_get_from_texture(texture)
            data, stride = pixbuf.get_pixels(), pixbuf.get_rowstride()
            channels = pixbuf.get_n_channels()
            def at(x, y):
                start = y * stride + x * channels
                return tuple(data[start:start + 3])
            return at

        # Wait for the indicator's first correctly painted frame instead of a
        # fixed wall-clock settle: under CPU load the toolkit's async style and
        # paint work can outlast a short settle, which made this test fail on a
        # busy machine. A sheet that never paints the dash still fails, after
        # the deadline, with the pixel tuple that is wrong.
        deadline = time.monotonic() + 30
        while True:
            while GLib.MainContext.default().pending():
                GLib.MainContext.default().iteration(False)
            at = painted()
            if at is not None and all(
                at(x, y) == (0, 0, 0) for x, y in dash
            ) and all(at(x, y) == face for x, y in surround):
                break
            if time.monotonic() >= deadline:
                if at is None:
                    raise AssertionError(
                        f"{name}: indicator produced no paintable node"
                    )
                for x, y in dash:
                    assert at(x, y) == (0, 0, 0), (name, x, y, at(x, y))
                for x, y in surround:
                    assert at(x, y) == face, (name, x, y, at(x, y))
                raise AssertionError(f"{name}: indicator did not settle")
            time.sleep(0.01)
        print(name + ": black dash at columns 4–11, rows 7–8; face surrounds it")
    finally:
        window.destroy()
''', str(THEME_DIR)],
            env={**os.environ, "GDK_BACKEND": "x11", "GSK_RENDERER": "cairo"},
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 77:
            self.skipTest("GTK 4 introspection or an X11 display is missing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

