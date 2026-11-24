# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
**Steward note 2026-11-24 by the steward role: drift in the queue, updated.**
The product-work gap this note named is closing: seven mimetype-icon plans
landed and were archived 2026-11-24, and three more wait in this queue
(QEMU `application-x-qemu-disk`, PGP `application-pgp-signature`, ICC
`application-vnd.iccprofile` — the last in flight by feature). The red
`make check` Open entry was closed 2026-11-24 by verification (re-tagged
to `slow-check` earlier; ledger back at its baseline). What still stands:
BUGS.md's `## Open` section holds 24 entries on main (`c2c8db08`), 23 of
them matching a test or self-check title pattern (`test_`, `failed`,
`Seven`, `self-check`) — most quarantined render flakes parked as "Needs
review" or "waiting for a recurrence" — and nothing queued addresses them.
The plan role should still weigh a plan that retires the flake backlog (for
example, the capture diagnostics several Open entries ask for) ahead of
another test-file split. This note is a flag, not a new entry, and does
not change queue order.

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

### Platinum icon theme: draw electronic books with an original `application-epub+zip` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** An electronic book file (`*.epub`) draws Breeze's art beside
the Platinum documents and folders. Ship one original placeholder
icon, `application-epub+zip`, at 16x16, 22x22 and 32x32, in the same
mimetype-item series as the landed `application-json` and
`application-x-mimearchive` files and the waiting
`application-x-openzim` entry. Provenance: the installed shared MIME
database (`/usr/share/mime/packages/freedesktop.org.xml`) declares the
type `application/epub+zip` ("Electronic book document") with no
`<icon>` element, no `<alias>` element, one `<generic-icon
g name="x-office-document"/>` element, one `<sub-class-of
type="application/zip"/>` element, the single glob
`<glob pattern="*.epub">` at the default weight 50 (owned by no other
MIME type) and one `<magic>` matcher (priority 70: the string
`PK\003\004` at offset 0, requiring the string `mimetype` at offset 30
and the string `application/epub+zip` at offset 38 or 43); the string
`application-epub+zip` occurs 0 times in the database (`str.count` is
0 — `grep -c` counts lines, not matches), so one file covers exactly
its own name. The theme ships `x-office-document.svg` at all three
sizes, but `index.theme` declares `Inherits=breeze`, and
`/usr/share/icons/breeze/mimetypes/` ships the exact-name
`application-epub+zip.svg` at 16, 22, 24, 32 and 64 — Breeze's
exact-name file beats the theme's generic-icon fallback, so a `.epub`
item draws Breeze's art unless the theme ships the name. No reference
screenshot shows an e-book item icon, so no reference pixels are used
and the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/application-epub+zip.svg` under `16x16`, `22x22`
  and `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme`
  already declares the three MimeTypes directories. Give each file the
  XML declaration, the comment `<!-- PLACEHOLDER: original electronic
  book illustration pending user-approved artwork. -->`, a short
  comment saying it is our own drawing in the Platinum palette, not
  traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art shares the generic document's page
  (every drawing element of that size's `x-office-document.svg`
  except the heading band, body lines and signature line — the
  `*_PAGE_*` tuples) and holds a black lowercase e — an open reader's
  letter on the blank page, distinct from JSON's curly braces, the
  shell script's `>_` prompt, the bzip2-compressed-tar's lowercase b,
  deb's hollow capital D, tar's T, the ISO disc's capital I, cpio's
  capital C, xz's stair-stepped X, the QCOW disc's white Q and the
  crash core's square ring with centre dot (no existing mark is a
  lowercase e, and the e's two notches and three bars separate it
  from all of them at every size):
  - 32x32: the `*_PAGE_32` page paths, then all `#000000`: top bar
    `10,12 8×2` (rows 12..13), upper-right notch `16,14 2×1` (row
    14), middle bar `10,15 8×2` (rows 15..16), lower-left notch
    `10,17 2×1` (row 17) and bottom bar `10,18 8×2` (rows 18..19);
    every cell sits on the white page inside the black outline and
    clear of the folded corner.
  - 22x22: the `*_PAGE_22` page paths, then all `#000000`: top bar
    `7,9 6×1` (row 9), upper-right notch `11,10 2×1` (row 10),
    middle bar `7,11 6×1` (row 11), lower-left notch `7,12 2×1`
    (row 12) and bottom bar `7,13 6×1` (row 13).
  - 16x16: the `*_PAGE_16` page paths, then all `#000000`: top bar
    `5,7 5×1` (row 7), upper-right notch `8,8 2×1` (row 8), middle
    bar `5,9 5×1` (row 9), lower-left notch `5,10 2×1` (row 10) and
    bottom bar `5,11 5×1` (row 11).

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the mimetype rows,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three
  drawings in `PINS` from the lists above (the `*_PAGE_*` page tuple,
  then the five e bars and notches).
