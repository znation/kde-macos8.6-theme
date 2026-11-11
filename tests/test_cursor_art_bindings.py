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

# Each data module, in the order cursor_art imports them, and the exported
# grid each contributes. The arrow's hotspot predates the sibling modules'
# naming rule, so its constant is simply ``HOTSPOT``; every other ``*_GRID``
# pairs with ``<grid>_HOTSPOT`` after stripping the ``_GRID`` suffix.
MODULES = (cursor_art_pointers, cursor_art_resize, cursor_art_drag)
ARROW_HOTSPOT_NAME = "HOTSPOT"


def _exported_grid_names(module):
    """Return the exported ``*_GRID`` names of *module*, sorted."""
    return sorted(
        name for name, value in vars(module).items() if name.endswith("_GRID")
    )


def _hotspot_name(grid_name):
    """Return the hotspot constant name paired with *grid_name*."""
    if grid_name == "ARROW_GRID":
        return ARROW_HOTSPOT_NAME
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
                with self.subTest(module=module.__name__, grid=grid_name):
                    self.assertEqual(
                        bound_grids.count(grid),
                        1,
                        f"{grid_name} is bound {bound_grids.count(grid)} times "
                        "in cursor_art.CURSORS; each data module's grid must "
                        "bind exactly once",
                    )

    def test_every_cursor_entry_binds_a_grid_a_data_module_exports(self):
        module_grids = {
            vars(module)[grid_name]
            for module in MODULES
            for grid_name in _exported_grid_names(module)
        }
        for name, grid, _hotspot, _aliases in cursor_art.CURSORS:
            with self.subTest(cursor=name):
                self.assertIn(
                    grid,
                    module_grids,
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


if __name__ == "__main__":
    unittest.main()
