"""The Makefile's parse-time refusals of shell-unsafe and control-byte values.

A refused value would reach a recipe shell inside a double-quoted recipe
word, where a metacharacter becomes shell syntax, or be pasted raw into the
guard's own diagnostic, where a control byte could drive a terminal. A guard
refuses before any recipe runs, so each class pins both the refusal itself and
that the shell never executes (`CANARY` style probes); where a guarded value
with a space or an apostrophe stays legal, the class pins that beside the
refusals. `make check`'s narrowing variables live in ``test_make_check.py``,
`make help` in ``test_make_help.py`` and the install behaviour those guards
wrap in ``test_theme_install.py``, whose whitespace-legal install paths round
trip under the quoting the guards wrap.
"""

import os
import unittest

from support import installed_paths, repo_root, theme_install
from support.process_assertions import assert_failed, assert_succeeded
from support.tmp_dir import make_tmp_dir


class TestShellUnsafeInstallPaths(unittest.TestCase):
    """A path variable carrying a recipe-shell metacharacter must be refused.

    DESTDIR, XDG_DATA_HOME and HOME reach recipe shells pasted into
    double-quoted recipe words, where a double quote, `$`, a backtick or a
    backslash is shell syntax: the words after it run as shell commands
    instead of naming a path. The Makefile refuses such a value at make
    level, before any recipe of any target runs, so a refused run must not
    create the data home -- or this test's canary file -- and its diagnostic
    must name the variable and the value. A space or an apostrophe is inert
    there and stays legal (`TestWhitespaceInInstallPaths`). The guarded
    variables are the install paths (`DESTDIR`, `XDG_DATA_HOME`, `HOME`), the
    lock timeout (`FLOCK_TIMEOUT`, whose value reaches the digit guard's
    `set -- "$(FLOCK_TIMEOUT)"` word) and the Firefox profile path.
    """

    # The guard reads each value after make's own expansion, so a `$` arrives
    # doubled: the make argument `x$$y` expands to `x$y`, the text the guard
    # and the diagnostic see. The other three characters pass through make
    # verbatim.
    HOSTILES = (
        ('"', 'x"; y"', 'x"; y"'),
        ("$", "x$$y", "x$y"),
        ("`", "x`y`", "x`y`"),
        ("\\", "x\\y", "x\\y"),
    )

    def _assert_refused(self, variable, make_value, shown_value, args=()):
        """Run `install`/`uninstall` with *variable* set and assert refusal.

        *make_value* is the assignment each target receives, *shown_value* the
        text the diagnostic must echo back verbatim. Both targets are driven
        because they share the guard.
        """
        theme_install.assert_both_targets_refused(
            self,
            None,
            (*args, f"{variable}={make_value}"),
            (
                f"{variable} contains a shell metacharacter",
                shown_value,
            ),
        )

    def test_a_hostile_DESTDIR_is_refused_without_running_its_shell(self):
        tmp = make_tmp_dir(self)
        canary = tmp / "injected"
        hostile = f'/tmp/x"; touch "{canary}"; echo "'
        self._assert_refused("DESTDIR", hostile, hostile)
        self.assertFalse(canary.exists(), hostile)
        data_home = os.path.join(
            tmp, installed_paths.XDG_DATA_HOME.lstrip("/")
        )
        self.assertFalse(os.path.exists(data_home), data_home)

    def test_each_metacharacter_is_refused_in_DESTDIR(self):
        for char, make_value, shown_value in self.HOSTILES:
            with self.subTest(char=char):
                self._assert_refused("DESTDIR", make_value, shown_value)

    def test_each_metacharacter_is_refused_in_XDG_DATA_HOME(self):
        for char, make_value, shown_value in self.HOSTILES:
            with self.subTest(char=char):
                tmp = make_tmp_dir(self)
                self._assert_refused(
                    "XDG_DATA_HOME",
                    make_value,
                    shown_value,
                    args=(f"DESTDIR={tmp}",),
                )

    def test_each_metacharacter_is_refused_in_HOME(self):
        # The guard is unconditional, so a hostile HOME is refused even when
        # an absolute XDG_DATA_HOME resolves without it.
        for char, make_value, shown_value in self.HOSTILES:
            with self.subTest(char=char):
                tmp = make_tmp_dir(self)
                env = theme_install.make_env()
                env["HOME"] = make_value
                env.pop("XDG_DATA_HOME", None)
                theme_install.assert_both_targets_refused(
                    self,
                    env,
                    (f"DESTDIR={tmp}", f"XDG_DATA_HOME={installed_paths.XDG_DATA_HOME}"),
                    (
                        "HOME contains a shell metacharacter",
                        shown_value,
                    ),
                )

    def test_each_metacharacter_is_refused_in_FLOCK_TIMEOUT(self):
        # FLOCK_TIMEOUT is pasted into the digit guard's double-quoted word
        # `set -- "$(FLOCK_TIMEOUT)"` (and passed on from there to `flock
        # -w`), so each metacharacter must be refused at make level before
        # that guard's own quoting can be escaped.
        for char, make_value, shown_value in self.HOSTILES:
            with self.subTest(char=char):
                self._assert_refused("FLOCK_TIMEOUT", make_value, shown_value)


