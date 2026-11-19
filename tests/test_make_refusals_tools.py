"""The Makefile's parse-time refusals of the tool and check-narrowing variables.

`PYTHON`, `CHECK_PATTERN`, `INSTALL_PACKAGES`, `CHECK_TESTS` and
`CHECK_PARALLEL` are pasted into unquoted recipe words or into `make check`'s
own guard lines, not into double-quoted install paths. A value carrying recipe
shell syntax or a control byte is refused at make level before any recipe runs,
so each class pins the refusal and that the shell never executes (`CANARY`
probes). The path, profile, color-scheme, theme-root and render-output refusals
stay in ``test_make_refusals.py``, which also pins the control-byte refusals.
"""

import os
import unittest

import test_make_refusals as refusals
from support import installed_paths, repo_root, theme_install
from support.process_assertions import assert_failed, assert_succeeded
from support.tmp_dir import make_tmp_dir


class TestShellUnsafePython(unittest.TestCase):
    """A `PYTHON` carrying recipe-shell syntax at an unquoted spot is refused.

    Recipes expand `$(PYTHON)` unquoted -- a value may carry arguments
    (`/usr/bin/python3 -X dev`), so the words cannot be double-quoted -- and
    at an unquoted position a wider character set is shell syntax than
    inside double quotes: beyond the four the double-quoted guard refuses,
    an apostrophe, a semicolon, a pipe, an ampersand, a parenthesis, a
    redirection character or a newline would run the words after it as
    shell commands instead of naming an interpreter. The make-level guard
    refuses such a value before any recipe of any target runs; a space
    stays legal because the multi-word form is the documented one.
    """

    # The unquoted hostiles beyond the double-quoted four
    # (`refusals.TestShellUnsafeInstallPaths.HOSTILES`): the make-argument form and
    # the text the diagnostic must echo back. A `$` arrives doubled in the
    # make argument, as HOSTILES there documents; the double-quoted four are
    # driven in test_the_double_quoted_hostiles_are_refused too.
    EXTRA_HOSTILES = (
        ("'", "x'; y'", "x'; y'"),
        (";", "x; y", "x; y"),
        ("|", "x|y", "x|y"),
        ("&", "x&y", "x&y"),
        ("(", "x(y", "x(y"),
        (")", "x)y", "x)y"),
        ("<", "x<y", "x<y"),
        (">", "x>y", "x>y"),
    )

    def _assert_refused(self, make_value, shown_value):
        """Dry-run `render` with *make_value*; make must refuse at parse time.

        A dry run is enough because the guard is a make-level `$(error)`: if
        it ever stops firing, make exits 0 here and the assertion fails.
        """
        result = theme_install.run_make(
            ["-n", "render", f"PYTHON={make_value}"]
        )
        assert_failed(self, result)
        self.assertIn("PYTHON contains a shell metacharacter", result.stderr)
        self.assertIn(shown_value, result.stderr)
        return result

    def test_the_double_quoted_hostiles_are_refused(self):
        # A value pasted into `set -- "$(PYTHON)"` (require_python) and into
        # the double-quoted echo of require_python_version needs the same
        # four refusals as the path variables.
        for char, make_value, shown_value in refusals.TestShellUnsafeInstallPaths.HOSTILES:
            with self.subTest(char=char):
                self._assert_refused(make_value, shown_value)

    def test_each_unquoted_metacharacter_is_refused(self):
        for char, make_value, shown_value in self.EXTRA_HOSTILES:
            with self.subTest(char=char):
                self._assert_refused(make_value, shown_value)

    def test_a_newline_is_refused(self):
        # An unquoted newline is a command separator, and make carries a
        # command-line assignment's newline into the value verbatim. The
        # value carries no other refused character, so the newline branch
        # itself must fire; make reports it as the word `newline`.
        result = self._assert_refused("py\nx", "py\nx")
        self.assertIn("('newline'", result.stderr)

    def test_a_hostile_value_runs_no_shell(self):
        """A refused PYTHON must not run any of its injected words.

        Without the guard, `make render PYTHON='python3; touch <canary>; :'`
        created the canary from the version probe line itself, before the
        main recipe line even ran. The refusal must come first and leave no
        canary.
        """
        tmp = make_tmp_dir(self)
        canary = tmp / "injected"
        result = theme_install.run_make(
            [
                "render",
                f"PYTHON=python3; touch '{canary}'; :",
            ]
        )
        assert_failed(self, result)
        self.assertIn("PYTHON contains a shell metacharacter", result.stderr)
        self.assertFalse(canary.exists(), tmp)

    def test_make_function_text_in_PYTHON_is_refused_without_evaluation(self):
        # The refusal's own diagnostic echoes the value, so it must echo the
        # raw text: expanding `$(PYTHON)` there would run the very function
        # the guard is refusing.
        tmp = make_tmp_dir(self)
        canary = tmp / "make-function-executed"
        env = theme_install.make_env("PYTHON")
        env["PYTHON"] = f"$(shell touch {canary})"
        result = theme_install.run_captured(
            ["make", "-n", "help"], cwd=str(repo_root.ROOT), env=env
        )
        assert_failed(self, result)
        self.assertIn("PYTHON contains a shell metacharacter", result.stderr)
        self.assertFalse(canary.exists(), canary)

    def test_a_multi_word_interpreter_stays_legal(self):
        # The documented form: an interpreter command with arguments. A dry
        # run must succeed and hand both words to the recipe unquoted.
        result = theme_install.run_make(
            ["-n", "render", "PYTHON=/usr/bin/python3 -X dev"]
        )
        assert_succeeded(self, result)
        self.assertIn(
            "/usr/bin/python3 -X dev tools/render_surface.py", result.stdout
        )


