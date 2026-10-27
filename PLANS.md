# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned


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


### Platinum Kvantum MDI window buttons: paint QMdiSubWindow's title-band close, minimize, maximize and restore indicators with the Aurorae-grounded Platinum box art (planned 2026-10-27 by the plan role; independent of the waiting Firefox preferences sidebar separators plan — the two touch disjoint files (`theme/kvantum/org.macos8.desktop/*` and its suites versus `theme/firefox/org.macos8.desktop/chrome/userContent.css` and its suite), so either order merges; it is part 2 of the MDI title-bar series, whose part 1 (the interior title band) landed 2026-10-27)

**Goal.** The landed part 1 painted the `QMdiSubWindow` interior title band but left its four window buttons on the engine's compiled-in default art: the theme's `[TitleBar]` names no `indicator.element`, and `org.macos8.desktop.svg` ships no `mdi` groups, so Kvantum 1.1.4 falls back to its built-in default theme's Breeze-style glyphs. Point the band at the `mdi` indicator element and ship the four glyphs as the Platinum window boxes the Aurorae decoration already pins — the plain close box and the zoom box with its inner square, pixel-sampled from the reference screenshots — so the band's buttons are this theme's own, consistent with the Aurorae title bars.

**Grounding.** No reference screenshot shows a `QMdiSubWindow`, so the surface is Kvantum-required, but the artwork is not: the reference's own window controls are the Aurorae decoration's close, zoom and collapse boxes, sampled from `macos8.6-screenshots/aboutsystem_betawiki.png` (close box x=11..22 y=29..40; collapse box x=343..354 y=29..40) and `systemprofiler_betawiki.png` (zoom box x=781..792 y=26..37) and re-derived pixel-by-pixel by `tests/test_aurorae_buttons.py::TestButtons`. The mapping: `mdi-close` is the plain 12x12 close box; `mdi-maximize` and `mdi-restore` are the zoom box (Mac OS does not change the zoom box when a window is zoomed — the same decision `theme/aurorae/themes/org.macos8.desktop/restore.svg` records); `mdi-minimize` reuses the collapse box's two-bars art as this theme's own choice, because Mac OS 8.6 windows show no minimize box for a reference to ground — the collapse box is the reference-grounded roll-up control closest to it. The disabled state flattens each box's gradient face to `#CCCCCC`, keeping the `#888888`/`#222222` outlines and the glyph — the Aurorae `inactive-center` groups' existing KDE-required provenance (the reference's inactive windows draw no boxes). Each group is the source's 12x12 box only: the reference's 13th-pixel `#FFFFFF` highlight column/row is dropped to fit the indicator cell, recorded as this theme's own choice. The engine side: Kvantum 1.1.4's compiled-in default config (`Kvantum/style/themeconfig/default.kvconfig`, read 2026-10-27 from upstream) already sets exactly `indicator.element=mdi` and `indicator.size=12` in `[TitleBar]` — the installed `KvantumAlt` theme's `[TitleBar]` carries the same pair — so the two keys pin what the engine already resolves and the art becomes ours. State coverage: `renderElement` in `Kvantum/style/rendering.cpp` (read 2026-10-27) falls back from a missing `-toggled`/`-pressed`/`-focused` id to the theme's own `-normal` id, so `normal` covers hover and press; `-disabled` has no such fallback (a missing one falls through to the engine's default SVG), so `disabled` ships. `QMdiSubWindow` draws no shade or system-menu button by default and the `CC_MdiControls` menubar variant uses standard icons, not this element, so no `mdi-shade-*` or `mdi-menu-*` art is needed.

**Approach.** In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, inside `[TitleBar]` after `interior.element=titlebar`, add `indicator.element=mdi` and `indicator.size=12`, and rewrite the section comment's last sentence (which defers the `mdi` glyphs to a later part) to record the provenance above: the keys match the engine's compiled-in default `[TitleBar]` and KvantumAlt's; the art is the Aurorae-sampled reference box art; `mdi-minimize`'s mapping to the collapse box, the dropped 13th highlight pixel and the disabled greys are recorded choices; declaration and SVG checks do not establish rendered Qt pixels.

