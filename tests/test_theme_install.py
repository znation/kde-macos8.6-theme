"""`make install`/`uninstall` behaviour: paths, XDG resolution and the lock.

`theme_install.run_make` drives `make` through the suite's timeout runner in
`process_runner`, so a `make` that never exits raises
`subprocess.TimeoutExpired` instead of stalling `make check`. These tests pin
that the Makefile survives a `DESTDIR` or `XDG_DATA_HOME` that contains
whitespace (its recipe words are quoted), that an empty or relative data home
falls back to the XDG default, and that an invalid `FLOCK_TIMEOUT` is refused
before the lock is taken. `make check`'s variables live in
``test_make_check.py`` and `make help` in ``test_make_help.py``.
"""

import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from support import installed_paths, repo_root, theme_install
from support.symlink_fixtures import symlinked_repo
from support.install_failure_cases import FailedInstallPreservesPackage
from support.process_assertions import assert_failed, assert_succeeded
from support.tmp_dir import make_tmp_dir


def _assert_both_targets_refused(case, env, args, expected):
    """Run `install` and `uninstall` with *env*; both must refuse.

    *args* carries the make variable assignments for each target, and *expected*
    names each substring the diagnostic must carry. `install` and `uninstall`
    share their guards, so a test that drove only one target would miss a guard
    wired to the other.
    """
    for target in ("install", "uninstall"):
        with case.subTest(target=target):
            result = theme_install.run_make([target, *args], env=env)
            assert_failed(case, result)
            for substring in expected:
                case.assertIn(substring, result.stderr)


class TestMakeEnv(unittest.TestCase):
    """`make_env` drops `MAKEFLAGS` and each named variable, and nothing else.

    The child `make` re-reads a caller's `make VAR=...` from `MAKEFLAGS`, so a
    test that pins a make variable must drop both forms; a sibling variable it
    did not name must survive so the child environment stays representative.
    """

    def test_removes_makeflags_and_each_named_variable(self):
        with unittest.mock.patch.dict(
            os.environ,
            {
                "MAKEFLAGS": "-- check",
                "CHECK_PATTERN": "test_x.py",
                "KEEP_ME": "yes",
            },
        ):
            env = theme_install.make_env("CHECK_PATTERN")
        self.assertNotIn("MAKEFLAGS", env)
        self.assertNotIn("CHECK_PATTERN", env)
        self.assertEqual(env["KEEP_ME"], "yes")

    def test_removes_makeflags_even_without_a_named_variable(self):
        with unittest.mock.patch.dict(os.environ, {"MAKEFLAGS": "-s"}):
            env = theme_install.make_env()
        self.assertNotIn("MAKEFLAGS", env)


