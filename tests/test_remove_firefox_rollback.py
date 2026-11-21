"""Tests for the Firefox profile removal's rollback (``install_firefox.py --remove``).

They pin what a removal leaves behind when a ``user.js`` rewrite, a sheet
unlink or a restore fails, or an interrupt lands before or after a step takes
effect. Removal outcomes, refusals and FIFO/size cases stay in
``tests/test_remove_firefox.py``; the shared temp-home case is
``support.firefox_profile_case``.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.theme_install import write_file as _write
from support.firefox_profile_case import FirefoxProfileTestCase, read_utf8 as _read
from tools import (
    firefox_user_files,
    firefox_user_js,
    install_firefox,
)


class TestRemoveRollback(FirefoxProfileTestCase):
    def test_a_failed_user_js_write_during_removal_is_reported_by_path(self):
        # Removal rewrites user.js before it deletes the sheet. A failure on
        # that first step must name user.js and leave both files unchanged
        # instead of deleting the sheet and leaving a stale preference.
        self.install()
        before_js = _read(self.user_js_path())
        before_sheet = _read(self.sheet_path())
        self.run_with_failed_write(
            self.user_js_path(), "--remove", "--profile", str(self.profile)
        )
        self.assertEqual(before_js, _read(self.user_js_path()))
        self.assertEqual(before_sheet, _read(self.sheet_path()))

    def test_a_failed_sheet_unlink_is_reported_by_path(self):
        # _remove promises a by-name "cannot remove" error when our sheet
        # cannot be deleted, leaving the sheet in place rather than crashing.
        # The user.js rewrite that preceded it is put back, so the failure
        # does not leave the preference removed from a sheet that remains.
        self.install()
        sheet = _read(self.sheet_path())
        before_js = _read(self.user_js_path())
        with mock.patch.object(Path, "unlink", side_effect=OSError("simulated failure")):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {self.sheet_path()}", result.stderr)
        self.assertEqual(sheet, _read(self.sheet_path()))
        self.assertEqual(before_js, _read(self.user_js_path()))

    def test_a_failed_user_content_unlink_restores_the_published_user_chrome(
        self,
    ):
        # Both owned sheets are deleted in SHEETS order. A failure on the
        # second unlink must name that sheet, leave it in place, and undo
        # both earlier steps: the user.js rewrite goes back and the user
        # chrome the first unlink took is written back byte-for-byte, so a
        # removal that fails partway leaves the profile exactly as it was.
        self.install()
        before_js = _read(self.user_js_path())
        before_sheet = _read(self.sheet_path())
        before_content = _read(self.content_sheet_path())
        with mock.patch.object(
            Path, "unlink", self.fail_unlink_to(self.content_sheet_path())
        ):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {self.content_sheet_path()}", result.stderr)
        self.assertEqual(before_sheet, _read(self.sheet_path()))
        self.assertEqual(before_content, _read(self.content_sheet_path()))
        self.assertEqual(before_js, _read(self.user_js_path()))

    def test_a_failed_deleted_sheet_restore_names_both_during_removal(self):
        # When the second unlink fails and the deleted user chrome cannot be
        # written back either, the removal cannot fully restore the pair. The
        # error must name both failures so the absent sheet is visible
        # instead of the rollback failure being swallowed.
        self.install()
        before_content = _read(self.content_sheet_path())
        real_write = firefox_user_files.write_atomically

        def failing_restore(path, writer):
            if Path(path) == self.sheet_path():
                raise OSError("simulated restore failure")
            return real_write(path, writer)

        with mock.patch.object(
            Path, "unlink", self.fail_unlink_to(self.content_sheet_path())
        ), mock.patch.object(
            firefox_user_files, "write_atomically", failing_restore
        ):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {self.content_sheet_path()}", result.stderr)
        self.assertIn(f"cannot write {self.sheet_path()}", result.stderr)
        self.assert_profile_absent(self.sheet_path())
        self.assertEqual(before_content, _read(self.content_sheet_path()))

    def test_a_failed_unlink_restores_an_outdated_sheet_reading_it_had(self):
        # A repeat install can adopt an outdated sheet that is still ours. A
        # removal of it that fails after the first unlink must restore the
        # sheet's own text, the one the removal read, not the shipped sheet
        # it shares a marker with.
        self.install()
        outdated = f"{install_firefox.CSS_MARKER}\n/* outdated sheet */\n"
        _write(self.sheet_path(), outdated)
        before_js = _read(self.user_js_path())
        with mock.patch.object(
            Path, "unlink", self.fail_unlink_to(self.content_sheet_path())
        ):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {self.content_sheet_path()}", result.stderr)
        self.assertEqual(outdated, _read(self.sheet_path()))
        self.assertEqual(before_js, _read(self.user_js_path()))

    def test_an_interrupt_after_only_the_first_sheet_unlink_restores_user_js(self):
        # An interrupt after the first sheet unlink leaves the second sheet
        # present, so the removal is half-applied and must undo it: the
        # previous user.js goes back and the deleted user chrome is restored,
        # leaving the profile exactly as it was instead of keeping the
        # rewritten one.
        self.install()
        before_js = _read(self.user_js_path())
        before_sheet = _read(self.sheet_path())
        with mock.patch.object(
            Path, "unlink", self.interrupt_unlink_to(self.sheet_path())
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(before_sheet, _read(self.sheet_path()))
        self.assertTrue(self.content_sheet_path().exists())
        self.assertEqual(before_js, _read(self.user_js_path()))

    def test_a_failed_user_js_restore_during_removal_names_both_errors(self):
        # If the sheet cannot be deleted and the user.js rewrite cannot be put
        # back, the removal cannot restore the pair. The error must name both
        # failures, so the preference-less user.js beside the surviving sheet
        # is visible instead of the rollback failure being swallowed.
        self.install()
        before_js = _read(self.user_js_path())
        before_sheet = _read(self.sheet_path())
        real_write = firefox_user_files.write_atomically
        js_writes = []

        def flaky_write(path, writer):
            if Path(path) == self.user_js_path():
                js_writes.append(path)
                if len(js_writes) > 1:
                    raise OSError("simulated rollback failure")
            return real_write(path, writer)

        with mock.patch.object(
            firefox_user_files, "write_atomically", flaky_write
        ), mock.patch.object(
            Path, "unlink", side_effect=OSError("simulated failure")
        ):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {self.sheet_path()}", result.stderr)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
        self.assertEqual(before_sheet, _read(self.sheet_path()))
        self.assertNotEqual(before_js, _read(self.user_js_path()))

    def test_an_interrupt_during_the_sheet_unlink_restores_user_js(self):
        # An interrupt after the user.js rewrite is not an OSError, but the
        # removal must still put the preference block back and then propagate
        # the interrupt instead of leaving a sheet with no preference.
        self.install()
        before_js = _read(self.user_js_path())
        before_sheet = _read(self.sheet_path())
        with mock.patch.object(Path, "unlink", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(before_sheet, _read(self.sheet_path()))
        self.assertEqual(before_js, _read(self.user_js_path()))

    def test_an_interrupt_after_the_user_js_rewrite_takes_effect_restores_it(self):
        # The rewrite can remove the preference block and then raise before
        # the caller records it. Without a pre-set intent flag that interrupt
        # skips the rollback and leaves the surviving sheet without its
        # preference; the previous user.js must be put back.
        self.install()
        before_js = _read(self.user_js_path())
        before_sheet = _read(self.sheet_path())
        real_write = firefox_user_files.write_atomically
        js_writes = []

        def interrupt_after_the_user_js_rewrite(path, writer):
            if Path(path) == self.user_js_path():
                js_writes.append(path)
                real_write(path, writer)
                if len(js_writes) == 1:
                    raise KeyboardInterrupt
                return
            return real_write(path, writer)

        with mock.patch.object(
            firefox_user_files, "write_atomically", interrupt_after_the_user_js_rewrite
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(before_js, _read(self.user_js_path()))
        self.assertEqual(before_sheet, _read(self.sheet_path()))

    def test_an_interrupt_after_the_sheet_unlink_takes_effect_keeps_the_removal(self):
        # An interrupt can arrive after the unlink removed the sheet but before
        # the removal records it. The sheet is gone, so the already rewritten
        # user.js matches a completed removal and must not be put back: a
        # rollback keyed on a late flag would leave a preference with no sheet.
        self.install()
        before_js = _read(self.user_js_path())
        with mock.patch.object(
            Path, "unlink", self.interrupt_unlink_to(self.content_sheet_path())
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--remove", "--profile", str(self.profile))
        self.assert_profile_absent(self.sheet_path(), self.content_sheet_path())
        self.assertEqual(
            firefox_user_js.remove_user_js(before_js), _read(self.user_js_path())
        )

if __name__ == "__main__":
    unittest.main()
