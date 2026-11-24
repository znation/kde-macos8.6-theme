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

### Platinum icon theme: draw compiled gettext catalogs with an original `application-x-gettext-translation` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A compiled gettext message catalog (`*.gmo` or `*.mo`, as
the file manager identifies it) draws Breeze's art beside the Platinum
documents and folders. Ship one original placeholder icon,
`application-x-gettext-translation`, at 16x16, 22x22 and 32x32, in the
same mimetype-item series as the landed `application-x-mimearchive`
MHTML and `application-pkix-cert` certificate entries and the
in-flight WIM, NZB and queued pkix-crl entries.
Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/x-gettext-translation` ("Translated messages
(machine-readable)") with no `<icon>` element, no `<generic-icon>`
element, no `<alias>` element and no `<sub-class-of>`, one `<magic>`
holding the two offset-0 string matchers `\336\22\4\225` and
`\225\4\22\336` (the GNU catalog magic number in both byte orders),
the `*.gmo` glob at the default weight 50 — unique in the database —
and the `*.mo` glob at the default weight 50, shared with
`text/x-modelica` (so a `.mo` file may type as Modelica; a real
compiled catalog still types as `application/x-gettext-translation`
through the magic matcher, so the canonical-name file is what the
lookup reaches). No other MIME type declares the `.gmo` glob, and the
string `application-x-gettext-translation` occurs 0 times in the
database (`str.count` is 0 — `grep -c` counts lines, not matches).
With no icon element the type asks its literal name; the theme's
`index.theme` declares `Inherits=breeze`, so the lookup falls through
to Breeze's exact-name file (Breeze ships it at 16, 22, 24, 32 and 64,
each verified with a `[ -f ]` check). Planning-time probe on
2026-11-24 with `kiconfinder6`, the theme installed into scratch XDG
homes (`XDG_DATA_HOME` naming the installed scratch data root,
`XDG_DATA_DIRS=/usr/share`, `[Icons]
Theme=org.macos8.desktop` in the scratch `kdeglobals`,
`QT_QPA_PLATFORM=offscreen`, no `DISPLAY`):
`application-x-gettext-translation` resolved to
`:/icons/breeze/mimetypes/32/application-x-gettext-translation.svg`
while `text-x-generic` resolved to the theme's own 32x32 file — the
gap is real, not the screened-out shape where the theme's own generic
art wins. No reference screenshot shows a message-catalog item icon,
so no reference pixels are used and the drawing is this theme's own
choice.

**Approach.**

- Add `mimetypes/application-x-gettext-translation.svg` under `16x16`,
  `22x22` and `32x32` of `theme/icons/org.macos8.desktop/`.
  `index.theme` already declares the three MimeTypes directories.
  Give each file the XML declaration, the comment `<!--
  PLACEHOLDER: original compiled-gettext-catalog illustration
  pending user-approved artwork. -->`, a short comment saying it is
  our own drawing in the Platinum palette, not traced from anyone's
  artwork, and a root with matching `width`, `height` and `viewBox`.
  The art shares the shell-script document's page (every drawing
  element of that size's `application-x-shellscript.svg`: the page
  outline, white page and folded-corner flap) and holds a black
  speech bubble with a square tail — a message bubble speaking the
  catalog's translated lines, its interior holding one white top bar
  longer than the white bottom bar — an original mark distinct from
  the web-document window's globe, the shell script's `>_` prompt,
  JSON's curly braces, BitTorrent's download arrow and tray, the
  backup file's tilde, the crash core's square ring and center dot,
  the database canister, the ISO disc's capital I, the Squashfs
  tapering bands, the WIM split-volume gap, the NZB dot-and-bars
  groups, the certificate's seal-and-ribbons, the Android zipper
  teeth, the deb box's letter D and the MHTML paperclip:
  - 32x32: the three shared page elements; then the bubble body
    `10,12 12×8` (cols 10..21, rows 12..19, `#000000`), the square
    tail `11,20 2×2` (cols 11..12, rows 20..21, `#000000`), the top
    bar `12,14 8×1` (cols 12..19, row 14, `#FFFFFF`) and the bottom
    bar `12,16 5×1` (cols 12..16, row 16, `#FFFFFF`); every cell sits
    inside the white page and clear of the flap.
  - 22x22: the three shared page elements; then the bubble body
    `7,7 8×6` (cols 7..14, rows 7..12, `#000000`), the square tail
    `8,13 2×1` (cols 8..9, row 13, `#000000`), the top bar `8,8 5×1`
    (cols 8..12, row 8, `#FFFFFF`) and the bottom bar `8,10 3×1`
    (cols 8..10, row 10, `#FFFFFF`); every cell sits inside the white
    page and clear of the flap.
  - 16x16: the three shared page elements; then the bubble body
    `5,5 6×4` (cols 5..10, rows 5..8, `#000000`), the square tail
    `6,9 1×1` (col 6, row 9, `#000000`), the top bar `6,6 4×1`
    (cols 6..9, row 6, `#FFFFFF`) and the bottom bar `6,7 2×1`
    (cols 6..7, row 7, `#FFFFFF`); every cell sits inside the white
    page and clear of the flap.

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the MHTML web-archive
  rows, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above (the `*_PAGE_*` page tuple, then the
  bubble body, square tail and the two bars).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-x-gettext-translation` in the last cell,
  as the `application-x-mimearchive` sentence there does.
- `docs/installing.md`: add the compiled gettext-catalog icon to the
  sentence listing the icon theme's placeholder illustrations and
  their sizes.
- The waiting WIM, NZB, pkix-crl and in-flight qcow, pgp-signature and
  iccprofile entries edit the same inventory block, `PINS` registry,
  invariants row and installing.md sentence; this entry sits behind
  them in the queue, so rebase on whatever they have landed when
  picking this up, keeping one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the page elements matching
  the `application-x-shellscript.svg` pin's page tuple, in the same
  order, then the bubble body, square tail and the two bars), carries
  a placeholder marker and has a `PLACEHOLDERS.md` row; the existing
  inventory, palette, geometry and placeholder-register tests cover
  all three.
- Changing one speech-bubble rect's position, size or fill, or the
  element order, in one file makes the geometry test fail; dropping a
  file while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The `#000000` and `#FFFFFF` fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME`, use a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset
  `DISPLAY` and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-x-gettext-translation` resolves to the theme's 32x32
  `mimetypes/application-x-gettext-translation.svg` (at planning time,
  before this change, it resolved to Breeze's `:/icons/breeze/
  mimetypes/32/application-x-gettext-translation.svg`), and
  `text-x-generic` still resolves to the theme's own file. Report the
  output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

### Platinum icon theme: draw offline wiki archives with an original `application-x-openzim` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** An OpenZIM offline-wiki archive (`*.zim`, the format Kiwix
reads) draws no mimetype icon at all today: neither the theme nor its
inherited Breeze fallback ships one, so the file manager's generic
fallback stands in beside the Platinum documents and folders. Ship one
original placeholder icon, `application-x-openzim`, at 16x16, 22x22
and 32x32, in the same mimetype-item series as the landed
`application-x-shellscript`, `application-vnd.squashfs`,
`application-pkix-cert` and `application-x-bittorrent` files.
Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/x-openzim` ("OpenZIM file", acronym ZIM, expanded "Zeno
IMproved") with no `<icon>` element, no `<generic-icon>` element, no
`<alias>` element, no `<sub-class-of>` element, the single glob
`<glob pattern="*.zim">` at the default weight 50 and the single
magic matcher `\x5a\x49\x4d\x04` at offset 0; no other MIME type in
the database declares a `.zim` glob, and the string
`application-x-openzim` occurs 0 times in the database (`str.count`
is 0 — `grep -c` counts lines, not matches). The theme's
`index.theme` declares `Inherits=breeze`, and
`/usr/share/icons/breeze/mimetypes/` holds no
`application-x-openzim.svg` at any size, so an unshipped name resolves
to nothing; the offscreen probe (`kiconfinder6 application-x-openzim`
with no `DISPLAY`/`WAYLAND_DISPLAY`, `QT_QPA_PLATFORM=offscreen`) on
2026-11-24 printed nothing and exited 1. No reference screenshot shows
an offline-archive item icon, so no reference pixels are used and the
drawing is this theme's own choice.

**Approach.**

- Add `mimetypes/application-x-openzim.svg` under `16x16`, `22x22`
  and `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme`
  already declares the three MimeTypes directories. Give each file the
  XML declaration, the comment `<!-- PLACEHOLDER: original offline
  wiki archive illustration pending user-approved artwork. -->`, a
  short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art shares the document page (every
  drawing element of that size's `application-x-shellscript.svg`
  except the prompt glyphs) and holds a black band carrying a white
  wireframe globe — a round ring with a meridian bar and an equator
  line — an original mark distinct from the shell script's `>_`
  prompt, JSON's curly braces, BitTorrent's download arrow, the PGP
  key, the SQLite canister, the crash core's square ring with center
  dot and the X.509 certificate's square seal with ribbon tails (the
  globe's round ring and cross lines separate it from all of them at
  every size):
  - 32x32: the page paths `M6 3 h14 l6 6 v20 H6 Z` `#000000`,
    `M7 4 h12 l6 6 v18 H7 Z` `#FFFFFF` and the flap
    `M19 4 L25 4 L25 10 Z` `#DDDDDD`; band `10,15 12×7` `#000000`;
    then, all `#FFFFFF`, ring top rim `13,16 6×1` (row 16), ring
    bottom rim `13,20 6×1` (row 20), ring left wall `13,17 1×3`
    (rows 17..19), ring right wall `18,17 1×3` (rows 17..19),
    meridian `15,17 2×3` (rows 17..19) and equator `14,18 4×1`
    (row 18); every cell sits inside the band.
  - 22x22: the page paths `M4 1 h10 l4 4 v15 H4 Z` `#000000`,
    `M5 2 h8 l4 4 v13 H5 Z` `#FFFFFF` and the flap
    `M13 2 L17 2 L17 6 Z` `#DDDDDD`; band `7,10 8×5` `#000000`;
    then, all `#FFFFFF`, ring top rim `9,11 4×1` (row 11), ring
    bottom rim `9,13 4×1` (row 13), ring left wall `9,12 1×1`
    (row 12), ring right wall `12,12 1×1` (row 12) and equator
    `10,12 2×1` (row 12); the single interior row leaves no room for
    a meridian at this size.
  - 16x16: the page paths `M3 1 h7 l3 3 v10 H3 Z` `#000000`,
    `M4 2 h5 l3 3 v8 H4 Z` `#FFFFFF` and the flap
    `M9 2 L12 2 L12 5 Z` `#DDDDDD`; band `5,6 6×5` `#000000`;
    then, all `#FFFFFF`, ring top rim `6,7 4×1` (row 7), ring
    bottom rim `6,9 4×1` (row 9), ring left wall `6,8 1×1`
    (row 8), ring right wall `9,8 1×1` (row 8) and equator
    `7,8 2×1` (row 8).

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the shell-script row,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above (the `*_PAGE_*` page tuple, then the
  band, then the rims, walls, meridian and equator).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-x-openzim` in the last cell, as the
  `application-pgp-keys` sentence there does.
- `docs/installing.md`: add the offline-wiki-archive icon to the
  sentence listing the icon theme's placeholder illustrations and
  their sizes.
- The waiting pkix-crl, iccprofile and gettext-translation entries edit
  the same inventory block, `PINS` registry, invariants row and
  installing.md sentence; this entry sits behind them in the queue, so
  rebase on whatever they have landed when picking this up, keeping
  one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the page elements matching
  the `application-x-shellscript.svg` pin's page tuple, in the same
  order, then the band, then the rims, walls and cross lines), carries
  a placeholder marker and has a `PLACEHOLDERS.md` row; the existing
  inventory, palette, geometry and placeholder-register tests cover
  all three.
- Changing one band rectangle's, ring wall's, meridian's or equator's
  position, size or fill, or the element order, in one file makes the
  geometry test fail; dropping a file while leaving it shipped makes
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
  `application-x-openzim` resolves to the theme's 32x32
  `mimetypes/application-x-openzim.svg`, while the same probe against
  a data root without the theme prints nothing and exits 1. Report
  the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are
  unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full
  `make check` after the final edit, apart from main's known-red
  tests.

### Platinum icon theme: draw Snap packages with an original `application-vnd.snap` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A Snap package file (`*.snap`, as the file manager
identifies it) draws Breeze's art beside the Platinum documents and
folders. Ship one original placeholder icon, `application-vnd.snap`,
at 16x16, 22x22 and 32x32, in the same mimetype-item series as the
landed `application-vnd.squashfs` filesystem image — the type this
entry's MIME type is a declared subclass of, so the two marks must
stay distinct. Provenance: the installed shared MIME database
(`/usr/share/mime/packages/freedesktop.org.xml`) declares the type
`application/vnd.snap` ("Snap package") with no `<icon>` element, no
`<generic-icon>` element, no `<alias>` element, the single glob
`<glob pattern="*.snap">` at the default weight 50 owned by no other
MIME type, no `<magic>` element, and `<sub-class-of
type="application/vnd.squashfs">`; no other MIME type in the database
declares a `.snap` glob, and the string `application-vnd.snap` occurs
0 times in the database (`str.count` is 0 — `grep -c` counts lines,
not matches). With no icon element the type asks its literal name;
the theme's `index.theme` declares `Inherits=breeze` and the theme
ships no `application-vnd.snap.svg`, while Breeze ships the exact-name
file at 16, 22, 24, 32, 48 and 64 (`find` over `/usr/share/icons`
lists it under both `breeze` and `breeze-dark`), so the lookup falls
through to Breeze's file. No scratch-theme `kiconfinder6` probe was
run at planning time: on this machine steering the probe at the
scratch-installed theme has not been reproducible (see the offline
wiki-archive entry's probe note), and the static evidence above pins
the gap — today a `.snap` file shows Breeze's snap art, not this
theme's own. No reference screenshot shows a Snap package item icon,
so no reference pixels are used and the drawing is this theme's own
choice.

**Approach.**

- Add `mimetypes/application-vnd.snap.svg` under `16x16`, `22x22` and
  `32x32` of `theme/icons/org.macos8.desktop/`. `index.theme`
  already declares the three MimeTypes directories. Give each file the
  XML declaration, the comment `<!-- PLACEHOLDER: original Snap
  package illustration pending user-approved artwork. -->`, a short
  comment saying it is our own drawing in the Platinum palette, not
  traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art shares the generic document's page
  (the page outline, white page and folded-corner flap matching the
  `application-json.svg` pin's first three elements) and holds a
  strapped crate — a closed box with a black lid seam and one vertical
  black strap down the middle, a sealed-package mark distinct from the
  Squashfs disc-stack's white tapering bands, the Android package's
  zipper band, the ISO disc's capital-I and hub rings, the QCOW disc's
  white Q, the JSON document's curly braces, the shell script's `>_`
  prompt, the certificate's seal-and-ribbons, the PGP key's
  silhouette, the NZB index's dot-and-bars groups and the crash core's
  square ring:
  - 32x32: the three shared page elements; then the crate — `rect
    x="10" y="12" width="12" height="11" fill="#000000"` (frame),
    `rect x="11" y="13" width="10" height="9" fill="#DDDDDD"` (face),
    `rect x="10" y="16" width="12" height="1" fill="#000000"` (lid
    seam) and `rect x="15" y="12" width="2" height="11"
    fill="#000000"` (strap), drawn in that order so the seam and strap
    read on top of the face. Every element sits inside the white page
    and clears the folded corner.
  - 22x22: the three shared page elements; then the crate — `rect
    x="7" y="8" width="8" height="8" fill="#000000"` (frame), `rect
    x="8" y="9" width="6" height="6" fill="#DDDDDD"` (face), `rect
    x="7" y="11" width="8" height="1" fill="#000000"` (lid seam) and
    `rect x="10" y="8" width="2" height="8" fill="#000000"` (strap),
    drawn in that order. Every element sits inside the white page and
    clears the folded corner.
  - 16x16: the three shared page elements; then the crate — `rect
    x="5" y="6" width="6" height="5" fill="#000000"` (frame), `rect
    x="6" y="7" width="4" height="3" fill="#DDDDDD"` (face), `rect
    x="5" y="8" width="6" height="1" fill="#000000"` (lid seam) and
    `rect x="7" y="6" width="2" height="5" fill="#000000"` (strap),
    drawn in that order. Every element sits inside the white page and
    clears the folded corner (the flap reaches `y="5"` at `x="9"`).

  Validate by XML only, never by rasterizing: `convert`'s MSVG reader
  bleeds 1px shapes, so the pins below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside the Squashfs rows,
  described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths beside
  the other `mimetypes` paths in `SHIPPED_ICONS`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in `PINS` from the lists above (the three shared page elements in
  document order, then the frame, face, lid seam and strap).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `application-vnd.snap` in the last cell, as the
  `application-vnd.squashfs` sentence there does.
- `docs/installing.md`: add the Snap package icon to the sentence
  listing the icon theme's placeholder illustrations and their sizes
  (the one naming the `application-vnd.squashfs` files).
- The queued mimetype-icon entries ahead of this one (the gettext
  catalog, the PKIX certificate revocation list and the offline wiki
  archive) edit the same inventory block, `PINS` registry, invariants
  row and installing.md sentence; this entry sits behind them in the
  queue, so rebase on whatever they have landed when picking this up,
  keeping one row per icon.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size (the three shared page
  elements matching the `application-json.svg` pin's first three
  elements, then the crate's frame, face, lid seam and strap), carries
  a placeholder marker and has a `PLACEHOLDERS.md` row; the existing
  inventory, palette, geometry and placeholder-register tests cover
  all three.
- Changing one crate element's position, size or fill, or the element
  order, in one file makes the geometry test fail; dropping a file
  while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The `#000000`, `#FFFFFF` and `#DDDDDD` fills stay inside
  `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- The crate mark shares no drawing element with the pinned
  `application-vnd.squashfs` disc-stack (no circles, no white bands),
  so the subclass sibling stays visually distinct.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme`
  puts the three files in the installed theme, and uninstalling
  removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme
  into a scratch `XDG_DATA_HOME`, use a scratch `HOME`,
  `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset
  `DISPLAY` and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `application-vnd.snap` resolves to the theme's 32x32
  `mimetypes/application-vnd.snap.svg` (at planning time the theme
  ships no such file, so the name fell through to Breeze's), and
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
