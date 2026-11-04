"""Pin a backlog `_None yet._` placeholder to a genuinely empty section.

A `## ` section's ``_None yet._`` line records "this section holds no
entries", but director commit 11e330eb4 (stamped 2026-11-04) shipped a
contradiction: PLANS.md's `## Planned` carried the placeholder directly above
the inactive-decoration plan heading, so a reader skimming the placeholder
line concludes the queue is empty. These tests fail while a placeholder
claims an empty section that a `### ` entry occupies, and pin the scanner's
exact section boundaries, so the slip cannot hide behind a green
``make check`` again.

The shipped backlogs are pinned both as one pass over both files
(``test_no_placeholder_claims_a_section_that_holds_an_entry``, the
no-observability ledger's reproduction for the `## Planned` slip) and
per file (``test_plans_sections_placeholders_match_their_entries``, the
ledger's reproduction for the `## Planned` claims-the-section-is-empty
record).

Run with the project's check harness (stdlib unittest) via ``make check``.
"""

from __future__ import annotations

import pathlib
import unittest

from support import repo_root

BACKLOG_FILES = ("PLANS.md", "BUGS.md")


def scan_placeholders(lines):
    """Return the ``## `` sections whose ``_None yet._`` line is unfounded.

    A line reading exactly ``_None yet._`` claims the section it sits in holds
    no entries; once a `### ` heading appears in that section, the claim is
    false and the section is reported. The next `## ` heading clears the
    claim, so an empty section's placeholder stays valid across the sections
    that follow it. Sections are reported as ``(section heading,)`` at most
    once, in file order.
    """
    offenders = []
    section = None
    waiting = False
    holds_entry = False
    for line in lines:
        if line.startswith("## "):
            section = line.strip()
            waiting = False
            holds_entry = False
        elif line.startswith("### "):
            holds_entry = True
            if waiting:
                offenders.append((section,))
                waiting = False
        elif line.strip() == "_None yet._":
            if holds_entry:
                offenders.append((section,))
            waiting = True
    return offenders


class TestScanPlaceholders(unittest.TestCase):
    """Pin the scanner's branches against constructed section layouts."""

    def test_a_placeholder_in_an_entryless_section_is_not_reported(self):
        lines = "## Open\n\n_None yet._\n\n## Fixed\n".splitlines()
        self.assertEqual(scan_placeholders(lines), [])

    def test_a_placeholder_directly_above_an_entry_is_reported(self):
        lines = (
            "## Planned\n\n_None yet._\n\n"
            "### A planned entry\n\n## Done\n"
        ).splitlines()
        self.assertEqual(
            scan_placeholders(lines),
            [("## Planned",)],
            "the placeholder claims an empty section an entry occupies",
        )

    def test_a_placeholder_is_cleared_by_the_next_section_heading(self):
        # A `## ` boundary resets the scan: an entry in a later section must
        # not condemn a placeholder left in an earlier, genuinely empty one.
        lines = (
            "## Planned\n\n_None yet._\n\n"
            "## Done\n\n### A done entry\n"
        ).splitlines()
        self.assertEqual(scan_placeholders(lines), [])

    def test_a_placeholder_after_an_entry_in_one_section_is_reported(self):
        lines = (
            "## Planned\n\n### A planned entry\n\n"
            "_None yet._\n\n## Done\n"
        ).splitlines()
        self.assertEqual(scan_placeholders(lines), [("## Planned",)])

    def test_two_placeholders_in_one_section_are_reported_once(self):
        # The section is the offender, not a placeholder line: two stray
        # placeholders in one entry-holding section read as one slip.
        lines = (
            "## Open\n\n_None yet._\n\n"
            "_None yet._\n\n### A bug\n"
        ).splitlines()
        self.assertEqual(scan_placeholders(lines), [("## Open",)])

    def test_a_placeholder_before_any_section_heading_is_not_reported(self):
        # The H1 title and its lines belong to no `## ` section, so a
        # placeholder written under the title has no section to falsify.
        lines = "# Bugs\n\n_None yet._\n\n## Open\n".splitlines()
        self.assertEqual(scan_placeholders(lines), [])


class TestShippedBacklogs(unittest.TestCase):
    """Drive the scan over the tracked PLANS.md and BUGS.md."""

    def _scan(self, name):
        text = (pathlib.Path(repo_root.ROOT) / name).read_text(
            encoding="utf-8"
        )
        return scan_placeholders(text.splitlines())

    def test_plans_sections_placeholders_match_their_entries(self):
        self.assertEqual(
            self._scan("PLANS.md"),
            [],
            "PLANS.md carries a _None yet._ placeholder in a section that "
            "holds ### entries; remove the stale placeholder or fill the "
            "section",
        )

    def test_bugs_sections_placeholders_match_their_entries(self):
        self.assertEqual(
            self._scan("BUGS.md"),
            [],
            "BUGS.md carries a _None yet._ placeholder in a section that "
            "holds ### entries; remove the stale placeholder or fill the "
            "section",
        )

    def test_no_placeholder_claims_a_section_that_holds_an_entry(self):
        for name in BACKLOG_FILES:
            with self.subTest(file=name):
                self.assertEqual(self._scan(name), [])


if __name__ == "__main__":
    unittest.main()
