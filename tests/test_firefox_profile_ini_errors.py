"""Tests for ``tools/firefox_profile.py`` -- reading ``installs.ini`` and ``profiles.ini``.

These pin how profile discovery reports an INI file that cannot be read: a
malformed, duplicate-keyed, non-UTF-8, unreadable, oversize, or FIFO file. They
do not pin which profile discovery picks; the selection tests stay in
``tests/test_firefox_profile.py``.

Each case runs against a temp ``HOME`` so a real Firefox profile is never read
or written.
"""

from __future__ import annotations

import os
import unittest
from unittest import mock

from support import repo_root, snippet_child
from support.fifo_fixtures import assert_fifo_refused, make_fifo
from support.firefox_profile_case import FirefoxProfileTestCase
from tools import firefox_profile, firefox_user_files


class TestProfileIniErrors(FirefoxProfileTestCase):
    def test_a_malformed_profiles_ini_is_reported_by_name(self):
        # A hand-edited profiles.ini that is not INI at all must be reported
        # by path. The reader's docstring promises a by-name ConfigError;
        # without this a configparser exception would escape as a traceback
        # that never names the file to fix.
        self.firefox_root.mkdir(parents=True)
        profiles = self.firefox_root / "profiles.ini"
        profiles.write_text("Profiles/onlydefault\n", encoding="utf-8")
        with self.assertRaises(firefox_user_files.ConfigError) as caught:
            self.resolve()
        self.assertIn(f"cannot read {profiles}", str(caught.exception))

    def test_a_duplicate_section_or_option_is_reported_by_name(self):
        # configparser is strict, so a repeated section or option is an error
        # rather than a silent last-one-wins pick of the profile to modify.
        self.firefox_root.mkdir(parents=True)
        for name, text in (
            ("profiles.ini", "[Profile0]\nPath=a\n[Profile0]\nPath=b\n"),
            ("profiles.ini", "[Profile0]\nPath=a\nPath=b\n"),
            ("installs.ini", "[ABC]\nDefault=a\n[ABC]\nDefault=b\n"),
        ):
            with self.subTest(name=name, text=text):
                path = self.firefox_root / name
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(firefox_user_files.ConfigError) as caught:
                    self.resolve()
                self.assertIn(f"cannot read {path}", str(caught.exception))
                path.unlink()

    def test_a_non_utf8_profiles_ini_is_reported_by_name(self):
        # Firefox's own ini files are UTF-8, but a stray byte must still name
        # the file rather than raise UnicodeDecodeError out of the tool.
        self.firefox_root.mkdir(parents=True)
        profiles = self.firefox_root / "profiles.ini"
        profiles.write_bytes(b"[Profile0]\nPath=\xff\n")
        with self.assertRaises(firefox_user_files.ConfigError) as caught:
            self.resolve()
        self.assertIn(f"cannot read {profiles}", str(caught.exception))

    def test_an_unreadable_profiles_ini_is_reported_by_name(self):
        # The reader's docstring promises an unreadable INI becomes a by-name
        # ConfigError. A self-referential symlink makes the open fail with
        # ELOOP deterministically -- no dependence on file permissions or on
        # the test user -- exercising the OSError arm that the malformed, the
        # non-UTF-8, the missing and the FIFO fixtures each miss.
        self.firefox_root.mkdir(parents=True)
        profiles = self.firefox_root / "profiles.ini"
        self.create_symlink(profiles, profiles)
        with self.assertRaises(firefox_user_files.ConfigError) as caught:
            self.resolve()
        self.assertIn(f"cannot read {profiles}", str(caught.exception))

    def test_an_oversize_ini_file_is_refused_by_name(self):
        # A profile-discovery INI is the user's file and can name something
        # arbitrarily large. Before the read cap, configparser read it whole,
        # so a huge file raised MemoryError instead of the by-name
        # ConfigError the reader promises.
        self.firefox_root.mkdir(parents=True)
        for name in ("installs.ini", "profiles.ini"):
            with self.subTest(ini=name):
                ini = self.firefox_root / name
                with ini.open("wb") as handle:
                    handle.truncate(firefox_profile._MAX_INI_FILE_BYTES + 1)
                with self.assertRaises(firefox_user_files.ConfigError) as caught:
                    self.resolve()
                message = str(caught.exception)
                self.assertIn(str(ini), message)
                self.assertIn(
                    f"{firefox_profile._MAX_INI_FILE_BYTES}-byte", message
                )
                ini.unlink()

    def test_an_ini_file_at_the_1_mib_cap_is_accepted(self):
        profile = self.firefox_root / "Profiles" / "live.default"
        profile.mkdir(parents=True)
        header = b"[Install]\nDefault=Profiles/live.default\n"
        comment = (
            b"#"
            + b"x"
            * (
                firefox_profile._MAX_INI_FILE_BYTES
                - len(header)
                - len(b"#\n")
            )
            + b"\n"
        )
        installs = self.firefox_root / "installs.ini"
        installs.write_bytes(header + comment)
        self.assertEqual(
            firefox_profile._MAX_INI_FILE_BYTES, installs.stat().st_size
        )
        self.assertEqual(profile, self.resolve())

    def test_a_fifo_at_either_ini_file_is_refused_without_blocking(self):
        # Profile discovery used Path.open, whose read waits forever on a FIFO,
        # so `make install-firefox` without --profile hung with no diagnostic.
        # Run the tool in a child so a regression fails on a timeout instead of
        # stalling the suite, and check the pipe is named before it is read.
        snippet = (
            "import sys; from tools.install_firefox import main; "
            "sys.exit(main([]))"
        )
        for name in ("installs.ini", "profiles.ini"):
            with self.subTest(ini=name):
                home = self.root / f"home-{name}"
                home.mkdir()
                root = home / ".mozilla" / "firefox"
                root.mkdir(parents=True)
                fifo = root / name
                make_fifo(self, fifo)
                with mock.patch.dict(os.environ, {"HOME": str(home)}, clear=True):
                    child = snippet_child.run(
                        [snippet], cwd=repo_root.ROOT, timeout=10
                    )
                assert_fifo_refused(self, child, fifo)


if __name__ == "__main__":
    unittest.main()
