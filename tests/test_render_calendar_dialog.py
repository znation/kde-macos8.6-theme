"""The calendar dialog gates' rendered pixels, pinned band by band.

``tools/render_surface.py``'s ``--calendar-dialog`` mode is rendered by both
gates here, the locale gate under a hostile caller locale. The shared capture
plumbing lives in ``tests/support/render/``, and the other kdialog
widget gates live in ``tests/test_render_dialog_gates.py``.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.platinum_palette import hex_colour
from support.render.gates import DialogGate
from support.render.skip_guards import (
    assert_gate_skips_only_when_a_tool_is_absent,
    dialog_gate_guard,
)
from tools.png import pixel_at  # noqa: E402


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
class TestCalendarLocaleDialogRender(DialogGate, unittest.TestCase):
    """A hostile caller locale must not move the calendar's day grid.

    The calendar pins describe the Sunday-first grid the measured captures
    show, and the grid's first day of week is the caller shell's locale:
    kdialog derives it from ``LANG``/``LC_*`` (Qt's C locale -- what an
    unset locale gives -- is Monday-first), so a caller without the en_US
    default shifted the whole grid one column left and turned the red-ink
    pins below dark, gray and white (the 2026-11-12 steward failure the
    bug ledger records). The render session therefore pins the
    measurement locale (``tools/render/session.py``), and this render
    starts from a Monday-first caller (``Renders.HOSTILE_ENVIRONMENTS``)
    so a session that leaks the caller's locale again fails here instead
    of on a user's shell.
    """

    KIND = "calendar_locale"

    def test_draws_the_red_sunday_digits_under_a_monday_first_caller(self):
        """Pin the red-ink cores and their white face rows under the hostile caller.

        The same pins ``TestCalendarDialogRender`` holds: a leaked caller
        locale moves every day one column left, so the pinned points read
        the Monday digits' black cores, their antialias grays and the
        white face instead of the #800000 Sunday ink.
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


class TestCalendarDialogGateSkipGuards(unittest.TestCase):
    """The calendar dialog gates skip wherever their render CLI refuses on a tool.

    The shared guard condition and the other widget gates' flags are pinned in
    ``tests/test_render_dialog_gates.py``; this module pins its own gates' flags
    beside the gates they guard.
    """

    def test_the_calendar_dialog_gates_skip_only_when_a_tool_is_absent(self):
        for gate in (TestCalendarDialogRender, TestCalendarLocaleDialogRender):
            with self.subTest(gate=gate.__name__):
                assert_gate_skips_only_when_a_tool_is_absent(self, gate)


if __name__ == "__main__":
    unittest.main()
