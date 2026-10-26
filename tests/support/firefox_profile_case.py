"""The temp-home Firefox profile case shared by the Firefox installer suites.

``tests/test_firefox_profile.py`` resolves profiles against a temp ``HOME``
and ``tests/test_firefox_install.py`` installs into a temp profile; both need
the same scratch root, home, profile and symlink/write-failure fixtures. They
live here once so each suite states only the behaviour it pins. The module
name does not match ``test*.py``, so ``unittest discover`` never collects it.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from support.cli_fixtures import run_main
from support.tmp_dir import make_tmp_dir
from tools import firefox_profile, firefox_user_files, install_firefox


class FirefoxProfileTestCase(unittest.TestCase):
    def setUp(self):
        self.root = make_tmp_dir(self)
        self.home = self.root / "home"
        self.home.mkdir()
        self.profile = self.root / "profile"
        self.profile.mkdir()

    def resolve(self, explicit=None, env=None):
        if env is None:
            env = {"HOME": str(self.home)}
        return firefox_profile.resolve_profile(explicit, env)

    def run_tool(self, *args, env=None):
        if env is None:
            env = {"HOME": str(self.home)}
        with mock.patch.dict(os.environ, env, clear=True):
            return run_main(install_firefox.main, install_firefox.TOOL, args)

    def sheet_path(self):
        return self.profile / "chrome" / "userChrome.css"

    def content_sheet_path(self):
        return self.profile / "chrome" / "userContent.css"

    def user_js_path(self):
        return self.profile / "user.js"

    def create_symlink(self, link, target, *, target_is_directory=False):
        """Create a fixture link, skipping the test if symlink creation fails."""
        try:
            link.symlink_to(target, target_is_directory=target_is_directory)
        except OSError:
            self.skipTest("cannot create a symlink on this platform")

    def fail_write_to(self, target):
        """Return a ``write_atomically`` stand-in that fails on *target*.

        Other paths still reach the real writer, so a test can pin which of
        the two profile files a failed publication names and what the other
        one holds.
        """
        real_write = firefox_user_files.write_atomically

        def flaky_write(path, writer):
            if Path(path) == target:
                raise OSError("simulated failure")
            return real_write(path, writer)

        return flaky_write

    @property
    def firefox_root(self):
        return self.home / ".mozilla" / "firefox"
