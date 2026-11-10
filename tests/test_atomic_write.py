"""Direct tests for tools/atomic_write.py.

The callers' suites pin umask handling and descriptor cleanup; these pin the
helper's own contract: an explicit mode wins over the umask, the temporary
sibling's name prefix is configurable, a failing fill or rename leaves the
previous file intact with no temporary sibling behind.
"""

from __future__ import annotations

import os
import stat
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from tools import atomic_write


class TestWriteAtomically(unittest.TestCase):
    def setUp(self):
        self.directory = tmp_dir.make_tmp_dir(self)
        self.target = self.directory / "target.txt"

    def test_explicit_mode_overrides_the_umask(self):
        previous = os.umask(0o077)
        self.addCleanup(os.umask, previous)
        atomic_write.write_atomically(
            self.target, lambda handle: handle.write(b"x"), mode=0o755
        )
        self.assertEqual(0o755, stat.S_IMODE(self.target.stat().st_mode))

    def test_prefix_names_the_temporary_sibling(self):
        seen = []

        def fill(handle):
            seen.extend(p.name for p in self.directory.iterdir())
            handle.write(b"x")

        atomic_write.write_atomically(self.target, fill, prefix=".custom-")
        self.assertEqual(1, len(seen))
        self.assertTrue(seen[0].startswith(".custom-"), seen)
        self.assertTrue(seen[0].endswith(".tmp"), seen)

    def test_default_prefix_comes_from_the_target_name(self):
        seen = []

        def fill(handle):
            seen.extend(p.name for p in self.directory.iterdir())

        atomic_write.write_atomically(self.target, fill)
        self.assertTrue(seen[0].startswith(".target.txt-"), seen)

    def test_failing_fill_keeps_the_previous_file_and_leaves_no_sibling(self):
        self.target.write_bytes(b"old")

        def fill(handle):
            handle.write(b"partial")
            raise RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            atomic_write.write_atomically(self.target, fill)
        self.assertEqual(b"old", self.target.read_bytes())
        self.assertEqual([self.target], list(self.directory.iterdir()))

    def test_a_failing_rename_keeps_the_previous_file_and_leaves_no_sibling(self):
        """A rename that fails raises with the previous file still in place.

        The rename is the last step that can fail; the cleanup it shares
        with the fill-failure path must also run for it, so a broken
        rename never strands a ``.target.txt-*.tmp`` sibling beside the
        target or destroys the previous contents.
        """
        failure = OSError("rename failed")
        self.target.write_bytes(b"old")
        with mock.patch.object(atomic_write.os, "replace", side_effect=failure):
            with self.assertRaises(OSError) as caught:
                atomic_write.write_atomically(
                    self.target, lambda handle: handle.write(b"x")
                )
        self.assertIs(failure, caught.exception)
        self.assertEqual(b"old", self.target.read_bytes())
        self.assertEqual([self.target], list(self.directory.iterdir()))

    def test_a_directory_target_refuses_the_replace_and_leaves_no_sibling(self):
        """Renaming the sibling over an existing directory fails cleanly.

        ``os.replace`` refuses to put a regular file over a directory
        (EISDIR); the helper must propagate that failure with the
        temporary sibling removed and the directory untouched.
        """
        target = self.directory / "target.txt"
        target.mkdir()
        inner = target / "kept"
        inner.write_bytes(b"inside")

        with self.assertRaises(IsADirectoryError):
            atomic_write.write_atomically(target, lambda handle: handle.write(b"x"))
        self.assertEqual(b"inside", inner.read_bytes())
        self.assertEqual([target], list(self.directory.iterdir()))

    def test_keyboard_interrupt_also_removes_the_sibling(self):
        def fill(handle):
            raise KeyboardInterrupt

        with self.assertRaises(KeyboardInterrupt):
            atomic_write.write_atomically(self.target, fill)
        self.assertEqual([], list(self.directory.iterdir()))

    def test_cleanup_failure_does_not_replace_the_write_failure(self):
        failure = RuntimeError("write failed")
        cleanup = PermissionError("cleanup denied")
        real_unlink = type(self.target).unlink

        def fail_cleanup(path, *args, **kwargs):
            if path.name.startswith(".target.txt-"):
                raise cleanup
            return real_unlink(path, *args, **kwargs)

        def fail_write(handle):
            raise failure

        with mock.patch.object(type(self.target), "unlink", fail_cleanup):
            with self.assertRaises(RuntimeError) as caught:
                atomic_write.write_atomically(self.target, fail_write)
        self.assertIs(failure, caught.exception)
        self.assertIs(cleanup, caught.exception.__cause__)

    def test_close_failure_still_removes_temporary_sibling(self):
        setup_failure = OSError("mode setup failed")
        close_failure = OSError("close failed")
        real_close = os.close

        def close_then_fail(descriptor):
            real_close(descriptor)
            raise close_failure

        with (
            mock.patch.object(atomic_write.os, "fchmod", side_effect=setup_failure),
            mock.patch.object(atomic_write.os, "close", side_effect=close_then_fail),
        ):
            with self.assertRaises(OSError) as caught:
                atomic_write.write_atomically(self.target, lambda handle: None)

        self.assertIs(setup_failure, caught.exception)
        self.assertIs(close_failure, caught.exception.__cause__)
        self.assertEqual([], list(self.directory.iterdir()))

    def test_write_bytes_replaces_existing_contents(self):
        self.target.write_bytes(b"a much longer previous body")
        atomic_write.write_bytes_atomically(self.target, b"new")
        self.assertEqual(b"new", self.target.read_bytes())
        self.assertEqual([self.target], list(self.directory.iterdir()))


if __name__ == "__main__":
    unittest.main()
