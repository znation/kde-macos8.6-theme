"""Tests for ``tools/firefox_profile.py`` -- resolving the Firefox profile directory.

Each case runs against a temp ``HOME`` so a real Firefox profile is never read
or written. The installer suites that use the resolved profile live in
``tests/test_install_firefox.py``; the shared temp-home case is
``support.firefox_profile_case``.
"""

from __future__ import annotations

import os
import unittest
from unittest import mock

from support import repo_root, snippet_child
from support.fifo_fixtures import assert_fifo_refused, make_fifo
from support.firefox_profile_case import FirefoxProfileTestCase
from tools import firefox_profile, firefox_user_files


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


class TestProfileResolution(FirefoxProfileTestCase):
    def test_explicit_absolute_profile_is_used(self):
        self.assertEqual(self.profile, self.resolve(str(self.profile)))

    def test_environment_profile_is_used_when_the_flag_is_absent(self):
        self.assertEqual(
            self.profile,
            self.resolve(None, {"HOME": str(self.home), "FIREFOX_PROFILE": str(self.profile)}),
        )

    def test_an_empty_environment_profile_falls_back_to_discovery(self):
        # GNU make exports a command-line FIREFOX_PROFILE= (empty) to the
        # recipe, which must mean "no profile named", as the Makefile's own
        # $(if ...) already treats it, not Path("") == ".".
        profile = self.firefox_root / "Profiles" / "active.default"
        profile.mkdir(parents=True)
        _write(
            self.firefox_root / "installs.ini",
            f"[Install1234]\nDefault={profile.relative_to(self.firefox_root)}\n",
        )
        self.assertEqual(
            profile,
            self.resolve(None, {"HOME": str(self.home), "FIREFOX_PROFILE": ""}),
        )

    def test_relative_named_profile_is_refused(self):
        with self.assertRaises(firefox_user_files.ConfigError) as caught:
            self.resolve("profile")
        self.assertIn("absolute", str(caught.exception))

    def test_missing_named_profile_is_refused(self):
        missing = self.root / "missing"
        with self.assertRaises(firefox_user_files.ConfigError) as caught:
            self.resolve(str(missing))
        self.assertIn(str(missing), str(caught.exception))

    def test_unusable_home_is_refused(self):
        with self.assertRaises(firefox_user_files.ConfigError) as caught:
            self.resolve(None, {"HOME": "relative/home"})
        self.assertIn("HOME", str(caught.exception))

    def test_installs_ini_default_is_the_first_candidate(self):
        profile = self.firefox_root / "Profiles" / "installed.default"
        profile.mkdir(parents=True)
        _write(
            self.firefox_root / "installs.ini",
            "[Install4F96]\nDefault=Profiles/installed.default\n",
        )
        self.assertEqual(profile, self.resolve())

    def test_installs_ini_hash_named_section_is_used(self):
        profile = self.firefox_root / "Profiles" / "hash.default"
        profile.mkdir(parents=True)
        _write(
            self.firefox_root / "installs.ini",
            "[3B6073811A6ABF12]\nDefault=Profiles/hash.default\n",
        )
        self.assertEqual(profile, self.resolve())

    def test_installs_ini_default_with_a_percent_sign_is_read_literally(self):
        # configparser interpolates %(...) and rejects a lone % by default, and
        # that error is raised by section.get() inside _candidate, outside the
        # reader's ConfigError wrap. A profile directory named "100% work"
        # must resolve, not escape discovery as a traceback.
        profile = self.firefox_root / "Profiles" / "100% work"
        profile.mkdir(parents=True)
        _write(
            self.firefox_root / "installs.ini",
            "[Install4F96]\nDefault=Profiles/100% work\n",
        )
        self.assertEqual(profile, self.resolve())

    def test_a_stale_first_installs_section_falls_through_a_later_install(self):
        live = self.firefox_root / "Profiles" / "live.default"
        live.mkdir(parents=True)
        _write(
            self.firefox_root / "installs.ini",
            "[InstallAAAA]\nDefault=Profiles/deleted.default\n"
            "[InstallBBBB]\nDefault=Profiles/live.default\n",
        )
        self.assertEqual(live, self.resolve())

    def test_stale_installs_default_falls_through_to_profiles_ini(self):
        # installs.ini can outlive the profile directory it names after a
        # profile is deleted; resolution must keep trying profiles.ini
        # instead of reporting that the stale candidate was not found.
        alive = self.firefox_root / "alive"
        alive.mkdir(parents=True)
        _write(
            self.firefox_root / "installs.ini",
            "[Install4F96]\nDefault=Profiles/deleted.default\n",
        )
        _write(
            self.firefox_root / "profiles.ini",
            "[Profile0]\nName=alive\nPath=alive\n",
        )
        self.assertEqual(alive, self.resolve())

    def test_stale_installs_default_does_not_hide_a_profiles_default_marker(self):
        # installs.ini can name a deleted profile while profiles.ini marks a
        # different, live profile Default=1. The stale install candidate must
        # be skipped without discarding the marker or falling back to the
        # first profiles.ini section instead of the marked one.
        first = self.firefox_root / "first"
        chosen = self.firefox_root / "chosen"
        first.mkdir(parents=True)
        chosen.mkdir()
        _write(
            self.firefox_root / "installs.ini",
            "[Install4F96]\nDefault=Profiles/deleted.default\n",
        )
        _write(
            self.firefox_root / "profiles.ini",
            "[Profile0]\nName=first\nPath=first\n"
            "[Profile1]\nName=chosen\nPath=chosen\nDefault=1\n",
        )
        self.assertEqual(chosen, self.resolve())

    def test_a_profiles_default_that_is_stale_falls_back_to_a_live_profile(self):
        # A Default=1 marker can outlive the profile directory it names. The
        # marked candidate is tried first, then the other sections, so a
        # deleted default must not turn into a not-found error.
        live = self.firefox_root / "live"
        live.mkdir(parents=True)
        _write(
            self.firefox_root / "profiles.ini",
            "[Profile0]\nName=live\nPath=live\n"
            "[Profile1]\nName=gone\nPath=gone\nDefault=1\n",
        )
        self.assertEqual(live, self.resolve())

    def test_a_stale_default_and_a_stale_first_section_fall_through_a_later_profile(self):
        # A Default=1 marker and the first section can both name deleted
        # profiles while a later section is live. Discovery must try every
        # section that names a Path, not stop after the first one.
        live = self.firefox_root / "live"
        live.mkdir(parents=True)
        _write(
            self.firefox_root / "profiles.ini",
            "[Profile0]\nName=gone\nPath=gone\n"
            "[Profile1]\nName=also-gone\nPath=also-gone\nDefault=1\n"
            "[Profile2]\nName=live\nPath=live\n",
        )
        self.assertEqual(live, self.resolve())

    def test_the_candidates_tried_diagnostic_lists_a_profile_once(self):
        # A profiles.ini whose marked default is also its first section names
        # one directory; the not-found diagnostic must not list it twice.
        missing = self.firefox_root / "only"
        _write(
            self.firefox_root / "profiles.ini",
            "[Profile0]\nName=only\nPath=only\nDefault=1\n",
        )
        with self.assertRaises(firefox_user_files.ConfigError) as caught:
            self.resolve()
        self.assertEqual(str(caught.exception).count(str(missing)), 1)

    def test_installs_section_without_default_is_skipped(self):
        # Firefox names installs.ini sections by install hash; a section
        # carrying no Default (or an empty one) must not hide a later one.
        profile = self.firefox_root / "Profiles" / "live.default"
        profile.mkdir(parents=True)
        _write(
            self.firefox_root / "installs.ini",
            "[InstallOld]\nName=old\nDefault=\n"
            "[InstallNew]\nDefault=Profiles/live.default\n",
        )
        self.assertEqual(profile, self.resolve())

    def test_profiles_ini_path_with_a_percent_sign_is_read_literally(self):
        # profiles.ini values are read through the same non-interpolating
        # parser as installs.ini, so a percent sign in a profile directory
        # name is literal there too instead of raising out of discovery.
        profile = self.firefox_root / "10% off"
        profile.mkdir(parents=True)
        _write(
            self.firefox_root / "profiles.ini",
            "[Profile0]\nName=discount\nPath=10% off\n",
        )
        self.assertEqual(profile, self.resolve())

    def test_profiles_ini_default_marker_is_used(self):
        first = self.firefox_root / "first"
        chosen = self.firefox_root / "chosen"
        first.mkdir(parents=True)
        chosen.mkdir()
        _write(
            self.firefox_root / "profiles.ini",
            "[Profile0]\nName=first\nPath=first\n"
            "[Profile1]\nName=chosen\nPath=chosen\nDefault=1\n",
        )
        self.assertEqual(chosen, self.resolve())

    def test_profiles_default_without_a_path_falls_back_to_the_first_path(self):
        # A Default=1 marker on a section with no Path names no directory;
        # resolution must still use the first section that has one rather
        # than dropping every profile candidate.
        first = self.firefox_root / "first"
        first.mkdir(parents=True)
        _write(
            self.firefox_root / "profiles.ini",
            "[Profile0]\nName=first\nPath=first\n"
            "[Profile1]\nName=chosen\nDefault=1\n",
        )
        self.assertEqual(first, self.resolve())

    def test_first_profile_with_a_path_is_the_fallback(self):
        first = self.firefox_root / "first"
        second = self.firefox_root / "second"
        first.mkdir(parents=True)
        second.mkdir()
        _write(
            self.firefox_root / "profiles.ini",
            "[Profile0]\nName=first\nPath=first\n"
            "[Profile1]\nName=second\nPath=second\n",
        )
        self.assertEqual(first, self.resolve())

    def test_absolute_profile_path_ignores_the_firefox_root(self):
        chosen = self.root / "elsewhere"
        chosen.mkdir()
        self.firefox_root.mkdir(parents=True)
        _write(
            self.firefox_root / "profiles.ini",
            f"[Profile0]\nPath={chosen}\nIsRelative=0\n",
        )
        self.assertEqual(chosen, self.resolve())

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

    def test_no_existing_candidate_names_the_root_and_candidates(self):
        self.firefox_root.mkdir(parents=True)
        _write(
            self.firefox_root / "profiles.ini",
            "[Profile0]\nPath=absent\n",
        )
        with self.assertRaises(firefox_user_files.ConfigError) as caught:
            self.resolve()
        message = str(caught.exception)
        self.assertIn(str(self.firefox_root), message)
        self.assertIn(str(self.firefox_root / "absent"), message)




if __name__ == "__main__":
    unittest.main()
