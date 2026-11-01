"""The tag ledger table and its lookup.

Keeps each tag's reproduction entries and the baseline its record count must
not exceed in one table, so the lookup and the suites cannot disagree about
which entries belong to a tag. A record whose tag or subject matches no entry
has no reproduction, so a new tag cannot borrow another ledger's entries.
"""

from __future__ import annotations

from collections import namedtuple

from support.validation_gaps.no_fake import (
    NO_FAKE_BASELINE,
    NO_FAKE_REPRODUCTIONS,
)
from support.validation_gaps.no_observability import (
    NO_OBSERVABILITY_BASELINE,
    NO_OBSERVABILITY_REPRODUCTIONS,
)
from support.validation_gaps.no_repro import (
    NO_REPRO_BASELINE,
    NO_REPRO_REPRODUCTIONS,
)
from support.validation_gaps.real_run_needed import (
    REAL_RUN_NEEDED_BASELINE,
    REAL_RUN_NEEDED_REPRODUCTIONS,
)
from support.validation_gaps.unclear_invariant import (
    UNCLEAR_INVARIANT_BASELINE,
    UNCLEAR_INVARIANT_REPRODUCTIONS,
)


# Each tag's ledger: its reproduction entries and the baseline its record count
# must not exceed. Keeping both in one table means the lookup and the suites
# cannot disagree about which entries belong to a tag.
Ledger = namedtuple("Ledger", "entries baseline")
LEDGERS = {
    "no-observability": Ledger(
        NO_OBSERVABILITY_REPRODUCTIONS, NO_OBSERVABILITY_BASELINE
    ),
    "unclear-invariant": Ledger(
        UNCLEAR_INVARIANT_REPRODUCTIONS, UNCLEAR_INVARIANT_BASELINE
    ),
    "no-fake": Ledger(NO_FAKE_REPRODUCTIONS, NO_FAKE_BASELINE),
    "real-run-needed": Ledger(
        REAL_RUN_NEEDED_REPRODUCTIONS, REAL_RUN_NEEDED_BASELINE
    ),
    "no-repro": Ledger(NO_REPRO_REPRODUCTIONS, NO_REPRO_BASELINE),
}


def _lookup(record, entries):
    """Return the entry whose markers match *record*, or ``None``."""
    for entry in entries:
        if any(marker in record.subject for marker in entry.markers):
            return entry
    return None


def reproduction_for(record):
    """Return the ledger entry for *record*'s tag, or ``None``.

    A record carrying a tag this module does not ledger (or one whose subject
    matches no entry) has no reproduction, so a new tag cannot borrow another
    ledger's entries. :data:`LEDGERS` names the five ledgers:
    ``no-observability``, ``unclear-invariant``, ``no-fake``,
    ``real-run-needed`` and ``no-repro``.
    """
    ledger = LEDGERS.get(record.tag)
    if ledger is None:
        return None
    return _lookup(record, ledger.entries)
