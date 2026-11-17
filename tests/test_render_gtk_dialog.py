"""The GTK 4 dialog gate's rendered zenity window, pinned region by region.

``tools/render_surface.py``'s ``--gtk-dialog`` mode captures a themed GTK 4
zenity window whose engine-drawn widgets this gate byte-compares: the shared
capture plumbing lives in ``tests/support/render_gates.py``, and the kdialog
widget gates live in ``tests/test_render_dialog_gates.py``.
"""

from __future__ import annotations

import shutil
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    WHITE,
    hex_colour,
)
from support.render_gates import (
    DIALOG_REAL_TOOLS,
    DialogGate,
    dialog_gate_guard,
    probe_gate_skip,
    software_renderer_skip_reason,
)
from tools.png import pixel_at  # noqa: E402


# The rendered GTK 4 entry field's right-hand cell: the entry's own painted
# edge rows and the right edge columns, plus the flat face interior, measured
# 2026-11-03 on a consecutive pair of full `tools/render_surface.py --gtk-dialog`
# runs on this host (zenity 4.1.90, GTK 4.18.6) whose two 480x360 captures
# agreed bit for bit under cmp. The empty entry's caret sits at x=136, so the
# cell stays right of it and carries no caret byte; the crop's right edge
# columns are the focused entry's 2px black edge (the stock focus halo over
# the 1px black ENTRY_FIELD border), so any off-by-one slips the flat face in
# under the pinned columns and fails.
ENTRY_FIELD_CROP = (300, 171, 54, 36)
# The rendered GTK 4 dialog's action-button row, left of the OK push button's
# label glyphs: the button band below the white entry box, whose face spans
# rows 240..285 (x=114..233) on the same 480x360 capture, measured
# 2026-11-03 on a consecutive pair of full `tools/render_surface.py
# --gtk-dialog` runs on this host (zenity 4.1.90, GTK 4.18.6) whose two
# captures agreed bit for bit under cmp, and reproduced bit for bit by a
# third consecutive run. The rendered button is the existing push-button
# recipe: 1px #000000 border rows (0 and 45) and border column, a 1px white
# BUTTON_BEVEL top arm (interior row 1) and left arm (column 1), the flat
# #DDDDDD face, and a 1px #AAAAAA (BUTTON_SHADOW) BUTTON_BEVEL bottom arm
# (row 44). The OK label's glyphs occupy x=149..196, so columns 114..145
# sit left of them and of the caret-free zone the entry pin already ruled:
# ghost-free by construction.
OK_BUTTON_CROP = (114, 240, 32, 46)
# The rendered GTK 4 dialog's Cancel push button's left-hand cell, in the
# same action-button row as the OK pin: the button spans rows 240..285 at
# x=246..365 on the same 480x360 capture, measured 2026-11-03 on a
# consecutive pair of full `tools/render_surface.py --gtk-dialog` runs on
# this host (zenity 4.1.90, GTK 4.18.6) whose two captures agreed bit for
# bit under cmp, and reproduced bit for bit by a third consecutive run.
# The rendered button is the same existing push-button recipe as the OK pin:
# 1px #000000 border rows (0 and 45) and border column, a 1px white
# BUTTON_BEVEL top arm (interior row 1) and left arm (column 1), the flat
# #DDDDDD face, and a 1px #AAAAAA (BUTTON_SHADOW) BUTTON_BEVEL bottom arm
# (row 44). The Cancel label's glyphs occupy x=295..313, so columns
# 246..277 sit right of the OK button's border column (x=233) and left of
# them; zenity's default button is the OK one, so the non-default Cancel
# carries no focus ring (the rows above and below the button stay the
# action-row background) and the span is ghost-free by construction.
CANCEL_BUTTON_CROP = (246, 240, 32, 46)
# The rendered GTK 4 dialog window's top shell edge strip, where the CSD
# window meets the session: the window's #DDDDDD surface spans x=90..389 with
# its top face row at y=49 on the same 480x360 capture, measured 2026-11-03
# on a consecutive pair of full `tools/render_surface.py --gtk-dialog` runs
# on this host (zenity 4.1.90, GTK 4.18.6) whose two captures agreed bit for
# bit under cmp, and reproduced bit for bit by a third consecutive run.
# The session background is black, so the existing active window.csd outline
# (box-shadow: 0 0 0 1px #000000, pinned in the sheet by
# TestGtk4WindowShell::test_csd_window_shell) is continuous with it: the pinned
# top row is the shell-edge row the ring paints where the surface margin
# admits it, and the rows beneath are the flat #DDDDDD surface from the
# window, .background rule. The span x=91..93 is past the square
# border-radius: 0 corner's edge column and clear of title glyphs. A
# 2026-11-03 probe (zenity 4.1.90, GTK 4.18.6) found no headerbar,
# .titlebar, windowcontrols, windowtitle or .title node; selector probes
# painted zero pixels while window, dialog and label probes painted. Thus
# the headerbar windowcontrols button.close recipe renders no pixels in
# this capture; its live pixels remain covered by declaration checks.
WINDOW_SHELL_EDGE_CROP = (91, 48, 3, 12)


