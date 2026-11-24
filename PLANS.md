# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
**Steward note 2026-11-24 by the steward role: drift in the queue, updated.**
The product-work gap this note named is closing: seven mimetype-icon plans
landed and were archived 2026-11-24, and three more wait in this queue
(QEMU `application-x-qemu-disk`, PGP `application-pgp-signature`, ICC
`application-vnd.iccprofile` — the last in flight by feature). The red
`make check` Open entry was closed 2026-11-24 by verification (re-tagged
to `slow-check` earlier; ledger back at its baseline). What still stands:
BUGS.md's `## Open` section holds 24 entries on main (`c2c8db08`), 23 of
them matching a test or self-check title pattern (`test_`, `failed`,
`Seven`, `self-check`) — most quarantined render flakes parked as "Needs
review" or "waiting for a recurrence" — and nothing queued addresses them.
The plan role should still weigh a plan that retires the flake backlog (for
example, the capture diagnostics several Open entries ask for) ahead of
another test-file split. This note is a flag, not a new entry, and does
not change queue order.

### Group the tests/support fidelity and kvantum modules into subpackages (part 3/6 of the tests/support regroup) (planned 2026-11-21 by the plan role)

**Needs review 2026-11-21 by feature: too large for one run**

**Goal.** Land the fidelity- and kvantum-family slices of the
tests/support regroup (see part 1/6 for the split's counts and rules; the
parts are independent).

**Modules to move (importer files counted on main).** `fidelity_cli_case`
(40) and `fidelity_delta_fixtures` (4) → `tests/support/fidelity/` with
`__init__.py`: `cli_case.py`, `delta_fixtures.py`. `kvantum_config_spec`
(4) → `tests/support/kvantum/` with `__init__.py`: `config_spec.py`.

**Approach.** As in part 1/6: move, rewrite importer lines and bare
references, retarget `mock.patch` strings, verify importers before each
move. Known stays, already measured: `kvantum_fixtures` (imported by
kvantum tests and the render dialog-gate tests), `jpeg_sampler_fixture`
(fidelity and sample tests), `png_fixtures` (fidelity, png and sample
tests), `sunken_field_reference` and `firstboot_lineedit` (each spans
desktoptheme, kvantum and render tests).

**Files touched.** The three moved modules, their importer files under
`tests/`, any `mock.patch` target strings, and docs naming the old paths.

**Acceptance criteria.**

- `ls tests/support/fidelity/ tests/support/kvantum/` lists both
  `__init__.py` files and the three moved modules;
  `rg -n 'support\.(fidelity_cli_case|fidelity_delta_fixtures|kvantum_config_spec)'`
  over `tests/`, `tools/`, `Makefile`, `docs/` and `*.md` finds no stale
  reference.
- Every `mock.patch` string naming a moved module resolves, and the tests
  that patch them pass.
- No behavior change: `git diff` shows moves, import lines, patch targets
  and doc paths only.
- `make check` passes after the final edit, apart from main's known-red
  tests.


---