In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, append after the `titlebar-focused` group, in the file's 60px cell grid (the next cell is `translate(10,24970)`, continuing the 60-step), eight groups: `mdi-close-normal`, `mdi-close-disabled`, `mdi-minimize-normal`, `mdi-minimize-disabled`, `mdi-maximize-normal`, `mdi-maximize-disabled`, `mdi-restore-normal`, `mdi-restore-disabled` (that order), each holding the source box art as 1px-thick run rects exactly as the Aurorae group draws it — copy close.svg's `active-center` for the close pairs and shade.svg's for the minimize pairs in place (canvas x=0..11, y=0..11, dropping the x=12 highlight column and y=12 highlight row), and maximize.svg's for both zoom pairs shifted five pixels left (the box sits at canvas x=5..16; drop the five gap columns at x=0..4, the three spacing columns at x=18..20, the x=17 highlight column and the y=12 highlight row). The disabled group's rects keep the source's geometry with every non-outline fill flattened: `#888888` and `#222222` stay, everything else becomes `#CCCCCC` (the `inactive-center` flattening). Precede the eight groups with a comment recording the provenance sentences above. Extend the SVG header comment's surface enumeration with the MDI window buttons.

In `tests/support/kvantum_config_spec.py`, extend `VALUE_KEYS["TitleBar"]` with `"indicator.element": "mdi"` and `"indicator.size": "12"`, so `TestValueKeys` and `test_every_key_is_pinned` stay exhaustive over the extended section.

In `tests/test_kvantum_config_elements.py`, extend `TestTitleBarSurface` with assertions that `[TitleBar]`'s `indicator.element` is `"mdi"` and its `indicator.size` is `"12"`.

In `tests/test_kvantum_svg.py`, add `MDI_STATES = ("normal", "disabled")` and the role tuple `("close", "minimize", "maximize", "restore")` beside `SIZEGRIP_STATES`; import `AURORAE_DIR` from `support.aurorae_fixtures`; add a `TestMdiButtons` class beside `TestSvg` (it can reuse `TestSvg`'s module helpers) pinning: (a) `test_mdi_buttons_ship_normal_and_disabled` — the SVG's id set contains exactly the eight `mdi-<role>-<state>` groups and no `mdi-<role>-focused`, `-pressed` or `-toggled` group, so a later state sneaking in (or a fallback-relevant one going missing) fails; (b) `test_mdi_buttons_are_the_aurorae_box_art` — for each of the eight groups, parse the source Aurorae SVG (`close.svg`, `maximize.svg` for both zoom roles, `shade.svg`; `AURORAE_DIR`), take its `active-center` group's `rect` attribute dicts, drop the highlight column/row rects, shift x by 5 for the zoom sources, flatten the fills for the disabled expectation as above, and assert the group's rect attribute tuples in document order equal the expectation — the art is *defined* as the Aurorae art, so any hand-redrawn pixel fails; and (c) `test_mdi_glyphs_survive_the_flattening` — the zoom glyph (the `#222222` rects at box-local x=7 y=2..6 and y=7 x=2..7) is present in all four zoom groups and the collapse bars (the `#222222` rects at y=5 and y=7) in both minimize groups, so a flattened disabled state cannot lose its glyph. Extend `assert_fill_palette`'s extras in `TestSvg::test_uses_exactly_the_platinum_palette` with two new named constants in `tests/support/platinum_palette.py`: `BOX_INNER_OUTLINE = "#222222"` and `BOX_FACE_MID = "#BBBBBB"`, each commented with its source (the Aurorae close box's inner outline and mid gradient band, sampled by `tests/test_aurorae_buttons.py`); `#EEEEEE`, `#888888`, `#AAAAAA` and `#CCCCCC` are already extras and `#DDDDDD`/`#FFFFFF` are in the base palette, so no other fill is new.

In `docs/invariants.md`, amend the `## kvantum` table row part 1 added (the one whose painted clause ends "and the `mdi` window buttons stay at the engine's default art"): the painted clause becomes that the band's close, minimize, maximize and restore buttons draw the Aurorae-grounded Platinum box art (the plain close box, the collapse box's two-bars art on minimize, the zoom box on maximize and restore) in the normal state — covering focused and pressed through the engine's `-normal` fallback — and its flattened-`#CCCCCC` disabled state; keep and extend the row's provenance with the engine-default config read, the `rendering.cpp` fallback, the minimize mapping and the dropped highlight pixel. `tests/invariants.py` is structural and stays green.

