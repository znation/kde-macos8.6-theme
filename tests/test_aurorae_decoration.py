"""Tests for the org.macos8.desktop Aurorae window decoration.

The decoration package itself (metadata, install lifecycle) and the artwork the
Aurorae engine draws: the active `decoration` nine-slice and the close/zoom
widget SVGs. Every sampled value is re-derived from
`macos8.6-screenshots/aboutsystem_betawiki.png` through `tools/png.py`, so a
theme that drifts from the reference fails here. The reference is stored with
Git LFS, so a clone without it skips the artwork tests rather than failing
`make check`.
"""

from __future__ import annotations

import gzip
import os
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from install_failure_cases import FailedInstallPreservesPackage
from install_lifecycle_cases import InstallLifecycleCases
from kde_config import read as read_kde_config
from kpackage_install_case import KPackageInstallCase
from nine_slice_case import NineSliceCase
from package_metadata import kplugin, load_metadata
from svg_assertions import (
    assert_no_script_elements,
    assert_root_canvas,
    assert_unique_ids,
    render_slices,
)
from theme_install import (
    ROOT,
    install,
    installed_aurorae_dir,
    installed_aurorae_theme,
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools import png  # noqa: E402


AURORAE_ID = "org.macos8.desktop"
AURORAE_DIR = os.path.join(ROOT, "theme", "aurorae", "themes", AURORAE_ID)
RC = os.path.join(AURORAE_DIR, AURORAE_ID + "rc")
DECORATION_SVG = os.path.join(AURORAE_DIR, "decoration.svg")
CLOSE_SVG = os.path.join(AURORAE_DIR, "close.svg")
MAXIMIZE_SVG = os.path.join(AURORAE_DIR, "maximize.svg")
RESTORE_SVG = os.path.join(AURORAE_DIR, "restore.svg")
METADATA = os.path.join(AURORAE_DIR, "metadata.json")
METADATA_DESKTOP = os.path.join(AURORAE_DIR, "metadata.desktop")
DECORATION_SVGZ = os.path.join(AURORAE_DIR, "decoration.svgz")

REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "aboutsystem_betawiki.png"
)
# The deepest reference row this module reads is the bottom border at y=424.
REFERENCE_ROWS = 425


def _hex(rgb):
    return "#%02X%02X%02X" % rgb


def _kde(rgb):
    return ",".join(str(channel) for channel in rgb)


class ReferenceImageCase:
    """Mixin: load the reference once and skip when it is not materialized.

    ``make check`` must not require the Git LFS reference set (that is what
    ``make check-references`` is for), so a test whose reference image is not
    materialized skips instead of failing. It is a plain mixin, not a
    `TestCase`, so importing it does not collect an unconfigured base.
    """

    image = None
    image_error = None

    @classmethod
    def setUpClass(cls):
        try:
            cls.image = png.read_png(REFERENCE, max_rows=REFERENCE_ROWS)
        except png.PngError as exc:
            cls.image = None
            cls.image_error = exc

    def reference_pixel(self, x, y):
        if self.image is None:
            self.skipTest(
                f"{REFERENCE} is not a materialized PNG: {self.image_error}"
            )
        return png.pixel_at(self.image, x, y)


class TestMetadata(unittest.TestCase):
    def test_metadata_identifies_the_aurorae_package(self):
        metadata = load_metadata(METADATA)
        self.assertEqual(metadata["KPackageStructure"], "KWin/Aurorae")
        plugin = kplugin(metadata, METADATA)
        self.assertEqual(plugin["Id"], AURORAE_ID)
        self.assertEqual(plugin["Name"], "Mac OS 8.6")
        self.assertEqual(plugin["License"], "GPL-2.0-or-later")

    def test_metadata_desktop_names_the_theme(self):
        # KWin 6.3.6's Aurorae SVG-theme discovery
        # (`ThemeProvider::findAllSvgThemes`) lists only theme directories that
        # contain a `metadata.desktop`, and reads its `Name` for the visible
        # name. Without it the decoration is never offered in System Settings.
        parser = read_kde_config(METADATA_DESKTOP)
        self.assertEqual(parser.get("Desktop Entry", "Name"), "Mac OS 8.6")


