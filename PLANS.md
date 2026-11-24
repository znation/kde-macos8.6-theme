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

### Platinum icon theme: draw AppImage bundles with an original `application-vnd.appimage` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** An AppImage application bundle (`*.appimage`, as the file
manager identifies it) draws this theme's own mark beside the Platinum
documents and folders. Ship one original placeholder icon,
`application-vnd.appimage`, at 16x16, 22x22 and 32x32, in the same
mimetype-item series as the `application-x-generic` blank page. It is
the type-2-bundle mark of the installed shared MIME database — the
database's older `application/x-iso9660-appimage` type shares the
`*.appimage` glob (at the default weight 50) but loses name-based
matching to this type's weight-60 glob and is declared here out of
scope, keeping Breeze's exact-name file for it. Provenance: the
installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/vnd.appimage` ("AppImage application bundle") with no
`<icon>` element, the single `<generic-icon
name="application-x-executable"/>` element, the single `<glob
weight="60" pattern="*.appimage"/>` owned by it at weight 60 and by
`application/x-iso9660-appimage` at the default weight 50, the
`<magic>` match `ELF` (string, offset 1) with the nested byte matches
`0x41` at 8, `0x49` at 9 and `0x02` at 10 (the sibling type-1 magic
takes `0x01` at 10 instead), no `<alias>` elements, and the two
sub-classes `application/x-executable` and `application/vnd.squashfs`;
the dash-form name `application-vnd.appimage` occurs 0 times in the
database (`grep -o` count 0). With no `<icon>` element the type asks
its literal dash-form name first: a Gio probe run at planning time
(2026-11-24, `Gio.content_type_guess` on a `test.appimage` file) shows
the fallback chain `application-vnd.appimage` then
`application-x-executable`, the theme ships no
`application-vnd.appimage.svg` (no such name in any of the three
mimetypes directories), while Breeze ships the exact-name
`application-vnd.appimage.svg` at 16, 22, 24, 32 and 64 (`find` over
`/usr/share/icons` lists it under both `breeze` and `breeze-dark`), so
today an `.appimage` file shows Breeze's art, not this theme's own. No
reference screenshot shows an AppImage item icon, so no reference
pixels are used and the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/application-vnd.appimage.svg` under `16x16`, `22x22`
  and `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme`
  already declares the three MimeTypes directories. Give each file the
  XML declaration, the comment `<!-- PLACEHOLDER: original AppImage
  bundle illustration pending user-approved artwork. -->`, a short
  comment saying it is our own drawing in the Platinum palette, not
  traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art shares the generic document's page
  (the page outline, white page and folded-corner flap of the
  `_PAGE_*` shapes the `shape_pins/_shared.py` registry keeps) and
  holds a launch arrow — an up-pointing black triangle head over a
  black shaft, a run-this-bundle mark distinct from the
  `video-x-generic` screen's right-pointing play triangle (different
  orientation, different backing), from the queued `audio-ogg`
  equalizer bars and the `application-x-executable` window's
  descending bars (no triangle in either), from the queued
  `application-x-arj` sealed-package letter-A mark, and from the
  declared superclass `application-vnd.squashfs`'s disc stack (no
  page, no arrow):
  - 32x32: the three `_PAGE_32` page elements; then the head, `path
    d="M16 9 L22 17 L10 17 Z" fill="#000000"` (apex on the page's
    centre column 16, base row 17 spanning columns 10..22), then the
    shaft, `rect x="15" y="17" width="2" height="8" fill="#000000"`
    (columns 15..16, rows 17..24). A script run at planning time
    checked the head's bounding vertices and the shaft's cells sit
    inside the white page polygon and clear of the folded corner (the
    flap spans columns 19..25 above row 10; the arrow's topmost row 9
    only reaches column 16).
  - 22x22: the three `_PAGE_22` page elements; then the head, `path
    d="M11 5 L15 11 L7 11 Z" fill="#000000"` (apex on column 11, base
    row 11 spanning columns 7..15), then the shaft, `rect x="10"
    y="11" width="2" height="6" fill="#000000"` (columns 10..11, rows
    11..16). Every vertex and cell sits inside the white page and
    clears the folded corner (the flap spans columns 13..17 above row
    6; the apex sits on column 11).
  - 16x16: the three `_PAGE_16` page elements; then the head, `path
    d="M8 5 L11 9 L5 9 Z" fill="#000000"` (apex on column 8, base row
    9 spanning columns 5..11), then the shaft, `rect x="8" y="9"
    width="1" height="4" fill="#000000"` (column 8, rows 9..12). Every
    vertex and cell sits inside the white page and clears the folded
    corner (the flap spans columns 9..12 above row 5; the apex sits on
    column 8), checked by the same script.

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the Squashfs rows,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above (the three `_PAGE_*` elements spread
  as the prefix, then the head path and the shaft rect in the order
  listed).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-vnd.appimage` in the last cell, as the
  `application-vnd.squashfs` sentence there does.
- `docs/installing.md`: add the AppImage bundle icon to the sentence
  listing the icon theme's placeholder illustrations and their sizes
  (the one naming the `application-vnd.squashfs` files).
- The queued mimetype-icon entries ahead of this one (the pending
  `application-x-arj` archive plan and the in-flight `application-ogg`
  and `audio-ogg` container-and-audio plans) edit the same inventory
  block, `PINS` registry, invariants row and installing.md sentence;
  this entry sits behind them in the queue, so rebase on whatever they
  have landed when picking this up, keeping one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the three `_PAGE_*`
  elements matching the blank-document pins, then the head path and
  the shaft rect), carries a placeholder marker and has a
  `PLACEHOLDERS.md` row; the existing inventory, palette, geometry and
  placeholder-register tests cover all three.
- Changing the head's apex, base or fill, the shaft's position, size
  or fill, or the element order, in one file makes the geometry test
  fail; dropping a file while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The `#000000` and `#FFFFFF` fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- The launch arrow shares no drawing element with the
  `video-x-generic` play triangle (up-pointing over a shaft, not
  right-pointing inside a screen), none with the queued `audio-ogg`
  equalizer bars and none with the `application-x-executable` bars (no
  triangle in either), so the siblings stay visually distinct.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into
  a scratch `XDG_DATA_HOME` (the `make install
  INSTALL_PACKAGES=icon-theme DESTDIR=<root>` route installs it at
  `<root>$XDG_DATA_HOME/icons`; add that installed path to
  `XDG_DATA_DIRS`), use a scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`),
  `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset `DISPLAY` and
  `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-vnd.appimage` resolves to the theme's 32x32
  `mimetypes/application-vnd.appimage.svg` (at planning time the theme
  ships no such file, so the name fell through to Breeze's), and
  `text-x-generic` still resolves to the theme's own file. Report the
  output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

### Platinum icon theme: draw Flatpak repository descriptions with an original `application-vnd.flatpak.repo` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A Flatpak repository description (`*.flatpakrepo`, as the
file manager identifies it) draws this theme's own mark beside the
Platinum documents and folders. Ship one original placeholder icon,
`application-vnd.flatpak.repo`, at 16x16, 22x22 and 32x32, in the same
mimetype-item series as the `application-x-generic` blank page. It is
a sibling of the pending `application-vnd.flatpak.ref` plan (the
`*.flatpakref` repository-reference type), which declares this type
out of scope; this entry covers only `application/vnd.flatpak.repo`.
Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/vnd.flatpak.repo` ("Flatpak repository description") with
no `<icon>` element and no `<alias>` element, the single `<generic-icon
name="package-x-generic"/>` element, the single `<glob
pattern="*.flatpakrepo"/>` at the default weight 50, the `<magic>`
match `[Flatpak Repo]` (string, offset 0:256) and the sub-class
`text/plain`; the dash-form name `application-vnd.flatpak.repo` occurs
0 times in the database (`grep -o` count 0). With no `<icon>` element
the type asks its literal dash-form name first: a Gio probe run at
planning time (2026-11-24, `Gio.content_type_guess` on a
`test.flatpakrepo` file) shows the fallback chain
`application-vnd.flatpak.repo` then `package-x-generic`. The theme
ships `package-x-generic.svg` at all three sizes, so today a
`.flatpakrepo` file draws this theme's own package box — the new icon
gives the type a mark of its own. Breeze ships no exact-name file
(`find` over `/usr/share/icons` lists no `application-vnd.flatpak.repo`
in either `breeze` or `breeze-dark`; its only close mimetype name is
`application-vnd.flatpak.ref.svg`, which the pending Flatpak-ref plan
covers), so nothing else competes for the name. No reference
screenshot shows a `.flatpakrepo` item icon, so no reference pixels
are used and the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/application-vnd.flatpak.repo.svg` under `16x16`,
  `22x22` and `32x32` of `theme/icons/org.macos8.desktop/`.
  `index.theme` already declares the three MimeTypes directories. Give
