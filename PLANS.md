# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
**Steward note 2026-11-24 by the steward role: drift in the queue.** Every
Planned entry on main (`2edd4589a`) is a test-file move or regroup: the
fidelity/kvantum regroup, the invariants checker split (two parts), and the
GTK staging split. None plans product work, and none plans a fix for the
Open flakes. Meanwhile BUGS.md's `## Open` section holds 27 entries on the
same commit, and 24 of them match a test or self-check title pattern
(`test_`, `failed`, `Seven`, `self-check`) — most are quarantined render
flakes parked as "Needs review" or "waiting for a recurrence". The
test-file splits are not wrong, but they are the only work being queued
while the red `make check` and the flake backlog stay unresolved. The plan
role should weigh a plan that addresses the flake backlog (for example, the
capture diagnostics several Open entries ask for) ahead of another split.
This note is a flag, not a new entry, and does not change queue order.

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

### Platinum icon theme: draw cpio archives with an original
`application-x-cpio` icon (planned 2026-11-24 by the plan role;
independent of the waiting plans)

**Goal.** A `.cpio` item maps to the shared MIME database's canonical
type `application/x-cpio`, whose database `generic-icon` is the theme's
own shipped `package-x-generic` file, but the lookup never reaches it:
Breeze ships the exact name, so under this theme a `.cpio` item draws
Breeze's cpio art instead of this theme's series — ship one original
placeholder icon, `application-x-cpio`, at 16x16, 22x22 and 32x32, in
the same mimetype-item series as the landed `application-octet-stream`,
`text-html`, `application-pdf`, `application-zip`, `application-x-tar`,
`application-x-7z-compressed`, `application-gzip` and
`application-vnd.debian.binary-package` files, the in-flight
RAR-archive, gzip-compressed-tar and xz-compressed-tar work and the
pending bzip2- and LZMA-compressed-tar entries. Provenance: the
installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/x-cpio` ("CPIO archive") with `generic-icon
name="package-x-generic"`, no `<icon>` element, no `<alias>` elements,
one `<glob pattern="*.cpio">` and a magic matcher; the database holds
zero occurrences of the hyphenated name `application-x-cpio`
(`str.count` is 0 — `grep -c` counts lines, not matches), so one file
covers exactly the canonical name and no alias file is shipped. Breeze
ships its own exact-name file at all three sizes, so the planning-time
probe on 2026-11-24 with `kiconfinder6`, the theme installed into
scratch XDG homes (`XDG_DATA_DIRS` naming the scratch data root,
`[Icons] Theme=org.macos8.desktop` in the scratch `kdeglobals`,
`QT_QPA_PLATFORM=offscreen`, no `DISPLAY`):
`application-x-cpio` resolved to Breeze's
`:/icons/breeze/mimetypes/32/application-x-cpio.svg` while
`package-x-generic` resolved to the theme's own 32x32
`mimetypes/package-x-generic.svg` — Breeze's exact-name file beats the
generic-icon fallback, so the theme must ship the name to put a `.cpio`
item in the series. No reference screenshot shows a cpio icon, so no
reference pixels are used and the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/application-x-cpio.svg` under `16x16`, `22x22` and
  `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme` already
  declares the three MimeTypes directories. Give each file the XML
  declaration, the comment `<!-- PLACEHOLDER: original cpio illustration pending user-approved artwork. -->`, a short comment saying it is our
  own drawing in the Platinum palette, not traced from anyone's
  artwork, and a root with matching `width`, `height` and `viewBox`.
  The art shares the sealed package box (every drawing element of
  `mimetypes/package-x-generic.svg` at that size) and holds a capital C
  on the white face, left of the grey tape stripe — a top bar, a left
  stem and a bottom bar opening right, an original archive mark
  distinct from deb's hollow full-height capital D, tar's T, 7z's
  stepped 7, zip's slider, the in-flight gzip arrow, rar diamond, xz's
  stair-stepped X and the pending lowercase b and capital L:
  - 32x32: the box rects `3,6 26×22` `#000000`, `4,7 24×3` `#DDDDDD`,
    `4,7 24×1` `#FFFFFF`, `4,10 24×17` `#FFFFFF` and the tape
    `15,10 2×17` `#999999`; C rects: top bar `5,13 8×2` `#000000`
    (rows 13..14), left stem `5,15 2×6` `#000000` (rows 15..20) and
    bottom bar `5,21 8×2` `#000000` (rows 21..22; all inside the face
    left of the tape).
  - 22x22: the box rects `2,4 18×16` `#000000`, `3,5 16×2` `#DDDDDD`,
    `3,5 16×1` `#FFFFFF`, `3,7 16×12` `#FFFFFF` and the tape
    `10,7 2×12` `#999999`; C rects: top bar `3,9 6×2` `#000000`, left
    stem `3,11 2×3` `#000000` and bottom bar `3,14 6×2` `#000000`.
  - 16x16: the box rects `1,3 14×11` `#000000`, `2,4 12×2` `#DDDDDD`,
    `2,4 12×1` `#FFFFFF`, `2,6 12×7` `#FFFFFF` and the tape
    `7,6 2×7` `#999999`; C rects: top bar `2,7 4×2` `#000000`, left
    stem `2,9 2×2` `#000000` and bottom bar `2,11 4×2` `#000000` (the
    face left of the tape is five columns, rows 6..12; the mark stays
    inside it).

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside that size's
  `package-x-generic` row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`, and extend the
  mimetypes comment above them to name the type-spelled package/archive
  series.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-x-cpio` in the last cell, as the
  `application-zip` sentence there does.
