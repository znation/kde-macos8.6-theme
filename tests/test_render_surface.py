"""Tests for the headless Plasma render CLI and throwaway workflow.

``tools/render_surface.py`` parses and validates arguments, while
``tools/render_workflow.py`` runs the session through capture and publication.
``tools/render_session.py`` owns scratch-session state and KWin command building,
``tools/render_setup.py`` installs and configures its theme, and
``tools/render_clients.py`` builds the dialog client argv;
this module drives the workflow through the public CLI.
"""

from __future__ import annotations

import atexit
import errno
import os
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import process_runner
from support.aurorae_fixtures import (
    AURORAE_DIR,
    INACTIVE_FRAME_GREY,
    REFERENCE_BOUNDS,
)
from support.cli_fixtures import assert_missing_tool_named, call_main  # noqa: F401
from support.firstboot_lineedit import FIELD_BORDER_RUNS, FIELD_CORNER_PIXELS
from support.kvantum_fixtures import SVG
from support.svg_case import parse_svg
from svg_assertions import render_slices
from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    INACTIVE_OUTLINE,
    WHITE,
    hex_colour,
)
from support.reference_image import read_reference, skip_unless_materialized
from tools import (
    render_session,
    render_setup,
    render_surface,
    render_window_rules,
    render_workflow,
)  # noqa: E402
from tools.fidelity_metrics import compare, crop  # noqa: E402
from tools.png import pixel_at, read_png  # noqa: E402
from tools.png.write import encode_png  # noqa: E402

SCRIPT = str(repo_root.ROOT / "tools" / "render_surface.py")
REFERENCE = str(
    repo_root.ROOT / "macos8.6-screenshots" / "aboutsystem_betawiki.png"
)
# The retail Japanese 8.6 System Profiler window shows a zoom box; the
# aboutsystem window cannot be zoomed, so its title bar has none.
PROFILER_REFERENCE = str(
    repo_root.ROOT / "macos8.6-screenshots" / "systemprofiler_betawiki.png"
)
# The render's title bar sits at the top of the 320x240 capture (row 0 is the
# top outline, row 21 the bottom outline); the reference screenshot has the
# same chrome at y=25..46, so the strips are compared at those offsets.
CANDIDATE_CROP = (30, 0, 80, 22)
REFERENCE_CROP = (30, 25, 80, 22)
# The frame's side and bottom borders sit at the render's edges; the reference
# screenshot has the same chrome offset by its window position (left outline
# x=7, top outline y=25). The reference window is taller than the render, so
# the side strips cover only the straight run between the title bar and the
# bottom border (212 rows), and the bottom strip the border between the two
# corners (308 columns).
LEFT_BORDER_CANDIDATE = (0, 22, 6, 212)
LEFT_BORDER_REFERENCE = (7, 47, 6, 212)
RIGHT_BORDER_CANDIDATE = (314, 22, 6, 212)
RIGHT_BORDER_REFERENCE = (354, 47, 6, 212)
BOTTOM_BORDER_CANDIDATE = (6, 234, 308, 6)
BOTTOM_BORDER_REFERENCE = (13, 419, 308, 6)
# The client work area begins one row below the title bar: the frame's white
# centre tile shows for exactly that highlight row and the application's
# content face fills the next rows. The reference screenshot shows the same
# chrome offset by its window position (top outline y=25): its bottom
# title-bar rule is y=46, the white highlight row y=47 and the content face
# from y=48. The rc's unset TitleEdgeBottom default (5) let the tile paint
# rows 22-26 white and pushed the client down to row 27.
CLIENT_ROWS_CANDIDATE = (30, 22, 80, 5)
CLIENT_ROWS_REFERENCE = (30, 47, 80, 5)
# The title-bar boxes: the 13x13 close and collapse boxes and the 21x13 zoom
# canvas (its stripe-free gap plus the 13px box). The render puts the window
# at the capture's origin; aboutsystem's window is at (7, 25), so its close
# box sits at (11, 29) and its collapse box at (343, 29), while the profiler
# window's zoom canvas is at (776, 26).
CLOSE_CANDIDATE = (4, 4, 13, 13)
CLOSE_REFERENCE = (11, 29, 13, 13)
COLLAPSE_CANDIDATE = (303, 4, 13, 13)
COLLAPSE_REFERENCE = (343, 29, 13, 13)
ZOOM_CANDIDATE = (282, 4, 21, 13)
ZOOM_REFERENCE = (776, 26, 21, 13)
# The applet face gate's client-face geometry, measured on three full
# `tools/render_surface.py` runs on 2026-11-11 (every pair compared
# byte-identical, so each pinned pixel is run-stable). The client face
# spans rows 22..233 between the frame borders (x=0..5 and x=314..319,
# which the existing chrome-strip tests byte-compare); its flat face rows
# run x=6..313.
# The display field: a 1px #000000 outline box x=10..309, y=27..78 whose
# interior x=11..308, y=28..77 is flat #DDDDDD except the digit's
# font-dependent ink, confined to the measured region below (197 pixels,
# antialiased greys included, on the three-render capture).
DISPLAY_FIELD = (10, 27, 309, 78)
DISPLAY_INK_REGION = (292, 45, 305, 63)
# The keypad: five button-row bands whose outline rows are y=83/113/143/
# 174/204 (top) and y=108/138/169/199/229 (bottom). The first three bands
# carry four cells over the column spans x=10..71, 76..138, 143..204 and
# 209..309; the fourth drops the rightmost span (the tall right cell
# merges bands four and five at x=209..309, y=174..229) and the fifth
# band's leftmost cell spans x=10..138 across the first four bands' first
# gap column, so the fifth band's cells are x=10..138 and x=143..204.
# (The planned re-derivation note's three fifth-band cells over x=10..71,
# 76..138, 143..204 with ink bleeding across x=72..76 do not match the
# capture: no frame pixels sit at x=71..76 in rows 207..226, and the
# circle around x=69..79 is the wide cell's label ink.)
KEYPAD_BANDS = ((83, 108), (113, 138), (143, 169), (174, 199), (204, 229))
KEYPAD_CELLS = tuple(
    (x, y0, x1 - x + 1, y1 - y0 + 1)
    for index, (y0, y1) in enumerate(KEYPAD_BANDS)
    for x, x1 in (
        ((10, 71), (76, 138), (143, 204), (209, 309))
        if index < 3
        else ((10, 71), (76, 138), (143, 204))
        if index == 3
        else ((10, 138), (143, 204))
    )
) + ((209, 174, 101, 56),)
# The keypad cells' shared corner arcs: the outline's rounded corners
# blend the black rectangle into the face over a three-pixel arc. The
# four full-width rows each cell draws (top outline, bevel, arm, bottom
# outline) carry the arcs' blend greys at their ends; rows y+2 and
# y+height-3 hold the remaining arc greys at the cell ends, below. All
# eighteen cells draw these rows identically (re-derived on the
# three-render capture; the two fifth-band left cells' label ink stays
# clear of their corner arcs).
KEYPAD_ROW_ENDS = (
    (("#D7D7D7", "#656565", "#151515"), "#000000", ("#151515", "#656565", "#D7D7D7")),
    (("#656565", "#4C4C4C", "#E8E8E8"), "#FFFFFF", ("#E8E8E8", "#595959", "#656565")),
    (("#656565", "#595959", "#B0B0B0"), "#AAAAAA", ("#9B9B9B", "#333333", "#656565")),
    (("#D7D7D7", "#656565", "#161616"), "#000000", ("#161616", "#656565", "#D7D7D7")),
)
KEYPAD_ARC_ROWS = (
    ("#151515", "#E8E8E8", "#E4E4E4"),  # y+2 at x..x+2
    ("#E3E3E3", "#B0B0B0", "#161616"),  # y+2 at x+width-3..x+width-1
    ("#151515", "#E8E8E8", "#E2E2E2"),  # y+height-3 at x..x+2
    ("#D2D2D2", "#9B9B9B", "#161616"),  # y+height-3 at x+width-3..x+width-1
)


def _keypad_rows(width):
    """Return the four full-width rows a *width*-wide keypad cell draws."""
    return [
        [*head, *([body] * (width - 6)), *tail]
        for head, body, tail in KEYPAD_ROW_ENDS
    ]
# The dialog render's engine-drawn widget gate: `--checkbox-dialog` opens a
# kdialog warning at the headless KWin session's centre in a 480x360 capture,
# and its dontagain check box draws the theme's `checkbox-normal` art through
# `[Session] check_size`. KWin centres the session's only window in the
# virtual framebuffer, so these crops are measured on this capture size; they
# assume the session the CLI builds for `--checkbox-dialog` (the same scratch
# config home, the applied kdeglobals defaults and the Kvantum selection).
DIALOG_WIDTH = 480
DIALOG_HEIGHT = 360
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