each file the XML declaration, the comment `<!-- PLACEHOLDER:
  original Flatpak repository-description illustration pending
  user-approved artwork. -->`, a short comment saying it is our own
  drawing in the Platinum palette, not traced from anyone's artwork,
  and a root with matching `width`, `height` and `viewBox`. The art
  shares the sealed package box (every drawing element of
  `package-x-generic.svg` at that size, the `_SEALED_PACKAGE_*` group
  the `tests/support/icon/shape_pins/_shared.py` registry keeps) and
  holds a black stepped capital letter R on the white body left of the
  grey tape stripe — a repository mark distinct from the deb package's
  letter D, the tar archive's letter T, the compressed-tar archive's
  stepped Z, the RAR archive's stepped diamond, the ZIP archive's
  zipper slider (all on the same box at other cells), the queued
  `application-vnd.flatpak.ref` arrow-into-open-crate mark and the
  queued `application-vnd.appimage` launch arrow (both other marks):
  - 32x32: the five `_SEALED_PACKAGE_32` box elements; then the
    letter, six rects — the stem, `rect x="5" y="15" width="1"
    height="7"` (column 5, rows 15..21); the top bar, `rect x="6"
    y="15" width="4" height="1"` (columns 6..9, row 15); the bowl's
    right side, `rect x="9" y="16" width="1" height="2"` (column 9,
    rows 16..17); the middle bar, `rect x="6" y="18" width="4"
    height="1"` (columns 6..9, row 18); and the two leg steps, `rect
    x="9" y="19" width="1" height="1"` and `rect x="10" y="20"
    width="1" height="1"`. A script run at planning time checked every
    letter cell sits on the box's white face, clear of the grey tape
    stripe (columns 15..16) and does not overlap another letter cell.
  - 22x22: the five `_SEALED_PACKAGE_22` box elements; then the
    letter, six rects — the stem, `rect x="4" y="9" width="1"
    height="7"` (column 4, rows 9..15); the top bar, `rect x="5" y="9"
    width="3" height="1"` (columns 5..7, row 9); the bowl's right
    side, `rect x="7" y="10" width="1" height="2"` (column 7, rows
    10..11); the middle bar, `rect x="5" y="12" width="3" height="1"`
    (columns 5..7, row 12); and the two leg steps, `rect x="7" y="13"
    width="1" height="1"` and `rect x="8" y="14" width="1" height="1"`.
    Every letter cell sits on the white face, clear of the tape
    (columns 10..11), checked by the same script.
  - 16x16: the five `_SEALED_PACKAGE_16` box elements; then the
    letter, five rects — the stem, `rect x="3" y="7" width="1"
    height="5"` (column 3, rows 7..11); the top bar, `rect x="4" y="7"
    width="2" height="1"` (columns 4..5, row 7); the bowl's right
    side, `rect x="5" y="8" width="1" height="1"`; the middle bar,
    `rect x="4" y="9" width="2" height="1"` (columns 4..5, row 9); and
    the leg step, `rect x="5" y="10" width="1" height="1"`. Every
    letter cell sits on the white face, clear of the tape (columns
    7..8), checked by the same script.

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the Squashfs rows,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above (the five `_SEALED_PACKAGE_*` box
  elements spread as the prefix, then the letter rects in the order
  listed).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-vnd.flatpak.repo` in the last cell, as
  the `application-vnd.squashfs` sentence there does.
- `docs/installing.md`: add the Flatpak repository-description icon to
  the sentence listing the icon theme's placeholder illustrations and
  their sizes (the one naming the `application-vnd.squashfs` files).
- The queued mimetype-icon entries ahead of this one (the pending
  `application-vnd.flatpak.ref` plan and the in-flight
  `application-vnd.appimage` and `application-x-arj` plans) edit the
  same inventory block, `PINS` registry, invariants row and
  installing.md sentence; this entry sits behind them in the queue, so
  rebase on whatever they have landed when picking this up, keeping
  one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the five
  `_SEALED_PACKAGE_*` elements matching the `package-x-generic` pins,
  then the letter rects), carries a placeholder marker and has a
  `PLACEHOLDERS.md` row; the existing inventory, palette, geometry and
  placeholder-register tests cover all three.
- Changing any letter rect's position, size or fill, or the element
  order, in one file makes the geometry test fail; dropping a file
  while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The `#000000` and `#FFFFFF` fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- The letter R shares no drawing element with the deb `D`, tar `T`,
  compressed-tar `Z`, RAR diamond or ZIP zipper on the same box, nor
  with the queued Flatpak-ref arrow-into-open-crate or AppImage launch
  arrow, so the siblings stay visually distinct.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into
  a scratch `XDG_DATA_HOME` (the `make install
  INSTALL_PACKAGES=icon-theme DESTDIR=<root>` route installs it at
  `<root>$XDG_DATA_HOME/icons`; add that installed path to
  `XDG_DATA_DIRS`), use a scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`),
  `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset `DISPLAY` and
  `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-vnd.flatpak.repo` resolves to the theme's 32x32
  `mimetypes/application-vnd.flatpak.repo.svg` (at planning time the
  name falls through to the theme's own `package-x-generic`), and
  `text-x-generic` still resolves to the theme's own file. Report the
  output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

### Platinum icon theme: draw Flatpak repository references with an original `application-vnd.flatpak.ref` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** KIO requests an `application/vnd.flatpak.ref` item's icon
under the shared MIME database's type-spelled name
`application-vnd.flatpak.ref`, and on this host that exact name draws
Breeze's art even though the database's `generic-icon` for the type is
the theme's own shipped `package-x-generic` file: ship one original
placeholder icon, `application-vnd.flatpak.ref`, at 16x16, 22x22 and
32x32, in the same mimetype-item package series as the landed
`application-vnd.rar`, `application-gzip` and `application-x-arj`
entries. Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/vnd.flatpak.ref` ("Flatpak repository reference") with
`generic-icon name="package-x-generic"` and no `<icon>` element; it
has `<sub-class-of type="text/plain"/>`, one `<magic>` matcher
(`value="[Flatpak Ref]"` at `offset="0:256"`), one `<glob
pattern="*.flatpakref">` at the default weight, no `<alias>` element,
and the string `flatpakref` occurs exactly once in the whole database
(that glob — the string `vnd.flatpak.ref` occurs once, the type name
itself), so one file covers exactly its own name: no alias file and no
per-type fallback are in play. Breeze ships the exact name under
`mimetypes/` — at 16, 22, 24, 32 and 64 in `breeze`, and at 16, 22, 32
and 64 in `breeze-dark` (`breeze-dark` has no 24 rendition) — and the
theme's `index.theme` declares `Inherits=breeze`, so Breeze's
exact-name file beats the theme's generic-icon fallback and a
`*.flatpakref` item draws Breeze's art unless the theme ships the
name. Planning-time probe on 2026-11-24 with the headless Gio check
(`Gio.content_type_guess` then `Gio.content_type_get_icon` on a
scratch-named `*.flatpakref` file): the file resolves to
`application/vnd.flatpak.ref` and the icon chain asks the exact
dash-form name `application-vnd.flatpak.ref` first, before
`package-x-generic` — no GUI probe needed to show the request order.
No reference screenshot shows a Flatpak repository reference item
icon, so no reference pixels are used and the drawing is this theme's
own choice. Out of scope, on checked evidence: `application/vnd.flatpak.repo`
(`*.flatpakrepo`, one `vnd.flatpak.repo` occurrence in the database,
a separate type) — Breeze ships no `application-vnd.flatpak.repo`
exact-name file, so its icon chain falls through to the theme's own
shipped `package-x-generic` drawing already, and this entry ships
nothing for it.

**Approach.**

- Add `mimetypes/application-vnd.flatpak.ref.svg` under `16x16`,
  `22x22` and `32x32` of `theme/icons/org.macos8.desktop/`.
  `index.theme` already declares the three MimeTypes directories. Give
  each file the XML declaration, the comment `<!-- PLACEHOLDER:
  original Flatpak repository-reference illustration pending
  user-approved artwork. -->`, a short comment saying it is our own
  drawing in the Platinum palette, not traced from anyone's artwork,
  and a root with matching `width`, `height` and `viewBox`. The art
  shares the sealed package box (the `_SEALED_PACKAGE_*` tuple) and
  holds an original repository-reference mark on the white face: a
  three-cell arrow-head bar, a one-cell shaft dropping from it, and an
  open crate under the shaft (a one-cell lip at each end sitting on a
  wider one-row floor) — a reference dropping into a depot, distinct
  from gzip's filled two-cell funnel shaft, tar's T, 7z's stepped 7,
  rar's stepped diamond, zip's zipper slider, deb's hollow capital D,
  cpio's capital C, xz's stair-stepped X and the QCOW disc's hollow Q
  with its tail. Every element is an axis-aligned rect in `#000000`;
  the cells below were verified by script at planning time to sit on
  the white face, clear of the grey tape stripe, and not to overlap:
  - 32x32: the `_SEALED_PACKAGE_32` box elements, then `x=9 y=14
    3×1`, `x=9 y=15 3×1` (head bar), `x=10 y=16 1×1` (shaft tip),
    `x=10 y=17 1×5` (shaft), `x=7 y=22 1×1` and `x=13 y=22 1×1`
    (lips), `x=7 y=23 7×1` (floor).
  - 22x22: the `_SEALED_PACKAGE_22` box elements, then `x=6 y=10
    3×1`, `x=6 y=11 3×1` (head bar), `x=7 y=12 1×1` (shaft tip),
    `x=7 y=13 1×4` (shaft), `x=5 y=16 1×1` and `x=9 y=16 1×1`
    (lips), `x=5 y=17 5×1` (floor).
  - 16x16: the `_SEALED_PACKAGE_16` box elements, then `x=3 y=7
    3×1` (head bar), `x=4 y=8 1×3` (shaft), `x=3 y=11 1×1` and
    `x=5 y=11 1×1` (lips), `x=3 y=12 3×1` (floor).

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the `application-vnd.rar`
  rows, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`, and extend the
  package-series comment above them to name the Flatpak
  repository-reference file.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three
  drawings in `PINS` from the lists above (the `_SEALED_PACKAGE_*`
  tuple, then the head bar, shaft and open crate).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-vnd.flatpak.ref` in the last cell, as the
  `application-vnd.rar` sentence there does.
- `docs/installing.md`: add the Flatpak repository-reference icon to
  the sentence listing the icon theme's placeholder illustrations and
  their sizes.
- The Flatpak work shares the inventory block, `PINS` registry,
  invariants row and installing.md sentence with the waiting mimetype
  entries (the epub, PKCS#12, Ogg-container, Ogg-audio, ARJ and
  AppImage plans); this entry sits behind them in the queue, so rebase
  on whatever they have landed when picking this up, keeping one row
  per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the `_SEALED_PACKAGE_*`
  box elements, in the same order, then the head bar, shaft tip,
  shaft, lips and floor), carries a placeholder marker and has a
  `PLACEHOLDERS.md` row; the existing inventory, palette, geometry and
  placeholder-register tests cover all three.
- Changing one mark cell's position, size or fill, or the element
  order, in one file makes the geometry test fail; dropping a file
  while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The `#000000` fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch data root and use the scratch-homes recipe the goal
  paragraph records (scratch `HOME`, `XDG_DATA_HOME`,
  `XDG_DATA_DIRS` naming the installed data root, `XDG_CONFIG_HOME`
  with `[Icons] Theme=org.macos8.desktop` in `kdeglobals`, scratch
  `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, `QT_QPA_PLATFORM=offscreen`,
  no `DISPLAY` or `WAYLAND_DISPLAY`). `application-vnd.flatpak.ref`
  resolves to the theme's 32x32
  `mimetypes/application-vnd.flatpak.ref.svg` (at planning time it
  resolved to Breeze's exact-name file) and `package-x-generic` still
  resolves to the theme's own file. Report the output in VERIFIED.
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
