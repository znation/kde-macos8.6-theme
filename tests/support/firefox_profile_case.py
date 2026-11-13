"""The temp-home Firefox profile case shared by the Firefox installer suites.

``tests/test_firefox_profile.py`` resolves profiles against a temp ``HOME``
and ``tests/test_install_firefox.py`` installs into a temp profile; both need
the same scratch root, home, profile and symlink/write-failure fixtures. They
live here once so each suite states only the behaviour it pins. The module
name does not match ``test*.py``, so ``unittest discover`` never collects it.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from support.cli_fixtures import run_main_with_env
from support.tmp_dir import make_tmp_dir
from tools import firefox_profile, firefox_user_files, firefox_user_js, install_firefox


class FirefoxProfileTestCase(unittest.TestCase):
    """Create the temp HOME and profile shared by the installer suites."""

    def setUp(self):
        self.root = make_tmp_dir(self)
        self.home = self.root / "home"
        self.home.mkdir()
        self.profile = self.root / "profile"
        self.profile.mkdir()

    def resolve(self, explicit=None, env=None):
        """Resolve *explicit* against *env*, defaulting to :attr:`home`."""
        if env is None:
            env = {"HOME": str(self.home)}
        return firefox_profile.resolve_profile(explicit, env)

    def run_tool(self, *args, env=None):
        """Run the installer with *args* under *env*; return the captured process."""
        if env is None:
            env = {"HOME": str(self.home)}
        return run_main_with_env(install_firefox.main, install_firefox.TOOL, args, env)

    def sheet_path(self):
        """Return the ``userChrome.css`` path inside :attr:`profile`."""
        return self.profile / "chrome" / "userChrome.css"

    def content_sheet_path(self):
        """Return the ``userContent.css`` path inside :attr:`profile`."""
        return self.profile / "chrome" / "userContent.css"

    def user_js_path(self):
        """Return the ``user.js`` path inside :attr:`profile`."""
        return self.profile / "user.js"

    def owned_profile_paths(self):
        """Return the three installer-owned profile paths as a tuple."""
        return (
            self.sheet_path(),
            self.content_sheet_path(),
            self.user_js_path(),
        )

    def assert_profile_absent(self, *paths):
        """Assert none of *paths* exist, naming the first survivor on failure.

        Shared by the installer suites' absence pins; every call site lives
        in ``tests/test_install_firefox.py``.
        """
        for path in paths:
            self.assertFalse(path.exists(), f"{path} unexpectedly exists")

    @staticmethod
    def _owned_user_js_block(newline="\n"):
        """Return the installer-owned preference block with *newline* endings."""
        return "".join(
            line + newline
            for line in (
                firefox_user_js.USER_JS_MARKER,
                *firefox_user_js.PREF_LINES,
            )
        )

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

    def run_with_failed_write(self, target, *tool_args):
        """Run the installer with the publication write to *target* failing.

        *tool_args* defaults to the install invocation; a removal caller
        passes ``--remove`` plus its profile. The run must be refused with
        exit status 2 and the by-name ``cannot write`` diagnostic naming
        *target*; the result is returned so a caller can pin what the
        rollback left behind. Seven callers in
        ``tests/test_install_firefox.py``; the write stand-in is
        :meth:`fail_write_to`.
        """
        if not tool_args:
            tool_args = ("--profile", str(self.profile))
        with mock.patch.object(
            firefox_user_files, "write_atomically", self.fail_write_to(target)
        ):
            result = self.run_tool(*tool_args)
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {target}", result.stderr)
        return result

    def interrupt_write_to(self, target, *, after_publish=False):
        """Return a ``write_atomically`` stand-in that interrupts at *target*.

        The stand-in raises ``KeyboardInterrupt`` while handling *target*:
        before the real writer never rewrites it, or, with ``after_publish``,
        once the real writer has published the file, so a test can pin what a
        roll-back sees after a write that took effect. Other paths still
        reach the real writer. Five callers in
        ``tests/test_install_firefox.py``; the failure twin is
        :meth:`fail_write_to`.
        """
        real_write = firefox_user_files.write_atomically

        def interrupted_write(path, writer):
            if Path(path) == target:
                if after_publish:
                    real_write(path, writer)
                raise KeyboardInterrupt
            return real_write(path, writer)

        return interrupted_write

    def interrupt_unlink_to(self, target):
        """Return a ``Path.unlink`` stand-in that removes *target*, then raises.

        The stand-in unlinks *target* really and raises ``KeyboardInterrupt``
        on the way back, so a test pins what survives a removal whose unlink
        took effect before the caller recorded it. Other paths still unlink
        really. Two callers in ``tests/test_install_firefox.py``; the
        failure twin is :meth:`fail_unlink_to`.
        """
        real_unlink = Path.unlink

        def interrupted_unlink(path, *args, **kwargs):
            if Path(path) == target:
                real_unlink(path, *args, **kwargs)
                raise KeyboardInterrupt
            return real_unlink(path, *args, **kwargs)

        return interrupted_unlink

    def fail_unlink_to(self, target):
        """Return a ``Path.unlink`` stand-in that fails on *target*.

        Other paths still unlink really, so a test can pin which of the
        profile files a failed removal names and what the others hold.
        The write-failure twin is :meth:`fail_write_to`; the
        remove-then-interrupt twin is :meth:`interrupt_unlink_to`.
        """
        real_unlink = Path.unlink

        def flaky_unlink(path, *args, **kwargs):
            if Path(path) == target:
                raise OSError("simulated failure")
            return real_unlink(path, *args, **kwargs)

        return flaky_unlink

    @property
    def firefox_root(self):
        """Return the ``~/.mozilla/firefox`` root under :attr:`home`."""
        return self.home / ".mozilla" / "firefox"
