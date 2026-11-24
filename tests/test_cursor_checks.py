"""Unit tests for the dispatch in ``tools.cursor.checks.checked_art``.

``checked_art`` either passes a ``VectorCursor`` through unchanged or checks a
pixel grid with ``checked_rows``, forwarding the caller's art name so the
refusal names the cursor. ``make_cursors`` branches on the returned object's
type, so both halves must hold.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401
from tools.cursor import checks as cursor_checks
from tools.cursor.vector import VectorCursor

# A valid 16x16 grid of white pixels: each row is a 16-character string of
# characters the cursor art accepts ("." is a white pixel).
GRID = tuple("." * 16 for _ in range(16))


def _square_art() -> VectorCursor:
    return VectorCursor(
        face=((0, 0), (32, 0), (32, 32), (0, 32)), outline_width=0, design_size=32
    )


class TestCheckedArt(unittest.TestCase):
    def test_a_vector_cursor_is_returned_as_the_same_object(self):
        art = _square_art()

        self.assertIs(cursor_checks.checked_art(art), art)

    def test_a_valid_grid_is_returned_as_a_tuple_of_its_rows(self):
        self.assertEqual(cursor_checks.checked_art(list(GRID)), GRID)
        self.assertEqual(cursor_checks.checked_art(GRID), GRID)

    def test_a_grid_refusal_names_the_art_the_caller_passed(self):
        with self.assertRaisesRegex(
            ValueError, r"^the hand grid must have 16 rows, not 15$"
        ):
            cursor_checks.checked_art(GRID[:-1], "hand")

    def test_a_grid_refusal_defaults_the_name_to_arrow(self):
        rows = list(GRID)
        rows[0] = 1

        with self.assertRaisesRegex(
            ValueError, r"^arrow grid row 0 must be a 16-character string, not int$"
        ):
            cursor_checks.checked_art(rows)

    def test_a_cell_outside_the_pixel_alphabet_is_refused_under_the_given_name(self):
        rows = list(GRID)
        rows[3] = "x" + rows[3][1:]

        with self.assertRaisesRegex(ValueError, r"^ibeam grid cell \(0, 3\) is 'x'"):
            cursor_checks.checked_art(rows, "ibeam")

    def test_a_non_sequence_that_is_not_a_grid_is_refused(self):
        with self.assertRaisesRegex(ValueError, r"^the arrow grid must have 16 rows, not str$"):
            cursor_checks.checked_art("not a grid")


if __name__ == "__main__":
    unittest.main()