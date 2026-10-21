"""The guarded byte reader must refuse a symlink that escapes its root.

The desktop-theme copy-identity tests compare two contributor-supplied SVGs
byte for byte, and ``assertEqual`` echoes both byte strings when they differ.
A checked-in symlink at the second path can point at a private file, so the
read must go through ``containment.read_bytes``, which refuses a path that
resolves outside the repository before it is opened. The color-scheme
provenance test feeds a file's comment lines to ``assertIn``/``assertRegex``,
which echo them, so it reads through the matching ``containment.read_text``.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import containment
from support.repo_root import ROOT
from tools import containment as containment_impl


def _run_reader_in_child(reader, path, root):
    """Run one guarded reader on *path* in a child; return its result.

    A reader handed a FIFO blocks in ``open()`` until a writer appears, so a
    direct call would stall the suite with no diagnostic. The child makes that
    hang a hard timeout instead.
    """
    return subprocess.run(
        [
            sys.executable,
            "-c",
            f"import sys; from tools.containment import {reader}; "
            f"{reader}(sys.argv[1], sys.argv[2])",
            str(path),
            str(root),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )


class TestReadBytes(unittest.TestCase):
    def test_rejects_a_symlink_that_escapes_the_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            secret = tmp / "secret.svg"
            secret.write_bytes(b"PRIVATE-SECRET-BYTES")
            link = root / "solid.svg"
            link.symlink_to(secret)
            with self.assertRaises(ValueError) as caught:
                containment.read_bytes(link, root)
        self.assertIn(str(link), str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_root(self):
        # The guard must refuse only escapes, not a legitimate repository path
        # that happens to be reached through a symlink inside the repository.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            (root / "theme").mkdir(parents=True)
            target = root / "theme" / "solid.svg"
            target.write_bytes(b"inside")
            link = root / "link.svg"
            link.symlink_to(target)
            self.assertEqual(containment.read_bytes(link, root), b"inside")

    def test_reads_a_path_outside_the_root(self):
        # Only a path lexically inside the root is checked, so a test's
        # temporary file is still readable.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            path = tmp / "temp.svg"
            path.write_bytes(b"temp")
            self.assertEqual(
                containment.read_bytes(path, tmp / "repo"), b"temp"
            )

    def test_refuses_a_file_larger_than_the_read_limit(self):
        # The path is contributor-supplied and can name something arbitrarily
        # large; a plain read would allocate the whole file and could raise a
        # MemoryError that no caller catches, so the guard must refuse it by
        # name. A file exactly at the limit is still read (pinned separately by
        # the ordinary reads above).
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            path = tmp / "huge.svg"
            path.write_bytes(b"x" * (containment_impl._MAX_READ_BYTES + 1))
            with self.assertRaises(ValueError) as caught:
                containment.read_bytes(path, tmp / "repo")
        self.assertIn(str(path), str(caught.exception))

    def test_refuses_a_fifo_instead_of_blocking(self):
        # open() on a FIFO blocks until a writer appears, and this reader has
        # no timeout, so a stray pipe at a contributor-file path would stall
        # make check with no diagnostic. Refuse it by name in a child process
        # so the pre-fix hang is a bounded timeout, not a stalled suite.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            fifo = tmp / "asset.svg"
            os.mkfifo(fifo)
            child = _run_reader_in_child("read_bytes", fifo, tmp)
        self.assertNotEqual(0, child.returncode, child.stdout + child.stderr)
        self.assertIn("not a regular file", child.stderr)
        self.assertIn(str(fifo), child.stderr)

    def test_rejects_a_fifo_opened_in_place_of_a_regular_path(self):
        # A regular file can be swapped for a FIFO between a check of the path
        # and the open. Patching os.open to open the FIFO while the path still
        # names a regular file proves the check runs on the opened descriptor,
        # so the swap is refused instead of reading the pipe.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            path = tmp / "asset.svg"
            path.write_bytes(b"inside")
            fifo = tmp / "pipe"
            os.mkfifo(fifo)
            real_open = os.open

            def open_the_fifo(target, flags, *args, **kwargs):
                return real_open(fifo, flags, *args, **kwargs)

            with mock.patch.object(
                containment_impl.os, "open", side_effect=open_the_fifo
            ):
                with self.assertRaises(ValueError) as caught:
                    containment.read_bytes(path, tmp / "repo")
        self.assertIn(str(path), str(caught.exception))
        self.assertIn("not a regular file", str(caught.exception))


class TestReadText(unittest.TestCase):
    def test_rejects_a_symlink_that_escapes_the_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            secret = tmp / "secret.colors"
            secret.write_text("# PRIVATE-SECRET-TEXT", encoding="utf-8")
            link = root / "MacOS8.colors"
            link.symlink_to(secret)
            with self.assertRaises(ValueError) as caught:
                containment.read_text(link, root)
        self.assertIn(str(link), str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_root(self):
        # The guard must refuse only escapes, not a legitimate repository path
        # that happens to be reached through a symlink inside the repository.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            (root / "theme").mkdir(parents=True)
            target = root / "theme" / "MacOS8.colors"
            target.write_text("inside", encoding="utf-8")
            link = root / "link.colors"
            link.symlink_to(target)
            self.assertEqual(containment.read_text(link, root), "inside")

    def test_reads_a_path_outside_the_root(self):
        # Only a path lexically inside the root is checked, so a test's
        # temporary file is still readable.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            path = tmp / "temp.colors"
            path.write_text("temp", encoding="utf-8")
            self.assertEqual(
                containment.read_text(path, tmp / "repo"), "temp"
            )

    def test_refuses_a_file_larger_than_the_read_limit(self):
        # The text reader shares the byte reader's bound: a register or source
        # file far larger than any shipped one must be refused by name rather
        # than loaded whole.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            path = tmp / "huge.colors"
            path.write_bytes(b"x" * (containment_impl._MAX_READ_BYTES + 1))
            with self.assertRaises(ValueError) as caught:
                containment.read_text(path, tmp / "repo")
        self.assertIn(str(path), str(caught.exception))

    def test_refuses_a_fifo_instead_of_blocking(self):
        # A FIFO at a register or colour-scheme path would block the text
        # reader's open() forever; refuse it by name in a child process.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            fifo = tmp / "MacOS8.colors"
            os.mkfifo(fifo)
            child = _run_reader_in_child("read_text", fifo, tmp)
        self.assertNotEqual(0, child.returncode, child.stdout + child.stderr)
        self.assertIn("not a regular file", child.stderr)
        self.assertIn(str(fifo), child.stderr)

    def test_matches_text_mode_newline_and_bom_handling(self):
        # read_text reads bytes to bound the allocation, then decodes through
        # the text layer, so it must still strip a utf-8-sig BOM and translate
        # CRLF and lone CR the way ``open(path, encoding=...)`` does. A bare
        # ``bytes.decode`` would leave the CR bytes in place.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            path = tmp / "crlf.colors"
            path.write_bytes("\ufeffa\r\nb\rc\n".encode("utf-8"))
            with open(path, encoding="utf-8-sig") as handle:
                expected = handle.read()
            self.assertEqual(
                containment.read_text(
                    path, tmp / "repo", encoding="utf-8-sig"
                ),
                expected,
            )


class TestResolutionFailureFailsClosed(unittest.TestCase):
    def test_an_embedded_nul_is_refused_not_raised(self):
        # POSIX ``Path.resolve()`` raises ``ValueError`` for an embedded NUL;
        # the guard must treat that resolution failure like any other and
        # refuse the path, not let the bare error abort the caller's read.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = str(root / "a\x00b")
            self.assertFalse(containment.resolves_within(root, path))
            with self.assertRaises(ValueError) as caught:
                containment.require_within_repo(path, root)
            self.assertIn("symlink escape", str(caught.exception))


class TestIsWithin(unittest.TestCase):
    """The lexical half of the guard must respect the path-component boundary.

    ``is_within`` decides whether a path is even eligible for the symlink
    check: only a path lexically inside the root is resolved and refused. Its
    comparison appends ``os.sep`` to the root, so a sibling directory whose
    name merely shares the root's prefix (``repo-other`` beside ``repo``) is
    outside, not inside. A bare ``startswith(root)`` would judge the sibling
    inside, hand it to the resolver, and refuse a legitimate file outside the
    repository.
    """

    def test_accepts_a_path_under_the_root(self):
        self.assertTrue(
            containment.is_within("/tmp/repo", "/tmp/repo/a.svg")
        )

    def test_accepts_the_root_itself(self):
        self.assertTrue(containment.is_within("/tmp/repo", "/tmp/repo"))

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
        "tests/placeholders.py",
        "tests/invariants.py",
        "tools/theme_defaults.py",
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
