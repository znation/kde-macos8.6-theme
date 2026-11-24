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

### Platinum icon theme: draw source RPM packages with an original `application-x-source-rpm` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A source RPM file (`*.src.rpm`, `*.spm`, as the file manager
identifies it) draws Breeze's art beside the Platinum documents and
folders. Ship one original placeholder icon, `application-x-rpm`'s
companion `application-x-source-rpm`, at 16x16, 22x22 and 32x32, in
the same sealed-package series as the deb box, the tar box, the ARJ,
cpio, RAR and ZIP boxes and the waiting RPM-hat and Flatpak-repository
entries. Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/x-source-rpm` ("Source RPM package") with no `<icon>`
element, the `<generic-icon name="package-x-generic"/>` the theme
already ships, no `<alias>` element, no `<magic>` of its own (the
matchers come from its parent `<sub-class-of type="application/x-rpm"/>`)
and the two globs `*.src.rpm` and `*.spm` at the default weight 50;
the dash-form string `application-x-source-rpm` occurs 0 times
elsewhere in the database (`str.count` is 0 — `grep -c` counts lines,
not matches), so one file covers exactly its own name and no per-type
fallback is in play. The theme's `index.theme` declares
`Inherits=breeze`, so the lookup falls through to Breeze's exact-name
file (Breeze ships `application-x-source-rpm.svg` at 16, 22, 24, 32
and 64 in both `breeze` and `breeze-dark`, each verified with an `ls`
check). Planning-time probe 2026-11-24 with `kiconfinder6`, the theme
installed into scratch XDG homes (`XDG_DATA_HOME` naming the installed
scratch data root, `XDG_DATA_DIRS=/usr/share`,
`[Icons] Theme=org.macos8.desktop` in the scratch `kdeglobals`,
`QT_QPA_PLATFORM=offscreen`, no `DISPLAY`): `application-x-source-rpm`
resolved to `:/icons/breeze/mimetypes/32/application-x-source-rpm.svg`
while `package-x-generic` resolved to the theme's own 32x32 file — the
gap is real, not the screened-out shape where the theme's own generic
art wins. A headless Gio probe agrees: `Gio.content_type_guess` on a
`test.src.rpm` and on a `test.spm` names `application/x-source-rpm`
and `Gio.content_type_get_icon(...).get_names()` lists
`application-x-source-rpm` first. No reference screenshot shows a
source-RPM-item icon, so no reference pixels are used and the drawing
is this theme's own choice. Out of scope, one name per entry as in
the deb plan: this entry draws only `application-x-source-rpm`; the
binary `application/x-rpm` type keeps its own entry.

**Approach.**

- Add `mimetypes/application-x-source-rpm.svg` under `16x16`, `22x22`
  and `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme`
  already declares the three MimeTypes directories. Give each file the
  XML declaration, the comment `<!-- PLACEHOLDER: original source-RPM
  illustration pending user-approved artwork. -->`, a short comment
  saying it is our own drawing in the Platinum palette, not traced
  from anyone's artwork, and a root with matching `width`, `height`
  and `viewBox`. The art shares the sealed package box (every drawing
  element of that size's `package-x-generic.svg`: the outline, lid
  highlight, white body and grey tape stripe) and holds a black
  capital letter S (for source), built from five rects in document
  order — top bar, left stem, middle bar, right stem, bottom bar — an
  original generic-letter mark distinct from the deb box's capital D,
  the tar box's capital T, the ARJ box's letter A, the cpio box's Z,
  the RAR box's diamond, the ZIP box's zipper, the waiting
  Flatpak-repository box's stepped capital R and the waiting RPM box's
  hat (it is a letter, not any vendor's logo):
  - 32x32: the five shared box elements; then, all `#000000`, the
    top bar `7,15 5×1` (cols 7..11, row 15), the left stem `7,16 1×2`
    (col 7, rows 16..17), the middle bar `7,18 5×1` (cols 7..11, row
    18), the right stem `11,19 1×2` (col 11, rows 19..20) and the
    bottom bar `7,21 5×1` (cols 7..11, row 21); every cell sits on
    the white body, left of and clear of the tape stripe (cols
    15..16).
  - 22x22: the five shared box elements; then, all `#000000`, the
    top bar `4,10 5×1` (cols 4..8, row 10), the left stem `4,11 1×2`
    (col 4, rows 11..12), the middle bar `4,13 5×1` (cols 4..8, row
    13), the right stem `8,14 1×2` (col 8, rows 14..15) and the
    bottom bar `4,16 5×1` (cols 4..8, row 16); every cell sits on
    the white body, left of and clear of the tape stripe (cols
    10..11).
  - 16x16: the five shared box elements; then, all `#000000`, the
    top bar `3,7 4×1` (cols 3..6, row 7), the left stem `3,8 1×1`
    (col 3, row 8), the middle bar `3,9 4×1` (cols 3..6, row 9), the
    right stem `6,10 1×1` (col 6, row 10) and the bottom bar `3,11
    4×1` (cols 3..6, row 11); every cell sits on the white body, left
    of and clear of the tape stripe (cols 7..8).

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the deb-package rows,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three
  drawings in `PINS` from the lists above (the `*_SEALED_PACKAGE_*`
  box tuple, then the five letter rects in document order), with the
  same type-spelled-name comment convention the deb pin carries. The
  mimetypes-split entry is reshaping `PINS` into per-group modules, so
  rebase on whatever shape it has landed when picking this up.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-x-source-rpm` in the last cell, as the
  `application-vnd.debian.binary-package` sentence there does.
- `docs/installing.md`: add a source-RPM icon to the sentence listing
  the icon theme's placeholder illustrations and their sizes (beside
  the deb-package clause).
- The in-flight `application-x-rpm`, Flatpak-repository and
  mimetypes-split entries edit the same inventory block, pin registry,
  invariants row and installing.md sentence; this entry sits behind
  them in the queue, so rebase on whatever they have landed when
  picking this up, keeping one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the five box elements
  matching the `package-x-generic.svg` pin's tuple, in the same
  order, then the five letter rects in document order), carries a
  placeholder marker and has a `PLACEHOLDERS.md` row; the existing
  inventory, palette, geometry and placeholder-register tests cover
  all three.
- Changing one letter rect's position, size or fill, or the element
  order, in one file makes the geometry test fail; dropping a file
  from one size directory makes the inventory test fail.
- `rg -n 'application-x-source-rpm' docs/installing.md
  docs/invariants.md PLACEHOLDERS.md` shows the new clause,
  provenance sentence and rows, each dated by its stamp.
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME` with a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset
  `DISPLAY` and `WAYLAND_DISPLAY`, set `QT_QPA_PLATFORM=offscreen`.
  `application-x-source-rpm` resolves to the theme's own file and
  `package-x-generic` still resolves to the theme's file. Report the
  output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

