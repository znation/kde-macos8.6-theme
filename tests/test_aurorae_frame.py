"""Tests for the org.macos8.desktop Aurorae frame artwork (`decoration.svg`).

The active `decoration` nine-slice, the flattened inactive
`decoration-inactive` nine-slice, the corner slices, and the gzipped
`decoration.svgz` form `kpackagetool6` requires. Every sampled value is
re-derived from `macos8.6-screenshots/aboutsystem_betawiki.png` through
`tools/png/__init__.py`; the inactive greys are KDE-required provenance (the
reference set has no inactive window) and are pinned against the active
artwork they grey. The reference is stored with Git LFS, so a clone without
it skips these tests rather than failing `make check`.
"""

from __future__ import annotations

import gzip
import os
import unittest
import xml.etree.ElementTree as ET

from support.aurorae_fixtures import (
    AURORAE_DIR,
    DECORATION_SVG,
    INACTIVE_GREY,
    ReferenceImageCase,
)
from support.nine_slice_case import NineSliceCase
from support.platinum_palette import hex_colour
from support.tmp_dir import make_tmp_dir
from svg_assertions import (
    SLICE_IDS,
    assert_ids_present,
    assert_no_script_elements,
    assert_root_canvas,
    assert_slice_pixels,
    assert_unique_ids,
    render_slices,
)


DECORATION_SVGZ = os.path.join(AURORAE_DIR, "decoration.svgz")

# The decoration artwork is ~35 KB uncompressed; cap the reads well above it.
# The `.svgz` is a compressed payload a contributor can replace with a
# decompression bomb, so both it and the uncompressed `decoration.svg` are
# read through `_read_capped`, which refuses an oversize payload instead of
# allocating its expansion whole.
_MAX_DECORATION_SVG_BYTES = 1 << 20


def _read_capped(path, opener, limit=_MAX_DECORATION_SVG_BYTES):
    """Return the bytes *opener* yields for *path*, refusing an oversize payload.

    A contributor controls `decoration.svgz`, and a few-KB gzip can expand to
    gigabytes; reading it with a bare ``.read()`` would allocate the whole
    expansion. Reading at most one byte past *limit* detects an oversize
    payload -- for the gzip opener without expanding past it -- and the caller
    gets a diagnostic naming the path and limit instead.
    """
    with opener(path) as handle:
        data = handle.read(limit + 1)
    if len(data) > limit:
        raise AssertionError(
            f"{path}: payload is larger than the {limit}-byte limit for "
            "Aurorae decoration artwork; refusing to read it whole"
        )
    return data


def _unmasked_points(width, height, mask):
    """Yield every (x, y) of a width x height region that is not in *mask*."""
    for y in range(height):
        for x in range(width):
            if (x, y) not in mask:
                yield x, y


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


