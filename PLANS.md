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

### Platinum icon theme: draw Squashfs images with an original `application-vnd.squashfs` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A Squashfs filesystem image file (`*.sqsh`, as the file
manager identifies it) draws Breeze's art beside the Platinum documents
and folders. Ship one original placeholder icon,
`application-vnd.squashfs`, at 16x16, 22x22 and 32x32, in the same
mimetype-item series as the landed `application-vnd.efi.iso` optical
disc and the in-flight sqlite3, backup-file, core-dump,
python-bytecode, X.509-certificate and Android-package entries.
Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/vnd.squashfs` ("Squashfs filesystem image") with no
`<icon>` element, no `<generic-icon>` element, no `<alias>` element,
the single glob `<glob pattern="*.sqsh">` at the default weight 50,
one `<magic>` holding the two offset-0 string matchers `sqsh` and
`hsqs`, and `<sub-class-of type="application/vnd.efi.img">` ("Raw disk
image"); no other MIME type in the database declares a `.sqsh` glob,
and the string `application-vnd.squashfs` occurs 0 times in the
database (`str.count` is 0 — `grep -c` counts lines, not matches).
With no icon element the type asks its literal name; the theme's
`index.theme` declares `Inherits=breeze`, so the lookup falls through
to Breeze's exact-name file. Planning-time probe on 2026-11-24 with
`kiconfinder6`, the theme installed into scratch XDG homes
(`XDG_DATA_DIRS=/usr/share` naming the scratch data root beside the
system data root, `[Icons] Theme=org.macos8.desktop` in the scratch
`kdeglobals`, `QT_QPA_PLATFORM=offscreen`, no `DISPLAY`):
`application-vnd.squashfs` resolved to
`:/icons/breeze/mimetypes/32/application-vnd.squashfs.svg` while
`text-x-generic` resolved to the theme's own 32x32 file — the gap is
real, not the screened-out shape where the theme's own generic art
wins. No reference screenshot shows a Squashfs item icon, so no
reference pixels are used and the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/application-vnd.squashfs.svg` under `16x16`, `22x22`
  and `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme`
  already declares the three MimeTypes directories. Give each file the
  XML declaration, the comment `<!-- PLACEHOLDER: original Squashfs
  filesystem-image illustration pending user-approved artwork. -->`, a
  short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art shares the disc family (every
  drawing element of that size's `devices/media-optical.svg` body:
  the black ring and the grey face) and holds three white tapering
  bands squeezed down the face — the top band widest, the lower bands
  narrower, a stack being squashed downward — an original
  filesystem-image mark distinct from the ISO disc's capital I and hub
  rings, the shell script's `>_` prompt, JSON's curly braces,
  BitTorrent's download arrow, the PGP key, the SQLite canister, the
  crash core's square ring and the certificate's seal-and-ribbons:
  - 32x32: `circle cx="16" cy="16" r="14"` `#000000`, `circle
    cx="16" cy="16" r="13"` `#DDDDDD`; then, all `#FFFFFF`, the
    bands `7,10 18×3` (rows 10..12), `9,15 14×3` (rows 15..17) and
    `11,20 10×3` (rows 20..22); every band sits inside the face.
  - 22x22: `circle cx="11" cy="11" r="10"` `#000000`, `circle
    cx="11" cy="11" r="9"` `#DDDDDD`; then, all `#FFFFFF`, the
    bands `5,7 12×2` (rows 7..8), `6,10 10×2` (rows 10..11) and
    `7,13 8×2` (rows 13..14); every band sits inside the face.
  - 16x16: `circle cx="8" cy="8" r="7"` `#000000`, `circle
    cx="8" cy="8" r="6"` `#DDDDDD`; then, all `#FFFFFF`, the
    bands `4,4 8×2` (rows 4..5), `5,7 6×2` (rows 7..8) and
    `6,10 4×2` (rows 10..11); every band sits inside the face.

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the ISO disc-image row,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above (the ring and face circles in
  document order, then the three bands).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-vnd.squashfs` in the last cell, as the
  `application-pgp-keys` sentence there does.
- `docs/installing.md`: add the Squashfs icon to the sentence listing
  the icon theme's placeholder illustrations and their sizes.
- The in-flight sqlite3, backup-file, core-dump, python-bytecode,
  X.509-certificate and Android-package entries edit the same
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
  exactly the elements listed for that size (the ring and face circles
  matching the `application-vnd.efi.iso.svg` pin's first two elements,
  then the three bands), carries a placeholder marker and has a
  `PLACEHOLDERS.md` row; the existing inventory, palette, geometry and
  placeholder-register tests cover all three.
- Changing one band's position, size or fill, or the element order, in
  one file makes the geometry test fail; dropping a file while leaving
  it shipped makes
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
  `application-vnd.squashfs` resolves to the theme's 32x32
  `mimetypes/application-vnd.squashfs.svg` (at planning time, before
  this change, it resolved to Breeze's
  `:/icons/breeze/mimetypes/32/application-vnd.squashfs.svg`), and
  `text-x-generic` still resolves to the theme's own file. Report the
  output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

---
### Platinum icon theme: draw WIM disk images with an original `application-x-ms-wim` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A WIM disk image (`.wim` or `.swm`) maps to the shared MIME
database's canonical type `application/x-ms-wim` ("WIM disk image"),
which the database gives no `generic-icon` and no `<icon>` element,
so there is no fallback file for the lookup to reach, and Breeze
ships the exact name: under this theme a WIM file draws Breeze's art
with nothing of this theme's series beside it — ship one original
placeholder icon, `application-x-ms-wim`, at 16x16, 22x22 and 32x32,
in the same mimetype-item series as the shipped
`application-x-sharedlib` shared-library window. Provenance: the
installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/x-ms-wim` ("WIM disk image", with the acronym WIM
expanded to "Windows Imaging Format") with no `<generic-icon>`
element, no `<icon>` element, no `<alias>` elements and no
`<sub-class-of>`, one `<magic>` matcher at priority 50 (the string
`MSWIM\0\0\0` at offset 0) and the two globs `*.wim` and `*.swm`
(each at the default weight 50, and each unique in the database — no
other type shares either glob), and holds zero occurrences of the
hyphenated name `application-x-ms-wim` (`str.count` is 0; the only
`x-ms-wim` occurrence is the type declaration itself), so one file
covers exactly the canonical name and no alias file is shipped. The
planning-time probe on 2026-11-24 with `kiconfinder6`, the theme
installed into scratch XDG homes (`HOME`, `XDG_CONFIG_HOME`,
`XDG_CACHE_HOME` and `XDG_RUNTIME_DIR` in a scratch tree,
`XDG_DATA_HOME` naming a scratch data root holding the copy of the
theme under `icons/` with the installed Breeze reachable beside it,
`XDG_DATA_DIRS=/usr/share`, `[Icons]
Theme=org.macos8.desktop` written into the scratch `kdeglobals` with
`kwriteconfig6 --file`, `QT_QPA_PLATFORM=offscreen`, no `DISPLAY`
and no `WAYLAND_DISPLAY`): `application-x-ms-wim` resolved to
Breeze's `:/icons/breeze/mimetypes/32/application-x-ms-wim.svg`
while `application-x-sharedlib`, `application-x-executable` and
`text-x-generic` resolved to the theme's own 32x32 files — Breeze's
exact-name file is the only art the lookup can find, so the theme
must ship the name to put a WIM file in the series. No reference
screenshot shows a WIM disk-image icon, so no reference pixels are
used and the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/application-x-ms-wim.svg` under `16x16`, `22x22`
  and `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme`
  already declares the three MimeTypes directories. Give each file
  the XML declaration, the comment `<!-- PLACEHOLDER: original WIM
  disk-image illustration pending user-approved artwork. -->`, a
  short comment saying it is our own drawing in the Platinum
  palette, not traced from anyone's artwork, and a root with
  matching `width`, `height` and `viewBox`. The art shares the
  program window (every drawing element of
  `mimetypes/application-x-sharedlib.svg` at that size) and holds a
  black split image plate — a plate with notched corners cut by a
  white vertical gap, the split-volume mark for the two globs the
  type owns (`.wim` and the split `.swm`), an original mark distinct
  from the executable's right-pointing triangle, the shared
  library's two-bar stack, the JSON braces, the Perl capital P, the
  archive letters, the download arrow, the PGP key, the backup
  tilde, the crash core band, the database canister, the EFI-ISO
  capital-I disc, the pending Squashfs tapering bands and the
  Python-bytecode chip:
  - 16x16: the window elements `rect 1,2 14×12 #000000`, `rect 2,3
    12×3 #DDDDDD`, `rect 2,3 12×1 #FFFFFF`, `rect 4,4 8×1 #999999`
    and `rect 2,7 12×6 #FFFFFF`; plate, all `#000000`: `rect 3,8
    10×4` (columns 3..12, rows 8..11); notches and gap, all
    `#FFFFFF`: `rect 3,8 1×1`, `rect 12,8 1×1`, `rect 3,11 1×1`,
    `rect 12,11 1×1` and the split `rect 8,8 1×4` — every element
    inside the body rows 7..12 and columns 2..13.
  - 22x22: the window elements `rect 2,3 18×16 #000000`, `rect 3,4
    16×3 #DDDDDD`, `rect 3,4 16×1 #FFFFFF`, `rect 5,5 12×1 #999999`
    and `rect 3,8 16×10 #FFFFFF`; plate, all `#000000`: `rect 4,9
    14×7` (columns 4..17, rows 9..15); notches and gap, all
    `#FFFFFF`: `rect 4,9 1×1`, `rect 17,9 1×1`, `rect 4,15 1×1`,
    `rect 17,15 1×1` and the split `rect 11,9 1×7` — every element
    inside the body rows 8..17 and columns 3..18.
  - 32x32: the window elements `rect 3,5 26×22 #000000`, `rect 4,6
    24×4 #DDDDDD`, `rect 4,6 24×1 #FFFFFF`, `rect 6,8 20×1 #999999`
    and `rect 4,11 24×15 #FFFFFF`; plate, all `#000000`: `rect 7,14
    19×9` (columns 7..25, rows 14..22); notches and gap, all
    `#FFFFFF`: `rect 7,14 1×1`, `rect 25,14 1×1`, `rect 7,22 1×1`,
    `rect 25,22 1×1` and the split `rect 16,14 1×9` (the gap leaves
    two 9-column halves, columns 7..15 and 17..25) — every element
    inside the body rows 11..25 and columns 4..27.

  Validate by XML only, never by rasterizing: `convert`'s MSVG
  reader bleeds 1px shapes, so the pins below are the drawing
  contract.
