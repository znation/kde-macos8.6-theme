"""Base class for tests that drive ``support.invariants`` on a synthetic repository.

A temp root holds a ``docs/invariants.md`` register plus test modules that
discovery never collects. Test modules subclass ``InvariantsRegisterTestCase`` for
its fixture and register helpers.
"""

import unittest

from support.invariants import cross_check
from support.theme_install import write_file
from support.tmp_dir import make_tmp_dir


class InvariantsRegisterTestCase(unittest.TestCase):
    """Build a synthetic repository holding a register and test modules."""

    # The synthetic module lives only in the temp root, never in the
    # repository, so its name carries no module suffix or repository
    # directory prefix that a repository path check could try to resolve.
    MODULE = "fake_module"
    # A module with no test case at all, for the bare-file reference check.
    NO_TESTS_MODULE = "no_tests_module"

    def setUp(self):
        self.root = make_tmp_dir(self)
        (self.root / "theme" / "aurorae").mkdir(parents=True)
        self._write(
            self.MODULE,
            "import unittest\n\n\n"
            "class TestFake(unittest.TestCase):\n"
            "    def setUp(self):\n"
            "        pass\n"
            "\n"
            "    def test_ok(self):\n"
            "        pass\n"
            "\n\n"
            "class Helper:\n"
            "    def helper(self):\n"
            "        pass\n"
            "\n\n"
            "class NotATestCase:\n"
            "    def test_looks_like_a_test(self):\n"
            "        pass\n"
            "\n\n"
            "class MixinCase(unittest.TestCase):\n"
            "    pass\n"
            "\n\n"
            "class TestViaMixin(MixinCase):\n"
            "    def test_ok(self):\n"
            "        pass\n"
            "\n\n"
            "class FakeTestCase:\n"
            "    pass\n"
            "\n\n"
            "class TestNotCollected(FakeTestCase):\n"
            "    def test_ok(self):\n"
            "        pass\n",
        )
        self._write(
            self.NO_TESTS_MODULE,
            "class Helper:\n"
            "    def helper(self):\n"
            "        pass\n",
        )

    def _write(self, rel, text):
        return write_file(self.root / rel, text)

    def _register(self, text):
        return str(self._write("docs/invariants.md", text))

    def _table(self, rows):
        lines = ["| Guarantee | Test | Provenance exception |", "| --- | --- | --- |"]
        for guarantee, reference in rows:
            lines.append(f"| {guarantee} | `{reference}` | none |")
        return "\n".join(lines) + "\n"

    def _valid_register(self, aurorae_rows=None):
        return self._register(
            "# Invariants\n\n"
            "## aurorae\n\n"
            + self._table(
                aurorae_rows
                if aurorae_rows is not None
                else [("The aurorae thing holds.", f"{self.MODULE}::TestFake")]
            )
            + "\n## tooling\n\n"
            + self._table(
                [("The gate holds.", f"{self.MODULE}::TestFake::test_ok")]
            )
        )

    def assert_cross_check_rejects(self, reference, message):
        """Assert `cross_check` rejects a register whose row names *reference*.

        The register is otherwise valid, so the failure isolates the
        malformed *reference*, and *message* is a regex the diagnostic must
        match.
        """
        register = self._valid_register([("The thing holds.", reference)])
        with self.assertRaisesRegex(AssertionError, message):
            cross_check(self.root, register)
