"""Pin the validation-gap ledgers and their non-growth.

The ``support.validation_gaps`` package (one module per concern under
``tests/support/validation_gaps/``) maps each surviving ``no-observability``
record to the test that now reproduces its failure offline, each
``unclear-invariant`` record to the test and the ``docs/invariants.md`` row
that now state the guarantee it needed, each ``no-fake`` record to the test
and fixture that now manufacture the failure, each ``real-run-needed``
record to the test that now pins the same bound offline, each ``no-repro``
record to the test that now reproduces it deterministically, and each
``slow-check`` record to the test that now pins its shipped budget or drives
its stub diagnosis offline. These tests drive
the six ledgers against the shipped ``BUGS.md``/``BUGS-FIXED.md`` archives:
every record must name an entry, every entry must name a real test (and, for
``unclear-invariant``, an existing register guarantee), and each tag's record
count must not exceed its baseline so a new tag fails the suite instead of
growing the gap.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import pathlib
import unittest

from support.invariants import check_reference, parse_rows
from support import containment, validation_gaps
from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir


class TestGapParser(unittest.TestCase):
    def _read(self, text):
        directory = make_tmp_dir(self)
        path = pathlib.Path(directory) / "bugs.md"
        path.write_text(text, encoding="utf-8")
        return validation_gaps.read_gaps(path)

    def test_reads_the_prose_form_with_its_heading_as_the_subject(self):
        records = self._read(
            "### A prose bug\n\n"
            "**Validation gap:** no-observability - left no trace.\n"
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].tag, "no-observability")
        self.assertEqual(records[0].line, 3)
        self.assertEqual(records[0].subject, "A prose bug")

    def test_reads_the_bullet_form_with_the_line_as_the_subject(self):
        records = self._read(
            "### An unrelated heading\n\n"
            "- `tests/invariants.py` accepts a bad shape (fixed 2026-10-18; "
            "gap: no-observability)\n"
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].tag, "no-observability")
        self.assertEqual(records[0].line, 3)
        self.assertIn("accepts a bad shape", records[0].subject)

    def test_ignores_other_tags_and_untagged_bullets(self):
        records = self._read(
            "**Validation gap:** no-fake - needed a fixture.\n"
            "- an untagged bullet (fixed 2026-10-18)\n"
            "- a tagged bullet (fixed 2026-10-18; gap: unclear-invariant)\n"
        )
        self.assertEqual([record.tag for record in records], ["no-fake", "unclear-invariant"])

    def test_a_prose_line_with_a_trailing_bullet_tag_is_read_once_as_prose(self):
        # A prose record that happens to end with the older bullet's
        # ``; gap: <tag>)`` spelling must be read once, with the prose tag and
        # the nearest heading as its subject: read_gaps' prose match comes
        # first and then skips the line. Counting both a bullet record under
        # the second tag would attribute the prose record to a ledger it
        # does not belong to, and double-counting the line would push the
        # tag's record count past each ledger's non-growth baseline.
        records = self._read(
            "### A hybrid record\n\n"
            "**Validation gap:** no-fake - needed a fixture "
            "(fixed 2026-10-27; gap: no-repro)\n"
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].tag, "no-fake")
        self.assertEqual(records[0].subject, "A hybrid record")
        self.assertEqual(
            [record.tag for record in validation_gaps.tagged(records, "no-repro")],
            [],
        )


class _LedgerMixin:
    """Drive one validation-gap tag's ledger against the shipped archives.

    Subclasses set ``tag`` and the advice their diagnostics give; the inherited
    tests pin every record to an entry, every entry to a real test and a
    shipped record, and the tag's record count to its baseline.
    """

    tag = ""
    missing_advice = ""
    growth_advice = ""

    @classmethod
    def setUpClass(cls):
        records = (
            validation_gaps.read_gaps(ROOT / "BUGS.md")
            + validation_gaps.read_gaps(ROOT / "BUGS-FIXED.md")
        )
        cls.records = validation_gaps.tagged(records, cls.tag)

    def test_every_record_names_a_reproduction(self):
        for record in self.records:
            with self.subTest(source=record.source, line=record.line):
                self.assertIsNotNone(
                    validation_gaps.reproduction_for(record),
                    f"{record.source}:{record.line} is tagged {self.tag} "
                    f"but names no reproduction; {self.missing_advice} "
                    "instead of growing the ledger",
                )

    def test_every_entry_names_a_real_test(self):
        for entry in validation_gaps.LEDGERS[self.tag].entries:
            with self.subTest(entry=entry.name):
                check_reference(
                    ROOT,
                    entry.reference,
                    f"{self.tag}:{entry.name}",
                )

    def test_every_ledger_entry_covers_a_shipped_record(self):
        # A stale entry would make the ledger read as coverage for a mechanism
        # no archived record names; the reproduction tests above would still
        # pass, so pin the other direction too.
        for entry in validation_gaps.LEDGERS[self.tag].entries:
            with self.subTest(entry=entry.name):
                self.assertTrue(
                    any(
                        validation_gaps.reproduction_for(record) is entry
                        for record in self.records
                    ),
                    f"{entry.name} matches no {self.tag} record",
                )

    def test_the_record_count_does_not_grow(self):
        lines = ", ".join(
            f"{record.source}:{record.line}" for record in self.records
        )
        self.assertLessEqual(
            len(self.records),
            validation_gaps.LEDGERS[self.tag].baseline,
            f"the {self.tag} tag grew past its baseline (records at "
            f"BUGS-FIXED.md lines {lines}); {self.growth_advice}",
        )

    def test_an_unmatched_mechanism_has_no_reproduction(self):
        record = validation_gaps.Gap(
            self.tag, "bugs.md", 1, "A brand-new failure mode"
        )
        self.assertIsNone(validation_gaps.reproduction_for(record))


class TestReproductionLookup(unittest.TestCase):
    """Pin reproduction_for's branches the real-archive suites do not reach.

    The prose matcher accepts any lowercase tag, so a tag name with no
    shipped ledger can reach read_gaps; its lookup must refuse that record
    rather than lend another ledger's entry, and a record must match an entry
    through any one of its markers, not all of them.
    """

    def test_a_foreign_tag_borrows_no_ledger_entry(self):
        # build the subject from a shipped entry's first marker, so a lookup
        # that ignores the tag would find that entry; the refusal is what we
        # pin.
        subject = validation_gaps.NO_OBSERVABILITY_REPRODUCTIONS[0].markers[0]
        # Every shipped tag now has a ledger, so the foreign tag here is one
        # that no ledger covers yet (rename it again if such a tag ever
        # becomes a real concern).
        record = validation_gaps.Gap("future-tag", "bugs.md", 1, subject)
        self.assertIsNone(validation_gaps.reproduction_for(record))

    def test_any_single_marker_of_an_entry_identifies_its_record(self):
        entry = validation_gaps.Reproduction(
            "synthetic",
            ("marker one", "marker two"),
            "tests/test_validation_gaps.py"
            "::TestReproductionLookup"
            "::test_any_single_marker_of_an_entry_identifies_its_record",
        )
        ledger = validation_gaps.Ledger((entry,), 0)
        original = validation_gaps.LEDGERS["no-observability"]
        validation_gaps.LEDGERS["no-observability"] = ledger
        self.addCleanup(
            validation_gaps.LEDGERS.__setitem__,
            "no-observability",
            original,
        )
        record = validation_gaps.Gap(
            "no-observability", "bugs.md", 1, "the record cites marker two"
        )
        self.assertIs(validation_gaps.reproduction_for(record), entry)


HEADER_TAGS = frozenset(
    {
        "none",
        "no-repro",
        "no-fake",
        "real-run-needed",
        "no-observability",
        "slow-check",
        "unclear-invariant",
    }
)
"""The seven validation-gap tags this file's header contract names.

