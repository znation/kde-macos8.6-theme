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


### Platinum icon theme: draw PKIX certificate revocation lists with an original `application-pkix-crl` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A certificate revocation list (`*.crl`, as the file manager
identifies it) currently draws nothing: no theme on the machine ships
art for it. Ship one original placeholder icon, `application-pkix-crl`,
at 16x16, 22x22 and 32x32, in the same mimetype-item series as the
landed `application-pkix-cert` certificate and `application-pgp-keys`
key. Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/pkix-crl` ("Certificate revocation list") with no `<icon>`
element, no `<generic-icon>` element, no `<alias>` element and no
`<sub-class-of>` element, the single glob `<glob pattern="*.crl">` at
the default weight 50 and owned by no other MIME type, and one
`<magic>` at priority 50 holding the offset-0 string matcher
`-----BEGIN X509 CRL-----`; the string `application-pkix-crl` occurs 0
times in the database (`str.count` is 0 — `grep -c` counts lines, not
matches). With no icon element the type asks its literal name; the
theme's `index.theme` declares `Inherits=breeze`, so the lookup falls
through to Breeze — which ships no such file: `find` over
`/usr/share/icons` for `application-pkix-crl*` returns no match, and a
per-size existence loop over `/usr/share/icons/breeze/mimetypes/` finds
none at 16, 22, 24, 32, 48 or 64. Planning-time probe on 2026-11-24
with `kiconfinder6`, the theme installed into scratch XDG homes
(`make install XDG_DATA_HOME=<scratch>/data DESTDIR=<scratch>/root
INSTALL_PACKAGES=icon-theme`, `XDG_DATA_HOME=<scratch>/root<data`
naming `/usr/share` beside it in `XDG_DATA_DIRS`,
`[Icons] Theme=org.macos8.desktop` in the scratch `kdeglobals`,
`QT_QPA_PLATFORM=offscreen`, no `DISPLAY`): `application-pkix-crl`
printed nothing and exited 1 — the type resolves to no icon at all —
while `text-x-generic` resolved to the theme's own 32x32 file. The gap
is real: today a `.crl` file shows no item icon. No reference
screenshot shows a CRL item icon, so no reference pixels are used and
the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/application-pkix-crl.svg` under `16x16`, `22x22` and
  `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme`
  already declares the three MimeTypes directories. Give each file the
  XML declaration, the comment `<!-- PLACEHOLDER: original certificate
  revocation list illustration pending user-approved artwork. -->`, a
  short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art shares the generic document's page
  (the page outline, white page and folded-corner flap matching the
  `application-json.svg` pin's first three elements) and holds a
  revocation list — grey entry rows struck through by a stepped black
  diagonal — an original mark distinct from the certificate's black
  band with white award seal and ribbon tails, the PGP key's silhouette,
  the JSON document's curly braces, the shell script's `>_` prompt, the
  NZB index's dot-and-bars groups and the crash core's square ring:
  - 32x32: the three shared page elements; then three grey bars
    (`#999999`) `rect x="10" width="12" height="2"` at `y="11"`,
    `y="15"` and `y="19"`; then the strike-out, five black 2x2 cells
    stepping two pixels right and two pixels down: `rect x="10" y="12"`,
    `x="12" y="14"`, `x="14" y="16"`, `x="16" y="18"` and `x="18"
    y="20"`, each `width="2" height="2" fill="#000000"`, drawn after the
    bars so the diagonal reads on top. Every element sits inside the
    white page and clears the folded corner.
  - 22x22: the three shared page elements; then three grey bars
    (`#999999`) `rect x="7" width="8" height="1"` at `y="9"`, `y="12"`
    and `y="15"`; then the strike-out, six black 1x1 cells stepping one
    pixel right and one pixel down: `rect x="7" y="10"`, `x="8" y="11"`,
    `x="9" y="12"`, `x="10" y="13"`, `x="11" y="14"` and `x="12"
    y="15"`, each `width="1" height="1" fill="#000000"`, drawn after the
    bars. Every element sits inside the white page and clears the
    folded corner.
  - 16x16: the three shared page elements; then three grey bars
    (`#999999`) `rect x="5" width="6" height="1"` at `y="6"`, `y="8"`
    and `y="10"`; then the strike-out, four black 1x1 cells stepping one
    pixel right and one pixel down: `rect x="5" y="7"`, `x="6" y="8"`,
    `x="7" y="9"` and `x="8" y="10"`, each `width="1" height="1"
    fill="#000000"`, drawn after the bars. Every element sits inside the
    white page and clears the folded corner (the flap reaches `y="5"`
    at `x="9"`).

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the certificate row,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above (the three shared page elements in
  document order, then the bars in row order, then the strike-out cells
  in stepping order).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-pkix-crl` in the last cell, as the
  `application-pkix-cert` sentence there does.
- `docs/installing.md`: add the certificate revocation list icon to the
  sentence listing the icon theme's placeholder illustrations and their
  sizes.
- The in-flight mimetype-icon entries ahead of this one edit the same
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
  exactly the elements listed for that size (the three shared page
  elements matching the `application-json.svg` pin's first three
  elements, then the bars and the strike-out), carries a placeholder
  marker and has a `PLACEHOLDERS.md` row; the existing inventory,
  palette, geometry and placeholder-register tests cover all three.
- Changing one bar's or cell's position, size or fill, or the element
  order, in one file makes the geometry test fail; dropping a file
  while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The `#000000`, `#FFFFFF`, `#DDDDDD` and `#999999` fills stay inside
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
  `application-pkix-crl` resolves to the theme's 32x32
  `mimetypes/application-pkix-crl.svg` (at planning time, before this
  change, it resolved to nothing — no output, exit 1), and
  `text-x-generic` still resolves to the theme's own file. Report the
  output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.


---

### Platinum icon theme: draw ICC color profiles with an original `application-vnd.iccprofile` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** An ICC color profile (`*.icc` or `*.icm`, as the file
manager identifies it) draws Breeze's art beside the Platinum documents
and folders. Ship one original placeholder icon,
`application-vnd.iccprofile`, at 16x16, 22x22 and 32x32, in the same
mimetype-item series as the landed `application-vnd.efi.iso` optical
disc, the in-flight squashfs, WIM and MHTML entries, the QCOW entry
waiting above, and the detached-signature entry waiting to merge.
Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/vnd.iccprofile` (English comment "ICC profile", with the
acronym ICC expanded by an `<expanded-acronym>` to "International
Color Consortium") with no `<icon>` element, no `<generic-icon>`
element, no `<alias>` element and no `<sub-class-of>`, the two globs
`*.icc` and `*.icm` (each at the default weight 50, and each unique in
the database — no other type shares either glob), and one `<magic>`
matcher at priority 50 (the string `acsp` at offset 36 — the color
signature every ICC profile carries in its header); no other MIME type
in the database declares a `.icc` or `.icm` glob, the string
`application/vnd.iccprofile` occurs exactly once in the database (its
own declaration — `str.count` is 1), and the dashed icon-name form
`application-vnd.iccprofile` occurs 0 times. With no icon element the
type asks its literal dashed name; the theme's `index.theme` declares
`Inherits=breeze`, so the lookup falls through to Breeze's exact-name
file. Planning-time probe on 2026-11-24 with `kiconfinder6` (queried
with the dashed icon name, not the MIME type — the MIME-type form
prints nothing and exits 1), the theme installed into scratch XDG
homes (`XDG_DATA_DIRS` naming the scratch data root beside
`/usr/share`, `XDG_DATA_HOME` pointing into the scratch home so the
real `~/.local/share` cannot shadow it, `[Icons] Theme=
org.macos8.desktop` in the scratch `kdeglobals` written with
`kwriteconfig6` under a scratch `HOME`, `QT_QPA_PLATFORM=offscreen`,
no `DISPLAY` and no `WAYLAND_DISPLAY`): `application-vnd.iccprofile`
resolved to `:/icons/breeze/mimetypes/32/
application-vnd.iccprofile.svg` while `text-x-generic` resolved to
the theme's own 32x32 file — the gap is real, not the screened-out
shape where the theme's own generic art wins. Breeze ships the name
at 16, 22, 24, 32 and 64 — checked per size, no 48. No reference
screenshot shows an ICC-profile icon, so no reference pixels are used
and the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/application-vnd.iccprofile.svg` under `16x16`,
  `22x22` and `32x32` of `theme/icons/org.macos8.desktop/`.
  `index.theme` already declares the three MimeTypes directories. Give
  each file the XML declaration, the comment `<!-- PLACEHOLDER:
  original ICC color-profile illustration pending user-approved
  artwork. -->`, a short comment saying it is our own drawing in the
  Platinum palette, not traced from anyone's artwork, and a root with
  matching `width`, `height` and `viewBox`. The art shares the
  page family (the black outline, white face and folded corner that
  `tests/support/icon/shape_pins/_shared.py` pins as `_PAGE_16`,
  `_PAGE_22` and `_PAGE_32`, spread by the shell-script, crash-core,
  Android-package and office-document pins) and holds a black-framed
  2x2 swatch grid — the color swatches a profile describes, drawn in
  the palette's four tones (the black frame is the fourth): an
  original mark distinct from the office-spreadsheet's ruled table
  (whose cells are separated by thin `#999999` rule lines under a
  `#DDDDDD` header band, not solid swatch cells in a black frame),
  from the shell script's `>_` prompt, JSON's curly braces,
  BitTorrent's download arrow, the PGP key, the ISO disc's capital I,
  the QCOW Q and the rest of the series:
  - 32x32: after `*_PAGE_32`, the frame `rect x="9" y="11"
    width="15" height="15"` `#000000` (x 9..23, y 11..25), then the
    four 5x5 swatch cells, all inside the frame with 2px top, left,
    right and bottom margins and a 1px black gap between the columns
    and rows: `rect x="11" y="13" width="5" height="5"` `#FFFFFF`,
    `rect x="17" y="13" width="5" height="5"` `#DDDDDD`, `rect
    x="11" y="19" width="5" height="5"` `#999999`, and `rect x="17"
    y="19" width="5" height="5"` `#DDDDDD`.
  - 22x22: after `*_PAGE_22`, the frame `rect x="6" y="7" width="11"
    height="11"` `#000000` (x 6..16, y 7..17), then the four 3x3
    swatch cells: `rect x="8" y="9" width="3" height="3"`
    `#FFFFFF`, `rect x="12" y="9" width="3" height="3"` `#DDDDDD`,
    `rect x="8" y="13" width="3" height="3"` `#999999`, and `rect
    x="12" y="13" width="3" height="3"` `#DDDDDD`.
  - 16x16: after `*_PAGE_16`, the frame `rect x="5" y="6" width="7"
    height="7"` `#000000` (x 5..11, y 6..12, set low enough to clear
    the folded corner, which reaches y 5 at x 9..12), then the four
    2x2 swatch cells: `rect x="6" y="7" width="2" height="2"`
    `#FFFFFF`, `rect x="9" y="7" width="2" height="2"` `#DDDDDD`,
    `rect x="6" y="10" width="2" height="2"` `#999999`, and `rect
    x="9" y="10" width="2" height="2"` `#DDDDDD`.

  Every swatch cell's bounds stay inside the white page face of its
  size (32: x 7..25, y 4..28; 22: x 5..17, y 2..19; 16: x 4..12,
  y 2..13) and clear of the folded corner triangle. Validate by XML
  only, never by rasterizing: `convert`'s MSVG reader bleeds 1px
  shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the ISO disc row,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths
  beside the other `mimetypes` paths in `SHIPPED_ICONS`, and extend
  the mimetypes comment above them to name the ICC color profile in
  the type-spelled series.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three
  drawings in `PINS` from the lists above (each spreading its
  `_PAGE_*` prefix, then the frame rect and the four swatch cells in
  document order).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-vnd.iccprofile` in the last cell, as the
  `application-pgp-keys` sentence there does.
- `docs/installing.md`: add the ICC color-profile icon to the
  sentence listing the icon theme's placeholder illustrations and
  their sizes.
- The in-flight squashfs, WIM and MHTML entries, the QCOW entry
  waiting above and the detached-signature entry waiting to merge
  edit the same inventory block, `PINS` registry, invariants row and
  installing.md sentence; this entry sits behind them in the queue,
  so rebase on whatever they have landed when picking this up,
  keeping one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the three page paths
  first, then the frame rect and the four swatch cells, in document
  order), carries a placeholder marker and has a `PLACEHOLDERS.md`
  row; the existing inventory, palette, geometry and
  placeholder-register tests cover all three.
- Changing the frame rect's position, size or fill, any swatch
  cell's position, size or fill, or the element order, in one file
  makes the geometry test fail; dropping a file while leaving it
  shipped makes `test_the_geometry_registry_covers_every_shipped_icon`
  fail.
- The `#000000`, `#FFFFFF`, `#DDDDDD` and `#999999` fills stay
  inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME`, use a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`, written with `kwriteconfig6`), `XDG_CACHE_HOME` and
  `XDG_RUNTIME_DIR`, name the scratch data root in `XDG_DATA_DIRS`
  beside `/usr/share`, and unset `DISPLAY` and `WAYLAND_DISPLAY`,
  with `QT_QPA_PLATFORM=offscreen`. Query `kiconfinder6` with the
  dashed icon name `application-vnd.iccprofile` (the MIME-type form
  prints nothing and exits 1). It resolves to the theme's 32x32
  `mimetypes/application-vnd.iccprofile.svg` (at planning time,
  before this change, it resolved to Breeze's `:/icons/breeze/
  mimetypes/32/application-vnd.iccprofile.svg`), and
  `text-x-generic` still resolves to the theme's own file. Report
  the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.


## Done

### Platinum icon theme: draw detached OpenPGP signatures with an original `application-pgp-signature` icon (planned 2026-11-24 by the plan role; independent of the waiting plans) — done 2026-11-24 by the feature role

**Goal.** A detached OpenPGP signature file (`*.sig`, `*.gpg`,
`*.pgp` or `*.asc`, as the file manager identifies it) draws Breeze's
art beside the Platinum documents and folders. Ship one original
placeholder icon, `application-pgp-signature`, at 16x16, 22x22 and
32x32, in the same mimetype-item series as the landed
`application-pgp-keys` key and the in-flight
`application-x-mimearchive` MHTML and queued
`application-x-qemu-disk` entries.
Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/pgp-signature` ("Detached OpenPGP signature") with no
`<icon>` element, no `<generic-icon>` element, no `<alias>` element,
no `<sub-class-of>` element and one `<magic>` matcher (the string
`-----BEGIN PGP SIGNATURE-----` at offset 0); its globs are `*.sig`
at the default weight 50, owned by no other MIME type, plus `*.pgp`
and `*.gpg`, each at weight 50 and each shared with
`application/pgp-encrypted` and `application/pgp-keys`, and `*.asc`
at weight 10 shared with `application/pgp-encrypted`,
`application/pgp-keys` and `text/plain`; the string
`application-pgp-signature` occurs 0 times in the database
(`str.count` is 0 — `grep -c` counts lines, not matches). With no
generic-icon element and no parent type the lookup asks the literal
type-spelled name; the theme's `index.theme` declares
`Inherits=breeze`, so the lookup falls through to Breeze's exact-name
file (Breeze ships `application-pgp-signature.svg` at 16, 22, 24, 32
and 64, each verified with a `[ -f ]` check). Planning-time probe on
2026-11-24 with `kiconfinder6`, the theme installed into scratch XDG
homes (`XDG_DATA_HOME` naming the installed scratch data root,
`XDG_DATA_DIRS=/usr/share`, `[Icons] Theme=org.macos8.desktop` in the
scratch `kdeglobals`, `QT_QPA_PLATFORM=offscreen`, no `DISPLAY`):
`application-pgp-signature` resolved to
`:/icons/breeze/mimetypes/32/application-pgp-signature.svg` while
`text-x-generic` resolved to the theme's own 32x32 file — the gap is
real, not the screened-out shape where the theme's own generic art
wins. No reference screenshot shows a detached-signature item icon,
so no reference pixels are used and the drawing is this theme's own
choice.

**Approach.**

- Add `mimetypes/application-pgp-signature.svg` under `16x16`,
  `22x22` and `32x32` of `theme/icons/org.macos8.desktop/`.
  `index.theme` already declares the three MimeTypes directories.
  Give each file the XML declaration, the comment `<!--
  PLACEHOLDER: original detached OpenPGP-signature illustration
  pending user-approved artwork. -->`, a short comment saying it is
  our own drawing in the Platinum palette, not traced from anyone's
  artwork, and a root with matching `width`, `height` and `viewBox`.
  The art shares the shell-script document's page (every drawing
  element of that size's `application-x-shellscript.svg`: the page
  outline, white page and folded-corner flap) and holds a black
  signature stroke — a stepped ink flourish stepping down and up
  across the page's foot with a straight underline beneath it, a pen
  signing off the detached signature — an original mark distinct from
  the key's wards-and-blade, the web-document window's globe, the
  shell script's `>_` prompt, JSON's curly braces, BitTorrent's
  download arrow and tray, the backup file's tilde, the crash core's
  square ring and center dot, the database canister, the ISO disc's
  capital I, the Squashfs tapering bands, the WIM split-volume gap,
  the NZB dot-and-bars groups, the paperclip of the waiting MHTML
  entry, the certificate's seal-and-ribbons, the Android zipper teeth
  and the deb box's letter D:
  - 32x32: the three shared page elements; then, all `#000000`, the
    stroke `9,18 3×1` (cols 9..11, row 18), `12,17 3×1` (cols 12..14,
    row 17), `15,18 3×1` (cols 15..17, row 18), `18,17 3×1` (cols
    18..20, row 17), `21,18 2×1` (cols 21..22, row 18) and the
    underline `9,20 14×1` (cols 9..22, row 20); every cell sits
    inside the white page and clear of the flap.
  - 22x22: the three shared page elements; then, all `#000000`, the
    stroke `7,13 2×1` (cols 7..8, row 13), `9,12 2×1` (cols 9..10,
    row 12), `11,13 2×1` (cols 11..12, row 13), `13,12 2×1` (cols
    13..14, row 12), `15,13 2×1` (cols 15..16, row 13) and the
    underline `7,15 10×1` (cols 7..16, row 15); every cell sits
    inside the white page and clear of the flap.
  - 16x16: the three shared page elements; then, all `#000000`, the
    stroke `5,10 2×1` (cols 5..6, row 10), `7,9 2×1` (cols 7..8,
    row 9), `9,10 2×1` (cols 9..10, row 10) and the underline `5,12
    7×1` (cols 5..11, row 12); every cell sits inside the white page
    and clear of the flap.

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the PGP-key rows,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above (the `*_PAGE_*` page tuple, then the
  stroke segments left to right, then the underline).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-pgp-signature` in the last cell, as the
  `application-pgp-keys` sentence there does.
- `docs/installing.md`: add the detached OpenPGP-signature icon to
  the sentence listing the icon theme's placeholder illustrations and
  their sizes.
- The in-flight MHTML and queued QEMU QCOW entries edit the same
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
  exactly the elements listed for that size (the page elements matching
  the `application-x-shellscript.svg` pin's page tuple, in the same
  order, then the stroke segments left to right and the underline),
  carries a placeholder marker and has a `PLACEHOLDERS.md` row; the
  existing inventory, palette, geometry and placeholder-register tests
  cover all three.
- Changing one signature-stroke rect's position, size or fill, or the
  element order, in one file makes the geometry test fail; dropping a
  file while leaving it shipped makes
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
  `application-pgp-signature` resolves to the theme's 32x32
  `mimetypes/application-pgp-signature.svg` (at planning time, before
  this change, it resolved to Breeze's
  `:/icons/breeze/mimetypes/32/application-pgp-signature.svg`), and
  `text-x-generic` still resolves to the theme's own file. Report the
  output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

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