class StubTools(unittest.TestCase):
    """Base for tests that run `main` against shell stubs of the external tools."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="render-surface-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        # Capture the real make and sleep before the stub directory goes on
        # PATH.
        self.real_make = shutil.which("make")
        self.real_sleep = shutil.which("sleep")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.scratch_parent = self.root / "tmp"
        self.scratch_parent.mkdir()
        self.stub("make", "exit 0")
        for name in render_surface.REQUIRED_TOOLS:
            if name != "make":
                self.stub(name, "exit 0")
        path = f"{self.bin}{os.pathsep}{os.environ['PATH']}"
        patches = (
            mock.patch.dict(os.environ, {"PATH": path}),
            mock.patch.object(tempfile, "tempdir", str(self.scratch_parent)),
            # These tests pin render and capture failure paths, not package
            # discovery; the applet preflight's XDG-root search is pinned off
            # so the runs stay host-independent.
            mock.patch.object(render_surface, "applet_problem", return_value=None),
        )
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def stub(self, name, body):
        """Write an executable stub named *name* that runs *body*."""
        path = self.bin / name
        path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def assert_scratch_removed(self):
        """Assert the scratch parent holds no leftover entries."""
        self.assertEqual([], os.listdir(self.scratch_parent))

    def assert_failed_run(self, status, stderr, output, expected_status, *diagnostics):
        """Assert a failed render's whole exit contract: the named exit
        status with only its own diagnostics on stderr (no traceback), no
        rendered output published and no leftover scratch session.

        Shared by the 18 failure-path tails in :class:`TestFailurePaths`.
        """
        self.assertEqual(expected_status, status)
        for diagnostic in diagnostics:
            self.assertIn(diagnostic, stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertFalse(output.exists())
        self.assert_scratch_removed()


class TestMissingTool(unittest.TestCase):
    def test_names_the_first_missing_tool_and_exits_2(self):
        with tempfile.TemporaryDirectory() as empty:
            with mock.patch.dict(os.environ, {"PATH": empty}):
                status, stderr = call_main(render_surface.main, "out.png")
        self.assertEqual(2, status)
        self.assertIn(render_surface.REQUIRED_TOOLS[0], stderr)
        self.assertIn("render_surface: error:", stderr)

    def test_applet_id_with_nul_is_rejected_as_usage_error(self):
        with tempfile.TemporaryDirectory() as empty:
            with mock.patch.dict(os.environ, {"PATH": empty}):
                status, stderr = call_main(
                    render_surface.main, "out.png", "--applet", "org.example\0widget"
                )
        self.assertEqual(2, status)
        self.assertIn("--applet must be a plasmoid id without NUL", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_a_single_missing_tool_is_the_one_named(self):
        assert_missing_tool_named(
            self, render_surface.main, render_surface.REQUIRED_TOOLS, ("out.png",)
        )


def crashed_applet_setup_diagnosis(setup_timeout):
    """Return the fail message the crashed-applet fixture builds on expiry.

    Shared by the crashed-applet test and the offline reproduction of its
    expired-wait diagnosis, so both name the recorded wait instead of a bare
    status mismatch.
    """
    return (
        "the crashed applet's setup did not "
        f"{setup_timeout.read_text().strip()} within the polling "
        "budget; the settle stub must start and reap it before the "
        "session's liveness check"
    )


class TestFailurePaths(StubTools):
    def run_main(self, *extra):
        """Run ``main`` on ``out.png`` with *extra* and return status, stderr, output."""
        output = self.root / "out.png"
        status, stderr = call_main(render_surface.main, str(output), *extra)
        return status, stderr, output

    def assert_unrunnable_command_is_reported(self, command, diagnostic):
        """Check the CLI handles a found executable that cannot be started."""
        executable = self.bin / command
        executable.write_text("#!/nonexistent/interpreter\n", encoding="utf-8")
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)

        # Keep execvp from falling through to a real command after ENOENT.
        with mock.patch.dict(os.environ, {"PATH": str(self.bin)}):
            status, stderr, output = self.run_main()

        self.assert_failed_run(status, stderr, output, 2, diagnostic)

    def test_menu_dialog_launches_its_kdialog_menu_client(self):
        # The menu mode must reach the session as a KDialog menu client (and
        # therefore apply the dialog's Kvantum configuration path), not fall
        # through to the default Plasma calculator applet.
        with mock.patch.object(render_workflow, "run_logged", return_value=1) as run, \
                mock.patch.object(render_workflow, "write_session_configs") as configs, \
                mock.patch.object(render_workflow, "write_kvantum_selection") as selection:
            status, stderr, output = self.run_main("--menu-dialog")

        # The menu mode takes the dialog path: the dialog's config files (the
        # global theme's kdeglobals) and the Kvantum selection, not the
        # applet render's session-only set. The rendered siblings pin this
        # path too, but only for the checkbox and combobox modes.
        self.assertEqual(
            render_setup.CONFIG_FILES + ("kdeglobals",),
            configs.call_args.kwargs["files"],
        )
        selection.assert_called_once_with(configs.call_args.args[0])
        argv = run.call_args.args[0]
        self.assertIn("kdialog", argv[-1])
        self.assertIn("--menu", argv[-1])
        self.assertIn("Alpha", argv[-1])
        self.assertNotIn("org.kde.plasma.calculator", argv[-1])
        self.assert_failed_run(
            status, stderr, output, 1, "render session exited 1",
        )

    def test_inactive_dialog_launches_its_two_window_wrapper(self):
        # The inactive mode must reach the session as the two-window sh -c
        # wrapper (one kdialog per fixed title, opened inactive-window
        # first), not fall through to the default Plasma calculator applet.
        # Its session also writes the forced-geometry rules the two titles
        # are matched by, beside the dialog's Kvantum selection.
        with mock.patch.object(render_workflow, "run_logged", return_value=1) as run, \
                mock.patch.object(render_workflow, "write_session_configs") as configs, \
                mock.patch.object(render_workflow, "write_kvantum_selection") as selection, \
                mock.patch.object(render_workflow, "write_window_rules") as rules:
            status, stderr, output = self.run_main("--inactive-dialog")

        self.assertEqual(
            render_setup.CONFIG_FILES + ("kdeglobals",),
            configs.call_args.kwargs["files"],
        )
        selection.assert_called_once_with(configs.call_args.args[0])
        rules.assert_called_once_with(configs.call_args.args[0])
        argv = run.call_args.args[0]
        self.assertIn("kdialog", argv[-1])
        self.assertIn(render_window_rules.INACTIVE_TITLE, argv[-1])
        self.assertIn(render_window_rules.FOCUSED_TITLE, argv[-1])
        self.assertNotIn("org.kde.plasma.calculator", argv[-1])
        self.assert_failed_run(
            status, stderr, output, 1, "render session exited 1",
        )

    def test_desktop_render_launches_the_plasmashell_client(self):
        # The desktop mode must reach the session as plasmashell (the shell
        # draws the menu bar itself), with the look-and-feel selection
        # written beside the session configs, not fall through to the
        # default Plasma calculator applet or a dialog client.
        with mock.patch.object(render_workflow, "run_logged", return_value=1) as run, \
                mock.patch.object(render_workflow, "write_session_configs") as configs, \
                mock.patch.object(render_workflow, "write_desktop_selection") as selection:
            status, stderr, output = self.run_main("--desktop")

        self.assertEqual(
            render_setup.CONFIG_FILES + ("kdeglobals",),
            configs.call_args.kwargs["files"],
        )
        selection.assert_called_once_with(configs.call_args.args[0])
        argv = run.call_args.args[0]
        self.assertIn("plasmashell", argv[-1])
        self.assertNotIn("org.kde.plasma.calculator", argv[-1])
        self.assertNotIn("plasmawindowed", argv[-1])
        self.assertNotIn("kdialog", argv[-1])
        self.assert_failed_run(
            status, stderr, output, 1, "render session exited 1",
        )

    def test_splash_render_launches_the_ksplashqml_client(self):
        # The splash mode must reach the session as ksplashqml pointing at
        # the session-local installed look-and-feel package (the splash
        # paints its own Splash.qml from the scratch data home, never the
        # caller's), writing only the applet's session configs: the splash
        # reads no selection, so no look-and-feel, Kvantum, GTK or window
        # rules write may ride the session.
        with mock.patch.object(render_workflow, "run_logged", return_value=1) as run, \
                mock.patch.object(render_workflow, "write_session_configs") as configs, \
                mock.patch.object(render_workflow, "write_desktop_selection") as look, \
                mock.patch.object(render_workflow, "write_kvantum_selection") as kvantum, \
                mock.patch.object(render_workflow, "write_window_rules") as rules, \
                mock.patch.object(render_workflow, "install_gtk_selection") as gtk:
            status, stderr, output = self.run_main("--splash")

        self.assertEqual(render_setup.CONFIG_FILES, configs.call_args.kwargs["files"])
        look.assert_not_called()
        kvantum.assert_not_called()
        rules.assert_not_called()
        gtk.assert_not_called()
        argv = run.call_args.args[0]
        self.assertIn("ksplashqml", argv[-1])
        self.assertIn("--nofork", argv[-1])
        self.assertIn(
            "plasma/look-and-feel/org.macos8.desktop", argv[-1]
        )
        self.assertNotIn("org.kde.plasma.calculator", argv[-1])
        self.assertNotIn("plasmawindowed", argv[-1])
        self.assertNotIn("kdialog", argv[-1])
        self.assert_failed_run(
            status, stderr, output, 1, "render session exited 1",
        )

    def test_only_the_inactive_dialog_writes_the_window_rules(self):
        # The two-window forced-geometry rules are the inactive mode's own
        # session config: no applet render and no one-window dialog render
        # may write a kwinrulesrc the other sessions never asked for.
        self.stub("kdialog", "exit 0")
        with mock.patch.object(
            render_workflow, "write_window_rules"
        ) as rules, mock.patch.object(
            render_workflow, "run_logged", return_value=1
        ):
            for extra in ((), ("--checkbox-dialog",)):
                with self.subTest(extra=extra):
                    status, _, _ = self.run_main(*extra)
                    self.assertEqual(1, status)
                    rules.assert_not_called()
            status, _, _ = self.run_main("--inactive-dialog")
            self.assertEqual(1, status)

        rules.assert_called_once()
        self.assert_scratch_removed()

    def test_only_dialog_renders_add_kdeglobals_to_the_session_configs(self):
        # Dialog clients are Qt applications, so the scratch session must
        # apply the global theme defaults that select Kvantum. The applet
        # render deliberately writes only the window-decoration configs.
        self.stub("kdialog", "exit 0")
        with mock.patch.object(
            render_workflow, "write_session_configs"
        ) as write_configs, mock.patch.object(
            render_workflow, "run_logged", return_value=1
        ):
            status, _, _ = self.run_main()
            self.assertEqual(1, status)
            applet_files = write_configs.call_args.kwargs["files"]

            status, _, _ = self.run_main("--checkbox-dialog")
            self.assertEqual(1, status)
            dialog_files = write_configs.call_args.kwargs["files"]

        self.assertEqual(("kwinrc", "plasmarc"), applet_files)
        self.assertEqual(
            ("kwinrc", "plasmarc", "kdeglobals"), dialog_files
        )
        self.assert_scratch_removed()

    def test_gtk_dialog_installs_the_gtk_selection_beside_the_kvatum_one(self):
        # The GTK mode's zenity client wears the theme through the selection
        # the workflow publishes into the scratch config home, so the GTK
        # selection install must run beside the Kvantum one, not be
        # forgotten the way a fourth copy of the fan-out could omit it.
        self.stub("zenity", "exit 0")
        with mock.patch.object(
            render_workflow, "install_gtk_selection"
        ) as install, mock.patch.object(
            render_workflow, "write_kvantum_selection"
        ) as kvantum, mock.patch.object(
            render_workflow, "run_logged", return_value=1
        ):
            status, stderr, output = self.run_main("--gtk-dialog")

        self.assert_failed_run(status, stderr, output, 1)
        install.assert_called_once()
        kvantum.assert_called_once()

    def test_a_failed_gtk_selection_install_exits_1_and_removes_scratch(self):
        self.stub("zenity", "exit 0")
        with mock.patch.object(
            render_workflow,
            "install_gtk_selection",
            side_effect=render_setup._ConfigError("sheet is missing"),
        ) as install, mock.patch.object(
            render_workflow, "run_logged", return_value=0
        ):
            status, stderr, output = self.run_main("--gtk-dialog")

        self.assert_failed_run(
            status,
            stderr,
            output,
            1,
            "cannot install the GTK selection",
            "sheet is missing",
        )
        install.assert_called_once()

    def test_unusable_scratch_directory_exits_2_without_a_traceback(self):
        # The scratch session is created before the install starts. Creating it
        # can fail (a full or unwritable TMPDIR) before there is anything to
        # clean up; it must be this tool's own exit-2 diagnostic, not a
        # traceback that skips the exit contract.
        with mock.patch.object(
            tempfile, "mkdtemp", side_effect=OSError("no space left")
        ):
            status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 2,
            "cannot create a scratch session directory", "no space left",
        )

    def test_failed_install_exits_1_and_removes_scratch(self):
        self.stub("make", "echo install exploded; exit 4")
        status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1,
            "make install exited 4", "install exploded",
        )

    def test_an_unrunnable_make_exits_2_and_removes_scratch(self):
        # `which` still finds an executable script whose interpreter is gone,
        # so the missing-tool check passes and Popen raises OSError. The tool
        # must report that itself instead of letting the OSError traceback.
        self.assert_unrunnable_command_is_reported(
            "make", "render_surface: error: cannot run make:"
        )

    def test_an_unrunnable_session_launcher_exits_2_and_removes_scratch(self):
        # Same fault as the make test, at the second command the tool starts
        # itself: `shutil.which` finds dbus-run-session, but Popen raises
        # OSError. It must be the tool's own exit-2 diagnostic, not a
        # traceback that skips the scratch cleanup.
        self.assert_unrunnable_command_is_reported(
            "dbus-run-session", "render_surface: error: cannot run dbus-run-session:"
        )

    def test_a_failed_session_config_write_exits_1_with_a_diagnostic(self):
        # The session config is derived from the shipped defaults and written
        # into the scratch config home. A write that fails there (a full disk),
        # a defaults file that cannot be decoded, or a malformed section
        # heading the reader rejects must become the tool's own diagnostic and
        # exit 1, not a traceback that bypasses the documented exit status.
        def die(config_home, names):
            raise failure

        for label, failure in (
            ("a full disk", OSError(errno.ENOSPC, "No space left on device")),
            (
                "a non-UTF-8 defaults file",
                UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"),
            ),
            (
                "a malformed defaults heading",
                ValueError("malformed section heading '[a][b] # note'"),
            ),
        ):
            with self.subTest(label):
                with mock.patch.object(render_setup, "write_configs", die):
                    status, stderr, output = self.run_main()
                self.assert_failed_run(
                    status, stderr, output, 1,
                    "render_surface: error:", "session config",
                )

    def test_a_failed_themes_link_exits_2_and_removes_scratch(self):
        # The scratch home's themes link is made after `make install`, at the
        # one place the engine's literal `$HOME/.local/share/themes/` search
        # path is satisfied. When the link cannot be made (an entry raced in
        # at the link name), the tool must report its own exit-2 diagnostic
        # naming the path, not a traceback that skips the scratch cleanup.
        themes = self.root / "themes"
        problem = OSError(errno.EEXIST, "File exists")

        def die(session):
            return problem, themes

        with mock.patch.object(render_workflow, "link_kvantum_themes", die):
            status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 2,
            "render_surface: error: cannot link",
            str(themes), "File exists",
        )

    def test_a_failed_kvantum_selection_write_exits_1_and_removes_scratch(self):
        # A dialog render selects the Kvantum theme in the scratch config
        # home before the session starts; without the name the engine falls
        # back to its compiled-in default and the gate would silently compare
        # the wrong theme's pixels. A selection write that fails there (a
        # full disk) must become the tool's own exit-1 diagnostic, not a
        # traceback that skips the scratch cleanup or a render that goes out
        # carrying an unthemed widget.
        def die(session):
            raise OSError(errno.ENOSPC, "No space left on device")

        with mock.patch.object(render_workflow, "write_kvantum_selection", die):
            status, stderr, output = self.run_main("--menu-dialog")
        self.assert_failed_run(
            status, stderr, output, 1,
            "render_surface: error:",
            "cannot write the Kvantum selection",
            "No space left on device",
        )

    def test_install_timeout_exits_1_with_a_timeout_diagnostic(self):
        # A hung `make install` is killed by run_logged, which reports the
        # timeout as None. The diagnostic must name the timeout rather than
        # the raw status ("exited None"), and the failure must still exit 1
        # and remove the scratch root. The real install timeout is minutes
        # long, so run_logged is stubbed instead of waited out; the render
        # session's own timeout is covered by
        # test_timeout_kills_the_session_group_and_exits_1.
        with mock.patch.object(render_setup, "run_logged", return_value=None):
            status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1, "make install timed out",
        )

    def test_failed_session_exits_1_and_removes_scratch(self):
        self.stub("dbus-run-session", "echo no display; exit 3")
        status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1,
            "render session exited 3", "no display",
        )

    def test_session_without_a_capture_exits_1(self):
        status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1, "not a readable PNG",
        )

    def stub_live_session(self, plasmawindowed_body):
        """Run the real session script under stubs of the tools it starts.

        The fake launcher evaluates the script ``render_surface`` hands the
        session, so the applet liveness check is the tool's own script and not
        a test double. ``spectacle`` writes a valid capture whenever the script
        reaches it, which is what makes a silently crashed applet observable.
        """
        fixture = self.root / "session-capture.png"
        fixture.write_bytes(
            encode_png(320, 240, bytes([0xDD]) * (320 * 240 * 3))
        )
        self.stub("plasmawindowed", plasmawindowed_body)
        self.stub(
            "spectacle",
            'out=; while [ "$#" -gt 0 ]; do '
            'if [ "$1" = -o ]; then shift; out=$1; fi; shift; done; '
            f'cp "{fixture}" "$out"',
        )
        self.stub("dbus-run-session", 'for script; do :; done; eval "$script"')

    def test_a_running_applet_is_still_captured(self):
        self.stub_live_session("exec sleep 60")
        status, stderr, output = self.run_main("--settle", "0")
        self.assertEqual((0, ""), (status, stderr))
        self.assertTrue(output.exists())
        self.assert_scratch_removed()

    def test_a_crashed_applet_is_not_captured_as_a_successful_render(self):
        # plasmawindowed is backgrounded, so its failure is otherwise invisible;
        # spectacle would capture the empty session and the tool would publish
        # that PNG as a successful render. The settle stub returns only once
        # the crashed applet has been started and reaped, so the liveness check
        # cannot race the background process's exit. A slow host can delay that
        # setup past the polling budget; the stub then records which wait
        # expired, so the test names the setup race instead of failing as a
        # bare status mismatch against a render of a still-starting applet.
        pidfile = self.root / "applet.pid"
        setup_timeout = self.root / "setup-timeout"
        self.stub_live_session(f"echo $$ > {shlex.quote(str(pidfile))}; exit 1")
        self.stub(
            "sleep",
            f"pidfile={shlex.quote(str(pidfile))}; "
            f"timeout={shlex.quote(str(setup_timeout))}; "
            f"pause={shlex.quote(self.real_sleep)}; "
            'n=0; while [ ! -s "$pidfile" ]; do n=$((n + 1)); '
            '[ "$n" -gt 1500 ] && { echo start > "$timeout"; exit 1; }; '
            '"$pause" 0.02; done; '
            'pid=$(cat "$pidfile"); n=0; '
            'while kill -0 "$pid" 2>/dev/null; do n=$((n + 1)); '
            '[ "$n" -gt 1500 ] && { echo reap > "$timeout"; exit 1; }; '
            '"$pause" 0.02; done',
        )
        status, stderr, output = self.run_main("--settle", "0")
        if setup_timeout.exists():
            self.fail(crashed_applet_setup_diagnosis(setup_timeout))
        self.assert_failed_run(
            status, stderr, output, 1,
            "render session exited 1", "plasmawindowed exited before the capture",
        )

    def test_an_expired_setup_wait_is_reported_by_name_not_as_a_status_mismatch(self):
        # The offline reproduction of the crashed-applet fixture's expired
        # setup wait (the archived slow-check record): a stubbed session whose
        # applet start passes inside the widened 1500-iteration bound, and
        # whose recorded `setup-timeout` file then names the expired wait, so
        # the shipped diagnosis branch fires and reports the wait by name
        # before any status assertion. The stub forces the file's content
        # instead of spending the real 1500-iteration 0.02 s poll -- the
        # ledger requires the failure diagnosis to be reproduced offline,
        # not the wall clock -- and it reaps the applet first, so the
        # session's own liveness check still fails the render deterministically.
        pidfile = self.root / "applet.pid"
        setup_timeout = self.root / "setup-timeout"
        self.stub_live_session(f"echo $$ > {shlex.quote(str(pidfile))}; exit 1")
        self.stub(
            "sleep",
            f"pidfile={shlex.quote(str(pidfile))}; "
            f"timeout={shlex.quote(str(setup_timeout))}; "
            f"pause={shlex.quote(self.real_sleep)}; "
            'n=0; while [ ! -s "$pidfile" ]; do n=$((n + 1)); '
            '[ "$n" -gt 1500 ] && exit 1; "$pause" 0.02; done; '
            'pid=$(cat "$pidfile"); n=0; '
            'while kill -0 "$pid" 2>/dev/null; do n=$((n + 1)); '
            '[ "$n" -gt 1500 ] && exit 1; "$pause" 0.02; done; '
            # Forced: name the expired start wait, then fail the settle
            # exactly as the shipped stub's expired branch does.
            'echo start > "$timeout"; exit 1',
        )
        status, stderr, output = self.run_main("--settle", "0")
        self.assert_failed_run(
            status, stderr, output, 1,
            "render session exited 1", "plasmawindowed exited before the capture",
        )
        # The forced record names the expired wait, and the diagnosis the
        # shipped crashed-applet fixture builds from it names that wait and
        # its polling budget -- never a bare status mismatch.
        self.assertEqual("start", setup_timeout.read_text().strip())
        diagnosis = crashed_applet_setup_diagnosis(setup_timeout)
        self.assertIn("start", diagnosis)
        self.assertIn("within the polling budget", diagnosis)

    def test_a_failing_capture_session_exits_1_writes_no_output_and_removes_scratch(self):
        # A live applet can sit inside a session whose capture command fails
        # -- spectacle without a usable compositor, an unwritable surface
        # path -- so the liveness check passes and the script reaches `exit
        # $status` with the capture command's own non-zero status. Keeping
        # the client alive pins that arm: the session must exit with the
        # capture's status and not call it a success, and the tool must
        # treat it exactly like any other failed session -- the failure and
        # the capture stub's word on stderr replayed, nothing published,
        # scratch removed.
        self.stub_live_session("exec sleep 60")
        self.stub("spectacle", "echo capture shot down >&2; exit 7")
        status, stderr, output = self.run_main("--settle", "0")
        self.assert_failed_run(
            status, stderr, output, 1,
            "render session exited 7", "capture shot down",
        )

    def test_a_capture_of_the_wrong_size_exits_1_and_writes_nothing(self):
        # spectacle can hand back a surface captured at the wrong geometry. The
        # render must refuse it: publishing that PNG would report success for a
        # size the fidelity comparison never asked to check.
        self.stub_capture()
        status, stderr, output = self.run_main("--width", "64", "--height", "48")
        self.assert_failed_run(
            status, stderr, output, 1,
            "capture is 320x240, expected 64x48",
        )

    def test_an_unpainted_capture_exits_1_and_writes_nothing(self):
        # A virtual session that has not painted presents an all-black screen.
        # The render used to publish that correctly sized PNG as a success,
        # which surfaced later as unexplained pixel mismatches. It must fail
        # here, naming the paint budget, instead of publishing a render of
        # nothing.
        self.stub_capture(fill=0x00)
        status, stderr, output = self.run_main()
        self.assert_failed_run(
            status, stderr, output, 1,
            "capture is entirely black", "did not paint", "8s settle",
        )

    def test_unwritable_output_is_refused_before_installing(self):
        marker = self.root / "make-ran"
        self.stub("make", f"touch {marker}")
        for label, output in (
            ("a directory", self.root),
            ("an empty path", Path("")),
            ("a missing directory", self.root / "missing" / "out.png"),
        ):
            with self.subTest(label):
                status, stderr = call_main(render_surface.main, str(output))
                self.assertEqual(2, status)
                self.assertIn("render_surface: error: cannot write", stderr)
                self.assertFalse(marker.exists())
                self.assert_scratch_removed()

    def test_a_read_only_output_directory_is_refused_before_installing(self):
        # The last branch of `tools/render_output.py`'s `output_problem`: the
        # directory exists but this
        # user may not write it. `os.access` is the only check that sees that,
        # and a refusal here keeps the failure a named diagnostic instead of
        # letting the copy fail later with an errno the operator has to read
        # out of a traceback.
        marker = self.root / "make-ran"
        self.stub("make", f"touch {marker}")
        locked = self.root / "locked"
        locked.mkdir()
        locked.chmod(0o500)
        self.addCleanup(locked.chmod, 0o700)
        if os.access(locked, os.W_OK):
            self.skipTest("directory permissions are not enforced for this user")
        status, stderr = call_main(render_surface.main, str(locked / "out.png"))
        self.assertEqual(2, status)
        self.assertIn("render_surface: error: cannot write", stderr)
        self.assertIn("its directory is not writable", stderr)
        self.assertFalse(marker.exists())
        self.assert_scratch_removed()

    def hidden_files(self):
        """Return the dot-prefixed entries left in the scratch root."""
        return [name for name in os.listdir(self.root) if name.startswith(".")]

    def stub_capture(self, fill=0xDD):
        """Make the stubbed session write a valid 320x240 PNG where spectacle would.

        *fill* is the byte every colour channel holds; the default is the
        theme's painted window face, while 0 gives the all-black surface of a
        session that has not painted yet.
        """
        fixture = self.root / "capture.png"
        fixture.write_bytes(
            encode_png(320, 240, bytes([fill]) * (320 * 240 * 3))
        )
        # The session's argv ends with the shlex-joined `sh -c` line whose
        # positional parameters are the settle seconds, the surface path and
        # then the client: the capture stub extracts the surface path between
        # them, so the fixture lands where spectacle would have written it.
        self.stub(
            "dbus-run-session",
            'for a; do :; done; '
            "dest=$(printf '%s\\n' \"$a\" | sed -n "
            "'s/.* sh [^ ]* \\([^ ]*\\) plasmawindowed.*/\\1/p'); "
            f'cp "{fixture}" "$dest"',
        )
        return fixture

    def test_a_capture_is_copied_to_the_output(self):
        fixture = self.stub_capture()
        status, stderr, output = self.run_main()
        self.assertEqual((0, ""), (status, stderr))
        self.assertEqual(fixture.read_bytes(), output.read_bytes())
        self.assertEqual([], self.hidden_files())

    def test_a_failed_copy_keeps_the_previous_output_and_leaves_no_partial_file(self):
        self.stub_capture()
        output = self.root / "out.png"
        output.write_bytes(b"previous good render")

        def die_midway(src, dst):
            dst.write(b"half a PNG")
            raise OSError(errno.ENOSPC, "No space left on device")

        with mock.patch.object(shutil, "copyfileobj", die_midway):
            status, stderr = call_main(render_surface.main, str(output))
        self.assertEqual(1, status)
        self.assertIn("cannot write", stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(b"previous good render", output.read_bytes())
        self.assertEqual([], self.hidden_files())
        self.assert_scratch_removed()

    def test_a_fifo_refusal_is_reported_as_a_failed_render(self):
        # The open guard refuses a non-regular capture source with ValueError,
        # not OSError; the CLI must still report it as a failed render with
        # its own diagnostic instead of tracebacking out of the exit contract.
        self.stub_capture()
        output = self.root / "out.png"
        output.write_bytes(b"previous good render")

        with mock.patch.object(
            render_workflow,
            "publish",
            side_effect=ValueError(
                f"{self.root / 'surface.png'} cannot be read: "
                "not a regular file; refusing to open it"
            ),
        ):
            status, stderr = call_main(render_surface.main, str(output))
        self.assertEqual(1, status)
        self.assertIn("cannot write", stderr)
        self.assertIn("not a regular file", stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(b"previous good render", output.read_bytes())
        self.assertEqual([], self.hidden_files())
        self.assert_scratch_removed()

    def test_make_render_passes_a_dash_leading_output_as_a_path(self):
        real_path = os.pathsep.join(
            entry
            for entry in os.environ["PATH"].split(os.pathsep)
            if entry != str(self.bin)
        )
        result = subprocess.run(
            ["make", "-n", "render", "RENDER_OUTPUT=-x.png"],
            cwd=repo_root.ROOT,
            env={**os.environ, "PATH": real_path},
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertIn('render_surface.py "$@" -- "-x.png"', result.stdout)

    def test_session_receives_the_geometry_and_the_themed_configs(self):
        record = self.root / "args"
        self.stub(
            "dbus-run-session",
            f'echo "$@" > "{record}"; cat "$XDG_CONFIG_HOME/kwinrc" >> "{record}";'
            f' echo "$XDG_DATA_HOME $WAYLAND_DISPLAY $DISPLAY" >> "{record}"',
        )
        with mock.patch.dict(os.environ, {"WAYLAND_DISPLAY": "wl", "DISPLAY": ":9"}):
            self.run_main("--width", "64", "--height", "48", "--applet", "a b")
        text = record.read_text(encoding="utf-8")
        self.assertIn("--width 64 --height 48", text)
        self.assertIn("--socket render-surface", text)
        self.assertIn("theme=org.macos8.desktop", text)
        self.assertIn("--exit-with-session", text)
        last = text.splitlines()[-1].split()
        self.assertTrue(Path(last[0]).parent.name.startswith("render-surface-"))
        self.assertEqual(
            ["render-surface"],
            last[1:],
            "the session did not get its own socket, or DISPLAY leaked",
        )

    def test_session_ignores_a_config_search_path_from_the_environment(self):
        # `plasma-apply-colorscheme` and the session resolve config through
        # XDG_CONFIG_DIRS as well as XDG_CONFIG_HOME, so a caller-set search
        # path would let the host session's kdeglobals/kwinrc leak into a
        # render that is supposed to run against the throwaway config home
        # only. The render must drop it like it drops the caller's
        # WAYLAND_DISPLAY/DISPLAY.
        record = self.root / "config-dirs"
        self.stub(
            "dbus-run-session",
            f'printf "%s" "$XDG_CONFIG_DIRS" > "{record}"',
        )
        with mock.patch.dict(
            os.environ, {"XDG_CONFIG_DIRS": str(self.root / "ambient")}
        ):
            self.run_main()
        self.assertEqual(
            "",
            record.read_text(encoding="utf-8"),
            "the caller's XDG_CONFIG_DIRS leaked into the render session",
        )

    def test_session_pins_the_nested_bus_to_a_display_free_qt_platform(self):
        # The private bus hands the session environment to every service it
        # D-Bus-activates. A GUI service activated while WAYLAND_DISPLAY
        # points at the nested KWin socket (not yet listening, or gone
        # because the nested KWin exited) aborts in QGuiApplication and the
        # bus re-activates it in a coredump loop. The session therefore pins
        # the whole bus subtree to a display-free Qt platform, overriding a
        # caller's ambient value, and only the session script (the clients
        # that must draw on the nested compositor) sets wayland back.
        record = self.root / "qt-platform"
        self.stub(
            "dbus-run-session",
            f'printf "%s" "$QT_QPA_PLATFORM" > "{record}"',
        )
        with mock.patch.dict(
            os.environ, {"QT_QPA_PLATFORM": "wayland"}
        ):
            self.run_main()
        self.assertEqual(
            "offscreen",
            record.read_text(encoding="utf-8"),
            "the caller's QT_QPA_PLATFORM leaked into the render session, or the "
            "activated services were left free to open the nested Wayland socket",
        )

    def test_session_script_keeps_the_clients_on_the_nested_compositor_platform(self):
        # The nested bus's display-free QT_QPA_PLATFORM applies to the
        # session script too, so the script itself must re-pin the clients to
        # the nested compositor's wayland socket: without the override a
        # client would never align its platform with the wayland socket the
        # script's own comment says it needs.
        script = render_session.session_script()
        self.assertIn(
            "export QT_QPA_PLATFORM=wayland; ",
            script,
            "the session script no longer re-pins the client to the nested "
            "compositor's wayland platform, while the session subtree is pinned "
            "to a display-free one",
        )

    def test_install_ignores_a_destdir_from_the_environment(self):
        record = self.root / "make-env"
        self.stub("make", f'echo "[$DESTDIR] $*" > "{record}"')
        with mock.patch.dict(os.environ, {"DESTDIR": str(self.root / "stage")}):
            self.run_main()
        argv = record.read_text(encoding="utf-8")
        self.assertTrue(argv.startswith("[] install XDG_DATA_HOME="), argv)

    def test_install_ignores_makefiles_from_the_environment(self):
        marker = self.root / "makefiles-executed"
        injected_makefile = self.root / "injected.mk"
        injected_makefile.write_text(
            f"$(shell touch '{marker}')\n", encoding="utf-8"
        )
        self.stub("make", f'exec "{self.real_make}" "$@"')
        with mock.patch.dict(os.environ, {"MAKEFILES": str(injected_makefile)}):
            self.run_main()
        self.assertFalse(
            marker.exists(), "caller-controlled MAKEFILES ran during the render install"
        )

    def test_install_ignores_a_destdir_from_the_outer_make_command_line(self):
        # `make DESTDIR=/stage render` exports the command-line variable through
        # MAKEFLAGS as well as the environment, so dropping DESTDIR alone leaves
        # the inner `make install` staging the theme outside the scratch home.
        # Run the real make so it imports MAKEFLAGS the way the outer one would.
        record = self.root / "make-destdir"
        makefile = self.root / "install.mk"
        makefile.write_text(
            f'install:\n\t@echo "[$(DESTDIR)]" > "{record}"\n', encoding="utf-8"
        )
        self.stub("make", f'exec "{self.real_make}" -f "{makefile}" "$@"')
        with mock.patch.dict(
            os.environ, {"MAKEFLAGS": f"-- DESTDIR={self.root / 'stage'}"}
        ):
            self.run_main()
        self.assertEqual("[]", record.read_text(encoding="utf-8").strip())

    def test_timeout_kills_the_session_group_and_exits_1(self):
        # The session must write its pid before the one-second timeout fires,
        # or the timeout kills it first and the read below has nothing to
        # check. A loaded host can lose that race, so retry with a fresh
        # pidfile per attempt; each timed-out attempt has already had its
        # whole group killed by run_logged, so retrying leaks nothing. The
        # deadline bounds the retries, so a host that never starts the session
        # fails instead of spinning.
        started = time.monotonic()
        deadline = started + 30
        while True:
            self.assertLess(
                time.monotonic(),
                deadline,
                "the session never wrote its pid before the timeout",
            )
            pidfile = self.root / f"pid-{time.monotonic_ns()}"
            self.stub(
                "dbus-run-session", f'echo $$ > "{pidfile}"; exec sleep 60'
            )
            status, stderr, output = self.run_main(
                "--settle", "0", "--timeout", "1"
            )
            self.assert_failed_run(
                status, stderr, output, 1, "render timed out after 1s",
            )
            try:
                pid = int(pidfile.read_text(encoding="utf-8"))
            except (FileNotFoundError, ValueError):
                # The timeout fired before the session finished its setup, so
                # this attempt proved nothing about the group kill.
                continue
            break
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)

    def test_sigterm_kills_the_session_group_and_removes_scratch(self):
        pidfile = self.root / "pid"
        self.stub("dbus-run-session", f'echo $$ > "{pidfile}"; exec sleep 60')
        env = dict(os.environ, TMPDIR=str(self.scratch_parent))
        argv = [sys.executable, render_surface.__file__, str(self.root / "o.png")]
        with process_runner.running(
            argv, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ) as process:
            pid = process_runner.wait_for_pidfile(
                self, process, pidfile, tool="render", child="session"
            )
            process.send_signal(signal.SIGTERM)
            process_runner.finish(process)
        self.assertEqual(128 + signal.SIGTERM, process.returncode)
        self.assert_scratch_removed()
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)


REAL_TOOLS = ("kwin_wayland", "dbus-run-session", "plasmawindowed", "spectacle",
              "plasma-apply-colorscheme")
# The dialog clients the dialog modes open, beside the applet render tools.
# One literal feeds the gates' skip guard and the guard pins below, so an
# edit to either the CLI's requirement list or this list cannot drift the
# skip condition away from the condition the render CLI refuses on: each
# dialog flag requires its own client by name (kdialog for the thirteen kdialog
# modes, zenity for the GTK mode), and the gates skip when either client
# or any Plasma tool is absent.
DIALOG_REAL_TOOLS = REAL_TOOLS + ("kdialog", "zenity")
# The desktop mode's client, beside the applet render tools: the same set the
# CLI's desktop preflight requires (render_surface.py joins "plasmashell"
# onto its requirements for --desktop). One literal feeds the desktop gate's
# skip guard, as DIALOG_REAL_TOOLS feeds the dialog gates'.
DESKTOP_REAL_TOOLS = REAL_TOOLS + ("plasmashell",)
# The splash mode's client, beside the applet render tools: the same set the
# CLI's splash preflight requires (render_surface.py joins "ksplashqml"
# onto its requirements for --splash). One literal feeds the splash gate's
# skip guard, as DESKTOP_REAL_TOOLS feeds the desktop gate's.
SPLASH_REAL_TOOLS = REAL_TOOLS + ("ksplashqml",)
# Mesa drivers that render on the CPU. KWin's ScreenShot2 offscreen effect
# allocates a non-software EGL buffer for its render target; on a software
# renderer the allocation has no render engine behind it, and llvmpipe faults
# while the DBus reply waits on the resulting fence. KWin fixed this in 6.8
# (offscreeneffect: allocate a software buffer on software renderers,
# add43708), which the hosted 26.04 image does not carry, so the capture
# gates skip rather than time out there.
SOFTWARE_RENDERER_DRIVERS = frozenset({"llvmpipe", "softpipe", "swrast", "zink"})


def software_renderer_skip_reason():
    """Return the capture gates' skip reason when Mesa is forced to software."""
    if os.environ.get("LIBGL_ALWAYS_SOFTWARE") == "1":
        return SOFTWARE_RENDER_SKIP_REASON
    for variable in ("MESA_LOADER_DRIVER_OVERRIDE", "GALLIUM_DRIVER"):
        if os.environ.get(variable, "").lower() in SOFTWARE_RENDERER_DRIVERS:
            return SOFTWARE_RENDER_SKIP_REASON
    return None


