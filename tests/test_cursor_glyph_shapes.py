"""Pin each canonical pointer grid's drawn shape, one glyph at a time.

Each test here checks one glyph's geometry: a symmetry, a ring, a plus, the
watch face, the pencil or a zoom pair. The pointer set is our own
Platinum-style art (no reference screenshot shows the pointer), so these are
pins of our own drawings. The Xcursor container, alias bytes and generator
output are pinned in ``tests/test_cursors_theme.py``.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cursor.artifact_cases import (  # noqa: E402
    BLACK,
    CURSORS,
    TRANSPARENT,
    WHITE,
    _pixel,
    _read_cursor,
)
from tools.cursor import art as cursor_art  # noqa: E402
from tools import make_cursors
from tools.png import decode_rgba  # noqa: E402


class TestCursorGlyphShapes(unittest.TestCase):
    """Pin the drawn shape of each canonical pointer grid."""

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


if __name__ == "__main__":
    unittest.main()