@dialog_gate_guard()
class TestGtkDialogRender(DialogGate, unittest.TestCase):
    """The GTK dialog render captures a themed GTK 4 window at the gate size.

    A real GTK 4 client (zenity, a GTK 4 build with no theme-name CSS
    switch) wears this theme through the selection
    ``tools/gtk_selection.py::apply`` publishes into the scratch config
    home: the ``gtk-4.0/settings.ini`` theme-name keys and the user CSS
    ``@import`` of the installed sheet. The capture-level assertions pin
    the 480x360 size the other dialog gates byte-compare at and a plane
    that actually painted, ``test_draws_the_entry_field_cell_1_to_1``
    byte-compares the content-area entry's cell with the arrangement the
    existing entry recipe re-derives, the two push-button pins
    (``test_draws_the_action_button_row_cell_1_to_1`` and
    ``test_draws_the_cancel_button_cell_1_to_1``) byte-compare the OK and
    Cancel buttons' cells with the arrangement the existing push-button
    recipe re-derives, and ``test_draws_the_window_shell_edge_cell_1_to_1``
    byte-compares the window's top shell edge strip with the arrangement
    the existing ``window.csd`` outline and ``window, .background`` surface rule
    re-derive (each crop is measured on this host's 480x360
    capture; see the ``## tooling`` row of ``docs/invariants.md``).
    """

    KIND = "gtk"

    def test_draws_the_action_button_row_cell_1_to_1(self):
        # Byte-compare the OK push button's left-hand cell with the
        # arrangement the existing push-button recipe's own constants
        # re-derive, never with the capture's own pixels. The cell spans the
        # button's full height at a label-free horizontal span: row 0 and
        # row 45 are the 1px black border rows, column 0 the black border
        # column; row 1 is the BUTTON_BEVEL white arm's top row (the inset
        # 1px 1px #FFFFFF shadow spans the interior's top width up to the
        # #AAAAAA bottom arm); rows 2..43 carry the white bevel's left arm
        # beside the flat face; row 44 is the BUTTON_BEVEL inset -1px -1px
        # #AAAAAA arm's bottom row. A one-pixel crop slip, an inverted or
        # recoloured bevel arm, a foreign face colour or a glyph row (text
        # antialiasing, the one painter outside the recipe's constants)
        # fails this byte-compare.
        image = self.candidate_image()
        x0, y0, width, height = OK_BUTTON_CROP
        expected = {
            (x, y): (
                BLACK
                if y == 0 or y == height - 1 or x == 0
                else WHITE
                if y == 1 or (2 <= y < height - 2 and x == 1)
                else BUTTON_SHADOW
                if y == height - 2
                else FACE
            )
            for x in range(width)
            for y in range(height)
        }
        actual = {
            (x, y): hex_colour(pixel_at(image, x0 + x, y0 + y))
            for x in range(width)
            for y in range(height)
        }
        self.assertEqual(expected, actual)

    def test_draws_the_cancel_button_cell_1_to_1(self):
        # Byte-compare the Cancel push button's left-hand cell with the
        # arrangement the existing push-button recipe's own constants
        # re-derive, never with the capture's own pixels. The cell spans
        # the button's full height at a label-free horizontal span, the
        # same shape the OK pin pins: row 0 and row 45 are the 1px black
        # border rows, column 0 the black border column; row 1 is the
        # BUTTON_BEVEL white arm's top row (the inset 1px 1px #FFFFFF
        # shadow spans the interior's top width up to the #AAAAAA bottom
        # arm); rows 2..43 carry the white bevel's left arm beside the
        # flat face; row 44 is the BUTTON_BEVEL inset -1px -1px #AAAAAA
        # arm's bottom row. Zenity's default button is the OK one, so the
        # non-default Cancel shows no focus ring. A one-pixel crop slip,
        # an inverted or recoloured bevel arm, a foreign face colour or a
        # glyph row (text antialiasing, the one painter outside the
        # recipe's constants) fails this byte-compare.
        image = self.candidate_image()
        x0, y0, width, height = CANCEL_BUTTON_CROP
        expected = {
            (x, y): (
                BLACK
                if y == 0 or y == height - 1 or x == 0
                else WHITE
                if y == 1 or (2 <= y < height - 2 and x == 1)
                else BUTTON_SHADOW
                if y == height - 2
                else FACE
            )
            for x in range(width)
            for y in range(height)
        }
        actual = {
            (x, y): hex_colour(pixel_at(image, x0 + x, y0 + y))
            for x in range(width)
            for y in range(height)
        }
        self.assertEqual(expected, actual)

    def test_draws_the_window_shell_edge_cell_1_to_1(self):
        # Byte-compare the window's top shell edge strip with the
        # arrangement the existing recipes' own constants re-derive, never
        # with the capture's own pixels. The strip crosses the window's top
        # edge past the square border-radius: 0 corner's edge column and
        # clear of title glyphs: row 0 is the shell-edge
        # row -- the existing window.csd active outline's 1px #000000 ring
        # (box-shadow: 0 0 0 1px #000000), which the black session
        # background makes continuous with -- and rows 1..11 are the flat
        # #DDDDDD window surface beneath it, painted by the existing
        # window, .background rule. A 2026-11-03 zenity 4.1.90 / GTK
        # 4.18.6 probe found no headerbar, .titlebar or windowcontrols
        # node, so the headerbar title-button recipe does not render in
        # this capture. A one-pixel vertical slip (the strip
        # starting on the face row), a recoloured or transplanted ring
        # (stock's translucent ring, the #555555 window.csd:backdrop tone)
        # or a foreign face colour fails this byte-compare.
        image = self.candidate_image()
        x0, y0, width, height = WINDOW_SHELL_EDGE_CROP
        expected = {
            (x, y): BLACK if y == 0 else FACE
            for x in range(width)
            for y in range(height)
        }
        actual = {
            (x, y): hex_colour(pixel_at(image, x0 + x, y0 + y))
            for x in range(width)
            for y in range(height)
        }
        self.assertEqual(expected, actual)

    def test_draws_the_entry_field_cell_1_to_1(self):
        # Byte-compare the entry's painted cell with the arrangement the
        # existing recipe's own constants re-derive, never with the capture's
        # own pixels. The entry is focused in zenity's dialog, so the
        # focused field carries stock's focus halo geometry (2px wide with
        # an inset -2px offset) recoloured black by the sheet's own
        # ``entry:focus-within`` outline-color pin: the halo paints black
        # over the border box's outer two pixels, namely the 1px black
        # ENTRY_FIELD border row/column plus one row/column of the padding
        # box, so the cell's edge rows and right edge columns are the 2px
        # black edge the capture shows. Proven 2026-11-03 with a throwaway
        # GTK 4 client in the project's own session machinery: clearing that
        # outline colour lays the sheet's ``box-shadow: inset 1px 1px
        # #999999`` strip bare (1px black border, grey strip, white face),
        # so the strip renders but sits under the black halo in the
        # published chain, and the pinned cell is exactly this edge plus the
        # flat #FFFFFF ENTRY_FIELD face.
        image = self.candidate_image()
        x0, y0, width, height = ENTRY_FIELD_CROP
        expected = {
            (x, y): (
                BLACK
                if y < 2 or y >= height - 2 or x >= width - 2
                else WHITE
            )
            for x in range(width)
            for y in range(height)
        }
        actual = {
            (x, y): hex_colour(pixel_at(image, x0 + x, y0 + y))
            for x in range(width)
            for y in range(height)
        }
        self.assertEqual(expected, actual)

    KIND = "gtk"

    def test_capture_paints_a_non_uniform_plane(self):
        # The CLI already refuses an all-black capture, so the plane is
        # painted; this asserts it is also not one flat colour, so a later
        # byte-compare of the entry cell is possible at all. A sampled grid
        # is enough: a themed zenity window over the virtual session's
        # background carries several distinct colours within it.
        image = self.candidate_image()
        colours = {
            hex_colour(pixel_at(image, x, y))
            for x in range(0, image.width, 8)
            for y in range(0, image.height, 8)
        }
        self.assertGreater(len(colours), 1)


class TestGtkDialogGateSkipGuards(unittest.TestCase):
    """The GTK 4 dialog gate skips wherever its render CLI refuses on a tool.

    The shared guard condition and the widget gates' flags are pinned in
    ``tests/test_render_dialog_gates.py``; this module pins its own gate's
    flag beside the gate it guards.
    """

    def test_the_gtk_dialog_gate_skips_only_when_a_tool_is_absent(self):
        expected = software_renderer_skip_reason() is not None or not all(
            shutil.which(tool) for tool in DIALOG_REAL_TOOLS
        )
        self.assertEqual(expected, TestGtkDialogRender.__unittest_skip__)
        # Reapply the real guard to disposable classes: never alter the
        # render gate or start a session while simulating missing tools.
        for missing in (None, *DIALOG_REAL_TOOLS):
            with self.subTest(missing=missing):
                self.assertEqual(
                    missing is not None,
                    probe_gate_skip(dialog_gate_guard, missing),
                )


if __name__ == "__main__":
    unittest.main()
