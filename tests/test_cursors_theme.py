"""Validate the icon theme package's Platinum Xcursor pointer set.

The cursors are our own Platinum-style drawings (no reference screenshot shows
the pointer), so these tests pin the Xcursor container, every frame's decoded
pixels, the alias bytes and the generator's deterministic output. The
test-side reader is independent of ``tools/xcursor.py``; see
``tests/support/xcursor.py``.
"""

from __future__ import annotations

import contextlib
import io
import os
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import xcursor as xcursor_reader  # noqa: E402
from support.tmp_dir import make_tmp_dir  # noqa: E402
from tools import cursor_art, make_cursors  # noqa: E402
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
    ),
    "size_ver": (
        "n-resize",
        "ns-resize",
        "s-resize",
        "sb_v_double_arrow",
        "v_double_arrow",
        "00008160000006810000408080010102",
    ),
    "size_fdiag": ("nw-resize", "se-resize", "nwse-resize"),
    "size_bdiag": ("ne-resize", "sw-resize", "nesw-resize"),
    "crosshair": ("cross", "tcross"),
    "not-allowed": (
        "circle",
        "crossed_circle",
        "03b6e0fcb3499374a867c041f52298f0",
        "forbidden",
        "no-drop",
        "dnd-no-drop",
    ),
    "dnd-copy": (),
    "grab": (),
    "grabbing": (),
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
}
CURSOR_FILES = tuple(
    name for canonical in CANONICAL for name in (canonical, *ALIASES[canonical])
)
HOTSPOTS = {
    "left_ptr": {16: (1, 1), 24: (2, 2), 32: (2, 2)},
    "xterm": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "hand2": {16: (7, 2), 24: (11, 3), 32: (14, 4)},
    "watch": {16: (7, 5), 24: (11, 8), 32: (14, 10)},
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
}
# A grid pixel that must be black (the face) and one that must be white (the
# outline) at the same place in every nominal size.
PINNED_PIXELS = {
    "left_ptr": {"face": (1, 1), "outline": (0, 0)},
    "xterm": {"face": (7, 7), "outline": (6, 7)},
    "hand2": {"face": (7, 2), "outline": (7, 1)},
    "watch": {"face": (7, 5), "outline": (6, 5)},
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
            with self.subTest(size=image.nominal_size):
                width, height, rgba = decode_rgba(image.png)
                hotspot = (image.hotspot_x, image.hotspot_y)
                self.assertEqual(hotspot, HOTSPOTS["left_ptr"][image.nominal_size])
                self.assertEqual(
                    _pixel(rgba, width, 0, 0), (255, 255, 255, 255)
                )
                self.assertEqual(
                    _pixel(rgba, width, *hotspot), (0, 0, 0, 255)
                )
                self.assertEqual(
                    _pixel(rgba, width, width - 1, height - 1),
                    (0, 0, 0, 0),
                )

    def test_aliases_are_byte_identical_to_left_ptr(self):
        expected = LEFT_PTR.read_bytes()
        for name in ALIASES["left_ptr"]:
            with self.subTest(name=name):
                self.assertEqual((CURSORS / name).read_bytes(), expected)

    def test_committed_artifact_is_a_fresh_generator_result(self):
        self.assertEqual(LEFT_PTR.read_bytes(), make_cursors.cursor_bytes())

    def test_a_corrupted_grid_dropped_size_or_moved_hotspot_changes_the_artifact(self):
        rows = list(cursor_art.ARROW_GRID)
        rows[1] = rows[1][0] + "." + rows[1][2:]
        variants = {
            "corrupted grid": make_cursors.cursor_bytes(rows=tuple(rows)),
            "dropped size": make_cursors.cursor_bytes(sizes=(16, 24)),
            "moved hotspot": make_cursors.cursor_bytes(hotspot=(2, 2)),
        }
        expected = LEFT_PTR.read_bytes()
        for name, data in variants.items():
            with self.subTest(variant=name):
                self.assertNotEqual(data, expected)

    def test_reader_rejects_a_truncated_or_corrupted_copy(self):
        tmp = make_tmp_dir(self)
        truncated = tmp / "truncated"
        truncated.write_bytes(LEFT_PTR.read_bytes()[:20])
        corrupted = tmp / "corrupted"
        corrupted.write_bytes(b"Xcur" + b"\xff" * 28)
        for name, path in (("truncated", truncated), ("corrupted", corrupted)):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    _read_cursor(path)

    def test_generator_refuses_a_grid_with_an_unknown_cell(self):
        rows = list(cursor_art.ARROW_GRID)
        rows[3] = "x" + rows[3][1:]
        with self.assertRaises(ValueError) as caught:
            make_cursors.cursor_bytes(rows=tuple(rows))
        self.assertIn("(0, 3)", str(caught.exception))

    def test_generator_refuses_a_cursors_directory_that_escapes_the_repository(self):
        tmp = make_tmp_dir(self)
        outside = make_tmp_dir(self)
        directory = tmp / make_cursors.PACKAGE_DIR / make_cursors.CURSORS_DIR
        directory.parent.mkdir(parents=True)
        os.symlink(outside, directory)
        stderr = io.StringIO()
        with mock.patch.object(make_cursors, "ROOT", tmp):
            with contextlib.redirect_stderr(stderr):
                status = make_cursors.main([])
        self.assertEqual(status, 2)
        self.assertIn(str(directory), stderr.getvalue())
        self.assertEqual(list(outside.iterdir()), [])


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
            cursor = _read_cursor(CURSORS / name)
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
            expected = (CURSORS / name).read_bytes()
            for alias in ALIASES[name]:
                with self.subTest(name=name, alias=alias):
                    self.assertEqual((CURSORS / alias).read_bytes(), expected)

    def test_every_committed_cursor_is_a_fresh_generator_result(self):
        for canonical, rows, hotspot, aliases in cursor_art.CURSORS:
            expected = make_cursors.cursor_bytes(
                rows=rows, hotspot=hotspot, name=canonical
            )
            for name in (canonical, *aliases):
                with self.subTest(name=name):
                    self.assertEqual((CURSORS / name).read_bytes(), expected)

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
                self.assertEqual(data, (CURSORS / name).read_bytes())

    def test_a_corrupted_grid_dropped_size_or_moved_hotspot_changes_each_glyph(self):
        for canonical, rows, hotspot, _ in cursor_art.CURSORS:
            committed = (CURSORS / canonical).read_bytes()
            mutated = list(rows)
            y = next(index for index, row in enumerate(mutated) if "#" in row)
            x = mutated[y].index("#")
            mutated[y] = mutated[y][:x] + "." + mutated[y][x + 1 :]
            variants = {
                "corrupted grid": make_cursors.cursor_bytes(
                    rows=tuple(mutated), hotspot=hotspot, name=canonical
                ),
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

    def test_an_unknown_cell_names_the_glyph(self):
        for canonical, rows, hotspot, _ in cursor_art.CURSORS:
            mutated = list(rows)
            mutated[0] = "x" + mutated[0][1:]
            with self.subTest(name=canonical):
                with self.assertRaises(ValueError) as caught:
                    make_cursors.cursor_bytes(
                        rows=tuple(mutated), hotspot=hotspot, name=canonical
                    )
                self.assertIn(
                    f"{canonical} grid cell (0, 0)", str(caught.exception)
                )

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
        for y in range(size):
            for x in range(size):
                if _pixel(rgba, size, x, y) == BLACK:
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
                if (x, y) in slash or (x, y) in slash_outline:
                    continue
                if (x - 7.5) ** 2 + (y - 7.5) ** 2 < 7.0**2:
                    with self.subTest(interior=(x, y)):
                        self.assertNotEqual(
                            _pixel(rgba, width, x, y), WHITE
                        )
    def test_dnd_copy_is_a_centred_plus(self):
        cursor = _read_cursor(CURSORS / "dnd-copy")
        image = next(
            image for image in cursor.images if image.nominal_size == 16
        )
        width, _, rgba = decode_rgba(image.png)
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

    def test_dnd_aliases_reuse_the_landed_glyphs(self):
        for alias, canonical in (
            ("dnd-move", "fleur"),
            ("dnd-none", "left_ptr"),
            ("forbidden", "not-allowed"),
            ("no-drop", "not-allowed"),
            ("dnd-no-drop", "not-allowed"),
        ):
            with self.subTest(alias=alias):
                self.assertEqual(
                    (CURSORS / alias).read_bytes(),
                    (CURSORS / canonical).read_bytes(),
                )


    def test_help_pins_the_arrow_and_question_mark(self):
        cursor = _read_cursor(CURSORS / "help")
        image = next(
            image for image in cursor.images if image.nominal_size == 16
        )
        width, _, rgba = decode_rgba(image.png)
        for x, y in ((1, 1), (10, 3), (13, 5), (12, 7)):
            with self.subTest(black=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), BLACK)
        for x, y in ((0, 0), (12, 6)):
            with self.subTest(white=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), WHITE)

    def test_progress_pins_the_arrow_and_hourglass(self):
        cursor = _read_cursor(CURSORS / "progress")
        image = next(
            image for image in cursor.images if image.nominal_size == 16
        )
        width, _, rgba = decode_rgba(image.png)
        for x, y in ((1, 1), (10, 9), (11, 10), (11, 11), (11, 12), (12, 11), (10, 13)):
            with self.subTest(black=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), BLACK)
        for x, y in ((12, 8), (12, 14)):
            with self.subTest(white=(x, y)):
                self.assertEqual(_pixel(rgba, width, x, y), WHITE)

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
        for x, y in ((7, 5), (7, 9)):
            self.assertEqual(_pixel(zoom_out, width, x, y), TRANSPARENT)

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
                    (CURSORS / alias).read_bytes(),
                    (CURSORS / canonical).read_bytes(),
                )