- `docs/installing.md`: add the cpio icon to the sentence listing the
  icon theme's placeholder illustrations and their sizes.
- The eligible bzip2-compressed-tar entry and the pending
  LZMA-compressed-tar entry edit the same inventory block, `PINS`
  registry, invariants row and installing.md sentence; this entry sits
  behind them in the queue, so rebase on whatever they have landed when
  picking it up, keeping one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the rectangles listed for that size (the box elements
  matching `package-x-generic.svg`'s pinned list, in the same order,
  then the top bar, left stem and bottom bar), carries a placeholder
  marker and has a `PLACEHOLDERS.md` row; the existing inventory,
  palette, geometry and placeholder-register tests cover all three.
- Changing one C rectangle's position, size or fill, or the element
  order, in one file makes the geometry test fail; dropping a file
  while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The C's `#000000` fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME`, use a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset
  `DISPLAY` and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-x-cpio` resolves to the theme's 32x32
  `mimetypes/application-x-cpio.svg` (at planning time, before this
  change, it resolved to Breeze's
  `:/icons/breeze/mimetypes/32/application-x-cpio.svg`), and
  `package-x-generic` still resolves to the theme's own file (the
  generic fallback keeps its own drawing). Report the output in
  VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

### Platinum icon theme: draw LZMA-compressed tar archives with an
original `application-x-lzma-compressed-tar` icon (planned 2026-11-24 by
the plan role; independent of the waiting plans)

**Goal.** KIO requests an `application/x-lzma-compressed-tar` item's
icon under the shared MIME database's type-spelled name
`application-x-lzma-compressed-tar`, and on this host that exact name
draws Breeze's art even though the database's `generic-icon` for the
type is the theme's own shipped `package-x-generic` file: ship one
original placeholder icon, `application-x-lzma-compressed-tar`, at
16x16, 22x22 and 32x32, in the same mimetype-item series as the
landed `application-octet-stream`, `text-html`, `application-pdf`,
`application-zip`, `application-x-tar`, `application-x-7z-compressed`
and `application-gzip` files and the waiting compressed-tar,
bzip2-compressed-tar, xz-compressed-tar, deb and RAR plans.
Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/x-lzma-compressed-tar` ("Tar archive (LZMA-compressed)")
with `generic-icon name="package-x-generic"`, no `<icon>` element and
no aliases, and the database holds zero occurrences of the hyphenated
name `application-x-lzma-compressed-tar` anywhere (`grep -c` counts
0, so no `<icon>` or `generic-icon` reference can name it), so one
file covers exactly its canonical name — no alias files and no
per-type fallback are in play; the type's `sub-class-of
application/x-lzma` link changes no icon resolution, since the probe
below shows the type's own spelled name is the one requested. Breeze
ships the exact name under `mimetypes/` at all three sizes, and at
the exact name Breeze's own file beats the theme's generic-icon
fallback. Planning-time probe on 2026-11-24 with `kiconfinder6`, the
theme installed into scratch XDG homes (`XDG_DATA_DIRS` naming the
scratch data root, `QT_QPA_PLATFORM=offscreen`, no `DISPLAY`):
`application-x-lzma-compressed-tar` resolved to Breeze's
`:/icons/breeze/mimetypes/32/application-x-lzma-compressed-tar.svg`
while `package-x-generic` resolved to the theme's own 32x32
`mimetypes/package-x-generic.svg`, so the theme must ship the exact
name to win it. No reference screenshot shows an LZMA-compressed tar
icon, so no reference pixels are used and the drawing is this theme's
own choice.

**Approach.**

- Add `mimetypes/application-x-lzma-compressed-tar.svg` under `16x16`,
  `22x22` and `32x32` of `theme/icons/org.macos8.desktop/`.
  `index.theme` already declares the three directories. Give each
  file the XML declaration, the comment `<!-- PLACEHOLDER: original
  LZMA-compressed-tar illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum
  palette, not traced from anyone's artwork, and a root with matching
  `width`, `height` and `viewBox`. The art shares the sealed package
  box (every drawing element of `mimetypes/package-x-generic.svg` at
  that size) and holds a capital L — a full-height left stem and a
  full-width bottom bar meeting at the lower-left corner — on the
  white face left of the grey tape stripe (the L reads as LZMA's
  first letter and stays clear of the tar icon's T bar-and-stem, the
  7z icon's stepped 7, the zip icon's slider, the gzip icon's
  downward arrow, the compressed-tar plan's stepped Z, whose top bar
  and diagonal the L lacks, the bzip2 plan's solid lowercase b, the
  xz plan's stair-stepped X, the deb icon's hollow D and the RAR
  plan's stepped diamond):
  - 32x32: the box rects `3,6 26×22` `#000000`, `4,7 24×3` `#DDDDDD`,
    `4,7 24×1` `#FFFFFF`, `4,10 24×17` `#FFFFFF` and the tape
    `15,10 2×17` `#999999`; letter rects `4,13 3×10` `#000000`
    (left stem) and `7,21 8×2` `#000000` (bottom bar).
  - 22x22: the box rects `2,4 18×16` `#000000`, `3,5 16×2` `#DDDDDD`,
    `3,5 16×1` `#FFFFFF`, `3,7 16×12` `#FFFFFF` and the tape
    `10,7 2×12` `#999999`; letter rects `3,9 2×6` `#000000` (left
    stem) and `5,14 5×1` `#000000` (bottom bar).
  - 16x16: the box rects `1,3 14×11` `#000000`, `2,4 12×2` `#DDDDDD`,
    `2,4 12×1` `#FFFFFF`, `2,6 12×7` `#FFFFFF` and the tape
    `7,6 2×7` `#999999`; letter rects `2,7 1×5` `#000000` (left
    stem) and `3,11 4×1` `#000000` (bottom bar).

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside that size's
  `package-x-generic` row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`, and extend the
  mimetypes comment above them to name the type-spelled
  package/archive series.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three
  drawings in `PINS` from the lists above.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-x-lzma-compressed-tar` in the last cell,
  as the `application-zip` sentence there does.
- `docs/installing.md`: add the LZMA-compressed-tar icon to the
  sentence listing the icon theme's placeholder illustrations and
  their sizes.
- The in-flight `application-vnd.debian.binary-package` and
  `application-vnd.rar` plans and the waiting compressed-tar,
  bzip2-compressed-tar and xz-compressed-tar plans edit the same
  inventory block, `PINS` registry, invariants row and
  installing.md sentence; this entry sits behind them in the queue,
  so rebase on whatever they have landed when picking it up.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the rectangles listed for that size (the box elements
  matching `package-x-generic.svg`'s pinned list, in the same order,
  then the L elements in the listed order), carries a placeholder
  marker and has a `PLACEHOLDERS.md` row; the existing inventory,
  palette, geometry and placeholder-register tests cover all three.
- Changing an L rectangle's position, size or fill, or the element
  order, in one file makes the geometry test fail; dropping a file
  while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The L's `#000000` fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME`, use a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset
  `DISPLAY` and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-x-lzma-compressed-tar` resolves to the theme's 32x32
  `mimetypes` file (at planning time, before this change, it resolved
  to Breeze's
  `:/icons/breeze/mimetypes/32/application-x-lzma-compressed-tar.svg`),
  and `package-x-generic` still resolves to the theme's own file (the
  generic fallback keeps its own drawing). Report the output in
  VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

## Done

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

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
