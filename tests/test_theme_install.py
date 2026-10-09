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
                self.assertIn("HOME is not an absolute path", result.stderr)

    def test_relative_home_without_an_absolute_data_home_is_refused(self):
        # A relative HOME makes the fallback a relative path, so `install -d`
        # would create a tree under the current directory (and `uninstall`
        # delete from it). DESTDIR is rooted at a temp dir so a guard that
        # wrongly let the run through cannot write into the checkout; the
        # guard reads HOME, not DESTDIR, so the refusal still exercises the
        # relative-HOME branch.
        env = dict(os.environ, HOME="relative")
        env.pop("XDG_DATA_HOME", None)
        with tempfile.TemporaryDirectory() as tmp:
            for target in ("install", "uninstall"):
                with self.subTest(target=target):
                    result = theme_install.run_make(
                        [target, f"DESTDIR={tmp}"], env=env
                    )
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(
                        "HOME is not an absolute path", result.stderr
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
        with tempfile.TemporaryDirectory() as tmp:
            for target in ("install", "uninstall"):
                with self.subTest(target=target):
                    result = theme_install.run_make(
                        [
                            target,
                            f"DESTDIR={tmp}",
                            f"XDG_DATA_HOME={theme_install.XDG_DATA_HOME}",
                            f"FLOCK_TIMEOUT={value}",
                        ]
                    )
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(
                        "FLOCK_TIMEOUT must be a non-negative integer "
                        "number of seconds",
                        result.stderr,
                    )
                    self.assertIn(f"'{value}'", result.stderr)
                    if extra is not None:
                        self.assertIn(extra, result.stderr)
            data_home = os.path.join(
                tmp, theme_install.XDG_DATA_HOME.lstrip("/")
            )
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

    def test_leading_zeros_do_not_make_a_small_value_look_too_large(self):
        # A valid value written with leading zeros ("000...0001") has more
        # than 19 characters but a value of 1. The length check must strip the
        # zeros before calling it too large; flock parses the value as 1
        # second, so the install must proceed and install the scheme.
        with tempfile.TemporaryDirectory() as tmp:
            result = theme_install.install(
                tmp, extra=["FLOCK_TIMEOUT=00000000000000000001"]
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            scheme = theme_install.installed_color_scheme(tmp)
            self.assertTrue(os.path.isfile(scheme), result.stderr)


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


class TestPythonInterpreter(unittest.TestCase):
    """`make check` must refuse a PYTHON that make would read as a flag.

    PYTHON is a make variable a caller can set from the environment or the
    command line, but `?=` keeps an empty environment value. An empty value
    leaves the `check` recipe line starting with `-`, which make reads as its
    ignore-errors prefix: it runs `m -m unittest ...`, fails with status 127,
    and exits 0 -- a green run that executed no tests. A leading dash (after
    any leading whitespace) has the same effect. The guard must refuse with a
    diagnostic naming PYTHON instead of reporting success. The child never
    reaches the suite: a refused recipe stops at the guard, so each case is
    fast even if the guard regresses (the swallowed command fails at once).
    """

    def _assert_refused(self, *, command_line=None, environment=None):
        env = dict(os.environ)
        env.pop("PYTHON", None)
        env.pop("MAKEFLAGS", None)
        args = ["check"]
        if command_line is not None:
            args.append(f"PYTHON={command_line}")
        if environment is not None:
            env["PYTHON"] = environment
        result = theme_install.run_make(args, env=env)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("PYTHON must name an interpreter", result.stderr)

    def test_empty_from_the_command_line_is_refused(self):
        self._assert_refused(command_line="")

    def test_empty_from_the_environment_is_refused(self):
        self._assert_refused(environment="")

    def test_leading_dash_is_refused(self):
        self._assert_refused(command_line="-m")

    def test_whitespace_only_is_refused(self):
        self._assert_refused(environment=" ")


class TestHelp(unittest.TestCase):
    """`make help` lists every public target and tunable-variable default.

    The Makefile documents each target and variable in a comment, but a
    contributor does not read those; the help target is the discoverable
    index. The public targets are the `.PHONY` names other than the
    `_`-prefixed internals, so reading that line catches a target added
    without a help line instead of pinning a hand-copied list here. Each
    `?=` variable's help line names its literal default, and that default is
    derived from the Makefile rather than copied here, so changing one
    without the other fails.
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

    def _tunable_defaults(self):
        """Return the literal defaults of the Makefile's `?=` variables.

        A `?=` assignment is the tunable-variable contract: the help target
        documents each one and states its default. Deriving the default from
        the Makefile keeps this test from pinning a second copy that could
        itself drift; only the literal right-hand side is read, so a value
        built from other variables (none today) is out of scope.
        """
        makefile = os.path.join(theme_install.ROOT, "Makefile")
        defaults = {}
        with open(makefile, encoding="utf-8") as handle:
            for line in handle:
                match = re.match(
                    r"([A-Za-z_][A-Za-z0-9_]*)\s*\?=(.*)$", line
                )
                if match:
                    # A `#` starts a Make comment, so an inline note after the
                    # value is not part of it; strip it before comparing.
                    value = match.group(2).split("#", 1)[0].strip()
                    if value:
                        defaults[match.group(1)] = value
        return defaults

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

    def test_names_every_tunable_variable_default(self):
        """Each `?=` variable's help line names the Makefile's own default.

        The help text states a default per variable, and a default changed in
        the Makefile but not the help (or the reverse) would mislead a
        contributor who reads the index. The expected value comes from the
        Makefile, so the two are compared instead of pinning a third copy.
        """
        lines = self._output().splitlines()
        defaults = self._tunable_defaults()
        self.assertTrue(defaults, "Makefile has no `?=` variables to check")
        for name, default in defaults.items():
            with self.subTest(variable=name):
                named = [
                    line
                    for line in lines
                    if line.strip().startswith(f"{name}=")
                ]
                self.assertTrue(named, f"help does not list variable {name!r}")
                self.assertTrue(
                    any(f"(default {default})" in line for line in named),
                    f"help does not name the {name} default {default!r}",
                )


if __name__ == "__main__":
    unittest.main()
