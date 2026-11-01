"""The archived validation-gap record reader.

Parses every ``**Validation gap:**`` record (and the older one-line ``;
gap:`` bullet) in ``BUGS.md``/``BUGS-FIXED.md`` into a :class:`~.records.Gap`
record, so the ledgers in the sibling tag modules reference the archive's
records by tag and subject instead of hand-maintained paths.
"""

from __future__ import annotations

import re

from support import containment
from support.repo_root import ROOT

from .records import Gap

PROSE_GAP = re.compile(r"^\*\*Validation gap:\*\*\s+(?P<tag>[a-z][a-z-]*)")
BULLET_GAP = re.compile(r";\s*gap:\s*(?P<tag>[a-z][a-z-]*)\)\s*$")
HEADING = re.compile(r"^###\s+(?P<title>.+?)\s*$")


def read_gaps(path, root=ROOT):
    """Return every validation-gap record in *path* as a list of :class:`Gap`.

    The prose form's subject is the nearest preceding ``###`` heading; the
    bullet form's subject is its own text, because the archived one-line
    records sit below an unrelated heading. *path* and *root* are passed to the
    shared containment reader, so a symlinked register or a FIFO is refused by
    name instead of leaking or blocking.
    """
    text = containment.read_text(path, root)
    records = []
    heading = ""
    for number, line in enumerate(text.splitlines(), 1):
        match = HEADING.match(line)
        if match:
            heading = match.group("title")
        match = PROSE_GAP.match(line)
        if match:
            records.append(
                Gap(match.group("tag"), str(path), number, heading)
            )
            continue
        match = BULLET_GAP.search(line)
        if match:
            records.append(
                Gap(match.group("tag"), str(path), number, line.strip())
            )
    return records


def tagged(records, tag):
    """Return the subset of *records* tagged *tag*."""
    return [record for record in records if record.tag == tag]
