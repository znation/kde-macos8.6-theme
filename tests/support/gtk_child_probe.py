"""Shared GTK 3 child-probe harness for the offscreen pixel probes.

Everything the GTK 3 offscreen pixel probes share: the child
interpreter's gi imports with their exit-77 skip guards, the sheet provider
the ``Gtk.OffscreenWindow`` paints with, and the pixel reader the assertions
sample through. The provider block ships twice over: ``_GTK3_SHEET_PROVIDER``
is the screen registration alone, and ``_GTK3_SHEET_AND_WINDOW`` appends the
one ``Gtk.OffscreenWindow`` line for probes that draw a single window. The middle of each program -- which bytes the
sheet is loaded from and which widget is drawn -- stays in the test that
owns it; ``tests/test_gtk_view_census.py``'s ``_CHILD_HEAD`` is the GTK 4
counterpart of the same isolation pattern.

The GTK work runs in a child interpreter, never in the suite process: a
child does the GTK introspection work and asserts on the pixels it draws;
the parent only judges its exit status, attaching the child's output to
the failure. Exit 77 is the skip marker ``tests/test_gtk4_theme.py``
established: introspection or a display is missing, so the child prints
its own skip reason first.

The child process is not only a sandbox: an in-process ``import gi``
leaves GLib's C worker threads in the suite process, which
``threading.active_count()`` cannot see, so every later
``tests/support/snippet_child.py`` ``os.fork`` FIFO guard would run
from a multi-threaded parent -- Python 3.12+ warns about that as a
deadlock hazard in the child, and a future Python may refuse it
outright. The suite therefore never imports ``gi`` in-process
(``tests/test_no_gtk_introspection.py`` pins that).
"""

import subprocess
import sys

_GTK3_CHILD_HEAD = '''import sys
from pathlib import Path

try:
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, Gtk
except (ImportError, ValueError):
    print("GTK 3 introspection is not installed")
    sys.exit(77)
if Gdk.Screen.get_default() is None:
    print("no display for GTK 3")
    sys.exit(77)
'''
_GTK3_SHEET_PROVIDER = '''provider = Gtk.CssProvider()
provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), provider, 800
)
'''
_GTK3_SHEET_AND_WINDOW = _GTK3_SHEET_PROVIDER + "window = Gtk.OffscreenWindow()\n"
_GTK3_PIXEL_HEAD = '''window.show_all()
while Gtk.events_pending():
    Gtk.main_iteration()
pixbuf = window.get_pixbuf()
pixels, stride, n = pixbuf.get_pixels(), pixbuf.get_rowstride(), pixbuf.get_n_channels()

def at(x, y):
    return "#%02X%02X%02X" % tuple(pixels[y * stride + x * n:][:3])

'''


def run_gtk_child(test, program, *paths):
    """Run the GTK 3 pixel *program* in a fresh child interpreter.

    *paths* are the child's ``sys.argv[1:]``. See the module docstring for
    why the GTK work never runs in the suite process.
    """
    result = subprocess.run(
        [sys.executable, "-c", program, *paths],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode == 77:
        test.skipTest(result.stdout.strip() or "GTK 3 is not available")
    test.assertEqual(result.returncode, 0, result.stdout + result.stderr)
