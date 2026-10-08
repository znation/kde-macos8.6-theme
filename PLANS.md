# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

## Done

### Mac OS 8.6 desktop theme package with the Platinum panel background (done 2026-10-07)

**Planned 2026-10-07 by plan.**

**Goal.** Ship the third installable artifact: a Plasma 6 desktop theme, `org.macos8.desktop`
(`KPackageStructure: "Plasma/Theme"`), whose `widgets/panel-background.svg` renders the Mac OS 8.6
Platinum menu bar, and wire it into the existing global theme so applying
`org.macos8.desktop` also selects it. This is the first widget-theme step toward pixel-perfect UI.

**Grounding.**
- Plasma desktop themes live at `$XDG_DATA_DIRS/plasma/desktoptheme/<KPlugin.Id>/`: a
  `metadata.json` plus `widgets/*.svg[z]`, optional `colors`, `plasmarc`, `opaque/`, `dialogs/`.
  The system references are `/usr/share/plasma/desktoptheme/default/` (43 `widgets/*.svgz`) and
  `/usr/share/plasma/desktoptheme/breeze-light/`, which ships **no `widgets/` at all** yet is an
  enabled, selectable theme — so Plasma renders missing widgets from the `default` theme and a
  partial theme is supported. `libPlasma.so.6` contains both the `.svgz` and `.svg` lookup
  strings, so an uncompressed, diffable `.svg` works. This plan therefore ships only
  `widgets/panel-background.svg`; every other widget keeps the Breeze default.
- The global theme selects a desktop theme through `contents/defaults`
  `[plasmarc][Theme] name=<id>` (Breeze uses `name=default`). Verified headless with a temp
  `XDG_DATA_HOME`: `plasma-apply-desktoptheme --list-themes` lists the package and
  `plasma-apply-desktoptheme org.macos8.desktop` exits 0 and writes `$XDG_CONFIG_HOME/plasmarc`
  `[Theme] name=org.macos8.desktop`; no session is needed.
- Palette sampled from `macos8.6-screenshots/desktop_betawiki.png` (top 20 rows at x=500) and
  `desktop_archiveorg8.6hd.png`: body `#DDDDDD`, top/left highlight `#FFFFFF`, bottom/right shadow
  `#999999`, bottom rule `#000000`. The body matches `theme/color-schemes/MacOS8.colors`
  (`[Colors:Button] BackgroundNormal=221,221,221`).
- Plasma's nine-slice contract: the SVG carries one element each with `id` `center`, `top`,
  `bottom`, `left`, `right`, `topleft`, `topright`, `bottomleft`, `bottomright`, plus magic-coloured
  hint rects `hint-tile-center`, `hint-{top,bottom,left,right}-margin` and
  `hint-{top,bottom,left,right}-inset`. A hint's value is the rect's height for top/bottom and its
  width for left/right (`zcat`
  `/usr/share/plasma/desktoptheme/default/widgets/panel-background.svgz` to see the encoding).
  `mask-*`/`shadow-*` only serve rounded corners and drop shadows; a square opaque bar omits them.

**Approach.**
1. A new package directory named `org.macos8.desktop` under `theme/desktop-themes/` (a new
   sibling of `look-and-feel`). Inside it, `metadata.json` (new) — `KPackageStructure`
   `"Plasma/Theme"`, `X-Plasma-API` `"5.0"` (the value `default` uses), and `KPlugin` with `Id`
   `org.macos8.desktop`, `Name` `Mac OS 8.6`, `Description`, `Version` `0.1.0`, `License`
   `GPL-2.0-or-later`, empty `Category`, one `Authors` entry.
2. In that package's `widgets/` subdirectory, `panel-background.svg` (new) — a tight 12x12
   canvas (no shadow space), 2px border, 8px centre tile: corners 2x2 at (0,0)/(10,0)/(0,10)/(10,10);
   `top` 8x2 at (2,0), `bottom` 8x2 at (2,10), `left` 2x8 at (0,2), `right` 2x8 at (10,2), `center`
   8x8 at (2,2). Fills: body `#DDDDDD`; outer 1px top/left `#FFFFFF`; outer 1px bottom/right
   `#999999`; an extra 1px `#000000` rule along the bottom outer edge; corners take the adjacent
   edge colour. Hint rects: `hint-tile-center` 8x8, each `hint-*-margin` 2x2, each `hint-*-inset`
   zero-height/width at its edge. Author the Platinum shapes; use the decompressed default SVG only
   as the element-ID/transform layout reference, not as artwork. No `class="ColorScheme-*"` hooks
   (the palette is fixed), no `mask-*`, `shadow-*`, `thick-*`, or `<script>`.
