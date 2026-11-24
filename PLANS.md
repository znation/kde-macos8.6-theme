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

### Platinum icon theme: draw JSON documents with an original
`application-json` icon (planned 2026-11-24 by the plan role;
independent of the waiting plans)

**Goal.** A `.json` item maps to the shared MIME database's canonical
type `application/json` ("JSON document"), whose database `generic-icon`
is the theme's own shipped `text-x-script` file, but the lookup never
reaches it: Breeze ships the exact name, so under this theme a `.json`
item draws Breeze's JSON art instead of this theme's document series —
ship one original placeholder icon, `application-json`, at 16x16, 22x22
and 32x32, in the same mimetype-item series as the landed
`text-x-script` document and the type-spelled archive icons. Provenance:
the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/json` with `generic-icon name="text-x-script"`, no
`<icon>` element, no `<alias>` elements, the single glob
`<glob pattern="*.json">` and no magic matcher, and holds zero
occurrences of the hyphenated name `application-json`, so one file
covers exactly the canonical name and no alias file is shipped. The
planning-time probe on 2026-11-24 with `kiconfinder6`, the theme
installed into scratch XDG homes (`XDG_DATA_DIRS` naming the scratch
data root, `[Icons] Theme=org.macos8.desktop` in the scratch
`kdeglobals`, `QT_QPA_PLATFORM=offscreen`, no `DISPLAY`):
`application-json` resolved to Breeze's
`:/icons/breeze/mimetypes/32/application-json.svg` while
`text-x-script` resolved to the theme's own 32x32
`mimetypes/text-x-script.svg` — Breeze's exact-name file beats the
generic-icon fallback, so the theme must ship the name to put a
`.json` item in the series. The same probe run resolved the sibling
MIME names `image-svg+xml`, `text-x-chdr` and `text-x-python` to the
theme's own `image-x-generic` and `text-x-generic` files, so those
types already draw theme art and stay unplanned. No reference
screenshot shows a JSON icon, so no reference pixels are used and the
drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/application-json.svg` under `16x16`, `22x22` and
  `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme` already
  declares the three MimeTypes directories. Give each file the XML
  declaration, the comment `<!-- PLACEHOLDER: original JSON illustration pending user-approved artwork. -->`, a short comment saying it is our
  own drawing in the Platinum palette, not traced from anyone's
  artwork, and a root with matching `width`, `height` and `viewBox`.
  The art shares the generic document's page (every drawing element of
  `mimetypes/text-x-script.svg` at that size except the angle brackets
  and the `#999999` code lines) and holds a pair of black curly
  braces — the script icon's angle-bracket chains with one middle nub
  added to each — instead of the angle brackets, with no code lines;
  an original JSON mark distinct from the script icon's open
  `<` `>` pair:
  - 32x32: the page paths `M6 3 h14 l6 6 v20 H6 Z` `#000000`,
    `M7 4 h12 l6 6 v18 H7 Z` `#FFFFFF` and the flap
    `M19 4 L25 4 L25 10 Z` `#DDDDDD`; left brace rects `12,11 2×2`,
    `10,13 2×2`, `8,15 2×2`, nub `10,15 2×2`, `10,17 2×2` and
    `12,19 2×2`; right brace rects `18,11 2×2`, `20,13 2×2`,
    `22,15 2×2`, nub `20,15 2×2`, `20,17 2×2` and `18,19 2×2`; all
    braces `#000000` (rows 11..20, inside the face rows 4..28 and
    clear of the flap rows 4..10).
  - 22x22: the page paths `M4 1 h10 l4 4 v15 H4 Z` `#000000`,
    `M5 2 h8 l4 4 v13 H5 Z` `#FFFFFF` and the flap
    `M13 2 L17 2 L17 6 Z` `#DDDDDD`; left brace rects `9,8 1×1`,
    `8,9 1×1`, `7,10 1×1`, nub `7,11 1×1`, `7,12 1×1`, `8,13 1×1` and
    `9,14 1×1`; right brace rects `12,8 1×1`, `13,9 1×1`,
    `14,10 1×1`, nub `14,11 1×1`, `14,12 1×1`, `13,13 1×1` and
    `12,14 1×1`; all braces `#000000` (rows 8..14, inside the face
    rows 2..15, clear of the flap rows 2..6).
  - 16x16: the page paths `M3 1 h7 l3 3 v10 H3 Z` `#000000`,
    `M4 2 h5 l3 3 v8 H4 Z` `#FFFFFF` and the flap
    `M9 2 L12 2 L12 5 Z` `#DDDDDD`; left brace rects `6,6 1×1`,
    `5,7 1×1`, `4,8 1×1`, nub `5,8 1×1`, `5,9 1×1` and `6,10 1×1`;
    right brace rects `9,6 1×1`, `10,7 1×1`, `11,8 1×1`, nub
    `10,8 1×1`, `10,9 1×1` and `9,10 1×1`; all braces `#000000`
    (rows 6..10, inside the face rows 2..12, clear of the flap rows
    2..5).

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside that size's
  `text-x-script` row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`, and extend the
  mimetypes comment above them to name the JSON document in the
  document series.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above, spreading `*_PAGE_16`, `*_PAGE_22`
  and `*_PAGE_32` from `tests/support/icon/shape_pins/_shared.py`
  for the page elements, then the brace rects.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-json` in the last cell, as the
  `text-x-script` sentence there does.
