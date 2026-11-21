"""The guarded byte reader must refuse a symlink that escapes its root.

The desktop-theme copy-identity tests compare two contributor-supplied SVGs
byte for byte, and ``assertEqual`` echoes both byte strings when they differ.
A checked-in symlink at the second path can point at a private file, so the
read must go through ``containment.read_bytes``, which refuses a path that
resolves outside the repository before it is opened. The color-scheme
provenance test feeds a file's comment lines to ``assertIn``/``assertRegex``,
which echo them, so it reads through the matching ``containment.read_text``.
The guard's lexical and resolved boundaries and its single implementation are
pinned in ``tests/test_containment_boundary.py``.
"""

from __future__ import annotations

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


def _assert_fifo_refused_by_child(case, reader, name):
    """Create a FIFO named *name* and assert *reader* refuses it in a child.

    Used by the FIFO tests of :func:`containment.read_bytes` and
    :func:`containment.read_text`; the skip guard and the temporary FIFO are
    the same for both, only the reader and the file name differ.
    """
    if not hasattr(os, "mkfifo"):
        case.skipTest("os.mkfifo is not available on this platform")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        fifo = tmp / name
        os.mkfifo(fifo)
        child = _run_reader_in_child(reader, fifo, tmp)
    assert_fifo_read_refused(case, child, fifo)


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
        _assert_fifo_refused_by_child(self, "read_bytes", "asset.svg")

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

    def test_negative_limit_is_rejected_before_opening_the_path(self):
        with mock.patch.object(
            containment_impl, "open_regular_binary"
        ) as open_file:
            with self.assertRaisesRegex(
                ValueError, r"^byte limit must be non-negative: -1$"
            ):
                containment_impl.read_capped_bytes(
                    "unused.ini", -1, "this test reads"
                )
        open_file.assert_not_called()

    def test_missing_ok_returns_none_for_an_absent_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.ini"
            self.assertIsNone(
                containment_impl.read_capped_bytes(
                    path, 16, "this test reads", missing_ok=True
                )
            )

    def test_missing_ok_still_refuses_an_unreadable_path(self):
        # missing_ok excuses only an absent path. A caller that reads profile
        # files treats None as "no file here" and then writes over it, so an
        # open failure that is not FileNotFoundError must still raise.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            blocker = tmp / "file.ini"
            blocker.write_bytes(b"x")
            with self.assertRaises(NotADirectoryError):
                containment_impl.read_capped_bytes(
                    blocker / "child.ini", 16, "this test reads",
                    missing_ok=True,
                )
            directory = tmp / "dir.ini"
            directory.mkdir()
            with self.assertRaisesRegex(ValueError, "not a regular file"):
                containment_impl.read_capped_bytes(
                    directory, 16, "this test reads", missing_ok=True,
                )

    def test_oversize_refusal_uses_the_callers_error_type(self):
        class Refusal(Exception):
            pass

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oversize.ini"
            path.write_bytes(b"1234")
            with self.assertRaisesRegex(Refusal, "3-byte limit"):
                containment_impl.read_capped_bytes(
                    path, 3, "this test reads", error=Refusal
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
            closed = self._open_with_fstat_failing(path)
            self.assertEqual(1, len(closed))

    def _open_with_fstat_failing(self, path):
        """Open *path* with os.fstat patched to fail; return the closed log."""
        with tracking_closes() as closed:
            with mock.patch.object(
                containment_impl.os,
                "fstat",
                side_effect=OSError("simulated fstat failure"),
            ):
                with self.assertRaises(OSError):
                    containment_impl.open_regular_binary(path)
        return closed


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
        _assert_fifo_refused_by_child(self, "read_text", "MacOS8.colors")

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

    def test_a_symlink_loop_inside_the_root_is_refused_not_resolved(self):
        # ``os.path.realpath`` returns a loop's path unresolved instead of
        # raising, so without the ELOOP stat the loop would look like a plain
        # in-root path and be accepted. The guard must refuse it, and the
        # caller must see the same "symlink escape" refusal as any escape.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            os.symlink(root / "loop_b", root / "loop_a")
            os.symlink(root / "loop_a", root / "loop_b")
            path = str(root / "loop_a")
            self.assertFalse(containment.resolves_within(root, path))
            with self.assertRaises(ValueError) as caught:
                containment.require_within_repo(path, root)
            self.assertIn("symlink escape", str(caught.exception))

    def test_a_loop_in_the_root_itself_fails_closed_for_every_path(self):
        # The root is the trusted side of the comparison. When it is a loop,
        # no path can be proven inside it, so even an ordinary child is refused.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            os.symlink(base / "loop_b", base / "loop_a")
            os.symlink(base / "loop_a", base / "loop_b")
            loop_root = base / "loop_a"
            self.assertFalse(containment.resolves_within(loop_root, loop_root / "child"))

    def test_a_missing_path_inside_the_root_is_still_contained(self):
        # Control for the loop cases: ELOOP alone is the failure, so a path
        # that does not exist yet (ENOENT) still resolves as inside the root.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertTrue(containment.resolves_within(root, root / "not_yet.txt"))


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


if __name__ == "__main__":
    unittest.main()
