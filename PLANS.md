# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Ground the Kvantum tab face in the reference's System Profiler tabs (planned 2026-10-19 by the plan role)

**Goal.** The Kvantum `[Tab]` element (`frame.element=tab`, `interior.element=tab` in
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`) paints every state as a raised
`#DDDDDD` face with a `#FFFFFF` top/left highlight: the `tab-normal-*`, `tab-focused-*` and
`tab-toggled-*` groups in `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`. The retail
reference `macos8.6-screenshots/systemprofiler_betawiki.png` shows two Platinum tab palettes: an
unselected tab is a `#CCCCCC` face with a `#DDDDDD` highlight, and the selected tab is an
`#EEEEEE` face with a `#FFFFFF` highlight. `tests/test_kvantum_bevel_pixels.py` currently pins all
three tab states to the button's `#DDDDDD`/`#FFFFFF` palette, so the wrong art passes. Correct the
art and that test, and add a reference test that re-derives both palettes from the screenshot.

**Grounding.** `systemprofiler_betawiki.png` is the retail Japanese 8.6 System Profiler the
`README` names as window-chrome ground truth. Its tab row runs y=54..70: the first tab
"システム情報" is selected, the others unselected. Sampled with `tools/sample.py`:
- unselected "環境とボリューム" at x=450: y=54 `#000000` outline, y=55 `#CCCCCC`, y=56 `#DDDDDD`
  highlight, y=57 and y=60 `#CCCCCC` face; y=70 `#000000` bottom outline. The "コントロールパネル"
  tab repeats it (x=700).
- selected "システム情報" at x=260: y=54 `#000000`, y=55 `#CCCCCC`, y=56 `#FFFFFF` highlight, y=57
  and y=60 `#EEEEEE` face; y=66..72 `#EEEEEE` (open bottom edge, no outline).
Kvantum draws an unselected tab through `tab-normal`/`tab-focused` and the selected tab through
`tab-toggled` (the same on/selected `toggled` state the button and slider use).

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: in every `tab-normal-*` and
  `tab-focused-*` group change the face fill `#DDDDDD` to `#CCCCCC` and the raised top/left
  highlight `#FFFFFF` to `#DDDDDD`; in every `tab-toggled-*` group change the face fill `#DDDDDD`
  to `#EEEEEE` and keep the `#FFFFFF` highlight. Keep the `#999999` shadow and the `#000000`
  outline in all three.
- `tests/test_kvantum_bevel_pixels.py`: add `SURFACE_HIGHLIGHT = "#FFFFFF"`, `TAB_FACE =
  "#CCCCCC"`, `TAB_HIGHLIGHT = "#DDDDDD"` and `TAB_SELECTED_FACE = "#EEEEEE"`; give
  `_button_edge_maps` and `_button_corners` a `highlight` parameter (default `SURFACE_HIGHLIGHT`)
  instead of the hard-coded `#FFFFFF`; set `SURFACE_STATES["tab"]` to `{"normal": ("raised",
  TAB_FACE), "focused": ("raised", TAB_FACE), "toggled": ("raised", TAB_SELECTED_FACE)}` and
  have `TestSurfaceBevelPixels` pass `TAB_HIGHLIGHT` for the tab's normal/focused states and
  `SURFACE_HIGHLIGHT` for every other state.
- Add `tests/test_kvantum_tab_reference.py`: a `ReferenceScreenshotMixin` class with `REFERENCE`
  and `MAX_ROWS` from `support.aurorae_fixtures` (`PROFILER_REFERENCE`, `PROFILER_ROWS`, so the
  decode is shared with the Aurorae readers). It samples the two tabs above, asserts the sampled
  pixels are `#000000`/`#CCCCCC`/`#DDDDDD`/`#CCCCCC` (unselected) and
  `#000000`/`#CCCCCC`/`#FFFFFF`/`#EEEEEE` (selected), and asserts the shipped `tab-normal`,
  `tab-focused` and `tab-toggled` centre tiles and raised top/left bands paint those palettes.
- `docs/invariants.md`: add a kvantum row naming
  `tests/test_kvantum_tab_reference.py::TestTabReference` and its guarantee.

**Acceptance criteria.**
- `tab-normal` and `tab-focused` centres are `#CCCCCC` and their raised top/left band is
  `#DDDDDD`; `tab-toggled` centre is `#EEEEEE` and its raised top/left band is `#FFFFFF`; all three
  keep the `#000000` outline and `#999999` shadow.
  `TestSurfaceBevelPixels.test_every_surface_state_paints_its_bevel` passes.
- The new reference test re-derives the unselected `#CCCCCC`/`#DDDDDD` and the selected
  `#EEEEEE`/`#FFFFFF` from `systemprofiler_betawiki.png` and passes; a tab left `#DDDDDD` fails
  it. It skips, not fails, when the reference is not materialized.
- `make check` exits 0.

**Recorded deviation.** The reference tab's top/left bevel is three bands -- the `#000000`
outline, a `#CCCCCC` mid-tone, then the `#DDDDDD`/`#FFFFFF` highlight, because the highlight is
inset one pixel. The Kvantum tab keeps its existing two-band outline+highlight geometry (the
same 2px bevel the button and line edit use), so this plan corrects the palette only; the
selected tab's open bottom edge is likewise not reproduced.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`tests/test_kvantum_bevel_pixels.py`, `tests/test_kvantum_tab_reference.py`,
`docs/invariants.md`.

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-19 by the clean role):** The initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-four widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's; `PLACEHOLDERS.md` is empty);
and the render and fidelity tooling
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


## Done
