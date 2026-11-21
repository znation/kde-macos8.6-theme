"""`make install`/`uninstall` behaviour: paths, symlink guards and packages.

`theme_install.run_make` drives `make` through the suite's timeout runner in
`process_runner`, so a `make` that never exits raises
`subprocess.TimeoutExpired` instead of stalling `make check`. These tests pin
that the Makefile survives a `DESTDIR` or `XDG_DATA_HOME` that contains
whitespace (its recipe words are quoted). The data-home fallback and the
`FLOCK_TIMEOUT` guard live in ``test_theme_install_guards.py``. The make-level refusal of a value carrying shell
syntax or a control byte lives in ``test_make_refusals.py`` and ``test_make_refusals_tools.py``, `make check`'s
variables in ``test_make_check.py`` and `make help` in ``test_make_help.py``.
The pins of the shared install helpers in ``support/theme_install.py`` live in
``test_theme_install_support.py``.
"""

import os
import unittest
import unittest.mock

from support import installed_paths, theme_install
from support.process_assertions import assert_failed, assert_succeeded
from support.tmp_dir import make_tmp_dir
from tools.gtk_user_files import GTK4_CSS_MARKER


def _assert_install_packages_refused(case, value, *expected):
    """Run `make install` with *value* and assert the guard refuses it.

    The `INSTALL_PACKAGES` guard tests share this setup: the run must fail
    before the data home exists, so a refused install leaves no tree behind.
    *expected* names each substring the diagnostic must carry. Each of the
    four tests in `TestInstallPackagesGuard` calls this once.
    """
    tmp = make_tmp_dir(case)
    env = theme_install.make_env("INSTALL_PACKAGES")
    env["INSTALL_PACKAGES"] = value
    result = theme_install.run_make(
        [
            "install",
            f"DESTDIR={tmp}",
            f"XDG_DATA_HOME={installed_paths.XDG_DATA_HOME}",
        ],
        env=env,
    )
    assert_failed(case, result)
    for substring in expected:
        case.assertIn(substring, result.stderr)
    data_home = os.path.join(tmp, installed_paths.XDG_DATA_HOME.lstrip("/"))
    case.assertFalse(os.path.exists(data_home), data_home)