### Platinum icon theme: draw RPM packages with an original `application-x-rpm` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** An RPM package file (`*.rpm`, as the file manager identifies
it) draws Breeze's art beside the Platinum documents and folders. Ship
one original placeholder icon, `application-x-rpm`, at 16x16, 22x22 and
32x32, in the same sealed-package series as the landed deb
`application-vnd.debian.binary-package` box and the waiting
`application-x-arj` letter-A and Flatpak-repository entries.
Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/x-rpm` ("RPM package") with no `<icon>` element, the
`<generic-icon name="package-x-generic"/>` the theme already ships, one
`<alias>` (`application/x-redhat-package-manager`), no
`<sub-class-of>` element, one `<magic>` matcher (the string
`\xed\xab\xee\xdb` at offset 0) and one glob `*.rpm` at the default
weight 50, owned by no other MIME type; the dash-form string
`application-x-rpm` occurs 0 times elsewhere in the database
(`str.count` is 0 — `grep -c` counts lines, not matches), so one file
covers exactly its own name and no per-type fallback is in play. The
theme's `index.theme` declares `Inherits=breeze`, so the lookup falls
through to Breeze's exact-name file (Breeze ships
`application-x-rpm.svg` at 16, 22, 24, 32 and 64 in both `breeze` and
`breeze-dark`, each verified with an `ls` check). Planning-time probe
2026-11-24 with `kiconfinder6`, the theme installed into scratch XDG
homes (`XDG_DATA_HOME` naming the installed scratch data root,
`XDG_DATA_DIRS=/usr/share`, `[Icons] Theme=org.macos8.desktop` in the
scratch `kdeglobals`, `QT_QPA_PLATFORM=offscreen`, no `DISPLAY`):
`application-x-rpm` resolved to
`:/icons/breeze/mimetypes/32/application-x-rpm.svg` while
`package-x-generic` resolved to the theme's own 32x32 file — the gap is
real, not the screened-out shape where the theme's own generic art
wins. A headless Gio probe agrees: `Gio.content_type_guess` on a
`test.rpm` names `application/x-rpm` and
`Gio.content_type_get_icon(...).get_names()` lists
`application-x-rpm` first. No reference screenshot shows an RPM-item
icon, so no reference pixels are used and the drawing is this theme's
own choice. Out of scope, one name per entry as in the deb plan: the
separate `application/x-source-rpm` type (globs `*.src.rpm` and
`*.spm`, sub-class of `application/x-rpm`, its own
`package-x-generic` generic-icon) keeps its own lookup name and is not
drawn by this entry.

**Approach.**

- Add `mimetypes/application-x-rpm.svg` under `16x16`, `22x22` and
  `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme` already
  declares the three MimeTypes directories. Give each file the XML
  declaration, the comment `<!-- PLACEHOLDER: original RPM-package
  illustration pending user-approved artwork. -->`, a short comment
  saying it is our own drawing in the Platinum palette, not traced
  from anyone's artwork, and a root with matching `width`, `height`
  and `viewBox`. The art shares the sealed package box (every drawing
  element of that size's `package-x-generic.svg`: the outline, lid
  highlight, white body and grey tape stripe) and holds a black hat —
  a plain crown above a wide brim, an original generic-hat mark
  distinct from the deb box's capital D, the tar box's capital T, the
  ARJ box's letter A, the cpio box's Z, the RAR box's diamond, the ZIP
  box's zipper and the waiting Flatpak-repository box's stepped
  capital R (it is a hat, not any vendor's logo):
  - 32x32: the five shared box elements; then, all `#000000`, the
    crown `7,16 5×5` (cols 7..11, rows 16..20) and the brim `5,21
    9×1` (cols 5..13, row 21); every cell sits on the white body,
    left of and clear of the tape stripe (cols 15..16).
  - 22x22: the five shared box elements; then, all `#000000`, the
    crown `5,11 3×3` (cols 5..7, rows 11..13) and the brim `4,14
    5×1` (cols 4..8, row 14); every cell sits on the white body, left
    of and clear of the tape stripe (cols 10..11).
  - 16x16: the five shared box elements; then, all `#000000`, the
    crown `4,8 2×2` (cols 4..5, rows 8..9) and the brim `3,10 4×1`
    (cols 3..6, row 10); every cell sits on the white body, left of
    and clear of the tape stripe (cols 7..8).

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the deb-package rows,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three
  drawings in `PINS` from the lists above (the `*_SEALED_PACKAGE_*`
  box tuple, then the crown, then the brim), with the same
  type-spelled-name comment convention the deb pin carries.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-x-rpm` in the last cell, as the
  `application-vnd.debian.binary-package` sentence there does.
- `docs/installing.md`: add an RPM-package icon to the sentence
  listing the icon theme's placeholder illustrations and their sizes
  (beside the deb-package clause).
- The waiting Flatpak-repository plans edit the same inventory block,
  `PINS` registry, invariants row and installing.md sentence; this
  entry sits behind them in the queue, so rebase on whatever they
  have landed when picking this up, keeping one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the five box elements
  matching the `package-x-generic.svg` pin's tuple, in the same
  order, then the crown and the brim), carries a placeholder marker
  and has a `PLACEHOLDERS.md` row; the existing inventory, palette,
  geometry and placeholder-register tests cover all three.
- Changing one hat rect's position, size or fill, or the element
  order, in one file makes the geometry test fail; dropping a file
  from one size directory makes the inventory test fail.
- `rg -n 'application-x-rpm' docs/installing.md docs/invariants.md
  PLACEHOLDERS.md` shows the new clause, provenance sentence and
  rows, each dated by its stamp.
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME` with a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset
  `DISPLAY` and `WAYLAND_DISPLAY`, set `QT_QPA_PLATFORM=offscreen`.
  `application-x-rpm` resolves to the theme's own file and
  `package-x-generic` still resolves to the theme's file. Report the
  output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

