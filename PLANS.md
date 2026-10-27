# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._


**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-eight widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight and the
`widgets/containment-controls.svg` panel resize and slider handles, plus
`dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's;
`PLACEHOLDERS.md` records no remaining placeholders); the `org.macos8.desktop` Kvantum widget
style (Platinum palette and core-control art); the
`org.macos8.desktop` Lato font package (Lato Regular and Bold, the Debian copyright file
carrying the upstream SIL OFL 1.1 body, and the provenance record; installed by `make install`,
and the global theme selects its `Lato` family for the general, menu, toolbar, smallest-readable
and window-title fonts, while monospaced text keeps the user's fixed font); the GTK 3 and GTK 4
Platinum stylesheets under `theme/gtk/` (installed by the opt-in `install-gtk` target and
selected by `apply-gtk`; `make install` copies no GTK files); the standalone Firefox Platinum
sheet under `theme/firefox/` (its `userChrome.css` copied and its profile preference written
only by the opt-in `install-firefox` target); and the render and fidelity tooling.
The live reference-comparison gate in `tests/test_render_surface.py` checks Aurorae window-chrome
regions when its render prerequisites are available (README.md, "Fidelity checking").
Firefox's `tests/test_firefox_theme_*.py` modules check stylesheet declarations;
those checks do not establish rendered Firefox pixels. Keep this distinction when assessing
progress toward pixel-perfect application chrome. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces and their status are each tracked here (updated 2026-10-21 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** was out of scope on 2026-10-17 because no reference
screenshot shows a cursor, so no pixel ground truth exists to match; on 2026-10-23 the plan role
queued it anyway as the theme's own Platinum-style pointer set (black-face, white-outline arrow,
text I-beam, pointing hand, busy hourglass, move cross, horizontal and vertical resize arrows,
NW-SE and NE-SW diagonal resize arrows, crosshair, circle-slash, drag-and-drop copy plus,
open and closed hands, the help question-mark arrow, the progress arrow with a small hourglass,
a pencil, the `zoom-in`/`zoom-out` magnifiers, and the drag-and-drop/forbidden aliases, not
traced from Apple's artwork), it
has landed inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; Xcursor roles the theme does not name still come from the fallback cursor
theme; **system sounds** are out
of scope (not a visual surface, so the reference set cannot ground them); and a **lock screen** is
out of scope unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered
2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widen the scope again, and both are being implemented in series.
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19) as a
four-part series: parts 1/4 (GTK 3 Platinum theme) and 2/4 (GTK 4/libadwaita stylesheet) have
landed, and part 3/4 has landed as three entries — the opt-in install (parts 1/3 and 2/3) and
the selection (part 3/3) — while part 4/4 is split into two runs: part 1/2 (the
Firefox `userChrome.css` stylesheet) has landed and part 2/2 (the profile install plus the
preference) has landed. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and has landed (installed and selected by the global theme); part 2/3
(a Chicago-style menu face, whose redistribution licence is still unresolved) is not planned
yet; and part 3/3 (selecting the installed family in KDE/Plasma/Qt) has landed for the Lato
body face only, because Lato is the only family the package installs. KDE, Plasma and Qt
applications now use Lato for the general, menu, toolbar, smallest-readable and window-title
fonts, and monospaced text keeps the user's fixed font; GTK and Firefox
applications keep their own chrome unless the opt-in GTK targets or the Firefox userChrome
install are used (the GTK entries have landed, and Firefox chrome is part 1/2, which has
landed, while its profile install is part 2/2, which has landed). Firefox work since that
series landed as single-surface chrome plans (the downloads-panel and all-tabs rows, the
sidebar frame, the menu-bar title box, the tab faces and the app-menu rows), and it now
reaches a content page: the `userContent.css` sheet paints the about:downloads
list (part 1/2), and its opt-in profile install as part 2/2 has also landed. That is an
extension of the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

_None yet._

### Platinum Kvantum MDI title band: paint QMdiSubWindow's interior title bar as the flat window face with a black label (planned 2026-10-27 by the plan role; independent of the waiting about:preferences navigation plan — the two touch disjoint files (`theme/kvantum/org.macos8.desktop/*` and its suites versus `theme/firefox/…/userContent.css` and its suite), so either order merges; it is part 1 of an MDI title-bar series — the min/max/close/restore button glyphs (Kvantum's `mdi` indicator element) are a later part that waits behind it)

**Goal.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig` defines no `[TitleBar]` section, so a `QMdiSubWindow`'s interior title bar — the band Qt draws for child windows inside a `QMdiArea` — resolves wholly through the engine's compiled-in default config (`interior.element=titlebar`, `indicator.element=mdi`, its own label colours), leaving the band's paint the engine's, not the theme's. Write the section so the band is this theme's own: the bare `#DDDDDD` window face with a plain black label in both the normal and the focused state, no frame and no rule.

**Grounding.** No reference screenshot shows a `QMdiSubWindow`, so this is a Kvantum-required adaptation recorded as such: the section and key names are Kvantum's, read 2026-10-27 from the four installed themes (`KvantumAlt`, `KvAdapta`, `KvAmbiance`, `KvAmbience`), whose `[TitleBar]` sections all share one shape — `inherits=PanelButtonCommand`, `frame=false`, `interior.element=titlebar`, text margins and light focused-label colours. That shape is the plan's; the dock band's `frame.element` route was rejected because none of the four themes sets `frame.element` in `[TitleBar]`. The `#DDDDDD` face and `#000000` label reuse the `[GeneralColors]` `window.color`/`text.color` roles pinned by `tests/test_kvantum_config.py::TestGeneralColors`, themselves grounded; every installed theme paints a light focused label (`KvantumAlt`'s white, `KvAmbiance`'s `#4C4C4C`), so the black focused label is this theme's own choice consistent with Platinum's always-black text. The 2/2/3/3 text margins reuse `KvantumAlt`'s and the landed `[DockTitle]`'s horizontal 3. The band is flat, with no etched bottom rule: interior nine-slice margins are not configurable keys, so a rule inside the `titlebar` element could not be pinned to the band's bottom edge the way `[DockTitle]`'s `frame.bottom=2` pins its own, and no reference surface shows an MDI band to ground one against — recorded as this theme's own choice; the band is distinguished from the window face by its label and window buttons alone. The `mdi` window-button glyphs are deliberately left unpinned: omitting `indicator.element` keeps the engine's internal default art (which all four installed themes also rely on — none ships `mdi` art) and keeps `tests/test_kvantum_svg.py`'s art-existence checks meaningful; pinning Platinum button glyphs is the series' later part.

**Approach.** In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, after the `[DockTitle]` section, append a comment naming the section and recording the provenance sentences above (no reference screenshot shows a `QMdiSubWindow`; the section shape read from the four installed themes; the face and label reuse the grounded `[GeneralColors]` window/text roles; the black focused label, the flat no-rule band and the 2/2/3/3 margins are this theme's own choices; the `mdi` buttons stay at the engine's default art for a later part), then:

```
[TitleBar]
inherits=PanelButtonCommand
frame=false
interior.element=titlebar
text.normal.color=#000000
text.focus.color=#000000
text.margin.top=2
text.margin.bottom=2
text.margin.left=3
text.margin.right=3
```

In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, after the `dock` element groups, append the `titlebar` interior element groups for the two states (`titlebar-normal`, `titlebar-focused`, centre ids only — pure interior elements like `checkbox` ship no slices): each a single flat `#DDDDDD` rect (20x18) in the file's 60px cell grid. Extend the SVG header comment's surface-controls enumeration with the MDI title band. No fill outside the existing set appears (`#DDDDDD` is in `PLATINUM_FILLS`).

Pin the section in `tests/support/kvantum_config_spec.py`: add `"TitleBar": {"frame": "false", "interior.element": "titlebar"}` to `SURFACE_CONTROL_CONFIG` (the `frame=false`-with-interior shape `[MenuItem]` uses) and `"TitleBar": {"text.normal.color": "#000000", "text.focus.color": "#000000", "text.margin.top": "2", "text.margin.bottom": "2", "text.margin.left": "3", "text.margin.right": "3"}` to `VALUE_KEYS`, so `TestSectionCoverage`, `TestValueKeys` and `test_every_key_is_pinned` stay exhaustive over the new section.

In `tests/test_kvantum_config_elements.py`, add a `TestTitleBarSurface` class beside `TestDockSurface` pinning: `[TitleBar]`'s `frame` is `"false"`; its `interior.element` resolves to `"titlebar"`; its `text.normal.color` and `text.focus.color` are both `"#000000"` — the focused colour differs from every installed theme's light focused label; and its text margins are 2/2/3/3.

In `tests/test_kvantum_svg.py`: add `"titlebar": ("normal", "focused")` to `INTERIOR_STATES`; add a `test_titlebar_band_is_the_bare_window_face` method beside `TestSvg::test_dock_band_draws_the_window_face_and_the_etched_rule` asserting, for both states, that the `titlebar-normal`/`titlebar-focused` centre groups equal `(_rect("0", "0", "20", "18", "#DDDDDD"),)` via `_drawing_elements` — so a stray bevel, rule or repaint (its colours are palette members the fill-set test cannot see) fails.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, `tests/support/kvantum_config_spec.py`, `tests/test_kvantum_config_elements.py`, `tests/test_kvantum_svg.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- The `.kvconfig` ends with the `[TitleBar]` section above, preceded by the provenance comment; no existing section changes.
- The SVG ships `titlebar-normal` and `titlebar-focused`; `TestSvg::test_interior_elements_ship_every_state`, `test_every_element_the_config_names_has_art` and `test_uses_exactly_the_platinum_palette` stay green, and the new bare-window-face test holds for both states.
- `TestTitleBarSurface` pins the mapping and label colours; `tests/test_kvantum_config.py`'s exhaustiveness tests stay green.
- `docs/invariants.md` gains a row at the end of the `## kvantum` table: a `QMdiSubWindow`'s interior title band is the bare `#DDDDDD` window face with a plain black label in both the normal and focused state, with no frame, rule, hover or pressed state, and the `mdi` window buttons stay at the engine's default art. Its test column cites `TestTitleBarSurface` and the new `TestSvg` band test; its provenance exception records the missing reference surface, the Kvantum-required names read from the four installed themes, the grounding reuse of `TestGeneralColors`, the theme's own choices and that config and SVG checks do not establish rendered Qt pixels. `tests/invariants.py` stays green.
- `README.md`'s Kvantum sentence that names the dock header band also names the MDI subwindow title band among the surfaces the style maps to the Platinum art.
- `make check` passes.

## Done
