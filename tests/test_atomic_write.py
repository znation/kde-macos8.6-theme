"""Direct tests for tools/atomic_write.py.

The callers' suites pin umask handling and descriptor cleanup; these pin the
helper's own contract: an explicit mode wins over the umask, the temporary
sibling's name prefix is configurable, and a failing fill leaves the previous
file intact with no temporary sibling behind.
"""

from __future__ import annotations

import os
import stat
import unittest

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

    def test_keyboard_interrupt_also_removes_the_sibling(self):
        def fill(handle):
            raise KeyboardInterrupt

        with self.assertRaises(KeyboardInterrupt):
            atomic_write.write_atomically(self.target, fill)
        self.assertEqual([], list(self.directory.iterdir()))

    def test_write_bytes_replaces_existing_contents(self):
        self.target.write_bytes(b"a much longer previous body")
        atomic_write.write_bytes_atomically(self.target, b"new")
        self.assertEqual(b"new", self.target.read_bytes())
        self.assertEqual([self.target], list(self.directory.iterdir()))


if __name__ == "__main__":
    unittest.main()
