"""Tests for tests/repo_root.py -- the suite's repository-root bootstrap.

The test modules and their helpers reach the ``tools/`` package by its dotted
name, which needs the repository root on ``sys.path``. ``repo_root`` computes
that root once and inserts it; these tests pin that the value really is the
repository root and that importing it twice does not stack a second copy on
``sys.path``.
"""

from __future__ import annotations

import importlib
import os
import sys
import unittest

import repo_root


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


if __name__ == "__main__":
    unittest.main()
