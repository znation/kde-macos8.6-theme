"""The kdialog widget dialog gates' rendered pixels, pinned gate by gate.

``tools/render_surface.py``'s thirteen ``--*-dialog`` modes open kdialog
clients whose engine-drawn widgets these gates byte-compare with the shipped
Kvantum art: the shared capture plumbing lives in
``tests/support/render_gates.py``, the file-dialog gate in
``tests/test_render_file_dialog.py``, and the applet, desktop and splash
gates in ``tests/test_render_surface.py``.
"""

from __future__ import annotations

import os
import shutil
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.aurorae_fixtures import AURORAE_DIR, INACTIVE_FRAME_GREY
from support.firstboot_lineedit import FIELD_BORDER_RUNS, FIELD_CORNER_PIXELS
from support.kvantum_fixtures import SVG
from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    INACTIVE_OUTLINE,
    WHITE,
    hex_colour,
)
from support.render_gates import (
    DIALOG_REAL_TOOLS,
    REAL_TOOLS,
    SOFTWARE_RENDER_SKIP_REASON,
    DialogGate,
    dialog_gate_guard,
    probe_gate_skip,
    software_renderer_skip_reason,
)
from support.svg_case import parse_svg
from svg_assertions import render_slices
from tools import render_surface  # noqa: E402
from tools.png import pixel_at  # noqa: E402