class TestThemeSymlinkGuard(unittest.TestCase):
    """`make install` must refuse a symlink under the theme package tree.

    The package files are contributor-supplied and git stores symlinks. The
    single-file installs use `install`, which follows a source symlink, so one
    at the color scheme, a Kvantum file or a GTK file would copy a private
    file's bytes or stream a device into the installed theme; the directory
    installs use `cp -r`, which preserves a link into the user's data home
    where a later reader follows it. The guard runs before the data home is
    created, so a refused install leaves no tree behind.
    """

    def test_a_symlink_under_the_theme_tree_is_refused_before_the_data_home(self):
        tmp = make_tmp_dir(self)
        private = make_tmp_dir(self) / "private"
        private.write_text("PRIVATE-SECRET-BYTES", encoding="utf-8")
        # The color scheme is installed with `install -Dm644`, which follows a
        # source symlink; without the guard this link's target bytes would land
        # in the installed scheme.
        source = tmp / "MacOS8.colors"
        source.symlink_to(private)
        destdir = tmp / "dest"
        env = theme_install.make_env("THEME_ROOT", "COLOR_SCHEME")
        result = theme_install.run_make(
            [
                "install",
                f"DESTDIR={destdir}",
                f"XDG_DATA_HOME={installed_paths.XDG_DATA_HOME}",
                f"THEME_ROOT={tmp}",
                f"COLOR_SCHEME={source}",
                "INSTALL_PACKAGES=color-scheme",
            ],
            env=env,
        )
        assert_failed(self, result)
        self.assertIn(
            "refusing a symlink in the theme package tree", result.stderr
        )
        self.assertNotIn("PRIVATE-SECRET-BYTES", result.stderr)
        self.assertFalse(
            destdir.exists(), "install created DESTDIR before refusing"
        )

    def test_a_symlinked_theme_root_is_refused_before_the_data_home(self):
        """A `THEME_ROOT` that is itself a link is refused by the guard.

        A checkout can replace `theme/` with a link (for example to another
        checkout); the guard checks the root with `-L` before it scans for
        links, and refuses before the data home is created, so neither the
        link nor the directory it names is installed.
        """
        tmp = make_tmp_dir(self)
        real = tmp / "real-theme"
        real.mkdir()
        (real / "MacOS8.colors").write_text(
            "PRIVATE-SECRET-BYTES", encoding="utf-8"
        )
        theme_root = tmp / "theme"
        theme_root.symlink_to(real, target_is_directory=True)
        destdir = tmp / "dest"
        env = theme_install.make_env("THEME_ROOT", "COLOR_SCHEME")
        result = theme_install.run_make(
            [
                "install",
                f"DESTDIR={destdir}",
                f"XDG_DATA_HOME={installed_paths.XDG_DATA_HOME}",
                f"THEME_ROOT={theme_root}",
                f"COLOR_SCHEME={theme_root / 'MacOS8.colors'}",
                "INSTALL_PACKAGES=color-scheme",
            ],
            env=env,
        )
        assert_failed(self, result)
        self.assertIn(
            "refusing a symlink in the theme package tree", result.stderr
        )
        self.assertFalse(
            destdir.exists(), "install created DESTDIR before refusing"
        )


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
    All nine artifacts must install and uninstall under a spaced root.
    """

    def _assert_round_trip(self, destdir):
        """Install all nine artifacts under *destdir*, then uninstall them."""
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
        gtk_dir = installed_paths.installed_gtk_theme(destdir)
        gtk_files = [
            os.path.join(gtk_dir, "index.theme"),
            os.path.join(gtk_dir, "gtk-3.0", "gtk.css"),
            os.path.join(gtk_dir, "gtk-4.0", "gtk.css"),
        ]
        self.assertTrue(os.path.isfile(scheme), scheme)
        for path in kvantum_files + gtk_files:
            self.assertTrue(os.path.isfile(path), path)
        for path in directories:
            self.assertTrue(os.path.isdir(path), path)

        assert_succeeded(self, theme_install.uninstall(destdir))
        for path in [scheme, *kvantum_files, *gtk_files, *directories]:
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



class TestUninstallSymlinkParents(unittest.TestCase):
    """Uninstall must not follow planted links in its destination tree."""

    def test_gtk_subdirectory_link_cannot_redirect_removal_outside_data_home(self):
        tmp = make_tmp_dir(self)
        data_home = tmp / "data"
        outside = tmp / "outside"
        outside.mkdir()
        sentinel = outside / "gtk.css"
        sentinel.write_text("foreign stylesheet", encoding="utf-8")
        gtk3 = data_home / "themes/org.macos8.desktop/gtk-3.0"
        gtk3.parent.mkdir(parents=True)
        gtk3.symlink_to(outside, target_is_directory=True)
        env = theme_install.make_env("XDG_DATA_HOME")
        env["XDG_DATA_HOME"] = str(data_home)

        result = theme_install.run_make(["uninstall"], env=env)

        assert_failed(self, result)
        self.assertIn("refusing a symlink in the install destination", result.stderr)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "foreign stylesheet")


class TestShellUnsafeXdgConfigHome(unittest.TestCase):
    """An `XDG_CONFIG_HOME` carrying a control byte is refused unecheod.

    `uninstall`'s trailing diagnostics read the config home through the
    recipe shell (`config_home="$${XDG_CONFIG_HOME:-}"`) and, when a
    selection still names our GTK theme after the data-home removals, echo
    the settings.ini and gtk.css paths under it on stderr. Make interpolates
    nothing of the value, so the metacharacter refusal cannot see it:
    shell syntax in the value stays inside the recipe's double quotes and is
    inert, but the echo still pastes the raw value into the terminal, like
    the guard echoes the other guarded values. Before the parse-time
    refusal, an escape byte in the variable rode that echo into the
    operator's terminal; the byte must now reach neither stdout nor stderr.
    """

    def test_an_escape_byte_in_XDG_CONFIG_HOME_is_refused_before_uninstall_echoes_it(self):
        # The realistic path: a marked gtk.css survives the uninstall under
        # an escape-carrying config home, so the data-home removals leave the
        # diagnostic block something real to echo. The refusal must fire at
        # make parse time, naming the variable, and echo nothing of it.
        tmp = make_tmp_dir(self)
        config_home = tmp / "cfg\x1b(2Jhome"
        (config_home / "gtk-4.0").mkdir(parents=True)
        (config_home / "gtk-4.0" / "gtk.css").write_text(
            GTK4_CSS_MARKER + "\n"
        )
        env = theme_install.make_env("XDG_CONFIG_HOME", "XDG_DATA_HOME")
        env["XDG_CONFIG_HOME"] = str(config_home)
        env["XDG_DATA_HOME"] = str(tmp / "data home")
        result = theme_install.run_make(["uninstall"], env=env)
        assert_failed(self, result)
        self.assertIn(
            "XDG_CONFIG_HOME contains a control character", result.stderr
        )
        output = result.stdout + result.stderr
        self.assertNotIn("\x1b", output)


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
            os.path.join(
                installed_paths.installed_gtk_theme(tmp), "index.theme"
            ),
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
        _assert_install_packages_refused(
            self, "", "INSTALL_PACKAGES must name at least one artifact family"
        )

    def test_unknown_family_is_refused_before_creating_the_data_home(self):
        # A typo'd family name filters every real family out, so without a
        # guard `make install` would create the data home, copy nothing and
        # exit 0 -- the same green install the empty-value guard refuses.
        _assert_install_packages_refused(
            self,
            "colour-scheme",
            "INSTALL_PACKAGES names unknown artifact families: colour-scheme",
            "color-scheme",
        )

    def test_an_unknown_family_after_a_known_one_is_still_refused(self):
        # The guard must check every word, not just the first: a known family
        # first (`color-scheme`) must not mask a typo after it (`bogus`). A
        # guard that inspected only `$1` would pass
        # test_unknown_family_is_refused_before_creating_the_data_home -- there
        # the single word is the typo -- and install the known family while
        # quietly dropping the unknown one.
        # Only the unknown word is named as unknown; the known family may
        # appear only in the trailing "known families" list.
        _assert_install_packages_refused(
            self,
            "color-scheme bogus",
            "INSTALL_PACKAGES names unknown artifact families: bogus;",
        )

    def test_a_glob_shaped_family_is_reported_literally_not_expanded(self):
        # `require_install_packages` opens with `set -f`, so a glob-shaped
        # INSTALL_PACKAGES value is not expanded by the shell before the guard
        # reads it; the diagnostic must name the literal value the caller
        # passed. Without `set -f`, `*.md` would expand to the repository's
        # markdown files (README.md and the backlog) and the guard would report
        # those names instead, sending the reader after files they never named.
        _assert_install_packages_refused(
            self,
            "*.md",
            "INSTALL_PACKAGES names unknown artifact families: *.md;",
        )


if __name__ == "__main__":
    unittest.main()
