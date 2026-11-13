"""Pixel gates for the headless Plasma render CLI's applet, desktop and splash captures.

``tools/render_surface.py`` parses and validates arguments, while
``tools/render_workflow.py`` runs the session through capture and publication.
``tools/render_session.py`` owns scratch-session state and KWin command building,
``tools/render_setup.py`` installs and configures its theme, and
``tools/render_clients.py`` builds the dialog client argv; this module pins
what the CLI's captures draw of the applet window's Aurorae chrome, the
desktop bar and the startup splash. The dialog clients' engine-drawn widgets
are pinned in ``tests/test_render_dialog_gates.py`` and
``tests/test_render_file_dialog.py``, the capture plumbing the three suites
share in ``tests/support/render_gates.py``, the CLI's failure paths against
shell stubs in ``tests/test_render_failure_paths.py``, and the session
script and argument handling without a session in
``tests/test_render_surface_units.py``.
"""

from __future__ import annotations

import os
import shutil
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.aurorae_fixtures import REFERENCE_BOUNDS
from support.platinum_palette import FACE, hex_colour
from support.reference_image import read_reference, skip_unless_materialized
from support.render_gates import (
    REAL_TOOLS,
    PixelPins,
    Renders,
    desktop_gate_guard,
    software_renderer_skip_reason,
)
from tools.fidelity_metrics import compare, crop  # noqa: E402
from tools.png import pixel_at, read_png  # noqa: E402


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


@unittest.skipIf(
    software_renderer_skip_reason() is not None,
    software_renderer_skip_reason() or "",
)
@unittest.skipUnless(
    all(shutil.which(tool) for tool in REAL_TOOLS),
    "needs kwin_wayland, dbus-run-session, plasmawindowed, spectacle and "
    "plasma-apply-colorscheme on PATH",
)
class TestRender(PixelPins, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run the CLI the way `make render` does, as one of Renders'
        # concurrent sessions, with the tool's documented settle default
        # (8s), not a tighter one. The session sleeps for that paint budget
        # and then captures: a loaded host that has not painted the window
        # within the budget has its all-black capture refused by the CLI,
        # which names the settle wait instead of leaving the pixel
        # comparisons below to report unexplained failures. The tool's default
        # is the paint budget it promises; the gate must not render below it.
        cls.stdout, cls.stderr, cls.returncode, cls.directory = Renders.ensure(
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


class TestRenderBudgets(unittest.TestCase):
    def test_gtk_dialog_gets_a_longer_settle_budget(self):
        flags = dict((kind, flags) for kind, flags, _ in Renders.KINDS)["gtk"]
        self.assertIn("--settle", flags)
        settle = flags[flags.index("--settle") + 1]
        self.assertEqual(settle, "20")

    def test_the_inactive_gate_renders_at_the_documented_default_settle(self):
        # The two-window inactive capture rides the same dialog defaults as
        # the kdialog widget gates: its flags in Renders.KINDS carry
        # no --settle argument, so the dialog default paint budget governs
        # and no under-budgeted override can shorten the two-window
        # session's settle. A static pin of the shipped flag list, like the
        # sibling applet pin below.
        flags = dict((kind, flags) for kind, flags, _ in Renders.KINDS)["inactive"]
        self.assertNotIn("--settle", flags)

    def test_the_applet_gate_renders_at_the_documented_default_settle(self):
        # The offline reproduction of the archived slow-check record about the
        # applet render gate: its flags in Renders.KINDS carry no --settle
        # argument at all, so the gate renders at the tool's documented
        # default paint budget (8 s) and cannot under-budget the paint wait
        # the way the removed --settle 3 override did on a loaded host. This
        # is a static pin of the shipped flag list -- a real render session
        # runs in none of it, and the stubbed capture the byte-compare gates
        # exercise is elsewhere; the tool's --settle default is the fixture
        # this pin's flag list keeps out of reach.
        flags = dict((kind, flags) for kind, flags, _ in Renders.KINDS)["applet"]
        self.assertNotIn("--settle", flags)



@desktop_gate_guard()
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
    ``DialogGate`` subclass: the capture is 640x400 into ``desktop.png``,
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
        # All renders run concurrently (see Renders); this class waits for
        # its own and leaves its siblings' to their own classes.
        cls.stdout, cls.stderr, cls.returncode, cls.directory = (
            Renders.ensure("desktop")
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



class TestSplashRender(PixelPins, unittest.TestCase):
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
    ``DialogGate`` subclass: the capture is 640x400 into ``splash.png``,
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
        # All renders run concurrently (see Renders); this class waits
        # for its own and leaves its siblings' to their own classes.
        cls.stdout, cls.stderr, cls.returncode, cls.directory = Renders.ensure(
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


# This module's three gates wait on three render kinds; requesting them at
# import time lets the first gate class to set up start the batch with one
# shared settle budget (see Renders in tests/support/render_gates.py). A
# gate whose skip guard holds never calls ensure, so a host that merely
# lacks the tools, or forces a software renderer, renders nothing.
Renders.request("applet", "desktop", "splash")


if __name__ == "__main__":
    unittest.main()