# The rendered check box cell: the shipped 14x14 canvas at 1:1, measured
# against `tests/test_kvantum_checkbox_reference.py`'s shipped-art slice.
CHECKBOX_CROP = (156, 187, 14, 14)
# The active Aurorae close box at the top-left of kdialog's decorated window,
# measured on two consecutive 480x360 `--checkbox-dialog` captures on this
# host (2026-11-04); `cmp` confirmed the captures were byte-identical. The
# window begins at (144, 117), and the rc's 4px left/top edge places the
# native 13x13 close art at (148, 121), matching frame-local (4, 4); those
# 169 capture pixels match `close.svg`'s active-center slice exactly.
CHECKBOX_CLOSE_BOX_CROP = (148, 121, 13, 13)
# A 1px face ring around the cell catches resampling bleed: at the engine's
# native size the cells around the art stay the flat client face.
CHECKBOX_FACE_RING_CROP = (155, 186, 16, 16)
CHECKBOX_YES_BUTTON = (156, 207, 82, 24)
CHECKBOX_NO_BUTTON = (241, 207, 82, 24)
# The rendered combo box indicator: the shipped 12x12 canvas at 1:1, measured
# against `tests/test_kvantum_combobox_reference.py`'s reference cell. The
# combo dialog is the session's only window like the checkbox dialog, so the
# crop is measured on the same 480x360 capture.
COMBOBOX_CROP = (316, 178, 12, 12)
# The rendered combo field: `[ComboBox] frame.element=combofield` draws its
# frame slices from the dedicated raised family, so the field bands are the
# reference's raised arrangement in every state the engine may select.
COMBOBOX_FIELD = (146, 172, 188, 24)
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
# The rendered Kvantum line edit in the input dialog: kdialog's
# `--inputbox` opens an empty QLineEdit the engine sinks with the theme's
# `lineedit-normal` art, in the reference Setup Assistant field's sunken
# arrangement: a #999999 top/left shadow over the window face, the 1px
# #000000 outline inside it and the #FFFFFF face. The field occupies
# (146,172)..(333,195), a 188x24 box, measured on two consecutive
# 480x360 `--lineedit-dialog` captures on this host (2026-11-10) whose two
# runs agreed byte for byte under `cmp`, and a third run in the same
# batch reproduced them byte for byte. The combo dialog is the
# session's only window like the checkbox dialog, so the crop is measured
# on the same 480x360 capture.
LINEEDIT_DIALOG_FIELD = (146, 172, 188, 24)
# The field's full-height face band, right of the caret: the empty input
# box's caret paints a 1px column at x=154 inside the face, and the
# caret's blink phase flips only that column's rows 176..191 between runs
# (every other byte of two consecutive runs agrees), so the band from
# x=200 stays clear of it; the band's top and bottom rows are the sunken
# bevel rows, so an off-by-one row slips a #DDDDDD window-face byte in
# and fails.
LINEEDIT_DIALOG_FIELD_CROP = (200, 172, 120, 24)
# The rendered OK push button, left of its label glyphs, measured on the
# same agreeing pair as the field: the existing push-button arrangement the
# checkbox and combo gates pin, at the same rect they measure, 1px
# #000000 border rows and border column, the #FFFFFF bevel top and left
# arms, the flat #DDDDDD face and the #AAAAAA bottom arm.
LINEEDIT_DIALOG_OK_BUTTON = (167, 199, 82, 24)
# The rendered GTK 4 dialog window's top shell edge strip, where the CSD
# window meets the session: the window's #DDDDDD surface spans x=90..389 with
# its top face row at y=49 on the same 480x360 capture, measured 2026-11-03
# on a consecutive pair of full `tools/render_surface.py --gtk-dialog` runs
# on this host (zenity 4.1.90, GTK 4.18.6) whose two captures agreed bit for
# bit under cmp, and reproduced bit for bit by a third consecutive run.
# The session background is black, so the existing active window.csd outline
# (box-shadow: 0 0 0 1px #000000, pinned in the sheet by
# TestGtk4Theme::test_csd_window_shell) is continuous with it: the pinned
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
PROGRESSBAR_DIALOG_TROUGH = (146, 172, 188, 24)
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
TEXTBOX_DIALOG_HANDLE = (352, 95, 16, 36)
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
# The calendar dialog's pinned bands, measured on two consecutive full
# `tools/render_surface.py --calendar-dialog` runs on 2026-11-10 whose two
# 480x360 captures agreed byte for byte under `cmp` (see
# TestCalendarDialogRender for what each band pins).
CALENDAR_WINDOW_FACE = (110, 68, 250, 8)
CALENDAR_SELECTED_CELL = (222, 157, 35, 18)
CALENDAR_WEEKDAY_FACE_ROWS = (140, 141, 152, 153, 154, 155)
# The selected day's digit renders anti-aliased over the #CCCCFF fill: the
# five #000000 pixels are its hinted core and the rest are the blend tones
# the engine paints around it, so the cell asserts the fill except this map.
CALENDAR_CELL_DIGIT_INK = {
    (236, 161): "#2A2A35", (237, 161): "#000000", (238, 161): "#000000",
    (239, 161): "#000000", (240, 161): "#000000", (241, 161): "#000000",
    (242, 161): "#62627B", (236, 162): "#BCBCEB", (237, 162): "#B2B2DF",
    (238, 162): "#B2B2DF", (239, 162): "#B2B2DF", (240, 162): "#ADADD8",
    (241, 162): "#121216", (242, 162): "#9A9AC0", (240, 163): "#7A7A99",
    (241, 163): "#2B2B36", (239, 164): "#CACAFC", (240, 164): "#1C1C23",
    (241, 164): "#8A8AAC", (239, 165): "#8686A7", (240, 165): "#1E1E25",
    (241, 165): "#CACAFD", (239, 166): "#26262F", (240, 166): "#7B7B9A",
    (238, 167): "#9292B6", (239, 167): "#131318", (240, 167): "#C6C6F8",
    (238, 168): "#31313D", (239, 168): "#6C6C87", (237, 169): "#9D9DC4",
    (238, 169): "#0A0A0D", (239, 169): "#C0C0F0", (237, 170): "#3D3D4C",
    (238, 170): "#66667F",
}
# The white-face weekday-letter row's hinted ink cores: the leading columns'
# letters core at the palette's ForegroundInactive gray, the trailing ones at
# full-strength black (see TestCalendarDialogRender).
CALENDAR_WEEKDAY_GRAY_INK = (
    (136, 144), (201, 144), (133, 146), (134, 146), (209, 146), (209, 147),
    (310, 149), (124, 151), (125, 151), (126, 151), (127, 151), (128, 151),
    (161, 151), (162, 151), (163, 151), (164, 151), (165, 151),
)
CALENDAR_WEEKDAY_BLACK_INK = (
    (350, 144), (310, 151), (311, 151), (312, 151), (313, 151), (314, 151),
)
# The leftmost day column's Sunday digits' hinted red cores (#800000, darker
# than the nearest palette entry -- see TestCalendarDialogRender).
CALENDAR_RED_INK = (
    (136, 200), (133, 202), (134, 202), (133, 217), (134, 217), (135, 217),
    (136, 223), (136, 224), (124, 226), (125, 226), (126, 226), (127, 226),
    (128, 226),
)
# The color dialog's pinned bands, measured on two consecutive full
# `tools/render_surface.py --color-dialog` runs on 2026-11-10 whose two
# 480x360 captures agreed byte for byte under `cmp` (see
# TestColorDialogRender for what each band pins).
COLOR_WINDOW_FACE = (100, 200, 120, 9)
# The basic-color grid's first row at its deepest pass: the #000000 lead
# cell and its #AA0000 neighbour, both the grid's constant fills, with
# the #DDDDDD gap columns between the cells.
BASIC_SWATCH_ROW = (17, 57, 46, 6)
# A band over one sunken value field's left edge and face interior, rows
# the field's spin box text never reaches: two face columns, the #999999
# top/left shadow column, the 1px #000000 outline column, the #FFFFFF
# face run and four face columns to the right of the field.
SUNKEN_VALUE_FIELD_BAND = (330, 212, 40, 4)
# The dialog's left push button in the default-button row: the existing
# raised recipe (see TestColorDialogRender) at the 82x24 button size the
# other dialog gates pin.
PUSH_BUTTON = (301, 324, 82, 24)
# The button's full-height label-free left cell: the outline row, the
# white bevel top arm, the bevel column over the #DDDDDD face and the
# #AAAAAA shadow arm, then the bottom outline row.
PUSH_BUTTON_CELL = (302, 324, 5, 24)
# Label-free face rows for the frame pin beside the cell band.
PUSH_BUTTON_FLAT_ROWS = (327, 328, 329, 341, 342, 343, 344, 345)
# The icon dialog's pinned bands, measured on two consecutive full
# `tools/render_surface.py --icon-dialog` runs on 2026-11-10 whose two
# 480x360 captures differ only in the search field's blinking caret (16
# pixels in the one column x=302, rows y=33..48) and agree everywhere
# else -- every band re-derived from the pair avoids that column and all
# its rows (see TestIconDialogRender for what each band pins).
ICON_WINDOW_FACE = (100, 23, 300, 6)
# A band over the icon-grid field's top edge: the window-face row above,
# the #999999 shadow-arm row, the 1px #000000 outline row and the white
# #FFFFFF field face below the outline.
ICON_GRID_TOP_EDGE = (200, 55, 40, 5)
# A band over the search field's left edge in caret- and glyph-free rows:
# the #999999 top/left shadow column and arm over the 1px #000000
# outline and the white #FFFFFF field face, with the outline's right
# corner and the outer white arm from the outline's edge on.
ICON_SEARCH_FIELD_BAND = (294, 29, 174, 4)
# The dialog's default-button row: the existing raised recipe (see
# TestIconDialogRender) at the 82x24 button size the other dialog gates
# pin.
ICON_PUSH_BUTTON = (301, 324, 82, 24)
# The button's full-height label-free left cell: the outline row, the
# white bevel top arm, the bevel column over the #DDDDDD face and the
# #AAAAAA shadow arm, then the bottom outline row.
ICON_PUSH_BUTTON_CELL = (302, 324, 5, 24)
# Label-free face rows for the frame pin beside the cell band.
ICON_PUSH_BUTTON_FLAT_ROWS = (327, 328, 329, 341, 342, 343, 344, 345)
COMBOBOX_OK_BUTTON = (167, 199, 82, 24)
COMBOBOX_CANCEL_BUTTON = (252, 199, 82, 24)
MENU_ITEM_VIEW = (112, 93, 256, 182)
# The clear part of the first selected row, away from its radio indicator and
# label glyphs; measured on two byte-identical radio-list captures on
# 2026-11-11.
RADIO_DIALOG_SELECTION_BAND = (200, 97, 164, 16)
# Dark core pixels in the selected radio dot and an unchecked radio ring.
RADIO_DIALOG_CHECKED_DOT = (121, 106)
RADIO_DIALOG_UNCHECKED_RING = (119, 120)
# The sunken list field's top-left outer and inner frame pixels; the viewport
# sample is below the selected row, clear of text and indicator art.
RADIO_DIALOG_FIELD_FRAME = ((112, 93), (113, 94))
RADIO_DIALOG_VIEW_FACE = (200, 140)

