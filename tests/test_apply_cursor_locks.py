"""Tests for the data-home lock of ``apply_cursor``.

An apply holds the data-home flock ``make install``/``make uninstall`` hold
(the Makefile's ``run_locked``) across its installed-theme check, the
``~/.icons`` link and the selection, so a concurrent uninstall cannot remove
the theme between the check and the selection and leave a dangling link.
The workflow, fault and removal arms live in ``tests/test_apply_cursor.py``;
the case base mirrors its ``CursorCase`` setUp.
"""

from __future__ import annotations

import fcntl
import os
import shutil
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import run_main
from support.process_assertions import assert_failed, assert_succeeded
from support.tmp_dir import make_tmp_dir
from tools import apply_cursor


class CursorLockCase(unittest.TestCase):
    """Base with a temp home, data/config homes and an installed theme."""

    def setUp(self):
        self.root = make_tmp_dir(self)
        self.home = self.root / "home"
        self.home.mkdir()
        self.data = self.root / "data"
        self.config = self.root / "config"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.installed = self.data / "icons" / apply_cursor.CURSOR_THEME
        self.link = self.home / ".icons" / apply_cursor.CURSOR_THEME
        self.env = {
            "HOME": str(self.home),
            "XDG_DATA_HOME": str(self.data),
            "XDG_CONFIG_HOME": str(self.config),
            "PATH": str(self.bin),
        }
        (self.installed / "cursors").mkdir(parents=True)
        (self.installed / "index.theme").write_text(
            "[Icon Theme]\nName=Mac OS 8.6\n", encoding="utf-8"
        )
        (self.installed / "cursors" / "left_ptr").write_bytes(b"cursor\n")

    def run_tool(self, *args):
        with mock.patch.dict(os.environ, self.env, clear=True):
            return run_main(apply_cursor.main, "apply_cursor", args)

    def stub_selector(self, body="exit 0"):
        """Write a ``plasma-apply-cursortheme`` stub recording its argv."""
        path = self.bin / apply_cursor.SELECT_TOOL
        path.write_text(
            "#!/bin/sh\n"
            f"{body}\n",
            encoding="utf-8",
        )
        path.chmod(0o755)

    def hold_data_lock(self):
        """Take the data-home lock a concurrent install or uninstall holds."""
        descriptor = os.open(
            self.data, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        )
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.addCleanup(os.close, descriptor)


class TestDataHomeLock(CursorLockCase):
    """An apply serializes on the data-home lock make install/uninstall hold."""

    def test_apply_times_out_without_linking_while_an_install_or_uninstall_holds_the_data_home_lock(self):
        self.hold_data_lock()

        with mock.patch.object(apply_cursor, "LOCK_TIMEOUT", 0.05):
            result = self.run_tool()

        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
        self.assertIn("waiting for another install or uninstall", result.stderr)
        self.assertIn(str(self.data), result.stderr)
        self.assertFalse(self.link.is_symlink())

    def test_apply_releases_the_data_home_lock_for_the_next_run(self):
        self.stub_selector()
        assert_succeeded(self, self.run_tool())

        descriptor = os.open(
            self.data, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        )
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(descriptor)

    def test_apply_rechecks_the_installed_theme_under_the_data_home_lock(self):
        """A theme removed before the lock is taken refuses the apply.

        A concurrent uninstall that removes the installed icon theme while
        this run waits for the data-home lock must not leave a ``~/.icons``
        symlink pointing into a directory that no longer exists: the
        re-check under the lock refuses with the missing-theme diagnostic
        before the link is created.
        """
        real = apply_cursor._require_installed
        calls = []

        def theme_vanishes_before_the_next_check(data_home):
            if calls:
                # A concurrent uninstall removed the icon theme while this
                # run waited for the data-home lock.
                shutil.rmtree(self.data / "icons")
            calls.append(data_home)
            return real(data_home)

        with mock.patch.object(
            apply_cursor,
            "_require_installed",
            side_effect=theme_vanishes_before_the_next_check,
        ):
            result = self.run_tool()

        assert_failed(self, result)
        self.assertEqual(2, result.returncode)
        self.assertIn("installed cursor theme is missing", result.stderr)
        self.assertIn("make install INSTALL_PACKAGES=icon-theme", result.stderr)
        self.assertFalse(self.link.is_symlink())


if __name__ == "__main__":
    unittest.main()
