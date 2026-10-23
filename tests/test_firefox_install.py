"""Tests for the Firefox profile install and its two helper modules.

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
from tools import firefox_profile, firefox_user_js, install_firefox

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
        with self.assertRaises(firefox_profile.ConfigError) as caught:
            self.resolve("profile")
        self.assertIn("absolute", str(caught.exception))

    def test_missing_named_profile_is_refused(self):
        missing = self.root / "missing"
        with self.assertRaises(firefox_profile.ConfigError) as caught:
            self.resolve(str(missing))
        self.assertIn(str(missing), str(caught.exception))

    def test_unusable_home_is_refused(self):
        with self.assertRaises(firefox_profile.ConfigError) as caught:
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
        with self.assertRaises(firefox_profile.ConfigError) as caught:
            self.resolve()
        self.assertIn(f"cannot read {profiles}", str(caught.exception))

    def test_a_non_utf8_profiles_ini_is_reported_by_name(self):
        # Firefox's own ini files are UTF-8, but a stray byte must still name
        # the file rather than raise UnicodeDecodeError out of the tool.
        self.firefox_root.mkdir(parents=True)
        profiles = self.firefox_root / "profiles.ini"
        profiles.write_bytes(b"[Profile0]\nPath=\xff\n")
        with self.assertRaises(firefox_profile.ConfigError) as caught:
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
        try:
            profiles.symlink_to(profiles)
        except OSError:
            self.skipTest("cannot create a symlink on this platform")
        with self.assertRaises(firefox_profile.ConfigError) as caught:
            self.resolve()
        self.assertIn(f"cannot read {profiles}", str(caught.exception))

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
        with self.assertRaises(firefox_profile.ConfigError) as caught:
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


class TestInstall(ProfileCase):
    def run_tool(self, *args, env=None):
        if env is None:
            env = {"HOME": str(self.home)}
        with mock.patch.dict(os.environ, env, clear=True):
            return run_main(install_firefox.main, install_firefox.TOOL, args)

    def sheet_path(self, profile=None):
        return (profile or self.profile) / "chrome" / "userChrome.css"

    def user_js_path(self, profile=None):
        return (profile or self.profile) / "user.js"

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

    def test_foreign_user_chrome_is_refused_and_nothing_is_written(self):
        foreign = "/* my own chrome */\n.tabbrowser-tab { color: red; }\n"
        _write(self.sheet_path(), foreign)
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(1, result.returncode)
        self.assertIn(str(self.sheet_path()), result.stderr)
        self.assertEqual(foreign, _read(self.sheet_path()))
        self.assertFalse(self.user_js_path().exists())

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
        # A write failure must name the file that failed and stop the install:
        # the sheet is published first, but user.js is left absent.
        real_write = install_firefox.write_atomically

        def flaky_write(path, writer):
            if Path(path) == self.user_js_path():
                raise OSError("simulated failure")
            return real_write(path, writer)

        with mock.patch.object(install_firefox, "write_atomically", flaky_write):
            result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot write {self.user_js_path()}", result.stderr)
        self.assertEqual(
            containment.read_bytes(SHEET_PATH, repo_root.ROOT),
            self.sheet_path().read_bytes(),
        )
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


class TestRemove(ProfileCase):
    def run_tool(self, *args):
        with mock.patch.dict(os.environ, {"HOME": str(self.home)}, clear=True):
            return run_main(install_firefox.main, install_firefox.TOOL, args)

    def sheet_path(self):
        return self.profile / "chrome" / "userChrome.css"

    def user_js_path(self):
        return self.profile / "user.js"

    def install(self):
        with mock.patch.dict(
            os.environ, {"HOME": str(self.home)}, clear=True
        ):
            result = run_main(
                install_firefox.main,
                install_firefox.TOOL,
                ("--profile", str(self.profile)),
            )
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

    def test_remove_keeps_a_foreign_sheet_and_foreign_pref(self):
        foreign_sheet = "/* my own chrome */\n"
        foreign_js = 'user_pref("tabs", 0);\r\n' + firefox_user_js.PREF_LINE + "\r\n"
        _write(self.sheet_path(), foreign_sheet)
        _write(self.user_js_path(), foreign_js)
        result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(foreign_sheet, _read(self.sheet_path()))
        self.assertEqual(foreign_js, _read(self.user_js_path()))

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
        # _read_text opens both profile files through the shared regular-file
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
                try:
                    unreadable.symlink_to(unreadable)
                except OSError:
                    self.skipTest("cannot create a symlink on this platform")
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

    def test_a_failed_sheet_unlink_is_reported_by_path(self):
        # _remove promises a by-name "cannot remove" error when our sheet
        # cannot be deleted, leaving the sheet in place rather than crashing.
        self.install()
        sheet = containment.read_bytes(self.sheet_path(), repo_root.ROOT)
        with mock.patch.object(Path, "unlink", side_effect=OSError("simulated failure")):
            result = self.run_tool("--remove", "--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn(f"cannot remove {self.sheet_path()}", result.stderr)
        self.assertEqual(sheet, containment.read_bytes(self.sheet_path(), repo_root.ROOT))


if __name__ == "__main__":
    unittest.main()