class TestInstalledDestdirSharing(unittest.TestCase):
    """`installed_destdir` installs once per class and copies that tree."""

    def setUp(self):
        # The helper caches on the test class; each test here starts a new
        # class-level cache so one test's install cannot satisfy another.
        self.addCleanup(self._forget_templates)
        self._forget_templates()

    def _forget_templates(self):
        if "_installed_templates" in type(self).__dict__:
            delattr(type(self), "_installed_templates")

    @staticmethod
    def _fake_install(calls, results):
        def install(destdir, **kwargs):
            calls.append(kwargs)
            if not results:
                raise AssertionError("install called more often than expected")
            result = results.pop(0)
            if result.returncode == 0:
                (Path(destdir) / "marker").write_text(
                    "installed", encoding="utf-8"
                )
            return result

        return install

    def _succeeded(self):
        return unittest.mock.Mock(returncode=0, stdout="", stderr="")

    def test_repeated_calls_install_once_and_copy_the_tree(self):
        calls = []
        with unittest.mock.patch.object(
            theme_install, "install", self._fake_install(calls, [self._succeeded()])
        ):
            with theme_install.installed_destdir(
                self, packages="color-scheme"
            ) as first:
                self.assertEqual(
                    "installed",
                    (Path(first) / "marker").read_text(encoding="utf-8"),
                )
            with theme_install.installed_destdir(
                self, packages="color-scheme"
            ) as second:
                self.assertEqual(
                    "installed",
                    (Path(second) / "marker").read_text(encoding="utf-8"),
                )
        self.assertEqual([{"packages": "color-scheme"}], calls)
        self.assertNotEqual(first, second)

    def test_each_package_family_gets_its_own_template(self):
        calls = []
        results = [self._succeeded(), self._succeeded()]
        with unittest.mock.patch.object(
            theme_install, "install", self._fake_install(calls, results)
        ):
            with theme_install.installed_destdir(
                self, packages="color-scheme"
            ):
                pass
            with theme_install.installed_destdir(self, packages="kvantum"):
                pass
        self.assertEqual(
            [{"packages": "color-scheme"}, {"packages": "kvantum"}], calls
        )

    def test_a_failed_install_is_not_reused(self):
        calls = []
        failed = unittest.mock.Mock(
            returncode=1, stdout="", stderr="template install failed"
        )
        results = [failed, self._succeeded()]
        with unittest.mock.patch.object(
            theme_install, "install", self._fake_install(calls, results)
        ):
            with self.assertRaises(AssertionError):
                with theme_install.installed_destdir(
                    self, packages="color-scheme"
                ):
                    pass
            with theme_install.installed_destdir(
                self, packages="color-scheme"
            ) as destdir:
                self.assertTrue((Path(destdir) / "marker").is_file())
        self.assertEqual(2, len(calls))


class TestFailedInstallSharing(unittest.TestCase):
    """`FailedInstallPreservesPackage` installs once per class and copies."""

    def test_install_ok_installs_once_and_copies_per_test(self):
        calls = []

        def fake_install(destdir, **kwargs):
            calls.append(kwargs)
            (Path(destdir) / "marker").write_text(
                "installed", encoding="utf-8"
            )
            return unittest.mock.Mock(returncode=0, stdout="", stderr="")

        class Case(FailedInstallPreservesPackage, unittest.TestCase):
            MAKE_PACKAGES = "color-scheme"

            def runTest(self):
                pass

            def _snapshot(self, tmp):
                return (str(tmp), "metadata", "good")

        case = Case()
        self.addCleanup(case.doCleanups)
        self.addCleanup(Case.doClassCleanups)
        with unittest.mock.patch.object(
            theme_install, "install", fake_install
        ):
            first = case._install_ok()
            second = case._install_ok()

        self.assertEqual([{"packages": "color-scheme"}], calls)
        self.assertNotEqual(first[0], second[0])
        for result in (first, second):
            self.assertTrue((Path(result[0]) / "marker").is_file())


