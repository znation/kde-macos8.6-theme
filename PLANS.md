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


### Platinum icon theme: draw video cameras with an original `camera-video` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** KDE's screen-capture tool requests the `camera-video` device
name, and on this host the name still resolves to Breeze: ship one
original placeholder icon, `camera-video`, at 16x16, 22x22 and 32x32,
in the same devices series as the landed `computer`, `input-keyboard`,
`input-mouse`, `printer`, `media-floppy`, `camera-photo`, `modem`,
`video-display` and `phone` files. Provenance: the installed
`/usr/bin/spectacle` carries the bare `camera-video` literal
(`strings -e l`), so a KDE consumer requests the name. The shared MIME
database gives the name no binding (zero `name="camera-video"` hits and
zero `generic-icon name="camera-video"` references counted on
`/usr/share/mime/packages/freedesktop.org.xml`), so no alias files and
no MIME fallback are in play — one file covers exactly its own name.
Planning-time probe on 2026-11-24 with `kiconfinder6`, the theme
installed into a scratch `DESTDIR` tree and probe XDG homes
(`QT_QPA_PLATFORM=offscreen`, no `DISPLAY`): `camera-video` resolved to
Breeze's `:/icons/breeze/devices/64/camera-video.svg` while
`camera-photo` resolved to the theme's 32x32 devices file, so the theme
must ship the name to win it. No reference screenshot shows a video
camera icon: no reference pixels are used, and the drawing is this
theme's own choice.

**Approach.**

- Add `devices/camera-video.svg` under `16x16`, `22x22` and `32x32` of
  `theme/icons/org.macos8.desktop/`. `index.theme` already declares the
  three directories. Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original camera-video illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art is a flat Platinum film camera seen
  from the side: two film reels on top, a raised body with the 1px
  #000000 outline and the #FFFFFF/#999999 bevel, a black lens hood on
  the body's right edge, and two tripod legs below the body. Each file
  holds these elements in order, written `x,y width×height fill` for
  rects and `cx cy r fill` for circles:
  - 32x32: circle `11,9 4 #000000`; circle `11,9 2 #DDDDDD`; circle
    `21,9 4 #000000`; circle `21,9 2 #DDDDDD`; `5,12 22×12 #000000`;
    `6,13 20×10 #DDDDDD`; `6,13 20×1 #FFFFFF`; `6,13 1×10 #FFFFFF`;
    `6,22 20×1 #999999`; `25,13 1×10 #999999`; `27,16 3×4 #000000`;
    `9,24 2×3 #000000`; `19,24 2×3 #000000`.
  - 22x22: circle `8,6 3 #000000`; circle `8,6 1 #DDDDDD`; circle
    `14,6 3 #000000`; circle `14,6 1 #DDDDDD`; `3,9 14×9 #000000`;
    `4,10 12×7 #DDDDDD`; `4,10 12×1 #FFFFFF`; `4,10 1×7 #FFFFFF`;
    `4,16 12×1 #999999`; `15,10 1×7 #999999`; `17,11 3×3 #000000`;
    `6,18 2×2 #000000`; `13,18 2×2 #000000`.
  - 16x16: circle `5,4 2 #000000`; circle `5,4 1 #DDDDDD`; circle
    `10,4 2 #000000`; circle `10,4 1 #DDDDDD`; `2,6 10×7 #000000`;
    `3,7 8×5 #DDDDDD`; `3,7 8×1 #FFFFFF`; `3,7 1×5 #FFFFFF`;
    `3,11 8×1 #999999`; `10,7 1×5 #999999`; `12,8 2×3 #000000`;
    `4,13 2×2 #000000`; `8,13 2×2 #000000`.

  In each list the first four elements are the reels (drawn first so
  the body covers their lower half), the next six are the body
  outline, fill and bevels, and the last three are the lens hood and
  the two legs. Validate by XML only, never by rasterizing:
  `convert`'s MSVG reader bleeds 1px rects, so the pins below are the
  drawing contract.
- `PLACEHOLDERS.md`: one row per file beside that size's
  `camera-photo` row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths where
  the other `devices` paths are listed in `SHIPPED_ICONS` (the base
  tuple or one of the `SHIPPED_ICONS += tuple(...)` blocks), and name
  the camera-video icon in the comment above the list beside
  `camera-photo`.
- `tests/support/icon/shape_pins/devices.py`: pin the three drawings
  in its `PINS` table from the lists above, using the same rect and
  circle entries the `camera-photo` pins use (the table feeds
  `ICON_SHAPES` in `tests/support/icon/shape_pins/__init__.py`).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, append the
  provenance of `camera-video` to the row's last cell: no reference
  pixels were used, the name is requested by KDE's screen-capture tool
  (the installed `/usr/bin/spectacle` carries the bare `camera-video`
  literal, `strings -e l` verified), the shared MIME database gives
  the name no binding, Breeze's own art was beaten by shipping the
  name at the theme's sizes (before the change, `kiconfinder6
  camera-video` with the theme installed into scratch XDG homes
  resolved to Breeze's `:/icons/breeze/devices/64/camera-video.svg`
  while `camera-photo` resolved to the theme's 32x32 devices file),
  and the reels-body-hood drawing is this theme's own choice.
- `docs/installing.md`: add the camera-video icon to the sentence
  listing the icon theme's placeholder illustrations and their sizes,
  beside the camera sentence.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/devices.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size, carries a placeholder
  marker and has a `PLACEHOLDERS.md` row; the existing inventory,
  palette, geometry and placeholder-register tests cover all three.
- Changing an element's position, size, fill or order, a reel's
  centre or radius, or the lens hood's or a leg's position or size, in
  one file makes `test_each_icon_draws_its_pinned_artwork` fail;
  dropping a file while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The new fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme` puts
  the three files in the installed theme, and uninstalling removes them
  (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into a
  scratch `DESTDIR` tree, use a scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`), `XDG_CACHE_HOME` and
  `XDG_RUNTIME_DIR`, unset `DISPLAY` and `WAYLAND_DISPLAY`, and set
  `QT_QPA_PLATFORM=offscreen`. `camera-video` resolves to the theme's
  32x32 devices file (at planning time, before this change, it resolved
  to Breeze's `:/icons/breeze/devices/64/camera-video.svg`), and
  `camera-photo` stays on the theme's 32x32 devices file. Report the
  output in VERIFIED.
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
