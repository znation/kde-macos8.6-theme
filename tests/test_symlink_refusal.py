"""Tests for refusing user paths that are symbolic links."""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.tmp_dir import make_tmp_dir
from tools.symlink_refusal import refuse_symlink


class TestRefuseSymlink(unittest.TestCase):
    def test_refuses_a_dangling_link_without_touching_its_target_name(self):
        root = make_tmp_dir(self)
        link = root / "managed.conf"
        target = root / "missing.conf"
        link.symlink_to(target)

        with self.assertRaisesRegex(
            ValueError,
            rf"cannot write {link}: it is a symbolic link; refusing to replace or delete the link instead of the file it names",
        ):
            refuse_symlink(link, "write", ValueError)

        self.assertTrue(link.is_symlink())
        self.assertFalse(target.exists())

    def test_allows_a_regular_path_even_when_it_does_not_exist(self):
        path = make_tmp_dir(self) / "new.conf"

        refuse_symlink(path, "remove", RuntimeError)

        self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
