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


---

### Platinum icon theme: draw NZB usenet indexes with an original `application-x-nzb` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** An NZB usenet-index file (`*.nzb`, as the file manager
identifies it) draws Breeze's art beside the Platinum documents and
folders. Ship one original placeholder icon, `application-x-nzb`, at
16x16, 22x22 and 32x32, in the same mimetype-item series as the landed
`application-vnd.efi.iso` optical disc and the in-flight sqlite3,
backup-file, core-dump, python-bytecode, X.509-certificate,
Android-package and Squashfs-image entries. Provenance: the installed
shared MIME database (`/usr/share/mime/packages/freedesktop.org.xml`)
declares the type `application/x-nzb` ("NewzBin usenet index") with no
`<icon>` element, no `<generic-icon>` element and no `<alias>` element,
the single glob `<glob pattern="*.nzb">` at the default weight 50 and
owned by no other MIME type, one `<magic>` at priority 80 holding the
offset-0:256 string matcher `<nzb`, and `<sub-class-of
type="application/xml">` ("XML document"); the string
`application-x-nzb` occurs 0 times in the database (`str.count` is 0 —
`grep -c` counts lines, not matches). With no icon element the type
asks its literal name; the theme's `index.theme` declares
`Inherits=breeze`, so the lookup falls through to Breeze's exact-name
file (Breeze ships it at 16, 22, 24, 32 and 64, checked with a
per-size file-existence loop). Planning-time probe on 2026-11-24 with
`kiconfinder6`, the theme installed into scratch XDG homes
(`make install XDG_DATA_HOME=<scratch>/data DESTDIR=<scratch>/root
INSTALL_PACKAGES=icon-theme`, `XDG_DATA_HOME=<scratch>/root<data`
naming `/usr/share` beside it in `XDG_DATA_DIRS`,
`[Icons] Theme=org.macos8.desktop` in the scratch `kdeglobals`,
`QT_QPA_PLATFORM=offscreen`, no `DISPLAY`):
`application-x-nzb` resolved to
`:/icons/breeze/mimetypes/32/application-x-nzb.svg` while
`text-x-generic` and `application-x-executable` resolved to the
theme's own 32x32 files — the gap is real, not the screened-out shape
where the theme's own art already wins. No reference screenshot shows
an NZB item icon, so no reference pixels are used and the drawing is
this theme's own choice.

**Approach.**

- Add `mimetypes/application-x-nzb.svg` under `16x16`, `22x22` and
  `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme`
  already declares the three MimeTypes directories. Give each file the
  XML declaration, the comment `<!-- PLACEHOLDER: original NZB
  usenet-index illustration pending user-approved artwork. -->`, a
  short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art shares the generic document's page
  (the page outline, white page and folded-corner flap matching the
  `application-json.svg` pin's first three elements) and holds segment
  groups — an index dot in black beside two grey segment bars, one
  group per article segment cluster an NZB file lists — an original
  index mark distinct from the JSON document's curly braces, the shell
  script's `>_` prompt, BitTorrent's download arrow and tray, the
  backup file's tilde and the crash core's square ring:
  - 32x32: the three shared page elements; then, per group at top
    rows 10, 16 and 22, the black dot `rect x="9" y="<row>" width="2"
    height="2"`, the grey bar `rect x="13" y="<row>" width="10"
    height="2"` and the grey bar `rect x="13" y="<row + 3>"
    width="7" height="2"` (bars `#999999`); every element sits inside
    the white page.
  - 22x22: the three shared page elements; then, per group at top
    rows 7, 11 and 15, the black dot `rect x="7" y="<row>" width="1"
    height="1"`, the grey bar `rect x="10" y="<row>" width="6"
    height="1"` and the grey bar `rect x="10" y="<row + 2>"
    width="4" height="1"`; every element sits inside the white page.
  - 16x16: the three shared page elements; then two groups (the
    page's height holds two) at top rows 5 and 8, the black dot
    `rect x="5" y="<row>" width="1" height="1"`, the grey bar
    `rect x="7" y="<row>" width="4" height="1"` and the grey bar
    `rect x="7" y="<row + 2>" width="3" height="1"`; every element
    sits inside the white page.

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the backup-file row,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above (the three shared page elements in
  document order, then the groups dot-first with each group's bars in
  row order).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-x-nzb` in the last cell, as the
  `application-pgp-keys` sentence there does.
- `docs/installing.md`: add the NZB icon to the sentence listing the
  icon theme's placeholder illustrations and their sizes.
- The in-flight sqlite3, backup-file, core-dump, python-bytecode,
  X.509-certificate, Android-package and Squashfs-image entries edit
  the same inventory block, `PINS` registry, invariants row and
  installing.md sentence; this entry sits behind them in the queue, so
  rebase on whatever they have landed when picking this up, keeping
  one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the three shared page
  elements matching the `application-json.svg` pin's first three
  elements, then the groups), carries a placeholder marker and has a
  `PLACEHOLDERS.md` row; the existing inventory, palette, geometry and
  placeholder-register tests cover all three.
- Changing one dot's or bar's position, size or fill, or the element
  order, in one file makes the geometry test fail; dropping a file
  while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The `#000000`, `#FFFFFF` and `#999999` fills stay inside
  `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME`, use a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset
  `DISPLAY` and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-x-nzb` resolves to the theme's 32x32
  `mimetypes/application-x-nzb.svg` (at planning time, before this
  change, it resolved to Breeze's
  `:/icons/breeze/mimetypes/32/application-x-nzb.svg`), and
  `text-x-generic` still resolves to the theme's own file. Report the
  output in VERIFIED.
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

**Approach and files.** In `tools/sample_lib/parser.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_lib/report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_lib/match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
