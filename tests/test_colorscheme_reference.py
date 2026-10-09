"""Reference-screenshot anchor tests for the Mac OS 8.6 color scheme.

Each sampled anchor must still be the pixel it was sampled from, tying the
scheme's own value to a retail screenshot rather than only to a hard-coded
string. ``[Colors:Tooltip]`` has no reference screenshot in the set and is
pinned by ``test_colorscheme`` alone.
"""

import os
import sys
import unittest

from colorscheme_fixtures import ROOT, load_scheme
from error_assertions import error_message

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools import png  # noqa: E402

# The retail screenshot the PNG-sourced anchors were sampled from. It is stored
# with Git LFS, so a clone without it skips the anchors sampled from it rather
# than failing `make check`.
REFERENCE_DESKTOP = os.path.join(
    ROOT, "macos8.6-screenshots", "desktop_archiveorg8.6hd.png"
)

# The Setup Assistant list selection (Colors:Selection) was sampled from this
# retail 8.6 PNG. It is stored with Git LFS too.
REFERENCE_FIRSTBOOT = os.path.join(
    ROOT, "macos8.6-screenshots", "firstboot_betawiki.png"
)


class TestReferenceAnchors(unittest.TestCase):
    """Each sampled anchor must still be the pixel it was sampled from.

    ``TestAnchors`` pins the scheme file to hard-coded strings, so it proves
    only that the file is self-consistent: a wrong anchor, or a reference image
    swapped for a different one, passed unnoticed. Each point below was sampled
    from a retail PNG (``desktop_archiveorg8.6hd.png`` for the face/view/chrome
    anchors, ``firstboot_betawiki.png`` for the selection anchor) and is
    asserted against the scheme's own value, so the file and the reference image
    must agree. ``[Colors:Tooltip]`` has no reference screenshot in the set: it
    is a KDE-required semantic role whose value comes from the classic Platinum
    palette, so it stays pinned by ``TestAnchors`` alone.
    """

    @classmethod
    def setUpClass(cls):
        cls.images = {}
        cls.image_errors = {}
        for path in (REFERENCE_DESKTOP, REFERENCE_FIRSTBOOT):
            try:
                cls.images[path] = png.read_png(path)
            except png.PngError as exc:
                # `make check` must not require the Git LFS reference set (that
                # is what `make check-references` is for), so a test whose
                # reference image is not materialized skips instead of failing.
                # Each image loads on its own, so a missing one skips only the
                # anchors sampled from it, not the whole class.
                cls.image_errors[path] = exc

    def pixel(self, path, x, y):
        """Return the RGB pixel at ``(x, y)`` of the reference image at *path*.

        A coordinate outside the image is rejected instead of read: the RGB
        slice would be empty (a bare comparison against ``()``) or, for an
        ``x`` past the row end, wrap to the next row and silently tie the
        anchor to the wrong pixel. Naming the coordinate and the image size
        turns that into a diagnostic.
        """
        if path not in self.images:
            self.skipTest(
                f"{path} is not a materialized PNG: {self.image_errors[path]}"
            )
        image = self.images[path]
        if not (0 <= x < image.width and 0 <= y < image.height):
            raise ValueError(
                f"pixel ({x}, {y}) is outside the {image.width}x{image.height} "
                f"reference image {path}"
            )
        offset = (y * image.width + x) * 3
        return tuple(image.rgb[offset : offset + 3])

    def assert_anchor_at(self, section, key, x, y, path=REFERENCE_DESKTOP):
        value = tuple(
            int(part) for part in load_scheme().get(section, key).split(",")
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

    def test_selection_background(self):
        # The Setup Assistant's list selection is a full-width highlighted row;
        # (200, 63) is inside the first row, clear of its label text.
        self.assert_anchor_at(
            "Colors:Selection",
            "BackgroundNormal",
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
                message = error_message(
                    self, ValueError, self.pixel, REFERENCE_DESKTOP, x, y
                )
                self.assertIn(f"({x}, {y})", message)
                self.assertIn("4x3", message)


if __name__ == "__main__":
    unittest.main()