- `docs/invariants.md`: a new `## icons` row after the
  `application-x-openzim` row, its guarantee pinning
  `tests/test_icon_theme_geometry.py::TestIconGeometry` and its last
  cell recording the provenance of `application-epub+zip` as the
  `application-pgp-keys` row does.
- `docs/installing.md`: add the e-book icon to the sentence listing
  the icon theme's placeholder illustrations and their sizes.
- The waiting openzim entry (and the gettext-translation and
  pkix-crl entries while they still wait) edits the same inventory
  block, `PINS` registry, invariants table and installing.md
  sentence; this entry sits behind them in the queue, so rebase on
  whatever they have landed when picking this up, keeping one row
  per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the page elements
  matching the `x-office-document.svg` pin's page tuple, in the same
  order, then the five e bars and notches), carries a placeholder
  marker and has a `PLACEHOLDERS.md` row; the existing inventory,
  palette, geometry and placeholder-register tests cover all three.
- Changing one bar's or notch's position, size or fill, or the
  element order, in one file makes the geometry test fail; dropping a
  file while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The `#000000`, `#FFFFFF` and `#DDDDDD` fills stay inside
  `PLATINUM_FILLS`, so `test_each_icon_uses_only_the_platinum_palette`
  passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present and can be steered to
  the installed scratch theme (the scratch-homes recipe the landed
  `application-pkix-cert` entry records): install the theme into a
  scratch data root, use scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`),
  `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset `DISPLAY` and
  `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`;
  `application-epub+zip` resolves to the theme's 32x32
  `mimetypes/application-epub+zip.svg`, while the same probe against
  a data root without the theme prints nothing and exits 1. Report
  the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

### Platinum icon theme: draw PKCS#12 certificate bundles with an original `application-pkcs12` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A PKCS#12 certificate-bundle file (`*.p12` or `*.pfx`, as
the file manager identifies it) draws Breeze's art beside the
Platinum documents and folders. Ship one original placeholder icon,
`application-pkcs12`, at 16x16, 22x22 and 32x32, in the same
mimetype-item series as the landed `application-pkix-cert` and
`application-pgp-keys` security marks — both must stay visually
distinct from the new drawing. Provenance: the installed shared MIME
database (`/usr/share/mime/packages/freedesktop.org.xml`) declares
the type `application/pkcs12` ("PKCS#12 certificate bundle") with no
`<icon>` element, no `<generic-icon>` element, one `<alias>` element
(`application/x-pkcs12`), the globs `*.p12` and `*.pfx` each at the
default weight 50 and each owned by no other MIME type, no `<magic>`
element and no `<sub-class-of>` element, and the database holds zero
occurrences of the hyphenated name `application-pkcs12` (`str.count`
is 0), so one file covers exactly the canonical name and no alias
file is shipped. With no icon element the type asks its literal
name; the theme's `index.theme` declares `Inherits=breeze` and the
theme ships no `application-pkcs12.svg`, while Breeze ships the
exact-name file at 16, 22, 24, 32 and 64 (`find` over
`/usr/share/icons` lists it under both `breeze` and `breeze-dark`),
so the lookup falls through to Breeze's file. Planning-time probe
(2026-11-24, scratch `XDG_DATA_HOME`/`HOME`/`XDG_CONFIG_HOME`/
`XDG_CACHE_HOME`/`XDG_RUNTIME_DIR`, `QT_QPA_PLATFORM=offscreen`,
`DISPLAY` and `WAYLAND_DISPLAY` unset): `kiconfinder6
application-pkcs12` resolves to
`:/icons/breeze/mimetypes/32/application-pkcs12.svg` while
`text-x-generic` resolves to the theme's own 32x32 file — today a
`.p12` file shows Breeze's PKCS#12 art, not this theme's own. No
reference screenshot shows a certificate-bundle item icon, so no
reference pixels are used and the drawing is this theme's own
choice.

