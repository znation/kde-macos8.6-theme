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
deterministic. This module turns all five into a structured ledger
that maps each mechanism to the test that confirms it offline, and refuses a
record that names no reproduction.
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
UNCLEAR_INVARIANT_BASELINE = 35

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

CURSOR_HOTSPOT_GUARANTEE = (
    "The cursor generator's nearest-neighbour hotspot mapping keeps every "
    "frame's pinned hotspot inside that frame: it rounds the grid hotspot "
    "up to the first destination pixel its source pixel covers, clamped to "
    "the last rendered pixel (size - 1), which bounds it even at a nominal "
    "size below the 16x16 grid where the downscale skips source pixels."
)

GTK_COMMIT_ROLLBACK_GUARANTEE = (
    "the commit replaces the settings and deletes the user CSS together, so "
    "a rename or removal that fails during it is reported by name after "
    "every file already changed is restored from its same-directory "
    "hard-link backup"
)

GTK_SYMLINK_GUARANTEE = (
    "a settings or user-CSS path that is a symbolic link is refused by name "
    "before staging any write or removal, so the user's link and the file "
    "it names are left untouched instead of the link being replaced or "
    "deleted."
)

FIREFOX_SYMLINK_GUARANTEE = (
    "a sheet or `user.js` path that is a symbolic link is refused by name "
    "before the install writes or the removal deletes anything, so the "
    "user's link and the file it names are left untouched instead of the link "
    "being replaced or deleted"
)

BOM_MARKER_GUARANTEE = (
    "a leading UTF-8 BOM does not hide either sheet marker"
)

USER_JS_BOM_MARKER_GUARANTEE = (
    "a leading UTF-8 BOM does not hide either sheet marker or our `user.js` "
    "marker block"
)

GTK_GLYPH_ROOT_GUARANTEE = (
    "the check, radio and arrow assets keep their provenance comments inside "
    "the root so GTK's CSS icon loader accepts them"
)

SELECTOR_MATCHER_ESCAPE_GUARANTEE = (
    "The test-side selector matcher decodes a backslash escape in an "
    "attribute selector's quoted or unquoted value, so an escaped quote or "
    "backslash, and a hex escape — whose one-whitespace terminator belongs to "
    "the escape, not the value — tests the character it denotes instead of "
    "being read as the string's end."
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
    UnclearInvariant(
        "theme-defaults-line-break",
        ("Unicode line separator",),
        "tests/test_theme_defaults.py::TestDefaultsGroups"
        "::test_a_unicode_line_separator_stays_inside_the_value",
        "The global theme's `contents/defaults` reader treats only CR, LF and "
        "CRLF as line breaks, so U+2028, U+2029, NEL or a C0 separator inside "
        "a value does not split it into a phantom line.",
    ),
    UnclearInvariant(
        "gtk-empty-user-css",
        ("empty `gtk-4.0/gtk.css`",),
        "tests/test_gtk_apply.py::TestApply"
        "::test_empty_user_css_is_adopted",
        "an existing but empty `gtk.css` is adopted rather than treated as "
        "foreign, because it has no content to preserve",
    ),
    UnclearInvariant(
        "firefox-empty-user-chrome",
        (
            "empty `userChrome.css`",
            "adopts an empty sheet of either name",
        ),
        "tests/test_firefox_install.py::TestInstall"
        "::test_an_empty_sheet_is_adopted",
        "adopts an empty sheet of either name, refuses a non-empty foreign "
        "sheet of either name",
    ),
    UnclearInvariant(
        "cursor-sub-grid-hotspot",
        ("cursor hotspot outside its frame",),
        "tests/test_make_cursors.py::TestGeneratorValidation"
        "::test_a_size_below_the_grid_keeps_its_hotspot_inside_the_frame",
        CURSOR_HOTSPOT_GUARANTEE,
    ),
    UnclearInvariant(
        "gtk-commit-rollback",
        ("GTK commit",),
        "tests/test_gtk_staging.py::TestCommit"
        "::test_a_failed_rename_is_reported_by_name_and_restores_the_earlier_target",
        GTK_COMMIT_ROLLBACK_GUARANTEE,
    ),
    UnclearInvariant(
        "gtk-symlinked-config",
        ("A GTK selection replaces a symlinked",),
        "tests/test_gtk_apply_errors.py::TestSettingsErrors",
        GTK_SYMLINK_GUARANTEE,
    ),
    UnclearInvariant(
        "firefox-symlinked-profile-file",
        (
            "A Firefox install replaces or removes a symlinked",
            "a sheet or `user.js` path that is a symbolic link is refused",
        ),
        "tests/test_firefox_install.py::TestInstall"
        "::test_install_refuses_symlinked_profile_files_before_writing_anything",
        FIREFOX_SYMLINK_GUARANTEE,
    ),
    UnclearInvariant(
        "bom-before-marker",
        (
            "A UTF-8 BOM before our marker",
            "a leading UTF-8 BOM does not hide either sheet marker",
        ),
        "tests/test_firefox_install.py::TestInstall"
        "::test_a_bom_before_our_marker_keeps_the_sheet_ours",
        BOM_MARKER_GUARANTEE,
    ),
    UnclearInvariant(
        "user-js-bom-before-marker",
        (
            "A UTF-8 BOM before our Firefox `user.js` marker",
            "a leading UTF-8 BOM does not hide either sheet marker or our `user.js` marker block",
        ),
        "tests/test_firefox_user_js.py::TestUserJs"
        "::test_a_bom_before_our_marker_still_matches_the_block",
        USER_JS_BOM_MARKER_GUARANTEE,
    ),
    UnclearInvariant(
        "gtk-glyph-svg-root-first",
        ("A checked GTK check box draws no check",),
        "tests/test_gtk_theme.py::TestCheckGlyphs"
        "::test_assets_put_the_root_first",
        GTK_GLYPH_ROOT_GUARANTEE,
    ),
    UnclearInvariant(
        "selector-matcher-escaped-quote",
        ("CSS escapes in attribute values",),
        "tests/test_selector_matching.py::TestSelectorMatching"
        "::test_an_escaped_quote_inside_an_attribute_value_is_literal",
        SELECTOR_MATCHER_ESCAPE_GUARANTEE,
    ),
    UnclearInvariant(
        "gtk-define-color-in-quoted-value",
        ("invents a colour from a @define-color inside a quoted value",),
        "tests/test_gtk_css.py::TestRuleBlockSemantics"
        "::test_a_define_color_inside_a_quoted_value_is_text",
        "A quoted string is literal to the comment, block and "
        "`@define-color` scanners too, so a comment marker, a brace or a "
        "colour definition inside one is text rather than a delimiter or a "
        "definition",
    ),
)

