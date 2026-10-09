"""Command-line entry-point tests for tools/check_references.py.

The checker's ``--self-test`` fixtures, the repository check ``main`` runs
with no arguments, and its unknown-argument diagnostic each have their own
exit-status and output contract.
"""

import contextlib
import io
import sys
import unittest
import unittest.mock

from check_references_fixtures import (
    CHECKER,
    ROOT,
    CheckerTestCase,
    good_reference,
    reference_set,
)
from error_assertions import assert_escapes_escape_character
from process_assertions import assert_succeeded
from theme_install import run_captured


def _capture(function, *args):
    """Run *function* with stdout and stderr captured.

    The checker's entry points report through ``print`` -- usage and self-test
    summaries on stdout, problem lists on stderr -- and return their exit
    status. Every test here reads a status beside one of those streams, so
    capture both once and let each test unpack the one it needs.
    """
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        status = function(*args)
    return status, out.getvalue(), err.getvalue()


class TestSelfTestDiagnostics(CheckerTestCase):
    """The self-test's failure output names the failing case, not its image."""

    def test_failure_names_the_case_not_the_last_image(self):
        module = self.checker
        # Force every fixture to fail so _self_test prints its diagnostics.
        module.check_references = lambda directory: ["boom"]
        code, printed, _ = _capture(module._self_test)
        self.assertEqual(code, 1)
        self.assertIn("self-test 'undeclared image'", printed)
        self.assertNotIn("self-test 'extra.png'", printed)


class TestSelfTestPasses(CheckerTestCase):
    """The checker's fixtures must pass under the default `make check`.

    The other tests here mock ``check_references`` (diagnostics) or deny a
    read (error paths), so the core checks -- missing file, duplicate, LFS
    pointer, non-image payload, undeclared image -- run only in the tool's
    built-in self-test, which `make check` does not otherwise invoke.
    """

    def test_built_in_fixtures_all_pass(self):
        module = self.checker
        code, out, _ = _capture(module._self_test)
        self.assertEqual(code, 0, out)


class TestSelfTestExactProblems(CheckerTestCase):
    """A fixture's expected problems must match exactly, not as a subset.

    The self-test once accepted any problem list that merely contained the
    expected substring, so a spurious extra diagnostic for a fixture passed
    unnoticed; the matcher now consumes one distinct problem per expectation
    and rejects anything left over.
    """

    def test_matching_problems_pass(self):
        module = self.checker
        self.assertTrue(
            module._problems_match(
                ["a: bad url", "a: image has no entry"],
                ["bad url", "image has no entry"],
            )
        )

    def test_extra_problem_fails(self):
        module = self.checker
        self.assertFalse(module._problems_match(["bad url", "spurious"], ["bad url"]))

    def test_missing_problem_fails(self):
        module = self.checker
        self.assertFalse(module._problems_match([], ["bad url"]))

    def test_one_expected_substring_consumes_only_one_problem(self):
        module = self.checker
        self.assertFalse(module._problems_match(["bad url"], ["bad", "url"]))


class TestRepositoryCheckEntryPoint(CheckerTestCase):
    """``main`` with no arguments runs the repository reference check.

    The built-in self-test drives only ``--help`` and unknown-argument
    handling, and ``make check`` does not run the opt-in
    ``make check-references``, so the exit status of the repository check was
    unverified: a regression that returned 0 on a broken set would let a
    missing or undeclared image pass silently.
    """

    def _run_no_args(self, module, directory):
        with unittest.mock.patch.object(module, "REFERENCE_DIR", str(directory)):
            return _capture(module.main, [])

    def test_clean_set_exits_zero(self):
        module = self.checker
        with good_reference(module) as root:
            code, out, err = self._run_no_args(module, root)
        self.assertEqual(code, 0, out + err)
        self.assertIn("reference set is consistent", out)
        self.assertEqual(err, "")

    def test_broken_set_exits_one_and_names_each_problem(self):
        module = self.checker
        with reference_set(module, "", {"extra.png": module.PNG_MAGIC}) as root:
            code, out, err = self._run_no_args(module, root)
        self.assertEqual(code, 1, out + err)
        self.assertIn("extra.png", err)
        # One problem takes the singular noun: the summary used to print the
        # literal "1 problem(s)".
        self.assertIn("1 problem in the reference set", err)

    def test_broken_set_counts_problems_in_the_plural(self):
        module = self.checker
        with reference_set(
            module,
            "",
            {"one.png": module.PNG_MAGIC, "two.png": module.PNG_MAGIC},
        ) as root:
            code, out, err = self._run_no_args(module, root)
        self.assertEqual(code, 1, out + err)
        self.assertIn("2 problems in the reference set", err)


class TestArgumentsExcludeProgramName(CheckerTestCase):
    """``main`` takes the argument list without a program name.

    This matches ``tools/fidelity.py`` and ``argparse.parse_args``. Under the
    old convention a caller who passed ``["--help"]`` had the first real
    argument dropped as a program name, so usage was not printed and the
    repository check ran instead.
    """

    def test_help_as_first_argument_prints_usage(self):
        module = self.checker
        code, out, _ = _capture(module.main, ["--help"])
        self.assertEqual(code, 0)
        self.assertIn("usage:", out)


class TestUnknownArgumentEscaping(CheckerTestCase):
    """An unrecognized argument must not print raw control bytes.

    The usage diagnostic joins argv, and a shell glob over the contributor-owned
    screenshot directory can put an ESC-bearing name there, so the message must
    escape it like every other path the tools print.
    """

    def test_unknown_argument_escapes_control_characters(self):
        module = self.checker
        code, _, err = _capture(module.main, ["evil\x1b[31m.png"])
        self.assertEqual(code, 2)
        self.assertIn("unknown argument", err)
        assert_escapes_escape_character(self, err)

    def test_two_unknown_arguments_are_named_in_the_plural(self):
        module = self.checker
        code, _, err = _capture(module.main, ["one", "two"])
        self.assertEqual(code, 2)
        self.assertIn("unknown arguments: one two", err)


class TestScriptEntryPoint(unittest.TestCase):
    """The checker must still run as ``python3 tools/check_references.py``.

    Every other test loads the module through ``importlib`` with the
    repository root on ``sys.path``, so ``from tools.terminal import ...``
    succeeds and the module's ``except ImportError`` direct-run fallback is
    never executed. ``make check-references`` and the README both invoke the
    script by path, where ``sys.path[0]`` is ``tools/`` and ``tools.terminal``
    is not importable, so the fallback is the only thing keeping the
    documented workflow working. Spawn the script to keep it covered.
    """

    def test_self_test_runs_by_path(self):
        result = run_captured(
            [sys.executable, CHECKER, "--self-test"],
            cwd=ROOT,
        )
        assert_succeeded(self, result)
        self.assertIn("cases passed", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
