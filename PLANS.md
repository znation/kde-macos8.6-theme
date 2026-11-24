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

### Platinum icon theme: draw contact files with an original `x-office-address-book` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** The contact-file name `x-office-address-book` is requested by
installed consumers but still draws Breeze's art beside the Platinum
placeholders: with the theme installed, `kiconfinder6
x-office-address-book` (2026-11-24, theme installed) resolves to
`:/icons/breeze/mimetypes/32/x-office-address-book.svg` and exits 0.
Ship one original placeholder icon, `x-office-address-book`, at 16x16,
22x22 and 32x32, in the mimetypes series beside the shipped
`x-office-document`, `x-office-spreadsheet` and `x-office-presentation`
files. Provenance of the name (measured by scanning
`strings -e l` output of every library under
`/usr/lib/x86_64-linux-gnu/*.so*`, not only `libKF6*`): the installed
`libkmailprivate.so.6` carries the literal beside KMail's recipient
action strings (`select_recipients`, `mail-message-new`), and
`libgtk-3.so`, `libgtk-4.so` and `libappstream-glib.so.8` carry it too;
`libKF6BreezeIcons.so.6` also holds the literal but embeds Breeze's own
art, so it is not a consumer. Breeze ships the name at mimetypes 16, 22,
24, 32 and 64 (`/usr/share/icons/breeze/mimetypes/*/`), which is what
the probe displaces. Nothing is captured: the installed shared MIME
database declares no `generic-icon` element named
`x-office-address-book` (`grep -c 'x-office-address-book'
/usr/share/mime/packages/freedesktop.org.xml` prints 1, the DTD's
allowed-values comment), so the KIconLoader per-type fallback captures
no MIME type — one file covers exactly its own name, no alias files.
No reference screenshot shows an address-book icon, so no reference
pixels are used and the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/x-office-address-book.svg` under `16x16`, `22x22` and
  `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme` already
  declares the three mimetypes directories. Give each file the XML
  declaration, the comment
  `<!-- PLACEHOLDER: original contact-book illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art is a Platinum closed address book:
  a book block with the 1px #000000 outline, the #DDDDDD cover face and
  the #FFFFFF/#999999 bevel, a dark name heading and ruled entry lines.
  Each file holds these elements in order, written `x,y width×height
  fill` for rects:
  - 32x32 (12): `4,2 24×28 #000000`; `5,3 22×26 #DDDDDD`; `5,3 22×2
    #FFFFFF`; `5,3 2×26 #FFFFFF`; `25,3 2×26 #999999`; `5,27 22×2
    #999999`; `8,7 12×2 #000000`; `8,11 14×1 #000000`; `8,13 11×1
    #000000`; `8,15 14×1 #000000`; `8,17 9×1 #000000`; `8,19 14×1
    #000000`.
  - 22x22 (11): `2,1 18×20 #000000`; `3,2 16×18 #DDDDDD`; `3,2 16×2
    #FFFFFF`; `3,2 2×18 #FFFFFF`; `17,2 2×18 #999999`; `3,18 16×2
    #999999`; `5,6 9×2 #000000`; `5,10 11×1 #000000`; `5,12 8×1
    #000000`; `5,14 11×1 #000000`; `5,16 6×1 #000000`.
  - 16x16 (11): `1,1 14×14 #000000`; `2,2 12×12 #DDDDDD`; `2,2 12×1
    #FFFFFF`; `2,2 1×12 #FFFFFF`; `13,2 1×12 #999999`; `2,13 12×1
    #999999`; `4,4 7×1 #000000`; `4,6 9×1 #000000`; `4,8 6×1 #000000`;
    `4,10 9×1 #000000`; `4,12 5×1 #000000`.

  These were drawn to read as a closed book with a white spine
  highlight, a dark heading line and ruled entry lines at every size
  (painted rect by rect at planning time), and to stay in the mimetypes
  document-page family's palette.
- `PLACEHOLDERS.md`: one row per file beside that size's
  `x-office-presentation` row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths to
  `SHIPPED_ICONS` beside the `x-office-presentation` paths, and name the
  contact-book icon in the comment above them (the comment records the
  requesting surface: KMail's recipient chooser in the installed
  `libkmailprivate.so.6`, plus the GTK and appstream-glib libraries).
- `tests/support/icon/shape_pins.py`: pin the three drawings in
  `ICON_SHAPES` from the lists above (every element is a `_shape("rect",
  ...)` keeping its attributes); the existing
  `test_the_geometry_registry_covers_every_shipped_icon` and
  `test_each_icon_draws_its_pinned_artwork` then enforce the pins in
  both directions.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `x-office-address-book` in the last cell: no reference
  pixels were used, the name is read by KMail's recipient chooser in the
  installed `libkmailprivate.so.6` and by the installed GTK 3, GTK 4 and
  appstream-glib libraries (measured with `strings -e l` over every
  `/usr/lib/x86_64-linux-gnu/*.so*`), `kiconfinder6` resolves it to the
  shipped file, and the shared MIME database declares no
  `generic-icon` binding for the name, so no per-type fallback is
  captured; the book drawing is this theme's own choice.
- `docs/installing.md`: add the contact-book icon to the sentence
  listing the icon theme's placeholder illustrations and their sizes.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`, `tests/support/icon/shape_pins.py`,