class TestShellUnsafeFirefoxProfile(unittest.TestCase):
    """A `FIREFOX_PROFILE` carrying a recipe-shell metacharacter is refused.

    install-firefox and remove-firefox pass the profile as a double-quoted
    recipe word (`--profile "$(FIREFOX_PROFILE)"`), so a value carrying a
    double quote, `$`, a backtick or a backslash would run the words after
    it as shell commands instead of naming a profile: before the refusal,
    `make install-firefox FIREFOX_PROFILE='p"; touch "canary"; echo "'`
    created the canary file, and because the last injected word was `echo`,
    the run exited 0 while the tool's refusal appeared as stray output. The
    refused value hits the same make-level guard
    `TestShellUnsafeInstallPaths` pins for the install paths, so the
    diagnostic must fire before any recipe of either target.
    """

    def _assert_refused(self, target, make_value, shown_value):
        """Run *target* with *make_value* and assert the make-level refusal.

        *shown_value* is the text the diagnostic must echo back verbatim.
        `install-firefox` and `remove-firefox` share the guard, so both are
        driven once per metacharacter case.
        """
        result = theme_install.run_make(
            [target, f"FIREFOX_PROFILE={make_value}"],
            env=theme_install.make_env("FIREFOX_PROFILE"),
        )
        assert_failed(self, result)
        self.assertIn(
            "FIREFOX_PROFILE contains a shell metacharacter", result.stderr
        )
        self.assertIn(shown_value, result.stderr)

    def _assert_both_targets_refused(self, make_value, shown_value):
        for target in ("install-firefox", "remove-firefox"):
            with self.subTest(target=target):
                self._assert_refused(target, make_value, shown_value)

    def test_a_hostile_FIREFOX_PROFILE_is_refused_without_running_its_shell(self):
        tmp = make_tmp_dir(self)
        canary = tmp / "injected"
        hostile = f'{tmp}/p"; touch "{canary}"; echo "'
        self._assert_both_targets_refused(hostile, hostile)
        self.assertFalse(canary.exists(), hostile)

    def test_each_metacharacter_is_refused_in_FIREFOX_PROFILE(self):
        # The guard reads the value after make's own expansion, so the same
        # HOSTILES pairs `TestShellUnsafeInstallPaths` documents apply: a
        # `$` arrives doubled in the make argument.
        for char, make_value, shown_value in TestShellUnsafeInstallPaths.HOSTILES:
            with self.subTest(char=char):
                self._assert_both_targets_refused(make_value, shown_value)

    def test_a_profile_path_with_a_space_is_still_legal(self):
        # As for the install paths, a space (and an apostrophe) is inert
        # inside the double-quoted recipe word: it must reach the tool
        # verbatim instead of being refused.
        tmp = make_tmp_dir(self)
        profile = tmp / "spaced profile"
        result = theme_install.run_make(
            ["-n", "install-firefox", f"FIREFOX_PROFILE={profile}"],
            env=theme_install.make_env("FIREFOX_PROFILE"),
        )
        assert_succeeded(self, result)
        self.assertIn("install_firefox.py --profile ", result.stdout)
        self.assertIn(f'--profile "{profile}"', result.stdout)


