"""Tests for tools/install_firefox.py and the Firefox profile targets.

The tool runs in-process with ``HOME`` pointed at a temp root, so profile
resolution, the sheet copy, the ``user.js`` edit and the removal are pinned
without touching a real Firefox profile.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from support import containment
from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import run_main
from support.tmp_dir import make_tmp_dir
from tools import install_firefox

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
        return install_firefox.resolve_profile(explicit, env)

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

    def test_relative_named_profile_is_refused(self):
        with self.assertRaises(install_firefox.ConfigError) as caught:
            self.resolve("profile")
        self.assertIn("absolute", str(caught.exception))

    def test_missing_named_profile_is_refused(self):
        missing = self.root / "missing"
        with self.assertRaises(install_firefox.ConfigError) as caught:
            self.resolve(str(missing))
        self.assertIn(str(missing), str(caught.exception))

    def test_unusable_home_is_refused(self):
        with self.assertRaises(install_firefox.ConfigError) as caught:
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
        # by path. The reader's docstring promises a by-name ConfigError, but
        # only a directory standing in for user.js exercises the OSError
        # branch; without this a configparser exception would escape as a
        # traceback that never names the file to fix.
        self.firefox_root.mkdir(parents=True)
        profiles = self.firefox_root / "profiles.ini"
        profiles.write_text("Profiles/onlydefault\n", encoding="utf-8")
        with self.assertRaises(install_firefox.ConfigError) as caught:
            self.resolve()
        self.assertIn(f"cannot read {profiles}", str(caught.exception))

    def test_a_non_utf8_profiles_ini_is_reported_by_name(self):
        # Firefox's own ini files are UTF-8, but a stray byte must still name
        # the file rather than raise UnicodeDecodeError out of the tool.
        self.firefox_root.mkdir(parents=True)
        profiles = self.firefox_root / "profiles.ini"
        profiles.write_bytes(b"[Profile0]\nPath=\xff\n")
        with self.assertRaises(install_firefox.ConfigError) as caught:
            self.resolve()
        self.assertIn(f"cannot read {profiles}", str(caught.exception))

    def test_no_existing_candidate_names_the_root_and_candidates(self):
        self.firefox_root.mkdir(parents=True)
        _write(
            self.firefox_root / "profiles.ini",
            "[Profile0]\nPath=absent\n",
        )
        with self.assertRaises(install_firefox.ConfigError) as caught:
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
            install_firefox.USER_JS_MARKER,
        )
        self.assertEqual(
            'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);',
            install_firefox.PREF_LINE,
        )
        first_line = containment.read_bytes(SHEET_PATH, repo_root.ROOT).decode(
            "utf-8"
        ).splitlines()[0]
        self.assertEqual(install_firefox.CSS_MARKER, first_line)

    def test_new_file_gets_one_marker_and_pref_block(self):
        self.assertEqual(
            install_firefox.USER_JS_MARKER
            + "\n"
            + install_firefox.PREF_LINE
            + "\n",
            install_firefox.set_user_js(""),
        )

    def test_repeat_install_leaves_exactly_one_block(self):
        once = install_firefox.set_user_js("")
        self.assertEqual(once, install_firefox.set_user_js(once))
        self.assertEqual(1, once.count(install_firefox.USER_JS_MARKER))
        self.assertEqual(1, once.count(install_firefox.PREF_LINE))

    def test_foreign_lines_keep_their_crlf_and_terminated_last_line(self):
        foreign = (
            'user_pref("browser.tabs.inTitlebar", 0);\r\n'
            'user_pref("browser.startup.homepage", "about:blank");'
        )
        self.assertEqual(
            foreign
            + "\r\n"
            + install_firefox.USER_JS_MARKER
            + "\r\n"
            + install_firefox.PREF_LINE
            + "\r\n",
            install_firefox.set_user_js(foreign),
        )

    def test_foreign_setting_of_the_same_pref_survives_before_our_line(self):
        foreign = install_firefox.PREF_LINE + "\n"
        updated = install_firefox.set_user_js(foreign)
        self.assertEqual(2, updated.count(install_firefox.PREF_LINE))
        self.assertTrue(updated.startswith(foreign))
        self.assertTrue(
            updated.endswith(
                install_firefox.USER_JS_MARKER
                + "\n"
                + install_firefox.PREF_LINE
                + "\n"
            )
        )

    def test_remove_deletes_only_the_marker_pair(self):
        foreign = 'user_pref("a", 1);\n'
        text = (
            foreign
            + install_firefox.USER_JS_MARKER
            + "\n"
            + install_firefox.PREF_LINE
            + "\n"
        )
        self.assertEqual(foreign, install_firefox.remove_user_js(text))

    def test_remove_leaves_a_foreign_pref_and_missing_final_newline(self):
        foreign = install_firefox.PREF_LINE + "\nuser_pref(\"last\", 1);"
        self.assertEqual(foreign, install_firefox.remove_user_js(foreign))
        self.assertEqual(
            'user_pref("last", 1);',
            install_firefox.remove_user_js('user_pref("last", 1);'),
        )

    def test_remove_is_repeatable_and_keeps_crlf(self):
        foreign = 'user_pref("a", 1);\r\n'
        text = (
            foreign
            + install_firefox.USER_JS_MARKER
            + "\r\n"
            + install_firefox.PREF_LINE
            + "\r\n"
        )
        once = install_firefox.remove_user_js(text)
        self.assertEqual(foreign, once)
        self.assertEqual(once, install_firefox.remove_user_js(once))


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
            install_firefox.USER_JS_MARKER
            + "\n"
            + install_firefox.PREF_LINE
            + "\n",
            user_js,
        )
        self.assertEqual(1, user_js.count(install_firefox.USER_JS_MARKER))

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
        foreign_js = 'user_pref("tabs", 0);\r\n' + install_firefox.PREF_LINE + "\r\n"
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
        self.assertEqual(1, installed.count(install_firefox.USER_JS_MARKER))
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
        # invalid bytes, but the directory case above is the only pinned read
        # failure. A user.js with a stray latin-1 byte must exit 2 naming the
        # file, and the install must stop before writing the sheet.
        self.user_js_path().write_bytes(b'user_pref("x", "\xff");\n')
        result = self.run_tool("--profile", str(self.profile))
        self.assertEqual(2, result.returncode)
        self.assertIn("cannot read", result.stderr)
        self.assertIn(str(self.user_js_path()), result.stderr)
        self.assertFalse(self.sheet_path().exists())

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
