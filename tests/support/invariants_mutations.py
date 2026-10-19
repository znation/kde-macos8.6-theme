"""The invariant register checker's mutation table.

``tests/invariants.py``'s register parser and reference resolver enforces a
boundary the shipped data happens not to cross. Each mutation here derives one
named boundary from a copy of the real register, so
``tests/test_checker_mutations.py`` can apply it and observe the checker's
answer instead of waiting for a reader. :mod:`support.checker_scratch` holds
the shared scratch copy and the :data:`~support.checker_scratch.Mutation`
record.

A mutation's ``diagnostic`` is the substring the checker's ``AssertionError``
must contain; a mutation with a diagnostic is a rejection boundary and must be
named in ``tests/invariants.py``'s ``REJECTION_SHAPES``. ``None`` marks an
acceptance boundary, where the checker must keep the input and ``observe``
pins what it must produce -- the escaped pipe is accepted, not rejected, so no
diagnostic exists to match.
"""

from __future__ import annotations

import re

from support.checker_scratch import Mutation

# The shipped files the reference mutations point the register's first row at.
# ``MUTANT_MODULE`` is a fixture, not a test module: unittest collects nothing
# from it, and it holds the class shapes the shipped tests never define.
# ``HARNESS_MODULE`` holds a real collected test case. Both are literal
# repository paths that exist in the tree, so the stage self-check's
# added-nonexistent-path guard sees them and passes on its own terms instead of
# the harness hiding them behind a ``./`` prefix or a runtime join.
MUTANT_MODULE = "tests/support/mutant_module.py"
HARNESS_MODULE = "tests/test_checker_mutations.py"

_REFERENCE = re.compile(r"`([^`]+)`")


def _first_data_row(text):
    """Return the first table row line that carries a test reference."""
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("|") and _REFERENCE.search(line):
            return line
    raise AssertionError("no table row carries a test reference")


def _replace_first_reference(text, reference):
    """Return *text* with the first row's backticked reference replaced."""
    line = _first_data_row(text)
    match = _REFERENCE.search(line)
    mutated = line[: match.start(1)] + reference + line[match.end(1):]
    return text.replace(line, mutated, 1)


def _replace_first_guarantee(text, guarantee):
    """Return *text* with the first row's Guarantee cell replaced."""
    line = _first_data_row(text)
    cells = line.rstrip("\n").split("|")
    cells[1] = f" {guarantee} "
    return text.replace(line, "|".join(cells) + "\n", 1)


def _drop_first_row_cell(text):
    """Return *text* with the first row's Provenance cell removed (two cells)."""
    line = _first_data_row(text)
    cells = line.rstrip("\n").split("|")
    del cells[-2]
    return text.replace(line, "|".join(cells) + "\n", 1)


def _strip_first_row_backticks(text):
    """Return *text* with the first row's backticks removed (no test named)."""
    line = _first_data_row(text)
    return text.replace(line, line.replace("`", ""), 1)


def _reference_apply(reference):
    """Return an ``apply`` that points the first register row at *reference*."""

    def apply(scratch):
        scratch.write_invariants(
            _replace_first_reference(scratch.invariants_text, reference)
        )

    return apply


def _apply_malformed_row(scratch):
    scratch.write_invariants(_drop_first_row_cell(scratch.invariants_text))


def _apply_test_cell_without_reference(scratch):
    scratch.write_invariants(_strip_first_row_backticks(scratch.invariants_text))


def _apply_unreadable_test_file(scratch):
    """Point the first row at a scratch copy of a module made undecodable.

    ``MUTANT_MODULE`` is a repository path that exists, so the stage
    self-check's added-nonexistent-path guard stays satisfied; ``write_bytes``
    overwrites the scratch copy (``reset`` restores it) with bytes no UTF-8
    decode accepts, so the checker's decode arm fires by name.
    """
    scratch.write_bytes(MUTANT_MODULE, b"\xff\xfe\x00")
    scratch.write_invariants(
        _replace_first_reference(scratch.invariants_text, MUTANT_MODULE)
    )


def _apply_escaped_pipe(scratch):
    scratch.write_invariants(
        _replace_first_guarantee(
            scratch.invariants_text, "The active \\| inactive title-bar boxes hold."
        )
    )


def _observe_escaped_pipe(scratch):
    from invariants import parse_rows

    sections = parse_rows(scratch.read_invariants())
    guarantees = [row.guarantee for rows in sections.values() for row in rows]
    if not any("|" in guarantee for guarantee in guarantees):
        raise AssertionError(
            "escaped-pipe row was dropped: no parsed guarantee kept a literal pipe"
        )


INVARIANTS_MUTATIONS = (
    Mutation(
        "local-base-that-only-looks-like-a-test-case",
        _reference_apply(MUTANT_MODULE + "::TestNotCollected::test_ok"),
        "names a class that is not a test case",
        None,
    ),
    Mutation(
        "reference-outside-repository",
        _reference_apply("../outside/mutant_module.py::TestReal"),
        "outside the repository",
        None,
    ),
    Mutation(
        "method-on-non-test-case-class",
        _reference_apply(MUTANT_MODULE + "::NotATestCase::test_looks_like_a_test"),
        "names a class that is not a test case",
        None,
    ),
    Mutation(
        "reference-to-non-test-case-class",
        _reference_apply(MUTANT_MODULE + "::Helper"),
        "names a class that is not a test case",
        None,
    ),
    Mutation(
        "non-test-method",
        _reference_apply(HARNESS_MODULE + "::TestCheckerMutations::setUpClass"),
        "names a method that is not a test",
        None,
    ),
    Mutation(
        "trailing-segment",
        _reference_apply(
            HARNESS_MODULE + "::TestCheckerMutations::test_invariants_mutations::junk"
        ),
        "names more than a class and method",
        None,
    ),
    Mutation(
        "empty-qualifier",
        _reference_apply(MUTANT_MODULE + "::"),
        "names no class or method",
        None,
    ),
    Mutation("malformed-row", _apply_malformed_row, "malformed table row", None),
    Mutation(
        "test-cell-without-reference",
        _apply_test_cell_without_reference,
        "no test reference",
        None,
    ),
    Mutation(
        "reference-with-nul-byte",
        _reference_apply("tests/\x00mutant.py"),
        "NUL byte",
        None,
    ),
    Mutation(
        "unreadable-test-file",
        _apply_unreadable_test_file,
        "cannot be read as Python",
        None,
    ),
    Mutation("escaped-pipe", _apply_escaped_pipe, None, _observe_escaped_pipe),
)