class TestShellUnsafeColorScheme(unittest.TestCase):
    """A `COLOR_SCHEME` carrying a recipe-shell metacharacter is refused.

    `COLOR_SCHEME` is a command-line overridable source path that reaches
    double-quoted recipe words (the install's staging copy and the uninstall's
    removal), so a double quote, `$`, a backtick or a backslash would run the
    words after it as shell commands instead of naming a path. The same
    make-level guard `TestShellUnsafeInstallPaths` pins for the install paths
    refuses such a value before any recipe of either target.
    """

    def _assert_refused(self, make_value, shown_value):
        """Run `install`/`uninstall` with *make_value*; both must refuse.

        *shown_value* is the text the diagnostic must echo back verbatim.
        """
        theme_install.assert_both_targets_refused(
            self,
            None,
            (f"COLOR_SCHEME={make_value}",),
            (
                "COLOR_SCHEME contains a shell metacharacter",
                shown_value,
            ),
        )

    def test_each_metacharacter_is_refused_in_COLOR_SCHEME(self):
        # The guard reads each value after make's own expansion, so the same
        # HOSTILES pairs `TestShellUnsafeInstallPaths` documents apply: a `$`
        # arrives doubled in the make argument.
        for char, make_value, shown_value in TestShellUnsafeInstallPaths.HOSTILES:
            with self.subTest(char=char):
                self._assert_refused(make_value, shown_value)

    def test_an_apostrophe_cannot_reach_the_id_derivation_shell(self):
        """An apostrophe in `COLOR_SCHEME` cannot breach a quoted shell word.

        The id derivation once interpolated the name into a single-quoted
        `$(shell)` word, where an apostrophe ended the quote and every word
        after it ran as shell commands: `make` with
        `COLOR_SCHEME=zzz/x'; touch <canary>; echo '.colors` created the
        canary at make-parse time, before any target ran. The name now
        travels through the exported environment instead of the shell text,
        and an apostrophe stays legal: a `touch` carried in the value must
        not run.
        """
        tmp = make_tmp_dir(self)
        makefile = repo_root.ROOT / "Makefile"
        canary = "color_scheme_id_derivation_canary"
        # The dry run needs a cwd where the relative payload cannot reach a
        # file outside the scratch tree, and `THEME_ROOT`'s default is
        # relative to that cwd, which a dry run never reads.
        result = theme_install.run_captured(
            [
                "make",
                "-f",
                str(makefile),
                "-n",
                "uninstall",
                f"COLOR_SCHEME=zzz/x'; touch {canary}; echo '.colors",
                f"DESTDIR={tmp}",
                f"XDG_DATA_HOME={tmp}",
            ],
            cwd=str(tmp),
            env=theme_install.make_env(),
        )
        assert_succeeded(self, result)
        self.assertFalse((tmp / canary).exists(), tmp)

    def test_a_rename_with_an_apostrophe_derives_the_id(self):
        """A renamed scheme source keeps the documented first-dot id rule.

        Renaming is the documented reason a command-line `COLOR_SCHEME`
        exists: install under the source's own basename, and derive the id
        from the basename up to the first dot, with an apostrophe inert
        throughout.
        """
        tmp = make_tmp_dir(self)
        result = theme_install.run_captured(
            [
                "make",
                "-f",
                str(repo_root.ROOT / "Makefile"),
                "-p",
                "-n",
                "uninstall",
                f"COLOR_SCHEME={tmp}/my scheme'.colors",
                f"DESTDIR={tmp}",
                f"XDG_DATA_HOME={tmp}",
            ],
            cwd=str(tmp),
            env=theme_install.make_env(),
        )
        assert_succeeded(self, result)
        # The `-p` database's destination (stdout or stderr) is make's own
        # choice, so the assertions read both.
        output = result.stdout + result.stderr
        self.assertIn("COLOR_SCHEME_NAME := my scheme'.colors", output)
        self.assertIn("COLOR_SCHEME_ID := my scheme'", output)


