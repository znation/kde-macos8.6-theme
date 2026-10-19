# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-18 by the clean role):** The initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-three widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document and
Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic`, our own mark rather than
Apple's; `PLACEHOLDERS.md` is empty); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces the theme does not ship are each tracked here (updated 2026-10-18 by the plan
role): a **Qt widget style** for KDE applications (the desktop theme styles only Plasma shell
widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** is out of scope (no reference screenshot shows a
cursor, so no pixel ground truth exists to match); and **system sounds** are out of scope (not a
visual surface, so the reference set cannot ground them). The shipped work should not be treated
as the whole of the prompt.

### Ground the Aurorae inactive frame in the reference's inactive windows (planned 2026-10-19 by the plan role)

**Goal.** The `decoration-inactive` nine-slice and its header comment claim "the reference set has
no inactive window" and therefore paint KDE-required greys: the active tile's
`#FFFFFF`/`#777777` pinstripes and `#CCCCCC` field flattened to `#CCCCCC`, keeping the `#000000`
outlines and the `#999999` shadow. The reference set does show inactive windows:
`macos8.6-screenshots/desktop_fandom.png` (retail 8.6, the image the tabbar and progressbar
already sample) shows four unfocused windows (the "Mac OS 8.6", "Utilities", "Applications" and
"Apple System Profiler" windows), and the lossless beta `macos8.6-screenshots/
systeminfo_betawiki.png` shows a fifth behind the active "System Info" window. Their frame is a
1px `#555555` outline around a flat `#DDDDDD` field, with no pinstripes, no white highlight and
no `#999999` shadow (verified with `tools/sample.py`; the scheme's own
`[WM] inactiveBackground=221,221,221` agrees). Correct the art and the provenance, and pin the
inactive frame to the reference pixels.

**Approach.**
- `theme/aurorae/themes/org.macos8.desktop/decoration.svg`: rewrite every `decoration-inactive-*`
  tile to the reference's flat inactive frame — a 1px `#555555` outline on the outer edge (the
  top row of `decoration-inactive-top`, the outer column/row of the side and bottom tiles, and
  the outer corner pixels) and `#DDDDDD` everywhere inside; drop the `#000000` outlines, the
  `#999999` shadow and the `#CCCCCC` highlight/field. Keep the active geometry (18x34 canvas, 6px
  side/bottom border, 22px top border, 6x6 centre). Recompress `decoration.svgz` (`gzip -9 -n`)
  so `test_svgz_is_the_compressed_svg` still passes.
- Reword the `decoration.svg` header comment: name `desktop_fandom.png` (2 image px per logical
  px) as the inactive anchor and `systeminfo_betawiki.png` as lossless corroboration, state the
  flat `#DDDDDD` field with the 1px `#555555` outline, and delete the "the reference set has no
  inactive window" clause.
- `tests/support/aurorae_fixtures.py`: add `INACTIVE_REFERENCE` (`desktop_fandom.png`, with a row
  bound covering y=900), `INACTIVE_FRAME_GREY = "#DDDDDD"` and `INACTIVE_OUTLINE = "#555555"`;
  keep `INACTIVE_GREY = "#CCCCCC"` for the button boxes. Load `INACTIVE_REFERENCE` in
  `ReferenceImageCase.setUpClass` (skip when unmaterialized, like `REFERENCE`) and add an
  `inactive_pixel(x, y)` accessor.
- `tests/test_aurorae_frame.py`: replace `_assert_flattened_inactive_tile` and its callers with
  reference-derived checks; add `TestDecorationSvg.test_inactive_frame_matches_reference`, which
  asserts the rendered `decoration-inactive-*` slices contain no `#FFFFFF`, `#777777`, `#999999`
  or `#CCCCCC` pixel and that the field is `#DDDDDD` and the outer edge `#555555`, cross-checked
  against `inactive_pixel(300, 75)`, `(1000, 130)`, `(1500, 80)`, `(300, 880)` (`#DDDDDD`) and
  `(300, 56)`, `(24, 75)` (`#555555`). Reword the module docstring and
  `test_inactive_top_tile_is_flat_grey` so they name the reference instead of claiming none
  exists.
- `theme/aurorae/themes/org.macos8.desktop/close.svg`, `maximize.svg`, `restore.svg`, `shade.svg`
  and `tests/test_aurorae_buttons.py`: replace each "the reference set has no inactive window"
  clause with the accurate one — the reference's inactive windows draw no close/collapse boxes in
  their title bars, so the greyed inactive box stays KDE-required. No art change; `INACTIVE_GREY`
  and the button tests are unchanged.
- `macos8.6-screenshots/sources.txt`: extend the `desktop_fandom.png` note to record that it
  grounds the inactive window frame (the flat `#DDDDDD` title bar and 1px `#555555` outline of its
  four unfocused windows).
- `docs/invariants.md`: update the aurorae frame row to name the inactive reference, and the
  title-bar-box row so its inactive grey is recorded as KDE-required rather than re-derived.

**Files touched.** `theme/aurorae/themes/org.macos8.desktop/decoration.svg` (+ `.svgz`),
`theme/aurorae/themes/org.macos8.desktop/close.svg`, `maximize.svg`, `restore.svg`, `shade.svg`,
`tests/support/aurorae_fixtures.py`, `tests/test_aurorae_frame.py`,
`tests/test_aurorae_buttons.py`, `macos8.6-screenshots/sources.txt`, `docs/invariants.md`.