- `docs/installing.md`: add the JSON document icon to the sentence
  listing the icon theme's placeholder illustrations and their sizes.
- The in-flight cpio and LZMA-compressed-tar entries and the pending
  ISO entry edit the same inventory block, `PINS` registry, invariants
  row and installing.md sentence; this entry sits behind them in the
  queue, so rebase on whatever they have landed when picking it up,
  keeping one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the page elements
  matching the same size's `text-x-script.svg` pinned page tuple, in
  the same order, then the brace rects), carries a placeholder marker
  and has a `PLACEHOLDERS.md` row; the existing inventory, palette,
  geometry and placeholder-register tests cover all three.
- Changing one brace rectangle's position, size or fill, or the
  element order, in one file makes the geometry test fail; dropping a
  file while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The braces' `#000000` fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME`, use a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset
  `DISPLAY` and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-json` resolves to the theme's 32x32
  `mimetypes/application-json.svg` (at planning time, before this
  change, it resolved to Breeze's
  `:/icons/breeze/mimetypes/32/application-json.svg`), and
  `text-x-script` still resolves to the theme's own file (the generic
  fallback keeps its own drawing). Report the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
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

### Platinum icon theme: draw Perl scripts with an original `application-x-perl` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A `.pl`, `.pm`, `.pod` or `.t` item maps to the shared MIME
database's canonical type `application/x-perl`, whose database
`generic-icon` is the theme's own shipped `text-x-script` file, but the
lookup never reaches it: Breeze ships the exact name, so under this
theme a Perl item draws Breeze's art instead of this theme's series —
ship one original placeholder icon, `application-x-perl`, at 16x16,
22x22 and 32x32, in the same mimetype-item series as the landed
`application-octet-stream`, `application-pdf`, `application-zip`,
`application-x-tar`, `application-x-7z-compressed`,
`application-gzip`, `application-x-shellscript` and
`application-vnd.debian.binary-package` files, the in-flight cpio and
ISO-disc-image work and the pending bzip2- and LZMA-compressed-tar and
JSON entries. Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/x-perl` ("Perl script") with `<generic-icon
name="text-x-script"/>`, no `<icon>` element, the alias
`text/x-perl`, the globs `*.pl`, `*.PL`, `*.pm`, `*.al`, `*.perl`,
`*.pod` and `*.t`, and a `<magic>` matcher; the database holds zero
occurrences of the hyphenated name `application-x-perl` (`str.count`
is 0 — `grep -c` counts lines, not matches), so one file covers
exactly the canonical name. The alias `text/x-perl` names its own
Breeze file too, but the MIME database resolves aliases to the
canonical type, so a `.pl` item asks the canonical name and one file
covers it; the magic matcher and the `sub-class-of` links
(`application/x-executable`, `text/plain`) change no icon resolution,
since the probe below shows the canonical name is the one requested.
Breeze ships its own exact-name file at all three sizes, so the
planning-time probe on 2026-11-24 with `kiconfinder6`, the theme
installed into scratch XDG homes (`XDG_DATA_DIRS` naming the scratch
data root, `[Icons] Theme=org.macos8.desktop` in the scratch
`kdeglobals`, `QT_QPA_PLATFORM=offscreen`, no `DISPLAY`):
`application-x-perl` resolved to Breeze's
`:/icons/breeze/mimetypes/32/application-x-perl.svg` while
`text-x-script` resolved to the theme's own 32x32
`mimetypes/text-x-script.svg` — Breeze's exact-name file beats the
generic-icon fallback, so the theme must ship the name to put a Perl
item in the series. No reference screenshot shows a Perl item icon,
so no reference pixels are used and the drawing is this theme's own
choice.

