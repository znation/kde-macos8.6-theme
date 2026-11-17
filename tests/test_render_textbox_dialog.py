"""The ``--textbox-dialog`` scrollbar gate's rendered pixels, pinned band by band.

``tools/render_surface.py``'s ``--textbox-dialog`` mode renders the Kvantum
scrollbar that kdialog's text box draws; the gate here byte-compares its
bands. The shared capture plumbing lives in ``tests/support/render_gates.py``,
and the other kdialog widget gates live in ``tests/test_render_dialog_gates.py``.
"""

from __future__ import annotations

import shutil
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.platinum_palette import hex_colour
from support.render_gates import (
    DIALOG_REAL_TOOLS,
    DialogGate,
    dialog_gate_guard,
    probe_gate_skip,
    software_renderer_skip_reason,
)
from tools.png import pixel_at  # noqa: E402


# The rendered Kvantum scrollbar in the text-box dialog: kdialog's
# `--textbox` opens a real read-only QTextEdit over a 40-line scratch text
# file whose vertical QScrollBar rests at value zero, drawn by the engine
# through the theme's `[Scrollbar]`/`[ScrollbarSlider]`/`[ScrollbarGroove]`
# sections: the 16px raised `scrollbarslider` handle with its 13px `grip`
# indicator, the `slider`-element trough and the `arrow`-element buttons.
# Measured on three consecutive 480x360 `--textbox-dialog` captures on this
# host (kdialog 25.04.0, 2026-11-10) -- two plain runs and one with a longer
# settle -- that agreed byte for byte under `cmp`; a 200-line probe file
# reproduced the same bytes because the 40-line file's handle already rests
# at the platform's minimum slider length. At value zero the bar rests, so
# no hover, press or focus byte enters any crop: value zero disables the up
# arrow (its triangle paints the disabled #999999 `arrow` tint, the same
# disabled tint the pinned `comboarrow-*` families draw) while the down
# arrow stays enabled in the normal #000000 state. The handle's interior is
# 12px wide (the `[Scrollbar]` `scroll_width=16` track minus the section's
# own 2px frame margins), so the 13px `grip` indicator lands resampled with
# half-pixel edge tones the engine paints from the shipped art: the engine
# cannot be steered to the art's native width here (the interior width is
# fixed by the shipped section itself), and the bars the grip band pins
# below are the drawn result of the shipped recipe.
# Narrow bands over the handle's edges and its grip: each spans the outline
# row/column and the bevel arm inside it, so a lost outline row, a swapped
# arm colour, a resampled or dropped grip, or an off-by-one edge fails.
TEXTBOX_DIALOG_HANDLE_TOP_BAND = (352, 95, 16, 3)
TEXTBOX_DIALOG_HANDLE_LEFT_BAND = (352, 97, 3, 32)
TEXTBOX_DIALOG_HANDLE_BOTTOM_BAND = (352, 128, 16, 3)
TEXTBOX_DIALOG_GRIP_BAND = (352, 107, 16, 13)
# Bands over the two arrow buttons the `[Scrollbar]` `scroll_arrows=true`
# section paints: the disabled #999999 up triangle over its raised #DDDDDD
# face and the enabled #000000 down triangle over the same face, so an
# always-enabled arrow or a one-tint arrow pair fails.
TEXTBOX_DIALOG_UP_ARROW_BAND = (352, 90, 16, 5)
TEXTBOX_DIALOG_UP_ARROW_TRIANGLE = (352, 80, 16, 15)
TEXTBOX_DIALOG_DOWN_ARROW_BAND = (352, 255, 16, 14)
# The trough interior below the handle: rows clear of the handle's bevel
# (the bottom outline row 130), of the trough's own outline columns (the
# groove frame draws them outside x=354..365) and of the engine's blue
# position-fade overlay the scrollbar paints below the resting handle
# (rows 131..161, a platform overlay no shipped art element defines;
# recorded in the gate class comment), so the whole band must stay the
# flat #EEEEEE `slider` interior face with no outline byte inside.
TEXTBOX_DIALOG_TROUGH_CROP = (354, 170, 12, 16)


