"""Tests for the Firefox profile install and its three helper modules.

The tool runs in-process with ``HOME`` pointed at a temp root, so profile
resolution, the sheet copy, the ``user.js`` edit and the removal are pinned
without touching a real Firefox profile.
"""

from __future__ import annotations

import errno
import os
import unittest
from pathlib import Path
from unittest import mock

from support import containment, snippet_child
from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import run_main
from support.fifo_fixtures import assert_fifo_refused, make_fifo
from support.tmp_dir import make_tmp_dir
from tools import firefox_profile, firefox_user_files, firefox_user_js, install_firefox

SHEET_PATH = Path(repo_root.ROOT) / install_firefox.SHEET


def _read(path):
    return path.read_bytes().decode("utf-8")


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


class ProfileCase(unittest.TestCase):
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


class TestProfileResolution(ProfileCase):
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


class TestUserJs(unittest.TestCase):
    def test_shipped_marker_and_preference_are_pinned(self):
        self.assertEqual(
            "/* org.macos8.desktop Firefox chrome, standalone userChrome.css",
            install_firefox.CSS_MARKER,
        )
        self.assertEqual(
            "// org.macos8.desktop Firefox Platinum userChrome",
            firefox_user_js.USER_JS_MARKER,
        )
        self.assertEqual(
            'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);',
            firefox_user_js.PREF_LINE,
        )
        first_line = containment.read_bytes(SHEET_PATH, repo_root.ROOT).decode(
            "utf-8"
        ).splitlines()[0]
        self.assertEqual(install_firefox.CSS_MARKER, first_line)

    def test_new_file_gets_one_marker_and_pref_block(self):
        self.assertEqual(
            firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n",
            firefox_user_js.set_user_js(""),
        )

    def test_repeat_install_leaves_exactly_one_block(self):
        once = firefox_user_js.set_user_js("")
        self.assertEqual(once, firefox_user_js.set_user_js(once))
        self.assertEqual(1, once.count(firefox_user_js.USER_JS_MARKER))
        self.assertEqual(1, once.count(firefox_user_js.PREF_LINE))

    def test_foreign_lines_keep_their_crlf_and_terminated_last_line(self):
        foreign = (
            'user_pref("browser.tabs.inTitlebar", 0);\r\n'
            'user_pref("browser.startup.homepage", "about:blank");'
        )
        self.assertEqual(
            foreign
            + "\r\n"
            + firefox_user_js.USER_JS_MARKER
            + "\r\n"
            + firefox_user_js.PREF_LINE
            + "\r\n",
            firefox_user_js.set_user_js(foreign),
        )

    def test_foreign_setting_of_the_same_pref_survives_before_our_line(self):
        foreign = firefox_user_js.PREF_LINE + "\n"
        updated = firefox_user_js.set_user_js(foreign)
        self.assertEqual(2, updated.count(firefox_user_js.PREF_LINE))
        self.assertTrue(updated.startswith(foreign))
        self.assertTrue(
            updated.endswith(
                firefox_user_js.USER_JS_MARKER
                + "\n"
                + firefox_user_js.PREF_LINE
                + "\n"
            )
        )

    def test_remove_deletes_only_the_marker_pair(self):
        foreign = 'user_pref("a", 1);\n'
        text = (
            foreign
            + firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n"
        )
        self.assertEqual(foreign, firefox_user_js.remove_user_js(text))

    def test_remove_leaves_a_foreign_pref_and_missing_final_newline(self):
        foreign = firefox_user_js.PREF_LINE + "\nuser_pref(\"last\", 1);"
        self.assertEqual(foreign, firefox_user_js.remove_user_js(foreign))
        self.assertEqual(
            'user_pref("last", 1);',
            firefox_user_js.remove_user_js('user_pref("last", 1);'),
        )

    def test_a_bom_before_our_marker_still_matches_the_block(self):
        # A UTF-8 BOM is valid at the start of a JavaScript file and some
        # editors add one. It must not hide our marker block: a repeat install
        # must not append a second copy, and a removal must delete the pair.
        block = (
            firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n"
        )
        text = "\ufeff" + block
        self.assertEqual(block, firefox_user_js.set_user_js(text))
        self.assertEqual("", firefox_user_js.remove_user_js(text))

    def test_a_bom_before_a_foreign_first_line_stays(self):
        # Only a marker line ignores the BOM; a foreign first line keeps it
        # byte for byte through an install and a removal.
        foreign = '\ufeffuser_pref("a", 1);\n'
        updated = firefox_user_js.set_user_js(foreign)
        self.assertTrue(updated.startswith(foreign))
        self.assertEqual(foreign, firefox_user_js.remove_user_js(foreign))

    def test_bom_tolerance_is_limited_to_one_bom_on_the_first_line(self):
        marker = firefox_user_js.USER_JS_MARKER
        pref = firefox_user_js.PREF_LINE
        block = marker + "\r\n" + pref + "\r\n"
        for foreign in (
            '// foreign header\r\n\ufeff' + block,
            '\ufeff\ufeff' + block,
        ):
            with self.subTest(foreign=foreign):
                # These are foreign marker lookalikes, so neither their
                # comments nor the preference following them may be deleted.
                self.assertEqual(foreign, firefox_user_js.remove_user_js(foreign))
                installed = firefox_user_js.set_user_js(foreign)
                self.assertEqual(foreign + block, installed)
                self.assertEqual(installed, firefox_user_js.set_user_js(installed))
                self.assertEqual(foreign, firefox_user_js.remove_user_js(installed))

    def test_first_line_stops_at_cr_lf_or_crlf_only(self):
        # The installer decides whether a file is ours from this line, so it
        # must end at the same breaks the block editor uses and keep a BOM.
        first_line = firefox_user_js.first_line
        self.assertEqual("", first_line(""))
        self.assertEqual("", first_line("\nrest"))
        self.assertEqual("a", first_line("a"))
        self.assertEqual("a", first_line("a\nb"))
        self.assertEqual("a", first_line("a\r\nb"))
        self.assertEqual("a", first_line("a\rb"))
        self.assertEqual("a\x0bb c", first_line("a\x0bb c\nd"))
        self.assertEqual("\ufeffa", first_line("\ufeffa\nb"))

    def test_remove_is_repeatable_and_keeps_crlf(self):
        foreign = 'user_pref("a", 1);\r\n'
        text = (
            foreign
            + firefox_user_js.USER_JS_MARKER
            + "\r\n"
            + firefox_user_js.PREF_LINE
            + "\r\n"
        )
        once = firefox_user_js.remove_user_js(text)
        self.assertEqual(foreign, once)
        self.assertEqual(once, firefox_user_js.remove_user_js(once))

    def test_remove_drops_a_marker_with_no_pref_line_after_it(self):
        # The block is exactly the marker plus the pref line immediately after
        # it, so a marker whose next line is foreign must not take that line
        # with it: losing a user preference is worse than leaving a comment.
        foreign = 'user_pref("a", 1);\n'
        following = 'user_pref("b", 2);\n'
        text = foreign + firefox_user_js.USER_JS_MARKER + "\n" + following
        self.assertEqual(foreign + following, firefox_user_js.remove_user_js(text))

    def test_install_removes_every_earlier_block(self):
        # A hand-edited user.js can hold two copies of our block; the docstring
        # promises exactly one at the end, and every foreign line survives
        # once, whatever the number of earlier pairs.
        foreign = 'user_pref("a", 1);\n'
        block = (
            firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n"
        )
        updated = firefox_user_js.set_user_js(foreign + block + foreign + block)
        self.assertEqual(foreign + foreign + block, updated)

    def test_dominant_ending_tie_keeps_the_earliest_ending(self):
        # One CRLF and one LF line tie; the block must use the ending the file
        # opened with rather than sorting or taking the last one seen, and the
        # foreign lines must keep their own endings either way.
        foreign = 'user_pref("a", 1);\r\nuser_pref("b", 2);\n'
        self.assertEqual(
            foreign
            + firefox_user_js.USER_JS_MARKER
            + "\r\n"
            + firefox_user_js.PREF_LINE
            + "\r\n",
            firefox_user_js.set_user_js(foreign),
        )

    def test_foreign_lines_keep_lone_cr_endings(self):
        # A user.js written with classic-Mac lone-CR line endings keeps every
        # foreign line's CR, the unterminated last line gains the file's own
        # ending, and the appended block uses CR too.
        foreign = 'user_pref("a", 1);\ruser_pref("b", 2);'
        self.assertEqual(
            foreign
            + "\r"
            + firefox_user_js.USER_JS_MARKER
            + "\r"
            + firefox_user_js.PREF_LINE
            + "\r",
            firefox_user_js.set_user_js(foreign),
        )

    def test_remove_keeps_lone_cr_endings(self):
        foreign = 'user_pref("a", 1);\r'
        text = (
            foreign
            + firefox_user_js.USER_JS_MARKER
            + "\r"
            + firefox_user_js.PREF_LINE
            + "\r"
        )
        self.assertEqual(foreign, firefox_user_js.remove_user_js(text))
        self.assertEqual(foreign, firefox_user_js.remove_user_js(foreign))

    def test_only_cr_and_lf_end_a_line(self):
        # A foreign line carrying another Unicode line separator (VT, FF,
        # U+0085 or U+2028) is content, not an ending: splitting there would
        # move our block into the middle of that line and a removal could
        # leave an extra line break behind.
        foreign = 'user_pref("a", "x\u2028y\u0085z\v\f");'
        self.assertEqual(
            foreign
            + "\n"
            + firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n",
            firefox_user_js.set_user_js(foreign),
        )
        self.assertEqual(foreign + "\n", firefox_user_js.remove_user_js(foreign + "\n"))


