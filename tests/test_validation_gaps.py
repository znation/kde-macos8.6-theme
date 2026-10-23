"""Pin the validation-gap ledgers and their non-growth.

``tests/support/validation_gaps.py`` maps each surviving ``no-observability``
record to the test that now reproduces its failure offline, each
``unclear-invariant`` record to the test and the ``docs/invariants.md`` row
that now state the guarantee it needed, and each ``no-fake`` record to the test
and fixture that now manufacture the failure. These tests drive the three
ledgers against the shipped ``BUGS.md``/``BUGS-FIXED.md`` archives: every
record must name an entry, every entry must name a real test (and, for
``unclear-invariant``, an existing register guarantee), and each tag's record
count must not exceed its baseline so a new tag fails the suite instead of
growing the gap.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import pathlib
import unittest

from invariants import check_reference, parse_rows
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


class TestNoObservabilityLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = validation_gaps.no_observability(
            validation_gaps.read_gaps(ROOT / "BUGS.md")
            + validation_gaps.read_gaps(ROOT / "BUGS-FIXED.md")
        )

    def test_every_record_names_an_offline_reproduction(self):
        for record in self.records:
            with self.subTest(source=record.source, line=record.line):
                self.assertIsNotNone(
                    validation_gaps.reproduction(record),
                    f"{record.source}:{record.line} is tagged no-observability "
                    "but names no test-side reproduction; add one to "
                    "tests/support/validation_gaps.py instead of growing the "
                    "ledger",
                )

    def test_every_reproduction_names_a_real_test(self):
        for reproduction in validation_gaps.NO_OBSERVABILITY_REPRODUCTIONS:
            with self.subTest(reproduction=reproduction.name):
                check_reference(
                    ROOT,
                    reproduction.reference,
                    f"no-observability:{reproduction.name}",
                )

    def test_every_ledger_entry_covers_a_shipped_record(self):
        # A stale entry would make the ledger read as coverage for a mechanism
        # no archived record names; the reproduction tests above would still
        # pass, so pin the other direction too.
        for reproduction in validation_gaps.NO_OBSERVABILITY_REPRODUCTIONS:
            with self.subTest(reproduction=reproduction.name):
                self.assertTrue(
                    any(
                        validation_gaps.reproduction(record) is reproduction
                        for record in self.records
                    ),
                    f"{reproduction.name} matches no no-observability record",
                )

    def test_the_record_count_does_not_grow(self):
        lines = ", ".join(
            f"{record.source}:{record.line}" for record in self.records
        )
        self.assertLessEqual(
            len(self.records),
            validation_gaps.NO_OBSERVABILITY_BASELINE,
            "the no-observability tag grew past its baseline (records at "
            f"BUGS-FIXED.md lines {lines}); add a test-side reproduction for "
            "the new failure and retire its tag instead of raising "
            "NO_OBSERVABILITY_BASELINE",
        )

    def test_an_unmatched_mechanism_has_no_reproduction(self):
        record = validation_gaps.Gap(
            "no-observability", "bugs.md", 1, "A brand-new failure mode"
        )
        self.assertIsNone(validation_gaps.reproduction(record))


class TestUnclearInvariantLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = validation_gaps.unclear_invariant(
            validation_gaps.read_gaps(ROOT / "BUGS.md")
            + validation_gaps.read_gaps(ROOT / "BUGS-FIXED.md")
        )
        cls.rows = parse_rows(
            containment.read_text(ROOT / "docs" / "invariants.md", ROOT)
        )

    def test_every_record_names_a_register_guarantee_and_test(self):
        for record in self.records:
            with self.subTest(source=record.source, line=record.line):
                self.assertIsNotNone(
                    validation_gaps.reproduction_for(record),
                    f"{record.source}:{record.line} is tagged unclear-invariant "
                    "but names no register guarantee or test; add one to "
                    "tests/support/validation_gaps.py instead of growing the "
                    "ledger",
                )

    def test_every_entry_names_a_real_test(self):
        for entry in validation_gaps.UNCLEAR_INVARIANT_REPRODUCTIONS:
            with self.subTest(entry=entry.name):
                check_reference(
                    ROOT,
                    entry.reference,
                    f"unclear-invariant:{entry.name}",
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

    def test_every_ledger_entry_covers_a_shipped_record(self):
        # A stale entry would make the ledger read as coverage for a mechanism
        # no archived record names; the reproduction tests above would still
        # pass, so pin the other direction too.
        for entry in validation_gaps.UNCLEAR_INVARIANT_REPRODUCTIONS:
            with self.subTest(entry=entry.name):
                self.assertTrue(
                    any(
                        validation_gaps.reproduction_for(record) is entry
                        for record in self.records
                    ),
                    f"{entry.name} matches no unclear-invariant record",
                )

    def test_the_record_count_does_not_grow(self):
        lines = ", ".join(
            f"{record.source}:{record.line}" for record in self.records
        )
        self.assertLessEqual(
            len(self.records),
            validation_gaps.UNCLEAR_INVARIANT_BASELINE,
            "the unclear-invariant tag grew past its baseline (records at "
            f"BUGS-FIXED.md lines {lines}); record its ledger entry, register "
            "row and test, and raise UNCLEAR_INVARIANT_BASELINE by one",
        )

    def test_an_unmatched_mechanism_has_no_reproduction(self):
        record = validation_gaps.Gap(
            "unclear-invariant", "bugs.md", 1, "A brand-new failure mode"
        )
        self.assertIsNone(validation_gaps.reproduction_for(record))


class TestNoFakeLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = validation_gaps.no_fake(
            validation_gaps.read_gaps(ROOT / "BUGS.md")
            + validation_gaps.read_gaps(ROOT / "BUGS-FIXED.md")
        )

    def test_every_record_names_a_reproduction(self):
        for record in self.records:
            with self.subTest(source=record.source, line=record.line):
                self.assertIsNotNone(
                    validation_gaps.reproduction_for(record),
                    f"{record.source}:{record.line} is tagged no-fake but "
                    "names no fixture and reproducing test; add one to "
                    "tests/support/validation_gaps.py instead of growing "
                    "the ledger",
                )

    def test_every_entry_names_a_real_test(self):
        for entry in validation_gaps.NO_FAKE_REPRODUCTIONS:
            with self.subTest(entry=entry.name):
                check_reference(
                    ROOT,
                    entry.reference,
                    f"no-fake:{entry.name}",
                )

    def test_every_ledger_entry_covers_a_shipped_record(self):
        # A stale entry would make the ledger read as coverage for a mechanism
        # no archived record names; the reproduction tests above would still
        # pass, so pin the other direction too.
        for entry in validation_gaps.NO_FAKE_REPRODUCTIONS:
            with self.subTest(entry=entry.name):
                self.assertTrue(
                    any(
                        validation_gaps.reproduction_for(record) is entry
                        for record in self.records
                    ),
                    f"{entry.name} matches no no-fake record",
                )

    def test_the_record_count_does_not_grow(self):
        lines = ", ".join(
            f"{record.source}:{record.line}" for record in self.records
        )
        self.assertLessEqual(
            len(self.records),
            validation_gaps.NO_FAKE_BASELINE,
            "the no-fake tag grew past its baseline (records at "
            f"BUGS-FIXED.md lines {lines}); add the fixture, reproducing test "
            "and ledger entry for the new failure, then raise "
            "NO_FAKE_BASELINE by one",
        )

    def test_an_unmatched_mechanism_has_no_reproduction(self):
        record = validation_gaps.Gap(
            "no-fake", "bugs.md", 1, "A brand-new failure mode"
        )
        self.assertIsNone(validation_gaps.no_fake_reproduction(record))


if __name__ == "__main__":
    unittest.main()
