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

### Firefox Platinum preferences sidebar separators: paint the sidebar's category rule, group rule and sidebar/content border as the Platinum etched separator (planned 2026-10-27 by the plan role; independent of the waiting Platinum Kvantum MDI title band plan — the two touch disjoint files (`theme/firefox/org.macos8.desktop/chrome/userContent.css` and its suite versus `theme/kvantum/org.macos8.desktop/*` and its suites), so either order merges; it is part 2 of the about:preferences series, whose part 1 (the category navigation rows) landed 2026-10-27 — the heading band, the page background and the panes' controls are later parts that share this sheet and wait behind it)

**Goal.** The landed part 1 painted the sidebar's category rows but left three separator surfaces Firefox's. In the installed Firefox ESR 153.5.1 the sidebar carries: (a) the light-DOM rule between the category groups — `chrome/browser/content/browser/preferences/preferences.xhtml` authors `html:hr class="nav-separator" id="nav-separator"` as a `moz-page-nav` child, slotted into the primary nav group, which `chrome/toolkit/content/global/elements/moz-page-nav.css`'s `hr { … background-color: var(--page-nav-hr-background-color) }` rule does not reach (shadow styles cannot match slotted content and the file ships no `::slotted(hr)`), so it paints the UA sheet's inset-border default; (b) the shadow-rendered `hr` between the primary and secondary nav groups, painted from `--page-nav-hr-background-color`; and (c) the sidebar/content border, `:host { border-inline-end: var(--border-width) solid var(--page-nav-border-color) }`. Paint all three Platinum: the etched `#888888`-over-`#FFFFFF` pair on (a), the dark half alone on (b) and (c), where a single custom property takes a single colour.

**Grounding.** No reference screenshot shows Firefox's about:preferences; the etched pair — 1px `#888888` over 1px `#FFFFFF` — is the reference-grounded separator artwork (`widgets/line.svg`, pinned by `tests/test_desktoptheme_line.py::TestLine` and its reference test, the same pair `userChrome.css`'s menu separators use). Surface (a) is document light DOM — `moz-page-nav.mjs` slots it and styles `hr` only in its own shadow tree — so the outer sheet paints the full etched pair on it directly. Surfaces (b) and (c) each take one colour through one custom property (`--page-nav-hr-background-color` defaulting to `var(--border-color)`, `--page-nav-border-color` defaulting to `var(--border-color-transparent)`, read 2026-10-27 from `moz-page-nav.css` and `chrome/toolkit/content/global/elements/moz-page-nav.tokens.css`), so a two-tone etch is impossible there; the flat `#888888` dark half is this theme's own choice, recorded as such, with the border width left at Firefox's `--border-width` and the rule's margins left at Firefox's. The token-override route — outer-sheet custom properties on a custom element beating its shadow `:host` defaults — is the one the landed part 1 verified headless on 2026-10-27, so no new reach run is required.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, append inside the existing `about:preferences` block, after the `moz-page-nav-button` rule (which stays byte-unchanged):

```
  moz-page-nav {
    --page-nav-border-color: #888888 !important;
    --page-nav-hr-background-color: #888888 !important;
  }

  #nav-separator {
    border: 0 !important;
    border-top: 1px solid #888888 !important;
    border-bottom: 1px solid #FFFFFF !important;
  }
```

Extend the header comment's about:preferences provenance paragraph, before its closing sentence: the sidebar's separators follow — the mid-list `#nav-separator` is document light DOM and gets the full etched `widgets/line.svg` pair pinned by `tests/test_desktoptheme_line.py`, while the shadow `hr` and the `:host` inline-end border each take one colour through one custom property, so they carry the dark half alone as this theme's own choice; the token names come from `chrome/toolkit/content/global/elements/moz-page-nav.css` and `moz-page-nav.tokens.css` (2026-10-27) and the token route reuses the headless verification the rows' adaptation recorded; declaration checks do not establish rendered separator pixels.

In `tests/support/platinum_palette.py`, add `ETCH_DARK = "#888888"` beside `GREY`, with a comment naming it the etched separator's dark half from `widgets/line.svg` (its light half is the existing `WHITE`). In `tests/test_firefox_content_theme.py`: import `ETCH_DARK`; add to `REQUIRED_PREFERENCES_NAV_RULES` a `"moz-page-nav"` rule pinning the two custom properties and a `"#nav-separator"` rule pinning `border: 0 !important`, `border-top: 1px solid #888888 !important` and `border-bottom: 1px solid #FFFFFF !important`; scope `test_nav_rule_sets_only_custom_properties` to the `moz-page-nav-button` rule only; add `test_host_rule_sets_only_custom_properties` (the `moz-page-nav` rule's declarations are all custom properties, so the rule changes no geometry or font) and `test_nav_separator_rule_is_the_etched_pair` (the `#nav-separator` rule's declaration set is exactly the three above, and no colour outside `#888888`/`#FFFFFF` appears in the block); `test_parsed_rules_are_exactly_the_nav_rules` already compares against `REQUIRED_PREFERENCES_NAV_RULES`, so it pins the three-selector set and order (`moz-page-nav-button`, `moz-page-nav`, `#nav-separator`); extend `test_header_names_preferences_provenance`'s required strings with `"nav-separator"`, `"moz-page-nav.css"`, `"widgets/line.svg"` and `"test_desktoptheme_line.py"`.

In `docs/invariants.md`, amend the about:preferences row in the `## firefox` table: the painted clause becomes that the sidebar's category rows keep their part 1 paint and the sidebar's three separators — the mid-list `#nav-separator` rule, the shadow group rule and the `:host` inline-end border — are the etched `#888888`-over-`#FFFFFF` pair on the first and the flat `#888888` dark half on the other two, while the heading band, page background and panes' controls stay Firefox's; extend the row's provenance with the separator sentences above. `tests/invariants.py` is structural and stays green.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/support/platinum_palette.py`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The `about:preferences` block holds exactly three rules — the byte-unchanged `moz-page-nav-button` rule, the new `moz-page-nav` token rule and the new `#nav-separator` etched rule — and the two new rules introduce no colour outside `#888888` and the pinned `#FFFFFF`.
- `TestFirefoxPreferencesNavTheme`'s updated and new tests pass: the exact-rule, only-custom-property, etched-pair and provenance tests; the shared `TestFirefoxContentTheme` tests (palette, no-`@import`/Adwaita, no-universal-selector, no-page-chrome) stay green.
- `tests/support/platinum_palette.py` exports `ETCH_DARK`; no existing palette constant changes.
- `docs/invariants.md`'s amended row keeps its test column citing `TestFirefoxPreferencesNavTheme`'s tests and `tests/invariants.py` stays green.
- `make check` passes.

## Done