3. The look-and-feel package's `contents/defaults` (edit) — add a
   `[plasmarc][Theme]` section with `name=org.macos8.desktop` after the existing
   `[kdeglobals][General] ColorScheme=MacOS8`.
4. A `test_desktoptheme.py` (new) under `tests/` — stdlib `unittest`, `json`, `configparser`,
   `xml.etree.ElementTree`, `shutil`, `subprocess`, `tempfile`:
   - `TestMetadata`: `KPackageStructure == "Plasma/Theme"`, `KPlugin.Id == "org.macos8.desktop"`,
     `Name`, non-empty `Version`, `X-Plasma-API == "5.0"`.
   - `TestPanelBackground`: `ET.parse` the SVG, collect every `id`, assert the nine slice ids and
     all nine hint ids are present, assert the text contains `#FFFFFF`, `#DDDDDD`, `#999999`,
     `#000000`, and assert no element tag ends in `script`.
   - `TestDefaultsWiring`: parse the LNF `contents/defaults` (same `configparser` trick as
     `tests/test_lookandfeel.py`) and assert `[plasmarc][Theme] name` equals the desktop theme's
     `KPlugin.Id`.
   - `TestInstall`: run `make install DESTDIR=<tmp> XDG_DATA_HOME=/share`; assert
     `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/{metadata.json,widgets/panel-background.svg}`
     are byte-identical to source and a second run exits 0.
   - `TestApplyDesktopTheme` (`@unittest.skipUnless(shutil.which("plasma-apply-desktoptheme"), ...)`):
     install into a temp prefix, run `plasma-apply-desktoptheme --list-themes` with
     `XDG_DATA_HOME=<tmp>/share` and a fresh `XDG_CONFIG_HOME`, assert the output names
     `org.macos8.desktop`; run `plasma-apply-desktoptheme org.macos8.desktop`, assert exit 0 and
     `<tmp>/config/plasmarc` contains `[Theme] name=org.macos8.desktop`.
   - `TestPackageValid` (`@unittest.skipUnless(shutil.which("kpackagetool6"), ...)`):
     `kpackagetool6 -t Plasma/Theme -p <fresh tmp> -i` on the new package directory
     exits 0 and leaves `<fresh tmp>/org.macos8.desktop/metadata.json`.
5. `tests/test_lookandfeel.py` (edit) — `TestDefaults.test_only_the_color_scheme_key_is_set` now
   fails because the defaults carry a second section; rewrite it to assert both sections
   (`kdeglobals][General` with `ColorScheme`, `plasmarc][Theme` with `name`) and leave
   `test_color_scheme_matches_the_scheme_file` unchanged.
6. `Makefile` (edit) — add `DTHEME_ID := org.macos8.desktop`,
   `DTHEME_PACKAGE := theme/desktop-themes/$(DTHEME_ID)`,
   `DTHEME_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/desktoptheme`; extend `install` with
   `install -d`, `rm -rf $(DTHEME_INSTALL_DIR)/$(DTHEME_ID)`, `cp -r` (the same replace-not-merge
   rule as the look-and-feel package).
7. `README.md` (edit) — extend the `tumwater:status` block and the Installing section: the panel
   background now ships, `plasma-apply-desktoptheme org.macos8.desktop` selects it, and the global
   theme applies it via `[plasmarc][Theme]`.