class TestGridValidation(unittest.TestCase):
    """The grid checks turn a bad contributor edit into a named ValueError."""

    def test_refuses_a_grid_with_the_wrong_row_count(self):
        for name, rows, _, _ in cursor_art.CURSORS:
            with self.subTest(name=name):
                with self.assertRaises(ValueError) as caught:
                    make_cursors._checked_rows(rows[:-1], name)
                self.assertIn(
                    f"the {name} grid must have 16 rows, not 15",
                    str(caught.exception),
                )

    def test_refuses_a_row_that_is_not_a_grid_width_string(self):
        for name, rows, _, _ in cursor_art.CURSORS:
            short = list(rows)
            short[0] = short[0][:-1]
            non_text = list(rows)
            non_text[0] = 1
            for rows, width in ((short, "15"), (non_text, "int")):
                with self.subTest(name=name, width=width):
                    with self.assertRaises(ValueError) as caught:
                        make_cursors._checked_rows(rows, name)
                    self.assertIn(
                        f"{name} grid row 0 must be a 16-character string, "
                        f"not {width}",
                        str(caught.exception),
                    )


class TestGeneratorValidation(unittest.TestCase):
    """Pin the size and hotspot refusals ``cursor_bytes`` builds on."""

    def test_render_rgba_refuses_a_size_that_is_not_a_positive_integer(self):
        for size in (0, -1, True, 1.5):
            with self.subTest(size=size):
                with self.assertRaises(ValueError) as caught:
                    make_cursors.render_rgba(cursor_art.ARROW_GRID, size)
                self.assertIn(
                    f"size must be a positive integer: size={size!r}",
                    str(caught.exception),
                )

    def test_scaled_hotspot_refuses_one_that_is_not_two_integers(self):
        for hotspot in ((1,), (1, 2, 3), ("a", 1), (1.5, 1)):
            with self.subTest(hotspot=hotspot):
                with self.assertRaises(ValueError) as caught:
                    make_cursors._scaled_hotspot(16, hotspot)
                self.assertIn(
                    f"hotspot must be two integers: hotspot={hotspot!r}",
                    str(caught.exception),
                )

    def test_scaled_hotspot_refuses_one_outside_the_grid(self):
        for hotspot in ((-1, 1), (16, 1), (1, -1), (1, 16)):
            with self.subTest(hotspot=hotspot):
                with self.assertRaises(ValueError) as caught:
                    make_cursors._scaled_hotspot(16, hotspot)
                self.assertIn(
                    f"hotspot {hotspot} lies outside the 16x16 grid",
                    str(caught.exception),
                )

    def test_cursor_bytes_refuses_a_bad_nominal_size(self):
        for sizes in ((0,), (True,)):
            with self.subTest(sizes=sizes):
                with self.assertRaises(ValueError) as caught:
                    make_cursors.cursor_bytes(sizes=sizes)
                self.assertIn(
                    f"nominal size must be a positive integer: size={sizes[0]!r}",
                    str(caught.exception),
                )

    def test_cursor_bytes_requires_at_least_one_size(self):
        with self.assertRaises(ValueError) as caught:
            make_cursors.cursor_bytes(sizes=())
        self.assertIn("at least one nominal size is required", str(caught.exception))