SOFTWARE_RENDER_SKIP_REASON = (
    "KWin's ScreenShot2 offscreen effect hangs on a software Mesa renderer "
    "(fixed in KWin 6.8); run on a GPU-backed host to exercise the capture gates"
)


class _PixelPins:
    """Pixel-reading assertions the render gates share.

    A plain mixin: unittest discovers test methods only on the
    ``TestCase`` subclasses that mix it in, so the mixin itself never
    runs as a test. ``TestRender`` and ``_DialogGate``'s concrete
    subclasses inherit these helpers beside their own ``candidate_image``
    accessors.
    """

    def assert_pixel(self, x, y, colour):
        self.assertEqual(colour, hex_colour(pixel_at(self.candidate_image(), x, y)))

    def assert_raised_frame(self, rect, *, flat_rows=(), corner_blend=0):
        """Pin a raised frame's outline/bevel and optional label-free rows.

        *corner_blend* excludes the antialiased corner arc some buttons
        draw over the sharp rectangle's ends: 0 (the default, and the
        dialog buttons' shape) asserts the full outline rows and columns;
        *n* > 0 shrinks each asserted span by *n* pixels at the row ends
        and by *n* - 1 at the column ends (the arc covers one fewer row),
        leaving the blend greys to the caller's row pins.
        """
        x, y, width, height = rect
        if corner_blend:
            rows = range(x + corner_blend, x + width - corner_blend)
            columns = range(y + corner_blend, y + height - corner_blend)
        else:
            rows = range(x, x + width)
            columns = range(y + 1, y + height - 1)
        for xx in rows:
            self.assert_pixel(xx, y, "#000000")
            self.assert_pixel(xx, y + height - 1, "#000000")
        for yy in columns:
            self.assert_pixel(x, yy, "#000000")
            self.assert_pixel(x + 1, yy, "#FFFFFF")
            self.assert_pixel(x + width - 2, yy, "#AAAAAA")
            self.assert_pixel(x + width - 1, yy, "#000000")
        for row in flat_rows:
            self.assert_pixel(x + 2, row, "#DDDDDD")
            self.assert_pixel(x + width - 3, row, "#DDDDDD")

    def assert_band(self, rect, rows):
        """Pin every cell of *rect* at the per-row colours *rows*.

        A blended bevel arm, a lost outline row, a swapped arm colour, a
        resampled grip bar or a one-pixel crop slip shows up here
        immediately.
        """
        image = self.candidate_image()
        x, y, width, height = rect
        for row in range(height):
            with self.subTest(row=y + row):
                self.assertEqual(
                    list(rows[row]),
                    [
                        hex_colour(pixel_at(image, x + dx, y + row))
                        for dx in range(width)
                    ],
                )

    def assert_flat_window_face(self, rect):
        """Pin every cell of *rect* at the flat #DDDDDD window face.

        The calendar, colour and icon dialog gates each pin one
        face crop this way: the rows must show the window body colour
        column to column, so a stray glyph row, a title-bar bleed or a
        repaint of the chrome above the widget inside fails row by row.
        """
        self.assert_band(
            rect, [["#DDDDDD"] * rect[2] for _ in range(rect[3])]
        )


