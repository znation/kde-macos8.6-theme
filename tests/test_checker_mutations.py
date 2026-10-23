"""Apply each checker mutation and observe the checker's answer.

``tests/support/invariants_mutations.py`` and
``tests/support/placeholders_mutations.py`` manufacture the malformed register
and theme inputs the shipped data never holds; this module drives them against
the real checkers on a scratch copy of the repository. A rejection mutation must
make the checker raise its named diagnostic; an acceptance mutation must be
kept or found, which ``observe`` pins. Two guards keep each checker's
``REJECTION_SHAPES`` and the mutation table in step: a boundary named in one
list but missing from the other fails here.
"""

from __future__ import annotations

import pathlib
import tempfile
import unittest
from unittest import mock

from invariants import REJECTION_SHAPES as INVARIANTS_REJECTION_SHAPES
from invariants import cross_check as invariants_cross_check
from placeholders import REJECTION_SHAPES as PLACEHOLDER_REJECTION_SHAPES
from placeholders import cross_check as placeholders_cross_check
from support import checker_scratch
from support.checker_scratch import Scratch
from support.symlink_fixtures import symlinked_repo
from support.invariants_mutations import INVARIANTS_MUTATIONS
from support.placeholders_mutations import PLACEHOLDER_MUTATIONS


class TestCheckerMutations(unittest.TestCase):
    """Drive the manufactured malformed inputs against the shipped checkers."""

    @classmethod
    def setUpClass(cls):
        # One scratch copy for the whole class; each mutation resets it, so the
        # shipped tests/ tree is copied once instead of once per case.
        tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(tmp.cleanup)
        cls.scratch = Scratch.build(tmp.name)

    def _run(self, mutation, cross_check, register):
        self.scratch.reset()
        mutation.apply(self.scratch)
        if mutation.diagnostic is None:
            cross_check(self.scratch.root, register)
        else:
            with self.assertRaises(AssertionError) as caught:
                cross_check(self.scratch.root, register)
            self.assertRegex(str(caught.exception), mutation.diagnostic)
        if mutation.observe is not None:
            mutation.observe(self.scratch)

    def test_invariants_seed_is_valid(self):
        # Without this, every rejection mutation could "pass" because the seed
        # already failed for an unrelated reason.
        self.scratch.reset()
        invariants_cross_check(self.scratch.root, self.scratch.invariants_register)

    def test_placeholder_seed_is_valid(self):
        self.scratch.reset()
        placeholders_cross_check(self.scratch.root, self.scratch.placeholders_register)

    def test_invariants_mutations(self):
        for mutation in INVARIANTS_MUTATIONS:
            with self.subTest(mutation=mutation.name):
                self._run(
                    mutation, invariants_cross_check, self.scratch.invariants_register
                )

    def test_placeholder_mutations(self):
        for mutation in PLACEHOLDER_MUTATIONS:
            with self.subTest(mutation=mutation.name):
                self._run(
                    mutation, placeholders_cross_check, self.scratch.placeholders_register
                )

    def test_invariants_rejection_shapes_match_the_mutation_table(self):
        names = {m.name for m in INVARIANTS_MUTATIONS if m.diagnostic is not None}
        self.assertEqual(set(INVARIANTS_REJECTION_SHAPES), names)

    def test_placeholder_rejection_shapes_match_the_mutation_table(self):
        names = {m.name for m in PLACEHOLDER_MUTATIONS if m.diagnostic is not None}
        self.assertEqual(set(PLACEHOLDER_REJECTION_SHAPES), names)

    def test_register_reads_refuse_a_symlink_escape(self):
        # A checked-in symlink at a register path would otherwise be read bare
        # and its private text copied into the scratch, where the checker
        # echoes a malformed row's line. `Scratch.build` must refuse it.
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = symlinked_repo(
                tmp, "docs/invariants.md", "private secret line\n"
            )
            (root / "tests").mkdir()
            (root / "theme").mkdir()
            (root / "PLACEHOLDERS.md").write_text("", encoding="utf-8")
            with mock.patch.object(checker_scratch, "ROOT", root), \
                    tempfile.TemporaryDirectory() as scratch_tmp:
                with self.assertRaises(ValueError) as caught:
                    Scratch.build(scratch_tmp)
        self.assertIn("resolves outside", str(caught.exception))
        self.assertNotIn("private secret line", str(caught.exception))

    def test_tests_tree_symlink_outside_the_repository_is_refused(self):
        # ``tests/`` itself can be a checked-in symlink. Dereferencing it
        # would copy an arbitrary directory into the scratch, so the copy
        # must be refused before it starts.
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            root = base / "repo"
            root.mkdir()
            private = base / "private"
            private.mkdir()
            (private / "secret.py").write_text(
                "PRIVATE_SECRET = 'do not copy'\n", encoding="utf-8"
            )
            (root / "tests").symlink_to(private)
            (root / "theme").mkdir()
            (root / "docs").mkdir()
            (root / "docs" / "invariants.md").write_text(
                "", encoding="utf-8"
            )
            (root / "PLACEHOLDERS.md").write_text("", encoding="utf-8")
            with mock.patch.object(checker_scratch, "ROOT", root), \
                    tempfile.TemporaryDirectory() as scratch_tmp:
                with self.assertRaises(ValueError) as caught:
                    Scratch.build(scratch_tmp)
        message = str(caught.exception)
        self.assertIn("resolves outside", message)
        self.assertNotIn("do not copy", message)

    def test_an_inner_tests_symlink_is_preserved_not_dereferenced(self):
        # A symlink inside tests/ that names a private file must be copied as
        # a link; copying its target's bytes would put a private file into
        # the scratch tree, where the checkers treat every path under the
        # scratch root as contained. A mutation that writes the link's name
        # must then be refused rather than following it.
        with tempfile.TemporaryDirectory() as tmp:
            base = pathlib.Path(tmp)
            root = base / "repo"
            root.mkdir()
            private = base / "private.txt"
            private.write_text("private secret line\n", encoding="utf-8")
            absent = base / "absent.txt"
            (root / "tests").mkdir()
            (root / "tests" / "support").mkdir()
            (root / "tests" / "support" / "mutant_module.py").symlink_to(private)
            (root / "tests" / "support" / "repo_root.py").symlink_to(absent)
            (root / "theme").mkdir()
            (root / "docs").mkdir()
            (root / "docs" / "invariants.md").write_text(
                "", encoding="utf-8"
            )
            (root / "PLACEHOLDERS.md").write_text("", encoding="utf-8")
            with mock.patch.object(checker_scratch, "ROOT", root), \
                    tempfile.TemporaryDirectory() as scratch_tmp:
                scratch = Scratch.build(scratch_tmp)
                copied = scratch.root / "tests" / "support" / "mutant_module.py"
                self.assertTrue(copied.is_symlink(), str(copied))
                self.assertEqual(copied.readlink(), private)
                with self.assertRaises(ValueError) as caught:
                    scratch.write_bytes(
                        "tests/support/mutant_module.py", b"overwritten\n"
                    )
                self.assertIn("resolves outside", str(caught.exception))
                self.assertEqual(
                    private.read_text(encoding="utf-8"),
                    "private secret line\n",
                )
                with self.assertRaises(ValueError) as caught:
                    scratch.write_bytes(
                        "tests/support/repo_root.py", b"created\n"
                    )
                self.assertIn("resolves outside", str(caught.exception))
                self.assertFalse(absent.exists())
                # The text writers take the same guard, not only write_bytes.
                with self.assertRaises(ValueError) as caught:
                    scratch.write_repo_file(
                        "tests/support/mutant_module.py", "overwritten\n"
                    )
                self.assertIn("resolves outside", str(caught.exception))
                self.assertEqual(
                    private.read_text(encoding="utf-8"),
                    "private secret line\n",
                )
                with self.assertRaises(ValueError) as caught:
                    scratch.write_repo_file(
                        "tests/support/repo_root.py", "created\n"
                    )
                self.assertIn("resolves outside", str(caught.exception))
                self.assertFalse(absent.exists())
                # write_invariants is a _write caller too; a register that
                # became a link must not be replaced through the link.
                register = scratch.root / "docs" / "invariants.md"
                register.unlink()
                register.symlink_to(private)
                with self.assertRaises(ValueError) as caught:
                    scratch.write_invariants("replaced\n")
                self.assertIn("resolves outside", str(caught.exception))
                self.assertEqual(
                    private.read_text(encoding="utf-8"),
                    "private secret line\n",
                )

    def test_harness_fails_when_the_diagnostic_is_wrong(self):
        # A scratch run with one mutation's expected diagnostic removed must
        # fail; otherwise the harness would pass no matter what the checker
        # raised and would pin nothing.
        mutation = INVARIANTS_MUTATIONS[0]._replace(
            diagnostic="a diagnostic that never appears"
        )
        with self.assertRaises(AssertionError):
            self._run(
                mutation, invariants_cross_check, self.scratch.invariants_register
            )


if __name__ == "__main__":
    unittest.main()
