"""Pin profile-directory lock serialization for Firefox install and removal.

These cases cover bounded waits, no writes under contention, release for the
next run and lock-failure refusals. Sheet and ``user.js`` install, rollback and
removal cases stay in ``tests/test_install_firefox.py``,
``tests/test_install_firefox_rollback.py``, ``tests/test_remove_firefox.py`` and
``tests/test_remove_firefox_rollback.py``.
"""

from __future__ import annotations

import errno
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.firefox_profile_case import FirefoxProfileTestCase
from support.flock_fixtures import assert_directory_flock_free, hold_directory_flock
from support.process_assertions import assert_lock_time_out, assert_succeeded
from tools import file_lock, install_firefox


class TestProfileLock(FirefoxProfileTestCase):
    """Concurrent installs and removals serialize on the profile directory."""

    def hold_profile_lock(self):
        """Take the lock a concurrent run would hold, and release it after."""
        hold_directory_flock(self, self.profile)

    def test_install_times_out_without_writing_while_another_run_holds_the_lock(
        self,
    ):
        self.hold_profile_lock()

        with mock.patch.object(install_firefox, "LOCK_TIMEOUT", 0.05):
            result = self.run_tool("--profile", str(self.profile))

        assert_lock_time_out(
            self,
            result,
            "waiting for another install-firefox/remove-firefox",
            self.profile,
        )
        self.assert_profile_absent(*self.owned_profile_paths())

    def test_remove_times_out_without_clearing_the_install(self):
        installed = self.run_tool("--profile", str(self.profile))
        assert_succeeded(self, installed)
        before_sheet = self.sheet_path().read_bytes()
        before_js = self.user_js_path().read_bytes()
        self.hold_profile_lock()

        with mock.patch.object(install_firefox, "LOCK_TIMEOUT", 0.05):
            result = self.run_tool("--remove", "--profile", str(self.profile))

        assert_lock_time_out(
            self,
            result,
            "waiting for another install-firefox/remove-firefox",
            self.profile,
        )
        self.assertEqual(before_sheet, self.sheet_path().read_bytes())
        self.assertEqual(before_js, self.user_js_path().read_bytes())

    def test_install_releases_the_lock_for_the_next_run(self):
        result = self.run_tool("--profile", str(self.profile))
        assert_succeeded(self, result)

        assert_directory_flock_free(self.profile)

    def test_install_refuses_when_the_profile_lock_cannot_be_opened(self):
        def refuse_open(*args, **kwargs):
            raise PermissionError(errno.EACCES, "simulated refusal")

        with mock.patch.object(install_firefox.os, "open", side_effect=refuse_open):
            result = self.run_tool("--profile", str(self.profile))

        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot lock {self.profile}", result.stderr)
        self.assertIn("simulated refusal", result.stderr)
        self.assert_profile_absent(self.sheet_path())

    def test_install_refuses_a_lock_that_fails_for_another_reason(self):
        def refuse_lock(*args, **kwargs):
            raise OSError(errno.EIO, "simulated failure")

        with mock.patch.object(file_lock.fcntl, "flock", side_effect=refuse_lock):
            result = self.run_tool("--profile", str(self.profile))

        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot lock {self.profile}", result.stderr)
        self.assertIn("simulated failure", result.stderr)
        self.assert_profile_absent(self.sheet_path())


if __name__ == "__main__":
    unittest.main()