class TestDialogGateSkipGuards(unittest.TestCase):
    """The fourteen dialog gates' shared skip guard encodes the render CLI's refusals.

    The dialog render CLI refuses with a missing-tool diagnostic when any
    of the five applet-render tools or the dialog client its requested mode
    opens is absent (kdialog for the thirteen kdialog modes, zenity for the
    GTK mode), and the fourteen dialog gates' shared skip guard encodes exactly
    that condition. These tests fail wherever a guard is removed
    (``AttributeError`` on ``__unittest_skip__``) and where a guard's tool
    list drifts from the render CLI's own requirement list, the local
    literal the guards otherwise all repeat. The thirteen widget gates'
    flags are pinned here; ``tests/test_render_file_dialog.py`` pins its
    own gate's.
    """

    def test_the_skip_guards_encode_the_render_cli_s_refusal_list(self):
        # The guards above skip on a local tool list, so the list must be
        # the render CLI's own requirement list: a tool the CLI requires
        # but a guard omits would make the guard's class run and fail on a
        # host that lacks it, where the CLI refuses and the sibling table
        # row says the suite skips. `make` is the only CLI requirement the
        # guards leave out: it names the command the suite itself runs
        # under, so it cannot be absent while one of these tests runs.
        self.assertEqual(
            {"make"},
            set(render_surface.REQUIRED_TOOLS) - set(REAL_TOOLS),
        )
        self.assertEqual(
            {"kdialog", "zenity"},
            set(DIALOG_REAL_TOOLS) - set(render_surface.REQUIRED_TOOLS),
        )

    def test_the_skip_guard_also_covers_a_software_renderer(self):
        # The hosted job forces llvmpipe, where KWin's ScreenShot2 effect
        # hangs before it can reply; the guard must skip the capture rather
        # than let the render time out.
        with mock.patch.dict(
            os.environ, {"MESA_LOADER_DRIVER_OVERRIDE": "llvmpipe"}, clear=False
        ):
            self.assertEqual(
                SOFTWARE_RENDER_SKIP_REASON, software_renderer_skip_reason()
            )
        with mock.patch.dict(
            os.environ, {"LIBGL_ALWAYS_SOFTWARE": "1"}, clear=False
        ):
            self.assertEqual(
                SOFTWARE_RENDER_SKIP_REASON, software_renderer_skip_reason()
            )
        with mock.patch.dict(
            os.environ, {"MESA_LOADER_DRIVER_OVERRIDE": "iris"}, clear=False
        ):
            os.environ.pop("LIBGL_ALWAYS_SOFTWARE", None)
            self.assertIsNone(software_renderer_skip_reason())

    def test_the_skip_guard_covers_a_case_insensitive_gallium_driver(self):
        with mock.patch.dict(
            os.environ, {"GALLIUM_DRIVER": "SoFtPiPe"}, clear=True
        ):
            self.assertEqual(
                SOFTWARE_RENDER_SKIP_REASON, software_renderer_skip_reason()
            )

    def test_the_widget_dialog_gates_skip_only_when_a_tool_is_absent(self):
        tools = DIALOG_REAL_TOOLS
        expected = software_renderer_skip_reason() is not None or not all(
            shutil.which(tool) for tool in tools
        )
        for gate in (
            TestCheckboxDialogRender,
            TestComboboxDialogRender,
            TestLineInputDialogRender,
            TestMenuDialogRender,
            TestRadioDialogRender,
            TestCalendarDialogRender,
            TestColorDialogRender,
            TestIconDialogRender,
            TestProgressbarDialogRender,
            TestSliderDialogRender,
            TestTextboxDialogRender,
            TestGtkDialogRender,
            TestInactiveDialogRender,
            # TestFileDialogRender's flag is pinned beside the gate, in
            # tests/test_render_file_dialog.py.
        ):
            with self.subTest(gate=gate.__name__):
                self.assertEqual(expected, gate.__unittest_skip__)

        # Reapply the real guard to disposable classes: never alter the
        # render gates or start a session while simulating missing tools.
        for missing in (None, *tools):
            with self.subTest(missing=missing):
                self.assertEqual(
                    missing is not None,
                    probe_gate_skip(dialog_gate_guard, missing),
                )


@dialog_gate_guard()
class TestCheckboxDialogRender(DialogGate, unittest.TestCase):
    """The engine-drawn check box the dialog render captures is the shipped art.

    The chrome strips above byte-compare the Aurorae decoration of an empty
    applet window; no strip ever compared a pixel the Kvantum engine drew, so
    a rendered widget could stay wrong -- the resampled check box indicator
    fixed 2026-10-30 was found only by a manual render pass. The dialog render
    opens a real QCheckBox (kdialog's ``--dontagain`` box) drawn by the engine
    with the theme's checkbox art, and this class byte-compares the rendered
    14x14 cell with the shipped-art slice the Kvantum reference suite derives
    from the same SVG, plus the flat face ring around it.
    """

    KIND = "checkbox"

    def test_draws_the_close_box_cell_1_to_1(self):
        # Re-derive the expected art from Aurorae's active SVG slice. This
        # catches a shifted crop, inactive state, resampling, or foreign paint.
        expected = dict(
            render_slices(parse_svg(os.path.join(AURORAE_DIR, "close.svg")))[
                "active-center"
            ]
        )
        x0, y0, width, height = CHECKBOX_CLOSE_BOX_CROP
        actual = {
            (x, y): hex_colour(
                pixel_at(self.candidate_image(), x0 + x, y0 + y)
            )
            for x in range(width)
            for y in range(height)
        }
        self.assertEqual(expected, actual)

    def test_draws_the_check_box_cell_1_to_1(self):
        # The candidate cell bytes come straight from the render (see
        # DialogGate.assert_cell_matches): a blended band shows up here
        # immediately.
        self.assert_cell_matches("checkbox-normal", CHECKBOX_CROP)

    def test_default_button_has_no_interior_focus_or_indicator_art(self):
        image = self.candidate_image()
        # These two points are on the focus ring's horizontal bands; the
        # bottom-right point also lies inside Kvantum's default indicator.
        for point in ((195, 209), (195, 228), (231, 224)):
            with self.subTest(point=point):
                self.assertEqual(FACE, hex_colour(pixel_at(image, *point)))

    def test_installs_the_check_box_cell_in_a_flat_face_ring(self):
        # One byte of resampling bleed lands on the 1px ring around the
        # cell, so the region the cell sits in must equal the flat client
        # face around the shipped art it byte-compares.
        slices = render_slices(parse_svg(SVG))
        art = slices["checkbox-normal"]
        image = self.candidate_image()
        x0, y0, width, height = CHECKBOX_FACE_RING_CROP
        for x in range(width):
            for y in range(height):
                expected = (
                    art[(x - 1, y - 1)]
                    if 1 <= x <= width - 2 and 1 <= y <= height - 2
                    else FACE
                )
                with self.subTest(x=x, y=y):
                    self.assertEqual(
                        expected, hex_colour(pixel_at(image, x0 + x, y0 + y))
                    )

    def test_default_button_focus_ring_does_not_cross_its_face(self):
        image = self.candidate_image()
        # These are label-free interior pixels on the focused Yes button.
        # The reference's default mark sits outside the bevel, so the button
        # face remains the shipped flat Platinum grey here.
        for x, y in ((195, 209), (195, 228)):
            with self.subTest(x=x, y=y):
                self.assertEqual("#DDDDDD", hex_colour(pixel_at(image, x, y)))

    def test_yes_and_no_buttons_keep_their_engine_drawn_frames(self):
        self.assert_raised_frame(CHECKBOX_YES_BUTTON, flat_rows=(209, 210, 211, 212))
        self.assert_raised_frame(CHECKBOX_NO_BUTTON, flat_rows=(209, 210, 211, 212))


