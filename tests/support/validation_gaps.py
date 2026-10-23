"""Read the validation-gap tags in BUGS.md/BUGS-FIXED.md and their offline tests.

Every Fixed bug records a ``**Validation gap:**`` tag, or (for the older
one-line bullets) a trailing ``; gap: <tag>``. The ``no-observability`` tag
marked a failure that left no trace the suite could see, so it could not be
confirmed until instrumentation was added; its records now have test-side
reproductions. The ``unclear-invariant`` tag marked a guarantee the code or
register left unstated or unpinned; its records now name the test and register
row that state it. The ``no-fake`` tag marked a failure whose confirmation
needed a fake, shim or manufactured fixture the suite did not have; its records
now name the fixture and the test that builds it. This module turns all three
into a structured ledger that maps each mechanism to the test that confirms it
offline, and refuses a record that names no reproduction.
``tests/test_validation_gaps.py`` drives the ledgers and caps each tag's count
at its baseline, so a new unrecorded tag fails the suite instead of silently
growing the gap.
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


# The number of ``unclear-invariant`` records the archive holds with ledger
# coverage. A new record must add its ledger entry, register row and test, and
# raise this by one in the same change instead of landing uncovered.
UNCLEAR_INVARIANT_BASELINE = 23

# One archived ``unclear-invariant`` mechanism: the record markers that
# identify it, the test that now pins it, and the guarantee text stated by its
# row in ``docs/invariants.md``.
UnclearInvariant = namedtuple(
    "UnclearInvariant", "name markers reference guarantee"
)

KDE_INI_GUARANTEE = (
    "The three KDE INI readers (`support.kde_config.read`, "
    "`theme_defaults.defaults_groups` and the `uninstall` recipe's `awk`) "
    "agree on one shared corpus's `[General] ColorScheme` selection: `=` is "
    "the only key/value delimiter (a colon-delimited line is ignored), each "
    "line is trimmed, section and key names are case-sensitive, the last "
    "duplicate key wins, a leading UTF-8 BOM is stripped, a present but "
    "empty value is distinct from a missing key, and a group header with no "
    "closing `]` is ignored (the open section continues). An empty `[]` "
    "header starts its own group, so the following key does not join the "
    "previous section, and `support.kde_config.read` keeps a key before the "
    "first heading in KDE's `<default>` root group instead of treating it as "
    "invalid. `defaults_groups` instead refuses a malformed heading because "
    "its headings name output files."
)

URL_CHECK_GUARANTEE = (
    "Every provenance citation is a well-formed absolute RFC 3986 URI: the "
    "scheme, authority, path, query and fragment each hold to the RFC's "
    "grammar, including case-insensitive IPvFuture, no IPv6 zone "
    "identifier, and a valid userinfo, bracketed host and port."
)

UNCLEAR_INVARIANT_REPRODUCTIONS = (
    UnclearInvariant(
        "png-iend-payload",
        ("non-empty IEND payload",),
        "tests/test_png_chunks.py::TestChunkFraming",
        "A PNG chunk stream whose IEND chunk carries a payload is refused by "
        "name instead of its non-empty data field being silently dropped, "
        "because IEND's data field must be empty.",
    ),
    UnclearInvariant(
        "png-chunks-after-iend",
        ("PNG chunks after IEND",),
        "tests/test_png_chunks.py::TestChunkFraming",
        "A PNG chunk stream carrying a complete chunk, or a shorter trailing "
        "fragment that cannot form one, after IEND is refused by name "
        "instead of decoded while silently dropping those bytes, because "
        "IEND must be the last chunk.",
    ),
    UnclearInvariant(
        "png-idat-consecutive",
        ("Non-consecutive IDAT chunks",),
        "tests/test_png_chunks.py::TestChunkFraming",
        "A PNG chunk stream whose IDAT chunks are not consecutive, or whose "
        "PLTE or tRNS chunk follows the image data, is refused by name "
        "rather than decoded as if its chunk order were valid.",
    ),
    UnclearInvariant(
        "png-plte-color-type",
        ("PLTE chunk on a greyscale color type",),
        "tests/test_png_malformed.py::TestPlteColorTypeValidation",
        "A PNG's `PLTE` chunk is refused for the greyscale color types 0 and "
        "4, where the PNG spec prohibits it, while a suggested palette on the "
        "truecolor color types 2 and 6 and the required palette on color type "
        "3 still decode, on both the RGB and RGBA decode paths.",
    ),
    UnclearInvariant(
        "png-trns-color-type",
        ("tRNS validation ran only on the RGBA decode path",),
        "tests/test_png_malformed.py::TestTrnsColorTypeValidation",
        "A PNG's `tRNS` chunk is refused unless the header's color type and "
        "palette can carry it — never for the alpha color types 4 and 6, "
        "only at its exact length for the greyscale and truecolor sample "
        "types, and only for 1 to the palette's entry count for color type "
        "3 — on both the RGB and RGBA decode paths.",
    ),
    UnclearInvariant(
        "png-trns-before-plte",
        ("truecolor tRNS before a suggested PLTE",),
        "tests/test_png_malformed.py::TestTrnsColorTypeValidation"
        "::test_truecolor_trns_before_suggested_plte_is_refused",
        "A PNG's `tRNS` chunk that precedes a `PLTE` chunk which is present is "
        "refused on both decode paths for every color type — the palette "
        "image's required palette and a truecolor image's suggested palette "
        "alike — while a color type 3 image with no `PLTE` at all keeps its "
        "missing-palette diagnosis.",
    ),
    UnclearInvariant(
        "png-idat-zlib-trailer",
        ("trailing bytes after the IDAT zlib stream",),
        "tests/test_png_malformed.py::TestMalformedImageData"
        "::test_rejects_trailing_bytes_after_the_zlib_stream",
        "The PNG decoder refuses bytes after the end of the IDAT zlib stream "
        "instead of silently dropping them, so the concatenated IDAT payload "
        "holds exactly one zlib stream.",
    ),
    UnclearInvariant(
        "kde-ini-indented-header",
        ("indented `[General]` section header",),
        "tests/test_kde_ini_parity.py::TestReadersAgree",
        KDE_INI_GUARANTEE,
    ),
    UnclearInvariant(
        "install-packages-family",
        ("INSTALL_PACKAGES=<unknown>",),
        "tests/test_theme_install.py::TestInstallPackagesGuard",
        "`INSTALL_PACKAGES` names only known artifact families, so `make "
        "install` copies at least one artifact or refuses before creating "
        "the data home.",
    ),
    UnclearInvariant(
        "kde-ini-last-duplicate-key",
        ("first duplicate `ColorScheme` key",),
        "tests/test_kde_ini_parity.py::TestReadersAgree",
        KDE_INI_GUARANTEE,
    ),
    UnclearInvariant(
        "render-config-search-path",
        ("leaks the caller's `XDG_CONFIG_DIRS`",),
        "tests/test_render_surface.py::TestFailurePaths"
        "::test_session_ignores_a_config_search_path_from_the_environment",
        "The render session resolves configuration only from its scratch "
        "data and config homes and the system defaults, never the caller's "
        "`XDG_CONFIG_DIRS`, so an ambient KDE configuration cannot change "
        "the rendered surface.",
    ),
    UnclearInvariant(
        "lineedit-corner-tiles",
        ("corner tiles miss the reference field's",),
        "tests/test_desktoptheme_lineedit.py::TestLineEditReference"
        "::test_corners_match_the_reference",
        "`widgets/lineedit.svg`'s corner tiles reproduce the reference "
        "field's outline and top-right notch, including the bottom outline "
        "row and the face-coloured outer corner.",
    ),
    UnclearInvariant(
        "url-check-path-query-fragment",
        ("malformed path, query or fragment",),
        "tests/test_url_check.py",
        URL_CHECK_GUARANTEE,
    ),
    UnclearInvariant(
        "url-check-ipvfuture-case",
        ("uppercase IPvFuture host",),
        "tests/test_url_check.py",
        URL_CHECK_GUARANTEE,
    ),
    UnclearInvariant(
        "url-check-ipv6-zone",
        ("IPv6 zone identifier",),
        "tests/test_url_check.py",
        URL_CHECK_GUARANTEE,
    ),
    UnclearInvariant(
        "url-check-userinfo",
        ("malformed userinfo",),
        "tests/test_url_check.py",
        URL_CHECK_GUARANTEE,
    ),
    UnclearInvariant(
        "url-check-empty-bracketed-host",
        ("empty bracketed host",),
        "tests/test_url_check.py",
        URL_CHECK_GUARANTEE,
    ),
    UnclearInvariant(
        "url-check-unbracketed-host",
        ("non-reg-name characters",),
        "tests/test_url_check.py",
        URL_CHECK_GUARANTEE,
    ),
    UnclearInvariant(
        "url-check-port",
        ("non-numeric or doubled port",),
        "tests/test_url_check.py",
        URL_CHECK_GUARANTEE,
    ),
    UnclearInvariant(
        "url-check-bracketed-host",
        ("malformed bracketed host",),
        "tests/test_url_check.py",
        URL_CHECK_GUARANTEE,
    ),
    UnclearInvariant(
        "icon-final-art",
        ('placeholder icons',),
        "tests/test_icon_theme.py::TestIndex",
        "The icon theme names our own final Platinum art, ships exactly the "
        "tracked icons, and declares each icon's size directory.",
    ),
    UnclearInvariant(
        "palette-anchor",
        ("Selection palette anchor",),
        "tests/test_colorscheme_reference.py::TestReferenceAnchors",
        "Every sampled palette anchor is still the pixel it was sampled from "
        "in a retail screenshot.",
    ),
    UnclearInvariant(
        "fidelity-objective-gate",
        ('No objective fidelity check',),
        "tests/test_fidelity_cli.py::TestCli",
        "The fidelity gate passes only when no pixel differs beyond its "
        "tolerance, or within an aggregate budget when one is given.",
    ),
)


# The number of ``no-fake`` records the archive holds with ledger coverage. A
# new record must name its fixture and reproducing test, and raise this by one
# in the same change instead of landing uncovered.
NO_FAKE_BASELINE = 17

NO_FAKE_REPRODUCTIONS = (
    Reproduction(
        "firefox-ini-fifo",
        ("Firefox profile-discovery INI",),
        "tests/test_firefox_install.py::TestProfileResolution"
        "::test_a_fifo_at_either_ini_file_is_refused_without_blocking",
    ),
    Reproduction(
        "firefox-profile-file-fifo",
        ("Firefox profile file blocks the install",),
        "tests/test_firefox_install.py::TestRemove"
        "::test_a_fifo_at_either_profile_file_is_refused_without_blocking",
    ),
    Reproduction(
        "png-trns-before-plte",
        ("palette image with tRNS before PLTE",),
        "tests/test_png_malformed.py::TestTrnsColorTypeValidation"
        "::test_palette_trns_before_plte_is_refused",
    ),
    Reproduction(
        "placeholders-symlinked-register",
        ("reads a symlinked `PLACEHOLDERS.md` bare",),
        "tests/test_placeholders.py::TestHelpers"
        "::test_cross_check_refuses_a_symlinked_register_that_escapes",
    ),
    Reproduction(
        "invariants-symlinked-register",
        ("reads a symlinked register bare",),
        "tests/test_invariants.py::TestHelpers"
        "::test_cross_check_refuses_a_symlinked_register_that_escapes",
    ),
    Reproduction(
        "checker-mutations-symlinked-register",
        ("register reads follow a symlinked register outside",),
        "tests/test_checker_mutations.py::TestCheckerMutations"
        "::test_register_reads_refuse_a_symlink_escape",
    ),
    Reproduction(
        "colorscheme-provenance-symlink",
        ("color-scheme provenance test",),
        "tests/test_containment.py::TestReadText"
        "::test_rejects_a_symlink_that_escapes_the_root",
    ),
    Reproduction(
        "desktoptheme-copy-symlink",
        ("secondary SVG copy unguarded",),
        "tests/test_containment.py::TestReadBytes"
        "::test_rejects_a_symlink_that_escapes_the_root",
    ),
    Reproduction(
        "splash-symlink",
        ("follows a symlinked `Splash.qml`",),
        "tests/test_splash_qml.py::TestSplashQmlContainment"
        "::test_rejects_a_symlink_that_escapes_the_repository",
    ),
    Reproduction(
        "metadata-symlink",
        ("load_metadata` follows a symlinked `metadata.json`",),
        "tests/test_package_metadata.py::TestLoadMetadataContainment"
        "::test_rejects_a_symlink_that_escapes_the_repository",
    ),
    Reproduction(
        "invariants-unreadable-register",
        ("`tests/invariants.py`'s `cross_check` lets an unreadable register",),
        "tests/test_invariants.py::TestHelpers"
        "::test_cross_check_rejects_an_unreadable_register",
    ),
    Reproduction(
        "metadata-unreadable",
        ("lets an unreadable `metadata.json`",),
        "tests/test_package_metadata.py::TestLoadMetadata"
        "::test_unreadable_file_names_the_path",
    ),
    Reproduction(
        "placeholders-unreadable-register",
        ("`tests/placeholders.py` lets an unreadable register",),
        "tests/test_placeholders.py::TestHelpers"
        "::test_register_entries_rejects_an_unreadable_register",
    ),
    Reproduction(
        "placeholders-dangling-symlink",
        ("dangling symlink inside `theme/`",),
        "tests/test_placeholders.py::TestHelpers"
        "::test_markers_rejects_a_dangling_symlink_within_the_theme_root",
    ),
    Reproduction(
        "invariants-nul-row",
        ("register reference with a NUL byte",),
        "tests/test_invariants.py::TestHelpers"
        "::test_cross_check_rejects_a_reference_with_a_nul_byte",
    ),
    Reproduction(
        "invariants-unreadable-test-file",
        ("reference to an unreadable test file",),
        "tests/test_checker_mutations.py::TestCheckerMutations"
        "::test_invariants_mutations",
    ),
    Reproduction(
        "apply-cursor-unrunnable-selector",
        ("unstartable cursor selector",),
        "tests/test_apply_cursor.py::TestSelection"
        "::test_unrunnable_selector_exits_2_without_a_traceback",
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


def unclear_invariant(records):
    """Return the subset of *records* tagged ``unclear-invariant``."""
    return [record for record in records if record.tag == "unclear-invariant"]


def no_fake(records):
    """Return the subset of *records* tagged ``no-fake``."""
    return [record for record in records if record.tag == "no-fake"]


def _lookup(record, entries):
    """Return the entry whose markers match *record*, or ``None``."""
    for entry in entries:
        if any(marker in record.subject for marker in entry.markers):
            return entry
    return None


def reproduction(record):
    """Return the no-observability entry matching *record*, or ``None``."""
    return _lookup(record, NO_OBSERVABILITY_REPRODUCTIONS)


def unclear_invariant_reproduction(record):
    """Return the unclear-invariant entry matching *record*, or ``None``."""
    return _lookup(record, UNCLEAR_INVARIANT_REPRODUCTIONS)


def no_fake_reproduction(record):
    """Return the no-fake entry matching *record*, or ``None``."""
    return _lookup(record, NO_FAKE_REPRODUCTIONS)


def reproduction_for(record):
    """Return the ledger entry for *record*'s tag, or ``None``.

    A record carrying a tag this module does not ledger (or one whose subject
    matches no entry) has no reproduction, so a new tag cannot borrow another
    ledger's entries. The three ledgers are ``no-observability``,
    ``unclear-invariant`` and ``no-fake``.
    """
    if record.tag == "no-observability":
        return reproduction(record)
    if record.tag == "unclear-invariant":
        return unclear_invariant_reproduction(record)
    if record.tag == "no-fake":
        return no_fake_reproduction(record)
    return None
