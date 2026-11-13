"""Validate the icon theme package's Platinum Xcursor pointer set.

The cursors are our own Platinum-style drawings (no reference screenshot shows
the pointer), so these tests pin the Xcursor container, every frame's decoded
pixels, the alias bytes and the generator's deterministic output. The
``tools/make_cursors.py`` generator's own grid and cache checks and its
``main`` failures live in ``tests/test_make_cursors.py``; its size rule is
the one ``tools/cursor_vector.py`` defines. The
test-side reader is independent of ``tools/xcursor.py``; see
``tests/support/xcursor.py``.
"""

from __future__ import annotations

import unittest
from unittest import mock

from support import containment  # noqa: E402
from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import xcursor as xcursor_reader  # noqa: E402
from support.tmp_dir import make_tmp_dir  # noqa: E402
from tools import cursor_art, cursor_art_pointers, make_cursors  # noqa: E402
from tools.cursor_vector import VectorCursor  # noqa: E402
from tools.png import decode_rgba  # noqa: E402

PACKAGE = make_cursors.ROOT / make_cursors.PACKAGE_DIR
CURSORS = PACKAGE / make_cursors.CURSORS_DIR
LEFT_PTR = CURSORS / "left_ptr"
SIZES = (16, 24, 32)
CANONICAL = (
    "left_ptr",
    "xterm",
    "hand2",
    "watch",
    "fleur",
    "size_hor",
    "size_ver",
    "size_fdiag",
    "size_bdiag",
    "crosshair",
    "not-allowed",
    "dnd-copy",
    "grab",
    "grabbing",
    "help",
    "progress",
    "pencil",
    "zoom-in",
    "zoom-out",
    "context-menu",
)
ALIASES = {
    "left_ptr": ("arrow", "default", "top_left_arrow", "dnd-none"),
    "xterm": ("text", "ibeam"),
    "hand2": ("hand1", "pointer", "pointing_hand"),
    "watch": ("wait",),
    "fleur": ("move", "all-scroll", "size_all", "dnd-move"),
    "size_hor": (
        "e-resize",
        "ew-resize",
        "w-resize",
        "h_double_arrow",
        "sb_h_double_arrow",
        "col-resize",
        "split_h",
        "left_side",
        "right_side",
    ),
    "size_ver": (
        "n-resize",
        "ns-resize",
        "s-resize",
        "sb_v_double_arrow",
        "v_double_arrow",
        "00008160000006810000408080010102",
        "row-resize",
        "split_v",
        "top_side",
        "bottom_side",
    ),
    "size_fdiag": (
        "nw-resize",
        "se-resize",
        "nwse-resize",
        "top_left_corner",
        "bottom_right_corner",
    ),
    "size_bdiag": (
        "ne-resize",
        "sw-resize",
        "nesw-resize",
        "top_right_corner",
        "bottom_left_corner",
    ),
    "crosshair": ("cross", "tcross"),
    "not-allowed": (
        "circle",
        "crossed_circle",
        "03b6e0fcb3499374a867c041f52298f0",
        "forbidden",
        "no-drop",
        "dnd-no-drop",
    ),
    "dnd-copy": ("cell", "plus"),
    "grab": ("openhand",),
    "grabbing": ("closedhand",),
    "help": (
        "left_ptr_help",
        "question_arrow",
        "whats_this",
        "5c6cd98b3f3ebcb1f9c7f1c204630408",
        "d9ce0ab605698f320427677b458ad60b",
    ),
    "progress": (
        "half-busy",
        "left_ptr_watch",
        "00000000000000020006000e7e9ffc3f",
        "08e8e1c95fe2fc01f976f1e063a24ccd",
        "3ecb610c1bf2410f44200f48c40d3599",
    ),
    "pencil": (),
    "zoom-in": (),
    "zoom-out": (),
    "context-menu": (),
}
CURSOR_FILES = tuple(
    name for canonical in CANONICAL for name in (canonical, *ALIASES[canonical])
)
# The arrow is vector art rasterized at each size, so its hotspot is the
# design tip (3, 3) mapped to each size's pixel: floor(3 * size / 32).
VECTOR_CURSORS = frozenset(
    canonical
    for canonical, art, _hotspot, _aliases in cursor_art.CURSORS
    if isinstance(art, VectorCursor)
)
HOTSPOTS = {
    "left_ptr": {16: (1, 1), 24: (2, 2), 32: (3, 3)},
    "xterm": {16: (7, 7), 24: (11, 11), 32: (15, 15)},
    "hand2": {16: (7, 2), 24: (10, 3), 32: (14, 4)},
    "watch": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "fleur": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "size_hor": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "size_ver": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "size_fdiag": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "size_bdiag": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "crosshair": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "not-allowed": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "dnd-copy": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "grab": {16: (7, 12), 24: (11, 18), 32: (14, 24)},
    "grabbing": {16: (7, 12), 24: (11, 18), 32: (14, 24)},
    "help": {16: (1, 1), 24: (2, 2), 32: (2, 2)},
    "progress": {16: (1, 1), 24: (2, 2), 32: (2, 2)},
    "pencil": {16: (2, 14), 24: (3, 21), 32: (4, 28)},
    "zoom-in": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "zoom-out": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "context-menu": {16: (1, 1), 24: (2, 2), 32: (2, 2)},
}
# A grid pixel that must be black (the face) and one that must be white (the
# outline) at the same place in every nominal size.
PINNED_PIXELS = {
    "watch": {"face": (7, 4), "outline": (6, 5)},
    "fleur": {"face": (7, 7), "outline": (7, 0)},
    "size_hor": {"face": (7, 7), "outline": (7, 6)},
    "size_ver": {"face": (7, 7), "outline": (6, 7)},
    "size_fdiag": {"face": (7, 7), "outline": (6, 7)},
    "size_bdiag": {"face": (7, 7), "outline": (6, 7)},
    "crosshair": {"face": (7, 7), "outline": (6, 6)},
    "not-allowed": {"face": (7, 7), "outline": (7, 0)},
    "dnd-copy": {"face": (7, 7), "outline": (6, 7)},
    "grab": {"face": (7, 12), "outline": (1, 12)},
    "grabbing": {"face": (7, 12), "outline": (1, 12)},
    "help": {"face": (1, 1), "outline": (0, 0)},
    "progress": {"face": (1, 1), "outline": (0, 0)},
    "pencil": {"face": (2, 14), "outline": (1, 14)},
    "zoom-in": {"face": (7, 7), "outline": (7, 2)},
    "zoom-out": {"face": (7, 7), "outline": (7, 2)},
    "context-menu": {"face": (1, 1), "outline": (0, 0)},
}
# The arrow's top-left corner is its white outline pixel; the other cursors
# leave all four corners transparent.
TRANSPARENT_CORNER_CURSORS = (
    "xterm",
    "hand2",
    "watch",
    "fleur",
    "size_hor",
    "size_ver",
    "size_fdiag",
    "size_bdiag",
    "crosshair",
    "not-allowed",
    "dnd-copy",
    "grab",
    "grabbing",
    "pencil",
    "zoom-in",
    "zoom-out",
)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)


