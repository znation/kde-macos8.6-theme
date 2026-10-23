"""Read the validation-gap tags in BUGS.md/BUGS-FIXED.md and their offline tests.

Every Fixed bug records a ``**Validation gap:**`` tag, or (for the older
one-line bullets) a trailing ``; gap: <tag>``. The ``no-observability`` tag
marked a failure that left no trace the suite could see, so it could not be
confirmed until instrumentation was added. The records that used it now have
test-side reproductions; this module turns them into a structured ledger that
maps each mechanism to the test that confirms it offline, and refuses a record
that names no reproduction. ``tests/test_validation_gaps.py`` drives the ledger
and caps the count at its 21-record baseline, so a new ``no-observability`` tag fails the suite instead
of silently growing the gap.
"""

from __future__ import annotations

import re
from collections import namedtuple

from support import containment
from support.repo_root import ROOT

PROSE_GAP = re.compile(r"^\*\*Validation gap:\*\*\s+(?P<tag>[a-z][a-z-]*)")
BULLET_GAP = re.compile(r";\s*gap:\s*(?P<tag>[a-z][a-z-]*)\)\s*$")
HEADING = re.compile(r"^###\s+(?P<title>.+?)\s*$")

# One parsed validation-gap record. ``subject`` is the bug's heading for the
# prose form and the bullet's own text for the older one-line form.
Gap = namedtuple("Gap", "tag source line subject")

# One mechanism's offline reproduction: the record markers that identify it
# and the test reference that confirms the failure without a real run.
Reproduction = namedtuple("Reproduction", "name markers reference")

# The number of ``no-observability`` records the archive held when the ledger
# landed. A new record must be retired with a test instead of raising this.
NO_OBSERVABILITY_BASELINE = 21

NO_OBSERVABILITY_REPRODUCTIONS = (
    Reproduction(
        "gtk-remove-data-home",
        ("apply_gtk --remove",),
        "tests/test_gtk_apply.py::TestRemove"
        "::test_remove_clears_the_selection_without_a_resolvable_data_home",
    ),
    Reproduction(
        "aurorae-reader-fifo",
        ("Aurorae decoration reader",),
        "tests/test_aurorae_frame.py::TestReadCappedContainment"
        "::test_refuses_a_fifo_instead_of_blocking",
    ),
    Reproduction(
        "containment-double-slash",
        ("POSIX double leading slash",),
        "tests/test_containment.py::TestIsWithin"
        "::test_treats_a_posix_double_slash_spelling_as_the_same_root",
    ),
    Reproduction(
        "containment-filesystem-root",
        ("child of a filesystem root",),
        "tests/test_containment.py::TestIsWithin"
        "::test_accepts_a_path_under_the_filesystem_root",
    ),
    Reproduction(
        "containment-nul-byte",
        ("NUL byte in a guarded path",),
        "tests/test_containment.py::TestResolutionFailureFailsClosed",
    ),
    Reproduction(
        "containment-single-guard",
        ("reimplemented at five sites",),
        "tests/test_containment.py::TestGuardIsShared",
    ),
    Reproduction(
        "uninstall-kdeglobals-bom",
        ("kdeglobals` that opens with a UTF-8 BOM",),
        "tests/test_colorscheme_install.py::TestInstall"
        "::test_make_uninstall_warns_for_a_kdeglobals_with_a_utf8_bom",
    ),
    Reproduction(
        "kde-config-bom",
        ("kde_config.py` cannot read a KDE INI",),
        "tests/test_kde_config.py::TestReadKdeConfig"
        "::test_strips_a_leading_utf8_bom",
    ),
    Reproduction(
        "register-mutation-harness",
        ("tests/invariants.py", "tests/placeholders.py"),
        "tests/test_checker_mutations.py",
    ),
    Reproduction(
        "palette-provenance",
        ("Palette anchors are not re-derivable",),
        "tests/test_colorscheme.py::TestProvenanceNote",
    ),
)


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


def no_observability(records):
    """Return the subset of *records* tagged ``no-observability``."""
    return [record for record in records if record.tag == "no-observability"]


def reproduction(record):
    """Return the ledger entry whose markers match *record*, or ``None``."""
    for entry in NO_OBSERVABILITY_REPRODUCTIONS:
        if any(marker in record.subject for marker in entry.markers):
            return entry
    return None
