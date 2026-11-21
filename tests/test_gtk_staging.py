"""Direct tests for tools/gtk_staging.py's staging and commit helpers.

``tools/gtk_selection.py`` drives these helpers through the CLI, so ``tests/test_apply_gtk.py``
covers the shapes the apply and remove paths produce end to end. These tests
pin the helpers on their own and add the branch that suite cannot reach: a
rename that fails during :func:`commit`, the step that actually replaces the
user's settings files. The failure must be a one-line ``ConfigError`` naming
the target, and every leftover ``.staging`` sibling must be removed. A
later failure must also restore every target the commit already changed,
including a user-CSS removal, instead of leaving the selection half-applied;
that rollback covers a non-``OSError`` interrupt (Ctrl-C's
``KeyboardInterrupt``) as well as an errno-carrying failure. The pins on the
hidden ``.backup`` siblings (cleanup, foreign siblings, name collisions) live
in ``tests/test_gtk_staging_backups.py``.

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
from tools.gtk_staging import (
    _attempt_all,
    _restore,
    _same_file,
    _stage,
    commit,
    discard,
    stage_all,
)
from tools.gtk_user_files import ConfigError


class TestStage(StagingTestCase):
    def test_writes_the_text_to_a_hidden_sibling_and_leaves_the_target_alone(self):
        target = self.root / "gtk-3.0" / "settings.ini"

        staging = _stage(target, "gtk-thème=Platine\n")

        # The exact name matters: `make uninstall` cleans up `.staging`
        # siblings, and the helper must create the parent directory too.
        self.assertEqual(self.staging_of(target), staging)
        self.assertEqual(
            "gtk-thème=Platine\n".encode("utf-8"), staging.read_bytes()
        )
        self.assertFalse(target.exists())

    def test_a_directory_target_is_refused_by_name_and_leaves_no_staging(self):
        target = self.root / "settings.ini"
        target.mkdir()

        with self.assertRaises(ConfigError) as caught:
            _stage(target, "text")

        self.assertIn(f"cannot write {target}: is a directory", str(caught.exception))
        self.assertTrue(target.is_dir())
        self.assertFalse(self.staging_of(target).exists())

    def test_an_os_error_while_creating_the_parent_is_refused_with_its_cause(self):
        # A regular file where the parent directory should be makes mkdir fail
        # with an OSError, which must surface as a ConfigError naming the
        # target, with the OSError kept as the cause and no staging left.
        blocker = self.root / "gtk-3.0"
        blocker.write_text("not a directory\n", encoding="utf-8")
        target = blocker / "settings.ini"

        with self.assertRaises(ConfigError) as caught:
            _stage(target, "text")

        self.assertTrue(str(caught.exception).startswith(f"cannot write {target}: "))
        self.assertIsInstance(caught.exception.__cause__, OSError)
        self.assertEqual("not a directory\n", blocker.read_text(encoding="utf-8"))
        self.assertFalse(self.staging_of(target).exists())


class TestAttemptAll(unittest.TestCase):
    """_attempt_all runs every attempt and reports each OSError together."""

    def test_runs_later_attempts_after_an_earlier_failure(self):
        ran = []

        def failing():
            ran.append("first")
            raise OSError("boom")

        def succeeding():
            ran.append("second")

        with self.assertRaises(ConfigError) as caught:
            _attempt_all([("cannot do a", failing), ("cannot do b", succeeding)])
        self.assertEqual(ran, ["first", "second"])
        self.assertEqual(str(caught.exception), "cannot do a: boom")

    def test_joins_every_failure_in_order(self):
        def fail(text):
            def attempt():
                raise OSError(text)
            return attempt

        with self.assertRaises(ConfigError) as caught:
            _attempt_all([("x", fail("one")), ("y", lambda: None), ("z", fail("two"))])
        self.assertEqual(str(caught.exception), "x: one; z: two")

    def test_silent_when_every_attempt_succeeds(self):
        calls = []
        _attempt_all([("a", lambda: calls.append(1)), ("b", lambda: calls.append(2))])
        self.assertEqual(calls, [1, 2])


class TestStageAll(StagingTestCase):
    def test_stages_every_pair_in_order_without_touching_the_targets(self):
        first = self.root / "gtk-3.0" / "settings.ini"
        second = self.root / "gtk-4.0" / "gtk.css"

        staged = stage_all([(first, "first\n"), (second, "second\n")])

        self.assertEqual(
            [(first, self.staging_of(first)), (second, self.staging_of(second))],
            staged,
        )
        self.assertEqual(b"first\n", staged[0][1].read_bytes())
        self.assertEqual(b"second\n", staged[1][1].read_bytes())
        self.assertFalse(first.exists())
        self.assertFalse(second.exists())

    def test_a_failed_later_write_discards_the_earlier_staging(self):
        good = self.root / "gtk-3.0" / "settings.ini"
        blocked = self.root / "gtk-4.0" / "settings.ini"
        blocked.mkdir(parents=True)

        with self.assertRaises(ConfigError):
            stage_all([(good, "new\n"), (blocked, "new\n")])

        # The earlier write was staged before the failure, so it must be
        # discarded rather than left behind for a later uninstall to trip on.
        self.assertFalse(self.staging_of(good).exists())
        self.assertFalse(good.exists())
        self.assertTrue(blocked.is_dir())

    def test_reports_when_failed_staging_cannot_be_discarded(self):
        good = self.root / "gtk-3.0" / "settings.ini"
        blocked = self.root / "gtk-4.0" / "settings.ini"
        blocked.mkdir(parents=True)
        staging = self.staging_of(good)
        real_unlink = Path.unlink

        def fail_staging_unlink(path, *args, **kwargs):
            if path == staging:
                raise OSError("injected cleanup failure")
            return real_unlink(path, *args, **kwargs)

        with mock.patch.object(Path, "unlink", fail_staging_unlink):
            with self.assertRaises(ConfigError) as caught:
                stage_all([(good, "new\n"), (blocked, "new\n")])

        self.assertIn(f"cannot write {blocked}", str(caught.exception))
        self.assertIn(f"cannot remove staging file {staging}", str(caught.exception))
        self.assertTrue(staging.exists())

    def test_a_failed_discard_does_not_stop_the_remaining_discards(self):
        first = self.root / "gtk-3.0" / "settings.ini"
        second = self.root / "gtk-4.0" / "settings.ini"
        blocked = self.root / "gtk-4.0" / "gtk.css"
        blocked.mkdir(parents=True)
        first_staging = self.staging_of(first)
        second_staging = self.staging_of(second)
        real_unlink = Path.unlink

        def fail_first_staging_unlink(path, *args, **kwargs):
            if path == first_staging:
                raise OSError("injected cleanup failure")
            return real_unlink(path, *args, **kwargs)

        with mock.patch.object(Path, "unlink", fail_first_staging_unlink):
            with self.assertRaises(ConfigError) as caught:
                stage_all([(first, "one\n"), (second, "two\n"), (blocked, "new\n")])

        # The failure on the first staging must not stop the second discard.
        self.assertFalse(second_staging.exists())
        self.assertTrue(first_staging.exists())
        self.assertIn(f"cannot write {blocked}", str(caught.exception))
        self.assertIn(f"cannot remove staging file {first_staging}", str(caught.exception))
        self.assertNotIn(str(second_staging), str(caught.exception))

    def test_every_failed_discard_is_joined_into_the_report(self):
        first = self.root / "gtk-3.0" / "settings.ini"
        second = self.root / "gtk-4.0" / "settings.ini"
        blocked = self.root / "gtk-4.0" / "gtk.css"
        blocked.mkdir(parents=True)
        first_staging = self.staging_of(first)
        second_staging = self.staging_of(second)
        real_unlink = Path.unlink

        def fail_staging_unlinks(path, *args, **kwargs):
            if path in (first_staging, second_staging):
                raise OSError("injected cleanup failure")
            return real_unlink(path, *args, **kwargs)

        with mock.patch.object(Path, "unlink", fail_staging_unlinks):
            with self.assertRaises(ConfigError) as caught:
                stage_all([(first, "one\n"), (second, "two\n"), (blocked, "new\n")])

        message = str(caught.exception)
        self.assertTrue(first_staging.exists())
        self.assertTrue(second_staging.exists())
        self.assertIn(f"cannot remove staging file {first_staging}", message)
        self.assertIn(f"cannot remove staging file {second_staging}", message)
        # Both cleanup messages follow the write error, joined by "; ".
        self.assertIn(
            f"; cannot remove staging file {first_staging}: injected cleanup failure"
            f"; cannot remove staging file {second_staging}: injected cleanup failure",
            message,
        )

    def test_an_empty_write_list_stages_nothing(self):
        self.assertEqual([], stage_all([]))


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


class TestDiscard(StagingTestCase):
    def test_removes_a_staged_file(self):
        target = self.root / "settings.ini"
        staging = _stage(target, "text")

        discard(staging)

        self.assertFalse(staging.exists())
        self.assertFalse(target.exists())

    def test_ignores_a_path_that_never_became_a_staging_file(self):
        discard(self.root / "never-created.staging")


class TestRestoreAfterVanishedTarget(StagingTestCase):
    """Rollback when the published target was removed before it could restore.

    The backup is a hard link to the previous inode, so it survives the target
    being deleted. ``_same_file`` must report "not the same inode" for a missing
    side rather than raising, so ``_restore`` renames the backup back into place
    instead of abandoning the user's previous settings.
    """

    def test_a_missing_side_names_no_inode_and_is_not_the_same_file(self):
        present = self.root / "settings.ini"
        present.write_text("old settings\n", encoding="utf-8")
        missing = self.root / "gone.ini"

        self.assertFalse(_same_file(present, missing))
        self.assertFalse(_same_file(missing, present))

    def test_restore_puts_the_backup_back_when_the_target_was_removed(self):
        target = self.root / "settings.ini"
        target.write_text("old settings\n", encoding="utf-8")
        backup = self.root / ".settings.ini.0123456789abcdef.backup"
        os.link(target, backup)
        target.unlink()

        _restore(target, backup)

        self.assertEqual("old settings\n", target.read_text(encoding="utf-8"))
        self.assertFalse(backup.exists())


if __name__ == "__main__":
    unittest.main()
