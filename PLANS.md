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

### Platinum icon theme: draw the printer with an original `printer` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** The printer — the device the Print Queue and printer-configuration
windows draw (`Icon=printer` in the installed
`org.kde.PrintQueue.desktop`, `org.kde.ConfigurePrinter.desktop` and
`org.kde.kde-add-printer.desktop` entries) — is drawn with Breeze's art
beside the Platinum drive and media icons. Ship one original placeholder
icon, `printer`, at 16x16, 22x22 and 32x32.
Planning-time probe with `kiconfinder6` and a copy of the theme selected
through scratch XDG homes (`DISPLAY` and `WAYLAND_DISPLAY` unset,
`QT_QPA_PLATFORM=offscreen`; the control, `drive-harddisk`, resolved to
the theme's 32x32 file): `printer` resolved to
`:/icons/breeze/devices/64/printer.svg`, as do `video-display`,
`camera-photo` and `phone`, which stay out of scope here. Provenance of
the name: the installed `libKF6Solid.so.6.13.0` contains no `print`
literal (`strings -e l`), so the surface that names the icon is the
installed KDE print desktop entries above; no reference screenshot in
`macos8.6-screenshots/` shows a printer, so the drawing is this theme's
own choice. Out of scope: ship no alias files and nothing but
`printer`; this plan shares no drawing with the drive family — a
printer is a body with paper sheets, not a drive body — so it gets its
own pins and no sharing test.

**Approach.**

- Add `devices/printer.svg` under `16x16`, `22x22` and `32x32` of
  `theme/icons/org.macos8.desktop/`. `index.theme` already declares the
  three directories. Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original printer illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art is a Platinum printer: a sheet feeding
  from the top, the raised #DDDDDD body with the 1px #000000 outline and
  the #FFFFFF/#999999 bevel, a #000000 output slot, a sheet emerging
  from the slot down the front, and a #000000 power light. Each file
  holds these elements in order, written `x,y width×height fill` for
  rects and `cx,cy r fill` for circles:
  - 32x32: `8,2 16×8 #000000`; `9,3 14×6 #FFFFFF`; `11,5 10×1
    #999999`; `4,10 24×13 #000000`; `5,11 22×11 #DDDDDD`; `5,11 22×1
    #FFFFFF`; `5,11 1×11 #FFFFFF`; `5,21 22×1 #999999`; `26,11 1×11
    #999999`; `9,14 14×1 #000000`; `8,15 14×12 #000000`; `9,16 12×10
    #FFFFFF`; `11,18 8×1 #999999`; `11,21 8×1 #999999`; `11,24 5×1
    #999999`; `24,18 1 #000000`.
  - 22x22: `6,1 10×6 #000000`; `7,2 8×4 #FFFFFF`; `8,3 6×1 #999999`;
    `2,7 18×9 #000000`; `3,8 16×7 #DDDDDD`; `3,8 16×1 #FFFFFF`; `3,8
    1×7 #FFFFFF`; `3,14 16×1 #999999`; `18,8 1×7 #999999`; `6,10 9×1
    #000000`; `6,11 10×8 #000000`; `7,12 8×6 #FFFFFF`; `8,14 6×1
    #999999`; `8,16 6×1 #999999`; `16,9 2×1 #000000`.
  - 16x16: `4,1 8×4 #000000`; `5,2 6×2 #FFFFFF`; `6,3 4×1 #999999`;
    `1,5 14×7 #000000`; `2,6 12×5 #DDDDDD`; `2,6 12×1 #FFFFFF`; `2,6
    1×5 #FFFFFF`; `2,10 12×1 #999999`; `13,6 1×5 #999999`; `4,8 8×1
    #000000`; `3,9 10×6 #000000`; `4,10 8×4 #FFFFFF`; `5,11 6×1
    #999999`; `5,13 6×1 #999999`; `11,7 2×1 #000000`.

  The pins read the SVG XML, so the geometry is checked by construction
  from these lists, not by rasterizing.
- `PLACEHOLDERS.md`: one row per file beside that size's `drive-harddisk`
  row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths to
  `SHIPPED_ICONS` beside the other `devices` paths, and name the printer
  in a comment above them.
- `tests/support/icon/shape_pins.py`: pin the three drawings in
  `ICON_SHAPES` from the lists above.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `printer` in the last cell: no reference pixels were
  used, the name is required by the installed KDE print desktop entries
  (`org.kde.PrintQueue.desktop` and friends) while `libKF6Solid.so.6.13.0`
  has no `print` literal, and the body-and-sheets drawing is this
  theme's own choice.
- `docs/installing.md`: add the printer icon to the sentence listing the
  icon theme's placeholder illustrations and their sizes.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`, `tests/support/icon/shape_pins.py`,
`docs/invariants.md`, `docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding exactly
  the elements listed for that size, carries a placeholder marker and has
  a `PLACEHOLDERS.md` row; the existing inventory, palette, geometry and
  placeholder-register tests cover all three.
- Changing an element's position, size or fill, the power light's
  position or size, or the element order, in one file makes
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
  `QT_QPA_PLATFORM=offscreen`. `printer` resolves to the theme's 32x32
  file, and `video-display`, `camera-photo` and `phone` stay on Breeze.
  Report the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full `make check`
  after the final edit, apart from main's known-red tests.

### Platinum icon theme: draw phones with an original `phone` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** The `phone` device name is what KDE's device views draw for
phones and the dash fallback of the `phone-apple-iphone` device icon
Solid builds for some of them, and on this host it still resolves to
Breeze: a planning-time probe on 2026-11-24 (`kiconfinder6` against a
scratch install of the theme, the `x-office-document` control resolving
to the theme's 32x32 file) showed `phone` resolving to Breeze's
devices/22 `phone.svg`. Ship one original placeholder icon, `phone`, at
16x16, 22x22 and 32x32.

**Approach.**

- Add `devices/phone.svg` under `16x16`, `22x22` and `32x32` of
  `theme/icons/org.macos8.desktop/`. `index.theme` already declares the
  three directories. Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original phone illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art is an upright Platinum smartphone: the
  raised #DDDDDD body with the 1px #000000 outline and the
  #FFFFFF/#999999 bevel, a #000000 screen, a #000000 speaker slot above
  the screen and a #000000 home button below it. Each file holds these
  elements in order, written `x,y width×height fill`:
  - 32x32: `9,2 14×28 #000000`; `10,3 12×26 #DDDDDD`; `10,3 12×1
    #FFFFFF`; `10,3 1×26 #FFFFFF`; `10,28 12×1 #999999`; `21,3 1×26
    #999999`; screen `11,7 10×14 #000000`; speaker `14,5 4×1 #000000`;
    home button `15,24 2×2 #000000`.
  - 22x22: `5,1 12×20 #000000`; `6,2 10×18 #DDDDDD`; `6,2 10×1
    #FFFFFF`; `6,2 1×18 #FFFFFF`; `6,19 10×1 #999999`; `15,2 1×18
    #999999`; screen `7,5 8×10 #000000`; speaker `9,3 4×1 #000000`;
    home button `10,16 2×2 #000000`.
  - 16x16: `3,1 10×14 #000000`; `4,2 8×12 #DDDDDD`; `4,2 8×1 #FFFFFF`;
    `4,2 1×12 #FFFFFF`; `4,13 8×1 #999999`; `11,2 1×12 #999999`;
    screen `5,4 6×7 #000000`; speaker `7,3 2×1 #000000`; home button
    `7,12 2×1 #000000`.

  The element lists were checked for geometric consistency at planning
  time (every rect lies inside its face, and the bevel rows overlay only
  the face's outermost rows as in the keyboard and computer pins); no
  rendered-pixel claim is made, since the shape pins pin the XML, not a
  raster.
- `PLACEHOLDERS.md`: one row per file beside that size's `drive-harddisk`
  row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths to
  `SHIPPED_ICONS` beside the other `devices` paths, and name the phone
  in the comment above it.
- `tests/support/icon/shape_pins.py`: pin the three drawings in
  `ICON_SHAPES` from the lists above.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `phone` in the last cell: no reference pixels were
  used; the name is a freedesktop icon-naming-spec device value and the
  dash fallback of the `phone-apple-iphone` device icon — the installed
  `libKF6Solid.so.6.13.0` carries `phone-apple-iphone` and no bare
  `phone` literal (`strings -e l`, verified), and the spec's lookup
  falls back by dropping dash segments, so a device asking for
  `phone-apple-iphone` reaches this file — and the
  screen-speaker-home-button drawing is this theme's own choice.
- `docs/installing.md`: add the phone to the sentence listing the icon
  theme's placeholder illustrations and their sizes.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`, `tests/support/icon/shape_pins.py`,
`docs/invariants.md`, `docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding exactly
  the elements listed for that size, carries a placeholder marker and has
  a `PLACEHOLDERS.md` row; the existing inventory, palette, geometry and
  placeholder-register tests cover all three.
- Changing an element's position, size or fill, or the element order, in
  one file makes `test_each_icon_draws_its_pinned_artwork` fail; dropping
  a file while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The new fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme` puts
  the three files in the installed theme, and uninstalling removes them
  (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into a
  scratch `XDG_DATA_HOME`, use a scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`), `XDG_CACHE_HOME`
  and `XDG_RUNTIME_DIR`, unset `DISPLAY` and `WAYLAND_DISPLAY`, and set
  `QT_QPA_PLATFORM=offscreen`. `phone` resolves to the theme's 32x32
  file, `x-office-document` still resolves to the theme's file, and the
  still-unplanned device names `video-display`, `camera-photo`,
  `network-wireless` and `battery` stay on Breeze (siblings planning
  `input-mouse` or the printer may have shipped those by the time this
  runs; do not assert their state). Report the output in VERIFIED.
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