class TestWhitespaceInInstallPaths(unittest.TestCase):
    """`make install`/`uninstall` must quote paths that contain whitespace.

    A `DESTDIR` or `XDG_DATA_HOME` with a space is legal; an unquoted recipe
    word-splits it, so the copy lands in the wrong place or fails outright.
    All eight artifacts must install and uninstall under a spaced root.
    """

    def _assert_round_trip(self, destdir):
        """Install all eight artifacts under *destdir*, then uninstall them."""
        assert_succeeded(self, theme_install.install(destdir))
        package = "org.macos8.desktop"
        scheme = installed_paths.installed_color_scheme(destdir)
        kvantum = os.path.join(
            destdir,
            installed_paths.XDG_DATA_HOME.lstrip("/"),
            "themes",
            package,
            "Kvantum",
        )
        kvantum_files = [
            os.path.join(kvantum, package + ".kvconfig"),
            os.path.join(kvantum, package + ".svg"),
        ]
        directories = [
            os.path.join(
                installed_paths.installed_plasma_dir(destdir, kind), package
            )
            for kind in ("look-and-feel", "desktoptheme")
        ]
        directories.append(installed_paths.installed_aurorae_theme(destdir, package))
        directories.append(installed_paths.installed_wallpaper(destdir, package))
        directories.append(installed_paths.installed_icon_theme(destdir, package))
        directories.append(installed_paths.installed_font_package(destdir, package))
        self.assertTrue(os.path.isfile(scheme), scheme)
        for path in kvantum_files:
            self.assertTrue(os.path.isfile(path), path)
        for path in directories:
            self.assertTrue(os.path.isdir(path), path)

        assert_succeeded(self, theme_install.uninstall(destdir))
        for path in [scheme, *kvantum_files, *directories]:
            self.assertFalse(os.path.exists(path), path)

    def test_install_and_uninstall_under_a_path_with_a_space(self):
        tmp = make_tmp_dir(self)
        self._assert_round_trip(os.path.join(tmp, "spaced root"))

    def test_install_and_uninstall_under_a_path_with_an_apostrophe(self):
        # The staging/old/trap words are shell-quoted; a single-quoted word
        # holding the path ended at the apostrophe and the recipe died with a
        # shell syntax error, e.g. under a home directory named `O'Brien`.
        tmp = make_tmp_dir(self)
        self._assert_round_trip(os.path.join(tmp, "O'Brien's root"))


class TestXdgDataHomeDefault(unittest.TestCase):
    """An empty or relative $XDG_DATA_HOME must fall back to the XDG default.

    The XDG Base Directory spec resolves $XDG_DATA_HOME to $HOME/.local/share
    when it is unset or empty, and treats a relative value as invalid and
    ignores it; README's Installing section documents the same default. `?=`
    alone kept an empty environment value, so `make install` targeted
    $(DESTDIR) itself (or, with no DESTDIR, ran `install -d ""`). Drive
    `make -n` with a controlled environment and read the data-home path the
    recipe would use.
    """

    HOME = "/tmp/tumwater-test-home"

    def _install_dry_run(self, xdg):
        """Return the `make -n install` output for *xdg* in the environment."""
        env = dict(os.environ, HOME=self.HOME, XDG_DATA_HOME=xdg)
        result = theme_install.run_make(["-n", "install"], env=env)
        assert_succeeded(self, result)
        return result.stdout

    def test_empty_falls_back_to_the_xdg_default(self):
        out = self._install_dry_run("")
        self.assertIn(f'install -d "{self.HOME}/.local/share"', out)

    def test_relative_falls_back_to_the_xdg_default(self):
        out = self._install_dry_run("relative/share")
        self.assertIn(f'install -d "{self.HOME}/.local/share"', out)
        self.assertNotIn("relative/share", out)

    def test_absolute_is_kept(self):
        out = self._install_dry_run("/custom/share")
        self.assertIn('install -d "/custom/share"', out)

    def test_unset_home_without_an_absolute_data_home_is_refused(self):
        # The fallback is $HOME/.local/share, so with HOME unset it becomes
        # /.local/share at the filesystem root. Both targets must refuse
        # rather than write there or delete from it. XDG_DATA_HOME is dropped
        # from the environment (not passed on the command line), so the
        # fallback -- and the guard -- actually run.
        env = dict(os.environ)
        env.pop("HOME", None)
        env.pop("XDG_DATA_HOME", None)
        _assert_both_targets_refused(self, env, (), ("HOME is unset",))

    def test_relative_home_without_an_absolute_data_home_is_refused(self):
        # A relative HOME makes the fallback a relative path, so `install -d`
        # would create a tree under the current directory (and `uninstall`
        # delete from it). DESTDIR is rooted at a temp dir so a guard that
        # wrongly let the run through cannot write into the checkout; the
        # guard reads HOME, not DESTDIR, so the refusal still exercises the
        # relative-HOME branch.
        env = dict(os.environ, HOME="relative")
        env.pop("XDG_DATA_HOME", None)
        tmp = make_tmp_dir(self)
        _assert_both_targets_refused(
            self,
            env,
            (f"DESTDIR={tmp}",),
            (
                "HOME is not an absolute path",
                # The guard names the offending HOME so a contributor can
                # see which value it read, not just that one was bad.
                "('relative')",
            ),
        )

    def test_guard_names_the_relative_data_home_it_refused(self):
        # XDG_DATA_HOME_ENV is exported so the guard can name the raw value
        # the caller gave; without the export the recipe shell sees no such
        # variable and the diagnostic shows an empty ('') value instead.
        env = dict(os.environ, HOME="relative", XDG_DATA_HOME="relative/share")
        env.pop("XDG_DATA_HOME_ENV", None)
        tmp = make_tmp_dir(self)
        result = theme_install.run_make(["install", f"DESTDIR={tmp}"], env=env)
        assert_failed(self, result)
        self.assertIn(
            "XDG_DATA_HOME is not an absolute path ('relative/share')",
            result.stderr,
        )