class TestInstall(ProfileCase):
    def test_install_and_remove_through_a_symlinked_profile_directory(self):
        profile_link = self.root / "linked-profile"
        self.create_symlink(profile_link, self.profile, target_is_directory=True)
        foreign = 'user_pref("keep.me", "caf\u00e9");\r\n'
        _write(self.user_js_path(), foreign)

        result = self.run_tool("--profile", str(profile_link))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(profile_link.is_symlink())
        self.assertEqual(self.profile, profile_link.readlink())
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            self.sheet_path().read_bytes(),
        )
        self.assertEqual(
            foreign + firefox_user_js.USER_JS_MARKER + "\r\n"
            + firefox_user_js.PREF_LINE + "\r\n",
            _read(self.user_js_path()),
        )

        result = self.run_tool("--remove", "--profile", str(profile_link))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(profile_link.is_symlink())
        self.assertEqual(self.profile, profile_link.readlink())
        self.assertFalse(self.sheet_path().exists())
        self.assertEqual(foreign.encode("utf-8"), self.user_js_path().read_bytes())

    def test_install_copies_the_sheet_byte_for_byte_and_adds_one_block(self):
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            self.sheet_path().read_bytes(),
        )
        user_js = _read(self.user_js_path())
        self.assertEqual(
            firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n",
            user_js,
        )
        self.assertEqual(1, user_js.count(firefox_user_js.USER_JS_MARKER))

    def test_environment_profile_is_used_by_the_target(self):
        result = self.run_tool(
            env={"HOME": str(self.home), "FIREFOX_PROFILE": str(self.profile)}
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(self.sheet_path().is_file())

    def test_repeat_install_does_not_duplicate_the_block(self):
        self.assertEqual(0, self.run_tool("--profile", str(self.profile)).returncode)
        first = _read(self.user_js_path())
        self.assertEqual(
            0, self.run_tool("--profile", str(self.profile)).returncode
        )
        self.assertEqual(first, _read(self.user_js_path()))

    def test_an_empty_user_chrome_is_adopted(self):
        # An empty file holds nothing to preserve, so it is ours to fill
        # instead of being refused as a foreign sheet.
        self.sheet_path().parent.mkdir(parents=True)
        self.sheet_path().write_bytes(b"")
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            self.sheet_path().read_bytes(),
        )
        self.assertIn(
            firefox_user_js.USER_JS_MARKER, _read(self.user_js_path())
        )

    def test_foreign_user_chrome_is_refused_and_nothing_is_written(self):
        foreign = "/* my own chrome */\n.tabbrowser-tab { color: red; }\n"
        _write(self.sheet_path(), foreign)
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(1, result.returncode)
        self.assertIn(str(self.sheet_path()), result.stderr)
        self.assertEqual(foreign, _read(self.sheet_path()))
        self.assertFalse(self.user_js_path().exists())

    def test_install_refuses_a_symlinked_user_chrome_before_writing_anything(self):
        # A dotfile manager commonly makes userChrome.css a symlink to a file
        # it manages. Replacing that link with a regular file would detach the
        # profile from the file the user meant to edit.
        target = self.root / "dotfiles" / "userChrome.css"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"")
        link = self.sheet_path()
        link.parent.mkdir(parents=True)
        self.create_symlink(link, target)

        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {link}", result.stderr)
        self.assertIn("symbolic link", result.stderr)
        # The refused link and the file it names are untouched, and the
        # preference file was not written either.
        self.assertTrue(link.is_symlink())
        self.assertEqual(b"", target.read_bytes())
        self.assertFalse(self.user_js_path().exists())

    def test_install_refuses_a_symlinked_user_js_before_writing_anything(self):
        target = self.root / "dotfiles" / "user.js"
        target.parent.mkdir(parents=True)
        original = 'user_pref("keep.me", true);\n'
        target.write_text(original, encoding="utf-8")
        link = self.user_js_path()
        self.create_symlink(link, target)

        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {link}", result.stderr)
        self.assertIn("symbolic link", result.stderr)
        # The link and its target are untouched, and the sheet was not
        # written before the second path was refused.
        self.assertTrue(link.is_symlink())
        self.assertEqual(original, target.read_text(encoding="utf-8"))
        self.assertFalse(self.sheet_path().exists())

    def test_install_refuses_dangling_profile_links_before_writing_anything(self):
        for relative in ("chrome/userChrome.css", "user.js"):
            with self.subTest(path=relative):
                profile = self.root / relative.replace("/", "-")
                profile.mkdir()
                sheet = profile / "chrome" / "userChrome.css"
                js = profile / "user.js"
                sheet.parent.mkdir()
                link = profile / relative
                sibling = js if link == sheet else sheet
                original = (
                    b'user_pref("keep.me", true);\r\n'
                    if sibling == js
                    else (install_firefox.CSS_MARKER + "\r\n/* old sheet */\r\n").encode()
                )
                sibling.write_bytes(original)
                target = self.root / (profile.name + "-missing")
                self.create_symlink(link, target)

                result = self.run_tool("--profile", str(profile))

                self.assertEqual(2, result.returncode)
                self.assertIn(f"install_firefox: error: cannot write {link}", result.stderr)
                self.assertIn("symbolic link", result.stderr)
                self.assertTrue(link.is_symlink())
                self.assertEqual(target, link.readlink())
                self.assertFalse(target.exists())
                self.assertEqual(original, sibling.read_bytes())
                self.assertEqual({sheet, js, sheet.parent}, set(profile.rglob("*")))

    def test_a_bom_before_our_marker_keeps_the_sheet_ours(self):
        # A UTF-8 BOM is valid in CSS and some editors add one. It must not
        # make our marker-led sheet look foreign: the install replaces it with
        # the shipped sheet, and the removal deletes it.
        _write(
            self.sheet_path(),
            f"\ufeff{install_firefox.CSS_MARKER}\nbody {{}}\n",
        )
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            self.sheet_path().read_bytes(),
        )

    def test_an_uncreatable_chrome_directory_is_reported_by_path(self):
        # _apply promises a by-name "cannot create" error when the chrome
        # directory cannot be made, rather than a traceback. The directory
        # does not exist yet, so the earlier reads return None and the mkdir
        # is reached; fail only that call.
        with mock.patch.object(Path, "mkdir", side_effect=OSError("simulated failure")):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot create {self.sheet_path().parent}", result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_a_failed_user_js_write_is_reported_by_path(self):
        # A write failure must name the file that failed and stop the install.
        # The sheet is published first, so the failure must remove it again:
        # a failed install leaves neither half of the pair behind.
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.fail_write_to(self.user_js_path()),
        ):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_a_failed_user_js_write_restores_the_previous_sheet(self):
        # A repeat install over an earlier sheet of ours must not replace it
        # when the user.js write fails: the previous sheet is put back, not
        # deleted and not left as the new one.
        previous = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        _write(self.sheet_path(), previous)
        real_write = firefox_user_files.write_atomically

        def flaky_write(path, writer):
            if Path(path) == self.user_js_path():
                raise OSError("simulated failure")
            return real_write(path, writer)

        with mock.patch.object(firefox_user_files, "write_atomically", flaky_write):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
        self.assertEqual(previous, _read(self.sheet_path()))
        self.assertFalse(self.user_js_path().exists())

    def test_a_failed_user_js_write_keeps_a_block_that_was_already_installed(self):
        # A repeat install over an outdated sheet rewrites a user.js that
        # already holds our block unchanged. When that write fails, the
        # sheet goes back to its previous text and the block stays in place.
        first = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, first.returncode, first.stderr)
        installed_js = _read(self.user_js_path())
        previous_sheet = f"{install_firefox.CSS_MARKER}\n/* outdated sheet */\n"
        _write(self.sheet_path(), previous_sheet)
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.fail_write_to(self.user_js_path()),
        ):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
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
        self.assertFalse(self.user_js_path().exists())

    def test_an_interrupt_during_the_user_js_write_restores_the_previous_sheet(self):
        # An interrupt is not a ConfigError, but it must roll the published
        # sheet back all the same and then propagate instead of being
        # swallowed; otherwise Ctrl-C leaves a half-installed profile.
        previous = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        _write(self.sheet_path(), previous)
        real_write = firefox_user_files.write_atomically

        def interrupt_the_user_js_write(path, writer):
            if Path(path) == self.user_js_path():
                raise KeyboardInterrupt
            return real_write(path, writer)

        with mock.patch.object(
            firefox_user_files, "write_atomically", interrupt_the_user_js_write
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assertEqual(previous, _read(self.sheet_path()))
        self.assertFalse(self.user_js_path().exists())

    def test_an_interrupt_after_the_user_js_write_takes_effect_restores_it(self):
        # The user.js write can publish the preference block and then raise
        # before the call returns. The install must put the previous user.js
        # back as well as the sheet, so the pair is not left half-applied.
        previous_sheet = f"{install_firefox.CSS_MARKER}\n/* previous sheet */\n"
        previous_js = 'user_pref("keep.me", true);\n'
        _write(self.sheet_path(), previous_sheet)
        _write(self.user_js_path(), previous_js)
        real_write = firefox_user_files.write_atomically

        def interrupt_after_the_user_js_write(path, writer):
            if Path(path) == self.user_js_path():
                real_write(path, writer)
                raise KeyboardInterrupt
            return real_write(path, writer)

        with mock.patch.object(
            firefox_user_files, "write_atomically", interrupt_after_the_user_js_write
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assertEqual(previous_sheet, _read(self.sheet_path()))
        self.assertEqual(previous_js, _read(self.user_js_path()))

    def test_an_interrupt_after_a_created_user_js_is_published_removes_it(self):
        # A first install has no previous user.js, so when the write
        # publishes it and then raises, the rollback removes the file it
        # created instead of leaving the preference block behind.
        real_write = firefox_user_files.write_atomically

        def interrupt_after_the_user_js_write(path, writer):
            if Path(path) == self.user_js_path():
                real_write(path, writer)
                raise KeyboardInterrupt
            return real_write(path, writer)

        with mock.patch.object(
            firefox_user_files, "write_atomically", interrupt_after_the_user_js_write
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

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
        real_write = firefox_user_files.write_atomically

        def interrupt_after_the_sheet_write(path, writer):
            if Path(path) == self.sheet_path():
                real_write(path, writer)
                raise KeyboardInterrupt
            return real_write(path, writer)

        with mock.patch.object(
            firefox_user_files, "write_atomically", interrupt_after_the_sheet_write
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--profile", str(self.profile))
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_a_failed_new_sheet_restore_is_reported_with_the_original_error(self):
        # A first install has no previous sheet, so its rollback removes the
        # shipped sheet it published. If that unlink also fails, the error
        # must name both failures and the sheet that could not be removed
        # stays visible instead of the rollback failure being swallowed.
        real_write = firefox_user_files.write_atomically
        real_unlink = Path.unlink

        def flaky_write(path, writer):
            if Path(path) == self.user_js_path():
                raise OSError("simulated user.js failure")
            return real_write(path, writer)

        def flaky_unlink(path, *args, **kwargs):
            if Path(path) == self.sheet_path():
                raise OSError("simulated restore failure")
            return real_unlink(path, *args, **kwargs)

        with mock.patch.object(
            firefox_user_files, "write_atomically", flaky_write
        ), mock.patch.object(Path, "unlink", flaky_unlink):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
        self.assertIn(f"cannot restore {self.sheet_path()}", result.stderr)
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            self.sheet_path().read_bytes(),
        )
        self.assertFalse(self.user_js_path().exists())

    def test_a_failed_sheet_write_is_reported_by_path(self):
        # _apply publishes userChrome.css before user.js; a failure on that
        # first write must name the sheet and leave no user.js behind instead
        # of escaping as a traceback. The existing user.js write-failure test
        # pins the second publication; this pins the first.
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.fail_write_to(self.sheet_path()),
        ):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.sheet_path()}", result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_a_missing_shipped_sheet_is_reported_by_path(self):
        # _apply reads the shipped userChrome.css before touching the profile
        # and promises a by-name "cannot read" error rather than a traceback
        # when the source tree is incomplete. Point ROOT at a tree with no
        # theme/ directory; neither profile file may be written.
        with mock.patch.object(install_firefox, "ROOT", self.root):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        sheet = self.root / install_firefox.SHEET
        self.assertIn(f"cannot read {sheet}", result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_a_shipped_sheet_that_is_a_directory_is_reported_by_path(self):
        # The shared regular-file reader refuses a directory with a
        # ValueError; _apply must wrap that in the same by-name diagnostic.
        sheet = self.root / install_firefox.SHEET
        sheet.mkdir(parents=True)
        with mock.patch.object(install_firefox, "ROOT", self.root):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot read {sheet}", result.stderr)
        self.assertIn("not a regular file", result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertFalse(self.user_js_path().exists())

    def test_an_oversize_user_chrome_is_refused_by_name(self):
        # The existing sheet is read only to compare its first line, so a
        # multi-gigabyte file at that path must be refused by name after one
        # byte past the cap. Reading it whole would exhaust memory, and a
        # MemoryError is not an OSError, so it would escape as a traceback
        # instead of the documented exit 2. A sparse file keeps the test
        # cheap without changing what the reader sees.
        path = self.sheet_path()
        path.parent.mkdir(parents=True)
        with path.open("wb") as handle:
            handle.truncate(firefox_user_files.MAX_PROFILE_FILE_BYTES + 1)
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn(str(path), result.stderr)
        self.assertIn("larger than", result.stderr)
        self.assertEqual(
            firefox_user_files.MAX_PROFILE_FILE_BYTES + 1, path.stat().st_size
        )
        self.assertFalse(self.user_js_path().exists())

    def test_an_oversize_user_js_is_refused_by_name(self):
        # user.js goes through the same reader, so its read is bounded too;
        # no sheet may be published before the refusal.
        path = self.user_js_path()
        with path.open("wb") as handle:
            handle.truncate(firefox_user_files.MAX_PROFILE_FILE_BYTES + 1)
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn(str(path), result.stderr)
        self.assertIn("larger than", result.stderr)
        self.assertFalse(self.sheet_path().exists())

    def test_a_user_chrome_at_the_1_mib_cap_is_accepted(self):
        # One byte past the cap is refused; exactly 1 MiB is the accepted
        # boundary, so the documented cap is pinned by an actual file rather
        # than only by one past the private constant.
        cap = 1 << 20
        path = self.sheet_path()
        path.parent.mkdir(parents=True)
        first_line = (install_firefox.CSS_MARKER + "\n").encode("utf-8")
        path.write_bytes(first_line + b"x" * (cap - len(first_line)))
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            path.read_bytes(),
        )

    def test_an_install_that_would_grow_user_js_past_the_1_mib_cap_is_refused(
        self,
    ):
        # The reader accepts exactly 1 MiB, but appending our marker block to
        # a file at that boundary would make a user.js the reader itself
        # refuses; a successful install must never create that state, or
        # every later install and removal would exit 2 and strand the sheet.
        cap = 1 << 20
        path = self.user_js_path()
        original = b"x" * (cap - 1) + b"\n"
        path.write_bytes(original)
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn(str(path), result.stderr)
        self.assertIn("1048576-byte limit", result.stderr)
        self.assertEqual(original, path.read_bytes())
        self.assertFalse(self.sheet_path().exists())


class TestRemove(ProfileCase):
    def install(self):
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)

    def test_remove_deletes_our_sheet_and_block_and_keeps_the_directory(self):
        self.install()
        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertTrue(self.sheet_path().parent.is_dir())
        self.assertEqual("", _read(self.user_js_path()))

    def test_remove_is_repeatable(self):
        self.install()
        self.assertEqual(
            0, self.run_tool("--remove", "--profile", str(self.profile)).returncode
        )
        self.assertEqual(
            0, self.run_tool("--remove", "--profile", str(self.profile)).returncode
        )

    def test_remove_after_install_at_the_1_mib_user_js_boundary(self):
        # A user.js whose marker block keeps it at exactly 1 MiB is accepted
        # by the reader; installing must leave it readable so removal can
        # reverse the block and restore the foreign line.
        cap = 1 << 20
        block = (
            firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n"
        )
        foreign = "x" * (cap - len(block.encode("utf-8")) - 1) + "\n"
        _write(self.user_js_path(), foreign + block)
        self.assertEqual(cap, self.user_js_path().stat().st_size)
        self.install()
        self.assertEqual(cap, self.user_js_path().stat().st_size)
        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(foreign, _read(self.user_js_path()))

    def test_remove_deletes_a_bom_prefixed_our_sheet(self):
        sheet_text = f"\ufeff{install_firefox.CSS_MARKER}\nbody {{}}\n"
        _write(self.sheet_path(), sheet_text)
        block = (
            firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n"
        )
        _write(self.user_js_path(), block)

        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(self.sheet_path().exists())
        self.assertEqual("", _read(self.user_js_path()))

    def test_remove_keeps_a_foreign_sheet_and_foreign_pref(self):
        foreign_sheet = "/* my own chrome */\n"
        foreign_js = 'user_pref("tabs", 0);\r\n' + firefox_user_js.PREF_LINE + "\r\n"
        _write(self.sheet_path(), foreign_sheet)
        _write(self.user_js_path(), foreign_js)
        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(foreign_sheet, _read(self.sheet_path()))
        self.assertEqual(foreign_js, _read(self.user_js_path()))

    def test_remove_preserves_dangling_links_and_cleans_the_owned_sibling(self):
        for relative in ("chrome/userChrome.css", "user.js"):
            with self.subTest(path=relative):
                profile = self.root / relative.replace("/", "-")
                profile.mkdir()
                sheet = profile / "chrome" / "userChrome.css"
                js = profile / "user.js"
                sheet.parent.mkdir()
                link = profile / relative
                foreign = b'user_pref("keep.me", true);\r\n'
                if link == sheet:
                    block = (
                        firefox_user_js.USER_JS_MARKER + "\r\n"
                        + firefox_user_js.PREF_LINE + "\r\n"
                    ).encode("utf-8")
                    js.write_bytes(foreign + block)
                else:
                    _write(sheet, install_firefox.CSS_MARKER + "\n/* owned */\n")
                target = self.root / (profile.name + "-missing")
                self.create_symlink(link, target)

                result = self.run_tool("--remove", "--profile", str(profile))

                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual("", result.stderr)
                self.assertTrue(link.is_symlink())
                self.assertEqual(target, link.readlink())
                self.assertFalse(target.exists())
                if link == sheet:
                    self.assertEqual(foreign, js.read_bytes())
                    expected = {sheet.parent, sheet, js}
                else:
                    self.assertFalse(sheet.exists())
                    expected = {sheet.parent, js}
                self.assertEqual(expected, set(profile.rglob("*")))

    def test_remove_refuses_a_symlinked_sheet_before_deleting_anything(self):
        target = self.root / "dotfiles" / "userChrome.css"
        target.parent.mkdir(parents=True)
        css_text = f"{install_firefox.CSS_MARKER}\nbody {{}}\n"
        target.write_text(css_text, encoding="utf-8")
        link = self.sheet_path()
        link.parent.mkdir(parents=True)
        self.create_symlink(link, target)
        js_text = firefox_user_js.USER_JS_MARKER + "\n" + firefox_user_js.PREF_LINE + "\n"
        _write(self.user_js_path(), js_text)

        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {link}", result.stderr)
        self.assertIn("symbolic link", result.stderr)
        # The link and its target survive, and the preference block was not
        # cleared before the sheet was refused.
        self.assertTrue(link.is_symlink())
        self.assertEqual(css_text, target.read_text(encoding="utf-8"))
        self.assertEqual(js_text, _read(self.user_js_path()))

    def test_remove_refuses_a_symlinked_user_js_before_clearing_the_sheet(self):
        sheet_text = f"{install_firefox.CSS_MARKER}\nbody {{}}\n"
        _write(self.sheet_path(), sheet_text)
        target = self.root / "dotfiles" / "user.js"
        target.parent.mkdir(parents=True)
        js_text = firefox_user_js.USER_JS_MARKER + "\n" + firefox_user_js.PREF_LINE + "\n"
        target.write_text(js_text, encoding="utf-8")
        link = self.user_js_path()
        self.create_symlink(link, target)

        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {link}", result.stderr)
        self.assertIn("symbolic link", result.stderr)
        # The sheet was not deleted before the preference path was refused,
        # and the link's target keeps its marker block.
        self.assertEqual(sheet_text, _read(self.sheet_path()))
        self.assertTrue(link.is_symlink())
        self.assertEqual(js_text, target.read_text(encoding="utf-8"))

    def test_install_and_remove_preserve_foreign_lines_and_crlf(self):
        foreign = (
            'user_pref("browser.tabs.inTitlebar", 0);\r\n'
            'user_pref("browser.startup.homepage", "about:blank");'
        )
        _write(self.user_js_path(), foreign)
        self.install()
        installed = _read(self.user_js_path())
        self.assertTrue(installed.startswith(foreign + "\r\n"))
        self.assertEqual(1, installed.count(firefox_user_js.USER_JS_MARKER))
        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(foreign + "\r\n", _read(self.user_js_path()))

    def test_unreadable_user_js_is_reported_without_writing_the_sheet(self):
        self.user_js_path().mkdir()
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(str(self.user_js_path()), result.stderr)
        self.assertFalse(self.sheet_path().exists())

    def test_non_utf8_user_js_is_reported_without_writing_the_sheet(self):
        # The reader decodes user.js as UTF-8 and promises a by-name error for
        # invalid bytes, while the directory case above pins a non-regular
        # path. A user.js with a stray latin-1 byte must exit 2 naming the
        # file, and the install must stop before writing the sheet.
        self.user_js_path().write_bytes(b'user_pref("x", "\xff");\n')
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn("cannot read", result.stderr)
        self.assertIn(str(self.user_js_path()), result.stderr)
        self.assertFalse(self.sheet_path().exists())

    def test_an_unreadable_profile_file_is_reported_by_name(self):
        # read_profile_text opens both profile files through the shared regular-file
        # reader. A self-referential symlink makes that open fail with ELOOP,
        # an OSError, deterministically -- no dependence on file permissions
        # or on the test user. The directory and FIFO fixtures reach the
        # ValueError arm and the stray-byte fixture the decode arm, so this
        # pins the OSError arm that becomes a by-name ConfigError.
        for name in ("userChrome.css", "user.js"):
            with self.subTest(profile_file=name):
                profile = self.root / f"unreadable-{name}"
                profile.mkdir()
                sheet = profile / "chrome" / "userChrome.css"
                js = profile / "user.js"
                unreadable = sheet if name == "userChrome.css" else js
                untouched = js if name == "userChrome.css" else sheet
                unreadable.parent.mkdir(parents=True, exist_ok=True)
                self.create_symlink(unreadable, unreadable)
                result = self.run_tool("--profile", str(profile))
                self.assertEqual(2, result.returncode)
                self.assertIn(f"cannot read {unreadable}", result.stderr)
                self.assertIn(os.strerror(errno.ELOOP), result.stderr)
                self.assertFalse(untouched.exists())

    def test_a_fifo_at_either_profile_file_is_refused_without_blocking(self):
        # A plain read_bytes on a FIFO waits forever for a writer, so it would
        # stall `make install-firefox` instead of reporting the profile file.
        # Run the install in a child so a regression is a bounded timeout, and
        # refuse the pipe by name before the other profile file is written.
        snippet = (
            "import sys; from tools.install_firefox import main; "
            "sys.exit(main(sys.argv[1:]))"
        )
        files = (
            ("userChrome.css", Path("chrome") / "userChrome.css", Path("user.js")),
            ("user.js", Path("user.js"), Path("chrome") / "userChrome.css"),
        )
        for name, fifo, untouched in files:
            with self.subTest(profile_file=name):
                profile = self.root / f"fifo-{name}"
                profile.mkdir()
                fifo_path = profile / fifo
                make_fifo(self, fifo_path)
                with mock.patch.dict(
                    os.environ, {"HOME": str(self.home)}, clear=True
                ):
                    child = snippet_child.run(
                        [snippet, "--profile", str(profile)],
                        cwd=repo_root.ROOT,
                        timeout=10,
                    )
                assert_fifo_refused(self, child, fifo_path)
                self.assertFalse((profile / untouched).exists())

    def test_a_failed_user_js_write_during_removal_is_reported_by_path(self):
        # Removal rewrites user.js before it deletes the sheet. A failure on
        # that first step must name user.js and leave both files unchanged
        # instead of deleting the sheet and leaving a stale preference.
        self.install()
        before_js = _read(self.user_js_path())
        before_sheet = _read(self.sheet_path())
        with mock.patch.object(
            firefox_user_files,
            "write_atomically",
            self.fail_write_to(self.user_js_path()),
        ):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
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
        real_unlink = Path.unlink

        def interrupt_after_the_sheet_unlink(path, *args, **kwargs):
            if Path(path) == self.sheet_path():
                real_unlink(path, *args, **kwargs)
                raise KeyboardInterrupt
            return real_unlink(path, *args, **kwargs)

        with mock.patch.object(Path, "unlink", interrupt_after_the_sheet_unlink):
            with self.assertRaises(KeyboardInterrupt):
                self.run_tool("--remove", "--profile", str(self.profile))
        self.assertFalse(self.sheet_path().exists())
        self.assertEqual(
            firefox_user_js.remove_user_js(before_js), _read(self.user_js_path())
        )


if __name__ == "__main__":
    unittest.main()
