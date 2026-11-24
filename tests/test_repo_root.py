"""Tests for tests/support/repo_root.py -- the suite's repository-root bootstrap.

The test modules and their helpers reach the ``tools/`` package by its dotted
name, which needs the repository root on ``sys.path``. ``repo_root`` finds that
root and inserts it, then re-exports the one production ``tools.repo_root``
value; these tests pin that the value really is the repository root, that the
tools share it, and that importing it twice does not stack a second copy on
``sys.path``. ``patched_root``, the shared containment swap, is pinned here
too: it points the calling test module's ``ROOT`` global at a fixture and
restores the original binding on exit, leaving every other module's binding
alone.
"""

from __future__ import annotations

import importlib
import os
import sys
import unittest

from support import repo_root
from support.repo_root import ROOT, patched_root
from tools import apply_theme, check_references, make_cursors, make_sheets, make_wallpaper
from tools import reference_validation, theme_defaults
from tools.render import setup as render_setup, workflow as render_workflow
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
            make_sheets,
            make_wallpaper,
            reference_validation,
            render_setup,
            render_workflow,
            theme_defaults,
        ):
            with self.subTest(module=module.__name__):
                self.assertIs(module.ROOT, tools_root.ROOT)


class TestPatchedRoot(unittest.TestCase):
    """The shared containment swap patches the caller and restores it."""

    def test_patched_root_shows_the_fixture_to_the_callers_globals(self):
        # The helper resolves the caller with sys._getframe(1): swapping this
        # test module's binding must be visible to code reading that global,
        # and must not raise on the helper's own module (which has no ROOT).
        fixture = object()
        with patched_root(fixture):
            self.assertIs(ROOT, fixture)

    def test_patched_root_restores_the_original_binding_on_exit(self):
        original = ROOT
        fixture = object()
        with patched_root(fixture):
            self.assertIsNot(ROOT, original)
        self.assertIs(ROOT, original)

    def test_patched_root_restores_the_original_binding_when_the_body_raises(self):
        # A containment refusal test asserts inside the swap; a failed
        # assertion must not leak the fixture into the remaining suites.
        original = ROOT
        with self.assertRaises(ValueError):
            with patched_root(object()):
                raise ValueError("the refusal under test")
        self.assertIs(ROOT, original)

    def test_patched_root_leaves_other_modules_bindings_alone(self):
        # Each suite patches only its own binding: the helper module's ROOT
        # and every other module's global keep the shared repository value.
        with patched_root(object()):
            self.assertIs(repo_root.ROOT, tools_root.ROOT)


if __name__ == "__main__":
    unittest.main()