**Approach.**

- Add `mimetypes/application-pkcs12.svg` under `16x16`, `22x22` and
  `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme`
  already declares the three MimeTypes directories. Give each file
  the XML declaration, the comment `<!-- PLACEHOLDER: original
  PKCS#12 certificate-bundle illustration pending user-approved
  artwork. -->`, a short comment saying it is our own drawing in the
  Platinum palette, not traced from anyone's artwork, and a root
  with matching `width`, `height` and `viewBox`. The art shares the
  generic document's page (the page outline, white page and
  folded-corner flap matching the `application-json.svg` pin's first
  three elements) and holds a padlock — a shackle over a locked
  body, the guarded-bundle mark distinct from the certificate's
  seal-and-ribbons, the PGP key's silhouette, the VPN network card's
  card-backed padlock (that one rides a network card, not the
  document page), the Snap crate, the Squashfs disc-stack's white
  tapering bands, the Android package's zipper band, the ISO disc's
  capital-I and hub rings, the QCOW disc's white Q, the JSON
  document's curly braces, the shell script's `>_` prompt, the NZB
  index's dot-and-bars groups and the crash core's square ring:
  - 32x32: the three shared page elements; then the padlock —
    `rect x="13" y="11" width="6" height="1" fill="#000000"`
    (shackle top bar), `rect x="13" y="11" width="1" height="4"
    fill="#000000"` (shackle left leg), `rect x="18" y="11"
    width="1" height="4" fill="#000000"` (shackle right leg),
    `rect x="12" y="15" width="8" height="7" fill="#000000"`
    (body frame), `rect x="13" y="16" width="6" height="5"
    fill="#DDDDDD"` (body face) and `rect x="15" y="17" width="2"
    height="3" fill="#000000"` (keyhole), drawn in that order so the
    shackle reads above the body and the keyhole on top of the face.
    Every element sits inside the white page and clears the folded
    corner.
  - 22x22: the three shared page elements; then the padlock —
    `rect x="9" y="7" width="4" height="1" fill="#000000"` (shackle
    top bar), `rect x="9" y="7" width="1" height="4"
    fill="#000000"` (shackle left leg), `rect x="12" y="7"
    width="1" height="4" fill="#000000"` (shackle right leg),
    `rect x="8" y="11" width="6" height="5" fill="#000000"` (body
    frame), `rect x="9" y="12" width="4" height="3"
    fill="#DDDDDD"` (body face) and `rect x="10" y="12" width="2"
    height="2" fill="#000000"` (keyhole), drawn in that order. Every
    element sits inside the white page and clears the folded corner.
  - 16x16: the three shared page elements; then the padlock —
    `rect x="6" y="6" width="4" height="1" fill="#000000"` (shackle
    top bar), `rect x="6" y="6" width="1" height="3"
    fill="#000000"` (shackle left leg), `rect x="9" y="6"
    width="1" height="3" fill="#000000"` (shackle right leg),
    `rect x="5" y="9" width="6" height="4" fill="#000000"` (body
    frame), `rect x="6" y="10" width="4" height="2"
    fill="#DDDDDD"` (body face) and `rect x="7" y="10" width="2"
    height="1" fill="#000000"` (keyhole), drawn in that order. Every
    element sits inside the white page and clears the folded corner
    (the flap reaches `y="5"` at `x="9"`).

  Validate by XML only, never by rasterizing: `convert`'s MSVG
  reader bleeds 1px shapes, so the pins below are the drawing
  contract.
