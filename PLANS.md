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

### Platinum icon theme: draw videos with an original `video-x-generic` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Needs review 2026-11-24 by feature: plan defect — the acceptance criterion
“video-mp4 stays on Breeze's own file” is disproven by measurement.** With the
theme installed (`make install INSTALL_PACKAGES=icon-theme` into a scratch
`XDG_DATA_HOME`) and the three planned `video-x-generic.svg` files added,
`kiconfinder6` (offscreen, scratch `HOME`/`XDG_CONFIG_HOME`/`XDG_CACHE_HOME`/
`XDG_RUNTIME_DIR`) resolves `video-mp4`, `video-webm` and `video-mpeg` to the
theme's own 32x32 `video-x-generic.svg` — not to Breeze's per-type files
(control without the theme installed: `:/icons/breeze/mimetypes/32/
video-mp4.svg` and kin). KIconLoader's generic fallback substitutes
`<type>-x-generic` for a missing MIME icon before the internal Breeze
resource, so shipping `video-x-generic` captures `video/mp4`, `video/webm`
and `video/mpeg` too, contradicting the plan's “one file covers only its own
name” scope claim (“video/mp4 … keep Breeze's per-type art”). The criterion
is self-contradictory while the plan also mandates shipping the icon; the
plan role needs to decide whether the fallback capture is acceptable and
rewrite the criterion and scope, or retire the entry.

**Goal.** A video file without Breeze art of its own type name — Flash
movies, Matroska, RealMedia, SMIL, MXF and their kin in the file manager
or an open or save dialog — is drawn with the theme's own screen art
beside the Platinum documents. Ship one original placeholder icon,
`video-x-generic`, at 16x16, 22x22 and 32x32. The installed shared MIME
database gives exactly 14 MIME types `generic-icon name="video-x-generic"`
(counted on `/usr/share/mime/packages/freedesktop.org.xml`):
`application/smil+xml`, `application/vnd.ms-wpl`, `video/x-flv`,
`video/x-javafx`, `video/vnd.youtube.yt`, `application/x-matroska`,
`application/mxf`, `application/annodex`, `application/ogg`,
`application/x-quicktime-media-link`,
`application/vnd.adobe.flash.movie`, `application/vnd.rn-realmedia`,
`application/x-netshow-channel` and `application/sdp`. Types the
database gives no `generic-icon` for (`video/mp4`, `video/webm`,
`video/mpeg`) keep Breeze's per-type art and are out of scope.
Planning-time probe with `kiconfinder6` under scratch `XDG_DATA_HOME`,
`XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
`kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, with `DISPLAY` and
`WAYLAND_DISPLAY` unset and `QT_QPA_PLATFORM=offscreen`: with the theme
installed, `video-x-generic` resolved to
`:/icons/breeze/mimetypes/32/video-x-generic.svg` (the loader's fallback
past the missing name) and `video-mp4` to Breeze's own
`video-mp4.svg`; after a stand-in `video-x-generic.svg` was added to the
installed copy's three `mimetypes` directories, `video-x-generic`
resolved to the copy's 32x32 file — so one file covers only its own
name; ship no alias files and nothing but `video-x-generic`. Audio,
presentation, font and text names are covered by other plans or stay out
of scope; this plan shares no drawing with them.

**Approach.**

- Add `mimetypes/video-x-generic.svg` under `16x16`, `22x22` and `32x32`
  of `theme/icons/org.macos8.desktop/`. `index.theme` already declares
  the three directories. Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original video illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art is a display screen with a play
  triangle: a black frame, a white face, a black triangle, and a black
  stand (neck and base). Each file holds these elements in order, written
  `x,y width×height fill` for rects and a path `d` for the triangle:
  - 32x32 (5): rects `3,7 26×20 #000000`; `4,8 24×18 #FFFFFF`; path
    `M13 11 L23 17 L13 23 Z #000000`; rects `12,27 8×2 #000000`;
    `8,29 16×2 #000000`.
  - 22x22 (5): rects `2,5 18×13 #000000`; `3,6 16×11 #FFFFFF`; path
    `M9 8 L15 11 L9 14 Z #000000`; rects `8,19 6×1 #000000`;
    `5,20 12×1 #000000`.
  - 16x16 (5): rects `1,3 14×10 #000000`; `2,4 12×8 #FFFFFF`; path
    `M7 6 L10 8 L7 10 Z #000000`; rects `6,13 4×1 #000000`;
    `4,14 8×1 #000000`.

  These were drawn to read as a screen with a play triangle centred on
  the face and a two-part stand under the frame at every size (painted
  rect by rect at planning time).
- `PLACEHOLDERS.md`: one row per file beside that size's
  `image-x-generic` row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths to
  `SHIPPED_ICONS` beside the flash-media paths, and name the video icon
  in the comment above it (the comment already records which
  `generic-icon` groups the shipped mimetype names cover — give the 14
  video types there).
- `tests/support/icon/shape_pins.py`: pin the three drawings in
  `ICON_SHAPES` from the lists above (translate each list to `_shape`
  calls: rects keep their attributes, the triangle is
  `_shape("path", d="M13 11 L23 17 L13 23 Z", fill="#000000")` and kin);
  the existing `test_the_geometry_registry_covers_every_shipped_icon`
  and `test_each_icon_draws_its_pinned_artwork` then enforce the pins in
  both directions.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `video-x-generic` in the last cell: no reference pixels
  were used, the name is the `generic-icon` of 14 MIME types in the
  installed shared MIME database (the types the database gives no
  `generic-icon` of their own — `video/mp4`, `video/webm`, `video/mpeg`
  — keep Breeze's per-type art), the screen-and-triangle drawing is this
  theme's own choice.
- `docs/installing.md`: add the video icon to the sentence listing the
  icon theme's placeholder illustrations and their sizes.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`, `tests/support/icon/shape_pins.py`,
`tests/test_icon_theme_geometry.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding exactly
  the elements listed for that size, carries a placeholder marker and
  comment and has a `PLACEHOLDERS.md` row; the existing inventory, palette,
  geometry and placeholder-register tests cover all three.
- Changing a rectangle's position, size or fill, the triangle's `d`, or
  the element order in one file makes the geometry pin fail.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme` puts
  the three files in the installed theme, and uninstalling removes them
  (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into a
  scratch `XDG_DATA_HOME` (create the destination `icons` directory before
  copying the theme into it, so the copy does not flatten), use a scratch
  `HOME`, `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset `DISPLAY`
  and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `video-x-generic` resolves to the theme's file, and `video-mp4` stays
  on Breeze's own file. Report the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full `make check`
  after the final edit, apart from main's known-red tests.

### Platinum icon theme: draw mice with an original `input-mouse` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** When KDE lists an input device — the `input-` device-icon
family KDE builds from the udev subsystem (`ID_INPUT_MOUSE` is the udev
property of a mouse; the installed `libKF6Solid.so.6.13.0` carries the
bare `input` stem) — the icon lookup falls through to Breeze today.
Ship one original placeholder icon, `input-mouse`, at 16x16, 22x22 and
32x32 in the theme's `devices` family.

Planning-time probe with `kiconfinder6` under scratch `XDG_DATA_HOME`,
`XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
`kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, with `DISPLAY`
and `WAYLAND_DISPLAY` unset and `QT_QPA_PLATFORM=offscreen`:
`input-mouse` resolved to `:/icons/breeze/devices/64/input-mouse.svg`
while the shipped `x-office-document` resolved to this theme's 32x32
file. No repo file ships or mentions `input-mouse` (grep across
`PLANS.md`, `PLANS-DONE.md`, `PLACEHOLDERS.md`, `docs/`, the theme tree
and `tests/support/icon/` finds nothing); no Planned entry covers it.
Out of scope: ship no alias files and nothing but `input-mouse`;
`input-keyboard` waits for its own plan.

**Approach.**

- Add `devices/input-mouse.svg` under `16x16`, `22x22` and `32x32` of
  `theme/icons/org.macos8.desktop/`. `index.theme` already declares the
  three directories. Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original mouse illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art is a mouse: a black-outlined rounded
  body with a grey face, a white two-button band across the top, a
  black split between the buttons and a black scroll wheel below the
  band. Each file holds exactly these five `rect` elements in
  document order, written `x,y width×height` with its `rx` and fill:
  - 32x32: `7,5 18×22 rx=9 #000000`; `8,6 16×20 rx=8 #DDDDDD`; `8,6
    16×7 #FFFFFF`; `15,6 2×7 #000000`; `14,13 4×7 rx=2 #000000`.
  - 22x22: `5,3 12×16 rx=6 #000000`; `6,4 10×14 rx=5 #DDDDDD`; `6,4
    10×5 #FFFFFF`; `10,4 2×5 #000000`; `10,10 2×4 rx=1 #000000`.
  - 16x16: `3,2 10×12 rx=5 #000000`; `4,3 8×10 rx=4 #DDDDDD`; `4,3
    8×3 #FFFFFF`; `7,3 2×3 #000000`; `7,7 2×3 rx=1 #000000`.
- `PLACEHOLDERS.md`: one row per file beside that size's device rows,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths to
  `SHIPPED_ICONS` beside the other `devices` paths, name the mouse icon
  in the inventory comment above them, and say in the comment that the
  name is the input-device icon name KDE builds from the udev
  subsystem.
- `tests/support/icon/shape_pins.py`: pin the three drawings in
  `ICON_SHAPES` from the element lists above (each pin carries the
  rect's `rx`, so dropping a radius fails the pin).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `input-mouse` in the last cell: no reference pixels
  were used, the name is the input-device icon name KDE builds as
  `input-` + the udev subsystem (the installed `libKF6Solid.so.6.13.0`
  contains the bare `input` stem and the udev property
  `ID_INPUT_MOUSE` names the mouse), and the rounded-body-and-wheel
  drawing is this theme's own choice.
- `docs/installing.md`: add the mouse icon to the sentence listing the
  device placeholder illustrations and their sizes.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the five rectangles listed for that size in order, carries a
  placeholder marker and has a `PLACEHOLDERS.md` row; the existing
  inventory, palette, geometry and placeholder-register tests cover
  all three.
- Changing a rectangle's position, size, radius or fill, or the
  element order, in one file makes the geometry test fail.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling removes
  them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into
  a scratch `XDG_DATA_HOME`, use a scratch `HOME`, `XDG_CONFIG_HOME`
  (with `[Icons] Theme=org.macos8.desktop` in `kdeglobals`),
  `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset `DISPLAY` and
  `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `input-mouse` resolves to the theme's new 32x32 file, and
  `x-office-document` and `text-x-generic` stay on their shipped theme
  files. Report the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full `make
  check` after the final edit, apart from main's known-red tests.

### Platinum icon theme: draw the desktop computer with an original `computer` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** The Computer place — the machine root Dolphin's places panel and
KInfoCenter draw — is drawn with Breeze's art beside the Platinum hard
disk, folder and Trash. Ship one original placeholder icon, `computer`,
at 16x16, 22x22 and 32x32.
Planning-time probe with `kiconfinder6` and a copy of the theme selected
through scratch XDG homes (the control, `x-office-document`, resolved to
the theme's 32x32 file): `computer`, `input-mouse`, `input-keyboard`,
`printer`, `video-display`, `camera-photo`, `phone`, `network-wireless`,
`battery` and `media-floppy` all resolved to Breeze. `computer` is the
most visible of these: it names the machine itself in the places list.
The installed `libKF6Solid.so.6` contains exactly two names with this
stem (`strings -e l`): `computer` and `computer-apple-ipad`. One file
covers only its own name, and the iPad subname is a niche surface, so
this plan ships `computer.svg` only; `computer-apple-ipad` stays out of
scope, as do the other probed names. This plan shares no drawing with
the drive family: the computer is a monitor over a case, not a drive
body, so it gets its own pins and no sharing test.

**Approach.**

- Add `devices/computer.svg` under `16x16`, `22x22` and `32x32` of
  `theme/icons/org.macos8.desktop/`. `index.theme` already declares the
  three directories. Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original desktop-computer illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art is a Platinum monitor over its desktop
  case: the raised #DDDDDD face with the 1px #000000 outline and the
  #FFFFFF/#999999 bevel on both, a #000000 screen with a white glint,
  a #000000 stand and drive slot and a #000000 power light. Each file
  holds these elements in order, written `x,y width×height fill` for
  rects and `cx,cy r fill` for circles:
  - 32x32: `4,2 24×18 #000000`; `5,3 22×16 #DDDDDD`; `5,3 22×2
    #FFFFFF`; `5,3 1×16 #FFFFFF`; `5,17 22×2 #999999`; `26,3 1×16
    #999999`; `8,6 16×10 #000000`; `10,8 6×2 #FFFFFF`; `10,12 4×1
    #999999`; `14,20 4×1 #000000`; `10,21 12×9 #000000`; `11,22 10×7
    #DDDDDD`; `11,22 10×1 #FFFFFF`; `11,22 1×7 #FFFFFF`; `11,28 10×1
    #999999`; `20,22 1×7 #999999`; `13,25 5×2 #000000`; `19,26 1
    #000000`.
  - 22x22: `2,1 18×13 #000000`; `3,2 16×11 #DDDDDD`; `3,2 16×1
    #FFFFFF`; `3,2 1×11 #FFFFFF`; `3,12 16×1 #999999`; `18,2 1×11
    #999999`; `5,4 12×7 #000000`; `6,5 4×2 #FFFFFF`; `10,14 2×1
    #000000`; `6,15 10×6 #000000`; `7,16 8×4 #DDDDDD`; `7,16 8×1
    #FFFFFF`; `7,16 1×4 #FFFFFF`; `7,19 8×1 #999999`; `14,16 1×4
    #999999`; `8,17 3×1 #000000`.
  - 16x16: `1,1 14×9 #000000`; `2,2 12×7 #DDDDDD`; `2,2 12×1 #FFFFFF`;
    `2,2 1×7 #FFFFFF`; `2,8 12×1 #999999`; `13,2 1×7 #999999`; `4,3
    8×5 #000000`; `5,4 3×1 #FFFFFF`; `7,10 2×1 #000000`; `4,11 8×4
    #000000`; `5,12 6×2 #DDDDDD`; `5,12 6×1 #FFFFFF`; `5,12 1×2
    #FFFFFF`; `10,12 1×2 #999999`; `5,13 3×1 #999999`.

  These were rendered at planning time and read as a monitor over a
  desktop case at each size, the screen glint clear of the bevel.
- `PLACEHOLDERS.md`: one row per file beside that size's `drive-harddisk`
  row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths to
  `SHIPPED_ICONS` beside the other `devices` paths, and name the desktop
  computer in the comment above it.
- `tests/support/icon/shape_pins.py`: pin the three drawings in
  `ICON_SHAPES` from the lists above.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `computer` in the last cell: no reference pixels were
  used, the name is a KDE-required value read from `libKF6Solid.so.6`
  (which also loads `computer-apple-ipad`, out of scope), and the
  monitor-over-case drawing is this theme's own choice.
- `docs/installing.md`: add the desktop-computer icon to the sentence
  listing the icon theme's placeholder illustrations and their sizes.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`, `tests/support/icon/shape_pins.py`,
`docs/invariants.md`, `docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding exactly
  the elements listed for that size, carries a placeholder marker and has
  a `PLACEHOLDERS.md` row; the existing inventory, palette, geometry and
  placeholder-register tests cover all three.
- Changing an element's position, size or fill, the power light's centre,
  radius or fill, or the element order, in one file makes
  `test_each_icon_draws_its_pinned_artwork` fail; dropping a file while
  leaving it shipped makes `test_the_geometry_registry_covers_every_shipped_icon`
  fail.
- The new fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme` puts
  the three files in the installed theme, and uninstalling removes them
  (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into a
  scratch `XDG_DATA_HOME`, use a scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`), `XDG_CACHE_HOME` and
  `XDG_RUNTIME_DIR`, unset `DISPLAY` and `WAYLAND_DISPLAY`, and set
  `QT_QPA_PLATFORM=offscreen`. `computer` resolves to the theme's 32x32
  file, and `media-floppy`, `input-mouse`, `input-keyboard`, `printer`,
  `video-display`, `camera-photo`, `phone`, `network-wireless` and
  `battery` stay on Breeze. Report the output in VERIFIED.
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