The ledger modules treat ``LEDGERS``' six tags as complete and reserve
``none`` for records the existing suite reproduces, so any other tag in an
archive is a bespoke tag that borrows no ledger and evades every cap.
"""


class TestArchiveVocabulary(unittest.TestCase):
    """Pin the archived records to the header's seven tags.

    ``read_gaps``' matchers accept any lowercase tag word, so a record whose
    tag is not one of the seven header tags sails past every ledger entry
    match, every baseline and every tally: a bespoke tag ships with no
    reproduction and no bounded count. This test reads the shipped archives
    themselves, so a foreign tag fails here in the commit that adds it, and
    a re-tag (or an extended ledger with a named entry) must land in the
    same change.
    """

    def test_every_archived_record_carries_a_header_tag(self):
        foreign = [
            (record.source, record.line, record.tag)
            for archive in ("BUGS.md", "BUGS-FIXED.md")
            for record in validation_gaps.read_gaps(ROOT / archive)
            if record.tag not in HEADER_TAGS
        ]
        self.assertFalse(
            foreign,
            "archived validation-gap records carry tags outside the "
            "header's seven (expected "
            + ", ".join(sorted(HEADER_TAGS))
            + "): found "
            + ", ".join("%s:%d %r" % beyond for beyond in foreign)
            + "; re-tag to the closest header tag in the same change",
        )

    def test_the_ledgers_cover_every_header_tag_but_none(self):
        # `none` is a header tag for records the existing suite reproduces,
        # so it needs no ledger; every other header tag must have one, so
        # the ledger modules cannot drift from the tag contract.
        self.assertEqual(
            frozenset(validation_gaps.LEDGERS),
            HEADER_TAGS - {"none"},
        )


class TestNoObservabilityLedger(_LedgerMixin, unittest.TestCase):
    tag = "no-observability"
    missing_advice = "add a test-side reproduction for the new failure"
    growth_advice = (
        "add a test-side reproduction for the new failure and retire its tag "
        "instead of raising NO_OBSERVABILITY_BASELINE"
    )


class TestUnclearInvariantLedger(_LedgerMixin, unittest.TestCase):
    tag = "unclear-invariant"
    missing_advice = (
        "add the register guarantee, test and ledger entry for the new failure"
    )
    growth_advice = (
        "record its ledger entry, register row and test, and raise "
        "UNCLEAR_INVARIANT_BASELINE by one"
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rows = parse_rows(
            containment.read_text(ROOT / "docs" / "invariants.md", ROOT)
        )

    def test_every_entry_names_a_register_guarantee(self):
        guarantees = [
            row.guarantee for rows in self.rows.values() for row in rows
        ]
        for entry in validation_gaps.UNCLEAR_INVARIANT_REPRODUCTIONS:
            with self.subTest(entry=entry.name):
                self.assertTrue(
                    entry.guarantee,
                    f"{entry.name} names no guarantee text",
                )
                self.assertTrue(
                    any(entry.guarantee in text for text in guarantees),
                    f"{entry.name} names a guarantee no docs/invariants.md "
                    "row states",
                )


class TestNoFakeLedger(_LedgerMixin, unittest.TestCase):
    tag = "no-fake"
    missing_advice = "add its fixture and reproducing test"
    growth_advice = (
        "add the fixture, reproducing test and ledger entry for the new "
        "failure, then raise NO_FAKE_BASELINE by one"
    )


class TestRealRunNeededLedger(_LedgerMixin, unittest.TestCase):
    tag = "real-run-needed"
    missing_advice = "pin the same bound in a test and add its ledger entry"
    growth_advice = (
        "pin the failure's bound in an offline test and add its ledger entry "
        "instead of raising REAL_RUN_NEEDED_BASELINE"
    )


class TestNoReproLedger(_LedgerMixin, unittest.TestCase):
    tag = "no-repro"
    missing_advice = (
        "make the failure deterministic in a test and add its ledger entry"
    )
    growth_advice = (
        "make the failure deterministic in a test and add its ledger entry "
        "instead of raising NO_REPRO_BASELINE"
    )


class TestSlowCheckLedger(_LedgerMixin, unittest.TestCase):
    tag = "slow-check"
    missing_advice = (
        "pin the shipped budget or drive the stub diagnosis offline in a "
        "test and add its ledger entry"
    )
    growth_advice = (
        "add the offline reproduction and ledger entry for the new failure "
        "instead of raising SLOW_CHECK_BASELINE"
    )


if __name__ == "__main__":
    unittest.main()
