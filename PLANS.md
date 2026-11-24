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

### Platinum icon theme: draw untyped and empty files with an original blank-document icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** The theme draws text files with the Platinum page, but files whose
type is not recognised, and empty files, get Breeze's art. Ship one original
placeholder drawing, a blank page, at 16x16, 22x22 and 32x32 under the three
names `application-octet-stream`, `application-x-zerosize` and `unknown`.
The first two are the MIME types `application/octet-stream` and
`application/x-zerosize` spelled as icon names; both types are declared in
the installed shared MIME database. `unknown` is a string in the installed
`libKF6KIOGui.so.6`.

Planning-time probe with `kiconfinder6` and a copy of the theme selected
through scratch XDG homes: all three names resolved to Breeze. Adding
`unknown.svg` to the copy's `32x32/mimetypes` changed only `unknown` among
them, and adding `application-octet-stream.svg` changed that name too but
left `application-x-zerosize` on Breeze, so each name needs its own file.
Other MIME-type icons are out of scope.

**Approach.**

- Add the three names under `mimetypes/` in `16x16`, `22x22` and `32x32` of
  `theme/icons/org.macos8.desktop/`, nine regular files. `index.theme`
  already declares the three directories. Each file has the XML declaration,
  `<!-- PLACEHOLDER: original blank-document illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette and
  shares the generic document's page, and a root with matching `width`,
  `height` and `viewBox`. Its drawing is the same size's
  `text-x-generic.svg` without the text lines, so exactly three `path`
  elements, in order, with fills `#000000`, `#FFFFFF`, `#DDDDDD`:
  - 32x32: `M6 3 h14 l6 6 v20 H6 Z`; `M7 4 h12 l6 6 v18 H7 Z`;
    `M19 4 L25 4 L25 10 Z`.
  - 22x22: `M4 1 h10 l4 4 v15 H4 Z`; `M5 2 h8 l4 4 v13 H5 Z`;
    `M13 2 L17 2 L17 6 Z`.
  - 16x16: `M3 1 h7 l3 3 v10 H3 Z`; `M4 2 h5 l3 3 v8 H4 Z`;
    `M9 2 L12 2 L12 5 Z`.
- `PLACEHOLDERS.md`: one row per file beside that size's `text-x-generic`
  row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add a `BLANK_DOCUMENTS` tuple of
  the three names with a comment recording where each comes from, and extend
  `SHIPPED_ICONS` with the nine paths after the `STANDARD_PLACES` extension.
- `tests/test_icon_theme_geometry.py`: pin the nine drawings in
  `ICON_SHAPES` from the lists above (one literal tuple per size, shared by
  the three names). Add a test that, at each size, each blank document's
  drawing equals the first three drawing elements of that size's
  `text-x-generic.svg`, comparing the shipped files.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, say the three names
  share the generic document's page without its text lines. In its last cell
  record the provenance: the references give no pixel ground truth for this
  art, the names are KDE-required values from the MIME database and
  `libKF6KIOGui.so.6`, and the drawing is this theme's own choice.
- `docs/installing.md`: add the blank-document icon to the sentence listing
  the icon theme's placeholder illustrations and their sizes.

**Files touched.** Nine new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`, `tests/test_icon_theme_geometry.py`,
`docs/invariants.md`, `docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding exactly
  the three paths listed for that size, carries a placeholder marker and has
  a `PLACEHOLDERS.md` row; the existing inventory, palette, geometry and
  placeholder-register tests cover all nine.
- Changing any path in one blank-document file makes the page-sharing test
  fail, as does adding a text line to it.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme` puts the
  nine files in the installed theme, and uninstalling removes them (the
  existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into a
  scratch `XDG_DATA_HOME`, use a scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`), `XDG_CACHE_HOME` and
  `XDG_RUNTIME_DIR`, unset `DISPLAY` and `WAYLAND_DISPLAY`, and set
  `QT_QPA_PLATFORM=offscreen`. The three names resolve to the theme's own
  files and `text-x-generic` still does. Report the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full `make check`
  after the final edit, apart from main's known-red tests.

### Platinum icon theme: draw removable drives with an original `drive-removable-media` icon (planned 2026-11-24 by the plan role; independent of the waiting regroup, invariants, staging and inactive-dialog plans)

