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

### Render-gate diagnostics: preserve the failing capture and name the failing pixel (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** When a render capture gate fails, the failure must keep the
capture image itself and name the first differing pixel's coordinates
and both colours. BUGS.md's umbrella entry "Seven icon-dialog render
gates failed with the same pixel mismatch" and the quarantined gate
entries under it ask for exactly this on recurrence: a recorded
`#CCCCCC` versus `#000000` mismatch shows the capture was the desktop
face, but `Renders._remove_directories` removes every scratch directory
at interpreter exit, so nothing distinguishes "the window was never
painted before the settle" from "the capture never showed a window".
The 2026-11-24 plan "Render gate failures name the render kind and
carry its own output" added kind attribution and the session-log tail;
this plan adds the two diagnostics that plan left out. Landing it does
not by itself close any BUGS.md entry — a recurrence recorded with the
new diagnostics does.

**Approach.**

- `tests/support/render/gates.py`:
  - Add a module helper, `preserve_capture(kind, directory, filename)`:
    when the capture PNG exists, copy it byte-for-byte into a
    diagnostics directory that survives the run —
    `${TMPDIR:-/tmp}/platinum-render-diagnostics/<UTC
    timestamp>-<pid>-<kind>/` under the capture's filename — and return
    that path; when no PNG was written, return `None`. That None is
    itself a diagnostic the entries ask for: a finished render with no
    capture says so. Prune the diagnostics root to its newest 8
    timestamped directories so parallel workers and repeated runs stay
    bounded, remove with `ignore_errors=True`, and never let a copy or
    prune error mask the gate's own failure (fall back to `None`).
  - Attach the capture's whereabouts to every failure-reporting path:
    `RenderOutputMessages.assertEqual` and `DialogGate.test_exits_zero`
    append a line naming the preserved path (or, when the render wrote
    no capture, saying so) after the render-output note;
    `Renders._finish_failure` does the same for batch-finish failures.
    A passing run creates no diagnostics: unittest builds a
    `msg` argument eagerly even for passing assertions, so the
    preservation must happen in the failure path (catch the
    `AssertionError` and re-raise with the note appended), never in the
    eager message-building path.
  - Name the failing pixel: `PixelPins.assert_band`'s per-row subTest
    context (today `band_mismatch_context`'s whole-band colour summary
    and stderr tail) gains the failing row's first differing cell — its
    absolute coordinates in the capture with the expected and observed
    hex colours. `band_mismatch_context`'s signature and output stay as
    they are; the pixel line is added at the `assert_band` call site.
- No production tooling under `tools/` changes; the sibling gates'
  own copies of `test_exits_zero` outside `gates.py`
  (`tests/test_render_surface.py`, `tests/test_render_splash_gate.py`)
  keep their current messages.

**Files.** `tests/support/render/gates.py`,
`tests/test_render_gate_messages.py`, `tests/test_render_gates_batch.py`.

**Acceptance criteria.**

- Preservation on a pixel mismatch: in `tests/test_render_gate_messages.py`
  (beside the existing `TestPixelAssertionMessages` probes), a probe
  gate whose `directory` holds a written `dialog.png` fails an
  `assertEqual` with a message naming a path outside the scratch tree
  at which a byte-identical copy of the PNG exists; a probe whose
  directory holds no `dialog.png` reports instead that the render
  wrote no capture; a passing assertion creates no diagnostics
  directory.
- Batch failure: in `tests/test_render_gates_batch.py` (extending the
  existing `_run_with_stubbed_runner` stubbing), a stubbed
  `process_runner.finish` raising for a kind whose directory holds a
  capture yields the attributable message naming the preserved copy's
  path; one whose directory holds no capture still names the kind and
  says no capture was written.
- Failing pixel: a band whose first differing cell sits at capture
  coordinates (x, y) fails with a message containing those coordinates
  beside the expected and observed hex colours; a fully matching band
  produces no diagnostics copy.
- Pruning: after the helper runs against a diagnostics root pre-seeded
  with more than 8 timestamped directories, only the 8 newest remain
  and the newly preserved capture is among them.
- The existing `tests/test_render_gate_messages.py` and
  `tests/test_render_gates_batch.py` cases pass unchanged; no test name
  elsewhere changes.
- `make check` passes after the final edit, apart from main's
  known-red tests.

