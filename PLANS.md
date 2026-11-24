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

### Platinum icon theme: draw shared libraries with an original `application-x-sharedlib` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A `.so` item maps to the shared MIME database's canonical type
`application/x-sharedlib`, which the database gives no `generic-icon`
and no `<icon>` element, so there is no fallback file for the lookup to
reach, and Breeze ships the exact name: under this theme a `.so` item
draws Breeze's shared-library art with nothing of this theme's series
beside it — ship one original placeholder icon, `application-x-sharedlib`,
at 16x16, 22x22 and 32x32, in the same mimetype-item series as the
shipped `application-x-executable` program window. Provenance: the
installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/x-sharedlib` ("Shared library") with no `<generic-icon>`
element, no `<icon>` element, no `<alias>` elements, the globs
`<glob pattern="*.so">` and `<glob weight="60" pattern="*.so.[0-9]*">`
and one `<magic>` matcher, and holds zero occurrences of the hyphenated
name `application-x-sharedlib` (`str.count` is 0 — `grep -c` counts
lines, not matches), so one file covers exactly the canonical name and
no alias file is shipped. The planning-time probe on 2026-11-24 with
`kiconfinder6`, the theme installed into scratch XDG homes
(`XDG_DATA_DIRS` naming the scratch data root, `[Icons]
Theme=org.macos8.desktop` in the scratch `kdeglobals`,
`QT_QPA_PLATFORM=offscreen`, no `DISPLAY`): `application-x-sharedlib`
resolved to Breeze's
`:/icons/breeze/mimetypes/32/application-x-sharedlib.svg` while
`application-x-executable` and `text-x-generic` resolved to the theme's
own 32x32 files — Breeze's exact-name file is the only art the lookup
can find, so the theme must ship the name to put a `.so` item in the
series. No reference screenshot shows a shared-library icon, so no
reference pixels are used and the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/application-x-sharedlib.svg` under `16x16`, `22x22`
  and `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme`
  already declares the three MimeTypes directories. Give each file the
  XML declaration, the comment `<!-- PLACEHOLDER: original
  shared-library illustration pending user-approved artwork. -->`, a
  short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art shares the program window (every
  drawing element of `mimetypes/application-x-executable.svg` at that
  size except the triangle: the `#000000` outline, the `#DDDDDD`
  title-bar face with its `#FFFFFF` highlight and `#999999` stripe, and
  the `#FFFFFF` body) and holds a black two-bar stack in the body — an
  original shared-library mark distinct from the executable's
  right-pointing triangle, the shell-script console prompt, the archive
  letters and marks (deb's hollow capital D, tar's T, 7z's stepped 7,
  zip's slider, gzip's arrow, cpio's capital C, the rar diamond, xz's
  stair-stepped X, bzip2's lowercase b, LZMA's capital L), the
  in-flight ISO capital I, the waiting JSON braces and the pending Perl
  capital P:
  - 32x32: the window elements `rect 3,5 26×22 #000000`, `rect 4,6
    24×4 #DDDDDD`, `rect 4,6 24×1 #FFFFFF`, `rect 6,8 20×1 #999999`
    and `rect 4,11 24×15 #FFFFFF`; stack bars, all `#000000`: `rect
    8,14 16×3` (rows 14..16) and `rect 8,19 16×3` (rows 19..21), with
    the gap rows 17..18 (both bars sit inside the body rows 11..25 and
    columns 4..27).
  - 22x22: the window elements `rect 2,3 18×16 #000000`, `rect 3,4
    16×3 #DDDDDD`, `rect 3,4 16×1 #FFFFFF`, `rect 5,5 12×1 #999999`
    and `rect 3,8 16×10 #FFFFFF`; stack bars, all `#000000`: `rect
    6,10 10×2` (rows 10..11) and `rect 6,14 10×2` (rows 14..15), with
    the gap rows 12..13 (inside the body rows 8..17 and columns
    3..18).
  - 16x16: the window elements `rect 1,2 14×12 #000000`, `rect 2,3
    12×3 #DDDDDD`, `rect 2,3 12×1 #FFFFFF`, `rect 4,4 8×1 #999999`
    and `rect 2,7 12×6 #FFFFFF`; stack bars, all `#000000`: `rect
    4,8 8×2` (rows 8..9) and `rect 4,11 8×1` (row 11), with the gap
    row 10 (inside the body rows 7..12 and columns 2..13).

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `tests/support/icon/shape_pins/_shared.py`: add `_PROGRAM_WINDOW_16`,
  `_PROGRAM_WINDOW_22` and `_PROGRAM_WINDOW_32` tuples holding the
  five window elements listed above per size, beside `_PAGE_*`, and
  spread them into the three existing `application-x-executable` pins
  in `shape_pins/mimetypes.py` in place of their first five inline
  shapes (the element lists stay identical, so the executable's pins
  still pass unchanged).
- `PLACEHOLDERS.md`: one row per file beside that size's
  `application-x-executable` row, described as the marker describes
  it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`, and extend the
  mimetypes comment above them to name the shared library in the
  type-spelled series.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above, spreading the new `*_PROGRAM_WINDOW_*`
  tuple for the window elements, then the two stack bars.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-x-sharedlib` in the last cell, as the
  `application-x-executable` sentence there does.
- `docs/installing.md`: add the shared-library icon to the sentence
  listing the icon theme's placeholder illustrations and their sizes.
- The in-flight ISO entry and the waiting JSON and pending Perl
  entries edit the same inventory block, `PINS` registry, invariants
  row and installing.md sentence; this entry sits behind them in the
  queue, so rebase on whatever they have landed when picking it up,
  keeping one row per icon.

**Files touched.** Three new SVGs,
`tests/support/icon/shape_pins/_shared.py`, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the window elements
  matching the same size's `application-x-executable.svg` window, in
  the same order, then the two stack bars), carries a placeholder
  marker and has a `PLACEHOLDERS.md` row; the existing inventory,
  palette, geometry and placeholder-register tests cover all three.
- Changing one stack-bar rectangle's position, size or fill, or the
  element order, in one file makes the geometry test fail; dropping a
  file while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The stack bars' `#000000` fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME`, use a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset
  `DISPLAY` and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-x-sharedlib` resolves to the theme's 32x32
  `mimetypes/application-x-sharedlib.svg` (at planning time, before
  this change, it resolved to Breeze's
  `:/icons/breeze/mimetypes/32/application-x-sharedlib.svg`), and
  `application-x-executable` still resolves to the theme's own file.
  Report the output in VERIFIED.
- The existing icon files keep their drawings (the executable's three
  files are untouched; only their pins spread the new window tuple),
  and `index.theme` and the cursors are unchanged.
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