@unittest.skipIf(
    software_renderer_skip_reason() is not None,
    software_renderer_skip_reason() or "",
)
@unittest.skipUnless(
    all(shutil.which(tool) for tool in REAL_TOOLS),
    "needs kwin_wayland, dbus-run-session, plasmawindowed, spectacle and "
    "plasma-apply-colorscheme on PATH",
)
class TestRender(_PixelPins, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run the CLI the way `make render` does, as one of _Renders'
        # concurrent sessions, with the tool's documented settle default
        # (8s), not a tighter one. The session sleeps for that paint budget
        # and then captures: a loaded host that has not painted the window
        # within the budget has its all-black capture refused by the CLI,
        # which names the settle wait instead of leaving the pixel
        # comparisons below to report unexplained failures. The tool's default
        # is the paint budget it promises; the gate must not render below it.
        cls.stdout, cls.stderr, cls.returncode, cls.directory = _Renders.ensure(
            "applet"
        )
        cls.output = os.path.join(cls.directory, "render.png")
        cls._candidate = None

    @classmethod
    def candidate_image(cls):
        """Return the render output decoded once, reused by every read below.

        The render writes one PNG that the size, body-colour and strip checks
        all read; decoding it per read re-decodes the same 320x240 file, so
        the first read caches it for the rest of the class. A failed render
        leaves the output absent and the first read raises ``PngError`` just
        as it did before.
        """
        if cls._candidate is None:
            cls._candidate = read_png(cls.output)
        return cls._candidate

    def test_exits_zero(self):
        self.assertEqual(0, self.returncode, self.stderr)

    def test_writes_a_320x240_png(self):
        image = self.candidate_image()
        self.assertEqual((320, 240), (image.width, image.height))

    def test_window_body_is_the_platinum_face(self):
        pixel = pixel_at(self.candidate_image(), 300, 200)
        self.assertEqual(FACE, hex_colour(pixel))

    def assert_strip_pixels_match(
        self, candidate_crop, reference_crop, reference_path=REFERENCE
    ):
        """Byte-compare one strip with the same ``crop``/``compare`` the CLI calls.

        Each strip is compared in process, reusing the process-cached
        reference decode instead of spawning the CLI and re-decoding the
        1024x768 screenshot once per strip. The CLI's crop options, including
        ``--candidate-crop`` and ``--crop`` in one run, stay covered end to
        end by ``tests/test_fidelity_cli_crops.py``.
        """
        reference, error = read_reference(
            reference_path, max_rows=REFERENCE_BOUNDS[reference_path]
        )
        skip_unless_materialized(self, reference_path, error)
        candidate = crop(self.candidate_image(), *candidate_crop)
        expected = crop(reference, *reference_crop)
        self.assertEqual(0, compare(candidate, expected).differing)

    def test_title_bar_matches_the_reference(self):
        self.assert_strip_pixels_match(CANDIDATE_CROP, REFERENCE_CROP)

    def test_first_client_rows_match_the_reference(self):
        # One white highlight row (the frame's centre tile), then the client;
        # against the unset TitleEdgeBottom the tile painted five rows white
        # here and the client sat four rows below the reference's.
        self.assert_strip_pixels_match(CLIENT_ROWS_CANDIDATE, CLIENT_ROWS_REFERENCE)

    def test_title_bar_boxes_match_the_reference(self):
        for candidate_crop, reference_crop, reference_path in (
            (CLOSE_CANDIDATE, CLOSE_REFERENCE, REFERENCE),
            (COLLAPSE_CANDIDATE, COLLAPSE_REFERENCE, REFERENCE),
            (ZOOM_CANDIDATE, ZOOM_REFERENCE, PROFILER_REFERENCE),
        ):
            with self.subTest(candidate_crop=candidate_crop):
                self.assert_strip_pixels_match(
                    candidate_crop, reference_crop, reference_path
                )

    def test_frame_borders_match_the_reference(self):
        for candidate_crop, reference_crop in (
            (LEFT_BORDER_CANDIDATE, LEFT_BORDER_REFERENCE),
            (RIGHT_BORDER_CANDIDATE, RIGHT_BORDER_REFERENCE),
            (BOTTOM_BORDER_CANDIDATE, BOTTOM_BORDER_REFERENCE),
        ):
            with self.subTest(candidate_crop=candidate_crop):
                self.assert_strip_pixels_match(candidate_crop, reference_crop)

    # The applet's own face below the existing chrome strips: the display
    # field and the keypad cells, pinned from the 2026-11-11 three-render
    # capture through the shared pixel helpers (the constants above quote
    # the measured geometry and each value's stability provenance). The
    # font-dependent label and digit ink stays out of the exact pins;
    # the live-ink checks at the end pin that the glyphs really draw.

    def assert_keypad_cell(self, rect):
        """Pin one keypad cell's raised frame and its corner arcs.

        ``assert_raised_frame`` pins the black outline rows and columns,
        the #FFFFFF bevel column, the #AAAAAA shadow column and the flat
        #DDDDDD face rows over their clean spans (corner_blend=3); the
        four full-width rows pin the outline/bevel/arm rows including
        their blend greys, and the two arc rows pin the remaining blend
        pixels at the cell's ends.
        """
        x, y, width, height = rect
        top, bevel, arm, bottom = _keypad_rows(width)
        self.assert_band((x, y, width, 1), [top])
        self.assert_band((x, y + 1, width, 1), [bevel])
        self.assert_band((x, y + height - 2, width, 1), [arm])
        self.assert_band((x, y + height - 1, width, 1), [bottom])
        for dx, colour in enumerate(KEYPAD_ARC_ROWS[0]):
            self.assert_pixel(x + dx, y + 2, colour)
        for dx, colour in enumerate(KEYPAD_ARC_ROWS[1]):
            self.assert_pixel(x + width - 3 + dx, y + 2, colour)
        for dx, colour in enumerate(KEYPAD_ARC_ROWS[2]):
            self.assert_pixel(x + dx, y + height - 3, colour)
        for dx, colour in enumerate(KEYPAD_ARC_ROWS[3]):
            self.assert_pixel(x + width - 3 + dx, y + height - 3, colour)
        self.assert_raised_frame(
            rect, corner_blend=3, flat_rows=range(y + 3, y + height - 3)
        )

    def test_the_display_field_pins_its_outline_and_flat_interior(self):
        # The display field is a 1px #000000 outline box (see
        # DISPLAY_FIELD) whose interior is flat #DDDDDD except the digit's
        # font-dependent ink, confined to the measured region; a
        # recoloured outline, a lost face row or stray art in the display
        # fails here.
        x0, y0, x1, y1 = DISPLAY_FIELD
        for xx in range(x0, x1 + 1):
            self.assert_pixel(xx, y0, "#000000")
            self.assert_pixel(xx, y1, "#000000")
        for yy in range(y0, y1 + 1):
            self.assert_pixel(x0, yy, "#000000")
            self.assert_pixel(x1, yy, "#000000")
        ix0, iy0, ix1, iy1 = DISPLAY_INK_REGION
        image = self.candidate_image()
        self.assertEqual(
            [],
            [
                (x, y, hex_colour(pixel_at(image, x, y)))
                for x in range(x0 + 1, x1)
                for y in range(y0 + 1, y1)
                if not (ix0 <= x <= ix1 and iy0 <= y <= iy1)
                and hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
            ],
        )

    def test_the_display_inks_its_digit(self):
        # The digit must really draw: at least one #000000 pixel inside
        # the measured ink region (the glyphs themselves stay unpinned,
        # mirroring the title gate's live-ink check).
        ix0, iy0, ix1, iy1 = DISPLAY_INK_REGION
        image = self.candidate_image()
        self.assertTrue(
            any(
                hex_colour(pixel_at(image, x, y)) == "#000000"
                for x in range(ix0, ix1 + 1)
                for y in range(iy0, iy1 + 1)
            ),
            "the display field carries no digit ink",
        )

    def test_the_keypad_cells_pin_the_raised_frames(self):
        # Each measured cell's raised frame: a dropped bevel arm, a
        # shifted cell boundary or a resampled frame fails here.
        for rect in KEYPAD_CELLS:
            with self.subTest(cell=rect):
                self.assert_keypad_cell(rect)

    def test_the_gaps_between_the_cells_stay_flat_face(self):
        # The flat #DDDDDD face rows between the bands: full client width
        # (x=6..313; x=0..5 and x=314..319 carry the side border art the
        # existing strip tests byte-compare) for rows 23..26 above the
        # display, 79..82 between display and keypad, 109..112, 139..142,
        # 170..173 and 230..233, and x=6..208 only for rows 200..203,
        # where the tall right cell spans them. The gap columns x=72..75
        # and 139..142 stay flat across each of the first four bands'
        # interior rows; the fifth band has no gap column to pin (its
        # leftmost cell spans x=10..138 across the first gap column).
        image = self.candidate_image()
        self.assertEqual(
            [],
            [
                (x, y, hex_colour(pixel_at(image, x, y)))
                for y0, y1 in ((23, 26), (79, 82), (109, 112), (139, 142),
                               (170, 173), (230, 233))
                for y in range(y0, y1 + 1)
                for x in range(6, 314)
                if hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
            ],
        )
        self.assertEqual(
            [],
            [
                (x, y, hex_colour(pixel_at(image, x, y)))
                for y in range(200, 204)
                for x in range(6, 209)
                if hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
            ],
        )
        for y0, y1 in KEYPAD_BANDS[:4]:
            self.assertEqual(
                [],
                [
                    (x, y, hex_colour(pixel_at(image, x, y)))
                    for x in (*range(72, 76), *range(139, 143))
                    for y in range(y0 + 3, y1 - 2)
                    if hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
                ],
            )

    def test_every_keypad_cell_inks_its_label(self):
        # Every cell must really draw its label: at least one #000000
        # pixel inside its interior (the glyphs themselves stay unpinned,
        # mirroring the dialog gates' live-ink checks).
        image = self.candidate_image()
        for rect in KEYPAD_CELLS:
            x, y, width, height = rect
            with self.subTest(cell=rect):
                self.assertTrue(
                    any(
                        hex_colour(pixel_at(image, x + 2 + dx, y + 2 + dy))
                        == "#000000"
                        for dx in range(width - 4)
                        for dy in range(height - 4)
                    ),
                    f"cell {rect} carries no label ink",
                )


class TestDialogGateSkipGuards(unittest.TestCase):
    """The fourteen dialog gates skip wherever their render CLI refuses on a tool.

    The dialog render CLI refuses with a missing-tool diagnostic when any
    of the five applet-render tools or the dialog client its requested mode
    opens is absent (kdialog for the thirteen kdialog modes, zenity for the
    GTK mode), and the fourteen dialog gates' shared skip guard encodes exactly
    that condition. These tests fail wherever a guard is removed
    (``AttributeError`` on ``__unittest_skip__``) and where a guard's tool
    list drifts from the render CLI's own requirement list, the local
    literal the guards otherwise all repeat.
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

    def test_all_dialog_gates_skip_only_when_a_tool_is_absent(self):
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
            TestFileDialogRender,
        ):
            with self.subTest(gate=gate.__name__):
                self.assertEqual(expected, gate.__unittest_skip__)

        # Reapply the real guard to disposable classes: never alter the
        # render gates or start a session while simulating missing tools.
        for missing in (None, *tools):
            with self.subTest(missing=missing):
                def which(tool):
                    return None if tool == missing else "/fake/bin/" + tool

                with (
                    mock.patch.object(shutil, "which", side_effect=which),
                    mock.patch.object(
                        sys.modules[__name__], "software_renderer_skip_reason",
                        return_value=None,
                    ),
                ):
                    guarded = _dialog_gate_guard()(type("Probe", (), {}))
                self.assertEqual(missing is not None, guarded.__unittest_skip__)


class _Renders:
    """The module's render gates' sessions, started together, finished once.

    Every render sleeps its configured settle budget before it captures --
    that budget is the paint budget the gate promises, and the
    byte-compare gates below must not render below it -- so serial
    back-to-back renders cost one settle budget per gate. The sessions
    sessions are independent -- each has its own ``dbus-run-session``,
    scratch XDG tree (and with it its own ``render-surface`` socket) and
    capture path -- and the settle is a sleep rather than CPU, so starting
    all at once and finishing them together costs one budget. The first gate
    class to set up records all results;
    :func:`_remove_directories` removes every scratch directory at
    interpreter exit, so a run that reaches only some of the classes still
    cleans up behind the others.
    """

    KINDS = (
        ("applet", (), "render.png"),
        ("checkbox", ("--checkbox-dialog",), "dialog.png"),
        ("combobox", ("--combobox-dialog",), "dialog.png"),
        ("lineedit", ("--lineedit-dialog",), "dialog.png"),
        ("menu", ("--menu-dialog",), "dialog.png"),
        ("radiolist", ("--radiolist-dialog",), "dialog.png"),
        ("calendar", ("--calendar-dialog",), "dialog.png"),
        ("color", ("--color-dialog",), "dialog.png"),
        ("icon", ("--icon-dialog",), "dialog.png"),
        ("progressbar", ("--progressbar-dialog",), "dialog.png"),
        ("slider", ("--slider-dialog",), "dialog.png"),
        ("textbox", ("--textbox-dialog",), "dialog.png"),
        ("gtk", ("--gtk-dialog", "--settle", "20"), "dialog.png"),
        ("inactive", ("--inactive-dialog",), "dialog.png"),
        ("file_dialog", ("--file-dialog",), "dialog.png"),
        ("desktop", ("--desktop",), "desktop.png"),
        ("splash", ("--splash",), "splash.png"),
    )
    # A kind whose tool runs a longer internal timeout waits on that budget
    # plus margin, not the shared 150 s dialog wait: the desktop render's
    # documented timeout default is 180 s (tools/render_surface.py's
    # _DESKTOP_TIMEOUT), so finishing it at 150 s would SIGKILL a legitimate
    # slow first plasmashell start the tool itself would still have served.
    FINISH_TIMEOUTS = {"desktop": 240}
    directories: dict[str, str] = {}
    results: dict[str, tuple[str, str, int, str]] = {}
    completed = False
    failure: BaseException | None = None

    @classmethod
    def ensure(cls, kind):
        """Finish all renders once and return *kind*'s result."""
        if not cls.completed:
            cls.completed = True
            # The sweep joins before the renders start: all scratch
            # directories may already exist by the time a render fails, and
            # a failed run must still remove them at interpreter exit.
            atexit.register(cls._remove_directories)
            try:
                cls._run_all()
            except Exception as error:
                cls.failure = error
                raise
        if cls.failure is not None:
            # The sibling gate re-raises the failed run's error instead of a
            # KeyError about a result the failed run never recorded.
            raise cls.failure
        return cls.results[kind]

    @classmethod
    def _run_all(cls):
        started = {}
        for kind, flags, filename in cls.KINDS:
            directory = tempfile.mkdtemp(prefix=f"{kind}-render-test-")
            cls.directories[kind] = directory
            started[kind] = process_runner.start(
                [sys.executable, SCRIPT, os.path.join(directory, filename), *flags],
                capture_output=True,
                text=True,
            )
        for kind, _, _ in cls.KINDS:
            # The first finish below waits one settle budget while the
            # other two renders run alongside it.
            stdout, stderr = process_runner.finish(
                started[kind], timeout=cls.FINISH_TIMEOUTS.get(kind, 150)
            )
            cls.results[kind] = (
                stdout,
                stderr,
                started[kind].returncode,
                cls.directories[kind],
            )

    @classmethod
    def _remove_directories(cls):
        for directory in cls.directories.values():
            shutil.rmtree(directory, ignore_errors=True)


class TestRenderBudgets(unittest.TestCase):
    def test_gtk_dialog_gets_a_longer_settle_budget(self):
        flags = dict((kind, flags) for kind, flags, _ in _Renders.KINDS)["gtk"]
        self.assertIn("--settle", flags)
        settle = flags[flags.index("--settle") + 1]
        self.assertEqual(settle, "20")

    def test_the_inactive_gate_renders_at_the_documented_default_settle(self):
        # The two-window inactive capture rides the same dialog defaults as
        # the kdialog widget gates: its flags in _Renders.KINDS carry
        # no --settle argument, so the dialog default paint budget governs
        # and no under-budgeted override can shorten the two-window
        # session's settle. A static pin of the shipped flag list, like the
        # sibling applet pin below.
        flags = dict((kind, flags) for kind, flags, _ in _Renders.KINDS)["inactive"]
        self.assertNotIn("--settle", flags)

    def test_the_applet_gate_renders_at_the_documented_default_settle(self):
        # The offline reproduction of the archived slow-check record about the
        # applet render gate: its flags in _Renders.KINDS carry no --settle
        # argument at all, so the gate renders at the tool's documented
        # default paint budget (8 s) and cannot under-budget the paint wait
        # the way the removed --settle 3 override did on a loaded host. This
        # is a static pin of the shipped flag list -- a real render session
        # runs in none of it, and the stubbed capture the byte-compare gates
        # exercise is elsewhere; the tool's --settle default is the fixture
        # this pin's flag list keeps out of reach.
        flags = dict((kind, flags) for kind, flags, _ in _Renders.KINDS)["applet"]
        self.assertNotIn("--settle", flags)


class _DialogGate(_PixelPins):
    """Test scaffolding the fourteen dialog render gates share.

    Each gate is a ``unittest.TestCase`` only through its concrete subclass
    (unittest discovers tests on the subclasses alone) and waits on its own
    ``_Renders`` render; the gates differ in the kind key they wait
    on, in the shipped slice and cell geometry they byte-compare and in the
    extra widget-specific tests they add below.
    """

    KIND: str

    @classmethod
    def setUpClass(cls):
        # All renders run concurrently (see _Renders); this class
        # waits for its own and leaves its siblings' to their own classes.
        cls.stdout, cls.stderr, cls.returncode, cls.directory = (
            _Renders.ensure(cls.KIND)
        )
        cls.output = os.path.join(cls.directory, "dialog.png")
        cls._candidate = None

    @classmethod
    def candidate_image(cls):
        """Return the dialog render decoded once, reused by every read below."""
        if cls._candidate is None:
            cls._candidate = read_png(cls.output)
        return cls._candidate

    def test_exits_zero(self):
        self.assertEqual(0, self.returncode, self.stderr)

    def test_writes_a_480x360_png(self):
        image = self.candidate_image()
        self.assertEqual((DIALOG_WIDTH, DIALOG_HEIGHT), (image.width, image.height))

    def assert_cell_matches(self, slice_name, cell):
        """Byte-compare the engine-drawn cell at *cell* with the shipped art.

        The expected pixels are the named shipped slice itself, at its canvas
        size, re-derived from the same SVG the Kvantum reference suites use:
        the engine may neither resample the art nor fill the cell from a
        foreign element.
        """
        expected = dict(render_slices(parse_svg(SVG))[slice_name])
        x0, y0, width, height = cell
        actual = {
            (x, y): hex_colour(
                pixel_at(self.candidate_image(), x0 + x, y0 + y)
            )
            for x in range(width)
            for y in range(height)
        }
        self.assertEqual(expected, actual)

    def assert_push_button_recipe(self, rect, cell, flat_rows):
        """Pin the raised push-button recipe over its full-height cell.

        The engine's raised button recipe is one contract, so its outline,
        bevel arms, face rows and shadow arm are asserted here and both
        gates that pin a push button walk their own rect and cell through
        it (the color and icon dialog gates below).
        """
        self.assert_raised_frame(rect, flat_rows=flat_rows)
        face_row = [
            "#FFFFFF",
            *["#DDDDDD"] * 4,
        ]
        arm_row = [
            "#FFFFFF",
            *["#AAAAAA"] * 4,
        ]
        rows = (
            [["#000000"] * 5]
            + [["#FFFFFF"] * 5]
            + [face_row] * 20
            + [arm_row]
            + [["#000000"] * 5]
        )
        self.assert_band(cell, rows)

    def assert_push_button_face_reaches_its_row(self, rect):
        """Pin the raised recipe's flat face across its label-free row.

        The raised recipe's flat face must reach the whole label-free
        row: a rounded stock face, a duplicated or shifted bevel arm or
        a recoloured face fails on the row's columns. Shared with
        ``assert_push_button_recipe`` by the color and icon dialog gates.
        """
        image = self.candidate_image()
        x, y, width, height = rect
        self.assertEqual(
            ["#DDDDDD"] * (width - 4),
            [hex_colour(pixel_at(image, x + 2 + dx, y + height - 4))
             for dx in range(width - 4)],
        )


def _dialog_gate_guard():
    """Return the skip guard the fourteen dialog render gates share.

    The dialog render CLI needs the same five Plasma tools as the applet
    render plus the client its requested mode opens (it exits 2 with a
    missing-tool diagnostic when one is absent: kdialog for the thirteen
    kdialog modes, zenity for the GTK mode), so the fourteen dialog gates skip
    under the condition the applet gate above's ``skipUnless`` guard uses,
    extended with both clients. A gate that failed rather than skipped
    where its tools are missing would turn `make check` red on a machine
    that merely lacks Plasma, where the sibling applet gate already skips.
    """
    tools = DIALOG_REAL_TOOLS
    reason = software_renderer_skip_reason() or (
        "needs kwin_wayland, dbus-run-session, plasmawindowed, spectacle, "
        "plasma-apply-colorscheme, kdialog and zenity on PATH"
    )
    missing = [tool for tool in tools if shutil.which(tool) is None]

    def decorator(cls):
        # `unittest.skip` only annotates when its condition fails, so the
        # guard writes the attributes itself: the skip flag must be
        # present (False where every tool exists and the renderer is a GPU)
        # whatever the host has.
        cls.__unittest_skip__ = bool(missing) or software_renderer_skip_reason() is not None
        cls.__unittest_skip_why__ = reason
        return cls

    return decorator


def _desktop_gate_guard():
    """Return the skip guard the desktop render gate uses.

    The desktop render CLI requires the same five Plasma tools as the applet
    render plus its own client, ``plasmashell`` (DESKTOP_REAL_TOOLS above, the
    set the CLI's desktop preflight refuses on), so the gate skips under the
    shared software-renderer condition extended with that client -- the same
    attribute-writing shape ``_dialog_gate_guard`` uses, so the skip flag is
    present (False where every tool exists and the renderer is a GPU)
    whatever the host has. The desktop mode opens no kdialog or zenity
    client, so neither belongs in its guarded set.
    """
    tools = DESKTOP_REAL_TOOLS
    reason = software_renderer_skip_reason() or (
        "needs kwin_wayland, dbus-run-session, plasmawindowed, spectacle, "
        "plasma-apply-colorscheme and plasmashell on PATH"
    )
    missing = [tool for tool in tools if shutil.which(tool) is None]

    def decorator(cls):
        cls.__unittest_skip__ = bool(missing) or software_renderer_skip_reason() is not None
        cls.__unittest_skip_why__ = reason
        return cls

    return decorator


@_dialog_gate_guard()
class TestCheckboxDialogRender(_DialogGate, unittest.TestCase):
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
        # _DialogGate.assert_cell_matches): a blended band shows up here
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


@_dialog_gate_guard()
class TestComboboxDialogRender(_DialogGate, unittest.TestCase):
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
        # _DialogGate.assert_cell_matches): a squashed or blended arrow shows
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


@_dialog_gate_guard()
class TestLineInputDialogRender(_DialogGate, unittest.TestCase):
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


@_dialog_gate_guard()
class TestMenuDialogRender(_DialogGate, unittest.TestCase):
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


@_dialog_gate_guard()
class TestRadioDialogRender(_DialogGate, unittest.TestCase):
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


@_dialog_gate_guard()
class TestCalendarDialogRender(_DialogGate, unittest.TestCase):
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


@_dialog_gate_guard()
class TestColorDialogRender(_DialogGate, unittest.TestCase):
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


@_dialog_gate_guard()
class TestIconDialogRender(_DialogGate, unittest.TestCase):
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


@_dialog_gate_guard()
class TestSliderDialogRender(_DialogGate, unittest.TestCase):
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
        # _DialogGate.assert_cell_matches): a resampled, recoloured or
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


@_dialog_gate_guard()
class TestTextboxDialogRender(_DialogGate, unittest.TestCase):
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


@_dialog_gate_guard()
class TestProgressbarDialogRender(_DialogGate, unittest.TestCase):
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


@_dialog_gate_guard()
class TestGtkDialogRender(_DialogGate, unittest.TestCase):
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


@_dialog_gate_guard()
class TestInactiveDialogRender(_DialogGate, unittest.TestCase):
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


@_dialog_gate_guard()
class TestFileDialogRender(_DialogGate, unittest.TestCase):
    """The KIO file chooser ``--file-dialog`` captures, region by region.

    The chooser capture lands in the shared 480x360 ``dialog.png`` (the
    dialog default size, like the kdialog widget gates), so this gate is a
    ``_DialogGate`` subclass waiting on the ``file_dialog`` render. The
    pinned values below were measured on a consecutive pair of full
    ``tools/render_surface.py <scratch>/file.png --file-dialog`` runs on
    this host (2026-11-11, both exit 0, both 480x360): the two captures
    differ in exactly 16 pixels, all in the Name field's text caret
    column x=200, y=267..282 (a third same-day run drew the caret off and
    compared byte-identical to the first), so every other pixel is
    run-stable. The title bar's two right-hand boxes are the shipped
    Aurorae maximize and collapse (windowshade) widgets drawn 1:1 by KWin,
    re-derived from ``render_slices`` like the sibling art-side pins;
    the leftmost box holds the window icon, whose mark is the fallback
    icon theme's rendering, pinned as measured.

    The list panel's content faces are pinned too, re-derived on
    2026-11-11 from three consecutive ``--file-dialog`` renders that
    agreed byte for byte outside the Name field's caret column: the
    session-measured Name column sat 7px narrower when the first pair
    measured it, and no repository change explains the width (the
    host's rendering shifted underneath the pins), so the divider,
    caption, sort-arrow and size-text pins below were re-derived from
    the agreeing second set. The column-header band rows
    99..120 draws face ``#DDDDDD`` with two full-height dividers (an
    ``#AAAAAA`` shadow column beside a ``#000000`` core column at
    x=350/351 and x=400/401) whose style-drawn sort arrow is byte-pinned
    as measured; the seeded file rows 123..182 pin their ``#FFFFFF`` and
    ``#EEEEEE`` (alternate-row trough) band faces with each per-file
    type icon's cell byte-pinned as measured; the empty rows 183..251
    are flat ``#FFFFFF``; and the caption glyphs, the file names, the
    size text and the clock-dependent date column stay live ink.

    The places sidebar is pinned beside its existing selected-row
    highlight (measured on the same fresh pair): the two group
    headers' live-ink bands, the Home entry's 40x26 folder icon cell
    and the two device entries' byte-identical 40x26 drive cells (one
    measured map pins both at the +52 row offset), each entry's
    live-label band and both capacity-bar troughs with their caps,
    edge column and left-anchored fills. After these pins only the
    label and group-header glyphs, the icon art's provenance and the
    capacity bars' fill/free boundary (the host filesystem's live
    used-space total) stay unpinned.
    """

    KIND = "file_dialog"

    # The Name field's text caret: the one unstable strip, excluded from
    # the field's interior pin because its blink phase varies between runs
    # (off in the first and third measured runs, on in the second).
    CARET_STRIP = (200, 267, 282)  # x=200, y=267..282
    # The Filter combo's "All Files" text ink (rows 297..306, x=200..243
    # measured): stable across all three measured runs but app-drawn text,
    # so it is excluded from the interior pin like the labels rather than
    # pinned as theme chrome.
    FILTER_TEXT = (200, 297, 243, 306)  # x0, y0, x1, y1
    # The centered title's glyph band over the pinstripes (ink measured at
    # x=217..240, rows 9..18, widened for antialiasing bleed): the pinstripe
    # rows carry the title's live ink here, so the band is excluded from
    # the stripe pin, not from the band's stripes elsewhere.
    TITLE_BAND = (214, 8, 243, 18)  # x0, y0, x1, y1

    # The title bar's leftmost 13x13 box (window icon box, x=4..16,
    # y=7..19): a #888888-outline box with the fallback-theme icon mark
    # inside and the #FFFFFF bevel column/row at x=16/y=19, measured
    # pixel-exact on the runs named in the class docstring.
    ICON_BOX_ROWS = (
        ("#888888", "#888888", "#888888", "#888888", "#888888", "#888888",
         "#888888", "#888888", "#888888", "#888888", "#888888", "#888888",
         "#CCCCCC"),
        ("#888888", "#222222", "#222222", "#222222", "#222222", "#222222",
         "#222222", "#222222", "#222222", "#222222", "#222222", "#222222",
         "#FFFFFF"),
        ("#888888", "#222222", "#FFFFFF", "#CCCCCC", "#CCCCCC", "#CCCCCC",
         "#CCCCCC", "#CCCCCC", "#CCCCCC", "#CCCCCC", "#CCCCCC", "#222222",
         "#FFFFFF"),
        ("#888888", "#222222", "#CCCCCC", "#999999", "#999999", "#AAAAAA",
         "#AAAAAA", "#BBBBBB", "#BBBBBB", "#CCCCCC", "#888888", "#222222",
         "#FFFFFF"),
        ("#888888", "#222222", "#CCCCCC", "#999999", "#AAAAAA", "#AAAAAA",
         "#BBBBBB", "#BBBBBB", "#CCCCCC", "#CCCCCC", "#888888", "#222222",
         "#FFFFFF"),
        ("#888888", "#222222", "#CCCCCC", "#AAAAAA", "#AAAAAA", "#BBBBBB",
         "#BBBBBB", "#CCCCCC", "#CCCCCC", "#DDDDDD", "#888888", "#222222",
         "#FFFFFF"),
        ("#888888", "#222222", "#CCCCCC", "#AAAAAA", "#BBBBBB", "#BBBBBB",
         "#CCCCCC", "#CCCCCC", "#DDDDDD", "#DDDDDD", "#888888", "#222222",
         "#FFFFFF"),
        ("#888888", "#222222", "#CCCCCC", "#BBBBBB", "#BBBBBB", "#CCCCCC",
         "#CCCCCC", "#DDDDDD", "#DDDDDD", "#EEEEEE", "#888888", "#222222",
         "#FFFFFF"),
        ("#888888", "#222222", "#CCCCCC", "#BBBBBB", "#CCCCCC", "#CCCCCC",
         "#DDDDDD", "#DDDDDD", "#EEEEEE", "#EEEEEE", "#888888", "#222222",
         "#FFFFFF"),
        ("#888888", "#222222", "#CCCCCC", "#CCCCCC", "#CCCCCC", "#DDDDDD",
         "#DDDDDD", "#EEEEEE", "#EEEEEE", "#FFFFFF", "#888888", "#222222",
         "#FFFFFF"),
        ("#888888", "#222222", "#CCCCCC", "#888888", "#888888", "#888888",
         "#888888", "#888888", "#888888", "#888888", "#888888", "#222222",
         "#FFFFFF"),
        ("#888888", "#222222", "#222222", "#222222", "#222222", "#222222",
         "#222222", "#222222", "#222222", "#222222", "#222222", "#222222",
         "#FFFFFF"),
        ("#CCCCCC", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF"),
    )

    # The title bar's two right-hand boxes: the shipped Aurorae maximize
    # widget (21x13, its glyph box in columns 5..17 with a pinstripe-matching
    # left pad) drawn at x=442..462, and the collapse (windowshade) widget
    # (13x13) drawn at x=463..475, both y=7..19, both byte-identical to the
    # ``render_slices`` re-derivation of the shipped SVG art.
    MAXIMIZE_BOX = (442, 7)
    SHADE_BOX = (463, 7)

    # The column-header band's two dividers (rows 99..120, measured): each
    # is a #AAAAAA shadow column beside a #000000 core column, at
    # x=350/351 and x=400/401. A lost shadow column, a lost core column or
    # a recoloured face fails the band test below.
    # Re-derived 2026-11-11 (second same-day drift: the KIO chooser's Name
    # column rendered 7px wider again, moving every pin right of it +7)
    # from three consecutive full --file-dialog renders on this host that
    # agreed byte-for-byte outside the caret strip x=200, y=267..282.
    HEADER_DIVIDERS = (
        (350, "#AAAAAA"),
        (351, "#000000"),
        (400, "#AAAAAA"),
        (401, "#000000"),
    )
    # The header captions' ink bands (measured columns; the glyphs stay
    # live): "Name" x=155..187, "Size" x=355..379 and "Date" x=406..433,
    # all inking rows 105..114.
    HEADER_CAPTIONS = ((155, 187), (355, 379), (406, 433))
    CAPTION_ROWS = (105, 114)
    # The header band's style-drawn sort arrow (a solid #000000
    # downward-pointing triangle with antialiased arms), byte-pinned as
    # measured at x=336..346, rows 106..114. A moved, dropped, recoloured
    # or resampled arrow fails the byte-compare.
    SORT_ARROW = (
        ("#DDDDDD", "#373737", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#373737", "#DDDDDD"),
        ("#DDDDDD", "#A6A6A6", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#A6A6A6", "#DDDDDD"),
        ("#DDDDDD", "#DDDDDD", "#373737", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#373737", "#DDDDDD", "#DDDDDD"),
        ("#DDDDDD", "#DDDDDD", "#A6A6A6", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#A6A6A6", "#DDDDDD", "#DDDDDD"),
        ("#DDDDDD", "#DDDDDD", "#DDDDDD", "#373737", "#000000",
         "#000000", "#000000", "#373737", "#DDDDDD", "#DDDDDD", "#DDDDDD"),
        ("#DDDDDD", "#DDDDDD", "#DDDDDD", "#A6A6A6", "#000000",
         "#000000", "#000000", "#A6A6A6", "#DDDDDD", "#DDDDDD", "#DDDDDD"),
        ("#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#373737",
         "#000000", "#373737", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD"),
        ("#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#A6A6A6",
         "#000000", "#A6A6A6", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD"),
        ("#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#6E6E6E", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD"),
    )
    SORT_ARROW_RECT = (336, 106)

    # The three seeded file rows' type-icon cells, byte-pinned as measured
    # (rows 1 and 2 draw the fallback theme's document glyph, row 3 its
    # distinct blue-ruled RTF glyph; the rightmost columns carry the
    # #7F7F7F/#777777 fold shading against the row's own face colour, so
    # the white-face and grey-face maps differ there).
    DOC_ICON_ON_WHITE = (
        ("#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#7F7F7F", "#FFFFFF", "#FFFFFF"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#AFAFAF", "#DDDDDD", "#DDDDDD", "#FFFFFF"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#AFAFAF", "#DDDDDD", "#7F7F7F"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#AFAFAF", "#000000"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#999999", "#999999", "#999999",
         "#999999", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
        ("#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000"),
    )
    DOC_ICON_ON_GREY = (
        ("#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#777777", "#EEEEEE", "#EEEEEE"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#AFAFAF", "#DDDDDD", "#DDDDDD", "#EEEEEE"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#AFAFAF", "#DDDDDD", "#777777"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#AFAFAF", "#000000"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#999999", "#999999", "#999999",
         "#999999", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
        ("#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#000000"),
        ("#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000"),
    )
    RTF_ICON = (
        ("#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63",
         "#0C2D63", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF"),
        ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF"),
        ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF"),
        ("#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63",
         "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63",
         "#0C2D63", "#0C2D63"),
        ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF"),
        ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF"),
        ("#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63",
         "#0C2D63", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF"),
        ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF"),
        ("#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63",
         "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63",
         "#0C2D63", "#0C2D63"),
        ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF"),
        ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF"),
        ("#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63",
         "#0C2D63", "#0C2D63", "#0C2D63", "#0C2D63", "#FFFFFF",
         "#FFFFFF", "#FFFFFF"),
    )
    # The icon cells' offsets and shapes: row 1 and row 2 draw the
    # document glyph 10x13 at (173, 126) and (173, 146); row 3 draws the
    # RTF glyph 12x12 at (172, 167) (all measured).
    ICON_CELLS = (
        (173, 126, 10, 13, DOC_ICON_ON_WHITE),
        (173, 146, 10, 13, DOC_ICON_ON_GREY),
        (172, 167, 12, 12, RTF_ICON),
    )

    # The three seeded file rows' band faces and their per-band measured
    # ink rectangles (the icon cell, the name text and the size text),
    # excluded from the face pin; rows are the bands' first row, each band
    # spanning 20 rows. The date band (DATE_BAND, x=395..473) is excluded
    # from the exactness pin across a band's full height and demands live
    # ink instead: the seeded files' modification times are the render
    # session's wall clock, so the date column's digits move between runs.
    # The size-text rectangles re-derived 2026-11-11 with the dividers
    # above (the wider Name column moved the size column's text +7).
    ROW_BANDS = (
        (123, "#FFFFFF", ((173, 182, 126, 138), (191, 241, 128, 139),
                          (375, 393, 128, 137))),
        (143, "#EEEEEE", ((173, 182, 146, 158), (191, 241, 148, 157),
                          (375, 393, 148, 157))),
        (163, "#FFFFFF", ((172, 183, 167, 178), (191, 241, 168, 178),
                          (375, 393, 168, 177))),
    )
    ROW_BAND_HEIGHT = 20
    ROW_TEXT_BANDS = ((191, 241), (375, 393), (395, 473))
    EMPTY_ROWS = (183, 251)

    # The places sidebar's two group headers: live-ink bands (measured
    # on the fresh pair named in the class docstring; "Places" inks
    # x=13..47, rows 39..48 and "Devices" x=13..56, rows 171..180; the
    # glyphs themselves stay unpinned like the other app-drawn text).
    GROUP_HEADERS = ((13, 47, 39, 48), (13, 56, 171, 180))
    # The Home entry's 40x26 folder icon cell (x=14..53, rows 70..95),
    # byte-pinned as measured, with its live-label band to the cell's
    # right (ink measured inside x=63..96, rows 77..86, band widened to
    # the plan's column extent; the glyphs themselves stay unpinned).
    FOLDER_CELL = (14, 70, 40, 26)
    PLACES_LABEL_BANDS = ((58, 96, 73, 86),)
    FOLDER_CELL_ROWS = (
        ("#6E6E6E", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#1B1B1B", "#C1C1C1", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD"),
        ("#6E6E6E", "#000000", "#DBDBDB", "#C9C9C9", "#B7B7B7",
         "#B7B7B7", "#B7B7B7", "#B7B7B7", "#B7B7B7", "#B7B7B7",
         "#B7B7B7", "#B7B7B7", "#B7B7B7", "#B7B7B7", "#B7B7B7",
         "#949494", "#1B1B1B", "#C1C1C1", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#B7B7B7", "#1B1B1B", "#C1C1C1", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#E1E1E1", "#FBFBFB", "#B7B7B7", "#1B1B1B", "#C1C1C1",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#E1E1E1", "#FBFBFB", "#B7B7B7", "#1B1B1B",
         "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E",
         "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E",
         "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E",
         "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E", "#A6A6A6"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#E1E1E1", "#FBFBFB", "#B7B7B7",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#E1E1E1", "#FBFBFB",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#CCCCCC", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#E1E1E1",
         "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE",
         "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE",
         "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE",
         "#EEEEEE", "#C3C3C3", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#CCCCCC", "#C3C3C3", "#BBBBBB",
         "#BBBBBB", "#BBBBBB", "#BBBBBB", "#BBBBBB", "#BBBBBB",
         "#BBBBBB", "#BBBBBB", "#BBBBBB", "#BBBBBB", "#BBBBBB",
         "#BBBBBB", "#BBBBBB", "#BBBBBB", "#BBBBBB", "#BBBBBB",
         "#BBBBBB", "#BBBBBB", "#BBBBBB", "#BBBBBB", "#BBBBBB",
         "#BBBBBB", "#BBBBBB", "#BBBBBB", "#BBBBBB", "#BBBBBB",
         "#BBBBBB", "#BBBBBB", "#BBBBBB", "#CCCCCC", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#BBBBBB", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6E6E6E"),
        ("#6E6E6E", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#6E6E6E"),
        ("#A6A6A6", "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E",
         "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E",
         "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E",
         "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E",
         "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E",
         "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E",
         "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E",
         "#6E6E6E", "#6E6E6E", "#6E6E6E", "#6E6E6E", "#A6A6A6"),
    )
    # The two device entries' 40x26 drive icon cells at (14, 202) and
    # (14, 254): measured byte-identical at the +52 row offset on the
    # fresh pair, so one map pins both. Their live-label bands (ink
    # measured inside x=63..119, rows 206..215 and 258..267) sit beside
    # them; the glyphs themselves stay unpinned.
    DRIVE_CELLS = ((14, 202), (14, 254))
    DEVICE_LABEL_BANDS = ((62, 119, 206, 215), (62, 119, 258, 267))
    DRIVE_CELL_ROWS = (
        ("#6F6F6F", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#DADADA", "#C8C8C8", "#B6B6B6",
         "#B6B6B6", "#B6B6B6", "#B6B6B6", "#B6B6B6", "#B6B6B6",
         "#B6B6B6", "#B6B6B6", "#B6B6B6", "#B6B6B6", "#B6B6B6",
         "#B6B6B6", "#B6B6B6", "#B6B6B6", "#B6B6B6", "#B6B6B6",
         "#B6B6B6", "#B6B6B6", "#B6B6B6", "#B6B6B6", "#B6B6B6",
         "#B6B6B6", "#B6B6B6", "#B6B6B6", "#B6B6B6", "#B6B6B6",
         "#B6B6B6", "#B6B6B6", "#B6B6B6", "#B6B6B6", "#B6B6B6",
         "#B6B6B6", "#AFAFAF", "#A7A7A7", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#CCCCCC", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#CCCCCC", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#F6F6F6", "#EEEEEE",
         "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE",
         "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE",
         "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE",
         "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE",
         "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE",
         "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE", "#EEEEEE",
         "#EEEEEE", "#C3C3C3", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#000000", "#3F3F3F", "#7F7F7F", "#7F7F7F", "#7F7F7F",
         "#7F7F7F", "#7F7F7F", "#7F7F7F", "#7F7F7F", "#7F7F7F",
         "#7F7F7F", "#7F7F7F", "#7F7F7F", "#7F7F7F", "#7F7F7F",
         "#7F7F7F", "#7F7F7F", "#7F7F7F", "#7F7F7F", "#3F3F3F",
         "#000000", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#C6C6C6", "#7A7A7A", "#7A7A7A", "#C6C6C6", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#000000", "#7F7F7F", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#7F7F7F",
         "#000000", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#ACACAC",
         "#0C0C0C", "#000000", "#000000", "#0D0D0D", "#ADADAD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#000000", "#7F7F7F", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#7F7F7F",
         "#000000", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#2A2A2A",
         "#000000", "#000000", "#000000", "#000000", "#2B2B2B",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#000000", "#7F7F7F", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#7F7F7F",
         "#000000", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#020202",
         "#000000", "#000000", "#000000", "#000000", "#020202",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#000000", "#7F7F7F", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#7F7F7F",
         "#000000", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#2A2A2A",
         "#000000", "#000000", "#000000", "#000000", "#2B2B2B",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#000000", "#7F7F7F", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
         "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#7F7F7F",
         "#000000", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#ACACAC",
         "#0D0D0D", "#000000", "#000000", "#0D0D0D", "#ADADAD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#000000", "#3F3F3F", "#7F7F7F", "#7F7F7F", "#7F7F7F",
         "#7F7F7F", "#7F7F7F", "#7F7F7F", "#7F7F7F", "#7F7F7F",
         "#7F7F7F", "#7F7F7F", "#7F7F7F", "#7F7F7F", "#7F7F7F",
         "#7F7F7F", "#7F7F7F", "#7F7F7F", "#7F7F7F", "#3F3F3F",
         "#000000", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#C6C6C6", "#7A7A7A", "#7A7A7A", "#C6C6C6", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#FFFFFF", "#EEEEEE", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD", "#DDDDDD",
         "#DDDDDD", "#BBBBBB", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#999999", "#999999",
         "#999999", "#999999", "#999999", "#000000", "#6F6F6F"),
        ("#6F6F6F", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#000000",
         "#000000", "#000000", "#000000", "#000000", "#6F6F6F"),
        ("#A6A6A6", "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F",
         "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F",
         "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F",
         "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F",
         "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F",
         "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F",
         "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F",
         "#6F6F6F", "#6F6F6F", "#6F6F6F", "#6F6F6F", "#A6A6A6"),
    )
    # The two device entries' capacity-bar troughs (x=62..134, 6 rows,
    # top rows 218 and 270): caps, edge column and left-anchored fill
    # pinned by test_the_capacity_bars_pin_their_troughs below; the
    # fill's extent stays unpinned (the live used-space total).
    CAPACITY_TROUGHS = (218, 270)

    def assert_box_matches_svg(self, x0, y0, svg_name):
        """Byte-compare the box at (x0, y0) with the shipped Aurorae SVG art.

        The expected pixels are the named widget SVG's ``active-center``
        slice at its canvas size, re-derived from the shipped file the way
        ``tests/test_aurorae_buttons.py`` does: KWin may neither resample
        the art nor fill the box from a foreign element.
        """
        expected = render_slices(
            parse_svg(os.path.join(AURORAE_DIR, svg_name))
        )["active-center"]
        width = max(x for x, _ in expected) + 1
        height = max(y for _, y in expected) + 1
        actual = {
            (x, y): hex_colour(pixel_at(self.candidate_image(), x0 + x, y0 + y))
            for x in range(width)
            for y in range(height)
        }
        self.assertEqual(expected, actual)

    def test_the_frame_and_title_bar_bands_pin_the_platinum_chrome(self):
        # Rows 0..3 the Aurorae decoration's 4px top border; row 4 the white
        # inner edge below it; rows 5..22 the title-bar band with its face
        # and edge columns; rows 23..25 the band's bottom shadow, outline
        # and client-edge rows; rows 26..349 the client frame's left and
        # right edges; rows 350..359 the closing frame. A dropped border
        # row, a lost pinstripe or a recoloured face fails here.
        for y in range(4):
            for x in range(480):
                self.assert_pixel(x, y, "#000000")
        self.assert_pixel(0, 4, "#000000")
        for x in range(1, 478):
            self.assert_pixel(x, 4, "#FFFFFF")
        self.assert_pixel(478, 4, "#CCCCCC")
        self.assert_pixel(479, 4, "#000000")
        for y in range(5, 23):
            self.assert_pixel(0, y, "#000000")
            self.assert_pixel(1, y, "#FFFFFF")
            self.assert_pixel(2, y, "#CCCCCC")
            self.assert_pixel(3, y, "#CCCCCC")
            self.assert_pixel(478, y, "#999999")
            self.assert_pixel(479, y, "#000000")
        # The face bands above and below the band's ink: rows 5..6 and
        # 20..22 carry no ink anywhere (the boxes and pinstripes span
        # rows 7..19), and the pinstripe band's face row 19 sits below it.
        for y in (5, 6, 20, 21, 22):
            for x in range(2, 478):
                self.assert_pixel(x, y, "#CCCCCC")
        for x in range(17, 442):
            self.assert_pixel(x, 19, "#CCCCCC")
        # The pinstriped band: alternating white (odd rows) and #777777
        # (even rows) stripes across x=17..441, the shipped decoration
        # SVG's 22px title-bar pinstripes (whose source pixels
        # tests/test_aurorae_frame.py already re-derive); even-row stripe
        # pixels at x=442 belong to the maximize widget's art below, and
        # the title's live glyph band (TITLE_BAND) carries ink over the
        # stripes and stays out of the pin.
        x0, y0, x1, y1 = self.TITLE_BAND
        for y in range(7, 19):
            colour = "#FFFFFF" if y % 2 else "#777777"
            for x in range(17, 442):
                if y0 <= y <= y1 and x0 <= x <= x1:
                    continue
                self.assert_pixel(x, y, colour)
        # The title band's right edge columns beside the collapse box.
        for y in range(7, 20):
            self.assert_pixel(476, y, "#CCCCCC")
            self.assert_pixel(477, y, "#CCCCCC")
        # Row 23 the band's #999999 shadow, row 24 its #000000 outline,
        # row 25 the client's white top edge.
        self.assert_pixel(0, 23, "#000000")
        self.assert_pixel(1, 23, "#FFFFFF")
        for x in range(2, 4):
            self.assert_pixel(x, 23, "#CCCCCC")
        for x in range(4, 475):
            self.assert_pixel(x, 23, "#999999")
        for x in range(475, 478):
            self.assert_pixel(x, 23, "#CCCCCC")
        self.assert_pixel(478, 23, "#999999")
        self.assert_pixel(479, 23, "#000000")
        self.assert_pixel(0, 24, "#000000")
        self.assert_pixel(1, 24, "#FFFFFF")
        for x in range(2, 4):
            self.assert_pixel(x, 24, "#CCCCCC")
        self.assert_pixel(4, 24, "#999999")
        for x in range(5, 475):
            self.assert_pixel(x, 24, "#000000")
        self.assert_pixel(475, 24, "#FFFFFF")
        for x in range(476, 478):
            self.assert_pixel(x, 24, "#CCCCCC")
        self.assert_pixel(478, 24, "#999999")
        self.assert_pixel(479, 24, "#000000")
        self.assert_pixel(0, 25, "#000000")
        self.assert_pixel(1, 25, "#FFFFFF")
        for x in range(2, 4):
            self.assert_pixel(x, 25, "#CCCCCC")
        self.assert_pixel(4, 25, "#999999")
        self.assert_pixel(5, 25, "#000000")
        for x in range(6, 474):
            self.assert_pixel(x, 25, "#FFFFFF")
        self.assert_pixel(474, 25, "#000000")
        self.assert_pixel(475, 25, "#FFFFFF")
        for x in range(476, 478):
            self.assert_pixel(x, 25, "#CCCCCC")
        self.assert_pixel(478, 25, "#999999")
        self.assert_pixel(479, 25, "#000000")
        # The client frame's edge columns, rows 26..349: a #FFFFFF inner
        # edge beside a #CCCCCC face, a #999999 shadow and a #000000
        # outline on each side.
        for y in range(26, 350):
            self.assert_pixel(0, y, "#000000")
            self.assert_pixel(1, y, "#FFFFFF")
            self.assert_pixel(2, y, "#CCCCCC")
            self.assert_pixel(3, y, "#CCCCCC")
            self.assert_pixel(4, y, "#999999")
            self.assert_pixel(5, y, "#000000")
            self.assert_pixel(474, y, "#000000")
            self.assert_pixel(475, y, "#FFFFFF")
            self.assert_pixel(476, y, "#CCCCCC")
            self.assert_pixel(477, y, "#CCCCCC")
            self.assert_pixel(478, y, "#999999")
            self.assert_pixel(479, y, "#000000")
        # The closing frame, rows 350..359.
        self.assert_pixel(0, 350, "#000000")
        self.assert_pixel(1, 350, "#FFFFFF")
        for x in range(2, 4):
            self.assert_pixel(x, 350, "#CCCCCC")
        self.assert_pixel(4, 350, "#999999")
        for x in range(5, 475):
            self.assert_pixel(x, 350, "#000000")
        self.assert_pixel(475, 350, "#FFFFFF")
        for x in range(476, 478):
            self.assert_pixel(x, 350, "#CCCCCC")
        self.assert_pixel(478, 350, "#999999")
        self.assert_pixel(479, 350, "#000000")
        self.assert_pixel(0, 351, "#000000")
        self.assert_pixel(1, 351, "#FFFFFF")
        for x in range(2, 5):
            self.assert_pixel(x, 351, "#CCCCCC")
        for x in range(5, 476):
            self.assert_pixel(x, 351, "#FFFFFF")
        for x in range(476, 478):
            self.assert_pixel(x, 351, "#CCCCCC")
        self.assert_pixel(478, 351, "#999999")
        self.assert_pixel(479, 351, "#000000")
        for y in (352, 353):
            self.assert_pixel(0, y, "#000000")
            self.assert_pixel(1, y, "#FFFFFF")
            for x in range(2, 478):
                self.assert_pixel(x, y, "#CCCCCC")
            self.assert_pixel(478, y, "#999999")
            self.assert_pixel(479, y, "#000000")
        self.assert_pixel(0, 354, "#000000")
        self.assert_pixel(1, 354, "#CCCCCC")
        for x in range(2, 479):
            self.assert_pixel(x, 354, "#999999")
        self.assert_pixel(479, 354, "#000000")
        for y in range(355, 360):
            for x in range(480):
                self.assert_pixel(x, y, "#000000")

    def test_the_title_bar_marks_draw_their_boxes(self):
        # The window-icon box, byte-exact as measured (see the class
        # docstring): the #888888-outline box at x=4..15, y=7..18 with the
        # fallback-theme icon mark inside, its #FFFFFF bevel column at x=16
        # and bevel row 19 at x=5..16.
        self.assert_band((4, 7, 13, 13), self.ICON_BOX_ROWS)
        # The two right-hand boxes re-derived from the shipped Aurorae
        # widgets: the maximize art (21x13, glyph box plus pinstripe-matching
        # left pad) at x=442 and the collapse art (13x13) at x=463. A
        # resampled, recoloured or swapped widget fails the byte-compare.
        self.assert_box_matches_svg(*self.MAXIMIZE_BOX, "maximize.svg")
        self.assert_box_matches_svg(*self.SHADE_BOX, "shade.svg")

    def test_the_title_text_inks_its_live_label(self):
        # The centered title must really draw: at least one #000000 pixel
        # inside its glyph band (the glyphs themselves stay unpinned,
        # mirroring the desktop gate's right-half live-content check).
        image = self.candidate_image()
        self.assertTrue(
            any(
                hex_colour(pixel_at(image, x, y)) == "#000000"
                for x in range(217, 261)
                for y in range(8, 19)
            ),
            "the title band carries no title ink",
        )

    def test_the_panels_pin_their_sunken_borders(self):
        # The two #000000 divider verticals at x=139 and x=145 with the 5px
        # #DDDDDD gap between them, rows 26..349; the splitter handle's
        # grip rows 180..195 pinned in the gap (a black-banded box with
        # #B0B0B0/#DDDDDD/#595959 grip rows, measured); the list panel's
        # #999999 left shadow at x=146 (rows 95..252, face elsewhere); the
        # header rules rows 96..97; the header's white row 98; the list
        # view's bottom outline row 252 and white bevel row 253; and the
        # face rows between the list view and the filter row (254..262).
        for y in range(26, 350):
            self.assert_pixel(139, y, "#000000")
            self.assert_pixel(145, y, "#000000")
        for y in range(26, 350):
            if 180 <= y <= 195:
                continue
            for x in range(140, 145):
                self.assert_pixel(x, y, "#DDDDDD")
        grip = (
            "#000000", "#000000", "#000000", "#B0B0B0", "#DDDDDD",
            "#DDDDDD", "#595959", "#000000", "#000000", "#595959",
            "#DDDDDD", "#DDDDDD", "#B0B0B0", "#000000", "#000000",
            "#000000",
        )
        for offset, colour in enumerate(grip):
            for x in range(140, 145):
                self.assert_pixel(x, 180 + offset, colour)
        for y in range(26, 350):
            expected = "#999999" if 95 <= y <= 252 else "#DDDDDD"
            self.assert_pixel(146, y, expected)
        for y in (96, 97):
            for x in range(147, 475):
                self.assert_pixel(x, y, "#000000")
        self.assert_pixel(147, 98, "#000000")
        self.assert_pixel(148, 98, "#000000")
        for x in range(149, 474):
            self.assert_pixel(x, 98, "#FFFFFF")
        for x in range(147, 475):
            self.assert_pixel(x, 252, "#000000")
        for x in range(147, 474):
            self.assert_pixel(x, 253, "#FFFFFF")
        for y in range(254, 263):
            for x in range(146, 474):
                self.assert_pixel(x, y, "#DDDDDD")
        # The chooser's directory label above the header draws live ink
        # (rows 68..77 measured); its glyphs stay unpinned.
        image = self.candidate_image()
        self.assertTrue(
            any(
                hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
                for x in range(150, 251)
                for y in range(60, 91)
            ),
            "the directory label above the header draws no ink",
        )
        # So do the header labels and the file rows (the row text and the
        # type-icon art stay unpinned per README; the icon cells themselves
        # are byte-pinned by the sibling type-icon test below).
        self.assertTrue(
            any(
                hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
                for x in range(152, 474)
                for y in range(99, 252)
            ),
            "the list panel draws no header or row ink",
        )

    def test_the_sidebar_pins_its_selected_row(self):
        # The selected places entry highlights #CCCCFF across x=6..138,
        # rows 108..159, except the highlighted entry's own icon and label
        # ink (measured inside x=8..53 and x=58..118; live, unpinned); the
        # sidebar's other surfaces are pinned beside it (the group headers,
        # entry icon cells, live labels and capacity-bar troughs in the
        # sibling tests below), leaving only the glyphs, the icon art's
        # provenance and the capacity bars' fill/free boundary unpinned.
        image = self.candidate_image()
        ink = [
            (x, y)
            for y in range(108, 160)
            for x in range(6, 139)
            if hex_colour(pixel_at(image, x, y)) != "#CCCCFF"
        ]
        self.assertTrue(ink, "the selected row's highlight is missing")
        for y in range(108, 160):
            for x in range(6, 139):
                if (x, y) in ink:
                    continue
                self.assert_pixel(x, y, "#CCCCFF")

    def test_the_sidebar_group_headers_ink_their_live_labels(self):
        # Each group header must really draw its caption: at least one
        # pixel off the #DDDDDD face inside its measured band (the
        # glyphs themselves stay unpinned, like the other app-drawn
        # text). A dropped header fails here.
        image = self.candidate_image()
        for x0, x1, y0, y1 in self.GROUP_HEADERS:
            with self.subTest(header=(x0, x1)):
                self.assertTrue(
                    any(
                        hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
                        for x in range(x0, x1 + 1)
                        for y in range(y0, y1 + 1)
                    ),
                    "the sidebar group header draws no ink",
                )

    def test_the_places_entry_pins_its_folder_cell(self):
        # The Home entry's 40x26 folder icon cell, byte-pinned to its
        # measured map (measured on the fresh pair named in the class
        # docstring): a moved, dropped or resampled cell fails the
        # byte-compare. The entry's label draws live ink beside it.
        x0, y0, width, height = self.FOLDER_CELL
        self.assert_band((x0, y0, width, height), self.FOLDER_CELL_ROWS)
        image = self.candidate_image()
        self.assertTrue(
            any(
                hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
                for x in range(58, 97)
                for y in range(73, 87)
            ),
            "the Home entry's label draws no ink",
        )

    def test_the_device_entries_pin_their_drive_cells(self):
        # Both device entries draw the same 40x26 drive icon cell
        # (measured byte-identical at the +52 row offset on the fresh
        # pair), so one measured map pins both: a moved, dropped,
        # resampled or diverging cell fails the byte-compare.
        for x0, y0 in self.DRIVE_CELLS:
            with self.subTest(drive_cell=y0):
                self.assert_band((x0, y0, 40, 26), self.DRIVE_CELL_ROWS)

    def test_the_device_entries_ink_their_live_labels(self):
        # Each device name must really draw beside its cell: at least
        # one pixel off the #DDDDDD face inside its measured band. A
        # dropped device entry's name fails here.
        image = self.candidate_image()
        for x0, x1, y0, y1 in self.DEVICE_LABEL_BANDS:
            with self.subTest(label=y0):
                self.assertTrue(
                    any(
                        hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
                        for x in range(x0, x1 + 1)
                        for y in range(y0, y1 + 1)
                    ),
                    "the device entry's label draws no ink",
                )

    def test_the_capacity_bars_pin_their_troughs(self):
        # Each device entry carries a 6-row capacity-bar trough at
        # x=62..134: no #DDDDDD face pixel inside the box, the left
        # cap's fill-side blends (#C8C8E4/#CACAF8 at x=62, the fill's
        # own #CCCCFF at x=63), the right cap's #B1B1B1 core at x=133
        # with its #C5C5C5/#DCDCDC edge column at x=134, at least one
        # full-strength #CCCCFF and one #B1B1B1 pixel per trough, and
        # the fill left-anchored at x=63. The fill's extent stays
        # deliberately unpinned: it is the host filesystem's live
        # used-space total, so session writes can move the fill/free
        # boundary between runs (the splash track's fill-extent
        # precedent). A dropped bar, a moved trough, a recoloured cap,
        # a lost fill or a right-anchored fill fails here.
        image = self.candidate_image()
        for trough_y0 in self.CAPACITY_TROUGHS:
            with self.subTest(trough=trough_y0):
                self.assertEqual(
                    [],
                    [
                        (x, y)
                        for y in range(trough_y0, trough_y0 + 6)
                        for x in range(62, 135)
                        if hex_colour(pixel_at(image, x, y)) == "#DDDDDD"
                    ],
                    "a #DDDDDD face pixel sits inside the trough box",
                )
                for offset, colour in enumerate(
                    ("#C8C8E4", "#CACAF8", "#CACAF8", "#C8C8E4")
                ):
                    self.assert_pixel(62, trough_y0 + 1 + offset, colour)
                    self.assert_pixel(63, trough_y0 + 1 + offset, "#CCCCFF")
                for y in range(trough_y0, trough_y0 + 6):
                    self.assert_pixel(
                        133,
                        y,
                        "#C5C5C5"
                        if y in (trough_y0, trough_y0 + 5)
                        else "#B1B1B1",
                    )
                self.assert_band(
                    (134, trough_y0, 1, 6),
                    [
                        ("#DCDCDC",),
                        ("#C5C5C5",),
                        ("#B5B5B5",),
                        ("#B5B5B5",),
                        ("#C5C5C5",),
                        ("#DCDCDC",),
                    ],
                )
                trough = [
                    hex_colour(pixel_at(image, x, y))
                    for y in range(trough_y0, trough_y0 + 6)
                    for x in range(62, 135)
                ]
                self.assertIn("#CCCCFF", trough)
                self.assertIn("#B1B1B1", trough)

    def test_the_sidebar_face_stays_flat_outside_its_ink(self):
        # Every sidebar pixel in x=6..138, rows 26..349 outside the
        # existing selected-row band, the pinned icon cells, the trough
        # boxes and the live-ink bands is the flat #DDDDDD face: a
        # stray widget or a recoloured face fails here.
        image = self.candidate_image()
        bands = (
            self.GROUP_HEADERS
            + self.PLACES_LABEL_BANDS
            + self.DEVICE_LABEL_BANDS
        )
        cells = [self.FOLDER_CELL[:2]] + list(self.DRIVE_CELLS)
        exclusions = list(bands)
        exclusions.extend((x0, x0 + 39, y0, y0 + 25) for x0, y0 in cells)
        exclusions.extend((62, 134, y0, y0 + 5) for y0 in self.CAPACITY_TROUGHS)
        stray = [
            (x, y, hex_colour(pixel_at(image, x, y)))
            for y in range(26, 350)
            for x in range(6, 139)
            if not (108 <= y <= 159)
            and not any(
                a <= x <= b and c <= y <= d for a, b, c, d in exclusions
            )
            and hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
        ]
        self.assertEqual([], stray)

    def test_the_filter_and_name_fields_draw_sunken_boxes(self):
        # Both labeled fields (Name above, Filter below, labels to their
        # left): a #999999 shadow row above, a #000000 top outline, a
        # #999999 shadow column at x=192 beside the #000000 left outline at
        # x=193, a #FFFFFF interior (x=194..473), a #000000 bottom outline
        # and a #FFFFFF bevel row below. The Name field's caret strip
        # (x=200, y=267..282) and the Filter combo's "All Files" text band
        # (FILTER_TEXT) stay out of the interiors; both labels draw live
        # ink, glyphs unpinned.
        for x in range(192, 474):
            self.assert_pixel(x, 263, "#999999")
        for x in range(192, 475):
            self.assert_pixel(x, 264, "#000000" if x >= 193 else "#999999")
        for y in range(265, 285):
            self.assert_pixel(192, y, "#999999")
            self.assert_pixel(193, y, "#000000")
            for x in range(194, 474):
                if x == self.CARET_STRIP[0] and self.CARET_STRIP[1] <= y <= self.CARET_STRIP[2]:
                    continue
                self.assert_pixel(x, y, "#FFFFFF")
        for x in range(192, 475):
            self.assert_pixel(x, 285, "#000000" if x >= 193 else "#999999")
        for x in range(193, 474):
            self.assert_pixel(x, 286, "#FFFFFF")
        for x in range(192, 474):
            self.assert_pixel(x, 290, "#999999")
        for x in range(192, 475):
            self.assert_pixel(x, 291, "#000000" if x >= 193 else "#999999")
        for y in range(292, 312):
            self.assert_pixel(192, y, "#999999")
            self.assert_pixel(193, y, "#000000")
            for x in range(194, 474):
                if (self.FILTER_TEXT[0] <= x <= self.FILTER_TEXT[2]
                        and self.FILTER_TEXT[1] <= y <= self.FILTER_TEXT[3]):
                    continue
                self.assert_pixel(x, y, "#FFFFFF")
        for x in range(192, 475):
            self.assert_pixel(x, 312, "#000000" if x >= 193 else "#999999")
        for x in range(193, 474):
            self.assert_pixel(x, 313, "#FFFFFF")
        # The face rows between the fields and the bottom buttons (the
        # divider verticals at x=139 and x=145 keep running through them).
        for y in range(314, 320):
            for x in range(6, 474):
                if x in (139, 145):
                    continue
                self.assert_pixel(x, y, "#DDDDDD")
        # The two labels draw live ink inside their measured glyph bands.
        image = self.candidate_image()
        self.assertTrue(
            any(
                hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
                for x in range(153, 190)
                for y in range(270, 280)
            ),
            "the Name row's label draws no ink",
        )
        self.assertTrue(
            any(
                hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
                for x in range(153, 166)
                for y in range(297, 307)
            ),
            "the Filter row's label draws no ink",
        )

    def test_the_toolbar_and_bottom_buttons_draw_raised_boxes(self):
        # The toolbar's two buttons (x=345..376 and x=382..413, rows
        # 28..57): a #000000 outline with the #AAAAAA shadow arm along the
        # top/left inner edges and the #FFFFFF bevel arm along the
        # bottom/right inner edges (the measured arms; unlike the bottom
        # buttons, the shadow leads), with the buttons' marks left live.
        for x0 in (345, 382):
            for x in range(x0, x0 + 32):
                self.assert_pixel(x, 28, "#000000")
                self.assert_pixel(x, 57, "#000000")
            for y in range(29, 57):
                self.assert_pixel(x0, y, "#000000")
                self.assert_pixel(x0 + 31, y, "#000000")
            for x in range(x0 + 1, x0 + 30):
                self.assert_pixel(x, 29, "#AAAAAA")
            for y in range(29, 57):
                self.assert_pixel(x0 + 1, y, "#AAAAAA")
                self.assert_pixel(x0 + 30, y, "#FFFFFF")
            for x in range(x0 + 2, x0 + 31):
                self.assert_pixel(x, 56, "#FFFFFF")
        # The bottom buttons (x=352..433 and x=437..474, rows 320..343)
        # carry the raised-frame shape: #000000 outline, #FFFFFF left/top
        # bevels, #AAAAAA bottom shadow; the wider OK button also carries
        # the #AAAAAA right shadow arm at x=432 (measured), the narrower
        # Cancel button's top-right corner stays #FFFFFF.
        for x0, x1, shadow_col in ((352, 433, 432), (437, 474, None)):
            for x in range(x0, x1 + 1):
                self.assert_pixel(x, 320, "#000000")
                self.assert_pixel(x, 343, "#000000")
            for y in range(321, 343):
                self.assert_pixel(x0, y, "#000000")
                self.assert_pixel(x1, y, "#000000")
                self.assert_pixel(x0 + 1, y, "#FFFFFF")
                if shadow_col is not None:
                    self.assert_pixel(shadow_col, y, "#AAAAAA")
            for x in range(x0 + 1, x1):
                self.assert_pixel(x, 321, "#AAAAAA" if x == shadow_col else "#FFFFFF")
            self.assert_pixel(x0 + 1, 342, "#FFFFFF")
            for x in range(x0 + 2, x1):
                self.assert_pixel(x, 342, "#AAAAAA")
        # Each of the four boxes really draws its mark: at least one pixel
        # off the #DDDDDD face inside the outline (the toolbar marks and
        # the button labels are app-drawn greys, left unpinned).
        image = self.candidate_image()
        for x0, x1, y0, y1 in (
            (348, 373, 30, 55),
            (385, 410, 30, 55),
            (355, 430, 322, 341),
            (440, 471, 322, 341),
        ):
            with self.subTest(box=(x0, x1, y0, y1)):
                self.assertTrue(
                    any(
                        hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
                        for x in range(x0, x1 + 1)
                        for y in range(y0, y1 + 1)
                    ),
                    "the box draws no mark inside its outline",
                )

    def test_the_column_header_band_pins_its_face_and_dividers(self):
        # Rows 99..120 across x=152..473 (right of the existing scrollbar-strip
        # exclusion): face #DDDDDD except the two full-height dividers (the
        # #AAAAAA shadow column beside the #000000 core column at x=350/351
        # and x=400/401) and the caption and sort-arrow ink bands pinned
        # live and byte-exact in the sibling tests below. Rows 121..122 are
        # the list field's top edge (#AAAAAA rule, #000000 outline). A lost
        # divider column, a recoloured header face or a recoloured top edge
        # fails here.
        divider_columns = {x for x, _ in self.HEADER_DIVIDERS}
        caption_y0, caption_y1 = self.CAPTION_ROWS
        arrow_x0, arrow_y0 = self.SORT_ARROW_RECT
        arrow_width, arrow_height = len(self.SORT_ARROW[0]), len(self.SORT_ARROW)
        for y in range(99, 121):
            for x in range(152, 474):
                if caption_y0 <= y <= caption_y1 and any(
                    a <= x <= b for a, b in self.HEADER_CAPTIONS
                ):
                    continue
                if (arrow_y0 <= y < arrow_y0 + arrow_height
                        and arrow_x0 <= x < arrow_x0 + arrow_width):
                    continue
                if x in divider_columns:
                    continue
                self.assert_pixel(x, y, "#DDDDDD")
        for x, colour in self.HEADER_DIVIDERS:
            for y in range(99, 121):
                self.assert_pixel(x, y, colour)
        for y in (121, 122):
            for x in range(152, 474):
                self.assert_pixel(x, y, "#AAAAAA" if y == 121 else "#000000")

    def test_the_header_inks_its_captions_and_sort_arrow(self):
        # The three captions must really draw: at least one pixel darker
        # than the #DDDDDD face inside each caption band (the glyphs
        # themselves stay live). The style-drawn sort arrow is byte-pinned
        # to its measured 11x9 pixel map: a dropped, moved, resampled or
        # recoloured arrow fails the byte-compare.
        image = self.candidate_image()
        for x0, x1 in self.HEADER_CAPTIONS:
            with self.subTest(caption=(x0, x1)):
                self.assertTrue(
                    any(
                        hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
                        for x in range(x0, x1 + 1)
                        for y in range(self.CAPTION_ROWS[0], self.CAPTION_ROWS[1] + 1)
                    ),
                    "the header caption draws no ink",
                )
        self.assert_band(
            (self.SORT_ARROW_RECT[0], self.SORT_ARROW_RECT[1],
             len(self.SORT_ARROW[0]), len(self.SORT_ARROW)),
            self.SORT_ARROW,
        )

    def test_the_list_rows_pin_their_band_faces(self):
        # The three seeded file rows: rows 123..142 and 163..182 face
        # #FFFFFF, rows 143..162 the #EEEEEE alternate-row trough, each
        # pinned across x=152..473 except the measured icon cell and name/size
        # text rectangles (ROW_BANDS) and the clock-dependent date band
        # (x=395..473, live ink demanded instead). Rows 183..251, the empty
        # rows below the listing, are flat #FFFFFF: a lost alternate-row
        # trough, a stray paint or art in the empty rows fails here.
        for start, face, rects in self.ROW_BANDS:
            with self.subTest(row_band=start):
                self._pin_row_band(start, face, rects)

    def _pin_row_band(self, start, face, rects):
        """Pin one row band's face across its span, skipping pinned rects."""
        for y in range(start, start + self.ROW_BAND_HEIGHT):
            for x in range(152, 474):
                if any(a <= x <= b and c <= y <= d for a, b, c, d in rects):
                    continue
                if 395 <= x <= 473:
                    continue
                self.assert_pixel(x, y, face)
        image = self.candidate_image()
        for start, face, _ in self.ROW_BANDS:
            with self.subTest(date_ink=start):
                self.assertTrue(
                    any(
                        hex_colour(pixel_at(image, x, y)) != face
                        for x in range(395, 474)
                        for y in range(start, start + self.ROW_BAND_HEIGHT)
                    ),
                    "the date column draws no ink",
                )
        for y in range(self.EMPTY_ROWS[0], self.EMPTY_ROWS[1] + 1):
            for x in range(152, 474):
                self.assert_pixel(x, y, "#FFFFFF")

    def test_the_file_rows_draw_their_type_icons(self):
        # The three type-icon cells, byte-pinned to their measured pixel
        # maps (rows 1 and 2 the fallback theme's document glyph against
        # its row's own face colour, row 3 the distinct blue-ruled RTF
        # glyph): a shifted cell, a dropped icon or a resampled glyph
        # fails the byte-compare.
        for x0, y0, width, height, rows in self.ICON_CELLS:
            with self.subTest(icon_cell=(x0, y0)):
                self.assert_band((x0, y0, width, height), rows)

    def test_the_file_rows_ink_their_columns(self):
        # Each seeded row must really draw its listing: at least one pixel
        # off the row's face inside the name, size and date bands. A
        # dropped listing or an emptied date cell fails here.
        image = self.candidate_image()
        for start, face, _ in self.ROW_BANDS:
            for x0, x1 in self.ROW_TEXT_BANDS:
                with self.subTest(row_column=(start, x0)):
                    self.assertTrue(
                        any(
                            hex_colour(pixel_at(image, x, y)) != face
                            for x in range(x0, x1 + 1)
                            for y in range(start, start + self.ROW_BAND_HEIGHT)
                        ),
                        "the file row draws no ink in one of its columns",
                    )


@_desktop_gate_guard()
class TestDesktopRender(unittest.TestCase):
    """The rendered plasmashell menu bar's Platinum structure, pinned.

    The ``--desktop`` capture is a 640x400 PNG whose top 20 rows are the
    flush menu-bar panel the look-and-feel layout builds and whose rows
    20..399 are the flat desktop area below it. The bar's pinned structure
    was measured on a consecutive pair of full
    ``tools/render_surface.py <scratch>/desktop.png --desktop`` runs on this
    host (2026-11-11, both exit 0, both 640x400): the two captures differ in
    exactly 54 pixels, all inside x=472..478, y=5..14 -- the clock digits.
    Later same-day runs drew one more stable element the first pair lacked:
    a tray icon whose ink reaches x=351, present in four further captures and
    absent from the first pair, so the exclusion boundary was re-derived from
    five same-day captures (the re-derivation the planned re-derivation note
    calls for) from the plan's x=359 to x=351: the bar's pinned empty corridor
    is x=17..350 and the excluded right half is x=351..639, verified stable
    and live across all five. The bar's right half (x=351..639, rows 3..16)
    holds the tray icons, the clock digits and the shell label and stays
    deliberately unpinned: the digits move with the wall clock, and the tray
    and label pixels change with session state. These are session-measured
    platform values (plasmashell on this host, 2026-11-11) no reference
    screenshot shows. This gate is a plain ``unittest.TestCase``, not a
    ``_DialogGate`` subclass: the capture is 640x400 into ``desktop.png``,
    not the shared 480x360 ``dialog.png``, and the desktop is not a dialog
    mode.
    """

    # The leftmost mark's measured rectangle: a 14x10 raised box at
    # x=3..16, y=3..12 (plasma's rendering of the bar's leftmost mark,
    # pinned at the pixel level whatever scale or crop plasma applies to
    # the shipped start-here-kde-symbolic source).
    LEFT_MARK = (3, 3, 14, 10)

    @classmethod
    def setUpClass(cls):
        # All renders run concurrently (see _Renders); this class waits for
        # its own and leaves its siblings' to their own classes.
        cls.stdout, cls.stderr, cls.returncode, cls.directory = (
            _Renders.ensure("desktop")
        )
        cls.output = os.path.join(cls.directory, "desktop.png")
        cls._candidate = None

    @classmethod
    def candidate_image(cls):
        """Return the desktop render decoded once, reused by every read below."""
        if cls._candidate is None:
            cls._candidate = read_png(cls.output)
        return cls._candidate

    def assert_pixel(self, x, y, colour):
        self.assertEqual(
            colour, hex_colour(pixel_at(self.candidate_image(), x, y))
        )

    def test_exits_zero_and_writes_a_640x400_png(self):
        self.assertEqual(0, self.returncode, self.stderr)
        image = self.candidate_image()
        self.assertEqual((640, 400), (image.width, image.height))

    def test_bar_rows_pin_the_platinum_structure(self):
        # The white top row, the two face rows above the mark and the third
        # face row below it (rows 1, 2 and 17), the two bottom rules (the
        # #999999/#000000 pair over the 514-pixel run, its one-shade-lighter
        # #9a9a9a/#020202 tail measured identical in both runs) and the flat
        # desktop area below the bar (rows 20..399, the wallpaper staying
        # out of the series as part 1/2 recorded).
        for x in range(640):
            self.assert_pixel(x, 0, "#FFFFFF")
        for y in (1, 2, 17):
            for x in range(640):
                self.assert_pixel(x, y, "#DDDDDD")
        for x in range(640):
            self.assert_pixel(x, 18, "#999999" if x <= 513 else "#9A9A9A")
            self.assert_pixel(x, 19, "#000000" if x <= 513 else "#020202")
        for y in range(20, 400):
            for x in range(640):
                self.assert_pixel(x, y, "#CCCCCC")

    def test_left_mark_is_the_raised_box(self):
        # The exact measured pixel map of the 14x10 raised box: a 1px black
        # outline rectangle, a white top/left inner bevel, a #999999
        # bottom/right inner shadow and a flat #dddddd interior. A moved,
        # resized or restyled leftmost mark fails here.
        image = self.candidate_image()
        x0, y0, width, height = self.LEFT_MARK
        expected = {}
        for x in range(width):
            expected[x, 0] = "#000000"
            expected[x, height - 1] = "#000000"
        for y in range(1, height - 1):
            expected[0, y] = "#000000"
            expected[1, y] = "#FFFFFF"  # the white left inner bevel, x=4
            expected[width - 1, y] = "#000000"
            expected[width - 2, y] = "#999999"  # the right inner shadow, x=15
        for x in range(1, width - 2):  # row 4 spans x=4..14 white
            expected[x, 1] = "#FFFFFF"
        for x in range(1, width - 1):  # row 11 spans x=4..15 shadow
            expected[x, height - 2] = "#999999"
        for x in range(2, width - 2):  # the flat interior, x=5..14, y=5..10
            for y in range(2, height - 2):
                expected[x, y] = "#DDDDDD"
        actual = {
            (x, y): hex_colour(pixel_at(image, x0 + x, y0 + y))
            for x in range(width)
            for y in range(height)
        }
        self.assertEqual(expected, actual)

    def test_the_bar_between_the_mark_and_the_right_half_is_empty(self):
        # Every pixel of the empty app-menu and panel-spacer corridor equals
        # the face colour: this kills stray art, a dropped face row or a
        # bevel bleeding into the empty area.
        for y in range(1, 18):
            for x in range(17, 351):
                self.assert_pixel(x, y, "#DDDDDD")

    def test_the_right_half_draws_its_live_content(self):
        # The excluded region must really carry the tray icons, clock digits
        # and shell label, or the exclusion would hide a bar that painted
        # nothing (mirrors the inactive gate's two-state check).
        image = self.candidate_image()
        self.assertTrue(
            any(
                hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
                for x in range(351, 640)
                for y in range(3, 17)
            ),
            "the bar's right half carries no live content",
        )



class TestSplashRender(_PixelPins, unittest.TestCase):
    """The rendered startup splash's Platinum structure, pinned.

    The ``--splash`` capture is a 640x400 PNG the look-and-feel's own
    ``Splash.qml`` paints at 2x of its 240x180 content grid (``unit`` =
    floor(min(640/240, 400/180)) = 2), centred with the content origin at
    (80, 20). The pinned values below were measured on a consecutive pair
    of full ``tools/render_surface.py <scratch>/s.png --splash`` runs on
    this host (2026-11-11, both exit 0, both 640x400): the two captures
    differ only inside the track box x=282..357, y=218..225, where the
    progress fill's extent lives, and a third same-day run's pinned
    regions compared byte-equal to the first's. Every pixel outside the
    bevel box is the flat field colour; the bevel face, the panel's border
    band and inner face, the placeholder logo cell (byte-pinned as
    measured, 56 antialiased inks across its 42 rows) and the wordmark's
    full-strength ink are pinned; the track fill's extent is the
    ``--test`` stage clock's (the splash engine advances one stage every
    2 s, recorded in docs/invariants.md's ``--splash`` row, so the 8 s
    settle captures at stage >= 3) and stays deliberately unpinned beyond
    the twelve leftmost columns, mirroring the desktop gate's clock-digit
    exclusion. This gate is a plain ``unittest.TestCase``, not a
    ``_DialogGate`` subclass: the capture is 640x400 into ``splash.png``,
    not the shared 480x360 ``dialog.png``, and the splash is not a dialog
    mode.
    """

    FIELD_COLOUR = "#63639C"
    BEVEL_COLOUR = "#DDDDDD"
    PANEL_BORDER_COLOUR = "#BFBFBF"
    FACE_COLOUR = "#FFFFFF"
    FILL_COLOUR = "#9B9BEA"

    # The bevel box the content grid paints at 2x: x=222..417, y=82..233.
    BEVEL_BOX = (222, 82, 196, 152)
    # The panel box: x=236..403, y=94..201.
    PANEL_BOX = (236, 94, 168, 108)
    # The panel's inner face: x=240..399, y=98..197.
    PANEL_FACE = (240, 98, 160, 100)
    # The placeholder logo cell: 52x42 at (294, 110) (the 26x21 logo grid
    # rectangle drawn at 2x).
    LOGO_CELL = (294, 110, 52, 42)
    # The wordmark's antialiased band: x=270..368, y=169..187. The glyphs
    # carry 27 full-strength #000000 pixels in the measured runs; the band
    # boundaries, not the count, are what the ink test pins.
    WORDMARK_BAND = (270, 169, 99, 19)
    # The progress track box: x=282..357, y=218..225.
    TRACK_BOX = (282, 218, 76, 8)
    # The pinned fill columns: x=282..293, rows 218..225 (left-anchored;
    # one stage's twelfth of the 76px track is already 12.7px wide, wider
    # than these twelve columns at every stage >= 1).
    TRACK_FILL = (282, 218, 12, 8)

    # The measured pixel map of the logo cell (52 wide, 42 rows), read
    # from the first of the runs named in the class docstring and
    # confirmed byte-equal in the other two. A moved, dropped or resampled
    # logo fails the byte-compare below.
    LOGO_CELL_ROWS = (
        ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
        "#FAFBFE", "#C2CAED", "#8A9ADD", "#667BD3", "#546CCD",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#546CCD", "#667BD3", "#8A9ADD",
        "#C2CAED", "#FAFBFE", "#FFFFFF", "#FFFFFF", "#FFFFFF",
        "#FFFFFF", "#FFFFFF"),
        ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#C4CCEE",
        "#6379D2", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#6379D2", "#C4CCEE", "#FFFFFF", "#FFFFFF",
        "#FFFFFF", "#FFFFFF"),
        ("#FFFFFF", "#FFFFFF", "#FDFDFE", "#9BA9E2", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#9BA9E2", "#FDFDFE",
        "#FFFFFF", "#FFFFFF"),
        ("#FFFFFF", "#FFFFFF", "#9BA9E2", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#9CAAE2",
        "#FFFFFF", "#FFFFFF"),
        ("#FFFFFF", "#C4CCEE", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#C4CCEE", "#FFFFFF"),
        ("#FAFBFE", "#6278D2", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#6379D2", "#FBFBFE"),
        ("#C2CAED", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7186D6",
        "#6B80D4", "#5A72CF", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#C2CAED"),
        ("#8A9ADD", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#5A72CF", "#4C65CB", "#4C65CB",
        "#4C65CB", "#8A9BDD"),
        ("#667BD3", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#6B80D4", "#4C65CB", "#4C65CB",
        "#4C65CB", "#677CD3"),
        ("#546CCD", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7186D6", "#4C65CB", "#4C65CB",
        "#4C65CB", "#546CCD"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4D66CB",
        "#4E66CC", "#4D66CB", "#4F67CC", "#4F67CC", "#4F68CB",
        "#5169CC", "#526ACD", "#536CCD", "#556DCD", "#576ECE",
        "#5970CF", "#5A71CF", "#5D73D0", "#6076D1", "#6378D2",
        "#657BD3", "#697ED3", "#6C81D4", "#7084D5", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C66CB", "#4F67CB",
        "#536CCD", "#586FCE", "#5D74D0", "#6378D2", "#697FD3",
        "#7185D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#5169CD", "#5870CF", "#6177D1", "#6B7FD4",
        "#7285D6", "#7286D6", "#7286D6", "#7286D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4F67CC", "#5870CF", "#647AD2", "#7084D6", "#7286D6",
        "#7286D6", "#7286D6", "#7286D6", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4E67CB", "#5971CF",
        "#687ED3", "#7286D6", "#7286D6", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#566ECE", "#697ED3", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB"),
        ("#546CCD", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#546CCD"),
        ("#667BD3", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#677CD3"),
        ("#8A9ADD", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#8A9BDD"),
        ("#C2CAED", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#C2CAED"),
        ("#FAFBFE", "#6379D2", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#6379D2", "#FBFBFE"),
        ("#FFFFFF", "#C4CCEE", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#C5CDEE", "#FFFFFF"),
        ("#FFFFFF", "#FFFFFF", "#9BA9E2", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#9CAAE2",
        "#FFFFFF", "#FFFFFF"),
        ("#FFFFFF", "#FFFFFF", "#FDFDFE", "#9CAAE2", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#9CAAE2", "#FDFDFE",
        "#FFFFFF", "#FFFFFF"),
        ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#C4CCEE",
        "#6379D2", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#6379D2", "#C4CCEE", "#FFFFFF", "#FFFFFF",
        "#FFFFFF", "#FFFFFF"),
        ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF",
        "#FBFBFE", "#C2CAED", "#8A9BDD", "#677CD3", "#546CCD",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB", "#4C65CB",
        "#4C65CB", "#4C65CB", "#546CCD", "#677CD3", "#8A9BDD",
        "#C2CAED", "#FBFBFE", "#FFFFFF", "#FFFFFF", "#FFFFFF",
        "#FFFFFF", "#FFFFFF"),
    )

    @classmethod
    def setUpClass(cls):
        # All renders run concurrently (see _Renders); this class waits
        # for its own and leaves its siblings' to their own classes.
        cls.stdout, cls.stderr, cls.returncode, cls.directory = _Renders.ensure(
            "splash"
        )
        cls.output = os.path.join(cls.directory, "splash.png")
        cls._candidate = None

    @classmethod
    def candidate_image(cls):
        """Return the splash render decoded once, reused by every read below."""
        if cls._candidate is None:
            cls._candidate = read_png(cls.output)
        return cls._candidate

    def test_exits_zero(self):
        self.assertEqual(0, self.returncode, self.stderr)

    def test_writes_a_640x400_png(self):
        image = self.candidate_image()
        self.assertEqual((640, 400), (image.width, image.height))

    def test_the_field_fills_everything_outside_the_bevel_box(self):
        # Every pixel outside the bevel box equals the field colour: a
        # recoloured field, a stray client surface or a moved content
        # origin fails here.
        image = self.candidate_image()
        bx, by, bw, bh = self.BEVEL_BOX
        for y in range(400):
            for x in range(640):
                if bx <= x < bx + bw and by <= y < by + bh:
                    continue
                self.assertEqual(
                    self.FIELD_COLOUR, hex_colour(pixel_at(image, x, y))
                )

    def test_the_bevel_box_pins_its_face(self):
        # Inside the bevel box, every pixel outside the panel box and the
        # track box equals the bevel colour: a shifted panel or track, a
        # lost bevel arm or stray ink fails here.
        image = self.candidate_image()
        bx, by, bw, bh = self.BEVEL_BOX
        px, py, pw, ph = self.PANEL_BOX
        tx, ty, tw, th = self.TRACK_BOX
        for y in range(by, by + bh):
            for x in range(bx, bx + bw):
                if px <= x < px + pw and py <= y < py + ph:
                    continue
                if tx <= x < tx + tw and ty <= y < ty + th:
                    continue
                self.assertEqual(
                    self.BEVEL_COLOUR, hex_colour(pixel_at(image, x, y))
                )

    def test_the_panel_pins_its_border_and_face(self):
        # The panel's full 4px border band (panel box minus inner face) is
        # one flat colour, and the inner face is white except the logo
        # cell and the wordmark band: a recoloured rule, a collapsed
        # border width or wordmark ink escaping its band fails here.
        image = self.candidate_image()
        px, py, pw, ph = self.PANEL_BOX
        fx, fy, fw, fh = self.PANEL_FACE
        for y in range(py, py + ph):
            for x in range(px, px + pw):
                if fx <= x < fx + fw and fy <= y < fy + fh:
                    continue
                self.assertEqual(
                    self.PANEL_BORDER_COLOUR, hex_colour(pixel_at(image, x, y))
                )
        lx, ly, lw, lh = self.LOGO_CELL
        wx, wy, ww, wh = self.WORDMARK_BAND
        for y in range(fy, fy + fh):
            for x in range(fx, fx + fw):
                if lx <= x < lx + lw and ly <= y < ly + lh:
                    continue
                if wx <= x < wx + ww and wy <= y < wy + wh:
                    continue
                self.assertEqual(
                    self.FACE_COLOUR, hex_colour(pixel_at(image, x, y))
                )

    def test_the_logo_cell_pins_its_art(self):
        # The 52x42 cell byte-compares to the measured map above: a moved,
        # dropped or resampled logo fails here.
        self.assert_band(self.LOGO_CELL, self.LOGO_CELL_ROWS)

    def test_the_wordmark_inks_platinum(self):
        # At least one full-strength black pixel inside the wordmark band:
        # a dropped wordmark fails here. The glyph antialiasing stays
        # unpinned, mirroring the display-digit and title-glyph live-ink
        # checks.
        image = self.candidate_image()
        wx, wy, ww, wh = self.WORDMARK_BAND
        self.assertTrue(
            any(
                hex_colour(pixel_at(image, wx + dx, wy + dy)) == "#000000"
                for dy in range(wh)
                for dx in range(ww)
            ),
            "the wordmark band carries no full-strength black ink",
        )

    def test_the_track_pins_its_left_anchored_fill(self):
        # The fill's leftmost twelve columns are all fill colour: a
        # dropped fill, a right- or centre-anchored fill or a recoloured
        # fill fails here. The fill's extent beyond those columns is the
        # --test stage clock's and stays deliberately unpinned -- the
        # measured pair differed only there, inside the track box.
        image = self.candidate_image()
        fx, fy, fw, fh = self.TRACK_FILL
        for y in range(fy, fy + fh):
            for x in range(fx, fx + fw):
                self.assertEqual(
                    self.FILL_COLOUR, hex_colour(pixel_at(image, x, y))
                )


if __name__ == "__main__":
    unittest.main()