`docs/invariants.md`, `docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding exactly
  the elements listed for that size, carries a placeholder marker and
  comment and has a `PLACEHOLDERS.md` row; the existing inventory, palette,
  geometry and placeholder-register tests cover all three.
- Changing a rectangle's position, size or fill, or the element order in
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
  `x-office-address-book` resolves to the theme's 32x32 file, and
  `x-office-spreadsheet` stays on the theme's 32x32 file. Report the
  output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full `make check`
  after the final edit, apart from main's known-red tests.

### Platinum icon theme: draw tablets with an original `input-tablet` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A drawing tablet is drawn with Breeze's art beside the
Platinum placeholders. Ship one original placeholder icon,
`input-tablet`, at 16x16, 22x22 and 32x32, in the same devices series
as the landed `computer`, `input-keyboard`, `input-mouse`, `printer`,
`media-floppy` and `camera-photo` files and the waiting `video-display`
entry. Provenance: the installed `libkwin.so.6` carries the bare
`input-tablet` literal (`strings -e l`; the only other library holding
the string is `libKF6BreezeIcons.so.6`, which embeds Breeze's own art,
not a consumer), so KWin requests the name — the graphics-tablet
side of System Settings' input devices draws it. Breeze ships the
name under `devices/` at 16, 22 and 24 (plus 2x/3x and scaled) and
64; this theme declares devices directories at 16x16, 22x22 and
32x32 and no symbolic or scaled directories, so exactly three files
go in `devices/` and the symbolic and scaled renditions stay out of
scope. Planning-time probe with `kiconfinder6` and the theme installed
into scratch XDG homes: with no tablet icon of its own, `input-tablet`
resolved to Breeze's `devices/64` file, so the theme must ship the
name to win it. No reference screenshot shows a tablet icon: no
reference pixels are used, and the drawing is this theme's own choice.
The shared MIME database gives the name no `generic-icon` binding
(counted on `/usr/share/mime/packages/freedesktop.org.xml`) and no
MIME type is captured by fallback, so one file covers exactly its own
name — no alias files.

**Approach.**

- Add `devices/input-tablet.svg` under `16x16`, `22x22` and `32x32`
  of `theme/icons/org.macos8.desktop/`. `index.theme` already declares
  the three directories. Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original tablet illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art is a flat Platinum graphics tablet
  seen from above: a landscape body with the 1px #000000 outline and
  the #FFFFFF/#999999 bevel, a white drawing surface outlined in
  black on the left, and a pen standing upright on the right with a
  white barrel stripe and a tip notch below the barrel. Each file
  holds these elements in order, written `x,y width×height fill` for
  rects:
  - 32x32: `2,6 28×20 #000000`; `3,7 26×18 #DDDDDD`; `3,7 26×1
    #FFFFFF`; `3,7 1×18 #FFFFFF`; `3,24 26×1 #999999`; `28,7 1×18
    #999999`; `6,10 14×12 #000000`; `7,11 12×10 #FFFFFF`; `24,9 3×11
    #000000`; `25,10 1×9 #FFFFFF`; `24,21 3×2 #000000`.
  - 22x22: `1,4 20×15 #000000`; `2,5 18×13 #DDDDDD`; `2,5 18×1
    #FFFFFF`; `2,5 1×13 #FFFFFF`; `2,17 18×1 #999999`; `19,5 1×13
    #999999`; `4,7 10×9 #000000`; `5,8 8×7 #FFFFFF`; `16,6 3×9
    #000000`; `17,7 1×7 #FFFFFF`; `16,16 3×2 #000000`.
  - 16x16: `1,2 14×11 #000000`; `2,3 12×9 #DDDDDD`; `2,3 12×1
    #FFFFFF`; `2,3 1×9 #FFFFFF`; `2,11 12×1 #999999`; `13,3 1×9
    #999999`; `3,5 6×6 #000000`; `4,6 4×4 #FFFFFF`; `11,4 2×9
    #000000`; `11,5 1×7 #FFFFFF`.

  In each list the first six elements are the body outline, fill and
  bevels, the next two are the surface frame and face, and the last
  two or three are the pen barrel, stripe and (at 22x22 and 32x32)
  tip. Validate by XML only, never by rasterizing: `convert`'s MSVG
  reader bleeds 1px rects, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside that size's `media-floppy`
  row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths to
  `SHIPPED_ICONS` beside the other `devices` paths, and name the
  input-tablet icon in the comment above the list where `media-floppy`
  is named.
- `tests/support/icon/shape_pins.py`: pin the three drawings in
  `ICON_SHAPES` from the lists above.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `input-tablet` in the last cell: no reference pixels
  were used, the name is a KDE-required value read from
  `libkwin.so.6` (the installed `libkwin.so.6` carries the bare
  `input-tablet` literal), the shared MIME database gives the name no
  `generic-icon` binding, and the tablet-with-surface-and-pen drawing
  is this theme's own choice.
- `docs/installing.md`: add the tablet icon to the sentence
  listing the icon theme's placeholder illustrations and their sizes,
  beside the floppy-disk sentence.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`, `tests/support/icon/shape_pins.py`,
`docs/invariants.md`, `docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size, carries a placeholder
  marker and has a `PLACEHOLDERS.md` row; the existing inventory,
  palette, geometry and placeholder-register tests cover all three.
- Changing an element's position, size, fill or order, the surface's
  position or size, or the pen's position or size, in one file makes
  `test_each_icon_draws_its_pinned_artwork` fail; dropping a file
  while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The new fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme` puts
  the three files in the installed theme, and uninstalling removes them
  (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into a
  scratch `XDG_DATA_HOME`, use a scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`), `XDG_CACHE_HOME` and
  `XDG_RUNTIME_DIR`, unset `DISPLAY` and `WAYLAND_DISPLAY`, and set
  `QT_QPA_PLATFORM=offscreen`. `input-tablet` resolves to the theme's
  32x32 file (at planning time, before this change, it resolved to
  Breeze's `devices/64` file), and `input-keyboard` stays on the
  theme's 32x32 file. Report the output in VERIFIED.
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
