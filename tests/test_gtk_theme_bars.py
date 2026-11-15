"""Validate the GTK 3 Platinum sheet's menu-bar, toolbar and notebook bars.

This module owns the bar slice split out of
the former GTK 3 controls suite: the rendered notebook tab faces (a child
interpreter renders the probe with a real GTK 3, so the suite process itself
imports no GTK), and the menu-bar titles and the toolbar and menu-bar faces.
"""

import unittest
from pathlib import Path

from support.gtk_child_probe import (
    Gtk3ChildProbeCases,
    _GTK3_PIXEL_HEAD,
    _GTK3_SHEET_AND_WINDOW,
    _GTK3_SHEET_PROLOGUE,
)
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import ETCH_DARK
from support.platinum_palette import (
    FACE,
    WHITE,
)
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"


class TestGtkThemeBars(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_notebook_tab_faces_render(self):
        # The tab recipe is matched by a live GTK paint only; pin the
        # rendered pixels of a two-page notebook's tab faces. The GTK work
        # runs in a child interpreter; see _run_gtk_child for why it never
        # runs in this one.
        program = (
            _GTK3_SHEET_PROLOGUE
            + _GTK3_SHEET_AND_WINDOW
            + '''window.set_default_size(160, 60)
notebook = Gtk.Notebook()
notebook.append_page(Gtk.Label(label=" "), Gtk.Label(label=" "))
notebook.append_page(Gtk.Label(label=" "), Gtk.Label(label=" "))
window.add(notebook)
'''
            + _GTK3_PIXEL_HEAD
            + r'''# Geometry measured 2026-11-10 on this host from this very render:
# the notebook is flush with the window, whose pixbuf it fills, and the
# toolkit's own notebook frame paints the 1px black line at row 0 and the
# columns at x 0 and 159; the band's own 1px black top border sits at
# y = 1 and its interior spans x 30-157 down to y = 32, with blend rows
# (y = 33) beneath and the page area from y = 35. The first tab is
# checked and the second is not; the tabs' shared black edge and each
# face's x are located at render time so the pin is not a transcription
# of tab widths, whose left edges depend on the tab-label metrics.
border = next(x for x in range(6, pixbuf.get_width() - 1) if at(x, 20) == "#000000")
# (a) The band interior beyond the tabs keeps the flat #DDDDDD face.
assert at(130, 20) == "#DDDDDD", at(130, 20)
# (b) The band's top border row is the toolkit frame's black under the
# header's own 1px black border.
assert at(130, 1) == "#000000", at(130, 1)
# (c) The unselected tab carries the raised bevel: the #FFFFFF top arm
# just below its top border row and the #999999 bottom arm symmetric
# above its bottom border row, with the tab's own #DDDDDD face between.
b1 = border + 6
assert at(b1, 3) == "#FFFFFF", at(b1, 3)
assert at(b1, 8) == "#DDDDDD", at(b1, 8)
assert at(b1, 32) == "#999999", at(b1, 32)
# (d) The checked tab is flattened in place: the very same rows carry
# the flat #DDDDDD face with neither bevel arm.
b0 = border - 5
assert at(b0, 3) == "#DDDDDD", at(b0, 3)
assert at(b0, 32) == "#DDDDDD", at(b0, 32)
print("notebook tab faces: the band interior and the flat checked tab read #DDDDDD, the band's top border #000000, the unselected tab's bevel #FFFFFF over #DDDDDD over #999999")
'''
        )
        self._run_gtk_child(program, str(CSS))

    def test_menubar_titles(self):
        self.assert_menubar_titles("menubar > menuitem")

    def test_toolbar_and_menubar(self):
        for selector in ("toolbar", "menubar"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "border-bottom": f"1px solid {ETCH_DARK}",
                    "box-shadow": f"inset 0 -1px {WHITE}",
                },
            )


if __name__ == "__main__":
    unittest.main()
