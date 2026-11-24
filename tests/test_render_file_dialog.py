"""The file-dialog gate's rendered KIO chooser, pinned region by region.

``tools/render_surface.py``'s ``--file-dialog`` mode opens a kdialog file
chooser whose engine-drawn frame, title bar and widgets this gate pins; the
shared capture plumbing lives in ``tests/support/render/gates.py``, the
thirteen kdialog widget gates in ``tests/test_render_dialog_gates.py``, the
calendar gates in ``tests/test_render_calendar_dialog.py``, and
the applet, desktop and splash gates in ``tests/test_render_surface.py``.
"""

from __future__ import annotations

import os
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.aurorae_fixtures import AURORAE_DIR
from support.render import file_dialog_chrome_fixtures as chrome_fixtures
from support.render import file_dialog_list_fixtures as list_fixtures
from support.render import file_dialog_sidebar_fixtures as sidebar_fixtures
from support.platinum_palette import hex_colour
from support.render.gates import (
    DialogGate,
    assert_gate_skips_only_when_a_tool_is_absent,
    dialog_gate_guard,
)
from support.svg_case import parse_svg
from svg_assertions import render_slices
from tools.png import pixel_at  # noqa: E402



@dialog_gate_guard()
class TestFileDialogRender(DialogGate, unittest.TestCase):
    """The KIO file chooser ``--file-dialog`` captures, region by region.

    The chooser capture lands in the shared 480x360 ``dialog.png`` (the
    dialog default size, like the kdialog widget gates), so this gate is a
    ``DialogGate`` subclass waiting on the ``file_dialog`` render. The
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
    icon theme's rendering, pinned as measured. The measured pixel maps
    live in ``tests/support/render/file_dialog_chrome_fixtures.py`` (the
    icon box), ``tests/support/render/file_dialog_list_fixtures.py`` (the
    sort arrow and the list panel) and
    ``tests/support/render/file_dialog_sidebar_fixtures.py`` (the sidebar).

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
    # The centered title's glyph band over the pinstripes. The rendered
    # title sits on a flat #CCCCCC field the decoration engine draws behind
    # the live text; after ChicagoFLF was selected for active titles
    # (2026-11-12) that field spans x=211..247, rows 7..18, measured from
    # three agreeing renders of this gate (the pre-ChicagoFLF ink was
    # x=217..240, rows 9..18). The pinstripe rows carry the title's live
    # ink here, so the band is excluded from the stripe pin, not from the
    # band's stripes elsewhere.
    TITLE_BAND = (211, 7, 247, 18)  # x0, y0, x1, y1

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
    SORT_ARROW_RECT = (336, 106)

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
    # The two device entries' 40x26 drive icon cells at (14, 202) and
    # (14, 254): both are pinned by the one drive-cell map in
    # ``tests/support/render/file_dialog_sidebar_fixtures.py``. Their live-label bands (ink
    # measured inside x=63..119, rows 206..215 and 258..267) sit beside
    # them; the glyphs themselves stay unpinned.
    DRIVE_CELLS = ((14, 202), (14, 254))
    DEVICE_LABEL_BANDS = ((62, 119, 206, 215), (62, 119, 258, 267))
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
        self.assert_band((4, 7, 13, 13), chrome_fixtures.ICON_BOX_ROWS)
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
        self.assert_band(
            (x0, y0, width, height), sidebar_fixtures.FOLDER_CELL_ROWS
        )
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
                self.assert_band(
                    (x0, y0, 40, 26), sidebar_fixtures.DRIVE_CELL_ROWS
                )

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
        arrow_width, arrow_height = len(list_fixtures.SORT_ARROW[0]), len(list_fixtures.SORT_ARROW)
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
             len(list_fixtures.SORT_ARROW[0]), len(list_fixtures.SORT_ARROW)),
            list_fixtures.SORT_ARROW,
        )

    def test_the_list_rows_pin_their_band_faces(self):
        # The three seeded file rows: rows 123..142 and 163..182 face
        # #FFFFFF, rows 143..162 the #EEEEEE alternate-row trough, each
        # pinned across x=152..473 except the measured icon cell and name/size
        # text rectangles (ROW_BANDS) and the clock-dependent date band
        # (x=395..473, live ink demanded instead). Rows 183..251, the empty
        # rows below the listing, are flat #FFFFFF: a lost alternate-row
        # trough, a stray paint or art in the empty rows fails here.
        for start, face, rects in list_fixtures.ROW_BANDS:
            with self.subTest(row_band=start):
                self._pin_row_band(start, face, rects)

    def _pin_row_band(self, start, face, rects):
        """Pin one row band's face across its span, skipping pinned rects."""
        for y in range(start, start + list_fixtures.ROW_BAND_HEIGHT):
            for x in range(152, 474):
                if any(a <= x <= b and c <= y <= d for a, b, c, d in rects):
                    continue
                if 395 <= x <= 473:
                    continue
                self.assert_pixel(x, y, face)
        image = self.candidate_image()
        for start, face, _ in list_fixtures.ROW_BANDS:
            with self.subTest(date_ink=start):
                self.assertTrue(
                    any(
                        hex_colour(pixel_at(image, x, y)) != face
                        for x in range(395, 474)
                        for y in range(start, start + list_fixtures.ROW_BAND_HEIGHT)
                    ),
                    "the date column draws no ink",
                )
        for y in range(list_fixtures.EMPTY_ROWS[0], list_fixtures.EMPTY_ROWS[1] + 1):
            for x in range(152, 474):
                self.assert_pixel(x, y, "#FFFFFF")

    def test_the_file_rows_draw_their_type_icons(self):
        # The three type-icon cells, byte-pinned to their measured pixel
        # maps (rows 1 and 2 the fallback theme's document glyph against
        # its row's own face colour, row 3 the distinct blue-ruled RTF
        # glyph): a shifted cell, a dropped icon or a resampled glyph
        # fails the byte-compare.
        for x0, y0, width, height, rows in list_fixtures.ICON_CELLS:
            with self.subTest(icon_cell=(x0, y0)):
                self.assert_band((x0, y0, width, height), rows)

    def test_the_file_rows_ink_their_columns(self):
        # Each seeded row must really draw its listing: at least one pixel
        # off the row's face inside the name, size and date bands. A
        # dropped listing or an emptied date cell fails here.
        image = self.candidate_image()
        for start, face, _ in list_fixtures.ROW_BANDS:
            for x0, x1 in list_fixtures.ROW_TEXT_BANDS:
                with self.subTest(row_column=(start, x0)):
                    self.assertTrue(
                        any(
                            hex_colour(pixel_at(image, x, y)) != face
                            for x in range(x0, x1 + 1)
                            for y in range(start, start + list_fixtures.ROW_BAND_HEIGHT)
                        ),
                        "the file row draws no ink in one of its columns",
                    )


class TestFileDialogGateSkipGuards(unittest.TestCase):
    """The file-dialog gate skips wherever its render CLI refuses on a tool.

    The shared guard condition and the widget gates' flags are pinned in
    ``tests/test_render_dialog_gates.py``, ``tests/test_render_calendar_dialog.py``
    and ``tests/test_render_gtk_dialog.py`` pins the GTK 4 gate's; this module pins its
    own gate's flag beside the gate it guards.
    """

    def test_the_file_dialog_gate_skips_only_when_a_tool_is_absent(self):
        assert_gate_skips_only_when_a_tool_is_absent(self, TestFileDialogRender)


if __name__ == "__main__":
    unittest.main()
