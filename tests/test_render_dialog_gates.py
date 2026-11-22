"""The kdialog widget dialog gates' rendered pixels, pinned gate by gate.

``tools/render_surface.py``'s thirteen ``--*-dialog`` modes open kdialog
clients whose engine-drawn widgets these gates byte-compare with the shipped
Kvantum art: the shared capture plumbing lives in
``tests/support/render/gates.py``, the menu gate in
``tests/test_render_menu_dialog.py``, the radio-list gate in
``tests/test_render_radio_dialog.py``, the line-input gate in
``tests/test_render_lineedit_dialog.py``, the combobox gate in
``tests/test_render_combobox_dialog.py``, the file-dialog gate in
``tests/test_render_file_dialog.py``, the GTK 4 window gate in
``tests/test_render_gtk_dialog.py``, the calendar gates in
``tests/test_render_calendar_dialog.py``, the text-box gate in
``tests/test_render_textbox_dialog.py``, the slider gate in
``tests/test_render_slider_dialog.py``, the progress meter gate in
``tests/test_render_progressbar_dialog.py``, and the applet, desktop and splash
gates in ``tests/test_render_surface.py``.
"""

from __future__ import annotations

import os
import shutil
import unittest
from collections import Counter
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.aurorae_fixtures import AURORAE_DIR, INACTIVE_FRAME_GREY
from support.kvantum_fixtures import SVG
from support.platinum_palette import (
    BLACK,
    FACE,
    INACTIVE_OUTLINE,
    hex_colour,
)
from support.render.gates import (
    DIALOG_REAL_TOOLS,
    REAL_TOOLS,
    SOFTWARE_RENDER_SKIP_REASON,
    DialogGate,
    PixelPins,
    dialog_gate_guard,
    probe_gate_skip,
    software_renderer_skip_reason,
)
from support.svg_case import parse_svg
from svg_assertions import render_slices
from tools import render_surface  # noqa: E402
from tools.png import Image, pixel_at  # noqa: E402


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
class TestDialogGateSkipGuards(unittest.TestCase):
    """The widget gates here share a guard encoding the render CLI's refusals.

    The dialog render CLI refuses with a missing-tool diagnostic when any
    of the five applet-render tools or the dialog client its requested mode
    opens is absent (kdialog for the thirteen kdialog modes, zenity for the
    GTK mode), and these widget gates' shared skip guard encodes that
    condition. The line-input, combobox and menu guards are pinned beside their
    gates in ``tests/test_render_lineedit_dialog.py``,
    ``tests/test_render_combobox_dialog.py`` and
    ``tests/test_render_menu_dialog.py``. These tests fail wherever a guard is removed
    (``AttributeError`` on ``__unittest_skip__``) and where a guard's tool
    list drifts from the render CLI's own requirement list, the local
    literal the guards otherwise all repeat. The widget gates' flags are
    pinned here; ``tests/test_render_file_dialog.py`` and
    ``tests/test_render_gtk_dialog.py`` pin their own gates'.
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
            TestColorDialogRender,
            TestIconDialogRender,
            TestInactiveDialogRender,
            # TestFileDialogRender's and TestGtkDialogRender's flags are
            # pinned beside their gates, in tests/test_render_file_dialog.py
            # and tests/test_render_gtk_dialog.py; the two calendar gates'
            # flags are pinned in tests/test_render_calendar_dialog.py,
            # TestTextboxDialogRender's in tests/test_render_textbox_dialog.py,
            # TestSliderDialogRender's in tests/test_render_slider_dialog.py,
            # and TestProgressbarDialogRender's in
            # tests/test_render_progressbar_dialog.py.
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


def band_colour_summary(image, band, limit=3):
    """Name the most common colours in *band* as ``"#RRGGBB xN"`` items.

    *band* is ``(x, y, width, height)``; the colours are ordered most common
    first, so a failure message shows what the band actually held.
    """
    bx, by, bw, bh = band
    counts = Counter(
        hex_colour(pixel_at(image, x, y))
        for x in range(bx, bx + bw)
        for y in range(by, by + bh)
    )
    return ", ".join(f"{colour} x{n}" for colour, n in counts.most_common(limit))


class TestBandColourSummary(unittest.TestCase):
    """The band summary names the dominant colours, most common first."""

    def test_names_the_dominant_colours_in_order(self):
        # A 2x2 band: three black pixels and one #777777 pixel.
        image = Image(
            2,
            2,
            bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0x77, 0x77, 0x77]),
        )
        self.assertEqual(
            band_colour_summary(image, (0, 0, 2, 2), limit=2),
            "#000000 x3, #777777 x1",
        )

    def test_limit_caps_the_number_of_colours_named(self):
        # A 3x2 band: black x3, #101010 x2, #202020 x1. A limit of 2 keeps
        # the two most common and drops the single #202020 pixel.
        black, mid, low = (0, 0, 0), (0x10, 0x10, 0x10), (0x20, 0x20, 0x20)
        pixels = [black] * 3 + [mid] * 2 + [low]
        image = Image(3, 2, bytes(b for pixel in pixels for b in pixel))
        self.assertEqual(
            band_colour_summary(image, (0, 0, 3, 2), limit=2),
            "#000000 x3, #101010 x2",
        )


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
    # client-edge rectangle, from tools/render/window_rules.py's
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
        found = any(
            hex_colour(pixel_at(image, x, y)) == "#777777"
            for x in range(gx, gx + gw)
            for y in range(gy, gy + gh)
        )
        if not found:
            # Name the colours the band holds: an all-black band is a capture
            # that never drew the title, a different shade is a colour change.
            self.fail(
                "the inactive title has no full-strength text ink; band colours: "
                + band_colour_summary(image, self.GLYPH_BAND)
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


class TestPixelMismatchNamesThePixel(PixelPins, unittest.TestCase):
    """A pixel mismatch's failure message names the pixel's coordinates.

    The shared ``assert_pixel`` reads one pixel of the capture. Its failure
    message must carry the ``(x, y)`` it read, after the standard
    ``'expected' != 'observed'`` text, so a recurrence of an intermittent
    colour mismatch shows where it happened. The reading is replaced with a
    fixed colour here, so no render runs.
    """

    def candidate_image(self):
        return None

    def test_a_matching_pixel_passes(self):
        with mock.patch("support.render.gates.pixel_at", return_value=(0, 0, 0)):
            self.assert_pixel(302, 324, "#000000")

    def test_a_mismatched_pixel_message_names_its_coordinates(self):
        with mock.patch(
            "support.render.gates.pixel_at", return_value=(0xCC, 0xCC, 0xCC)
        ):
            with self.assertRaises(AssertionError) as caught:
                self.assert_pixel(302, 324, "#000000")
        message = str(caught.exception)
        self.assertIn("'#000000' != '#CCCCCC'", message)
        self.assertIn("pixel (302, 324)", message)


if __name__ == "__main__":
    unittest.main()