**Approach.**

- Add `mimetypes/application-x-perl.svg` under `16x16`, `22x22` and
  `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme` already
  declares the three MimeTypes directories. Give each file the XML
  declaration, the comment `<!-- PLACEHOLDER: original Perl-script
  illustration pending user-approved artwork. -->`, a short comment
  saying it is our own drawing in the Platinum palette, not traced
  from anyone's artwork, and a root with matching `width`, `height`
  and `viewBox`. The art shares the document page (every drawing
  element of that size's `_PAGE_<N>` tuple in
  `tests/support/icon/shape_pins/_shared.py`, in order) and holds a
  black capital P on the white face — a full-height left stem and a
  closed upper bowl — clear of the folded corner, an original mark
  distinct from the shell-script terminal band, the JSON braces and
  the other series marks:
  - 32x32: the `_PAGE_32` elements, then P rects, all `#000000`:
    stem `10,11 2x13` (rows 11..23), bowl top `12,11 5x1` (row 11,
    columns 12..16), bowl right `16,12 1x5` (rows 12..16) and bowl
    bottom `12,16 5x1` (row 16, columns 12..16).
  - 22x22: the `_PAGE_22` elements, then P rects, all `#000000`:
    stem `7,8 2x9` (rows 8..16), bowl top `9,8 4x1` (row 8, columns
    9..12), bowl right `12,9 1x3` (rows 9..11) and bowl bottom
    `9,11 4x1` (row 11, columns 9..12).
  - 16x16: the `_PAGE_16` elements, then P rects, all `#000000`:
    stem `5,6 1x6` (rows 6..11), bowl top `6,6 3x1` (row 6, columns
    6..8), bowl right `8,7 1x2` (rows 7..8) and bowl bottom `6,8
    3x1` (row 8, columns 6..8).

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside that size's
  `text-x-script` row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`, and extend the
  mimetypes comment above them to name the type-spelled series.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three
  drawings in `PINS` from the lists above (that size's `_*PAGE_*`
  tuple spread first, in order, then the four P rects).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-x-perl` in the last cell, as the
  `application-zip` sentence there does.
- `docs/installing.md`: add the Perl-script icon to the sentence
  listing the icon theme's placeholder illustrations and their sizes.
- The in-flight cpio and ISO entries and the pending
  compressed-tar and JSON entries edit the same inventory block,
  `PINS` registry, invariants row and installing.md sentence; this
  entry sits behind them in the queue, so rebase on whatever they
  have landed when picking it up, keeping one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (that size's `_*PAGE_*`
  tuple in the same order, then the four P rects), carries a
  placeholder marker and has a `PLACEHOLDERS.md` row; the existing
  inventory, palette, geometry and placeholder-register tests cover
  all three.
- Changing one P rectangle's position, size or fill, or the element
  order, in one file makes the geometry test fail; dropping a file
  while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The P's `#000000` fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME`, use a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset
  `DISPLAY` and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-x-perl` resolves to the theme's 32x32
  `mimetypes/application-x-perl.svg` (at planning time, before this
  change, it resolved to Breeze's
  `:/icons/breeze/mimetypes/32/application-x-perl.svg`), and
  `text-x-script` still resolves to the theme's own file (the generic
  fallback keeps its own drawing). Report the output in VERIFIED.
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
