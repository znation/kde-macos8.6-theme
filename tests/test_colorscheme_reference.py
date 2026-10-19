"""Reference-screenshot anchor tests for the Mac OS 8.6 color scheme.

Each sampled anchor must still be the pixel it was sampled from, tying the
scheme's own value to a retail screenshot rather than only to a hard-coded
string. ``[Colors:Tooltip]`` has no reference screenshot in the set and is
pinned by ``test_colorscheme`` alone.
"""

import unittest

from support.colorscheme_fixtures import load_scheme
from support.desktoptheme_paths import (
    ARCHIVEORG_MAX_ROWS,
    ARCHIVEORG_REFERENCE,
    FIRSTBOOT_MAX_ROWS,
    FIRSTBOOT_REFERENCE,
    SETUP_MAX_ROWS,
    SETUP_REFERENCE,
)
from support.error_assertions import assert_error_names
from support.reference_image import read_reference, skip_unless_materialized

from tools import png  # noqa: E402

# The retail screenshots the PNG-sourced anchors were sampled from, each
# shared with the other readers of the same screenshot so the reference cache
# decodes it once. All are stored with Git LFS, so a clone without them skips
# the anchors sampled from them rather than failing `make check`.
#
# desktop_archiveorg8.6hd.png grounds the menu-bar face, window view, chrome
# and selection-fill anchors.
REFERENCE_DESKTOP = ARCHIVEORG_REFERENCE
# firstboot_betawiki.png is the Setup Assistant's "Introduction" title
# banner (Colors:Selection): the flat #CCCCFF band at y=61..85, under the
# #000000 rule at y=59 and the #FFFFFF highlight at y=60.
REFERENCE_FIRSTBOOT = FIRSTBOOT_REFERENCE
# setup_emaculation.png is the installer CD window's horizontal scroll bar
# (Colors:View BackgroundAlternate), a flat #EEEEEE trough.
REFERENCE_SCROLLBAR = SETUP_REFERENCE

# The deepest anchor row sampled from each reference, plus one, shared with
# the other readers so each screenshot decodes once. setUpClass decodes only
# these top rows: unfiltering the rest of a large screenshot is the dominant
# cost of the decode, and no anchor reads below this. A new anchor below the
# bound here must raise the matching shared constant, or its pixel read fails
# the out-of-bounds check in ``pixel``.
DESKTOP_ANCHOR_ROWS = ARCHIVEORG_MAX_ROWS  # deepest desktop anchor is (470, 300)
FIRSTBOOT_ANCHOR_ROWS = FIRSTBOOT_MAX_ROWS  # deepest firstboot anchor is (431, 351)
SCROLLBAR_ANCHOR_ROWS = SETUP_MAX_ROWS  # deepest scrollbar anchor is (200, 477)