@dialog_gate_guard()
class TestComboboxDialogRender(DialogGate, unittest.TestCase):
    """The engine-drawn combo box indicator the dialog render captures is 1:1.

    The combo render opens a real ``QComboBox`` (kdialog's ``--combobox``)
    drawn by the engine with this theme's ``comboarrow-*`` art through
    ``[ComboBox] indicator.size``, and byte-compares the rendered 12x12 cell
    with the shipped-art slice. The squashed 4px-wide arrow this gate guards
    against was the very render bug the check box cell alone could not see;
    the render pass found the combo arrow while the check box one was fixed,
    so the two gates must hold together.
    """

    KIND = "combobox"

    def test_draws_the_combo_arrow_cell_1_to_1(self):
        # The candidate cell bytes come straight from the render (see
        # DialogGate.assert_cell_matches): a squashed or blended arrow shows
        # up here immediately.
        self.assert_cell_matches("comboarrow-normal", COMBOBOX_CROP)

    def test_combo_field_keeps_its_engine_drawn_raised_frame(self):
        self.assert_raised_frame(COMBOBOX_FIELD)

    def test_draws_the_combo_field_raised_bevel(self):
        """Pin the Kvantum field frame around the selected combo contents."""
        image = self.candidate_image()
        x, y, width, height = COMBOBOX_FIELD
        # `[ComboBox] frame.element=combofield` maps every state to the
        # reference's raised arrangement, whatever state the engine selects.
        # The upper and lower bands and the two bevel columns are outside
        # the text and arrow, so these pixels isolate the engine's frame
        # mapping.
        expected_top = ["#000000"] * width
        expected_upper = ["#000000", *(["#FFFFFF"] * (width - 3)), "#AAAAAA", "#000000"]
        expected_lower = ["#000000", "#FFFFFF", *(["#AAAAAA"] * (width - 3)), "#000000"]
        expected_bottom = ["#000000"] * width
        for row, expected in ((0, expected_top), (1, expected_upper),
                              (height - 2, expected_lower), (height - 1, expected_bottom)):
            with self.subTest(row=row):
                self.assertEqual(
                    expected,
                    [hex_colour(pixel_at(image, x + dx, y + row)) for dx in range(width)],
                )
        for dy in range(2, height - 2):
            with self.subTest(column="left", row=dy):
                self.assertEqual("#000000", hex_colour(pixel_at(image, x, y + dy)))
            with self.subTest(column="left-highlight", row=dy):
                self.assertEqual("#FFFFFF", hex_colour(pixel_at(image, x + 1, y + dy)))
            with self.subTest(column="right-shadow", row=dy):
                self.assertEqual("#AAAAAA", hex_colour(pixel_at(image, x + width - 2, y + dy)))
            with self.subTest(column="right-edge", row=dy):
                self.assertEqual("#000000", hex_colour(pixel_at(image, x + width - 1, y + dy)))
        # The flat interior fill's edge columns: the field's face runs flat
        # beside the bevel where neither the selected text nor the pinned
        # arrow cell reaches.
        for yy in range(y + 2, y + height - 2):
            self.assert_pixel(x + 2, yy, "#DDDDDD")
            self.assert_pixel(x + width - 3, yy, "#DDDDDD")

    def test_ok_and_cancel_buttons_keep_their_engine_drawn_frames(self):
        self.assert_raised_frame(COMBOBOX_OK_BUTTON, flat_rows=(201, 202, 203, 204))
        self.assert_raised_frame(COMBOBOX_CANCEL_BUTTON, flat_rows=(201, 202, 203, 204))