def _pixel(rgba, width, x, y):
    """Return pixel (*x*, *y*) of packed *rgba* as an RGBA tuple."""
    start = (y * width + x) * 4
    return tuple(rgba[start : start + 4])


def _scaled(x, y, size):
    """Return grid pixel (*x*, *y*) at the first destination pixel it covers."""
    return ((x * size + 15) // 16, (y * size + 15) // 16)


def _read_cursor(path):
    """Read *path* through the independent test-side reader."""
    return xcursor_reader.read_cursor(path)


def _repo_bytes(path):
    """Return *path*'s bytes, refusing a repository symlink escape.

    The committed cursor files are contributor-supplied, so a checked-in
    symlink at one could make a direct read follow it outside the repository
    (or block on a FIFO). The shared containment reader refuses such a path,
    a non-regular file, and an oversize file by name.
    """
    return containment.read_bytes(path, repo_root.ROOT)


class TestCursorArtifact(unittest.TestCase):
    """Pin the committed ``left_ptr`` artifact and its alias bytes."""

    def setUp(self):
        self.cursor = _read_cursor(LEFT_PTR)

    def test_parser_accepts_three_image_chunks_at_the_nominal_sizes(self):
        self.assertEqual(
            tuple(image.nominal_size for image in self.cursor.images), SIZES
        )
        for image in self.cursor.images:
            with self.subTest(size=image.nominal_size):
                self.assertIn(image.nominal_size, SIZES)

    def test_each_chunk_png_decodes_at_its_nominal_size(self):
        for image in self.cursor.images:
            with self.subTest(size=image.nominal_size):
                width, height, rgba = decode_rgba(image.png)
                self.assertEqual((width, height), (image.nominal_size,) * 2)
                self.assertEqual((image.width, image.height), (width, height))
                self.assertEqual(len(rgba), width * height * 4)

    def test_each_frame_pins_the_hotspot_outline_tip_and_transparency(self):
        for image in self.cursor.images:
            size = image.nominal_size
            with self.subTest(size=size):
                width, height, rgba = decode_rgba(image.png)
                hotspot = (image.hotspot_x, image.hotspot_y)
                self.assertEqual(hotspot, HOTSPOTS["left_ptr"][size])
                # Design point (6, 14) of the 32-unit grid lies in the face;
                # the pixel covering it is floor(coordinate * size / 32).
                self.assertEqual(
                    _pixel(rgba, width, 6 * size // 32, 14 * size // 32), BLACK
                )
                self.assertEqual(_pixel(rgba, width, *hotspot)[3], 255)
                self.assertEqual(_pixel(rgba, width, width - 1, 0)[3], 0)
                self.assertEqual(
                    _pixel(rgba, width, width - 1, height - 1)[3], 0
                )
                alphas = {
                    _pixel(rgba, width, x, y)[3]
                    for y in range(height)
                    for x in range(width)
                }
                self.assertTrue(
                    any(0 < alpha < 255 for alpha in alphas),
                    "no antialiased edge pixel in the frame",
                )

    def test_aliases_are_byte_identical_to_left_ptr(self):
        expected = _repo_bytes(LEFT_PTR)
        for name in ALIASES["left_ptr"]:
            with self.subTest(name=name):
                self.assertEqual(_repo_bytes(CURSORS / name), expected)

    def test_committed_artifact_is_a_fresh_generator_result(self):
        self.assertEqual(_repo_bytes(LEFT_PTR), make_cursors.cursor_bytes())

    def test_a_corrupted_grid_dropped_size_or_moved_hotspot_changes_the_artifact(self):
        art = cursor_art_pointers.ARROW_ART
        face = list(art.face)
        face[3] = (face[3][0], face[3][1] - 1)  # the tail tip moves up one unit
        moved_vertex = VectorCursor(
            face=tuple(face),
            outline_width=art.outline_width,
            design_size=art.design_size,
        )
        variants = {
            "moved face vertex": make_cursors.cursor_bytes(rows=moved_vertex),
            "dropped size": make_cursors.cursor_bytes(sizes=(16, 24)),
            "moved hotspot": make_cursors.cursor_bytes(hotspot=(4, 3)),
        }
        expected = _repo_bytes(LEFT_PTR)
        for name, data in variants.items():
            with self.subTest(variant=name):
                self.assertNotEqual(data, expected)

    def test_reader_rejects_a_truncated_or_corrupted_copy(self):
        tmp = make_tmp_dir(self)
        truncated = tmp / "truncated"
        truncated.write_bytes(_repo_bytes(LEFT_PTR)[:20])
        corrupted = tmp / "corrupted"
        corrupted.write_bytes(b"Xcur" + b"\xff" * 28)
        for name, path in (("truncated", truncated), ("corrupted", corrupted)):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    _read_cursor(path)


class TestVectorPointerArtifacts(unittest.TestCase):
    """Pin the committed I-beam and pointing-hand vector artifacts per size.

    Each design point maps to the pixel that contains it at a nominal size:
    ``floor(coordinate * size / 32)``. The expectations below come from the
    design coordinates in ``tools/cursor_art_pointers.py``, not from the
    rendered output.
    """

    # (name, design points that must be black, design points that must be
    # white). The hotspot is checked separately, as its alpha.
    EXPECTATIONS = {
        "xterm": {"black": ((15, 15),), "white": ((17, 15),), "grey": (24,)},
        "hand2": {"black": ((14, 8),), "white": ((17, 7),), "grey": SIZES},
    }

    def _frames(self, name):
        cursor = _read_cursor(CURSORS / name)
        for image in cursor.images:
            width, height, rgba = decode_rgba(image.png)
            yield image, width, height, rgba

    def test_each_frame_has_the_pinned_hotspot_and_face_and_outline(self):
        for name, points in self.EXPECTATIONS.items():
            for image, width, _height, rgba in self._frames(name):
                size = image.nominal_size
                with self.subTest(name=name, size=size):
                    self.assertEqual(
                        (image.hotspot_x, image.hotspot_y), HOTSPOTS[name][size]
                    )
                    self.assertEqual(
                        _pixel(rgba, width, *HOTSPOTS[name][size])[3], 255
                    )
                    for x, y in points["black"]:
                        self.assertEqual(
                            _pixel(rgba, width, x * size // 32, y * size // 32),
                            BLACK,
                        )
                    for x, y in points["white"]:
                        self.assertEqual(
                            _pixel(rgba, width, x * size // 32, y * size // 32),
                            WHITE,
                        )

    def test_each_frame_has_transparent_corners(self):
        for name in self.EXPECTATIONS:
            for image, width, height, rgba in self._frames(name):
                with self.subTest(name=name, size=image.nominal_size):
                    for x, y in (
                        (0, 0),
                        (width - 1, 0),
                        (0, height - 1),
                        (width - 1, height - 1),
                    ):
                        self.assertEqual(_pixel(rgba, width, x, y), TRANSPARENT)

    def test_each_frame_is_antialiased(self):
        for name, points in self.EXPECTATIONS.items():
            for image, width, height, rgba in self._frames(name):
                size = image.nominal_size
                with self.subTest(name=name, size=size):
                    pixels = [
                        _pixel(rgba, width, x, y)
                        for y in range(height)
                        for x in range(width)
                    ]
                    self.assertTrue(
                        any(0 < p[3] < 255 for p in pixels),
                        "no partly covered edge pixel",
                    )
                    # Only the sizes the design pins: the I-beam's stem edges
                    # fall inside a pixel at 24 but on pixel boundaries at 16
                    # and 32, so only its 24 frame has a grey-level edge.
                    if size in points["grey"]:
                        self.assertTrue(
                            any(p[3] == 255 and 0 < p[0] < 255 for p in pixels),
                            "no opaque pixel with an intermediate grey level",
                        )


class TestCursorSet(unittest.TestCase):
    """Pin every canonical pointer, its aliases and the generator's output."""

    def test_every_cursor_parses_to_three_chunks_at_the_nominal_sizes(self):
        for name in CANONICAL:
            cursor = _read_cursor(CURSORS / name)
            with self.subTest(name=name):
                self.assertEqual(
                    tuple(image.nominal_size for image in cursor.images), SIZES
                )

    def test_every_frame_pins_its_hotspot_face_and_outline(self):
        for name in CANONICAL:
            if name in VECTOR_CURSORS:
                # Vector art has no grid cells; its frames are pinned by
                # TestCursorArtifact and TestVectorPointerArtifacts instead.
                continue
            cursor = _read_cursor(CURSORS / name)
            face = PINNED_PIXELS[name]["face"]
            outline = PINNED_PIXELS[name]["outline"]
            for image in cursor.images:
                size = image.nominal_size
                with self.subTest(name=name, size=size):
                    width, _, rgba = decode_rgba(image.png)
                    self.assertEqual(
                        (image.hotspot_x, image.hotspot_y),
                        HOTSPOTS[name][size],
                    )
                    self.assertEqual(
                        _pixel(rgba, width, *_scaled(*face, size)), BLACK
                    )
                    self.assertEqual(
                        _pixel(rgba, width, *_scaled(*outline, size)), WHITE
                    )

    def test_each_new_cursor_has_transparent_corners(self):
        for name in TRANSPARENT_CORNER_CURSORS:
            self._assert_transparent_corners(name, _read_cursor(CURSORS / name))

    def _assert_transparent_corners(self, name, cursor):
        """Pin every image of cursor *name*'s four corners transparent."""
        for image in cursor.images:
            width, height, rgba = decode_rgba(image.png)
            with self.subTest(name=name, size=image.nominal_size):
                for x, y in (
                    (0, 0),
                    (width - 1, 0),
                    (0, height - 1),
                    (width - 1, height - 1),
                ):
                    self.assertEqual(_pixel(rgba, width, x, y), TRANSPARENT)

    def test_every_alias_is_byte_identical_to_its_canonical(self):
        for name in CANONICAL:
            expected = _repo_bytes(CURSORS / name)
            for alias in ALIASES[name]:
                with self.subTest(name=name, alias=alias):
                    self.assertEqual(_repo_bytes(CURSORS / alias), expected)

    def test_every_committed_cursor_is_a_fresh_generator_result(self):
        for canonical, rows, hotspot, aliases in cursor_art.CURSORS:
            expected = make_cursors.cursor_bytes(
                rows=rows, hotspot=hotspot, name=canonical
            )
            for name in (canonical, *aliases):
                with self.subTest(name=name):
                    self.assertEqual(_repo_bytes(CURSORS / name), expected)

    def test_each_new_grid_differs_from_the_arrow_grid(self):
        for name, rows, _, _ in cursor_art.CURSORS[1:]:
            with self.subTest(name=name):
                self.assertNotEqual(rows, cursor_art.ARROW_GRID)

    def test_generator_writes_every_file_deterministically_in_a_temp_directory(self):
        tmp = make_tmp_dir(self)
        with mock.patch.object(make_cursors, "ROOT", tmp):
            self.assertEqual(make_cursors.main([]), 0)
            directory = tmp / make_cursors.PACKAGE_DIR / make_cursors.CURSORS_DIR
            self.assertEqual(
                sorted(path.name for path in directory.iterdir()),
                sorted(CURSOR_FILES),
            )
            first = {
                name: (directory / name).read_bytes() for name in CURSOR_FILES
            }
            self.assertEqual(make_cursors.main([]), 0)
            second = {
                name: (directory / name).read_bytes() for name in CURSOR_FILES
            }
        self.assertEqual(first, second)
        for name, data in first.items():
            with self.subTest(name=name):
                self.assertEqual(data, _repo_bytes(CURSORS / name))

    def test_a_corrupted_grid_dropped_size_or_moved_hotspot_changes_each_glyph(self):
        for canonical, rows, hotspot, _ in cursor_art.CURSORS:
            committed = _repo_bytes(CURSORS / canonical)
            if canonical in VECTOR_CURSORS:
                # A vector entry has no grid cells; a moved face vertex stands
                # in for the corrupted cell.
                face = list(rows.face)
                face[3] = (face[3][0], face[3][1] - 1)
                corrupted = make_cursors.cursor_bytes(
                    rows=VectorCursor(
                        face=tuple(face),
                        outline_width=rows.outline_width,
                        design_size=rows.design_size,
                    ),
                    hotspot=hotspot,
                    name=canonical,
                )
            else:
                mutated = list(rows)
                y = next(index for index, row in enumerate(mutated) if "#" in row)
                x = mutated[y].index("#")
                mutated[y] = mutated[y][:x] + "." + mutated[y][x + 1 :]
                corrupted = make_cursors.cursor_bytes(
                    rows=tuple(mutated), hotspot=hotspot, name=canonical
                )
            variants = {
                "corrupted grid": corrupted,
                "dropped size": make_cursors.cursor_bytes(
                    rows=rows,
                    sizes=(16, 24),
                    hotspot=hotspot,
                    name=canonical,
                ),
                "moved hotspot": make_cursors.cursor_bytes(
                    rows=rows,
                    hotspot=(hotspot[0] + 1, hotspot[1]),
                    name=canonical,
                ),
            }
            for variant, data in variants.items():
                with self.subTest(glyph=canonical, variant=variant):
                    self.assertNotEqual(data, committed)

    def test_size_ver_is_the_horizontal_glyph_rotated_a_quarter_turn(self):
        size = cursor_art.GRID_SIZE
        rotated = tuple(
            "".join(
                cursor_art.SIZE_HOR_GRID[size - 1 - x][y]
                for x in range(size)
            )
            for y in range(size)
        )
        self.assertEqual(
            make_cursors.render_rgba(cursor_art.SIZE_VER_GRID, size),
            make_cursors.render_rgba(rotated, size),
        )

    def test_move_and_axis_resize_grids_are_mirror_symmetric(self):
        for name in ("FLEUR", "SIZE_HOR", "SIZE_VER"):
            grid = getattr(cursor_art, name + "_GRID")
            with self.subTest(name=name):
                self.assertEqual(grid, tuple(row[::-1] for row in grid))
                self.assertEqual(grid, grid[::-1])

    def test_fleur_grid_is_symmetric_about_its_diagonal(self):
        grid = cursor_art.FLEUR_GRID
        transposed = tuple(
            "".join(grid[y][x] for y in range(len(grid)))
            for x in range(len(grid[0]))
        )
        self.assertEqual(grid, transposed)

    def test_size_bdiag_is_the_forward_diagonal_mirrored(self):
        size = cursor_art.GRID_SIZE
        mirrored = tuple(row[::-1] for row in cursor_art.SIZE_FDIAG_GRID)
        self.assertEqual(
            make_cursors.render_rgba(cursor_art.SIZE_BDIAG_GRID, size),
            make_cursors.render_rgba(mirrored, size),
        )

    def test_crosshair_black_cells_lie_on_the_centre_row_or_column(self):
        size = cursor_art.GRID_SIZE
        centre = size // 2 - 1
        rgba = make_cursors.render_rgba(cursor_art.CROSSHAIR_GRID, size)
        black_cells = [
            (x, y)
            for y in range(size)
            for x in range(size)
            if _pixel(rgba, size, x, y) == BLACK
        ]
        for x, y in black_cells:
            with self.subTest(x=x, y=y):
                self.assertTrue(x == centre or y == centre)

    def test_not_allowed_is_a_ring_with_a_slash(self):
        cursor = _read_cursor(CURSORS / "not-allowed")
        image = next(
            image for image in cursor.images if image.nominal_size == 16
        )
        width, _, rgba = decode_rgba(image.png)
        for x, y in ((0, 0), (15, 0), (0, 15), (15, 15)):
            with self.subTest(corner=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), TRANSPARENT)
        self.assertEqual(_pixel(rgba, width, 7, 7), BLACK)
        for x, y in ((7, 0), (7, 15), (0, 7), (15, 7)):
            with self.subTest(cardinal=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), WHITE)

    def test_dnd_copy_plus_outline_separates_the_arms(self):
        rgba = make_cursors.render_rgba(cursor_art.DND_COPY_GRID, 16)
        self.assertEqual(_pixel(rgba, 16, 7, 7), BLACK)
        self.assertEqual(_pixel(rgba, 16, 3, 7), BLACK)
        self.assertEqual(_pixel(rgba, 16, 11, 7), BLACK)
        self.assertEqual(_pixel(rgba, 16, 6, 7), WHITE)
        self.assertEqual(_pixel(rgba, 16, 8, 7), WHITE)

    def test_not_allowed_ring_interior_is_transparent_except_the_slash(self):
        cursor = _read_cursor(CURSORS / "not-allowed")
        image = next(
            image for image in cursor.images if image.nominal_size == 16
        )
        width, height, rgba = decode_rgba(image.png)
        slash = {(i, i) for i in range(4, 13)}
        slash_outline = {
            (x + dx, y + dy)
            for x, y in slash
            for dx, dy in ((1, 0), (0, 1))
        }
        for y in range(height):
            for x in range(width):
                if self._is_slash_cell(x, y, slash, slash_outline):
                    continue
                if not self._is_inside_not_allowed_ring(x, y):
                    continue
                self._assert_white_ring_shield(rgba, width, x, y)

    @staticmethod
    def _is_slash_cell(x, y, slash, slash_outline):
        return (x, y) in slash or (x, y) in slash_outline

    @staticmethod
    def _is_inside_not_allowed_ring(x, y):
        return (x - 7.5) ** 2 + (y - 7.5) ** 2 < 7.0**2

    def _assert_white_ring_shield(self, rgba, width, x, y):
        if _pixel(rgba, width, x, y) != WHITE:
            return
        # The ring's one-cell white inner outline is the drawing set's
        # shield between black and the transparent interior, so the only
        # whites inside the disc must touch a ring black side-on.
        neighbours = [
            _pixel(rgba, width, x + dx, y + dy)
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
        ]
        with self.subTest(interior=(x, y)):
            self.assertIn(BLACK, neighbours)

    def test_dnd_copy_is_a_centred_plus(self):
        cursor = _read_cursor(CURSORS / "dnd-copy")
        image = next(
            image for image in cursor.images if image.nominal_size == 16
        )
        width, _, rgba = decode_rgba(image.png)
        expected = (
            "                ",
            "       .        ",
            "      .#.       ",
            "      .#.       ",
            "      .#.       ",
            "      .#.       ",
            "  .....#.....   ",
            " .####.#.####.  ",
            "  .....#.....   ",
            "      .#.       ",
            "      .#.       ",
            "      .#.       ",
            "      .#.       ",
            "       .        ",
            "                ",
            "                ",
        )
        colors = {" ": TRANSPARENT, ".": WHITE, "#": BLACK}
        for y, row in enumerate(expected):
            for x, cell in enumerate(row):
                with self.subTest(x=x, y=y):
                    self.assertEqual(_pixel(rgba, width, x, y), colors[cell])
        for x, y in ((7, 2), (7, 12), (2, 7), (12, 7), (7, 7)):
            with self.subTest(black=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), BLACK)
        for x, y in ((6, 7), (7, 1)):
            with self.subTest(white=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), WHITE)
        for x, y in ((0, 0), (15, 0), (0, 15), (15, 15)):
            with self.subTest(corner=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), TRANSPARENT)

    def test_grab_and_grabbing_pin_open_and_closed_hands(self):
        images = {}
        for name in ("grab", "grabbing"):
            cursor = _read_cursor(CURSORS / name)
            image = next(
                image for image in cursor.images if image.nominal_size == 16
            )
            images[name] = (image.nominal_size, *decode_rgba(image.png))
        for name in ("grab", "grabbing"):
            width, _, rgba = images[name][1:]
            with self.subTest(name=name):
                self.assertEqual(_pixel(rgba, width, 7, 12), BLACK)
                self.assertEqual(_pixel(rgba, width, 1, 12), WHITE)
        width, _, rgba = images["grab"][1:]
        self.assertEqual(_pixel(rgba, width, 3, 2), BLACK)
        width, _, rgba = images["grabbing"][1:]
        self.assertEqual(_pixel(rgba, width, 3, 2), TRANSPARENT)
        self.assertNotEqual(
            cursor_art.GRAB_GRID, cursor_art.GRABBING_GRID
        )

    def test_dnd_aliases_reuse_the_existing_glyphs(self):
        for alias, canonical in (
            ("dnd-move", "fleur"),
            ("dnd-none", "left_ptr"),
            ("forbidden", "not-allowed"),
            ("no-drop", "not-allowed"),
            ("dnd-no-drop", "not-allowed"),
            ("cell", "dnd-copy"),
            ("plus", "dnd-copy"),
            ("col-resize", "size_hor"),
            ("split_h", "size_hor"),
            ("row-resize", "size_ver"),
            ("split_v", "size_ver"),
            ("openhand", "grab"),
            ("closedhand", "grabbing"),
        ):
            with self.subTest(alias=alias):
                self.assertEqual(
                    _repo_bytes(CURSORS / alias),
                    _repo_bytes(CURSORS / canonical),
                )

    def test_context_menu_keeps_the_arrow_cells(self):
        # The panel restates, never redraws, the existing arrow: every cell the
        # arrow draws black stays black at the same grid coordinates.
        arrow_blacks = {
            (x, y)
            for y, row in enumerate(cursor_art.ARROW_GRID)
            for x, cell in enumerate(row)
            if cell == "#"
        }
        menu_blacks = {
            (x, y)
            for y, row in enumerate(cursor_art.CONTEXT_MENU_GRID)
            for x, cell in enumerate(row)
            if cell == "#"
        }
        self.assertEqual(menu_blacks & arrow_blacks, arrow_blacks)

    def test_context_menu_pins_the_menu_panel(self):
        cursor = _read_cursor(CURSORS / "context-menu")
        image = next(
            image for image in cursor.images if image.nominal_size == 16
        )
        width, _, rgba = decode_rgba(image.png)
        # The panel's walls and its two text bars sit on the redrawn cells.
        for x, y in (
            (8, 11), (11, 11), (14, 11),
            (8, 12), (14, 12),
            (8, 14), (11, 14), (14, 14),
            (10, 12), (11, 12), (12, 12),
            (10, 13), (11, 13),
        ):
            with self.subTest(black=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), BLACK)
        for x, y in (
            (0, 0), (11, 10), (13, 10), (7, 12), (9, 12),
            (13, 12), (9, 13), (12, 13), (13, 13), (15, 13), (9, 15),
        ):
            with self.subTest(white=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), WHITE)

    def test_every_cursor_grid_shields_its_black_from_transparent(self):
        # The set's shared drawing language: a one-cell white outline
        # separates every black cell from transparent pixels and from the
        # frame edge, orthogonal on every side, in every shipped grid.
        for canonical, rows, _, _ in cursor_art.CURSORS:
            if canonical in VECTOR_CURSORS:
                continue
            with self.subTest(canonical=canonical):
                self._assert_grid_is_shielded(canonical, rows)

    def _assert_grid_is_shielded(self, canonical, rows):
        self.assertEqual(len(rows), 16)
        self.assertEqual({len(row) for row in rows}, {16})
        for y, row in enumerate(rows):
            for x, cell in enumerate(row):
                if cell == "#":
                    self._assert_black_cell_is_shielded(rows, x, y)

    def _assert_black_cell_is_shielded(self, rows, x, y):
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            inside = 0 <= nx < 16 and 0 <= ny < 16
            with self.subTest(black=(x, y)):
                self.assertTrue(inside)
                self.assertNotEqual(rows[ny][nx], " ")

    def _sixteen_pixel_image(self, canonical):
        cursor = _read_cursor(CURSORS / canonical)
        image = next(
            image for image in cursor.images if image.nominal_size == 16
        )
        return (image,) + decode_rgba(image.png)

    def test_watch_draws_the_round_faced_wristwatch(self):
        image, width, _, rgba = self._sixteen_pixel_image("watch")
        self.assertEqual((image.hotspot_x, image.hotspot_y), (7, 7))
        # The crown sits above the ring.
        self.assertEqual(_pixel(rgba, width, 7, 2), BLACK)
        for x, y in ((6, 2), (8, 2), (7, 3)):
            with self.subTest(white=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), WHITE)
        # The closed round ring reaches its cardinals before its diagonals.
        for x, y in ((7, 4), (7, 10), (4, 7), (10, 7)):
            with self.subTest(cardinal=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), BLACK)
        for x, y in ((5, 4), (4, 5), (10, 5), (5, 9), (9, 9)):
            with self.subTest(shoulder=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), BLACK)
        for x, y in (
            (4, 4),
            (10, 4),
            (4, 3),
            (3, 7),
            (4, 10),
            (11, 7),
            (6, 5),
            (5, 6),
            (6, 6),
        ):
            with self.subTest(outline_or_face=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), WHITE)
        # The two-cell minute hand stands on the centre and the hour hand
        # crosses it to the right.
        for x, y in ((7, 5), (7, 6), (7, 7), (8, 7)):
            with self.subTest(hand=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), BLACK)

    def test_help_pins_the_arrow_and_question_mark(self):
        image, width, _, rgba = self._sixteen_pixel_image("help")
        self.assertEqual((image.hotspot_x, image.hotspot_y), (1, 1))
        arrow_blacks = {
            (x, y)
            for y, row in enumerate(cursor_art.ARROW_GRID)
            for x, cell in enumerate(row)
            if cell == "#"
        }
        for x, y in sorted(arrow_blacks):
            with self.subTest(arrow=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), BLACK)
        for x, y in ((10, 3), (13, 5), (12, 7)):
            with self.subTest(black=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), BLACK)
        for x, y in ((0, 0), (12, 6)):
            with self.subTest(white=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), WHITE)

    def test_progress_pins_the_arrow_and_watch_face(self):
        image, width, _, rgba = self._sixteen_pixel_image("progress")
        self.assertEqual((image.hotspot_x, image.hotspot_y), (1, 1))
        arrow_blacks = {
            (x, y)
            for y, row in enumerate(cursor_art.ARROW_GRID)
            for x, cell in enumerate(row)
            if cell == "#"
        }
        for x, y in sorted(arrow_blacks):
            with self.subTest(arrow=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), BLACK)
        # The miniature of the busy watch's round face: ring top, two-cell
        # hands and the white interior between them.
        for x, y in ((11, 3), (12, 3), (13, 3), (12, 4), (12, 5), (13, 5)):
            with self.subTest(black=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), BLACK)
        for x, y in ((11, 5), (12, 6), (9, 5), (12, 8)):
            with self.subTest(white=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), WHITE)

    def test_help_and_progress_draw_the_arrow_cells_at_the_same_coordinates(self):
        arrow_blacks = {
            (x, y)
            for y, row in enumerate(cursor_art.ARROW_GRID)
            for x, cell in enumerate(row)
            if cell == "#"
        }
        for name, grid in (
            ("help", cursor_art.HELP_GRID),
            ("progress", cursor_art.PROGRESS_GRID),
        ):
            extras = {
                (x, y)
                for y, row in enumerate(grid)
                for x, cell in enumerate(row)
                if cell == "#"
            } - arrow_blacks
            with self.subTest(name=name):
                # The restated question mark and mini-face cells live only in
                # the free right-hand area beside the untouched arrow cells.
                self.assertTrue(all(x >= 9 for x, _ in extras))

    def test_pencil_draws_a_diagonal_shaft_to_its_writing_tip(self):
        cursor = _read_cursor(CURSORS / "pencil")
        image = next(
            image for image in cursor.images if image.nominal_size == 16
        )
        width, _, rgba = decode_rgba(image.png)
        for x, y in ((2, 14), (8, 7), (12, 3)):
            with self.subTest(black=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), BLACK)
        for x, y in ((1, 14), (13, 1)):
            with self.subTest(white=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), WHITE)
        for x, y in ((0, 0), (15, 0), (0, 15), (15, 15)):
            with self.subTest(corner=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), TRANSPARENT)

    def test_zoom_in_and_out_differ_only_at_the_plus_arms(self):
        images = {}
        for name in ("zoom-in", "zoom-out"):
            cursor = _read_cursor(CURSORS / name)
            image = next(
                image for image in cursor.images if image.nominal_size == 16
            )
            images[name] = decode_rgba(image.png)
        for name in ("zoom-in", "zoom-out"):
            width, _, rgba = images[name]
            with self.subTest(name=name):
                for x, y in ((7, 3), (3, 7), (7, 11), (13, 13)):
                    self.assertEqual(_pixel(rgba, width, x, y), BLACK)
                self.assertEqual(_pixel(rgba, width, 7, 2), WHITE)
        width, _, zoom_in = images["zoom-in"]
        for x, y in ((7, 5), (5, 7), (9, 7), (7, 9)):
            self.assertEqual(_pixel(zoom_in, width, x, y), BLACK)
        width, _, zoom_out = images["zoom-out"]
        for x, y in ((5, 7), (9, 7)):
            self.assertEqual(_pixel(zoom_out, width, x, y), BLACK)
        # Dropping the vertical arm colour its four cells back into the
        # white glass; the pair still differs only at the plus arms.
        for x, y in ((7, 5), (7, 9)):
            self.assertEqual(_pixel(zoom_out, width, x, y), WHITE)

    def test_help_and_progress_alias_names_reuse_their_canonical(self):
        for alias, canonical in (
            ("left_ptr_help", "help"),
            ("question_arrow", "help"),
            ("whats_this", "help"),
            ("5c6cd98b3f3ebcb1f9c7f1c204630408", "help"),
            ("d9ce0ab605698f320427677b458ad60b", "help"),
            ("half-busy", "progress"),
            ("left_ptr_watch", "progress"),
            ("00000000000000020006000e7e9ffc3f", "progress"),
            ("08e8e1c95fe2fc01f976f1e063a24ccd", "progress"),
            ("3ecb610c1bf2410f44200f48c40d3599", "progress"),
        ):
            with self.subTest(alias=alias):
                self.assertEqual(
                    _repo_bytes(CURSORS / alias),
                    _repo_bytes(CURSORS / canonical),
                )


if __name__ == "__main__":
    unittest.main()