class TestFlockTimeout(unittest.TestCase):
    """An invalid FLOCK_TIMEOUT must be refused before the lock is taken.

    FLOCK_TIMEOUT is a make variable a caller can set, but `flock -w` accepts
    only a non-negative integer number of seconds that fits its 64-bit signed
    timer. An empty, non-numeric, or too-large value otherwise reaches flock,
    which fails with its own "invalid timeout value" or "cannot set up timer"
    message that does not name the variable -- after `install` has already
    created the data home. The guard must name FLOCK_TIMEOUT and leave the
    tree untouched. `install` and `uninstall` share the guard.

    The guard must also accept every value flock accepts: leading zeros are
    characters, not magnitude, so a small value written with them must not be
    refused as too large.
    """

    def _assert_refused(self, value, extra=None):
        expected = [
            "FLOCK_TIMEOUT must be a non-negative integer number of seconds",
            f"'{value}'",
        ]
        if extra is not None:
            expected.append(extra)
        tmp = make_tmp_dir(self)
        _assert_both_targets_refused(
            self,
            None,
            (
                f"DESTDIR={tmp}",
                f"XDG_DATA_HOME={installed_paths.XDG_DATA_HOME}",
                f"FLOCK_TIMEOUT={value}",
            ),
            expected,
        )
        data_home = os.path.join(tmp, installed_paths.XDG_DATA_HOME.lstrip("/"))
        self.assertFalse(os.path.exists(data_home), data_home)

    def test_empty_is_refused_before_creating_the_data_home(self):
        self._assert_refused("")

    def test_non_numeric_is_refused_before_creating_the_data_home(self):
        self._assert_refused("60s")

    def test_above_the_timer_limit_is_refused_before_creating_the_data_home(self):
        # `flock -w` stores the timeout in a signed 64-bit timer field, so a
        # value above 2**63 - 1 reaches it and fails with its own "cannot set
        # up timer: Invalid argument" after the data home exists. The guard
        # must reject it and name the limit.
        self._assert_refused(
            "9223372036854775808",
            "at most 9223372036854775807",
        )

    def test_a_value_longer_than_the_timer_limit_is_refused_by_length(self):
        # After leading zeros are stripped, a value of more than 19 digits
        # cannot fit flock's signed 64-bit timer whatever its digits, so the
        # guard refuses it by length before comparing the digits. Without that
        # length clause a 20-digit value slips past the 19-digit comparison,
        # reaches flock, and fails with flock's own message after the data
        # home exists.
        self._assert_refused(
            "99999999999999999999",
            "at most 9223372036854775807",
        )

    def test_leading_zeros_do_not_make_a_small_value_look_too_large(self):
        # A valid value written with leading zeros ("000...0001") has more
        # than 19 characters but a value of 1. The length check must strip the
        # zeros before calling it too large; flock parses the value as 1
        # second, so the install must proceed and install the scheme.
        tmp = str(make_tmp_dir(self))
        result = theme_install.install(
            tmp,
            extra=["FLOCK_TIMEOUT=00000000000000000001"],
            packages="color-scheme",
        )
        assert_succeeded(self, result)
        scheme = installed_paths.installed_color_scheme(tmp)
        self.assertTrue(os.path.isfile(scheme), result.stderr)