class TestInstall(
    FailedInstallPreservesPackage, InstallLifecycleCases, unittest.TestCase
):
    KIND = "aurorae"
    PACKAGE_ID = AURORAE_ID
    PACKAGE_DIR = AURORAE_DIR
    INSTALLED_FILES = (
        "metadata.json",
        "metadata.desktop",
        "org.macos8.desktoprc",
        "decoration.svg",
        "decoration.svgz",
        "close.svg",
        "maximize.svg",
        "restore.svg",
    )
    COPY_FAILURE_GLOB = "*/aurorae/themes/*"

    def installed_parent(self, tmp):
        return installed_aurorae_dir(tmp)

    def installed_package_dir(self, tmp):
        return installed_aurorae_theme(tmp, self.PACKAGE_ID)


class TestRc(ReferenceImageCase, unittest.TestCase):
    def setUp(self):
        self.parser = read_kde_config(RC)

    def _title_bar_height(self):
        """Return the black->black title-bar run at a clear column x=250."""
        column = [self.reference_pixel(250, y) for y in range(20, 60)]
        blacks = [20 + i for i, colour in enumerate(column) if colour == (0, 0, 0)]
        first = blacks[0]
        second = next(y for y in blacks if y > first + 1)
        return second - first + 1

    def _side_border_thickness(self):
        """Return the black->black side-border run at a clear row y=100."""
        row = [self.reference_pixel(x, 100) for x in range(0, 16)]
        blacks = [i for i, colour in enumerate(row) if colour == (0, 0, 0)]
        first = blacks[0]
        second = next(x for x in blacks if x > first + 1)
        return second - first + 1

    def _bottom_border_thickness(self):
        """Return the black->black bottom-border run at a clear column x=250."""
        column = [self.reference_pixel(250, y) for y in range(417, 425)]
        blacks = [417 + i for i, colour in enumerate(column) if colour == (0, 0, 0)]
        first = blacks[0]
        second = next(y for y in blacks if y > first + 1)
        return second - first + 1

    def _close_box_size(self):
        """Return the (width, height) of the close box's #888888 bounding box."""
        points = [
            (x, y)
            for y in range(26, 44)
            for x in range(8, 26)
            if self.reference_pixel(x, y) == (136, 136, 136)
        ]
        xs = [x for x, _ in points]
        ys = [y for _, y in points]
        return max(xs) - min(xs) + 1, max(ys) - min(ys) + 1

    def test_layout_metrics_match_reference(self):
        layout = "Layout"
        title_height = self._title_bar_height()
        side = self._side_border_thickness()
        bottom = self._bottom_border_thickness()
        box_w, box_h = self._close_box_size()
        self.assertEqual(int(self.parser.get(layout, "TitleHeight")), title_height)
        self.assertEqual(int(self.parser.get(layout, "BorderTop")), title_height)
        self.assertEqual(int(self.parser.get(layout, "BorderLeft")), side)
        self.assertEqual(int(self.parser.get(layout, "BorderRight")), side)
        self.assertEqual(int(self.parser.get(layout, "BorderBottom")), bottom)
        self.assertEqual(int(self.parser.get(layout, "ButtonWidth")), box_w)
        self.assertEqual(int(self.parser.get(layout, "ButtonHeight")), box_h)

    def test_title_bar_colours_match_reference(self):
        # The pinstripe field is uniform along the bar, so one clear column
        # pins it: local y = reference y - 25.
        samples = {
            2: self.reference_pixel(250, 27),
            4: self.reference_pixel(250, 29),
            5: self.reference_pixel(250, 30),
        }
        top = render_slices(ET.parse(DECORATION_SVG))["decoration-top"]
        for local_y, colour in samples.items():
            self.assertEqual(top[(0, local_y)], _hex(colour), local_y)

    def test_caption_colour_matches_reference(self):
        # ActiveTextColor is the caption glyph colour; (198, 30) is inside a
        # glyph stroke of the "About This Computer" caption.
        glyph = self.reference_pixel(198, 30)
        self.assertEqual(glyph, (0, 0, 0))
        self.assertEqual(self.parser.get("General", "ActiveTextColor"), _kde(glyph))


class TestDecorationSvg(NineSliceCase, unittest.TestCase):
    SVG_PATH = DECORATION_SVG
    PREFIXES = ("decoration",)

    def test_root_canvas(self):
        assert_root_canvas(self, self.tree, 18, 34)

    def test_unique_ids(self):
        assert_unique_ids(self, self.tree)

    def test_svgz_is_the_compressed_svg(self):
        # `kpackagetool6 -t KWin/Aurorae` requires `decoration.svgz`, while the
        # Aurorae runtime prefers the uncompressed `decoration.svg`; pin that
        # the compressed copy cannot drift from the artwork under test.
        with open(DECORATION_SVG, "rb") as handle:
            uncompressed = handle.read()
        with gzip.open(DECORATION_SVGZ, "rb") as compressed:
            self.assertEqual(compressed.read(), uncompressed)


