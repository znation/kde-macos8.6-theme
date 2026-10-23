"""`make check`'s narrowing variables: CHECK_PATTERN, CHECK_TESTS and PYTHON.

`make check` defaults to the whole suite and accepts a narrowing glob
(`CHECK_PATTERN`), named specs (`CHECK_TESTS`) or a different interpreter
(`PYTHON`); the Makefile validates each before it runs the suite. These tests
pin that wiring with `make -n` and the guards' refusals. The install and
uninstall behaviour lives in ``test_theme_install.py`` and `make help` in
``test_make_help.py``.
"""

import os
import unittest

from support import repo_root
from support import theme_install
from support.process_assertions import assert_failed, assert_succeeded
from support.tmp_dir import make_tmp_dir


class TestCheckPattern(unittest.TestCase):
    """`make check` defaults to the whole suite and accepts a narrowing glob.

    The suite is slow (the install tests spawn `make`), so a focused run should
    not have to retype `python3 -m unittest discover -s tests ...`. `make -n`
    prints the recipe without running it, so the wiring is checked without a
    nested suite run.
    """

    def _dry_run(self, *extra, env=None):
        # A caller's `make check CHECK_PATTERN=...` reaches the recipe both as
        # a CHECK_PATTERN environment variable and as a command-line variable
        # definition inside MAKEFLAGS; the child `make` re-reads the latter and
        # would otherwise use the ambient pattern for the default case.
        # `make_env` drops both so each case pins the pattern it means to; a
        # command-line assignment passed below still overrides the Makefile
        # default. A case that needs an environment value `make` would not
        # preserve in a command-line assignment (surrounding whitespace)
        # passes its own `env`.
        if env is None:
            env = theme_install.make_env("CHECK_PATTERN", "CHECK_TESTS")
        result = theme_install.run_make(["-n", "check", *extra], env=env)
        assert_succeeded(self, result)
        return result.stdout

    def test_default_pattern_runs_every_test_module(self):
        self.assertIn("-p 'test*.py'", self._dry_run())

    def test_pattern_narrows_the_discovered_modules(self):
        self.assertIn(
            "-p 'test_byteops.py'",
            self._dry_run("CHECK_PATTERN=test_byteops.py"),
        )

    def test_empty_pattern_is_refused(self):
        # CHECK_PATTERN is a make variable a caller can set from the
        # environment, but `?=` keeps an empty environment value, so `-p ''`
        # reaches `unittest discover` and matches no file. Interpreters before
        # 3.12 then exit 0 having run nothing -- a green run that executed no
        # tests. The guard must refuse it with a diagnostic naming
        # CHECK_PATTERN instead.
        env = theme_install.make_env("CHECK_PATTERN", "CHECK_TESTS")
        env["CHECK_PATTERN"] = ""
        result = theme_install.run_make(["check"], env=env)
        assert_failed(self, result)
        self.assertIn("CHECK_PATTERN must name", result.stderr)

    def test_whitespace_pattern_is_refused(self):
        # A whitespace-only value is no better: `-p ' '` matches no file
        # either, so it must be refused the same way. The environment keeps
        # the whitespace, so the diagnostic must name it rather than report an
        # empty string.
        env = theme_install.make_env("CHECK_PATTERN", "CHECK_TESTS")
        env["CHECK_PATTERN"] = " "
        result = theme_install.run_make(["check"], env=env)
        assert_failed(self, result)
        self.assertIn("CHECK_PATTERN must name", result.stderr)
        self.assertIn(": ' '", result.stderr)

    @unittest.skipUnless(
        os.path.isdir("/proc"), "recovery reads make's /proc command line"
    )
    def test_command_line_whitespace_pattern_is_refused(self):
        # Make strips leading whitespace from a command-line assignment before
        # the recipe sees it, so `make check CHECK_PATTERN=' '` arrives empty.
        # The guard recovers the caller's text from make's command line, so the
        # diagnostic names the whitespace the caller typed instead of an empty
        # string.
        env = theme_install.make_env("CHECK_PATTERN", "CHECK_TESTS")
        result = theme_install.run_make(["check", "CHECK_PATTERN= "], env=env)
        assert_failed(self, result)
        self.assertIn("CHECK_PATTERN must name", result.stderr)
        self.assertIn(": ' '", result.stderr)

    def test_pattern_matching_no_module_is_refused(self):
        # A typo in the glob matches no test module, so `unittest discover`
        # would import nothing and, on interpreters before 3.12, exit 0 -- the
        # same silent green run the empty-pattern guard exists to prevent. The
        # guard must match the pattern against the modules on disk and refuse
        # it, naming CHECK_PATTERN and the offending value.
        env = theme_install.make_env("CHECK_PATTERN", "CHECK_TESTS")
        env["CHECK_PATTERN"] = "test_no_such_module*.py"
        result = theme_install.run_make(["check"], env=env)
        assert_failed(self, result)
        self.assertIn("CHECK_PATTERN must match at least one", result.stderr)
        self.assertIn("test_no_such_module*.py", result.stderr)

    def test_pattern_matching_only_a_helper_module_is_refused(self):
        # `tests/invariants.py` matches `invar*.py` but defines no test case:
        # discovery would import it and run an empty suite, another green run
        # that ran nothing. Requiring a `test*.py` match refuses it.
        env = theme_install.make_env("CHECK_PATTERN", "CHECK_TESTS")
        env["CHECK_PATTERN"] = "invar*.py"
        result = theme_install.run_make(["check"], env=env)
        assert_failed(self, result)
        self.assertIn("CHECK_PATTERN must match at least one", result.stderr)

    def test_pattern_matching_a_module_runs_that_module(self):
        # The match guard must not refuse a real narrowing glob; run one
        # module for real, which also exercises the guard's accepting path.
        env = theme_install.make_env("CHECK_PATTERN", "CHECK_TESTS")
        env["CHECK_PATTERN"] = "test_byteops.py"
        result = theme_install.run_make(["check"], env=env)
        assert_succeeded(self, result)
        self.assertIn("-p 'test_byteops.py'", result.stdout)

    def test_surrounding_whitespace_pattern_is_stripped(self):
        # The guard strips surrounding whitespace to spot a whitespace-only
        # value, but the recipe used to hand the untrimmed glob to `unittest
        # discover`, so `-p ' test_byteops.py '` matched no file: a silent
        # green run on interpreters before 3.12 (which the version guard
        # accepts), and a "NO TESTS RAN" failure on newer ones. The recipe
        # must strip the pattern so the value the guard validates and the
        # value the run uses are the same.
        env = theme_install.make_env("CHECK_PATTERN", "CHECK_TESTS")
        env["CHECK_PATTERN"] = " test_byteops.py "
        self.assertIn("-p 'test_byteops.py'", self._dry_run(env=env))

    def test_tests_variable_runs_the_named_specs(self):
        # CHECK_TESTS names a module, class or method directly, which the
        # filename glob CHECK_PATTERN cannot do. The specs run from tests/ so
        # the modules' bare-name imports resolve as under `discover`.
        output = self._dry_run(
            "CHECK_TESTS=test_byteops.TestRequireEqualLengths"
        )
        self.assertIn("cd tests &&", output)
        self.assertIn(
            "-m unittest -v test_byteops.TestRequireEqualLengths", output
        )
        self.assertNotIn("discover", output)

    def test_relative_python_path_is_resolved_before_cd(self):
        # The CHECK_TESTS recipe changes into tests/ before it runs the
        # interpreter, so a relative PYTHON path (`./.venv/bin/python`) would
        # resolve against tests/ and fail to start, though the discovery
        # recipe, run from the repository root, works with it. The recipe
        # resolves a path-shaped PYTHON against the repository root first.
        output = self._dry_run(
            "CHECK_TESTS=test_byteops.TestRequireEqualLengths",
            "PYTHON=./.venv/bin/python",
        )
        resolved = os.path.join(
            str(repo_root.ROOT), ".venv", "bin", "python"
        )
        self.assertIn(f"cd tests && {resolved} -m unittest", output)
        self.assertNotIn("cd tests && ./.venv/bin/python", output)

    def test_bare_python_name_is_left_for_the_path_lookup(self):
        # A bare interpreter name has no path separator, so it is left as-is
        # for the shell to resolve through PATH, independent of the recipe's
        # directory.
        output = self._dry_run(
            "CHECK_TESTS=test_byteops.TestRequireEqualLengths",
            "PYTHON=python3",
        )
        self.assertIn("cd tests && python3 -m unittest", output)

    def test_python_value_with_arguments_is_left_whole(self):
        # A PYTHON carrying arguments has whitespace, so it must not be run
        # through `abspath`, which would rewrite each word into a path.
        output = self._dry_run(
            "CHECK_TESTS=test_byteops.TestRequireEqualLengths",
            "PYTHON=/usr/bin/python3 -X dev",
        )
        self.assertIn(
            "cd tests && /usr/bin/python3 -X dev -m unittest", output
        )

    def test_option_like_tests_variable_is_refused(self):
        # A leading `-` makes unittest read the value as an option (`-x`
        # aborts on the first failure) instead of a test name, so the guard
        # must refuse it with a diagnostic naming CHECK_TESTS. The second word
        # is a real test module, so a guard regression still finishes quickly
        # instead of running the whole suite.
        env = theme_install.make_env("CHECK_TESTS")
        result = theme_install.run_make(
            ["check", "CHECK_TESTS=-x test_byteops"], env=env
        )
        assert_failed(self, result)
        self.assertIn("CHECK_TESTS must name", result.stderr)

    def test_option_like_tests_variable_after_leading_whitespace_is_refused(self):
        # The guard strips leading whitespace before it looks for the leading
        # `-`, so `'  -x test_byteops'` is refused even though its first
        # character is a space. The value comes from the environment because
        # make trims a command-line assignment's leading whitespace, which
        # would hide the case. The strip's only observable effect for
        # CHECK_TESTS is this case -- an empty value selects discovery and a
        # bare `-x` is already refused -- so without this test the loop could
        # be deleted and `-x` would still reach unittest as a fail-fast flag.
        env = theme_install.make_env("CHECK_TESTS")
        env["CHECK_TESTS"] = "  -x test_byteops"
        result = theme_install.run_make(["check"], env=env)
        assert_failed(self, result)
        self.assertIn("CHECK_TESTS must name", result.stderr)


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
        env = theme_install.make_env("PYTHON")
        args = ["check"]
        if command_line is not None:
            args.append(f"PYTHON={command_line}")
        if environment is not None:
            env["PYTHON"] = environment
        result = theme_install.run_make(args, env=env)
        assert_failed(self, result)
        self.assertIn("PYTHON must name an interpreter", result.stderr)

    def test_empty_from_the_command_line_is_refused(self):
        self._assert_refused(command_line="")

    def test_empty_from_the_environment_is_refused(self):
        self._assert_refused(environment="")

    def test_leading_dash_is_refused(self):
        self._assert_refused(command_line="-m")

    def test_leading_dash_after_leading_whitespace_is_refused(self):
        # The guard strips leading whitespace before it looks for the leading
        # `-`, so `'  -m'` is refused too. The value comes from the
        # environment because make trims a command-line assignment's leading
        # whitespace, which would hide the case; the whitespace-only case
        # pins the strip's existence, and this pins that it runs before the
        # dash check, so a value that is option-like only after the
        # whitespace cannot reach the recipe as a make flag.
        self._assert_refused(environment="  -m")

    def test_whitespace_only_is_refused(self):
        self._assert_refused(environment=" ")


class TestPythonVersion(unittest.TestCase):
    """`make check`/`check-references` must refuse an unsupported interpreter.

    The fidelity tool uses ``int.bit_count()`` (Python 3.10), so an older
    interpreter fails deep in the suite with an ``AttributeError`` that names
    neither ``PYTHON`` nor the requirement. The guard probes the version once
    and refuses with a diagnostic naming both. The fake interpreter exits
    non-zero for every invocation, so a guard that regresses fails fast instead
    of running the suite under it.
    """

    def _assert_refused(self, target):
        fake = os.path.join(make_tmp_dir(self), "python")
        with open(fake, "w", encoding="utf-8") as handle:
            handle.write("#!/bin/sh\nexit 3\n")
        os.chmod(fake, 0o755)
        env = theme_install.make_env("PYTHON")
        result = theme_install.run_make([target, f"PYTHON={fake}"], env=env)
        assert_failed(self, result)
        self.assertIn("Python 3.10 or newer", result.stderr)
        self.assertIn(fake, result.stderr)

    def test_check_refuses_an_old_interpreter(self):
        self._assert_refused("check")

    def test_check_references_refuses_an_old_interpreter(self):
        self._assert_refused("check-references")


if __name__ == "__main__":
    unittest.main()
