"""The ``unclear-invariant`` validation-gap ledger: entries and baseline.

Each entry names the archived record's markers, the test that now pins its
failure, and the guarantee text stated by its row in ``docs/invariants.md``,
so the suite can check that every record's guarantee is registered as well as
tested. A new archived record must add its entry, register row and test (and
raise this baseline by one in the same change) instead of growing the gap
untested.
"""

from __future__ import annotations

from collections import namedtuple

# The number of ``unclear-invariant`` records the archive holds with ledger
# coverage. A new record must add its ledger entry, register row and test, and
# raise this by one in the same change instead of merging uncovered.
UNCLEAR_INVARIANT_BASELINE = 38

# One archived ``unclear-invariant`` mechanism: the record markers that
# identify it, the test that now pins it, and the guarantee text stated by its
# row in ``docs/invariants.md``.
UnclearInvariant = namedtuple(
    "UnclearInvariant", "name markers reference guarantee"
)

KDE_INI_GUARANTEE = (
    "The three KDE INI readers (`support.kde_config.read`, "
    "`theme_defaults.defaults_groups` and the uninstall diagnostics reader "
    "(`tools.uninstall_config.py`)) "
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

GTK_SETTINGS_LATCH_GUARANTEE = (
    "that hold latches on any `[Settings]` line, as the recipe's original "
    "awk's never-unset `found=1` did: only a line in `[Settings]` marks the "
    "file, and a later duplicate key naming a foreign theme or a later "
    "section switch never unmarks an earlier one of ours"
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
    "being replaced or deleted; the refusal fires at a path the action plans "
    "to change — the install refuses every link at those paths because its "
    "write would replace it, while the removal refuses the `chrome` directory "
    "up front, then an owned sheet's link and a `user.js` link whose "
    "preference block it would rewrite — so a dangling link at a sheet or "
    "`user.js` path reads back as an absent file and a removal exits 0 "
    "leaving that link in place while it still removes what it owns beside it"
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
    "backslash, a CSS string continuation, and a hex escape — whose one-"
    "whitespace terminator belongs to the escape, not the value — test the "
    "character or string they denote instead of being read as the string's end."
)

CALENDAR_GRID_LOCALE_GUARANTEE = (
    "The day grid is caller-locale-independent: the scratch session pins the "
    "measurement locale (en_US.UTF-8) over the caller's LANG and LC_* and "
    "drops LANGUAGE, so kdialog's calendar starts its grid on Sunday whatever "
    "the invoking shell exports, and a session that leaks the caller's locale "
    "shifts the grid one column left and fails the red Sunday-ink pins."
)

UNCLEAR_INVARIANT_REPRODUCTIONS = (
    UnclearInvariant(
        "calendar-day-grid-locale",
        ("red Sunday ink",),
        "tests/test_render_dialog_gates.py::TestCalendarLocaleDialogRender",
        CALENDAR_GRID_LOCALE_GUARANTEE,
    ),
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
        "tests/test_render_failure_paths.py::TestFailurePaths"
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
        "icon-placeholder-art",
        ("icon theme",),
        "tests/test_icon_theme.py::TestIndex"
        "::test_placeholder_register_matches_the_icon_art",
        "The icon theme names its original placeholder artwork, registers and "
        "marks every shipped SVG illustration, ships exactly the tracked "
        "icons, and declares each icon's size directory.",
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
        "tests/test_apply_gtk.py::TestApply"
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
        "tests/test_install_firefox.py::TestInstall"
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
        "tests/test_apply_gtk_errors.py::TestSettingsErrors",
        GTK_SYMLINK_GUARANTEE,
    ),
    UnclearInvariant(
        "firefox-symlinked-profile-file",
        (
            "A Firefox install replaces or removes a symlinked",
            "a sheet or `user.js` path that is a symbolic link is refused",
        ),
        "tests/test_install_firefox.py::TestInstall"
        "::test_install_refuses_symlinked_profile_files_before_writing_anything",
        FIREFOX_SYMLINK_GUARANTEE,
    ),
    UnclearInvariant(
        "bom-before-marker",
        (
            "A UTF-8 BOM before our marker",
            "a leading UTF-8 BOM does not hide either sheet marker",
        ),
        "tests/test_install_firefox.py::TestInstall"
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
        "tests/test_gtk_theme_controls.py::TestCheckGlyphs"
        "::test_assets_put_the_root_first",
        GTK_GLYPH_ROOT_GUARANTEE,
    ),
    UnclearInvariant(
        "selector-matcher-escaped-quote",
        (
            "The test-side selector matcher rejects CSS escapes in attribute values",
            "post-merge review of 932f21cb",
        ),
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
    UnclearInvariant(
        "gtk-uninstall-settings-latch",
        ("later duplicate `gtk-theme-name` key names a foreign theme",),
        "tests/test_gtk_uninstall_diagnostic.py::TestGtkSettingsLatch"
        "::test_latches_when_a_later_duplicate_names_a_foreign_theme",
        GTK_SETTINGS_LATCH_GUARANTEE,
    ),
)