class TestShellUnsafeThemeRoot(unittest.TestCase):
    """A `THEME_ROOT` carrying a recipe-shell metacharacter is refused.

    `THEME_ROOT` is a command-line overridable tree root that pushes into
    double-quoted recipe words: `install`'s symlink guard
    (`require_theme_links`) runs `[ -L "$(THEME_ROOT)" ]` and
    `find "$(THEME_ROOT)" ...`, so a double quote, `$`, a backtick or a
    backslash would run the words after it as shell commands instead of
    naming a tree -- with a backtick in the value, `make install
    THEME_ROOT='x`touch canary`'` executes `touch canary` from the recipe
    shell. The same make-level guard that `TestShellUnsafeInstallPaths`
    pins for the install paths, `FLOCK_TIMEOUT`, `FIREFOX_PROFILE` and
    `COLOR_SCHEME` refuses such a value at parse time, before any recipe of
    any target runs. A space or an apostrophe is inert inside a
    double-quoted word and stays legal.
    """

    def _assert_refused(self, make_value, shown_value):
        """Run `install`/`uninstall` with *make_value*; both must refuse.

        *shown_value* is the text the diagnostic must echo back verbatim.
        """
        theme_install.assert_both_targets_refused(
            self,
            None,
            (f"THEME_ROOT={make_value}",),
            (
                "THEME_ROOT contains a shell metacharacter",
                shown_value,
            ),
        )

    def test_a_hostile_THEME_ROOT_is_refused_without_running_its_shell(self):
        """A double quote in `THEME_ROOT` cannot escape the symlink guard.

        Before this guard, `make install THEME_ROOT='x"; touch {canary};
        exit 7; echo "'` broke out of `require_theme_links`' quoted word:
        the injected words made the recipe shell create the canary and exit
        before the guard could refuse anything.
        """
        tmp = make_tmp_dir(self)
        canary = "theme_root_guard_canary"
        result = theme_install.run_captured(
            [
                "make",
                "-f",
                str(repo_root.ROOT / "Makefile"),
                "install",
                f"THEME_ROOT=x\"; touch {canary}; exit 7; echo \"",
                f"DESTDIR={tmp}",
                f"XDG_DATA_HOME={tmp}",
            ],
            cwd=str(tmp),
            env=theme_install.make_env(),
        )
        assert_failed(self, result)
        self.assertIn("THEME_ROOT contains a shell metacharacter", result.stderr)
        self.assertIn("x\"; touch theme_root_guard_canary; exit 7; echo \"", result.stderr)
        self.assertFalse((tmp / canary).exists(), tmp)

    def test_each_metacharacter_is_refused_in_THEME_ROOT(self):
        # The guard reads each value after make's own expansion, so the same
        # HOSTILES pairs `TestShellUnsafeInstallPaths` documents apply: a `$`
        # arrives doubled in the make argument.
        for char, make_value, shown_value in TestShellUnsafeInstallPaths.HOSTILES:
            with self.subTest(char=char):
                self._assert_refused(make_value, shown_value)

    def test_an_escape_byte_in_THEME_ROOT_is_refused_without_echoing_it(self):
        # Control bytes are not shell syntax inside a double-quoted word, but
        # the metacharacter branch's diagnostic pastes the refused value raw:
        # the control-byte branch must fire first, as for the other guards
        # (`TestShellUnsafeControlCharacters`).
        byte = "\x1b"
        result = theme_install.run_make(
            ["install", f"THEME_ROOT=/t{byte}tree"], env=theme_install.make_env()
        )
        assert_failed(self, result)
        self.assertIn("THEME_ROOT contains a control character", result.stderr)
        output = result.stdout + result.stderr
        self.assertNotIn(byte, output)

    def test_a_tree_root_with_a_space_or_an_apostrophe_is_still_legal(self):
        # A space or an apostrophe is inert inside the double-quoted word:
        # a dry run must print the recipes instead of refusing.
        result = theme_install.run_captured(
            [
                "make",
                "-f",
                str(repo_root.ROOT / "Makefile"),
                "-p",
                "-n",
                "install",
                "THEME_ROOT=theme' spaced tree",
            ],
            env=theme_install.make_env(),
        )
        assert_succeeded(self, result)
        output = result.stdout + result.stderr
        self.assertIn("THEME_ROOT = theme' spaced tree", output)


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
    # (`TestShellUnsafeInstallPaths.HOSTILES`): the make-argument form and
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

    def test_the_double_quoted_hostiles_are_refused(self):
        # A value pasted into `set -- "$(PYTHON)"` (require_python) and into
        # the double-quoted echo of require_python_version needs the same
        # four refusals as the path variables.
        for char, make_value, shown_value in TestShellUnsafeInstallPaths.HOSTILES:
            with self.subTest(char=char):
                self._assert_refused(make_value, shown_value)

    def test_each_unquoted_metacharacter_is_refused(self):
        for char, make_value, shown_value in self.EXTRA_HOSTILES:
            with self.subTest(char=char):
                self._assert_refused(make_value, shown_value)

    def test_a_newline_is_refused(self):
        # An unquoted newline is a command separator, and make carries a
        # command-line assignment's newline into the value verbatim.
        self._assert_refused("py\nx; touch CANARY", "py\nx; touch CANARY")

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
        # TestShellUnsafeInstallPaths.HOSTILES (`$` arrives doubled in the
        # make argument, the other three pass through verbatim).
        for char, make_value, shown_value in TestShellUnsafeInstallPaths.HOSTILES:
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
        for char, make_value, shown_value in TestShellUnsafeInstallPaths.HOSTILES:
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


