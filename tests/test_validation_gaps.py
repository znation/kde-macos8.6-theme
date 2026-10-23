"""Pin the ``no-observability`` validation-gap ledger and its non-growth.

``tests/support/validation_gaps.py`` maps each surviving ``no-observability``
record to the test that now reproduces its failure offline. These tests drive
that ledger against the shipped ``BUGS.md``/``BUGS-FIXED.md`` archives: every
record must name a reproduction, every reproduction must name a real test, and
the record count must not exceed the baseline so a new tag fails the suite
instead of growing the gap.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import pathlib
import unittest

from invariants import check_reference
from support import validation_gaps
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


if __name__ == "__main__":
    unittest.main()
