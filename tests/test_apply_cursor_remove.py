"""Tests for ``apply_cursor --remove``.

The removal arm of the apply-cursor suite pins that only our symlink is
unlinked (a dangling one included), that foreign paths are kept, that a
missing or non-directory data home is handled, that link-removal, readlink
and data-home inspection failures are reported by path, and that the
kcminputrc reset note is printed while the file is left unedited (a FIFO
included). The workflow and install arms stay in
``tests/test_apply_cursor.py``, the selector arms in
``tests/test_apply_cursor_selection.py``; the shared base is ``CursorTestCase`` in
``tests/support/apply/cursor_case.py``.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import snippet_child
from support.apply.cursor_case import CursorTestCase
from support.process_assertions import (
    assert_exit_2_without_traceback,
    assert_succeeded,
)
from support.theme_install import write_file
from support.unlink_failure import unlink_failing_for
from tools import apply_cursor


class TestRemove(CursorTestCase):
    def make_our_link(self):
        self.link.parent.mkdir(parents=True)
        os.symlink(str(self.installed), str(self.link))

    def clear_link(self):
        if not self.link.is_symlink() and not os.path.lexists(self.link):
            return
        if self.link.is_dir() and not self.link.is_symlink():
            self.link.rmdir()
            return
        self.link.unlink()

    def test_removal_unlinks_only_our_symlink_and_keeps_the_icons_dir(self):
        self.make_our_link()
        result = self.run_tool("--remove")
        assert_succeeded(self, result)
        self.assertFalse(os.path.lexists(self.link))
        self.assertTrue((self.home / ".icons").is_dir())

    def test_data_home_inspection_failure_is_reported_before_removing_link(self):
        self.make_our_link()
        original_stat = Path.stat

        def failing_stat(path, *args, **kwargs):
            if path == self.data:
                raise PermissionError("simulated inspection failure")
            return original_stat(path, *args, **kwargs)

        with mock.patch.object(Path, "stat", failing_stat):
            result = self.run_tool("--remove")

        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot inspect data home {self.data}", result.stderr)
        self.assertTrue(self.link.is_symlink())

    def test_removal_accepts_a_dangling_link_to_our_theme(self):
        self.make_our_link()
        self.assertFalse(self.installed.exists())
        result = self.run_tool("--remove")
        assert_succeeded(self, result)
        self.assertFalse(os.path.lexists(self.link))

    def test_removal_is_repeatable(self):
        self.make_our_link()
        assert_succeeded(self, self.run_tool("--remove"))
        assert_succeeded(self, self.run_tool("--remove"))

    def test_a_missing_data_home_still_removes_our_link(self):
        # The data home can be gone entirely when the removal runs: nothing
        # else owns that path, and a caller may have deleted it after moving
        # the tree (make uninstall removes the installed icon theme, never the
        # data home itself).
        # cursor_workflow.remove stats the data home only to learn whether a
        # directory flock is even available: an absent home means no lock, and
        # the removal must still take its own link down (a run that instead
        # locked unconditionally would fail at os.open's O_DIRECTORY flag).
        self.make_our_link()
        self.assertFalse(self.data.exists())

        result = self.run_tool("--remove")

        assert_succeeded(self, result)
        self.assertNotIn("cannot lock", result.stderr)
        self.assertNotIn("cannot inspect", result.stderr)
        self.assertFalse(os.path.lexists(self.link))
        self.assertTrue((self.home / ".icons").is_dir())

    def test_a_non_directory_data_home_still_removes_our_link(self):
        # A stray regular file at the data-home path carries no directory
        # inode to flock; attempting the lock would fail os.open's
        # O_DIRECTORY check, so the non-directory state must skip the lock
        # and still remove the link instead of printing a refusal.
        self.make_our_link()
        self.data.write_text("stray\n", encoding="utf-8")

        result = self.run_tool("--remove")

        assert_succeeded(self, result)
        self.assertNotIn("cannot lock", result.stderr)
        self.assertFalse(os.path.lexists(self.link))
        self.assertTrue((self.home / ".icons").is_dir())

    def test_removal_leaves_a_foreign_symlink_dir_and_file(self):
        for kind in ("symlink", "directory", "file"):
            with self.subTest(kind=kind):
                self.clear_link()
                self.link.parent.mkdir(parents=True, exist_ok=True)
                if kind == "symlink":
                    elsewhere = self.root / "foreign"
                    os.symlink(str(elsewhere), str(self.link))
                elif kind == "directory":
                    self.link.mkdir()
                else:
                    self.link.write_text("foreign\n", encoding="utf-8")
                result = self.run_tool("--remove")
                assert_succeeded(self, result)
                self.assertIn(str(self.link), result.stdout)
                self.assertTrue(os.path.lexists(self.link))

    def test_a_failed_link_removal_is_reported_by_path(self):
        # The link this tool created can still fail to unlink (a read-only
        # ~/.icons, for example). The OSError must become the tool's own exit-2
        # diagnostic naming the link -- not a traceback -- and the link must
        # stay in place so the operator can retry.
        self.make_our_link()

        with unlink_failing_for(self.link, "simulated unlink failure"):
            result = self.run_tool("--remove")

        assert_exit_2_without_traceback(self, result)
        self.assertIn("cannot remove", result.stderr)
        self.assertIn(str(self.link), result.stderr)
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(str(self.installed), os.readlink(self.link))

    def test_unreadable_cursor_symlink_is_reported_on_removal_without_traceback(self):
        # Removal reads the link's target before deciding whether it is ours.
        # When that read fails, the tool must refuse by path (exit 2, no
        # traceback) and leave the link in place: an unread link is never
        # assumed to be ours and unlinked.
        self.make_our_link()
        real_readlink = os.readlink

        def failing_readlink(path, *args, **kwargs):
            if Path(path) == self.link:
                raise PermissionError("simulated readlink failure")
            return real_readlink(path, *args, **kwargs)

        with mock.patch.object(apply_cursor.os, "readlink", failing_readlink):
            result = self.run_tool("--remove")

        assert_exit_2_without_traceback(self, result)
        self.assertIn("cannot read symlink", result.stderr)
        self.assertIn(str(self.link), result.stderr)
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(str(self.installed), real_readlink(self.link))

    def test_kcminputrc_note_names_the_reset_only_when_our_theme_is_selected(self):
        self.make_our_link()
        kcminputrc = self.config / "kcminputrc"
        write_file(kcminputrc, "[Mouse]\ncursorTheme=org.macos8.desktop\n")
        result = self.run_tool("--remove")
        assert_succeeded(self, result)
        self.assertIn("plasma-apply-cursortheme breeze_cursors", result.stdout)
        self.assertEqual(
            "[Mouse]\ncursorTheme=org.macos8.desktop\n",
            kcminputrc.read_text(encoding="utf-8"),
        )

    def test_kcminputrc_note_is_absent_for_a_foreign_selection(self):
        self.make_our_link()
        kcminputrc = self.config / "kcminputrc"
        write_file(kcminputrc, "[Mouse]\ncursorTheme=Adwaita\n")
        result = self.run_tool("--remove")
        assert_succeeded(self, result)
        self.assertNotIn("breeze_cursors", result.stdout)

    def test_a_fifo_kcminputrc_does_not_block_removal(self):
        # A plain read_text/open on a FIFO waits forever for a writer. Run the
        # removal in a child so a regression is a bounded timeout rather than
        # a stalled check, and the removal still succeeds with no note.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        self.make_our_link()
        self.config.mkdir(parents=True)
        os.mkfifo(self.config / "kcminputrc")
        snippet = (
            "import sys; from tools.apply_cursor import main; "
            "sys.exit(main(sys.argv[1:]))"
        )
        with mock.patch.dict(os.environ, self.env, clear=True):
            child = snippet_child.run(
                [snippet, "--remove"], cwd=repo_root.ROOT, timeout=10
            )
        self.assertEqual(0, child.returncode, child.stdout + child.stderr)
        self.assertFalse(os.path.lexists(self.link))
        self.assertNotIn("breeze_cursors", child.stdout)


if __name__ == "__main__":
    unittest.main()
