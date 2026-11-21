"""The shared containment guard's boundaries and its single implementation.

These tests pin the lexical path-component boundary (``TestIsWithin``), the
resolved boundary (``TestResolvedBoundary``) and the rule that no contributor-
file reader re-implements the guard (``TestGuardIsShared``). The reader tests
that run the guarded readers on real files stay in ``tests/test_containment.py``.
"""

from __future__ import annotations

import ast
import os
import tempfile
import unittest
from pathlib import Path

from support import containment
from support.repo_root import ROOT


class TestIsWithin(unittest.TestCase):
    """The lexical half of the guard must respect the path-component boundary.

    ``is_within`` decides whether a path is even eligible for the symlink
    check: only a path lexically inside the root is resolved and refused. Its
    comparison appends ``os.sep`` to a root that does not already end with
    one, so a sibling directory whose name merely shares the root's prefix
    (``repo-other`` beside ``repo``) is outside, not inside. A bare
    ``startswith(root)`` would judge the sibling inside, hand it to the
    resolver, and refuse a legitimate file outside the repository. A
    filesystem root already ends with the separator, so appending another
    would make the boundary ``//`` and reject every real child. A POSIX path
    may also spell the root with exactly two leading slashes; both spellings
    must name the same directory in the comparison.
    """

    def test_accepts_a_path_under_the_root(self):
        self.assertTrue(
            containment.is_within("/tmp/repo", "/tmp/repo/a.svg")
        )

    def test_accepts_the_root_itself(self):
        self.assertTrue(containment.is_within("/tmp/repo", "/tmp/repo"))

    def test_accepts_a_path_under_the_filesystem_root(self):
        # A root already ends with the separator, so unconditionally
        # appending another makes the boundary ``//`` and every child fails
        # the lexical check; the guard then skips the symlink check entirely.
        self.assertTrue(containment.is_within("/", "/etc"))

    def test_treats_a_posix_double_slash_spelling_as_the_same_root(self):
        if os.name != "posix":
            self.skipTest("a double leading slash is POSIX-specific")
        self.assertTrue(containment.is_within("//", "/etc"))
        self.assertTrue(
            containment.is_within("//tmp/repo", "/tmp/repo/a.svg")
        )
        self.assertTrue(
            containment.is_within("/tmp/repo", "//tmp/repo/a.svg")
        )
        self.assertFalse(
            containment.is_within("//tmp/repo", "/tmp/repo-other/a.svg")
        )

    def test_rejects_a_sibling_directory_that_shares_the_root_prefix(self):
        self.assertFalse(
            containment.is_within("/tmp/repo", "/tmp/repo-other/a.svg")
        )

    def test_reads_a_sibling_directory_that_shares_the_root_prefix(self):
        # The boundary is load-bearing: with a bare ``startswith(root)`` the
        # sibling is judged inside, ``resolves_within`` resolves it outside
        # the root, and this read raises ValueError instead of returning the
        # file's bytes.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            sibling = tmp / "repo-other"
            sibling.mkdir()
            path = sibling / "asset.svg"
            path.write_bytes(b"sibling")
            self.assertEqual(containment.read_bytes(path, root), b"sibling")


class TestResolvedBoundary(unittest.TestCase):
    """The resolved comparison must respect the path-component boundary.

    ``resolves_within`` compares the resolved path with the resolved root, so
    a sibling directory whose name merely shares the root's prefix is outside.
    ``require_within_repo`` never reaches this comparison for such a path
    because its lexical ``is_within`` skips it first, so the boundary is
    pinned here directly.
    """

    def test_rejects_a_sibling_directory_that_shares_the_root_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            sibling = tmp / "repo-other"
            sibling.mkdir()
            path = sibling / "asset.svg"
            path.write_bytes(b"sibling")
            self.assertFalse(containment.resolves_within(root, path))


class TestGuardIsShared(unittest.TestCase):
    """The containment guard is implemented once; every reader routes to it.

    A refinement to a private copy does not reach the other readers, so the
    contributor-file readers must not carry their own resolution guard. This
    reads each reader's source and rejects a local ``_resolves_within`` or
    ``_require_within_repo`` definition and an inline ``os.path.realpath`` or
    ``is_relative_to`` resolution -- the two mechanisms the five copies used
    before they were routed through ``tools.containment``.
    """

    READERS = (
        "tests/support/placeholders.py",
        "tests/support/invariants.py",
        "tools/theme_defaults.py",
        "tools/reference_sources.py",
        "tools/reference_validation.py",
    )

    def test_no_reader_reimplements_the_guard(self):
        for relative in self.READERS:
            with self.subTest(module=relative):
                tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
                definitions = {
                    node.name
                    for node in ast.walk(tree)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                self.assertNotIn("_resolves_within", definitions)
                self.assertNotIn("_require_within_repo", definitions)
                mechanisms = {
                    node.attr
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Attribute)
                    and node.attr in {"realpath", "is_relative_to"}
                }
                self.assertEqual(mechanisms, set(), mechanisms)


if __name__ == "__main__":
    unittest.main()
