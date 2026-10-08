# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

## Done

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

1. `theme/color-schemes/MacOS8.6.colors` (new) — an ini color scheme using the same key set as
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
   `inactiveForeground=shadow`. `[General]` gets `ColorScheme=MacOS8.6`, `Name=Mac OS 8.6`,
   `shadeSortColumn=true`; `[KDE]` gets `contrast=4`; the `ColorEffects` sections copy
   BreezeLight with `Color=136,136,136` (Disabled) and `Color=136,136,136` (Inactive).
2. `tests/test_colorscheme.py` (new) — stdlib `unittest` + `configparser` (`interpolation=None`).
   Asserts the file parses; every section and key above exists; every `[Colors:*]` value matches
   `^\d{1,3},\d{1,3},\d{1,3}$` with components 0–255; and the sampled anchors hold
   (`Window`/`Button`/`Header` `BackgroundNormal == 221,221,221`, `View BackgroundNormal ==
   255,255,255`, `Selection BackgroundNormal == 206,206,255`, `Tooltip BackgroundNormal ==
   255,255,204`, `Window ForegroundNormal == 0,0,0`). A `TestInstall` case runs
   `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` in a subprocess and asserts
   `<tmp>/share/color-schemes/MacOS8.6.colors` is byte-identical to the source.
3. `Makefile` (new) — `check` runs `$(PYTHON) -m unittest discover -s tests -v`; `install` runs
   `install -Dm644 theme/color-schemes/MacOS8.6.colors
   $(DESTDIR)$(XDG_DATA_HOME)/color-schemes/MacOS8.6.colors`, with
   `XDG_DATA_HOME ?= $(HOME)/.local/share`.

**Files touched.** `theme/color-schemes/MacOS8.6.colors`, `tests/test_colorscheme.py`, `Makefile`
— all new; no existing file changes.

**Acceptance criteria.**
- `make check` exits 0 and the run reports the color-scheme structure, anchor, and install tests
  passing.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/color-schemes/MacOS8.6.colors` byte-identical to the source file.
- Manual smoke test (needs a Plasma session, so outside `make check`): with the file copied to
  `~/.local/share/color-schemes/`, `plasma-apply-colorscheme --list-schemes` lists `MacOS8`, and
  `plasma-apply-colorscheme MacOS8` exits 0 with window/button faces `#DDDDDD` and view
  backgrounds `#FFFFFF`.

**Implementation note (2026-10-07).** `plasma-apply-colorscheme` derives a scheme's ID from the
part of its filename before the first dot, so `MacOS8.6.colors` is listed and selectable as
`MacOS8`, not `MacOS8.6` (verified by running the tool against a temp `XDG_DATA_HOME` holding
copies named `MacOS8.6.colors`, `MacOS86.colors`, and `Platinum.colors`: it printed `MacOS8`,
`MacOS86`, and `Platinum`). The filename is kept as planned so the install path and the
`[General] ColorScheme`/`Name` keys still read "Mac OS 8.6"; the smoke test uses the ID KDE
actually exposes.

**Follow-ups (not planned here).** Wrap the scheme in a `look-and-feel` global-theme package,
then build the Plasma desktop-theme widget SVGs and the Platinum window decoration.

