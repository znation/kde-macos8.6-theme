"""The shipped-file walk must not follow a contributor-supplied symlink.

``shipped_files`` derives the set of files a package ships for the registry
tests. A package directory is contributor-supplied and git stores symlinks, so
a checked-in link at the package root -- or an ancestor of the root, even when
the root is spelled with a trailing separator or a ``..`` component that hides
the link -- makes ``os.walk`` list whatever
it names, and the registry assertion echoes those names into a failing test's
diagnostic. ``make install`` already refuses every theme symlink; the walk
refuses one too, before it lists anything.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from support.shipped_files import shipped_files


class TestShippedFilesSymlinks(unittest.TestCase):
    def test_refuses_a_symlinked_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "private"
            target.mkdir()
            (target / "secret.png").write_bytes(b"")
            root = Path(tmp) / "package"
            root.symlink_to(target, target_is_directory=True)
            with self.assertRaises(ValueError) as caught:
                shipped_files(root)
        self.assertIn(str(root), str(caught.exception))

    def test_refuses_a_symlinked_root_with_a_trailing_separator(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "private"
            target.mkdir()
            (target / "secret.png").write_bytes(b"")
            root = Path(tmp) / "package"
            root.symlink_to(target, target_is_directory=True)
            with self.assertRaises(ValueError) as caught:
                shipped_files(str(root) + os.sep)
        self.assertIn(str(root), str(caught.exception))

    def test_refuses_a_symlinked_ancestor_of_the_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            private = Path(tmp) / "private"
            (private / "org.macos8.desktop").mkdir(parents=True)
            (private / "org.macos8.desktop" / "secret.png").write_bytes(b"")
            theme = Path(tmp) / "theme"
            theme.mkdir()
            icons = theme / "icons"
            icons.symlink_to(private, target_is_directory=True)
            root = icons / "org.macos8.desktop"
            with self.assertRaises(ValueError) as caught:
                shipped_files(root, anchor=tmp)
        self.assertIn(str(icons), str(caught.exception))

    def test_refuses_an_ancestor_link_hidden_behind_a_dot_dot_component(self):
        # ``abspath`` collapses ``..`` lexically, which can erase a symlinked
        # component before ``islink`` sees it while ``os.walk`` still resolves
        # the given path through the link physically. The scan must read the
        # path as given, so this spelling is refused too.
        with tempfile.TemporaryDirectory() as tmp:
            private = Path(tmp) / "private"
            (private / "org.macos8.desktop").mkdir(parents=True)
            (private / "org.macos8.desktop" / "secret.png").write_bytes(b"")
            theme = Path(tmp) / "theme"
            theme.mkdir()
            icons = theme / "icons"
            icons.symlink_to(private, target_is_directory=True)
            root = (
                str(icons) + os.sep + ".." + os.sep
                + "private" + os.sep + "org.macos8.desktop"
            )
            with self.assertRaises(ValueError) as caught:
                shipped_files(root, anchor=tmp)
        self.assertIn(str(icons), str(caught.exception))

    def test_follows_a_symlinked_ancestor_above_the_anchor(self):
        # The scan stops at the anchor, so a benign symlinked ancestor above
        # the trusted boundary -- a symlinked TMPDIR on the host, say -- does
        # not fail a clean tree.
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "outside"
            (outside / "package").mkdir(parents=True)
            (outside / "package" / "real.txt").write_text(
                "shipped", encoding="utf-8"
            )
            link = Path(tmp) / "link"
            link.symlink_to(outside, target_is_directory=True)
            self.assertEqual(
                shipped_files(link / "package", anchor=outside),
                {"real.txt"},
            )

    def test_refuses_a_symlink_inside_the_package(self):
        for kind in ("file", "directory", "contained"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "package"
                root.mkdir()
                (root / "real.txt").write_text("shipped", encoding="utf-8")
                if kind == "file":
                    target = Path(tmp) / "private.png"
                    target.write_bytes(b"")
                    link = root / "secret.png"
                elif kind == "directory":
                    target = Path(tmp) / "private"
                    target.mkdir()
                    (target / "secret.png").write_bytes(b"")
                    link = root / "secret"
                else:
                    target = root / "real.txt"
                    link = root / "alias.txt"
                link.symlink_to(target, target_is_directory=target.is_dir())
                with self.assertRaises(ValueError) as caught:
                    shipped_files(root)
            self.assertIn(str(link), str(caught.exception))

    def test_lists_a_clean_tree_as_package_relative_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sub").mkdir()
            (root / "real.txt").write_text("text", encoding="utf-8")
            (root / "sub" / "widget.svg").write_text("<svg/>", encoding="utf-8")
            (root / "other.png").write_bytes(b"")
            self.assertEqual(
                shipped_files(root),
                {"real.txt", "sub/widget.svg", "other.png"},
            )
            self.assertEqual(shipped_files(root, suffix=".svg"), {"sub/widget.svg"})


if __name__ == "__main__":
    unittest.main()