class TestShellUnsafeRenderOutput(unittest.TestCase):
    """A `RENDER_OUTPUT` carrying a recipe-shell metacharacter is refused.

    `render` pastes the value into the double-quoted word
    `-- "$(RENDER_OUTPUT)"`, so a double quote, `$`, a backtick or a
    backslash would run the words after it as shell commands instead of
    naming a PNG file. The same make-level guard the install paths pin
    refuses such a value before any recipe of any target runs; the variable's
    `?=` default sits further down in the Makefile, so the guard sees it as
    still undefined there and only environment or command-line values are
    checked.
    """

    def _assert_refused(self, make_value, shown_value):
        result = theme_install.run_make(
            ["-n", "render", f"RENDER_OUTPUT={make_value}"]
        )
        assert_failed(self, result)
        self.assertIn("RENDER_OUTPUT contains a shell metacharacter", result.stderr)
        self.assertIn(shown_value, result.stderr)

    def test_each_metacharacter_is_refused_in_RENDER_OUTPUT(self):
        # The value reaches a double-quoted word, so the same HOSTILES pairs
        # `TestShellUnsafeInstallPaths` documents apply.
        for char, make_value, shown_value in TestShellUnsafeInstallPaths.HOSTILES:
            with self.subTest(char=char):
                self._assert_refused(make_value, shown_value)

    def test_a_hostile_value_runs_no_shell(self):
        """A refused RENDER_OUTPUT must not run any of its injected words.

        Without the guard, `make render RENDER_OUTPUT='x"; touch <canary>;
        echo "'` created the canary after the render tool's word closed. The
        refusal must come first and leave no canary.
        """
        tmp = make_tmp_dir(self)
        canary = tmp / "injected"
        result = theme_install.run_make(
            ["render", f"RENDER_OUTPUT=x\"; touch '{canary}'; echo \""]
        )
        assert_failed(self, result)
        self.assertIn("RENDER_OUTPUT contains a shell metacharacter", result.stderr)
        self.assertFalse(canary.exists(), tmp)

    def test_a_name_with_a_space_stays_legal(self):
        # Inside the double-quoted word a space is inert, so a file name with
        # one keeps working.
        result = theme_install.run_make(
            ["-n", "render", "RENDER_OUTPUT=my render.png"]
        )
        assert_succeeded(self, result)
        self.assertIn('-- "my render.png"', result.stdout)