### Platinum icon theme: draw PGP keys with an original `application-pgp-keys` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A PGP key file (`.gpg`, `.asc`, `.pgp`, `.skr`, `.pkr`,
`.key`) maps to the shared MIME database's canonical type
`application/pgp-keys` ("PGP keys"), which the database gives no
`generic-icon` and no `<icon>` element, so there is no fallback file
for the lookup to reach, and Breeze ships the exact name: under this
theme a key file draws Breeze's keyring art with nothing of this
theme's series beside it — ship one original placeholder icon,
`application-pgp-keys`, at 16x16, 22x22 and 32x32, in the same
mimetype-item series as the shipped `application-x-sharedlib`
shared-library window. Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/pgp-keys` ("PGP keys", with the acronym PGP expanded to
Pretty Good Privacy) with no `<generic-icon>` element, no `<icon>`
element, no `<alias>` elements, the globs `*.skr`, `*.pkr`,
`<glob weight="10" pattern="*.asc">`, `*.pgp`, `*.gpg` and `*.key`,
four string `<magic>` matchers (`-----BEGIN PGP PUBLIC KEY BLOCK-----`,
`-----BEGIN PGP PRIVATE KEY BLOCK-----`) and four `big16` magic
matchers, and holds zero occurrences of the hyphenated name
`application-pgp-keys` (`str.count` is 0), so one file covers exactly
the canonical name and no alias file is shipped. The globs `*.pgp`,
`*.gpg` and `*.asc` are shared with the sibling type
`application/pgp-encrypted` (alias `application/pgp`), so which of the
two a given file resolves to is magic-based; files resolving to
`pgp-keys` draw this icon, and the sibling types `application/pgp-encrypted`
and `application/pgp-signature` keep their own names and are out of
scope. The planning-time probe on 2026-11-24 with `kiconfinder6`, the
theme installed into scratch XDG homes (`XDG_DATA_DIRS` naming the
scratch data root, `[Icons] Theme=org.macos8.desktop` in the scratch
`kdeglobals`, `QT_QPA_PLATFORM=offscreen`, no `DISPLAY`):
`application-pgp-keys` resolved to Breeze's
`:/icons/breeze/mimetypes/32/application-pgp-keys.svg` while
`application-x-executable` and `application-x-sharedlib` resolved to
the theme's own 32x32 files — Breeze's exact-name file is the only art
the lookup can find, so the theme must ship the name to put a key file
in the series. No reference screenshot shows a key icon, so no
reference pixels are used and the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/application-pgp-keys.svg` under `16x16`, `22x22` and
  `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme` already
  declares the three MimeTypes directories. Give each file the XML
  declaration, the comment `<!-- PLACEHOLDER: original PGP-key
  illustration pending user-approved artwork. -->`, a short comment
  saying it is our own drawing in the Platinum palette, not traced from
  anyone's artwork, and a root with matching `width`, `height` and
  `viewBox`. The art shares the program window (every drawing element
  of `mimetypes/application-x-executable.svg` at that size) and holds
  a black skeleton key in the body — an original keyring mark distinct
  from the executable's right-pointing triangle, the shared library's
  two-bar stack, the JSON braces, the Perl capital P and the archive
  letters:
  - 16x16: the window elements `rect 1,2 14×12 #000000`, `rect 2,3
    12×3 #DDDDDD`, `rect 2,3 12×1 #FFFFFF`, `rect 4,4 8×1 #999999` and
    `rect 2,7 12×6 #FFFFFF`; key, all `#000000`: bow ring `rect 3,8
    3×1`, `rect 3,10 3×1`, `rect 3,9 1×1` and `rect 5,9 1×1` (ring
    columns 3..5, rows 8..10, hole at 4,9), stem `rect 6,9 4×1` (row
    9, columns 6..9) and teeth `rect 7,10 1×2` and `rect 9,10 1×2`
    (rows 10..11) — every rect inside the body rows 7..12 and columns
    2..13.
  - 22x22: the window elements `rect 2,3 18×16 #000000`, `rect 3,4
    16×3 #DDDDDD`, `rect 3,4 16×1 #FFFFFF`, `rect 5,5 12×1 #999999`
    and `rect 3,8 16×10 #FFFFFF`; key, all `#000000`: bow ring `rect
    4,9 5×1`, `rect 4,13 5×1`, `rect 4,10 1×3` and `rect 8,10 1×3`
    (ring columns 4..8, rows 9..13, hole at 6,11), stem `rect 9,11
    6×1` (row 11, columns 9..14) and teeth `rect 11,12 1×2` and `rect
    14,12 1×2` (rows 12..13) — every rect inside the body rows 8..17
    and columns 3..18.
  - 32x32: the window elements `rect 3,5 26×22 #000000`, `rect 4,6
    24×4 #DDDDDD`, `rect 4,6 24×1 #FFFFFF`, `rect 6,8 20×1 #999999`
    and `rect 4,11 24×15 #FFFFFF`; key, all `#000000`: bow ring `rect
    6,13 7×1`, `rect 6,19 7×1`, `rect 6,14 1×5` and `rect 12,14 1×5`
    (ring columns 6..12, rows 13..19, hole at 9,16), stem `rect 13,16
    8×1` (row 16, columns 13..20) and teeth `rect 16,17 1×2` and
    `rect 20,17 1×2` (rows 17..18) — every rect inside the body rows
    11..25 and columns 4..27.

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside that size's
  `application-x-sharedlib` row, described as the marker describes
  it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`, and extend the
  mimetypes comment above them to name the PGP key in the type-spelled
  series.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above, spreading the existing
  `_PROGRAM_WINDOW_16`, `_PROGRAM_WINDOW_22` and `_PROGRAM_WINDOW_32`
  tuples from `tests/support/icon/shape_pins/_shared.py` for the
  window elements (the tuples already exist; `_shared.py` itself needs
  no change), then the bow ring, stem and teeth.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-pgp-keys` in the last cell, as the
  `application-x-sharedlib` sentence there does.
- `docs/installing.md`: add the PGP-key icon to the sentence listing
  the icon theme's placeholder illustrations and their sizes.
- The in-flight desktop-launcher and BitTorrent entries edit the same
  inventory block, `PINS` registry, invariants row and installing.md
  sentence; this entry sits behind them in the queue, so rebase on
  whatever they have landed when picking it up, keeping one row per
  icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the window elements
  matching the same size's `application-x-executable.svg` window, in
  the same order, then the bow ring, stem and teeth), carries a
  placeholder marker and has a `PLACEHOLDERS.md` row; the existing
  inventory, palette, geometry and placeholder-register tests cover
  all three.
- Changing one key rectangle's position, size, fill or the element
  order in one file makes the geometry test fail; dropping a file
  while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The key's `#000000` fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME`, use a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset
  `DISPLAY` and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-pgp-keys` resolves to the theme's 32x32
  `mimetypes/application-pgp-keys.svg` (at planning time, before this
  change, it resolved to Breeze's
  `:/icons/breeze/mimetypes/32/application-pgp-keys.svg`), and
  `application-x-executable` and `application-x-sharedlib` still
  resolve to the theme's own files. Report the output in VERIFIED.
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
