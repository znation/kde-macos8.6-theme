"""Direct tests for tests/support/checker_scratch.py's seeded scratch repository.

``tests/test_checker_mutations.py`` applies each mutation and observes only the
checker's answer. If :meth:`Scratch.reset` forgot to remove or restore a
mutation's write, a later mutation could pass or fail for the wrong reason with
no failing assertion naming the scratch. These tests pin the reset contract on
its own: a written file, directory or symlink disappears, and a seeded file
that a mutation overwrote gets its shipped bytes back.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import os
import tempfile
import unittest

from support.checker_scratch import (
    INVARIANTS_REGISTER,
    PLACEHOLDERS_REGISTER,
    Scratch,
)

# A fixture module the shipped tests tree carries; the mutation table
# overwrites it with undecodable bytes, which reset must undo.
MUTANT_MODULE = os.path.join("tests", "support", "mutant_module.py")


class ScratchCase(unittest.TestCase):
    """Build one scratch copy for the class and reset it before each test."""

    @classmethod
    def setUpClass(cls):
        # Copying the tests tree is the expensive part; each test resets the
        # copy instead of building its own.
        cls._tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls._tmp.cleanup)
        cls.scratch = Scratch.build(cls._tmp.name)

    def setUp(self):
        self.scratch.reset()

    def path(self, rel):
        """Return the scratch root's path for *rel*."""
        return self.scratch.root / rel


class TestBuild(ScratchCase):
    def test_seeds_both_registers_and_copies_the_tests_tree(self):
        self.assertEqual(
            self.scratch.invariants_text, self.scratch.read_invariants()
        )
        self.assertEqual(
            self.scratch.placeholders_text,
            self.path(PLACEHOLDERS_REGISTER).read_text(encoding="utf-8"),
        )
        self.assertTrue(self.path(MUTANT_MODULE).is_file())
        self.assertEqual(
            self.scratch.invariants_register, str(self.path(INVARIANTS_REGISTER))
        )
        self.assertEqual(
            self.scratch.placeholders_register,
            str(self.path(PLACEHOLDERS_REGISTER)),
        )


class TestResetRemovesWhatAMutationWrote(ScratchCase):
    def test_removes_a_written_file(self):
        rel = os.path.join("theme", "extra.svg")
        self.scratch.write_repo_file(rel, "<svg/>")
        written = self.path(rel)
        self.assertTrue(written.is_file())

        self.scratch.reset()

        self.assertFalse(written.exists())

    def test_removes_a_written_directory(self):
        self.scratch.write_directory("theme/extra")
        written = self.path("theme/extra")
        self.assertTrue(written.is_dir())

        self.scratch.reset()

        self.assertFalse(written.exists())

    def test_removes_a_written_symlink(self):
        rel = os.path.join("theme", "link.svg")
        self.scratch.write_symlink(rel, "missing.svg")
        link = self.path(rel)
        self.assertTrue(link.is_symlink())

        self.scratch.reset()

        self.assertFalse(link.is_symlink())
        self.assertFalse(link.exists())


class TestResetRestoresSeededFiles(ScratchCase):
    def test_restores_a_repository_file_a_mutation_overwrote(self):
        target = self.path(MUTANT_MODULE)
        original = target.read_bytes()
        self.scratch.write_bytes(MUTANT_MODULE, b"\xff\xfe\x00")
        self.assertEqual(b"\xff\xfe\x00", target.read_bytes())

        self.scratch.reset()

        self.assertEqual(original, target.read_bytes())

    def test_restores_an_invariants_register_a_mutation_replaced(self):
        self.scratch.write_invariants("REPLACED\n")
        self.assertEqual("REPLACED\n", self.scratch.read_invariants())

        self.scratch.reset()

        self.assertEqual(self.scratch.invariants_text, self.scratch.read_invariants())

    def test_restores_a_register_a_mutation_replaced_with_a_directory(self):
        register = self.path(PLACEHOLDERS_REGISTER)
        self.scratch.write_directory(PLACEHOLDERS_REGISTER)
        self.assertTrue(register.is_dir())

        self.scratch.reset()

        self.assertTrue(register.is_file())
        self.assertEqual(
            self.scratch.placeholders_text, register.read_text(encoding="utf-8")
        )


if __name__ == "__main__":
    unittest.main()
