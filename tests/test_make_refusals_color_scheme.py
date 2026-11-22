"""The Makefile's parse-time refusals of the colour-scheme variables.

`COLOR_SCHEME` is a source path pasted into the install's staging copy and the
uninstall's removal, and `COLOR_SCHEME_NAME` is the installed basename both
recipes expand and the id derivation shell reads through the environment. Each
class pins that a metacharacter in its value is refused at make level, before
any recipe runs, and that the shell never executes (`canary` probes). The
other path, profile, theme-root and control-byte refusals stay in
``test_make_refusals.py``; the tool and check-narrowing variables live in
``test_make_refusals_tools.py``.
"""

import unittest

from support import repo_root, theme_install
from support.make_hostiles import HOSTILES
from support.process_assertions import assert_failed, assert_succeeded
from support.tmp_dir import make_tmp_dir


class TestShellUnsafeColorScheme(unittest.TestCase):
    """A `COLOR_SCHEME` carrying a recipe-shell metacharacter is refused.

    `COLOR_SCHEME` is a command-line overridable source path that reaches
    double-quoted recipe words (the install's staging copy and the uninstall's
    removal), so a double quote, `$`, a backtick or a backslash would run the
    words after it as shell commands instead of naming a path. The same
    make-level guard `TestShellUnsafeInstallPaths` pins for the install paths
    refuses such a value before any recipe of either target.
    """

    def test_each_metacharacter_is_refused_in_COLOR_SCHEME(self):
        # The guard reads each value after make's own expansion, so the same
        # HOSTILES pairs `support.make_hostiles` documents apply: a `$`
        # arrives doubled in the make argument.
        for char, make_value, shown_value in HOSTILES:
            with self.subTest(char=char):
                theme_install.assert_metacharacter_refused(
                    self, "COLOR_SCHEME", make_value, shown_value
                )

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


class TestShellUnsafeColorSchemeName(unittest.TestCase):
    """A `COLOR_SCHEME_NAME` override carrying a metacharacter is refused.

    The Makefile derives `COLOR_SCHEME_NAME` from `COLOR_SCHEME`, but a
    command-line or environment override bypasses that derivation (a
    command-line definition precedes parse and survives the makefile's own
    `:=`), and the name is expanded into double-quoted recipe words: the
    color scheme's staging copy (`staging=".../.$(COLOR_SCHEME_NAME).staging"`
    and `mv "$staging" "$(INSTALL_DIR)/$(COLOR_SCHEME_NAME)"`) and the
    uninstall's removal (`rm -f "$(INSTALL_DIR)/$(COLOR_SCHEME_NAME)"`), plus
    the exported environment the `$(shell)` id derivation reads
    (`name="$$COLOR_SCHEME_NAME"`). A double quote, `$`, a backtick or a
    backslash in an override would run the words after it as shell commands
    or escape the derivation word instead of naming an installed file
    basename. The parse-time guard `TestShellUnsafeColorScheme` pins for
    `COLOR_SCHEME` reads the name before any recipe runs, whether the value
    comes from a command-line assignment or the environment.
    """

    def test_each_metacharacter_is_refused_in_COLOR_SCHEME_NAME(self):
        # The guard reads each value after make's own expansion, so the same
        # HOSTILES pairs `support.make_hostiles` documents apply: a `$`
        # arrives doubled in the make argument.
        for char, make_value, shown_value in HOSTILES:
            with self.subTest(char=char):
                theme_install.assert_metacharacter_refused(
                    self, "COLOR_SCHEME_NAME", make_value, shown_value
                )

    def test_a_hostile_override_never_runs_its_shell(self):
        """A double-quote breakout in an override must not run a canary.

        Without the parse-time guard, an override like
        `x"; touch <canary>; echo "` exited the double-quoted
        `mv "$staging" "$(INSTALL_DIR)/$(COLOR_SCHEME_NAME)"` word and ran
        the middle words when the recipe executed.
        """
        tmp = make_tmp_dir(self)
        canary = tmp / "injected"
        hostile = f'x"; touch "{canary}"; echo "'
        theme_install.assert_metacharacter_refused(self, "COLOR_SCHEME_NAME", hostile, hostile)
        self.assertFalse(canary.exists(), hostile)

    def test_an_escape_byte_in_an_override_is_refused_without_echoing_it(self):
        # The override reaches recipes through both routes a command-line
        # definition and the environment offer; the guard's diagnostic must
        # not echo a value that carries a terminal byte, the way
        # TestShellUnsafeControlCharacters pins for the install paths.
        for target in ("install", "uninstall"):
            with self.subTest(target=target):
                result = theme_install.run_make(
                    [target, "COLOR_SCHEME_NAME=ab\x1b[0;31m"],
                    env=theme_install.make_env("COLOR_SCHEME_NAME"),
                )
                assert_failed(self, result)
                self.assertIn(
                    "COLOR_SCHEME_NAME contains a control character",
                    result.stderr,
                )
                output = result.stdout + result.stderr
                self.assertNotIn("\x1b", output)

    def test_an_environment_override_is_refused(self):
        # The environment route matters because the `$(shell)` id derivation
        # reads the exported value: make must refuse it before that shell
        # runs at all.
        tmp = make_tmp_dir(self)
        env = theme_install.make_env("COLOR_SCHEME_NAME")
        hostile = f'z"; touch "{tmp}/canary2"; echo "'
        env["COLOR_SCHEME_NAME"] = hostile
        for target in ("install", "uninstall"):
            with self.subTest(target=target):
                result = theme_install.run_make([target], env=env)
                assert_failed(self, result)
                self.assertIn(
                    "COLOR_SCHEME_NAME contains a shell metacharacter",
                    result.stderr,
                )
        self.assertFalse((tmp / "canary2").exists(), tmp)

    def test_an_override_with_a_space_or_an_apostrophe_is_still_legal(self):
        # A space and an apostrophe are inert inside double-quoted recipe
        # words, and the id derivation reads the name through the exported
        # environment, not through a quoted shell word. A renamed value
        # therefore keeps installing under its basename.
        result = theme_install.run_make(
            ["-n", "install", "COLOR_SCHEME_NAME=dotted 1.0.1-a's root"]
        )
        assert_succeeded(self, result)


if __name__ == "__main__":
    unittest.main()
