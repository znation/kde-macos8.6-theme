"""Tests for the org.macos8.desktop Aurorae window decoration.

The decoration package itself (metadata, install lifecycle) and the artwork the
Aurorae engine draws: the active `decoration` nine-slice, the inactive
`decoration-inactive` nine-slice, and the close/zoom widget SVGs with their
active and inactive states. Every sampled value is re-derived from
`macos8.6-screenshots/aboutsystem_betawiki.png` through `tools/png.py`, so a
theme that drifts from the reference fails here. The inactive greys are
KDE-required provenance (the reference set has no inactive window) and are
pinned against the active artwork they grey. The reference is stored with
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
from package_metadata import assert_named_authors, kplugin, load_metadata
from reference_image import skip_unless_materialized
from svg_assertions import (
    SLICE_IDS,
    assert_ids_present,
    assert_no_script_elements,
    assert_root_canvas,
    assert_slice_pixels,
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

# The three Aurorae button SVGs: the close widget on the left, and the
# maximize and restore states of the zoom widget on the right.
BUTTON_SVGS = (CLOSE_SVG, MAXIMIZE_SVG, RESTORE_SVG)
ZOOM_SVGS = (MAXIMIZE_SVG, RESTORE_SVG)

REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "aboutsystem_betawiki.png"
)
# The deepest reference row this module reads is the bottom border at y=424.
REFERENCE_ROWS = 425


def _hex(rgb):
    return "#%02X%02X%02X" % rgb


def _parsed_svgs(paths):
    """Return each SVG in *paths* as a ``(basename, parsed tree)`` pair.

    The button tests parse one or more of the button SVGs and label each
    subTest with the file's basename; pairing the name and the tree here keeps
    that parse-and-label step in one place.
    """
    return [(os.path.basename(path), ET.parse(path)) for path in paths]


def _kde(rgb):
    return ",".join(str(channel) for channel in rgb)


def _black_run_length(colours, start=0):
    """Return the length of the first black->black run in *colours*.

    *colours* are RGB triples sampled at consecutive coordinates beginning at
    *start*; the run spans the first black pixel through the next black pixel
    after a gap.
    """
    blacks = [
        start + i
        for i, colour in enumerate(colours)
        if colour == (0, 0, 0)
    ]
    first = blacks[0]
    second = next(index for index in blacks if index > first + 1)
    return second - first + 1


def _rect_fills(tree, group_id):
    """Return every rect fill inside the ``<g id=group_id>`` of *tree*.

    ``render_slices`` reads the composited pixels, so a rect that a later rect
    overpaints is invisible there; the inactive-state checks read the rects'
    own fills to pin that no ``#FFFFFF``/``#777777`` rect survives at all.
    """
    for element in tree.iter():
        if element.get("id") == group_id:
            return [child.get("fill") for child in element]
    raise AssertionError(f"no element with id {group_id!r}")


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
        skip_unless_materialized(self, REFERENCE, self.image_error)
        return png.pixel_at(self.image, x, y)

    def reference_box(self, x0, y0, size=12):
        """Return a *size* x *size* reference region as {(x, y): '#RRGGBB'}.

        The keys are the region-local coordinates (0, 0)..(*size*-1,
        *size*-1), so the map can be compared directly against a rendered
        slice. Used for the two 12x12 button boxes.
        """
        return {
            (x, y): _hex(self.reference_pixel(x0 + x, y0 + y))
            for y in range(size)
            for x in range(size)
        }


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

    def test_metadata_desktop_matches_metadata_json(self):
        # metadata.json and metadata.desktop describe the same package to two
        # consumers -- KPackage and System Settings read the JSON, KWin's
        # Aurorae discovery reads the desktop file -- so their shared identity
        # fields must agree. Name is pinned on each file already, but nothing
        # checks the two files agree, and Version is pinned nowhere, so a
        # version bump that updates only one file would leave the two views
        # disagreeing silently. X-KDE-PluginInfo-Name is the KPlugin identity
        # (the theme directory name, the `org.macos8.desktoprc` stem and the id
        # the global theme's `[kwinrc]` defaults point KWin at), so pin it to
        # AURORAE_ID as well. The desktop file's `Comment` is the KPlugin
        # `Description` shown to the user, so a description edit that touches
        # only one file would show two different texts for one package.
        plugin = kplugin(load_metadata(METADATA), METADATA)
        parser = read_kde_config(METADATA_DESKTOP)
        for key, expected in (
            ("X-KDE-PluginInfo-Name", AURORAE_ID),
            ("X-KDE-PluginInfo-Version", plugin.get("Version")),
            ("X-KDE-PluginInfo-License", plugin.get("License")),
            ("Comment", plugin.get("Description")),
        ):
            self.assertEqual(
                parser.get("Desktop Entry", key),
                expected,
                f"{METADATA_DESKTOP}: {key} must match {METADATA}",
            )
        # The desktop file's `X-KDE-PluginInfo-Author` is one string; the JSON
        # `KPlugin.Authors` is the list KDE's About dialog reads. Both name the
        # package's author, so the desktop file's name must be one of them, or
        # the two consumers disagree. `assert_named_authors` validates the list
        # shape first (nothing else checks the Aurorae metadata.json's Authors)
        # and returns the names it accepted.
        authors = assert_named_authors(self, plugin.get("Authors"), METADATA)
        self.assertIn(
            parser.get("Desktop Entry", "X-KDE-PluginInfo-Author"),
            authors,
            f"{METADATA_DESKTOP}: X-KDE-PluginInfo-Author must name one of "
            f"{METADATA}'s KPlugin.Authors",
        )


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
        return _black_run_length(column, 20)

    def _side_border_thickness(self):
        """Return the black->black side-border run at a clear row y=100."""
        row = [self.reference_pixel(x, 100) for x in range(0, 16)]
        return _black_run_length(row)

    def _bottom_border_thickness(self):
        """Return the black->black bottom-border run at a clear column x=250."""
        column = [self.reference_pixel(250, y) for y in range(417, 425)]
        return _black_run_length(column, 417)

    def _frame_edges(self):
        """Return the frame's (left, right, top) reference coordinates.

        At the title bar's top row (y=25) the black outline spans the frame's
        full width, so its first and last black pixels are the outer left and
        right edges; the first black pixel down the clear column x=250 is the
        outer top edge. These are the edges the button offsets are measured
        from.
        """
        top_row = [self.reference_pixel(x, 25) for x in range(0, 400)]
        blacks = [x for x, colour in enumerate(top_row) if colour == (0, 0, 0)]
        column = [self.reference_pixel(250, y) for y in range(20, 60)]
        top = 20 + next(
            i for i, colour in enumerate(column) if colour == (0, 0, 0)
        )
        return blacks[0], blacks[-1], top

    def _box_bounds(self, x0, x1):
        """Return the (x, y, width, height) of a #888888 button face.

        The close and zoom boxes are the only #888888 faces in this band of
        the title bar; ``x0`` and ``x1`` bound the columns searched so each
        box's bounds are measured from its own face.
        """
        points = [
            (x, y)
            for y in range(26, 44)
            for x in range(x0, x1)
            if self.reference_pixel(x, y) == (136, 136, 136)
        ]
        xs = [x for x, _ in points]
        ys = [y for _, y in points]
        return min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1

    def _close_box_size(self):
        """Return the (width, height) of the close box's #888888 bounding box."""
        _, _, width, height = self._box_bounds(8, 26)
        return width, height

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

    def test_button_offsets_match_reference(self):
        # The close and zoom boxes are drawn over the frame at the offsets the
        # rc names: Aurorae anchors the left button group TitleEdgeLeft from
        # the frame's left edge and the right group TitleEdgeRight from its
        # right edge, both ButtonMarginTop below the frame's top edge, and the
        # decoration declares no padding hints, so those rc values are the
        # boxes' frame-local offsets. Re-deriving them from the reference is
        # what pins the rc to the artwork instead of trusting it.
        layout = "Layout"
        left, right, top = self._frame_edges()
        close_x, close_y, _, _ = self._box_bounds(8, 26)
        zoom_x, zoom_y, zoom_w, _ = self._box_bounds(338, 360)
        self.assertEqual(close_y, zoom_y)
        self.assertEqual(
            int(self.parser.get(layout, "TitleEdgeLeft")), close_x - left
        )
        self.assertEqual(
            int(self.parser.get(layout, "TitleEdgeRight")),
            right - (zoom_x + zoom_w - 1),
        )
        self.assertEqual(
            int(self.parser.get(layout, "ButtonMarginTop")), close_y - top
        )

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