class TestShellUnsafeCheckPattern(unittest.TestCase):
    """A `CHECK_PATTERN` carrying recipe-shell syntax is refused at make level.

    `check` pastes CHECK_PATTERN into double-quoted recipe words (the glob
    guard's `set -- "$(CHECK_PATTERN)"` and `find ... -name "$value"`), where
    a double quote, `$`, a backtick or a backslash would run the words after
    it as shell commands before the guard's own "matches no test module"
    refusal runs; into the single-quoted `-p '$(CHECK_PATTERN)'` word, where
    an apostrophe would close that quoting instead. The make-level guard
    refuses both before any recipe of any target runs, so a refused `check`
    must not run the suite (or a canary command) at all. The
    `TestShellUnsafeInstallPaths` class shapes these tests after the path
    guards; the metacharacter diagnostic reuses `refuse_unsafe_value`.
    """

    def _assert_refused(self, make_value, shown_value):
        """Dry-run `check` with *make_value*; make must refuse at parse time.

        A dry run is enough because the guard is a make-level `$(error)`: if
        it ever stops firing, make proceeds to print the `check` recipe and
        this run exits 0, failing the assertion.
        """
        result = theme_install.run_make(
            ["-n", "check", f"CHECK_PATTERN={make_value}"],
            env=theme_install.make_env("CHECK_PATTERN", "CHECK_TESTS"),
        )
        assert_failed(self, result)
        self.assertIn("CHECK_PATTERN contains", result.stderr)
        self.assertIn(shown_value, result.stderr)

    def test_each_metacharacter_is_refused(self):
        # The value is expanded into double-quoted recipe words, where each
        # of the four characters below is shell syntax. Same values as
        # refusals.TestShellUnsafeInstallPaths.HOSTILES (`$` arrives doubled in the
        # make argument, the other three pass through verbatim).
        for char, make_value, shown_value in refusals.TestShellUnsafeInstallPaths.HOSTILES:
            with self.subTest(char=char):
                self._assert_refused(make_value, shown_value)

    def test_an_apostrophe_is_refused(self):
        # An apostrophe is inert inside the double-quoted words above, but
        # `check` also pastes the value into `-p '$(CHECK_PATTERN)'` before
        # the interpreter runs, where the apostrophe closes that quoting.
        # The guard refuses it at make level with its own diagnostic naming
        # that single-quoted word.
        self._assert_refused(
            "test_byteops.py'; echo",
            "test_byteops.py'; echo",
        )

    def test_a_refused_pattern_runs_no_shell(self):
        """A refused CHECK_PATTERN must not run any of its injected words.

        Without the guard, `make check CHECK_PATTERN='testX"; touch
        <canary>; echo "'` ran the touch inside the glob guard's own `find`
        subshell, before that guard's refusal. The refusal must come first
        and leave no canary; this case runs `check` for real (not dry) for
        the same reason.
        """
        tmp = make_tmp_dir(self)
        canary = tmp / "injected"
        result = theme_install.run_make(
            ["check", f"CHECK_PATTERN=testX\"; touch '{canary}'; echo \""],
            env=theme_install.make_env("CHECK_PATTERN", "CHECK_TESTS"),
        )
        assert_failed(self, result)
        self.assertIn(
            "CHECK_PATTERN contains a shell metacharacter", result.stderr
        )
        self.assertFalse(canary.exists(), "canary created; the guard escaped")


