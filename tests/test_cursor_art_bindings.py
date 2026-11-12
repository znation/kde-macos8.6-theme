"""Tests for the cursor-art data modules' binding contract.

``tools/cursor_art_pointers.py``, ``tools/cursor_art_resize.py`` and
``tools/cursor_art_drag.py`` are pure data modules: each exports 16x16 ASCII
``*_GRID`` tuples, each paired with a hotspot constant, and each docstring
promises that ``tools/cursor_art.py`` binds the module's grids "to their
canonical X names". No existing test reads the data modules directly -- every
cursor test reaches the art through ``cursor_art.CURSORS`` plus the committed
artifacts, so the binding promise itself is unpinned: a grid added to a data
module and never bound would silently ship nothing, the same grid bound twice
would overwrite a cursor's alias set, and a hotspot constant edited in a data
module could drift away from the value ``CURSORS`` carries.

These tests pin the module-to-binding edge directly: every exported grid is
bound exactly once in ``cursor_art.CURSORS`` by the grid object the module
exports, each binding carries the hotspot constant from its own module by
identity, and every hotspot lies inside its grid and names the black ``#``
face the module docstrings promise ("the middle of the stem", "the hands'
crossing point", "the middle of the slash", "the centre" of the drag plus).

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import cursor_art, cursor_art_drag, cursor_art_pointers, cursor_art_resize  # noqa: F401
from tools.cursor_vector import VectorCursor

# Each data module, in the order cursor_art imports them, and the exported
# art each contributes: a ``*_GRID`` pixel grid or a ``*_ART`` VectorCursor.
# Every ``*_GRID`` pairs with ``<grid>_HOTSPOT`` after stripping the ``_GRID``
# suffix, except the arrow's grid, whose hotspot predates that naming rule and
# is ``HOTSPOT``; ``ARROW_ART`` pairs with ``ARROW_HOTSPOT``.
MODULES = (cursor_art_pointers, cursor_art_resize, cursor_art_drag)
# Grids kept exported as the grid reference for the tests that compare the
# arrow's cells. ``cursor_art.CURSORS`` no longer binds them, so each must be
# bound zero times; every other exported art must be bound exactly once.
REFERENCE_GRIDS = frozenset({"ARROW_GRID"})
ARROW_GRID_HOTSPOT_NAME = "HOTSPOT"


def _exported_grid_names(module):
    """Return the exported ``*_GRID`` and ``*_ART`` names of *module*, sorted."""
    return sorted(
        name
        for name in vars(module)
        if name.endswith(("_GRID", "_ART"))
    )


def _hotspot_name(grid_name):
    """Return the hotspot constant name paired with *grid_name*."""
    if grid_name == "ARROW_GRID":
        return ARROW_GRID_HOTSPOT_NAME
    if grid_name.endswith("_ART"):
        return grid_name[: -len("_ART")] + "_HOTSPOT"
    return grid_name[: -len("_GRID")] + "_HOTSPOT"


def _module_exporting_grid(grid):
    """Return the ``(module, grid name)`` exporting *grid*, or ``None``."""
    for module in MODULES:
        for grid_name in _exported_grid_names(module):
            if vars(module)[grid_name] is grid:
                return module, grid_name
    return None


def _bindings():
    """Yield ``(cursor name, module, grid, grid name, hotspot)`` per entry."""
    for name, grid, hotspot, _aliases in cursor_art.CURSORS:
        found = _module_exporting_grid(grid)
        if found is None:
            raise AssertionError(f"{name} binds a grid no data module exports")
        module, grid_name = found
        yield name, module, grid, grid_name, hotspot


class TestCursorArtBindings(unittest.TestCase):
    """Pin the data modules' promise that cursor_art binds each grid once."""

    def test_every_exported_grid_is_bound_exactly_once_in_cursors(self):
        bound_grids = [entry[1] for entry in cursor_art.CURSORS]
        for module in MODULES:
            for grid_name in _exported_grid_names(module):
                grid = vars(module)[grid_name]
                binding_count = sum(bound is grid for bound in bound_grids)
                expected = 0 if grid_name in REFERENCE_GRIDS else 1
                with self.subTest(module=module.__name__, grid=grid_name):
                    self.assertEqual(
                        binding_count,
                        expected,
                        f"{grid_name} is bound {binding_count} times "
                        "in cursor_art.CURSORS; each data module's art must "
                        f"bind exactly {expected} time(s), reference grids "
                        "zero",
                    )

    def test_every_cursor_entry_binds_a_grid_a_data_module_exports(self):
        module_grids = [
            vars(module)[grid_name]
            for module in MODULES
            for grid_name in _exported_grid_names(module)
        ]
        for name, grid, _hotspot, _aliases in cursor_art.CURSORS:
            with self.subTest(cursor=name):
                self.assertTrue(
                    any(grid is exported for exported in module_grids),
                    f"{name} binds a grid no cursor-art data module exports",
                )

    def test_every_binding_carries_its_module_hotspot_constant(self):
        for name, module, _grid, grid_name, hotspot in _bindings():
            expected_hotspot = vars(module)[_hotspot_name(grid_name)]
            with self.subTest(cursor=name):
                self.assertIs(
                    expected_hotspot,
                    hotspot,
                    f"{name} binds hotspot {hotspot!r} instead of its grid "
                    f"module's {grid_name[:-5]} hotspot "
                    f"constant {_hotspot_name(grid_name)}",
                )

    def test_every_hotspot_lies_inside_its_grid_and_names_the_black_face(self):
        for name, _module, grid, _grid_name, hotspot in _bindings():
            x, y = hotspot
            if isinstance(grid, VectorCursor):
                # Vector art measures its hotspot in design units, so it must
                # lie inside the design grid and on the face's own outline.
                with self.subTest(cursor=name):
                    self.assertTrue(
                        0 <= x < grid.design_size and 0 <= y < grid.design_size,
                        f"{name}'s hotspot {(x, y)} lies outside its "
                        f"{grid.design_size}-unit design grid",
                    )
                    self.assertIn(
                        (x, y),
                        [tuple(vertex) for vertex in grid.face],
                        f"{name}'s hotspot {(x, y)} is not a vertex of its face",
                    )
                continue
            with self.subTest(cursor=name):
                self.assertTrue(
                    0 <= x < len(grid) and 0 <= y < len(grid),
                    f"{name}'s hotspot {(x, y)} lies outside its grid",
                )
                self.assertEqual(
                    grid[y][x],
                    "#",
                    f"{name}'s hotspot {(x, y)} does not name the black face "
                    f"the module docstring promises; grid cell is "
                    f"{grid[y][x]!r}",
                )

    def test_every_exported_grid_is_sixteen_by_sixteen_of_face_characters(self):
        # Each data module's docstring promises 16x16 ASCII grids whose cells
        # are ``#`` (black face), ``.`` (white outline) or a space (transparent).
        # make_cursors scales these grids, so a ragged or non-square grid would
        # be drawn wrong without any test noticing.
        allowed = set("#. ")
        for module in MODULES:
            for grid_name in _exported_grid_names(module):
                if not grid_name.endswith("_GRID"):
                    # ``*_ART`` exports are VectorCursor objects, not pixel grids;
                    # the other binding tests pin their hotspot and face instead.
                    continue
                grid = vars(module)[grid_name]
                with self.subTest(grid=grid_name):
                    self.assertEqual(len(grid), 16, f"{grid_name} has {len(grid)} rows")
                    for row_index, row in enumerate(grid):
                        self.assertEqual(
                            len(row), 16,
                            f"{grid_name} row {row_index} is {len(row)} cells wide",
                        )
                        self.assertTrue(
                            set(row) <= allowed,
                            f"{grid_name} row {row_index} has characters "
                            f"outside '#', '.' and space: {row!r}",
                        )


if __name__ == "__main__":
    unittest.main()
