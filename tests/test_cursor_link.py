"""Unit tests for the cursor link's path and symlink-reading helpers.

``tools/cursor_link.py`` decides whether ``~/.icons/<theme>`` is ours by reading
the literal text of the symlink there. The CLI tests in ``test_apply_cursor.py``
only ever create absolute links, so these tests pin the helper's own contract:
it returns the link text exactly as written, without resolving it, including
for relative and dangling links, and returns ``None`` for anything that is not
a symbolic link. ``TestRemoveLink`` pins ``remove_link``'s own return value,
which tells the CLI whether a foreign path was left in place.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import cursor_link


class TestLinkTarget(unittest.TestCase):
    def test_link_lives_under_icons_named_for_the_theme(self):
        home = Path("/home/example")
        self.assertEqual(
            cursor_link.link_target(home),
            home / ".icons" / "org.macos8.desktop",
        )


class TestSymlinkTarget(unittest.TestCase):
    def setUp(self):
        self._scratch = tempfile.TemporaryDirectory()
        self.root = Path(self._scratch.name)
        self.link = self.root / "link"

    def tearDown(self):
        self._scratch.cleanup()

    def test_missing_path_has_no_target(self):
        self.assertIsNone(cursor_link.symlink_target(self.root / "missing"))

    def test_regular_file_has_no_target(self):
        self.link.write_text("not a link", encoding="utf-8")
        self.assertIsNone(cursor_link.symlink_target(self.link))

    def test_real_directory_has_no_target(self):
        self.link.mkdir()
        self.assertIsNone(cursor_link.symlink_target(self.link))

    def test_relative_link_returns_its_text_without_resolving(self):
        os.symlink("../elsewhere/theme", self.link)
        self.assertEqual(cursor_link.symlink_target(self.link),
                         "../elsewhere/theme")

    def test_dangling_link_returns_its_text_without_resolving(self):
        gone = self.root / "gone"
        os.symlink(str(gone), self.link)
        self.assertFalse(gone.exists())
        self.assertEqual(cursor_link.symlink_target(self.link), str(gone))


class TestRemoveLink(unittest.TestCase):
    """remove_link reports whether a path other than our link remains."""

    def setUp(self):
        self._scratch = tempfile.TemporaryDirectory()
        root = Path(self._scratch.name)
        self.home = root / "home"
        self.data_home = root / "data"
        (self.home / ".icons").mkdir(parents=True)
        self.theme = cursor_link.installed_theme(self.data_home)
        self.theme.mkdir(parents=True)
        self.target = cursor_link.link_target(self.home)

    def tearDown(self):
        self._scratch.cleanup()

    def test_our_link_is_removed_and_no_foreign_path_remains(self):
        os.symlink(str(self.theme), self.target)
        path, foreign = cursor_link.remove_link(self.home, self.data_home)
        self.assertEqual(path, self.target)
        self.assertFalse(foreign)
        self.assertFalse(os.path.lexists(self.target))
        self.assertTrue(self.theme.is_dir())

    def test_foreign_link_is_left_in_place_and_reported(self):
        other = self.home / "elsewhere" / cursor_link.CURSOR_THEME
        os.symlink(str(other), self.target)
        path, foreign = cursor_link.remove_link(self.home, self.data_home)
        self.assertEqual(path, self.target)
        self.assertTrue(foreign)
        self.assertEqual(os.readlink(self.target), str(other))

    def test_regular_file_is_left_in_place_and_reported(self):
        self.target.write_text("someone else's file", encoding="utf-8")
        path, foreign = cursor_link.remove_link(self.home, self.data_home)
        self.assertEqual(path, self.target)
        self.assertTrue(foreign)
        self.assertEqual(self.target.read_text(encoding="utf-8"),
                         "someone else's file")

    def test_real_directory_is_left_in_place_and_reported(self):
        self.target.mkdir()
        path, foreign = cursor_link.remove_link(self.home, self.data_home)
        self.assertEqual(path, self.target)
        self.assertTrue(foreign)
        self.assertTrue(self.target.is_dir())

    def test_nothing_at_target_reports_no_foreign_path(self):
        path, foreign = cursor_link.remove_link(self.home, self.data_home)
        self.assertEqual(path, self.target)
        self.assertFalse(foreign)
        self.assertFalse(os.path.lexists(self.target))


class TestRequireInstalled(unittest.TestCase):
    """``require_installed`` names a non-file at a required path as such.

    A directory or dangling link where ``index.theme`` or ``cursors/left_ptr``
    belongs is not missing; calling it missing sends the user to a fix that
    does not match what is on disk.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.data_home = Path(self._tmp.name)
        self.theme = cursor_link.installed_theme(self.data_home)
        self.theme.mkdir(parents=True)
        (self.theme / "cursors").mkdir()
        (self.theme / "index.theme").write_text("[Icon Theme]\n")
        (self.theme / "cursors" / "left_ptr").write_text("")

    def tearDown(self):
        self._tmp.cleanup()

    def test_complete_theme_is_accepted(self):
        self.assertEqual(cursor_link.require_installed(self.data_home), self.theme)

    def test_absent_pointer_is_called_missing(self):
        pointer = self.theme / "cursors" / "left_ptr"
        pointer.unlink()
        with self.assertRaises(cursor_link.CursorError) as ctx:
            cursor_link.require_installed(self.data_home)
        self.assertIn(f"is missing {pointer}", str(ctx.exception))

    def test_directory_at_pointer_is_not_called_missing(self):
        pointer = self.theme / "cursors" / "left_ptr"
        pointer.unlink()
        pointer.mkdir()
        with self.assertRaises(cursor_link.CursorError) as ctx:
            cursor_link.require_installed(self.data_home)
        message = str(ctx.exception)
        self.assertIn(f"is not a regular file: {pointer}", message)
        self.assertNotIn("is missing", message)

    def test_dangling_link_at_index_is_not_called_missing(self):
        index = self.theme / "index.theme"
        index.unlink()
        os.symlink(self.data_home / "nowhere", index)
        with self.assertRaises(cursor_link.CursorError) as ctx:
            cursor_link.require_installed(self.data_home)
        message = str(ctx.exception)
        self.assertIn(f"is not a regular file: {index}", message)
        self.assertNotIn("is missing", message)


if __name__ == "__main__":
    unittest.main()
