"""Pins the lifecycle of the hidden ``.backup`` siblings that ``commit`` makes.

A target that never changed keeps no backup, a cleanup failure after
publishing is reported, foreign siblings are left alone, and a name
collision retries. Rollback of an earlier target after a failed step is
pinned in ``tests/test_gtk_staging_commit.py``; this module covers the backup
files themselves.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.gtk.staging_case import StagingTestCase
from support.theme_install import write_file
from support.unlink_failure import unlink_failing_for
from tools.gtk.staging import commit, stage_all
from tools.config_read import ConfigError


class TestCommitBackups(StagingTestCase):
    """The ``.backup`` sibling each ``commit`` target gets, and when it is removed."""

    def test_a_failed_first_rename_leaves_no_backup_sibling(self):
        target = self.root / "gtk-3.0" / "settings.ini"
        write_file(target, "old settings\n")
        staged = stage_all([(target, "new settings\n")])

        with mock.patch.object(os, "replace", self.fail_the_staged_rename(target)):
            with self.assertRaises(ConfigError):
                commit(staged)

        # The target was never changed, so restoring it must drop the backup
        # link instead of renaming two links to the same inode, a no-op that
        # would leave the backup sibling behind.
        self.assertEqual("old settings\n", target.read_text(encoding="utf-8"))
        self.assertEqual([], self.backups_of(target))

    def test_a_failed_removal_unlink_leaves_no_backup_sibling(self):
        css = self.root / "gtk-4.0" / "gtk.css"
        write_file(css, "marker\n")

        with unlink_failing_for(css):
            with self.assertRaises(ConfigError):
                commit([], removals=[css])

        # The css still exists, so its backup is a link to the same inode;
        # rollback must remove that link rather than leave it behind.
        self.assertEqual("marker\n", css.read_text(encoding="utf-8"))
        self.assertEqual([], self.backups_of(css))

    def test_run_a_second_commit_after_a_failure_leaves_no_backups(self):
        target = self.root / "gtk-3.0" / "settings.ini"
        write_file(target, "old settings\n")
        staged = stage_all([(target, "new settings\n")])

        with mock.patch.object(os, "replace", self.fail_the_staged_rename(target)):
            with self.assertRaises(ConfigError):
                commit(staged)

        commit(stage_all([(target, "new settings\n")]))

        self.assertEqual("new settings\n", target.read_text(encoding="utf-8"))
        self.assertEqual([], self.backups_of(target))

    def test_removals_delete_the_named_files_and_leave_no_backup(self):
        css = self.root / "gtk-4.0" / "gtk.css"
        write_file(css, "marker\n")

        commit([], removals=[css])

        self.assertFalse(css.exists())
        self.assertEqual([], self.backups_of(css))

    def test_a_backup_cleanup_failure_is_reported_after_publish(self):
        target = self.root / "settings.ini"
        target.write_text("old settings\n", encoding="utf-8")
        staged = stage_all([(target, "new settings\n")])
        real_unlink = Path.unlink

        def fail_backup_cleanup(path, *args, **kwargs):
            if str(path).endswith(".backup"):
                raise OSError("injected backup cleanup failure")
            return real_unlink(path, *args, **kwargs)

        with mock.patch.object(Path, "unlink", fail_backup_cleanup):
            with self.assertRaises(ConfigError) as caught:
                commit(staged)

        self.assertIn("cannot remove backup", str(caught.exception))
        self.assertIn("injected backup cleanup failure", str(caught.exception))
        self.assertEqual("new settings\n", target.read_text(encoding="utf-8"))
        self.assertEqual(1, len(self.backups_of(target)))

    def test_backup_cleanup_continues_and_reports_every_failure(self):
        targets = [self.root / name for name in ("first", "second", "third")]
        for target in targets:
            target.write_text("old settings\n", encoding="utf-8")
        staged = stage_all([(target, "new settings\n") for target in targets])
        real_unlink = Path.unlink

        def fail_two_backups(path, *args, **kwargs):
            if path.name.startswith((".first.", ".third.")) and path.suffix == ".backup":
                raise OSError("injected backup cleanup failure")
            return real_unlink(path, *args, **kwargs)

        with mock.patch.object(Path, "unlink", fail_two_backups):
            with self.assertRaises(ConfigError) as caught:
                commit(staged)

        for target in targets:
            self.assertEqual("new settings\n", target.read_text(encoding="utf-8"))
            self.assertFalse(self.staging_of(target).exists())
        self.assertEqual([], self.backups_of(targets[1]))
        for target in (targets[0], targets[2]):
            backups = self.backups_of(target)
            self.assertEqual(1, len(backups))
            self.assertIn(f"cannot remove backup {backups[0]}:", str(caught.exception))
            self.assertEqual("old settings\n", backups[0].read_text(encoding="utf-8"))

    def test_a_foreign_backup_sibling_is_left_untouched(self):
        target = self.root / "gtk-3.0" / "settings.ini"
        write_file(target, "old settings\n")
        foreign = target.with_name(f".{target.name}.backup")
        foreign.write_text("user data\n", encoding="utf-8")

        commit(stage_all([(target, "new settings\n")]))

        self.assertEqual("new settings\n", target.read_text(encoding="utf-8"))
        self.assertEqual("user data\n", foreign.read_text(encoding="utf-8"))
        self.assertEqual([], self.backups_of(target))

    def test_a_backup_name_collision_retries_without_touching_the_foreign_file(self):
        target = self.root / "settings.ini"
        target.write_bytes(b"old settings\n")
        foreign = target.with_name(f".{target.name}.occupied.backup")
        foreign.write_bytes(b"user backup\n")
        staged = stage_all([(target, "new settings\n")])

        with mock.patch(
            "tools.gtk.staging.secrets.token_hex",
            side_effect=["occupied", "available"],
        ) as token:
            commit(staged)

        self.assertEqual([mock.call(8), mock.call(8)], token.call_args_list)
        self.assertEqual(b"new settings\n", target.read_bytes())
        self.assertEqual(b"user backup\n", foreign.read_bytes())
        self.assertEqual([foreign], self.backups_of(target))
        self.assertFalse(self.staging_of(target).exists())

    def test_exhausted_backup_names_restore_an_earlier_write(self):
        first = self.root / "first.ini"
        blocked = self.root / "second.ini"
        first.write_bytes(b"old first\n")
        blocked.write_bytes(b"old second\n")
        foreign = blocked.with_name(f".{blocked.name}.occupied.backup")
        foreign.write_bytes(b"user backup\n")
        staged = stage_all([(first, "new first\n"), (blocked, "new second\n")])

        with mock.patch(
            "tools.gtk.staging.secrets.token_hex", return_value="occupied"
        ):
            with self.assertRaises(ConfigError) as caught:
                commit(staged)

        self.assertIn(f"cannot write {blocked}", str(caught.exception))
        self.assertIn(f"cannot name a backup for {blocked}", str(caught.exception))
        self.assertEqual(b"old first\n", first.read_bytes())
        self.assertEqual(b"old second\n", blocked.read_bytes())
        self.assertEqual(b"user backup\n", foreign.read_bytes())
        self.assertEqual([], self.backups_of(first))
        self.assertEqual([foreign], self.backups_of(blocked))
        for _, staging in staged:
            self.assertFalse(staging.exists())


if __name__ == "__main__":
    unittest.main()
