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
``KeyboardInterrupt``) as well as an errno-carrying failure.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.tmp_dir import make_tmp_dir
from support.unlink_failure import unlink_failing_for
from tools.gtk_staging import _stage, commit, discard, stage_all
from tools.gtk_user_files import ConfigError


class StagingCase(unittest.TestCase):
    """Base with a temp root and the staging-name helper."""

    def setUp(self):
        self.root = make_tmp_dir(self)

    def staging_of(self, target: Path) -> Path:
        """Return the ``.staging`` sibling ``_stage`` uses for *target*."""
        return target.with_name(f".{target.name}.staging")

    def backups_of(self, target: Path) -> list[Path]:
        """Return the ``.backup`` siblings ``commit`` may use for *target*."""
        return list(target.parent.glob(f".{target.name}.*.backup"))

    def fail_the_staged_rename(self, target: Path):
        """Return an ``os.replace`` stand-in that refuses to publish *target*.

        The staged file's rename onto *target* raises ``OSError``; every
        other rename goes to the real ``os.replace``.
        """
        real_replace = os.replace

        def replace(source, destination, *args, **kwargs):
            if str(source).endswith(".staging") and Path(destination) == target:
                raise OSError("injected rename failure")
            return real_replace(source, destination, *args, **kwargs)

        return replace


class TestStage(StagingCase):
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


class TestStageAll(StagingCase):
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

    def test_an_empty_write_list_stages_nothing(self):
        self.assertEqual([], stage_all([]))


class TestCommit(StagingCase):
    def test_removing_a_missing_file_is_a_no_op(self):
        missing = self.root / "gtk-4.0" / "gtk.css"

        commit([], removals=[missing])

        self.assertFalse(missing.exists())
        self.assertFalse(missing.parent.exists())
        self.assertEqual([], self.backups_of(missing))

    def test_renames_each_staged_file_over_its_target(self):
        first = self.root / "gtk-3.0" / "settings.ini"
        second = self.root / "gtk-4.0" / "settings.ini"
        first.parent.mkdir(parents=True)
        first.write_text("old\n", encoding="utf-8")
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
        good.parent.mkdir(parents=True)
        good.write_text("old good\n", encoding="utf-8")
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

    def test_a_failed_first_rename_leaves_no_backup_sibling(self):
        target = self.root / "gtk-3.0" / "settings.ini"
        target.parent.mkdir(parents=True)
        target.write_text("old settings\n", encoding="utf-8")
        staged = stage_all([(target, "new settings\n")])

        with mock.patch.object(os, "replace", self.fail_the_staged_rename(target)):
            with self.assertRaises(ConfigError):
                commit(staged)

        # The target was never changed, so restoring it must drop the backup
        # link instead of renaming two links to the same inode, a no-op that
        # would leave the backup sibling behind.
        self.assertEqual("old settings\n", target.read_text(encoding="utf-8"))
        self.assertEqual([], self.backups_of(target))

    def test_an_interrupt_during_the_commit_restores_the_earlier_target(self):
        # Ctrl-C surfaces as KeyboardInterrupt, which is not an OSError. The
        # commit promises rollback for a failure at any step, not only an
        # errno-carrying one, so an aborted apply-gtk must not leave the
        # selection half-applied with a hidden backup beside it.
        good = self.root / "gtk-3.0" / "settings.ini"
        interrupted = self.root / "gtk-4.0" / "settings.ini"
        good.parent.mkdir(parents=True)
        good.write_text("old good\n", encoding="utf-8")
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

    def test_a_failed_removal_unlink_leaves_no_backup_sibling(self):
        css = self.root / "gtk-4.0" / "gtk.css"
        css.parent.mkdir(parents=True)
        css.write_text("marker\n", encoding="utf-8")

        with unlink_failing_for(css):
            with self.assertRaises(ConfigError):
                commit([], removals=[css])

        # The css still exists, so its backup is a link to the same inode;
        # rollback must remove that link rather than leave it behind.
        self.assertEqual("marker\n", css.read_text(encoding="utf-8"))
        self.assertEqual([], self.backups_of(css))

    def test_run_a_second_commit_after_a_failure_leaves_no_backups(self):
        target = self.root / "gtk-3.0" / "settings.ini"
        target.parent.mkdir(parents=True)
        target.write_text("old settings\n", encoding="utf-8")
        staged = stage_all([(target, "new settings\n")])

        with mock.patch.object(os, "replace", self.fail_the_staged_rename(target)):
            with self.assertRaises(ConfigError):
                commit(staged)

        commit(stage_all([(target, "new settings\n")]))

        self.assertEqual("new settings\n", target.read_text(encoding="utf-8"))
        self.assertEqual([], self.backups_of(target))

    def test_a_failed_restore_is_reported_with_the_original_failure(self):
        target = self.root / "gtk-3.0" / "settings.ini"
        target.parent.mkdir(parents=True)
        target.write_text("old settings\n", encoding="utf-8")
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

    def test_removals_delete_the_named_files_and_leave_no_backup(self):
        css = self.root / "gtk-4.0" / "gtk.css"
        css.parent.mkdir(parents=True)
        css.write_text("marker\n", encoding="utf-8")

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
        target.parent.mkdir(parents=True)
        target.write_text("old settings\n", encoding="utf-8")
        foreign = target.with_name(f".{target.name}.backup")
        foreign.write_text("user data\n", encoding="utf-8")

        commit(stage_all([(target, "new settings\n")]))

        self.assertEqual("new settings\n", target.read_text(encoding="utf-8"))
        self.assertEqual("user data\n", foreign.read_text(encoding="utf-8"))
        self.assertEqual([], self.backups_of(target))

    def test_a_failed_removal_restores_earlier_replacements_and_removals(self):
        target = self.root / "gtk-3.0" / "settings.ini"
        target.parent.mkdir(parents=True)
        target.write_text("old settings\n", encoding="utf-8")
        css = self.root / "gtk-4.0" / "gtk.css"
        css.parent.mkdir(parents=True)
        css.write_text("marker\n", encoding="utf-8")
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

    def test_a_backup_name_collision_retries_without_touching_the_foreign_file(self):
        target = self.root / "settings.ini"
        target.write_bytes(b"old settings\n")
        foreign = target.with_name(f".{target.name}.occupied.backup")
        foreign.write_bytes(b"user backup\n")
        staged = stage_all([(target, "new settings\n")])

        with mock.patch(
            "tools.gtk_staging.secrets.token_hex",
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
            "tools.gtk_staging.secrets.token_hex", return_value="occupied"
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
        good.parent.mkdir(parents=True)
        good.write_bytes(b"old good\n")
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
        removable.parent.mkdir(parents=True)
        replaced.parent.mkdir(parents=True)
        removable.write_bytes(b"keep me\n")
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


class TestDiscard(StagingCase):
    def test_removes_a_staged_file(self):
        target = self.root / "settings.ini"
        staging = _stage(target, "text")

        discard(staging)

        self.assertFalse(staging.exists())
        self.assertFalse(target.exists())

    def test_ignores_a_path_that_never_became_a_staging_file(self):
        discard(self.root / "never-created.staging")


if __name__ == "__main__":
    unittest.main()
