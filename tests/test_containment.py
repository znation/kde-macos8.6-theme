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

import tempfile
import unittest
from pathlib import Path

from support import containment


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


if __name__ == "__main__":
    unittest.main()