@dialog_gate_guard()
class TestLineInputDialogRender(DialogGate, unittest.TestCase):
    """The engine-drawn line edit the dialog render captures is the shipped art.

    The line-edit dialog opens a real ``QLineEdit`` (kdialog's ``--inputbox``
    with no initial value) which the engine sinks with this theme's
    ``lineedit-normal`` art; the shipped tiles' pixels are the reference
    Setup Assistant field's sunken arrangement (the Kvantum reference suite
    re-derives both from the same image), but no pixel-level gate watched a
    rendered line edit, so a ``[LineEdit]`` regression would have shipped
    green. This class pins the rendered field's sunken arrangement against
    the reference-derived border-role table the two reference suites share.
    """

    KIND = "lineedit"

    def test_draws_the_field_sunken_bevel(self):
        """Pin the Kvantum field's sunken rows right of the caret."""
        width, height = LINEEDIT_DIALOG_FIELD_CROP[2:]
        # The reference field's border runs (tests/support/firstboot_lineedit.py)
        # give the arrangement: #999999 shadow row, #000000 outline, #FFFFFF
        # face, then the bottom outline and outer #FFFFFF highlight. The
        # crop's rows are exactly the field's, so an off-by-one row fails.
        self.assert_band(
            LINEEDIT_DIALOG_FIELD_CROP,
            (
                ["#999999"] * width,
                ["#000000"] * width,
                *( ["#FFFFFF"] * width for _ in range(height - 4) ),
                ["#000000"] * width,
                ["#FFFFFF"] * width,
            ),
        )

    def test_field_lands_keep_the_reference_corner_arrangement(self):
        """Pin the field's border columns and the four 2x2 corner blocks.

        The expected pixels are the reference field's border runs and corner
        pixels (``tests/support/firstboot_lineedit.py``) transposed onto the
        rendered 188x24 field: left/top runs replace with shadow #999999 and
        outline #000000, while the right/bottom runs and the corners keep
        the reference's face/outline/highlight roles. The two corner slots
        the reference leaves unpainted (the top-right and bottom-left outer
        pixels showing that Finder window's own face) stay engine-unpainted
        here and show this dialog's own window face, the #DDDDDD body face
        the checkbox gate's window probes.
        """
        image = self.candidate_image()
        window_face = "#DDDDDD"
        ref_x0 = min(rx for (rx, _), _ in FIELD_BORDER_RUNS)
        ref_x1 = max(rx for (rx, _), _ in FIELD_BORDER_RUNS)
        ref_y0 = min(ry for (_, ry), _ in FIELD_BORDER_RUNS)
        ref_y1 = max(ry for (_, ry), _ in FIELD_BORDER_RUNS)
        x0, y0, width, height = LINEEDIT_DIALOG_FIELD

        def position(rx, ry):
            """Transposing a reference field pixel's role onto the render.

            Left/top reference runs land on the shadow and outline columns
            and rows at the field's origin; the right/bottom runs and both
            corner blocks land at the field's far edges, where the rendered
            field's box is one column narrower than the reference's forty-
            pixel-wide face, so the roles map by their run side, not by a
            global offset.
            """
            dx = rx - ref_x0 if rx <= ref_x0 + 1 else width - 2 + (rx - ref_x1 + 1)
            dy = ry - ref_y0 if ry <= ref_y0 + 1 else height - 2 + (ry - ref_y1 + 1)
            return x0 + dx, y0 + dy

        expected = {
            position(rx, ry): (window_face if colour == "#CCCCCC" else colour)
            for (rx, ry), colour in FIELD_CORNER_PIXELS
        }
        # The border runs themselves, minus the corner blocks the pin above
        # named: the left shadow and outline columns down the face-band rows
        # and the right face/outline/highlight trio on the same rows.
        face_row_lo, face_row_hi = y0 + 2, y0 + height - 3
        for yy in range(face_row_lo, face_row_hi + 1):
            expected[x0, yy], expected[x0 + 1, yy] = "#999999", "#000000"
            expected[x0 + width - 3, yy] = "#FFFFFF"
            expected[x0 + width - 2, yy] = "#000000"
            expected[x0 + width - 1, yy] = "#FFFFFF"
        # Top and bottom border rows off the corner columns: the same runs
        # the reference pins at a mid-face column.
        for xx in range(x0 + 2, x0 + width - 1):
            expected[xx, y0] = "#999999"
            expected[xx, y0 + 1] = "#000000"
            expected[xx, y0 + height - 2] = "#000000"
            expected[xx, y0 + height - 1] = "#FFFFFF"
        self.assertEqual(
            expected,
            {
                (xx, yy): hex_colour(pixel_at(image, xx, yy))
                for xx, yy in sorted(expected)
            },
        )

    def test_ok_button_keeps_its_engine_drawn_frame(self):
        self.assert_raised_frame(
            LINEEDIT_DIALOG_OK_BUTTON, flat_rows=(201, 202, 203, 204)
        )

    def test_draws_the_ok_button_face_at_the_existing_recipe(self):
        # The OK button is the dialog's default, so a focus ring painted at
        # the face rows would cross this pin the way the checkbox gate's
        # default-button pin does.
        image = self.candidate_image()
        x, y, width, height = LINEEDIT_DIALOG_OK_BUTTON
        self.assertEqual(
            ["#DDDDDD"] * (width - 4),
            [hex_colour(pixel_at(image, x + 2 + dx, y + 2)) for dx in range(width - 4)],
        )


@dialog_gate_guard()
class TestMenuDialogRender(DialogGate, unittest.TestCase):
    """The menu dialog's item view keeps its engine-drawn sunken frame."""

    KIND = "menu"

    def test_item_view_frame_matches_its_measured_border_runs(self):
        x, y, width, height = MENU_ITEM_VIEW
        for xx in range(x, x + width - 1):
            self.assert_pixel(xx, y, "#999999")
        for xx in range(x + 1, x + width):
            self.assert_pixel(xx, y + height - 1, "#FFFFFF")
        for xx in range(x + 1, x + width - 1):
            self.assert_pixel(xx, y + height - 2, "#000000")
        for yy in range(y, y + height - 1):
            self.assert_pixel(x, yy, "#999999")
        for yy in range(y + 1, y + height - 1):
            self.assert_pixel(x + 1, yy, "#000000")
            self.assert_pixel(x + width - 2, yy, "#000000")
            self.assert_pixel(x + width - 1, yy, "#FFFFFF")
        # Both unpainted corners are the window face, stated explicitly as
        # the record requires; the art never paints either of them.
        self.assert_pixel(x + width - 1, y, "#DDDDDD")
        self.assert_pixel(x, y + height - 1, "#DDDDDD")
        # The flat interior fill beside the focus ring: the interior's edge
        # columns and its first row stay the viewport's flat white where no
        # item text or focus art reaches them.
        for yy in range(y + 2, y + height - 2):
            self.assert_pixel(x + 2, yy, "#FFFFFF")
            self.assert_pixel(x + width - 3, yy, "#FFFFFF")
        for xx in range(x + 2, x + width - 2):
            self.assert_pixel(xx, y + 2, "#FFFFFF")

    def test_current_item_focus_ring_is_pinned_inside_the_field(self):
        for xx in range(115, 365):
            self.assert_pixel(xx, 96, "#000000")
            self.assert_pixel(xx, 113, "#000000")
        for yy in range(96, 114):
            self.assert_pixel(115, yy, "#000000")
            self.assert_pixel(364, yy, "#000000")

    def test_draws_the_item_view_frame_and_white_interior(self):
        image = self.candidate_image()
        x0, y0, width, height = MENU_ITEM_VIEW
        self.assertEqual("#999999", hex_colour(pixel_at(image, x0, y0)))
        for x in range(x0, x0 + width - 1):
            with self.subTest(edge="top", x=x):
                self.assertEqual("#999999", hex_colour(pixel_at(image, x, y0)))
        for x in range(x0 + 1, x0 + width - 1):
            with self.subTest(edge="bottom", x=x):
                self.assertEqual("#000000", hex_colour(pixel_at(image, x, y0 + height - 2)))
        self.assertEqual("#999999", hex_colour(pixel_at(image, x0, y0 + height - 2)))
        self.assertEqual("#FFFFFF", hex_colour(pixel_at(image, x0 + width - 1, y0 + height - 2)))
        for y in range(y0 + 1, y0 + height - 1):
            with self.subTest(edge="left", y=y):
                self.assertEqual("#999999", hex_colour(pixel_at(image, x0, y)))
            with self.subTest(edge="right", y=y):
                self.assertEqual("#FFFFFF", hex_colour(pixel_at(image, x0 + width - 1, y)))
        # The two unpainted upper/lower frame corners are the window face.
        self.assertEqual("#DDDDDD", hex_colour(pixel_at(image, x0 + width - 1, y0)))
        self.assertEqual("#DDDDDD", hex_colour(pixel_at(image, x0, y0 + height - 1)))
        for x in range(x0 + 1, x0 + width):
            with self.subTest(edge="lower-white", x=x):
                self.assertEqual("#FFFFFF", hex_colour(pixel_at(image, x, y0 + height - 1)))
        # The current item's focus ring is at y=96..113; sample the white
        # field below it so a frame mapping regression cannot hide in the ring.
        for point in ((114, 120), (200, 120), (365, 272)):
            with self.subTest(point=point):
                self.assertEqual("#FFFFFF", hex_colour(pixel_at(image, *point)))


