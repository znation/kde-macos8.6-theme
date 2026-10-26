"""Tests for tests/support/repo_root.py -- the suite's repository-root bootstrap.

The test modules and their helpers reach the ``tools/`` package by its dotted
name, which needs the repository root on ``sys.path``. ``repo_root`` finds that
root and inserts it, then re-exports the one production ``tools.repo_root``
value; these tests pin that the value really is the repository root, that the
tools share it, and that importing it twice does not stack a second copy on
``sys.path``.
"""

from __future__ import annotations

import importlib
import os
import sys
import unittest

from support import repo_root
from tools import apply_theme, check_references, make_cursors, make_wallpaper
from tools import reference_validation, render_session, render_surface, theme_defaults
from tools import repo_root as tools_root


class TestRepoRoot(unittest.TestCase):
    def test_root_names_the_repository(self):
        self.assertTrue(
            os.path.isfile(os.path.join(repo_root.ROOT, "Makefile")),
            repo_root.ROOT,
        )
        self.assertTrue(
            os.path.isdir(os.path.join(repo_root.ROOT, "tools")),
            repo_root.ROOT,
        )

    def test_root_is_on_sys_path(self):
        self.assertIn(str(repo_root.ROOT), sys.path)

    def test_reimport_does_not_duplicate_the_entry(self):
        before = sys.path.count(str(repo_root.ROOT))
        importlib.reload(repo_root)
        self.assertEqual(sys.path.count(str(repo_root.ROOT)), before)


class TestSharedRoot(unittest.TestCase):
    """The test bootstrap and the tools that need the root share one value."""

    def test_the_test_bootstrap_uses_the_tools_root(self):
        self.assertIs(repo_root.ROOT, tools_root.ROOT)

    def test_every_tool_that_needs_the_root_imports_it(self):
        for module in (
            apply_theme,
            check_references,
            make_cursors,
            make_wallpaper,
            reference_validation,
            render_session,
            render_surface,
            theme_defaults,
        ):
            with self.subTest(module=module.__name__):
                self.assertIs(module.ROOT, tools_root.ROOT)


if __name__ == "__main__":
    unittest.main()
