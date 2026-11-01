"""Read the validation-gap tags in BUGS.md/BUGS-FIXED.md and their offline tests.

Every Fixed bug records a ``**Validation gap:**`` tag, or (for the older
one-line bullets) a trailing ``; gap: <tag>``. The ``no-observability`` tag
marked a failure that left no trace the suite could see, so it could not be
confirmed until instrumentation was added; its records now have test-side
reproductions. The ``unclear-invariant`` tag marked a guarantee the code or
register left unstated or unpinned; its records now name the test and register
row that state it. The ``no-fake`` tag marked a failure whose confirmation
needed a fake, shim or manufactured fixture the suite did not have; its records
now name the fixture and the test that builds it. The ``real-run-needed``
tag marked a failure the suite could only confirm with a bounded real run
(a memory limit, a live KDE session); its records now name the offline test
that pins the same bound. The ``no-repro`` tag marked a failure that was not
deterministic when filed; its records now name the test that makes it
deterministic. This package turns all five into a structured ledger
that maps each mechanism to the test that confirms it offline, and refuses a
record that names no reproduction.
``tests/test_validation_gaps.py`` drives the ledgers and caps each tag's count
at its baseline, so a new unrecorded tag fails the suite instead of silently
growing the gap.

The package is split by concern and re-exported here, so a test module imports
every public name from ``validation_gaps`` regardless of which submodule
defines it: ``records`` holds the shared ``Gap`` and ``Reproduction`` record
types, ``reader`` parses the archives' records, the five per-tag modules
(``no_observability``, ``unclear_invariant``, ``no_fake``, ``real_run_needed``
and ``no_repro``) hold each ledger's reproduction entries and baseline, and
``ledgers`` maps every tag to its entries in one table.
"""

from __future__ import annotations

from .ledgers import (
    LEDGERS,
    Ledger,
    reproduction_for,
)
from .no_fake import (
    NO_FAKE_BASELINE,
    NO_FAKE_REPRODUCTIONS,
)
from .no_observability import (
    NO_OBSERVABILITY_BASELINE,
    NO_OBSERVABILITY_REPRODUCTIONS,
)
from .no_repro import (
    NO_REPRO_BASELINE,
    NO_REPRO_REPRODUCTIONS,
)
from .reader import read_gaps, tagged
from .real_run_needed import (
    REAL_RUN_NEEDED_BASELINE,
    REAL_RUN_NEEDED_REPRODUCTIONS,
)
from .records import Gap, Reproduction
from .unclear_invariant import (
    UNCLEAR_INVARIANT_BASELINE,
    UNCLEAR_INVARIANT_REPRODUCTIONS,
    UnclearInvariant,
)

__all__ = [
    "LEDGERS",
    "Ledger",
    "NO_FAKE_BASELINE",
    "NO_FAKE_REPRODUCTIONS",
    "NO_OBSERVABILITY_BASELINE",
    "NO_OBSERVABILITY_REPRODUCTIONS",
    "NO_REPRO_BASELINE",
    "NO_REPRO_REPRODUCTIONS",
    "REAL_RUN_NEEDED_BASELINE",
    "REAL_RUN_NEEDED_REPRODUCTIONS",
    "UNCLEAR_INVARIANT_BASELINE",
    "UNCLEAR_INVARIANT_REPRODUCTIONS",
    "Gap",
    "Reproduction",
    "UnclearInvariant",
    "read_gaps",
    "reproduction_for",
    "tagged",
]
