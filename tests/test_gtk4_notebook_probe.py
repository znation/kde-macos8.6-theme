"""Rendered GTK 4 notebook probe."""

import unittest

from support.gtk4_child_probe import GTK4_PROBE_PROLOGUE, run_gtk4_probe
from support.gui_tests import require_gui_opt_in


class TestGtk4NotebookProbe(unittest.TestCase):
    def test_notebook_tab_faces_render(self):
        require_gui_opt_in()
        run_gtk4_probe(self, GTK4_PROBE_PROLOGUE + '''
window = Gtk.Window()
window.set_default_size(240, 90)
notebook = Gtk.Notebook()
notebook.append_page(Gtk.Label(label="page one"), Gtk.Label(label=" "))
notebook.append_page(Gtk.Label(label="page two"), Gtk.Label(label=" "))
window.set_child(notebook)
window.present()
header = notebook.get_first_child()
assert header.get_css_name() == "header", header.get_css_name()
tabs = header.get_first_child()
tab_nodes = []
child = tabs.get_first_child()
while child is not None:
    if child.get_css_name() == "tab":
        tab_nodes.append(child)
    child = child.get_next_sibling()
assert len(tab_nodes) == 2, len(tab_nodes)

def capture():
    snapshot = Gtk.Snapshot()
    Gtk.WidgetPaintable.new(header).snapshot(snapshot, header.get_width(), header.get_height())
    node = snapshot.to_node()
    renderer = window.get_renderer()
    if node is None or renderer is None or header.get_width() <= 0:
        return None
    viewport = Graphene.Rect()
    viewport.init(0, 0, header.get_width(), header.get_height())
    pixbuf = Gdk.pixbuf_get_from_texture(renderer.render_texture(node, viewport))
    data, stride, channels = pixbuf.get_pixels(), pixbuf.get_rowstride(), pixbuf.get_n_channels()
    def at(x, y):
        start = y * stride + x * channels
        return tuple(data[start:start + 3])
    return at

deadline = time.monotonic() + 30
while True:
    while GLib.MainContext.default().pending():
        GLib.MainContext.default().iteration(False)
    at = capture()
    if at is not None and all(tab.get_width() > 0 for tab in tab_nodes):
        break
    if time.monotonic() >= deadline:
        raise AssertionError("notebook header produced no allocated paintable")
    time.sleep(0.01)
# The two tabs occupy the header's leading edge. Probe one pixel inside each
# tab, and the header face beyond both tabs; positions are derived from the
# fresh allocations so font metrics do not become a fixture.
tabs_x = tabs.get_allocation().x
first_x = tabs_x + tab_nodes[0].get_allocation().x
second_x = tabs_x + tab_nodes[1].get_allocation().x
header_y = header.get_height() // 2
top = next(y for y in range(4) if at(header.get_width() - 3, y) == (0, 0, 0))
tab_y_top = tab_nodes[0].get_allocation().y + 1
tab_y_bottom = (tab_nodes[0].get_allocation().y
                + tab_nodes[0].get_allocation().height - 2)
assert at(header.get_width() - 3, header_y) == (221, 221, 221)
assert at(header.get_width() - 3, top) == (0, 0, 0)
assert at(second_x + 3, tab_y_top) == (255, 255, 255)
assert at(second_x + 3, tab_y_bottom) == (153, 153, 153)
assert at(first_x + 3, tab_y_top) == (221, 221, 221)
assert at(first_x + 3, tab_y_bottom) == (221, 221, 221)
assert at(second_x + 3, tab_nodes[1].get_allocation().y + tab_nodes[1].get_height() - 1) == (0, 0, 0)
assert at(first_x + 3, tab_nodes[0].get_allocation().y + tab_nodes[0].get_height() - 1) == (221, 221, 221)
''')


if __name__ == "__main__":
    unittest.main()