@dialog_gate_guard()
class TestRadioDialogRender(DialogGate, unittest.TestCase):
    """The radio-list selection, indicators and sunken field keep their paint."""

    KIND = "radiolist"

    def test_selected_row_keeps_its_flat_selection_face(self):
        image = self.candidate_image()
        x, y, width, height = RADIO_DIALOG_SELECTION_BAND
        for yy in range(y, y + height):
            for xx in range(x, x + width):
                self.assertEqual(
                    "#CCCCFF", hex_colour(pixel_at(image, xx, yy)),
                    (xx, yy),
                )

    def test_checked_radio_keeps_its_dark_dot_core(self):
        self.assert_pixel(*RADIO_DIALOG_CHECKED_DOT, "#0C0C0F")

    def test_unchecked_radio_keeps_its_dark_ring_on_white(self):
        self.assert_pixel(*RADIO_DIALOG_UNCHECKED_RING, "#000000")
        self.assert_pixel(117, 120, "#FFFFFF")

    def test_list_field_keeps_its_sunken_frame_and_white_viewport(self):
        outer, inner = RADIO_DIALOG_FIELD_FRAME
        self.assert_pixel(*outer, "#999999")
        self.assert_pixel(*inner, "#000000")
        self.assert_pixel(*RADIO_DIALOG_VIEW_FACE, "#FFFFFF")


@dialog_gate_guard()
class TestCalendarDialogRender(DialogGate, unittest.TestCase):
    """The calendar dialog's day table keeps its palette-painted faces.

    The calendar dialog opens a real month view (kdialog's ``--calendar``
    pinned to January 1970 through ``--default 1970-01-07`` with the
    load-bearing ``--dateformat``: without it kdialog ignores ``--default``
    and opens today's month, with it the view never contains today's date,
    so no today marker, no clock-driven selection and no month-by-month
    layout drift can enter any crop). The day table's faces come from the
    theme's colorscheme palette -- the #DDDDDD window face ([Colors:Window]
    ``BackgroundNormal``), the white day-table face ([Colors:View]
    ``BackgroundNormal``), the #CCCCFF selected-day fill ([Colors:Selection]
    ``BackgroundNormal``), the weekday letter cores over the white face
    (the leading columns' cores at [Colors:View] ``ForegroundInactive``
    #888888, the trailing columns' at full-strength black -- the measured
    blend is the contract and the invariants row records the mixed inks)
    and the leftmost day column's red Sunday digits (nearest palette entry
    [Colors:View] ``ForegroundNegative``; the measured #800000 ink is
    darker, and the discrepancy is recorded rather than the band widened).
    No collected reference screenshot shows a dialog calendar, so the
    comparison values are the measured palette inks over the measured
    480x360 geometry, re-derived on 2026-11-10 from two consecutive full
    captures that agreed byte for byte under ``cmp`` (the crops above).
    """

    KIND = "calendar"

    def test_draws_the_flat_window_face(self):
        """Pin the window-color face crop with no other ink inside.

        The rows are flat #DDDDDD column to column, so a stray glyph row, a
        title-bar bleed or a repaint of the chrome above the day table
        fails row by row.
        """
        self.assert_flat_window_face(CALENDAR_WINDOW_FACE)

    def test_draws_the_selected_day_cell(self):
        """Pin the #CCCCFF selection fill, its digit ink and the white face.

        A re-mapped selection ink, a shifted selection rect or a dropped
        selection fill fails pixel by pixel; the digit ink pins the
        selected day's hinted glyphs (the #000000 cores and the blend
        tones the engine paints around them) so a recoloured or moved
        digit fails too, and the white strips beside the fill pin the day
        table's white face on both sides.
        """
        image = self.candidate_image()
        x0, y0, width, height = CALENDAR_SELECTED_CELL
        expected = {
            (x0 + column, y0 + row): CALENDAR_CELL_DIGIT_INK.get(
                (x0 + column, y0 + row), "#CCCCFF"
            )
            for row in range(height)
            for column in range(width)
        }
        actual = {
            (x0 + column, y0 + row): hex_colour(
                pixel_at(image, x0 + column, y0 + row)
            )
            for row in range(height)
            for column in range(width)
        }
        self.assertEqual(expected, actual)
        # The white day-table face reaches both sides of the selection fill.
        for row in range(y0, y0 + height):
            with self.subTest(row=row):
                self.assertEqual(
                    ["#FFFFFF"] * (x0 - 214),
                    [hex_colour(pixel_at(image, x, row)) for x in range(214, x0)],
                )
                self.assertEqual(
                    ["#FFFFFF"] * 7,
                    [hex_colour(pixel_at(image, x, row))
                     for x in range(x0 + width, x0 + width + 7)],
                )

    def test_draws_the_weekday_letter_inks_over_the_white_face(self):
        """Pin the weekday-letter row's measured inks over the white face.

        The flat white rows above and below the letters pin the face
        itself, and the hinted ink cores pin the letters: a full-strength
        or palette-text ink in the leading columns, a dropped letter tint
        or a shifted letter row fails on the pinned cores.
        """
        image = self.candidate_image()
        for row in CALENDAR_WEEKDAY_FACE_ROWS:
            with self.subTest(row=row):
                self.assertEqual(
                    ["#FFFFFF"] * 252,
                    [hex_colour(pixel_at(image, x, row)) for x in range(114, 366)],
                )
        for point in CALENDAR_WEEKDAY_GRAY_INK:
            with self.subTest(point=point):
                self.assert_pixel(*point, "#888888")
        for point in CALENDAR_WEEKDAY_BLACK_INK:
            with self.subTest(point=point):
                self.assert_pixel(*point, "#000000")

    def test_draws_the_leftmost_day_column_s_red_digits(self):
        """Pin the leftmost day column's red digit cores over the white face.

        The #800000 cores are the measured blend the engine paints from
        the palette's negative-red role; a dropped day tint, a recoloured
        ink or a shifted day column fails on the pinned pixels, and the
        glyph-free white rows beside the digits pin the column's face.
        """
        image = self.candidate_image()
        for point in CALENDAR_RED_INK:
            with self.subTest(point=point):
                self.assert_pixel(*point, "#800000")
        for row in (176, 177, 178, 190, 227, 228):
            with self.subTest(row=row):
                self.assertEqual(
                    ["#FFFFFF"] * 47,
                    [hex_colour(pixel_at(image, x, row)) for x in range(114, 161)],
                )