## Done

### Platinum icon theme: draw detached OpenPGP signatures with an original `application-pgp-signature` icon (planned 2026-11-24 by the plan role; independent of the waiting plans) — done 2026-11-24 by the feature role

**Goal.** A detached OpenPGP signature file (`*.sig`, `*.gpg`,
`*.pgp` or `*.asc`, as the file manager identifies it) draws Breeze's
art beside the Platinum documents and folders. Ship one original
placeholder icon, `application-pgp-signature`, at 16x16, 22x22 and
32x32, in the same mimetype-item series as the landed
`application-pgp-keys` key and the in-flight
`application-x-mimearchive` MHTML and queued
`application-x-qemu-disk` entries.
Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/pgp-signature` ("Detached OpenPGP signature") with no
`<icon>` element, no `<generic-icon>` element, no `<alias>` element,
no `<sub-class-of>` element and one `<magic>` matcher (the string
`-----BEGIN PGP SIGNATURE-----` at offset 0); its globs are `*.sig`
at the default weight 50, owned by no other MIME type, plus `*.pgp`
and `*.gpg`, each at weight 50 and each shared with
`application/pgp-encrypted` and `application/pgp-keys`, and `*.asc`
at weight 10 shared with `application/pgp-encrypted`,
`application/pgp-keys` and `text/plain`; the string
`application-pgp-signature` occurs 0 times in the database
(`str.count` is 0 — `grep -c` counts lines, not matches). With no
generic-icon element and no parent type the lookup asks the literal
type-spelled name; the theme's `index.theme` declares
`Inherits=breeze`, so the lookup falls through to Breeze's exact-name
file (Breeze ships `application-pgp-signature.svg` at 16, 22, 24, 32
and 64, each verified with a `[ -f ]` check). Planning-time probe on
2026-11-24 with `kiconfinder6`, the theme installed into scratch XDG
homes (`XDG_DATA_HOME` naming the installed scratch data root,
`XDG_DATA_DIRS=/usr/share`, `[Icons] Theme=org.macos8.desktop` in the
scratch `kdeglobals`, `QT_QPA_PLATFORM=offscreen`, no `DISPLAY`):
`application-pgp-signature` resolved to
`:/icons/breeze/mimetypes/32/application-pgp-signature.svg` while
`text-x-generic` resolved to the theme's own 32x32 file — the gap is
real, not the screened-out shape where the theme's own generic art
wins. No reference screenshot shows a detached-signature item icon,
so no reference pixels are used and the drawing is this theme's own
choice.

**Approach.**

- Add `mimetypes/application-pgp-signature.svg` under `16x16`,
  `22x22` and `32x32` of `theme/icons/org.macos8.desktop/`.
  `index.theme` already declares the three MimeTypes directories.
  Give each file the XML declaration, the comment `<!--
  PLACEHOLDER: original detached OpenPGP-signature illustration
  pending user-approved artwork. -->`, a short comment saying it is
  our own drawing in the Platinum palette, not traced from anyone's
  artwork, and a root with matching `width`, `height` and `viewBox`.
  The art shares the shell-script document's page (every drawing
  element of that size's `application-x-shellscript.svg`: the page
  outline, white page and folded-corner flap) and holds a black
  signature stroke — a stepped ink flourish stepping down and up
  across the page's foot with a straight underline beneath it, a pen
  signing off the detached signature — an original mark distinct from
  the key's wards-and-blade, the web-document window's globe, the
  shell script's `>_` prompt, JSON's curly braces, BitTorrent's
  download arrow and tray, the backup file's tilde, the crash core's
  square ring and center dot, the database canister, the ISO disc's
  capital I, the Squashfs tapering bands, the WIM split-volume gap,
  the NZB dot-and-bars groups, the paperclip of the waiting MHTML
  entry, the certificate's seal-and-ribbons, the Android zipper teeth
  and the deb box's letter D:
  - 32x32: the three shared page elements; then, all `#000000`, the
    stroke `9,18 3×1` (cols 9..11, row 18), `12,17 3×1` (cols 12..14,
    row 17), `15,18 3×1` (cols 15..17, row 18), `18,17 3×1` (cols
    18..20, row 17), `21,18 2×1` (cols 21..22, row 18) and the
    underline `9,20 14×1` (cols 9..22, row 20); every cell sits
    inside the white page and clear of the flap.
  - 22x22: the three shared page elements; then, all `#000000`, the
    stroke `7,13 2×1` (cols 7..8, row 13), `9,12 2×1` (cols 9..10,
    row 12), `11,13 2×1` (cols 11..12, row 13), `13,12 2×1` (cols
    13..14, row 12), `15,13 2×1` (cols 15..16, row 13) and the
    underline `7,15 10×1` (cols 7..16, row 15); every cell sits
    inside the white page and clear of the flap.
  - 16x16: the three shared page elements; then, all `#000000`, the
    stroke `5,10 2×1` (cols 5..6, row 10), `7,9 2×1` (cols 7..8,
    row 9), `9,10 2×1` (cols 9..10, row 10) and the underline `5,12
    7×1` (cols 5..11, row 12); every cell sits inside the white page
    and clear of the flap.

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the PGP-key rows,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above (the `*_PAGE_*` page tuple, then the
  stroke segments left to right, then the underline).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-pgp-signature` in the last cell, as the
  `application-pgp-keys` sentence there does.
- `docs/installing.md`: add the detached OpenPGP-signature icon to
  the sentence listing the icon theme's placeholder illustrations and
  their sizes.
- The in-flight MHTML and queued QEMU QCOW entries edit the same
  inventory block, `PINS` registry, invariants row and installing.md
  sentence; this entry sits behind them in the queue, so rebase on
  whatever they have landed when picking this up, keeping one row per
  icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the page elements matching
  the `application-x-shellscript.svg` pin's page tuple, in the same
  order, then the stroke segments left to right and the underline),
  carries a placeholder marker and has a `PLACEHOLDERS.md` row; the
  existing inventory, palette, geometry and placeholder-register tests
  cover all three.
- Changing one signature-stroke rect's position, size or fill, or the
  element order, in one file makes the geometry test fail; dropping a
  file while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The `#000000`, `#FFFFFF` and `#DDDDDD` fills stay inside
  `PLATINUM_FILLS`, so `test_each_icon_uses_only_the_platinum_palette`
  passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME`, use a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset
  `DISPLAY` and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-pgp-signature` resolves to the theme's 32x32
  `mimetypes/application-pgp-signature.svg` (at planning time, before
  this change, it resolved to Breeze's
  `:/icons/breeze/mimetypes/32/application-pgp-signature.svg`), and
  `text-x-generic` still resolves to the theme's own file. Report the
  output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