class TestShellUnsafeCheckVariables(unittest.TestCase):
    """A `check` narrowing value carrying a control byte is refused unecheod.

    `require_check_tests` and `require_check_parallel` echo a refused value
    back inside quotes (`CHECK_TESTS may contain only dotted test names:
    '<value>'`, `CHECK_PARALLEL must be a worker count ...: '<value>'`), and
    CHECK_PARALLEL additionally reaches the unquoted `--workers` position,
    CHECK_TESTS the unquoted unittest one. Both recipe guards limit the value
    first, so a metacharacter cannot reach an unquoted position; a control
    byte is not shell syntax anywhere, but the guards' quoted echo pasted it
    raw into the operator's terminal before these parse-time refusals joined
    the others (`TestShellUnsafeControlCharacters`). The refusal must name
    the variable, and the byte must reach neither stdout nor stderr.
    """

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


class TestShellUnsafeControlCharacters(unittest.TestCase):
    """A guarded value carrying a control byte must be refused, not echoed.

    A control byte is not shell syntax inside a double-quoted recipe word, but
    the guard's own diagnostic pastes the refused value raw, and
    `require_flock_timeout` echoes a refused `FLOCK_TIMEOUT` back at run time:
    before this refusal, `make help` with a `DESTDIR` carrying a terminal
    escape byte beside a metacharacter printed the raw 0x1b byte into the
    operator's terminal inside the diagnostic's quoted value, and a real
    `make install FLOCK_TIMEOUT='ab<ESC>'` echoed it from the digit guard's
    (`install: FLOCK_TIMEOUT must be ... 'ab<ESC>'"`). The guard now refuses
    a value carrying a control byte before any recipe and before any branch
    of its own diagnostic runs, so it does not echo the value back: neither
    stderr nor stdout may carry the byte.
    """

    def _assert_control_refused(self, variable, byte, env_value=None):
        """Drive both targets with a control byte in *variable*; both refuse.

        The value reaches the guard either through a command-line assignment
        or, when *env_value* is given, through the environment
        (`XDG_DATA_HOME_ENV` keeps the raw environment value; a command-line
        one overrides the `?=` fallback). The refusal names the variable, and
        the terminal byte must reach neither stdout nor stderr: the guard
        never echoes a value that carries one.
        """
        terms = theme_install.make_env(variable)
        args = []
        if env_value is None:
            args.append(f"{variable}={byte}")
        else:
            terms[variable] = env_value
        for target in ("install", "uninstall"):
            with self.subTest(target=target, variable=variable):
                result = theme_install.run_make([target, *args], env=terms)
                assert_failed(self, result)
                self.assertIn(
                    f"{variable} contains a control character", result.stderr
                )
                output = result.stdout + result.stderr
                self.assertNotIn(byte, output)

    def test_an_escape_byte_beside_a_metacharacter_is_refused_without_echoing_it(self):
        # The regression: the metacharacter branch fired first and echoed the
        # value, so the escape byte inside it reached the terminal raw.
        tmp = make_tmp_dir(self)
        self._assert_control_refused(
            "DESTDIR", f"/x\x1b[0;31m; touch {tmp}/canary; echo \""
        )
        self.assertFalse((tmp / "canary").exists(), tmp)

    def test_an_escape_byte_alone_is_refused_in_XDG_DATA_HOME(self):
        # Through the environment, the route `XDG_DATA_HOME_ENV` keeps raw:
        tmp = make_tmp_dir(self)
        self._assert_control_refused(
            "XDG_DATA_HOME",
            "/abs/\x1bhome",
            env_value=f"{tmp}/\x1bscratch home",
        )

    def test_an_escape_byte_in_FLOCK_TIMEOUT_is_refused_before_the_digit_guard_echoes_it(self):
        # A `FLOCK_TIMEOUT` that fails the digit guard used to be echoed
        # verbatim by the guard's own refusal, control byte and all:
        self._assert_control_refused("FLOCK_TIMEOUT", "ab\x1b")

    def test_del_is_refused_in_DESTDIR(self):
        self._assert_control_refused("DESTDIR", "/x\x7fdel")

    def test_a_carriage_return_beside_a_metacharacter_is_refused_without_echoing_it(self):
        # CR (0x0d) is blank to make, so the awk-generated foreach list
        # dropped it and the control-byte branch passed: the metacharacter
        # branch then fired and echoed the value raw, pasting the CR into the
        # operator's terminal inside the diagnostic's quoted value.
        tmp = make_tmp_dir(self)
        self._assert_control_refused(
            "DESTDIR", f"/x\r; touch {tmp}/canary; echo \""
        )
        self.assertFalse((tmp / "canary").exists(), tmp)

    def test_a_carriage_return_in_FLOCK_TIMEOUT_is_refused_before_the_digit_guard_echoes_it(self):
        # The objection's repro: a CR rode through the guard and the digit
        # guard's refusal echoed it verbatim, letting the value's tail forge
        # what looks like the operator's own terminal output. (A command-line
        # assignment's LEADING CR is stripped by make's own parsing, so the
        # reachable byte sits mid-value; via the environment even a leading
        # CR arrives.)
        self._assert_control_refused("FLOCK_TIMEOUT", "ab\r<attacker text>")

    def test_each_make_blank_control_byte_is_refused_in_FLOCK_TIMEOUT(self):
        # VT (0x0b) and FF (0x0c) are also blank to make's word splitter, so
        # the foreach list dropped them too; each of the three is refused by
        # an explicit findstring test against a single-byte variable, driven
        # here through the digit guard's echo sink.
        for name, byte in (("VT", "\x0b"), ("FF", "\x0c"), ("CR", "\r")):
            with self.subTest(byte=name):
                self._assert_control_refused("FLOCK_TIMEOUT", f"ab{byte}")

    def test_a_tab_stays_legal_and_a_metacharacter_beside_a_tab_is_refused(self):
        # The two documented residuals: a tab byte is invisible to the byte
        # scan (make word-splits it away) and stays legal, while a
        # metacharacter beside one is still refused.
        result = theme_install.run_make(
            ["-n", "install", "XDG_DATA_HOME=/abs/tab\thome"]
        )
        assert_succeeded(self, result)
        theme_install.assert_both_targets_refused(
            self,
            theme_install.make_env("XDG_DATA_HOME"),
            ['XDG_DATA_HOME=/abs/tab\thome"; touch injected'],
            ["contains a shell metacharacter"],
        )

    def test_a_path_with_an_apostrophe_still_passes_the_control_scan(self):
        """A printable path, even one with an apostrophe, is still legal."""
        # The control-byte scan reads an apostrophe as just another printable
        # byte: a `make install` dry run with a value the whole guard passes
        # still reaches recipes, so a `-n` run succeeds and creates nothing.
        tmp = make_tmp_dir(self)
        result = theme_install.run_make(
            ["-n", "install", f"XDG_DATA_HOME={tmp}/dotted 1.0.1-a's root"],
            env=theme_install.make_env("XDG_DATA_HOME"),
        )
        assert_succeeded(self, result)
        self.assertFalse(os.path.exists(tmp / "dotted 1.0.1-a's root"), tmp)

    def test_python_escape_and_metacharacter_are_refused_without_echoing_escape(self):
        self._assert_control_refused("PYTHON", "python3\x1b[2J; touch CANARY")

if __name__ == "__main__":
    unittest.main()
