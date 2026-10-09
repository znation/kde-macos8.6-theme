"""Command-line entry-point tests for tools/check_references.py.

The checker's ``--self-test`` fixtures, the repository check ``main`` runs
with no arguments, and its unknown-argument diagnostic each have their own
exit-status and output contract.
"""

import contextlib
import io
import unittest
import unittest.mock

from check_references_fixtures import good_reference, load_checker, reference_set


class TestSelfTestDiagnostics(unittest.TestCase):
    """The self-test's failure output names the failing case, not its image."""

    def test_failure_names_the_case_not_the_last_image(self):
        module = load_checker()
        # Force every fixture to fail so _self_test prints its diagnostics.
        module.check_references = lambda directory: ["boom"]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = module._self_test()
        self.assertEqual(code, 1)
        printed = out.getvalue()
        self.assertIn("self-test 'undeclared image'", printed)
        self.assertNotIn("self-test 'extra.png'", printed)


class TestSelfTestPasses(unittest.TestCase):
    """The checker's fixtures must pass under the default `make check`.

    The other tests here mock ``check_references`` (diagnostics) or deny a
    read (error paths), so the core checks -- missing file, duplicate, LFS
    pointer, non-image payload, undeclared image -- run only in the tool's
    built-in self-test, which `make check` does not otherwise invoke.
    """

    def test_built_in_fixtures_all_pass(self):
        module = load_checker()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = module._self_test()
        self.assertEqual(code, 0, out.getvalue())


class TestSelfTestExactProblems(unittest.TestCase):
    """A fixture's expected problems must match exactly, not as a subset.

    The self-test once accepted any problem list that merely contained the
    expected substring, so a spurious extra diagnostic for a fixture passed
    unnoticed; the matcher now consumes one distinct problem per expectation
    and rejects anything left over.
    """

    def test_matching_problems_pass(self):
        module = load_checker()
        self.assertTrue(
            module._problems_match(
                ["a: bad url", "a: image has no entry"],
                ["bad url", "image has no entry"],
            )
        )

    def test_extra_problem_fails(self):
        module = load_checker()
        self.assertFalse(module._problems_match(["bad url", "spurious"], ["bad url"]))

    def test_missing_problem_fails(self):
        module = load_checker()
        self.assertFalse(module._problems_match([], ["bad url"]))

    def test_one_expected_substring_consumes_only_one_problem(self):
        module = load_checker()
        self.assertFalse(module._problems_match(["bad url"], ["bad", "url"]))


class TestRepositoryCheckEntryPoint(unittest.TestCase):
    """``main`` with no arguments runs the repository reference check.

    The built-in self-test drives only ``--help`` and unknown-argument
    handling, and ``make check`` does not run the opt-in
    ``make check-references``, so the exit status of the repository check was
    unverified: a regression that returned 0 on a broken set would let a
    missing or undeclared image pass silently.
    """

    def _run_no_args(self, module, directory):
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.object(module, "REFERENCE_DIR", str(directory)):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = module.main([])
        return code, out.getvalue(), err.getvalue()

    def test_clean_set_exits_zero(self):
        module = load_checker()
        with good_reference(module) as root:
            code, out, err = self._run_no_args(module, root)
        self.assertEqual(code, 0, out + err)
        self.assertIn("reference set is consistent", out)
        self.assertEqual(err, "")

    def test_broken_set_exits_one_and_names_each_problem(self):
        module = load_checker()
        with reference_set(module, "", {"extra.png": module.PNG_MAGIC}) as root:
            code, out, err = self._run_no_args(module, root)
        self.assertEqual(code, 1, out + err)
        self.assertIn("extra.png", err)
        # One problem takes the singular noun: the summary used to print the
        # literal "1 problem(s)".
        self.assertIn("1 problem in the reference set", err)

    def test_broken_set_counts_problems_in_the_plural(self):
        module = load_checker()
        with reference_set(
            module,
            "",
            {"one.png": module.PNG_MAGIC, "two.png": module.PNG_MAGIC},
        ) as root:
            code, out, err = self._run_no_args(module, root)
        self.assertEqual(code, 1, out + err)
        self.assertIn("2 problems in the reference set", err)


class TestArgumentsExcludeProgramName(unittest.TestCase):
    """``main`` takes the argument list without a program name.

    This matches ``tools/fidelity.py`` and ``argparse.parse_args``. Under the
    old convention a caller who passed ``["--help"]`` had the first real
    argument dropped as a program name, so usage was not printed and the
    repository check ran instead.
    """

    def test_help_as_first_argument_prints_usage(self):
        module = load_checker()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = module.main(["--help"])
        self.assertEqual(code, 0)
        self.assertIn("usage:", out.getvalue())


class TestUnknownArgumentEscaping(unittest.TestCase):
    """An unrecognized argument must not print raw control bytes.

    The usage diagnostic joins argv, and a shell glob over the contributor-owned
    screenshot directory can put an ESC-bearing name there, so the message must
    escape it like every other path the tools print.
    """

    def test_unknown_argument_escapes_control_characters(self):
        module = load_checker()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = module.main(["evil\x1b[31m.png"])
        self.assertEqual(code, 2)
        self.assertIn("unknown argument", err.getvalue())
        self.assertNotIn("\x1b", err.getvalue())
        self.assertIn("\\u001b", err.getvalue())

    def test_two_unknown_arguments_are_named_in_the_plural(self):
        module = load_checker()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = module.main(["one", "two"])
        self.assertEqual(code, 2)
        self.assertIn("unknown arguments: one two", err.getvalue())


if __name__ == "__main__":
    unittest.main()