### GTK 3 suite extraction: isolate drag-and-drop declarations (planned 2026-11-18 by the plan role) — done 2026-11-18 by the feature role

**Goal.** Give GTK 3 header drag-feedback declaration checks a focused
suite outside the oversized views module. This relocation is independent
of the waiting paned-handle and pending message-dialog extractions.

**Approach and files touched.** Move
`TestGtkThemeViews.test_header_drop_indicator`,
`test_header_drop_arm_carries_no_padding` and
`test_no_dndtarget_node_declared` from `tests/test_gtk_theme_views.py` to
new `tests/test_gtk_theme_drag_drop.py::TestGtkThemeDragDrop`, preserving
their bodies. Inherit `support.gtk_rule_cases.GtkSheetRuleCases` and
`unittest.TestCase`; set
`CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"`, importing
`ROOT` from `support.repo_root` and `BLACK` and `SELECTION` from
`support.platinum_palette`. The base supplies sheet parsing and assertions;
no shared helper change is needed. Update the source routing docstring and
repoint the moved anchors in the GTK 3 drag-and-drop row of
`docs/invariants.md`, retaining its guarantee and stock-resource provenance.
Search `docs/rendering.md`, `docs/fidelity.md`, `tests/test_ci_workflow.py`
and `tests/support/` for other moved anchors. Keep GTK 4 coverage and GTK 3
rubberband checks in their existing suites; theme sheets need no changes.