In `README.md`, extend the Kvantum sentence that names the dock header band and the MDI subwindow title band to name the MDI title band's window buttons too.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, `tests/support/kvantum_config_spec.py`, `tests/support/platinum_palette.py`, `tests/test_kvantum_config_elements.py`, `tests/test_kvantum_svg.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `[TitleBar]` sets exactly the two new keys (`indicator.element=mdi`, `indicator.size=12`) beside its byte-unchanged part 1 keys; no other section changes.
- The SVG ships exactly the eight `mdi` groups after `titlebar-focused`, with the comment and header-extension provenance; `TestMdiButtons`'s exact-art, state-set and glyph tests pass, and `TestSvg::test_interior_elements_ship_every_state`, `test_every_element_the_config_names_has_art`, `test_uses_exactly_the_platinum_palette` (with the two new named extras) and the safety-guard test stay green.
- `TestTitleBarSurface` pins the two indicator keys; `tests/test_kvantum_config.py`'s exhaustiveness tests stay green over the extended `VALUE_KEYS`.
- `docs/invariants.md`'s amended row keeps its test column citing `TestTitleBarSurface`, `TestMdiButtons` and the title-band test, and `tests/invariants.py` stays green.
- `README.md`'s Kvantum sentence names the MDI window buttons.
- `make check` passes.

### Firefox Platinum preferences panes: paint about:preferences' page background white and each group heading band as the etched rule with black text (planned 2026-10-27 by the plan role; independent of the waiting Platinum Kvantum MDI window-buttons plan — the two touch disjoint files (`theme/firefox/org.macos8.desktop/chrome/userContent.css` and its suite versus `theme/kvantum/org.macos8.desktop/*` and its suites), so either order merges; it is part 3 of the about:preferences series, whose parts 1 (category navigation rows) and 2 (sidebar separators) both landed 2026-10-27 — the panes' controls (the search field, group cards and native widgets inside `#mainPrefPane`) stay Firefox's and are a later part that waits behind this one)

**Goal.** Parts 1–2 painted the sidebar's rows and separators; the pane itself still wears Firefox's ghost palette: the whole page is painted from the `:root`-level `background-color: var(--background-color-canvas)` of `chrome/toolkit/skin/classic/global/in-content/common-shared.css` (read 2026-10-27 from the installed Firefox ESR 153.5.1 toolkit omni.ja), and every group heading — the `hbox.subcategory` rows of `#mainPrefPane` holding each pane's `html:h1` (and the search-results `html:h2`) — carries `border-top: 1px solid var(--border-color)` from `chrome/browser/skin/classic/browser/preferences/preferences.css` (read 2026-10-27) with Firefox's default-canvas text colour. Paint the page with the theme's reference-grounded white view background and each heading band as black text over the same 1px etch the sidebar's `#nav-separator` got in part 2, so a settings pane reads as one Platinum white field with etched group rules; painting the page itself — rather than only fields, as the landed about:downloads/about:config rules chose — is this theme's own choice, recorded here, because this is the one in-content page whose layout is a document body with a sidebar.