### Platinum icon theme: draw WAVE audio with an original `audio-vnd.wave` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A WAVE audio file (`*.wav`, as the file manager identifies
it) draws this theme's own mark beside the Platinum documents and
folders instead of falling through to the generic audio art. Ship one
original placeholder icon, `audio-vnd.wave`, at 16x16, 22x22 and
32x32, in the page-backed mimetype-item series the `audio-ogg` icon
belongs to. Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`audio/vnd.wave` ("WAV audio") with no `<icon>` element and no
`<generic-icon>` element, sub-class-of `application/x-riff`, the
single `<glob pattern="*.wav"/>` at the default weight, the `<magic>`
string matches `WAVE` at offset 8 and `WAV ` at offset 8, and the
aliases `audio/wav` and `audio/x-wav` (no separate `audio/x-wav`
block exists in this database build). With no `generic-icon` the type
asks its literal dash-form name first: a Gio probe run at planning
time returned the `GThemedIcon` names `audio-vnd.wave` then
`audio-x-generic` for `song.wav`. A `kiconfinder6` probe run at
planning time (2026-11-24, theme copied into a scratch
`XDG_DATA_HOME`/`XDG_CONFIG_HOME`, `[Icons] Theme=org.macos8.desktop`)
resolved `audio-vnd.wave` to the theme's own
`32x32/mimetypes/audio-x-generic.svg` — the generic-audio fallback.
Breeze does list `audio-vnd.wave.svg` under
`/usr/share/icons/breeze/mimetypes` (16/22/32), but a `Theme=breeze`
probe run the same day resolves Breeze's names to its embedded
`:/icons` resource, and the theme-selected probe resolved to the
theme's own generic file instead of Breeze's installed
`audio-vnd.wave.svg`, so the theme's generic-audio fallback answers
the name today and shipping it wins the in-theme exact-name match. No
reference screenshot shows a `.wav` item icon, so no reference pixels
are used and the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/audio-vnd.wave.svg` under `16x16`, `22x22` and
  `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme` already
  declares the three MimeTypes directories. Give each file the XML
  declaration, the comment `<!-- PLACEHOLDER: original WAVE audio
  illustration pending user-approved artwork. -->`, a short comment
  saying it is our own drawing in the Platinum palette, not traced
  from anyone's artwork, and a root with matching `width`, `height`
  and `viewBox`. The art shares the generic document's page (the
  `_PAGE_16`, `_PAGE_22` and `_PAGE_32` tuples the
  `tests/support/icon/shape_pins/_shared.py` registry keeps) and adds
  one connected sine-wave ribbon — a single filled `polygon` (no
  stroke, no `fill="none"`): one full smooth wave period drawn as a
  ribbon two-to-three pixels thick. One smooth periodic ribbon is
  distinct from the sharp EKG zigzag the queued `audio-flac` entry
  plans on the same page, the four disjoint equalizer bars
  `audio-ogg.svg` draws, the beamed note pair `audio-x-generic.svg`
  draws and every other mark in the series:
  - 32x32: the three `_PAGE_32` elements, then
    `<polygon points="9,18 10,16 11,15 12,14 13,14 14,15 15,16 16,18
    17,20 18,21 19,22 20,22 21,21 22,20 23,18 23,21 22,23 21,24 20,25
    19,25 18,24 17,23 16,21 15,19 14,18 13,17 12,17 11,18 10,19 9,21"
    fill="#000000"/>` (top edge left to right — the wave rises from
    the mid-line over its crest, dips through the mid-line into its
    trough and returns — then the same curve three rows lower, right
    to left).
  - 22x22: the three `_PAGE_22` elements, then
    `<polygon points="7,10 8,8 9,7 10,7 11,9 12,11 13,13 14,13 15,12
    16,10 16,12 15,14 14,15 13,15 12,13 11,11 10,9 9,9 8,10 7,12"
    fill="#000000"/>` (top edge left to right, then the same curve
    two rows lower, right to left).
  - 16x16: the three `_PAGE_16` elements, then
    `<polygon points="5,8 6,6 7,6 8,7 9,9 10,10 11,10 12,8 12,10
    11,12 10,12 9,11 8,9 7,8 6,8 5,10" fill="#000000"/>` (top edge
    left to right, then the same curve two rows lower, right to
    left).

  A script run at planning time checked every vertex of each polygon
  sits strictly inside that size's white page polygon (clear of the
  folded flap, whose diagonal is `y = x - 15` at 32, `y = x - 11` at
  22 and `y = x - 7` at 16) and that no polygon self-intersects.
  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the `audio-ogg` rows,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the `audio-ogg` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three
  drawings in `PINS` beside the `audio-ogg` pins (the `_PAGE_*`
  elements spread as the prefix, then the polygon exactly as listed).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `audio-vnd.wave` in the last cell, as the `audio-ogg`
  sentence there does.
