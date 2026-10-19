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
import unittest
import unittest.mock

from support import theme_install
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


class TestWhitespaceInInstallPaths(unittest.TestCase):
    """`make install`/`uninstall` must quote paths that contain whitespace.

    A `DESTDIR` or `XDG_DATA_HOME` with a space is legal; an unquoted recipe
    word-splits it, so the copy lands in the wrong place or fails outright.
    All seven artifacts must install and uninstall under a spaced root.
    """

    def _assert_round_trip(self, destdir):
        """Install all seven artifacts under *destdir*, then uninstall them."""
        assert_succeeded(self, theme_install.install(destdir))
        package = "org.macos8.desktop"
        scheme = theme_install.installed_color_scheme(destdir)
        kvantum = os.path.join(
            destdir,
            theme_install.XDG_DATA_HOME.lstrip("/"),
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
                theme_install.installed_plasma_dir(destdir, kind), package
            )
            for kind in ("look-and-feel", "desktoptheme")
        ]
        directories.append(theme_install.installed_aurorae_theme(destdir, package))
        directories.append(theme_install.installed_wallpaper(destdir, package))
        directories.append(theme_install.installed_icon_theme(destdir, package))
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
                f"XDG_DATA_HOME={theme_install.XDG_DATA_HOME}",
                f"FLOCK_TIMEOUT={value}",
            ),
            expected,
        )
        data_home = os.path.join(tmp, theme_install.XDG_DATA_HOME.lstrip("/"))
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
            tmp, extra=["FLOCK_TIMEOUT=00000000000000000001"]
        )
        assert_succeeded(self, result)
        scheme = theme_install.installed_color_scheme(tmp)
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
        scheme = theme_install.installed_color_scheme(tmp)
        self.assertTrue(os.path.isfile(scheme), scheme)
        data_home = os.path.join(tmp, theme_install.XDG_DATA_HOME.lstrip("/"))
        other_dirs = [
            theme_install.installed_plasma_dir(tmp, "look-and-feel"),
            theme_install.installed_plasma_dir(tmp, "desktoptheme"),
            theme_install.installed_aurorae_dir(tmp),
            theme_install.installed_wallpaper_dir(tmp),
            theme_install.installed_icons_dir(tmp),
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
                f"XDG_DATA_HOME={theme_install.XDG_DATA_HOME}",
            ],
            env=env,
        )
        assert_failed(self, result)
        self.assertIn(
            "INSTALL_PACKAGES must name at least one artifact family",
            result.stderr,
        )
        data_home = os.path.join(tmp, theme_install.XDG_DATA_HOME.lstrip("/"))
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
                f"XDG_DATA_HOME={theme_install.XDG_DATA_HOME}",
            ],
            env=env,
        )
        assert_failed(self, result)
        self.assertIn(
            "INSTALL_PACKAGES names unknown artifact families: colour-scheme",
            result.stderr,
        )
        self.assertIn("color-scheme", result.stderr)
        data_home = os.path.join(tmp, theme_install.XDG_DATA_HOME.lstrip("/"))
        self.assertFalse(os.path.exists(data_home), data_home)


if __name__ == "__main__":
    unittest.main()
