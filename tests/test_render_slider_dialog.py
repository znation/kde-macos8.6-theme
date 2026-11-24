"""The ``--slider-dialog`` thumb and trough gate's rendered pixels, pinned band by band.

``tools/render_surface.py``'s ``--slider-dialog`` mode opens an at-rest Kvantum
slider; the gate here byte-compares its thumb cell and trough band. The shared
capture plumbing lives in ``tests/support/render/gates.py``, and the other
kdialog widget gates live in ``tests/test_render_dialog_gates.py``.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.render.gates import (
    DialogGate,
    assert_gate_skips_only_when_a_tool_is_absent,
    dialog_gate_guard,
)


# The rendered Kvantum slider thumb in the slider dialog: kdialog's
# `--slider` opens an at-rest QSlider at value zero, its thumb resting at
# the trough's left end, drawn by the engine with the theme's
# `slidercursor-normal` art in its native 16x16 cell and shipped raised
# arrangement on the 480x360 capture, measured on two consecutive
# `tools/render_surface.py --slider-dialog` runs on this host (2026-11-10)
# whose two 480x360 captures agreed byte for byte under `cmp`; a third run
# in the same batch reproduced them byte for byte. The engine draws the
# thumb at the art's native size, so the `.kvconfig` needed no steering key
# and nothing re-derived the fixture: the shipped art is never resampled.
SLIDER_DIALOG_THUMB_CROP = (146, 178, 16, 16)
# The trough band right of the thumb, (162,182)..(332,189): the 1px #000000
# boundary rows above and below the flat #EEEEEE interior face the `[Slider]`
# section's interior `slider` element draws (the shipped comment names the
# desktop theme's shared trough face). The band's columns sit right of the
# thumb's right outline column (x=161) and left of the dialog group box's
# right border column (x=333), and its rows sit between the boundary rows,
# so no thumb, label-glyph or foreign-border byte enters the crop. Measured
# on the same agreeing pair as the thumb.
SLIDER_DIALOG_TROUGH = (162, 182, 171, 8)


@dialog_gate_guard()
class TestSliderDialogRender(DialogGate, unittest.TestCase):
    """The slider dialog's thumb and trough keep their engine-drawn art.

    The slider dialog opens a real at-rest ``QSlider`` (kdialog's
    ``--slider`` at value zero) whose trough the engine draws with this
    theme's ``[Slider]`` ``slider`` art and whose thumb rests at the
    trough's left end as the theme's ``slidercursor`` raised arrangement;
    no collected reference screenshot shows a dialog with a slider, so the
    comparison surfaces are the shipped art recipe. No pixel gate watched a
    rendered slider, so a ``slidercursor`` art change, a ``[Slider]`` trough
    change or a resampled thumb would have shipped green. Value zero keeps
    the thumb in its resting state, so no pressed or hover byte enters any
    crop, and a slider has no caret: two consecutive captures are
    byte-identical with no phase-dependent column to steer around.
    """

    KIND = "slider"

    def test_draws_the_thumb_cell_1_to_1(self):
        # The candidate cell bytes come straight from the render (see
        # DialogGate.assert_cell_matches): a resampled, recoloured or
        # sunken thumb shows up here immediately.
        self.assert_cell_matches("slidercursor-normal", SLIDER_DIALOG_THUMB_CROP)

    def test_draws_the_trough_face_between_its_boundary_rows(self):
        """Pin the flat trough face and the 1px #000000 boundary rows.

        The rows between the boundary rows are flat #EEEEEE col to col, so
        a groove bevel arm, a filled value band or a glyph byte inside the
        face fails row by row; the boundary rows are all #000000, so a
        swapped arm colour or a lost outline row fails.
        """
        width, height = SLIDER_DIALOG_TROUGH[2:]
        self.assert_band(
            SLIDER_DIALOG_TROUGH,
            [
                ["#000000"] * width if row in (0, height - 1) else ["#EEEEEE"] * width
                for row in range(height)
            ],
        )


class TestSliderDialogGateSkipGuards(unittest.TestCase):
    """The slider dialog gate skips wherever its render CLI refuses on a tool.

    The shared guard condition and the other widget gates' flags are pinned in
    ``tests/test_render_dialog_gates.py``; this module pins its own gate's flag
    beside the gate it guards.
    """

    def test_the_slider_dialog_gate_skips_only_when_a_tool_is_absent(self):
        assert_gate_skips_only_when_a_tool_is_absent(self, TestSliderDialogRender)


if __name__ == "__main__":
    unittest.main()