**Acceptance criteria.**

- Discovery exposes the named methods in the destination without duplicate
  methods in views or inherited shared-control tests in the destination.
  Source and destination pass independently through project check selectors.
- The plain, legacy dotted-header and spaced-header selector spellings,
  each with plain, hover, active and selected states, retain selection fill,
  black ink, cleared background image and shadows, no border and zero
  radius checks. Changing just the legacy hovered header arm's fill fails
  a moved check.
- Adding padding to `treeview.view button.dnd` or declaring a `dndtarget`
  node in the GTK 3 sheet fails a moved check.
- Invariant anchors resolve and full `make check` passes. This relocation
  adds no rendered-pixel claim.

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_lib/parser.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_lib/report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_lib/match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

### Platinum icon theme: draw FLAC audio with an original `audio-flac` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A FLAC audio file (`*.flac`, as the file manager identifies it)
draws this theme's own mark beside the Platinum documents and folders.
Ship one original placeholder icon, `audio-flac`, at 16x16, 22x22 and
32x32, in the same mimetype-item series as the queued `audio-ogg`
container icon. It is the type-2-audio mark of the installed shared MIME
database, sibling to the audio containers that already ship. Provenance:
the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`audio/flac` ("FLAC audio") with no `<icon>` element, no
`<generic-icon>` element and no `<alias>` elements, the single glob
`*.flac` and a `<magic>` string match at offset 0; the dash-form name
`audio-flac` occurs 0 times in the database (`grep -o` count 0). With no
`<icon>` element the type asks its literal dash-form name first: a
kiconfinder6 probe run at planning time (2026-11-24, theme installed
into a scratch `XDG_DATA_HOME`, scratch `HOME`/`XDG_CONFIG_HOME` with
`[Icons] Theme=org.macos8.desktop` in `kdeglobals`) resolved
`audio-flac` to Breeze's `:/icons/breeze/mimetypes/32/audio-flac.svg`
(Breeze ships the exact-name file at every mimetype size) while
`audio-x-generic` resolved to the theme's own 32x32 file, and the theme
ships no `audio-flac.svg` (no such name in any of the three mimetypes
directories), so today a `.flac` file shows Breeze's art, not this
theme's own. No reference screenshot shows a FLAC item icon, so no
reference pixels are used and the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/audio-flac.svg` under `16x16`, `22x22` and `32x32` of
  `theme/icons/org.macos8.desktop/`. `index.theme` already declares the
  three MimeTypes directories. Give each file the XML declaration, the
  comment `<!-- PLACEHOLDER: original FLAC audio illustration pending
  user-approved artwork. -->`, a short comment saying it is our own
  drawing in the Platinum palette, not traced from anyone's artwork,
  and a root with matching `width`, `height` and `viewBox`. The art
  shares the generic document's page (the page outline, white page and
  folded-corner flap of the `_PAGE_*` shapes the `shape_pins/_shared.py`
  registry keeps) and holds a waveform pulse — one connected black
  zigzag polygon (an EKG-style pulse line: rise, dip, taller rise, fall
  to the baseline), a mark distinct from the `audio-ogg` equalizer's
  four separate vertical bars (disjoint rects, not one connected
  shape), from the `application-ogg` container's black box with the
  white Ogg glyph, from the `video-x-generic` screen's right-pointing
  play triangle and from the `application-vnd.appimage` launch arrow
  (no triangle head, no shaft):
  - 32x32: the three `_PAGE_32` page elements; then the pulse, `path
    d="M9 21 L13 9 L15 17 L19 7 L21 21 Z" fill="#000000"` (vertices on
    the page's centre columns, baseline row 21 spanning columns 9..21).
    A script run at planning time checked every vertex sits inside the
    white page polygon (`M7 4 h12 l6 6 v18 H7 Z`) and below the folded
    corner's hypotenuse `y = x - 15` (the flap spans columns 19..25
    above row 10; the pulse's topmost vertex is `(19, 7)`, on the white
    side).
  - 22x22: the three `_PAGE_22` page elements; then the pulse, `path
    d="M7 15 L10 6 L11 12 L14 5 L15 15 Z" fill="#000000"` (baseline row
    15 spanning columns 7..15). Every vertex sits inside the white page
    (`M5 2 h8 l4 4 v13 H5 Z`) and below the flap hypotenuse `y = x - 11`
    (the flap spans columns 13..17 above row 6; the topmost vertex is
    `(14, 5)`), checked by the same script.
  - 16x16: the three `_PAGE_16` page elements; then the pulse, `path
    d="M5 11 L7 6 L8 9 L10 4 L11 11 Z" fill="#000000"` (baseline row 11
    spanning columns 5..11). Every vertex sits inside the white page
    (`M4 2 h5 l3 3 v8 H4 Z`) and below the flap hypotenuse `y = x - 7`
    (the flap spans columns 9..12 above row 5; the topmost vertex is
    `(10, 4)`), checked by the same script.

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract. The
  mark is a single filled path — `fill="none"` strokes are outside
  `PLATINUM_FILLS`, so no stroke-based element may appear.
- `PLACEHOLDERS.md`: one row per file beside the audio-ogg rows,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above (the three `_PAGE_*` elements spread
  as the prefix, then the pulse path), with a comment recording the
  provenance as this plan states it.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `audio-flac` in the last cell, as the
  `application-vnd.appimage` sentence there does.
- `docs/installing.md`: add the FLAC audio icon to the sentence listing
  the icon theme's placeholder illustrations and their sizes (the one
  naming the `application-vnd.appimage` files).
- The queued mimetype-icon entries ahead of this one (the pending
  `application-ogg`, `application-vnd.flatpak.repo` and
  `application-x-rpm` plans) edit the same inventory block, `PINS`
  registry, invariants row and installing.md sentence; this entry sits
  behind them in the queue, so rebase on whatever they have landed when
  picking this up, keeping one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the three `_PAGE_*`
  elements matching the blank-document pins, then the pulse path),
  carries a placeholder marker and has a `PLACEHOLDERS.md` row; the
  existing inventory, palette, geometry and placeholder-register tests
  cover all three.
- Changing one pulse vertex, the path's `d` or its fill, or the element
  order, in one file makes the geometry test fail; dropping a file
  while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The `#000000` and `#FFFFFF` fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged; no
  element carries `fill="none"` or a `stroke` attribute.
- The waveform pulse shares no drawing element with the `audio-ogg`
  equalizer bars (one connected polygon, not four disjoint rects), none
  with the `application-ogg` box-and-glyph container mark, none with
  the `video-x-generic` play triangle and none with the
  `application-vnd.appimage` arrow, so the siblings stay visually
  distinct.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into
  a scratch `XDG_DATA_HOME` (the `make install
  INSTALL_PACKAGES=icon-theme DESTDIR=<root>` route installs it at
  `<root>$XDG_DATA_HOME/icons`; add that installed path to
  `XDG_DATA_DIRS`), use a scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`),
  `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset `DISPLAY` and
  `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `audio-flac` resolves to the theme's 32x32
  `mimetypes/audio-flac.svg` (at planning time the name falls through
  to Breeze's `:/icons/breeze/mimetypes/32/audio-flac.svg`), and
  `audio-x-generic` still resolves to the theme's own file. Report the
  output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.
