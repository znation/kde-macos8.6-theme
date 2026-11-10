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
from support.aurorae_fixtures import AURORAE_DIR, REFERENCE_BOUNDS
from support.cli_fixtures import assert_missing_tool_named, call_main  # noqa: F401
from support.firstboot_lineedit import FIELD_BORDER_RUNS, FIELD_CORNER_PIXELS
from support.kvantum_fixtures import SVG
from support.svg_case import parse_svg
from svg_assertions import render_slices
from support.platinum_palette import (
    BLACK,
    BUTTON_SHADOW,
    FACE,
    WHITE,
    hex_colour,
)
from support.reference_image import read_reference, skip_unless_materialized
from tools import render_session, render_setup, render_surface, render_workflow  # noqa: E402
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
# third consecutive run. The rendered button is the landed push-button
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
# The rendered button is the same landed push-button recipe as the OK pin:
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
# same agreeing pair as the field: the landed push-button arrangement the
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
# The session background is black, so the landed active window.csd outline
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
COMBOBOX_OK_BUTTON = (167, 199, 82, 24)
COMBOBOX_CANCEL_BUTTON = (252, 199, 82, 24)
MENU_ITEM_VIEW = (112, 93, 256, 182)


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

        self.assertEqual(render_setup.CONFIG_FILES, applet_files)
        self.assertEqual(
            render_setup.CONFIG_FILES + ("kdeglobals",), dialog_files
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

    def test_a_failed_kvatum_selection_write_exits_1_and_removes_scratch(self):
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
        self.stub("spectacle", "echo capture shot down; exit 7")
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
# dialog flag requires its own client by name (kdialog for the seven kdialog
# modes, zenity for the GTK mode), and the gates skip when either client
# or any Plasma tool is absent.
DIALOG_REAL_TOOLS = REAL_TOOLS + ("kdialog", "zenity")
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


@unittest.skipIf(
    software_renderer_skip_reason() is not None,
    software_renderer_skip_reason() or "",
)
@unittest.skipUnless(
    all(shutil.which(tool) for tool in REAL_TOOLS),
    "needs kwin_wayland, dbus-run-session, plasmawindowed, spectacle and "
    "plasma-apply-colorscheme on PATH",
)
class TestRender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run the CLI the way `make render` does, as one of _Renders' three
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


class TestDialogGateSkipGuards(unittest.TestCase):
    """The eight dialog gates skip wherever their render CLI would refuse on a tool.

    The dialog render CLI refuses with a missing-tool diagnostic when any
    of the five applet-render tools or the dialog client its requested mode
    opens is absent (kdialog for the seven kdialog modes, zenity for the
    GTK mode), and the eight dialog gates' shared skip guard encodes exactly
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
            TestProgressbarDialogRender,
            TestSliderDialogRender,
            TestTextboxDialogRender,
            TestGtkDialogRender,
        ):
            with self.subTest(gate=gate.__name__):
                self.assertEqual(expected, gate.__unittest_skip__)


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
        ("progressbar", ("--progressbar-dialog",), "dialog.png"),
        ("slider", ("--slider-dialog",), "dialog.png"),
        ("textbox", ("--textbox-dialog",), "dialog.png"),
        ("gtk", ("--gtk-dialog", "--settle", "20"), "dialog.png"),
    )
    directories: dict[str, str] = {}
    results: dict[str, tuple[str, str, int, str]] = {}
    completed = False

    @classmethod
    def ensure(cls, kind):
        """Finish all renders once and return *kind*'s result."""
        if not cls.completed:
            cls.completed = True
            cls._run_all()
            atexit.register(cls._remove_directories)
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
            stdout, stderr = process_runner.finish(started[kind], timeout=150)
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


class _DialogGate:
    """Test scaffolding the eight dialog render gates share.

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

    def assert_pixel(self, x, y, colour):
        self.assertEqual(colour, hex_colour(pixel_at(self.candidate_image(), x, y)))

    def assert_raised_frame(self, rect, *, flat_rows=()):
        """Pin a raised frame's outline/bevel and optional label-free rows."""
        x, y, width, height = rect
        for xx in range(x, x + width):
            self.assert_pixel(xx, y, "#000000")
            self.assert_pixel(xx, y + height - 1, "#000000")
        for yy in range(y + 1, y + height - 1):
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


def _dialog_gate_guard():
    """Return the skip guard the eight dialog render gates share.

    The dialog render CLI needs the same five Plasma tools as the applet
    render plus the client its requested mode opens (it exits 2 with a
    missing-tool diagnostic when one is absent: kdialog for the five
    kdialog modes, zenity for the GTK mode), so the eight dialog gates skip
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
        image = self.candidate_image()
        x, y, width, height = LINEEDIT_DIALOG_FIELD_CROP
        # The reference field's border runs (tests/support/firstboot_lineedit.py)
        # give the arrangement: #999999 shadow row, #000000 outline, #FFFFFF
        # face, then the bottom outline and outer #FFFFFF highlight. The
        # crop's rows are exactly the field's, so an off-by-one row fails.
        expected_rows = (
            ["#999999"] * width,
            ["#000000"] * width,
            *( ["#FFFFFF"] * width for _ in range(height - 4) ),
            ["#000000"] * width,
            ["#FFFFFF"] * width,
        )
        for row, expected in enumerate(expected_rows):
            with self.subTest(row=row):
                self.assertEqual(
                    expected,
                    [
                        hex_colour(pixel_at(image, x + dx, y + row))
                        for dx in range(width)
                    ],
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

    def test_draws_the_ok_button_face_at_the_landed_recipe(self):
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
        self.assert_pixel(x, y + height - 1, "#DDDDDD")

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
        self.assertEqual("#DDDDDD", hex_colour(pixel_at(image, x0 + width - 1, y0)))
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
        image = self.candidate_image()
        x, y, width, height = SLIDER_DIALOG_TROUGH
        for row in range(height):
            if row in (0, height - 1):
                expected = ["#000000"] * width
            else:
                expected = ["#EEEEEE"] * width
            with self.subTest(row=y + row):
                self.assertEqual(
                    expected,
                    [
                        hex_colour(pixel_at(image, x + dx, y + row))
                        for dx in range(width)
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
    landed entry recipe re-derives, the two push-button pins
    (``test_draws_the_action_button_row_cell_1_to_1`` and
    ``test_draws_the_cancel_button_cell_1_to_1``) byte-compare the OK and
    Cancel buttons' cells with the arrangement the landed push-button
    recipe re-derives, and ``test_draws_the_window_shell_edge_cell_1_to_1``
    byte-compares the window's top shell edge strip with the arrangement
    the landed ``window.csd`` outline and ``window, .background`` surface rule
    re-derive (each crop is measured on this host's 480x360
    capture; see the ``## tooling`` row of ``docs/invariants.md``).
    """

    KIND = "gtk"

    def test_draws_the_action_button_row_cell_1_to_1(self):
        # Byte-compare the OK push button's left-hand cell with the
        # arrangement the landed push-button recipe's own constants
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
        # arrangement the landed push-button recipe's own constants
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
        # arrangement the landed recipes' own constants re-derive, never
        # with the capture's own pixels. The strip crosses the window's top
        # edge past the square border-radius: 0 corner's edge column and
        # clear of title glyphs: row 0 is the shell-edge
        # row -- the landed window.csd active outline's 1px #000000 ring
        # (box-shadow: 0 0 0 1px #000000), which the black session
        # background makes continuous with -- and rows 1..11 are the flat
        # #DDDDDD window surface beneath it, painted by the landed
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
        # landed recipe's own constants re-derive, never with the capture's
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


if __name__ == "__main__":
    unittest.main()
