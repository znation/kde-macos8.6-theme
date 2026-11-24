"""Direct tests for tools/gtk/staging.py's :func:`commit` replacement and rollback.

A rename that fails during :func:`commit` must be a one-line ``ConfigError``
naming the target, and every leftover ``.staging`` sibling must be removed. A
later failure must restore every target the commit already changed, including
a user-CSS removal, instead of leaving the selection half-applied. That
rollback covers a non-``OSError`` interrupt (Ctrl-C's ``KeyboardInterrupt``) as
well as an errno-carrying failure. The staging and discard helpers live in
``tests/test_gtk_staging.py``; the hidden ``.backup`` siblings in
``tests/test_gtk_staging_backups.py``.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import errno
import os
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.gtk.staging_case import StagingTestCase
from support.theme_install import write_file
from tools.gtk.staging import commit, stage_all
from tools.gtk.user_files import ConfigError


class TestCommit(StagingTestCase):
    def test_removing_a_missing_file_is_a_no_op(self):
        missing = self.root / "gtk-4.0" / "gtk.css"

        commit([], removals=[missing])

        self.assertFalse(missing.exists())
        self.assertFalse(missing.parent.exists())
        self.assertEqual([], self.backups_of(missing))

    def test_renames_each_staged_file_over_its_target(self):
        first = self.root / "gtk-3.0" / "settings.ini"
        second = self.root / "gtk-4.0" / "settings.ini"
        write_file(first, "old\n")
        staged = stage_all([(first, "new first\n"), (second, "new second\n")])

        commit(staged)

        self.assertEqual("new first\n", first.read_text(encoding="utf-8"))
        self.assertEqual("new second\n", second.read_text(encoding="utf-8"))
        for _, staging in staged:
            self.assertFalse(staging.exists())

    def test_a_failed_rename_is_reported_by_name_and_restores_the_earlier_target(
        self,
    ):
        good = self.root / "gtk-3.0" / "settings.ini"
        blocked = self.root / "gtk-4.0" / "settings.ini"
        write_file(good, "old good\n")
        staged = stage_all([(good, "new good\n"), (blocked, "new blocked\n")])
        # The second target's rename raises after the first target has already
        # been replaced, so the commit must restore the first rather than
        # leave the selection half-applied.

        with mock.patch.object(os, "replace", self.fail_the_staged_rename(blocked)):
            with self.assertRaises(ConfigError) as caught:
                commit(staged)

        self.assertIn(f"cannot write {blocked}", str(caught.exception))
        self.assertIn("injected rename failure", str(caught.exception))
        self.assertFalse(blocked.exists())
        self.assertEqual("old good\n", good.read_text(encoding="utf-8"))
        self.assertEqual([], self.backups_of(good))
        self.assertEqual([], self.backups_of(blocked))
        # Failed publication must also discard every staged sibling when
        # the second target did not previously exist.
        for _, staging in staged:
            self.assertFalse(staging.exists())

    def test_a_backup_link_failure_is_reported_by_name_and_restores_the_earlier_target(
        self,
    ):
        good = self.root / "gtk-3.0" / "settings.ini"
        blocked = self.root / "gtk-4.0" / "settings.ini"
        write_file(good, "old good\n")
        write_file(blocked, "old blocked\n")
        staged = stage_all([(good, "new good\n"), (blocked, "new blocked\n")])
        # Creating the backup hard link is the first step that touches the
        # second target. A link failure that is not "name taken" or "gone"
        # (here EPERM, as on a filesystem without hard links) must refuse the
        # commit by name, not be read as an absent target, and the first
        # target must come back. The second target was never touched.
        real_link = os.link

        def link(source, destination, *args, **kwargs):
            if Path(source) == blocked:
                raise PermissionError(errno.EPERM, "injected link failure")
            return real_link(source, destination, *args, **kwargs)

        with mock.patch.object(os, "link", link):
            with self.assertRaises(ConfigError) as caught:
                commit(staged)

        self.assertIn(f"cannot write {blocked}", str(caught.exception))
        self.assertIn("injected link failure", str(caught.exception))
        self.assertEqual("old good\n", good.read_text(encoding="utf-8"))
        self.assertEqual("old blocked\n", blocked.read_text(encoding="utf-8"))
        self.assertEqual([], self.backups_of(good))
        self.assertEqual([], self.backups_of(blocked))
        for _, staging in staged:
            self.assertFalse(staging.exists())

    def test_rollback_restores_a_symlink_target_it_replaced(self):
        referent = self.root / "real-settings.ini"
        referent.write_bytes(b"referent settings\n")
        link = self.root / "settings.ini"
        link.symlink_to(referent)
        blocked = self.root / "blocked.ini"
        blocked.write_bytes(b"old blocked\n")
        staged = stage_all(
            [(link, "new settings\n"), (blocked, "new blocked\n")]
        )

        with mock.patch.object(
            os, "replace", self.fail_the_staged_rename(blocked)
        ):
            with self.assertRaises(ConfigError):
                commit(staged)

        self.assertTrue(link.is_symlink())
        self.assertEqual(referent, link.resolve())
        self.assertEqual(b"referent settings\n", referent.read_bytes())
        self.assertEqual(b"old blocked\n", blocked.read_bytes())
        self.assertEqual([], self.backups_of(link))
        self.assertEqual([], self.backups_of(blocked))
        # commit()'s finally clause discards every staged file, including the
        # ones it has not renamed yet, so no `.staging` sibling is left over.
        for _, staging in staged:
            self.assertFalse(staging.exists())

    def test_a_created_target_is_removed_again_when_a_later_step_fails(self):
        created = self.root / "gtk-3.0" / "settings.ini"
        blocked = self.root / "gtk-4.0" / "settings.ini"
        staged = stage_all(
            [(created, "new created\n"), (blocked, "new blocked\n")]
        )
        blocked.mkdir()

        with self.assertRaises(ConfigError):
            commit(staged)

        self.assertFalse(created.exists())

    def test_an_interrupt_during_the_commit_restores_the_earlier_target(self):
        # Ctrl-C surfaces as KeyboardInterrupt, which is not an OSError. The
        # commit promises rollback for a failure at any step, not only an
        # errno-carrying one, so an aborted apply-gtk must not leave the
        # selection half-applied with a hidden backup beside it.
        good = self.root / "gtk-3.0" / "settings.ini"
        interrupted = self.root / "gtk-4.0" / "settings.ini"
        write_file(good, "old good\n")
        staged = stage_all([(good, "new good\n"), (interrupted, "new blocked\n")])
        real_replace = os.replace

        def interrupt_the_second_rename(source, destination, *args, **kwargs):
            if Path(destination) == interrupted and str(source).endswith(
                ".staging"
            ):
                raise KeyboardInterrupt
            return real_replace(source, destination, *args, **kwargs)

        with mock.patch.object(
            os, "replace", side_effect=interrupt_the_second_rename
        ):
            with self.assertRaises(KeyboardInterrupt):
                commit(staged)

        self.assertEqual("old good\n", good.read_text(encoding="utf-8"))
        self.assertFalse(interrupted.exists())
        self.assertEqual([], self.backups_of(good))
        self.assertEqual([], self.backups_of(interrupted))
        for _, staging in staged:
            self.assertFalse(staging.exists())

    def test_a_failed_restore_is_reported_with_the_original_failure(self):
        target = self.root / "gtk-3.0" / "settings.ini"
        write_file(target, "old settings\n")
        blocked = self.root / "gtk-4.0" / "settings.ini"
        staged = stage_all(
            [(target, "new settings\n"), (blocked, "new blocked\n")]
        )
        blocked.mkdir()
        real_replace = os.replace

        def fail_the_restore(source, destination, *args, **kwargs):
            if Path(destination) == target and str(source).endswith(".backup"):
                raise OSError("restore failure")
            return real_replace(source, destination, *args, **kwargs)

        with mock.patch.object(os, "replace", side_effect=fail_the_restore):
            with self.assertRaises(ConfigError) as caught:
                commit(staged)

        message = str(caught.exception)
        self.assertIn(f"cannot write {blocked}", message)
        self.assertIn(f"cannot restore {target}: restore failure", message)
        # The restore failed, so the new content stays and its backup is
        # retained rather than discarded --- the user can still recover it.
        self.assertEqual("new settings\n", target.read_text(encoding="utf-8"))
        self.assertEqual(1, len(self.backups_of(target)))

    def test_every_failed_restore_is_joined_newest_first_and_none_stops_the_rest(
        self,
    ):
        # _rollback restores newest first and keeps going after a failure, so
        # both failed restores must be named in that order, joined by "; ",
        # behind the write error that started the rollback.
        first = self.root / "gtk-3.0" / "settings.ini"
        second = self.root / "gtk-4.0" / "settings.ini"
        blocked = self.root / "gtk-2.0" / "gtkrc"
        write_file(first, "old first\n")
        write_file(second, "old second\n")
        staged = stage_all(
            [
                (first, "new first\n"),
                (second, "new second\n"),
                (blocked, "new blocked\n"),
            ]
        )
        blocked.mkdir()
        real_replace = os.replace
        restore_targets = []

        def fail_every_restore(source, destination, *args, **kwargs):
            if str(source).endswith(".backup") and Path(destination) in (
                first,
                second,
            ):
                restore_targets.append(Path(destination))
                raise OSError("restore failure")
            return real_replace(source, destination, *args, **kwargs)

        with mock.patch.object(os, "replace", side_effect=fail_every_restore):
            with self.assertRaises(ConfigError) as caught:
                commit(staged)

        message = str(caught.exception)
        self.assertEqual([second, first], restore_targets)
        second_text = f"cannot restore {second}: restore failure"
        first_text = f"cannot restore {first}: restore failure"
        self.assertIn(f"cannot write {blocked}", message)
        self.assertIn(f"; {second_text}; {first_text}", message)
        self.assertLess(message.index(second_text), message.index(first_text))
        self.assertEqual("new first\n", first.read_text(encoding="utf-8"))
        self.assertEqual("new second\n", second.read_text(encoding="utf-8"))
        self.assertEqual(1, len(self.backups_of(first)))
        self.assertEqual(1, len(self.backups_of(second)))

    def test_a_failed_removal_restores_earlier_replacements_and_removals(self):
        target = self.root / "gtk-3.0" / "settings.ini"
        write_file(target, "old settings\n")
        css = self.root / "gtk-4.0" / "gtk.css"
        write_file(css, "marker\n")
        blocked = self.root / "blocked"
        blocked.mkdir()
        staged = stage_all([(target, "new settings\n")])

        with self.assertRaises(ConfigError) as caught:
            commit(staged, removals=[css, blocked])

        self.assertIn(f"cannot remove {blocked}", str(caught.exception))
        self.assertEqual("old settings\n", target.read_text(encoding="utf-8"))
        self.assertEqual("marker\n", css.read_text(encoding="utf-8"))
        self.assertEqual([], self.backups_of(target))
        self.assertEqual([], self.backups_of(css))

    def test_a_directory_target_is_refused_and_the_earlier_write_is_restored(
        self,
    ):
        # A target that became a directory since it was selected (a dotfile
        # manager's redirect, say) must be refused rather than replaced:
        # linking over it would either fail with a bare errno or destroy a
        # directory the user owns. The commit reports it by name and rolls
        # back the target the commit already replaced.
        good = self.root / "gtk-3.0" / "settings.ini"
        blocked = self.root / "gtk-4.0" / "settings.ini"
        write_file(good, b"old good\n")
        blocked.mkdir(parents=True)
        # A directory target cannot be staged (stage_all refuses it before
        # the commit ever runs), so a commit reaches this branch through a
        # pair like the caller's own: target plus an existing `.staging`.
        blocked_staging = self.staging_of(blocked)
        blocked_staging.write_bytes(b"new blocked\n")
        staged = stage_all([(good, "new good\n")])
        staged.append((blocked, blocked_staging))

        with self.assertRaises(ConfigError) as caught:
            commit(staged)

        self.assertIn(f"cannot write {blocked}", str(caught.exception))
        self.assertIn(f"is a directory: {blocked}", str(caught.exception))
        self.assertTrue(blocked.is_dir())
        self.assertEqual(b"old good\n", good.read_bytes())
        self.assertEqual([], self.backups_of(good))
        self.assertEqual([], self.backups_of(blocked))
        for _, staging in staged:
            self.assertFalse(staging.exists())

    def test_removal_of_a_directory_target_and_a_created_file_rolls_back(
        self,
    ):
        # The removal half carries the same refusal, with the removal
        # wording: the removal that already ran (one step earlier) is
        # un-done when the directory removal is refused, and a file the
        # commit replaced before that must go away again just the same.
        replaced = self.root / "gtk-3.0" / "settings.ini"
        removable = self.root / "gtk-4.0" / "gtk.css"
        blocked = self.root / "gtk-4.0" / "launchers"
        write_file(removable, b"keep me\n")
        replaced.parent.mkdir(parents=True)
        blocked.mkdir(parents=True)
        staged = stage_all([(replaced, "new\n")])

        with self.assertRaises(ConfigError) as caught:
            commit(staged, removals=[removable, blocked])

        self.assertIn(f"cannot remove {blocked}", str(caught.exception))
        self.assertIn(f"is a directory: {blocked}", str(caught.exception))
        self.assertTrue(blocked.is_dir())
        self.assertEqual(b"keep me\n", removable.read_bytes())
        self.assertEqual([], self.backups_of(removable))
        self.assertFalse(replaced.exists())
        for _, sibling in staged:
            self.assertFalse(sibling.exists())


if __name__ == "__main__":
    unittest.main()