- `PLACEHOLDERS.md`: one row per file beside the other mimetype
  placeholder rows, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths
  beside the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three
  drawings in `PINS` from the lists above (the three shared page
  elements in document order, then the shackle top bar, shackle
  legs, body frame, body face and keyhole).
- `docs/invariants.md`: a new `## icons` row after the
  `application-x-openzim` row, its guarantee pinning
  `tests/test_icon_theme_geometry.py::TestIconGeometry` and its last
  cell recording the provenance of `application-pkcs12` as the
  `application-vnd.squashfs` row does.
- `docs/installing.md`: add the PKCS#12 certificate-bundle icon to
  the sentence listing the icon theme's placeholder illustrations
  and their sizes (the one naming the `application-vnd.squashfs`
  files).
- The queued mimetype-icon entries ahead of this one (the gettext
  catalog, the offline wiki archive, the Snap package and the
  e-book) edit the same inventory block, `PINS` registry, invariants
  table and installing.md sentence; this entry sits behind them in the
  queue, so rebase on whatever they have landed when picking this
  up, keeping one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the three shared page
  elements matching the `application-json.svg` pin's first three
  elements, then the shackle top bar, shackle legs, body frame, body
  face and keyhole), carries a placeholder marker and has a
  `PLACEHOLDERS.md` row; the existing inventory, palette, geometry
  and placeholder-register tests cover all three.
- Changing one padlock element's position, size or fill, or the
  element order, in one file makes the geometry test fail; dropping
  a file while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The `#000000`, `#FFFFFF` and `#DDDDDD` fills stay inside
  `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- The padlock mark shares no drawing element with the pinned
  `application-pkix-cert` seal-and-ribbons or
  `application-pgp-keys` key silhouette (no seal ring, no ribbons,
  no key bow-and-teeth), so the sibling security marks stay visually
  distinct.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME`, use a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset
  `DISPLAY` and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-pkcs12` resolves to the theme's 32x32
  `mimetypes/application-pkcs12.svg` (at planning time the name fell
  through to Breeze's file), and `text-x-generic` still resolves to
  the theme's own file. Report the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

### Platinum icon theme: draw Ogg multimedia containers with an original `application-ogg` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** An Ogg multimedia container file (`*.ogx`) draws Breeze's
art beside the Platinum documents and folders. Ship one original
placeholder icon, `application-ogg`, at 16x16, 22x22 and 32x32, in
the same mimetype-item series as the landed `application-json`,
`application-pgp-signature` and `application-vnd.iccprofile` files.
Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/ogg` ("Ogg multimedia file") with no `<icon>` element,
no `<sub-class-of>` element, one `<generic-icon
name="video-x-generic"/>` element, one `<alias
type="application/x-ogg"/>` element, the single glob
`<glob pattern="*.ogx">` at the default weight 50 (owned by no other
MIME type) and one `<magic>` matcher at the default priority (the
string `OggS` at offset 0); the string `application-ogg` occurs 0
times in the database (`str.count` is 0 — `grep -c` counts lines,
not matches), so one file covers exactly its own name and no alias
file is shipped for `application/x-ogg`. The theme now ships
`video-x-generic.svg` at all three sizes (the landed video plan), but
`index.theme` declares `Inherits=breeze`, and
`/usr/share/icons/breeze/mimetypes/` ships the exact-name
`application-ogg.svg` at 16, 22, 24, 32 and 64 (breeze-dark likewise)
— Breeze's exact-name file beats the theme's generic-icon fallback,
so a `.ogx` item draws Breeze's art unless the theme ships the name.
The separate `audio/ogg` type (`*.oga`, `*.ogg`, `*.opus`) and its
Breeze exact-name `audio-ogg.svg` are a different candidate and stay
out of this entry. No reference screenshot shows a multimedia-
container item icon, so no reference pixels are used and the drawing
is this theme's own choice.

**Approach.**

