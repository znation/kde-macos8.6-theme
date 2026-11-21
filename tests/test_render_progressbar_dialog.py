"""The ``--progressbar-dialog`` meter gate's rendered pixels, pinned band by band.

``tools/render_surface.py``'s ``--progressbar-dialog`` mode renders the Kvantum
progress meter that kdialog's progress helper draws; the gate here
byte-compares its face and edge bands. The shared capture plumbing lives in
``tests/support/render/gates.py``, and the other kdialog widget gates live in
``tests/test_render_dialog_gates.py``.
"""

from __future__ import annotations

import shutil
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.render.gates import (
    DIALOG_REAL_TOOLS,
    DialogGate,
    dialog_gate_guard,
    probe_gate_skip,
    software_renderer_skip_reason,
)



# The rendered Kvantum progress meter in the progressbar dialog: the
# helper-client `kdialog_progress_helper` opens an at-rest QProgressBar at
# value zero, whose trough the engine stretches over the theme's `progress`
# element art in the raised arrangement: the 1px #000000 outline with the
# #FFFFFF top/left bevel arms, the #999999 bottom/right bevel arms and the
# flat #DDDDDD face, inside the `[Progressbar]` section's 2px frame margins.
# The trough occupies (146,172)..(333,195), measured on two consecutive
# 480x360 `--progressbar-dialog` captures on this host (kdialog 25.04.0,
# 2026-11-10) whose two runs agreed byte for byte under `cmp`. The meter
# never moves -- only its D-Bus interface drives it, and the render session
# calls none of it -- so no striped progress-pattern tile and no busy
# animation enters any crop, and a progress meter has no caret: no
# phase-dependent column to steer around.
# The trough's face interior band: rows clear of every frame row (the arms
# end at the face's row 174 above 193) and of the "Working:" label glyphs
# (rows 153..163, above the trough), so the whole band must stay the flat
# #DDDDDD face. An off-by-one row slips a bevel-arm or window-face byte in
# and fails; a glyph or a filled value band inside the face fails too.
PROGRESSBAR_DIALOG_FACE_CROP = (200, 174, 120, 20)
# Narrow bands over the trough's edges: each band spans one #DDDDDD window
# face row, the outline row/column and the bevel arm inside it, so a lost
# outline row, a swapped arm colour or an off-by-one edge fails.
PROGRESSBAR_DIALOG_TOP_BAND = (200, 171, 121, 4)
PROGRESSBAR_DIALOG_BOTTOM_BAND = (200, 193, 121, 4)
PROGRESSBAR_DIALOG_LEFT_BAND = (144, 178, 5, 8)


@dialog_gate_guard()
class TestProgressbarDialogRender(DialogGate, unittest.TestCase):
    """The progress dialog's meter keeps its engine-drawn trough frame.

    The progressbar dialog opens a real at-rest ``QProgressBar`` (the
    ``kdialog --progressbar`` dialog, rendered through the helper daemon
    ``kdialog_progress_helper`` that kdialog itself execs for it -- the
    launcher prints the D-Bus reference and exits, so the shared session
    script's liveness check would fail it after the settle) whose trough
    the engine stretches over this theme's ``[Progressbar]`` ``progress``
    element with the section's 2px frame margins. No collected reference
    screenshot shows a dialog with a meter, so the comparison surfaces are
    the shipped art recipe: the raised arrangement the Kvantum reference
    suite pins by id -- the 1px #000000 outer outline with the #FFFFFF
    top/left bevel arms, the #999999 bottom/right bevel arms and the flat
    #DDDDDD face. Value zero keeps the meter in its resting state, so no
    striped ``progress-pattern`` tile, no value fill and no busy animation
    enter any crop, and a progress meter has no caret: no phase-dependent
    column to steer around. Measured on two consecutive full
    ``--progressbar-dialog`` captures on this host (2026-11-10) that agree
    byte for byte under ``cmp``.
    """

    KIND = "progressbar"

    def test_keeps_the_trough_face_interior_flat_at_rest(self):
        # The rows between the arms run clear of the outline rows and of
        # the label glyphs (which sit above the trough), so every byte
        # must be the flat #DDDDDD face: a striped progress-pattern tile,
        # a value fill or a glyph byte fails row by row.
        x, y, width, height = PROGRESSBAR_DIALOG_FACE_CROP
        self.assert_band(
            PROGRESSBAR_DIALOG_FACE_CROP,
            [["#DDDDDD"] * width for _ in range(height)],
        )

    def test_pins_the_top_edge_outline_and_its_white_bevel_arm(self):
        # One window-face row, the 1px #000000 outline and the #FFFFFF
        # top bevel arm inside it, then the face -- the raised
        # arrangement the progress element art draws.
        self.assert_band(
            PROGRESSBAR_DIALOG_TOP_BAND,
            (
                ["#DDDDDD"] * 121,
                ["#000000"] * 121,
                ["#FFFFFF"] * 121,
                ["#DDDDDD"] * 121,
            ),
        )

    def test_pins_the_left_edge_outline_and_its_white_bevel_arm(self):
        # Two window-face columns, the 1px #000000 outline column and the
        # #FFFFFF left bevel arm inside it, then the face, over eight
        # face rows clear of every horizontal band.
        arm_row = ["#DDDDDD", "#DDDDDD", "#000000", "#FFFFFF", "#DDDDDD"]
        self.assert_band(
            PROGRESSBAR_DIALOG_LEFT_BAND,
            tuple(arm_row for _ in range(8)),
        )

    def test_pins_the_bottom_edge_outline_and_its_shadow_bevel_arm(self):
        # The face row, the #999999 bottom bevel arm inside the 1px
        # #000000 outline, and the window face below it -- swapping the
        # highlight and shadow arms fails both this pin and the top one.
        self.assert_band(
            PROGRESSBAR_DIALOG_BOTTOM_BAND,
            (
                ["#DDDDDD"] * 121,
                ["#999999"] * 121,
                ["#000000"] * 121,
                ["#DDDDDD"] * 121,
            ),
        )


class TestProgressbarDialogGateSkipGuards(unittest.TestCase):
    """The progress dialog gate skips wherever its render CLI refuses on a tool.

    The shared guard condition and the other widget gates' flags are pinned in
    ``tests/test_render_dialog_gates.py``; this module pins its own gate's flag
    beside the gate it guards.
    """

    def test_the_progressbar_dialog_gate_skips_only_when_a_tool_is_absent(self):
        expected = software_renderer_skip_reason() is not None or not all(
            shutil.which(tool) for tool in DIALOG_REAL_TOOLS
        )
        self.assertEqual(expected, TestProgressbarDialogRender.__unittest_skip__)
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
