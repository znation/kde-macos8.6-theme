# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

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


### Correct the desktop theme tabbar to the reference's selected System Profiler tab (planned 2026-10-19 by the plan role)

**Goal.** `theme/desktoptheme/org.macos8.desktop/widgets/tabbar.svg` paints every
`*-active-tab` face `#CCCCCC` with a `#DDDDDD` highlight, grounded on the
`desktop_fandom.png` System Profiler tabs -- but that window is inactive and its tabs are
unselected. Plasma 6 requests only the `*-active-tab` ids: `TabButton.qml` uses prefix
`north-active-tab`/`south-active-tab` for every tab and varies only `enabledBorders` by
`checked`, `TabBar.qml` draws that art as the highlight behind the current item, and the
kickoff footer, the system-tray current-item highlight and the panel popups use the same
`*-active-tab` ids. The art is therefore the *selected* tab. The lossless retail
`macos8.6-screenshots/systemprofiler_betawiki.png` shows the selected tab's top and left edge
as three bands -- `#000000` outline, `#CCCCCC` mid-tone, `#FFFFFF` highlight -- over an
`#EEEEEE` face, with an open (face-only) bottom. The shipped 3px nine-slice border has exactly
three rows/columns, so it can paint all three bands; the current art paints only two
(`outline`, `#DDDDDD`) and drops the mid-tone, and its face is the unselected grey.

**Grounding.** At the selected tab's column `x=260` (the first tab, "システム情報"),
`tools/sample.py` reads `y=54 #000000`, `y=55 #CCCCCC`, `y=56 #FFFFFF`, `y=57 #EEEEEE`, and
the open bottom `y=72 #EEEEEE`. Its left edge at `y=60` reads `x=225 #000000`, `x=226 #CCCCCC`,
`x=227 #FFFFFF`, `x=228 #EEEEEE`. The unselected tab at `x=450` reads `y=54 #000000`,
`y=55 #CCCCCC`, `y=56 #DDDDDD`, `y=57 #CCCCCC`, `y=70 #000000`, which is what the current art
matches.

**Approach.**
- `theme/desktoptheme/org.macos8.desktop/widgets/tabbar.svg`: in all four `*-active-tab`
  prefixes change the face fill `#CCCCCC` to `#EEEEEE` (centres, open-edge slices and the base
  rect of every closed-edge slice), and change the closed top/left band from `#000000`,
  `#DDDDDD`, face to `#000000`, `#CCCCCC`, `#FFFFFF` (the third row/column becomes the
  highlight). Keep the closed bottom/right band `face, #999999, #000000` and the face-only open
  edge. Update the header comment to name `systemprofiler_betawiki.png` and the selected tab,
  and drop the `desktop_fandom.png` provenance.
- `tests/test_desktoptheme_tabbar.py`: set `FACE = "#EEEEEE"`, add `MIDTONE = "#CCCCCC"` and
  `HIGHLIGHT = "#FFFFFF"`; set `TOP_LEFT_BAND = ("#000000", MIDTONE, HIGHLIGHT)`, keep
  `BOTTOM_RIGHT_BAND = (FACE, "#999999", "#000000")`, and `FLAT_BAND = (FACE,) * 3`. Rewrite
  `raised_tab_corners` for the three-band top/left bevel: `topleft` is
  `("#000000",) * 3 + ("#000000", MIDTONE, MIDTONE) + ("#000000", MIDTONE, HIGHLIGHT)`,
  `topright` is `("#000000",) * 3 + (MIDTONE, "#999999", "#000000") + (HIGHLIGHT, "#999999",
  "#000000")`, `bottomleft` is `("#000000", MIDTONE, HIGHLIGHT) + ("#000000", MIDTONE,
  "#999999") + ("#000000",) * 3`, and `bottomright` is `(FACE, "#999999", "#000000") +
  ("#999999", "#999999", "#000000") + ("#000000",) * 3`. The `tab_corners` mixed tables build
  from `EDGE_BANDS` and adapt to the new bands unchanged. Update `test_tabbar_palette` and
  `test_tabbar_colours`'s expected set to `{#000000, #CCCCCC, #EEEEEE, #FFFFFF, #999999}`.
- Replace `TestTabBarReference`'s `desktop_fandom.png` face rectangles with the selected tab's
  anchors: assert `self.pixel(260, y)` is `#000000`, `#CCCCCC`, `#FFFFFF`, `#EEEEEE` for
  `y = 54, 55, 56, 57`, `#EEEEEE` at `y = 72`, and at `y = 60` assert `self.pixel(x, 60)` is
  `#000000`, `#CCCCCC`, `#FFFFFF`, `#EEEEEE` for `x = 225, 226, 227, 228` (compare each against
  the module constants `MIDTONE`, `HIGHLIGHT`, `FACE` so the art and the reference stay tied).
  Import `PROFILER_REFERENCE`/`PROFILER_ROWS` from `support.aurorae_fixtures` instead of
  `FANDOM_REFERENCE`/`FANDOM_MAX_ROWS` from `support.desktoptheme_paths`.
- `tests/support/desktoptheme_paths.py`: the `FANDOM_MAX_ROWS` comment lists "the dialog,
  fill-gradient and tab-bar anchors" as its readers; drop the tab-bar entry now that
  `test_desktoptheme_tabbar.py` reads the profiler reference.
- `docs/invariants.md`: add a desktoptheme row: "`widgets/tabbar.svg`'s `*-active-tab` face and
  top/left bevel are the reference active-window selected tab's (`#EEEEEE` face, `#CCCCCC`
  mid-tone, `#FFFFFF` highlight)." pinned by
  `tests/test_desktoptheme_tabbar.py::TestTabBarReference`, with the provenance exception "The
  reference tab is a trapezoid; the nine-slice is rectangular (PLANS-DONE.md)."

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/tabbar.svg`,
`tests/test_desktoptheme_tabbar.py`, `tests/support/desktoptheme_paths.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Every `*-active-tab` centre, open edge and closed-edge base is `#EEEEEE`; the closed top/left
  band is `#000000`, `#CCCCCC`, `#FFFFFF`; the closed bottom/right band is `#EEEEEE`, `#999999`,
  `#000000`; `test_tabbar_centres_are_the_face`, `test_tabbar_closed_edges_are_raised`,
  `test_tabbar_inner_edges_are_open` and `test_tabbar_corners` pass.
- `TestTabBarReference` re-derives the selected tab's `#000000`/`#CCCCCC`/`#FFFFFF`/`#EEEEEE`
  top band and left edge from `systemprofiler_betawiki.png` and passes; a face left `#CCCCCC` or
  a two-band top/left bevel fails it. It skips, not fails, when the reference is not
  materialized (`skip_unless_materialized`).
- `tabbar.svg`'s header names `systemprofiler_betawiki.png` and the selected tab and no longer
  claims `desktop_fandom.png` as the tab's ground truth.
- `make check` exits 0.


## Done