**Files touched.** New: `metadata.json` and `panel-background.svg` (in the package's `widgets/`) in
the new `org.macos8.desktop` package under `theme/desktop-themes/`, plus `test_desktoptheme.py`
under `tests/`. Edited: the look-and-feel package's `contents/defaults`,
`tests/test_lookandfeel.py`, `Makefile`, `README.md`. No change to the color scheme.

**Acceptance criteria.**
- `make check` exits 0 with the new metadata, SVG-contract, defaults-wiring, install,
  `plasma-apply-desktoptheme`, and `kpackagetool6` tests passing (the last two skipped only when
  the tool is absent).
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/metadata.json` and
  `widgets/panel-background.svg` byte-identical to source, and a second `make install` still exits
  0.
- `plasma-apply-desktoptheme --list-themes` with `XDG_DATA_HOME` pointed at the installed tree
  lists `org.macos8.desktop`; applying it exits 0 and writes
  `plasmarc [Theme] name=org.macos8.desktop`.
- Manual smoke test (needs a Plasma session): a top panel renders `#DDDDDD` with a white top/left
  highlight and a `#999999`+black bottom edge, and every other widget still renders Breeze.

**Follow-ups (not planned here).** Further widget families (button, scrollbar, tooltip), the
Platinum window decoration, an 8.6 splash, and the automated render/capture step (BUGS.md
`## Open`) — the panel background gives the render harness its first real surface.
### Mac OS 8.6 look-and-feel global theme package (done 2026-10-07)

**Planned 2026-10-07 by plan.**

**Goal.** Ship the second installable artifact: a Plasma 6 `Plasma/LookAndFeel` global theme,
`org.macos8.desktop`, that applies the existing Platinum color scheme as one selectable global
theme and gives the later desktop-theme, window-decoration, and splash plans a package to plug
into.

**Grounding.**
- A `Plasma/LookAndFeel` package is `metadata.json` (`KPackageStructure`, `KPlugin.Id`) plus
  `contents/defaults`; the reference is `/usr/share/plasma/look-and-feel/org.kde.breeze.desktop/`.
  Packages live under `$XDG_DATA_DIRS/plasma/look-and-feel/<KPlugin.Id>/`, and `lookandfeeltool -l`
  lists them (verified with a temp `XDG_DATA_HOME`).
- `contents/defaults` is ini merged into the user's config. Breeze sets every surface
  (`widgetStyle`, `ColorScheme`, `Theme`, cursor, decoration, splash); this project only has a
  color scheme, so the defaults set only `[kdeglobals][General] ColorScheme` and leave the rest at
  the user's current values instead of silently resetting them to Breeze.
- The value must be `MacOS8`, the CLI-visible id: KDE's scheme resolver turns the config value
  into `<value>.colors`, and the file is `theme/color-schemes/MacOS8.colors` (renamed from the
  dotted `MacOS8.6.colors`; see the Fixed BUGS.md entry). Verified by running
  `plasma-apply-colorscheme` with no argument against a temp `XDG_CONFIG_HOME`:
  `ColorScheme=MacOS8` resolves, `ColorScheme=MacOS8.6` prints `Could not find color scheme
  "MacOS8.6" falling back to BreezeLight`.

**Approach.**
1. The package metadata manifest, `metadata.json` (new) — `KPackageStructure`
   `"Plasma/LookAndFeel"`; `KPlugin` with `Id` `org.macos8.desktop`, `Name` `Mac OS 8.6`,
   `Description`, `Version` `0.1.0`, `License` `GPL-2.0-or-later`, empty `Category`, and one
   `Authors` entry; `X-Plasma-APIVersion` `"2"`; `Keywords`
   `"Desktop;Workspace;Appearance;Look and Feel;"`.
2. `theme/look-and-feel/org.macos8.desktop/contents/defaults` (new) — exactly two lines,
   `[kdeglobals][General]` and `ColorScheme=MacOS8`. No other sections or keys.
3. A new `test_lookandfeel.py` module under `tests/` — stdlib `unittest`, `json`, `configparser`, `shutil`,
   `subprocess`, `tempfile`:
   - `TestMetadata`: `json.load` the metadata and assert `KPackageStructure`,
     `KPlugin.Id == "org.macos8.desktop"`, `KPlugin.Name == "Mac OS 8.6"`, `KPlugin.Version`,
     `X-Plasma-APIVersion == "2"`, and a non-empty `Keywords`.
   - `TestDefaults`: parse `contents/defaults` with
     `configparser.ConfigParser(interpolation=None)` and `optionxform = str` (the section key is
     `kdeglobals][General`); assert that is the only section and `ColorScheme` its only option;
     assert the value equals `theme/color-schemes/MacOS8.colors`'s `[General] ColorScheme` and
     that `theme/color-schemes/<value>.colors` exists (the cross-artifact invariant, which stays
     true if the scheme is later renamed).
   - `TestInstall`: run `make install DESTDIR=<tmp> XDG_DATA_HOME=/share`; assert
     `<tmp>/share/plasma/look-and-feel/org.macos8.desktop/metadata.json` and `contents/defaults`
     exist and are byte-identical to source, and that a second run exits 0.
   - `TestPackageValid` (`@unittest.skipUnless(shutil.which("kpackagetool6"), ...)`): run
     `kpackagetool6 -t Plasma/LookAndFeel -p <fresh tmp> -i theme/look-and-feel/$LNF_ID`
     and assert exit 0 with `<fresh tmp>/org.macos8.desktop/metadata.json` present.
4. `Makefile` — add `LNF_ID := org.macos8.desktop` and
   `LNF_PACKAGE := theme/look-and-feel/$LNF_ID`, and
   `LNF_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/look-and-feel`; extend `install` to
   `install -d $(LNF_INSTALL_DIR)` then `cp -r $(LNF_PACKAGE) $(LNF_INSTALL_DIR)/`. Plain copy, not
   `kpackagetool6 -i`, because `-i` exits 4 when the target already exists and `-u` does not honour
   `--packageroot` (both verified); the copy is idempotent.
5. `README.md` — update the `tumwater:status` block and the Installing section to describe the
   global theme and `lookandfeeltool -a org.macos8.desktop`.

**Files touched.** New files under `theme/look-and-feel`: `metadata.json` and `contents/defaults`;
a new `test_lookandfeel.py` under `tests/`; `Makefile` and `README.md` edited. No change to the
color scheme itself.

**Acceptance criteria.**
- `make check` exits 0; the metadata, defaults/cross-artifact, install, and (on this host)
  kpackagetool6-validity tests pass.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/look-and-feel/org.macos8.desktop/metadata.json` and `contents/defaults`
  byte-identical to source, and a second `make install` still exits 0.
- Manual smoke test (needs a Plasma session, so outside `make check`): with the package under
  `~/.local/share/plasma/look-and-feel/`, `lookandfeeltool -l` lists `org.macos8.desktop`, and
  `lookandfeeltool -a org.macos8.desktop` exits 0 and leaves `kdeglobals [General]
  ColorScheme=MacOS8`, which `plasma-apply-colorscheme` resolves without the "Could not find"
  warning.

**Follow-ups (not planned here).** Desktop-theme widget SVGs, the Platinum window decoration, and
an 8.6 splash (`contents/splash/`) — each adds its own key to this package's `contents/defaults`.

**Implementation note (2026-10-07).** Landed as planned: `metadata.json` (top-level
`KPackageStructure`, `Keywords`, `X-Plasma-APIVersion`; `KPlugin` with `Id`, `Name`,
`Description`, `Version`, `License`, empty `Category`, one author), the two-line
`contents/defaults`, `tests/test_lookandfeel.py`, and the `Makefile` install step. Verified beyond
`make check`: `kpackagetool6 -t Plasma/LookAndFeel -p <tmp> -i` exits 0; with the package
installed under a temp `XDG_DATA_HOME`, `lookandfeeltool -l` lists `org.macos8.desktop` and
`lookandfeeltool -a org.macos8.desktop` exits 0. Headless, the apply wrote the scheme's colour
sections into `kdeglobals` and `[General] ColorScheme=MacOS8` into `kdedefaults/kdeglobals` (KDE's
defaults layer), not the main `kdeglobals`; the in-session restart check still needs a Plasma
session.

### Mac OS 8.6 Platinum color scheme and project check harness (done 2026-10-07)
**Planned 2026-10-07 by plan.**

**Goal.** Ship the project's first artifact — a Plasma 6 color scheme encoding the Mac OS 8.6
"Platinum" palette sampled from the reference screenshots — together with the project's first
`make check` harness that validates the scheme and exercises its install path.

**Evidence.** Palette anchors were sampled with ImageMagick from the retail reference set and are
recorded as assertions in the test: `desktop_archiveorg8.6hd.png` (menu bar and window face
`221,221,221`; view `255,255,255`; chrome `0,0,0`; desktop `100,98,160`), `desktop_fandom.png`
(`192,192,192`, `136,136,136`, `85,85,85`), `opendialog_macrumors86.jpg` (list selection
`206,206,255`).

**Palette tokens (RGB).** `platinum`=221,221,221 · `white`=255,255,255 · `black`=0,0,0 ·
`alternate`=238,238,238 · `shadow`=136,136,136 · `silver`=192,192,192 · `selection`=206,206,255 ·
`tooltip`=255,255,204. KDE requires semantic roles with no Mac OS 8.6 counterpart; use
`link`=0,0,238 · `negative`=204,0,0 · `positive`=0,128,0 · `neutral`=204,102,0 ·
`visited`=85,26,139.

**Approach.**

1. `theme/color-schemes/MacOS8.colors` (new) — an ini color scheme using the same key set as
   `/usr/share/color-schemes/BreezeLight.colors`, with sections `[ColorEffects:Disabled]`,
   `[ColorEffects:Inactive]`, `[Colors:Button]`, `[Colors:Complementary]`, `[Colors:Header]`,
   `[Colors:Header][Inactive]`, `[Colors:Selection]`, `[Colors:Tooltip]`, `[Colors:View]`,
   `[Colors:Window]`, `[General]`, `[KDE]`, `[WM]`. Every `[Colors:*]` section carries
   `BackgroundAlternate`, `BackgroundNormal`, `DecorationFocus`, `DecorationHover`,
   `ForegroundActive`, `ForegroundInactive`, `ForegroundLink`, `ForegroundNegative`,
   `ForegroundNeutral`, `ForegroundNormal`, `ForegroundPositive`, `ForegroundVisited`.
   Mapping: Window/Button/Header/Header][Inactive/Complementary get
   `BackgroundNormal=BackgroundAlternate=platinum`, `ForegroundNormal=ForegroundActive=black`,
   `ForegroundInactive=shadow`, `DecorationFocus=DecorationHover=black`; View gets
   `BackgroundNormal=white`, `BackgroundAlternate=alternate`, the rest as Window; Selection gets
   `BackgroundNormal=BackgroundAlternate=selection` and the Window foregrounds; Tooltip gets
   `BackgroundNormal=tooltip`, `ForegroundNormal=black`, the rest as Window; semantic roles map to
   the tokens above. `[WM]` gets `activeBackground=activeBlend=platinum`,
   `activeForeground=black`, `inactiveBackground=inactiveBlend=platinum`,
   `inactiveForeground=shadow`. `[General]` gets `ColorScheme=MacOS8`, `Name=Mac OS 8.6`,
   `shadeSortColumn=true`; `[KDE]` gets `contrast=4`; the `ColorEffects` sections copy
   BreezeLight with `Color=136,136,136` (Disabled) and `Color=136,136,136` (Inactive).
2. `tests/test_colorscheme.py` (new) — stdlib `unittest` + `configparser` (`interpolation=None`).
   Asserts the file parses; every section and key above exists; every `[Colors:*]` value matches
   `^\d{1,3},\d{1,3},\d{1,3}$` with components 0–255; and the sampled anchors hold
   (`Window`/`Button`/`Header` `BackgroundNormal == 221,221,221`, `View BackgroundNormal ==
   255,255,255`, `Selection BackgroundNormal == 206,206,255`, `Tooltip BackgroundNormal ==
   255,255,204`, `Window ForegroundNormal == 0,0,0`). A `TestInstall` case runs
   `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` in a subprocess and asserts
   `<tmp>/share/color-schemes/MacOS8.colors` is byte-identical to the source.
3. `Makefile` (new) — `check` runs `$(PYTHON) -m unittest discover -s tests -v`; `install` runs
   `install -Dm644 theme/color-schemes/MacOS8.colors
   $(DESTDIR)$(XDG_DATA_HOME)/color-schemes/MacOS8.colors`, with
   `XDG_DATA_HOME ?= $(HOME)/.local/share`.

**Files touched.** `theme/color-schemes/MacOS8.colors`, `tests/test_colorscheme.py`, `Makefile`
— all new; no existing file changes.

**Acceptance criteria.**
- `make check` exits 0 and the run reports the color-scheme structure, anchor, and install tests
  passing.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/color-schemes/MacOS8.colors` byte-identical to the source file.
- Manual smoke test (needs a Plasma session, so outside `make check`): with the file copied to
  `~/.local/share/color-schemes/`, `plasma-apply-colorscheme --list-schemes` lists `MacOS8`, and
  `plasma-apply-colorscheme MacOS8` exits 0 with window/button faces `#DDDDDD` and view
  backgrounds `#FFFFFF`.

**Implementation note (2026-10-07).** `plasma-apply-colorscheme` derives a scheme's ID from the
part of its filename before the first dot, so the originally planned `MacOS8.6.colors` was listed
and selectable as `MacOS8`, not `MacOS8.6` (verified by running the tool against a temp
`XDG_DATA_HOME` holding copies named `MacOS8.6.colors`, `MacOS86.colors`, and `Platinum.colors`:
it printed `MacOS8`, `MacOS86`, and `Platinum`). That mismatch made the applied id fail to
resolve on restart, so the scheme was later renamed to `MacOS8.colors` with `ColorScheme=MacOS8`
(see the Fixed BUGS.md entry); `Name` still reads "Mac OS 8.6".

**Follow-ups (not planned here).** Wrap the scheme in a `look-and-feel` global-theme package,
then build the Plasma desktop-theme widget SVGs and the Platinum window decoration.

