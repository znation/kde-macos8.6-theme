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
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import containment
from support import snippet_child
from support.close_tracking import failing_fdopen, tracking_closes
from support.fifo_fixtures import assert_fifo_read_refused
from support.repo_root import ROOT
from support.symlink_fixtures import symlinked_repo
from tools import containment as containment_impl


def _run_reader_in_child(reader, path, root):
    """Run one guarded reader on *path* in a child; return its result.

    A reader handed a FIFO blocks in ``open()`` until a writer appears, so a
    direct call would stall the suite with no diagnostic. The child makes that
    hang a hard timeout instead.
    """
    return snippet_child.run(
        [
            f"import sys; from tools.containment import {reader}; "
            f"{reader}(sys.argv[1], sys.argv[2])",
            str(path),
            str(root),
        ],
        cwd=ROOT,
        timeout=10,
    )


class TestReadBytes(unittest.TestCase):
    def test_rejects_a_symlink_that_escapes_the_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "solid.svg", b"PRIVATE-SECRET-BYTES"
            )
            with self.assertRaises(ValueError) as caught:
                containment.read_bytes(link, root)
        self.assertIn(str(link), str(caught.exception))

    def test_rejects_a_symlink_escape_when_the_root_has_a_double_slash_prefix(self):
        # POSIX may spell a root with two leading slashes, and os.path.abspath
        # preserves that spelling. If the lexical guard treats it as a
        # different root, it skips the symlink check and returns the secret's
        # bytes instead of refusing the escape.
        if os.name != "posix":
            self.skipTest("a double leading slash is POSIX-specific")
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "solid.svg", b"PRIVATE-SECRET-BYTES"
            )
            double_root = "//" + str(root).lstrip("/")
            with self.assertRaises(ValueError) as caught:
                containment.read_bytes(link, double_root)
        self.assertIn(str(link), str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_root(self):
        # The guard must refuse only escapes, not a legitimate repository path
        # that happens to be reached through a symlink inside the repository.
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "link.svg", b"inside", target="theme/solid.svg"
            )
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

    def test_a_missing_file_raises_file_not_found(self):
        # The shared capped reader returns None for a missing path only when a
        # caller asks for that (the Firefox discovery readers do). A repository
        # reader must still raise FileNotFoundError naming the path instead of
        # turning an absent contributor file into a later None failure.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            path = tmp / "missing.svg"
            with self.assertRaises(FileNotFoundError) as caught:
                containment.read_bytes(path, tmp)
        self.assertIn(str(path), str(caught.exception))

    def test_a_file_exactly_at_the_read_limit_is_read(self):
        # The reader takes one byte past the cap so the boundary is inclusive:
        # a file of exactly _MAX_READ_BYTES is accepted, while the next test
        # shows one byte more is refused. A ``>=`` comparison here would refuse
        # a legitimate source file that happens to reach the cap.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            path = tmp / "at-limit.svg"
            payload = b"x" * containment_impl._MAX_READ_BYTES
            path.write_bytes(payload)
            self.assertEqual(containment.read_bytes(path, tmp / "repo"), payload)

    def test_refuses_a_file_larger_than_the_read_limit(self):
        # The path is contributor-supplied and can name something arbitrarily
        # large; a plain read would allocate the whole file and could raise a
        # MemoryError that no caller catches, so the guard must refuse it by
        # name. A file exactly at the limit is still read (pinned by the
        # exact-limit test above).
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
        assert_fifo_read_refused(self, child, fifo)

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


class TestReadCappedBytes(unittest.TestCase):
    """The shared capped read keeps the missing-file choice to its caller.

    The repository readers need a missing file to raise, while the Firefox
    profile and discovery readers treat one as absent. Both sides go through
    this helper, so its ``missing_ok`` arm is pinned directly rather than only
    through those callers.
    """

    def test_missing_ok_returns_none_for_an_absent_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.ini"
            self.assertIsNone(
                containment_impl.read_capped_bytes(
                    path, 16, "this test reads", missing_ok=True
                )
            )


class TestOpenRegularBinaryCleanup(unittest.TestCase):
    """A failure after the descriptor is opened must close it.

    ``open_regular_binary`` opens the path with ``os.open`` and then inspects
    and wraps that descriptor. If either later step fails, the raw descriptor
    must be closed, or a caller that keeps reading through the guard leaks one
    descriptor per failure. The read paths reach these arms only through a
    filesystem error, so each failure is injected and the closes counted.
    """

    def test_a_failed_fdopen_closes_the_descriptor(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "asset.svg"
            path.write_bytes(b"inside")
            with failing_fdopen() as closed:
                with self.assertRaises(OSError):
                    containment_impl.open_regular_binary(path)
            self.assertEqual(1, len(closed))
            self.assertEqual(b"inside", path.read_bytes())

    def test_a_failed_fstat_closes_the_descriptor(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "asset.svg"
            path.write_bytes(b"inside")
            with tracking_closes() as closed:
                with mock.patch.object(
                    containment_impl.os,
                    "fstat",
                    side_effect=OSError("simulated fstat failure"),
                ):
                    with self.assertRaises(OSError):
                        containment_impl.open_regular_binary(path)
            self.assertEqual(1, len(closed))


class TestReadText(unittest.TestCase):
    def test_rejects_a_symlink_that_escapes_the_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "MacOS8.colors", "# PRIVATE-SECRET-TEXT"
            )
            with self.assertRaises(ValueError) as caught:
                containment.read_text(link, root)
        self.assertIn(str(link), str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_root(self):
        # The guard must refuse only escapes, not a legitimate repository path
        # that happens to be reached through a symlink inside the repository.
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "link.colors", "inside", target="theme/MacOS8.colors"
            )
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
        assert_fifo_read_refused(self, child, fifo)

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
        # POSIX ``os.path.realpath()`` raises ``ValueError`` for an embedded NUL;
        # the guard must treat that resolution failure like any other and
        # refuse the path, not let the bare error abort the caller's read.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = str(root / "a\x00b")
            self.assertFalse(containment.resolves_within(root, path))
            with self.assertRaises(ValueError) as caught:
                containment.require_within_repo(path, root)
            self.assertIn("symlink escape", str(caught.exception))


class TestRefusalNamesTheOperation(unittest.TestCase):
    """The guard's diagnostic names the operation the escape would have reached.

    The same guard refuses a path a caller is about to read and one it is
    about to write (the wallpaper generator's output directory), so the
    message says which one it is: the default is a read, and a caller that
    passes ``action="write"`` says so.
    """

    def escaping_path(self, tmp):
        """Return a path inside *tmp* that resolves outside it."""
        root = tmp / "repo"
        root.mkdir()
        outside = tmp / "outside"
        outside.mkdir()
        path = root / "escape"
        path.symlink_to(outside, target_is_directory=True)
        return path, root

    def test_the_default_refusal_names_a_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, root = self.escaping_path(Path(tmp))
            with self.assertRaises(ValueError) as caught:
                containment.require_within_repo(path, root)
            message = str(caught.exception)
            self.assertIn("refusing to read it", message)
            self.assertIn(str(path), message)

    def test_a_write_refusal_names_the_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, root = self.escaping_path(Path(tmp))
            with self.assertRaises(ValueError) as caught:
                containment.require_within_repo(path, root, action="write")
            message = str(caught.exception)
            self.assertIn("refusing to write it", message)
            self.assertIn("symlink escape", message)


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