def _assert_flattened_inactive_tile(case, tree, slices, name, flattened):
    """Assert inactive tile *name* is its active tile with *flattened* gone.

    The inactive window's tiles mirror the active ones with the highlight and
    pinstripe fills flattened to `INACTIVE_GREY`. Check the composited pixels
    against that derivation, then the rects' own fills, so a flattened colour
    that a later rect overpaints still fails. *slices* is the shared
    ``render_slices(tree)`` map.
    """
    expected = {
        point: INACTIVE_GREY if fill in flattened else fill
        for point, fill in slices[name.replace("inactive-", "")].items()
    }
    assert_slice_pixels(case, slices, name, expected)
    for fill in _rect_fills(tree, name):
        case.assertNotIn(fill, flattened)


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
        self.assertEqual(hex_colour(grey), INACTIVE_GREY)
        slices = render_slices(self.tree)
        _assert_flattened_inactive_tile(
            self,
            self.tree,
            slices,
            "decoration-inactive-top",
            ("#FFFFFF", "#777777"),
        )
        self.assertEqual(slices["decoration-inactive-top"][(0, 2)], hex_colour(grey))

    def test_inactive_bevel_has_no_highlight(self):
        slices = render_slices(self.tree)
        for name in (
            "decoration-inactive-left",
            "decoration-inactive-right",
            "decoration-inactive-bottom",
        ):
            with self.subTest(slice=name):
                _assert_flattened_inactive_tile(
                    self, self.tree, slices, name, ("#FFFFFF",)
                )

    def test_inactive_corners_flatten_active_corners(self):
        # The inactive corners are hand-derived, and test_inactive_slices_present
        # only checks their ids: a wrong inactive corner passed every test.
        # They mirror the active corners with the 1px #FFFFFF highlight and
        # the #777777 pinstripes flattened to #CCCCCC (KDE-required
        # provenance: the reference set has no inactive window). The active
        # corners are pinned against the reference by TestCorners, so tying
        # each inactive corner to its active one makes a wrong hand-derived
        # corner fail here.
        slices = render_slices(self.tree)
        for name in (
            "decoration-inactive-topleft",
            "decoration-inactive-topright",
            "decoration-inactive-bottomleft",
            "decoration-inactive-bottomright",
        ):
            with self.subTest(slice=name):
                _assert_flattened_inactive_tile(
                    self, self.tree, slices, name, ("#FFFFFF", "#777777")
                )

    # The reference frame's borders, at the coordinate each tile's local
    # origin maps to: the left border starts at its outer black column x=7,
    # the right border at its inner black column x=354, and the bottom border
    # at its inner black row y=419. A clear row y=100 (between the title
    # bar and the bottom border) and a clear column x=250 cross each border
    # away from the corners and the button footprints.
    EDGE_CLEAR_Y = 100
    EDGE_CLEAR_X = 250
    LEFT_BORDER_X = 7
    RIGHT_BORDER_X = 354
    BOTTOM_BORDER_Y = 419

    def test_side_and_bottom_tiles_match_reference(self):
        # The title bar (test_title_bar_colours_match_reference) and the
        # four corners (TestCorners) are pinned against the reference, but the
        # stretched edge tiles were only pinned through the inactive tiles
        # derived from them, so a wrong active bevel row passed every test.
        # The reference border is uniform along its length and the artwork's
        # edge tile is constant across the edge, so each tile repeats one
        # cross-section sampled from the reference.
        slices = render_slices(self.tree)
        # (slice, reference x0, reference y0, cross-section runs along x)
        edges = (
            ("decoration-left", self.LEFT_BORDER_X, self.EDGE_CLEAR_Y, True),
            ("decoration-right", self.RIGHT_BORDER_X, self.EDGE_CLEAR_Y, True),
            ("decoration-bottom", self.EDGE_CLEAR_X, self.BOTTOM_BORDER_Y, False),
        )
        for name, x0, y0, along_x in edges:
            with self.subTest(slice=name):
                cross = [
                    hex_colour(
                        self.reference_pixel(
                            x0 + (step if along_x else 0),
                            y0 + (0 if along_x else step),
                        )
                    )
                    for step in range(6)
                ]
                expected = {
                    (x, y): cross[x if along_x else y]
                    for x in range(6)
                    for y in range(6)
                }
                assert_slice_pixels(self, slices, name, expected)

    def test_title_bar_colours_match_reference(self):
        # The pinstripe field is uniform along the bar, so one clear column
        # pins it: local y = reference y - 25. Pin every row, not only the
        # bevel and the first stripe: the inactive tile is derived from this
        # active one (its #FFFFFF/#777777 rows flatten to #CCCCCC), so a wrong
        # active pinstripe row would otherwise pass every other test.
        top = render_slices(self.tree)["decoration-top"]
        for local_y in range(22):
            self.assertEqual(
                top[(0, local_y)],
                hex_colour(self.reference_pixel(250, 25 + local_y)),
                local_y,
            )

    def test_svgz_is_the_compressed_svg(self):
        # `kpackagetool6 -t KWin/Aurorae` requires `decoration.svgz`, while the
        # Aurorae runtime prefers the uncompressed `decoration.svg`; pin that
        # the compressed copy cannot drift from the artwork under test.
        uncompressed = _read_capped(DECORATION_SVG, lambda path: open(path, "rb"))
        decompressed = _read_capped(DECORATION_SVGZ, gzip.open)
        self.assertEqual(decompressed, uncompressed)

    def test_svgz_decompression_bomb_is_refused(self):
        # A small `.svgz` can expand to far more than its file size; the capped
        # read must refuse it after the limit instead of allocating the whole
        # expansion. 8 MiB expands from a few KB and is 8x the limit.
        tmp = str(make_tmp_dir(self))
        bomb = os.path.join(tmp, "bomb.svgz")
        with gzip.open(bomb, "wb") as handle:
            for _ in range(8):
                handle.write(b"\x00" * _MAX_DECORATION_SVG_BYTES)
        with self.assertRaises(AssertionError) as caught:
            _read_capped(bomb, gzip.open)
        self.assertIn("larger than", str(caught.exception))


class TestCorners(ReferenceImageCase, unittest.TestCase):
    """Each corner slice reproduces the reference frame.

    The only pixels skipped are the exact 13x13 close and collapse button
    footprints the Aurorae engine draws over the frame: the close button at
    TitleEdgeLeft=4 / ButtonMarginTop=4 covers frame-local x=4..16, y=4..16
    (the top-left corner's x=4,5), and the collapse button at
    TitleEdgeRight=4 has its right edge at frame-local x = width - 5,
    covering the top-right corner's x=0,1. Every other corner pixel is
    compared.
    """

    BUTTON_MASK = {
        "decoration-topleft": {(x, y) for x in (4, 5) for y in range(4, 17)},
        "decoration-topright": {(x, y) for x in (0, 1) for y in range(4, 17)},
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
                for x, y in _unmasked_points(width, height, mask):
                    self.assertEqual(
                        slices[name][(x, y)],
                        hex_colour(self.reference_pixel(x0 + x, y0 + y)),
                        (x, y),
                    )


if __name__ == "__main__":
    unittest.main()