**Goal.** The icon theme's only device icon is `drive-harddisk`, so a USB
stick on the desktop or in the file manager's Places list is drawn with
Breeze's art beside the Platinum hard disk. Ship one original placeholder
icon, `drive-removable-media`, at 16x16, 22x22 and 32x32. The installed
`libKF6Solid.so.6` (6.13.0) contains the names `drive-removable-media`,
`drive-removable-media-usb` and `drive-removable-media-usb-pendrive`. One
name covers all three: planning-time probe with `kiconfinder6`, with a copy
of the theme selected through scratch XDG homes, resolved the first two to
Breeze; after a file named `drive-removable-media.svg` was added to the
copy's `32x32/devices`, all three resolved to that file (the icon loader
drops dash suffixes within a theme before trying the inherited one). Do not
ship alias files for the two longer names.

Optical, floppy and flash media icons are out of scope; so are the other
names the theme inherits from Breeze.

**Approach.**

- Add `devices/drive-removable-media.svg` under `16x16`, `22x22` and `32x32`
  of `theme/icons/org.macos8.desktop/`. `index.theme` already declares the
  three directories. Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original removable-drive illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette, not
  traced from anyone's artwork, and a root with matching `width`, `height`
  and `viewBox`. The art is the matching size's hard-disk body and bevel
  with a media slot (black, white lower lip) and a black eject button in
  place of the label plate and light. Each file holds these nine `rect`
  elements in order, written `x,y width×height fill`:
  - 32x32: `3,8 26×17 #000000`; `4,9 24×15 #DDDDDD`; `4,9 24×2 #FFFFFF`;
    `4,9 1×15 #FFFFFF`; `4,22 24×2 #999999`; `27,9 1×15 #999999`;
    `7,13 18×2 #000000`; `7,15 18×1 #FFFFFF`; `21,18 4×2 #000000`.
  - 22x22: `2,4 18×15 #000000`; `3,5 16×13 #DDDDDD`; `3,5 16×2 #FFFFFF`;
    `3,5 1×13 #FFFFFF`; `3,17 16×1 #999999`; `18,5 1×13 #999999`;
    `5,9 12×2 #000000`; `5,11 12×1 #FFFFFF`; `13,14 4×1 #000000`.
  - 16x16: `1,3 14×10 #000000`; `2,4 12×8 #DDDDDD`; `2,4 12×1 #FFFFFF`;
    `2,4 1×8 #FFFFFF`; `2,11 12×1 #999999`; `13,4 1×8 #999999`;
    `4,7 8×1 #000000`; `4,8 8×1 #FFFFFF`; `9,10 3×1 #000000`.
- `PLACEHOLDERS.md`: one row per file beside that size's `drive-harddisk`
  row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths to
  `SHIPPED_ICONS` after the hard-disk paths, and name the removable drive in
  the comment above it.
- `tests/test_icon_theme_geometry.py`: add the three `ICON_SHAPES` entries
  from the lists above. Add one test that each size's removable drive starts
  with the same six drawing elements (body and bevel) as that size's
  `drive-harddisk.svg`, comparing the shipped files.
- `docs/invariants.md`: in the icon-theme row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, say the
  `drive-removable-media` icon shares the hard disk's body and bevel, and
  record its provenance in the row's last cell: no reference pixels were
  used, the name is a KDE-required value read from `libKF6Solid.so.6`, and
  the drawing is this theme's own choice.
- `docs/installing.md`: add the removable-drive icon to the sentence listing
  the shipped placeholder illustrations.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`, `tests/test_icon_theme_geometry.py`,
`docs/invariants.md`, `docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding exactly
  the nine rectangles listed for that size, carries a placeholder marker and
  has a `PLACEHOLDERS.md` row; the existing inventory, palette, geometry and
  placeholder-register tests cover all three.
- Changing any of the first six rectangles in one removable-drive file makes
  the body-sharing test fail.
- Installing into a scratch root with
  `INSTALL_PACKAGES=icon-theme` puts the three files in the installed theme,
  and uninstalling removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into a
  scratch `XDG_DATA_HOME`, use a scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`), `XDG_CACHE_HOME` and
  `XDG_RUNTIME_DIR`, unset `DISPLAY` and `WAYLAND_DISPLAY`, and set
  `QT_QPA_PLATFORM=offscreen`. The three Solid names all resolve to the
  theme's `drive-removable-media.svg`. Report the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full `make check`
  after the final edit, apart from main's known-red tests.

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
