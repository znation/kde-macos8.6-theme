"""The install harness's Makefile paths and the Makefile's own behavior.

`theme_install.run_make` drives `make` through the suite's timeout runner in
`process_runner`, so a `make` that never exits raises
`subprocess.TimeoutExpired` instead of stalling `make check`. These tests pin
that the Makefile survives a `DESTDIR` or `XDG_DATA_HOME` that contains
whitespace (its recipe words are quoted), that `make check` accepts a narrowing
glob, and that `make help` indexes the public targets the README names.
"""

import os
import re
import tempfile
import unittest

import theme_install


class TestWhitespaceInInstallPaths(unittest.TestCase):
    """`make install`/`uninstall` must quote paths that contain whitespace.

    A `DESTDIR` or `XDG_DATA_HOME` with a space is legal; an unquoted recipe
    word-splits it, so the copy lands in the wrong place or fails outright.
    All three artifacts must install and uninstall under a spaced root.
    """

    def test_install_and_uninstall_under_a_path_with_a_space(self):
        with tempfile.TemporaryDirectory() as tmp:
            destdir = os.path.join(tmp, "spaced root")
            result = theme_install.install(destdir)
            self.assertEqual(result.returncode, 0, result.stderr)

            scheme = theme_install.installed_color_scheme(destdir)
            self.assertTrue(os.path.isfile(scheme), scheme)
            lnf = os.path.join(
                theme_install.installed_plasma_dir(destdir, "look-and-feel"),
                "org.macos8.desktop",
            )
            self.assertTrue(os.path.isdir(lnf), lnf)
            dtheme = os.path.join(
                theme_install.installed_plasma_dir(destdir, "desktoptheme"),
                "org.macos8.desktop",
            )
            self.assertTrue(os.path.isdir(dtheme), dtheme)

            removed = theme_install.uninstall(destdir)
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(os.path.exists(scheme), scheme)
            self.assertFalse(os.path.exists(lnf), lnf)
            self.assertFalse(os.path.exists(dtheme), dtheme)


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
        self.assertEqual(result.returncode, 0, result.stderr)
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
        for target in ("install", "uninstall"):
            with self.subTest(target=target):
                result = theme_install.run_make([target], env=env)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("HOME is unset", result.stderr)


class TestCheckPattern(unittest.TestCase):
    """`make check` defaults to the whole suite and accepts a narrowing glob.

    The suite is slow (the install tests spawn `make`), so a focused run should
    not have to retype `python3 -m unittest discover -s tests ...`. `make -n`
    prints the recipe without running it, so the wiring is checked without a
    nested suite run.
    """

    def _dry_run(self, *extra):
        # A caller's `make check CHECK_PATTERN=...` reaches the recipe both as
        # a CHECK_PATTERN environment variable and as a command-line variable
        # definition inside MAKEFLAGS; the child `make` re-reads the latter and
        # would otherwise use the ambient pattern for the default case. Drop
        # both so each case pins the pattern it means to; a command-line
        # assignment passed below still overrides the Makefile default.
        env = dict(os.environ)
        env.pop("CHECK_PATTERN", None)
        env.pop("MAKEFLAGS", None)
        result = theme_install.run_make(["-n", "check", *extra], env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_default_pattern_runs_every_test_module(self):
        self.assertIn("-p 'test*.py'", self._dry_run())

    def test_pattern_narrows_the_discovered_modules(self):
        self.assertIn(
            "-p 'test_byteops.py'",
            self._dry_run("CHECK_PATTERN=test_byteops.py"),
        )


class TestHelp(unittest.TestCase):
    """`make help` lists every public target and the CHECK_PATTERN default.

    The Makefile documents each target and variable in a comment, but a
    contributor does not read those; the help target is the discoverable
    index. The public targets are the `.PHONY` names other than the
    `_`-prefixed internals, so reading that line catches a target added
    without a help line instead of pinning a hand-copied list here.
    """

    def _output(self):
        env = dict(os.environ)
        env.pop("CHECK_PATTERN", None)
        env.pop("MAKEFLAGS", None)
        result = theme_install.run_captured(
            ["make", "help"],
            cwd=theme_install.ROOT,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def _public_targets(self):
        """Return the `.PHONY` targets other than the `_`-prefixed internals."""
        makefile = os.path.join(theme_install.ROOT, "Makefile")
        with open(makefile, encoding="utf-8") as handle:
            phony = next(
                line
                for line in handle
                if line.startswith(".PHONY:")
            )
        return [
            name
            for name in phony.split(":", 1)[1].split()
            if not name.startswith("_")
        ]

    def test_lists_every_public_target(self):
        lines = self._output().splitlines()
        for target in self._public_targets():
            with self.subTest(target=target):
                self.assertTrue(
                    any(line.startswith(f"  {target} ") for line in lines),
                    f"help does not list target {target!r}",
                )

    def test_readme_names_every_public_target(self):
        r"""README is the entry point, so it must name every public target.

        `make help` is only discoverable if a contributor already knows it
        exists, so the README has to mention each target; a target added to
        the Makefile without a README line otherwise stays invisible. The
        `(?![-\w])` guard keeps a shorter target from matching as a prefix of
        a longer one (`check` inside `check-references`).
        """
        readme = os.path.join(theme_install.ROOT, "README.md")
        with open(readme, encoding="utf-8") as handle:
            text = handle.read()
        for target in self._public_targets():
            with self.subTest(target=target):
                self.assertRegex(
                    text,
                    rf"make {re.escape(target)}(?![-\w])",
                    f"README does not name target {target!r}",
                )

    def test_names_check_pattern_default(self):
        self.assertTrue(
            any(
                "CHECK_PATTERN" in line and "test*.py" in line
                for line in self._output().splitlines()
            ),
            "help does not name the CHECK_PATTERN default",
        )


if __name__ == "__main__":
    unittest.main()
