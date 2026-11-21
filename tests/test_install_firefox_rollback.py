"""Tests for the Firefox install transaction's rollback.

These pin what the install leaves behind when a write fails or an interrupt
lands mid-publish, before or after each file publishes. The transaction
guarantee they back is named in ``docs/invariants.md``. Installs, refusals and
size caps stay in ``tests/test_install_firefox.py``, and the shared temp-home
case is ``support.firefox_profile_case``.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from support import containment
from support import repo_root
from support.theme_install import write_file as _write
from support.firefox_profile_case import FirefoxProfileTestCase, read_utf8 as _read
from tools import (
    firefox_user_files,
    install_firefox,
)

SHEET_PATH = Path(repo_root.ROOT) / install_firefox.SHEET


class TestInstallRollback(FirefoxProfileTestCase):
    def test_an_uncreatable_chrome_directory_is_reported_by_path(self):
        # _apply promises a by-name "cannot create" error when the chrome
        # directory cannot be made, rather than a traceback. The directory
        # does not exist yet, so the earlier reads return None and the mkdir
        # is reached; fail only that call.
        with mock.patch.object(Path, "mkdir", side_effect=OSError("simulated failure")):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot create {self.sheet_path().parent}", result.stderr)
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_a_failed_user_js_write_is_reported_by_path(self):
        # A write failure must name the file that failed and stop the install.
        # The sheet is published first, so the failure must remove it again:
        # a failed install leaves neither half of the pair behind.
        self.run_with_failed_write(self.user_js_path())
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_a_failed_user_js_write_restores_both_previous_sheets(self):
        # A repeat install over earlier sheets of ours must not replace them
        # when the user.js write fails: each previous sheet is put back, not
        # deleted and not left as the new one.
        previous = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        previous_content = (
            f"{install_firefox.CONTENT_CSS_MARKER}\n/* previous content */\n"
        )
        _write(self.sheet_path(), previous)
        _write(self.content_sheet_path(), previous_content)
        self.run_with_failed_write(self.user_js_path())
        self.assertEqual(previous, _read(self.sheet_path()))
        self.assertEqual(previous_content, _read(self.content_sheet_path()))
        self.assert_profile_absent(self.user_js_path())

    def test_a_failed_user_js_write_keeps_a_block_that_was_already_installed(self):
        # A repeat install over an outdated sheet rewrites a user.js that
        # already holds our block unchanged. When that write fails, the
        # sheet goes back to its previous text and the block stays in place.
        first = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, first.returncode, first.stderr)
        installed_js = _read(self.user_js_path())
        previous_sheet = f"{install_firefox.CSS_MARKER}\n/* outdated sheet */\n"
        _write(self.sheet_path(), previous_sheet)
        self.run_with_failed_write(self.user_js_path())
        self.assertEqual(previous_sheet, _read(self.sheet_path()))
        self.assertEqual(installed_js, _read(self.user_js_path()))

    def test_a_failed_sheet_restore_is_reported_with_the_original_error(self):
        # When the user.js write and the sheet restore both fail, the restore
        # cannot put the profile back. The error must name both failures so
        # the half-applied sheet is visible instead of reported as clean, and
        # the failed restore leaves the shipped sheet in place.
        previous = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        _write(self.sheet_path(), previous)
        real_write = firefox_user_files.write_atomically
        sheet_writes = []

        def flaky_write(path, writer):
            if Path(path) == self.user_js_path():
                raise OSError("simulated user.js failure")
            if Path(path) == self.sheet_path():
                sheet_writes.append(path)
                if len(sheet_writes) > 1:
                    raise OSError("simulated restore failure")
            return real_write(path, writer)

        with mock.patch.object(firefox_user_files, "write_atomically", flaky_write):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
        self.assertIn(f"cannot write {self.sheet_path()}", result.stderr)
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            self.sheet_path().read_bytes(),
        )
        self.assert_profile_absent(self.user_js_path())

    def test_an_interrupt_during_the_user_js_write_restores_the_previous_sheet(self):
        # An interrupt is not a ConfigError, but it must roll the published
        # sheet back all the same and then propagate instead of being
        # swallowed; otherwise Ctrl-C leaves a half-installed profile.
        previous = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        _write(self.sheet_path(), previous)
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.interrupt_write_to(self.user_js_path()),
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assertEqual(previous, _read(self.sheet_path()))
        self.assert_profile_absent(self.content_sheet_path(), self.user_js_path())

    def test_an_interrupt_after_the_user_js_write_takes_effect_restores_it(self):
        # The user.js write can publish the preference block and then raise
        # before the call returns. The install must put the previous user.js
        # back as well as the sheet, so the pair is not left half-applied.
        previous_sheet = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        previous_js = 'user_pref("keep.me", true);\n'
        _write(self.sheet_path(), previous_sheet)
        _write(self.user_js_path(), previous_js)
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.interrupt_write_to(self.user_js_path(), after_publish=True),
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assertEqual(previous_sheet, _read(self.sheet_path()))
        self.assert_profile_absent(self.content_sheet_path())
        self.assertEqual(previous_js, _read(self.user_js_path()))

    def test_an_interrupt_after_a_created_user_js_is_published_removes_it(self):
        # A first install has no previous user.js, so when the write
        # publishes it and then raises, the rollback removes the file it
        # created instead of leaving the preference block behind.
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.interrupt_write_to(self.user_js_path(), after_publish=True),
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_a_failed_user_js_restore_is_reported_with_the_original_error(self):
        # The user.js write publishes and then raises, and putting the
        # previous user.js back fails too. The error must name both
        # failures, and the sheet is still rolled back.
        previous_sheet = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        previous_js = 'user_pref("keep.me", true);\n'
        _write(self.sheet_path(), previous_sheet)
        _write(self.user_js_path(), previous_js)
        real_write = firefox_user_files.write_atomically
        js_writes = []

        def flaky_write(path, writer):
            if Path(path) == self.user_js_path():
                js_writes.append(path)
                if len(js_writes) > 1:
                    raise OSError("simulated user.js restore failure")
                real_write(path, writer)
                raise OSError("simulated user.js failure")
            return real_write(path, writer)

        with mock.patch.object(firefox_user_files, "write_atomically", flaky_write):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn("simulated user.js failure", result.stderr)
        self.assertIn("simulated user.js restore failure", result.stderr)
        self.assertEqual(previous_sheet, _read(self.sheet_path()))

    def test_an_interrupt_after_the_sheet_write_takes_effect_removes_it(self):
        # The sheet write can publish its file and then raise before the
        # caller records any state. A rollback flag set after the write would
        # miss that interrupt and leave the sheet behind; the install must
        # remove the sheet it just published and propagate the interrupt.
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.interrupt_write_to(self.sheet_path(), after_publish=True),
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_a_failed_new_sheet_restore_is_reported_with_the_original_error(self):
        # A first install has no previous sheet, so its rollback removes the
        # shipped sheet it published. If that unlink also fails, the error
        # must name both failures and the sheet that could not be removed
        # stays visible instead of the rollback failure being swallowed.
        with mock.patch.object(
            Path, "unlink", self.fail_unlink_to(self.sheet_path())
        ):
            result = self.run_with_failed_write(self.user_js_path())
        self.assertIn(f"cannot restore {self.sheet_path()}", result.stderr)
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            self.sheet_path().read_bytes(),
        )
        self.assert_profile_absent(self.user_js_path())

    def test_a_failed_sheet_write_is_reported_by_path(self):
        # _apply publishes userChrome.css before user.js; a failure on that
        # first write must name the sheet and leave no user.js behind instead
        # of escaping as a traceback. The existing user.js write-failure test
        # pins the second publication; this pins the first.
        self.run_with_failed_write(self.sheet_path())
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_a_failed_user_content_write_removes_the_published_user_chrome(self):
        # The content sheet is published after userChrome.css; a failure on
        # that second write must name the content path and roll the already
        # published chrome sheet back, leaving no user.js behind.
        self.run_with_failed_write(self.content_sheet_path())
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_an_interrupt_after_the_user_content_write_takes_effect_removes_both(self):
        # The content-sheet write can publish its file and then raise before
        # the call returns. The rollback must remove that sheet as well as the
        # already published chrome sheet, and leave no user.js behind.
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.interrupt_write_to(self.content_sheet_path(), after_publish=True),
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assert_profile_absent(*self.owned_profile_paths())


if __name__ == "__main__":
    unittest.main()