class TestDecorationSvg(ReferenceImageCase, NineSliceCase, unittest.TestCase):
    SVG_PATH = DECORATION_SVG
    PREFIXES = ("decoration", "decoration-inactive")
    # The inactive frame paints its own tiles but declares no margin hints of
    # its own: KSvg looks up `decoration-inactive-hint-*-margin`, finds none
    # and falls back to the `decoration-inactive-*` element sizes, which
    # mirror the active tiles. So its tiles are placed by the active hints.
    HINT_ALIASES = {"decoration-inactive": "decoration"}

    def test_root_canvas(self):
        assert_root_canvas(self, self.tree, 18, 34)

    def test_unique_ids(self):
        assert_unique_ids(self, self.tree)

    def test_inactive_slices_present(self):
        assert_ids_present(
            self,
            self.tree,
            [f"decoration-inactive-{name}" for name in SLICE_IDS],
        )
        ids = [
            element.get("id")
            for element in self.tree.iter()
            if element.get("id")
        ]
        self.assertEqual(
            [name for name in ids if name.startswith("decoration-inactive-hint-")],
            [],
        )
        assert_unique_ids(self, self.tree)
        assert_no_script_elements(self, self.tree)

    def test_inactive_top_tile_is_flat_grey(self):
        # The reference set has no inactive window, so the grey is
        # KDE-required provenance; #CCCCCC is the active title field's flat
        # row (250,27). The inactive top tile is the active tile with every
        # #FFFFFF/#777777 pinstripe (and the 1px highlight) flattened.
        grey = self.reference_pixel(250, 27)
        self.assertEqual(_hex(grey), "#CCCCCC")
        slices = render_slices(self.tree)
        expected = {
            point: "#CCCCCC" if fill in ("#FFFFFF", "#777777") else fill
            for point, fill in slices["decoration-top"].items()
        }
        assert_slice_pixels(self, slices, "decoration-inactive-top", expected)
        self.assertEqual(slices["decoration-inactive-top"][(0, 2)], _hex(grey))
        for fill in _rect_fills(self.tree, "decoration-inactive-top"):
            self.assertNotIn(fill, ("#FFFFFF", "#777777"))

    def test_inactive_bevel_has_no_highlight(self):
        slices = render_slices(self.tree)
        for name in (
            "decoration-inactive-left",
            "decoration-inactive-right",
            "decoration-inactive-bottom",
        ):
            with self.subTest(slice=name):
                expected = {
                    point: "#CCCCCC" if fill == "#FFFFFF" else fill
                    for point, fill in slices[name.replace("inactive-", "")].items()
                }
                assert_slice_pixels(self, slices, name, expected)
                for fill in _rect_fills(self.tree, name):
                    self.assertNotEqual(fill, "#FFFFFF")

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
    # The zoom glyph: two horizontal #222222 bars at local y=5 and y=7
    # spanning x=2..10.
    ZOOM_GLYPH = frozenset((x, y) for x in range(2, 11) for y in (5, 7))

    def test_close_box_matches_reference(self):
        expected = self.reference_box(11, 29)
        slices = render_slices(ET.parse(CLOSE_SVG))
        self.assertEqual(slices["active-center"], expected)

    def test_zoom_box_matches_reference(self):
        # The reference's zoom box (x=343..354) differs from its close box: it
        # carries an inner #222222 glyph. Pin every pixel against the zoom box.
        expected = self.reference_box(343, 29)
        for name, tree in _parsed_svgs(ZOOM_SVGS):
            with self.subTest(svg=name):
                slices = render_slices(tree)
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
        self.assertEqual(glyph, self.ZOOM_GLYPH)
        for x, y in sorted(glyph):
            self.assertEqual(
                zoom[(x, y)],
                _hex(self.reference_pixel(343 + x, 29 + y)),
                (x, y),
            )

    def test_inactive_center_is_flat(self):
        # The inactive box keeps the active box's #888888/#222222 outlines and
        # flattens its gradient face to #CCCCCC (KDE-required provenance: the
        # reference set has no inactive window). The zoom glyph is #222222, so
        # it survives over the flat face.
        for name, tree in _parsed_svgs(BUTTON_SVGS):
            with self.subTest(svg=name):
                assert_unique_ids(self, tree)
                slices = render_slices(tree)
                active = slices["active-center"]
                inactive = slices["inactive-center"]
                self.assertEqual(set(inactive), set(active))
                for point, fill in active.items():
                    if fill in ("#888888", "#222222"):
                        self.assertEqual(inactive[point], fill, point)
                    else:
                        self.assertEqual(inactive[point], "#CCCCCC", point)

    def test_inactive_zoom_glyph_survives(self):
        close = render_slices(ET.parse(CLOSE_SVG))["inactive-center"]
        for name, tree in _parsed_svgs(ZOOM_SVGS):
            with self.subTest(svg=name):
                zoom = render_slices(tree)["inactive-center"]
                glyph = {point for point in zoom if zoom[point] != close[point]}
                self.assertEqual(glyph, self.ZOOM_GLYPH)

    def test_button_svgs_are_self_contained(self):
        for name, tree in _parsed_svgs(BUTTON_SVGS):
            with self.subTest(svg=name):
                assert_unique_ids(self, tree)
                assert_no_script_elements(self, tree)


@unittest.skipUnless(shutil.which("kpackagetool6"), "needs kpackagetool6")
class TestPackageValid(KPackageInstallCase, unittest.TestCase):
    KPACKAGETOOL_TYPE = "KWin/Aurorae"
    PACKAGE_DIR = AURORAE_DIR
    PACKAGE_ID = AURORAE_ID


if __name__ == "__main__":
    unittest.main()
