"""Apply each checker mutation and observe the checker's answer.

``tests/support/checker_mutations.py`` manufactures the malformed register and
theme inputs the shipped data never holds; this module drives them against the
real checkers on a scratch copy of the repository. A rejection mutation must
make the checker raise its named diagnostic; an acceptance mutation must be
kept or found, which ``observe`` pins. Two guards keep each checker's
``REJECTION_SHAPES`` and the mutation table in step: a boundary named in one
list but missing from the other fails here.
"""

from __future__ import annotations

import tempfile
import unittest

from invariants import REJECTION_SHAPES as INVARIANTS_REJECTION_SHAPES
from invariants import cross_check as invariants_cross_check
from support.checker_mutations import (
    INVARIANTS_MUTATIONS,
    PLACEHOLDER_MUTATIONS,
    Scratch,
)
from test_placeholders import REJECTION_SHAPES as PLACEHOLDER_REJECTION_SHAPES
from test_placeholders import cross_check as placeholders_cross_check


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