@dialog_gate_guard()
class TestColorDialogRender(DialogGate, unittest.TestCase):
    """The color dialog's swatches, value fields and push buttons are the theme's.

    The color dialog opens kdialog's ``--getcolor`` picker, whose window
    face, basic-color swatch grid, sunken value fields and push buttons
    the engine draws with the theme's colorscheme palette entries
    ([Colors:Window] and [Colors:Button] the existing art's bevel and
    shadow arms serve): the raised push-button recipe's outline and bevel
    arrangement comes from the shipped button art, the flat face and
    shadow arms from the palette, just as the line-edit gate's field and
    button pins compare. The swatch cells' fills are the grid's own
    constants (the #000000 lead and the #AA0000 neighbour of its first
    row), not palette inks. No collected reference screenshot shows a
    dialog color picker, so the comparison values are the shipped art
    recipe and palette entries above over the measured 480x360 geometry,
    re-derived on 2026-11-10 from two consecutive full captures that
    agreed byte for byte under ``cmp``.

    The dialog shows no clock-dependent content -- no date and no
    clock-driven selection can enter any crop -- so it needs no date or
    default pin. The pinned bands sit clear of the gradient selector's
    dithered rows and of every glyph row: with only flat cells of one
    colour per row, a stray glyph row, a one-pixel crop slip, a lost
    shadow or outline row, a swapped arm colour or a resampled, recoloured
    or dropped swatch fill fails row by row or pixel by pixel.
    """

    KIND = "color"

    def test_draws_the_flat_window_face(self):
        """Pin the window-color face crop with no other ink inside."""
        self.assert_flat_window_face(COLOR_WINDOW_FACE)

    def test_draws_the_basic_swatch_row(self):
        """Pin the grid's #000000 lead cell and its #AA0000 neighbour."""
        expected_row = [
            *["#000000"] * 18,
            *["#DDDDDD"] * 10,
            *["#AA0000"] * 18,
        ]
        self.assert_band(BASIC_SWATCH_ROW, [expected_row] * BASIC_SWATCH_ROW[3])

    def test_draws_the_sunken_value_field(self):
        """Pin the field's shadow, outline, face and window-face gap."""
        expected_row = [
            *["#DDDDDD"] * 2,
            "#999999",
            "#000000",
            *["#FFFFFF"] * 32,
            *["#DDDDDD"] * 4,
        ]
        self.assert_band(
            SUNKEN_VALUE_FIELD_BAND, [expected_row] * SUNKEN_VALUE_FIELD_BAND[3]
        )

    def test_draws_the_push_button_frame_and_cell(self):
        """Pin the raised push-button recipe over the full-height cell."""
        self.assert_push_button_recipe(
            PUSH_BUTTON, PUSH_BUTTON_CELL, PUSH_BUTTON_FLAT_ROWS
        )

    def test_draws_the_push_button_face_at_the_existing_recipe(self):
        self.assert_push_button_face_reaches_its_row(PUSH_BUTTON)


@dialog_gate_guard()
class TestIconDialogRender(DialogGate, unittest.TestCase):
    """The icon dialog's fields and push buttons are the theme's.

    The icon dialog opens kdialog's ``--geticon`` chooser, whose top-row
    search field, sunken icon-grid field and push buttons the engine
    draws with the theme's colorscheme palette entries ([Colors:Window]
    and [Colors:Button] the existing art's bevel and shadow arms serve):
    the search-field sunken recipe's shadow and outline arrangement comes
    from the shipped line-edit art, the raised push-button recipe from
    the shipped button art, the flat faces from the palette, just as the
    line-edit and color gates' field and button pins compare. The grid's
    icon cells' picture content is the fallback icon theme's art, not
    theme-owned: no pin touches an icon-art cell, so the gate fails on a
    theme change but never on a fallback-icon-set change, and the icon
    labels' glyph rows sit below every band. No collected reference
    screenshot shows an icon chooser, so the comparison values are the
    shipped art recipe and palette entries above over the measured
    480x360 geometry, re-derived on 2026-11-10 from two consecutive full
    captures: the pair differs only in the search field's blinking caret
    (a 16-pixel column at x=302 whose on/off state races the settling
    captures) and agrees everywhere else, and every band avoids that
    column. The dialog shows no clock-dependent content -- no date and no
    clock-driven selection can enter any crop -- so it needs no date or
    default pin. With only flat cells of one colour per row inside each
    band, a stray glyph row, a one-pixel crop slip, a lost shadow or
    outline row, a swapped arm colour or a resampled, recoloured or
    dropped field face fails row by row or pixel by pixel.
    """

    KIND = "icon"

    def test_draws_the_flat_window_face(self):
        """Pin the window-color face crop with no other ink inside."""
        self.assert_flat_window_face(ICON_WINDOW_FACE)

    def test_draws_the_grid_field_top_edge(self):
        """Pin the outline rule, shadow row and white face at the field's top."""
        expected_rows = [
            ["#DDDDDD"] * ICON_GRID_TOP_EDGE[2],
            ["#999999"] * ICON_GRID_TOP_EDGE[2],
            ["#000000"] * ICON_GRID_TOP_EDGE[2],
            ["#FFFFFF"] * ICON_GRID_TOP_EDGE[2],
            ["#FFFFFF"] * ICON_GRID_TOP_EDGE[2],
        ]
        self.assert_band(ICON_GRID_TOP_EDGE, expected_rows)

    def test_draws_the_search_field(self):
        """Pin the field's shadow arm, outline and white face, caret-free rows."""
        shadow_arm_row = ["#999999"] * 173 + ["#DDDDDD"]
        outline_row = ["#999999"] + ["#000000"] * 172 + ["#FFFFFF"]
        face_row = [
            "#999999",
            "#000000",
            *["#FFFFFF"] * 170,
            "#000000",
            "#FFFFFF",
        ]
        self.assert_band(
            ICON_SEARCH_FIELD_BAND,
            [shadow_arm_row, outline_row, face_row, face_row],
        )

    def test_draws_the_push_button_frame_and_cell(self):
        """Pin the raised push-button recipe over the full-height cell."""
        self.assert_push_button_recipe(
            ICON_PUSH_BUTTON, ICON_PUSH_BUTTON_CELL, ICON_PUSH_BUTTON_FLAT_ROWS
        )

    def test_draws_the_push_button_face_at_the_existing_recipe(self):
        self.assert_push_button_face_reaches_its_row(ICON_PUSH_BUTTON)


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


