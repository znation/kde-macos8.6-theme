"""Tests for the serialization locks of ``apply_gtk``.

An apply and a removal serialize on an exclusive flock over the directory
containing the config home, and an apply also holds the data-home flock
``make install``/``make uninstall`` hold, so concurrent runs cannot publish
stale edits or race an uninstall. The workflow and fault arms live in
``tests/test_gtk_apply.py`` and ``tests/test_gtk_apply_errors.py``; the
shared temp-root case is ``support.gtk_apply_case``.
"""

from __future__ import annotations

import errno
import fcntl
import os
import shutil
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import run_main
from support.gtk_apply_case import GtkApplyTestCase
from support.process_assertions import (
    assert_exit_2_without_traceback,
    assert_failed,
    assert_succeeded,
)
from tools import apply_gtk


class TestConfigLock(GtkApplyTestCase):
    """Concurrent applies and removals serialize on the config home."""

    def hold_config_lock(self):
        """Take the lock a concurrent run would hold, and release it after."""
        lock_dir = self.config.parent
        lock_dir.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(
            lock_dir, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        )
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.addCleanup(os.close, descriptor)

    def test_apply_times_out_without_writing_while_another_run_holds_the_lock(self):
        self.install_sheet()
        before = "[Settings]\ngtk-theme-name=Adwaita\n"
        self.write(self.settings("gtk-3.0"), before)
        self.hold_config_lock()

        with mock.patch.object(apply_gtk, "LOCK_TIMEOUT", 0.05):
            result = self.run_tool()

        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
        self.assertIn("waiting for another apply-gtk/remove-gtk", result.stderr)
        self.assertIn(str(self.config), result.stderr)
        self.assertFalse(self.settings("gtk-4.0").exists())
        self.assertFalse((self.config / "gtk-4.0" / "gtk.css").exists())
        self.assertEqual(before, self.settings("gtk-3.0").read_text(encoding="utf-8"))

    def test_apply_releases_the_lock_for_the_next_run(self):
        self.install_sheet()
        assert_succeeded(self, self.run_tool())

        descriptor = os.open(
            self.config.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        )
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(descriptor)

    def test_apply_with_a_missing_sheet_does_not_create_the_config_home(self):
        result = self.run_tool()

        self.assertEqual(1, result.returncode)
        self.assertIn("make install-gtk", result.stderr)
        self.assertFalse(self.config.exists())

    def test_remove_times_out_without_clearing_the_selection(self):
        before = "[Settings]\ngtk-theme-name=org.macos8.desktop\n"
        self.write(self.settings("gtk-3.0"), before)
        self.hold_config_lock()

        with mock.patch.object(apply_gtk, "LOCK_TIMEOUT", 0.05):
            result = self.run_tool("--remove")

        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
        self.assertIn("waiting for another apply-gtk/remove-gtk", result.stderr)
        self.assertIn(str(self.config), result.stderr)
        self.assertEqual(
            before, self.settings("gtk-3.0").read_text(encoding="utf-8")
        )

    def test_remove_waits_for_the_lock_even_without_a_config_home(self):
        self.hold_config_lock()

        with mock.patch.object(apply_gtk, "LOCK_TIMEOUT", 0.05):
            result = self.run_tool("--remove")

        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
        self.assertIn("waiting for another apply-gtk/remove-gtk", result.stderr)
        self.assertIn(str(self.config), result.stderr)
        self.assertFalse(self.config.exists())

    def test_remove_creates_only_the_containing_directory_it_locks(self):
        nested_config = self.root / "nested" / "config"

        with mock.patch.dict(
            os.environ, {"XDG_CONFIG_HOME": str(nested_config)}, clear=True
        ):
            result = run_main(apply_gtk.main, "apply_gtk", ("--remove",))

        assert_succeeded(self, result)
        self.assertTrue(nested_config.parent.is_dir())
        self.assertFalse(nested_config.exists())

    def test_remove_refuses_when_the_lock_directory_cannot_be_created(self):
        blocked = self.root / "blocked"
        blocked.write_text("not a directory", encoding="utf-8")
        env = {**self.env, "XDG_CONFIG_HOME": str(blocked / "config")}

        with mock.patch.dict(os.environ, env, clear=True):
            result = run_main(apply_gtk.main, "apply_gtk", ("--remove",))

        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot create {blocked}", result.stderr)
        self.assertFalse((blocked / "config").exists())

    def test_remove_refuses_when_the_lock_directory_cannot_be_opened(self):
        def refuse_open(*args, **kwargs):
            raise PermissionError(errno.EACCES, "simulated refusal")

        with mock.patch.object(apply_gtk.os, "open", side_effect=refuse_open):
            result = self.run_tool("--remove")

        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot lock {self.config.parent}", result.stderr)
        self.assertIn("simulated refusal", result.stderr)


class TestDataHomeLock(GtkApplyTestCase):
    """An apply serializes on the data-home lock make install/uninstall hold."""

    def hold_data_lock(self):
        """Take the data-home lock a concurrent install or uninstall holds."""
        descriptor = os.open(
            self.data, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        )
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.addCleanup(os.close, descriptor)

    def test_apply_times_out_without_writing_while_an_install_or_uninstall_holds_the_data_home_lock(self):
        self.install_sheet()
        before = "[Settings]\ngtk-theme-name=Adwaita\n"
        self.write(self.settings("gtk-3.0"), before)
        self.hold_data_lock()

        with mock.patch.object(apply_gtk, "LOCK_TIMEOUT", 0.05):
            result = self.run_tool()

        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
        self.assertIn("waiting for another install or uninstall", result.stderr)
        self.assertIn(str(self.data), result.stderr)
        self.assertFalse(self.settings("gtk-4.0").exists())
        self.assertFalse((self.config / "gtk-4.0" / "gtk.css").exists())
        self.assertEqual(before, self.settings("gtk-3.0").read_text(encoding="utf-8"))

    def test_apply_releases_the_data_home_lock_for_the_next_run(self):
        self.install_sheet()
        assert_succeeded(self, self.run_tool())

        descriptor = os.open(
            self.data, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        )
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(descriptor)

    def test_apply_rechecks_the_sheets_under_the_data_home_lock(self):
        """Sheets removed before the lock is taken refuse the apply.

        A concurrent uninstall that removes the installed sheets while this
        run waits for the data-home lock must not leave a published selection
        naming sheets that no longer exist: the re-check under the lock
        refuses with the missing-sheet diagnostic instead.
        """
        self.install_sheet()
        real = apply_gtk._installed_sheets
        calls = []

        def sheets_vanish_before_the_next_check(data_home):
            if calls:
                # A concurrent uninstall removed the sheets while this run
                # waited for the data-home lock.
                shutil.rmtree(self.data / "themes")
            calls.append(data_home)
            return real(data_home)

        with mock.patch.object(
            apply_gtk, "_installed_sheets", side_effect=sheets_vanish_before_the_next_check
        ):
            result = self.run_tool()

        assert_failed(self, result)
        self.assertEqual(1, result.returncode)
        self.assertIn("installed gtk-4.0 sheet is missing", result.stderr)
        self.assertIn("make install-gtk", result.stderr)
        self.assertFalse(self.settings("gtk-4.0").exists())
        self.assertFalse((self.config / "gtk-4.0" / "gtk.css").exists())



if __name__ == "__main__":
    unittest.main()