**Grounding.** No reference screenshot shows Firefox's about:preferences, so the surface is platform-required, but every value is reference-grounded through existing pins: the white page background picks up `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_window_view_background` (the same `#FFFFFF` the sheet already paints the about:downloads and about:config list fields with); the heading band's rule is the etched `widgets/line.svg` pair (1px `#888888` over 1px `#FFFFFF`), pinned by `tests/test_desktoptheme_line.py::TestLine` and already painted on `#nav-separator` by part 2 as a `border-top: 1px solid #888888` + `border-bottom: 1px solid #FFFFFF` pair; and the heading text is the theme's black label, `#000000`, the same colour the part 1 rows pinned. Values with no separate reference ground, recorded as this theme's own choices: the white half sits as `box-shadow: inset 0 1px 0 #FFFFFF` directly inside the dark top border (Firefox gives `.subcategory` no bottom border or box-shadow, so a part-2-style `border-bottom` would shift the heading down 1px; the inset shadow overlays only the band's existing top padding and changes no geometry), and Firefox's `.subcategory` heading margins, padding and font sizes stay Firefox's. Reach is verified: part 1's headless run of 2026-10-27 confirmed that the sheet's `@-moz-document url("about:preferences")` block reaches the page's document light DOM (the `body`, `.main-content`, `#mainPrefPane` and `.subcategory` rows live there, unlike the sidebar's shadow tokens), so no new reach run is required; declaration checks do not establish rendered pane pixels.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, append inside the existing `about:preferences` block, after the `#nav-separator` rule (which stays byte-unchanged), two rules in this order: `:root` — `background-color: #FFFFFF !important` — so the canvas under the sidebar (whose `:host`, read 2026-10-27 from `chrome/toolkit/content/global/elements/moz-page-nav.css`, paints no background and lets the page through) and the pane alike are the white field; and `.subcategory` — `border-top-color: #888888 !important`, `box-shadow: inset 0 1px 0 #FFFFFF !important`, `color: #000000 !important` — which repaints the rule, adds the white half and pins black heading text by inheritance into each `html:h1`/`html:h2` (neither selector carries the sheet's forbidden page-chrome tokens: no `body`, `h1`, `hgroup` or `main-content-title` appears, and `.subcategory` is document light DOM). Extend the header comment's about:preferences provenance paragraph, before its closing sentence: the pane follows — Firefox paints the page from `:root`'s `background-color-canvas` in common-shared.css and each heading band from `.subcategory`'s `border-top` in preferences.css (both read 2026-10-27); the page takes the reference-grounded white view background (`test_window_view_background`) and each band the part 2 etch with black text and an inset white half over the band's own padding, no geometry changed; the panes' controls stay Firefox's for a later part.

In `tests/test_firefox_content_theme.py`, add `ROOT = ":root"` and `HEADING = ".subcategory"` beside `SEPARATOR`, append their expected declarations to `REQUIRED_PREFERENCES_NAV_RULES` in document order (so `test_sheet_has_the_downloads_config_and_preferences_at_rules`, `test_required_rules` and `test_parsed_rules_are_exactly_the_nav_rules` stay exact), and add a class constant `HEADING = ...` used by: `test_root_rule_is_the_white_page` — the `:root` rule is exactly `{"background-color": "#FFFFFF !important"}`, reusing the same `#FFFFFF` the about:downloads and about:config field rules pin; `test_heading_band_is_the_etched_rule_with_black_text` — the `.subcategory` rule is exactly the three declarations above, each with `!important`, and a loop asserts every `HEX` token in its values lies in `{ETCH_DARK, WHITE, BLACK}` so the etch cannot drift outside the pinned palette; and `test_heading_selector_avoids_page_chrome` — neither new selector contains `body`, `h1`, `hgroup` or `main-content-title`, mirroring `test_no_rule_paints_page_chrome`'s cross-body guard locally. Extend `TestFirefoxPreferencesNavTheme::test_header_names_preferences_provenance`'s required names with `"common-shared.css"`, `"preferences.css"`, `"test_window_view_background"` and `"#mainPrefPane"`.

In `docs/invariants.md`, amend the about:preferences row in the `## firefox` table: the painted clause becomes that the sidebar keeps its part 1 rows and part 2 separators, the page background is the reference-grounded white view background, and each `.subcategory` heading band is black text over the etched rule with the inset white half, while the panes' controls stay Firefox's; extend the row's provenance with the pane sentences above (the `:root` canvas, the `.subcategory` border, the inset-white choice, the reach reuse). Keep the row's test column citing `TestFirefoxPreferencesNavTheme`'s six original tests plus the two new ones. `tests/invariants.py` is structural and stays green.

No palette constants change: `#000000`, `#888888` and `#FFFFFF` are all already named in `tests/test_firefox_content_theme.py` and `tests/test_firefox_content_theme.py::TestFirefoxContentTheme::test_palette_is_exact` (over the whole text) stays green unchanged.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The `about:preferences` block holds exactly five rules in order — the byte-unchanged `moz-page-nav-button` token rule, the byte-unchanged `moz-page-nav` token rule, the byte-unchanged `#nav-separator` etched rule, the new `:root` white-page rule and the new `.subcategory` heading rule — and the two new rules introduce no colour outside `#FFFFFF`, `#888888` and `#000000`.
- `TestFirefoxPreferencesNavTheme`'s extended `test_required_rules` and `test_parsed_rules_are_exactly_the_nav_rules` pin all five; the two new tests pin the white page and the etched heading band, and every other class test in `tests/test_firefox_content_theme.py` (including `test_palette_is_exact` and the cross-body page-chrome guard) stays green over the unchanged downloads and config bodies.
- The header comment's about:preferences paragraph names the pane surfaces and their sources as above; `test_header_names_preferences_provenance` pins the new required names.
- `docs/invariants.md`'s amended row keeps its test column citing `TestFirefoxPreferencesNavTheme` and `tests/invariants.py` stays green.
- `make check` passes.

## Done