@dialog_gate_guard()
class TestInactiveDialogRender(DialogGate, unittest.TestCase):
    """The shipped inactive Aurorae decoration as KWin draws the unfocused window.

    The two-window ``--inactive-dialog`` capture holds one unfocused client
    (the left window, the earlier-spawned of the pair the forced-geometry
    rules place side by side) beside one focused client, and this class pins
    the left window's decoration pixels: the 1px ``#555555`` inactive outline
    ring, the active frame's black client edge recoloured to the same grey,
    the flat buttonless ``#DDDDDD`` bar and the ``#777777`` title ink. It
    complements the existing art-side pins in ``tests/test_aurorae_frame.py``
    and ``tests/test_aurorae_rc.py`` and holds no client-widget pin: the
    message-box contents stay unpinned, where the other dialog gates own
    widget pins.
    """

    KIND = "inactive"

    # The left (unfocused) window's forced frame rectangle and the inner
    # client-edge rectangle, from tools/render_window_rules.py's
    # INACTIVE_GEOMETRY (position (4, 8), size (224, 344)); the ring test
    # pins the forced placement too, since a moved or resized window no
    # longer puts the ring on these coordinates.
    LEFT_WINDOW = (4, 8, 224, 344)
    CLIENT_EDGE = (9, 29, 214, 318)  # corners (9, 29) and (222, 346)
    # The right (focused) window's forced frame rectangle and title-bar band.
    RIGHT_WINDOW = (252, 8, 224, 344)
    RIGHT_TITLE_BAND = (253, 9, 222, 20)  # rows y=9..28, x=253..474
    # The centered title "Inactive window"'s glyph band, the one region of
    # the between-rings field the text's antialiasing may bleed into.
    # Measured 2026-11-12 from the isolated render after selecting ChicagoFLF:
    # full-strength #777777 ink spans x=48..163 at y=14..23; antialiasing
    # extends to x=47..164, within this padded band.
    GLYPH_BAND = (46, 13, 120, 12)  # x=46..165, y=13..24

    def assert_ring(self, rect, colour):
        """Pin every border-ring pixel of *rect* at *colour*."""
        image = self.candidate_image()
        x0, y0, width, height = rect
        actual = {
            (x, y): hex_colour(pixel_at(image, x0 + x, y0 + y))
            for x in range(width)
            for y in range(height)
            if x in (0, width - 1) or y in (0, height - 1)
        }
        self.assertEqual(
            {(x, y): colour for (x, y) in actual},
            actual,
        )

    def test_left_window_outline_is_the_inactive_outline(self):
        # Every border pixel of the left window's forced frame rectangle
        # equals the shipped INACTIVE_OUTLINE: the recoloured inactive ring
        # (the active frame's #000000 would fail here), and the ring's
        # coordinates also pin the forced placement -- a moved or resized
        # window no longer puts the ring on these coordinates.
        self.assert_ring(self.LEFT_WINDOW, INACTIVE_OUTLINE)

    def test_left_window_client_edge_is_the_recoloured_inner_rectangle(self):
        # The ring of the client-edge rectangle equals the same
        # INACTIVE_OUTLINE: the active frame's black client edge recoloured,
        # the same derivation test_inactive_frame_matches_reference pins in
        # the art.
        self.assert_ring(self.CLIENT_EDGE, INACTIVE_OUTLINE)

    def test_left_window_field_is_the_flat_buttonless_bar(self):
        # Every pixel of the frame rect that lies neither on the outer
        # ring, nor on the inner-rectangle ring, nor strictly inside the
        # inner rectangle, nor in the title glyph band (GLYPH_BAND above,
        # with its measured-run provenance), equals the flat
        # INACTIVE_FRAME_GREY. A flattened box art, a stray active bevel
        # row or a resampling bleed in the bar fails here.
        image = self.candidate_image()
        fx, fy, fw, fh = self.LEFT_WINDOW
        ex, ey, ew, eh = self.CLIENT_EDGE
        gx, gy, gw, gh = self.GLYPH_BAND
        actual = {
            (x, y): hex_colour(pixel_at(image, fx + x, fy + y))
            for x in range(fw)
            for y in range(fh)
            if x not in (0, fw - 1)
            and y not in (0, fh - 1)
            and not (ex <= fx + x < ex + ew and ey <= fy + y < ey + eh)
            and not (gx <= fx + x < gx + gw and gy <= fy + y < gy + gh)
        }
        self.assertEqual(
            {(x, y): INACTIVE_FRAME_GREY for (x, y) in actual},
            actual,
        )

    def test_title_ink_is_the_inactive_text_colour(self):
        # The centered title carries full-strength InactiveTextColor ink
        # somewhere in its measured glyph bounds. The title font is ChicagoFLF;
        # pinning a fixed stem column would couple this check to one face's
        # glyph layout. The full antialiased glyph set is deliberately not
        # byte-compared.
        image = self.candidate_image()
        gx, gy, gw, gh = self.GLYPH_BAND
        self.assertTrue(
            any(
                hex_colour(pixel_at(image, x, y)) == "#777777"
                for x in range(gx, gx + gw)
                for y in range(gy, gy + gh)
            ),
            "the inactive title has no full-strength text ink",
        )

    def test_right_window_keeps_its_active_frame(self):
        # The right window's border ring stays the active BLACK frame, and
        # its title bar carries non-field ink: the capture must hold two
        # different states or the left-window pins prove nothing.
        self.assert_ring(self.RIGHT_WINDOW, BLACK)
        image = self.candidate_image()
        bx, by, bw, bh = self.RIGHT_TITLE_BAND
        self.assertTrue(
            any(
                hex_colour(pixel_at(image, bx + x, by + y)) != INACTIVE_FRAME_GREY
                for x in range(bw)
                for y in range(bh)
            ),
            "the right window's title bar carries no ink",
        )


if __name__ == "__main__":
    unittest.main()
