"""Record GTK 4 view-family class facts and rendered selected/disabled faces.

The text node cannot be reached by a widget-tree census. This module records
that historical limitation, the rendered selected face, and the rendered
disabled field after the disabled-face selector was added.

The census runs GTK 4 child interpreters under the suite's own
``GDK_BACKEND=x11`` / ``GSK_RENDERER=cairo`` pattern (see
``tests/test_gtk4_theme.py::test_mixed_indicators_draw_black_dashes``):
each child exits 77 without GTK 4 introspection or an X11 display, and the
test skips instead of failing. Sheet loading uses the existing ``../assets/``
URI replacement, so ``tests/test_icon_sources_resolve_to_shipped_files``'s
URL grep stays untouched.

Census findings, recorded 2026-11-05 during the probe run:

- **Probe 1 (class census).** A child interpreter created bare
  ``Gtk.TextView``, ``Gtk.IconView`` and ``Gtk.ListView`` widgets and reported
  each node's ``get_css_name()`` and ``get_css_classes()``; every one of the
  three view-family widget nodes carried the ``view`` class and no others
  (``['view']``), and a presented window's own node reported ``['background']``
  (its CSS node name is ``window``). This extends the existing icon-view
  record's census to the whole view family.

- **Probe 1b (text-node reachability).** The same child walked a presented
  ``Gtk.TextView`` with ``get_first_child()`` / ``get_next_sibling()`` and
  found no widget child at all — public GTK 4.18 introspection never parents
  the ``text`` widget where a widget-tree walk can see it. A class-list
  census therefore cannot resolve the ``textview > text`` question directly;
  the finding is pinned, so a future GTK that starts parenting the node
  fails the pin honestly and gets the recorded route re-derived there.

- **Probe 2 (rendered census, selected face).** The same pipeline loaded the
  shipped sheet, presented a ``Gtk.TextView`` whose whole ``Hello World``
  buffer is selected, rendered it offscreen at 220x60 through
  ``Gtk.WidgetPaintable`` + ``Gtk.Snapshot.to_node()`` + the window
  renderer's ``render_texture`` + ``Gdk.pixbuf_get_from_texture``, computed
  the band of exact ``#CCCCFF`` pixels
  (``tests/support/platinum_palette.py::SELECTION``, the existing
  ``textview > text > selection`` fill), and found all four extreme pixels
  of the band's bounding box inside that exact band: the selected text face
  is flat and unrounded today. Stock's ``textview > text:selected`` radius
  members (libadwaita ``/org/gnome/Adwaita/styles/base.css`` line 2507's 9px
  25%-accent wash for integration-library surfaces, and plain-GTK
  ``/org/gtk/libgtk/theme/Default/Default-light.css`` in
  ``/usr/lib/x86_64-linux-gnu/libgtk-4.so.1``'s line-21 ``border-radius:
  3px`` group, whose comma group carries the byte-twin members
  ``textview > text:selected:focus`` and ``textview > text:selected``) ride
  no visible corner ship here today: the existing sheet's flat selection fill
  owns the face and the existing selection-surface corner records square the
  compound members.

- **Historical Probe 2b (rendered census, before the white restatement).** The
  same scroll rendered a ``set_sensitive(False)``
  ``Gtk.TextView`` as a flat single-colour 220x60 frame entirely ``#FAF9F8``
  in every corner: that is the plain-GTK stock resource's disabled view face
  (``Default-light.css`` line 19 group ``.view:disabled, iconview:disabled,
  textview > text:disabled { color: #929595; background-color: #faf9f8; }``,
  quoted in resource order; 60% of ``@window_bg_color #DDDDDD`` over
  ``@view_bg_color #FFFFFF`` would compute ``#EBEBEB`` instead), not the
  existing white field. This was the historical finding that motivated the
  disabled text-node restatement; the isolated probe now pins plain GTK
  pixels to white. It does not measure libadwaita's later transparent rule.
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

from support.gtk4_child_probe import GTK4_PROBE_PROLOGUE
from support.platinum_palette import SELECTION
from support.repo_root import ROOT
from support.gui_tests import require_gui_opt_in

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"

# The bare bootstrap the two census children share: the suite's GTK 4
# isolation pattern (a missing gi module or version, or no X11 display,
# exits 77 and the test skips) and the non-blocking pending-iteration
# helper the suite's indicator test uses instead of a blocking main-loop
# call. The class census deliberately runs without a theme selection, so
# these children do not interpolate the shared probe prologue that the
# two face children below use.
_CHILD_HEAD = '''
import sys, time
try:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, Gdk, GLib, Graphene
except (ImportError, ValueError):
    sys.exit(77)
Gtk.init()
if Gdk.Display.get_default() is None:
    sys.exit(77)

def pending():
    while GLib.MainContext.default().pending():
        GLib.MainContext.default().iteration(False)
'''


def _selection_rgb():
    """Derive the pinned selection pixel triple from the palette constant."""
    hex_text = SELECTION.lstrip("#")
    return tuple(int(hex_text[i:i + 2], 16) for i in (0, 2, 4))


def _run_child(source, *args):
    """Run *source* as a GTK 4 child interpreter; 77 means the skip path."""
    require_gui_opt_in()
    return subprocess.run(
        [sys.executable, "-c", source, *[str(a) for a in args]],
        env={**os.environ, "GDK_BACKEND": "x11", "GSK_RENDERER": "cairo"},
        capture_output=True, text=True, timeout=120,
    )


CENSUS_CHILD = _CHILD_HEAD + '''
for make in (Gtk.TextView, Gtk.IconView, Gtk.ListView):
    widget = make()
    print("%s %r" % (widget.get_css_name(), widget.get_css_classes()))
window = Gtk.Window()
window.present()
deadline = time.monotonic() + 2.0
while True:
    pending()
    if window.is_visible() or time.monotonic() >= deadline:
        break
    time.sleep(0.01)
print("%s %r" % (window.get_css_name(), window.get_css_classes()))
'''

UNREACHABLE_CHILD = _CHILD_HEAD + '''
def widget_count(widget):
    total = 0
    child = widget.get_first_child()
    while child is not None:
        total += 1 + widget_count(child)
        child = child.get_next_sibling()
    return total

text_view = Gtk.TextView()
window = Gtk.Window()
window.set_child(text_view)
window.present()
# Sleep-poll the whole two-second window: if a future GTK starts parenting
# the text node, any sighting inside the window fails the pin honestly.
deadline = time.monotonic() + 2.0
while True:
    pending()
    count = widget_count(text_view)
    if count != 0:
        print("children appeared after %.3fs: %d" % (
            2.0 - (deadline - time.monotonic()), count))
        sys.exit(1)
    if time.monotonic() >= deadline:
        break
    time.sleep(0.01)
print("text view has no widget child")
'''

# The two face children interpolate the shared GTK 4 probe prologue:
# the class census above must stay bare, but a rendered pixel pin needs
# the theme selection and the sheet's provider (Adwaita race, asset-URI
# rewrite, priority 801) exactly as the probe suites' children get them
# from the shared constant.
SELECTED_FACE_CHILD = (
    GTK4_PROBE_PROLOGUE
    + '''

def pending():
    while GLib.MainContext.default().pending():
        GLib.MainContext.default().iteration(False)

SELECTION_RGB = %r

SELECTION = SELECTION_RGB
WIDTH, HEIGHT = 220, 60
''' % (_selection_rgb(),)
    + '''
text_view = Gtk.TextView()
text_view.get_buffer().set_text("Hello World", -1)
start, end = text_view.get_buffer().get_bounds()
text_view.get_buffer().select_range(start, end)
window = Gtk.Window()
window.set_child(text_view)
window.present()
text_view.grab_focus()

def at_function():
    snapshot = Gtk.Snapshot()
    Gtk.WidgetPaintable.new(text_view).snapshot(snapshot, WIDTH, HEIGHT)
    node = snapshot.to_node()
    renderer = window.get_renderer()
    if node is None or renderer is None:
        # Not allocated or realized yet: no frame to inspect.
        return None
    viewport = Graphene.Rect()
    viewport.init(0, 0, WIDTH, HEIGHT)
    texture = renderer.render_texture(node, viewport)
    pixbuf = Gdk.pixbuf_get_from_texture(texture)
    data, stride = pixbuf.get_pixels(), pixbuf.get_rowstride()
    channels = pixbuf.get_n_channels()
    def at(x, y):
        pos = y * stride + x * channels
        return tuple(data[pos:pos + 3])
    return at

def band_and_corners(at):
    matches = [
        (x, y) for y in range(HEIGHT) for x in range(WIDTH)
        if at(x, y) == SELECTION
    ]
    if not matches:
        return None
    xs = [x for x, _ in matches]
    ys = [y for _, y in matches]
    corners = (min(xs), min(ys)), (min(xs), max(ys)), \\
        (max(xs), min(ys)), (max(xs), max(ys))
    return matches, corners

# Wait for the first frame whose selection band exists and is flat at its
# bounding-box corners, then settle once, instead of a fixed wall-clock
# settle: the suite's indicator test uses the same deadline pattern.
deadline = time.monotonic() + 30
while True:
    pending()
    at = at_function()
    result = band_and_corners(at) if at is not None else None
    if result is not None:
        matches, corners = result
        if all(at(x, y) == SELECTION for x, y in corners):
            print("selection band %d px; flat bounding box %r" % (
                len(matches), corners))
            break
    if time.monotonic() >= deadline:
        if result is None:
            raise AssertionError(
                "no #CCCCFF selection band settled in the 220x60 frame"
                if at is not None else
                "text view produced no paintable frame"
            )
        matches, corners = result
        for x, y in corners:
            assert at(x, y) == SELECTION, (x, y, at(x, y), SELECTION)
        raise AssertionError("selection face did not settle flat")
    time.sleep(0.01)
window.destroy()
'''
)

DISABLED_FACE_CHILD = (
    GTK4_PROBE_PROLOGUE
    + '''

def pending():
    while GLib.MainContext.default().pending():
        GLib.MainContext.default().iteration(False)

WIDTH, HEIGHT = 220, 60'''
    + '''
text_view = Gtk.TextView()
text_view.get_buffer().set_text("Hello World", -1)
text_view.set_sensitive(False)
window = Gtk.Window()
window.set_child(text_view)
window.present()

def pixels():
    snapshot = Gtk.Snapshot()
    Gtk.WidgetPaintable.new(text_view).snapshot(snapshot, WIDTH, HEIGHT)
    node = snapshot.to_node()
    renderer = window.get_renderer()
    if node is None or renderer is None:
        return None
    viewport = Graphene.Rect()
    viewport.init(0, 0, WIDTH, HEIGHT)
    texture = renderer.render_texture(node, viewport)
    pixbuf = Gdk.pixbuf_get_from_texture(texture)
    data, stride = pixbuf.get_pixels(), pixbuf.get_rowstride()
    channels = pixbuf.get_n_channels()
    return [tuple(data[y * stride + x * channels:y * stride + x * channels + 3])
            for x, y in ((0, 0), (219, 0), (0, 59), (219, 59), (110, 55))]

deadline = time.monotonic() + 30
while True:
    pending()
    result = pixels()
    if result is not None and all(pixel == (255, 255, 255) for pixel in result):
        print("disabled field pixels %r" % result)
        break
    if time.monotonic() >= deadline:
        raise AssertionError("disabled field did not settle white: %r" % result)
    time.sleep(0.01)
window.destroy()
'''
)


class TestViewClassCensus(unittest.TestCase):
    """Pin the GTK 4.18 view-family class facts the recorded census found."""

    def test_view_family_class_list(self):
        result = _run_child(CENSUS_CHILD)
        if result.returncode == 77:
            self.skipTest("GTK 4 introspection or an X11 display is missing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "textview ['view']",
                "iconview ['view']",
                "listview ['view']",
                "window ['background']",
            ],
        )

    def test_text_node_unreachable_in_widget_tree(self):
        result = _run_child(UNREACHABLE_CHILD)
        if result.returncode == 77:
            self.skipTest("GTK 4 introspection or an X11 display is missing")
        self.assertEqual(
            result.returncode, 0,
            "the text node became reachable (a future GTK parented it): "
            + result.stdout + result.stderr,
        )
        self.assertEqual(result.stdout.strip(), "text view has no widget child")


class TestSelectedViewFace(unittest.TestCase):
    """Pin the rendered selected text face flat at the selection fill."""

    def test_selected_face_is_flat(self):
        # The child pins its fill to this module's derived palette triple, so
        # the pixel pin rides the same #CCCCFF constant the sheet declares.
        result = _run_child(SELECTED_FACE_CHILD, THEME_DIR)
        if result.returncode == 77:
            self.skipTest("GTK 4 introspection or an X11 display is missing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(
            result.stdout,
            r"selection band \d+ px; "
            r"flat bounding box \((\(\d+, \d+\)(?:, )?)+\)",
        )

    def test_palette_constant_is_the_pinned_fill(self):
        self.assertEqual(
            "#%02X%02X%02X" % _selection_rgb(), SELECTION,
            "the pinned fill is the palette's #CCCCFF selection constant",
        )


class TestDisabledViewFace(unittest.TestCase):
    """Pin the rendered insensitive text field to the existing white face."""

    def test_disabled_text_field_is_white(self):
        result = _run_child(DISABLED_FACE_CHILD, THEME_DIR)
        if result.returncode == 77:
            self.skipTest("GTK 4 introspection or an X11 display is missing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("(255, 255, 255)", result.stdout)

class TestGuiProbeGuard(unittest.TestCase):
    def test_host_display_does_not_enable_gui_probes(self):
        from unittest.mock import patch
        for value in (None, "0", "true"):
            env = {"DISPLAY": ":77"}
            if value is not None:
                env["PLATINUM_RUN_GUI_TESTS"] = value
            with patch.dict(os.environ, env, clear=True):
                with self.assertRaises(unittest.SkipTest):
                    _run_child("pass")

    def test_explicit_opt_in_allows_child_launch(self):
        from unittest.mock import patch
        completed = subprocess.CompletedProcess([], 77, "", "")
        with patch.dict(os.environ, {"DISPLAY": ":77", "PLATINUM_RUN_GUI_TESTS": "1"}, clear=True):
            with unittest.mock.patch(__name__ + ".subprocess.run", return_value=completed) as run:
                self.assertEqual(_run_child("pass").returncode, 77)
                run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
