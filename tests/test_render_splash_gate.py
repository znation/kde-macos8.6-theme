"""Pixel gate for the headless Plasma render CLI's ``--splash`` capture.

``TestSplashRender`` pins what the splash capture draws: the flat field, the
bevel box, the panel, the logo cell, the wordmark and the track. The splash
client's argv is tested in ``tests/test_render_splash_client.py``, which starts
no session. The applet and desktop gates stay in ``tests/test_render_surface.py``.
"""

from __future__ import annotations

import os
import shutil
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.render import splash_capture_fixtures
from support.platinum_palette import hex_colour
from support.render.candidate_png import CachedCandidatePng
from support.render.pixel_pins import PixelPins
from support.render.renders import Renders
from support.render.skip_guards import (
    SPLASH_REAL_TOOLS,
    software_renderer_skip_reason,
)
from tools.png import pixel_at  # noqa: E402


@unittest.skipIf(
    software_renderer_skip_reason() is not None,
    software_renderer_skip_reason() or "",
)
@unittest.skipUnless(
    all(shutil.which(tool) for tool in SPLASH_REAL_TOOLS),
    "needs kwin_wayland, dbus-run-session, plasmawindowed, spectacle, "
    "plasma-apply-colorscheme and ksplashqml on PATH",
)
class TestSplashRender(CachedCandidatePng, PixelPins, unittest.TestCase):
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

    @classmethod
    def setUpClass(cls):
        # All renders run concurrently (see Renders); this class waits
        # for its own and leaves its siblings' to their own classes.
        cls.stdout, cls.stderr, cls.returncode, cls.directory = Renders.ensure(
            "splash"
        )
        cls.output = os.path.join(cls.directory, "splash.png")
        cls._candidate = None

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
        # The 52x42 cell byte-compares to the measured map in
        # tests/support/render/splash_capture_fixtures.py: a moved, dropped or
        # resampled logo fails here.
        self.assert_band(
            self.LOGO_CELL, splash_capture_fixtures.LOGO_CELL_ROWS
        )

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


# This module's gate waits on the splash render kind; requesting it at import
# time lets it join the shared batch that the applet and desktop gates start
# (see Renders in tests/support/render/renders.py). A skip guard that holds never
# calls ensure, so a host without the tools renders nothing.
Renders.request("splash")


if __name__ == "__main__":
    unittest.main()