@dialog_gate_guard()
class TestTextboxDialogRender(DialogGate, unittest.TestCase):
    """The text-box dialog's scrollbar keeps its engine-drawn art.

    The textbox dialog opens a real read-only ``QTextEdit`` (kdialog's
    ``--textbox``) over a 40-line scratch text file whose vertical
    ``QScrollBar`` rests at value zero; the engine draws the bar through
    this theme's ``[Scrollbar]``/``[ScrollbarSlider]``/``[ScrollbarGroove]``
    sections: the raised 16px ``scrollbarslider`` handle with its 13px
    ``grip`` indicator, the ``slider``-element trough and the
    ``arrow``-element buttons. No collected reference screenshot shows a
    dialog with a scrollbar, so the comparison surfaces are the shipped art
    recipe. At value zero the bar rests, so no hover, press or focus byte
    enters any crop: value zero disables the up arrow (its triangle paints
    the disabled #999999 ``arrow`` tint) while the down arrow stays enabled
    in the normal #000000 state, and the bar has no caret: the dialog is
    byte-deterministic at rest. Measured on three consecutive full
    ``--textbox-dialog`` captures on this host (kdialog 25.04.0,
    2026-11-10) -- two plain runs and one with a longer settle -- that
    agreed byte for byte under ``cmp``; a 200-line probe file reproduced
    the same bytes because the 40-line file's handle already rests at the
    platform's minimum slider length. The handle's interior is 12px wide
    (the ``[Scrollbar]`` ``scroll_width=16`` track minus the section's own
    2px frame margins), so the 13px ``grip`` indicator lands resampled with
    half-pixel edge tones the engine paints from the shipped art: the
    engine cannot be steered to the art's native width here (the interior
    width is fixed by the shipped section itself), and the grip band below
    pins the drawn result of the shipped recipe, recording that deviation.
    The engine also paints a blue position-fade overlay across the trough's
    first rows below the resting handle (rows 131..161, a platform value no
    shipped art element defines and no reference screenshot shows; recorded
    2026-11-10 from the same agreeing capture set), so the trough pin's
    crop sits below it, where the ``slider`` interior is flat #EEEEEE.
    """

    KIND = "textbox"

    def test_pins_the_handle_top_outline_and_its_white_arm(self):
        # Row 95 the 1px #000000 outline, row 96 the #FFFFFF top bevel arm
        # inside it, row 97 the face -- the raised arrangement the
        # scrollbarslider element art draws.
        self.assert_band(
            TEXTBOX_DIALOG_HANDLE_TOP_BAND,
            (
                ('#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000'),
                ('#000000', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#FFFFFF', '#999999', '#000000'),
                ('#000000', '#FFFFFF', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#999999', '#000000'),
            ),
        )

    def test_pins_the_handle_left_outline_and_its_white_arm(self):
        # Column 352 the 1px #000000 outline, column 353 the #FFFFFF left
        # bevel arm inside it, column 354 the face (the grip's resampled
        # leftmost bar reaches it on rows 107..119), over the handle's 32
        # interior rows clear of every horizontal band.
        self.assert_band(
            TEXTBOX_DIALOG_HANDLE_LEFT_BAND,
            (
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#000000'),
                ('#000000', '#FFFFFF', '#000000'),
                ('#000000', '#FFFFFF', '#000000'),
                ('#000000', '#FFFFFF', '#000000'),
                ('#000000', '#FFFFFF', '#000000'),
                ('#000000', '#FFFFFF', '#000000'),
                ('#000000', '#FFFFFF', '#000000'),
                ('#000000', '#FFFFFF', '#000000'),
                ('#000000', '#FFFFFF', '#000000'),
                ('#000000', '#FFFFFF', '#000000'),
                ('#000000', '#FFFFFF', '#000000'),
                ('#000000', '#FFFFFF', '#000000'),
                ('#000000', '#FFFFFF', '#000000'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
                ('#000000', '#FFFFFF', '#DDDDDD'),
            ),
        )

    def test_pins_the_handle_bottom_outline_and_its_shadow_arm(self):
        # Row 128 the face, row 129 the #999999 bottom bevel arm inside the
        # 1px #000000 outline of row 130 -- swapping the highlight and
        # shadow arms fails both this pin and the top one.
        self.assert_band(
            TEXTBOX_DIALOG_HANDLE_BOTTOM_BAND,
            (
                ('#000000', '#FFFFFF', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#999999', '#000000'),
                ('#000000', '#FFFFFF', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#000000'),
                ('#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000'),
            ),
        )

    def test_draws_the_grip_bars_across_the_handle_middle(self):
        # Thirteen identical rows across the handle's middle: the 13px
        # `grip` indicator's three #000000 bars painted from the shipped
        # art over the #DDDDDD face (resampled, with the half-pixel edge
        # tones the class comment records), flanked by the outline and
        # bevel columns. A dropped `grip` indicator, a foreign bar tint or
        # a shifted indicator centre fails row by row.
        grip_row = (
            '#000000', '#FFFFFF', '#000000', '#000000', '#838383',
            '#DDDDDD', '#B0B0B0', '#000000', '#000000', '#B0B0B0',
            '#DDDDDD', '#838383', '#000000', '#000000', '#999999',
            '#000000',
        )
        self.assert_band(
            TEXTBOX_DIALOG_GRIP_BAND,
            tuple(grip_row for _ in range(TEXTBOX_DIALOG_GRIP_BAND[3])),
        )

    def test_pins_the_disabled_up_arrow_rows(self):
        # The disabled up triangle's widest rows: the #999999 `arrow`
        # disabled tint with its antialiased #CCCCCC/#AAAAAA edge tones
        # over the button's raised #DDDDDD face, and never #000000.
        self.assert_band(
            TEXTBOX_DIALOG_UP_ARROW_BAND,
            (
                ('#DDDDDD', '#DDDDDD', '#AAAAAA', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#AAAAAA', '#DDDDDD', '#DDDDDD'),
                ('#DDDDDD', '#CCCCCC', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#CCCCCC', '#DDDDDD'),
                ('#DDDDDD', '#AAAAAA', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#AAAAAA', '#DDDDDD'),
                ('#CCCCCC', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#CCCCCC'),
                ('#AAAAAA', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#999999', '#AAAAAA'),
            ),
        )

    def test_the_disabled_up_triangle_carries_no_black_byte(self):
        # Value zero disables the up arrow: the enabled `arrow` state paints
        # #000000, so a #000000 byte anywhere in the resting up triangle
        # fails -- an always-enabled arrow cannot hide from this scan.
        image = self.candidate_image()
        x, y, width, height = TEXTBOX_DIALOG_UP_ARROW_TRIANGLE
        for row in range(height):
            for dx in range(width):
                with self.subTest(row=y + row, x=x + dx):
                    self.assertNotEqual(
                        "#000000", hex_colour(pixel_at(image, x + dx, y + row))
                    )

    def test_pins_the_enabled_down_arrow_rows(self):
        # The enabled down triangle: the normal #000000 `arrow` state over
        # the same raised #DDDDDD face, so a one-tint arrow pair or a
        # disabled bottom arrow fails row by row.
        self.assert_band(
            TEXTBOX_DIALOG_DOWN_ARROW_BAND,
            (
                ('#373737', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#373737'),
                ('#A6A6A6', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#A6A6A6'),
                ('#DDDDDD', '#373737', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#373737', '#DDDDDD'),
                ('#DDDDDD', '#A6A6A6', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#A6A6A6', '#DDDDDD'),
                ('#DDDDDD', '#DDDDDD', '#373737', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#373737', '#DDDDDD', '#DDDDDD'),
                ('#DDDDDD', '#DDDDDD', '#A6A6A6', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#A6A6A6', '#DDDDDD', '#DDDDDD'),
                ('#DDDDDD', '#DDDDDD', '#DDDDDD', '#373737', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#373737', '#DDDDDD', '#DDDDDD', '#DDDDDD'),
                ('#DDDDDD', '#DDDDDD', '#DDDDDD', '#A6A6A6', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#A6A6A6', '#DDDDDD', '#DDDDDD', '#DDDDDD'),
                ('#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#373737', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#373737', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD'),
                ('#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#A6A6A6', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#A6A6A6', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD'),
                ('#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#373737', '#000000', '#000000', '#000000', '#000000', '#373737', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD'),
                ('#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#A6A6A6', '#000000', '#000000', '#000000', '#000000', '#A6A6A6', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD'),
                ('#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#373737', '#000000', '#000000', '#373737', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD'),
                ('#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#A6A6A6', '#000000', '#000000', '#A6A6A6', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD', '#DDDDDD'),
            ),
        )

    def test_keeps_the_trough_interior_flat_below_the_handle(self):
        # The rows between the trough's outline columns run clear of the
        # handle's outline row above and of the engine's blue position-fade
        # overlay (rows 131..161, see the class comment), so every byte
        # must be the flat #EEEEEE `slider` interior face: a groove bevel
        # arm, a filled value band or a glyph byte inside the face fails
        # row by row.
        x, y, width, height = TEXTBOX_DIALOG_TROUGH_CROP
        self.assert_band(
            TEXTBOX_DIALOG_TROUGH_CROP,
            tuple(["#EEEEEE"] * width for _ in range(height)),
        )


class TestTextboxDialogGateSkipGuards(unittest.TestCase):
    """The text-box dialog gate skips wherever its render CLI refuses on a tool.

    The shared guard condition and the other widget gates' flags are pinned in
    ``tests/test_render_dialog_gates.py``; this module pins its own gate's flag
    beside the gate it guards.
    """

    def test_the_textbox_dialog_gate_skips_only_when_a_tool_is_absent(self):
        expected = software_renderer_skip_reason() is not None or not all(
            shutil.which(tool) for tool in DIALOG_REAL_TOOLS
        )
        self.assertEqual(expected, TestTextboxDialogRender.__unittest_skip__)
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