- `docs/installing.md`: add the WAVE audio icon to the sentence
  listing the icon theme's placeholder illustrations and their sizes
  (the one naming the `audio-ogg` files).
- The queued mimetype-icon entries ahead of this one (the in-flight
  `application-x-rpm` plan, the in-flight mimetypes shape-pin
  registry split and the queued `audio-flac` plan) edit the same
  inventory block, `PINS` registry, invariants row and installing.md
  sentence; this entry sits behind them at the back of the queue, so
  rebase on whatever they have landed when picking this up, keeping
  one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the three `_PAGE_*`
  elements matching the `text-x-generic` pins, then the wave ribbon
  polygon), carries a placeholder marker and has a `PLACEHOLDERS.md`
  row; the existing inventory, palette, geometry and
  placeholder-register tests cover all three.
- Changing the polygon's points or fill, or the element order, in one
  file makes the geometry test fail; deleting a file while its paths
  remain in `SHIPPED_ICONS` makes the inventory test fail.
- The polygon's `#000000` fill (over the page's `#000000`, `#FFFFFF`
  and `#DDDDDD`) stays inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- The wave ribbon shares no drawing element with the `audio-ogg`
  equalizer bars, the `audio-x-generic` note rects or the queued
  `audio-flac` pulse polygon (one smooth connected ribbon, not a
  spiky zigzag and not disjoint bars), so the audio marks stay
  visually distinct.
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
  `audio-vnd.wave` resolves to the theme's 32x32
  `mimetypes/audio-vnd.wave.svg` (at planning time the name falls
  through to the theme's own `audio-x-generic`), and
  `text-x-generic` still resolves to the theme's own file. Report the
  output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

### Platinum icon theme: draw RPM spec files with an original `text-x-rpm-spec` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** An RPM spec file (`*.spec`, as the file manager identifies
it) draws this theme's own mark beside the Platinum documents and
folders instead of falling through to the generic document art. Ship
one original placeholder icon, `text-x-rpm-spec`, at 16x16, 22x22 and
32x32, in the page-backed text-item series the `text-x-script` icon
belongs to. Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`text/x-rpm-spec` ("RPM spec file") with no `<icon>` element and no
`<generic-icon>` element, sub-class-of `text/plain`, the single
`<glob pattern="*.spec"/>` at the default weight, no aliases, no
tree-magic, and one `<magic>` block of priority 50 matching the
strings `Summary: ` and `%define ` at offset 0. With no
`generic-icon` the type asks its literal dash-form name first: a
`kiconfinder6` probe run at planning time (2026-11-24, theme copied
into a scratch `XDG_DATA_HOME`/`XDG_CONFIG_HOME`,
`[Icons] Theme=org.macos8.desktop`) resolved `text-x-rpm-spec` to the
theme's own `32x32/mimetypes/text-x-generic.svg` — the
generic-document fallback — the same file a `text-x-generic` probe
resolved to, so the theme's generic-document art answers the name
today and shipping it wins the in-theme exact-name match. Breeze
ships `text-x-rpm-spec.svg` under both
`/usr/share/icons/breeze/mimetypes` and
`/usr/share/icons/breeze-dark/mimetypes` at 16, 22 and 32. No
reference screenshot shows a `.spec` item icon, so no reference
pixels are used and the drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/text-x-rpm-spec.svg` under `16x16`, `22x22` and
  `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme` already
  declares the three MimeTypes directories. Give each file the XML
  declaration, the comment `<!-- PLACEHOLDER: original RPM spec
  illustration pending user-approved artwork. -->`, a short comment
  saying it is our own drawing in the Platinum palette, not traced
  from anyone's artwork, and a root with matching `width`, `height`
  and `viewBox`. The art shares the generic document's page (the
  `_PAGE_16`, `_PAGE_22` and `_PAGE_32` tuples the
  `tests/support/icon/shape_pins/_shared.py` registry keeps) and adds
  one black check mark — a single filled `polygon` (no stroke, no
  `fill="none"`), the tick a checked-off specification makes: a short
  arm descending to a low vertex, then a long arm rising to the
  page's right. One angular connected tick is distinct from the
  `#999999` text lines `text-x-generic.svg` draws, the stepped angle
  brackets `text-x-script.svg` draws, the framed grey stencil plate
  `text-x-generic-template.svg` draws and every other mark in the
  text series (the queued source-RPM plan's capital S sits on a
  sealed package box, not a page):
  - 32x32: the three `_PAGE_32` elements, then
    `<polygon points="9,16 12,19 20,11 20,8 12,16 9,13"
    fill="#000000"/>` (upper edge of the tick band left to right —
    down the short arm, up the long arm to the tip — then the lower
    edge right to left, tip to foot).
  - 22x22: the three `_PAGE_22` elements, then
    `<polygon points="6,10 8,12 14,6 14,4 8,10 6,8"
    fill="#000000"/>` (same tick, same construction).
  - 16x16: the three `_PAGE_16` elements, then
    `<polygon points="5,8 7,10 11,6 11,4 7,8 5,6"
    fill="#000000"/>` (same tick, same construction).

  A script run at planning time rasterized each polygon (even-odd
  fill on whole-pixel cells) and checked every filled cell sits
  strictly inside that size's white page polygon and clear of the
  folded flap, whose diagonal is `y = x - 15` at 32, `y = x - 11` at
  22 and `y = x - 7` at 16. Validate by XML only, never by
  rasterizing in the suite: `convert`'s MSVG reader bleeds 1px
  shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the `text-x-script`
  rows, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the `text-x-script` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes/documents.py` (the module
  that holds the `text-x-generic` pins once the queued mimetypes
  registry split lands; `tests/support/icon/shape_pins/mimetypes.py`
  before it): pin the three drawings beside the `text-x-script` pins
  (the `_PAGE_*` elements spread as the prefix, then the polygon
  exactly as listed).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `text-x-rpm-spec` in the last cell, as the
  `media-optical` sentence there does.
- `docs/installing.md`: add the RPM spec icon to the sentence listing
  the icon theme's placeholder illustrations and their sizes (the one
  naming the `text-x-script` files).
- The queued mimetype-icon entries ahead of this one (the in-flight
  mimetypes shape-pin registry split, the in-flight
  `application-x-rpm` and `audio-flac` icon plans and the queued
  `audio-vnd.wave` and `application-x-source-rpm` plans) edit the
  same inventory block, pins registry, invariants row and
  installing.md sentence; this entry sits at the back of the queue,
  so rebase on whatever they have landed when picking it up, keeping
  one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes/documents.py` (or
`tests/support/icon/shape_pins/mimetypes.py` before the queued
registry split), `docs/invariants.md`, `docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the three `_PAGE_*`
  elements matching the `text-x-generic` pins, then the check-mark
  polygon), carries a placeholder marker and has a
  `PLACEHOLDERS.md` row; the existing inventory, palette, geometry
  and placeholder-register tests cover all three.
- Changing the polygon's points or fill, or the element order, in one
  file makes the geometry test fail; deleting a file while its paths
  remain in `SHIPPED_ICONS` makes the inventory test fail.
- The polygon's `#000000` fill (over the page's `#000000`, `#FFFFFF`
  and `#DDDDDD`) stays inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- The check mark shares no drawing element with the `text-x-generic`
  text lines, the `text-x-script` angle brackets, the
  `text-x-generic-template` stencil plate or the queued
  `application-x-source-rpm` sealed box (one connected angular tick,
  no grey lines, no brackets, no frame), so the text marks stay
  visually distinct.
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
  `text-x-rpm-spec` resolves to the theme's 32x32
  `mimetypes/text-x-rpm-spec.svg` (at planning time the name falls
  through to the theme's own `text-x-generic`), and
  `text-x-generic` still resolves to the theme's own file. Report the
  output in VERIFIED.
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
