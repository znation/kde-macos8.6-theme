"""The ``no-observability`` validation-gap ledger's reproduction entries and baseline.

Each entry names the archived record's markers and the offline test that
reproduces its failure. The suite caps the tag's record count at the
baseline, so a new archived record must name its reproduction entry here
(and raise the baseline by one in the same change) instead of growing the
gap untested.
"""

from __future__ import annotations

from .records import Reproduction

# The number of ``no-observability`` records the archive held when the ledger
# landed. A new record must be retired with a test instead of raising this.
NO_OBSERVABILITY_BASELINE = 24

NO_OBSERVABILITY_REPRODUCTIONS = (
    Reproduction(
        "gtk-remove-data-home",
        ("apply_gtk --remove",),
        "tests/test_apply_gtk.py::TestRemove"
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
    Reproduction(
        "checklog-tracked",
        ("`check.log` full-check output is tracked",),
        "tests/test_scratch_hygiene.py::TestNoTrackedScratchFiles"
        "::test_check_log_is_not_tracked",
    ),
    Reproduction(
        "scratchpath-tracked",
        ("`.scratchpath`",),
        "tests/test_scratch_hygiene.py::TestNoTrackedScratchFiles"
        "::test_scratchpath_is_not_tracked",
    ),
    Reproduction(
        "plans-planned-placeholder",
        ("`## Planned` is empty while it holds a planned entry",),
        "tests/test_backlog_placeholders.py::TestShippedBacklogs"
        "::test_no_placeholder_claims_a_section_that_holds_an_entry",
    ),
)