- `PLACEHOLDERS.md`: one row per file beside that size's
  `application-x-sharedlib` row, described as the marker describes
  it.
- `tests/support/icon/theme_inventory.py`: add the three paths
  beside the other `mimetypes` paths in `SHIPPED_ICONS`, and extend
  the mimetypes comment above them to name the WIM disk image in
  the type-spelled series.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three
  drawings in `PINS` from the lists above, spreading the existing
  `_PROGRAM_WINDOW_16`, `_PROGRAM_WINDOW_22` and `_PROGRAM_WINDOW_32`
  tuples from `tests/support/icon/shape_pins/_shared.py` for the
  window elements (the tuples already exist; `_shared.py` itself
  needs no change), then the plate, the four notches and the split.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-x-ms-wim` in the last cell, as the
  `application-x-sharedlib` sentence there does.
- `docs/installing.md`: add the WIM disk-image icon to the sentence
  listing the icon theme's placeholder illustrations and their
  sizes.
- The in-flight Python-bytecode and Squashfs entries edit the same
  inventory block, `PINS` registry, invariants row and
  installing.md sentence; this entry sits behind them in the queue,
  so rebase on whatever they have landed when picking it up,
  keeping one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the window elements
  matching the same size's `application-x-sharedlib.svg` window, in
  the same order, then the plate, the four notches and the split),
  carries a placeholder marker and has a `PLACEHOLDERS.md` row; the
  existing inventory, palette, geometry and placeholder-register
  tests cover all three.
- Changing one plate, notch or split rectangle's position, size,
  fill or the element order in one file makes the geometry test
  fail; dropping a file while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The plate's `#000000` fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME`, use a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`, written with `kwriteconfig6 --file`),
  `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset `DISPLAY` and
  `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-x-ms-wim` resolves to the theme's 32x32
  `mimetypes/application-x-ms-wim.svg` (at planning time, before
  this change, it resolved to Breeze's
  `:/icons/breeze/mimetypes/32/application-x-ms-wim.svg`), and
  `application-x-sharedlib`, `application-x-executable` and
  `text-x-generic` still resolve to the theme's own files. Report
  the output in VERIFIED.
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
