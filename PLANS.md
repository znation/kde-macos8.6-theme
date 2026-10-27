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

### Firefox Platinum content: paint about:preferences' category navigation rows as Platinum list rows (planned 2026-10-27 by the plan role; independent of the waiting Kvantum dock-titles plan — the two touch disjoint files (`theme/firefox/…/userContent.css` and its suite versus `theme/kvantum/org.macos8.desktop/*` and its suites), so either order merges; it is part 1 of an about:preferences series — the sidebar's own separator rule and heading band, the page background and the panes' controls are later parts that share this sheet and wait behind it)

**Goal.** The redesigned about:preferences in the installed Firefox ESR 153.5.1 (`chrome/browser/content/browser/preferences/preferences.xhtml`) builds its navigation sidebar as `html:moz-page-nav id="categories"` holding `html:moz-page-nav-button` children (`#category-general` through `#category-experimental`), each a custom element whose shadow root paints an inner `a[href]`/`button` from `chrome/toolkit/content/global/elements/moz-page-nav-button.css`. That sheet paints the rows with ghost-token colour washes (`--button-background-color-ghost` and its hover/active variants), rounded corners (`--button-border-radius`, `--border-radius-small`), a violet-accent selected row (`color-mix(in srgb, currentColor 8%, transparent)` over `--color-accent-primary` text) and a `::before` accent bar at `--page-nav-button-indicator-width` — nothing Platinum. The inner button lives in a shadow root with no `::part()` exposed, but its whole paint reads CSS custom properties the `:host` declares, so the content sheet can retheme every row by overriding those tokens on the `moz-page-nav-button` host element: black text, transparent face, flat `#CCCCFF` hover and selection, square corners, no accent bar.

**Grounding.** No reference screenshot shows a settings navigation sidebar, so this is a platform-required adaptation; the rows adapt the reference-grounded `widgets/listitem.svg` (flat `#CCCCFF` selection, black text, no separate selected affordance) and `widgets/viewitem.svg` (flat `#CCCCFF` hover) — the same pair the landed about:config row rules already use — with `#CCCCFF` the pinned selection token of `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`. Reach and the token route are verified: a headless run of this ESR on 2026-10-27 with a temporary profile whose `userContent.css` held `@-moz-document url-prefix("about:preferences") { body { background-color: #FF0000 !important } moz-page-nav-button { --page-nav-button-background-color: #00FF00 !important } }` rendered the page body red and the category rows green (sampled from the screenshot), confirming the URL match, this sheet's reach and that outer-sheet custom properties override the shadow `:host` defaults. Values with no reference ground, recorded as this theme's own choices: the transparent unselected row face (the sidebar keeps Firefox's page background behind it) and the accent bar's removal (width 0) — Platinum selection is the `#CCCCFF` fill itself. Row padding, icon size, gap and collapsed-width stay Firefox's; `--page-nav-border-color` (the sidebar's 1px inline-end separator, a `moz-page-nav` token) stays Firefox's for a later part.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, after the about:config block, append:

```
/* about:preferences category navigation adaptation 2026-10-27 */
@-moz-document url("about:preferences") {
  moz-page-nav-button {
    --page-nav-button-background-color: transparent !important;
    --page-nav-button-background-color-hover: #CCCCFF !important;
    --page-nav-button-background-color-active: #CCCCFF !important;
    --page-nav-button-background-color-selected: #CCCCFF !important;
    --page-nav-button-text-color: #000000 !important;
    --page-nav-button-text-color-hover: #000000 !important;
    --page-nav-button-text-color-active: #000000 !important;
    --page-nav-button-border-radius: 0 !important;
    --page-nav-button-indicator-color: #000000 !important;
    --page-nav-button-indicator-width: 0 !important;
    --border-radius-small: 0 !important;
  }
}
```

`--page-nav-button-indicator-color` drives both the selected label colour and the `::before` bar; with the width 0 the bar disappears and the selected row is the flat `#CCCCFF` fill with black text. `--border-radius-small: 0` squares the host element's own radius. Add one provenance paragraph to the header comment block, before its closing `*/` (after the about:config paragraph): no reference shows Firefox's about:preferences; the rows adapt `widgets/listitem.svg` and `widgets/viewitem.svg` with the pinned `#CCCCFF` selection; `preferences.xhtml` builds the sidebar as `moz-page-nav#categories` of `moz-page-nav-button` hosts whose `moz-page-nav-button.css` paints the inner `a[href]`/`button` from the `:host` tokens with no `::part()`, so the sheet overrides the tokens on the host element; the headless run of 2026-10-27 confirmed the reach and the token route; declaration checks do not establish rendered row pixels.

In `tests/test_firefox_content_theme.py`, add a `TestFirefoxPreferencesNavTheme(SheetCase)` class with `AT_RULE_URL = "about:preferences"` beside `TestFirefoxConfigTheme`, asserting: `test_required_rules` pins the single rule's exact custom-property declarations; `test_parsed_rules_are_exactly_the_nav_rules` pins the selector set (`moz-page-nav-button`, once); `test_nav_rule_sets_only_custom_properties` requires every declaration to be a `--page-nav-*` or `--border-radius-small` custom property, so the rule changes no geometry, layout or font; `test_header_names_preferences_provenance` requires the strings `"No reference shows Firefox's about:preferences"`, `"widgets/listitem.svg"`, `"widgets/viewitem.svg"`, `"test_selection_background"`, `"moz-page-nav#categories"`, `"moz-page-nav-button.css"`, `"::part"`, `"preferences.xhtml"`, `"2026-10-27"` and `"platform colour adaptation 2026-10-27"`. Update the shared tests for the third block: rename `TestFirefoxContentTheme.test_sheet_has_the_downloads_and_config_at_rules` to `test_sheet_has_the_downloads_config_and_preferences_at_rules`, and let `test_no_rule_paints_page_chrome` accept the `moz-page-nav-button` host selector while still forbidding `body`, `h1`, the heading-wrapper and page-background selectors. The shared `test_palette_is_exact` already admits `#CCCCFF` and `#000000`.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userContent.css` contains exactly three `@-moz-document` blocks: the existing two byte-unchanged and the new `about:preferences` block with the single rule above; no existing declaration changes and no colour outside the pinned palette appears.
- `tests/test_firefox_content_theme.py` gains `TestFirefoxPreferencesNavTheme` with the four new tests, the shared renames land, and the existing downloads, config, palette, no-`@import`/Adwaita, no-universal-selector and provenance tests stay green.
- `docs/invariants.md` gains a row in the `## firefox` table inserted after the about:config row: the sidebar's category rows are transparent-faced with black text, a flat `#CCCCFF` hover and the same flat `#CCCCFF` selection, square and without the accent bar, while the sidebar separator, heading band, page background and panes' controls stay Firefox's. Its test column cites the new class; its provenance records the missing reference surface, the `listitem.svg`/`viewitem.svg` anchors, `test_selection_background`, the shadow-DOM token mechanism with no `::part()`, the ESR 153.5.1 files, the 2026-10-27 headless reach run and that declaration checks do not establish rendered row pixels. `tests/invariants.py` stays green.
- `make check` passes.

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