class TestShellUnsafeInstallPackages(unittest.TestCase):
    """An `INSTALL_PACKAGES` carrying recipe-shell syntax is refused.

    `require_install_packages` expands INSTALL_PACKAGES unquoted (its value
    is a list of family names), so beyond the double-quoted hostiles a wider
    set is shell syntax at that position: an apostrophe, semicolon, pipe,
    ampersand, parenthesis, redirection character or newline. The packaging
    guard's unknown-family refusal runs inside the shell the payload has
    already escaped, so the make-level guard refuses the value before it is
    expanded into any recipe; a space stays legal because the value is a
    list of names.
    """

    EXTRA_HOSTILES = (
        ("'", "x'; y'", "x'; y'"),
        (";", "x; y", "x; y"),
        ("|", "x|y", "x|y"),
        ("&", "x&y", "x&y"),
        ("(", "x(y", "x(y"),
        (")", "x)y", "x)y"),
        ("<", "x<y", "x<y"),
        (">", "x>y", "x>y"),
    )

    def _assert_refused(self, make_value, shown_value):
        """Dry-run `install` with *make_value*; make must refuse at parse time."""
        result = theme_install.run_make(
            ["-n", "install", f"INSTALL_PACKAGES={make_value}"],
            env=theme_install.make_env("INSTALL_PACKAGES"),
        )
        assert_failed(self, result)
        self.assertIn(
            "INSTALL_PACKAGES contains a shell metacharacter", result.stderr
        )
        self.assertIn(shown_value, result.stderr)

    def test_the_double_quoted_hostiles_are_refused(self):
        # The unquoted paste inherits the double-quoted four as well.
        for char, make_value, shown_value in refusals.TestShellUnsafeInstallPaths.HOSTILES:
            with self.subTest(char=char):
                self._assert_refused(make_value, shown_value)

    def test_each_unquoted_metacharacter_is_refused(self):
        for char, make_value, shown_value in self.EXTRA_HOSTILES:
            with self.subTest(char=char):
                self._assert_refused(make_value, shown_value)

    def test_a_newline_is_refused(self):
        # An unquoted newline is a command separator; make carries a
        # command-line assignment's newline into the value verbatim.
        self._assert_refused(
            "color-scheme\nlook-and-feel; echo",
            "color-scheme\nlook-and-feel; echo",
        )

    def test_a_refused_family_list_runs_no_shell(self):
        """A refused INSTALL_PACKAGES must not run any of its injected words.

        Before the guard, `make install INSTALL_PACKAGES='noop; touch
        <canary'` fired the touch inside `set -- noop; touch ...` before the
        unknown-family refusal. The refusal must come first and leave no
        canary and no data home.
        """
        tmp = make_tmp_dir(self)
        canary = tmp / "injected"
        result = theme_install.run_make(
            [
                "install",
                f"INSTALL_PACKAGES=noop; touch '{canary}'",
                f"DESTDIR={tmp}",
            ],
            env=theme_install.make_env("INSTALL_PACKAGES"),
        )
        assert_failed(self, result)
        self.assertIn(
            "INSTALL_PACKAGES contains a shell metacharacter", result.stderr
        )
        self.assertFalse(canary.exists(), "canary created; the guard escaped")
        data_home = os.path.join(tmp, installed_paths.XDG_DATA_HOME.lstrip("/"))
        self.assertFalse(os.path.exists(data_home), data_home)

    def test_make_function_text_in_INSTALL_PACKAGES_is_refused_without_evaluation(self):
        # The refusal's own diagnostic echoes the value, so it must echo the
        # raw text: expanding `$(INSTALL_PACKAGES)` there would run the very
        # function the guard is refusing.
        tmp = make_tmp_dir(self)
        canary = tmp / "make-function-executed"
        env = theme_install.make_env("INSTALL_PACKAGES")
        env["INSTALL_PACKAGES"] = f"$(shell touch {canary})"
        result = theme_install.run_make(["-n", "install"], env=env)
        assert_failed(self, result)
        self.assertIn(
            "INSTALL_PACKAGES contains a shell metacharacter", result.stderr
        )
        self.assertFalse(canary.exists(), canary)

    def test_a_clean_family_list_runs_the_install_recipe(self):
        # The guard must not refuse the documented single-family form.
        result = theme_install.run_make(
            [
                "-n",
                "install",
                "INSTALL_PACKAGES=look-and-feel",
            ],
            env=theme_install.make_env("INSTALL_PACKAGES"),
        )
        assert_succeeded(self, result)
        self.assertIn("look-and-feel", result.stdout)