class TestCorners(ReferenceImageCase, unittest.TestCase):
    """Each corner slice reproduces the reference frame.

    The only pixels skipped are the exact 12x12 close/zoom button footprints
    the Aurorae engine draws over the frame: the close box at
    TitleEdgeLeft=4 / ButtonMarginTop=4 covers frame-local x=4..15, y=4..15
    (the top-left corner's x=4,5), and the zoom box at TitleEdgeRight=5 has
    its right edge at frame-local x = width - 6, covering the top-right
    corner's x=0 only. Every other corner pixel is compared.
    """

    BUTTON_MASK = {
        "decoration-topleft": {(x, y) for x in (4, 5) for y in range(4, 16)},
        "decoration-topright": {(0, y) for y in range(4, 16)},
    }
    REGIONS = {
        "decoration-topleft": (7, 25, 6, 22),
        "decoration-topright": (354, 25, 6, 22),
        "decoration-bottomleft": (7, 419, 6, 6),
        "decoration-bottomright": (354, 419, 6, 6),
    }

    def test_corners_match_reference(self):
        slices = render_slices(ET.parse(DECORATION_SVG))
        for name, (x0, y0, width, height) in self.REGIONS.items():
            mask = self.BUTTON_MASK.get(name, set())
            with self.subTest(slice=name):
                for y in range(height):
                    for x in range(width):
                        if (x, y) in mask:
                            continue
                        self.assertEqual(
                            slices[name][(x, y)],
                            _hex(self.reference_pixel(x0 + x, y0 + y)),
                            (x, y),
                        )


class TestButtons(ReferenceImageCase, unittest.TestCase):
    def test_close_box_matches_reference(self):
        expected = {
            (x, y): _hex(self.reference_pixel(11 + x, 29 + y))
            for y in range(12)
            for x in range(12)
        }
        slices = render_slices(ET.parse(CLOSE_SVG))
        self.assertEqual(slices["active-center"], expected)

    def test_zoom_box_matches_reference(self):
        # The reference's zoom box (x=343..354) differs from its close box: it
        # carries an inner #222222 glyph. Pin every pixel against the zoom box.
        expected = {
            (x, y): _hex(self.reference_pixel(343 + x, 29 + y))
            for y in range(12)
            for x in range(12)
        }
        for path in (MAXIMIZE_SVG, RESTORE_SVG):
            with self.subTest(svg=os.path.basename(path)):
                slices = render_slices(ET.parse(path))
                self.assertEqual(slices["active-center"], expected)

    def test_zoom_glyph_is_the_reference_glyph(self):
        # Pin the glyph itself, not only the whole-box comparison: two
        # horizontal #222222 bars at local y=5 and y=7 spanning x=2..10.
        zoom = render_slices(ET.parse(MAXIMIZE_SVG))["active-center"]
        close = render_slices(ET.parse(CLOSE_SVG))["active-center"]
        glyph = {
            (x, y)
            for y in range(12)
            for x in range(12)
            if zoom[(x, y)] != close[(x, y)]
        }
        expected = {(x, y) for x in range(2, 11) for y in (5, 7)}
        self.assertEqual(glyph, expected)
        for x, y in sorted(glyph):
            self.assertEqual(
                zoom[(x, y)],
                _hex(self.reference_pixel(343 + x, 29 + y)),
                (x, y),
            )

    def test_button_svgs_are_self_contained(self):
        for path in (CLOSE_SVG, MAXIMIZE_SVG, RESTORE_SVG):
            with self.subTest(svg=os.path.basename(path)):
                tree = ET.parse(path)
                assert_unique_ids(self, tree)
                assert_no_script_elements(self, tree)


@unittest.skipUnless(shutil.which("kpackagetool6"), "needs kpackagetool6")
class TestPackageValid(KPackageInstallCase, unittest.TestCase):
    KPACKAGETOOL_TYPE = "KWin/Aurorae"
    PACKAGE_DIR = AURORAE_DIR
    PACKAGE_ID = AURORAE_ID


if __name__ == "__main__":
    unittest.main()
