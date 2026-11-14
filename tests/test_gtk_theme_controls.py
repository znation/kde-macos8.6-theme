"""Validate the GTK 3 Platinum sheet's controls.

This module owns the control slice of ``tests/test_gtk_theme.py``'s split:
the spinner, level bar, switch, the control focus outlines
(the button arms and button focus outline are checked in
``tests/test_gtk_theme_buttons.py``, the spin-button focus outlines, stepper
seams and RTL etch in ``tests/test_gtk_theme_spinbutton.py``), the menu-bar and
toolbar titles, and the rendered notebook tab faces. The linked border pairs are
checked in ``tests/test_gtk_theme_linked.py``, the scale geometry and ink in
``tests/test_gtk_theme_scale.py`` and the entry fields in
``tests/test_gtk_theme_entry.py`` and the progress bar and meter faces in
``tests/test_gtk_theme_progress.py``, the view field, viewport and frame
borders in ``tests/test_gtk_theme_frames.py``, the check and radio indicators in
``tests/test_gtk_theme_check.py``. The shipped glyph assets are checked in
``tests/test_gtk_theme_glyphs.py``. The notebook tab-face
probe renders with a real GTK 3 in a child interpreter (see
``_run_gtk_child``); the suite process itself imports no GTK.
"""

import unittest
from pathlib import Path

from support.gtk_child_probe import (
    _GTK3_PIXEL_HEAD,
    _GTK3_SHEET_AND_WINDOW,
    _GTK3_SHEET_PROLOGUE,
    Gtk3ChildProbeCases,
)
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    ETCH_DARK,
)
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    TROUGH,
    WHITE,
)
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"

class TestGtkThemeControls(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase):
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

    def test_spinner(self):
        self.assert_spinner("-gtk-icon-transform")

    def test_levelbar(self):
        self.assert_levelbar(
            trough="levelbar trough",
            filled="levelbar block.filled",
            empty="levelbar block.empty",
            disabled="levelbar block.filled:disabled",
            horizontal="levelbar.horizontal block",
            vertical="levelbar.vertical block",
        )

    def test_switch(self):
        self.assert_switch(
            slider="switch slider",
            disabled_slider="switch:disabled slider",
            glyph="switch image",
        )

    def test_switch_focus_outline(self):
        self.assert_dotted_focus_outline("switch:focus")

    def test_switch_state_and_backdrop_faces(self):
        """The existing switch faces hold through every toolkit repaint.

        The toolkit's state, backdrop and selected-row switch arms
        out-specify the existing groups (see the
        sheet), so each stock spelling is restated byte-equal and wins by
        later user-sheet source order. Each spelling counts exactly once,
        the three existing groups carry exactly one added member each, and
        the family sweeps admit no stray or renamed spelling.
        """
        # The restated knob arms: the raised bevel face, no fade.
        for selector in ("switch:hover slider", "switch:backdrop slider"):
            self.assert_rule(
                selector,
                {
                    "border-color": BLACK,
                    "background-image": "none",
                    "box-shadow": "inset 1px 1px #FFFFFF,"
                    " inset -1px -1px #999999",
                    "transition": "none",
                },
            )
        self.assert_rule("switch:checked > slider", {"border-color": BLACK})
        self.assert_rule(
            "switch:backdrop",
            {
                "background-color": TROUGH,
                "border-color": BLACK,
                "transition": "none",
            },
        )
        self.assert_rule(
            "switch:backdrop:checked",
            {"background-color": WHITE, "border-color": BLACK},
        )
        self.assert_rule(
            "switch:backdrop:disabled",
            {"background-color": TROUGH, "border-color": GREY},
        )
        self.assert_rule(
            "switch:backdrop:disabled slider",
            {
                "border-color": GREY,
                "background-image": "none",
                "box-shadow": "none",
                "transition": "none",
            },
        )
        # The selected-row twins of the existing `row:selected button` record.
        for selector in (
            "row:selected switch",
            "row:selected switch:backdrop",
            "row:selected switch > slider:checked",
            "row:selected switch > slider",
        ):
            self.assert_rule(selector, {"border-color": BLACK})

        # The three amended existing groups: one added member each, no more.
        self.assert_rule("switch:checked", {"border-color": BLACK})
        self.assert_rule("switch:disabled", {"background-color": TROUGH})
        self.assert_rule("switch slider", {"transition": "none"})
        self.assertEqual(
            self.rules["switch:checked"],
            {
                "background-color": WHITE,
                "background-image": "none",
                "border-color": BLACK,
            },
        )
        self.assertEqual(
            self.rules["switch:disabled"],
            {"background-color": TROUGH, "border-color": GREY},
        )
        self.assertEqual(
            self.rules["switch slider"],
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": "inset 1px 1px #FFFFFF,"
                " inset -1px -1px #999999",
                "margin": "-1px",
                "min-width": "12px",
                "min-height": "16px",
                "transition": "none",
            },
        )
        for selector in ("switch:checked", "switch:disabled", "switch slider"):
            self.assertEqual(self.selectors.count(selector), 1, selector)

        # Family sweeps: no stray or renamed spelling survives.
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("switch") and ":backdrop" in s
            },
            {
                "switch:backdrop",
                "switch:backdrop:checked",
                "switch:backdrop:disabled",
                "switch:backdrop slider",
                "switch:backdrop:checked > slider",
                "switch:backdrop:disabled slider",
            },
        )
        self.assertEqual(
            {s for s in self.selectors if "row:selected switch" in s},
            {
                "row:selected switch",
                "row:selected switch:backdrop",
                "row:selected switch > slider:checked",
                "row:selected switch > slider",
            },
        )
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("switch")
                and ":backdrop" not in s
                and (
                    ":hover" in s
                    or ":active" in s
                    or ":checked" in s
                    or ":disabled" in s
                )
            },
            {
                "switch:checked",
                "switch:disabled",
                "switch:disabled slider",
                "switch:hover slider",
                "switch:checked > slider",
            },
        )

        # Order: the restated block sits between the existing `switch image`
        # group and the existing toolbar band group.
        self.assertGreater(
            self.css.index("switch:hover slider"),
            self.css.index("switch image {"),
        )
        self.assertLess(
            self.css.index("switch:hover slider"),
            self.css.index("toolbar, menubar {"),
        )

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
