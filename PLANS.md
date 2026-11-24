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

### Platinum icon theme: draw a modem with an original `modem` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A modem is drawn with no Platinum art at all today: the name
`modem` resolves to nothing on this system. Ship one original
placeholder icon, `modem`, at 16x16, 22x22 and 32x32, in the same
devices series as the landed `computer`, `media-flash`, `printer`,
`phone`, `battery`, `camera-photo`, `media-floppy`, `network-server`
and `network-vpn` files and the waiting `video-display` entry.
Provenance: the installed `libKF6BluezQt.so.6.13.0` carries the bare
`modem` literal (`strings -e l`) and no reduced `modem-*` subnames
(`grep -o "modem[a-z-]*"` over the same library prints only `modem`),
the same library-literal pattern as the `media-floppy` plan's Solid
anchor; BluezQt's modem device type is what a Solid modem device is
listed as. Breeze ships the name nowhere: `find
/usr/share/icons/breeze -name 'modem*'` is empty, and the planning-time
`kiconfinder6 modem` probe (theme installed, 2026-11-24) exits 1 with
no output — so unlike the floppy, VPN and server entries, the theme
wins the name outright instead of competing with Breeze's art. This
time that also means the resolution change is from "nothing" to the
theme's file, which the manual check below pins. No reference
screenshot shows a modem icon: no reference pixels are used, and the
drawing is this theme's own choice.

**Approach.**

- Add `devices/modem.svg` under `16x16`, `22x22` and `32x32` of
  `theme/icons/org.macos8.desktop/`. `index.theme` already declares the
  three directories. Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original modem illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art is a flat Platinum external modem
  seen from the front: a wide box with the 1px #000000 outline and the
  #FFFFFF/#999999 bevels on the #DDDDDD face, a telephone jack on the
  right, and a row of black indicator LEDs along the front. Each file
  holds these elements in order, written `x,y width×height fill` for
  rects:
  - 32x32: `3,8 26×18 #000000`; `4,9 24×16 #DDDDDD`; `4,9 24×1
    #FFFFFF`; `4,9 1×16 #FFFFFF`; `4,24 24×1 #999999`; `27,9 1×16
    #999999`; `21,11 5×3 #000000`; `22,12 3×1 #FFFFFF`; `7,20 2×2
    #000000`; `11,20 2×2 #000000`; `15,20 2×2 #000000`.
  - 22x22: `2,6 18×13 #000000`; `3,7 16×11 #DDDDDD`; `3,7 16×1
    #FFFFFF`; `3,7 1×11 #FFFFFF`; `3,17 16×1 #999999`; `18,7 1×11
    #999999`; `14,9 4×3 #000000`; `15,10 2×1 #FFFFFF`; `5,15 2×2
    #000000`; `9,15 2×2 #000000`; `13,15 2×2 #000000`.
  - 16x16: `1,4 14×10 #000000`; `2,5 12×8 #DDDDDD`; `2,5 12×1
    #FFFFFF`; `2,5 1×8 #FFFFFF`; `2,12 12×1 #999999`; `13,5 1×8
    #999999`; `9,7 3×2 #000000`; `4,10 1×1 #000000`; `6,10 1×1
    #000000`; `8,10 1×1 #000000`.

  In each list the first six elements are the body outline, fill and
  bevels, the next two or three are the jack frame and slot (the
  16x16 drawing keeps the frame and drops the slot, as the small
  floppy drawing drops its label line), and the last ones are the
  LEDs. Validate by XML only, never by rasterizing: `convert`'s MSVG
  reader bleeds 1px rects, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside that size's
  `media-floppy` row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths to
  `SHIPPED_ICONS` beside the other `devices` paths, and name the
  modem icon in the comment above the list where `media-floppy` is
  named.
- `tests/support/icon/shape_pins.py`: pin the three drawings in
  `ICON_SHAPES` from the lists above.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `modem` in the last cell: no reference pixels were
  used, the name is a KDE-required value read from
  `libKF6BluezQt.so.6` (the installed `libKF6BluezQt.so.6.13.0` carries
  the bare `modem` literal), Breeze ships the name nowhere (the
  planning-time `kiconfinder6 modem` probe of 2026-11-24 exited 1 with
  no output), and the box-with-LEDs-and-jack drawing is this theme's
  own choice.
- `docs/installing.md`: add the modem icon to the sentence listing the
  icon theme's placeholder illustrations and their sizes, beside the
  floppy-disk sentence.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`, `tests/support/icon/shape_pins.py`,
`docs/invariants.md`, `docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding exactly
  the elements listed for that size, carries a placeholder marker and has
  a `PLACEHOLDERS.md` row; the existing inventory, palette, geometry and
  placeholder-register tests cover all three.
- Changing an element's position, size, fill or order, the jack's
  position or size, or an LED's position or size, in one file makes
  `test_each_icon_draws_its_pinned_artwork` fail; dropping a file while
  leaving it shipped makes
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
  `QT_QPA_PLATFORM=offscreen`. `modem` resolves to the theme's 32x32
  file (at planning time, before this change, the probe exited 1 with
  no output), and `x-office-document` stays on the theme's 32x32 file.
  Also record what `camera-web` and `input-tablet` resolve to, without
  pinning them. Report the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full `make
  check` after the final edit, apart from main's known-red tests.

