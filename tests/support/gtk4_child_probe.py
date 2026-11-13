"""Parent-side runner for the GTK 4 rendered pixel probes.

The seven ``tests/test_gtk4_*_probe.py`` suites render their widgets in a
child interpreter and assert on the pixels it samples. This module holds
the parent half they share: the child's environment (X11 backend, cairo
renderer), the theme directory it is handed as ``sys.argv[1]``, the
120-second bound, the exit-77 skip, and the child program's bootstrap
prologue (:data:`GTK4_PROBE_PROLOGUE`). Each suite still owns its own
widget-building half, interpolated after the prologue.

``tests/test_gtk4_spin_probe.py`` deliberately keeps its own prologue: its
child never sets ``gtk-theme-name``. ``tests/test_gtk_view_census.py``
runs its own GTK 4 children and reads their result itself, so it does not
use this runner (deliberately left).

``tests/test_gtk_view_census.py`` runs its own GTK 4 children and reads
their result itself, so it does not use this runner (deliberately left).
"""

import os
import subprocess
import sys

from support.gtk4_sheet import THEME_DIR

# The bootstrap the six theme-loading probe children share, byte for byte:
# import and init GTK 4 (a missing gi module or version, or no X11 display,
# exits 77 and the test skips), point the theme selection at Adwaita so the
# sheet's provider races a real theme rather than the empty default, and
# load the theme's ``gtk-4.0/gtk.css`` with its asset URIs rewritten to the
# repo tree, at priority 801 above GTK's USER priority. ``spin_probe``
# leaves the theme-name line out; its child keeps its own prologue.
GTK4_PROBE_PROLOGUE = '''
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
Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider, 801)'''  # no trailing newline: suites interpolate after it verbatim.


def run_gtk4_probe(test, program):
    """Run the GTK 4 pixel *program* in a fresh child interpreter.

    The child receives ``THEME_DIR`` as ``sys.argv[1]``. Exit 77 skips
    *test* (introspection or an X11 display is missing); any other
    non-zero exit fails it with the child's output attached.
    """
    result = subprocess.run(
        [sys.executable, "-c", program, str(THEME_DIR)],
        env={**os.environ, "GDK_BACKEND": "x11", "GSK_RENDERER": "cairo"},
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode == 77:
        test.skipTest("GTK 4 introspection or an X11 display is missing")
    test.assertEqual(result.returncode, 0, result.stdout + result.stderr)
