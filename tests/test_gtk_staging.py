"""Direct tests for tools/gtk/staging.py's staging and discard helpers.

``tools/gtk/selection.py`` drives these helpers through the CLI, so ``tests/test_apply_gtk.py``
covers the shapes the apply and remove paths produce end to end. These tests
pin the helpers on their own. The :func:`commit` replacement and rollback
branches, the step that actually replaces the user's settings files, live in
``tests/test_gtk_staging_commit.py``. The pins on the hidden ``.backup``
siblings (cleanup, foreign siblings, name collisions) live in
``tests/test_gtk_staging_backups.py``.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.gtk.staging_case import StagingTestCase
from tools.gtk.staging import (
    _attempt_all,
    _restore,
    _same_file,
    _stage,
    discard,
    stage_all,
)
from tools.config_read import ConfigError


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