### Platinum icon theme: draw displays with an original `video-display` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A display — the device the installed KInfoCenter draws for its
information modules (`video-display` is the plugin icon of the installed
KInfoCenter EDID, GLX, EGL, OpenCL and Vulkan modules, read with
`strings` from each module's metadata in the installed
`/usr/lib/x86_64-linux-gnu/qt6/plugins/plasma/kcms/kinfocenter/kcm_edid.so`
and its four siblings) — is drawn with Breeze's art beside the Platinum
placeholders. Ship one original placeholder icon, `video-display`, at
16x16, 22x22 and 32x32, in the same devices series as the landed
`computer`, `printer`, `phone`, `battery`, `camera-photo`, `network-vpn`
and `network-server` files and the waiting `video-x-generic` and
`media-floppy` entries. The drawing is a monitor alone: the `computer`
file already draws a monitor above a desktop case, and this one is the
display without the case. Planning-time probe with `kiconfinder6` under
scratch `XDG_DATA_HOME`, `XDG_CONFIG_HOME` (with
`[Icons] Theme=org.macos8.desktop` in `kdeglobals`), `XDG_CACHE_HOME`
and `XDG_RUNTIME_DIR`, with `DISPLAY` and `WAYLAND_DISPLAY` unset and
`QT_QPA_PLATFORM=offscreen`: with the theme installed and no
`video-display` of its own, `video-display` resolved to Breeze's
internal `:/icons/breeze/devices/64/video-display.svg`. The brightness
applet (`org.kde.plasma.brightness`) draws `video-display-brightness`,
but Breeze ships that exact name
(`:/icons/breeze/devices/22/video-display-brightness.svg`, measured in
the same probe), so the shipped display file does not capture it: one
file covers its own name only — no alias files, nothing but
`video-display`. The other recorded straggler, `network-wireless`,
stays out of scope and stays on Breeze, because the same probe shows
Breeze ships every name the network applet asks for (`network-wireless`
resolved to Breeze's internal `:/icons/breeze/devices/22/network-wireless.svg`
and `network-wireless-on` and `network-wireless-80` to Breeze's system
`status/24` files), so no theme file could win there (re-verified
2026-11-24 by the plan role). No reference screenshot shows a display
icon: no reference pixels are used, and the monitor drawing is this
theme's own choice.

**Approach.**

- Add `devices/video-display.svg` under `16x16`, `22x22` and `32x32` of
  `theme/icons/org.macos8.desktop/`. `index.theme` already declares the
  three directories. Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original display illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art is a Platinum monitor alone: a screen
  housing with the 1px #000000 outline, the #DDDDDD face and the
  #FFFFFF/#999999 bevel, a #000000 screen with white and grey glints,
  and a #000000 stand (neck and base). Each file holds these elements
  in order, written `x,y width×height fill` for rects:
  - 32x32 (11): `3,3 26×22 #000000`; `4,4 24×20 #DDDDDD`; `4,4 24×2
    #FFFFFF`; `4,4 1×20 #FFFFFF`; `4,22 24×2 #999999`; `27,4 1×20
    #999999`; `7,7 18×13 #000000`; `9,9 7×2 #FFFFFF`; `9,15 5×1
    #999999`; `14,25 4×2 #000000`; `10,27 12×3 #000000`.
  - 22x22 (11): `2,2 18×15 #000000`; `3,3 16×13 #DDDDDD`; `3,3 16×2
    #FFFFFF`; `3,3 1×13 #FFFFFF`; `3,14 16×2 #999999`; `18,3 1×13
    #999999`; `5,5 12×8 #000000`; `6,6 5×2 #FFFFFF`; `6,10 3×1
    #999999`; `9,17 4×1 #000000`; `6,18 10×2 #000000`.
  - 16x16 (10): `1,2 14×12 #000000`; `2,3 12×10 #DDDDDD`; `2,3 12×1
    #FFFFFF`; `2,3 1×10 #FFFFFF`; `2,12 12×1 #999999`; `13,3 1×10
    #999999`; `4,5 8×6 #000000`; `5,6 3×2 #FFFFFF`; `6,14 4×1
    #000000`; `4,15 8×1 #000000`.

  These were drawn to read as a monitor with a centred screen and a
  two-part stand under the housing at every size (painted rect by rect
  at planning time), and to stay distinct from the `computer` file's
  monitor-above-case drawing.
- `PLACEHOLDERS.md`: one row per file beside that size's `network-vpn`
  row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths to
  `SHIPPED_ICONS` beside the `network-server` paths, and name the
  display icon in the comment above them (the comment records the
  requesting surface: the five installed KInfoCenter information
  modules' plugin icons).
- `tests/support/icon/shape_pins.py`: pin the three drawings in
  `ICON_SHAPES` from the lists above (every element is a `_shape("rect",
  ...)` keeping its attributes); the existing
  `test_the_geometry_registry_covers_every_shipped_icon` and
  `test_each_icon_draws_its_pinned_artwork` then enforce the pins in
  both directions.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `video-display` in the last cell: no reference pixels
  were used, the name is the plugin icon of the five installed
  KInfoCenter EDID, GLX, EGL, OpenCL and Vulkan information modules
  (read with `strings` from the installed `.so` files under
  `.../plasma/kcms/kinfocenter/`; measured with `kiconfinder6`:
  `video-display` resolves to the shipped file), Breeze's own
  `video-display-brightness` name is not captured because Breeze ships
  that exact file, and the monitor drawing is this theme's own choice.
- `docs/installing.md`: add the display icon to the sentence listing
  the icon theme's placeholder illustrations and their sizes.

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
  `video-display` resolves to the theme's 32x32 file, and `computer`
  stays on the theme's 32x32 file. Report the output in VERIFIED.
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
