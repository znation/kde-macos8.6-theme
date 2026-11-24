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

### Platinum icon theme: draw flash media with an original `media-flash` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** Flash media — the memory card shown by the device notifier and
Dolphin's places — is drawn with Breeze's art beside the Platinum hard
disk, removable drive and optical drive. Ship one original placeholder
icon, `media-flash`, at 16x16, 22x22 and 32x32. The installed
`libKF6Solid.so.6.13.0` contains the name `media-flash` itself plus the
loader-reduced subnames `media-flash-sd-mmc`, `media-flash-memory-stick`
and `media-flash-smart-media` (`strings -e l`), and the shared MIME
database gives `media-flash` no `generic-icon` binding, so Solid is the
name's only source. Planning-time probe with `kiconfinder6` and a copy of
the theme selected through scratch XDG homes: all four names resolved to
Breeze; after `media-flash.svg` was added to the copy's three `devices`
directories, all four resolved to the theme's 32x32 file while
`media-floppy` stayed on Breeze. One file therefore covers its own name
and the three reduced subnames without alias files; ship no aliases and
nothing but `media-flash`. `media-floppy` stays out of scope. This plan
shares no drawing with the drive plans (a card is not the drive body);
either order works.

**Approach.**

- Add `devices/media-flash.svg` under `16x16`, `22x22` and `32x32` of
  `theme/icons/org.macos8.desktop/`. `index.theme` already declares the
  three directories. Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original flash-media illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art is an upright flash card standing on
  its contact pins: the Platinum body-and-bevel, a white label plate
  outlined in black, and a row of black contact pins clear of the bevel.
  Each file holds these elements in order, written `x,y W×H fill` for
  rects:
  - 32x32 (11): `9,3 14×26 #000000`; `10,4 12×24 #DDDDDD`; `10,4 12×1
    #FFFFFF`; `10,4 1×24 #FFFFFF`; `10,27 12×1 #999999`; `21,4 1×24
    #999999`; `11,7 10×8 #000000`; `12,8 8×6 #FFFFFF`; `11,21 2×3
    #000000`; `15,21 2×3 #000000`; `19,21 2×3 #000000`.
  - 22x22 (11): `6,2 10×18 #000000`; `7,3 8×16 #DDDDDD`; `7,3 8×1
    #FFFFFF`; `7,3 1×16 #FFFFFF`; `7,18 8×1 #999999`; `14,3 1×16
    #999999`; `8,5 6×5 #000000`; `9,6 4×3 #FFFFFF`; `8,15 1×2 #000000`;
    `10,15 1×2 #000000`; `12,15 1×2 #000000`.
  - 16x16 (10, two pins): `4,1 8×14 #000000`; `5,2 6×12 #DDDDDD`; `5,2
    6×1 #FFFFFF`; `5,2 1×12 #FFFFFF`; `5,13 6×1 #999999`; `10,2 1×12
    #999999`; `6,4 4×3 #000000`; `7,5 2×1 #FFFFFF`; `6,10 1×2 #000000`;
    `8,10 1×2 #000000`.

  These were rendered at planning time (painted rect by rect, and via
  ImageMagick at 4x for the eye) and read as a card with a label plate
  and separate pins at every size.
- `PLACEHOLDERS.md`: one row per file beside that size's
  `drive-removable-media` row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths to
  `SHIPPED_ICONS` beside the other `devices` paths, and name the
  flash-media card in the comment above it.
- `tests/test_icon_theme_geometry.py`: pin the three drawings in
  `ICON_SHAPES` from the lists above; the existing
  `test_the_geometry_registry_covers_every_shipped_icon` and
  `test_each_icon_draws_its_pinned_artwork` then enforce the pins in both
  directions. No sharing check is added: the card does not share the
  drive family's body.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `media-flash` in the last cell: no reference pixels were
  used, the name is a KDE-required value read from `libKF6Solid.so.6`
  (the shared MIME database gives it no `generic-icon` binding), and the
  upright-card-with-pins drawing is this theme's own choice.
- `docs/installing.md`: add the flash-media card to the sentence listing
  the icon theme's placeholder illustrations and their sizes.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`, `tests/test_icon_theme_geometry.py`,
`docs/invariants.md`, `docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding exactly
  the elements listed for that size, carries a placeholder marker and
  comment and has a `PLACEHOLDERS.md` row; the existing inventory, palette,
  geometry and placeholder-register tests cover all three.
- Changing a rectangle's position, size or fill, or the element order, in
  one file makes the geometry pin fail.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme` puts
  the three files in the installed theme, and uninstalling removes them
  (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into a
  scratch `XDG_DATA_HOME` (create the destination `icons` directory before
  copying the theme into it, so the copy does not flatten), use a scratch
  `HOME`, `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset `DISPLAY`
  and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `media-flash`, `media-flash-sd-mmc`, `media-flash-memory-stick` and
  `media-flash-smart-media` resolve to the theme's file, and
  `media-floppy` stays on Breeze. Report the output in VERIFIED.
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