**Acceptance criteria.**
- The `decoration-inactive-*` tiles paint only `#DDDDDD` and `#555555`, with `#555555` on the
  outer edge; no `#FFFFFF`, `#777777`, `#999999` or `#CCCCCC` pixel remains in them.
- `python3 tools/sample.py macos8.6-screenshots/desktop_fandom.png 300 75` (and `1000 130`,
  `1500 80`, `300 880`) prints `221,221,221 #DDDDDD`; `... 300 56` and `... 24 75` print
  `85,85,85 #555555`.
- `TestDecorationSvg.test_inactive_frame_matches_reference` passes when `desktop_fandom.png` is
  materialized and skips (not fails) when it is not, through the `skip_unless_materialized` path.
- No Aurorae SVG header or Aurorae test docstring still claims the reference set has no inactive
  window.
- `decoration.svgz` decompresses to the edited `decoration.svg`.
- `make check` is green.

### Ship the Platinum menu submenu arrow (`go-next-symbolic`) grounded in the open Apple menu (planned 2026-10-19 by the plan role)

**Goal.** KDE draws a menu's submenu indicator as a `Kirigami.Icon` with
`source: "go-next-symbolic"` — `PlasmaComponents` `MenuItem.qml`'s `arrow` and the kicker's
`ItemListDelegate.qml` both name that icon — and the icon theme declares `Inherits=breeze`, so
the indicator is Breeze's thin chevron. The reference's open Apple menu
(`macos8.6-screenshots/desktop_archiveorg8.6hd.png`, retail 8.6, already the anchor for the menu
body and the view item) draws a solid black right triangle on each submenu row: at the
"Automated Tasks" row the dark pixels (every channel < #AA) are a 5x9 right triangle with a
full-height left edge, bounding box x=151..155, y=91..99, and the triangle is pure `#000000` at
(152, 93). Ship that triangle as the theme's `go-next-symbolic` so the submenu indicator matches
the reference instead of falling back to Breeze's chevron.

**Approach.**
- Add `theme/icons/org.macos8.desktop/16x16/actions/go-next-symbolic.svg` (16x16) and
  `theme/icons/org.macos8.desktop/22x22/actions/go-next-symbolic.svg` (22x22), each a single
  solid `#000000` right-triangle path — 16x16 `M 6,3 L 6,11 L 10,7 Z` (a 5x9 triangle whose left
  edge is full-height and whose tip is at the vertical middle), the 22x22 path the same shape at
  the 22/16 scale — with a header comment naming the `desktop_archiveorg8.6hd.png` anchor and
  recording that the 16px canvas is KDE-required (the reference menu row is ~17px). Draw the
  triangle alone: the reference's 1px lighter left edge (x=150 is #E8E8E8 against the #DDDDDD
  body) is a bevel a `-symbolic` icon cannot keep, because KDE recolours the icon to the menu
  text colour.
- `theme/icons/org.macos8.desktop/index.theme`: add `16x16/actions` and `22x22/actions` to
  `Directories` and add the matching `[16x16/actions]` / `[22x22/actions]` sections (`Size=16`
  and `22`, `Context=Actions`, `Type=Fixed`), so a 16px or 22px lookup resolves to the theme's
  triangle before Breeze's chevron.
- `tests/test_icon_theme.py`: add both icons to `SHIPPED_ICONS` and to `ICON_SHAPES` (one
  `path` element with its `d` and `fill`); `INSTALLED_FILES` derives from `SHIPPED_ICONS`.
- New `tests/test_icon_arrow_reference.py`: a `ReferenceScreenshotMixin` case over
  `desktop_archiveorg8.6hd.png` that re-derives the "Automated Tasks" submenu triangle — the
  dark pixels (every channel < 170) in x=146..159, y=86..104 — asserts it is a right triangle
  (its left column spans the full 9-row height, its widest row is the vertical middle) with a
  5x9 bounding box, and asserts the shipped 16x16 path's bounding box is the same 5x9; it skips
  when the reference is not materialized.
- `docs/invariants.md`: add an icons row naming the new test.
- `README.md`: extend the icon-theme sentence to name the menu submenu arrow alongside the
  kicker logo.

**Files touched.** `theme/icons/org.macos8.desktop/16x16/actions/go-next-symbolic.svg` (new),
`theme/icons/org.macos8.desktop/22x22/actions/go-next-symbolic.svg` (new),
`theme/icons/org.macos8.desktop/index.theme`, `tests/test_icon_theme.py`,
`tests/test_icon_arrow_reference.py` (new), `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- Both icons ship, are square SVGs of their declared size (16x16, 22x22), and each one's only
  drawing element is a solid `#000000` right-triangle `path`; `TestIcons` and `TestIconGeometry`
  pass.
- `index.theme` declares both `actions` directories, so
  `test_every_shipped_icon_lives_in_a_declared_size_directory` passes.
- The new reference test re-derives the 5x9 right triangle from `desktop_archiveorg8.6hd.png`
  (`python3 tools/sample.py macos8.6-screenshots/desktop_archiveorg8.6hd.png 152 93` prints
  `0,0,0 #000000`) and passes; it skips (not fails) when the reference is not materialized.
- `make check` is green.

Recorded scope: the RTL names (`go-next-rtl-symbolic`, `go-next-symbolic-rtl`) are not shipped;
the theme targets the reference's LTR English UI, so a right-to-left layout keeps Breeze's
chevron.

## Done
