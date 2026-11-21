"""Validate the icon theme package's Platinum Xcursor pointer set.

The cursors are our own Platinum-style drawings (no reference screenshot shows
the pointer), so these tests pin the Xcursor container, every frame's decoded
pixels, the alias bytes and the generator's deterministic output. Vector I-beam
and pointing-hand pins live in ``tests/test_cursors_vector_artifacts.py``.
Per-glyph drawn-shape pins live in ``tests/test_cursor_glyph_shapes.py``.
The ``tools/make_cursors.py`` generator's own grid and cache checks and its
``main`` failures live in ``tests/test_make_cursors.py``; its size rule is
the one ``tools/cursor_vector.py`` defines. The test-side reader is independent of ``tools/xcursor.py``; see
``tests/support/xcursor.py``.
"""

from __future__ import annotations

import unittest
from unittest import mock

from support import containment  # noqa: E402
from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cursor_artifact_cases import (  # noqa: E402
    BLACK,
    CURSORS,
    HOTSPOTS,
    SIZES,
    TRANSPARENT,
    WHITE,
    _pixel,
    _read_cursor,
)
from support.tmp_dir import make_tmp_dir  # noqa: E402
from tools import cursor_art, cursor_art_pointers, make_cursors  # noqa: E402
from tools.cursor_vector import VectorCursor  # noqa: E402
from tools.png import decode_rgba  # noqa: E402

LEFT_PTR = CURSORS / "left_ptr"
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
def _scaled(x, y, size):
    """Return grid pixel (*x*, *y*) at the first destination pixel it covers."""
    return ((x * size + 15) // 16, (y * size + 15) // 16)


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