class TestInstallPackages(unittest.TestCase):
    """`INSTALL_PACKAGES` must narrow `_install` to the named families.

    Each artifact suite passes `packages=` so its install copies only its own
    family. That filter is invisible to those suites: each asserts only its
    own artifact, which an unfiltered install would also produce. Pin it here
    by installing one family and asserting every other family's directory is
    absent.
    """

    def test_one_family_installs_only_that_family(self):
        tmp = str(make_tmp_dir(self))
        assert_succeeded(
            self,
            theme_install.install(tmp, packages="color-scheme"),
        )
        scheme = installed_paths.installed_color_scheme(tmp)
        self.assertTrue(os.path.isfile(scheme), scheme)
        data_home = os.path.join(tmp, installed_paths.XDG_DATA_HOME.lstrip("/"))
        other_dirs = [
            installed_paths.installed_plasma_dir(tmp, "look-and-feel"),
            installed_paths.installed_plasma_dir(tmp, "desktoptheme"),
            installed_paths.installed_aurorae_dir(tmp),
            installed_paths.installed_wallpaper_dir(tmp),
            installed_paths.installed_icons_dir(tmp),
            installed_paths.installed_fonts_dir(tmp),
            os.path.join(data_home, "themes", "org.macos8.desktop", "Kvantum"),
        ]
        for path in other_dirs:
            self.assertFalse(os.path.exists(path), path)