class TestReferenceAnchors(unittest.TestCase):
    """Each sampled anchor must still be the pixel it was sampled from.

    ``TestAnchors`` pins the scheme file to hard-coded strings, so it proves
    only that the file is self-consistent: a wrong anchor, or a reference image
    swapped for a different one, passed unnoticed. Each point below was sampled
    from a retail PNG (``desktop_archiveorg8.6hd.png`` for the face/view/chrome
    anchors, ``firstboot_betawiki.png`` for the Introduction-banner selection
    anchor,
    ``setup_emaculation.png`` for the scroll-bar trough anchor) and is
    asserted against the scheme's own value, so the file and the reference image
    must agree. ``[Colors:Tooltip]`` has no reference screenshot in the set: it
    is a KDE-required semantic role whose value comes from the classic Platinum
    palette, so it stays pinned by ``TestAnchors`` alone.
    """

    @classmethod
    def setUpClass(cls):
        # The scheme file is read-only for the suite, so parse it once for the
        # class instead of re-reading and re-parsing it per anchor assertion.
        cls.parser = load_scheme()
        cls.images = {}
        cls.image_errors = {}
        for path, max_rows in (
            (REFERENCE_DESKTOP, DESKTOP_ANCHOR_ROWS),
            (REFERENCE_FIRSTBOOT, FIRSTBOOT_ANCHOR_ROWS),
            (REFERENCE_SCROLLBAR, SCROLLBAR_ANCHOR_ROWS),
        ):
            image, error = read_reference(path, max_rows=max_rows)
            if error is not None:
                # `make check` must not require the Git LFS reference set (that
                # is what `make check-references` is for), so a test whose
                # reference image is not materialized skips instead of failing.
                # Each image loads on its own, so a missing one skips only the
                # anchors sampled from it, not the whole class.
                cls.image_errors[path] = error
            else:
                cls.images[path] = image

    def pixel(self, path, x, y):
        """Return the RGB pixel at ``(x, y)`` of the reference image at *path*.

        The bounds check and the byte-slice arithmetic live in
        ``png.pixel_at``, so the same validation serves the splash tests and
        any other sampler; this adds only the skip when the reference image is
        not materialized.
        """
        skip_unless_materialized(self, path, self.image_errors.get(path))
        return png.pixel_at(self.images[path], x, y)

    def assert_anchor_at(self, section, key, x, y, path=REFERENCE_DESKTOP):
        """Assert the scheme's ``section``/``key`` RGB equals *path*'s ``(x, y)``."""
        value = tuple(
            int(part) for part in self.parser.get(section, key).split(",")
        )
        self.assertEqual(
            self.pixel(path, x, y),
            value,
            f"{section}/{key} is {value} in the scheme but "
            f"{self.pixel(path, x, y)} at ({x}, {y}) in {path}",
        )

    def test_menu_bar_face(self):
        # The Platinum menu bar (and the window/button faces it shares) is the
        # flat #DDDDDD band across the top of the screen.
        for section in ("Colors:Window", "Colors:Button", "Colors:Header"):
            with self.subTest(section=section):
                self.assert_anchor_at(section, "BackgroundNormal", 400, 5)

    def test_window_view_background(self):
        # A window's content area is white.
        self.assert_anchor_at("Colors:View", "BackgroundNormal", 470, 300)

    def test_window_chrome_foreground(self):
        # The 1px black rule along the bottom of a window is the chrome
        # foreground (Window/ForegroundNormal).
        self.assert_anchor_at("Colors:Window", "ForegroundNormal", 408, 226)

    def test_view_background_alternate(self):
        # The installer CD window's horizontal scroll bar is a flat #EEEEEE
        # trough between the 1px black rules at y=462 and y=477; (200, 470)
        # is inside it, clear of both rules and of the arrow boxes.
        self.assert_anchor_at(
            "Colors:View",
            "BackgroundAlternate",
            200,
            470,
            path=REFERENCE_SCROLLBAR,
        )

    def test_selection_background(self):
        # The Setup Assistant's "Introduction" title banner is a flat #CCCCFF
        # band spanning roughly x=31..428, y=61..85, under the #000000 rule at
        # y=59 and the #FFFFFF highlight at y=60. Pin the fill flat across the
        # band, at points clear of its text.
        for x, y in ((100, 63), (200, 63), (300, 63), (200, 80)):
            with self.subTest(x=x, y=y):
                self.assert_anchor_at(
                    "Colors:Selection",
                    "BackgroundNormal",
                    x,
                    y,
                    path=REFERENCE_FIRSTBOOT,
                )
        # The scheme sets BackgroundAlternate to the same fill.
        self.assert_anchor_at(
            "Colors:Selection",
            "BackgroundAlternate",
            200,
            63,
            path=REFERENCE_FIRSTBOOT,
        )

    def test_missing_reference_skips_only_its_own_anchor(self):
        # A reference that failed to load must skip only the anchors sampled
        # from it; the other reference stays usable.
        self.images = {
            REFERENCE_DESKTOP: png.Image(1, 1, bytes([221, 221, 221]))
        }
        self.image_errors = {REFERENCE_FIRSTBOOT: png.PngError("missing")}
        self.assertEqual(self.pixel(REFERENCE_DESKTOP, 0, 0), (221, 221, 221))
        with self.assertRaises(unittest.SkipTest):
            self.pixel(REFERENCE_FIRSTBOOT, 0, 0)

    def test_out_of_bounds_anchor_coordinate_is_rejected(self):
        # An anchor coordinate outside the reference must not be read: the
        # byte slice would be empty, and an x past the row end would wrap to
        # the next row and tie the anchor to the wrong pixel. Pin that it is
        # rejected with the coordinate and the image size.
        self.images = {REFERENCE_DESKTOP: png.Image(4, 3, bytes(4 * 3 * 3))}
        self.image_errors = {}
        for x, y in ((4, 0), (0, 3), (-1, 0), (0, -1)):
            with self.subTest(x=x, y=y):
                assert_error_names(
                    self,
                    ValueError,
                    self.pixel,
                    REFERENCE_DESKTOP,
                    x,
                    y,
                    needles=(f"({x}, {y})", "4x3"),
                )


if __name__ == "__main__":
    unittest.main()
