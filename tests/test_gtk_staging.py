"""Direct tests for tools/gtk_staging.py's staging and commit helpers.

``tools/apply_gtk.py`` drives these helpers, so ``tests/test_gtk_apply.py``
covers the shapes the apply and remove paths produce end to end. These tests
pin the helpers on their own and add the branch that suite cannot reach: a
rename that fails during :func:`commit`, the step that actually replaces the
user's settings files. The failure must be a one-line ``ConfigError`` naming
the target, and every leftover ``.staging`` sibling must be removed.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.tmp_dir import make_tmp_dir
from tools.gtk_staging import _stage, commit, discard, stage_all
from tools.gtk_user_files import ConfigError


class StagingCase(unittest.TestCase):
    """Base with a temp root and the staging-name helper."""

    def setUp(self):
        self.root = make_tmp_dir(self)

    def staging_of(self, target: Path) -> Path:
        """Return the ``.staging`` sibling ``_stage`` uses for *target*."""
        return target.with_name(f".{target.name}.staging")


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

    def test_an_empty_write_list_stages_nothing(self):
        self.assertEqual([], stage_all([]))


class TestCommit(StagingCase):
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

    def test_a_failed_rename_is_reported_by_name_and_discards_the_staging(self):
        good = self.root / "gtk-3.0" / "settings.ini"
        blocked = self.root / "gtk-4.0" / "settings.ini"
        staged = stage_all([(good, "new good\n"), (blocked, "new blocked\n")])
        # A directory occupies the second target by the time the commit runs:
        # os.replace() cannot rename a file over it and raises OSError. This is
        # the branch a staging failure never reaches -- the files are already
        # staged and the first one may already have replaced its target.
        blocked.mkdir()

        with self.assertRaises(ConfigError) as caught:
            commit(staged)

        self.assertIn(f"cannot write {blocked}", str(caught.exception))
        self.assertTrue(blocked.is_dir())
        # commit()'s finally clause discards every staged file, including the
        # ones it has not renamed yet, so no `.staging` sibling is left over.
        for _, staging in staged:
            self.assertFalse(staging.exists())


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