class TestShellUnsafeCheckVariables(unittest.TestCase):
    """A `check` narrowing value carrying a control byte is refused unecheod.

    `require_check_tests` and `require_check_parallel` echo a refused value
    back inside quotes (`CHECK_TESTS may contain only dotted test names:
    '<value>'`, `CHECK_PARALLEL must be a worker count ...: '<value>'`), and
    CHECK_PARALLEL additionally reaches the unquoted `--workers` position,
    CHECK_TESTS the unquoted unittest one. Both guards paste the value into
    the double-quoted words `set -- "$(CHECK_TESTS)"` and
    `set -- "$(CHECK_PARALLEL)"` first, so a double quote, `$`, a backtick
    or a backslash rewrites the guard line itself and runs as shell syntax
    before any guard logic: both variables join the shared parse-time
    refusal for those four metacharacters (TestShellUnsafeThemeRoot pins the
    same hole in `require_theme_links`). The guards' own alphabet tests keep
    refusing the wider punctuation (a semicolon, an apostrophe and the like
    are inert inside double quotes, and the guards echo the shell-copied
    `$1`, not the raw value); a control byte is refused unecheod by the same
    shared refusal, which also covers the guards' quoted echo pasting a
    byte like 0x1b raw into the operator's terminal before it joined the
    others (`TestShellUnsafeControlCharacters`). The refusal must name the
    variable, and neither the byte nor the metacharacter may run a recipe.
    """

    def _assert_check_metachar_is_refused(self, variable):
        """Drive `make check` with a double quote in *variable*; refuse it.

        The value breaks out of `set -- "$(CHECK_TESTS)"` or
        `set -- "$(CHECK_PARALLEL)"` six characters in, so the injected
        words run before either guard can refuse anything: without the
        parse-time refusal the canary file is created and the injected
        `exit 7` ends the recipe. The refusal happens when make parses the
        guard call, so nothing runs: the diagnostic is the run's whole
        output and the canary never appears.
        """
        tmp = make_tmp_dir(self)
        canary = f"{variable.lower()}_guard_canary"
        result = theme_install.run_captured(
            [
                "make",
                "-f",
                str(repo_root.ROOT / "Makefile"),
                "check",
                f'{variable}=p"; touch {canary}; exit 7; echo "',
            ],
            cwd=str(tmp),
            env=theme_install.make_env(),
        )
        assert_failed(self, result)
        self.assertIn(f"{variable} contains a shell metacharacter", result.stderr)
        self.assertIn(
            f'p"; touch {canary}; exit 7; echo "', result.stderr
        )
        self.assertFalse((tmp / canary).exists(), tmp)
        # The injected words never made the recipe shell run: no coordinator
        # banner or unittest line beside the refusal.
        self.assertNotIn("NO TESTS RAN", result.stdout + result.stderr)
        self.assertNotIn("tools/check_parallel.py", result.stdout + result.stderr)

    def test_a_double_quote_in_each_check_narrower_runs_neither_recipe_nor_shell(self):
        for variable in ("CHECK_TESTS", "CHECK_PARALLEL"):
            with self.subTest(variable=variable):
                self._assert_check_metachar_is_refused(variable)

    def _assert_check_refused(self, variable, byte, env_value=None):
        """Drive `make check` with a control byte in *variable*; refuse it.

        The value reaches the refusal either through a command-line
        assignment or, when *env_value* is given, through the environment.
        A refusal happens before any recipe unless the parse-time guard misses
        it, in which case the run-time guard still refuses -- but echoes the
        byte, which the `assertNotIn` catches.
        """
        env = theme_install.make_env(variable)
        args = []
        if env_value is None:
            args.append(f"{variable}={byte}")
        else:
            env[variable] = env_value
        result = theme_install.run_make(["check", *args], env=env)
        assert_failed(self, result)
        self.assertIn(
            f"{variable} contains a control character", result.stderr
        )
        output = result.stdout + result.stderr
        self.assertNotIn(byte, output)

    def test_an_escape_byte_in_each_check_narrower_is_refused_without_echoing_it(self):
        for variable in ("CHECK_TESTS", "CHECK_PARALLEL"):
            with self.subTest(variable=variable):
                self._assert_check_refused(variable, "ab\x1b tests_x")

    def test_an_escape_byte_reaches_the_refusal_through_the_environment(self):
        # The environment route alongside the command-line one, the way
        # TestShellUnsafeControlCharacters drives both for the install paths.
        self._assert_check_refused(
            "CHECK_TESTS", "tests_x\x1b", env_value="tests_x\x1b"
        )

    def test_del_is_refused_in_each_check_narrower(self):
        for variable in ("CHECK_TESTS", "CHECK_PARALLEL"):
            with self.subTest(variable=variable):
                self._assert_check_refused(variable, "ab\x7fdel")

    def test_a_refused_check_narrower_runs_no_tests(self):
        # The refusal happens before the suite could start: the diagnostic is
        # the run's whole output, with no coordinator banner or unittest line
        # anywhere beside it.
        result = theme_install.run_make(
            ["check", "CHECK_TESTS=ab\x1b tests_x"],
            env=theme_install.make_env("CHECK_TESTS"),
        )
        assert_failed(self, result)
        self.assertNotIn("NO TESTS RAN", result.stdout + result.stderr)
        self.assertNotIn("tools/check_parallel.py", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
