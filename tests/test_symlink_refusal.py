"""Tests for refusing user paths that are symbolic links."""

from __future__ import annotations

import re
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

    def test_refuses_a_link_to_an_existing_file_with_the_callers_error_class(self):
        # The caller's own exception class and its action word must both
        # reach the diagnostic; a fixed ValueError or "write" would pass the
        # test above, which uses those values by coincidence.
        root = make_tmp_dir(self)
        target = root / "managed.conf"
        target.write_text("kept\n", encoding="utf-8")
        link = root / "link.conf"
        link.symlink_to(target)

        with self.assertRaisesRegex(
            RuntimeError,
            rf"^cannot remove {re.escape(str(link))}: it is a symbolic link; "
            r"refusing to replace or delete the link instead of the file it names$",
        ):
            refuse_symlink(link, "remove", RuntimeError)

        self.assertTrue(link.is_symlink())
        self.assertEqual(target.read_text(encoding="utf-8"), "kept\n")

    def test_allows_an_existing_regular_file(self):
        # Only a symbolic link is refused; an ordinary file the caller is
        # about to replace must pass through untouched.
        path = make_tmp_dir(self) / "plain.conf"
        path.write_text("plain\n", encoding="utf-8")

        refuse_symlink(path, "write", ValueError)

        self.assertFalse(path.is_symlink())
        self.assertEqual(path.read_text(encoding="utf-8"), "plain\n")


if __name__ == "__main__":
    unittest.main()