class TestMainErrors(unittest.TestCase):
    """``main`` must report a creation or write failure and stop, exiting 2."""

    def test_reports_a_cursors_path_that_is_a_file(self):
        tmp = make_tmp_dir(self)
        blocked = tmp / make_cursors.PACKAGE_DIR / make_cursors.CURSORS_DIR
        blocked.parent.mkdir(parents=True)
        blocked.write_text("occupied", encoding="utf-8")
        stderr = io.StringIO()
        with mock.patch.object(make_cursors, "ROOT", tmp):
            with contextlib.redirect_stderr(stderr):
                status = make_cursors.main([])
        self.assertEqual(status, 2)
        self.assertIn(f"cannot create {blocked}", stderr.getvalue())
        self.assertEqual("occupied", blocked.read_text(encoding="utf-8"))

    def test_reports_a_failed_write_and_stops_at_that_cursor(self):
        tmp = make_tmp_dir(self)
        directory = tmp / make_cursors.PACKAGE_DIR / make_cursors.CURSORS_DIR
        real_write = make_cursors.write_bytes_atomically
        attempted = []

        def flaky_write(path, data):
            attempted.append(path.name)
            if path.name == "arrow":
                raise OSError("simulated failure")
            real_write(path, data)

        stderr = io.StringIO()
        with mock.patch.object(make_cursors, "ROOT", tmp):
            with mock.patch.object(
                make_cursors, "write_bytes_atomically", flaky_write
            ):
                with contextlib.redirect_stderr(stderr):
                    status = make_cursors.main([])
        self.assertEqual(status, 2)
        self.assertIn(
            f"cannot write {directory / 'arrow'}: simulated failure",
            stderr.getvalue(),
        )
        self.assertEqual(["left_ptr", "arrow"], attempted)
        self.assertEqual(
            ["left_ptr"], sorted(path.name for path in directory.iterdir())
        )


if __name__ == "__main__":
    unittest.main()