# The number of ``no-fake`` records the archive holds with ledger coverage. A
# new record must name its fixture and reproducing test, and raise this by one
# in the same change instead of landing uncovered.
NO_FAKE_BASELINE = 20

NO_FAKE_REPRODUCTIONS = (
    Reproduction(
        "unused-imports-aliased-reexport",
        ("matches an aliased import by its binding name",),
        "tests/test_no_unused_imports.py::TestNoUnusedImports"
        "::test_an_aliased_import_from_here_keeps_the_imported_name",
    ),
    Reproduction(
        "firefox-ini-fifo",
        ("Firefox profile-discovery INI",),
        "tests/test_firefox_profile.py::TestProfileResolution"
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
    Reproduction(
        "run-logged-start-sigterm",
        ("A SIGTERM that arrives while a child starts",),
        "tests/test_process_group.py::TestRunLogged"
        "::test_a_sigterm_while_popen_returns_still_kills_the_child",
    ),
    Reproduction(
        "run-logged-start-sigint",
        ("A Ctrl-C that arrives while a child starts",),
        "tests/test_process_group.py::TestRunLogged"
        "::test_a_sigint_while_popen_returns_still_kills_the_child",
    ),
)


# The five ``real-run-needed`` records the archive held when the ledger landed.
# Each once needed a bounded real run to confirm; its offline test now pins the
# same bound. A new record must name an offline test instead of raising this.
REAL_RUN_NEEDED_BASELINE = 5

REAL_RUN_NEEDED_REPRODUCTIONS = (
    Reproduction(
        "firefox-profile-discovery-ini-cap",
        ("Firefox profile-discovery INI",),
        "tests/test_firefox_profile.py::TestProfileResolution"
        "::test_an_oversize_ini_file_is_refused_by_name",
    ),
    Reproduction(
        "gtk-config-cap",
        ("An oversize GTK settings or user-CSS file",),
        "tests/test_gtk_apply_errors.py::TestUnreadableConfig"
        "::test_apply_refuses_an_oversize_settings_file_before_writing_anything",
    ),
    Reproduction(
        "firefox-profile-file-cap",
        ("An oversize Firefox profile file",),
        "tests/test_firefox_install.py::TestInstall"
        "::test_an_oversize_user_chrome_is_refused_by_name",
    ),
    Reproduction(
        "colorscheme-uninstall-still-selected",
        ("Uninstalling the scheme while it is selected",),
        "tests/test_colorscheme_install.py::TestInstall"
        "::test_make_uninstall_warns_when_the_removed_scheme_is_still_selected",
    ),
    Reproduction(
        "colorscheme-restart-id",
        ("`plasma-apply-colorscheme` writes a scheme ID",),
        "tests/test_colorscheme_install.py::TestInstall"
        "::test_make_install_names_the_scheme_after_its_source_basename",
    ),
)


# The three ``no-repro`` records the archive held when the ledger landed. Each
# failure was not deterministic when filed; its test now reproduces it every run.
# A new record must name such a test instead of raising this.
NO_REPRO_BASELINE = 3

NO_REPRO_REPRODUCTIONS = (
    Reproduction(
        "cursor-write-helper-patch",
        ("The cursor generator test patches a removed `_write_atomic` symbol",),
        "tests/test_make_cursors.py::TestMainErrors"
        "::test_reports_a_failed_write_and_stops_at_that_cursor",
    ),
    Reproduction(
        "check-pattern-whitespace",
        ("`CHECK_PATTERN` guard accepts a pattern with surrounding whitespace",),
        "tests/test_make_check.py::TestCheckPattern"
        "::test_surrounding_whitespace_pattern_is_stripped",
    ),
    Reproduction(
        "desktoptheme-session-theme",
        ("fails when `XDG_CONFIG_DIRS` already names a session theme",),
        "tests/test_desktoptheme.py::TestApplyDesktopTheme"
        "::test_apply_ignores_a_session_theme_in_the_config_search_path",
    ),
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