- Add `mimetypes/application-ogg.svg` under `16x16`, `22x22` and
  `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme`
  already declares the three MimeTypes directories. Give each file
  the XML declaration, the comment `<!-- PLACEHOLDER: original Ogg
  multimedia-container illustration pending user-approved artwork.
  -->`, a short comment saying it is our own drawing in the Platinum
  palette, not traced from anyone's artwork, and a root with matching
  `width`, `height` and `viewBox`. The art shares the generic
  document's page (every drawing element of that size's
  `x-office-document.svg` except the heading band, body lines and
  signature line — the `*_PAGE_*` tuples) and holds a black
  film-strip band — two rows of white sprocket holes around a white
  frame window, the container that holds a multimedia stream,
  distinct from JSON's curly braces, the shell script's `>_` prompt,
  the bzip2-compressed-tar's lowercase b, deb's hollow capital D,
  tar's T, the ISO disc's capital I, cpio's capital C, xz's
  stair-stepped X, the QCOW disc's white Q, the crash core's square
  ring with centre dot and the video screen's play triangle (no
  shipped mimetype page mark is a film-strip band; the two sprocket
  rows and the frame window separate it from every one of them at
  every size). Every cell was verified by script to sit on the white
  page and clear of the folded corner:
  - 32x32: the `*_PAGE_32` page paths, then a `#000000` band
    `9,14 14×8` (rows 14..21), four `#FFFFFF` sprocket cells `2×1`
    at `10,15`, `13,15`, `16,15` and `19,15`, the `#FFFFFF` frame
    window `11,17 10×2` (rows 17..18) and four `#FFFFFF` sprocket
    cells `2×1` at `10,20`, `13,20`, `16,20` and `19,20`.
  - 22x22: the `*_PAGE_22` page paths, then a `#000000` band
    `6,10 10×8` (rows 10..17), three `#FFFFFF` sprocket cells `2×1`
    at `7,11`, `10,11` and `13,11`, the `#FFFFFF` frame window
    `8,13 6×2` (rows 13..14) and three `#FFFFFF` sprocket cells
    `2×1` at `7,16`, `10,16` and `13,16`.
  - 16x16: the `*_PAGE_16` page paths, then a `#000000` band
    `5,6 6×6` (rows 6..11), two `#FFFFFF` sprocket cells `1×1` at
    `6,7` and `8,7`, the `#FFFFFF` frame window `6,8 4×2` (rows
    8..9) and two `#FFFFFF` sprocket cells `1×1` at `6,10` and
    `8,10`.

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the mimetype rows,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`, and update the
  `video-x-generic` pin's comment there so it no longer counts
  `application/ogg` among the types the generic fallback covers (it
  now resolves to its own exact-name file).
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three
  drawings in `PINS` from the lists above (the `*_PAGE_*` page tuple,
  then the band, the sprocket cells, the window and the lower
  sprocket cells).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-ogg` in the last cell, as the
  `application-pgp-keys` sentence there does.
- `docs/installing.md`: add the Ogg-container icon to the sentence
  listing the icon theme's placeholder illustrations and their sizes.
- The `application/ogg` work shares the inventory block, `PINS`
  registry, invariants row and installing.md sentence with the
  waiting mimetype entries; this entry sits behind them in the
  queue, so rebase on whatever they have landed when picking this
  up, keeping one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the page elements
  matching the `x-office-document.svg` pin's page tuple, in the same
  order, then the band, the sprocket cells, the window and the lower
  sprocket cells), carries a placeholder marker and has a
  `PLACEHOLDERS.md` row; the existing inventory, palette, geometry
  and placeholder-register tests cover all three.
- Changing one band, sprocket or window cell's position, size or
  fill, or the element order, in one file makes the geometry test
  fail; dropping a file while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The `#000000`, `#FFFFFF` and `#DDDDDD` fills stay inside
  `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present and can be steered to
  the installed scratch theme (the scratch-homes recipe the landed
  `application-pkix-cert` entry records): install the theme into a
  scratch data root, use scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`),
  `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset `DISPLAY` and
  `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`;
  `application-ogg` resolves to the theme's 32x32
  `mimetypes/application-ogg.svg` (at planning time the theme ships
  no such file, so the name fell through to Breeze's),
  `text-x-generic` still resolves to the theme's own file, and the
  same probe against a data root without the theme resolves
  `application-ogg` to Breeze's `:/icons/breeze/mimetypes/32/`
  file. Report the output in VERIFIED.
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