class TestInstallPackagesGuard(unittest.TestCase):
    """An empty `INSTALL_PACKAGES` must be refused, not install nothing.

    `?=` keeps an empty value from the environment, and `_install`'s guards
    then filter every family out: `make install` creates the data home, copies
    nothing, and exits 0. Refuse it with a diagnostic naming INSTALL_PACKAGES,
    before the data home exists.
    """

    def test_empty_is_refused_before_creating_the_data_home(self):
        tmp = make_tmp_dir(self)
        env = theme_install.make_env("INSTALL_PACKAGES")
        env["INSTALL_PACKAGES"] = ""
        result = theme_install.run_make(
            [
                "install",
                f"DESTDIR={tmp}",
                f"XDG_DATA_HOME={installed_paths.XDG_DATA_HOME}",
            ],
            env=env,
        )
        assert_failed(self, result)
        self.assertIn(
            "INSTALL_PACKAGES must name at least one artifact family",
            result.stderr,
        )
        data_home = os.path.join(tmp, installed_paths.XDG_DATA_HOME.lstrip("/"))
        self.assertFalse(os.path.exists(data_home), data_home)

    def test_unknown_family_is_refused_before_creating_the_data_home(self):
        # A typo'd family name filters every real family out, so without a
        # guard `make install` would create the data home, copy nothing and
        # exit 0 -- the same green install the empty-value guard refuses.
        tmp = make_tmp_dir(self)
        env = theme_install.make_env("INSTALL_PACKAGES")
        env["INSTALL_PACKAGES"] = "colour-scheme"
        result = theme_install.run_make(
            [
                "install",
                f"DESTDIR={tmp}",
                f"XDG_DATA_HOME={installed_paths.XDG_DATA_HOME}",
            ],
            env=env,
        )
        assert_failed(self, result)
        self.assertIn(
            "INSTALL_PACKAGES names unknown artifact families: colour-scheme",
            result.stderr,
        )
        self.assertIn("color-scheme", result.stderr)
        data_home = os.path.join(tmp, installed_paths.XDG_DATA_HOME.lstrip("/"))
        self.assertFalse(os.path.exists(data_home), data_home)

    def test_an_unknown_family_after_a_known_one_is_still_refused(self):
        # The guard must check every word, not just the first: a known family
        # first (`color-scheme`) must not mask a typo after it (`bogus`). A
        # guard that inspected only `$1` would pass
        # test_unknown_family_is_refused_before_creating_the_data_home -- there
        # the single word is the typo -- and install the known family while
        # quietly dropping the unknown one.
        tmp = make_tmp_dir(self)
        env = theme_install.make_env("INSTALL_PACKAGES")
        env["INSTALL_PACKAGES"] = "color-scheme bogus"
        result = theme_install.run_make(
            [
                "install",
                f"DESTDIR={tmp}",
                f"XDG_DATA_HOME={installed_paths.XDG_DATA_HOME}",
            ],
            env=env,
        )
        assert_failed(self, result)
        # Only the unknown word is named as unknown; the known family may
        # appear only in the trailing "known families" list.
        self.assertIn(
            "INSTALL_PACKAGES names unknown artifact families: bogus;",
            result.stderr,
        )
        data_home = os.path.join(tmp, installed_paths.XDG_DATA_HOME.lstrip("/"))
        self.assertFalse(os.path.exists(data_home), data_home)

    def test_a_glob_shaped_family_is_reported_literally_not_expanded(self):
        # `require_install_packages` opens with `set -f`, so a glob-shaped
        # INSTALL_PACKAGES value is not expanded by the shell before the guard
        # reads it; the diagnostic must name the literal value the caller
        # passed. Without `set -f`, `*.md` would expand to the repository's
        # markdown files (README.md and the backlog) and the guard would report
        # those names instead, sending the reader after files they never named.
        tmp = make_tmp_dir(self)
        env = theme_install.make_env("INSTALL_PACKAGES")
        env["INSTALL_PACKAGES"] = "*.md"
        result = theme_install.run_make(
            [
                "install",
                f"DESTDIR={tmp}",
                f"XDG_DATA_HOME={installed_paths.XDG_DATA_HOME}",
            ],
            env=env,
        )
        assert_failed(self, result)
        self.assertIn(
            "INSTALL_PACKAGES names unknown artifact families: *.md;",
            result.stderr,
        )
        data_home = os.path.join(tmp, installed_paths.XDG_DATA_HOME.lstrip("/"))
        self.assertFalse(os.path.exists(data_home), data_home)


class TestAssertFilesIdentical(unittest.TestCase):
    """The install byte-comparison must refuse a source symlink that escapes.

    ``assert_files_identical`` reads a contributor-supplied package file and
    compares it with the installed copy; ``assertEqual`` echoes both byte
    strings on a mismatch, so a checked-in symlink at the source that resolves
    outside the repository must be refused before it is opened. The copy in the
    throwaway DESTDIR is not contributor-supplied and is read as before.
    """

    def test_rejects_a_source_symlink_that_escapes_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root, source = symlinked_repo(
                tmp, "theme/icons/icon.svg", b"PRIVATE-SECRET-BYTES"
            )
            target = tmp / "installed.svg"
            target.write_bytes(b"a different installed copy")
            with unittest.mock.patch.object(repo_root, "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    theme_install.assert_files_identical(self, source, target)
        self.assertIn(str(source), str(caught.exception))
        self.assertNotIn("PRIVATE-SECRET-BYTES", str(caught.exception))

    def test_reads_a_source_symlink_that_stays_within_the_repository(self):
        # The guard must refuse only escapes, not a legitimate package file
        # reached through a symlink inside the repository.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root, source = symlinked_repo(
                tmp,
                "theme/icons/alias.svg",
                b"same bytes",
                target="theme/icons/icon.svg",
            )
            target = tmp / "installed.svg"
            target.write_bytes(b"same bytes")
            with unittest.mock.patch.object(repo_root, "ROOT", root):
                theme_install.assert_files_identical(self, source, target)


if __name__ == "__main__":
    unittest.main()
