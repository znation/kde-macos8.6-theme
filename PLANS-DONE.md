# Done plans

Finished plans, newest first, moved here by tumwater from PLANS.md's `## Done`. This file
only grows: search it with grep, or read one entry by its line range. Never read it whole.

## Done

### Platinum desktoptheme notes paper: ship `widgets/notes.svg` for the Notes plasmoid's sticky-note papers (planned 2026-10-27 by the plan role; independent of the waiting Firefox preferences-panes plan — the two touch disjoint files (`theme/desktoptheme/org.macos8.desktop/*` and its suites versus `theme/firefox/org.macos8.desktop/chrome/userContent.css` and its suite), so either order merges; the theme's other unshipped plasmoid elements (the analog clock face, the timer digits, dragger, monitor, plot-background and the rest of the installed default theme's set) stay unplanned) — done 2026-10-27 by the feature role

**Goal.** The desktop theme ships twenty-eight `widgets/` SVGs but not `notes.svg`, so the optional Notes plasmoid (`org.kde.plasma.notes`, KDE's Stickies analog — a yellow paper pinned to the desktop) falls back to Breeze's gradient papers. The installed plasmoid draws its full representation and its config thumbnails as `KSvg.SvgItem` with `imagePath: "widgets/notes"` and `elementId: Plasmoid.configuration.color + "-notes"` (`contents/ui/main.qml`, read 2026-10-27 from the installed plasma-workspace), over the ten note colours its config offers — `view.model: ["white", "black", "red", "orange", "yellow", "green", "blue", "pink", "translucent", "translucent-light"]` in `contents/ui/configAppearance.qml`, default `yellow` (`contents/config/main.xml`). Ship all ten papers as flat Platinum-style sticky notes, so every note colour draws this theme's art. The installed default theme is no help for two of them: it spells its element `transluscent-notes` (a typo this plasmoid never requests) and has no `translucent-light-notes` at all, so today those two colours draw nothing.

**Grounding.** No reference screenshot shows a sticky note (nor Mac OS 8.6's Stickies), so the papers are platform-required adaptations. The `imagePath` and the ten `<color>-notes` element ids are KDE-required, read from the installed plasmoid's `main.qml`, `configAppearance.qml` and `config/main.xml` (2026-10-27). The paper recipe is the theme's flat, black-outlined art: each paper is a flat fill inside a 1px `#000000` outline, the outline being the same black the checkmarks and arrows glyphs pin. The fills: `white` `#FFFFFF` and `black` `#000000` reuse the grounded view/label anchors; `yellow` `#FFFFCC` reuses the colour scheme's `[Colors:Tooltip]` role, `255,255,204` — the classic Platinum pale-yellow the scheme already ships as a KDE-required semantic role (QUESTIONS.md decision of 2026-10-08: recorded as not sampled, no retail balloon reference exists) — so the default note echoes the scheme's own pale-yellow rather than introducing a new value; the six remaining chromatic fills (`red` `#FF6666`, `orange` `#FFCC99`, `green` `#99FF99`, `blue` `#99CCFF`, `pink` `#FF99CC`) and the two translucent opacities (`translucent` = `#FFFFFF` at 0.5, `translucent-light` = `#FFFFFF` at 0.35) have no reference ground and are this theme's own choices, recorded in the file's header and pinned by the test so they cannot drift.

**Approach.** Add `theme/desktoptheme/org.macos8.desktop/widgets/notes.svg`: a tight 320x32 canvas holding ten 32x32 cells side by side (the convention `widgets/radiobutton.svg` uses for side-by-side elements, `widgets/checkmarks.svg` for the invisible bounds rect). Each element is a `<g id="<color>-notes">` holding an invisible full-cell bounds rect (`fill="none"`, pinning the element bounds KSvg scales to the note) plus one paper rect — `x="0.5" y="0.5" width="31" height="31"`, `fill` per the mapping above, `stroke="#000000"` `stroke-width="1"` — with the translucent papers' rect adding `fill-opacity` in place of a solid colour. The leading XML comment names the consumer (`org.kde.plasma.notes` `main.qml` `imagePath: "widgets/notes"`), the ten ids as KDE-required, the missing reference surface (no screenshot shows a sticky note), the yellow fill's `[Colors:Tooltip]` reuse with its not-sampled caveat, and the own-choice chromatic fills and translucent opacities. No nine-slice: the plasmoid's SvgItem scales the element, it does not read margins.

In `tests/support/desktoptheme_paths.py`, add `NOTES_SVG = os.path.join(PACKAGE, "widgets", "notes.svg")` beside `PAGER_SVG`. In `tests/test_desktoptheme.py`, import `NOTES_SVG` and append `("notes.svg", NOTES_SVG, 320, 32)` to `SVG_CANVASES`, extending the comment above it with one clause for the ten side-by-side 32x32 note cells; `TestSvgRootCanvas::test_registry_covers_every_shipped_svg` fails until the row lands, so the file cannot ship unregistered.

Add `tests/test_desktoptheme_notes.py` (pattern: `tests/test_desktoptheme_checkmarks.py` — attribute-level assertions via `svg_assertions.elements_by_id`/`attribute_values`, no rendering needed for flat rects) with: `test_notes_declares_exactly_the_kde_required_ids` — the SVG's `id` attributes are exactly the ten `<color>-notes` values the plasmoid's `view.model` names, in canvas order; `test_each_paper_is_a_flat_fill_with_a_black_outline` — a `NOTES_PAPERS` mapping pins all ten `(fill, fill-opacity, stroke)` triples (opacity `None` on the eight solid papers, `0.5` and `0.35` on the two translucent ones), and each element's paper rect is 31x31 at (0.5, 0.5) with `stroke="#000000"` and `stroke-width="1"`; `test_translucent_papers_are_the_only_opacity_carriers` — no element outside the two translucent papers carries a `fill-opacity`, so an opaque paper cannot silently turn translucent; and `test_yellow_paper_reuses_the_tooltip_role` — `yellow-notes`' fill is `#FFFFCC`, with the test's comment naming the `[Colors:Tooltip]` provenance so a future edit re-grounds it deliberately.

In `docs/invariants.md`, append a row to the `## desktoptheme` table: `widgets/notes.svg` draws the Notes plasmoid's ten sticky-note papers as flat fills inside a 1px black outline on ten side-by-side 32x32 cells. Test column: `tests/test_desktoptheme_notes.py::TestNotes`. Provenance exception: no reference screenshot shows a sticky note; the ten ids are KDE-required (read from the installed plasmoid's `main.qml`/`configAppearance.qml`/`config/main.xml`), the yellow fill reuses the scheme's not-sampled `[Colors:Tooltip]` pale-yellow, and the other chromatic fills and translucent opacities are this theme's own; `tests/support/invariants.py` stays green.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/notes.svg`, `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, `tests/test_desktoptheme_notes.py`, `docs/invariants.md`, plus `README.md` (implemented 2026-10-27: the desktop-theme suite requires README to name every shipped SVG in backticks, so the widget list gained the notes.svg clause).

**Acceptance criteria.**
- `widgets/notes.svg` holds exactly ten `<color>-notes` elements — `white`, `black`, `red`, `orange`, `yellow`, `green`, `blue`, `pink`, `translucent`, `translucent-light` — on one 320x32 canvas, each paper the flat-fill/1px-black-outline recipe with the pinned fills, and the header comment names the consumer, the KDE-required ids, the missing reference surface, the tooltip-role reuse and the own-choice values as above.
- `TestNotes`'s four tests pass and pin the ids, the fill/opacity/outline mapping, the opacity carriers and the yellow provenance; `TestSvgRootCanvas`'s registry and root-canvas tests pass with the new `SVG_CANVASES` row; every other desktop-theme test stays green over the unchanged SVGs.
- `docs/invariants.md`'s new row cites `TestNotes` and records the provenance exception; `tests/support/invariants.py` stays green.
- `make check` passes.

### Firefox Platinum preferences panes: paint about:preferences' page background white and each group heading band as the etched rule with black text (planned 2026-10-27 by the plan role; independent of the waiting Platinum Kvantum MDI window-buttons plan — the two touch disjoint files (`theme/firefox/org.macos8.desktop/chrome/userContent.css` and its suite versus `theme/kvantum/org.macos8.desktop/*` and its suites), so either order merges; it is part 3 of the about:preferences series, whose parts 1 (category navigation rows) and 2 (sidebar separators) both landed 2026-10-27 — the panes' controls (the search field, group cards and native widgets inside `#mainPrefPane`) stay Firefox's and are a later part that waits behind this one) — done 2026-10-27 by the feature role

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

### Platinum Kvantum MDI window buttons: paint QMdiSubWindow's title-band close, minimize, maximize and restore indicators with the Aurorae-grounded Platinum box art (planned 2026-10-27 by the plan role; independent of the waiting Firefox preferences sidebar separators plan — the two touch disjoint files (`theme/kvantum/org.macos8.desktop/*` and its suites versus `theme/firefox/org.macos8.desktop/chrome/userContent.css` and its suite), so either order merges; it is part 2 of the MDI title-bar series, whose part 1 (the interior title band) landed 2026-10-27) — done 2026-10-27 by the bugfix role

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

### Firefox Platinum preferences sidebar separators: paint the sidebar's category rule, group rule and sidebar/content border as the Platinum etched separator (planned 2026-10-27 by the plan role; independent of the waiting Platinum Kvantum MDI title band plan — the two touch disjoint files (`theme/firefox/org.macos8.desktop/chrome/userContent.css` and its suite versus `theme/kvantum/org.macos8.desktop/*` and its suites), so either order merges; it is part 2 of the about:preferences series, whose part 1 (the category navigation rows) landed 2026-10-27 — the heading band, the page background and the panes' controls are later parts that share this sheet and wait behind it) — done 2026-10-27 by the feature role

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

**Feature note 2026-10-27.** The approach's test list omits one edit the
criteria force: `test_palette_is_exact` scans the whole sheet text, so its
expected set gained `ETCH_DARK` for the two new rules' `#888888` — that is
what keeps the shared palette test green.

### Platinum Kvantum MDI title band: paint QMdiSubWindow's interior title bar as the flat window face with a black label (planned 2026-10-27 by the plan role; independent of the waiting about:preferences navigation plan — the two touch disjoint files (`theme/kvantum/org.macos8.desktop/*` and its suites versus `theme/firefox/…/userContent.css` and its suite), so either order merges; it is part 1 of an MDI title-bar series — the min/max/close/restore button glyphs (Kvantum's `mdi` indicator element) are a later part that waits behind it) — done 2026-10-27 by the feature role

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

### Firefox Platinum content: paint about:preferences' category navigation rows as Platinum list rows (planned 2026-10-27 by the plan role; independent of the waiting Kvantum dock-titles plan — the two touch disjoint files (`theme/firefox/…/userContent.css` and its suite versus `theme/kvantum/org.macos8.desktop/*` and its suites), so either order merges; it is part 1 of an about:preferences series — the sidebar's own separator rule and heading band, the page background and the panes' controls are later parts that share this sheet and wait behind it) — done 2026-10-27 by the feature role

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

### Platinum Kvantum dock titles: pin the `QDockWidget` title band and dock area (planned 2026-10-27 by the plan role; independent of the waiting GTK infobar plan — the two touch disjoint files (`theme/kvantum/org.macos8.desktop/*` and its suites versus `theme/gtk/…/gtk.css` and its suites), so either order merges) — done 2026-10-27 by the feature role

**Goal.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig` defines no `[Dock]` or `[DockTitle]` section, while the installed engine's themes define both (`/usr/share/Kvantum/KvantumAlt/KvantumAlt.kvconfig` and `/usr/share/Kvantum/KvAdapta/KvAdapta.kvconfig`, read 2026-10-27): `[Dock]` is the area a `QDockWidget` occupies inside a main window and `[DockTitle]` is the header band Qt's `CE_DockWidgetTitle` paints at the top of every dock panel — the panel headers Qt Creator, Krita and similar Qt applications show. With both sections absent, Kvantum resolves the two surfaces from its compiled-in defaults, so a Qt dock's header band and dock area are the engine's, not the theme's. Write both sections so the surfaces are this theme's own: the docking area draws nothing (`frame=false`, `interior=false`, as KvantumAlt pins it, so the panel body keeps the `#DDDDDD` window face), and the header band becomes the menu-bar band read in Kvantum terms — the `#DDDDDD` window face with a plain black label and the bottom edge's etched rule (a `#FFFFFF` row above a 1px `#888888` row at the band's very bottom), the same pair `widgets/line.svg` and the GTK sheets' menubar bands pin. Neither Kvantum-requirement colour nor metric is new to the pinned palette.

**Grounding.** No reference screenshot shows a Qt dock panel, palette or its header band, so this is a Kvantum-required adaptation recorded as such: the section and key names (`[Dock]`, `[DockTitle]`, `inherits`, `frame.*`, `interior.*`, `text.*`) are Kvantum's, read from the two installed themes above (KvAdapta ships an unused `dock-normal`/`dock-focused-*` element set and also sets `text.bold=true`, showing the state ids the engine requests are `normal` and `focused`; responsibility for the paint is ours). The `#DDDDDD` face and `#000000` label reuse the `[GeneralColors]` `window.color` and `text.color` roles pinned by `tests/test_kvantum_config.py::TestGeneralColors`, themselves grounded; the etched pair reuses the reference-grounded `#888888`/`#FFFFFF` rule that `tests/test_desktoptheme_line.py::TestLineReference` re-derives and the GTK menubar bands draw. Chosen values with no reference ground: the band's 0/2/0/0 frame margins (top/left/right/bottom), the 2/3 text margins and the plain (non-bold) label — the reference set shows no dock header to sample a spacing or a weight from, KvantumAlt's bold white-on-default header is clearly not Platinum, and these three are recorded as this theme's own choice.

**Approach.** In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, after `[StatusBar]` (the file's last section), append two commented sections:

```
[Dock]
inherits=PanelButtonCommand
frame=false
interior=false

[DockTitle]
inherits=PanelButtonCommand
frame=true
frame.element=dock
frame.top=0
frame.bottom=2
frame.left=0
frame.right=0
interior=false
text.normal.color=#000000
text.focus.color=#000000
text.margin.top=2
text.margin.bottom=2
text.margin.left=3
text.margin.right=3
```

`[Dock]` mirrors `[StatusBar]` (flat window face, no bevel). `[DockTitle]` draws through one nine-sliced frame element `dock` with `interior=false`, so the label sits on the bare `#DDDDDD` window background and the band's only art is the bottom 2px etched rule: the `frame.bottom=2` margin holds the two rule rows fixed while everything above stretches freely. Treating the band this way reuses exactly the established machinery: `[Splitter]` already ships zero-height slices with frame margins 0.

In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, after the `toolbar` frame groups, append the `dock` element groups for the two states (`dock-normal`, `dock-focused`, centre ids plus all eight `-top`/`-bottom`/`-left`/`-right`/`-topleft`/`-topright`/`-bottomleft`/`-bottomright` slice ids each, in the file's nine-slice layout): each centre group is a flat `#DDDDDD` rect (20x18), each `-bottom` group is two 20x1 rows (`#FFFFFF` at y=0, `#888888` at y=1), and the six margin-degenerate slices (top/left/right and all four corners, x-height or width 0 under the 0 margins) are `fill="none"` one-px rects documented as invisible degenerate slices, the way the size-grip bounds rects read. Extend the SVG header comment's surface-controls enumeration with the dock band. No fill outside the existing set appears: `#DDDDDD` and `#FFFFFF` are in `PLATINUM_FILLS`, `#888888` is the named `CHECKBOX_SHADOW` extra and `"none"` is already accepted.

Pin the sections in `tests/support/kvantum_config_spec.py`: add `"Dock": {"inherits": "PanelButtonCommand", "frame": "false", "interior": "false"}` to `FRAMELESS_SECTIONS` (pinning the `inherits` target like `[StatusBar]`), `"DockTitle": {"frame.element": "dock"}` to `SURFACE_CONTROL_CONFIG`, and `"DockTitle": {"frame": "true", "frame.top": "0", "frame.bottom": "2", "frame.left": "0", "frame.right": "0", "interior": "false", "text.normal.color": "#000000", "text.focus.color": "#000000", "text.margin.top": "2", "text.margin.bottom": "2", "text.margin.left": "3", "text.margin.right": "3"}` to `VALUE_KEYS`, so `TestSectionCoverage`, `TestValueKeys` and `test_every_key_is_pinned` stay exhaustive.

In `tests/test_kvantum_svg.py`: add `"dock": ("normal", "focused")` to `FRAME_STATES`; add a `test_dock_band_draws_the_window_face_and_the_etched_rule` method to `TestSvg` asserting, for both states, that `dock-normal-centre` (and `dock-focused-centre`) equals `(_rect("0", "0", "20", "18", "#DDDDDD"),)` and each `-bottom` slice equals `(_rect("0", "0", "20", "1", "#FFFFFF"), _rect("0", "1", "20", "1", "#888888"))` via `_drawing_elements`, reusing the check-state pin style of `INTERIOR_GROUP_SHAPES` — so a rule row deleted, reordered, rescaled or repainted (all its colours are palette members the fill-set test cannot see) fails.

In `tests/test_kvantum_config_elements.py`, add a `TestDockSurface` class beside `TestToolboxTabSurface` pinning: `Dock`'s `frame` and `interior` are `"false"` and its `inherits` is `"PanelButtonCommand"`; and `[DockTitle]`'s `frame.element` resolves to `"dock"` and differs from KvantumAlt's unpinned default by asserting `frame.bottom` is `"2"` while `frame.top`, `frame.left` and `frame.right` are `"0"`.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, `tests/support/kvantum_config_spec.py`, `tests/test_kvantum_svg.py`, `tests/test_kvantum_config_elements.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- Both sections exist at the end of the `.kvconfig` with exactly the keys above, each preceded by a comment naming the section and recording the no-reference-surface provenance sentence: no reference screenshot shows a Qt dock panel; `[Dock]`/`[DockTitle]` are Kvantum-required (read from the installed KvantumAlt and KvAdapta themes); the face and label reuse the grounded `[GeneralColors]` window/text colours; the etched pair reuses the reference-grounded rule pinned by `TestLineReference`; the 0/2/0/0 margins, 2/3 text margins and plain label are this theme's own choices.
- The SVG ships both `dock` states' nine ids; `TestSvg::test_every_frame_element_ships_its_centre_and_eight_slices`, `test_every_element_the_config_names_has_art` and `test_uses_exactly_the_platinum_palette` stay green, and the new band/rule shape test holds for both states.
- `tests/test_kvantum_config.py::TestSectionCoverage`, `TestFrameMargins` and `TestValueKeys`, `tests/test_kvantum_config_elements.py` (including the new `TestDockSurface`), and every existing Kvantum test pass with no other section, key or element changed.
- `docs/invariants.md` gains a row at the end of the `## kvantum` table: the `QDockWidget` docking area draws nothing (`frame=false`/`interior=false`, flat window face) and its `CE_DockWidgetTitle` header band is the `#DDDDDD` window face with a plain black label and the etched `#FFFFFF`-over-`#888888` bottom rule, with no hover or pressed state. Its test column cites `TestDockSurface` and the new `TestSvg` band test; its provenance exception records the missing reference surface, the Kvantum-required names read from the installed themes, the grounding reuse, `TestGeneralColors` and `TestLineReference`, and that config and SVG checks do not establish rendered Qt pixels. `tests/invariants.py` stays green.
- `README.md`'s Kvantum sentence that names the toolbar buttons, toolbar combo boxes and line edits, split-button dropdowns, tree-view expanders, toolbox tabs and the status bar names the dock header band among the surfaces the style maps to the Platinum art.
- `make check` passes.

*Implementation note (2026-10-27 by the feature role):* the `dock` element groups are appended at the end of the `.svg` (after the size grip, keeping the file's 60px cell grid) rather than inline after the `toolbar` groups, which would have renumbered every later `translate`; and the band test pins the centre ids by the file's `<element>-<state>` naming (`dock-normal`/`dock-focused`), not a `-centre` suffix, which no frame element in the SVG uses.

### Platinum GTK infobar: paint `Gtk.InfoBar` as the menu-bar band with the etched bottom rule (planned 2026-10-27 by the plan role; independent of the waiting Firefox Page Info groupbox plan — the two touch disjoint files (`theme/firefox/…/userChrome.css` and its suite versus `theme/gtk/…/gtk.css` and its suites), so either order merges) — done 2026-10-27 by the feature role

**Goal.** Under both standalone GTK sheets a `Gtk.InfoBar` draws nothing of its own: the bar's content box keeps its transparent background over the window face, its labels take the toolkit's default black, and the `info`, `question`, `warning` and `error` message-type classes distinguish nothing — GTK 3 replaces the toolkit's compiled-in Adwaita rules entirely when `GTK_THEME` names this theme, and GTK 4's embedded `Default` theme defines no infobar rule at all. Give the bar the menu-bar band's recipe — the reference-grounded `#DDDDDD` face, black text and the bottom edge's `#888888`/`#FFFFFF` etch (`border-bottom: 1px solid #888888` with `box-shadow: inset 0 -1px #FFFFFF`, the exact declarations the GTK 4 sheet's `.toolbar, menubar` rule and the GTK 3 sheet's `toolbar, menubar` rule already draw) — so a message band reads as a Platinum band separated from the pane below it. All four message types take the same band: Platinum has no per-type message colour, and the type class names are GTK-required. The bar's close and action buttons keep the sheets' existing `button` paint, `:backdrop` stays out of scope as in the calendar plan, and GTK CSS needs no `appearance` reset — the paint is plain declarations.

**Grounding.** No reference screenshot shows a GTK infobar, so this is a platform-required adaptation; the recipe reuses only values the reference set already pins — the menu-bar face `#DDDDDD` (`tests/test_colorscheme_reference.py::TestReferenceAnchors::test_menu_bar_face`) and the etched pair (`tests/test_desktoptheme_line.py::TestLineReference`) — through the sheets' own menubar band rules, adding no new colour or metric. Measured live with PyGObject (GTK 3.24.49 and GTK 4.18.6, `GTK_THEME=org.macos8.desktop` with the sheet symlinked under a temp `XDG_DATA_HOME/themes`, on the session display): both toolkits build `infobar > revealer > box` — the infobar node carries the message-type style class (GTK 3 showed `horizontal, error`; GTK 4 showed `warning` with the node tree `infobar > revealer > box > [box, box, button.close > image]`; GTK 3's adds the message box holding the label and an action-area box beside it) — and the infobar node resolves `background-color` transparent with black text under this theme, so today the band is invisible and the type classes change nothing; the one `infobar > revealer > box` selector reaches both toolkits' band box, its `color` inherits to the message label, and the close and action buttons keep their own paint.

**Approach.** Append at the very end of `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, after each sheet's calendar rules, one comment and one rule (the same text in both sheets):

```css
/* An infobar draws the menu-bar band: the #DDDDDD face, black text and the
   etched bottom rule. The info, question, warning and error type classes all
   take this band; no reference screenshot shows a GTK infobar, and the type
   class names are GTK-required. */
infobar > revealer > box {
  background-color: #DDDDDD;
  color: #000000;
  border-bottom: 1px solid #888888;
  box-shadow: inset 0 -1px #FFFFFF;
}
```

Add one sentence to each sheet's header comment block, before its closing `*/` (after the spinner sentence): "An infobar band reuses the menu-bar band's face and etched bottom rule with black text; no reference screenshot shows a GTK infobar, and the four message-type class names are GTK-required, so all types take the same band." In `tests/support/gtk_theme_spec.py`, add beside `RUBBERBAND`:

```python
# An infobar draws the menu-bar band's face and etched bottom rule. No
# reference screenshot shows a GTK infobar; the GTK-required type class names
# take no per-type colour, so all four message types use this one band.
INFOBAR = {
    "background-color": FACE,
    "color": BLACK,
    "border-bottom": f"1px solid {ETCH_DARK}",
    "box-shadow": f"inset 0 -1px {WHITE}",
}
```

In `tests/support/gtk_rule_cases.py`, add `assert_infobar(self, selectors)` to `GtkSheetRuleCases` next to `assert_rubberband`, asserting each of the suite's own selectors against `INFOBAR`, and add infobar to the two docstring lists of assertions that take the suites' own selectors.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/support/gtk_theme_spec.py`, `tests/support/gtk_rule_cases.py`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Each sheet ends with exactly the rule above (the same selector and the same four declarations, after its calendar rules), and each header comment gains the infobar sentence. Both sheets' `test_only_palette_hex_literals` tests stay green: the rule adds no hex literal outside each suite's pinned palette (`#DDDDDD`, `#000000`, `#888888` and `#FFFFFF` are already in it).
- `tests/test_gtk_theme.py::TestGtkTheme` gains `test_infobar` calling `self.assert_infobar(("infobar > revealer > box",))`, and `tests/test_gtk4_theme.py::TestGtk4Theme` gains the same test, both placed immediately after their `test_calendar`; each also asserts the sheets name no message type — no rule selector contains `.info`, `.question`, `.warning` or `.error` — and `assert_rule` pins each of the four declarations against `INFOBAR`.
- `docs/invariants.md` gains a row appended at the end of the `## gtk` table: both GTK sheets draw an infobar (`infobar > revealer > box`) as the menu-bar band — the `#DDDDDD` face, black text and the `#888888`/`#FFFFFF` etched bottom rule — with all four message types (`info`, `question`, `warning`, `error`) taking the same band, the close and action buttons keeping the `button` paint and `:backdrop` out of scope. Its test column names the two new `test_infobar` tests; its provenance records the missing reference surface (no screenshot shows a GTK infobar), the live-measured node tree and current transparent background (GTK 3.24.49 / GTK 4.18.6, 2026-10-27), the re-used reference-grounded values (`TestReferenceAnchors::test_menu_bar_face`, `TestLineReference`, the sheets' own menubar band rules), and the GTK-required class names. `tests/invariants.py` stays green.
- `make check` passes, and every existing rule in both sheets keeps its declarations and selector, including the menubar bands the infobar reuses.

### Firefox Platinum chrome: paint the Page Info security panel's groupbox frames and headers as the Platinum group frame (planned 2026-10-27 by the plan role; independent of the waiting Page Info meta/image-trees plan — both append at the very end of `userChrome.css`, insert their provenance paragraphs before the header's closing `*/` and trim only their own words from the shared stay-Firefox sentences, so either order merges) — done 2026-10-27 by the feature role

**Goal.** Make the security panel's three group frames read as Platinum group boxes: each `groupbox` child of `vbox#securityPanel` gets the reference's etched group frame — a 1px `#888888` rectangle carrying the same `#888888`/`#FFFFFF` etched pair the sheet's rules already pin, drawn as the 1px highlight copy offset one pixel right and down (the light half running inside the dark top and left, outside the dark bottom and right) — over a transparent interior that keeps the dialog body face, square corners, `2px 8px` interior padding, and a `1em` face gap between stacked frames; each frame's `label.header` keeps Firefox's heading weight but takes the black Platinum text colour. The frames' contents — the identity table's readonly inputs (still the `#mainDeck input` paint), the `#securityTable` rows, the `#security-technical-*` labels and descriptions — and the security panel's already-painted buttons keep their own paints, as do the General and Media panels' `.header` labels (`#metaTagsCaption`, `html:input#hostText`) which sit outside `#securityPanel`.

**Grounding.** Unlike the sheet's other Page Info surfaces, this frame IS in the lossless reference set: `macos8.6-screenshots/systemprofiler_betawiki.png` (the retail Japanese 8.6 System Profiler) draws the framed group box for the first Software-overview section as a dark 1px `#888888` rectangle spanning x=241..678, y=103..153 with the 1px `#FFFFFF` copy offset one pixel right and down (top row y=104 and left column x=242 inside the dark lines, right column x=679 and bottom row y=154 outside), whose bottom rule and left edge `tests/test_desktoptheme_line.py::TestLineReference` already re-derives as the etched pair — `test_horizontal_rule_matches_reference` pins this box's bottom rule ((260,153) dark, (260,154) light) and `test_vertical_rule_matches_reference` its left edge ((241,128) dark, (242,128) light). The same screenshot grounds the black text: the reference's header glyphs (the section label beside its disclosure triangle, above the frame at y=80..86) sample pure `#000000`, the shared Platinum foreground. The reference header sits above the frame with a disclosure triangle, which this plan does not reproduce: `pageInfo.xhtml`'s groupboxes carry no disclosure control and the label is the groupbox's first child inside the frame, so the headers stay in Firefox's markup order and only their colour is adapted. In the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/pageinfo/pageInfo.xhtml` opens `vbox#securityPanel` with three `groupbox` elements, each headed by a `label.header` (the `security-view-identity`, `security-view-privacy` and `security-view-technical` l10n ids) and holding the pane's table or descriptions; `chrome/toolkit/content/global/xul.css` gives `groupbox` only `flex-direction: column` and no `-moz-default-appearance`, and neither `chrome/toolkit/skin/classic/global/global.css` (whose `global-shared.css` supplies only the `.header` font weight and the stock label margins) nor the pageinfo skin's `pageInfo.css` paints any groupbox border, so the sheet adds the whole frame with plain declarations and no `appearance: none` is needed (`!important` keeps the sheet's convention). `#securityPanel` appears in no chrome file outside page info (`pageInfo.xhtml`, `pageInfo.js`, `pageInfo.css`), so the `#securityPanel >` scoping cannot leak into browser chrome. The between-frames gap is not re-derivable from the reference set — the lossless PNG shows one framed box and no second frame, and the lossy `apps_macrumors8.6.jpg` shows the English 8.6 Profiler's stacked framed sections but is not pixel ground — so the `1em` face gap reuses `pageInfo.css`'s own `#securityPanel table { margin-bottom: 1em }` spacing unit (platform geometry adaptation 2026-10-27); the reference renders no pad value usable as a CSS literal either, and `2px 8px` keeps the first content rows about 8px clear of the light half (the box's interior content starts at x≈250, seven pixels inside the x=242 light column, and six rows below the y=104 light row) within the stock label margins.

**Approach.** Append at the very end of `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the `#imagecontainerbox` rule (or after the trees plan's rules when that plan has landed), one short comment naming the adaptation and these three rules in this order:

```css
#securityPanel > groupbox {
  border: 1px solid #888888 !important;
  border-radius: 0 !important;
  padding: 2px 8px !important;
  box-shadow: 1px 1px #FFFFFF, inset 1px 1px #FFFFFF !important;
}

#securityPanel > groupbox + groupbox {
  margin-top: 1em !important;
}

#securityPanel > groupbox > label.header {
  color: #000000 !important;
}
```

The border is the dark half and the two shadow halves reproduce the reference's offset highlight copy exactly: the outset `1px 1px #FFFFFF` draws the light bottom row and right column outside the border box, and the inset `1px 1px #FFFFFF` draws the light top row and left column just inside the border, so every frame edge reads dark-over-light as the reference's rectangle does, corners included. Keep the interiors transparent (no `background-color` or `color` declaration on the groupbox — the dialog body face and the stock content colours show through, and the tables' rows, readonly inputs and technical descriptions keep their paints), keep `xul.css`'s `flex-direction: column` and the labels' stock margins and bold `.header` weight, and add no rule for the frame's contents, the `hbox` help-button row, the deck's other panels' `groupbox` elements (there are none — but the selectors stay `#securityPanel`-scoped so none could leak from later Firefox markup), any hover, focus, active or disabled frame variant (a groupbox and its header are static), the disclosure triangle the reference draws (the Page Info groupboxes carry none) or any `caption` element (the markup has none), and change no existing selector. In the header comment block, insert a group-frame provenance paragraph immediately before the closing `*/` (after whichever Page Info paragraphs are present when this lands): the reference group box — `macos8.6-screenshots/systemprofiler_betawiki.png`'s framed Software-overview section at x=241..679, y=103..154, the dark `#888888` rectangle with its `#FFFFFF` highlight copy offset one pixel right and down — is re-derived edge for edge and corner by the extended `tests/test_desktoptheme_line.py::TestLineReference`, whose existing bottom-rule and left-edge pair assertions already pin this box's etched pair; `pageInfo.xhtml` supplies the three `#securityPanel` groupboxes and their `label.header` headers, `chrome/toolkit/content/global/xul.css` gives `groupbox` only `flex-direction: column` with no default appearance and no skin paints a border, so the sheet adds the whole frame; the headers stay inside the frame in Firefox's markup order and black takes the shared Platinum foreground; `1em` between frames is `pageInfo.css`'s own spacing unit because the lossless reference shows a single framed box (lossy `apps_macrumors8.6.jpg` is not pixel ground); declaration checks pin the sheet's declarations and the reference test re-derives the frame's pixels, not Firefox's rendered dialog (reference grounding 2026-10-27). Also trim the frame from the shared stay-Firefox sentences by replacing `security tables` with `security-table rows` in exactly three sheet texts — the top-bar provenance paragraph's stay list (`…the dialog body, security-table rows, description labels and focus rings…`; the trees plan, landed first, had already trimmed its tree words from this list), the `#topBar` rule's leading comment (`…the dialog body, fields, security-table rows and labels…`, again carrying no tree words after the trees plan), and `docs/invariants.md`'s security-table stay lists in the top-band, field, permission-list, media-preview and trees rows — leaving every other word unchanged (the trees plan merged before this one, so its own tree-word trims were already in place, and its invariants row's `security tables` did become `security-table rows` in this edit).

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py`, `tests/test_firefox_theme_page_info.py`, `tests/test_desktoptheme_line.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` gains exactly the three new rules above, with no rule name other than the three selectors namespaced to `groupbox` and no new hex literal (`#888888` is the sheet's existing etched `#888888`, and `#FFFFFF`/`#000000` are the palette's `WHITE`/`BLACK`), so `test_palette_is_exact` keeps its expected hex set. Every existing selector keeps its declarations, and the two shared stay-Firefox sentences change only as the trim above specifies.
- `REQUIRED_RULES` in `tests/support/firefox_chrome_cases.py` gains, appended after the last existing Page Info assignment (`REQUIRED_RULES["#permList .permission:hover"]`, or after `"tree#imagetree treechildren::-moz-tree-cell-text(broken)"` when the trees plan has landed): `"#securityPanel > groupbox"` mapping to `border: 1px solid {ETCH_DARK} !important`, `border-radius: 0 !important`, `padding: 2px 8px !important` and `box-shadow: 1px 1px {WHITE}, inset 1px 1px {WHITE} !important`; `"#securityPanel > groupbox + groupbox"` mapping to `margin-top: 1em !important`; and `"#securityPanel > groupbox > label.header"` mapping to `color: {BLACK} !important` — importing `ETCH_DARK` from `support.gtk_theme_spec` beside the existing `BUTTON_BEVEL`/`ETCH_DARK`/`RAISED_BEVEL` import, and with no entry carrying `background-color`, `color` (except the header), `font-weight` or an `appearance` declaration. The paged entry order is the CSS order above; the `+` selector needs no element matching (the `support.selector_matching` subset has no adjacent-sibling combinator), so it is assertion-only like the trees plan's pseudo-element selectors.
- New `TestFirefoxPageInfo.test_page_info_groupbox_paint_is_scoped_to_page_info`, placed immediately after the last Page Info scope test (`test_page_info_permission_list_paint_is_scoped_to_page_info`, the last Page Info scope test in the landed file): asserts the rule names containing `groupbox` are exactly the three selector names and each equals its `REQUIRED_RULES` entry; and element matching covers the two matchable selectors: build `window` holding `deck#mainDeck` with `vbox#securityPanel` holding three `groupbox` children whose first children are `label.header` labels, plus a stray `groupbox` with a `label.header` child elsewhere in the deck (outside `#securityPanel`); assert the three security groupboxes match `"#securityPanel > groupbox"` and the stray one matches neither that nor the `+` selector's key, the three headers match `"#securityPanel > groupbox > label.header"` and the stray header matches none of the three names.
- New `TestFirefoxPageInfo.test_page_info_groupbox_provenance`, placed immediately after the scope test, asserts the leading comment names `"systemprofiler_betawiki.png"`, `"x=241..679"`, `"y=103..154"`, `"#888888"`, `"offset one pixel right and down"`, `"tests/test_desktoptheme_line.py::TestLineReference"`, `"pageInfo.xhtml"`, `"label.header"`, `"chrome/toolkit/content/global/xul.css"`, `"flex-direction: column"`, `"-moz-default-appearance"`, `"#securityPanel"`, `"pageInfo.css"`, `"apps_macrumors8.6.jpg"`, `"1em"`, `"Declaration checks pin the sheet's declarations"` and `"reference grounding 2026-10-27"`. Leave every existing provenance test's tuple untouched so this plan edits none of them.
- `tests/test_desktoptheme_line.py::TestLineReference` gains three test methods after `test_vertical_rule_matches_reference`, reusing `assert_rule` where it applies: `test_group_box_top_rule_matches_reference` asserts the same box's top rule (`assert_rule((400, 103), (400, 104), (400, 102), (400, 105))`) and `test_group_box_right_rule_matches_reference` its right edge (`assert_rule((678, 110), (679, 110), (677, 110), (680, 110))`); `test_group_box_corners_match_reference` asserts the box's four corner blocks pixel for pixel — (241,103)/(242,103)/(241,104)/(242,104) from the top-left are `#888888`/`#888888`/`#888888`/`#FFFFFF`, (678,103)/(678,104)/(679,104)/(677,104) from the top-right are `#888888`/`#888888`/`#FFFFFF`/`#FFFFFF` with (679,103) the `#EEEEEE` body, (241,153)/(242,153)/(242,154)/(241,154) from the bottom-left are `#888888`/`#888888`/`#FFFFFF`/`#EEEEEE`, and (678,153)/(679,153)/(678,154)/(679,154) from the bottom-right are `#888888`/`#FFFFFF`/`#FFFFFF`/`#FFFFFF` — so the extended reference covers every edge and corner of the frame this sheet's rule adapts. Existing test methods stay untouched.
- `docs/invariants.md` gains a row appended at the end of the `## firefox` table, after the last Page Info row and before `## gtk`: the security panel's group frames (`#securityPanel > groupbox`) are the reference's etched group box — a 1px `#888888` rectangle with the `#FFFFFF` highlight copy offset one pixel right and down, square corners `2px 8px` interior padding and a transparent interior over the dialog body face, `1em` between stacked frames — with each frame's `label.header` black at Firefox's stock heading weight and the reference's disclosure-triangle header not reproduced (the Page Info groupboxes carry no disclosure control), while the frames' contents, the deck's other painted surfaces and the General and Media panels' `.header` labels keep their own paints. Its test column names the new scope and `TestLineReference` extension tests, and its provenance records the `systemprofiler_betawiki.png` group box at x=241..679, y=103..154 that `tests/test_desktoptheme_line.py::TestLineReference` re-derives, the installed Firefox ESR 153.5.1 `pageInfo.xhtml`/`xul.css`/`pageInfo.css` facts, the `1em` gap's pageInfo.css spacing source, and the not-reproduced disclosure header. `tests/invariants.py` stays green.
- `make check` passes, and the existing `userChrome.css` rules (including the `#topBar`, `#viewGroup`, `#mainDeck`, `#mainDeck input`, `#permList`, `#imagecontainerbox` and, when it has landed, the trees paints), the Firefox install and their tests keep their declarations and scope.

### Firefox Platinum chrome: paint the Page Info dialog's meta and image trees as Platinum list rows (planned 2026-10-27 by the plan role; independent of the waiting Page Info media-preview plan — both append at the very end of `userChrome.css`, insert their provenance paragraphs before the header's closing `*/` and trim only their own words from the shared stay-Firefox sentences, so either order merges) — done 2026-10-27 by the feature role

**Goal.** Make the General panel's meta table and the Media panel's image list read as Platinum lists: the `tree#metatree` and `tree#imagetree` containers become the opaque `#FFFFFF` sunken field the landed `#permList` recipe uses — square corners, a 1px `#000000` outline, the `inset 1px 1px #999999` top-left shadow and black text — with rows left transparent over the field so no skin hover wash paints, a selected row flat `#CCCCFF` with black text (the theme's flat selection), and the Media panel's broken-image rows keeping their stock italic `graytext`. No `appearance: none` is needed: the trees are painted with plain declarations, no `-moz-default-appearance`. The trees' stock geometry stays Firefox's — the `tree { margin: 0.5em }` and `tree { margin: 0 4px }` margins, `#imagetree`'s `min-height: 10em` and `margin-block: 2px 0`, the rows' `1px solid transparent` border and `max(24px, 1.3em)` min-height, the cells, twisties, sort direction and `hidecolumnpicker` behaviour. The column headers (`treecol` and the column-picker button, painted `-moz-ColHeader` with a `ThreeDLightShadow` divider) stay Firefox's stock paint and are named as untouched. The deck's permission list, display fields, media preview, security tables and the landed top-bar, tab and button paints are untouched. The tree rows need `::-moz-tree-row`/`::-moz-tree-cell-text` pseudo-element selectors that `tests/support/selector_matching` does not evaluate (only `#id`, `.class`, `[attribute]`, `:hover` and `:not(...)` are in its subset), so the new tests are rule-name and declaration assertions, with element matching used only for the two container selectors.

**Grounding.** No reference screenshot shows Firefox's Page Info trees, so the paint adapts this theme's Platinum list surfaces (platform colour adaptation 2026-10-27). The `#FFFFFF` face and `#999999` sunken shadow adapt `widgets/lineedit.svg` (`tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`), grounded in `macos8.6-screenshots/firstboot_betawiki.png`, and are the exact recipe the sheet's landed `#mainDeck input` and `#permList` rules already ship; `#metatree`/`#imagetree` are the deck's remaining list-shaped surfaces. The transparent rows and no hover highlight adapt `widgets/listitem.svg` (`tests/test_desktoptheme_listitem.py::TestListItem`), whose comment records that Mac OS 8.6 lists have no hover highlight, and the flat `#CCCCFF` black-text selection adapts `widgets/viewitem.svg` (`tests/test_desktoptheme_viewitem.py::TestViewItem`), pinned by `test_selection_background` — the same reading the sheet's `#prefs > tr:hover` and the downloads panel's `richlistitem[selected]` rules already paint. In the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/pageinfo/pageInfo.xhtml` defines `tree#metatree` inside `vbox#metaTags` (`hidecolumnpicker="true"`, columns `#meta-name`/`#meta-content`) and `tree#imagetree` in `vbox#mediaPanel` (columns `#image-address`, `#image-type` and their siblings), and neither tree carries a `multicol` attribute, so the global skin's `treechildren::-moz-tree-row(multicol, odd)` odd-row paint never applies to them. `chrome/toolkit/skin/classic/global/tree/tree.css` paints `tree` with plain declarations (`background-color: Field`, `color: FieldText`, `border: 1px solid ThreeDShadow`, `margin: 0 4px`) and paints rows through `treechildren::-moz-tree-row(hover)` (an `hsla(0, 0%, 50%, 0.15)` wash), `::-moz-tree-row(selected)` (`-moz-cellhighlight`) and `::-moz-tree-row(selected, focus)` (`SelectedItem`), with cell text through `::-moz-tree-cell-text` (`color: inherit`) and `::-moz-tree-cell-text(selected)`/`(selected, focus)` (`-moz-cellhighlighttext`/`SelectedItemText`), so every overridden paint is a plain declaration and no `appearance` declaration is needed; the pageinfo skin `chrome/browser/skin/classic/browser/pageInfo.css` adds only `tree { margin: 0.5em }`, `#imagetree { min-height: 10em; margin-block: 2px 0 }` and `treechildren::-moz-tree-cell-text(broken) { font-style: italic; color: graytext }`. Both ids appear only in page-info files, so the rules cannot leak into browser chrome. Declaration checks do not establish rendered pixels.

**Approach.** Append at the very end of `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the `#permList .permission:hover` rule (or after the `#imagecontainerbox` rule when the media-preview plan has landed), one short comment naming the adaptation and these five rules in this order (the later selected rule paints a hovered selected row):

```css
#metatree,
#imagetree {
  background-color: #FFFFFF !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #999999 !important;
}

tree#metatree treechildren::-moz-tree-row(hover),
tree#imagetree treechildren::-moz-tree-row(hover) {
  background-color: transparent !important;
}

tree#metatree treechildren::-moz-tree-row(selected),
tree#imagetree treechildren::-moz-tree-row(selected) {
  background-color: #CCCCFF !important;
}

tree#metatree treechildren::-moz-tree-cell-text,
tree#imagetree treechildren::-moz-tree-cell-text {
  color: #000000 !important;
}

tree#imagetree treechildren::-moz-tree-cell-text(broken) {
  color: graytext !important;
}
```

Each `!important` declaration beats the skin's normal ones, so one `(selected)` rule covers `(selected, focus)` and one cell-text rule covers `(selected)`/`(selected, focus)`; the `(broken)` rule re-asserts `graytext` because the black cell-text rule would otherwise recolour the broken rows. Keep the stock margins, `#imagetree`'s min-height and margin-block, the rows' transparent border and min-height, and every cell, twisty, splitter and sort behaviour. Add no rule for `treecol`, `.tree-columnpicker-button`, `.treecol-text` or the sort direction (headers keep Firefox's paint), for `treechildren::-moz-tree-row(multicol, odd)` (both page-info trees lack a `multicol` attribute, verified in `pageInfo.xhtml`), for the `dropOn`/`current`/`editing` states (a page-info tree is never edited or a drop target) or for `#metaTags`, `#mediaPanel` or any label, and change no existing selector. In the header comment block, insert a tree provenance paragraph immediately before the closing `*/` (after the permission-list paragraph, and after the media-preview paragraph when that plan has landed): no reference shows Firefox's Page Info trees; the `#FFFFFF` face and `#999999` sunken shadow adapt `widgets/lineedit.svg` and the `#mainDeck input`/`#permList` recipes, the transparent rows honour `widgets/listitem.svg`'s no-hover-highlight list reading and the flat `#CCCCFF` black-text selected row adapts `widgets/viewitem.svg` pinned by `test_selection_background`; `pageInfo.xhtml` defines `tree#metatree` and `tree#imagetree` with no `multicol` attribute and `chrome/toolkit/skin/classic/global/tree/tree.css` plus the pageinfo skin's `pageInfo.css` own the stock `Field`/`ThreeDShadow` paint, the row hover wash, the `-moz-cellhighlight`/`SelectedItem` selection, the `-moz-cellhighlighttext`/`SelectedItemText` selected text and the broken rows' italic `graytext`; the column headers stay Firefox's; declaration checks do not establish rendered pixels (platform colour adaptation 2026-10-27). Also trim the trees from the stay-Firefox surface lists in the existing Page Info texts — the header's top-bar provenance paragraph drops `meta and image trees` ("…the dialog body, media preview, security tables, description labels and focus rings stay Firefox's…"), the `#topBar` rule's leading comment drops `trees` ("…the dialog body, fields, media preview, security tables and labels keep Firefox's own paint…"), and the `docs/invariants.md` Page Info top-bar, fields, permission-list and media-preview rows drop the trees from their stay-Firefox lists — leaving every other word unchanged (the waiting media-preview plan trims `media preview` from the same sentences; whichever lands first, the other's words are still present to trim).

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py`, `tests/test_firefox_theme_page_info.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` gains exactly the five new rules above: the two container selectors `#metatree` and `#imagetree` (one block, split by the test parser's selector-list splitting in `tests/support/gtk_css.py::parse_css`), the two hover row selectors, the two selected row selectors, the two cell-text selectors and the one `(broken)` cell-text selector. Every existing selector keeps its declarations, and `test_palette_is_exact` keeps its expected hex set because the rules introduce no new hex literal (`graytext` is a system colour, not a hex literal; the `#CCCCFF` is the palette's `SELECTION`).
- `REQUIRED_RULES` in `tests/support/firefox_chrome_cases.py` gains, appended immediately after the last existing Page Info assignment (after `REQUIRED_RULES["#permList .permission:hover"]`, after the `#imagecontainerbox` assignment, which precedes the permission-list assignments): `"#metatree"` and `"#imagetree"` mapping to `background-color: {WHITE} !important`, `color: {BLACK} !important`, `border: 1px solid {BLACK} !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px {GREY} !important`; the two hover row selectors mapping to `background-color: transparent !important`; the two selected row selectors mapping to `background-color: {SELECTION} !important`; the two cell-text selectors mapping to `color: {BLACK} !important`; and `"tree#imagetree treechildren::-moz-tree-cell-text(broken)"` mapping to `color: graytext !important` — with the constants `support.platinum_palette` already exports, and no container entry carrying an `appearance` declaration.
- New `TestFirefoxPageInfo.test_page_info_tree_paint_is_scoped_to_page_info`, placed immediately after `test_page_info_permission_list_paint_is_scoped_to_page_info` (after `test_page_info_media_preview_paint_is_scoped_to_page_info`, since the media-preview plan has landed): asserts the rule names containing `metatree` or `imagetree` are exactly those nine selector names, each equals its `REQUIRED_RULES` entry, the pseudo-element names contain `::-moz-tree-row(hover)`, `::-moz-tree-row(selected)` and `::-moz-tree-cell-text`, and no rule name contains `treecol` or `tree-columnpicker`. Element matching (`support.selector_matching.element`/`matches`) covers only the containers: build `window` holding `deck#mainDeck` with `vbox#metaTags` containing `tree#metatree` and `vbox#mediaPanel` containing `tree#imagetree`, plus a stray `tree` with no id in another panel and the bookmark panel's `tree#editBMPanel_folderTree`; assert `tree#metatree` and `tree#imagetree` each match their own container selector and not the other's, and the stray trees match none of the eight names.
- New `TestFirefoxPageInfo.test_page_info_tree_provenance`, placed immediately after the scope test, asserts the leading comment names `"No reference shows Firefox's Page Info trees"`, `"widgets/lineedit.svg"`, `"firstboot_betawiki.png"`, `"tests/test_desktoptheme_lineedit.py::TestLineEdit"`, `"TestLineEditReference"`, `"#mainDeck input"`, `"#permList"`, `"widgets/listitem.svg"`, `"tests/test_desktoptheme_listitem.py::TestListItem"`, `"no hover highlight"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"pageInfo.xhtml"`, `"multicol"`, `"chrome/toolkit/skin/classic/global/tree/tree.css"`, `"pageInfo.css"`, `"Field"`, `"ThreeDShadow"`, `"-moz-cellhighlight"`, `"SelectedItem"`, `"-moz-cellhighlighttext"`, `"SelectedItemText"`, `"graytext"`, `"column headers stay Firefox's"`, `"Declaration checks do not establish rendered pixels"` and `"platform colour adaptation 2026-10-27"`. Leave `test_page_info_provenance`, `test_page_info_permission_list_provenance`, and the field and (when landed) media-preview provenance tests untouched so this plan does not edit their tuples.
- `docs/invariants.md` gains a row appended at the end of the `## firefox` table, after the media-preview row and before `## gtk`: the Page Info dialog's meta and image trees (`tree#metatree`, `tree#imagetree`) are the opaque `#FFFFFF` sunken list field — square corners, a 1px `#000000` outline, the `inset 1px 1px #999999` top-left shadow and black text — with rows transparent over the field so no hover wash paints, a selected row flat `#CCCCFF` with black text, and the Media panel's broken-image rows keeping their italic `graytext`, while the column headers, the rows' stock border and min-height, the cells, twisties, splitters, sort direction and column-picker behaviour and the trees' stock margins and `#imagetree` min-height stay Firefox's, and the permission list, display fields, media preview and security tables stay their own paints. Its test column names the new scope test, and its provenance records the missing Page Info trees reference, the `widgets/lineedit.svg` (grounded in `firstboot_betawiki.png`, pinned by `tests/test_desktoptheme_lineedit.py`), `widgets/listitem.svg` and `widgets/viewitem.svg` (`test_selection_background`) anchors, the installed Firefox ESR 153.5.1 `pageInfo.xhtml`, global `tree.css` and pageinfo skin `pageInfo.css` files, the no-`multicol` fact, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing `userChrome.css` rules (including the `#viewGroup`, `#mainDeck`, `#mainDeck input`, `#permList` and, when it has landed, `#imagecontainerbox` paints), the Firefox install and their tests keep their declarations and scope.

### Firefox Platinum chrome: paint the Page Info media preview like a Platinum sunken field (planned 2026-10-26 by the plan role; independent of the waiting Page Info permission-list plan — both append at the very end of `userChrome.css`, insert their provenance paragraphs before the header's closing `*/` and trim only their own word from the shared stay-Firefox lists, so either order merges) — done 2026-10-27 by the feature role

**Goal.** Make the Media panel's preview pane read as a Platinum sunken field: the `vbox#imagecontainerbox` container — the pane holding the embedded preview and the broken-image placeholder — becomes the opaque `#FFFFFF` field the deck's display fields use, with square corners, a 1px `#000000` outline, the `inset 1px 1px #999999` top-left shadow and black text, replacing Firefox's `Field` background and `1px ThreeDLightShadow` border. The pane is a static preview surface, so there is no hover, focus or selected variant. The embedded `browser#mediaBrowser`, the `hbox#brokenimagecontainer`/`image#brokenimage` placeholder, the media table's inputs (already covered by the landed `#mainDeck input` rule), the pane's stock `margin: 0.5em` and `overflow: auto` and all geometry stay Firefox's. The deck's trees, permission list, display fields, security tables and the landed top-bar, tab and button paints are untouched.

**Grounding.** No reference screenshot shows Firefox's Page Info media preview, so the paint adapts this theme's Platinum line-edit field (platform colour adaptation 2026-10-26). The `#FFFFFF` face, 1px `#000000` outline, `#999999` sunken shadow and black text adapt `widgets/lineedit.svg` (`tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`), grounded in `macos8.6-screenshots/firstboot_betawiki.png`, and are the exact recipe the sheet's landed `#mainDeck input` rule already ships; `#imagecontainerbox` is the deck's preview-shaped surface, so the same field recipe applies. In the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/pageinfo/pageInfo.xhtml` defines `vbox#imagecontainerbox` (flex child of `vbox#mediaPreviewBox` in the Media panel) holding `hbox#theimagecontainer` with `browser#mediaBrowser` and collapsed `hbox#brokenimagecontainer` with `image#brokenimage`; `chrome/browser/skin/classic/browser/pageInfo.css` gives it `margin: 0.5em`, a `Field` background, `overflow: auto` and a `1px solid ThreeDLightShadow` border with no `-moz-default-appearance`, so the CSS declarations override the stock paint with no `appearance` declaration needed; the content copy `chrome/browser/content/browser/pageinfo/pageInfo.css` only sets its `min-width`/`min-height`. `#imagecontainerbox` appears only in page-info files, so the rule cannot leak into browser chrome. Declaration checks do not establish rendered pixels.

**Approach.** Append at the very end of `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the `#mainDeck input` rule, one short comment naming the adaptation and this rule:

```css
#imagecontainerbox {
  background-color: #FFFFFF !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #999999 !important;
}
```

Keep the stock `margin: 0.5em` and `overflow: auto` and every child's own paint. Add no rule for `#mediaPreviewBox`, `#theimagecontainer`, `#mediaBrowser`, `#brokenimagecontainer`, `#brokenimage`, `#mediaTable`, the media panel's labels, inputs or buttons, and change no existing selector. In the header comment block, insert a media-preview provenance paragraph immediately before the closing `*/`: no reference shows Firefox's Page Info media preview; the `#FFFFFF` face, 1px `#000000` outline, `#999999` sunken shadow and black text adapt `widgets/lineedit.svg` (grounded in `firstboot_betawiki.png` and pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`) and reuse the landed `#mainDeck input` recipe; `pageInfo.xhtml` defines the pane holding `#mediaBrowser` and the `#brokenimagecontainer` placeholder and the skin's `pageInfo.css` owns the stock `Field` background and `ThreeDLightShadow` border; declaration checks do not establish rendered pixels (platform colour adaptation 2026-10-26). Also trim the words `media preview` from the stay-Firefox surface lists in the two existing Page Info texts — the header's top-bar provenance paragraph ("…the dialog body, meta and image trees, permission list, media preview, security tables, description labels and focus rings stay Firefox's…") and the `#topBar` rule's leading comment ("…the dialog body, fields, trees, permission list, media preview, security tables and labels keep Firefox's own paint…") — leaving every other word of both lists unchanged (the waiting permission-list plan trims `permission list` from the same sentences; it has since landed and already trims `permission list` from the same phrases).

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py`, `tests/test_firefox_theme_page_info.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` gains exactly one new selector, `#imagecontainerbox`, carrying exactly the five declarations above; every existing selector keeps its declarations, and `test_palette_is_exact` keeps its expected hex set because the rule introduces no new hex literal (the constants the rules already use only).
- `REQUIRED_RULES` in `tests/support/firefox_chrome_cases.py` gains, appended immediately after the `REQUIRED_RULES["#mainDeck input"]` assignment, `REQUIRED_RULES["#imagecontainerbox"]` mapping to `background-color: {WHITE} !important`, `color: {BLACK} !important`, `border: 1px solid {BLACK} !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px {GREY} !important`, using the constants `support.platinum_palette` already exports.
- New `TestFirefoxPageInfo.test_page_info_media_preview_paint_is_scoped_to_page_info`, placed immediately after `test_page_info_field_paint_is_scoped_to_page_info`: asserts `self.rules["#imagecontainerbox"]` equals its `REQUIRED_RULES` entry. Using `support.selector_matching.element`/`matches`, build `window` holding `deck#mainDeck` with `vbox#mediaPreviewBox`, inside it `vbox#imagecontainerbox` holding `hbox#theimagecontainer` with `browser#mediaBrowser` and `hbox#brokenimagecontainer` with `image#brokenimage`. Assert the container matches with and without `hover: true` (no hover or focus variant), `#mediaBrowser` and `#brokenimage` match no selector whose name contains `imagecontainerbox`, and stray surfaces — a `textbox` in the findbar, `input#editBMPanel_locationField`, `input#searchbar-textbox` and `input#urltext` — match none of the rule names containing `imagecontainerbox`. Assert the rule names containing `imagecontainerbox` are exactly `["#imagecontainerbox"]`, and that no `"#imagecontainerbox:hover"`, `"#imagecontainerbox:focus"` or `"#mediaPreviewBox"` selector exists in `self.rules`.
- New `TestFirefoxPageInfo.test_page_info_media_preview_provenance`, placed immediately after `test_page_info_field_provenance`, asserts the leading comment names `"No reference shows Firefox's Page Info media preview"`, `"#imagecontainerbox"`, `"widgets/lineedit.svg"`, `"firstboot_betawiki.png"`, `"tests/test_desktoptheme_lineedit.py::TestLineEdit"`, `"TestLineEditReference"`, `"#mainDeck input"`, `"pageInfo.xhtml"`, `"#mediaBrowser"`, `"#brokenimagecontainer"`, `"pageInfo.css"`, `"Field"`, `"ThreeDLightShadow"`, `"no hover, focus or selected variant"`, `"platform colour adaptation 2026-10-26"` and `"Declaration checks do not establish rendered pixels"`. Leave `test_page_info_provenance`, `test_page_info_field_paint_is_scoped_to_page_info` and `test_page_info_field_provenance` untouched so this plan does not edit their bodies.
- `docs/invariants.md` gains a row appended at the end of the `## firefox` table, after the last Page Info row and before `## gtk`: the Media panel's preview pane (`vbox#imagecontainerbox`) is the opaque `#FFFFFF` sunken field — square corners, a 1px `#000000` outline, the `inset 1px 1px #999999` top-left shadow and black text, with no stock `ThreeDLightShadow` border and no hover, focus or selected variant — while the embedded `#mediaBrowser`, the `#brokenimagecontainer` placeholder, the media table's inputs (still the `#mainDeck input` paint) and labels stay Firefox's, and the trees and security tables stay Firefox's. Its test column names the new scope test, and its provenance records the missing Page Info media-preview reference, the `widgets/lineedit.svg` anchor (grounded in `firstboot_betawiki.png` and pinned by `tests/test_desktoptheme_lineedit.py`), the installed Firefox ESR 153.5.1 `pageInfo.xhtml` and skin `pageInfo.css` files, and that declaration checks do not establish rendered pixels. In the `## firefox` table's Page Info top-bar row, Page Info fields row and Page Info permission-list row, drop `media preview` from the lists of surfaces whose guarantees say they stay Firefox's. `tests/invariants.py` stays green.
- `make check` passes, and the existing `userChrome.css` rules (including the `#viewGroup`, `#mainDeck`, `#mainDeck input` and, if it has landed, `#permList` paints), the Firefox install and their tests keep their declarations and scope.

### Kvantum Platinum toolbox tabs: paint a QToolBox's tabs with the reference-grounded Platinum tab face (planned 2026-10-26 by the plan role; independent of the waiting downloads-panel-buttons chrome plan) — done 2026-10-26 by the feature role

**Goal.** Make a Qt toolbox's tabs read as Platinum. `org.macos8.desktop.kvconfig` defines no `[ToolboxTab]` section, so a `QToolBox` falls back to Kvantum's compiled-in tab paint instead of the reference-grounded tab face the config already draws for `[Tab]`. Add the section and point it at the existing `[Tab]` surface, so a toolbox's selected and unselected tabs use the same Platinum `#CCCCCC`/`#EEEEEE` tab art, 2px frame margin and 8px side text margins as the theme's tab bars.

**Grounding.** No reference screenshot shows a Qt `QToolBox`, so the `[ToolboxTab]` section name is Kvantum-required: the installed KvantumAlt theme defines `[ToolboxTab]` with `inherits=PanelButtonCommand` in `/usr/share/Kvantum/KvantumAlt/KvantumAlt.kvconfig`. Drawing it from the existing tab surface adapts the reference-grounded System Profiler tab face (`tests/test_kvantum_tab_reference.py::TestTabReference`) rather than introducing new art or a new palette value.

**Approach.** In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, insert the section immediately after `[Tab]` and before `[TabFrame]`, with `inherits=Tab` as its only key, and extend the container/text-surface comment paragraph to say tabs (including Qt toolbox tabs) draw the same raised Platinum face. In `tests/support/kvantum_config_spec.py`, add `"ToolboxTab": 2` to `CORE_FRAME_MARGINS` immediately after `"Tab"`, and add this entry to `SURFACE_CONTROL_CONFIG` immediately after `"Tab"`:

```python
"ToolboxTab": {
    "frame.element": "tab",
    "interior.element": "tab",
    "indicator.element": "tab",
},
```

No SVG, palette or value-key change: every mapping and margin resolves through `inherits=Tab` to the existing pinned values.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, `tests/support/kvantum_config_spec.py`, `tests/test_kvantum_config_elements.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- The `.kvconfig` has exactly one `[ToolboxTab]` section, positioned between `[Tab]` and `[TabFrame]`, whose options are exactly `{"inherits": "Tab"}`; the container/text-surface comment names toolbox tabs.
- `CORE_FRAME_MARGINS` contains `"ToolboxTab": 2` and `SURFACE_CONTROL_CONFIG` contains the `"ToolboxTab"` mapping above. The existing `TestSectionCoverage.test_every_section_is_pinned`, `TestCoreControlElements.test_every_core_section_mapping_is_pinned`, `TestSurfaceElements.test_every_surface_section_maps_to_its_element`, `TestFrameMargins.test_every_core_section_resolves_to_the_expected_frame_margin` and `TestValueKeys.test_every_key_is_pinned` pass unchanged, because the new section adds no non-`inherits` key.
- New `TestToolboxTabSurface.test_toolbox_tab_inherits_the_tab_surface` in `tests/test_kvantum_config_elements.py`, placed after `TestSurfaceElements`, reads `KVCONFIG` through `support.kde_config.read` and asserts `parser.get("ToolboxTab", "inherits") == "Tab"`, `set(parser.options("ToolboxTab")) == {"inherits"}`, and that for `frame.element`, `interior.element`, `indicator.element`, the four `frame.*` margins and `text.margin.left`/`text.margin.right`, `_resolved(parser, "ToolboxTab", key)` equals `_resolved(parser, "Tab", key)`.
- `docs/invariants.md` gains a row in `## kvantum` immediately after the row beginning "The tab face is the reference System Profiler tabs'": the Qt toolbox tab (`[ToolboxTab]`) draws the same reference-grounded Platinum tab face as `[Tab]`, inheriting its frame, interior and indicator art, 2px frame margin and 8px side text margins. Its test column names `tests/test_kvantum_config_elements.py::TestToolboxTabSurface`, `tests/test_kvantum_config_elements.py::TestSurfaceElements`, `tests/test_kvantum_config.py::TestSectionCoverage` and `tests/test_kvantum_config.py::TestFrameMargins`; its provenance records that no reference screenshot shows a Qt QToolBox, that `[ToolboxTab]` is Kvantum-required (the installed KvantumAlt theme defines it), that the mapping adapts the reference-grounded tab face pinned by `tests/test_kvantum_tab_reference.py::TestTabReference`, and that config checks do not establish rendered Qt pixels. `tests/invariants.py` stays green.
- `README.md`: in the Kvantum paragraph's control list, add toolbox tabs alongside the toolbar buttons, toolbar combo boxes and line edits, split-button dropdowns, tree-view expanders and status bar that map onto the shipped Platinum art.
- `make check` passes, and every existing Kvantum section, element, frame-margin and palette assertion keeps its expected value.

### Firefox Platinum chrome: paint the Page Info permission list like a Platinum list (planned 2026-10-26 by the plan role; independent of the waiting Kvantum toolbox-tab plan, whose done stamp still sits in `## Planned` awaiting the move to PLANS-DONE.md) — done 2026-10-26 by the feature role

**Goal.** Make the Permissions panel's permission list read as a Platinum list: the `vbox#permList` container becomes the opaque `#FFFFFF` sunken field the deck's display fields use — square corners, a 1px `#000000` outline and the `inset 1px 1px #999999` top-left shadow — with the native listbox frame dropped and black text; a hovered `.permission` row keeps the field's face with a transparent background and black text instead of Firefox's `-moz-dialog` wash, honouring the reference theme's no-hover-highlight list behaviour. The rows' bold labels, use-default checkboxes, per-state radios, dotted bottom separators, padding and geometry stay Firefox's. The deck's trees, media preview, display fields, security tables and the landed top-bar, tab and button paints are untouched.

**Grounding.** No reference screenshot shows Firefox's Page Info permission list, so the paint adapts this theme's Platinum list (platform colour adaptation 2026-10-26). The `#FFFFFF` face and `#999999` sunken shadow adapt `widgets/lineedit.svg` (`tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`), grounded in `macos8.6-screenshots/firstboot_betawiki.png`, and are the exact recipe the sheet's landed `#mainDeck input` rule already ships; `#permList` is the deck's second list-shaped surface after that field rule, so the same face applies. The transparent hover and plain rows adapt `widgets/listitem.svg` (`tests/test_desktoptheme_listitem.py::TestListItem`), whose comment records that Mac OS 8.6 lists have no hover highlight, matching the GTK sheets' row mapping and this sheet's about:config table, whose `#prefs > tr:hover` rule paints hovered rows transparent. Dropping the native frame reuses the sheet's `#viewGroup > radio` precedent (`appearance: none !important`).

In the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/pageinfo/pageInfo.xhtml` defines `vbox#permPanel` holding the empty `vbox#permList`, and `chrome/browser/content/browser/pageinfo/permissions.js`'s `createRow` builds each permission row at runtime as a `vbox.permission` containing `label.permissionLabel`, a `hbox` with a `native` checkbox and a horizontal `radiogroup`, appending it to `permList`; rows have no selectable or selected state. `chrome/browser/skin/classic/browser/pageInfo.css` gives `#permList` `appearance: auto` (`-moz-default-appearance: listbox`), `-moz-dialog`-independent `Field` background, `FieldText` text, a 1px `ThreeDShadow` border and `0.5em` margins, paints `.permission` with `6px 7px` padding and a dotted `ThreeDShadow` bottom border, and paints `.permission:hover` with `-moz-dialog` background and `-moz-DialogText` text. `#permList` is page-info-only, so the rules cannot leak into browser chrome. Declaration checks do not establish rendered pixels.

**Approach.** Append at the very end of `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the `#mainDeck input` rule, one short comment naming the adaptation and these two rules:

```css
#permList {
  appearance: none !important;
  background-color: #FFFFFF !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #999999 !important;
}

#permList .permission:hover {
  background-color: transparent !important;
  color: #000000 !important;
}
```

`appearance: none` drops the stock `-moz-default-appearance: listbox` native frame, so the CSS border stands in. Keep the stock `margin: 0.5em` and `overflow: auto`, the rows' `6px 7px` padding and `1px dotted ThreeDShadow` bottom separators, and every row's label, checkbox, radios and geometry. Add no rule for `.permissionLabel`, the checkbox, the radios, `#permPanel`'s labels, `#hostText` (already covered by `#mainDeck input`), the trees, the media preview or the security tables, add no selected or pressed variant (rows have none), and change no existing selector. In the header comment block, insert a permission-list provenance paragraph immediately after the Page Info fields paragraph and before the closing `*/`: no reference shows Firefox's Page Info permission list; the `#FFFFFF` face and `#999999` sunken shadow adapt `widgets/lineedit.svg` and the `#mainDeck input` recipe, the transparent hover honours `widgets/listitem.svg`'s no-hover-highlight list reading, `permissions.js`'s `createRow` builds the rows and `pageInfo.css` owns the stock `-moz-default-appearance: listbox` paint and the `-moz-dialog` hover wash; declaration checks do not establish rendered pixels (platform colour adaptation 2026-10-26). Also trim the word `permission list` from the stay-Firefox surface lists in the two existing Page Info texts — the header's top-bar provenance paragraph ("…the dialog body, meta and image trees, permission list, media preview, security tables, description labels and focus rings stay Firefox's…") and the `#topBar` rule's leading comment ("…the dialog body, fields, trees, permission list, media preview, security tables and labels keep Firefox's own paint…") — leaving every other word of both lists unchanged.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` gains exactly two new selectors, `#permList` and `#permList .permission:hover`, carrying exactly the declarations above (including `#permList`'s `appearance: none !important`); every existing selector keeps its declarations, and `test_palette_is_exact` keeps its expected hex set because the rules introduce no new hex literal (`transparent` and the existing palette constants only).
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains, appended after the `"#mainDeck input"` entry, `"#permList"` mapping to `appearance: none !important`, `background-color: {WHITE} !important`, `color: {BLACK} !important`, `border: 1px solid {BLACK} !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px {GREY} !important`, and `"#permList .permission:hover"` mapping to `background-color: transparent !important` and `color: {BLACK} !important`, with the constants `support.platinum_palette` already exports.
- New `TestFirefoxChrome.test_page_info_permission_list_paint_is_scoped_to_page_info`, placed immediately after `test_page_info_field_provenance`: asserts the rule names containing `permList` or `.permission` outside the permission-popup selectors are exactly those two (the permission-popup button names also contain `.permission`), each equals its `REQUIRED_RULES` entry, and the hover selector carries `:hover` with no bevel declaration. Using `support.selector_matching.element`/`matches`, build `window` holding `deck#mainDeck` with `vbox#permPanel`, inside it `vbox#permList` and one `vbox.permission` row containing `label.permissionLabel` and a `radiogroup`, plus `vbox#securityPanel` holding `input#hostText`. Assert the row matches `#permList .permission:hover` only when `hover` is true (with and without, it matches no `#permList` container rule, which is a container selector), `#hostText` matches `#mainDeck input` and neither perm-list rule, and a `vbox.permission` row inside a `vbox#otherList` that is not `#permList` matches neither rule.
- New `TestFirefoxChrome.test_page_info_permission_list_provenance`, placed immediately after the scope test, asserts the leading comment names `"No reference shows Firefox's Page Info permission list"`, `"widgets/lineedit.svg"`, `"firstboot_betawiki.png"`, `"tests/test_desktoptheme_lineedit.py::TestLineEdit"`, `"TestLineEditReference"`, `"#mainDeck input"`, `"widgets/listitem.svg"`, `"tests/test_desktoptheme_listitem.py::TestListItem"`, `"no hover highlight"`, `"#prefs > tr:hover"`, `"permissions.js"`, `"createRow"`, `"pageInfo.css"`, `"-moz-default-appearance: listbox"`, `"-moz-dialog"`, `"#permList"`, `".permission"` and `"platform colour adaptation 2026-10-26"`. Leave `test_page_info_provenance` and `test_page_info_field_provenance` untouched so this plan does not edit their tuples.
- `docs/invariants.md` gains a row appended at the end of the `## firefox` table, after the Page Info fields row and before `## gtk`: the Permissions panel's permission list (`vbox#permList`) is the opaque `#FFFFFF` sunken list field — square corners, a 1px `#000000` outline, the `inset 1px 1px #999999` top-left shadow and black text, with no native listbox frame — and a hovered `.permission` row keeps the field's face with a transparent background and black text instead of the `-moz-dialog` wash, while rows keep Firefox's dotted bottom separators, padding, bold labels, use-default checkboxes and per-state radios, and the trees, media preview, display fields and security tables stay Firefox's. Its test column names the new scope test, and its provenance records the missing Page Info permission-list reference, the `widgets/lineedit.svg` (grounded in `firstboot_betawiki.png` and pinned by `tests/test_desktoptheme_lineedit.py`) and `widgets/listitem.svg` anchors, the installed Firefox ESR 153.5.1 `pageInfo.xhtml`, `permissions.js` (`createRow`) and `pageInfo.css` files, and that declaration checks do not establish rendered pixels. In the `## firefox` table's Page Info top-bar row, drop the permission list from the list of surfaces whose guarantee says they stay Firefox's. `tests/invariants.py` stays green.
- `make check` passes, and the existing `userChrome.css` rules (including the `#viewGroup`, `#mainDeck` and `#mainDeck input` paints), the Firefox install and their tests keep their declarations and scope.
- Implementation note: the plan's rule-name criterion also matched the permission-popup button selectors, so the scope test excludes `permission-popup` names from the `.permission` filter, and the two Page Info header/rule comments plus the invariants fields row drop the permission list from their stay-Firefox surface lists along with the top-bar row. Each changed note names the permission list's own provenance paragraph/row.

### Firefox Platinum chrome: paint the Page Info dialog's readonly display fields as Platinum line edits (planned 2026-10-26 by the plan role; independent of every other plan — `## Planned` holds nothing else) — done 2026-10-26 by the feature role

**Goal.** Finish the Page Info window's fields: the landed top-bar plan (PLANS-DONE.md, "paint the Page Info dialog's view tabs and action buttons") deliberately left the panels' readonly `input` display fields Firefox's, so the General, Media, Permissions and Security panels show stock form-field chrome inside the Platinum top band. Give every display field in the dialog body the reference-grounded Platinum line-edit paint — an opaque `#FFFFFF` face, black text, a square 1px `#000000` outline and the `#999999` sunken top-left inner shadow — as the sheet already does for the find field and the bookmark editor's fields.

**Grounding.** The field recipe adapts `theme/desktoptheme/org.macos8.desktop/widgets/lineedit.svg`, which is grounded in `macos8.6-screenshots/firstboot_betawiki.png` (the Setup Assistant body text field: 1px `#000000` outline, `#999999` top/left shadow, `#FFFFFF` bottom/right highlight) and pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`. No reference screenshot shows Firefox's Page Info window, so the paint is a platform adaptation; the same `inset 1px 1px #999999` recipe is already shipped by this sheet's `findbar .findbar-textbox` and `#editBookmarkPanel` field rules.

In the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/pageinfo/pageInfo.xhtml` defines every display field as an HTML `input` (most `readonly="readonly"`; `#imagetypetext` is JS-managed without the attribute) inside `deck#mainDeck`'s four panels — `#titletext`, `#urltext`, `#typetext`, `#modetext`, `#encodingtext`, `#sizetext`, `#refertext`, `#modifiedtext`, `#imageurltext`, `#imagetypetext`, `#imagesizetext`, `#imagedimensiontext`, `#imagetext`, `#imagelongdesctext`, the `html:input#hostText` permission header, and the security panel's `#security-identity-domain-value`, `#security-identity-owner-value`, `#security-identity-verifier-value` and `#security-identity-validity-value`. `chrome/browser/skin/classic/browser/pageInfo.css` only sets the fields' widths and block margins (`th > label, td > input { width: -moz-available; margin-block: 1px 4px; }`); their face, border and corners come from the HTML form UA styles, so one `#mainDeck input` rule recolours them all without touching geometry. `#mainDeck` is page-info-only, so the rule cannot leak into browser chrome.

**Approach.** Append at the very end of `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the Page Info button-hover rules, one short comment naming the adaptation and this rule:

```css
#mainDeck input {
  background-color: #FFFFFF !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #999999 !important;
}
```

No hover, focus or `:not([readonly])` variant: every `input` in the deck is a display field, and a focused readonly field keeps Firefox's focus ring. Add no rule for the panels' labels, trees (`#metatree`, `#imagetree`), the permission list, the media preview, the security tables, `#mainDeck`'s padding or any other element, and do not change the `:root` block or any existing selector. In the leading comment block, append a Page Info fields provenance paragraph before the closing `*/`: no reference shows Firefox's Page Info window; the display fields adapt `widgets/lineedit.svg` grounded in `firstboot_betawiki.png` and pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`, with black text from the shared Platinum foreground; `pageInfo.xhtml` defines the inputs and `pageInfo.css` owns their widths and margins; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` gains exactly one new selector, `#mainDeck input`, with exactly the five declarations above; every existing selector keeps its declarations.
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the `"#mainDeck input"` entry appended after the Page Info hover rules (beside the `_PAGE_INFO_CONTROL_IDS` loops), mapping to `background-color: {WHITE} !important`, `color: {BLACK} !important`, `border: 1px solid {BLACK} !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px {GREY} !important` (the constants `support.platinum_palette` already exports). `test_palette_is_exact` keeps its expected hex set unchanged because the rule introduces no new hex literal.
- New `TestFirefoxChrome.test_page_info_field_paint_is_scoped_to_page_info`, placed immediately after `test_page_info_provenance`: using `support.selector_matching.element`/`matches`, build a page-info tree — `deck#mainDeck` holding a panel with `input#titletext`, `input#imagetypetext` (no `readonly` attribute) and `html:input#hostText` — and assert each matches the `#mainDeck input` rule and that a focused one still matches (no state variants exist). Build the sheet's other fields — a `findbar .findbar-textbox`, `#editBookmarkPanel #editBMPanel_locationField`, `#searchbar` — and an `input` under `#navigator-toolbox`, and assert none matches the new rule. Assert `REQUIRED_RULES` contains no other `#mainDeck input` selector (no hover or focus variant).
- New `TestFirefoxChrome.test_page_info_field_provenance`, placed immediately after the scope test, asserts the leading comment names `"widgets/lineedit.svg"`, `"firstboot_betawiki.png"`, `"tests/test_desktoptheme_lineedit.py::TestLineEdit"`, `"TestLineEditReference"`, `"pageInfo.xhtml"`, `"pageInfo.css"`, `"#mainDeck input"`, `"#titletext"` and `"platform adaptation 2026-10-26"`. Leave `test_page_info_provenance` and `test_header_names_provenance_and_preference` untouched.
- `docs/invariants.md` gains a row appended at the end of the `## firefox` table, after the Page Info top-bar row and before `## gtk`: the Page Info panels' display fields (`#mainDeck input`, including `#titletext` and `#hostText`) are Platinum line edits — an opaque `#FFFFFF` face, black text, a square 1px `#000000` outline and the `#999999` sunken top-left inner shadow, with no hover or focus variant — while a focused field keeps Firefox's focus ring and the trees, permission list, media preview, security tables and labels stay Firefox's. Its test column names the new scope test; its provenance records the missing Page Info reference, the `widgets/lineedit.svg` anchor grounded in `firstboot_betawiki.png` and pinned by `tests/test_desktoptheme_lineedit.py`, the installed Firefox ESR 153.5.1 `pageInfo.xhtml`/`pageInfo.css` files, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing `userChrome.css` rules, the Firefox install and their tests keep their declarations and scope.

### Firefox Platinum chrome: paint the Page Info dialog's view tabs and action buttons as Platinum controls (planned 2026-10-26 by the plan role; independent of the waiting Kvantum toolbox-tab plan) — done 2026-10-26 by the feature role

**Goal.** Make Firefox's Page Info window read as Platinum: its top band (`#topBar`) becomes the grey `#DDDDDD` Platinum toolbar with the etched `#888888`/`#FFFFFF` bottom rule; its three view-tab states (`#viewGroup > radio`) become the sheet's Platinum tab faces — unselected raised `#DDDDDD` with black text, a square 1px black outline and the white/`#999999` bevel; selected flat `#EEEEEE` with its bottom border merged into the face; an unselected hovered tab flat `#EEEEEE`. Its plain action buttons — the `.help-button` in each panel, the media panel's `#selectallbutton`, `#imagesaveasbutton` and `#mediasaveasbutton`, and the security panel's `#security-view-qwac`, `#security-view-cert`, `#security-clear-sitedata` and `#security-view-password` — become square `#DDDDDD` push buttons with a black outline and the reference's white/`#AAAAAA` raised bevel; an enabled hovered one is flat `#CCCCFF` with black text and no bevel, while a disabled one keeps Firefox's disabled face. The dialog body, readonly `input` fields, meta/image trees, permission list, media preview, security tables, description labels, permission rows and focus rings stay Firefox's.

**Grounding.** No reference screenshot shows Firefox's Page Info window, so the paint adapts this theme's Platinum controls (platform adaptation 2026-10-26). The tab face and top band copy the sheet's existing `.tab-background` and `#nav-bar`/`#TabsToolbar` recipes: the raised face adapts the reference-grounded `widgets/tabbar.svg` (`tests/test_desktoptheme_tabbar.py::TestTabBar`, `tests/test_desktoptheme_tabbar.py::TestTabBarReference`), the `#EEEEEE` trough is the pinned `[Colors:View] BackgroundAlternate` (`tests/test_colorscheme_reference.py::TestReferenceAnchors::test_view_background_alternate`), and the etched pair is re-derived by `tests/test_desktoptheme_line.py::TestLineReference`. The push-button face, outline and white/`#AAAAAA` bevel adapt `widgets/button.svg` (`tests/test_desktoptheme_button.py::TestButton`, `tests/test_desktoptheme_button_reference.py::TestButtonReference`), and the flat `#CCCCFF` hover adapts `widgets/viewitem.svg` (`tests/test_desktoptheme_viewitem.py::TestViewItem`, `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`).

In the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/pageinfo/pageInfo.xhtml` defines `vbox#topBar` holding `radiogroup#viewGroup.chromeclass-toolbar` with the `radio` tabs `#generalTab`, `#mediaTab` (hidden by default), `#permTab` and `#securityTab`; `deck#mainDeck` holds `#generalPanel`, `#mediaPanel`, `#permPanel` and `#securityPanel`; each panel ends in a `button.help-button` carrying `command="cmd_help"`, the media panel adds `#selectallbutton`, `#imagesaveasbutton` and `#mediasaveasbutton`, and the security panel adds `#security-view-qwac`, `#security-view-cert`, `#security-clear-sitedata` and `#security-view-password`. `chrome/browser/content/browser/pageinfo/pageInfo.js` selects a view by setting `selected` on its tab and swapping the deck, and `chrome/browser/skin/classic/browser/pageInfo.css` gives the non-macOS Linux build `#topBar` the Field background and ThreeDShadow bottom border and `#viewGroup > radio` `appearance: none`, a 4.5em minimum width, 3px padding and black `FieldText`, painting `#viewGroup > radio[selected]` with SelectedItem; the native anonymous radio glyph is already suppressed there. The sheet is loaded in every chrome document, so the new rules are scoped through the page-info-only ids `#topBar`, `#viewGroup` and `#mainDeck`. Declaration checks do not establish rendered pixels.

**Approach.** Append at the very end of `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the bookmark-editor rules, one short comment naming the adaptation and these rules, each selector on one line:

```css
#topBar {
  background-color: #DDDDDD !important;
  border-bottom: 1px solid #888888 !important;
  box-shadow: inset 0 -1px #FFFFFF !important;
}

#viewGroup > radio {
  appearance: none !important;
  background-color: #DDDDDD !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999 !important;
}

#viewGroup > radio[selected] {
  background-color: #EEEEEE !important;
  border-bottom-color: #EEEEEE !important;
}

#viewGroup > radio:not([selected]):hover {
  background-color: #EEEEEE !important;
}

#mainDeck .help-button:not([disabled]),
#mainDeck #selectallbutton:not([disabled]),
#mainDeck #imagesaveasbutton:not([disabled]),
#mainDeck #mediasaveasbutton:not([disabled]),
#mainDeck #security-view-qwac:not([disabled]),
#mainDeck #security-view-cert:not([disabled]),
#mainDeck #security-clear-sitedata:not([disabled]),
#mainDeck #security-view-password:not([disabled]) {
  background-color: #DDDDDD !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
}

#mainDeck .help-button:not([disabled]):hover,
#mainDeck #selectallbutton:not([disabled]):hover,
#mainDeck #imagesaveasbutton:not([disabled]):hover,
#mainDeck #mediasaveasbutton:not([disabled]):hover,
#mainDeck #security-view-qwac:not([disabled]):hover,
#mainDeck #security-view-cert:not([disabled]):hover,
#mainDeck #security-clear-sitedata:not([disabled]):hover,
#mainDeck #security-view-password:not([disabled]):hover {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Leave the tabs' stock minimum width and padding in place and set no `outline`, so focus keeps Firefox's ring. Add no rule for the deck, panels, `input` fields, trees, permission list, media preview, security tables or labels, and do not change the `:root` block, the `.tab-background` rules or any existing selector. In the leading comment block, append a Page Info provenance paragraph before the closing `*/`: no reference shows Firefox's Page Info window; the tab and top band adapt `widgets/tabbar.svg` and the pinned `#EEEEEE` trough, and the buttons adapt `widgets/button.svg` and its white/`#AAAAAA` bevel, with the flat `#CCCCFF` hover from `widgets/viewitem.svg`; `pageInfo.xhtml` defines the ids, `pageInfo.js` swaps the deck and `pageInfo.css` owns the stock paint; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` gains exactly the twenty selectors above (one `#topBar`, three `#viewGroup` tab rules, eight button rules and eight hover rules) and no other new selector. Every existing selector keeps its declarations.
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains those twenty selectors, appended at the end of the dict and built from the constants the module already imports: `#topBar` is exactly `background-color: FACE !important`, `border-bottom: 1px solid ETCH_DARK !important` and `box-shadow: inset 0 -1px WHITE !important`; the base tab rule is exactly `appearance: none !important`, `background-color: FACE !important`, `color: BLACK !important`, `border: 1px solid BLACK !important`, `border-radius: 0 !important` and `box-shadow: RAISED_BEVEL !important`; the selected rule is exactly `background-color: TROUGH !important` and `border-bottom-color: TROUGH !important`; the hover rule is exactly `background-color: TROUGH !important`; each of the eight button selectors is exactly `background-color: FACE !important`, `color: BLACK !important`, `border: 1px solid BLACK !important`, `border-radius: 0 !important` and `box-shadow: BUTTON_BEVEL !important`; each of the eight hover selectors is exactly `background-color: SELECTION !important`, `color: BLACK !important` and `box-shadow: none !important`. `test_palette_is_exact` keeps its expected hex set unchanged because the rules introduce no new hex literal.
- New `TestFirefoxChrome.test_page_info_control_paint_is_scoped_to_page_info`, placed immediately before `test_readme_names_the_sheet`, asserts the rule names containing `#topBar`, `#viewGroup` or `#mainDeck` are exactly those twenty, each equals its `REQUIRED_RULES` entry, and the selected and hover rules do not paint the wrong state. Using `support.selector_matching.element`/`matches`, build a page-info tree: a window holding `vbox#topBar` with `radiogroup#viewGroup.chromeclass-toolbar` and the four `radio` tabs, and `deck#mainDeck` holding panels with a `.help-button`, the three media ids and the four security ids. Assert every tab matches the base rule, a selected tab matches the selected rule, a hovered unselected tab matches the hover rule, a selected hovered tab does not match the hover rule, each button matches its enabled selector and, when hovered, its hover selector but not when idle, and a disabled button matches neither. Assert the deck's `input#titletext`, `input#urltext`, `tree#metatree`, `tree#imagetree`, permission rows and labels match none of the twenty, and that an identically named `#selectallbutton` or `.help-button` outside `#mainDeck` and a `#navigator-toolbox` outside `#topBar` match none.
- New `TestFirefoxChrome.test_page_info_provenance`, placed immediately after the scope test, asserts the leading comment names `"No reference shows Firefox's Page Info window"`, `"widgets/tabbar.svg"`, `"tests/test_desktoptheme_tabbar.py::TestTabBar"`, `"tests/test_desktoptheme_tabbar.py::TestTabBarReference"`, `"tests/test_desktoptheme_line.py::TestLineReference"`, `"test_view_background_alternate"`, `"widgets/button.svg"`, `"tests/test_desktoptheme_button.py::TestButton"`, `"tests/test_desktoptheme_button_reference.py::TestButtonReference"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"pageInfo.xhtml"`, `"pageInfo.js"`, `"pageInfo.css"`, `"#topBar"`, `"#viewGroup"`, `"#mainDeck"`, `"#generalTab"`, `"#selectallbutton"`, `"#security-view-qwac"` and `"platform adaptation 2026-10-26"`. Leave `test_header_names_provenance_and_preference` untouched so this plan and the waiting toolbox-tab plan do not edit the same tuple.
- `docs/invariants.md` gains a row appended at the end of the `## firefox` table, after the bookmark-editor row and before `## gtk`: the Page Info window's `#topBar` is the grey `#DDDDDD` Platinum toolbar with the etched `#888888`/`#FFFFFF` bottom rule, its `#viewGroup` view tabs are the Platinum tab faces (unselected raised `#DDDDDD` with black text, a square 1px black outline and the white/`#999999` bevel; selected flat `#EEEEEE` with the bottom border merged; unselected hovered flat `#EEEEEE`), and its `.help-button` and eight media/security action ids are square `#DDDDDD` push buttons with a black outline and the white/`#AAAAAA` bevel, an enabled hovered one being flat `#CCCCFF` with black text and no bevel, while a disabled button, the dialog body, fields, trees, permission list, media preview, security tables and labels stay Firefox's. Its test column names the new scope test, and its provenance records the missing Page Info reference, the `widgets/tabbar.svg`, `widgets/button.svg` and `widgets/viewitem.svg` anchors, the installed Firefox ESR 153.5.1 files above, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing `userChrome.css` rules, the Firefox install and their tests keep their declarations and scope.

### Firefox Platinum chrome: paint the downloads panel's footer and action buttons as Platinum push buttons (planned 2026-10-26 by the plan role; independent of the waiting about:config content plan) — done 2026-10-26 by the feature role

**Goal.** Make the downloads panel's buttons read as Platinum: in `#downloadsPanel`, the Show All Downloads footer button (`#downloadsHistory`), each row's action button (`button.downloadButton`), and the blocked and private subviews' footer buttons (`html:moz-button-group#downloadsPanel-blockedSubview-buttons .footer-button` and the two `.footer-button`s in `#downloadsPanel-privateBrowsing`) become square `#DDDDDD` push-button faces with a 1px black outline and the reference's white/`#AAAAAA` raised bevel; an enabled hovered one is flat `#CCCCFF` with black text and no bevel. Disabled buttons keep Firefox's disabled paint, and the panel rows, `.downloadMainArea`, the downloads summary, the panel header, the subview copy and the content-area downloads list stay as they are.

**Grounding.** No reference screenshot shows Firefox's downloads panel buttons, so the paint adapts this theme's Platinum controls (platform colour adaptation 2026-10-26). The `#DDDDDD` face, 1px black outline and white/`#AAAAAA` raised bevel adapt the reference-grounded `widgets/button.svg` (`tests/test_desktoptheme_button.py::TestButton`, `tests/test_desktoptheme_button_reference.py::TestButtonReference`), and the flat `#CCCCFF` hover adapts `widgets/viewitem.svg` (`tests/test_desktoptheme_viewitem.py::TestViewItem`, `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`). The landed downloads-panel row plan deliberately left these buttons to Firefox, so this entry completes that panel.

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<panel id="downloadsPanel" type="arrow">` with `<vbox id="downloadsFooter">`, `#downloadsFooterButtons` and `<button id="downloadsHistory" class="downloadsPanelFooterButton subviewbutton panel-subview-footer-button toolbarbutton-1">`; its `#downloadsPanel-blockedSubview` holds `<html:moz-button-group id="downloadsPanel-blockedSubview-buttons" class="panel-footer">` with `button#downloadsPanel-blockedSubview-unblockButton.footer-button` and `button#downloadsPanel-blockedSubview-deleteButton.footer-button` (`default`), and `#downloadsPanel-privateBrowsing` holds `.footer-button.secondary` and `.footer-button.primary` (`default`). `moz-src/browser/components/downloads/DownloadsViewUI.sys.mjs` builds each row's `button.downloadButton`. `chrome/browser/skin/classic/browser/downloads/downloads.inc.css` gives `.downloadButton` an `appearance: none`, 32px box, transparent border, ghost background and `--border-radius-small`, and paints `.downloadButton:hover:not(:active)` and `.downloadsPanelFooterButton:hover` from the ghost hover tokens; `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` its `appearance: none`, transparent background and `--panel-menuitem-border-radius`; and `chrome/toolkit/skin/classic/global/global-shared.css` paints `.footer-button` from the `--button-*` tokens. The sheet has no rule targeting `.downloadButton`, `.downloadsPanelFooterButton` or a `.footer-button` inside `#downloadsPanel`.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, insert these two grouped rules immediately after the existing `#downloadsPanel #downloadsListBox > richlistitem[selected]` rule and before the `panel[type="arrow"]` rule, with a short comment naming the adaptation:

```css
/* The downloads panel's footer, subview and per-row action buttons adapt the
   desktop theme's push button; disabled ones keep Firefox's paint. */
#downloadsPanel .downloadsPanelFooterButton:not([disabled]),
#downloadsPanel .downloadButton:not([disabled]),
#downloadsPanel .footer-button:not([disabled]) {
  background-color: #DDDDDD !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
}

#downloadsPanel .downloadsPanelFooterButton:not([disabled]):hover,
#downloadsPanel .downloadButton:not([disabled]):hover,
#downloadsPanel .footer-button:not([disabled]):hover {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Use `:not([disabled])` on both rules so a disabled button keeps Firefox's disabled background and text; keep the stock button geometry, padding, margins, icon and font, and add no declaration for `.downloadMainArea`, `#downloadsSummary`, `#downloadsSummaryProgress`, `#downloadsPanel-blockedSubview-title`, the panel header or the content-area downloads view. Do not add a pressed-state rule; like the sheet's other Platinum push buttons, a pressed enabled button keeps the flat `#CCCCFF` hover face with no bevel. In the header comment block, insert a downloads-panel-buttons provenance paragraph between the downloads-panel-rows paragraph (ending "declaration checks do not establish rendered pixels.") and the bookmark-editor paragraph (starting "No reference shows Firefox's bookmark editor"): no reference shows Firefox's downloads panel buttons; the `#DDDDDD`/`#CCCCFF` faces, black outline and white/`#AAAAAA` bevel adapt `widgets/button.svg` and `widgets/viewitem.svg` with the anchors above; `browser.xhtml` defines `#downloadsHistory` and the subview `.footer-button`s, `DownloadsViewUI.sys.mjs` builds the row `.downloadButton`s, `downloads.inc.css`, `panelUI-shared.css` and `global-shared.css` own the stock paint, disabled buttons keep Firefox's paint, and declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` contains exactly the two grouped rules above (six parsed selectors after the comma lists are split). `test_palette_is_exact` keeps its expected hex set because the rules introduce no new literal.
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains six entries inserted after the three downloads-row entries and before the `.tab-background` entry, with `FACE`, `SELECTION`, `BLACK`, `WHITE` and `BUTTON_SHADOW` built from the constants the module imports: the three normal selectors carry `background-color: FACE`, `color: BLACK`, `border: 1px solid BLACK`, `border-radius: 0` and `box-shadow: BUTTON_BEVEL`; the three hover selectors carry `background-color: SELECTION`, `color: BLACK` and `box-shadow: none`.
- New `TestFirefoxChrome.test_downloads_panel_button_paint_is_scoped_to_the_panel`, placed immediately after `test_downloads_panel_row_paint_is_scoped_to_the_panel_list`, asserts the `#downloadsPanel`-scoped rule names containing `downloadButton`, `downloadsPanelFooterButton` or `footer-button` are exactly those six, each starts with `#downloadsPanel `, and each equals its `REQUIRED_RULES` entry; the normal selectors carry `:not([disabled])` and no `:hover`, and the hover selectors carry `:not([disabled]):hover`. Using `support.selector_matching.element`/`matches`, build a `panel#downloadsPanel` (`attrs={"type": "arrow"}`) with a `panelview#downloadsPanel-mainView` holding `richlistbox#downloadsListBox` with a `richlistitem` containing `hbox.downloadMainArea` and `button.downloadButton`, a `vbox#downloadsFooter` holding `button#downloadsHistory.downloadsPanelFooterButton.subviewbutton.panel-subview-footer-button.toolbarbutton-1`, a `panelview#downloadsPanel-blockedSubview` holding `moz-button-group#downloadsPanel-blockedSubview-buttons.panel-footer` with `button#downloadsPanel-blockedSubview-unblockButton.footer-button` and `button#downloadsPanel-blockedSubview-deleteButton.footer-button` (`attrs={"default": ""}`), and a `panelview#downloadsPanel-privateBrowsing` holding `button.footer-button.secondary` and `button.footer-button.primary`. The footer button, row action button and all four subview footer buttons match their normal selector with and without `hover`, match their hover selector only when hovered, and a `[disabled]` button matches neither; `#downloadsSummary`, `#downloadsSummaryProgress`, `.downloadMainArea`, `#downloadsPanel-blockedSubview-title` and the panel header match none; a `.downloadButton` in a `richlistbox#downloadsListBox` outside `#downloadsPanel` matches none; and `button#editBookmarkPanelDoneButton.footer-button` under `#editBookmarkPanel` matches none.
- Extend `test_header_names_provenance_and_preference` with the new strings after the downloads-row provenance entries (the bookmark editor keeps its own provenance test): `"No reference shows Firefox's downloads panel buttons"`, `"widgets/button.svg"`, `"tests/test_desktoptheme_button.py::TestButton"`, `"tests/test_desktoptheme_button_reference.py::TestButtonReference"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"downloadsPanelFooterButton"`, `"downloadButton"`, `"footer-button"`, `"DownloadsViewUI.sys.mjs"`, `"panelUI-shared.css"`, `"global-shared.css"`, `"disabled buttons keep Firefox's paint"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md`: in the existing downloads-panel row under `## firefox`, drop the clause that the row's action button and footer button stay Firefox's from its guarantee, and end its provenance at "on the panel rows only" instead of leaving those buttons to Firefox. Add a row immediately after it whose guarantee is: the downloads panel's footer button (`#downloadsPanel .downloadsPanelFooterButton`), row action buttons (`#downloadsPanel .downloadButton`) and blocked/private subview footer buttons (`#downloadsPanel .footer-button`) are square `#DDDDDD` faces with a 1px black outline and the reference's white/`#AAAAAA` raised bevel, an enabled hovered one being flat `#CCCCFF` with black text and no bevel, while disabled buttons, the panel summary, header and subview copy stay Firefox's. Its test column names the new scope test, and its provenance records the missing downloads-panel-buttons reference, the `widgets/button.svg` and `widgets/viewitem.svg` anchors, the installed Firefox ESR 153.5.1 files named above, the disabled-button guard, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing sheet rules, the downloads panel rows, the Firefox install and their tests keep their declarations and scope.

### Firefox Platinum content: paint about:config's preference table, search field and buttons as Platinum controls (planned 2026-10-26 by the plan role; independent of the waiting notification-doorhanger plan) — done 2026-10-26 by the feature role

**Goal.** Make Firefox's `about:config` page read as Platinum: the preference table (`#prefs:not(:empty)`) becomes a white square field with black text, a 1px black outline and the sunken `#999999` top-left shadow; its alternate rows are `#EEEEEE`; its stock hover wash is removed, so a hovered odd row stays `#EEEEEE` and a hovered even row keeps the field's white, both with black text. The search field (`#about-config-search`) becomes the white square sunken field, and the Show All ghost button (`#show-all`) and the warning page's primary button (`#warningButton`) become square `#DDDDDD` push buttons with a black outline and the reference's white/`#AAAAAA` raised bevel, an enabled hovered one being flat `#CCCCFF` with black text and no bevel. The warning page's copy, checkbox and background illustration, the help text, the Show Only Modified checkbox, the rows' name/value text and their `has-user-value`, `locked` and `deleted` styling, the per-row add/edit/save/reset buttons and the page background and toolbar band stay Firefox's.

**Grounding.** No reference screenshot shows Firefox's `about:config` page, so the paint adapts this theme's Platinum controls (platform colour adaptation 2026-10-26). The table field and search field adapt the reference-grounded `widgets/lineedit.svg` (`tests/test_desktoptheme_lineedit.py::TestLineEdit`), and the alternate row `#EEEEEE` is the pinned `[Colors:View] BackgroundAlternate` trough (`tests/test_colorscheme_reference.py::TestReferenceAnchors::test_view_background_alternate`). The rows adapt `widgets/listitem.svg` (`tests/test_desktoptheme_listitem.py::TestListItem`), which has no hover highlight, and the flat `#CCCCFF` hover adapts `widgets/viewitem.svg` (`tests/test_desktoptheme_viewitem.py::TestViewItem`, `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`). The push buttons adapt `widgets/button.svg` (`tests/test_desktoptheme_button.py::TestButton`) and its reference `#AAAAAA` bevel (`tests/test_desktoptheme_button_reference.py::TestButtonReference`).

In the installed Firefox ESR 153.5.1, `chrome/toolkit/content/global/aboutconfig/aboutconfig.html` defines `#warningButton` (`.primary`), `#showWarningNextTime`, `#about-config-search`, `#about-config-show-only-modified`, `table#prefs` and `#show-all` (`.ghost-button`). `chrome/toolkit/content/global/aboutconfig/aboutconfig.js`'s `PrefRow` builds each row as a `tr` with a `th` name cell and `td.cell-value`/`td.cell-edit`/`td.cell-reset`, `refreshClass` adds the `odd`, `has-user-value`, `locked` and `deleted` classes, and `loadPrefs` disables the `info-pages.css` sheet (`[...document.styleSheets].find(s => s.title == "infop").disabled = true;`), so the main page's table is painted by `aboutconfig.css` and `common-shared.css`, not the warning page's `info-pages.css`. `chrome/toolkit/content/global/aboutconfig/aboutconfig.css` paints `#prefs`, `#prefs > tr.odd` and `#prefs > tr:hover`; `chrome/toolkit/skin/classic/global/in-content/common-shared.css` gives `html|input[type="text"]` its rounded `--border-color`/`--background-color-box` face and paints `button`/`button.primary` from the `--button-*` tokens and `.ghost-button` transparent; `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` declares those tokens. A headless run of this ESR with a temporary profile whose `userContent.css` painted `about:config`'s body red rendered the page red, and a second run with the candidate block below and `browser.aboutConfig.showWarning=false` rendered the search field's square black border and the Show All button's `#DDDDDD` face. Declaration checks do not establish rendered row pixels.

**Approach.** Append this block at the very end of `theme/firefox/org.macos8.desktop/chrome/userContent.css`, after the existing `about:downloads` block, with a short comment naming the adaptation:

```css
@-moz-document url("about:config") {
  #prefs:not(:empty) {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #999999 !important;
  }

  #prefs > tr.odd {
    background-color: #EEEEEE !important;
  }

  #prefs > tr:hover {
    background-color: transparent !important;
    color: #000000 !important;
  }

  #prefs > tr.odd:hover {
    background-color: #EEEEEE !important;
  }

  #about-config-search {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #999999 !important;
  }

  #show-all,
  #warningButton {
    background-color: #DDDDDD !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
  }

  #show-all:hover:not(:disabled),
  #warningButton:hover:not(:disabled) {
    background-color: #CCCCFF !important;
    color: #000000 !important;
    box-shadow: none !important;
  }
}
```

Use `#prefs:not(:empty)` so the initial page, whose table has no rows, draws no field line; leave the empty table, the warning page's checkbox and copy, the Show Only Modified checkbox, the `#toolbar` band, `.config-background`, `.config-help-text` and the per-row cell buttons alone. Do not add an `outline` rule: the search field keeps Firefox's `:focus` outline and the buttons keep their `:focus-visible` ring. Do not change the existing `about:downloads` block or `userChrome.css`. In the `userContent.css` header comment, append an about:config provenance paragraph after the downloads provenance and before the closing `*/`: no reference shows Firefox's about:config; the field and rows adapt `widgets/lineedit.svg`, `widgets/listitem.svg` and the pinned `#EEEEEE`/`#CCCCFF` anchors, and the buttons adapt `widgets/button.svg` and its `#AAAAAA` bevel; `aboutconfig.html` defines the ids, `aboutconfig.js` builds the rows and disables the `infop` sheet, `aboutconfig.css` and `common-shared.css` own the stock paint; a headless run reached the page; declaration checks do not establish rendered row pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userContent.css` contains exactly the two `@-moz-document` blocks: the existing `about:downloads` block byte-unchanged and the new `about:config` block with the seven rules above (nine parsed selectors after the grouped selectors are split). `test_palette_is_exact` in `tests/test_firefox_content_theme.py` expects the expanded set `{WHITE, BLACK, GREY, SELECTION, FACE, TROUGH, BUTTON_SHADOW}` imported from `support.platinum_palette`.
- `tests/test_firefox_content_theme.py` gains a general `@-moz-document url("...")` reader that returns the block bodies by URL. `TestFirefoxContentTheme` parses only the `about:downloads` body, keeps its three-rule assertions, and renames `test_sheet_is_one_about_downloads_at_rule` to `test_sheet_has_the_downloads_and_config_at_rules` and `test_parsed_rules_are_exactly_the_three_list_rules` to `test_downloads_rules_are_exactly_the_three_list_rules`; the shared marker, palette, no-`@import`/Adwaita, no-universal-selector and downloads provenance tests stay. New `TestFirefoxConfigTheme` parses the `about:config` body and asserts: `test_required_rules` pins the nine selectors' exact declarations; `test_parsed_rules_are_exactly_the_config_rules` pins the selector set and order; `test_config_rules_are_scoped_to_the_prefs_table_and_controls` requires every selector to start with `#prefs`, `#about-config-search`, `#show-all` or `#warningButton` and names none of `.config-background`, `.config-help-text`, `#about-config-show-only-modified`, `.cell-edit`, `.cell-reset` or `.button-`; `test_config_selector_guards_the_empty_table` requires `:not(:empty)` on `#prefs`; `test_header_names_config_provenance` requires the header to name `"No reference shows Firefox's about:config"`, `"widgets/lineedit.svg"`, `"widgets/listitem.svg"`, `"widgets/button.svg"`, `"tests/test_desktoptheme_button_reference.py::TestButtonReference"`, `"test_view_background_alternate"`, `"test_selection_background"`, `"aboutconfig.html"`, `"aboutconfig.js"`, `"aboutconfig.css"`, `"common-shared.css"`, `"#prefs"`, `"#about-config-search"`, `"#show-all"`, `"#warningButton"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md` gains a row inserted after the existing `about:downloads` content row and before `## gtk`: the `about:config` preference table (`#prefs:not(:empty)`) is a white square field with black text, a 1px black outline and the sunken `#999999` top-left shadow, its alternate rows are `#EEEEEE`, and a hovered odd row stays `#EEEEEE` while a hovered even row keeps the field's white, both with black text; the search field is the same white sunken field; Show All and the warning page's primary button are square `#DDDDDD` controls with a black outline and the reference's white/`#AAAAAA` raised bevel, an enabled hovered one being flat `#CCCCFF` with black text and no bevel; the warning copy, checkbox, background illustration, help text, Show Only Modified checkbox, row `has-user-value`/`locked`/`deleted` styling, per-row cell buttons and page background stay Firefox's. Its test column names the new config tests and `test_palette_is_exact`, and its provenance records the missing about:config reference, the `widgets/lineedit.svg`, `widgets/listitem.svg` and `widgets/button.svg` anchors, the installed ESR 153.5.1 files and the `infop`-sheet disabling, the headless reach run, and that declaration checks do not establish rendered row pixels. The existing downloads row's test column is updated for the two renamed tests. `tests/invariants.py` stays green.
- Repeat the headless reach check against the edited sheet with `browser.aboutConfig.showWarning=false` and record what it renders; declaration checks do not establish rendered row pixels.
- `make check` passes, and the existing `userChrome.css` rules, the Firefox install and their tests keep their declarations and scope.

### Firefox Platinum chrome: paint the notification doorhanger's primary button as a Platinum control (planned 2026-10-26 by the plan role; queued after the waiting bookmark-editor plan's `userChrome.css` edits) — done 2026-10-26 by the feature role

**Goal.** Make the primary action button of Firefox's generic notification doorhanger read as Platinum: in `#notification-popup`, the `html:moz-button.popup-notification-primary-button` (`type="primary"`) becomes a square `#DDDDDD` face with a 1px black outline and a black label, and an enabled hovered or active one becomes a flat `#CCCCFF` face with black text and the same black outline. The secondary split/close button, the header, icon, description, checkbox, learn-more link, panel body and the `moz-button-group.panel-footer` wrapper stay Firefox's.

**Grounding.** No reference screenshot shows Firefox's notification doorhanger, so the paint adapts this theme's Platinum controls (platform colour adaptation 2026-10-26). The `#DDDDDD` face and 1px black outline adapt `widgets/button.svg` (`tests/test_desktoptheme_button.py::TestButton`), and the flat `#CCCCFF` hover adapts `widgets/viewitem.svg` (`tests/test_desktoptheme_viewitem.py::TestViewItem`, `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`). In the installed Firefox ESR 153.5.1, `chrome/toolkit/content/global/elements/popupnotification.js` renders the footer as an `html:moz-button-group.panel-footer` holding an `html:moz-button.popup-notification-secondary-button` (`type="split"`) and an `html:moz-button.popup-notification-primary-button` (`type="primary"`), `chrome/browser/content/browser/browser.xhtml` defines the `#notification-popup` arrow panel, and `chrome/browser/skin/classic/browser/browser-shared.css` gives the primary host a translucent grey face, white text and a small radius. `chrome/toolkit/content/global/elements/moz-button.css` paints the shadow-DOM `.button-background` from the `--button-background-color-primary*`, `--button-border`, `--button-border-color-primary*`, `--button-text-color-primary*` and `--button-border-radius` tokens, which `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` declares; `tokens-shared.css` resolves the radius from `--border-radius-medium` and the hover and active border and text tokens from their base tokens at `:root`, so the rule sets `--button-border-radius` and those hover and active tokens on the host; there is no inner-shadow or bevel token, so the raised white/`#AAAAAA` bevel is not reproduced and a flat face stands in (platform geometry adaptation 2026-10-26).

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, insert one rule immediately after the permission-popup rules and before the `menupopup > menuitem:hover` group:

```css
#notification-popup .popup-notification-primary-button {
  --button-background-color-primary: #DDDDDD !important;
  --button-background-color-primary-hover: #CCCCFF !important;
  --button-background-color-primary-active: #CCCCFF !important;
  --button-border: 1px solid !important;
  --button-border-color-primary: #000000 !important;
  --button-border-color-primary-hover: #000000 !important;
  --button-border-color-primary-active: #000000 !important;
  --button-text-color-primary: #000000 !important;
  --button-text-color-primary-hover: #000000 !important;
  --button-text-color-primary-active: #000000 !important;
  --button-border-radius: 0 !important;
  background-color: transparent !important;
  color: #000000 !important;
  border-radius: 0 !important;
}
```

The host's transparent background exposes the arrow panel's existing `#DDDDDD` body. Set `--button-border-radius`, not `--border-radius-medium`: `tokens-shared.css` resolves the radius at `:root`, so a host `--border-radius-medium` never reaches the shadow face. Set the hover and active border and text tokens too, because `tokens-shared.css` resolves those at `:root` from the base tokens. The permission-popup test's token-scope assertion now checks only its own selectors. Do not add a rule for the secondary split/close button, the `moz-button-group` footer, the header, icon, description, checkbox, learn-more link or panel body, and do not change `:root`, the arrow-panel token rules or any existing selector. In the header comment block, append a notification-doorhanger provenance paragraph immediately after the permission-popup paragraph (before the trust-panel paragraph): no reference shows Firefox's notification doorhanger; the flat `#DDDDDD`/`#CCCCFF` face with a 1px black outline adapts `widgets/button.svg` and `widgets/viewitem.svg` with the anchors above; `popupnotification.js` builds the `moz-button` footer, `browser.xhtml` defines `#notification-popup`, `browser-shared.css` paints the primary host, and `moz-button.css`/`tokens-shared.css` consume the `--button-*` tokens with no bevel token; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains one entry, keyed `#notification-popup .popup-notification-primary-button` and inserted after the permission-popup entries and before the `menupopup > menuseparator` entries, whose declarations are exactly the fourteen above, with `FACE`, `SELECTION` and `BLACK` built from the constants the module already imports. `test_palette_is_exact` keeps its expected hex set unchanged because the rule introduces no new hex literal.
- New `TestFirefoxChrome.test_notification_popup_primary_button_paint_is_scoped_to_the_notification_popup`, placed immediately after `test_permission_popup_control_paint_is_scoped_to_the_permission_popup`, asserts the rule names containing `notification-popup` are exactly that selector, the rule equals its `REQUIRED_RULES` entry, no rule defines the exact `--button-background-color` or `--button-border-color` token, `--button-border-radius` appears only on that selector, `--border-radius-medium` appears on none, and the hover and active border and text tokens are set on the primary. Using `support.selector_matching.element`/`matches`, build a `panel#notification-popup` (`popup-notification-panel`, `attrs={"type": "arrow"}`) with a `moz-button-group.panel-footer` holding `moz-button.popup-notification-primary-button` (`attrs={"type": "primary"}`) and `moz-button.popup-notification-secondary-button` (`attrs={"type": "split"}`); the primary matches with and without `hover`, while the secondary, the footer group, a plain `button` with that class, and the same primary classes under `#trustpanel-popup` match none.
- New `TestFirefoxChrome.test_notification_popup_provenance`, placed immediately after the scope test, asserts the leading comment names `"No reference shows Firefox's notification doorhanger"`, `"widgets/button.svg"`, `"tests/test_desktoptheme_button.py::TestButton"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"#notification-popup"`, `"popup-notification-primary-button"`, `"popup-notification-secondary-button"`, `"popupnotification.js"`, `"browser.xhtml"`, `"browser-shared.css"`, `"moz-button.css"`, `"tokens-shared.css"`, `"--button-border"` and `"platform adaptation 2026-10-26"`. Leave `test_header_names_provenance_and_preference` untouched.
- `docs/invariants.md` gains a row inserted after the permission popup row and before the trust panel row in the `## firefox` table: the notification doorhanger's primary button (`#notification-popup .popup-notification-primary-button`) is a square `#DDDDDD` face with a 1px `#000000` outline and black label, and an enabled hovered or active one is flat `#CCCCFF` with black text, while the secondary split/close button, header, icon, description, checkbox, learn-more link, panel body and footer group stay Firefox's; its test column names the new scope test and its provenance records the missing notification-doorhanger reference, the `widgets/button.svg` and `widgets/viewitem.svg` anchors, the installed Firefox ESR 153.5.1 files and tokens above, the absent inner-shadow/bevel token, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing sheet rules, the Firefox install and their tests keep their declarations and scope.
- Implementation note (2026-10-26): the permission popup test's shared-token assertion now checks only its own selectors, because this rule intentionally sets `--button-border-radius` and the hover and active border and text tokens for the notification primary button; the bookmark-editor test's shared-token assertion now checks `--button-border-radius` only against its own selectors and keeps the sheet-wide guard for `--input-border-color`, `--input-text-background-color` and `--border-radius-medium`, because this rule is the only one that defines `--button-border-radius`.

### Firefox Platinum chrome: paint the bookmark editor's fields, folder dropdown and footer buttons as Platinum controls (planned 2026-10-26 by the plan role; independent of the waiting trust-panel plan) — done 2026-10-26 by the feature role

**Goal.** Make the bookmark editor panel Firefox opens from the star / "Bookmark This Page" read as Platinum: in `#editBookmarkPanel`, the four text fields (`#editBMPanel_namePicker`, `#editBMPanel_locationField`, `#editBMPanel_tagsField`, `#editBMPanel_keywordField`) become the white square sunken field; the folder dropdown (`#editBMPanel_folderMenuList`) and the Done/Remove footer buttons (`#editBookmarkPanelDoneButton`, `#editBookmarkPanelRemoveButton`) become square `#DDDDDD` push-button faces with a black outline and the reference's white/`#AAAAAA` raised bevel; an enabled hovered dropdown or button is flat `#CCCCFF` with black text and no bevel. The panel header, labels, checkbox, folder and tag expander buttons, folder tree and its New Folder button, tag selector and tags autocomplete, separator and panel body stay Firefox's, and so does the bookmark properties dialog (`#bookmarkpropertiesdialog`), which reuses the same control ids.

**Grounding.** No reference screenshot shows Firefox's bookmark editor, so the paint adapts this theme's Platinum controls (platform adaptation 2026-10-26). The field recipe is the sheet's existing findbar text box: white face, black text, square 1px black border and `inset 1px 1px #999999` shadow, which adapts the reference-grounded `widgets/lineedit.svg` (`tests/test_desktoptheme_lineedit.py::TestLineEdit`). The push-button recipe is the harness's `#DDDDDD` face, black outline and `BUTTON_BEVEL` (`inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA`) that the sheet's permission-popup controls already use, adapting `widgets/button.svg` (`tests/test_desktoptheme_button.py::TestButton`, `tests/test_desktoptheme_button_reference.py::TestButtonReference`). The flat `#CCCCFF` hover adapts `widgets/viewitem.svg` (`tests/test_desktoptheme_viewitem.py::TestViewItem`, `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`) and matches the sheet's menu-row mapping.

In the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/browser.xhtml` defines `html:template#editBookmarkPanelTemplate` with `#editBookmarkPanel` (`.panel-no-padding`, `type="arrow"`), its `.panel-header` holding `#editBookmarkPanelTitle`, `#editBookmarkHeaderSeparator`, a `.panel-subview-body` and a `div#editBookmarkPanelContent` holding the four `html:input`s above, `menulist#editBMPanel_folderMenuList` (`.folder-icon`, `size="large"`), `button#editBMPanel_foldersExpander` and `button#editBMPanel_tagsSelectorExpander` (`.expander-down.panel-button`), `button#editBMPanel_newFolderButton`, `richlistbox#editBMPanel_tagsSelector`, `checkbox#editBookmarkPanel_showForNewBookmarks`, and an `html:moz-button-group.panel-footer` holding `button#editBookmarkPanelDoneButton` (`.footer-button`, `default="true"`) and `button#editBookmarkPanelRemoveButton`. `chrome/browser/content/browser/browser-places.js` lazily instantiates that template on the first star click (`StarUI._element("editBookmarkPanelTemplate")`), and `chrome/browser/content/browser/places/editBookmark.js` fills the rows. `chrome/browser/skin/classic/browser/places/editBookmarkPanel.css` paints `#editBMPanel_newFolderButton` and `.expander-up`/`.expander-down` through `--button-*` tokens and makes the focused input's border transparent; `chrome/browser/skin/classic/browser/places/editBookmark.css` paints the folder tree, tag selector and menulist icon. `chrome/toolkit/skin/classic/global/global-shared.css` paints `html|input` from `--input-text-background-color`, `--input-border-color` and `--border-radius-medium`, and paints `.footer-button` from `--button-*` with `[default]` taking the primary accent face. `chrome/toolkit/skin/classic/global/button.css` paints a plain XUL `button` from the system `ButtonFace`/`ButtonBorder`, `chrome/toolkit/skin/classic/global/menulist.css` gives a non-native `menulist` its `--button-background-color` and `--button-border-radius`, `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` declares those tokens, and `chrome/browser/content/browser/places/bookmarkProperties.xhtml` reuses `#editBMPanel_namePicker`, `#editBMPanel_locationField` and `#editBMPanel_folderMenuList` inside `#bookmarkpropertiesdialog`. Nothing in the sheet names `#editBookmarkPanel`, `#editBMPanel_*` or `#bookmarkpropertiesdialog`, and the generic `toolbarbutton:hover` rule does not match these controls, so today the fields keep the rounded stock input face, the dropdown keeps the rounded button face and the Done button keeps the accent primary face.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, append at the very end of the sheet (after the findbar text-box rule) one short comment and three rules, each selector on one line:

```css
#editBookmarkPanel #editBMPanel_namePicker,
#editBookmarkPanel #editBMPanel_locationField,
#editBookmarkPanel #editBMPanel_tagsField,
#editBookmarkPanel #editBMPanel_keywordField {
  background-color: #FFFFFF !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #999999 !important;
}

#editBookmarkPanel #editBMPanel_folderMenuList,
#editBookmarkPanel #editBookmarkPanelDoneButton,
#editBookmarkPanel #editBookmarkPanelRemoveButton {
  background-color: #DDDDDD !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
}

#editBookmarkPanel #editBMPanel_folderMenuList:hover:not([disabled]),
#editBookmarkPanel #editBookmarkPanelDoneButton:hover:not([disabled]),
#editBookmarkPanel #editBookmarkPanelRemoveButton:hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Paint the fields in every state and leave the stock `:focus-visible` outline in place (the sheet sets no `outline`), so focus keeps Firefox's ring. Scope every selector through `#editBookmarkPanel` so the bookmark properties dialog keeps Firefox's controls. Add no rule for the header, title, labels, checkbox, expander buttons, folder tree, New Folder button, tag selector, tags autocomplete, separator or panel body, and do not change the `:root` block, the `panel[type="arrow"]`/`menupopup` token rules or any existing selector. In the header comment block, append a bookmark-editor provenance paragraph immediately after the downloads-panel paragraph (before the "Install it opt-in" paragraph): no reference shows Firefox's bookmark editor; the field, push-button and hover paint adapt `widgets/lineedit.svg`, `widgets/button.svg` and `widgets/viewitem.svg` with the anchors above; `browser.xhtml` defines `editBookmarkPanelTemplate` and its controls, `browser-places.js` instantiates it and `places/editBookmark.js` fills it, `places/editBookmarkPanel.css` and `places/editBookmark.css` own the stock control paint, and `chrome/toolkit/skin/classic/global/global-shared.css`/`button.css`/`menulist.css` supply the input, button and menulist faces; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the ten selectors above (one entry each), appended at the end of the dict: each field selector is exactly `background-color: WHITE !important`, `color: BLACK !important`, `border: 1px solid BLACK !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px GREY !important`; each dropdown/button selector is exactly `background-color: FACE !important`, `color: BLACK !important`, `border: 1px solid BLACK !important`, `border-radius: 0 !important` and `box-shadow: BUTTON_BEVEL !important`; each `:hover:not([disabled])` selector is exactly `background-color: SELECTION !important`, `color: BLACK !important` and `box-shadow: none !important`, built from the constants the module already imports. `test_palette_is_exact` keeps its expected hex set unchanged because the rules introduce no new hex literal.
- New `TestFirefoxChrome.test_bookmark_panel_control_paint_is_scoped_to_the_bookmark_panel`, placed immediately before `test_readme_names_the_sheet` (the end of the class), asserts the rule names containing `editBookmark` are exactly those ten, each equals its `REQUIRED_RULES` entry, the field and normal rules carry no `:hover`, the hover rules carry `:hover` and `:not([disabled])`, and no rule in the sheet defines `--button-border-radius`, `--input-border-color`, `--input-text-background-color` or `--border-radius-medium`. Using `support.selector_matching.element`/`matches`, build a `panel#editBookmarkPanel` (`panel-no-padding`, `attrs={"type": "arrow"}`) holding a `.panel-header` box with `h1 > span#editBookmarkPanelTitle`, a `toolbarseparator#editBookmarkHeaderSeparator`, a `vbox.panel-subview-body` with `div#editBookmarkPanelContent`, the four `input` elements with the ids above, an `hbox.editBMPanel_folderRow` holding `menulist#editBMPanel_folderMenuList` (`.folder-icon`), `button#editBMPanel_foldersExpander` and `#editBMPanel_tagsSelectorExpander` (`.expander-down.panel-button`), a `vbox#editBMPanel_folderTreeRow` holding `button#editBMPanel_newFolderButton`, an `hbox.editBMPanel_tagsRow` holding `#editBMPanel_tagsField` and `#editBMPanel_tagsSelectorExpander`, a `div#editBMPanel_tagsSelectorRow` holding `richlistbox#editBMPanel_tagsSelector`, a `panel#editBMPanel_tagsAutocomplete`, a `checkbox#editBookmarkPanel_showForNewBookmarks`, and an `html:moz-button-group.panel-footer` holding `button#editBookmarkPanelDoneButton.footer-button` (with `attrs={"default": ""}`) and `button#editBookmarkPanelRemoveButton.footer-button`. Each field matches its field selector with and without `hover`; the dropdown and both footer buttons match their normal selector and, when hovered, their hover selector but not when idle; a `[disabled]` hovered button still matches the normal rule and not the hover rule; every excluded element above matches none of the ten selectors, a `toolbarbutton.subviewbutton` under `#nav-bar` matches none, and the same four inputs plus the menulist built inside `#bookmarkpropertiesdialog` match none of the ten.
- New `TestFirefoxChrome.test_bookmark_panel_provenance`, placed immediately after the scope test, asserts the leading comment names `"No reference shows Firefox's bookmark editor"`, `"widgets/lineedit.svg"`, `"tests/test_desktoptheme_lineedit.py::TestLineEdit"`, `"widgets/button.svg"`, `"tests/test_desktoptheme_button.py::TestButton"`, `"tests/test_desktoptheme_button_reference.py::TestButtonReference"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"#editBookmarkPanel"`, `"editBookmarkPanelTemplate"`, `"editBMPanel_namePicker"`, `"editBMPanel_locationField"`, `"editBMPanel_tagsField"`, `"editBMPanel_keywordField"`, `"editBMPanel_folderMenuList"`, `"editBookmarkPanelDoneButton"`, `"editBookmarkPanelRemoveButton"`, `"chrome/browser/content/browser/browser-places.js"`, `"chrome/browser/content/browser/places/editBookmark.js"`, `"chrome/browser/skin/classic/browser/places/editBookmarkPanel.css"`, `"chrome/browser/skin/classic/browser/places/editBookmark.css"`, `"chrome/toolkit/skin/classic/global/global-shared.css"`, `"chrome/toolkit/skin/classic/global/button.css"`, `"chrome/toolkit/skin/classic/global/menulist.css"`, `"#bookmarkpropertiesdialog"` and `"platform adaptation 2026-10-26"`. Leave `test_header_names_provenance_and_preference` untouched so this plan and the waiting trust-panel plan do not edit the same tuple.
- `docs/invariants.md` gains a row appended at the end of the `## firefox` table, after the unified-extensions panel row and before `## gtk`: the bookmark editor's fields (`#editBookmarkPanel #editBMPanel_namePicker`, `#editBMPanel_locationField`, `#editBMPanel_tagsField`, `#editBMPanel_keywordField`) are the white square sunken field with black text, and its folder dropdown (`#editBMPanel_folderMenuList`) and Done/Remove footer buttons (`#editBookmarkPanelDoneButton`, `#editBookmarkPanelRemoveButton`) are square `#DDDDDD` controls with a black outline and the reference's white/`#AAAAAA` raised bevel, an enabled hovered one being flat `#CCCCFF` with black text and no bevel, while the header, labels, checkbox, expander buttons, folder tree and New Folder button, tag selector, tags autocomplete, separator, panel body and the `#bookmarkpropertiesdialog` copies stay Firefox's; its test column names the new scope test and its provenance records the missing Firefox bookmark-editor reference, the `widgets/lineedit.svg`, `widgets/button.svg` and `widgets/viewitem.svg` anchors, the installed Firefox ESR 153.5.1 files and functions above, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing sheet rules, the Firefox install and their tests keep their declarations and scope.

### Firefox Platinum chrome: paint the default trust panel's button rows like a Platinum menu (planned 2026-10-26 by the plan role; independent of the waiting permission-popup plan) — done 2026-10-26 by the feature role

**Goal.** Make the site-information panel Firefox opens by default read as Mac OS 8.6 chrome: in the trust panel (`#trustpanel-popup`), every plain XUL button row (`#trustpanel-popup-connection`, `#trustpanel-clear-cookies-button`, `#trustpanel-privacy-link` — all `toolbarbutton.subviewbutton`) is square, and an enabled one under the pointer is flat `#CCCCFF` with black text and no toolbar bevel. The panel's cards and graphics, its dynamically built `moz-button` rows and actions, the tracking `moz-toggle`, the https-only menulist, the labels, the generated back buttons, the separators, the `.panel-button` certificate action, the footer link and the panel body stay Firefox's.

**Grounding.** No reference screenshot shows Firefox chrome or its trust panel. The row paint adapts the reference-grounded `widgets/viewitem.svg`: its hover face is the flat `#CCCCFF` selection fill with black text (`tests/test_desktoptheme_viewitem.py::TestViewItem`, `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`), matching the sheet's existing menu-row mapping (platform colour adaptation 2026-10-26).

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/navigator-toolbox.js` sends a click on `#identity-icon-box` (when `browser.urlbar.trustPanel.featureGate` is set) and on `#trust-icon-container` to `gTrustPanelHandler.handleProtectionsButtonEvent`; `defaults/preferences/firefox.js` sets that pref to `true`, and `chrome/browser/content/browser/browser-siteProtections.js`'s `showProtectionsPopup` returns early when the trust panel is enabled, so the site-information button opens the trust panel, which the sheet's `#identity-popup` rows do not paint. `chrome/browser/content/browser/browser.xhtml` defines `template-trustpanel-popup` with `#trustpanel-popup` (`.panel-no-padding.site-information-popup`, `type="arrow"`), `#trustpanel-popup-multiView`, `#trustpanel-popup-mainView`, `#trustpanel-header-section` / `#trustpanel-header-row` holding `#trustpanel-popup-connection` (`.subviewbutton.subviewbutton-nav`), `#trustpanel-graphic-section`, `#trustpanel-toggle` (`html:moz-toggle`), `#trustpanel-clear-cookies-button` (`.subviewbutton.subviewbutton-nav`), `#trustpanel-privacy-link` (`.subviewbutton`), and the `securityInformationView`, `blockerView`, `blockerDetailsView` and `clearcookiesView` panelviews, whose `#trustpanel-siteinformation-morelink` is an `html:a.trustpanel-section.panel-subview-footer-button` and whose `#identity-popup-remove-cert-exception` is a `button.panel-button`. `chrome/browser/content/browser/browser-trustPanel.js` `#addButtons` builds the tracker rows as `moz-button.moz-button-subviewbutton-nav`. `chrome/browser/skin/classic/browser/controlcenter/panel.css` owns the trust panel's layout and the `.moz-button-subviewbutton-nav` part paint, `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` its `--panel-menuitem-border-radius` and ghost hover tokens, `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines those tokens, and `moz-src/browser/components/customizableui/PanelMultiView.sys.mjs` creates the `.panel-header` back button carrying `subviewbutton-back`. Nothing in the sheet names `#trustpanel-popup`, so today those rows keep Firefox's rounded corners and violet ghost hover under the sheet's generic `toolbarbutton:hover` bevel.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the protections-panel rules and before the all-tabs rules, add two rules with a short comment (each selector on one line):

```css
#trustpanel-popup .subviewbutton:not(.panel-header .subviewbutton) {
  border-radius: 0 !important;
}

#trustpanel-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Square the rows directly rather than overriding `--panel-menuitem-border-radius`, because that token also paints the app-menu, overflow, all-tabs, unified-extensions, identity and protections rows. Excluding `.panel-header .subviewbutton` leaves PanelMultiView's generated back buttons Firefox's; the `:hover:not([disabled])` rule out-specifies the stock ghost hover and the generic `toolbarbutton:hover:not([disabled="true"])` bevel. Add no rule for the cards, graphics, `moz-button` rows and actions, the tracking toggle, the https-only menulist, the labels, the `.panel-button` certificate action, `#trustpanel-siteinformation-morelink`, the separators or the panel body, and do not change the `#appMenu-popup`, `#widget-overflow`, `#allTabsMenu-allTabsView`, `#unified-extensions-panel`, `#identity-popup` or `#protections-popup` selectors.

In the header comment block, append a trust-panel provenance paragraph before the closing `*/`, after the protections paragraph (and after the permission-popup paragraph once that plan has landed): no reference shows Firefox's trust panel; the row highlight adapts the reference-grounded `widgets/viewitem.svg` and the sheet's menu-row mapping (platform colour adaptation 2026-10-26); `chrome/browser/content/browser/navigator-toolbox.js` routes the site-information buttons to the trust panel, `defaults/preferences/firefox.js` enables it with `browser.urlbar.trustPanel.featureGate`, and `chrome/browser/content/browser/browser-siteProtections.js` `showProtectionsPopup` returns early; `chrome/browser/content/browser/browser.xhtml` defines `template-trustpanel-popup` and its rows, `chrome/browser/content/browser/browser-trustPanel.js` `#addButtons` builds the `moz-button` rows, `chrome/browser/skin/classic/browser/controlcenter/panel.css` and `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` own the stock row paint, and `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` declares the tokens; the sheet paints only the plain `.subviewbutton` rows; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the two selectors above (one entry each) using the existing `SELECTION` and `BLACK` constants: the square rule is exactly `border-radius: 0 !important`, and the hover rule is `background-color: SELECTION !important`, `color: BLACK !important` and `box-shadow: none !important`.
- New `TestFirefoxChrome.test_trust_panel_row_paint_is_scoped_to_the_trust_panel` asserts the selectors naming `trustpanel-popup` are exactly those two, each starts with `#trustpanel-popup`, includes `:not(.panel-header .subviewbutton)` and equals its `REQUIRED_RULES` entry, the square rule carries no declaration besides `border-radius`, the hover rule carries `:hover` and `:not([disabled])`, and no rule in the sheet defines `--panel-menuitem-border-radius`. Using `support.selector_matching.element`/`matches`, build a `panel#trustpanel-popup` holding a `panelmultiview#trustpanel-popup-multiView`, its `panelview#trustpanel-popup-mainView` (`PanelUI-subView`), a `.panel-header` box with a generated `toolbarbutton.subviewbutton.subviewbutton-iconic.subviewbutton-back`, a `#trustpanel-popup-connection` `toolbarbutton.subviewbutton.subviewbutton-nav`, a `#trustpanel-clear-cookies-button` with the same classes, a `#trustpanel-privacy-link` `toolbarbutton.subviewbutton`, an `html:moz-toggle#trustpanel-toggle`, a `menulist#trustpanel-popup-security-httpsonlymode-menulist`, an `html:moz-button#trustpanel-blocker-see-all`, an `html:moz-button.moz-button-subviewbutton-nav`, a `#trustpanel-siteinformation-morelink` `html:a` carrying `trustpanel-section` and `panel-subview-footer-button`, a `button#identity-popup-remove-cert-exception.panel-button`, and a `vbox#trustpanel-graphic-section`; the three plain rows each match the square rule and, when not disabled and hovered, the hover rule, a `[disabled]` row matches neither hover nor square-only hover, and every other element (plus a `.subviewbutton` under `#nav-bar`) matches neither rule.
- `test_header_names_provenance_and_preference` gains the strings `"No reference shows Firefox's trust panel"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"chrome/browser/content/browser/navigator-toolbox.js"`, `"browser.urlbar.trustPanel.featureGate"`, `"defaults/preferences/firefox.js"`, `"chrome/browser/content/browser/browser-siteProtections.js"`, `"showProtectionsPopup"`, `"chrome/browser/content/browser/browser.xhtml"`, `"template-trustpanel-popup"`, `"trustpanel-popup-connection"`, `"trustpanel-clear-cookies-button"`, `"trustpanel-privacy-link"`, `"trustpanel-siteinformation-morelink"`, `"trustpanel-toggle"`, `"chrome/browser/content/browser/browser-trustPanel.js"`, `"moz-button-subviewbutton-nav"`, `"chrome/browser/skin/classic/browser/controlcenter/panel.css"`, `"chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css"`, `"chrome/toolkit/skin/classic/global/design-system/tokens-shared.css"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md` gains a row in the `## firefox` table after the protections-panel row (after the permission-popup row once that plan has landed): the trust panel's plain button rows (`#trustpanel-popup .subviewbutton` outside `.panel-header`) are square, and an enabled hovered row is flat `#CCCCFF` with black text and no toolbar bevel, while the cards, graphics, `moz-button` rows and actions, tracking toggle, https-only menulist, generated back buttons, `.panel-button` certificate action, footer link, separators and panel body stay Firefox's; its test column names the new test, and its provenance records the missing Firefox trust-panel reference, the `widgets/viewitem.svg` anchors, the installed Firefox ESR 153.5.1 pref and files above, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing sheet rules, the install and their tests keep their declarations and scope.

### Firefox Platinum chrome: paint the permission popup's clear buttons and permission dropdown as Platinum controls (planned 2026-10-26 by the plan role; independent of the landed protections-panel plan) — done 2026-10-26 by the feature role

**Goal.** Make Firefox's permission popup (`#permission-popup`, the site-permissions panel whose rows show a site's granted permissions) read as Mac OS 8.6 chrome: each row's clear-permission button (`button.permission-popup-permission-remove-button`) is a square `#DDDDDD` push button with a 1px black outline and the reference push button's raised white/`#AAAAAA` bevel, and an enabled one under the pointer is flat `#CCCCFF` with black text and no bevel; the popup/autoplay permission dropdown (`#permission-popup-menulist`) wears the same square face, outline, bevel and hover. The permission rows (`hbox.permission-popup-permission-item`), their icons, name labels, state labels and remove-button boxes, the storage-access hint and learn-more link, the panel header, the separator, the reload hint and the panel body stay Firefox's.

**Grounding.** No reference screenshot shows Firefox chrome or its permission popup. The control art adapts the reference-grounded `widgets/button.svg`: its normal/pressed push button has a `#DDDDDD` face, a 1px `#000000` outline, a `#FFFFFF` top/left highlight and the reference's `#AAAAAA` bottom/right shadow (`tests/test_desktoptheme_button.py::TestButton`, `tests/test_desktoptheme_button_reference.py::TestButtonReference`). The hover fill and black text adapt the reference-grounded `widgets/viewitem.svg` and the sheet's menu-item mapping, with `#CCCCFF` pinned by `tests/test_desktoptheme_viewitem.py::TestViewItem` and `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`.

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<html:template id="template-permission-popup">` with `<panel id="permission-popup" class="panel-no-padding">`, its `#permission-popup-multiView`, the `#permission-popup-mainView` panelview whose `#permission-popup-mainView-panel-header` is a plain `.panel-header` (an `html:h1` around `#permission-popup-mainView-panel-header-span`), a `toolbarseparator`, and the `#permission-popup-permission-list` that holds `#permission-popup-permission-list-default-anchor`, the `anchorfor="3rdPartyStorage"` anchor, `#permission-popup-storage-access-permission-list-header` (`.permission-popup-permission-header-label`), `#permission-popup-storage-access-permission-learn-more`, and `#permission-popup-permission-reload-hint`. `chrome/browser/content/browser/browser-sitePermissionPanel.js` `_createPermissionItem` builds each row as an `hbox.permission-popup-permission-item` holding a `.permission-popup-permission-icon`, a `.permission-popup-permission-label` and either a `#permission-popup-menulist` (for `popup` and `autoplay-media`, disabled when the popup preference is locked) or a `.permission-popup-permission-state-label` and the `button.permission-popup-permission-remove-button` built by `_createPermissionClearButton`. `chrome/browser/skin/classic/browser/controlcenter/panel.css` owns the popup layout, gives the remove button `var(--button-background-color)`, `var(--button-border)` and `var(--button-border-radius)` plus a `:hover`/`:hover:active` recolour, and gives `#permission-popup-menulist` its padding and locked-state dimming; `chrome/toolkit/skin/classic/global/button.css` supplies the plain XUL button's `ButtonFace`/`ButtonBorder` paint, `chrome/toolkit/skin/classic/global/menulist.css` gives the non-native menulist host its `--button-background-color`, `--button-border-radius` and hover/active recolour, and `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` declares those button tokens. Nothing in the sheet targets `#permission-popup`, so today the remove button and dropdown keep Firefox's rounded control paint.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the all-tabs rules and before the global `menupopup > menuitem:hover` rule, add four rules with a short comment (each selector on one line so the parsed text matches the test's expectation):

```css
#permission-popup .permission-popup-permission-remove-button {
  background-color: #DDDDDD !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
}

#permission-popup .permission-popup-permission-remove-button:hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}

#permission-popup-menulist {
  background-color: #DDDDDD !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
}

#permission-popup-menulist:hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Paint the controls directly rather than overriding `--button-background-color`, `--button-border-color` or `--button-border-radius`, because those tokens paint every Firefox button and menulist. The `:hover:not([disabled])` rules override the stock `panel.css` and menulist `:host` hover/active paint through the user-origin `!important` declarations and keep a locked popup dropdown's dimmed state (Firefox's `[disabled]` opacity and no-pointer rule is left alone). Add no rule for the row containers, labels, state labels, icons, the storage-access link or hint, the header, the separator or the panel body, and do not change the `#appMenu-popup`, `#widget-overflow`, `#allTabsMenu-allTabsView`, `#unified-extensions-panel`, `#identity-popup` or `#protections-popup` selectors.

In the header comment block, append a provenance paragraph after the site-information paragraph and before the closing `*/`: no reference shows Firefox's permission popup; the control art adapts `widgets/button.svg` and the `#AAAAAA` bevel reference (citation above) and the flat `#CCCCFF` row mapping (platform colour adaptation 2026-10-26); `chrome/browser/content/browser/browser.xhtml` defines `template-permission-popup`, `chrome/browser/content/browser/browser-sitePermissionPanel.js` builds the rows and buttons via `_createPermissionItem` and `_createPermissionClearButton`, `chrome/browser/skin/classic/browser/controlcenter/panel.css` owns the permission-popup layout and control paint, `chrome/toolkit/skin/classic/global/button.css` and `chrome/toolkit/skin/classic/global/menulist.css` supply the stock button and menulist paint, and `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` declares the `--button-background-color` and `--button-border-radius` tokens; the sheet paints only the remove button and the permission menulist, leaving the rows, labels, icons, header, separator and panel body Firefox's; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the four selectors above (one entry each), using the existing `FACE`, `BLACK`, `SELECTION` and `WHITE` constants and `BUTTON_BEVEL` (import it from `support.gtk_theme_spec`): each normal control has `background-color: FACE`, `color: BLACK`, `border: 1px solid BLACK`, `border-radius: 0` and `box-shadow: BUTTON_BEVEL`; each hover control has `background-color: SELECTION`, `color: BLACK` and `box-shadow: none`, all with `!important`.
- New `TestFirefoxChrome.test_permission_popup_control_paint_is_scoped_to_the_permission_popup` asserts the selectors naming `permission-popup` are exactly those four, each starts with `#permission-popup`, each equals its `REQUIRED_RULES` entry, the normal rules carry no `:hover`, both hover rules carry `:hover` and `:not([disabled])`, and no rule in the sheet defines `--button-background-color`, `--button-border-color` or `--button-border-radius`. Using `support.selector_matching.matches`, a remove button inside `#permission-popup` and `#permission-popup-menulist` each match both their rules, their `[disabled]` and non-hover forms match only the normal rule, and a row `hbox.permission-popup-permission-item`, a `.permission-popup-permission-icon`, a `.permission-popup-permission-label`, a `.permission-popup-permission-state-label`, the `.panel-header` box, its `html:span`, the `toolbarseparator` and the storage-access `moz-support-link` each match neither rule; a same-class remove button outside `#permission-popup` and a menulist with another id each match neither rule.
- `test_header_names_provenance_and_preference` gains the strings `"No reference shows Firefox's permission popup"`, `"widgets/button.svg"`, `"tests/test_desktoptheme_button.py::TestButton"`, `"tests/test_desktoptheme_button_reference.py::TestButtonReference"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"chrome/browser/content/browser/browser.xhtml"`, `"template-permission-popup"`, `"chrome/browser/content/browser/browser-sitePermissionPanel.js"`, `"_createPermissionItem"`, `"_createPermissionClearButton"`, `"chrome/browser/skin/classic/browser/controlcenter/panel.css"`, `"permission-popup-permission-remove-button"`, `"permission-popup-menulist"`, `"chrome/toolkit/skin/classic/global/button.css"`, `"chrome/toolkit/skin/classic/global/menulist.css"`, `"chrome/toolkit/skin/classic/global/design-system/tokens-shared.css"`, `"--button-background-color"`, `"--button-border-radius"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md` gains a row in the `## firefox` table after the site-information row (after the protections-panel row once that plan has landed): the permission popup's clear button and permission menulist are square `#DDDDDD` controls with a black outline and the reference's white/`#AAAAAA` raised bevel, and an enabled hovered one is flat `#CCCCFF` with black text and no bevel, while the permission rows, labels, icons, header, separator and panel body stay Firefox's; its test column names the new test, and its provenance records the missing Firefox permission-popup reference, the `widgets/button.svg` bevel with the pinned anchors, the installed Firefox ESR 153.5.1 files and symbols above, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing sheet rules, the install and their tests keep their declarations and scope.

### Firefox Platinum chrome: paint the protections panel rows like a Platinum menu (planned 2026-10-26 by the plan role; independent of the landed Kvantum size-grip plan) — done 2026-10-26 by the feature role

**Goal.** Make Firefox's protections panel (`#protections-popup`, the shield menu that shows the site's tracking-protection state and blocked categories) read as a Mac OS 8.6 menu: each `.subviewbutton` row is square, and an enabled one under the pointer takes the flat `#CCCCFF` fill with black text and no toolbar bevel (the show-report footer row also paints when its stack is hovered). The panel header (including PanelMultiView's generated back buttons), the tracking-protection toggle, the dynamically built tracker/cookie list rows, separators, icons and the panel body stay Firefox's.

**Grounding.** No reference screenshot shows Firefox chrome or its protections panel. The row fill adapts the reference-grounded `widgets/viewitem.svg`, whose `hover`/`selected`/`selected+hover` slices are each a flat square `#CCCCFF` with no bevel or outline (`tests/test_desktoptheme_viewitem.py::TestViewItem`), and reuses the sheet's existing menu-item mapping (`menupopup > menuitem:hover`). `#CCCCFF` is the project's sampled `[Colors:Selection]` token pinned by `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`.

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<html:template id="template-protections-popup">` with `<panel id="protections-popup" class="panel-no-padding">`, its `<panelmultiview id="protections-popup-multiView" mainViewId="protections-popup-mainView">`, the main `<panelview id="protections-popup-mainView" class="PanelUI-subView" mainview-with-header="true" has-custom-header="true">`, and the custom header `<box id="protections-popup-mainView-panel-header" class="panel-header panel-header-with-additional-element panel-header-with-info-button">` holding `#protections-popup-info-button` (class `panel-info-button`) and the two toast buttons. The main view's `<vbox id="protections-popup-main-body" class="panel-subview-body">` holds `#protections-popup-tp-switch` (`html:moz-toggle`), `#protections-popup-report-broken-site-button` (`.subviewbutton .subviewbutton-nav`, `disabled` by default) and `#protections-popup-category-list` with the category rows `#protections-popup-category-trackers`, `-socialblock`, `-cookies`, `-cryptominers` and `-fingerprinters` (each `.protections-popup-category .subviewbutton .subviewbutton-iconic`); the footer `<vbox id="protections-popup-footer" class="panel-subview-footer-button">` holds `#protections-popup-settings-button` and the `<stack id="protections-popup-show-report-stack">` that holds `#protections-popup-show-report-button` (`.subviewbutton .protections-popup-footer-button`) and `#protections-popup-trackers-blocked-counter-box`, and the same view holds `#protections-popup-milestones-content` (`.subviewbutton`) and `#protections-popup-cookie-banner-switch` (`.subviewbutton .subviewbutton-nav`). The trackers/cookies/social-block subviews each hold a `#protections-popup-<name>View` panelview whose footer is a `.subviewbutton .panel-subview-footer-button` (for example `#protections-popup-trackersView-settings-button`). `chrome/browser/content/browser/browser-siteProtections.js` builds each tracker/cookie list row as an HTML `<div class="protections-popup-list-item">` (with no `.subviewbutton`), marks undetected categories `disabled`, and the CSS hides `[uidisabled]` rows. `moz-src/browser/components/customizableui/PanelMultiView.sys.mjs` builds a subview header's back button with `subviewbutton subviewbutton-iconic subviewbutton-back` inside a `.panel-header`. `chrome/browser/skin/classic/browser/controlcenter/panel.css` owns the protections panel layout and its category/footer hover paint, including the show-report stack's hover (so a button-only hover would leave the counter overlay's half of the row unpainted); `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` `border-radius: var(--panel-menuitem-border-radius)` and the ghost hover tokens `--button-text-color-ghost-hover` / `--button-background-color-ghost-hover`; `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines `--panel-menuitem-border-radius`. The sheet's generic `toolbarbutton:hover:not([disabled="true"])` adds the raised bevel, and nothing in the sheet targets `#protections-popup`, so today a row keeps Firefox's violet wash and rounded corners and the footer rows keep the toolbar bevel.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the site-information panel rules and before the all-tabs comment, add two rule blocks (three selectors) with a short comment (each selector on one line so the parsed text matches the test's expectation):

```css
#protections-popup .subviewbutton:not(.panel-header .subviewbutton) {
  border-radius: 0 !important;
}

#protections-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled]),
#protections-popup-show-report-stack:hover > .protections-popup-footer-button:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Square the rows directly rather than overriding `--panel-menuitem-border-radius`, because that token is shared with the app-menu, overflow, all-tabs, unified-extensions and identity rows. The `.subviewbutton` selector covers the report-broken-site row, the five category rows, the milestones and cookie-banner rows, both footer rows and each subview's footer row. Excluding `.panel-header .subviewbutton` leaves PanelMultiView's generated back buttons Firefox's. `#protections-popup-show-report-button` shares its `#protections-popup-show-report-stack` with `#protections-popup-trackers-blocked-counter-box`, so the third selector paints the show-report footer row when the stack is hovered (stock `panel.css` puts the footer hover on the stack, and a button-only hover would leave the counter overlay's half of the row unpainted); the button's own hover stays covered by the generic hover selector. Both hover selectors exclude disabled rows (including the not-found categories the script marks `disabled`) and paint while `:active` too, so they out-specify the stock category/footer hover and the generic toolbar bevel. Add no rule for the `moz-toggle` tracking switch, the header info button, the `.protections-popup-list-item` tracker rows, separators, icons or the panel body. Do not change the `#appMenu-popup`, `#widget-overflow`, `#allTabsMenu-allTabsView`, `#unified-extensions-panel` or `#identity-popup` selectors.

In the header comment block, append a provenance paragraph after the site-information paragraph and before the closing `*/`: no reference shows Firefox's protections panel; the row fill adapts `widgets/viewitem.svg` and the sheet's menu-item mapping (platform colour adaptation 2026-10-26); `chrome/browser/skin/classic/browser/controlcenter/panel.css` owns the protections panel layout and its category/footer hover, `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` its `--panel-menuitem-border-radius` and ghost hover, `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines those tokens, `chrome/browser/content/browser/browser.xhtml` defines the `template-protections-popup` elements above, `chrome/browser/content/browser/browser-siteProtections.js` builds the `.protections-popup-list-item` rows and disables undetected categories, and `moz-src/browser/components/customizableui/PanelMultiView.sys.mjs` creates the `.panel-header` back button; the sheet squares and recolours the `.subviewbutton` rows only (the show-report row also on its stack's hover, because the blocked-counter box overlays the button), leaving the header, the `moz-toggle` switch, the tracker list rows, separators and the panel body Firefox's; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the three selectors above (one entry each): the square selector with `border-radius: 0 !important`; the generic hover selector and the stack hover selector each with `background-color: #CCCCFF !important` (via `SELECTION`), `color: #000000 !important` (via `BLACK`) and `box-shadow: none !important`.
- New `TestFirefoxChrome.test_protections_popup_row_paint_is_scoped_to_the_protections_popup` asserts the selectors naming `protections-popup` are exactly those three, the square selector and generic hover selector start with `#protections-popup` and exclude `.panel-header .subviewbutton`, each equals its `REQUIRED_RULES` entry, the square selector carries no declaration besides `border-radius`, both hover selectors carry `:hover` and `:not([disabled])`, and no rule in the sheet overrides `--panel-menuitem-border-radius`. Using `support.selector_matching.matches`, a category row, `#protections-popup-report-broken-site-button`, `#protections-popup-settings-button`, `#protections-popup-show-report-button`, `#protections-popup-milestones-content`, `#protections-popup-cookie-banner-switch` and a trackers-subview footer button each match the square rule and the generic hover rule when hovered; a disabled such row matches neither hover selector; the show-report button also matches the stack hover selector only when its parent `#protections-popup-show-report-stack` is hovered, and the blocked-counter box, a `.panel-header` back `toolbarbutton.subviewbutton.subviewbutton-iconic.subviewbutton-back`, `#protections-popup-info-button` (`panel-info-button`), the `html:moz-toggle#protections-popup-tp-switch`, a `div.protections-popup-list-item` and a `toolbarbutton.toolbarbutton-1` under `#nav-bar` each match none of the three selectors.
- `test_header_names_provenance_and_preference` gains the strings `"No reference shows Firefox's protections panel"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"chrome/browser/skin/classic/browser/controlcenter/panel.css"`, `"chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css"`, `"chrome/browser/content/browser/browser.xhtml"`, `"chrome/browser/content/browser/browser-siteProtections.js"`, `"moz-src/browser/components/customizableui/PanelMultiView.sys.mjs"`, `"#protections-popup"`, `"protections-popup-mainView-panel-header"`, `"protections-popup-main-body"`, `"protections-popup-category-trackers"`, `"protections-popup-report-broken-site-button"`, `"protections-popup-settings-button"`, `"protections-popup-show-report-stack"`, `"protections-popup-trackers-blocked-counter-box"`, `"protections-popup-milestones-content"`, `"protections-popup-cookie-banner-switch"`, `"protections-popup-list-item"`, `"subviewbutton-back"`, `"--panel-menuitem-border-radius"`, `"--button-background-color-ghost-hover"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md` gains a row in the `## firefox` table after the site-information row: the protections panel rows (`#protections-popup .subviewbutton` outside `.panel-header`) are square, and an enabled hovered row is flat `#CCCCFF` with black text and no toolbar bevel; the show-report footer row takes the same fill when its stack (holding the blocked-counter box) is hovered, while the generated back buttons, the `moz-toggle` tracking switch, the `.protections-popup-list-item` tracker rows, the header, separators and panel body stay Firefox's; its test column names the new test, and its provenance records the missing Firefox protections-panel reference, the `widgets/viewitem.svg` and menu-item mapping with the pinned anchors, the installed Firefox ESR 153.5.1 files, elements and tokens above, including the show-report stack and blocked-counter box, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing sheet rules, the install and their tests keep their declarations and scope.

### Kvantum Platinum size grip: draw the reference's grow-box diamond (planned 2026-10-26 by the plan role; independent of the Firefox site-information panel plan) — done 2026-10-26 by the feature role

**Goal.** Make a Qt size grip (`QSizeGrip`, which Kvantum draws from its `[SizeGrip]` section) read as a Mac OS 8.6 grow box. `org.macos8.desktop.kvconfig` defines no `[SizeGrip]` section, so a KDE/Qt window's bottom-right resize grip falls back to Kvantum's compiled-in art instead of the Platinum grow box the reference windows show. Add the section and draw its indicator from the reference: a white and `#777777` checker diamond with the three `#AAAAAA` pixels the reference shows along its lower-left edge, with a transparent surround so the grip sits on whatever face the widget draws.

**Grounding.** No reference screenshot shows a KDE/Qt size grip, so the section and key names are Kvantum-required and the art adapts the grow box in a reference window. In `macos8.6-screenshots/systemprofiler_betawiki.png` (the retail Japanese 8.6 System Profiler window whose tabs already ground `test_kvantum_tab_reference.py`), the window's bottom-right grow box occupies the 12x11 rectangle x=796..807, y=748..758 on the window-frame `#CCCCCC` face. Its 132 pixels are 90 `#CCCCCC`, 21 `#FFFFFF`, 18 `#777777` and three `#AAAAAA` (at 797/754, 799/756 and 801/758); the diamond's non-background pixels are the pinned pattern. `#777777` is a new sampled fill, so add `SIZEGRIP_DARK = "#777777"` to `tests/support/platinum_palette.py`; the `#AAAAAA` edge pixels reuse the existing `BUTTON_SHADOW` value already allowed by `TestSvg.test_uses_exactly_the_platinum_palette`. The installed Kvantum themes ship `[SizeGrip]` with only `indicator.element=sizegrip` (for example `/usr/share/Kvantum/KvantumAlt/KvantumAlt.kvconfig`) or `indicator.element=resize-grip`, and name the art `<element>-normal`/`<element>-focused`; `[SizeGrip]`, the `indicator.element` key and those state suffixes are Kvantum-required, while the element id `sizegrip` is this theme's chosen value (the installed themes also use `resize-grip`). The reference's `#CCCCCC` is the surrounding window frame, not part of the indicator, so the shipped art draws no background rect.

**Approach.**
- In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, after `[HeaderSection]`, add `[SizeGrip]` with the single setting `indicator.element=sizegrip` and a short comment naming the provenance exception (no reference shows a KDE/Qt size grip; the art adapts the window grow box, platform adaptation 2026-10-26).
- In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, after the branch arrows, add `sizegrip-normal` and `sizegrip-focused` groups, each led by an invisible 12x11 `x=0`/`y=0` bounds rect with `fill="none"` so Kvantum scales the element at the sampled footprint, then one 1x1 `<rect>` for every non-`#CCCCCC` pixel of the sampled 12x11 region, at that pixel's relative coordinate and with that pixel's sampled fill (`#FFFFFF`, `#777777` or `#AAAAAA`). Ship no rect for the 90 background pixels. Put the groups at the next two 60px slots and raise the root canvas height by 120. Update the header comment to name the sampled grow box, its origin, the bounds rect and the three fills.
- In `tests/support/kvantum_config_spec.py`, add `"SizeGrip": {"indicator.element": "sizegrip"}` to `FRAMELESS_SECTIONS` so `test_every_section_is_pinned`, `test_every_frameless_section_resolves_its_pins` and `test_every_key_is_pinned` cover the new section and setting.
- In `tests/support/platinum_palette.py`, add the sampled `SIZEGRIP_DARK` constant with a comment naming the reference and its pixel anchors.
- In `tests/test_kvantum_svg.py`, add `sizegrip` to the palette test's `extra` set through `SIZEGRIP_DARK` (the `#AAAAAA` fill is already covered by `BUTTON_SHADOW`), and add a test that both `sizegrip-normal` and `sizegrip-focused` exist, start with the invisible 12x11 bounds rect, and then hold only 1x1 painted rects at distinct coordinates with fills from the three sampled values.
- Add `tests/test_kvantum_sizegrip_reference.py`. It uses `ReferenceScreenshotMixin` with `REFERENCE = PROFILER_REFERENCE`, its own `MAX_ROWS = 760` (the grow box is below `PROFILER_ROWS`' 256), and the origin/width/height constants above. One test re-derives the 12x11 reference region and asserts its exact colour map (including the three `#AAAAAA` pixels) and the `#CCCCCC` corner. A second test composes the shipped `sizegrip-normal` and `sizegrip-focused` rects onto the sampled `#CCCCCC` background and asserts both maps equal the reference map, so a hand-drawn symmetric diamond, a missing edge pixel, a wrong fill or a stray background rect fails.
- `README.md`: in the Kvantum paragraph, add that a Qt size grip draws the reference grow box's white/`#777777` diamond.
- `docs/invariants.md`: add a `## kvantum` row: the size grip draws the reference grow box's 12x11 diamond on a transparent surround, with the three sampled fills, while the section has no frame or interior; its test column names `tests/test_kvantum_sizegrip_reference.py::TestSizeGripReference`, `tests/test_kvantum_svg.py::TestSvg`, `tests/test_kvantum_config.py::TestSectionCoverage` and `tests/test_kvantum_config.py::TestValueKeys`, and its provenance records that no reference screenshot shows a KDE/Qt size grip, that `[SizeGrip]`, the `indicator.element` key and the state suffixes are Kvantum-required while the element id `sizegrip` is a chosen value (installed themes also use `resize-grip`), the art adapts the window grow box in `systemprofiler_betawiki.png` at x=796..807, y=748..758 (platform adaptation 2026-10-26), the `#777777`/`#AAAAAA` fills, and that SVG checks do not establish rendered Qt pixels. `tests/invariants.py` stays green.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, `tests/support/kvantum_config_spec.py`, `tests/support/platinum_palette.py`, `tests/test_kvantum_svg.py`, `tests/test_kvantum_sizegrip_reference.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- `[SizeGrip]` resolves `indicator.element` to `sizegrip` and declares no frame, interior or other unpinned setting; `TestSectionCoverage` and `TestValueKeys` pin it through `FRAMELESS_SECTIONS`.
- `sizegrip-normal` and `sizegrip-focused` each exist, carry an invisible 12x11 bounds rect (`fill="none"`) that fixes the footprint, and contain one 1x1 rect per non-background reference pixel (42 rects), with no two painted rects at the same coordinate and no background rect; their painted fills are exactly `#FFFFFF`, `#777777` and `#AAAAAA`.
- `TestSizeGripReference.test_reference_grow_box_pattern` re-derives the 12x11 region and asserts the 90 `#CCCCCC`, 21 `#FFFFFF`, 18 `#777777` and three `#AAAAAA` pixels at their coordinates (including 797/754, 799/756 and 801/758).
- `TestSizeGripReference.test_shipped_size_grip_paints_the_reference_pattern` composes both shipped state groups onto the sampled background and asserts each equals the reference pixel map; a symmetric white/`#777777` diamond without the edge pixels, a misplaced pixel or a re-coloured fill fails.
- `TestSvg.test_uses_exactly_the_platinum_palette` accepts `SIZEGRIP_DARK`, and `TestSvg` pins both size-grip states' 12x11 bounds rect and their 1x1-rect children.
- `docs/invariants.md` carries the new `## kvantum` row with its test columns and provenance, and `tests/invariants.py` is green.
- `make check` passes, and the existing Kvantum config, palette, SVG and reference tests keep their assertions.

### Firefox Platinum chrome: paint the site-information panel rows like a Platinum menu (planned 2026-10-26 by the plan role; independent of the waiting unified extensions panel plan) — done 2026-10-26 by the feature role

**Goal.** Make Firefox's site-information panel (`#identity-popup`, the lock/shield panel that shows a page's connection, permissions and clear-site-data action) read as a Mac OS 8.6 menu: its `.subviewbutton` rows — the connection row `#identity-popup-security-button` and the footer rows `#identity-popup-clear-sitedata-button` and `#identity-popup-more-info` — are square, and an enabled one under the pointer takes the flat `#CCCCFF` fill with black text and no toolbar bevel. Disabled rows, focus rings, separators, the panel header (including PanelMultiView's generated `.subviewbutton-back` back button), the security view's `.panel-button` action, icons and the panel body stay Firefox's.

**Grounding.** No reference screenshot shows Firefox chrome or its site-information panel. The row fill adapts the reference-grounded `widgets/viewitem.svg`, whose `hover`/`selected`/`selected+hover` slices are each a flat square `#CCCCFF` with no bevel or outline (`tests/test_desktoptheme_viewitem.py::TestViewItem`), and reuses the sheet's existing menu-item mapping (`menupopup > menuitem:hover`). `#CCCCFF` is the project's sampled `[Colors:Selection]` token pinned by `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`.

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<html:template id="template-identity-popup">` with `<panel id="identity-popup" class="panel-no-padding site-information-popup" type="arrow">`, its `<panelmultiview id="identity-popup-multiView" mainViewId="identity-popup-mainView">`, a `<panelview id="identity-popup-mainView" class="PanelUI-subView" mainview-with-header="true">`, the hardcoded `<box id="identity-popup-mainView-panel-header" class="panel-header">`, and that view's `<vbox class="panel-subview-body">` holding the `<toolbarbutton id="identity-popup-security-button" class="identity-popup-security-connection subviewbutton subviewbutton-iconic">`; the `<vbox id="identity-popup-clear-sitedata-footer" class="panel-subview-footer-button">` holds the `<toolbarbutton id="identity-popup-clear-sitedata-button" class="subviewbutton">` and is a sibling after the main view's `.panel-subview-body`, not inside it. The separate security view `<panelview id="identity-popup-securityView" class="PanelUI-subView">` has its own `.panel-subview-body` holding the `<button id="identity-popup-remove-cert-exception" class="panel-button">` action, and the `<vbox id="identity-popup-more-info-footer">` holding the `<toolbarbutton id="identity-popup-more-info" class="subviewbutton panel-subview-footer-button">` is a sibling after that body. `/usr/lib/firefox-esr/omni.ja` `moz-src/browser/components/customizableui/PanelMultiView.sys.mjs` builds a subview header's back button with `subviewbutton subviewbutton-iconic subviewbutton-back` inside a `.panel-header`. `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` `border-radius: var(--panel-menuitem-border-radius)` and the ghost hover tokens `--button-text-color-ghost-hover` / `--button-background-color-ghost-hover`; `chrome/browser/skin/classic/browser/controlcenter/panel.css` owns the identity panel's layout and consumes the ghost-hover token; `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines `--panel-menuitem-border-radius`. The sheet's generic `toolbarbutton:hover:not([disabled="true"])` adds the raised bevel, and nothing in the sheet targets `#identity-popup`, so today a row keeps Firefox's violet wash and rounded corners and the footer rows keep the toolbar bevel.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the toolbar overflow panel rules and before the all-tabs comment, add two rules with a short comment (each selector on one line so the parsed text matches the test's expectation):

```css
#identity-popup .subviewbutton:not(.panel-header .subviewbutton) {
  border-radius: 0 !important;
}

#identity-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Square the rows directly rather than overriding `--panel-menuitem-border-radius`, because that token is shared with the app-menu, overflow, all-tabs and unified-extensions rows. The `.subviewbutton` selector covers the connection row and both footer rows. Excluding `.panel-header .subviewbutton` leaves PanelMultiView's generated back button Firefox's, the same way the app-menu plan leaves its header buttons. The hover rule excludes disabled rows and paints while `:active` too, so it out-specifies the stock ghost pressed rule and the generic toolbar bevel. Add no rule for the `.panel-button` certificate action, the panel header, separators, icons or the panel body. Do not change the `#appMenu-popup`, `#widget-overflow`, `#allTabsMenu-allTabsView` or `#unified-extensions-panel` selectors.

In the header comment block, append a provenance paragraph after the toolbar overflow paragraph and before the closing `*/`: no reference shows Firefox's site-information panel; the row fill adapts `widgets/viewitem.svg` and the sheet's menu-item mapping (platform colour adaptation 2026-10-26); `chrome/browser/skin/classic/browser/controlcenter/panel.css` owns the identity panel layout and ghost-hover consumption, `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` its `--panel-menuitem-border-radius` and ghost hover, `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines those tokens, `chrome/browser/content/browser/browser.xhtml` defines the `template-identity-popup` elements above, and `moz-src/browser/components/customizableui/PanelMultiView.sys.mjs` creates the `.panel-header` back button; the sheet squares and recolours the rows only, leaving the back button, the `.panel-button` action, header, separators and panel body Firefox's; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the two selectors above (one entry each): the square selector with `border-radius: 0 !important`, the hover selector with `background-color: #CCCCFF !important` (via `SELECTION`), `color: #000000 !important` (via `BLACK`) and `box-shadow: none !important`.
- New `TestFirefoxChrome.test_identity_popup_row_paint_is_scoped_to_the_identity_popup` asserts the selectors naming `identity-popup` are exactly those two, each starts with `#identity-popup`, each equals its `REQUIRED_RULES` entry, the square selector carries no declaration besides `border-radius`, the hover selector carries `:hover` and `:not([disabled])`, both exclude `.panel-header .subviewbutton`, and no rule in the sheet overrides `--panel-menuitem-border-radius`. Using `support.selector_matching.matches`, the `toolbarbutton#identity-popup-security-button.subviewbutton.subviewbutton-iconic` inside the main view's `.panel-subview-body` matches both rules; a disabled such button matches neither hover rule; the `#identity-popup-clear-sitedata-button` footer row and the `#identity-popup-more-info` footer row each match both; a `.panel-header` back `toolbarbutton.subviewbutton.subviewbutton-iconic.subviewbutton-back` matches neither; the `button#identity-popup-remove-cert-exception` carrying only `.panel-button` matches neither; and a `toolbarbutton.toolbarbutton-1` under `#nav-bar` matches neither.
- `test_header_names_provenance_and_preference` gains the strings `"No reference shows Firefox's site-information panel"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"chrome/browser/skin/classic/browser/controlcenter/panel.css"`, `"chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css"`, `"chrome/browser/content/browser/browser.xhtml"`, `"moz-src/browser/components/customizableui/PanelMultiView.sys.mjs"`, `"#identity-popup"`, `"identity-popup-mainView-panel-header"`, `"identity-popup-security-button"`, `"identity-popup-clear-sitedata-button"`, `"identity-popup-more-info"`, `"subviewbutton-back"`, `"--panel-menuitem-border-radius"`, `"--button-background-color-ghost-hover"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md` gains a row in the `## firefox` table after the toolbar overflow row: the site-information panel rows (`#identity-popup .subviewbutton` outside `.panel-header`) are square, and an enabled hovered row is flat `#CCCCFF` with black text and no toolbar bevel, while the generated back button, the `.panel-button` certificate action, panel header, separators and panel body stay Firefox's; its test column names the new test, and its provenance records the missing Firefox site-information reference, the `widgets/viewitem.svg` and menu-item mapping with the pinned anchors, the installed Firefox ESR 153.5.1 files, elements and tokens above, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing sheet rules, the install and their tests keep their declarations and scope.

### Firefox Platinum chrome: paint the unified extensions panel rows like a Platinum menu (planned 2026-10-26 by the plan role; independent of the waiting about:downloads install plan) — done 2026-10-26 by the feature role

**Goal.** Make Firefox's unified extensions panel (`#unified-extensions-panel`, the puzzle-piece menu that lists the installed extensions) read as a Mac OS 8.6 menu: each extension row's action button and the `#unified-extensions-manage-extensions` footer row is square, and an enabled one under the pointer takes the flat `#CCCCFF` fill with black text and no toolbar bevel. The per-row gear menu button keeps Firefox's own icon-only hover paint, and the panel header, separators and empty state stay Firefox's.

**Grounding.** No reference screenshot shows Firefox chrome or its unified extensions panel. The row fill adapts the reference-grounded `widgets/viewitem.svg`, whose `hover`/`selected`/`selected+hover` slices are each a flat square `#CCCCFF` with no bevel or outline (`tests/test_desktoptheme_viewitem.py::TestViewItem`), and reuses the sheet's existing menu-item mapping (`menupopup > menuitem:hover`). `#CCCCFF` is the project's sampled `[Colors:Selection]` token pinned by `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`.

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<html:template id="unified-extensions-panel-template">` with `<panel id="unified-extensions-panel" type="arrow">`, its `<panelview id="unified-extensions-view" class="cui-widget-panelview">`, a `<box class="panel-header">`, a `<vbox class="panel-subview-body">` holding `#overflowed-extensions-list`, `#unified-extensions-area` and `<vbox class="unified-extensions-list">`, and the `<toolbarbutton id="unified-extensions-manage-extensions" class="subviewbutton panel-subview-footer-button">` footer. Its `<html:template id="unified-extensions-item-template">` puts a `<toolbarbutton class="unified-extensions-item-action-button subviewbutton">` and a `<toolbarbutton class="unified-extensions-item-menu-button subviewbutton subviewbutton-iconic">` inside a `<box class="unified-extensions-item-row-wrapper">`. `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` `border-radius: var(--panel-menuitem-border-radius)` and the ghost hover tokens `--button-text-color-ghost-hover` / `--button-background-color-ghost-hover`; `chrome/browser/skin/classic/browser/addons/unified-extensions.css` sets the item buttons' `--uei-button-hover-bgcolor` to that ghost-hover token and deliberately paints the gear menu button's background transparent with its paint on the icon only; `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines `--panel-menuitem-border-radius`. `chrome/browser/content/browser/browser-addons.js` builds the empty state's `#unified-extensions-discover-extensions` button as a `moz-button` carrying `.subviewbutton`. The sheet's generic `toolbarbutton:hover:not([disabled="true"])` adds the raised bevel, and nothing in the sheet targets `#unified-extensions-panel`, so today an extension row keeps Firefox's violet wash and rounded corners and the footer row keeps the toolbar bevel.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the toolbar overflow panel rules and before the all-tabs comment, add three rules with short comments (each selector on one line so the parsed text matches the test's expectation):

```css
#unified-extensions-panel .subviewbutton:not(.panel-header .subviewbutton):not(.unified-extensions-item-menu-button):not(#unified-extensions-discover-extensions) {
  border-radius: 0 !important;
}

#unified-extensions-panel .subviewbutton:not(.panel-header .subviewbutton):not(.unified-extensions-item-menu-button):not(#unified-extensions-discover-extensions):hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}

#unified-extensions-panel .unified-extensions-item-menu-button:hover {
  box-shadow: none !important;
}
```

Square the rows directly rather than overriding `--panel-menuitem-border-radius`, because that token is shared with the app-menu, overflow and all-tabs rows. The `.subviewbutton` selector covers the custom-element action button, the plain extension buttons placed in `#overflowed-extensions-list` and `#unified-extensions-area`, and the footer manage row. Excluding `.unified-extensions-item-menu-button` leaves the gear's stock transparent button background and icon-only hover paint in place, the same way the all-tabs plan leaves the mute and close buttons Firefox's, so the row fill never paints a square block behind it. The gear is still a `toolbarbutton`, so the sheet's generic `toolbarbutton:hover` raised bevel would paint it; the third rule drops that `box-shadow` on the gear and changes nothing else about it. Excluding `.panel-header .subviewbutton` keeps a future header button Firefox's, and excluding `#unified-extensions-discover-extensions` keeps the empty state's `moz-button` Firefox's. The hover rule excludes disabled rows and paints while `:active` too, so it out-specifies the stock ghost pressed rule and the generic toolbar bevel. Add no rule for the panel header, separators, empty state or icons. Do not change the `#appMenu-popup` or `#widget-overflow` selectors.

In the header comment block, append a provenance paragraph after the toolbar overflow paragraph and before the closing `*/`: no reference shows Firefox's unified extensions panel; the row fill adapts `widgets/viewitem.svg` and the sheet's menu-item mapping (platform colour adaptation 2026-10-26); `chrome/browser/skin/classic/browser/addons/unified-extensions.css` gives the item buttons their ghost-hover token and paints the gear's icon only, `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` its `--panel-menuitem-border-radius` and ghost hover, `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines those tokens, and `chrome/browser/content/browser/browser.xhtml` defines the `unified-extensions-panel-template` and `unified-extensions-item-template` elements above; the sheet squares and recolours the rows only, drops the generic toolbar bevel from the gear menu button so its own icon-only hover paint shows, and leaves the panel header, separators and empty state Firefox's; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the three selectors above (one entry each): the square selector with `border-radius: 0 !important`, the hover selector with `background-color: #CCCCFF !important` (via `SELECTION`), `color: #000000 !important` (via `BLACK`) and `box-shadow: none !important`, and the gear selector with only `box-shadow: none !important`.
- New `TestFirefoxChrome.test_unified_extensions_panel_row_paint_is_scoped_to_the_panel` asserts the selectors naming `unified-extensions` are exactly those three, each starts with `#unified-extensions-panel`, each equals its `REQUIRED_RULES` entry, the square selector carries no declaration besides `border-radius`, the hover selector carries `:hover` and `:not([disabled])`, both row selectors exclude `.unified-extensions-item-menu-button`, `.panel-header .subviewbutton` and `#unified-extensions-discover-extensions`, the gear selector carries no declaration besides `box-shadow`, and no rule in the sheet overrides `--panel-menuitem-border-radius`. Using `support.selector_matching.matches`, an action `toolbarbutton.unified-extensions-item-action-button.subviewbutton` inside a `.unified-extensions-item-row-wrapper` inside `unified-extensions-item` inside `<vbox class="unified-extensions-list">` inside `.panel-subview-body` matches both row rules; a disabled such button matches neither hover rule; a `toolbarbutton.webextension-browser-action.subviewbutton` inside `#unified-extensions-area` matches both row rules; the `#unified-extensions-manage-extensions` footer matches both row rules; the `.unified-extensions-item-menu-button` gear matches neither row rule but matches the gear rule when hovered; a `.subviewbutton` inside a `.panel-header`, the empty-state `moz-button#unified-extensions-discover-extensions`, and a `toolbarbutton.toolbarbutton-1` under `#nav-bar` match none of the three.
- `test_header_names_provenance_and_preference` gains the strings `"No reference shows Firefox's unified extensions panel"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"chrome/browser/skin/classic/browser/addons/unified-extensions.css"`, `"chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css"`, `"chrome/browser/content/browser/browser.xhtml"`, `"chrome/browser/content/browser/browser-addons.js"`, `"#unified-extensions-discover-extensions"`, `"#unified-extensions-panel"`, `"#unified-extensions-view"`, `"unified-extensions-item-action-button"`, `"unified-extensions-item-menu-button"`, `"#unified-extensions-manage-extensions"`, `"--panel-menuitem-border-radius"`, `"--button-background-color-ghost-hover"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md` gains a row in the `## firefox` table after the toolbar overflow row: the unified extensions panel rows (`#unified-extensions-panel .subviewbutton` outside `.panel-header` and outside the gear `.unified-extensions-item-menu-button`) are square, and an enabled hovered row is flat `#CCCCFF` with black text and no toolbar bevel, while the gear menu button, panel header, separators and empty state stay Firefox's; its test column names the new test, and its provenance records the missing Firefox unified-extensions reference, the `widgets/viewitem.svg` and menu-item mapping with the pinned anchors, the installed Firefox ESR 153.5.1 files, elements and tokens above, the gear's generic-bevel reset, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing sheet rules, the install and their tests keep their declarations and scope.

### Firefox Platinum chrome, part 2/2: install the about:downloads `userContent.css` beside `userChrome.css` (planned 2026-10-26 by the plan role; independent of the waiting toolbar overflow panel plan) — done 2026-10-26 by the feature role

**Goal.** Make `make install-firefox` copy both standalone Firefox sheets — the landed `userChrome.css` and the part 1/2 about:downloads `userContent.css` — into one profile's `chrome/` directory and add the one marker-delimited `user.js` preference that makes Firefox read them, and make `make remove-firefox` remove exactly those three changes. The two-sheet installer keeps the single-sheet installer's guarantees for both sheets: a non-empty foreign sheet is refused by path with nothing written, an empty or BOM-prefixed sheet of ours is adopted or recognised, a symlinked destination is refused before any write, a failed or interrupted write restores both sheets and `user.js`, and removal leaves a foreign sheet or preference untouched. The sheets' paint and declarations do not change; only how they reach a profile does.

**Grounding.** Part 1/2 landed the sheet at `theme/firefox/org.macos8.desktop/chrome/userContent.css`, whose first line is `/* org.macos8.desktop Firefox content, standalone userContent.css` (pinned by `tests/test_firefox_content_theme.py::TestFirefoxContentTheme::test_first_line_is_the_marker`), and its header still says the sheet is not installed until part 2/2 adds it to `make install-firefox`. The install today lives in `tools/install_firefox.py`: `SHEET` and `CSS_MARKER` name the one sheet, `_apply` reads it and the profile's `chrome/userChrome.css`, refuses a foreign non-empty file, refuses a symlinked destination, publishes the sheet and then `user.js`, and rolls both back from `_restore_file`/`_restore_user_js` on any `BaseException`; `_remove` rewrites `user.js` first, deletes the sheet only when its first line is our marker (BOM-stripped by `_is_our_sheet`), and restores `user.js` whenever the sheet still exists. The destination paths, bounded read and atomic write are `user_chrome_path`, `user_js_path`, `read_profile_text`, `write_profile_bytes` and `MAX_PROFILE_FILE_BYTES` in `tools/firefox_user_files.py`. `docs/invariants.md`'s `## firefox` opt-in-install row states that guarantee, and `tests/test_firefox_install.py` pins it: `TestInstall` and `TestRemove` mock writes and unlinks by exact path, and `TestRemove::test_an_interrupt_after_the_sheet_unlink_takes_effect_keeps_the_removal` encodes the one-sheet rule that an interrupt after the sheet unlink keeps the rewritten `user.js`. A grep of PLANS-DONE.md for `userContent` finds only the part 1/2 entry; no plan covers installing it.

**Approach.** In `tools/firefox_user_files.py`, add `user_content_path(profile)` returning `profile / "chrome" / "userContent.css"` beside `user_chrome_path`, and update the module docstring's two-file description to the three files the installer now reads and writes.

In `tools/install_firefox.py`, add `CONTENT_SHEET = "theme/firefox/org.macos8.desktop/chrome/userContent.css"`, `CONTENT_CSS_MARKER = "/* org.macos8.desktop Firefox content, standalone userContent.css"`, and an ordered module-level `SHEETS` tuple of `(source relative path, marker, path function)` entries: `(SHEET, CSS_MARKER, user_chrome_path)` then `(CONTENT_SHEET, CONTENT_CSS_MARKER, user_content_path)`. Keep `SHEET` and `CSS_MARKER` so existing imports and tests stand. Change `_is_our_sheet(text)` to `_is_our_sheet(text, marker)` and call it with each entry's marker.

Rewrite `_apply` to drive both sheets from `SHEETS` while preserving today's order and diagnostics. Read both shipped sheets up front in `SHEETS` order, wrapping an `OSError`/`ValueError` as `cannot read <source>` for that source (userChrome first, so the existing missing-source diagnostics still name it). Then read each destination with `read_profile_text`, remembering its previous text, and return `report_failure` for the first non-empty destination whose text is not that sheet's marker; nothing is written yet. Keep the existing `user.js` growth check. Refuse a symlink on every sheet destination and then `user.js` before `mkdir`, so a refused link leaves all three paths untouched. Create `chrome/` once, write the sheets in `SHEETS` order (userChrome, then userContent), then `user.js`. On any `BaseException`, call `_restore_file` for each sheet with its remembered text and `_restore_user_js` once, collecting rollback errors in `SHEETS` then `user.js` order, and raise a `ConfigError` combining the original failure with them exactly as today.

Rewrite `_remove` to read both destinations, treat each as owned when its text is that marker, and rewrite `user.js` before deleting anything, as today. Refuse a symlink on every owned sheet and then `user.js`. Delete the owned sheets in `SHEETS` order. On `BaseException`, restore the previous `user.js` only while at least one owned sheet still exists (replace the single `sheet_path.exists()` test with an `any(path.exists() ...)` over the owned sheet paths); once every owned sheet is gone, the rewrite is the completed removal and stays. Keep the existing by-name `cannot remove`/`cannot write` messages.

Update the module docstring and the parser description/epilog to name both sheets and both markers, the Makefile `install-firefox`/`remove-firefox` comments and help lines (`a foreign userChrome.css` becomes `a foreign userChrome.css or userContent.css`), and README's standalone-Firefox paragraph so it names `userContent.css`, both profile destinations and the fact that removal clears three changes. In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, replace the header sentence "This sheet is not installed until part 2/2 adds it to make install-firefox." with "Part 2/2 installs it through make install-firefox." (keeping the `part 2/2` phrase the header test pins). Update the opt-in-install row in `docs/invariants.md` to cover both sheets, both markers and the extended test column.

**Files touched.** `tools/install_firefox.py`, `tools/firefox_user_files.py`, `Makefile`, `README.md`, `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_install.py`, `tests/test_firefox_content_theme.py` (docstring only, if it still says the install is unplanned), `tests/support/validation_gaps.py` (renamed test ledger entries and updated guarantee markers), `docs/invariants.md`, `PLANS.md` (this entry's scope sentence).

**Acceptance criteria.**
- `install_firefox.CONTENT_SHEET` names the shipped `userContent.css`; `install_firefox.SHEETS` lists exactly two entries in userChrome-then-userContent order, each pairing its `SHEET`/`CONTENT_SHEET` source with `CSS_MARKER`/`CONTENT_CSS_MARKER` and `user_chrome_path`/`user_content_path`; and `firefox_user_files.user_content_path(profile)` equals `profile / "chrome" / "userContent.css"`.
- `TestUserJs.test_shipped_marker_and_preference_are_pinned` also asserts the content sheet's BOM-stripped first line equals `install_firefox.CONTENT_CSS_MARKER` and `tests/test_firefox_content_theme.py`'s `MARKER`, and that `CONTENT_SHEET` exists. The existing `CSS_MARKER` pin and one-block `user.js` pin stay unchanged.
- `TestInstall.test_install_copies_the_sheets_byte_for_byte_and_adds_one_block` asserts both installed sheets byte-equal their shipped files and `user.js` holds the marker and preference once; `TestInstall.test_an_empty_sheet_is_adopted` adopts an empty destination for either sheet. `TestInstall.test_a_foreign_sheet_is_refused_and_nothing_is_written` is the `SHEETS`-driven replacement for the foreign-`userChrome.css` test and asserts for each sheet: exit 1, the foreign destination's path in stderr, that file unchanged, the other destination absent, and no `user.js`.
- `TestInstall.test_install_refuses_symlinked_profile_files_before_writing_anything` (the existing symlink test extended to `userContent.css`) asserts for all three destinations that exit 2 names `cannot write <path>` and `symbolic link`, the link and its target are untouched, and the other two destination files are not created. The dangling-link loop, the unreadable-file loop and the FIFO test cover `chrome/userContent.css` as well as `chrome/userChrome.css` and `user.js`.
- New `TestInstall.test_a_failed_user_content_write_removes_the_published_user_chrome` fails the write to `chrome/userContent.css` and asserts exit 2 names that path, `chrome/userChrome.css` is absent (or its prior text restored when it existed), and no `user.js` remains. New `TestInstall.test_a_failed_user_js_write_restores_both_previous_sheets` starts with both sheets carrying prior marker-led text and asserts a failed `user.js` write restores both texts exactly. New `TestInstall.test_an_interrupt_after_the_user_content_write_takes_effect_removes_both` publishes then interrupts on the content-sheet write and asserts neither sheet nor `user.js` remains; the existing failed-restore and interrupt tests still pass with the second sheet present.
- `TestRemove.test_remove_deletes_our_sheets_and_block_and_keeps_the_directory` also asserts `chrome/userContent.css` is gone, the `chrome/` directory remains and `user.js` is empty. New `TestRemove.test_remove_keeps_a_foreign_user_content_and_removes_our_user_chrome` leaves a foreign content sheet and our chrome sheet, then asserts removal drops only the chrome sheet and preference. New `TestRemove.test_remove_deletes_our_user_content_when_user_chrome_is_absent` asserts a lone our-marker content sheet and its preference block are removed. New `TestRemove.test_a_failed_user_content_unlink_is_reported_by_path` unlinks our chrome sheet, fails on the content sheet, and asserts exit 2 names the content path, the content sheet remains, and the previous `user.js` is restored. New `TestRemove.test_an_interrupt_after_only_the_first_sheet_unlink_restores_user_js` interrupts after the chrome-sheet unlink and asserts `user.js` is restored because the content sheet remains; `test_an_interrupt_after_the_sheet_unlink_takes_effect_keeps_the_removal` is retargeted to an interrupt after the last owned (content) sheet unlink, so it still pins the keep-the-removal case. A BOM-prefixed content-sheet marker is recognised for both replacement and removal.
- README's Firefox paragraph names `userContent.css`, `chrome/userChrome.css`, `chrome/userContent.css` and the three changes removal reverses; the Makefile comment and `make help` lines name both sheets and both foreign-sheet refusals; the content sheet's header contains "Part 2/2 installs it through make install-firefox." and `test_header_names_provenance` still passes with its `"part 2/2"` string.
- `docs/invariants.md`'s `## firefox` opt-in-install row now says both sheets are copied byte-for-byte, each with its own marker, and that the refusal, adoption, symlink, rollback, interrupt and removal rules apply to either sheet; its test column names the new and extended tests above, every named test exists, and its provenance records that the profile layout, `userContent.css` name and preference are Firefox-required. `tests/invariants.py` stays green.
- `make check` passes, the two shipped sheets are byte-identical to their pre-change content except the one userContent.css header sentence, and `tests/test_firefox_theme.py` and `tests/test_firefox_content_theme.py`'s paint and palette assertions are unchanged.

### Firefox Platinum chrome: paint the toolbar overflow panel rows like a Platinum menu (planned 2026-10-26 by the plan role; independent of the about:downloads content sheet) — done 2026-10-26 by the feature role

**Goal.** Make Firefox's toolbar overflow panel (`#widget-overflow`, the chevron menu that holds toolbar buttons which do not fit) read as a Mac OS 8.6 menu: every row is square, and an enabled row under the pointer takes the flat `#CCCCFF` menu-item highlight with black text and no toolbar bevel. The panel's disabled rows, focus rings, separators, toolbar springs, panel headers and panel body stay Firefox's. This is the same row treatment the app menu already has, applied to the remaining toolbar-facing arrow panel.

**Grounding.** No reference screenshot shows Firefox chrome or its toolbar overflow panel. The row highlight adapts the reference-grounded `widgets/viewitem.svg`, whose `hover`/`selected`/`selected+hover` slices are each a flat square `#CCCCFF` with no bevel or outline (`tests/test_desktoptheme_viewitem.py::TestViewItem`), and reuses the sheet's existing menu-item mapping (`menupopup > menuitem:hover`). `#CCCCFF` is the project's sampled `[Colors:Selection]` token pinned by `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`. Record the missing Firefox overflow-panel reference and the dated adaptation in the sheet header and the invariants row.

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<panel id="widget-overflow" type="arrow">` around `<panelmultiview id="widget-overflow-mainView">`; its `.panel-subview-body` holds the `.widget-overflow-list` elements `#widget-overflow-list` and `#widget-overflow-fixed-list`, and its footer row is the `toolbarbutton.subviewbutton.panel-subview-footer-button` `#overflowMenu-customize-button`. `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton, .widget-overflow-list .toolbarbutton-1` `border-radius: var(--panel-menuitem-border-radius)` and gives `toolbarbutton.subviewbutton`, `.widget-overflow-list .toolbarbutton-1` and `.toolbaritem-combined-buttons:is(...) > toolbarbutton` the ghost hover tokens `--button-text-color-ghost-hover` and `--button-background-color-ghost-hover`, with a pressed shadow; `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines `--panel-menuitem-border-radius: var(--border-radius-small)` (4px) and maps the ghost hover to the violet theme token. The sheet's `panel[type="arrow"]` rule already sets the panel face `#DDDDDD` and black text, its generic `toolbarbutton:hover:not([disabled="true"])` adds the raised bevel, and nothing in the sheet targets `#widget-overflow`, so today these rows keep Firefox's violet wash and rounded corners.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, immediately after the app-menu hover rule and before the all-tabs comment, add two rules with a short comment:

```css
#widget-overflow .subviewbutton:not(.panel-header .subviewbutton),
#widget-overflow .widget-overflow-list .toolbarbutton-1 {
  border-radius: 0 !important;
}

#widget-overflow .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled]),
#widget-overflow .widget-overflow-list .toolbarbutton-1:hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Square the rows directly rather than overriding `--panel-menuitem-border-radius`, because that token is shared with the all-tabs, library and history subviewbuttons. The `.subviewbutton` selectors cover the footer customize row and exclude `.panel-header` descendants (the main view has no header today) so a future subview's back or edit button keeps Firefox's paint; the `.widget-overflow-list .toolbarbutton-1` selectors cover the overflowed toolbar items in both lists. The hover rule excludes disabled rows and matches while `:active` too, so it out-specifies Firefox's ghost pressed rule and the sheet's generic toolbar bevel. Add no rule for separators, toolbar springs, focus rings, icons, text, the panel body or the panel header.

In the header, append a provenance paragraph after the app-menu paragraph and before the closing `*/`: no reference shows Firefox's toolbar overflow panel; the row highlight adapts `widgets/viewitem.svg` and the sheet's menu-item mapping (platform colour adaptation 2026-10-26); Firefox's `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` and `.widget-overflow-list .toolbarbutton-1` their `--panel-menuitem-border-radius` and their `--button-background-color-ghost-hover` violet hover, `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines those tokens, `chrome/browser/content/browser/browser.xhtml` defines `#widget-overflow`, its two `.widget-overflow-list` lists and the `#overflowMenu-customize-button` footer row, and the sheet squares and suppresses the ghost hover and generic toolbar bevel on those rows only, leaving the panel's disabled rows, focus rings, separators, springs and panel-header buttons Firefox's; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the four selectors above (each list item of a grouped rule is one entry), with `border-radius: 0 !important` for the two square selectors and `background-color: #CCCCFF !important`, `color: #000000 !important`, `box-shadow: none !important` for the two hover selectors, using `SELECTION` and `BLACK` from `support.platinum_palette`.
- New `TestFirefoxChrome.test_overflow_panel_row_paint_is_scoped_to_the_overflow_panel` asserts the selectors naming `widget-overflow` are exactly those four, each starts with `#widget-overflow`, each equals its `REQUIRED_RULES` entry, the square selectors carry no declaration besides `border-radius`, both hover selectors carry `:hover` and `:not([disabled])`, and no rule in the sheet overrides `--panel-menuitem-border-radius`. It also matches the sheet selectors against a representative element tree with `support.selector_matching.matches`: an overflowed `toolbarbutton.toolbarbutton-1` inside `#widget-overflow-list` and one inside `#widget-overflow-fixed-list` match the square and hover rules, the `.subviewbutton.panel-subview-footer-button` `#overflowMenu-customize-button` matches both rules, a disabled overflowed row matches neither hover selector, a `.panel-header` button carrying `.subviewbutton` matches neither rule, and a `toolbarbutton.toolbarbutton-1` under `#nav-bar` matches none of them.
- `test_header_names_provenance_and_preference` gains the strings `"No reference shows Firefox's toolbar overflow panel"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css"`, `"chrome/browser/content/browser/browser.xhtml"`, `"#widget-overflow"`, `"widget-overflow-list"`, `"widget-overflow-fixed-list"`, `"#overflowMenu-customize-button"`, `"--panel-menuitem-border-radius"`, `"--button-background-color-ghost-hover"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md` gains a row in the `## firefox` table after the app-menu row: the toolbar overflow panel's rows (`#widget-overflow .subviewbutton` outside `.panel-header` and `#widget-overflow .widget-overflow-list .toolbarbutton-1`) are square, an enabled hovered row is flat `#CCCCFF` with black text and no toolbar bevel, and disabled rows, focus rings, separators, toolbar springs, panel headers and the panel body stay Firefox's; its test column names the new test, and its provenance records the missing Firefox overflow-panel reference, the `widgets/viewitem.svg` and menu-item mapping with the pinned anchors, the installed Firefox ESR 153.5.1 files, selectors and tokens above, and that declaration checks do not establish rendered pixels.
- `make check` passes, and the existing sheet, its install and their tests keep their declarations and scope.

### Firefox Platinum chrome, part 1/2: ship a `userContent.css` painting the about:downloads list like a Platinum list (planned 2026-10-26 by the plan role; the opt-in profile install is its own later run) — done 2026-10-26 by the feature role

**Goal.** Ship a standalone `userContent.css` that gives Firefox's `about:downloads` page a Mac OS 8.6 item-view field: a non-empty downloads list is white with black text, a square 1px black outline and the sunken `#999999` top-left shadow, every row is square, and a selected row is a flat `#CCCCFF` fill with black text. The empty-list state, the page background and text, each row's `.downloadButton` action button, the `#downloadsContextMenu` context menu and every other page stay Firefox's. This part ships and tests the sheet; the opt-in profile install is part 2/2, planned separately because extending the installer's atomic install/rollback and its tests is its own run.

**Grounding.** No reference screenshot shows Firefox chrome. The list face adapts the pinned white view background (`tests/test_colorscheme_reference.py::TestReferenceAnchors.test_window_view_background`) with the desktop theme's sunken field: `widgets/lineedit.svg`'s `#FFFFFF` face, `#000000` outline and `#999999` shadow (`tests/test_desktoptheme_lineedit.py::TestLineEdit.test_lineedit_face_is_white` and `test_lineedit_colours`), the same paint the Firefox sheet's `findbar .findbar-textbox` rule already applies. The selected row adapts the reference-grounded `widgets/listitem.svg`: flat `#CCCCFF`, square corners and no hover highlight (`tests/test_desktoptheme_listitem.py::TestListItem.test_listitem_selection_is_flat_selection_colour`, `test_listitem_normal_has_no_fill` and `test_listitem_hint_geometry`); `#CCCCFF` is the pinned `[Colors:Selection]` token (`tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`).

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/downloads/contentAreaDownloadsView.xhtml` defines `<window id="contentAreaDownloadsView">` around `<richlistbox id="downloadsListBox" class="allDownloadsListBox">`, and `chrome/browser/content/browser/downloads/allDownloadsView.js` builds each row as a `richlistitem` with the `download` and `download-state` classes. `chrome/browser/skin/classic/browser/downloads/allDownloadsView.inc.css` sets `#downloadsListBox > richlistitem { min-height: 4.5em }` and paints no row hover background, leaving the `.downloadButton` its own hover. `chrome/toolkit/skin/classic/global/richlistbox.css` paints `richlistbox` with `appearance: auto`, `background-color: Field`, `color: FieldText` and `border: 1px solid ThreeDShadow`, and paints `richlistitem[selected="true"]` with `-moz-cellhighlight`/`SelectedItem`; `chrome/browser/content/browser/downloads/contentAreaDownloadsView.css` hides an empty `#downloadsListBox` with `#downloadsListBox:empty { display: none; }`. `browser/omni.ja` `defaults/preferences/firefox.js` sets `browser.tabs.remote.separatePrivilegedContentProcess` true, so about:downloads runs in a content process where `userContent.css` applies. A headless run of this ESR with a temporary profile whose `userContent.css` held `@-moz-document url("about:downloads") { #contentAreaDownloadsView { background-color: #FF0000 !important } }` rendered the page red, confirming both the URL match and the sheet's reach; declaration checks do not establish rendered list pixels.

**Approach.** Create `theme/firefox/org.macos8.desktop/chrome/userContent.css` with the marker first line `/* org.macos8.desktop Firefox content, standalone userContent.css` and a provenance header, then one at-rule containing three rules:

```css
@-moz-document url("about:downloads") {
  #contentAreaDownloadsView #downloadsListBox:not(:empty) {
    appearance: none !important;
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #999999 !important;
  }

  #contentAreaDownloadsView #downloadsListBox > richlistitem {
    border-radius: 0 !important;
  }

  #contentAreaDownloadsView #downloadsListBox > richlistitem[selected] {
    background-color: #CCCCFF !important;
    color: #000000 !important;
  }
}
```

Square the rows directly rather than overriding a Firefox radius token, because the page shares no token with the chrome panels. The `:not(:empty)` guard leaves Firefox's hidden empty-list state (`#downloadsListBox:empty { display: none; }`); the list face's `appearance: none` and colours override the toolkit listbox paint, and a non-selected row keeps the white field because no row hover is added. Add no rule for the page background, `.downloadButton`, `#downloadsHistory`, `#downloadsListEmptyDescription` or `#downloadsContextMenu`; the context menu is a popup in the content document and stays Firefox's.

The header states: no reference shows Firefox's content-area downloads page; the field adapts `widgets/lineedit.svg` and the sheet's find-field paint, the row adapts `widgets/listitem.svg`, with the pinned anchors above; the installed ESR paths, selectors and the empty-list rule above; the `browser.tabs.remote.separatePrivilegedContentProcess` content-process basis and the headless `@-moz-document` render check; that declaration checks do not establish rendered pixels; and that this sheet is not installed until part 2/2 adds it to `make install-firefox`.

**Files touched.** New `theme/firefox/org.macos8.desktop/chrome/userContent.css`, new `tests/test_firefox_content_theme.py`, `docs/invariants.md`. README.md is untouched until part 2/2 makes the sheet installable.

**Acceptance criteria.**
- `tests/test_firefox_content_theme.py` reads the sheet with `support.gtk_css.parse_css`: the first line, with a UTF-8 BOM stripped, equals the marker above; the sheet's comments-stripped text names exactly one at-keyword, `@-moz-document`, whose prelude is exactly `url("about:downloads")` and whose block encloses every rule (no selector appears before or after it).
- The parsed rules are exactly the three selectors above, each equal to its `REQUIRED_RULES` entry built from `WHITE`, `BLACK`, `GREY` and `SELECTION` in `support.platinum_palette`; the list selector carries `:not(:empty)` and `border-radius: 0`; no rule is added for a non-selected row's hover, the empty-list description, a download button or the context menu.
- The test asserts the raw sheet's hex values are exactly `{WHITE, BLACK, GREY, SELECTION}` (comments included, as the userChrome palette test does), no selector contains `*`, and the sheet neither imports nor names Adwaita.
- A header-provenance test asserts the sheet's header contains `"No reference shows Firefox's"`, `"widgets/lineedit.svg"`, `"tests/test_desktoptheme_lineedit.py::TestLineEdit"`, `"widgets/listitem.svg"`, `"tests/test_desktoptheme_listitem.py::TestListItem"`, `"test_selection_background"`, `"chrome/browser/content/browser/downloads/contentAreaDownloadsView.xhtml"`, `"contentAreaDownloadsView"`, `"contentAreaDownloadsView.css"`, `"richlistbox.css"`, `"browser.tabs.remote.separatePrivilegedContentProcess"`, `"@-moz-document"`, `"platform colour adaptation 2026-10-26"` and `"part 2/2"`.
- `docs/invariants.md` gains a row in the `## firefox` table after the all-tabs row: the content-area downloads list (`#contentAreaDownloadsView #downloadsListBox`) is a non-empty white field with black text, a square 1px black outline and the sunken `#999999` top-left shadow, its rows are square and a selected row is flat `#CCCCFF` with black text, while the empty-list state, page background, row action buttons and context menu stay Firefox's; its test column names each test in the new module; its provenance records the missing Firefox content-area reference, the `widgets/lineedit.svg`/`widgets/listitem.svg` adaptations and pinned anchors, the installed ESR selectors and the content-process basis above, and that declaration checks do not establish rendered pixels.
- `make check` passes, and the existing `userChrome.css`, its install, and their tests keep their declarations (this part changes no existing file but `docs/invariants.md`).

### Firefox Platinum chrome: paint the app-menu rows like a Platinum menu (planned 2026-10-26 by the plan role) — done 2026-10-26 by the feature role

**Goal.** Make the toolbar app menu (`#appMenu-popup`) read as a Mac OS 8.6 menu: each row, including the footer rows outside a view's body, is square, and an enabled row under the pointer takes the flat `#CCCCFF` menu-item highlight with black text and no toolbar bevel. The app menu's disabled and focus states, separators, panel headers and check glyphs stay Firefox's, as do the library, history and identity arrow panels.

**Grounding.** No reference screenshot shows Firefox chrome or its app menu. The highlight adapts the reference-grounded `widgets/viewitem.svg`, whose `hover`/`selected`/`selected+hover` slices are each a flat square `#CCCCFF` with no bevel or outline (`tests/test_desktoptheme_viewitem.py::TestViewItem.test_viewitem_highlights_are_flat_selection_colour`), and reuses the sheet's existing `menupopup > menuitem:hover` mapping of that menu-item highlight. `#CCCCFF` is the project's sampled `[Colors:Selection]` token pinned by `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`; the reference's open Apple menu shows no highlighted item, so the menu-item highlight has no per-pixel sample. Record the missing Firefox app-menu reference and the dated adaptation in the sheet header and the invariants row.

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<panel id="appMenu-popup" type="arrow">` around `<panelmultiview id="appMenu-multiView">`, whose views' `.panel-subview-body` hold `toolbarbutton.subviewbutton` rows (e.g. `#appMenu-new-tab-button2`, `#appMenu-passwords-button`, `#appMenu-settings-button`). `#PanelUI-history` and `#PanelUI-bookmarks` place one more enabled row, `#PanelUI-historyMore` and `#panelMenu_showAllBookmarks` (both `toolbarbutton.subviewbutton.panel-subview-footer-button`), directly in the panelview outside that body. Each view's header is a `.panel-header` whose back button (`PanelMultiView.sys.mjs` creates `toolbarbutton.subviewbutton.subviewbutton-iconic.subviewbutton-back`) and edit button (`#profiles-edit-this-profile-button` in the profiles view) also carry `.subviewbutton`, so a rule scoped only to `#appMenu-popup .subviewbutton` would square and repaint the headers. `browser/omni.ja` `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` `border-radius: var(--panel-menuitem-border-radius)` and gives `toolbarbutton.subviewbutton:not([disabled]):hover` the ghost tokens `--button-text-color-ghost-hover` and `--button-background-color-ghost-hover`, with a pressed `box-shadow`; toolkit `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines `--panel-menuitem-border-radius: var(--border-radius-small)` (4px) and maps the ghost hover to the violet `--button-background-color-hover`. The sheet's generic `toolbarbutton:hover:not([disabled="true"])` rule also adds its raised bevel, and the `#appMenu-popup` panel is already a `panel[type="arrow"]`, so the `#DDDDDD` face and black text tokens apply but the rows' radius and hover are still Firefox's.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, immediately after the `toolbarbutton:hover:active:not([disabled="true"])` rule and before the `/* The all-tabs panel rows ... */` comment, add two rules with a short comment:

```css
#appMenu-popup .subviewbutton:not(.panel-header .subviewbutton) {
  border-radius: 0 !important;
}

#appMenu-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Scope both rules to `#appMenu-popup` but exclude `.panel-header .subviewbutton`, so body rows and the footer rows directly in a panelview are painted while the `.panel-header` back and edit buttons keep Firefox's paint even though they also carry `.subviewbutton`. Square the rows directly rather than overriding `--panel-menuitem-border-radius`, because `panelUI-shared.css` applies that token to every `.subviewbutton` in every panel, including the all-tabs panel's mute and close controls and the library/history panels, which stay Firefox's. The hover rule excludes disabled rows, so a disabled row keeps Firefox's dimmed paint; because it matches while `:active` too and out-specifies Firefox's pressed ghost rule, a pressed row stays `#CCCCFF` with no pressed shadow. Add no margin, padding, border, font, separator or panel-header declaration, and do not touch `:focus-visible`.

In the header, append a provenance paragraph after the all-tabs paragraph (the one beginning `No reference shows Firefox's all-tabs panel;`) and before the closing `*/`: no reference shows Firefox's app menu; the row highlight adapts `widgets/viewitem.svg` and the sheet's menu-item mapping (platform colour adaptation 2026-10-26); Firefox's `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` its `--panel-menuitem-border-radius` and its `--button-background-color-ghost-hover` violet hover, `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines those tokens, `chrome/browser/content/browser/browser.xhtml` defines `#appMenu-popup` with each view's rows inside a `.panel-subview-body` and the `#PanelUI-historyMore` and `#panelMenu_showAllBookmarks` footer rows outside it, and the sheet squares and suppresses the ghost hover and toolbar bevel on every app-menu `.subviewbutton` row except the `.panel-header` back and edit buttons; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, new `tests/support/selector_matching.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the two selectors `#appMenu-popup .subviewbutton:not(.panel-header .subviewbutton)` (`border-radius: 0 !important`) and `#appMenu-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled])` (`background-color: #CCCCFF !important`, `color: #000000 !important`, `box-shadow: none !important`), after the all-tabs entries, using `SELECTION` and `BLACK` from `support.platinum_palette`.
- New `TestFirefoxChrome.test_app_menu_row_paint_is_scoped_to_the_app_menu` asserts the selectors naming `appMenu` are exactly the radius and hover rules, each starts with `#appMenu-popup .subviewbutton:not(.panel-header .subviewbutton)`, each equals its `REQUIRED_RULES` entry, the radius selector excludes `.panel-header` descendants, the hover selector carries `:not([disabled])` and `:hover`, the radius rule carries no declaration besides `border-radius`, and no rule in the sheet overrides `--panel-menuitem-border-radius`. It also matches the sheet selectors against a representative app-menu element tree: both rules match a `.subviewbutton` row inside a view's `.panel-subview-body` and both the `#PanelUI-historyMore` and `#panelMenu_showAllBookmarks` `.panel-subview-footer-button` rows directly in a panelview, the hover rule matches only an enabled hovered row, and neither rule matches the `.panel-header` back or edit buttons even though they also carry `.subviewbutton`.
- New `tests/support/selector_matching.py` provides the test-only matcher the scope assertion uses: descendant combinators over compounds with an element name, `#id`, `.class`, `[attribute]`, `:hover` and `:not(...)` (whose argument may be a descendant selector). It replaces no existing helper.
- `test_header_names_provenance_and_preference` gains the new paragraph's strings: `"No reference shows Firefox's app menu"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css"`, `"#appMenu-popup"`, `"panel-subview-body"`, `"panel-subview-footer-button"`, `"panel-header"`, `"toolbarbutton.subviewbutton"`, `"--panel-menuitem-border-radius"`, `"--button-background-color-ghost-hover"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md` gains a row in the `## firefox` table after the all-tabs row: the app-menu rows (`#appMenu-popup .subviewbutton` outside `.panel-header`) are square and a hovered enabled row is flat `#CCCCFF` with black text and no bevel, while disabled rows, focus rings, separators, panel headers and check glyphs stay Firefox's; it records that the footer `.panel-subview-footer-button` rows sit outside the `.panel-subview-body` and that the `.panel-header` back and edit buttons also carry `.subviewbutton` and are excluded; its test column names the new test; its provenance records the missing Firefox app-menu reference, the `widgets/viewitem.svg` adaptation, the installed Firefox ESR 153.5.1 selectors and tokens above, and that declaration checks do not establish rendered pixels.
- `make check` passes; the generic `toolbarbutton` rules, the menu, tab, downloads-panel, all-tabs, sidebar, address-bar, find-bar and tooltip rules keep their declarations, and no rule is added for a non-`#appMenu-popup` panel.

### Split the render scratch session out of the render CLI (planned 2026-10-26 by the organize role) — done 2026-10-26 by the feature role

**Goal.** Give `tools/render_surface.py` one job -- parse the CLI, run the capture and publish the PNG -- and move the throwaway session it prepares (scratch root, sanitized environment, theme install, session config and in-session command) into a new `tools/render_session.py`. `make render`, its options, exit statuses, diagnostics, scratch cleanup and rendered bytes stay unchanged.

**Cost today.** `tools/render_surface.py` is the second-largest production Python module at 329 lines, and its 127-line `_render` mixes two layers: it creates the scratch XDG root and its environment, runs `make install`, writes `kwinrc`/`plasmarc`, builds the `dbus-run-session`/`kwin_wayland` command, then reads and publishes the PNG. A reader changing the capture has to read through the session setup, and `tests/test_render_surface.py` patches `render_surface.run_logged` and `render_surface.write_configs` to exercise session preparation that has no module of its own. The CLI's unit tests reach into session internals (`_session_script`, `COLOR_SCHEME`) from `render_surface`.

**Target structure.** New `tools/render_session.py` owns the throwaway session:
- move `COLOR_SCHEME`, `SOCKET`, `INSTALL_TIMEOUT` and `CONFIG_FILES` out of `render_surface`;
- move `_session_script` as `session_script()`, returning the same shell text;
- a `Session` value or context manager that creates the `rt/`, `cfg/` and `data/` directories, makes `rt/` mode `0700`, names `surface.png`, and builds the environment that drops `WAYLAND_DISPLAY`, `DISPLAY`, `DESTDIR`, `MAKEFLAGS` and `XDG_CONFIG_DIRS` and sets `XDG_RUNTIME_DIR`, `XDG_CONFIG_HOME` and `XDG_DATA_HOME`; its cleanup replaces the `_render` `finally` that removes the scratch root;
- `install_theme(session)` running `make install XDG_DATA_HOME=...` through `run_logged` and returning the status and install-log path, and `write_session_configs(session)` calling `theme_defaults.write_configs(session.config, CONFIG_FILES)`;
- `session_command(session, applet, settle, width, height, timeout)` returning the `dbus-run-session -- kwin_wayland ... sh -c <script> ...` argv and render-log path.

`tools/render_surface.py` keeps `TOOL`, `REQUIRED_TOOLS`, the argument types, `main` and `_render`; `_render` becomes create session, install, configure, launch, read the capture, check its size and publish, with every diagnostic still reported under `TOOL`. Keep the CLI at `tools/render_surface.py`: README.md, the Makefile and `docs/invariants.md` name that path as the entry point.

**Files touched.** `tools/render_surface.py`, new `tools/render_session.py`, `tests/test_render_surface.py`, `tests/test_render_surface_units.py`, `tests/test_repo_root.py` (the new module imports the shared `ROOT`, so the shared-root test names it too). `docs/invariants.md` keeps its rows and test names unless the render-session tests move to a new module, in which case update the affected rows in the same change.

**Acceptance criteria.**
- `tools/render_session.py` imports no `render_surface`; `render_surface._render` no longer creates scratch directories, builds the session environment, calls `make install`/`write_configs`, or builds the `dbus-run-session` argv; grep finds no `_session_script`, `COLOR_SCHEME`, `SOCKET`, `INSTALL_TIMEOUT` or `CONFIG_FILES` left in `render_surface`.
- The session script text, scratch layout and modes, environment, install/config order, session argv, exit codes, diagnostic text and cleanup on success and failure are the same before and after; no external dependency or CLI option changes.
- The session-script and environment tests import the moved names from `render_session`, and the install/config/session failure tests patch `render_session.run_logged` or `render_session.write_configs`; CLI, argument and output-publication tests stay on `render_surface`.
- `make check` passes, and a grep over the sources, tests and markdown docs finds no stale reference to a moved name or path outside the archives.

### Firefox Platinum chrome: paint the downloads panel rows like a Platinum list (planned 2026-10-26 by the plan role; independent of the waiting all-tabs panel rows paint) — done 2026-10-26 by the feature role

**Goal.** Give the downloads panel's rows Mac OS 8.6 list behaviour: a hovered non-selected row keeps the `#DDDDDD` panel face with black text and no violet hover wash, the selected row takes the flat `#CCCCFF` selection fill with black text, and every row in the panel is square. Scope the change to `#downloadsPanel #downloadsListBox > richlistitem`: Firefox's content-area downloads view (`chrome/browser/content/browser/downloads/contentAreaDownloadsView.xhtml`) names its own `#downloadsListBox`, and its rows stay Firefox's, as do the row's `.downloadButton` action button, the `#downloadsHistory` footer button and the `.downloadMainArea`'s own paint.

**Grounding.** No reference screenshot shows Firefox chrome or its downloads panel. The row behaviour adapts the reference-grounded `widgets/listitem.svg`, whose comment records that Mac OS 8.6 has no hover highlight and whose `pressed` (selected) row is a flat `#CCCCFF` rectangle with square corners, no bevel and no outline; `tests/test_desktoptheme_listitem.py::TestListItem` pins that art and `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background` pins the `#CCCCFF` sample. The GTK sheets make the same adaptation (transparent hover, flat `#CCCCFF` black-text selection, square corners) for tree, list and column rows (`docs/invariants.md`, `## gtk`), and this sheet already paints menu items, bookmark items and address-bar result rows `#CCCCFF`. Record the missing Firefox downloads reference and the dated adaptation (2026-10-26).

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<panel id="downloadsPanel" type="arrow">`, whose `<panelview id="downloadsPanel-mainView">` holds `<richlistbox id="downloadsListBox">` with the footer's `#downloadsHistory` button below it; `moz-src/browser/components/downloads/DownloadsViewUI.sys.mjs`'s `connect()` builds each row as a `richlistitem` containing an `hbox.downloadMainArea` (with `.downloadTypeIcon`, `.downloadContainer`, `.downloadTarget` and the detail descriptions) plus a `button.downloadButton`, and `chrome/browser/content/browser/downloads/downloads.js` selects rows through `richListBox.selectedIndex`. `browser/omni.ja` `chrome/browser/skin/classic/browser/downloads/downloads.inc.css` gives `#downloadsListBox > richlistitem` `border-radius: var(--border-radius-small)` and paints its hover states (`.hoveringMainArea:hover`, `.openWhenFinished:hover`, `[verdict]:hover`) with `--button-background-color-ghost-hover` and `--button-text-color-ghost-hover`; toolkit `chrome/toolkit/skin/classic/global/richlistbox.css` paints `richlistitem[selected="true"]` with `-moz-cellhighlight` (and `SelectedItem` when the list is focused); `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` maps `--button-background-color-ghost-hover` to `--button-background-color-hover`, `light-dark(var(--color-violet-desaturated-20), var(--color-violet-desaturated-50))`, and `--border-radius-small` to 4px. The sheet's `panel[type="arrow"]` rule already sets the panel face `#DDDDDD`, and nothing in the sheet targets these rows, so today a hovered row shows the violet wash instead of the panel face.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: immediately after the `#statuspanel-label` rule and before the `panel[type="arrow"]` rule, add three rules with a short comment: `#downloadsPanel #downloadsListBox > richlistitem { border-radius: 0 !important; }`; `#downloadsPanel #downloadsListBox > richlistitem:not([selected]):hover { background-color: #DDDDDD !important; color: #000000 !important; }`; and `#downloadsPanel #downloadsListBox > richlistitem[selected] { background-color: #CCCCFF !important; color: #000000 !important; }`. The selected rule comes after the hover rule and the hover selector excludes `[selected]`, so a hovered selected row keeps `#CCCCFF`. `#DDDDDD` is the panel face `panel[type="arrow"]` already sets, so a hovered row paints the same face rather than a wash, and the `#downloadsPanel` ancestor keeps the change off the content-area `#downloadsListBox`. Add no declaration for `.downloadButton`, `#downloadsHistory`, `.downloadMainArea`, margin, padding, border, font or box-shadow: those controls keep Firefox's paint and geometry. In the header, insert a provenance paragraph between the sidebar paragraph (ending "the sidebar's inner document is not userChrome territory.") and the install-instructions paragraph (starting "Install it opt-in"): no reference shows Firefox's downloads panel; the row face, black text and flat selection adapt `widgets/listitem.svg`, pinned by `tests/test_desktoptheme_listitem.py::TestListItem`, and the GTK row mapping (platform colour adaptation 2026-10-26); Firefox's `chrome/browser/skin/classic/browser/downloads/downloads.inc.css` gives the rows their radius through `--border-radius-small` and paints `--button-background-color-ghost-hover` on hover, `chrome/toolkit/skin/classic/global/richlistbox.css` paints `richlistitem[selected="true"]`, `chrome/browser/content/browser/browser.xhtml` defines the panel and `moz-src/browser/components/downloads/DownloadsViewUI.sys.mjs` builds each row, and Firefox's own violet ghost hover and the toolkit's system-colour selection are suppressed on these panel rows only; declaration checks do not establish rendered pixels.
- `tests/test_firefox_theme.py`: add the three selectors to `REQUIRED_RULES` after the `#sidebar-header` entry and before the `.tab-background` entry, with the declarations above (`FACE`, `BLACK` and `SELECTION` from `support.platinum_palette`). Add `TestFirefoxChrome.test_downloads_panel_row_paint_is_scoped_to_the_panel_list`: it asserts the selectors naming `downloadsListBox` are exactly those three, each starts with `#downloadsPanel #downloadsListBox > richlistitem`, each equals its `REQUIRED_RULES` entry, the hover selector carries `:not([selected])` and `:hover`, and the selected rule follows the hover rule in `self.selectors` order. Extend `test_header_names_provenance_and_preference` between the `"modules/ThemeVariableMap.sys.mjs"` entry and the `"the sidebar's inner document is not userChrome territory"` entry with the new provenance strings: `"No reference shows Firefox's downloads panel"`, `"widgets/listitem.svg"`, `"tests/test_desktoptheme_listitem.py::TestListItem"`, `"chrome/browser/skin/classic/browser/downloads/downloads.inc.css"`, `"chrome/toolkit/skin/classic/global/richlistbox.css"`, `"chrome/browser/content/browser/browser.xhtml"`, `"moz-src/browser/components/downloads/DownloadsViewUI.sys.mjs"`, `"--button-background-color-ghost-hover"`, `"richlistitem[selected=\"true\"]"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md`: add a row to the `## firefox` table between the menu-bar title-box row and the sidebar-frame row whose guarantee is: the downloads panel's rows (`#downloadsPanel #downloadsListBox > richlistitem`) are square; a hovered non-selected row keeps the `#DDDDDD` panel face with black text instead of Firefox's violet ghost wash; the selected row is flat `#CCCCFF` with black text; the row's action button, footer button and the content-area downloads list stay Firefox's. Its test column names the new test, and its provenance records the missing Firefox-downloads reference, the `widgets/listitem.svg` and GTK row adaptation, the installed Firefox ESR 153.5.1 files, selectors and tokens above, and that declaration checks do not establish rendered pixels.

**Acceptance criteria.**
- Required-rule validation fails when the radius, hover or selected rule is missing, carries a different colour, or loses its `!important`; the scope test fails when a `downloadsListBox` rule sits outside `#downloadsPanel #downloadsListBox > richlistitem`, when the hover selector loses `:not([selected])` or `:hover`, or when the selected rule precedes the hover rule.
- The `#statuspanel-label`, `panel[type="arrow"]`, tab, toolbar, menu-bar, menu, bookmark, urlbar, find bar, search field, sidebar, tooltip and other existing rules keep their current declarations, so their surfaces keep their current paints; the downloads row's action and footer buttons and the content-area downloads list keep Firefox's paint; no `.downloadButton` or `#downloadsHistory` rule is added.
- A hovered non-selected panel row paints the `#DDDDDD` panel face with black text; the selected panel row paints flat `#CCCCFF` with black text; every panel row is square. The content-area downloads list is unchanged.
- `make check` passes without Firefox or a new dependency, the palette hex set is unchanged, and implementation stays within these three files. Report declaration validation separately from live browser rendering.

### Firefox Platinum chrome: paint the all-tabs panel rows like a Platinum list (planned 2026-10-26 by the plan role; independent of the waiting menu-bar title spacing) — done 2026-10-26 by the feature role

**Goal.** Give the all-tabs panel's rows Mac OS 8.6 list behaviour: a hovered row keeps the `#DDDDDD` panel face with no hover wash and no raised bevel, the current tab's row takes the flat `#CCCCFF` selection fill with black text, and every row in the view has square corners. Scope the change to `#allTabsMenu-allTabsView`, so toolbar buttons, menus, urlbar results, bookmark items and other panels keep their current paints.

**Grounding.** No reference screenshot shows Firefox chrome or its all-tabs panel. The row behaviour adapts the reference-grounded `widgets/listitem.svg`, whose own comment records that Mac OS 8.6 has no hover highlight and whose `pressed` (selected) row is a flat `#CCCCFF` rectangle with square corners, no bevel and no outline; `tests/test_desktoptheme_listitem.py::TestListItem` pins that art and `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background` pins the `#CCCCFF` sample. The GTK sheets make the same adaptation (transparent hover, flat `#CCCCFF` black-text selection) for tree, list and column rows (`docs/invariants.md`, `## gtk`), and this sheet already paints menu items and bookmark items `#CCCCFF`. Record the missing Firefox all-tabs reference and the dated adaptation (2026-10-26).

In the installed Firefox ESR (`/usr/lib/firefox-esr/browser/omni.ja` and `/usr/lib/firefox-esr/omni.ja`), `chrome/browser/content/browser/browser.xhtml` defines `<panelview id="allTabsMenu-allTabsView">` containing `<vbox id="allTabsMenu-allTabsView-tabs">`; `moz-src/browser/components/tabbrowser/TabsList.sys.mjs`'s `_createRow` builds each row as a `toolbaritem.all-tabs-item` around a `toolbarbutton.all-tabs-button.subviewbutton.subviewbutton-iconic`, and `_setRowAttributes` sets `selected` on the current tab's row. `chrome/browser/skin/classic/browser/tabbrowser/tabs.css` gives `.all-tabs-item > toolbarbutton` a transparent ghost background whose `:hover` becomes `--button-background-color-ghost-hover`, and gives `.all-tabs-item` `border-radius: var(--panel-menuitem-border-radius)`; `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines `--panel-menuitem-border-radius: var(--border-radius-small)` (4px) and maps the ghost token to `--button-background-color-hover`, a violet theme token, while `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` applies the radius to every `.subviewbutton`. Nothing in the sheet targets these rows, so today a hovered row shows the violet wash with the sheet's generic `toolbarbutton:hover` bevel on top.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: immediately after the `toolbarbutton:hover:active` rule and before the `menupopup > menuitem:hover` rule, add three rules with a short comment: `#allTabsMenu-allTabsView .all-tabs-item, #allTabsMenu-allTabsView .all-tabs-item > .all-tabs-button { border-radius: 0 !important; }`; `#allTabsMenu-allTabsView .all-tabs-item:not([selected]) > .all-tabs-button:hover { background-color: #DDDDDD !important; color: #000000 !important; box-shadow: none !important; }`; and `#allTabsMenu-allTabsView .all-tabs-item[selected] > .all-tabs-button { background-color: #CCCCFF !important; color: #000000 !important; box-shadow: none !important; }`. The square-corner rule squares the row and its main button directly rather than overriding the view's `--panel-menuitem-border-radius`, because `panelUI-shared.css` applies that token to every `.subviewbutton`, including the row's mute and close `.all-tabs-secondary-button` controls, which stay Firefox's. The selected rule comes after the hover rule and the hover selector excludes `[selected]`, so hovering the current tab keeps `#CCCCFF`. Target only `.all-tabs-button`, leaving the row's `.all-tabs-secondary-button` mute and close buttons (and their hover) to Firefox. `#DDDDDD` is the panel face `panel[type="arrow"]` already sets, so a hovered row paints the same face rather than a wash. Add no margin, padding, border or font declaration. In the header, add a provenance paragraph at the end of the header block, after the multi-selected-tab paragraph and before the closing `*/` (the waiting menu-bar plan inserts its paragraph earlier, so the two stay apart): no reference shows Firefox's all-tabs panel; the row face, black text and flat selection adapt `widgets/listitem.svg` and the GTK row mapping; the row's stock 4px radius is Firefox's `--panel-menuitem-border-radius`, defined in `tokens-shared.css` as `--border-radius-small`; Firefox's own violet ghost hover and this sheet's generic toolbarbutton bevel are suppressed on these rows only; declaration checks do not establish rendered pixels.
- `tests/test_firefox_theme.py`: add the four selectors to `REQUIRED_RULES` (the row and main-button square-corner rules, the hover rule and the selected rule) with the declarations above (`FACE`, `BLACK` and `SELECTION` from `support.platinum_palette`). Add `TestFirefoxChrome.test_all_tabs_row_paint_is_scoped_to_the_all_tabs_view`: it asserts the selectors naming `all-tabs` are exactly those four, each equals its `REQUIRED_RULES` entry, no selector sets `--panel-menuitem-border-radius`, the hover selector carries `:not([selected])` and `:hover`, and the selected rule follows the hover rule in `self.selectors` order. Extend `test_header_names_provenance_and_preference` with the new provenance strings: `"No reference shows Firefox's all-tabs panel"`, `"widgets/listitem.svg"`, `"tests/test_desktoptheme_listitem.py::TestListItem"`, `"allTabsMenu-allTabsView"`, `"all-tabs-item"`, `"chrome/browser/skin/classic/browser/tabbrowser/tabs.css"`, `"chrome/toolkit/skin/classic/global/design-system/tokens-shared.css"`, `"chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css"`, `"moz-src/browser/components/tabbrowser/TabsList.sys.mjs"`, `"--button-background-color-ghost-hover"`, `"--panel-menuitem-border-radius"`, `"--border-radius-small"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md`: add a row to the `## firefox` table after the sidebar-frame row whose guarantee is: the all-tabs panel rows (`#allTabsMenu-allTabsView .all-tabs-item`) have square corners set directly on the row and its main button; a hovered non-selected row keeps the `#DDDDDD` face with black text and no bevel; and the current tab's `[selected]` row is flat `#CCCCFF` with black text and no bevel, while the row's mute and close buttons stay Firefox's. Its test column names the new test, and its provenance records the missing Firefox reference, the `widgets/listitem.svg` and GTK row adaptation, the installed Firefox ESR files and the `tokens-shared.css`/`panelUI-shared.css` radius attribution above, and the 2026-10-26 date.

**Acceptance criteria.**
- Required-rule validation fails when either square-corner rule, the hover rule or the selected rule is missing, carries a different colour, or loses its `!important`; the scope test fails when an `all-tabs` rule sits outside `#allTabsMenu-allTabsView`, when a selector overrides `--panel-menuitem-border-radius`, when the hover selector loses `:not([selected])`, or when the selected rule precedes the hover rule.
- The generic `toolbarbutton:hover:not([disabled="true"])` and `toolbarbutton:hover:active:not([disabled="true"])` entries keep their current declarations, so toolbar buttons, menus, menu items, bookmark items, urlbar results, tabs, sidebar, find bar, search field, tooltips and status panel keep their current paints; the mute and close buttons in all-tabs rows keep Firefox's paint.
- A hovered non-selected row paints the `#DDDDDD` panel face with black text and no bevel; the current tab's row paints flat `#CCCCFF` with black text and no bevel; every row in the view is square, including tab-group rows, which share `.all-tabs-item`.
- `make check` passes without Firefox or a new dependency, the palette hex set is unchanged, and implementation stays within these three files. Report declaration validation separately from live browser rendering.

### Firefox Platinum chrome: space the menu-bar titles with the Platinum menu-bar margins (planned 2026-10-26 by the plan role; independent of the landed sidebar frame) — done 2026-10-26 by the feature role

**Goal.** Give Firefox's menu-bar titles the same 3px/7px title box the desktop theme and the GTK sheets use, so an idle or open title sits with the reference menu bar's spacing instead of Firefox's font-relative, bottom-heavy stock padding. Change the title box's padding only; the open title's `#CCCCFF` fill and the menubar's face and etched rule stay as they are.

**Grounding.** No reference screenshot shows Firefox chrome or a Firefox menu bar. The geometry is `widgets/menubaritem.svg`'s `normal-hint-top-margin`/`normal-hint-bottom-margin` height (3px) and `normal-hint-left-margin`/`normal-hint-right-margin` width (7px), pinned by `tests/test_desktoptheme_menubaritem.py::TestMenuBarItem::test_menubaritem_hint_geometry`, and the 7px is re-derived from the reference title gaps by `TestMenuTitleSpacingMatchesReference::test_horizontal_margin_is_half_the_mean_gap`. Both GTK sheets already apply it as `padding: 3px 7px` (`menubar > item` in `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `menubar > menuitem` in `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`). Firefox's installed `chrome/toolkit/skin/classic/global/menu.css` gives `menubar > menu` on Linux `padding: 0.25em 0.5em; padding-bottom: 1px; border-bottom: 3px solid transparent`, so its title box is font-relative and bottom-heavy; nothing in the sheet overrides it; a zero bottom pad leaves that stock 3px transparent border in place to complete the bottom margin, and the open title recolours it. Record the missing Firefox menu-bar reference and the dated geometry adaptation (2026-10-26).

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: immediately after the `#toolbar-menubar` face rule and before the open-title rule, add `#toolbar-menubar menubar > menu { padding: 3px 7px 0 !important; }`; the zero bottom pad leaves Firefox's stock 3px transparent bottom border to complete the 3px bottom margin. Add nothing else: no fill, text colour, border, margin or hover declaration. In the header, insert a provenance paragraph after the open-menu-bar paragraph (ending "`chrome/toolkit/skin/classic/global/menu.css` on Linux.") and before the find-field paragraph (starting "No reference shows Firefox's find field"): no reference shows a Firefox menu bar; the title box takes `widgets/menubaritem.svg`'s 3px/7px margins, re-derived from the reference title gaps; Firefox's stock Linux rule is font-relative and bottom-heavy; only the padding is overridden, with a zero bottom pad so the retained stock border completes the bottom margin and stays the open title's landed `#CCCCFF` underline.
- `tests/test_firefox_theme.py`: add `"#toolbar-menubar menubar > menu": {"padding": "3px 7px 0 !important"}` to `REQUIRED_RULES` directly before the `[open]` entry. Add `TestFirefoxChrome.test_menubar_title_geometry_matches_the_menubaritem_margins`, which derives the top/bottom and left/right hint sizes with `MENUBARITEM_SVG` from `support.desktoptheme_paths`, `parse_svg` from `support.svg_case` and `rect_geometry` from `svg_assertions` (as `tests/test_desktoptheme_menubaritem.py` does) and checks the 3px top and 7px side padding against the SVG, subtracts Firefox's retained 3px stock bottom border from the SVG's 3px bottom margin to expect the zero bottom pad, and adds that border back to check the rendered bottom margin, so the SVG is the source and a sheet/SVG drift fails. Extend `test_menubar_open_title_paint_is_scoped_to_the_open_title`: its title-rule set becomes exactly `#toolbar-menubar`, the new base title rule and the `[open]` rule; the base rule's declaration names are exactly `{"padding"}`; the open rule keeps its two declarations. Add provenance entries after `"not-found and flash states stay"` and before `"No reference shows Firefox multi-selected tabs"`: `"No reference shows Firefox's menu bar titles"`, `"TestMenuBarItem.test_menubaritem_hint_geometry"`, `"TestMenuTitleSpacingMatchesReference"`, `"padding: 0.25em 0.5em"`, `"chrome/toolkit/skin/classic/global/menu.css"` and `"platform geometry adaptation 2026-10-26"`.
- `docs/invariants.md`: extend the existing open-menu-bar-title row under `## firefox` so its guarantee also covers the title box's top/side padding and retained stock bottom border, its test list adds the new geometry test, and its provenance names the `menubaritem.svg` hint geometry and reference title gaps, the stock Firefox Linux padding and the missing Firefox menu-bar reference; keep its statement that declaration checks do not establish rendered pixels.

**Acceptance criteria.**
- `REQUIRED_RULES` validation fails when the base title rule is missing, its padding is not `3px 7px 0 !important`, or it gains another declaration.
- The geometry test fails when the sheet's top or side padding differs from the menubaritem SVG's normal-hint margins, or when its bottom pad plus the retained 3px stock bottom border differs from the 3px bottom margin.
- The scope test fails when any selector other than `#toolbar-menubar`, the base title rule and the open-title rule targets a menu-bar title.
- An idle, hovered or open title keeps its inherited black text; the open title keeps its `#CCCCFF` fill and `#CCCCFF` bottom border; the `#toolbar-menubar` face and etched bottom rule, the toolbar buttons, tabs, sidebar, menus, find bar, search field, tooltips, results rows and status panel keep their current paints.
- `make check` passes without Firefox or a new dependency, the palette hex set is unchanged, and implementation stays within these three files. Report declaration validation separately from live browser rendering.

### Firefox Platinum chrome: frame the sidebar with the Platinum face (planned 2026-10-26 by the plan role; independent of the waiting multi-selected tab face) — done 2026-10-26 by the feature role

**Goal.** Give Firefox's sidebar the Platinum frame the toolbars already wear: the sidebar box takes the shared `#DDDDDD` face and black text, and the header band above the sidebar content gets the theme's etched `#888888`/`#FFFFFF` bottom rule, so an open sidebar reads as a Platinum panel rather than a band with no face of its own. The sidebar's inner document (bookmarks, history and other panel rows) stays Firefox's: `userChrome.css` does not style that document, and this plan claims no paint there.

**Grounding.** No reference screenshot shows Firefox chrome or a sidebar. Firefox's `chrome/browser/skin/classic/browser/sidebar.css` paints `#sidebar-container, #sidebar-box` with `--sidebar-background-color` and `--sidebar-text-color` and gives `#sidebar-header` a 1px `--sidebar-border-color` bottom border; those are lightweight-theme sidebar keys mapped from `sidebar`, `sidebar_text` and `sidebar_border` in `modules/ThemeVariableMap.sys.mjs`, and this userChrome-only sheet sets none of them, so it gives the header band no Platinum face or rule. `chrome/browser/content/browser/browser.xhtml` puts `#sidebar-header` inside `#sidebar-box`, with the `<browser id="sidebar">` panel document below it; the installed ESR's `defaults/preferences/firefox.js` leaves `sidebar.revamp` off, so that is the sidebar markup in use, and the revamped launcher is a different document outside this plan. The face `#DDDDDD` is the reference-grounded menu-bar face (`tests/test_colorscheme_reference.py::TestReferenceAnchors.test_menu_bar_face`) and the etched pair is the desktop theme's separator rule (`tests/test_desktoptheme_line.py::TestLineReference`), already used by this sheet's `#nav-bar`, `#PersonalToolbar` and `#toolbar-menubar`; no new colour literal is added. Record the missing reference surface and the dated platform adaptation (2026-10-26) in the sheet header.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: immediately after the `#nav-bar, #PersonalToolbar, #toolbar-menubar` rule and before the open menu-bar title comment, add
  `#sidebar-box { background-color: #DDDDDD !important; color: #000000 !important; }`
  and
  `#sidebar-header { border-bottom: 1px solid #888888 !important; box-shadow: inset 0 -1px #FFFFFF !important; }`.
  Replace no existing rule and add no hover, geometry, font or inner-document rule: `#sidebar-switcher-target` already takes `#EEEEEE` hover and `#CCCCFF` pressed/active fills from the sheet's `:root` toolbar-button tokens. In the header, insert a provenance paragraph between the tab-hover note (ending "`tests/test_desktoptheme_scrollbar.py::TestScrollbarReference.`") and the install-instructions paragraph (starting "Install it opt-in"): no reference shows a Firefox sidebar; its face reuses the reference-grounded `#DDDDDD` menu-bar face and its header rule the pinned etched pair rather than a screenshot sample; Firefox's `chrome/browser/skin/classic/browser/sidebar.css` consumes `--sidebar-background-color`, `--sidebar-text-color` and `--sidebar-border-color`, lightweight-theme sidebar keys mapped in `modules/ThemeVariableMap.sys.mjs`; the sidebar's inner document is not userChrome territory.
- `tests/test_firefox_theme.py`: add `#sidebar-box` and `#sidebar-header` entries to `REQUIRED_RULES` after the `#toolbar-menubar menubar > menu[open]` entry, with the declarations above. Add `TestFirefoxChrome.test_sidebar_frame_is_scoped_to_the_box_and_header`: the selectors naming `sidebar` are exactly `#sidebar-box` and `#sidebar-header`; each declaration set equals its `REQUIRED_RULES` entry; the box's face is `FACE`, its text `BLACK`, the header's border `1px solid ETCH_DARK` and its inset highlight `WHITE`. Append `"No reference shows a Firefox sidebar"`, `"chrome/browser/skin/classic/browser/sidebar.css"`, `"--sidebar-background-color"`, `"modules/ThemeVariableMap.sys.mjs"` and `"the sidebar's inner document is not userChrome territory"` at the end of the provenance tuple in `test_header_names_provenance_and_preference`, after the menu-bar entries.
- `docs/invariants.md`: add a new row at the end of `## firefox` (after the open-menu-bar-title row) whose guarantee is "The legacy Firefox sidebar frame (`#sidebar-box` above `#sidebar-header`) is the `#DDDDDD` Platinum face with black text and an etched `#888888`/`#FFFFFF` bottom rule on the header band, while the sidebar's inner document stays Firefox's", whose test is the new scope test, and whose provenance exception names the missing Firefox-sidebar reference, the reference-grounded menu-bar face and separator pair, Firefox's `sidebar.css` consumers and `ThemeVariableMap.sys.mjs` keys, the inner-document boundary, and that declaration checks do not establish rendered pixels.

**Acceptance criteria.**
- `REQUIRED_RULES` validation fails when either sidebar rule is missing, the box face or text is not `#DDDDDD`/`#000000`, the header rule is not `#888888` with a `#FFFFFF` inset highlight, or any of them loses `!important`.
- The scope test fails when any selector other than `#sidebar-box` and `#sidebar-header` names a sidebar element, when either declaration set differs from `REQUIRED_RULES`, or when the header gains a declaration beyond the etched pair.
- The sidebar header's switcher keeps `#EEEEEE` hover and `#CCCCFF` pressed/active fills from the existing `:root` tokens; the tab strip, menu-bar titles, find bar, tooltip, search field, menus, arrow panels, results rows and status panel keep their current paints.
- `make check` passes without Firefox or a new dependency, the palette hex set is unchanged, and implementation stays within these three files. Report declaration validation separately from live browser rendering.

### Firefox Platinum chrome: give a tab in a multi-selection the selected tab face (planned 2026-10-26 by the plan role; independent of the waiting open menu-bar title paint) — done 2026-10-26 by the feature role

**Goal.** Repaint a ctrl-clicked tab in a multi-selection with the selected tab's `#EEEEEE` face and open `#EEEEEE` bottom edge, so every tab in the selection reads as selected. The sheet's base `.tab-background` rule paints every tab face `#DDDDDD` with `!important`, and the sheet repaints only the active `.tabbrowser-tab[selected] .tab-background`; Firefox marks the other tabs of a multi-selection with the `multiselected` attribute (a ctrl-click on a non-active tab calls `addToMultiSelectedTabs`, which sets `multiselected` without `selected`, and `tab.js` mirrors it onto `.tab-background`), so those tabs keep the plain face even though Firefox's own `.tab-background:is([selected], [multiselected])` rule paints them.

**Grounding.** No reference screenshot shows Firefox chrome, or tabs and multi-selection at all. The face is the sheet's existing selected-tab `#EEEEEE` trough (`TROUGH`), already pinned by `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_view_background_alternate` and `tests/test_desktoptheme_scrollbar.py::TestScrollbarReference`; this plan adds no colour literal. Firefox's `chrome/browser/skin/classic/browser/tabbrowser/tabs.css` paints `.tab-background:is([selected], [multiselected])` with `--tab-background-color-selected`, and its `chrome/browser/content/browser/tabbrowser/tab.js` sets `multiselected` on the tab itself and, through `inheritedAttributes`, on `.tab-background` (`selected=visuallyselected`, `multiselected`); the sheet's selector keys off the tab's own attributes so the existing `[selected]` behaviour is unchanged. Record the missing reference and the dated platform adaptation (2026-10-26) in the sheet header.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: change the existing `.tabbrowser-tab[selected] .tab-background` selector to `.tabbrowser-tab:is([selected], [multiselected]) .tab-background`, keeping `background-color: #EEEEEE !important` and `border-bottom-color: #EEEEEE !important` and its position between the base `.tab-background` rule and the hover comment. Add no colour, geometry, text or close-button rule. Append the provenance paragraph at the end of the leading comment, immediately before its closing `*/`, after the install-instructions paragraph (the waiting menu-bar plan inserts between the optional-search-field and find-field notes): no reference shows Firefox multi-selection; the multiselected face reuses the sheet's `#EEEEEE` selected-tab trough rather than a screenshot sample; Firefox's `tabs.css` consumes `--tab-background-color-selected` on `.tab-background:is([selected], [multiselected])` and `tab.js` sets the tab's `selected` and `multiselected` attributes (`selected=visuallyselected` is mirrored onto `.tab-background`); declaration checks do not establish rendered pixels.
- `tests/test_firefox_theme.py`: re-key the `REQUIRED_RULES` entry from `.tabbrowser-tab[selected] .tab-background` to `.tabbrowser-tab:is([selected], [multiselected]) .tab-background`, keeping its two declarations. Update the exact selector set and the assertion loop in `TestFirefoxChrome.test_tab_hover_paint_is_scoped_to_unselected_tabs` to the new key. Add `TestFirefoxChrome.test_selected_face_covers_multiselected_tabs`: the selected-face selector contains both `[selected]` and `[multiselected]` and no `[selected]`-only tab rule paints a face; its declarations equal its `REQUIRED_RULES` entry; the only other parsed selector containing `multiselected` is the hover selector; the face and bottom border are `#EEEEEE` with `!important`. Insert `"No reference shows Firefox multi-selected tabs"` and `"selected=visuallyselected"` in `test_header_names_provenance_and_preference` after `"not-found and flash states stay"` and before `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md`: extend the existing standalone-sheet row under `## firefox` (the row naming the hovered-tab guarantee) with "a tab in a multi-selection (`[multiselected]`) paints the same `#EEEEEE` selected face and open bottom border as the active tab", the new test, and the dated provenance exception naming the missing Firefox multi-selection reference, Firefox's `tabs.css` consumer and `tab.js`'s tab attributes (`multiselected`, and `selected=visuallyselected` mirrored onto `.tab-background`); keep the row's caveat that declaration checks do not establish rendered pixels and add multi-selected tabs to that list.

**Acceptance criteria.**
- `REQUIRED_RULES` validation fails when the selected-face rule is missing, either declaration is not `#EEEEEE`, or either loses `!important`.
- The scope test fails when the selector drops `[selected]` or `[multiselected]`, when a separate selected-only rule paints a tab face, or when the face is applied to any selector beyond the selected/multiselected tab background; the hover test's exact set fails on any extra `tab-background` selector.
- A hovered unselected tab stays `#EEEEEE` and remains guarded from selected and multiselected tabs; a multiselected tab's face and bottom border are `#EEEEEE`; the active face, tab border, bevel, radius, tab text, close button, pinned and vertical tabs, and find-bar states stay as they are.
- `make check` passes without Firefox or a new dependency, the palette hex set is unchanged, and implementation stays within these three files. Report declaration validation separately from live browser rendering.

### Firefox Platinum chrome: paint the open menu-bar title with the Platinum highlight (planned 2026-10-26 by the plan role; independent of the waiting hovered-tab paint) — done 2026-10-26 by the feature role

**Goal.** When the Firefox menu bar is shown and one of its titles is open, paint that title with the Platinum selection lavender `#CCCCFF` instead of Firefox's Linux accent underline, so the open title matches the desktop theme's reference-derived menu-bar title. The sheet paints `#toolbar-menubar`'s face and etched bottom rule, but its `menubar > menu` titles keep Firefox's stock rule in `chrome/toolkit/skin/classic/global/menu.css` (Linux: transparent face and a 3px transparent bottom border, which `[open]` recolours to `AccentColor`), so an open title is underlined in the system accent colour rather than filled.

**Grounding.** No reference screenshot shows Firefox chrome. The open title's fill is the already-pinned `#CCCCFF` selection: `theme/desktoptheme/org.macos8.desktop/widgets/menubaritem.svg`'s pressed slices are that flat fill, pinned by `tests/test_desktoptheme_menubaritem.py::TestMenuBarItem.test_menubaritem_pressed_is_flat_selection_colour`, and the colour itself is re-derived from `firstboot_betawiki.png` (`REFERENCE_FIRSTBOOT`) by `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`. The same widget's `normal` and `hover` slices paint nothing (`TestMenuBarItem.test_menubaritem_normal_and_hover_have_no_fill`), so this plan adds no hover rule. Record the missing Firefox menu-bar surface and the dated platform adaptation.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: after the existing `#toolbar-menubar` rule and before `.tab-background`, add
  `#toolbar-menubar menubar > menu[open] { background-color: #CCCCFF !important; border-bottom-color: #CCCCFF !important; }`
  Keep the `#toolbar-menubar` face, etched bottom border and inset white shadow unchanged, and add no hover, text-colour or geometry rule. In the header, insert the provenance paragraph between the optional-search-field note (ending "`#searchbar-new` stays Firefox's.") and the find-field note (starting "No reference shows Firefox's find field"), so it does not share an anchor with the waiting hovered-tab plan: no reference shows Firefox's menu bar; the open title's flat fill comes from `widgets/menubaritem.svg`'s pressed slices with no hover highlight; the `menubar > menu[open]` selector and its `[open]` state are Firefox's, from `chrome/toolkit/skin/classic/global/menu.css` on Linux.
- `tests/test_firefox_theme.py`: add `#toolbar-menubar menubar > menu[open]` to `REQUIRED_RULES` directly after the `#toolbar-menubar` entry, with `background-color: f"{SELECTION} !important"` and `border-bottom-color: f"{SELECTION} !important"`. Add `TestFirefoxChrome.test_menubar_open_title_paint_is_scoped_to_the_open_title`: the selectors that target a menu-bar title (any naming `menubar`, or a `menu` element outside a popup) are exactly `#toolbar-menubar` and the new selector; both declaration sets equal their `REQUIRED_RULES` entries; no other rule paints a menubar title. Append `"No reference shows Firefox's menu bar"`, `"TestMenuBarItem.test_menubaritem_pressed_is_flat_selection_colour"` and `"TestReferenceAnchors.test_selection_background"` at the end of the provenance tuple in `test_header_names_provenance_and_preference`, after `"platform colour adaptation 2026-10-26"`, rather than after `"Provenance exception"`, so the waiting hovered-tab plan's insertion there does not collide.
- `docs/invariants.md`: add a new row at the end of `## firefox` (not an edit of the existing standalone-sheet row) whose guarantee is "The open Firefox menu-bar title (`#toolbar-menubar menubar > menu[open]`) is a flat `#CCCCFF` fill with a `#CCCCFF` bottom border and no hover rule", whose test is the new scope test, and whose provenance exception names the missing Firefox menu-bar reference, the desktop-theme menubaritem provenance, that the selector and `[open]` state are Firefox's, and that declaration checks do not establish rendered pixels.

**Acceptance criteria.**
- `REQUIRED_RULES` validation fails when the rule is removed, its fill or bottom border is not `#CCCCFF`, or either declaration loses `!important`.
- The scope test fails when a `:hover` or `[_moz-menuactive="true"]` menubar rule is added, when the `[open]` guard is dropped, or when the new declarations are applied to any selector beyond the open title.
- A closed or hovered menu-bar title keeps Firefox's transparent face and inherited black text; the `#toolbar-menubar` face, its etched bottom rule, popup menus, toolbar buttons, tabs and find bar stay as they are.
- `make check` passes without Firefox or a new dependency, the palette hex set is unchanged, and implementation stays within these three files. Report declaration validation separately from live browser rendering.

### Firefox Platinum chrome: paint the hovered unselected tab face (planned 2026-10-26 by the plan role; independent of the Firefox find-field foreground plan) — done 2026-10-26 by the feature role

**Goal.** Give a hovered, unselected Firefox tab the Platinum hover fill `#EEEEEE`, so the tab strip responds to the pointer again. The sheet's `.tab-background` rule paints every tab face `#DDDDDD` with `!important`, and its greater user-origin weight suppresses Firefox's own `background-color: var(--tab-background-color-hover)` rule in `chrome/browser/skin/classic/browser/tabbrowser/tabs.css` (`.tabbrowser-tab:hover > .tab-stack > .tab-background:not([selected], [multiselected])`), leaving hover with no visible feedback.

**Grounding.** No reference screenshot shows Firefox chrome or a hovered tab. The fill is the already-pinned flat trough `#EEEEEE` (`TROUGH` in `tests/support/platinum_palette.py`, painted from `[Colors:View] BackgroundAlternate`): `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_view_background_alternate` re-derives it from `setup_emaculation.png`, and `tests/test_desktoptheme_scrollbar.py::TestScrollbarReference` ties it to the desktop theme's artwork. The sheet already uses it for the selected tab face, `--toolbarbutton-background-color-hover` and the results-row hover; this adds no new colour literal. Record the hover state as a platform adaptation dated 2026-10-26, naming Firefox's consumed `--tab-background-color-hover` source and the missing reference.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: immediately after the `.tabbrowser-tab[selected] .tab-background` rule, add
  `.tabbrowser-tab:hover > .tab-stack > .tab-background:not([selected]):not([multiselected]) { background-color: #EEEEEE !important; }`.
  Keep the base `.tab-background` face, border, bevel and radius unchanged; the hover rule only overrides its fill. Extend the header provenance with the dated missing-surface note, the `#EEEEEE` source and the two tests named above.
- `tests/test_firefox_theme.py`: add the hover selector to `REQUIRED_RULES` directly after the selected-tab entry, with `background-color: f"{TROUGH} !important"`. Add `TestFirefoxChrome.test_tab_hover_paint_is_scoped_to_unselected_tabs`: the selectors naming `tab-background` are exactly `.tab-background`, `.tabbrowser-tab[selected] .tab-background` and the new hover selector; each declaration set equals its `REQUIRED_RULES` entry; the hover selector contains `:hover`, `:not([selected])` and `:not([multiselected])`. Extend `test_header_names_provenance_and_preference` with `"No reference shows Firefox tab hover"` and `"tests/test_desktoptheme_scrollbar.py::TestScrollbarReference"` at the start of the provenance tuple, ahead of the existing entries.
- `docs/invariants.md`: extend the standalone-sheet row under `## firefox` with the hovered unselected tab guarantee and the new scope test, and add the dated platform-adaptation provenance; keep the row's statement that declaration checks do not establish rendered pixels.

**Acceptance criteria.**
- `REQUIRED_RULES` validation fails when the hover fill is removed, made non-#EEEEEE or loses `!important`; the scope test fails for an unguarded `.tab-background:hover` rule, for a rule that omits the selected or multiselected guard, and for any extra selector painting a tab background.
- Selected and multiselected tabs keep the selected fill and open bottom border; the tab face, border, bevel, radius, tab text, close button, pinned and vertical tabs and find-bar states stay as they are.
- `make check` passes without Firefox or a new dependency, the palette hex set is unchanged, and implementation stays within these three files. Report declaration validation separately from live browser rendering.

### Firefox Platinum chrome: pair the idle find field with black text (planned 2026-10-25 by the plan role; independent of the optional search-field plan) — done 2026-10-26 by the feature role

**Goal.** Pair the existing white find-field face with black text instead of Firefox's theme-dependent foreground, preserving its focused, not-found and flash states.

**Grounding.** The sheet and `REQUIRED_RULES` paint the guarded `.findbar-textbox` background but omit `color`. The finished secondary-chrome plan specifies that same background-only treatment; searches of Planned and the archive found no find-field foreground plan. In the installed `/usr/lib/firefox-esr/omni.ja`, `chrome/toolkit/skin/classic/global/findbar.css` assigns `.findbar-textbox` its input text token and, under `:root[lwtheme]`, its toolbar-field text token; focus and feedback states have separate foreground handling. A white face therefore needs its own paired foreground.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: add `color: #000000 !important` to the existing `findbar .findbar-textbox:not([status="notfound"]):not([flash="true"]):not(:focus)` rule. Keep its three guards and existing paint declarations. Do not add a foreground to the parent `findbar`, change shared field tokens, or style selection, placeholder text or other field states.
- Extend the header with provenance dated 2026-10-26: no reference shows Firefox's find field; the black-on-white pairing adapts the shared Platinum foreground and view background, pinned by `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_window_chrome_foreground` and `test_window_view_background`. Name the Firefox consumer above and the excluded states. Introduce no visual value beyond those existing palette anchors.
- `tests/test_firefox_theme.py`: extend that selector's `REQUIRED_RULES` dictionary with `color` using `BLACK`. Add `TestFirefoxChrome.test_find_field_foreground_is_guarded`: require the parsed selectors containing `findbar-textbox` to be exactly the existing guarded selector, its declarations to equal its required dictionary, and the parent `findbar` dictionary to retain its existing background and border only. Extend `test_header_names_provenance_and_preference` to pin the missing-reference statement, consumer path and state limitation.
- `docs/invariants.md`: extend the standalone-sheet row under `## firefox` with the guarded black-on-white find-field guarantee, the new scope test and the dated platform adaptation. Describe these as declaration checks, not rendered-pixel evidence.

**Acceptance criteria.**
- Required-rule validation rejects a missing or non-black foreground or missing `!important`; the scope test rejects an unguarded textbox rule or a parent foreground override. Focus, not-found and flash declarations remain Firefox-owned.
- `make check` passes without requiring Firefox or adding dependencies. Limit implementation to these three files; keep the palette set unchanged.
- Report declaration validation separately from live browser rendering.

### Firefox Platinum chrome: paint the unfocused optional search field (planned 2026-10-25 by the plan role; independent of explicit XUL tooltips) — done 2026-10-26 by the feature role

**Goal.** Give Firefox's optional classic search field a white, square Platinum face when unfocused, while leaving its focused appearance to Firefox. This is one field-paint change, independent of the waiting tooltip plan.

**Grounding.** Searches of the sheet, its tests, Planned and the finished plans found no `searchbar` styling. The finished standalone-sheet and secondary-chrome plans cover the address field and find bar instead. In the installed `/usr/lib/firefox-esr/browser/omni.ja`, `chrome/browser/skin/classic/browser/urlbar-searchbar.css` paints `#searchbar` itself; `.searchbar-textbox` is transparent and inherits its text colour. Firefox supplies separate `#searchbar:focus-within` background, outline, border and text rules. The newer `#searchbar-new` widget is a separate surface and is outside this plan.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: add exactly `#searchbar:not(:focus-within)` with `background-color: #FFFFFF`, `color: #000000`, `border: 1px solid #000000`, `border-radius: 0` and `box-shadow: none`, each `!important`. Do not override shared field tokens, the inner textbox, outlines, dimensions, icons, suggestions or widget visibility. The focus guard must cover the entire paint rule.
- Extend the header with a platform adaptation dated 2026-10-25: no reference shows Firefox's optional search field; the square 1px border and shadow-free face follow this sheet's `#urlbar-background`, and black text follows the shared Platinum foreground. Name the Firefox consumer above. Retain the white and black reference evidence in `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_window_view_background` and `test_window_chrome_foreground`; do not claim the search-field geometry is screenshot-sampled.
- `tests/test_firefox_theme.py`: add the guarded selector and five declarations to `REQUIRED_RULES`, reusing `WHITE` and `BLACK`. Add a scope test requiring parsed selectors containing `searchbar` to be exactly this guarded selector and its declaration dictionary to equal the required dictionary. Pin the missing-reference statement, consumer path and focus limitation in the provenance test. Keep the palette set as it stands after any tooltip merge; this change adds no colour.
- `docs/invariants.md`: extend the standalone-sheet row under `## firefox` with unfocused classic search-field paint, its scope test and dated provenance exception. Explicitly exclude focused paint and `#searchbar-new` from this guarantee.

**Acceptance criteria.**
- Required-rule checks reject a missing paint, wrong value or missing `!important`; the scope check rejects an unguarded rule or a second searchbar selector, preserving Firefox's focused styling at the declaration level.
- `make check` passes without requiring an installed Firefox or adding dependencies. Keep the implementation within these three files.
- Report declaration validation separately from live rendering; do not claim coverage of the newer search widget or rendered reference-pixel fidelity.

### Firefox Platinum chrome: style explicit XUL tooltips (planned 2026-10-25 by the plan role; independent of arrow-panel colour tokens) — done 2026-10-25 by the feature role

**Goal.** Give stylesheet-addressable Firefox XUL tooltips the flat pale-yellow Platinum face and black outline already used by the desktop theme. Keep this to tooltip paint; native anonymous tooltips and page content are outside the guarantee.

**Grounding.** The current Firefox sheet and `REQUIRED_RULES` in `tests/test_firefox_theme.py` contain no tooltip selector. The finished Firefox stylesheet and secondary-chrome plans cover other surfaces. The installed `/usr/lib/firefox-esr/omni.ja` member `chrome/toolkit/content/global/xul.css` sets `tooltip` appearance, InfoBackground/InfoText colours and platform-dependent borders/radii; it also warns that default tooltips are native anonymous content requiring UA styling. This plan therefore makes no claim to restyle those default tooltips.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: add one `tooltip` rule with `appearance: none`, `background-color: #FFFFCC`, `color: #000000`, `border: 1px solid #000000`, `border-radius: 0` and `box-shadow: none`, each `!important`. Preserve Firefox's padding, font, wrapping, positioning and visibility. Do not add panel tokens or profile preferences.
- Extend the provenance comment with a dated 2026-10-25 platform adaptation: no reference image shows Firefox tooltips or a Balloon Help balloon. Source yellow from `[Colors:Tooltip] BackgroundNormal` and `tests/support/platinum_palette.py::TOOLTIP_FACE`, the explicitly accepted classic-palette exception in QUESTIONS.md; source the flat square face and black outline from `theme/desktoptheme/org.macos8.desktop/widgets/tooltip.svg`, pinned by `tests/test_desktoptheme_tooltip.py::TestTooltip.test_tooltip_pixels`. Name the toolkit `xul.css` selector and native-anonymous limitation. Do not describe yellow as screenshot-sampled.
- `tests/test_firefox_theme.py`: import `TOOLTIP_FACE`, add the six declarations to `REQUIRED_RULES`, and extend `TestFirefoxChrome.test_palette_is_exact` with that constant. Add a scope test requiring declarations whose value contains `TOOLTIP_FACE` to belong to exactly the `tooltip` selector, so the new face cannot accidentally spread to menus or panels. Pin the provenance exception and native-anonymous limitation in the header test. Retain the existing standalone-sheet checks.
- `docs/invariants.md`: extend the standalone-sheet row under `## firefox` with explicit XUL tooltip paint, its test and the dated palette/geometry exception; distinguish stylesheet declarations from rendered coverage and exclude native anonymous tooltips.

**Acceptance criteria.**
- Required-rule checks fail for a missing paint declaration, incorrect value or missing `!important`; the scope check fails if the yellow face is assigned outside `tooltip`.
- The desktop tooltip palette/geometry tests and `make check` pass. Tests require no installed Firefox or new dependency.
- Report declaration validation separately from a live rendering check; no claim of default-tooltip coverage or screenshot-derived yellow. The change is confined to these three files and is independently mergeable from arrow-panel colours.

### Firefox Platinum chrome: connect arrow-panel colours to consumed popup tokens (planned 2026-10-25 by the plan role; independent of square arrow-panel corners) — done 2026-10-25 by the feature role

**Goal.** Make arrow-panel bodies use the intended Platinum face, text and border through Firefox's current popup colour tokens. This is one consumer-mapping correction, independently mergeable from the queued square-corners plan.

**Grounding.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css` sets three `--arrowpanel-*` colour properties on `:root`. Searching CSS in the installed `/usr/lib/firefox-esr/omni.ja` and `browser/omni.ja` found no occurrences of those three names. Toolkit `chrome/toolkit/skin/classic/global/popup.css` instead consumes `--panel-background-color`, `--panel-text-color` and `--panel-border-color` in `:is(menupopup, panel)::part(content)`. The sheet supplies these on `menupopup` but not arrow panels. The finished menu-colour plan explicitly left root arrow-panel tokens alone; the waiting arrow-panel plan changes radius only.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: remove `--arrowpanel-background`, `--arrowpanel-color` and `--arrowpanel-border-color` from `:root`. Set `--panel-background-color: #DDDDDD !important`, `--panel-text-color: #000000 !important` and `--panel-border-color: #000000 !important` on `panel[type="arrow"]`. Extend that rule if the corners plan has merged; otherwise create it. Preserve its radius if present and the existing menu declarations. Leave panel contents, shadows, padding and general non-arrow panels outside this change.
- Extend the sheet's provenance comment: no reference screenshot shows Firefox arrow panels; this is a platform adaptation dated 2026-10-25, sourcing the face and black from the existing Platinum menu mapping and naming the toolkit popup.css consumer. Retain the palette evidence in `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_menu_bar_face` and `test_window_chrome_foreground`; introduce no colour or metric.
- `tests/test_firefox_theme.py`: replace the three root expectations in `REQUIRED_RULES` with the consumed tokens on `panel[type="arrow"]`, using `FACE` and `BLACK`. Update `TestFirefoxChrome.test_consumed_popup_colour_tokens_are_scoped_to_menu_popups` and its name to require each of the three consumed colour tokens on exactly `menupopup` and `panel[type="arrow"]`. Keep its obsolete menu-token assertions, and add assertions that the three old arrow-panel properties occur in no parsed rule. Do not change the radius scope test or require host Firefox files.
- `docs/invariants.md`: update the standalone-sheet row under `## firefox` to include arrow-panel body colours, the two permitted selectors, the removed arrow-panel token names and the dated consumer/provenance exception. Preserve the independent radius guarantee as it stands when implementing.

**Acceptance criteria.**
- Required-rule checks reject a missing consumed arrow-panel token, incorrect palette value or missing `!important`; scope checks reject moving these overrides to `:root` or general `panel`, dropping the menu mapping or retaining old arrow-panel properties.
- Existing palette and standalone-sheet checks, reference palette tests and `make check` pass. The correction works as a declaration change whether or not the square-corners plan has merged.
- Report declaration validation separately from live rendering; these tests do not establish rendered Firefox pixels. The face/text/border mapping is one cohesive change, with no new panel-content styling.

### Firefox Platinum chrome: square arrow-panel corners (planned 2026-10-25 by the plan role; independent of the waiting menu colour token correction) — done 2026-10-25 by the feature role

**Goal.** Give Firefox `panel[type="arrow"]` popup bodies the square corners already used for this sheet's menus, tabs and address field. This is one geometry change, separate from the waiting menu palette correction.

**Grounding.** The sheet currently declares `--panel-border-radius` only on `menupopup`. The installed `/usr/lib/firefox-esr/omni.ja` member `chrome/toolkit/skin/classic/global/popup.css` consumes it in `:is(menupopup, panel)::part(content)` as `border-radius` and separately identifies arrow panels with `panel:where([type="arrow"])`. The completed menu-corners plan explicitly excluded arrow panels; searches of Planned and the finished Firefox entries found no arrow-panel radius override. No reference screenshot shows Firefox arrow panels: zero radius is a platform adaptation sourced from the sheet's existing square menu, `.tab-background` and `#urlbar-background` convention, not a sampled Mac OS metric. Record that missing surface and source with the adaptation date.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: add `panel[type="arrow"] { --panel-border-radius: 0 !important; }` and extend the header provenance. Keep the existing `menupopup` radius. Leave palette tokens, padding, shadows and panel contents outside this change; do not broaden the override to `panel` or `:root`.
- `tests/test_firefox_theme.py`: add that exact selector and declaration to `REQUIRED_RULES`. Rename `TestFirefoxChrome.test_panel_radius_override_is_scoped_to_menu_popups` to reflect menus and arrow panels, and require the set of selectors declaring the radius token to equal `{"menupopup", 'panel[type="arrow"]'}`. This deliberately extends the previous menu-only guarantee while continuing to exclude general panels. Tests must run without Firefox or host archives.
- `docs/invariants.md`: update the `## firefox` standalone-sheet row to name square menu and arrow-panel bodies, their restricted selectors and the dated platform geometry provenance.

**Acceptance criteria.**
- `TestFirefoxChrome.test_required_rules` rejects a missing arrow-panel radius, a nonzero value or missing `!important`; the scope test rejects moving it to `:root` or general `panel`, and still requires the menu override.
- No new palette value is introduced. Existing exact-palette and standalone-sheet checks pass, and `make check` passes after the invariant update.
- Report these as declaration checks, not proof of live Firefox rendered pixels. This plan neither corrects the separate arrow-panel colour tokens nor changes the waiting menu-colour plan's scope.

### Declare the project's deterministic check (planned 2026-10-25 by the plan role; independent of the Firefox plans) — done 2026-10-25 by the feature role

**Declares the project check**

**Goal.** Register the existing `make check` command with tumwater so its build pre-check, red-main baseline and redeploy check can use the project's unittest suite.

**Grounding.** `Makefile`'s `check` target runs `python3 -m unittest discover -s tests -v -p 'test*.py'` by default, with interpreter and selection guards. `tests/test_make_check.py::TestCheckPattern.test_default_pattern_runs_every_test_module` pins that default wiring. README.md documents this command, and `.github/workflows/ci.yml` already runs it; the finished CI repair covers workflow parity, not tumwater's declaration. No `package.json` was found on the worktree's ancestor chain. The supplied no-check alert therefore calls for the `check.command` route, not an npm wrapper.

**Approach and files touched.**
- Declare the exact command `make check` through `check.command` in the worktree-root `.tumwater-config-request.json`. The run's explicit no-check instructions authorize this request route; do not edit `tumwater.json` or configure the primary checkout from this worktree.
- Update README.md's Development team section with the request lifecycle, the manual operator command and its primary-checkout context, and post-merge verification using `tumwater doctor check --json` and `tumwater status --json`. Keep `Makefile`, its tests and the separate `make check-references` workflow step intact.
- Use the existing suite and `TestCheckPattern` coverage to validate the registered command; no new runner, dependency or test that merely mirrors configuration is needed.

**Acceptance criteria.**
- The request declares `check.command` as exactly `make check`, without a narrowed `CHECK_PATTERN` or `CHECK_TESTS`; run it with those overrides unset and record its exit status.
- After the request is applied at merge, the primary project's `tumwater doctor check --json` reports its `check` row as `ok`, and `tumwater status --json` carries no `noDeclaredCheck`. Merge confirms the live configuration; in-run results still reflect the pre-declaration state.
- `make check` passes after the documentation and plan changes. Existing default-discovery and invalid-selection tests continue to pass. Configuration verification is deferred to merge, separately from this run's suite result.

**Implementation adjustment 2026-10-25 by the feature role.** Replaced the operator-only prerequisite with the configuration request explicitly authorized by this run. Completion records the declaration; applying and confirming the live configuration belongs to merge.

### Firefox Platinum chrome: connect menu colours to the consumed popup tokens (planned 2026-10-25 by the plan role; independent of the square menu popup corners plan) — done 2026-10-25 by the feature role

**Goal.** Make the existing Platinum menu face and text declarations reach Firefox's popup content. This repairs the token mapping from the finished standalone-sheet plan; it adds no new surface or palette value.

**Grounding.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css` and `tests/test_firefox_theme.py::REQUIRED_RULES` currently use `--panel-background` and `--panel-color` on `menupopup`. The installed `/usr/lib/firefox-esr/omni.ja` member `chrome/toolkit/skin/classic/global/popup.css` instead defines `--panel-background-color` and `--panel-text-color` locally on non-arrow popups and consumes them in `:is(menupopup, panel)::part(content)` as background and text colour. Searching CSS in both installed omni.ja archives found no alias connecting the old pair to these consumed tokens. Searches of Planned and the finished Firefox plans found no correction of these names; the original stylesheet plan specified the old pair.

No reference screenshot shows Firefox menu chrome. This is a Firefox-required token adaptation using the sheet's existing `FACE` (#DDDDDD) and `BLACK` (#000000) mapping. Preserve the shared palette evidence in `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_menu_bar_face` and `test_window_chrome_foreground`; record the missing Firefox surface and the toolkit popup.css consumer as provenance, without claiming a Firefox reference-pixel match.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: replace the two old declarations in `menupopup` with `--panel-background-color: #DDDDDD !important` and `--panel-text-color: #000000 !important`. Keep them on `menupopup` to override Firefox's element-local defaults. Extend the provenance comment with the consumer and adaptation date. Preserve the border declaration and any radius declaration added by the independent corners plan; leave root arrow-panel tokens and menu-item states alone.
- `tests/test_firefox_theme.py`: replace the two keys in `REQUIRED_RULES["menupopup"]`, reusing `FACE` and `BLACK`. Add a focused `TestFirefoxChrome` test asserting that declarations of the new pair occur only on `menupopup` and that its old pair is absent. Do not require Firefox or a host omni.ja archive to run the tests.
- `docs/invariants.md`: clarify the `## firefox` standalone-sheet guarantee to name menu background/text through the consumed popup tokens and retain the platform-adaptation provenance exception.

**Acceptance criteria.**
- `TestFirefoxChrome.test_required_rules` rejects either missing consumed token, a wrong value or missing `!important`; the focused test rejects putting the overrides on `:root` or general `panel`, and rejects retaining the obsolete pair on `menupopup`.
- Existing exact-palette and standalone-sheet checks pass, as do the reference palette tests and `make check`. No geometry or menu-item state change is part of this correction.
- Report declaration checks separately from live Firefox rendering: these tests do not establish rendered menu pixels. The background and foreground replacements are one paired consumer-mapping correction and should ship together.

### Firefox Platinum chrome: square menu popup corners (planned 2026-10-25 by the plan role; independent of the address-bar button fills plan) — done 2026-10-25 by the feature role

**Goal.** Give Firefox `menupopup` surfaces square corners consistent with the sheet's existing square fields and tabs. This is one geometry change; it does not extend to arrow panels or menu-item highlight shapes.

**Grounding.** The sheet's `menupopup` rule sets palette variables but no radius. In `/usr/lib/firefox-esr/omni.ja`, `chrome/toolkit/skin/classic/global/popup.css` sets `--panel-border-radius: 6px` on non-arrow popups when Nova is disabled; its `:is(menupopup, panel)` nested `::part(content)` consumes that token as `border-radius`. A root-only override would lose to that local declaration. The Linux fallback without CSD transparency already uses zero. Searches of Planned and the finished Firefox stylesheet, secondary-chrome and results-dropdown plans found no menu-popup radius change.

No reference screenshot shows Firefox menus. Zero radius is an explicit platform adaptation sourced from this sheet's existing `.tab-background` and `#urlbar-background` square-corner convention, not a newly sampled Mac OS metric. Record both the missing surface and this source in the provenance comment; no new palette value is needed.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: add `--panel-border-radius: 0 !important` to the existing `menupopup` rule, placing the override on the element where Firefox defines the token. Extend the header provenance with the menu-popup geometry adaptation. Do not put the token on `:root` or `panel`, or change shadows, padding, colours or item states.
- `tests/test_firefox_theme.py`: extend `REQUIRED_RULES["menupopup"]` with that exact declaration so `TestFirefoxChrome.test_required_rules` pins its value and priority. Add a focused test asserting that the only selector declaring `--panel-border-radius` is `menupopup`, guarding against accidentally squaring unrelated panels such as autoscroll.
- `docs/invariants.md`: extend the `## firefox` standalone-sheet guarantee to name square menu-popup corners and retain the explicit adaptation provenance exception.

**Acceptance criteria.**
- The required-rules test rejects a missing radius, a nonzero radius or missing `!important`; the scope test rejects a root or general panel radius override.
- The exact-palette, no-at-rule/import and non-universal-selector tests continue to pass. Existing palette pixel evidence requires no new anchor because this change introduces no colour.
- `make check` passes. Report declaration verification separately from live Firefox rendering: these tests do not launch Firefox or prove a rendered menu's corner pixels.

### Firefox Platinum chrome: use Platinum hover and pressed fills for address-bar buttons (planned 2026-10-25 by the plan role; independent of the address-bar results dropdown plan) — done 2026-10-25 by the feature role

**Goal.** Give Firefox's address-bar buttons the same #EEEEEE hover and #CCCCFF pressed/open fills as the sheet's toolbar buttons. The current sheet sets `--toolbarbutton-background-color-hover` and `--toolbarbutton-background-color-active`, but not the separate `--urlbar-box-background-color-hover` and `--urlbar-box-background-color-active` tokens those controls consume. This is one state-palette change, independent of the queued results-row styling.

**Grounding.** In `/usr/lib/firefox-esr/browser/omni.ja`, `chrome/browser/skin/classic/browser/urlbar/urlbar.tokens.css` defines these two tokens on `:root, :host` using Firefox button colours and dark-mode colour mixing. `identity-block/identity-block.css` under the same browser skin consumes them for `.identity-box-button`, `#trust-icon-container` and `#tracking-protection-icon-container` hover and pressed/open states. `urlbar-searchbar.css` consumes them for `.urlbar-page-action`, the go buttons, search-mode close buttons and `#urlbar-zoom-button`. The theme does not override these tokens; searches of Planned and the finished-plan archive found no plan covering them.

No reference screenshot shows Firefox address-bar buttons. This is a platform adaptation of the existing toolbar state mapping, not a claim of reference-exact Firefox chrome. Its values come from `tests/support/platinum_palette.py`: `TROUGH` is re-derived by `TestReferenceAnchors.test_view_background_alternate` in `tests/test_colorscheme_reference.py` from `setup_emaculation.png` at (200, 470); `SELECTION` is re-derived by `test_selection_background` from the Introduction banner in `firstboot_betawiki.png`. Keep those pixel tests as the palette evidence.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: add `--urlbar-box-background-color-hover: #EEEEEE !important` and `--urlbar-box-background-color-active: #CCCCFF !important` to `:root`. Extend the header's adaptation provenance to name address-bar button states and their reuse of the toolbar state mapping. Use the shared tokens so Firefox's existing disabled, hover and open selectors continue deciding when a fill applies.
- `tests/test_firefox_theme.py`: add both declarations to `REQUIRED_RULES[":root"]`, using `TROUGH` and `SELECTION`. `TestFirefoxChrome.test_required_rules` must pin each value and its `!important`. Retain the existing palette set.
- `docs/invariants.md`: add address-bar button state fills to the `## firefox` standalone-sheet guarantee and retain its no-reference-screenshot provenance exception.

**Scope.** Change these two background tokens only; idle/focus fills, security glyph colours, outlines, geometry and results-row tokens are outside this plan. The shared tokens also affect Firefox's search go button; this is intentional consistency with the address-bar go button. No new dependency or profile preference is needed.

**Acceptance criteria.**
- `TestFirefoxChrome.test_required_rules` fails when either token is absent, has the wrong value, or lacks `!important`.
- `test_palette_is_exact`, `test_sheet_has_no_at_rule_or_import` and `test_selectors_are_not_universal` pass; the existing reference-anchor tests continue to derive the two reused colours from PNG pixels.
- `make check` passes, including the invariant register checks. Tests pin declarations and palette evidence, not a live Firefox chrome render; retain that limitation in implementation reporting.

### Firefox Platinum chrome: paint the address-bar results dropdown's selected and hovered rows, separator and square corners (planned 2026-10-24 by the plan role; independent of the waiting GTK mixed check box plan) — done 2026-10-25 by the feature role

**Goal.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css` paints the urlbar field white with a black outline (`#urlbar-background`), but the results dropdown that opens under it still uses Firefox's own colours. The selected row is `SelectedItem` blue, or `rgb(0, 99, 255)` under a lightweight theme. The hover wash is `rgb(240, 240, 244)`, the separator above the results is a translucent grey, and each row has rounded corners. Paint these with the Platinum values the sheet already uses for its menus: the #CCCCFF selection with black text (as `menupopup > menuitem[_moz-menuactive="true"]`), the #EEEEEE trough as the hover wash (as `--toolbarbutton-background-color-hover`), the etched separator's #888888 dark half as the rule, and square corners.

**Grounding (Firefox 153.5.1esr, `/usr/lib/firefox-esr/browser/omni.ja`, read with python `zipfile`).**
- `chrome/browser/skin/classic/browser/urlbar/urlbarview.tokens.css` defines `--urlbarview-background-color-hover`, `--urlbarview-background-color-selected`, `--urlbarview-text-color-selected` and `--urlbarview-separator-color` on `:root`.
- `chrome/browser/skin/classic/browser/urlbar/view-proton.css` uses those tokens:
  - `.urlbarView-row[row-selectable]:not([selected]):hover` paints `var(--urlbarview-background-color-hover)`.
  - `.urlbarView-row[selected]` paints `var(--urlbarview-background-color-selected)` with `color: var(--urlbarview-text-color-selected)`.
  - `.urlbarView-body-inner`'s top border is `1px solid var(--urlbarview-separator-color)`.
  - `.urlbarView-row` sets `border-radius: calc(var(--urlbarView-row-gutter) + var(--urlbar-inner-border-radius))`.
  - Its `:root[lwtheme]` block overrides the selected colours with the blue values above.
- A user-sheet `!important` declaration outranks these author declarations, which is the same mechanism the sheet's existing `--toolbarbutton-*` variables rely on.

**Approach.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`:
  - Paint `.urlbarView-row[selected]` directly with `background-color: #CCCCFF !important` and `color: #000000 !important`.
  - Paint `.urlbarView-row[row-selectable]:not([selected]):hover` with `background-color: #EEEEEE !important` and `.urlbarView-body-inner` with `border-top-color: #888888 !important`.
  - Leave shared `--urlbarview-*` tokens to Firefox so these overrides do not propagate to realtime sub-items and one-off buttons.
  - Add a rule `.urlbarView-row` with `border-radius: 0 !important`, placed directly after the `#urlbar-background` rule.
  - In the header's provenance paragraph, add "address-bar results" to the list of adapted surfaces, after "fields".
- `tests/test_firefox_theme.py`:
  - Add the selected-row, hover-row and body-separator declarations to `REQUIRED_RULES`, using `SELECTION`, `BLACK`, `TROUGH` and `ETCH_DARK`.
  - Add a `REQUIRED_RULES[".urlbarView-row"]` entry `{"border-radius": "0 !important"}`.
  - Add `test_results_paint_does_not_override_shared_tokens` to prohibit shared `--urlbarview-*` declarations and constrain urlbarView selectors and declarations to `REQUIRED_RULES`.
  - Leave `test_palette_is_exact`'s expected set unchanged, because every new value is already in it.
- `docs/invariants.md`: in the `## firefox` standalone-sheet guarantee, add "address-bar results rows" to the listed surfaces (after "toolbars"). Keep the row's no-reference-screenshot provenance exception as it is.

**Out of scope.** The `.urlbarView-realtime-item` sub-items (multi-item realtime rows behind a feature gate) and the one-off search buttons. Both keep Firefox's styling.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `test_required_rules` fails if a selected-row, hover-row or body-separator declaration or the `.urlbarView-row` radius is removed or changed.
- `test_results_paint_does_not_override_shared_tokens` rejects shared `--urlbarview-*` declarations and unexpected urlbarView selectors or declarations.
- `test_palette_is_exact` passes with the same hex set. `test_sheet_has_no_at_rule_or_import` and `test_selectors_are_not_universal` still pass.
- `tests/invariants.py` accepts the updated `## firefox` row, and `make check` is green.

### Platinum GTK mixed check boxes: draw an inconsistent check box or radio as a 2px black dash in GTK 3 and GTK 4 (planned 2026-10-24 by the plan role; independent of the waiting GTK 3 popover submenu-arrow plan) — done 2026-10-24 by the feature role

**Goal.** Both GTK sheets give `check:checked` and `radio:checked` a shipped glyph, but neither names `:indeterminate`. So a check button in the mixed state (`set_inconsistent(True)`, for example a "select all" box over a partial selection) draws GTK's builtin dash, not a Platinum one. I measured this live under `GDK_BACKEND=x11` (DISPLAY=:1), loading each sheet with its asset URLs rewritten to absolute paths:
- GTK 3 (`Gtk.OffscreenWindow.get_pixbuf` of a `Gtk.CheckButton` with `set_inconsistent(True)`): the 14px `#DDDDDD` face shows a broken builtin dash of three separate 2x2 black squares.
- GTK 4 (`Gtk.WidgetPaintable` of the `check` indicator node rendered to a texture): the builtin dash is drawn near-white (`#FFFFFF`/`#FBFBFB`) on rows 6–7 of the 16px indicator texture. So it is faint on the grey check face and invisible on the white radio face.
- With the candidate asset and rule below appended to a copy of each sheet, the check and the radio both show a solid `#000000` dash 8px wide and 2px tall, centred in the 14px glyph area (canvas columns 3–10, rows 6–7). In GTK 3 the dash also wins over `check:checked` when the button is both active and inconsistent, because the rule comes later in the sheet at equal specificity.

**Design (decided; do not widen).**
- New asset `theme/gtk/org.macos8.desktop/assets/check-mixed.svg`. It is a 14x14 canvas like `checkmark.svg`, with the root element first and a comment after it (see the earlier BUGS-FIXED entry about an SVG comment before the root). It holds a single path: `<path d="M 4,7 L 10,7" fill="none" stroke="#000000" stroke-width="2" stroke-linecap="square"/>`. The comment names its provenance: the 2px square-capped black stroke reuses `checkmark.svg`'s stroke, which is adapted from the desktop theme's `widgets/checkmarks.svg`. No reference screenshot shows a mixed-state control, and GTK requires the `:indeterminate` state.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`: directly after the `radio:checked` rule, add `check:indeterminate, radio:indeterminate { -gtk-icon-source: url("../assets/check-mixed.svg"); }`. It must come after both `:checked` rules. In each header comment, extend the sentence about the checked glyphs: a mixed (indeterminate) check box or radio loads the shared `assets/check-mixed.svg` dash.
- Out of scope:
  - Menu and popover-row indeterminate checks: their rules stay unchanged, and the new rule applies wherever it matches.
  - The Kvantum (Qt) tristate check box: no Qt bindings are installed to measure it.
  - `:disabled` or `:backdrop` variants.
- Install plumbing for the new tenth asset. Mirror every place `bullet.svg` appears:
  - `Makefile`: the `install-gtk` staging trap, the `install -Dm644`, the `mv`, and the uninstall `rm -f`. That is the four `bullet.svg` occurrences, each with its `.check-mixed.svg.staging` counterpart.
  - `tests/support/gtk_fixtures.py` `SHIPPED_FILES`.
  - `tests/test_gtk_install.py` `STAGING_PATHS`.
  - README: "the nine shared check, radio, …" becomes ten and names the mixed-state dash; both "twelve GTK files" / "twelve opt-in GTK files" become thirteen.
  - `docs/invariants.md`: the GTK install row's "twelve GTK theme files" becomes thirteen.

**Files touched.**
- `theme/gtk/org.macos8.desktop/assets/check-mixed.svg` (new).
- Both GTK sheets: the rule and the header sentence.
- `tests/support/gtk_theme_spec.py`: add `MIXED_GLYPH = {"-gtk-icon-source": 'url("../assets/check-mixed.svg")'}` beside `RADIO_GLYPH`. In `GtkSheetRuleCases.test_check_and_radio`, add `self.assert_rule("check:indeterminate, radio:indeterminate", MIXED_GLYPH)`. First check how `parse_css` keys a selector list (by the full list or by each selector) and use that key form.
- `tests/test_gtk_theme.py`:
  - Add `CHECK_MIXED` beside `BULLET`.
  - Add `'"../assets/check-mixed.svg"'` to `test_icon_sources_point_at_shipped_assets`.
  - In `TestCheckGlyphs`, include the new tree in `test_assets_stand_alone`, `test_assets_put_the_root_first`, `test_assets_span_a_14px_canvas` and `test_assets_use_only_the_two_glyph_fills`, and add `test_mixed_geometry`. It pins the single path's `d`, fill `none`, stroke `#000000`, stroke-width `2` and square linecap.
  - Add `test_mixed_check_draws_a_black_dash`, modelled on `test_entry_progress_draws_a_two_pixel_strip`. It renders a `Gtk.CheckButton` with `set_can_focus(False)` and `set_inconsistent(True)` offscreen, with the `../assets/` URLs rewritten to the absolute assets directory instead of `none`, and asserts three things:
    - `#000000` at the dash centre;
    - the `#DDDDDD` face one row above and one row below the dash;
    - `#DDDDDD` at the face column just left of the dash.
    It skips when GTK 3 introspection or a display is missing.
- `tests/test_gtk4_theme.py`: add `'"../assets/check-mixed.svg"'` to its `test_icon_sources_point_at_shipped_assets`.
- `Makefile`, `tests/support/gtk_fixtures.py`, `tests/test_gtk_install.py`, `README.md`: the plumbing above.
- `docs/invariants.md`:
  - The count edit above.
  - A new row at the end of `## gtk`.
    - Guarantee: both GTK sheets draw an indeterminate check box or radio with the shipped `check-mixed.svg` 2px black dash.
    - Tests: `test_check_and_radio` in both suites, `TestCheckGlyphs::test_mixed_geometry`, and the GTK 3 pixel test.
    - Provenance: no reference screenshot shows a mixed-state control. The stroke reuses the reference-grounded check glyph's 2px black stroke. The 8px dash length is this theme's choice, centred on the 14px glyph canvas.

**Acceptance criteria.**
- In either sheet, removing the rule, renaming its selector, or changing its URL fails `test_check_and_radio`. Changing the asset's path data fails `test_mixed_geometry`.
- The GTK 3 pixel test passes against the edited sheet. Repeat the GTK 4 live capture above against the edited sheet: it shows `#000000` on columns 4–11 of rows 7–8 of the 16px check and radio indicator textures.
- `make install-gtk DESTDIR=…`-style tests in `tests/test_gtk_install.py` install, stage and uninstall the new asset. `test_only_palette_hex_literals`, `TestArrowGlyphs` and the rest of both GTK suites still pass. `tests/invariants.py` accepts the edited rows, and `make check` is green.

### Platinum GTK 3 popover submenu arrows: draw the reference's solid black submenu triangle on a GTK 3 popover menu row that opens a submenu (planned 2026-10-24 by the plan role; independent of the waiting GTK entry progress plan) — done 2026-10-24 by the feature role

**Goal.** The GTK 3 sheet gives `menu menuitem arrow` the shipped `assets/submenu-arrow.svg`, and the GTK 4 sheet gives `popover.menu modelbutton > arrow.right` the same asset. But no GTK 3 rule names a popover menu row's arrow, so in a GTK 3 popover built from a `Gio.Menu` (`Gtk.MenuButton` with `set_use_popover(True)`, as in GNOME-style app menus), a row from `append_submenu` draws GTK's builtin chevron, not the Platinum triangle. A live dump of that popover's style tree shows the node path `popover.background.menu … modelbutton.flat > arrow.right`. Stock Adwaita covers it with `modelbutton.flat arrow.right { -gtk-icon-source: -gtk-icontheme("pan-end-symbolic"); }`.

I measured this live with PyGObject on GTK 3 under `GDK_BACKEND=x11` (Wayland windows cannot be read back), with `XDG_DATA_HOME` pointing at a temp dir whose `themes/` holds the theme. The capture is `Gdk.pixbuf_get_from_window` of the submenu row's allocation in the open popover:
- `GTK_THEME=org.macos8.desktop`: the right end of the row shows the builtin chevron, an outlined `>` about 4px thick that spans 16 rows.
- A copy of the sheet with the rule below appended: the chevron is gone, and the row shows a small solid triangle that includes pure `#000000` pixels, matching `submenu-arrow.svg`'s `M 6,3 L 6,11 L 10,7 Z` path. The node already reserves 16x16 (the builtin chevron fills 16 rows), so the rule does not set a size.

**Design (decided; do not widen).**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: directly after the `menu menuitem arrow` rule, add `popover modelbutton arrow.right { -gtk-icon-source: url("../assets/submenu-arrow.svg"); }`. The `popover modelbutton` prefix matches the sheet's existing popover row rules (`popover modelbutton:hover, popover modelbutton:selected` and `popover modelbutton check, popover modelbutton radio`).
- In the GTK 3 header comment, extend the sentence "A menu row's submenu arrow loads the shared assets/submenu-arrow.svg, …" so it says a menu row's or popover menu row's submenu arrow loads it.
- Out of scope:
  - The sliding-submenu back arrow (`arrow.left`), which the reference never shows. The GTK 4 submenu-arrow plan left out the same arrow.
  - Right-to-left mirroring, and hover or disabled arrow colours. The arrow stays black on the `#CCCCFF` hover fill, as in the reference.
  - Any GTK 4 change.
- No new asset, colour or file is added, so the Makefile, `SHIPPED_FILES`, `STAGING_PATHS` and the README counts do not change.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: the rule and the header sentence.
- `tests/test_gtk_theme.py`: in `TestGtkTheme.test_submenu_arrow`, keep the existing `self.assert_submenu_arrow(("menu menuitem arrow",), sized=True)` call and add `self.assert_submenu_arrow(("popover modelbutton arrow.right",), sized=False)`. `assert_submenu_arrow` and `SUBMENU_ARROW` in `tests/support/gtk_theme_spec.py` already exist; do not change them.
- `docs/invariants.md`: update the existing `## gtk` row that begins "Both GTK sheets draw a submenu row's arrow from the shipped `submenu-arrow.svg`" so the guarantee says it covers GTK 3 menu rows, GTK 3 popover menu rows and GTK 4 popover menu rows. Its tests and provenance cells stay as they are.

**Acceptance criteria.**
- Removing the new rule, renaming its selector, or changing its URL fails `TestGtkTheme.test_submenu_arrow`.
- Run the live X11 capture above against the edited sheet (a temp `XDG_DATA_HOME` whose `themes/org.macos8.desktop` is a symlink to the absolute `theme/gtk/org.macos8.desktop` path, `GDK_BACKEND=x11`, `timeout 20 python3 -I`). It shows the solid triangle with `#000000` pixels where the builtin chevron was.
- `TestArrowGlyphs`, `test_only_palette_hex_literals` and the rest of `tests/test_gtk_theme.py` and `tests/test_gtk4_theme.py` still pass. `tests/invariants.py` accepts the edited row, and `make check` is green.

### Platinum GTK entry progress: draw an entry's progress fraction as a 2px selection-lavender strip in GTK 3 and GTK 4 (planned 2026-10-24 by the plan role; independent of the waiting GTK 3 popover check/radio plan) — done 2026-10-24 by the feature role

**Goal.** Both GTK sheets are standalone (no `@import` of Adwaita), and neither names an entry's progress node, so `gtk_entry_set_progress_fraction()` / `set_progress_pulse_step()` draw nothing. Download fields, location bars and similar entries show no progress at all. Adwaita draws it as a 2px blue underline: GTK 3 `entry progress`, GTK 4 `entry > progress > trough > progress`. Neither sheet has any rule that matches those nodes: `progressbar progress` and `progressbar > trough > progress` need a `progressbar` ancestor.

I measured this live under `GTK_THEME=org.macos8.desktop`:
- GTK 3, `Gtk.StyleContext` on the `Gtk.WidgetPath` `window > entry > progress`: background `rgba(0,0,0,0)`, `min-height` 0, border 0, margin 0. The node has no height and no paint.
- GTK 4, rendering a `Gtk.WidgetPaintable` of a 120px `Gtk.Entry` with `set_progress_fraction(0.5)` (texture 150x19): the rows above the bottom border stay `#FFFFFF` across the field.
- With the candidate GTK 4 rules below appended to a copy of the sheet, a `#CCCCFF` strip covers about the left half of the field, just above the black bottom border. Without `margin-bottom: 1px` it spills into the border row.

**Design (decided; do not widen).**
- `tests/support/gtk_theme_spec.py`: add `ENTRY_PROGRESS` (GTK 3: transparent background, `border-color: #CCCCFF`, `border-width: 0 0 2px`, plus `background-image: none; border-radius: 0; border-style: solid; box-shadow: none; margin: 0`) and `ENTRY_PROGRESS_GTK4 = {**PROGRESSBAR_PROGRESS, "min-height": "2px"}` beside `PROGRESSBAR_PROGRESS`. Comment: an entry's progress reuses the progress-bar selection fill as a 2px strip, Adwaita's stock thickness.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: directly after the `progressbar progress:disabled` rule, add `entry progress` drawing the strip as a 2px bottom border, because GTK 3 ignores `min-height` on this node: `background-color: transparent; background-image: none; border-color: #CCCCFF; border-radius: 0; border-style: solid; border-width: 0 0 2px; box-shadow: none; margin: 0;`.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: directly after `progressbar > trough > progress:disabled`, add three rules:
  - `entry > progress { margin-bottom: 1px; }`
  - `entry > progress > trough { min-height: 2px; }`
  - `entry > progress > trough > progress` with `ENTRY_PROGRESS_GTK4`: the progress-bar fill declarations plus `min-height: 2px`.
- In each sheet's header comment, extend the sentence about the level bar reusing the progress-bar trough and selection fill: an entry's progress fraction is a 2px strip of the same selection fill. The 2px thickness is Adwaita's stock value, because no reference screenshot shows an entry progress, and the node names are GTK-required.
- Out of scope:
  - Spin-button progress (`spinbutton progress`).
  - A `:disabled` or `:backdrop` variant.
  - Any change to the progress bar or level bar rules.
- No new asset or colour is added (`#CCCCFF` is already in both sheets), so the Makefile, `SHIPPED_FILES`, `STAGING_PATHS` and the README counts do not change.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: the rules and the header sentence.
- `tests/support/gtk_theme_spec.py`: `ENTRY_PROGRESS` and `ENTRY_PROGRESS_GTK4`.
- `tests/test_gtk_theme.py`: add `TestGtkTheme.test_entry_progress`, which calls `self.assert_rule("entry progress", ENTRY_PROGRESS)`, and `test_entry_progress_draws_a_two_pixel_strip`, which renders an `Gtk.Entry` with `set_progress_fraction(0.5)` offscreen and pins the drawn strip pixels (skipped when GTK 3 introspection or a display is missing).
- `tests/test_gtk4_theme.py`: add `TestGtk4Theme.test_entry_progress`, which asserts three things:
  - `self.assert_rule("entry > progress > trough > progress", ENTRY_PROGRESS_GTK4)`
  - `{"min-height": "2px"}` on `entry > progress > trough`
  - `{"margin-bottom": "1px"}` on `entry > progress`
- `docs/invariants.md`: add one row at the end of the `## gtk` section.
  - Guarantee: the GTK 3 and GTK 4 sheets draw an entry's progress fraction as a 2px strip of the `#CCCCFF` selection fill.
  - Tests: both `test_entry_progress` tests and the GTK 3 pixel test.
  - Provenance: no reference screenshot shows an entry progress. The fill reuses the reference-grounded progress-bar selection. The 2px thickness and the node names come from the toolkits' stock sheets.

**Acceptance criteria.**
- Removing any of the four new rules, or changing any declaration in them, fails the matching `test_entry_progress`.
- The GTK 3 offscreen render of an `Gtk.Entry` with `set_progress_fraction(0.5)` shows a 2px `#CCCCFF` strip, pinned by `test_entry_progress_draws_a_two_pixel_strip`.
- A live GTK 4 render of a `Gtk.Entry` with `set_progress_fraction(0.5)` shows `#CCCCFF` on the strip at a quarter of the field width and `#FFFFFF` at three quarters. Its bottom border row matches the same entry without progress.
- `test_only_palette_hex_literals`, `test_progressbar`, `test_levelbar` and the rest of `tests/test_gtk_theme.py` and `tests/test_gtk4_theme.py` still pass. `tests/invariants.py` accepts the new row, and `make check` is green.

### Platinum GTK 3 popover menus: draw a popover menu row's check and radio without the box, as GTK 3 menus and GTK 4 popovers do (planned 2026-10-24 by the plan role; independent of the waiting GTK spinner plan) — done 2026-10-24 by the feature role

**Goal.** In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, the boxless rule (`menu menuitem check, menu menuitem radio`) covers only `GtkMenu` rows. A check or radio row in a GTK 3 popover menu (`GtkModelButton`, CSS node `modelbutton` with a `check` or `radio` child) still matches the generic `check, radio` rule, so it draws the raised button face inside a menu. The GTK 4 sheet already strips that face with `popover modelbutton check, popover modelbutton radio, popover.background modelbutton check, popover.background modelbutton radio`. `docs/invariants.md`'s GTK 3 sheet row already promises faces that are "boxless in menus".

I measured this live with PyGObject and GTK 3 under `GTK_THEME=org.macos8.desktop`, through a `Gtk.StyleContext` set to a `Gtk.WidgetPath` of named nodes:
- `window > menu > menuitem > check` has a transparent background and a 0 margin.
- `window > popover > modelbutton > check` has background `rgb(221,221,221)` (the raised face) and a 4px left margin.
- `window > popover > modelbutton > radio` has background `rgb(255,255,255)` (the radio face) and a 4px left margin.

**Design (decided; do not widen).**
- In `gtk-3.0/gtk.css`, extend the selector list of the existing `menu menuitem check, menu menuitem radio` rule with `popover modelbutton check, popover modelbutton radio`. Leave its four declarations unchanged (`margin: 0; background-color: transparent; border-color: transparent; box-shadow: none;`).
- `check:checked` and `radio:checked` keep supplying the shipped `assets/checkmark.svg` and `assets/bullet.svg` glyphs, so a checked row shows the bare glyph. GTK 3's popover node is `popover.background`, which `popover` already matches, so no `.background` selector is needed.
- In the header comment's popover sentence ("A popover menu row (modelbutton) takes the same #CCCCFF highlight …"), add that a popover row's check and radio show the bare glyph, as a menu row's do.
- Out of scope:
  - GTK 3 popover row padding and min-height. The only open-menu reference, `desktop_archiveorg8.6hd.png`, is scaled: its Apple-menu rows are 14px apart and its text is antialiased, so it cannot ground a row metric.
  - GTK 3 popover submenu arrows (`modelbutton arrow.right`/`.left`).
  - Any GTK 4 change.
- No new asset, colour or metric is added, so the Makefile, `SHIPPED_FILES`, `STAGING_PATHS` and the README counts do not change.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: the selector list and the header sentence.
- `tests/test_gtk_theme.py`: in `TestGtkTheme.test_menu_check_and_radio_are_boxless`, add `"popover modelbutton check"` and `"popover modelbutton radio"` to the selector tuple. Each is checked against the existing `MENU_CHECK` from `tests/support/gtk_theme_spec.py`.
- `docs/invariants.md`: add one row at the end of the `## gtk` section.
  - Guarantee: the GTK 3 sheet draws a popover menu row's (`popover modelbutton`) check and radio without the raised face, margin or bevel, as it does for a `menu menuitem` row.
  - Test: `tests/test_gtk_theme.py::TestGtkTheme::test_menu_check_and_radio_are_boxless`.
  - Provenance: no reference screenshot shows a GTK popover. The rule reuses the existing boxless menu-check declarations and adds no colour or metric.

**Acceptance criteria.**
- The GTK 3 sheet's boxless rule names both popover selectors with the unchanged `MENU_CHECK` declarations.
- Removing either popover selector, or changing any of the four declarations, fails `test_menu_check_and_radio_are_boxless`.
- A live `Gtk.StyleContext` probe of `window > popover > modelbutton > check` reports a transparent background and a 0 margin.
- `test_icon_sources_point_at_shipped_assets`, `test_only_palette_hex_literals` and the rest of `tests/test_gtk_theme.py` still pass. `tests/invariants.py` accepts the new row, and `make check` is green.

### Platinum GTK spinners: draw a running `GtkSpinner` and hide a stopped one in GTK 3 and GTK 4 (planned 2026-10-24 by the plan role; independent of the waiting GTK 3 popover-row highlight plan) — done 2026-10-24 by the feature role

**Goal.** Neither GTK sheet names `spinner` (grep finds no `spinner` and no `@keyframes` in `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` or `gtk-4.0/gtk.css`). The stock spinner rules live in Adwaita's `gtk-contained.css` (GTK 3) and in GTK 4's `Default-light.css`. Our standalone sheets never load either file, so a `GtkSpinner` loses them.

I measured this live with PyGObject under `GTK_THEME=org.macos8.desktop`, with `XDG_DATA_HOME` pointing at a temp dir that holds a `themes/org.macos8.desktop` symlink to the absolute `theme/gtk/org.macos8.desktop` path.
- GTK 4: a started 16x16 `Gtk.Spinner` in a presented `Gtk.Window` renders nothing. Its `Gtk.WidgetPaintable` snapshot `to_node()` is `None`. With the GTK 4 rules below appended to a `cp -rL` copy of the theme, it renders a `GskMaskNode` with 122 non-transparent pixels. Under `GTK_THEME=Adwaita` it renders 112.
- GTK 3: a stopped spinner's `get_style_context().get_property("opacity", state)` is `1.0` today. With the GTK 3 rules appended it is `0.0`, and a started (`CHECKED`) spinner stays at `1.0`. GTK 3 pixels cannot be measured on this machine, so only the CSS side of GTK 3 is verified.

**Design (decided; do not widen).** Both sheets copy the stock spinner rules. The only difference is the transform property inside the keyframes, which the two toolkits spell differently.
- `gtk-3.0/gtk.css`: directly after the `levelbar.vertical block` rule, add:
  ```css
  @keyframes spin { to { -gtk-icon-transform: rotate(1turn); } }
  spinner { background: none; opacity: 0; -gtk-icon-source: -gtk-icontheme("process-working-symbolic"); }
  spinner:checked { opacity: 1; animation: spin 1s linear infinite; }
  spinner:checked:disabled { opacity: 0.5; }
  ```
- `gtk-4.0/gtk.css`: directly after the `levelbar.vertical > trough > block` rule, add the same four rules, except that the keyframe reads `to { transform: rotate(1turn); }`. That is GTK 4's own spelling in `Default-light.css`.
- Format the rules multi-line, as in the rest of each sheet. Values stay exactly as above.
- The icon comes from the user's icon theme via the GTK-required `process-working-symbolic` name. Our icon theme does not ship that name, so it resolves through the `Inherits` chain (Breeze on KDE). No new asset is added, so the Makefile, `SHIPPED_FILES`, `STAGING_PATHS` and the README asset counts do not change.
- Out of scope:
  - A Platinum spinner asset, such as a GTK copy of the desktop theme's `widgets/busywidget.svg` ring. That would need a new shipped asset plus install and uninstall changes.
  - A `spinner:backdrop` colour.
- No reference screenshot shows a GTK spinner or any busy indicator other than the watch cursor. The rules add no colour or metric. Say so in each sheet's header comment, in one sentence: a spinner shows the icon theme's `process-working-symbolic` while it runs and is hidden while stopped.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`: the rules and the header sentence.
- `tests/support/gtk_theme_spec.py`:
  - Add a `SPINNER_RULES` dict mapping `"spinner"`, `"spinner:checked"` and `"spinner:checked:disabled"` to the declarations above. Values are whitespace-normalised, as `parse_css` stores them, e.g. `"-gtk-icon-source": '-gtk-icontheme("process-working-symbolic")'`.
  - Add a `GtkSheetRuleCases.assert_spinner(self, transform)` helper. It calls `assert_rule` for each `SPINNER_RULES` entry. It also asserts that `gtk_css.strip_comments(self.css)` matches `@keyframes\s+spin\s*\{\s*to\s*\{\s*<transform>\s*:\s*rotate\(1turn\)\s*;?\s*\}\s*\}`, with the property name passed through `re.escape`.
  - Check the regex against the raw text, not `self.rules`: `parse_css` files a nested keyframe block under a bare `to` selector.
  - Add "spinner" to the module docstring's list of shared assertions.
- `tests/test_gtk_theme.py`: add `TestGtkTheme.test_spinner`, which calls `self.assert_spinner("-gtk-icon-transform")`.
- `tests/test_gtk4_theme.py`: add `TestGtk4Theme.test_spinner`, which calls `self.assert_spinner("transform")`.
- `docs/invariants.md`: add one row at the end of the `## gtk` section.
  - Guarantee: the GTK 3 and GTK 4 sheets show a running spinner as the icon theme's `process-working-symbolic`, rotating once per second, and hide a stopped one.
  - Tests: both `test_spinner` methods.
  - Provenance: no reference screenshot shows a GTK spinner. The icon name, states and animation are GTK-required, copied from the toolkits' stock sheets, and add no colour or metric.

**Acceptance criteria.**
- Both sheets carry the four rules exactly as described, with each toolkit's own keyframe property.
- Each of these fails the matching `test_spinner`:
  - deleting any of the four rules;
  - changing `opacity: 0` or the `-gtk-icon-source` value;
  - spelling the GTK 3 keyframe with `transform`, or the GTK 4 keyframe with `-gtk-icon-transform`.
- `test_stands_alone` (GTK 4), `test_icon_sources_point_at_shipped_assets` (GTK 3), `test_only_palette_hex_literals` and the rest of both GTK suites still pass. `tests/invariants.py` accepts the new row, and `make check` is green.

### Platinum GTK 3 popover menus: paint the hovered and selected popover menu row with the Platinum highlight (planned 2026-10-24 by the plan role; independent of the waiting GTK 4 menu-button arrow plan) — done 2026-10-24 by the feature role

**Goal.** A GTK 3 popover menu, such as the hamburger menu of a `Gtk.MenuButton` built with `Gtk.Popover.new_from_model`, gives no feedback when the pointer moves over a row. The GTK 3 sheet styles `menuitem:hover` but names no `modelbutton`, and those rows are `GtkModelButton` widgets (CSS node `modelbutton.flat`). The stock `modelbutton.flat:hover` rule is in Adwaita's `gtk-contained.css`, which our standalone sheet never loads. The GTK 4 sheet already has `popover.menu modelbutton:hover, popover.menu modelbutton:selected` with `#CCCCFF`.

I measured this live with PyGObject under `GTK_THEME=org.macos8.desktop`, with `XDG_DATA_HOME` pointing at a temp dir that holds a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`. The test popover was built from a `Gio.Menu` with one item and one `append_submenu` row, on a `Gtk.MenuButton` in a shown `Gtk.Window`. Each row's `get_style_context().get_property("background-color", Gtk.StateFlags.PRELIGHT)` returned transparent `(0,0,0,0)`, where Adwaita gives white. Then I appended the rule below to a `cp -rL` copy of the theme and re-ran the script. The same query then returned `(0.8, 0.8, 1.0, 1.0)`, which is `#CCCCFF`, and the row text stayed black.

**Design (decided; do not widen).**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: directly after the `menuitem:hover, .menuitem:hover` rule, add
  `popover modelbutton:hover, popover modelbutton:selected { background-color: #CCCCFF; }`
  This is the GTK 4 sheet's state pair, scoped by `popover` instead of `popover.menu`. GTK 3 puts `.menu` on popovers built from a model, but a hand-built `Gtk.Popover` holding model buttons does not have it.
- Out of scope:
  - The popover row's submenu `arrow.right`/`arrow.left`. GTK 3 draws it as a gadget, not a widget. `Gdk.pixbuf_get_from_window` returned all-dark garbage under both the Wayland and X11 backends, and `Gtk.Widget.draw` needs `gi-cairo`, which is not installed. So no run could confirm what it draws.
  - Popover row check/radio glyphs, row padding and min-height. Our rows measure 0px padding and 0 min-height, against Adwaita's 5px and 26px.
  - Disabled-row text.
- No reference screenshot shows a GTK popover. The fill is the reference-grounded `#CCCCFF` row highlight that `menuitem:hover` and `widgets/viewitem.svg` already use. Say so in the provenance.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: the rule above. The header comment also gets one sentence saying that a popover menu row (`modelbutton`) takes the same `#CCCCFF` highlight as a menu row when hovered or selected.
- `tests/test_gtk_theme.py`: in `TestGtkTheme.test_menu`, extend the hover loop over `("menuitem:hover", ".menuitem:hover")` with `"popover modelbutton:hover"` and `"popover modelbutton:selected"`. Each still calls `self.assert_rule(selector, {"background-color": SELECTION})`.
- `docs/invariants.md`: add a new row at the end of the `## gtk` section.
  - Guarantee: the GTK 3 sheet fills a hovered or selected popover menu row (`popover modelbutton`) with `#CCCCFF`.
  - Test: `tests/test_gtk_theme.py::TestGtkTheme::test_menu`.
  - Provenance: no reference screenshot shows a GTK popover. The fill reuses the reference-grounded menu-row highlight, and the node name and states are GTK-required.

**Acceptance criteria.**
- The rule exists exactly as described, and the GTK 4 sheet is unchanged.
- Each of these fails `test_menu`: removing the rule, dropping either state from its selector, or changing its colour.
- `test_icon_sources_point_at_shipped_assets` and the rest of the GTK 3 suite still pass, `tests/invariants.py` accepts the new row, and `make check` is green.

### Platinum GTK 4 menu-button arrows: draw the shipped down and up triangles on GTK 4 menu buttons (planned 2026-10-24 by the plan role; independent of the waiting GTK submenu-arrow plan) — done 2026-10-24 by the feature role

**Goal.** The GTK 4 sheet does not style a `Gtk.MenuButton`'s arrow. The stock rules that give it an icon are in `Default-light.css`, which our standalone sheet never loads, so a menu button with no icon or label of its own shows an empty face. Measured live with PyGObject under `GTK_THEME=org.macos8.desktop` (with `XDG_DATA_HOME` pointing at a temp dir holding a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`): a bare `Gtk.MenuButton()` parented in a presented `Gtk.Window` maps `menubutton > button > arrow.down` at 16x16, but snapshotting that arrow through `Gtk.WidgetPaintable` gives no render node, so nothing is drawn. Under `GTK_THEME=Adwaita` the same arrow renders a dark triangle. Stock `Default-light.css` (`gresource extract /usr/lib/x86_64-linux-gnu/libgtk-4.so.1 /org/gtk/libgtk/theme/Default/Default-light.css`) has `menubutton arrow { min-height: 16px; min-width: 16px; }` and one `-gtk-icon-source: -gtk-icontheme(...)` rule per direction class: `.none` uses `open-menu-symbolic`, `.down` `pan-down-symbolic`, `.up` `pan-up-symbolic`, `.left` `pan-start-symbolic` and `.right` `pan-end-symbolic`.

I appended the two rules below to a `cp -rL` copy of the theme and re-ran the snapshot. The arrow then renders a 16x16 texture, with dark opaque pixels (every channel below 170) filling the shipped triangles. For the default direction (down), they fill x=4..11, y=5..9, widest at the top. After `set_direction(Gtk.ArrowType.UP)` they fill x=4..11, y=6..10, widest at the bottom. The arrow stayed 16x16 without a `min-width`/`min-height` rule, so the plan adds none.

**Design (decided; do not widen).**
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: directly after the `combobox arrow, dropdown arrow` rule, add
  - `menubutton arrow.down { -gtk-icon-source: url("../assets/arrow-down.svg"); }`
  - `menubutton arrow.up { -gtk-icon-source: url("../assets/arrow-up.svg"); }`
- Both assets already ship, and their triangles reuse the desktop theme's pinned `widgets/arrows.svg` shapes, as the combo box arrow's does. So this plan adds no asset, Makefile, fixture or README-count change.
- Out of scope:
  - `arrow.none` (the hamburger `open-menu-symbolic` glyph) and `arrow.left`/`arrow.right`: no shipped asset fits, and the down direction is GTK's default.
  - The GTK 3 menu button: GTK 3 builds its arrow as a `GtkImage` from the icon theme, not a CSS `arrow` node.
  - Hover and disabled glyph colours, and the menu button's face.
- No reference screenshot shows a GTK menu button. The reference's pop-up menus show a double arrow (`TestComboBoxReference`). So the single triangle is the same KDE-required shape the combo box and dropdown arrows already use. Say so in the provenance.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: the two rules above. The header comment's sentence "The combo box and dropdown arrows load from the shared assets/arrow-down.svg ..." also names the menu button's down arrow, plus its up arrow from `assets/arrow-up.svg`.
- `tests/support/gtk_theme_spec.py`: next to `COMBO_ARROW`, add `MENUBUTTON_ARROWS = {"menubutton arrow.down": {"-gtk-icon-source": 'url("../assets/arrow-down.svg")'}, "menubutton arrow.up": {"-gtk-icon-source": 'url("../assets/arrow-up.svg")'}}`, with a one-line comment.
- `tests/test_gtk4_theme.py`: add `TestGtk4Theme.test_menubutton_arrows`, which imports `MENUBUTTON_ARROWS` and calls `self.assert_rule(selector, expected)` for each entry. Both URLs are already in the `test_stands_alone` URL set, so that set stays unchanged.
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section.
  - Guarantee: the GTK 4 sheet draws a menu button's down and up arrows from the shipped `arrow-down.svg` and `arrow-up.svg` triangles.
  - Test: `tests/test_gtk4_theme.py::TestGtk4Theme::test_menubutton_arrows`.
  - Provenance: no reference screenshot shows a GTK menu button. The triangles reuse the desktop theme's pinned `widgets/arrows.svg` shapes, as the combo box arrow does. The node and direction-class names are GTK-required.

**Acceptance criteria.**
- Both rules exist exactly as described, and the GTK 3 sheet is unchanged.
- Each of these fails `test_menubutton_arrows`: removing either rule, renaming either selector, or swapping either URL.
- `test_only_palette_hex_literals`, `test_no_universal_selector` and `test_stands_alone` still pass in the GTK 4 suite, `tests/invariants.py` accepts the new row, and `make check` is green.

### Platinum GTK submenu arrows: draw the reference's solid black submenu triangle on GTK 3 and GTK 4 menu rows that open a submenu (planned 2026-10-24 by the plan role; independent of the waiting GTK calendar plan) — done 2026-10-24 by the feature role

**Goal.** Neither standalone GTK sheet styles a menu row's submenu arrow, and the stock rules that give it an icon and a size are in sheets we never load. So a menu row that opens a submenu shows no arrow. Measured live with PyGObject under `GTK_THEME=org.macos8.desktop` (with `XDG_DATA_HOME` pointing at a temp dir holding a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`):
- GTK 3: a style context on the path `menu > menuitem > arrow` resolves `min-width` and `min-height` to `0`, so the arrow has no size. Under `GTK_THEME=Adwaita` both are `16`. Stock `gtk-contained.css` has `menu menuitem arrow { min-height: 16px; min-width: 16px; }` and `-gtk-icon-source: -gtk-icontheme("pan-end-symbolic")` for `:dir(ltr)`.
- GTK 4: a `Gtk.PopoverMenu` built from a `Gio.Menu` with one `append_submenu` row maps that row's `modelbutton > arrow.right` at 16x16. But snapshotting it through `Gtk.WidgetPaintable` gives no render node at all, so nothing is drawn. Stock `Default-light.css` has `modelbutton.flat arrow.right { -gtk-icon-source: -gtk-icontheme("go-next-symbolic"); }`.
- The reference's open Apple menu (`desktop_archiveorg8.6hd.png`) draws a solid black 5x9 right triangle on each submenu row. The icon theme already ships that triangle as `theme/icons/org.macos8.desktop/16x16/actions/go-next-symbolic.svg` (path `M 6,3 L 6,11 L 10,7 Z`, fill `#000000`), and `tests/test_icon_arrow_reference.py::TestSubmenuArrowReference` pins it to the reference. The GTK assets' `arrow-right.svg` (`M 5,4 L 5,12 L 11,8 Z`, the disclosure arrow) is a different shape, so do not reuse it here.

With the rules below and a scratch `assets/submenu-arrow.svg` (that same path) appended to a `cp -rL` copy of the theme:
- GTK 3: the `menu > menuitem > arrow` context resolves `min-width` and `min-height` to `16`.
- GTK 4: the arrow snapshot renders a 16x16 texture with opaque dark pixels (every channel below 170) inside x=6..9, y=3..9.

**Design (decided; do not widen).**
- New asset `theme/gtk/org.macos8.desktop/assets/submenu-arrow.svg`: a 16x16 root (`width="16" height="16" viewBox="0 0 16 16"`, root element first, no `<?xml` prolog needed) holding one `<path d="M 6,3 L 6,11 L 10,7 Z" fill="#000000"/>`. Put its comment inside the root, as `arrow-right.svg` does. The comment says the path copies the icon theme's reference-pinned `16x16/actions/go-next-symbolic.svg` triangle (the open Apple menu's 5x9 submenu arrow) and names the test that pins the copy. GTK loads it directly, so it does not depend on which icon theme the user selected.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: directly after the `menu menuitem check, menu menuitem radio` rule, add `menu menuitem arrow { min-width: 16px; min-height: 16px; -gtk-icon-source: url("../assets/submenu-arrow.svg"); }`.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: directly after the `popover modelbutton check, popover modelbutton radio, popover.background modelbutton check, popover.background modelbutton radio` rule, add `popover.menu modelbutton > arrow.right { -gtk-icon-source: url("../assets/submenu-arrow.svg"); }`. GTK 4 already gives the node its 16px size.
- Out of scope: margins between label and arrow, the GTK 4 sliding-submenu back arrow (`arrow.left`, which the reference never shows), right-to-left mirroring, `menubutton arrow`, and hover or disabled arrow colours. The arrow stays black on the `#CCCCFF` hover fill, as in the reference.

**Files touched.**
- The new asset, and both sheets' rules above. Add one sentence to each sheet's header comment: the submenu arrow loads the shared `assets/submenu-arrow.svg`, the icon theme's reference-grounded submenu triangle.
- `tests/support/gtk_theme_spec.py`:
  - Add `SUBMENU_ARROW = {"-gtk-icon-source": 'url("../assets/submenu-arrow.svg")'}` next to `EXPANDER_EXPANDED`.
  - Add `assert_submenu_arrow(self, selectors, sized)` to `GtkSheetRuleCases`, next to `assert_expander_arrows`. Each selector must match `SUBMENU_ARROW`. When `sized` is true, it must also match `min-width: 16px` and `min-height: 16px`.
  - Add the submenu arrow to the docstrings' list of assertions that take the suites' own selectors.
- `tests/test_gtk_theme.py`:
  - Add `TestGtkTheme.test_submenu_arrow`, calling `self.assert_submenu_arrow(("menu menuitem arrow",), sized=True)`.
  - Add `'"../assets/submenu-arrow.svg"'` to `test_icon_sources_point_at_shipped_assets`.
  - Add `SUBMENU_ARROW_SVG = THEME_DIR / "assets" / "submenu-arrow.svg"` beside `ARROW_RIGHT`, and include it in the `TestArrowGlyphs` stand-alone, root-first, 16px-canvas and black-fill checks.
  - Add `TestArrowGlyphs.test_submenu_arrow_copies_the_icon_theme_triangle`. It parses the new asset and `theme/icons/org.macos8.desktop/16x16/actions/go-next-symbolic.svg`, and asserts that each has exactly one `path`, with equal `d` and `fill`.
- `tests/test_gtk4_theme.py`:
  - Add `TestGtk4Theme.test_submenu_arrow`, calling `self.assert_submenu_arrow(("popover.menu modelbutton > arrow.right",), sized=False)`.
  - Add the new URL to the `test_stands_alone` URL set.
- Install wiring for the twelfth GTK file:
  - `Makefile` `install_gtk`: add the staging `install` line, the commit `mv` line and the trap's staging path for `assets/submenu-arrow.svg`, written the same way as `arrow-right.svg`.
  - `Makefile` `_uninstall`: add the file and its `.submenu-arrow.svg.staging` to the GTK `rm -f`.
  - `tests/support/gtk_fixtures.py`: add the file to `SHIPPED_FILES`.
  - `tests/test_gtk_install.py`: add `"assets/submenu-arrow.svg": "assets/.submenu-arrow.svg.staging"` to `STAGING_PATHS`.
- `README.md`:
  - "the eight shared check, radio, combo box, menu arrow, disclosure arrow and title-button box assets" becomes nine, naming the submenu arrow.
  - Both "eleven" GTK file counts become "twelve".
- `docs/invariants.md`:
  - The GTK install row's "eleven GTK theme files" becomes "twelve".
  - Add a new `## gtk` row at the end of the gtk section. Guarantee: both GTK sheets draw a submenu row's arrow from the shipped `submenu-arrow.svg`, whose path is the icon theme's reference-pinned submenu triangle, and GTK 3 sizes it 16x16. Tests: the two `test_submenu_arrow` tests and `TestArrowGlyphs.test_submenu_arrow_copies_the_icon_theme_triangle`. Provenance: the 16px canvas and the node names are GTK-required, and the triangle comes from `TestSubmenuArrowReference`.

**Acceptance criteria.**
- The asset and both rules exist exactly as described, and `make install-gtk` installs the asset beside the other assets, which `make uninstall` removes.
- Each of these fails a test: removing either rule, renaming its selector or its URL, dropping either GTK 3 min size, or changing the asset's path or fill (or the icon theme's 16x16 `go-next-symbolic.svg` path alone).
- `test_only_palette_hex_literals` and `test_no_universal_selector` still pass in both suites, the GTK install tests pass with the new file, `tests/invariants.py` accepts the edited rows, and `make check` is green.

### Platinum GTK calendars: fill the selected day with the selection lavender and grey the other months' days (planned 2026-10-24 by the plan role; independent of the waiting GTK links plan) — done 2026-10-24 by the feature role

**Goal.** Neither standalone GTK sheet styles `calendar`. So a `Gtk.Calendar` draws its selected day with no fill, and days from the previous and next months look the same as the current month's. Measured live with PyGObject under `GTK_THEME=org.macos8.desktop` (with `XDG_DATA_HOME` pointing at a temp dir holding a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`), with the calendar inside a `Gtk.Window`:
- GTK 3: the calendar's style context resolves `background-color` to `rgba(0,0,0,0)` and colour to `rgb(0,0,0)` for `SELECTED` (and for `SELECTED|FOCUSED`). The colour for `INCONSISTENT` is also `rgb(0,0,0)`. GTK 3 draws other-month days in the inconsistent state, which is `calendar:indeterminate` in CSS.
- GTK 4: the selected `label.day-number` resolves to `rgb(0,0,0)`, and a texture rendered from it has a transparent `(0,0,0,0)` corner pixel. An `other-month` day label resolves to `rgb(0,0,0)`.
- Stock Adwaita, for comparison: a blue fill with white text, and other-month days at 30% alpha.

With the rules below appended to scratch copies of both sheets (`cp -rL`), the same checks give this:
- GTK 3: `SELECTED` is `rgb(204,204,255)` behind `rgb(0,0,0)` text, and `INCONSISTENT` is `rgb(136,136,136)`.
- GTK 4: the selected day's rendered corner pixel is `(204,204,255,255)` and its text is `rgb(0,0,0)`. The other-month label is `rgb(136,136,136)`.
- A plain `Gtk.Label` stays `rgb(0,0,0)`.

**Design (decided; do not widen).**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: append at the end of the sheet `calendar:selected { background-color: #CCCCFF; color: #000000; }` and `calendar:indeterminate { color: #888888; }`. Both outrank the sheet's `.view` rule by specificity, so their order relative to it does not matter.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: append at the end of the sheet `calendar > grid > label.day-number:selected { background-color: #CCCCFF; color: #000000; }` and `calendar > grid > label.day-number.other-month { color: #888888; }`.
- If the links plan has landed by then, still append these rules after its rules. Out of scope: the calendar border, the header and arrow buttons, the day-name and week-number `.highlight` colour, the GTK 4 today marker, day padding, `:backdrop`, and a disabled calendar. No new hex literals are needed: `#CCCCFF`, `#000000` and `#888888` are already in both palette sets.

**Files touched.**
- Both sheets get the rules above. Add one sentence to each header comment: a calendar's selected day reuses the row selection fill `#CCCCFF` with black text, and other months' days use the disabled-text `ForegroundInactive` grey `#888888`; no reference screenshot shows a calendar, and the node names and states are GTK-required.
- `tests/support/gtk_theme_spec.py`:
  - Next to `TEXT_SELECTION`, add `CALENDAR_SELECTED_DAY = {"background-color": SELECTION, "color": BLACK}`, with a one-line comment that it reuses the row selection fill.
  - Add `assert_calendar(self, selected, other_month)` to `GtkSheetRuleCases`, next to `assert_rubberband`. Each `selected` selector must match `CALENDAR_SELECTED_DAY`. Each `other_month` selector must match `DISABLED_TEXT`. Like `assert_disabled_text`, it re-derives `DISABLED_TEXT["color"]` from `load_scheme().get("Colors:Button", "ForegroundInactive")` with `hex_colour`. Move that re-derivation into one private helper that both methods call, rather than copying it.
  - Add calendar to the list of assertions that take the suites' own selectors, in the module docstring and in the `GtkSheetRuleCases` docstring.
- `tests/test_gtk_theme.py`: add `TestGtkTheme.test_calendar`, calling `self.assert_calendar(("calendar:selected",), ("calendar:indeterminate",))`.
- `tests/test_gtk4_theme.py`: add `TestGtk4Theme.test_calendar`, calling `self.assert_calendar(("calendar > grid > label.day-number:selected",), ("calendar > grid > label.day-number.other-month",))`.
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section.
  - Guarantee: both GTK sheets fill a calendar's selected day with `#CCCCFF` behind black text, and colour other months' days with the colour scheme's `ForegroundInactive` grey `#888888`.
  - Tests: the two `test_calendar` tests.
  - Provenance exception: no reference screenshot shows a calendar. The fill reuses the reference-grounded row selection, the grey copies the disabled-text `ForegroundInactive` role, and the node names and states are GTK-required.

**Acceptance criteria.**
- Both sheets have the two rules above, with exactly the declarations listed.
- Each of these fails that sheet's `test_calendar`: removing either rule, renaming its selector, or changing its fill or a colour. Changing `[Colors:Button] ForegroundInactive` in the colour scheme alone fails both suites' `test_calendar`, as well as `test_disabled_text`.
- `test_only_palette_hex_literals` and `test_no_universal_selector` still pass in both suites, `tests/invariants.py` accepts the new row, and `make check` is green.

### Platinum GTK links: colour link text with the scheme's link blue and visited purple, and drop the GTK 3 link-button face (planned 2026-10-24 by the plan role; independent of the waiting GTK disabled-text plan) — done 2026-10-24 by the feature role

**Goal.** Neither standalone GTK sheet styles links. Measured live with PyGObject under `GTK_THEME=org.macos8.desktop` (with `XDG_DATA_HOME` pointing at a temp dir holding a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`), inside a `Gtk.Window`: a GTK 3 and a GTK 4 `Gtk.LinkButton` both resolve their text to `rgb(0,0,0)`, the same as a plain label. The GTK 3 link button also gets the full Platinum push-button face from the `button` rule: `background-color` `rgb(221,221,221)` and a 1px solid border. So a link looks like ordinary text or like a button. Stock Adwaita colours links `rgb(27,106,203)` (visited `rgb(21,83,158)`) and draws no face. The KDE side already has link colours: the colour scheme's `ForegroundLink=0,0,238` and `ForegroundVisited=85,26,139`, which Kvantum copies as `link.color=#0000EE` and `link.visited.color=#551A8B`. `COLOR_ROLES` in `tests/support/kvantum_config_spec.py` pins those two to `("Window", "ForegroundLink")` and `("Window", "ForegroundVisited")`. With the rules below appended to scratch copies of both sheets, the same check gives this. GTK 3 link button: `background-color` and `border-top-color` `rgba(0,0,0,0)` when normal and when hovered and active; label `rgb(0,0,238)`, then `rgb(85,26,139)` after `set_visited(True)`. GTK 3 `Gtk.Label` with `<a>` markup: `rgb(0,0,238)` for the `LINK` state and `rgb(85,26,139)` for `VISITED`. GTK 4 link button label: `rgb(0,0,238)`, then `rgb(85,26,139)` once visited. Plain labels and plain-button labels stay `rgb(0,0,0)`, and a plain GTK 3 button keeps its `rgb(221,221,221)` face. The GTK 4 `link` node inside a label is not a widget, so it was not measured live; the rule test pins it.

**Design (decided; do not widen).**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: append at the end of the sheet:
  `button:link, button:visited { background-color: transparent; background-image: none; border-color: transparent; box-shadow: none; }`,
  `label:link, button:link > label { color: #0000EE; text-decoration-line: underline; }` and
  `label:visited, button:visited > label { color: #551A8B; }`.
  These come after `button`, `button:hover` and `button:active, button:checked`, and have the same specificity, so they win by order.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: append at the end of the sheet:
  `button.link { background-color: transparent; background-image: none; border-color: transparent; box-shadow: none; }`,
  `link, button.link > label { color: #0000EE; text-decoration: underline; }` and
  `link:visited, button.link:visited > label { color: #551A8B; }`.
- If the disabled-text plan has landed by then, still append these rules after its rule. Out of scope: greying an insensitive link, hover and active link colours, `:selected` links, `:backdrop`, and the Firefox sheet. Do not use `*:link`: each suite's `test_no_universal_selector` forbids `*`.
- New hex literals: `#0000EE` and `#551A8B`.

**Files touched.**
- Both sheets: the rules above. Add one sentence to each header comment: links use the colour scheme's `ForegroundLink` blue `#0000EE` and `ForegroundVisited` purple `#551A8B` (Kvantum's link colours too), and a link button draws no button face; no reference screenshot shows a GTK link, and the node names and `:link`/`:visited` states are GTK-required.
- `tests/support/gtk_theme_spec.py`: add `LINK = "#0000EE"` and `VISITED_LINK = "#551A8B"` next to `ETCH_DARK`, with a comment naming the scheme roles. Add the rule dicts `LINK_BUTTON = {"background-color": "transparent", "background-image": "none", "border-color": "transparent", "box-shadow": "none"}`, `LINK_TEXT = {"color": LINK}` and `VISITED_TEXT = {"color": VISITED_LINK}`. The underline is not in `LINK_TEXT` because the property name differs per toolkit. Then add an `assert_links(self, button, link, visited, underline)` method in `GtkSheetRuleCases` next to `assert_rubberband`:
  - `button` is the link-button selectors. Each must match `LINK_BUTTON`.
  - `link` is the link-text selectors. Each must match `{**LINK_TEXT, **underline}`.
  - `visited` is the visited-text selectors. Each must match `VISITED_TEXT`.
  - It re-derives both colours from the scheme: `hex_colour` of the `int` parts of `load_scheme().get("Colors:Window", "ForegroundLink")` (and of `"ForegroundVisited"`) must equal `LINK` (and `VISITED_LINK`). `load_scheme` comes from `support.colorscheme_fixtures`.
  - Mention the link assertion in the module docstring's list of assertions that take the suites' own selectors.
- `tests/test_gtk_theme.py`: add `LINK` and `VISITED_LINK` to the `test_only_palette_hex_literals` palette set. Add `TestGtkTheme.test_links`, which calls `self.assert_links(("button:link", "button:visited"), ("label:link", "button:link > label"), ("label:visited", "button:visited > label"), {"text-decoration-line": "underline"})`.
- `tests/test_gtk4_theme.py`: add the same two constants to its `test_only_palette_hex_literals` set. Add `TestGtk4Theme.test_links`, which calls `self.assert_links(("button.link",), ("link", "button.link > label"), ("link:visited", "button.link:visited > label"), {"text-decoration": "underline"})`.
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section. Guarantee: both GTK sheets colour link text with the colour scheme's `ForegroundLink` `#0000EE` (underlined) and visited links with `ForegroundVisited` `#551A8B`, and draw link buttons without a face. Tests: the two `test_links` tests. Provenance exception: no reference screenshot shows a link; the colours copy the colour scheme's link roles (Kvantum's link colours too), and the node names and states are GTK-required.

**Acceptance criteria.**
- Both sheets have the three rules above, with exactly the declarations listed.
- Each of these fails that sheet's `test_links`: removing any of the three rules, dropping one of their selectors, or changing a colour or the underline. Changing `[Colors:Window] ForegroundLink` or `ForegroundVisited` in the colour scheme alone fails both suites' `test_links`.
- `test_only_palette_hex_literals` and `test_no_universal_selector` still pass in both suites, `tests/invariants.py` accepts the new row, and `make check` is green.

### Platinum GTK disabled text: grey the labels and entry text of insensitive widgets (planned 2026-10-24 by the plan role; independent of the waiting GTK rubberband plan) — done 2026-10-24 by the feature role

**Goal.** Neither standalone GTK sheet greys the text of an insensitive widget, so a disabled button, check box, menu item, entry or spin button reads exactly like an enabled one. Measured live with PyGObject under `GTK_THEME=org.macos8.desktop` (with `XDG_DATA_HOME` pointing at a temp dir holding a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`): after `set_sensitive(False)`, a GTK 3 `Gtk.Label`, `Gtk.Button`, `Gtk.Entry`, `Gtk.CheckButton` and `Gtk.SpinButton` all resolve `get_color()` to `rgb(0,0,0)`, and in GTK 4 the `Label` child of a `Gtk.Button` or `Gtk.CheckButton`, and the `Text` child of a `Gtk.Entry` or `Gtk.SpinButton`, are also `rgb(0,0,0)`. Stock Adwaita greys them (`rgb(146,149,149)`). The KDE side already greys disabled text with `#888888`: the colour scheme's `ForegroundInactive=136,136,136` and Kvantum's `disabled.text.color`, which `COLOR_ROLES` in `tests/support/kvantum_config_spec.py` pins to `("Button", "ForegroundInactive")`. With the rules below appended to scratch copies of both sheets, the same check gives `rgb(136,136,136)` for each of those labels and text nodes (GTK 3 also greys a disabled `Gtk.MenuBar` item's label) and `rgb(0,0,0)` once they are sensitive again.

**Design (decided; do not widen).**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: append `label:disabled, entry:disabled, spinbutton:disabled { color: #888888; }` at the end of the sheet. Insensitivity reaches child nodes, so `label:disabled` covers the labels of buttons, check and radio buttons and menu items.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: append `label:disabled, text:disabled { color: #888888; }` at the end of the sheet. `text` is the editable node inside GTK 4 entries and spin buttons.
- Colour only. Do not use `*:disabled`: it would also reach `switch image`, whose transparent colour hides the switch glyph. Out of scope: disabled faces, borders and glyph assets (a URL icon's fill is fixed, as the GTK 3 header comment already says), and `:backdrop`.
- No new hex literal: `#888888` is already in both palettes as `ETCH_DARK`.

**Files touched.**
- Both sheets: the rule above. Add one sentence to each header comment: an insensitive widget's label and entry text use the colour scheme's `ForegroundInactive` grey `#888888`, which Kvantum's disabled text also uses; no reference screenshot shows a disabled GTK widget, and the node names and `:disabled` state are GTK-required.
- `tests/support/gtk_theme_spec.py`: add `DISABLED_TEXT = {"color": ETCH_DARK}` with a short comment, and an `assert_disabled_text(self, selectors)` method in `GtkSheetRuleCases` next to `assert_view_background`. It calls `assert_rule` for each selector. It also re-derives the grey: `hex_colour` of the `int` parts of `load_scheme().get("Colors:Button", "ForegroundInactive")` (`load_scheme` from `support.colorscheme_fixtures`, `hex_colour` from `support.platinum_palette`) must equal `DISABLED_TEXT["color"]`. Mention the disabled-text assertion in the class docstring's list of assertions that take the suite's own selectors.
- `tests/test_gtk_theme.py`: `TestGtkTheme.test_disabled_text` calls `self.assert_disabled_text(("label:disabled", "entry:disabled", "spinbutton:disabled"))`.
- `tests/test_gtk4_theme.py`: `TestGtk4Theme.test_disabled_text` calls `self.assert_disabled_text(("label:disabled", "text:disabled"))`.
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section. Guarantee: both GTK sheets colour an insensitive widget's labels and entry text with the colour scheme's `ForegroundInactive` grey `#888888`. Tests: the two `test_disabled_text` tests. Provenance exception: no reference screenshot shows a disabled GTK widget; the grey copies the colour scheme's `ForegroundInactive` role (also Kvantum's disabled text), whose value matches the reference-sampled etched-rule dark `#888888`, and the node names and `:disabled` state are GTK-required.

**Acceptance criteria.**
- The GTK 3 sheet has the `label:disabled, entry:disabled, spinbutton:disabled` rule and the GTK 4 sheet has the `label:disabled, text:disabled` rule, each with only the `color: #888888` declaration.
- Removing either rule, dropping one of its selectors or changing its colour fails that sheet's `test_disabled_text`. Changing the colour scheme's `[Colors:Button] ForegroundInactive` alone also fails both tests.
- `test_only_palette_hex_literals` still passes in both suites, `tests/invariants.py` accepts the new row, and `make check` is green.

### Platinum GTK rubberbands: draw the drag-selection marquee as a dotted outline with no fill (planned 2026-10-24 by the plan role; independent of the waiting GTK 4 scroll-bar plan) — done 2026-10-24 by the feature role

**Goal.** Neither standalone GTK sheet styles the rubberband, the rectangle a view draws while the pointer drag-selects items (file choosers, icon views, tree views). Measured live with PyGObject under `GTK_THEME=org.macos8.desktop` (with `XDG_DATA_HOME` pointing at a temp dir that holds a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`): a GTK 3 `Gtk.TreeView` or `Gtk.IconView` style context with the `rubberband` class added resolves `background-color` to opaque `rgb(255,255,255)` (the `.view` rule's white) and `border-top-style` to `none`. So the marquee paints an opaque white block over the items it covers, with no outline. Stock Adwaita gives it a 1px solid border and a 20% alpha fill. The GTK 4 sheet has no rule that matches the `rubberband` child node, so a GTK 4 marquee is invisible. The Mac OS Finder drew its selection marquee as a 1px dotted outline with no fill. With `.rubberband, rubberband { background-color: transparent; border: 1px dotted #000000; }` appended to a scratch copy of the GTK 3 sheet, the same live check gives `rgba(0,0,0,0)`, a 1px border, `rgb(0,0,0)` and `GTK_BORDER_STYLE_DOTTED` for both views. So the rule beats the `.view` white because it comes later at equal specificity.

**Design (decided; do not widen).**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: add `.rubberband, rubberband { background-color: transparent; border: 1px dotted #000000; }` after the `.view, textview text, list` rule. It must come after that rule: GTK 3 tree and icon views draw the marquee with the `.rubberband` class on the view's own `.view` context, and flow boxes and list boxes draw it as a `rubberband` node.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: add `rubberband { background-color: transparent; border: 1px dotted #000000; }` after the `.view, list` rule. GTK 4 views draw the marquee only as a `rubberband` child node.
- No new colour: black is already in both sheets' palette. Out of scope: `:backdrop`, the GTK 4 text-view selection, and any square-dot pattern art.

**Files touched.**
- Both sheets: the rule above. Add one sentence to each header comment: the drag-selection rubberband is a 1px dotted black outline with no fill, after the Mac OS Finder marquee; no reference screenshot shows a marquee, so its shape is this theme's adaptation, and the `rubberband` node and class names are GTK-required.
- `tests/support/gtk_theme_spec.py`: add a `RUBBERBAND = {"background-color": "transparent", "border": f"1px dotted {BLACK}"}` constant with a short comment (as `TEXT_SELECTION` has), and a `SheetRuleAssertions`-style `assert_rubberband(self, selectors)` method in `GtkSheetRuleCases` next to `assert_view_background`.
- `tests/test_gtk_theme.py`: `TestGtkTheme.test_rubberband` calls `self.assert_rubberband((".rubberband", "rubberband"))`. It also asserts that the rule comes after the `.view` rule in `self.css`: `self.css.index(".rubberband, rubberband {")` is greater than `self.css.index(".view, textview text, list {")`. A later `.view` would win the cascade again.
- `tests/test_gtk4_theme.py`: `TestGtk4Theme.test_rubberband` calls `self.assert_rubberband(("rubberband",))`.
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section. Guarantee: both GTK sheets draw the drag-selection rubberband as a 1px dotted `#000000` outline with a transparent fill, and GTK 3's rule follows the white `.view` rule. Tests: the two `test_rubberband` tests. Provenance exception: no reference screenshot shows a selection marquee; the dotted outline with no fill follows the Mac OS Finder marquee, the black reuses the palette's reference-grounded outline, and the `rubberband` node and class names are GTK-required.

**Acceptance criteria.**
- The GTK 3 sheet has the `.rubberband, rubberband` rule after the `.view` rule, and the GTK 4 sheet has the `rubberband` rule, each with exactly the two declarations above.
- Removing either sheet's rule, changing its border style or colour, or giving it a fill fails that sheet's `test_rubberband`. Moving the GTK 3 rule above the `.view` rule also fails it.
- `test_only_palette_hex_literals` still passes in both suites, `tests/invariants.py` accepts the new row, and `make check` is green.

### Platinum GTK 4 scroll bars: give the GTK 4 scroll bar the reference's 16px breadth (planned 2026-10-24 by the plan role; independent of the waiting GTK menu-bar plan) — done 2026-10-24 by the feature role

**Goal.** The GTK 4 sheet is standalone: it loads no stock rules. Its `scrollbar > range > trough` rule (1px black border, no padding) and `scrollbar > range > trough > slider` rule (1px black border, `margin: 0`) set no minimum size. GTK 4 also has no stepper buttons, so nothing else gives the bar any breadth. Measured live with PyGObject (`Gtk.Scrollbar().measure(...)` under `GTK_THEME=org.macos8.desktop` with `XDG_DATA_HOME` pointing at a temp dir that holds a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`), a GTK 4 scroll bar is 4px across and 4px long in both orientations. That is only the four border pixels, so the thumb is a sliver. The GTK 3 bar measures 16px across, and stock Adwaita GTK 4 measures 14px. The reference installer CD window (`setup_emaculation.png`) shows a 16px horizontal bar: black rules at y=462 and y=477 around a flat `#EEEEEE` band, which `tests/test_desktoptheme_scrollbar.py::TestScrollbarReference` already samples. The fix is to give the GTK 4 slider a 12px minimum in both axes: 16px = 1px trough border + 1px slider border + 12px + 1px slider border + 1px trough border. Measured live with that rule added through a display CSS provider, the bar is 16px across in both orientations.

**Design (decided; do not widen).**
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: in `scrollbar > range > trough > slider`, add `min-width: 12px;` and `min-height: 12px;`. The equal minimum length makes the smallest thumb square. Change no other rule.
- Out of scope: overlay-scrolling behaviour (`.overlay-indicator`/`.hovering`, and the `gtk-overlay-scrolling` setting), GTK 3 (already 16px), the thumb's grip, and `:disabled`.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: the two declarations. Add one sentence to the header comment: the scroll-bar thumb's 12px minimum fills the reference's 16px bar inside the trough's and thumb's 1px borders, because GTK 4 has no steppers to size the bar.
- `tests/test_gtk4_theme.py`:
  - Extend `TestGtk4Theme.test_scrollbar`'s slider expectation with `"min-width": "12px"` and `"min-height": "12px"`.
  - Add `TestScrollbarBreadthReference(ReferenceScreenshotMixin, unittest.TestCase)` with `REFERENCE = SETUP_REFERENCE` and `MAX_ROWS = SETUP_MAX_ROWS`. Import these from `support.desktoptheme_paths` and `support.reference_image`, as `tests/test_gtk_theme.py::TestScrollbarStepperReference` does.
  - Its test asserts that pixels (200, 462) and (200, 477) are `BLACK` and that every row in between at x=200 is `TROUGH`. It derives `band = 477 - 462 + 1` and asserts `band == 16`.
  - It then parses `CSS` with `parse_css` and asserts the slider's `min-width` and `min-height` both equal `f"{band - 4}px"`. The 4 is the trough's and slider's 1px borders, so the test should also assert that both rules' `border` is `1px solid #000000` (spelled through `BLACK`).
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section. Guarantee: the GTK 4 sheet gives the scroll-bar thumb a 12px minimum in both axes, so a GTK 4 scroll bar is the reference's 16px across. Tests: `tests/test_gtk4_theme.py::TestGtk4Theme::test_scrollbar` and `tests/test_gtk4_theme.py::TestScrollbarBreadthReference`. Provenance: none (the 16px is re-derived from `setup_emaculation.png`).

**Acceptance criteria.**
- The GTK 4 sheet's `scrollbar > range > trough > slider` carries `min-width: 12px` and `min-height: 12px`, and no other rule changes.
- Removing either declaration, or changing it to a value other than the reference band minus the two 1px borders, fails `TestScrollbarBreadthReference`. Removing either one also fails `test_scrollbar`.
- The sheet's hex-literal allow-list tests still pass, since no colour is added. The new invariant row is accepted by `tests/invariants.py`, and `make check` is green.

### Platinum GTK menu bars: give GTK 4 the etched menu-bar face and space both toolkits' titles like the reference (planned 2026-10-24 by the plan role; independent of the waiting GTK disclosure-arrow plan) — done 2026-10-24 by the feature role

**Goal.** Both standalone GTK sheets load no stock rules, so a GTK menu bar gets only what we write. The GTK 3 sheet's `toolbar, menubar` rule gives the bar the `#DDDDDD` face with the etched `#888888`/`#FFFFFF` bottom rule. Its `menuitem:hover, .menuitem:hover` rule paints a hovered or open title `#CCCCFF`. The titles themselves get no padding, so they sit edge to edge. The GTK 4 sheet's `.toolbar` rule does not match a `GtkPopoverMenuBar` (CSS node `menubar > item`), so a GTK 4 menu bar has no Platinum face and its open title gets no highlight. Stock rules, which we never load, are GTK 4 `Default-light.css` `menubar > item { min-height: 16px; padding: 4px 8px; }` with `menubar > item:selected { box-shadow: inset 0 -3px …; }`, and GTK 3 Adwaita `gtk-contained.css` `menubar > menuitem { min-height: 16px; padding: 4px 8px; }`. Give both toolkits the Platinum menu-bar title geometry that the desktop theme already re-derives from the reference: `widgets/menubaritem.svg`'s 7px left/right margins (pinned to the reference title gaps by `tests/test_desktoptheme_menubaritem.py::TestMenuTitleSpacingMatchesReference::test_horizontal_margin_is_half_the_mean_gap`) and its 3px top/bottom margins. Give GTK 4 the face and the flat `#CCCCFF` open title (the colour the menubaritem `pressed` slices are pinned to).

**Design (decided; do not widen).**
- GTK 4: change the selector `.toolbar {` to `.toolbar, menubar {`, keeping its three declarations. Add `menubar > item { padding: 3px 7px; }` and `menubar > item:selected { background-color: #CCCCFF; }` right after it. GTK 4 marks an open menu-bar title `:selected`; stock uses that state too.
- GTK 3: add `menubar > menuitem { padding: 3px 7px; }` right after the `toolbar, menubar` rule. The open/hovered title colour already comes from `menuitem:hover`, so add no colour rule.
- Out of scope: `:disabled` title colours (no reference shows one), `:backdrop`, `min-height`, the menus' own popover bodies (already styled), and `-GtkWidget-window-dragging`.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: the selector change and the two new rules. In the header comment, add one sentence: menu-bar titles take `widgets/menubaritem.svg`'s 3px/7px margins, re-derived from the reference title gaps, and an open title takes the `#CCCCFF` selection; the `menubar > item` node and `:selected` state are GTK-required.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: the one new rule, plus the matching header sentence (naming `menubar > menuitem`, and saying the open title's colour comes from the existing `menuitem:hover` rule).
- `tests/support/gtk_theme_spec.py`: add `assert_menubar_titles(self, selector)` at the end of `GtkSheetRuleCases`. It parses `MENUBARITEM_SVG` (from `support.desktoptheme_paths`) with `support.svg_case.parse_svg`, reads `normal-hint-top-margin` height and `normal-hint-left-margin` width through `svg_assertions.rect_geometry` (as `test_horizontal_margin_is_half_the_mean_gap` does), and calls `assert_rule(selector, {"padding": f"{top}px {left}px"})`. The padding is then derived from the pinned SVG rather than restated. Import them at module top the way `tests/test_desktoptheme_menubaritem.py` does (`svg_assertions` is the `tests/svg_assertions/` package).
- `tests/test_gtk_theme.py`: add `TestGtkTheme.test_menubar_titles`, calling `self.assert_menubar_titles("menubar > menuitem")`. (The open-title `#CCCCFF` from `menuitem:hover` is already pinned in that module; add nothing for it.)
- `tests/test_gtk4_theme.py`: rename `test_toolbar` to `test_toolbar_and_menubar`, looping over `(".toolbar", "menubar")` like the GTK 3 test of the same name. Add `test_menubar_titles`, calling `self.assert_menubar_titles("menubar > item")`, then `self.assert_rule("menubar > item:selected", {"background-color": SELECTION})`, importing `SELECTION` from `support.platinum_palette` if the module does not already.
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section. Guarantee: both GTK sheets pad menu-bar titles with `widgets/menubaritem.svg`'s 3px/7px margins, and GTK 4 paints the menu bar with the etched Platinum face and an open title `#CCCCFF`. Tests: both `test_menubar_titles` cases and `tests/test_gtk4_theme.py::TestGtk4Theme::test_toolbar_and_menubar`. Provenance: the 7px is re-derived from the reference title gaps by `TestMenuTitleSpacingMatchesReference`, and the `#CCCCFF` by `TestReferenceAnchors.test_selection_background`. The 3px vertical margin is the desktop theme's menubaritem contract, not measured on a GTK widget, since no reference screenshot shows one. The node names and the `:selected` state are GTK-required.

**Acceptance criteria.**
- The GTK 4 sheet matches `menubar` with the toolbar's face, border and inset shadow, pads `menubar > item` `3px 7px`, and paints `menubar > item:selected` `#CCCCFF`. The GTK 3 sheet pads `menubar > menuitem` `3px 7px`.
- Changing either sheet's title padding, or the menubaritem margins without updating the sheets, fails a `test_menubar_titles` case. Dropping `menubar` from the GTK 4 face rule fails `test_toolbar_and_menubar`.
- The sheets' existing hex-literal allow-list tests still pass, since no new colour is introduced. The new invariant row is accepted by `tests/invariants.py`, and `make check` is green.

### Platinum GTK disclosure arrows: point tree-view and expander arrows at the Platinum right and down triangles (planned 2026-10-24 by the plan role; independent of the waiting GTK view-background plan) — done 2026-10-24 by the feature role

**Goal.** Neither standalone GTK sheet names an expander, so a tree view's row expander and a `GtkExpander`'s arrow get no `-gtk-icon-source` from us. Stock GTK sets them only in sheets we never load: GTK 3 Adwaita's `gtk-contained.css` (`libgtk-3.so.0` gresource) has `treeview.view.expander { -gtk-icon-source: -gtk-icontheme("pan-end-symbolic"); … }`, `treeview.view.expander:checked { … "pan-down-symbolic" }` and `expander title > arrow { min-width: 16px; min-height: 16px; -gtk-icon-source: -gtk-icontheme("pan-end-symbolic"); }` with a matching `:checked` rule; GTK 4's `Default/Default-light.css` has `columnview.view.expander, treeview.view.expander { min-width: 16px; min-height: 16px; -gtk-icon-source: … }` and bare `expander { min-width: 16px; min-height: 16px; -gtk-icon-source: -gtk-icontheme("pan-end-symbolic"); }`, with `:checked` switching to `pan-down-symbolic`. Without our own rules, these arrows get the toolkit's unstyled default instead of a Platinum triangle. The Kvantum style already draws `[TreeExpander]` with the desktop theme's pinned right and down triangles (the `## kvantum` secondary-controls invariant row). Give GTK the same disclosure triangles: right when collapsed, down when expanded. Both shapes already exist in `theme/desktoptheme/org.macos8.desktop/widgets/arrows.svg` (`right-arrow` `M 5,4 L 5,12 L 11,8 Z`, `down-arrow` `M 4,5 L 12,5 L 8,11 Z`). The down triangle already ships as `assets/arrow-down.svg`, so only a right-triangle asset is new.

**Design (decided; do not widen).** Checked with PyGObject on this machine: a GTK 3 `Gtk.Expander` is `expander > title > arrow.horizontal` (bare `expander` is the widget itself, so GTK 3 must use `expander title > arrow`), and a GTK 4 `Gtk.Expander` is `expander-widget > box > title > expander`. GTK 4's `GtkTreeExpander` arrow is also an `expander` node, so bare `expander` covers both, as stock does. In both toolkits, `GtkTreeView` draws its expander with the `expander` class on `treeview.view`. Expanded is `:checked` everywhere. Rules:
- GTK 3: `treeview.view.expander, expander title > arrow { min-width: 16px; min-height: 16px; -gtk-icon-source: url("../assets/arrow-right.svg"); }` and `treeview.view.expander:checked, expander title > arrow:checked { -gtk-icon-source: url("../assets/arrow-down.svg"); }`.
- GTK 4: `treeview.view.expander, expander { min-width: 16px; min-height: 16px; -gtk-icon-source: url("../assets/arrow-right.svg"); }` and `treeview.view.expander:checked, expander:checked { -gtk-icon-source: url("../assets/arrow-down.svg"); }`.
- Out of scope: `:dir(rtl)` mirroring (an RTL tree keeps the right-pointing triangle), `:hover`/`:selected`/`:disabled`/`:backdrop` colours (the url() SVG paints its own black fill), `columnview.view.expander` (GTK 4 column views draw expanders through `treeexpander`, which bare `expander` already covers), and indent sizes.

**Files touched.**
- `theme/gtk/org.macos8.desktop/assets/arrow-right.svg` (new): a 16x16 canvas holding one `<path d="M 5,4 L 5,12 L 11,8 Z" fill="#000000"/>`, laid out like `assets/arrow-down.svg`, with its provenance comment *inside* the root (naming `widgets/arrows.svg` `right-arrow` and `TestArrowGlyphs`), because GTK's CSS icon loader rejects a comment before the root.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: put the two GTK 3 rules immediately after the row-selection rule (`treeview.view:selected, … list row.activatable:selected:hover`). In the header comment, add a sentence: tree-view and expander disclosure arrows load the shared `assets/arrow-right.svg` (collapsed) and `assets/arrow-down.svg` (expanded), whose triangles reuse the desktop theme's pinned `widgets/arrows.svg` shapes; no reference screenshot shows a GTK widget; the node names are GTK-required.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: put the two GTK 4 rules immediately after its row-selection rule (the one ending `listview > row.activatable:selected:hover`), and add the matching header sentence.
- `tests/support/gtk_theme_spec.py`: add `EXPANDER_COLLAPSED = {"min-width": "16px", "min-height": "16px", "-gtk-icon-source": 'url("../assets/arrow-right.svg")'}` and `EXPANDER_EXPANDED = {"-gtk-icon-source": 'url("../assets/arrow-down.svg")'}`. Add `assert_expander_arrows(self, collapsed, expanded)` to `GtkSheetRuleCases`, after `assert_tree_header`: it asserts `EXPANDER_COLLAPSED` on each collapsed selector and `EXPANDER_EXPANDED` on each expanded selector through `assert_rule`. Mention it in the class docstring's list of selector-taking assertions, if that list exists.
- `tests/test_gtk_theme.py`: add `ARROW_RIGHT = THEME_DIR / "assets" / "arrow-right.svg"` beside `ARROW_UP`. Extend `TestArrowGlyphs` (setUpClass, stand-alone, root-first, 16px canvas, black-only fill, and `test_arrow_geometry` with `M 5,4 L 5,12 L 11,8 Z`) to cover the right arrow, and update its docstring to mention disclosure arrows. Add `TestGtkTheme.test_expander_arrows`, calling `self.assert_expander_arrows(("treeview.view.expander", "expander title > arrow"), ("treeview.view.expander:checked", "expander title > arrow:checked"))`.
- `tests/test_gtk4_theme.py`: add `TestGtk4Theme.test_expander_arrows`, calling `self.assert_expander_arrows(("treeview.view.expander", "expander"), ("treeview.view.expander:checked", "expander:checked"))`.
- `Makefile` `install_gtk`: add `assets/arrow-right.svg` to the `trap` cleanup list, the `install -Dm644 … .arrow-right.svg.staging` chain and the `mv` chain, beside `arrow-up.svg`. In the uninstall recipe, add the file and its `.arrow-right.svg.staging` to the GTK `rm -f` line.
- `tests/support/gtk_fixtures.py` `SHIPPED_FILES` and `tests/test_gtk_install.py` `STAGING_PATHS`: add `assets/arrow-right.svg` (staging `assets/.arrow-right.svg.staging`) after `arrow-up.svg`.
- `README.md` (outside the brief markers): "the seven shared check, radio, combo box, menu arrow and title-button box assets" becomes "the eight shared check, radio, combo box, menu arrow, disclosure arrow and title-button box assets", and "removes the ten GTK files" becomes "eleven". Update `docs/invariants.md`'s GTK install row from "ten GTK theme files" to "eleven". Grep both files for any other GTK file count and fix it too.
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section. Guarantee: both sheets point tree-view and expander disclosure arrows at the shipped right (collapsed) and down (`:checked`) triangles in a 16px box. Tests: the two `test_expander_arrows` cases and `tests/test_gtk_theme.py::TestArrowGlyphs`. Provenance: no reference screenshot shows a GTK widget or a disclosure triangle; the triangles reuse the desktop theme's pinned `widgets/arrows.svg` `right-arrow`/`down-arrow` shapes; the node names, the `:checked` state and the 16px size are GTK-required; RTL mirroring is not done.

**Acceptance criteria.**
- `assets/arrow-right.svg` ships with the right-arrow path, a 16x16 canvas, only `#000000` fill and the root first. `TestArrowGlyphs` fails if the path, canvas or fill changes.
- The GTK 3 sheet carries `treeview.view.expander` and `expander title > arrow` with the 16px minimum and the right-arrow source, plus their `:checked` forms with the down-arrow source. The GTK 4 sheet carries the same for `treeview.view.expander` and `expander`. Both `test_expander_arrows` cases pin them.
- `make install-gtk` installs `assets/arrow-right.svg` byte-for-byte, and `make uninstall` removes it and its staging file. The existing `tests/test_gtk_install.py` cases pass with the extended `STAGING_PATHS`/`SHIPPED_FILES`.
- The new invariant row is accepted by `tests/invariants.py`, the other GTK tests still pass, and `make check` is green.

### Platinum GTK view backgrounds: paint tree, list, icon and text views on the white content field (planned 2026-10-24 by the plan role; independent of the waiting GTK spin-button plan) — done 2026-10-24 by the feature role

**Goal.** Both opt-in GTK sheets are standalone (they import nothing), and neither gives a view its base fill: no rule names `.view`, `list` or `textview text`, so a `GtkTreeView`, `GtkTextView`, `GtkIconView`, `GtkListBox` (and in GTK 4 `GtkListView`, `GtkColumnView`, `GtkGridView`) paints transparently over the `#DDDDDD` window face. Stock GTK paints them in sheets we never load: GTK 3 Adwaita's `gtk-contained.css` (`libgtk-3.so.0` gresource) has `.view, iconview, .view text, iconview text, textview text { color: black; background-color: #ffffff; }` and `list { … background-color: #ffffff; }`; GTK 4's `Default/Default-light.css` has `.view, iconview, textview > text { … background-color: #ffffff; }` and `listview, list { … background-color: #ffffff; }`. The row rules already assume this base: their comment says "a hovered row stays the view background". Mac OS 8.6's window content area is white: the `[Colors:View] BackgroundNormal` anchor `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_window_view_background` re-derives `#FFFFFF` from the reference, already `WHITE` in `tests/support/platinum_palette.py` and the sheets' `theme_base_color`. Paint views white with black text. No new colours are needed.

**Design (decided; do not widen).** Checked with PyGObject on this machine: GTK 3 `TextView`, `TreeView` and `IconView` carry the `view` class and `ListBox` is the class-less `list` node (GTK 3's text view also has a `text` child node, which stock paints too); GTK 4 `TextView`, `ListView`, `ColumnView`, `TreeView`, `IconView` and `GridView` all carry `view` and `ListBox` is `list`. So the selector lists are GTK 3 `.view, textview text, list` and GTK 4 `.view, list`. Declarations: `background-color: #FFFFFF; color: #000000;` only — no border, padding or `:backdrop`/`:disabled` variant (out of scope). Specificity keeps existing rules on top: `.view` and `list` are weaker than `treeview.view:hover`, `treeview.view:selected` and the `list row.activatable…` / `listview > row.activatable…` rules, and the header buttons are not `view` nodes, so their `#DDDDDD` face is untouched.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: add `.view, textview text, list { background-color: #FFFFFF; color: #000000; }` immediately before the `treeview.view:hover, list row.activatable:hover` rule. In the header comment, say views paint the reference-grounded white content field (the colour scheme's View background) with black text, that no reference screenshot shows a GTK widget, and that the `view` class and node names are GTK-required.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: add `.view, list { background-color: #FFFFFF; color: #000000; }` immediately before the `listview > row.activatable:hover` rule, with the matching header-comment sentence.
- `tests/support/gtk_theme_spec.py`: beside `ROW_HOVER`, add `VIEW_BACKGROUND = {"background-color": WHITE, "color": BLACK}` with a comment naming the `test_window_view_background` anchor; add `assert_view_background(self, selectors)` to `GtkSheetRuleCases` after `assert_text_selection`, asserting `VIEW_BACKGROUND` on each selector; mention view-background in the class docstring's list of selector-taking assertions.
- `tests/test_gtk_theme.py`: `TestGtkTheme.test_view_background` calls `self.assert_view_background((".view", "textview text", "list"))`.
- `tests/test_gtk4_theme.py`: `TestGtk4Theme.test_view_background` calls `self.assert_view_background((".view", "list"))`.
- `docs/invariants.md`: a new `## gtk` row at the end of the gtk section: both GTK sheets paint views (`.view`, `list`, and GTK 3's `textview text`) white with black text; tests are the two `test_view_background` cases; provenance: the white is re-derived by `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_window_view_background`, no reference screenshot shows a GTK widget, and the class and node names are GTK-required.

**Acceptance criteria.**
- The GTK 3 sheet carries `.view`, `textview text` and `list` with `background-color: #FFFFFF` and `color: #000000`; the GTK 4 sheet carries `.view` and `list` with the same declarations; both `test_view_background` cases pin them through `assert_view_background`.
- The existing row-hover, row-selection, tree-header and text-selection tests still pass unchanged, and no new hex literal appears in either sheet (`#FFFFFF` and `#000000` are already used).
- The new invariant row is accepted by `tests/invariants.py`, and `make check` is green.

### Platinum GTK spin buttons: give a `GtkSpinButton` the Platinum entry field (planned 2026-10-24 by the plan role; independent of the waiting GTK paned-handle plan) — done 2026-10-24 by the feature role

**Goal.** Both sheets paint text fields with one rule, `entry { background-color: #FFFFFF; border: 1px solid #000000; border-radius: 0; box-shadow: inset 1px 1px #999999; color: #000000; }`, pinned by `GtkSheetRuleCases.test_entry` in `tests/support/gtk_theme_spec.py`. A horizontal spin button never matches it. In GTK 3, `GtkSpinButton` is a `GtkEntry` subclass whose own CSS node is renamed `spinbutton`. In GTK 4 the node is `spinbutton` with `text`, `button.down` and `button.up` children. Neither has an `entry` node, which is why stock styles the field as `spinbutton:not(.vertical), entry` in both GTK 3 Adwaita `gtk-contained.css` and GTK 4 `Default-light.css` (extract them with `gresource extract`; see the separator plan in PLANS-DONE.md). We never load those sheets, so a spin button's number sits on the window's `#DDDDDD` face with no white field or black outline, unlike the entry next to it. That comes from reading the sheets and was not checked in a running app. A vertical spin button behaves differently in each version. GTK 3 gives it a real `entry` descendant (stock `spinbutton.vertical entry`), which our `entry` rule already reaches. GTK 4 uses `spinbutton.vertical > text` (stock spells it that way), which nothing in our GTK 4 sheet names. `grep -n spinbutton theme/gtk` finds only the text-selection selectors. This plan reuses the entry's declarations and adds no new colour or value.

**Design (decided; do not widen).**
- GTK 3 sheet: extend the existing `entry {` rule's selector list to `entry, spinbutton:not(.vertical) {`. GTK 4 sheet: extend it to `entry, spinbutton:not(.vertical), spinbutton.vertical > text {`. The declarations do not change. Keeping one rule means the field cannot drift between the two.
- The spin button's `button.up`/`button.down` keep the existing `button` rule. Their arrow icons still come from the icon theme, as the `## gtk` invariant rows already say. `:disabled`, `:focus`, `.flat`, `.error`/`.warning`, `:backdrop` and padding are out of scope. Stock's `spinbutton:not(.vertical) { padding: 0 }` is not copied, because our `entry` sets no padding either.

**Approach.**
- `tests/support/gtk_theme_spec.py`: next to `TEXT_SELECTION`, add `ENTRY_FIELD` with the five declarations `test_entry` asserts now, and make `test_entry` assert `self.assert_rule("entry", ENTRY_FIELD)`. After `assert_text_selection`, add `GtkSheetRuleCases.assert_spin_button_field(self, selectors)`, which asserts `ENTRY_FIELD` on each selector. Add "spin-button field" to the module docstring's list of named assertions.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`: change the selector lists as above. In each header comment, add one sentence: spin buttons reuse the entry field because their field node is `spinbutton` (GTK 4 vertical: `spinbutton.vertical > text`), not `entry`, and those node names are GTK-required.
- `tests/test_gtk_theme.py` (`TestGtkTheme`): after `test_text_selection`, add `test_spin_button_field`, which calls `self.assert_spin_button_field(("spinbutton:not(.vertical)",))` and also asserts `"spinbutton.vertical > text"` is not in `self.rules`, since GTK 3 reaches it through `entry`. `tests/test_gtk4_theme.py` (`TestGtk4Theme`): add `test_spin_button_field`, which calls `self.assert_spin_button_field(("spinbutton:not(.vertical)", "spinbutton.vertical > text"))`.
- `docs/invariants.md`: add one `## gtk` row as the last row of the section: "Both GTK sheets paint a spin button's field with the Platinum entry field: white, a 1px `#000000` outline and a 1px `#999999` inner top-left shadow". It is tested by `tests/test_gtk_theme.py::TestGtkTheme::test_spin_button_field` and `tests/test_gtk4_theme.py::TestGtk4Theme::test_spin_button_field`. Exception: the field copies the sheets' existing `entry` rule, no reference screenshot shows a GTK spin button, and the `spinbutton` node, its `.vertical` class and GTK 4's `text` child are GTK-required.

**Files touched.** `tests/support/gtk_theme_spec.py`, `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `test_spin_button_field` runs in `TestGtkTheme` and `TestGtk4Theme`. Removing a spin-button selector from either sheet's entry rule, or moving it to a rule that lacks any `ENTRY_FIELD` declaration, makes that test fail.
- `test_entry` (now on `ENTRY_FIELD`), `test_text_selection` and `test_only_palette_hex_literals` pass, with the palette set left as it is.
- The new invariant row is accepted by `tests/invariants.py`, and `make check` is green.

### Platinum GTK paned handles: etch the `paned > separator` split handle like the reference rule (planned 2026-10-24 by the plan role; independent of the waiting GTK level-bar plan) — done 2026-10-24 by the feature role

**Goal.** A `GtkPaned`'s draggable split handle is a `separator` node with no orientation class (`paned > separator`, `.wide` when the paned's `wide-handle` is set). The standalone separator rules (`separator.horizontal`, `separator.vertical`) skip it on purpose: see the done separator plan's "Selector scoping" in PLANS-DONE.md. No other rule in either sheet names it either (`grep -n paned theme/gtk` finds nothing). Stock GTK sizes and paints this handle only in its own sheets, which we never load. GTK 3 Adwaita `gtk-contained.css` and GTK 4 `Default-light.css` both have `paned > separator { min-width: 1px; min-height: 1px; -gtk-icon-source: none; … background-image: image(#cdc7c2); }`. So in our theme the split between, say, a file manager's sidebar and its view most likely has zero size and draws nothing (from reading the sheets; not checked in a running app). Etch it with the same reference-grounded `#888888`/`#FFFFFF` pair the standalone separators use (`ETCH_DARK`, re-derived by `tests/test_desktoptheme_line.py::TestLineReference`). No new colour or spec value is introduced.

**Design (decided; do not widen).**
- A horizontal paned (`paned.horizontal`, side-by-side children) has a vertical handle, so it gets `SEPARATOR_VERTICAL` from `tests/support/gtk_theme_spec.py`: `background-color: #888888; border: 0; border-right: 1px solid #FFFFFF; min-width: 1px; padding: 0`. A vertical paned (`paned.vertical`) gets `SEPARATOR_HORIZONTAL` (`border-bottom` and `min-height` instead). Each rule also sets `-gtk-icon-source: none`, as stock does, so GTK 3's builtin pane-handle image never draws, and `margin: 0`.
- Both sheets use the child selectors `paned.horizontal > separator` and `paned.vertical > separator`. That is stock's spelling in both GTK 3 and GTK 4, because the handle is always a direct child. The rules' specificity is (0,1,2), and they cannot match a classed `GtkSeparator`, since that is never a paned's direct `separator` child.
- `.wide` handles, `:selected`, `:backdrop` and `:dir()` get no rule. Stock's negative-margin grab-area extension (`margin: 0 -8px 0 0; padding: 0 8px 0 0`) is not copied: it would move our `border-right` 8px away from the dark line. All of these are out of scope.

**Approach.**
- `tests/support/gtk_theme_spec.py`: after `SEPARATOR_VERTICAL`, add `PANED_HANDLE_HORIZONTAL = {**SEPARATOR_VERTICAL, "-gtk-icon-source": "none", "margin": "0"}` and `PANED_HANDLE_VERTICAL = {**SEPARATOR_HORIZONTAL, "-gtk-icon-source": "none", "margin": "0"}`. Give them a comment saying a horizontal paned's handle is a vertical rule and that both reuse the reference etch. After `assert_separators`, add `GtkSheetRuleCases.assert_paned_handles(self)`. It takes no selectors, because both sheets spell them alike. It asserts `PANED_HANDLE_HORIZONTAL` on `paned.horizontal > separator` and `PANED_HANDLE_VERTICAL` on `paned.vertical > separator`. Add "paned-handle" to the module docstring's list of named assertions.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`: after each sheet's `separator.vertical` rule, add the two rules with exactly those declarations. Extend the header comment's "The standalone separators reuse …" sentence to say that the paned split handles reuse the same etch, and that the `paned` orientation classes are GTK-required.
- `tests/test_gtk_theme.py` (`TestGtkTheme`) and `tests/test_gtk4_theme.py` (`TestGtk4Theme`): add `test_paned_handle` after `test_separator`. It calls `self.assert_paned_handles()`.
- `docs/invariants.md`: add one `## gtk` row as the last row of the section. It reads "Both GTK sheets etch a `GtkPaned` split handle with a 1px `#888888` line and a 1px `#FFFFFF` line on its right (side-by-side panes) or bottom (stacked panes), with no builtin handle image". It is tested by `tests/test_gtk_theme.py::TestGtkTheme::test_paned_handle` and `tests/test_gtk4_theme.py::TestGtk4Theme::test_paned_handle`. Its exception: the etched pair is re-derived from the reference by `tests/test_desktoptheme_line.py::TestLineReference`, no reference screenshot shows a split pane, and the `paned` node and orientation classes are GTK-required.

**Files touched.** `tests/support/gtk_theme_spec.py`, `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry `paned.horizontal > separator` and `paned.vertical > separator` with the declarations above. `test_paned_handle` runs in `TestGtkTheme` and `TestGtk4Theme`. Dropping any asserted declaration, or swapping the two orientations' specs, fails it.
- `test_separator` and `test_titlebutton_separator_hidden` still pass unchanged, and `test_only_palette_hex_literals` passes with its expected set unchanged.
- The new invariant row is accepted by `tests/invariants.py`, and `make check` is green.

### Platinum GTK level bars: paint `levelbar` as the Platinum progress bar's trough and fill (planned 2026-10-24 by the plan role; independent of the waiting GTK separator plan) — done 2026-10-24 by the feature role

**Goal.** Neither standalone GTK sheet has a `levelbar` rule (`grep -n levelbar theme/gtk` finds nothing). Stock GTK sizes and paints a `GtkLevelBar`'s blocks only in its own Adwaita/Default sheets, which we never load: GTK 3 `levelbar.horizontal block { min-height: 1px; }` plus `levelbar trough`/`levelbar block.*` colours, and GTK 4 `levelbar.horizontal trough > block { min-height: 9px; }` plus `levelbar > trough > block.*`. So a level bar in our theme, such as a password-strength meter or a disk-usage gauge, has no styled trough, and its zero-height blocks most likely draw nothing (from reading the sheets; not checked in a running app). Mac OS 8.6 has no separate level meter. Its gauge is the progress bar, which both sheets already paint from the reference-grounded spec pinned in `tests/support/gtk_theme_spec.py` (`PROGRESSBAR_TROUGH`, `PROGRESSBAR_PROGRESS`, which `test_progressbar` pins in both suites). Paint the level bar with that same trough and fill. No new colour or spec value is introduced.

**Design (decided; do not widen).**
- Nodes: in both GTK 3 and 4 a level bar is `levelbar[.horizontal|.vertical][.discrete] > trough > block`, where each filled block carries `.filled` (plus the `low`/`high`/`full` offset class) and each unfilled block carries `.empty`. Style `.filled` and `.empty` only. Platinum has one fill colour, so the offset classes get no rule.
- The trough is `PROGRESSBAR_TROUGH` without its `min-height`/`min-width`, plus `padding: 0`. The blocks set the size instead: `min-height: 10px` on horizontal blocks and `min-width: 10px` on vertical blocks, so the content box matches the progress trough's 10px.
- A filled block is `PROGRESSBAR_PROGRESS` (flat `#CCCCFF`, no border, bevel or margin). A disabled filled block is `#999999`, like `progressbar progress:disabled`. An empty block is `SCALE_EMPTY_FILL` (transparent, so the `#EEEEEE` trough shows).
- Discrete mode gets no rule: its blocks abut like one continuous progress fill. Out of scope.
- Spell selectors the way each sheet already spells the progress bar: GTK 3 uses descendants (`levelbar trough`, `levelbar block.filled`, `levelbar block.empty`, `levelbar block.filled:disabled`, `levelbar.horizontal block`, `levelbar.vertical block`). GTK 4 uses children (`levelbar > trough`, `levelbar > trough > block.filled`, `levelbar > trough > block.empty`, `levelbar > trough > block.filled:disabled`, `levelbar.horizontal > trough > block`, `levelbar.vertical > trough > block`).

**Approach.**
- `tests/support/gtk_theme_spec.py`: after `SCALE_EMPTY_FILL` add `LEVELBAR_TROUGH`, built from `PROGRESSBAR_TROUGH` minus `min-height`/`min-width` plus `"padding": "0"`, with a comment saying it reuses the progress trough. Add `GtkSheetRuleCases.assert_levelbar(self, trough, filled, empty, disabled, horizontal, vertical)` beside `assert_progressbar`. It asserts `LEVELBAR_TROUGH` on *trough* and `assertNotIn` for `min-height` and `min-width` there; `PROGRESSBAR_PROGRESS` on *filled*; `SCALE_EMPTY_FILL` on *empty*; `{"background-color": GREY}` on *disabled*; `{"min-height": "10px"}` on *horizontal*; and `{"min-width": "10px"}` on *vertical*. Add "level-bar" to the module docstring's list of named assertions.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`: after each sheet's `progressbar … progress:disabled` rule, add the six rules above with exactly those declarations. Add one header-comment sentence: the level bar reuses the reference-grounded progress-bar trough and selection fill, and its node and class names are GTK-required.
- `tests/test_gtk_theme.py` (`TestGtkTheme`) and `tests/test_gtk4_theme.py` (`TestGtk4Theme`): add `test_levelbar` after `test_progressbar`, calling `assert_levelbar` with that sheet's selectors.
- `docs/invariants.md`: add one `## gtk` row after the text-selection row. It reads "Both GTK sheets paint a level bar as the Platinum progress bar: the `#EEEEEE` black-bordered inset trough with no padding, flat `#CCCCFF` filled blocks (`#999999` when disabled), transparent empty blocks and a 10px block cross-size in each orientation". It is tested by `test_levelbar` in both suites. Its exception: the trough and fill reuse the reference-grounded progress-bar spec, no reference screenshot shows a level meter, and the node and class names are GTK-required.

**Files touched.** `tests/support/gtk_theme_spec.py`, `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry the six level-bar rules with the declarations above. `test_levelbar` runs in `TestGtkTheme` and `TestGtk4Theme`. Dropping any asserted declaration, or adding `min-height` to the trough, fails it.
- `test_progressbar` and `test_scale` still pass unchanged in both suites, and `test_only_palette_hex_literals` passes with its expected set unchanged.
- The new invariant row is accepted by `tests/invariants.py`, and `make check` is green.

### Platinum GTK separators: etch standalone horizontal and vertical separators like the reference's rule (planned 2026-10-24 by the plan role; independent of the waiting GTK text-selection plan) — done 2026-10-24 by the feature role

**Goal.** Both opt-in GTK sheets are standalone and etch only menu separators (`menu separator, .menu separator` in GTK 3, `popover separator, popover.background separator` in GTK 4). A `GtkSeparator` anywhere else, such as a dialog's divider, a toolbar's or a settings pane's, matches no rule, so GTK draws nothing. Stock GTK's own `separator` rule is in sheets we never load. Mac OS 8.6 draws a separator as an etched pair, a 1px `#888888` line beside a 1px `#FFFFFF` line. `tests/test_desktoptheme_line.py::TestLineReference` re-derives that pair from the reference in both orientations: `test_horizontal_rule_matches_reference` has dark above light, and `test_vertical_rule_matches_reference` has dark left of light. Paint each orientable `GtkSeparator` with that pair. No new colours are needed: `ETCH_DARK` and `WHITE` are already pinned in `tests/support/gtk_theme_spec.py`.

**Selector scoping (decided; do not widen).** Use `separator.horizontal` and `separator.vertical`, not a bare `separator`. GTK puts the orientation class only on orientable `GtkSeparator` widgets. That keeps the rule off the unclassed nodes that share the `separator` name: paned handles (`paned > separator`), GTK 3's `GtkSeparatorMenuItem` (already etched by the menu rule) and tree-view row separators. GTK 4's popover menu separators are horizontal `GtkSeparator` widgets, so `separator.horizontal` (specificity 0,1,1) outranks `popover separator` (0,0,2) there. For that reason the horizontal rule repeats the menu rule's declarations exactly and **declares no `margin`**, which keeps the menu's `margin: 2px 0` in force. Stock Adwaita hides GTK 3's headerbar title-button separator (`headerbar separator.titlebutton { opacity: 0; }`), and our new vertical etch would otherwise make it visible. So the GTK 3 sheet adds that hide rule too: `headerbar separator.titlebutton` at (0,1,2) outranks `separator.vertical`. GTK 4's `windowcontrols` has no such separator.

**Approach.**
- `tests/support/gtk_theme_spec.py`: after `MENU_SEPARATOR` add `SEPARATOR_HORIZONTAL = {"background-color": ETCH_DARK, "border": "0", "border-bottom": f"1px solid {WHITE}", "min-height": "1px", "padding": "0"}` and `SEPARATOR_VERTICAL = {"background-color": ETCH_DARK, "border": "0", "border-right": f"1px solid {WHITE}", "min-width": "1px", "padding": "0"}`, with a comment that they are the reference's etched rule from `widgets/line.svg`. Add `GtkSheetRuleCases.test_separator`, a shared case that both suites inherit because the two sheets spell these selectors the same way. It asserts both specs on `separator.horizontal` and `separator.vertical` and runs `assertNotIn("margin", ...)` on each rule. Mention the separator in the class docstring.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the `menu separator, .menu separator` rule add `separator.horizontal { background-color: #888888; border: 0; border-bottom: 1px solid #FFFFFF; min-height: 1px; padding: 0; }`, `separator.vertical { background-color: #888888; border: 0; border-right: 1px solid #FFFFFF; min-width: 1px; padding: 0; }` and `headerbar separator.titlebutton, .titlebar separator.titlebutton { opacity: 0; }`. In the header comment, say that the standalone separators reuse the reference-grounded etched pair in both orientations and that the orientation classes are GTK-required.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: after the `popover separator, popover.background separator` rule add the same two orientation rules (no title-button rule), plus the same header-comment sentence.
- `tests/test_gtk_theme.py`: add `TestGtkTheme.test_titlebutton_separator_hidden`, which asserts `{"opacity": "0"}` on both title-button selectors.
- `docs/invariants.md`: add one `## gtk` row after the newest per-feature row. It reads "Both GTK sheets etch each horizontal and vertical `GtkSeparator` with a 1px `#888888` line and a 1px `#FFFFFF` line on its bottom or right, without overriding the menu separator's margin, and GTK 3 hides the headerbar title-button separator". It is tested by `test_separator` in both suites and `test_titlebutton_separator_hidden`. Its provenance exception: the etched pair is re-derived from the reference by `TestLineReference`, no reference screenshot shows a GTK widget, and the orientation classes and the title-button hide are GTK-required.

**Files touched.** `tests/support/gtk_theme_spec.py`, `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry `separator.horizontal` and `separator.vertical` with exactly the declarations above, and neither rule sets `margin`. `test_separator` runs in both `TestGtkTheme` and `TestGtk4Theme`, and removing any declaration, or adding a `margin`, fails it.
- The existing `test_menu_separator` cases still pass unchanged in both suites.
- The GTK 3 sheet hides `headerbar separator.titlebutton` and `.titlebar separator.titlebutton` with `opacity: 0`, which `test_titlebutton_separator_hidden` pins.
- `test_only_palette_hex_literals` passes in both suites with its expected set unchanged.
- The new invariant row is accepted by `tests/invariants.py`, and `make check` is green.

### Platinum GTK text selection: paint selected text in entries, labels and text views with the Platinum highlight (planned 2026-10-24 by the plan role; independent of the waiting GTK switch plan) — done 2026-10-24 by the feature role

**Goal.** Both opt-in GTK sheets are standalone (they import nothing), and neither names a `selection` node, so selected text in a `GtkEntry`, `GtkSpinButton`, selectable `GtkLabel` or `GtkTextView` gets no fill: the `@define-color theme_selected_bg_color #CCCCFF` role is defined but no rule reads it. Stock GTK paints that node in its own sheets, which we never load: GTK 3 Adwaita's `gtk-contained.css` (the `libgtk-3.so.0` gresource) has `entry selection`, `spinbutton:not(.vertical) selection`, `label selection` and `textview text selection`, and GTK 4's `Default/Default-light.css` has `entry > text > selection`, `spinbutton:not(.vertical) > text > selection`, `textview > text > selection`, `label > selection` and `editablelabel > stack > text > selection`. Paint selected text with the reference-grounded flat `#CCCCFF` selection fill (the `[Colors:Selection] BackgroundNormal` anchor `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background` re-derives from `firstboot_betawiki.png`, already `SELECTION` in `tests/support/platinum_palette.py`) and black text. No new colours are needed.

**Approach.**
- `tests/support/gtk_theme_spec.py`: after `ROW_SELECTED` add `TEXT_SELECTION = {"background-color": SELECTION, "color": BLACK}`, with a comment that it reuses the row selection fill. The `color` must be `#000000`, not GTK 4's stock `transparent`: GTK draws the selected range's text a second time in the selection node's colour over its fill, so an opaque fill with a transparent colour would hide the selected glyphs. Add `GtkSheetRuleCases.assert_text_selection(self, selectors)`, modelled on `assert_frame`, that asserts `TEXT_SELECTION` for each selector, and name the text selection in the class docstring's list of suite-selector assertions.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the `list row.activatable:selected, list row.activatable:selected:hover` rule add one rule `entry selection, spinbutton selection, label selection, textview text selection { background-color: #CCCCFF; color: #000000; }` (GTK 3's spin button is itself the entry node, hence its own selector). In the header comment, say the text selection reuses the reference-grounded #CCCCFF selection fill with black text, that no reference screenshot shows selected text in a field, so applying the fill there is this theme's adaptation, and that the node names are GTK-required.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: after the row selection rule add `text > selection, label > selection { background-color: #CCCCFF; color: #000000; }` — GTK 4's entry, spin button, password entry, search entry, editable label and text view all draw their text in a `text` node, so the one child selector reaches them. Add the same header-comment sentence.
- `tests/test_gtk_theme.py`: `TestGtkTheme.test_text_selection` calls `self.assert_text_selection(("entry selection", "spinbutton selection", "label selection", "textview text selection"))`.
- `tests/test_gtk4_theme.py`: `TestGtk4Theme.test_text_selection` calls it with `("text > selection", "label > selection")`.
- `docs/invariants.md`: add one `## gtk` row after the title-button row: "Both GTK sheets paint selected text in entries, spin buttons, labels and text views with the flat `#CCCCFF` selection fill and black text", tested by both `test_text_selection` cases, with the provenance exception that the fill is the reference-grounded `[Colors:Selection]` anchor, no reference screenshot shows selected text in a field, and the node names are GTK-required.

**Files touched.** `tests/support/gtk_theme_spec.py`, `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The GTK 3 sheet carries the four GTK 3 selection selectors and the GTK 4 sheet the two GTK 4 selectors, each with exactly `background-color: #CCCCFF; color: #000000;`, and `test_text_selection` in each suite asserts them through `assert_text_selection`. Removing either declaration, or any one selector, fails that suite.
- `test_only_palette_hex_literals` in both suites passes with its expected set unchanged: the text selection adds no hex literal outside the existing palette.
- The new `## gtk` invariant row is accepted by `tests/invariants.py`, and `make check` is green.

### Platinum GTK switches: paint the track and thumb from the desktop theme's switch (planned 2026-10-24 by the plan role; independent of the waiting `no-repro` ledger plan) — done 2026-10-24 by the feature role

**Goal.** Both opt-in GTK sheets are standalone (they import nothing), and neither names a `switch` node, so a `GtkSwitch` gets no track fill, outline or thumb face. Stock GTK styles it in its own sheets, which we never load: the installed GTK 3 Adwaita `gtk-contained.css` (in the `libgtk-3.so.0` gresource) has `switch`, `switch:checked`, `switch:disabled`, `switch slider` and `switch image { color: transparent; }`, and GTK 4's `Default/Default-light.css` has `switch`, `switch:checked`, `switch:disabled`, `switch > slider` and `switch:disabled > slider`, with no rule hiding the I/O `image` glyphs. Paint the switch the way the desktop theme's `widgets/switch.svg` already does (pinned by `tests/test_desktoptheme_switch.py::TestSwitch`): a flat `#EEEEEE` inactive trough with a 1px `#000000` outline, a flat `#FFFFFF` active field, and the raised `#DDDDDD` slider thumb with no glyph. No new colours are needed.

**Approach.**
- `tests/support/gtk_theme_spec.py`: next to the scale constants add `SWITCH_TRACK = {"background-color": TROUGH, "background-image": "none", "border": f"1px solid {BLACK}", "border-radius": "0", "box-shadow": "none", "min-width": "30px", "min-height": "16px"}` (the 30x16 `hint-bar-size` track in `switch.svg`), `SWITCH_TRACK_CHECKED = {"background-color": WHITE, "background-image": "none"}`, `SWITCH_TRACK_DISABLED = {"border-color": GREY}`, `SWITCH_THUMB = {**SCALE_THUMB, "margin": "-1px", "min-width": "12px", "min-height": "16px"}` (the 12px thumb width, its outline laid over the track's), `SWITCH_THUMB_DISABLED` with the same three declarations `assert_scale` gives a disabled scale thumb (`#DDDDDD` face, `1px solid #999999` border, `box-shadow: none`), and `SWITCH_GLYPH = {"color": "transparent"}`. Add `GtkSheetRuleCases.assert_switch(self, slider, disabled_slider, glyph)`, modelled on `assert_scale`: it asserts `switch`, `switch:checked` and `switch:disabled` against the three track constants, then the suite's slider, disabled-slider and glyph selectors. Name the switch in the module and class docstrings next to the scale.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after `scale slider:disabled` add `switch`, `switch:checked`, `switch:disabled`, `switch slider`, `switch:disabled slider` and `switch image` carrying exactly those declarations. In the header comment, say the switch reuses `widgets/switch.svg`'s faces, that GTK splits the track between the two states so the thumb's drawn width is GTK's layout rather than the 12px floor, and that the node names and the hidden I/O glyphs are GTK-required.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: the same rules with the child selectors `switch > slider`, `switch:disabled > slider` and `switch > image`, after `scale > trough > slider:disabled`, plus the same header-comment sentence.
- `tests/test_gtk_theme.py`: `TestGtkTheme.test_switch` calls `self.assert_switch(slider="switch slider", disabled_slider="switch:disabled slider", glyph="switch image")`.
- `tests/test_gtk4_theme.py`: `TestGtk4Theme.test_switch` calls it with `switch > slider`, `switch:disabled > slider` and `switch > image`.
- `docs/invariants.md`: in both `## gtk` rows (GTK 3 and GTK 4), extend the guarantee sentence to name the switch track and thumb. In the provenance cell, add that the switch reuses the `widgets/switch.svg` faces (the `#EEEEEE` trough, the `#FFFFFF` active field and the raised `#DDDDDD` thumb), whose shape is KDE-required provenance with no reference screenshot, and that the switch node names and hidden glyphs are GTK-required.

**Files touched.** `tests/support/gtk_theme_spec.py`, `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry the six switch rules with exactly the shared spec's declarations, and `test_switch` in each suite asserts them through `assert_switch`. Removing any one declaration fails that suite.
- `test_only_palette_hex_literals` in both suites passes with its expected set unchanged: the switch adds no hex literal outside the existing palette.
- Both updated `## gtk` invariant rows are accepted by `tests/invariants.py`, and `make check` is green.

### Retire the `no-repro` validation gap with a deterministic-reproduction ledger (planned 2026-10-24 by the steward role; promotes the recurring `gap: no-repro` tag, 3 Fixed entries) — done 2026-10-24 by the feature role

**Goal.** Three Fixed entries in BUGS-FIXED.md carry `gap: no-repro` — confirming the failure was not deterministic when the bug was filed. Each fix now has a test that reproduces the failure deterministically: the cursor write-failure test patches the imported `write_bytes_atomically` helper the generator actually calls, the `CHECK_PATTERN` whitespace test pins the stripped glob the recipe now runs, and the desktop-theme test plants a session-theme `plasmarc` in an isolated `XDG_CONFIG_DIRS`. Add the fifth validation-gap ledger, mirroring the `no-observability`, `unclear-invariant`, `no-fake` and `real-run-needed` ones, so every record names the test that now confirms it deterministically and the suite refuses a new uncovered `no-repro` record instead of letting the tag grow.

**Cited entries.** The three `gap: no-repro` records in BUGS-FIXED.md:
- `` `The cursor generator test patches a removed `_write_atomic` symbol` `` (line 411) — `tests/test_cursors_theme.py::TestMainErrors::test_reports_a_failed_write_and_stops_at_that_cursor` patches the shared atomic-write helper the cursor generator imports and calls.
- `` `make check`'s `CHECK_PATTERN` guard accepts a pattern with surrounding whitespace that then matches no test module `` (line 1260) — `tests/test_make_check.py::TestCheckPattern::test_surrounding_whitespace_pattern_is_stripped` runs the trimmed glob through the project's own check.
- `` `tests/test_desktoptheme.py::TestApplyDesktopTheme` fails when `XDG_CONFIG_DIRS` already names a session theme `` (line 1335) — `tests/test_desktoptheme.py::TestApplyDesktopTheme::test_apply_ignores_a_session_theme_in_the_config_search_path` plants the session-theme `plasmarc` so the failure no longer depends on the developer's ambient config.

**Approach.**
- `tests/support/validation_gaps.py`: add `NO_REPRO_BASELINE = 3` and `NO_REPRO_REPRODUCTIONS` with one `Reproduction` per cited entry (markers that match the record subject and the test reference above); add `no_repro(records)` and `no_repro_reproduction(record)`; dispatch `no-repro` in `reproduction_for` and name the five ledgers in its docstring. Update the module docstring from four ledgers to five and describe the tag: a failure that was not deterministic when filed and now names the test that makes it deterministic.
- `tests/test_validation_gaps.py`: add `TestNoReproLedger` mirroring `TestRealRunNeededLedger`, with `test_every_record_names_a_reproduction`, `test_every_entry_names_a_real_test`, `test_every_ledger_entry_covers_a_shipped_record`, `test_the_record_count_does_not_grow` and `test_an_unmatched_mechanism_has_no_reproduction`; update the module docstring to five ledgers.
- `docs/invariants.md`: extend the tooling row that names the four existing ledgers to name the `no-repro` ledger and `tests/test_validation_gaps.py::TestNoReproLedger`.

**Files touched.** `tests/support/validation_gaps.py`, `tests/test_validation_gaps.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The task's gap query over BUGS.md and BUGS-FIXED.md returns the 3 `no-repro` records; each maps to a `NO_REPRO_REPRODUCTIONS` entry and each entry covers a shipped record.
- Every cited test resolves through `check_reference`; a new `no-repro` record without an entry, or a count above 3, fails the suite.
- The updated tooling row is accepted by `tests/invariants.py`, and `make check` is green.

### Platinum GTK headerbars: floor the title bar at the reference's 22px and paint the inactive frame (planned 2026-10-24 by the plan role; independent of the waiting GTK scroll-bar stepper plan) — done 2026-10-24 by the feature role

**Goal.** Both GTK sheets paint the headerbar face and border but leave its height and backdrop state to the toolkit. The installed Adwaita GTK 3 sheet floors every `headerbar` at `min-height: 46px`, and its `headerbar:backdrop` rule paints a `#f6f5f4` face with a white inset shadow, so a GTK 3 client-side title bar is more than twice the reference's 22px `TitleHeight` and its unfocused state is Adwaita's, not Platinum. The reference derives a 22px title bar from `aboutsystem_betawiki.png` (`tests/test_aurorae_rc.py::test_layout_metrics_match_reference`) and a flat inactive frame from the four unfocused windows in `desktop_fandom.png` (`tests/test_aurorae_frame.py`, a `#DDDDDD` field with a `#555555` outer outline), while the Aurorae rc keeps `InactiveTextColor=153,153,153`. Floor both sheets' `headerbar`/`.titlebar` at that 22px title height with the reference's 4px title edge, and give the inactive state the reference's grey field, outline and title text. No reference screenshot shows a GTK widget, so this is the same adaptation the shipped GTK rules already make from the reference-grounded Aurorae art.

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: in the existing `headerbar, .titlebar` rule add `padding: 0 4px` and `min-height: 22px`. The 22px is the Aurorae `TitleHeight`; the 4px side padding is the Aurorae `TitleEdgeLeft`/`TitleEdgeRight` value, and the existing title-button rules already set `margin: 0` with a 16px minimum, so the 13px boxes centre in the 22px bar. The declarations are a floor, not a cap: a headerbar carrying a taller child still grows, which is this theme's adaptation.
- Immediately after the existing `headerbar { border-width: 0 0 1px 0; }` rule in each sheet, add `headerbar:backdrop, .titlebar:backdrop` with `background-color: #DDDDDD`, `background-image: none`, `border-color: #555555`, `box-shadow: none` and `color: #999999`. This outranks the toolkit's backdrop face and inset shadow and matches the reference's unfocused window: the `#555555` outline re-derived from `desktop_fandom.png` and the rc's `InactiveTextColor` for the title text. Leave the title-button backdrop rules as they are; the landed rules already keep the boxes transparent in backdrop.
- `tests/support/platinum_palette.py`: add `INACTIVE_OUTLINE = "#555555"` with a comment recording that the inactive Aurorae frame re-derives it from `desktop_fandom.png` (the "Mac OS 8.6" window's outer outline, x=25 and y=57) via `tests/test_aurorae_frame.py`. `tests/support/aurorae_fixtures.py` now imports it from there instead of defining a second literal.
- `tests/support/gtk_theme_spec.py`: in the shared `GtkSheetRuleCases.test_headerbar`, assert `min-height: 22px` and `padding: 0 4px` on both `headerbar` and `.titlebar`, and add a loop over `headerbar:backdrop` and `.titlebar:backdrop` asserting the `#DDDDDD` face, `#555555` border, `#999999` text, `background-image: none` and `box-shadow: none`. Import `INACTIVE_OUTLINE` beside the existing palette names.
- `tests/test_gtk_theme.py` and `tests/test_gtk4_theme.py`: add `INACTIVE_OUTLINE` to the palette set in each `test_only_palette_hex_literals`; the GTK 3 case scans the raw sheet, comments included, so the provenance comment's literal is covered too.
- Extend each sheet's header provenance paragraph to name the 22px headerbar (Aurorae `TitleHeight`), the 4px title edge, the inactive `#DDDDDD`/`#555555`/`#999999` backdrop, and the GTK-required headerbar/backdrop node names.
- `docs/invariants.md`: extend both GTK rows (GTK 3 and GTK 4) to name the headerbar floor, the 4px title edge and the inactive backdrop, and add the provenance exception that no reference screenshot shows a GTK widget while the height, outline and title colour copy the reference-grounded Aurorae copy.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/support/platinum_palette.py`, `tests/support/aurorae_fixtures.py`, `tests/support/gtk_theme_spec.py`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`. The palette owns the `#555555` sample now and `aurorae_fixtures` re-exports it, so the value has one definition. No asset, `Makefile` or README change.

**Acceptance criteria.**
- Both sheets' `headerbar, .titlebar` rule carries `padding: 0 4px` and `min-height: 22px`; `headerbar` keeps its bottom-only 1px border; both `headerbar:backdrop` and `.titlebar:backdrop` carry the `#DDDDDD` face, `#555555` border, `#999999` text, no background image and no box shadow.
- The shared `GtkSheetRuleCases.test_headerbar` passes for both suites, `test_only_palette_hex_literals` in both suites accepts `#555555`, the updated GTK 3 and GTK 4 invariant rows are accepted by `tests/invariants.py`, and `make check` is green.

### Platinum GTK scroll-bar steppers: paint the reference's arrow boxes and reuse the shipped triangles (planned 2026-10-24 by the plan role; independent of the waiting GTK window-controls plan) — done 2026-10-24 by the feature role

**Goal.** The GTK 3 sheet paints the scroll-bar trough and thumb but names no `scrollbar button` rule, so a non-overlay scroll bar keeps the toolkit's stepper buttons. The reference `setup_emaculation.png` shows a 16px horizontal scroll bar with a 16x16 arrow box at each end: a flat `#EEEEEE` face inside a 1px `#000000` outline, with the arrow glyph centred in it. The desktop theme's `widgets/scrollbar.svg` records that Plasma cannot draw those boxes (`ScrollBar.qml` computes but never uses `arrowPresent`); GTK 3 can, because its steppers are `scrollbar button` nodes whose glyph comes from `-gtk-icon-source`, and they are shown only on a non-overlay scroll bar. Paint them as the reference's arrow boxes using the already-shipped `assets/arrow-up.svg` and `assets/arrow-down.svg`, rotated for the horizontal bar, so no new asset ships and the opt-in install count does not change. GTK 4's installed `Default-light.css` names no `scrollbar button` rule, so the GTK 4 sheet is untouched.

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after `scrollbar slider` and before `progressbar trough`, add `scrollbar:not(.overlay-indicator)` with `-GtkScrollbar-has-backward-stepper: true` and `-GtkScrollbar-has-forward-stepper: true`, and `scrollbar.overlay-indicator` with both false. The installed Adwaita GTK 3 sheet sets both properties false globally; this theme turns the reference's boxes back on for a normal scroll bar and keeps an overlay scroll bar slider-only.
- Add `scrollbar button` with `background-color: #EEEEEE`, `background-image: none`, `border: 0`, `border-radius: 0`, `box-shadow: none`, `min-height: 14px`, `min-width: 14px` and `padding: 0`. The 14px face plus the scroll bar's own 1px `#000000` border and the 1px trough divider gives the reference's 16x16 visible box, so no second inset ring is added. Add `padding: 0` to the existing `scrollbar` rule: the system Breeze GTK 3 sheet sets `scrollbar { padding: 5px 0px; }`, and without the reset the rendered face sat 5px in from the bar's end border, making the visible box 21px instead of 16px. Add `scrollbar button:hover` with `background-color: #EEEEEE` and `scrollbar button:active` with `background-color: #EEEEEE` and the inverted `inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF` bevel; the scoped selectors outrank the generic `button`, `button:hover` and `button:active` rules, so a stepper does not become a grey push button.
- Add the four direction rules: `scrollbar.vertical button.up` with `-gtk-icon-source: url("../assets/arrow-up.svg")`; `scrollbar.vertical button.down` with the down asset; `scrollbar.horizontal button.up` with the up asset and `-gtk-icon-transform: rotate(-0.25turn)`; `scrollbar.horizontal button.down` with the down asset and the same transform. GTK names the horizontal steppers `.up`/`.down` (start/end), so the counter-clockwise quarter turn points the up triangle left and the down triangle right. `-gtk-icon-transform` is the property the installed Adwaita sheet uses on its icon-source check and radio glyphs. Each rule adds the reference's 1px `#555555` divider on the edge facing the trough (`border-bottom`/`border-top` vertically, `border-right`/`border-left` horizontally); `#555555` is the pinned `INACTIVE_OUTLINE`. Move the two arrow assets' provenance comments inside the `<svg>` root: GTK 3's CSS icon loader rejects a file whose first markup is a comment, so a leading comment left the steppers blank even though the images parsed. The triangle path, fill, canvas and URL stay the same.
- Extend the sheet's header provenance paragraph to name the stepper rules, the reference's 16px arrow box with its 14px face and 1px `#555555` divider, the zeroed scroll-bar padding, the reused `widgets/arrows.svg` triangles, the arrow assets' comments inside the root, the normal/overlay stepper switch, and the one detail this sheet does not reproduce: the reference's grey disabled glyph (a URL icon is a fixed fill; the shipped triangle stays black when disabled).
- `tests/support/gtk_theme_spec.py`: add `SCROLLBAR_STEPPER` (the base declarations), `SCROLLBAR_STEPPER_ACTIVE` (the active box-shadow) and `SCROLLBAR_STEPPER_ARROWS` (the four selector → icon-source/transform/divider pairs) beside `FRAME`.
- `tests/test_gtk_theme.py`: add `test_scrollbar_steppers` to `TestGtkTheme`, next to `test_scrollbar`, and extend `test_scrollbar` to assert the `padding: 0` reset; assert the two stepper-property rules, the base, hover and active button rules, and each of the four direction rules. Add `TestScrollbarStepperReference`, which samples the reference screenshot's 14px `#EEEEEE` face, 1px `#000000` bar border and 1px `#555555` divider (`SETUP_REFERENCE`, `SETUP_MAX_ROWS`, `ReferenceScreenshotMixin` and `hex_colour`) and ties the pinned stepper declarations to them. Add `TestArrowGlyphs::test_assets_put_the_root_first`, which rejects a leading comment before the `<svg>` root (an optional XML declaration is still allowed). `test_icon_sources_point_at_shipped_assets` needs no change because the rules reuse the two already-listed arrow URLs.
- `docs/invariants.md`: extend the GTK 3 `## gtk` control row to name the scroll-bar steppers: a normal scroll bar shows the reference's 16px `#EEEEEE` arrow boxes with their `#555555` trough edge and the shipped up/down triangles, an overlay scroll bar keeps no steppers, the box and overlay/normal property names are GTK-required, and the reference's grey disabled glyph is not reproduced.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/assets/arrow-up.svg`, `theme/gtk/org.macos8.desktop/assets/arrow-down.svg`, `tests/support/gtk_theme_spec.py`, `tests/test_gtk_theme.py`, `docs/invariants.md`. No new asset, `Makefile`, README or GTK 4 sheet change: the steppers reuse the two shipped arrow assets, whose provenance comments move inside the root so GTK's CSS icon loader accepts them, so the opt-in install count is unchanged.

**Acceptance criteria.**
- The GTK 3 sheet's `scrollbar` rule carries `padding: 0`, its `scrollbar:not(.overlay-indicator)` sets both stepper properties true and its `scrollbar.overlay-indicator` sets both false; `scrollbar button` carries the `#EEEEEE` face, no border, no box shadow, square corners and the 14px minimum; each direction rule adds the 1px `#555555` divider on the trough-facing edge; hover keeps the face and active uses the inverted bevel.
- The four direction rules point vertical up/down at `arrow-up.svg`/`arrow-down.svg` and horizontal up/down at the same two assets with `rotate(-0.25turn)`; the sheet's `url(...)` set is still exactly the seven shipped asset paths, and the only new hex literal is the pinned `#555555` (`INACTIVE_OUTLINE`) divider; the arrow assets keep their paths, 16px canvas, `#000000` fill and triangle geometry, with only their provenance comments moved inside the root so GTK's CSS icon loader accepts them.
- `TestGtkTheme::test_scrollbar_steppers`, `TestGtkTheme::test_scrollbar` and `TestArrowGlyphs::test_assets_put_the_root_first` pass, the GTK 4 suite is unchanged, the updated `## gtk` invariant row is accepted by `tests/invariants.py`, and `make check` is green.

### Platinum GTK window controls: paint the title-bar buttons as Platinum boxes (planned 2026-10-23 by the plan role; independent of the waiting GTK header plan) — done 2026-10-24 by the feature role

**Goal.** Both opt-in GTK sheets name no `button.titlebutton` or `windowcontrols` rule. GTK 3's default sheet paints `button.titlebutton` transparent and draws the close, maximize and minimize glyphs from the icon theme; GTK 4's `Default-light.css` gives `windowcontrols button > image` a 30px circular background and tints it on hover. A client-side-decorated GTK window therefore keeps Adwaita's title-bar controls beside the Platinum header bar. Paint them with the reference-grounded Aurorae box art: the blank close box, the zoom (maximize) box whose inner square is the same in GTK's restore state, and the collapse (minimize) box with its two bars. The 16px square hit area and centre placement are this theme's GTK adaptation; every box pixel comes from the Aurorae SVGs that `tests/test_aurorae_buttons.py` re-derives from `aboutsystem_betawiki.png` and `systemprofiler_betawiki.png`. This plan paints the controls in the order GTK and KDE already lay them out; it does not change `gtk-decoration-layout`.

**Approach.**
- Add three assets under `theme/gtk/org.macos8.desktop/assets/`, each a 13x13 canvas carrying only the `active-center` group and a comment naming its Aurorae source, reference coordinates and `tests/test_gtk_title_buttons.py`. `window-close.svg` copies the rects of the Aurorae `close.svg` active group; `window-minimize.svg` copies the Aurorae `shade.svg` active group; `window-maximize.svg` copies the Aurorae `maximize.svg` active group with canvas x=5..17 (the box plus its highlight) translated to x=0..12, dropping its pinstripe, gap and spacing columns. Do not copy the Aurorae files whole: a plain SVG renderer draws both their `active-center` and later `inactive-center` groups, so the inactive art would cover the active box. GTK's restore state keeps the `.maximize` class and gets the zoom art, matching the Aurorae `restore.svg` decision, so it ships no fourth asset.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the `headerbar` rule and before the generic `button` rule, add one rule group per control for both scoped selectors `headerbar button.titlebutton.close` and `.titlebar button.titlebutton.close` (and `.maximize` / `.minimize`), each with `background-color: transparent`, `background-image: url("../assets/window-close.svg")` (or the matching asset), `background-position: center`, `background-repeat: no-repeat`, `background-size: 13px 13px`, `border: 0`, `border-radius: 0`, `box-shadow: none`, `margin: 0`, `min-height: 16px`, `min-width: 16px`, `padding: 0` and `-gtk-icon-source: none`; add `headerbar button.titlebutton image, .titlebar button.titlebutton image` with `color: transparent`, `min-height: 16px` and `min-width: 16px`. The scoped selectors outrank the default sheet's `button.titlebutton`, `button.titlebutton:not(.appmenu)` and `button.titlebutton:backdrop` rules, so the box survives hover, active and backdrop instead of reverting to a transparent circular button.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: after the `headerbar` rule and before the generic `button` rule, add the same three rule groups for `headerbar windowcontrols button.close` and `.titlebar windowcontrols button.close` (and `.maximize` / `.minimize`) with the same declarations; add `headerbar windowcontrols button image, .titlebar windowcontrols button image` with `color: transparent`, `min-height: 16px` and `min-width: 16px`, which also overrides the default sheet's 30px image circle. Extend both sheets' provenance comments to name the title-bar boxes, their Aurorae source and the no-restore-asset decision.
- `tests/support/gtk_theme_spec.py`: add `TITLE_BUTTON` (the base declarations above without `background-image`) and `TITLE_BUTTON_IMAGE` beside `FRAME`, plus `assert_title_button(self, selector, asset)` after `assert_scale`, which asserts the base declarations and the `url("../assets/<asset>")` background image on one selector.
- `tests/test_gtk_theme.py`: add `test_title_buttons` asserting the three controls on both `headerbar` and `.titlebar` selectors and the image rule on both image selectors, and add the three new URLs to `test_icon_sources_point_at_shipped_assets`.
- `tests/test_gtk4_theme.py`: add `test_title_buttons` with the `windowcontrols` selectors and the same image assertion, and add the three new URLs to `test_stands_alone`.
- Add `tests/test_gtk_title_buttons.py`: parse the three assets with `support.svg_case.parse_svg`, assert each is a 13x13, script-free, style-free SVG holding only an `active-center` group, assert `window-close.svg` and `window-minimize.svg` render the same `active-center` pixels as their Aurorae sources, and assert `window-maximize.svg` renders exactly the Aurorae maximize group's x=5..17 pixels shifted by `-ZOOM_BOX_X`. The test needs no reference image, so it does not skip when the LFS set is absent.
- Install plumbing: add the three assets to the `install_gtk` staging trap, install and rename steps and to the `make uninstall` removal list in `Makefile`; add them to `SHIPPED_FILES` in `tests/support/gtk_fixtures.py` and to `STAGING_PATHS` in `tests/test_gtk_install.py`; move that suite's shadowed failing staging path to the new last asset (`*/assets/.window-minimize.svg.staging`) so its "last staging step fails" check still exercises the last step. Update `README.md`'s "four shared ... glyph assets" phrase and both "seven GTK files" counts to the new seven assets and ten files, and update the `## gtk` install invariant row in `docs/invariants.md` to the ten files and seven assets. Add one new `## gtk` invariant row at the end of the table naming the title-button rules and the Aurorae-derived assets.

**Files touched.** `theme/gtk/org.macos8.desktop/assets/window-close.svg`, `theme/gtk/org.macos8.desktop/assets/window-maximize.svg`, `theme/gtk/org.macos8.desktop/assets/window-minimize.svg`, `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/support/gtk_theme_spec.py`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `tests/test_gtk_title_buttons.py`, `tests/support/gtk_fixtures.py`, `tests/test_gtk_install.py`, `Makefile`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- The three assets are 13x13 SVGs with one `active-center` group and no inactive group; close and minimize are pixel-identical to their Aurorae active groups, and maximize is the Aurorae zoom box's 13x13 crop.
- Both sheets carry the close, maximize and minimize rule groups on both `headerbar` and `.titlebar` selectors with the base declarations, the matching asset URL, `-gtk-icon-source: none`, and the image rule that hides the toolkit icon; no new hex literal appears in either sheet.
- The new asset test and both suites' title-button tests pass, and both sheets' URL allowlists accept exactly the shipped assets they name.
- The opt-in install copies the now ten files byte-for-byte, a failed staging step still leaves every previous file intact, `make uninstall` removes all ten and the emptied directories, and the README and `docs/invariants.md` counts and rows match.
- `make check` is green.

### Platinum GTK headers: paint the tree and column headers as raised Platinum buttons (planned 2026-10-23 by the plan role; independent of the waiting GTK row plan) — done 2026-10-23 by the feature role

**Goal.** Both opt-in GTK sheets paint windows, header bars, buttons, entries, tabs, menus, scroll bars, meters, scales, check and radio faces, arrows, tooltips, separators and frames, but they name no tree-view or column-view header rule. The GTK 3 sheet is selected as a standalone theme (`make apply-gtk` writes `gtk-theme-name=org.macos8.desktop`), so no Adwaita header rule is in its cascade: the generic `button` rule already reaches a header button, but outlines every cell rather than drawing the shared grid. In GTK 4 the header button and its `sort-indicator` node need explicit rules so the Platinum grid and shipped triangles replace the toolkit's default cells and native sort glyphs. Paint them as the same raised Platinum button `widgets/button.svg` pins: a `#DDDDDD` face, `#000000` text, square corners, the raised bevel and a single 1px `#000000` line between columns and under the header row, with no right line after the last column. In GTK 4, replace the sort indicator's icon-theme chevrons with the already-shipped `assets/arrow-up.svg` and `assets/arrow-down.svg` black triangles. GTK 3's default sheet names no `sort-indicator` node, so this plan paints no GTK 3 sort indicator. No reference screenshot shows a GTK widget or a list header row, so the geometry is this theme's adaptation of the reference-grounded Platinum push button; the rules introduce no hex literal the sheets do not already use.

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the notebook tab rules and before `menu, .menu, popover, .popover`, add `treeview.view header button` with `background-color: #DDDDDD`, `background-image: none`, `color: #000000`, `text-shadow: none`, `border-width: 0 1px 1px 0`, `border-style: solid`, `border-color: #000000`, `border-radius: 0` and `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA`; add `treeview.view header button:hover` with `background-color: #DDDDDD`, `color: #000000`, `text-shadow: none` and the same raised bevel; add `treeview.view header button:active` with `color: #000000`, `text-shadow: none` and the inverted `inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF` bevel. The right and bottom widths, not a four-side border shorthand, make adjacent columns share one line; add `treeview.view header button:last-child` with `border-right-width: 0` so the last column ends the grid without a right line. Extend the header provenance paragraph to name the header rule and say it adapts the grounded Platinum button and that GTK 3 exposes no sort-indicator node to redirect.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: after the notebook tab rules and before `popover > contents, popover > arrow`, add the same three rule groups for the selector pair `columnview.view > header > button, treeview.view > header > button` (and each state), with the same declarations; add the matching `:last-child` pair with `border-right-width: 0`; add `columnview.view > header > button sort-indicator.ascending, treeview.view > header > button sort-indicator.ascending` with `-gtk-icon-source: url("../assets/arrow-up.svg")` and the matching `descending` pair with `url("../assets/arrow-down.svg")`. Extend its header provenance paragraph the same way, naming the two sort triangles.
- `tests/support/gtk_theme_spec.py`: add `TREE_HEADER = {background-color: FACE, background-image: none, color: BLACK, text-shadow: none, border-width: "0 1px 1px 0", border-style: solid, border-color: BLACK, border-radius: "0", box-shadow: BUTTON_BEVEL}`, `TREE_HEADER_HOVER = {background-color: FACE, color: BLACK, text-shadow: none, box-shadow: BUTTON_BEVEL}`, `TREE_HEADER_ACTIVE = {color: BLACK, text-shadow: none, box-shadow: INVERTED_BUTTON_BEVEL}` and `TREE_HEADER_LAST = {border-right-width: "0"}` beside `FRAME`; add `assert_tree_header(self, selectors)` after `assert_scale`, which asserts the base, `:hover`, `:active` and `:last-child` declarations on every selector.
- `tests/test_gtk_theme.py`: add `test_tree_header` calling `self.assert_tree_header(("treeview.view header button",))`.
- `tests/test_gtk4_theme.py`: add `test_tree_and_column_headers` calling `self.assert_tree_header(("columnview.view > header > button", "treeview.view > header > button"))` and asserting the up URL on both `sort-indicator.ascending` selectors and the down URL on both `sort-indicator.descending` selectors; add `"../assets/arrow-up.svg"` to `test_stands_alone`'s URL allowlist, which then names all four shipped assets.
- `docs/invariants.md`: add one new row at the end of the `## gtk` table, after the last settings row, naming the header face, the shared header case including the last column's cleared right line, the GTK 4 sort indicator and the GTK 3 omission. Leave the two existing `## gtk` control rows for the waiting row plan to extend.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/support/gtk_theme_spec.py`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`. The install list, `Makefile` and `README.md` are untouched: no new asset ships and the README's GTK paragraphs enumerate no painted surface.

**Acceptance criteria.**
- Both sheets carry the header rules above; every base header rule paints the `#DDDDDD` face, `#000000` text with no shadow, the `0 1px 1px 0` black grid, square corners and the raised bevel, every hover rule keeps the raised bevel and black text, every active rule uses the inverted bevel, the `:last-child` rule clears the right line on both sheets, and no new hex literal appears in either sheet. The GTK 4 sheet's ascending and descending sort indicators point at the shipped up and down assets.
- The shared header case passes for both sheets, the GTK 4-only sort-indicator case passes, `test_stands_alone` accepts the four shipped asset URLs, and `test_only_palette_hex_literals` still accepts both sheets unchanged.
- The new `## gtk` invariant row names these tests and the provenance exception, `tests/invariants.py` accepts it, and `make check` is green.

### Platinum GTK rows: paint the list and tree selection and drop the hover wash (planned 2026-10-23 by the plan role; independent of the waiting icon-theme plan) — done 2026-10-23 by the feature role

**Goal.** Both opt-in GTK sheets paint windows, header bars, buttons, entries, tabs, menus, scroll bars, meters, scales, check and radio faces, arrows, tooltips, separators and frames, but they name no row rule. GTK 4's installed Default theme paints a selected tree-view, column-view or list row in its accent blue (`#3584e4`) and gives an activatable list row a grey hover wash (`row.activatable:hover`); a GTK 3 application gets whatever its fallback sheet supplies. Mac OS 8.6's list row is the reference-grounded Platinum row pinned in `theme/desktoptheme/org.macos8.desktop/widgets/listitem.svg`: the unselected row is the view background, a hovered row stays pixel-identical to an unselected one, and the selected row is a flat `#CCCCFF` fill with square corners, no bevel and black text. Paint that row in both sheets for `GtkTreeView` and `GtkListBox`, and in GTK 4 for `GtkColumnView` and `GtkListView`. No reference screenshot shows a GTK widget, so the geometry is this theme's adaptation of the grounded `listitem.svg` row; the fill reuses the pinned `SELECTION` value and introduces no hex literal.

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the `frame > border, .frame` rule and before `scrollbar`, add `treeview.view:hover` and `list row.activatable:hover` with `background-color: transparent`; then `treeview.view:selected, treeview.view:selected:hover` and `list row.activatable:selected, list row.activatable:selected:hover` with `background-color: #CCCCFF`, `color: #000000` and `border-radius: 0`. The list-row rules name `.activatable` because the toolkit's fallback row rules select that class, so a plain `list row:selected` would lose to `row.activatable:selected`. Extend the header provenance paragraph to name the row rules and say they adapt the grounded `widgets/listitem.svg` row.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: after the `frame > border, .frame` rule and before `scrollbar > range > trough`, add the same hover and selection rules, plus `listview > row.activatable:hover`, `columnview.view:selected, columnview.view:selected:hover` and `listview > row.activatable:selected, listview > row.activatable:selected:hover`. Extend its header provenance paragraph the same way.
- `tests/support/gtk_theme_spec.py`: add `ROW_HOVER = {"background-color": "transparent"}` and `ROW_SELECTED = {"background-color": SELECTION, "color": BLACK, "border-radius": "0"}` beside the other shared specs; add `test_row_hover` (asserting `treeview.view:hover` and `list row.activatable:hover`) and `test_row_selection` (asserting `treeview.view:selected`, `treeview.view:selected:hover`, `list row.activatable:selected` and `list row.activatable:selected:hover`) to `GtkSheetRuleCases`, so both sheet suites run them.
- `tests/test_gtk4_theme.py`: add `test_columnview_and_listview_rows` asserting `ROW_HOVER` on `listview > row.activatable:hover` and `ROW_SELECTED` on `columnview.view:selected`, `columnview.view:selected:hover`, `listview > row.activatable:selected` and `listview > row.activatable:selected:hover`.
- `docs/invariants.md`: extend both `## gtk` control rows to name the tree, column, list-view and list-box row hover and selection rules, with the provenance exception that no reference screenshot shows a GTK widget, the row's no-hover and flat `#CCCCFF` selection adapt the reference-grounded `widgets/listitem.svg` row, and the node and class names are GTK-required.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/support/gtk_theme_spec.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry the row hover and selection rules above; every selected-row rule paints `#CCCCFF` with `#000000` text and square corners, every hover rule is transparent, and no new hex literal appears in either sheet.
- The shared `GtkSheetRuleCases` row cases pass for both sheets, the GTK 4-only column-view and list-view case passes, and `test_only_palette_hex_literals` still accepts both sheets unchanged.
- Both `## gtk` rows name the row rules and their `listitem.svg` provenance, `tests/invariants.py` accepts them, and `make check` is green.

### Platinum icon theme: draw the standard XDG places as the Platinum folder (planned 2026-10-23 by the plan role) — done 2026-10-23 by the feature role

**Goal.** The icon theme ships `places/folder.svg`, `places/inode-directory.svg`, `places/user-home.svg`, `places/user-desktop.svg`, `places/user-trash.svg` and `places/user-trash-full.svg` at 32x32, 22x22 and 16x16, so a Home, Desktop or generic directory draws the Platinum folder. KIO's places model names its standard folder places with eight more icons — `folder-documents` (Documents), `folder-download` (Downloads), `folder-music` (Music), `folder-pictures` (Pictures), `folder-videos` (Videos), `folder-templates` (Templates), `folder-public` (Public) and `folder-temp` (Temporary Files) — and the standard `user-places.xbel` entries spell Downloads with the plural `folder-downloads`, so the package ships both download names as well (nine names in all). The package ships none of them, so Dolphin's Places sidebar and every place menu draw Breeze's blue folders beside the Platinum ones. Ship the nine names at 32x32, 22x22 and 16x16 as the matching size's Platinum folder, exactly as `inode-directory` already aliases `folder`, so every standard place draws one Platinum folder. No reference screenshot shows these places; the art is the existing folder drawing rather than new art and introduces no palette value. The installed KIO core names `folder-public`, not Breeze's older `folder-publicshare`, and its places model names `folder-download`, while the standard `user-places.xbel` Downloads bookmark is `folder-downloads`; ship both download names.

**Approach.**
- Add `theme/icons/org.macos8.desktop/{32x32,22x22,16x16}/places/` files for the nine names above, each drawing the matching `folder.svg`'s root children in the same document order with the same `d`, geometry and `fill` attributes. Each comment names the place it draws and says it shares the folder geometry because Mac OS 8.6 draws one folder shape for a directory; only the comment differs from `folder.svg`.
- `theme/icons/org.macos8.desktop/index.theme`: no change; `32x32/places`, `22x22/places` and `16x16/places` are already declared with their `Size`, `Context=Places` and `Type=Fixed` sections.
- `tests/test_icon_theme.py`: define `STANDARD_PLACES` with the nine names (both `folder-download` and `folder-downloads`) beside `SHIPPED_ICONS`; extend `SHIPPED_ICONS` with one comprehension over `("16x16", "22x22", "32x32")` and `STANDARD_PLACES`, so the inventory carries the 27 paths without 27 hand-written literals; define `USER_PLACES_ICONS` from the standard `user-places.xbel` folder names this package draws, whose Downloads entry is the plural `folder-downloads`; add `test_standard_places_file_names_are_shipped` asserting each `USER_PLACES_ICONS` name is in `STANDARD_PLACES` and shipped at all three sizes; extend the existing `ICON_SHAPES` alias loop's alias tuple with `*STANDARD_PLACES`, so each new path maps to its size's `folder.svg` tuple; and extend `test_the_folder_alias_shares_the_folder_art` (rename it to `test_every_place_alias_shares_the_folder_art`) to iterate the same alias tuple at all three sizes.
- `README.md`: in the icon-theme sentence that names the hard-disk, folder, document, Trash and full-Trash icons and the Home and Desktop places as the same Platinum folder, name the standard Documents, Downloads, Music, Pictures, Videos, Templates, Public and Temporary Files places as that same folder.
- `docs/invariants.md`: extend the `## icons` geometry row ("the `inode-directory`, `user-home` and `user-desktop` aliases share the folder art") to name the nine standard place names and cite the same test; keep the provenance exception that the art is our own and the reference set has no pixel ground truth, adding that the standard names are KDE-required values read from the installed KIO core's places model, the standard `user-places.xbel` entries spell Downloads as the plural `folder-downloads`, and the shared folder shape is this theme's own choice.

**Files touched.** Twenty-seven new SVGs under `theme/icons/org.macos8.desktop/{32x32,22x22,16x16}/places/` (`folder-documents.svg`, `folder-download.svg`, `folder-downloads.svg`, `folder-music.svg`, `folder-pictures.svg`, `folder-videos.svg`, `folder-templates.svg`, `folder-public.svg`, `folder-temp.svg`), `tests/test_icon_theme.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- Each of the 27 new icons is a square SVG of its declared size whose drawing elements equal the matching `folder.svg`'s in document order, and the alias test compares the `inode-directory`, `user-home` and `user-desktop` aliases plus all nine standard places at 16x16, 22x22 and 32x32.
- The shipped-icon inventory and the `ICON_SHAPES` registry both include the 27 paths and remain equal; the `USER_PLACES_ICONS` case pins the standard places file's plural `folder-downloads`; the palette, structure, placeholder and index-directory tests pass with no new hex literal and no `index.theme` edit.
- The README names the standard places as the Platinum folder, the `## icons` row names the nine place names and their KIO and `user-places.xbel` provenance, `tests/invariants.py` accepts the row, and `make check` is green.

### Platinum GTK control glyphs, part 2/2: paint the combo box and menu scroll arrows from shipped assets (planned 2026-10-23 by the plan role; "requires part 1/2 landed") — done 2026-10-23 by the feature role

**Goal.** After part 1/2 both sheets ship the shared `assets/` directory and the check and radio glyphs, but `GtkComboBox`'s dropdown indicator (and, in GTK 3, a long menu's scroll arrows) still draw the toolkit's icon-theme chevrons, because the sheets never set `-gtk-icon-source` on those nodes. Paint them with the solid black Platinum triangles the desktop theme already pins in `widgets/arrows.svg`: the `down-arrow` path `M 4,5 L 12,5 L 8,11 Z` and the `up-arrow` path `M 4,11 L 12,11 L 8,5 Z`. Ship the two glyphs beside the check and radio assets and point the sheets' `-gtk-icon-source` at them. No reference screenshot shows a GTK widget, so the triangle geometry is the desktop theme's pinned shape and the 16x16 size is the installed default sheet's combo-arrow size. Spin-button arrows stay out of scope: GTK draws them from the icon theme rather than from a CSS `-gtk-icon-source` the sheet can redirect, so pointing the sheet at an asset would only repaint their faces and leave a stock chevron beside them.

**Approach.**
- New `theme/gtk/org.macos8.desktop/assets/arrow-down.svg` and `assets/arrow-up.svg`: standalone 16x16 SVGs with no script, style or id, each one `<path>` with `fill="#000000"` and the corresponding path above.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the part 1/2 check/radio rules add `combobox arrow` with `-gtk-icon-source: url("../assets/arrow-down.svg")`, `min-height: 16px` and `min-width: 16px`; add `menu > arrow.top, .menu > arrow.top, .context-menu > arrow.top` with `-gtk-icon-source: url("../assets/arrow-up.svg")`; add the matching `menu > arrow.bottom, .menu > arrow.bottom, .context-menu > arrow.bottom` group with the down URL. Extend the sheet's header provenance paragraph to name the two arrow glyphs and state that spin-button arrows stay from the icon theme.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: add `combobox arrow, dropdown arrow` with the down URL and the same 16px min size, and extend its header provenance paragraph the same way. GTK 4 has no `menu > arrow.top`/`bottom` scroll nodes (its menus scroll inside a popover), so the GTK 4 sheet names only the combo and dropdown arrows.
- `Makefile` (the `install_gtk` define and the uninstall recipe): add `assets/arrow-down.svg` and `assets/arrow-up.svg` to the part 1/2 two-phase sequence (stage every file, then rename every file), add both staging paths to the `trap`, and on uninstall remove the two assets and their staging siblings, then `rmdir` the emptied `assets/` after removing the part 1/2 glyphs. Add no `.old` rollback phase, for the same reason as part 1/2.
- `README.md`: the GTK install paragraph that names the shared glyph assets gains the two arrow glyphs, and the `make uninstall` sentence keeps naming the emptied `assets` directory beside `gtk-3.0`/`gtk-4.0`.
- `tests/support/gtk_fixtures.py`: add `assets/arrow-down.svg` and `assets/arrow-up.svg` to `SHIPPED_FILES`, so the package-coverage, repeat-install, failed-install and uninstall tests iterate them.
- `tests/support/gtk_theme_spec.py`: add `COMBO_ARROW = {"-gtk-icon-source": 'url("../assets/arrow-down.svg")', "min-height": "16px", "min-width": "16px"}` and a `test_combobox_arrow` case in `GtkSheetRuleCases` asserting it on `combobox arrow`, which both sheets spell the same way.
- `tests/test_gtk_theme.py`: assert the three `.top` selectors carry the up URL and the three `.bottom` selectors the down URL; add a `TestArrowGlyphs` case (modelled on part 1/2's `TestCheckGlyphs`) that parses both assets through `support.svg_case.parse_svg` and pins each root's 16x16 `viewBox`, each path's `d` and `fill="#000000"`, the `{#000000}` fill set and the absence of script and style elements; add a `test_icon_sources_point_at_shipped_assets` that collects every `url(...)` value in the sheet and asserts it is one of the four shipped `../assets/` paths (checkmark, bullet, arrow-down, arrow-up).
- `tests/test_gtk4_theme.py`: assert the shared `combobox arrow` rule and the GTK 4-only `dropdown arrow` rule; change `test_stands_alone`'s URL allowlist, which part 1/2 narrowed to the two check/radio paths, to the three paths the GTK 4 sheet names (checkmark, bullet, arrow-down).
- `tests/test_gtk_install.py`: add both arrow assets to `STAGING_PATHS`, and move the mocked staging failure from `assets/.bullet.svg.staging` to `assets/.arrow-up.svg.staging` (the last staging step) so the commented two-phase guarantee still holds.
- `docs/invariants.md`: extend both `## gtk` control rows to name the combo box dropdown arrow and the GTK 3 menu scroll arrows, with the provenance exception that no reference screenshot shows a GTK widget, the triangles are the desktop theme's pinned `widgets/arrows.svg` shapes, the 16px size and selectors are GTK-required (read from the installed default sheet), and spin-button arrows are not redirected because GTK draws them from the icon theme; extend the opt-in install row to copy and remove the two arrow assets and say they are this theme's own.

**Files touched.** `theme/gtk/org.macos8.desktop/assets/arrow-down.svg`, `theme/gtk/org.macos8.desktop/assets/arrow-up.svg` (both new), `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `Makefile`, `README.md`, `tests/support/gtk_fixtures.py`, `tests/support/gtk_theme_spec.py`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `tests/test_gtk_install.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets' `combobox arrow` (and GTK 4's `dropdown arrow`) carry the down asset URL and the 16px min size, and the GTK 3 menu `.top`/`.bottom` groups carry the up/down URLs; no new hex literal appears in either sheet.
- Each arrow asset is a 16x16 standalone SVG with its pinned path and `#000000` fill, and the GTK 3 sheet's `url(...)` values are exactly the four shipped asset paths.
- The opt-in install copies the seven package files byte-for-byte (index, two sheets, four assets), a failure while staging any file leaves the previous files intact with no staging sibling, and uninstall removes only those files and the emptied `assets`, `gtk-3.0` and `gtk-4.0` directories, leaving `Kvantum/`.
- The GTK 3 and GTK 4 suites pass (including the narrowed `test_stands_alone`), `tests/invariants.py` accepts the updated `## gtk` rows, and `make check` is green.

### Platinum GTK control glyphs, part 1/2: paint the check and radio buttons and their checked glyphs (planned 2026-10-23 by the plan role; part 2/2 adds the combo box and menu scroll arrows) — done 2026-10-23 by the feature role

**Goal.** Both opt-in GTK sheets paint windows, header bars, buttons, entries, tabs, menus, scroll bars, meters, toolbars, tooltips, separators and frames, but leave `GtkCheckButton` and `GtkRadioButton` to GTK's generic rounded rendering, so a check box is a rounded grey square and a checked box draws no Platinum glyph (the sheet imports no upstream stylesheet, so it supplies none). Paint them from the Platinum art the theme already ships: the raised `#DDDDDD` check square inside a `#000000` outline with a `#FFFFFF` top/left bevel and an `#888888` bottom/right bevel (the reference-grounded Kvantum check box face), and the round `#FFFFFF` radio face with the `#000000` outline (matching `widgets/radiobutton.svg`). GTK draws the checked glyph from `-gtk-icon-source`, which the sheet cannot compose itself, so ship two tiny glyph assets beside the sheets — a 2px black check and a black 2.5px-radius dot — and copy them in the same opt-in install.

**Approach.**
- New `theme/gtk/org.macos8.desktop/assets/checkmark.svg` and `assets/bullet.svg`, each a standalone 14x14 SVG with no script or style element: the check is one path `M 2.5,7.5 L 5.5,10.5 L 11.5,4.5` with `fill="none"`, `stroke="#000000"`, `stroke-width="2"`, `stroke-linecap="square"` and `stroke-linejoin="miter"` (the desktop theme's `widgets/checkmarks.svg` check scaled from its 16px cell), and the bullet is `<circle cx="7" cy="7" r="2.5" fill="#000000"/>` (the Kvantum radio dot). The shared `assets/` directory sits beside `gtk-3.0/` and `gtk-4.0/`, so both sheets address it with `url("../assets/...")`.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the `entry` rule add `check, radio` with `min-height: 14px`, `min-width: 14px`, `margin: 0 4px`, `background-color: #DDDDDD`, `background-image: none`, `border: 1px solid #000000` and `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #888888`; `check` with `border-radius: 0`; `radio` with `background-color: #FFFFFF`, `border-radius: 50%` and `box-shadow: none`; `check:checked` with `-gtk-icon-source: url("../assets/checkmark.svg")`; and `radio:checked` with `-gtk-icon-source: url("../assets/bullet.svg")`. Beside the menu rules add `menu menuitem check, menu menuitem radio` with `margin: 0`, `background-color: transparent`, `border-color: transparent` and `box-shadow: none`, so a menu shows the bare check mark the reference menus draw rather than a raised box.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: the same six rules after its `entry` rule, and the GTK 4 menu form `popover modelbutton check, popover modelbutton radio, popover.background modelbutton check, popover.background modelbutton radio` with the same declarations. Extend both sheets' header provenance paragraphs to name the check/radio faces and their glyph assets.
- `Makefile` (the `install_gtk` define and the `_uninstall` recipe): extend `install_gtk` to two phases while keeping its existing `.staging` + `mv` pattern. The `trap` removes all five staging paths; five `install -Dm644` commands stage `index.theme`, both sheets, `assets/.checkmark.svg.staging` and `assets/.bullet.svg.staging` under `$(GTK_INSTALL_DIR)`; only after every staging command succeeds do five `mv` commands rename them over their finals. Do not add an `.old` backup or rollback phase: no cleanup step follows the renames, and a rename failure is reported without restoring anything (the files already renamed stay in place, each byte-complete). In `_uninstall`, add the two asset finals and their `.staging` siblings to the `rm -f` list and add `$(GTK_INSTALL_DIR)/assets` to the `rmdir` list beside `gtk-3.0` and `gtk-4.0`.
- `README.md`: the GTK install paragraph ("`make install-gtk` copies the two stylesheets") names the two shared glyph assets; the GTK paragraph's "`make uninstall` removes the three GTK files, their `.staging` leftovers and the emptied `gtk-3.0`/`gtk-4.0` directories" names the five files and the emptied `assets/` directory beside them; the general uninstall paragraph's "the eight default artifacts and the three opt-in GTK files" becomes "the five opt-in GTK files".
- `tests/support/gtk_fixtures.py`: add `assets/checkmark.svg` and `assets/bullet.svg` to `SHIPPED_FILES`, so the package-coverage, repeat-install, failed-install and uninstall tests iterate them.
- `tests/test_gtk_install.py`: rename `test_make_install_copies_all_three_byte_for_byte` to `test_make_install_copies_every_shipped_file_byte_for_byte`; in `TestInstall.test_failed_install_keeps_previous_files` overwrite every installed `SHIPPED_FILES` entry with distinct sentinel bytes before the failing install, keep the shadow `install` shim failing on a `.staging` destination, and assert every sentinel survives and no staging sibling exists -- this fails unless every staging precedes every rename; add `test_a_failed_rename_does_not_roll_back_earlier_renames`, which shadows `mv` to fail on one asset final and asserts the files renamed before it hold the new bytes, the failed target still holds its sentinel, and no `.old` or `.staging` sibling exists; in `TestUninstall` add the two asset staging paths to the planted staging leftovers.
- `tests/support/gtk_theme_spec.py`: add `test_check_and_radio` to `GtkSheetRuleCases` pinning the `check`, `radio`, `check:checked` and `radio:checked` declarations and both `-gtk-icon-source` URLs.
- `tests/test_gtk_theme.py`: add the `menu menuitem check` / `menu menuitem radio` case, and a `TestCheckGlyphs` case (modelled on `test_desktoptheme_checkmarks.py`'s `SvgCase` use) that parses both assets through `support.svg_case.parse_svg` and pins each root's 14x14 `viewBox`, the check path's `d` and stroke attributes, the bullet's centre, radius and fill, the `{none, #000000}` fill set and the absence of script elements.
- `tests/test_gtk4_theme.py`: add the four `popover modelbutton check/radio` selectors to the rule test, and change `test_stands_alone`'s blanket `assertNotIn("url(", self.css)` to assert that the only `url(...)` values are the two `../assets/` paths, while it still finds no `@import` and no Adwaita mention. The sheet still imports no other stylesheet; the imported installed sheet resolves the relative assets from its own `gtk-4.0/` directory.
- `docs/invariants.md`: extend both `## gtk` control rows to name the check/radio faces and checked glyphs (and the menu-boxless treatment), with the provenance exception that no reference screenshot shows a GTK widget, the faces reuse the reference-grounded Kvantum check box and the desktop theme's radio face, and the checked glyph shape is this theme's adaptation; extend the opt-in install row to copy and remove the two shared glyph assets, change its `three GTK theme files` / `removes only the three files` wording to five, and say the assets are this theme's own.

**Files touched.** `theme/gtk/org.macos8.desktop/assets/checkmark.svg`, `theme/gtk/org.macos8.desktop/assets/bullet.svg` (both new), `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `Makefile`, `README.md`, `tests/support/gtk_fixtures.py`, `tests/test_gtk_install.py`, `tests/support/gtk_theme_spec.py`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry the pinned rules; `check`/`radio` faces use only palette values already accepted by `test_only_palette_hex_literals`, and no new hex literal appears in either sheet.
- A checked check box draws the black check and a checked radio the black dot, from the two shipped assets, in content and menus (menus boxless); the asset tests pin each asset's geometry and `{none, #000000}` fill set.
- `install_gtk` stages every shipped file before renaming any: a shim that fails an `install` stage leaves all previously installed bytes unchanged with no `.staging` sibling, and a shim that fails one `mv` leaves the earlier renames in place without restoring an older copy or creating an `.old` sibling. A successful install copies the five package files byte-for-byte, and uninstall removes only those files and the emptied directories, leaving `Kvantum/`.
- `grep -n 'three GTK' README.md docs/invariants.md` and `grep -n 'the three files' README.md docs/invariants.md` print nothing, and both files name five opt-in GTK files and the emptied `assets/` directory.
- The GTK 3 and GTK 4 suites pass (including the narrowed `test_stands_alone`), `tests/invariants.py` accepts the updated `## gtk` rows, and `make check` is green.

### Platinum icon theme: draw the Home and Desktop places as the Platinum folder (planned 2026-10-23 by the plan role; independent of the waiting GTK glyph series) — done 2026-10-23 by the feature role

**Goal.** The icon theme inherits Breeze and ships `places/folder.svg`, `places/inode-directory.svg`, `places/user-trash.svg` and `places/user-trash-full.svg` at 32x32 with 16x16 and 22x22 renditions. KDE's standard Places list names three special items by icon: `user-home` (Home), `user-desktop` (Desktop) and `user-trash` (Trash), as the standard `user-places.xbel` entries write them. The theme draws `user-trash`, but no `user-home` or `user-desktop`, so Dolphin's Places sidebar and any place menu that shows Home or Desktop inherits Breeze's blue artwork while every generic folder is Platinum. Ship the two missing names at 32x32, 22x22 and 16x16 as the Platinum folder shape, exactly as `inode-directory` already aliases `folder`, so every place and directory draws one Platinum folder. No reference screenshot shows a Home or Desktop place; the art is the existing folder drawing rather than new art and introduces no palette value.

**Approach.**
- Add `theme/icons/org.macos8.desktop/32x32/places/user-home.svg`, `22x22/places/user-home.svg` and `16x16/places/user-home.svg`, and the same three files for `user-desktop`, each drawing the matching `folder.svg`'s root children in the same document order with the same `d`, geometry and `fill` attributes. Each comment names the place it draws and says it shares the folder geometry because Mac OS 8.6 draws one folder shape for a directory; only the comment differs from `folder.svg`.
- `theme/icons/org.macos8.desktop/index.theme`: no change; `32x32/places`, `22x22/places` and `16x16/places` are already declared with their `Size`, `Context=Places` and `Type=Fixed` sections.
- `tests/test_icon_theme.py`: add the six new paths to `SHIPPED_ICONS`; add each path to `ICON_SHAPES` with the same `_shape` tuples as the matching `folder.svg` (either repeat the six tuples or map the alias paths to the folder tuple after the literal dictionary); extend `test_the_folder_alias_shares_the_folder_art` so `inode-directory`, `user-home` and `user-desktop` each equal `folder`'s drawing at 16x16, 22x22 and 32x32.
- `README.md`: in the icon-theme sentence that names the hard-disk, folder, document, Trash and full-Trash icons, name the Home and Desktop places as the same Platinum folder.
- `docs/invariants.md`: extend the `## icons` geometry row ("the `inode-directory` alias shares the folder art") to name the `user-home` and `user-desktop` places and cite the same test; keep the provenance exception that the art is our own and the reference set has no pixel ground truth, adding that the three place names are KDE-required values read from the standard `user-places.xbel` entries and the shared folder shape is this theme's own choice.

**Files touched.** Six new SVGs under `theme/icons/org.macos8.desktop/{32x32,22x22,16x16}/places/` (`user-home.svg`, `user-desktop.svg`), `tests/test_icon_theme.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- Each of the six new icons is a square SVG of its declared size whose drawing elements equal the matching `folder.svg`'s in document order, and the alias test compares all three aliases at all three sizes.
- The shipped-icon inventory and the `ICON_SHAPES` registry both include the six paths and remain equal; the palette, structure and index-directory tests pass with no new hex literal and no `index.theme` edit.
- The README and the `## icons` row name Home and Desktop as the Platinum folder, `tests/invariants.py` accepts the row, and `make check` is green.

### Retire the `real-run-needed` validation gap with a bounded-run ledger (planned 2026-10-23 by the steward role; promotes the recurring `gap: real-run-needed` tag, 5 Fixed entries) — done 2026-10-23 by the feature role

**Goal.** Five Fixed entries in BUGS-FIXED.md carry `gap: real-run-needed` — confirming the failure needed a real bounded run because no offline test covered it. Three are prose records from 2026-10-23: each MemoryError on an oversize Firefox INI, GTK config or Firefox profile file now has a sparse-file cap test pinning the same bound offline. Two are older one-line bullets whose fixes now have offline install tests: the still-selected color-scheme warning and the scheme filename that KDE must be able to resolve on restart. Add the fourth validation-gap ledger, mirroring the `no-observability`, `unclear-invariant` and `no-fake` ones, so every record names the test that now confirms it offline and the suite refuses a new uncovered `real-run-needed` record instead of letting the tag grow.

**Cited entries.** The five `gap: real-run-needed` records in BUGS-FIXED.md:
- "An oversize Firefox profile-discovery INI file crashes with a MemoryError", reproduced by `tests/test_firefox_install.py::TestProfileResolution::test_an_oversize_ini_file_is_refused_by_name`.
- "An oversize GTK settings or user-CSS file crashes the GTK selection with a MemoryError", reproduced by `tests/test_gtk_apply.py::TestUnreadableConfig::test_apply_refuses_an_oversize_settings_file_before_writing_anything` and `tests/test_gtk_apply.py::TestUnreadableConfig::test_remove_refuses_an_oversize_user_css_before_clearing_anything`.
- "An oversize Firefox profile file crashes the installer with a MemoryError", reproduced by `tests/test_firefox_install.py::TestInstall::test_an_oversize_user_chrome_is_refused_by_name` and `tests/test_firefox_install.py::TestInstall::test_an_oversize_user_js_is_refused_by_name`.
- "Uninstalling the scheme while it is selected leaves KDE warning `Could not find color scheme \"MacOS8\"`", reproduced by `tests/test_colorscheme_install.py::TestInstall::test_make_uninstall_warns_when_the_removed_scheme_is_still_selected`.
- "`plasma-apply-colorscheme` writes a scheme ID that does not survive a restart", reproduced offline by `tests/test_colorscheme_install.py::TestInstall::test_make_install_names_the_scheme_after_its_source_basename` (the basename is what KDE resolves on restart); the live `TestRestartRoundTrip` test stays skipped when the Plasma CLI is absent.

**Approach.**
- `tests/support/validation_gaps.py`: add `REAL_RUN_NEEDED_BASELINE = 5`, a `REAL_RUN_NEEDED_REPRODUCTIONS` tuple reusing `Reproduction` with one entry per cited record (markers match the prose heading or the older bullet), a `real_run_needed(records)` filter and a `real_run_needed_reproduction(record)` lookup, and extend `reproduction_for` to dispatch the tag; update the module docstring to four ledgers.
- `tests/test_validation_gaps.py`: update the module docstring to four ledgers; add `TestRealRunNeededLedger` mirroring `TestNoFakeLedger`, with `test_every_record_names_a_reproduction`, `test_every_entry_names_a_real_test`, `test_every_ledger_entry_covers_a_shipped_record`, `test_the_record_count_does_not_grow` and `test_an_unmatched_mechanism_has_no_reproduction`.
- `docs/invariants.md`: extend the tooling row that names the three existing ledgers to name the `real-run-needed` ledger and `tests/test_validation_gaps.py::TestRealRunNeededLedger`.

**Files touched.** `tests/support/validation_gaps.py`, `tests/test_validation_gaps.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The task's gap query over BUGS.md and BUGS-FIXED.md returns the 5 `real-run-needed` records; each maps to a `REAL_RUN_NEEDED_REPRODUCTIONS` entry and each entry covers a shipped record.
- Every cited test resolves through `check_reference`; a new `real-run-needed` record without an entry, or a count above 5, fails the suite.
- `tests/invariants.py` accepts the extended tooling row and `make check` is green.

### Platinum GTK secondary chrome: paint the tooltip, menu separator and frame (planned 2026-10-23 by the plan role; independent of the waiting Firefox chrome plan) — done 2026-10-23 by the feature role

**Goal.** Both opt-in GTK sheets paint windows, header bars, buttons, entries, tabs, menus, scroll bars, progress bars, scales and toolbars, but they leave `GtkTooltip`, `GtkSeparatorMenuItem` and `GtkFrame` to GTK's generic rendering, so a tooltip, a menu separator and a group box still draw the toolkit's own rounded greys. Paint them from the Platinum art the theme already ships: the flat `#FFFFCC` tooltip face with a 1px `#000000` outline (matching `widgets/tooltip.svg`), the etched `#888888` over `#FFFFFF` menu separator (matching `widgets/line.svg`), and the sunken 1px `#000000` frame with the `#999999` inner shadow the entry and trough rules already use. No reference screenshot shows a GTK widget, so the geometry is this theme's adaptation; the only palette value the sheets do not already carry is the already-pinned `TOOLTIP_FACE` from `tests/support/platinum_palette.py`, and every other declaration reuses a token the sheet already names.

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the `menuitem:hover` rules and before `scrollbar`, add:
  - `tooltip` with `background-color: #FFFFCC`, `color: #000000`, `border: 1px solid #000000`, `border-radius: 0`, `box-shadow: none` and `padding: 2px 4px`; `tooltip.background` with `background-color: #FFFFCC` and `background-clip: padding-box`.
  - `menu separator, .menu separator` with `background-color: #888888`, `border: 0`, `border-bottom: 1px solid #FFFFFF`, `margin: 2px 0`, `min-height: 1px` and `padding: 0`.
  - `frame > border, .frame` with `border: 1px solid #000000`, `border-radius: 0`, `box-shadow: inset 1px 1px #999999`, `margin: 0` and `padding: 0`.
  - Extend the header provenance paragraph to name the `#FFFFCC` tooltip face pinned by `tests/support/platinum_palette.py` beside the existing `#888888` separator sentence.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: add the same tooltip and frame rules, and the GTK 4 menu selector `popover separator, popover.background separator` (the selector the installed Breeze GTK 4 sheet uses for menu separators) with the same separator declarations, after the `popover.menu modelbutton` rules and before the scrollbar rules. Extend its header provenance paragraph the same way.
- `tests/test_gtk_theme.py`: import `TOOLTIP_FACE` from `support.platinum_palette`, add it to the expected set in `test_only_palette_hex_literals`, and add `test_tooltip`, `test_menu_separator` and `test_frame` pinning every declaration above for both menu selector forms (`menu separator`, `.menu separator`) and both frame selector forms (`frame > border`, `.frame`).
- `tests/test_gtk4_theme.py`: import `TOOLTIP_FACE`, add it to `test_only_palette_hex_literals`, and add matching `test_tooltip`, `test_menu_separator` (for `popover separator` and `popover.background separator`) and `test_frame` methods.
- `docs/invariants.md`: extend both `## gtk` guarantee sentences (GTK 3 and GTK 4) to name the tooltip, menu-separator and frame rules; keep their no-reference-screenshot provenance exception and add that the tooltip face is the classic Platinum `[Colors:Tooltip]` role no screenshot shows.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry the tooltip, menu-separator and frame rules, and the new test methods fail if any selector or declaration changes.
- `test_only_palette_hex_literals` in both suites accepts the sheets with `TOOLTIP_FACE` added and rejects any other new hex literal; the GTK 4 `test_stands_alone` still finds no `@import` and no `url(`, and no selector is universal.
- `tests/invariants.py` accepts the updated `## gtk` rows and `make check` is green.

### Firefox Platinum chrome: paint the toolbar button states, bookmark items, menu separators and the find bar (planned 2026-10-23 by the plan role; independent of the waiting GTK meters plan) — done 2026-10-23 by the feature role

**Goal.** The Firefox sheet paints the tab strip, navigation bar, bookmarks-bar background, menus and status panel, but it leaves Firefox's own rounded hover and pressed washes on the toolbar buttons, rounded highlights on bookmarks-bar items, the stock grey menu separator, and the default find bar. Paint those surfaces with the pinned Platinum values the sheet already uses: the #EEEEEE trough as the hover wash, the #CCCCFF selection as the pressed/open fill, the raised bevel (`inset 1px 1px #FFFFFF, inset -1px -1px #999999`) on the hovered button, the etched #888888/#FFFFFF rule from `widgets/line.svg`, the #DDDDDD face for the find bar and the white sunken field with its #999999 shadow for its text box. No reference screenshot shows Firefox chrome, so the geometry is this theme's adaptation of the Platinum controls; the new rules introduce no new hex literal.

**Approach.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`:
  - Extend the `:root` block with Firefox's toolbarbutton variables: `--toolbarbutton-border-radius: 0 !important`, `--toolbarbutton-background-color-hover: #EEEEEE !important` and `--toolbarbutton-background-color-active: #CCCCFF !important`.
  - Add `toolbarbutton:hover:not([disabled="true"])` with the raised bevel box-shadow and `toolbarbutton:hover:active:not([disabled="true"])` with `box-shadow: inset 1px 1px #999999 !important`.
  - Add one rule `#PersonalToolbar .bookmark-item:hover, #PersonalToolbar .bookmark-item[open]` with `background-color: #CCCCFF !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px #FFFFFF !important`.
  - Add `menupopup > menuseparator` with `padding: 0 !important` and `margin: 2px 0 !important`, and `menupopup > menuseparator::before` with `border-top: 1px solid #888888 !important` and `border-bottom: 1px solid #FFFFFF !important` (the etched separator, matching `widgets/line.svg`).
  - Add `findbar` with `background-color: #DDDDDD !important` and `border-top: 1px solid #000000 !important`, and `findbar .findbar-textbox:not([status="notfound"]):not([flash="true"]):not(:focus)` with `background-color: #FFFFFF !important`, `border: 1px solid #000000 !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px #999999 !important`; the guards leave Firefox's own red not-found wash, yellow flash and focus ring in place.
  - Extend the header's provenance paragraph to name the toolbar button states, bookmark items, menu separators and find bar among the sheet's adapted surfaces.
- `tests/test_firefox_theme.py`: add the three `:root` variables to `REQUIRED_RULES[":root"]` and add `REQUIRED_RULES` entries for the toolbar button states, bookmark-item, menuseparator and `::before`, findbar and findbar-textbox selectors, reusing the imported `BLACK`, `FACE`, `GREY`, `SELECTION`, `TROUGH` and `WHITE` values and importing `RAISED_BEVEL` from `support.gtk_theme_spec`; leave `test_palette_is_exact`'s expected set unchanged (every new declaration uses a value it already accepts).
- `docs/invariants.md`: extend the `## firefox` standalone-sheet guarantee sentence to name the toolbar button states, bookmark items, menu separators and find bar; keep its no-reference-screenshot provenance exception.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The sheet carries the pinned `:root` variables and the bookmark-item, menuseparator and findbar rules, and `test_required_rules` fails if any selector or declaration changes.
- `test_palette_is_exact` still passes with the same hex set, the sheet still contains no at-rule or import, and no selector is universal.
- `tests/invariants.py` accepts the updated `## firefox` row and `make check` is green.

### Platinum GTK meters and sliders: paint the progress-bar track and fill and the scale trough and thumb (planned 2026-10-23 by the plan role; independent of the waiting pointer plan) — done 2026-10-23 by the feature role

**Goal.** Both opt-in GTK sheets cover windows, buttons, entries, tabs, menus, scroll bars and toolbars, but they leave `GtkProgressBar` and `GtkScale` to the Adwaita fallback, so a file-copy meter or a volume slider still draws Adwaita's rounded blue track and thumb. Paint them from the Platinum art the theme already ships: the flat #EEEEEE trough with its 1px #000000 outline that `widgets/scrollbar.svg` and `widgets/slider.svg` ship, the #999999 sunken shadow `widgets/lineedit.svg` uses, the flat #CCCCFF selection for the progress fill (the reference progress gradient's middle row is `#CBCCFF`), and the desktop theme's raised #DDDDDD slider thumb from `widgets/slider.svg`. No reference screenshot shows a GTK widget, so the geometry stays this theme's adaptation, but every colour is an existing pinned Platinum palette value and the sheets stay standalone (no `@import`, no `url()`).

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the scrollbar rules, add these rules. Do not introduce a new hex literal anywhere in the file, including the header comment: `test_only_palette_hex_literals` scans the raw GTK 3 sheet text.
  - `progressbar trough`: `background-color: #EEEEEE; background-image: none; border: 1px solid #000000; border-radius: 0; box-shadow: inset 1px 1px #999999; min-height: 10px; min-width: 10px;`
  - `progressbar progress`: `background-color: #CCCCFF; background-image: none; border: 0; border-radius: 0; box-shadow: none; margin: 0;`
  - `progressbar progress:disabled`: `background-color: #999999;`
  - `scale trough`: the same declaration block as `progressbar trough` but `min-height: 6px; min-width: 6px;` (the desktop slider's 6px track).
  - `scale fill, scale highlight`: `background-color: transparent; background-image: none; border: 0; border-radius: 0; box-shadow: none; margin: 0;` (the desktop slider deliberately omits its `groove-highlight`, so the trough stays one uniform Platinum bar and the thumb marks the value).
  - `scale slider`: `background-color: #DDDDDD; background-image: none; border: 1px solid #000000; border-radius: 0; box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999; margin: -5px;`
  - `scale.horizontal slider`: `min-width: 12px; min-height: 16px;` and `scale.vertical slider`: `min-width: 16px; min-height: 12px;` (the desktop theme's two handle shapes).
  - `scale slider:hover, scale slider:active`: the same face, outline, square corners and bevel as the base `scale slider`, so no fallback hover colour shows through.
  - `scale slider:disabled`: `background-color: #DDDDDD; border: 1px solid #999999; box-shadow: none;`
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: add the same declarations with the GTK 4 node paths, immediately after the scrollbar rules:
  - `progressbar > trough` and `progressbar > trough > progress` (plus `progressbar > trough > progress:disabled`).
  - `scale > trough`, `scale > trough > fill, scale > trough > highlight`, `scale > trough > slider` (with `margin: -5px`), `scale.horizontal > trough > slider`, `scale.vertical > trough > slider`, `scale > trough > slider:hover, scale > trough > slider:active`, and `scale > trough > slider:disabled`, with the same values as the GTK 3 rules.
- `tests/test_gtk_theme.py`: add `test_progressbar` pinning the trough, fill and disabled-fill rules, and `test_scale` pinning the trough, the transparent fill/highlight, the base/hover/active/disabled thumb, and the 12x16 and 16x12 orientation sizes. Reuse the already-imported `BLACK`, `FACE`, `GREY`, `SELECTION`, `TROUGH` and `WHITE` values and `RAISED_BEVEL` from `support.gtk_theme_spec`.
- `tests/test_gtk4_theme.py`: add the matching `test_progressbar` and `test_scale` against the GTK 4 selectors and the same values; `DEFINED_COLOURS` is unchanged.
- `docs/invariants.md`: in the `## gtk` section, extend the GTK 3 and GTK 4 guarantee sentences to name the progress-bar and scale rules (and keep their existing no-reference-screenshot provenance exception).

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry the pinned progress-bar and scale rules, and `test_only_palette_hex_literals` still passes unchanged in both suites (every hex in either sheet remains a value that test already accepts; the new declarations use only `#000000`, `#999999`, `#DDDDDD`, `#EEEEEE`, `#FFFFFF` and `#CCCCFF`).
- The new tests fail if a track, fill, thumb face, outline, bevel, square corner, orientation size or state rule changes, and the GTK 4 sheet still passes `test_stands_alone` (no `@import`, no `url()`).
- `tests/invariants.py` accepts the updated `## gtk` rows and `make check` is green.

### Platinum pointer roles: ship the context-menu pointer and alias the resize, hand and cell roles (planned 2026-10-23 by the plan role; independent of the landed pager plan) — done 2026-10-23 by the feature role

**Goal.** The icon theme's `cursors/` names the Platinum pointers for the arrow, text, hand, busy, move, resize, crosshair, forbidden, drag-and-drop, help, progress, pencil and zoom roles, but several common Xcursor names still come from the fallback Breeze set: right-click uses `context-menu`, table and splitter borders use `col-resize`/`split_h` and `row-resize`/`split_v`, panning uses `openhand`/`closedhand`, and cell selection uses `cell`/`plus`. Add one new Platinum pointer for `context-menu` (the arrow beside a small menu panel) and alias the role-equivalent names to the already-shipped resize, grab and copy-plus art, so those roles stop changing shape when the Platinum cursor theme is selected. No reference screenshot shows a pointer, so the art stays our own `#000000`-face/`#FFFFFF`-outline drawing; the names and their Breeze byte groups are X/KDE-required values read from `/usr/share/icons/breeze_cursors/cursors` (`alias` and `link` share one file there, as do `cell` and `plus`, `col-resize` and `split_h`, `row-resize` and `split_v`, `openhand` and `grab`, and `closedhand` and `grabbing`).

**Approach.**
- `tools/cursor_art.py`: add `CONTEXT_MENU_HOTSPOT = (1, 1)` and `CONTEXT_MENU_GRID`, the arrow with a white-faced, black-bordered menu panel at x=8..14, y=9..14 carrying two black text bars:

  ```python
  CONTEXT_MENU_GRID = (
      "...             ",
      ".#..            ",
      ".##..           ",
      ".###..          ",
      ".####..         ",
      ".#####..        ",
      ".######..       ",
      ".#######..      ",
      ".########.      ",
      "....##..#######.",
      "   .##..#.....#.",
      "   .##..#.###.#.",
      "   .##..#.....#.",
      "   .##..#.##..#.",
      "   .##..#######.",
      "   ....         ",
  )
  ```

  Append `("context-menu", CONTEXT_MENU_GRID, CONTEXT_MENU_HOTSPOT, ())` to `CURSORS`, and extend the existing alias tuples: `size_hor` gains `col-resize` and `split_h`; `size_ver` gains `row-resize` and `split_v`; `dnd-copy` gains `cell` and `plus`; `grab` gains `openhand`; `grabbing` gains `closedhand`. Update the module docstring: the package ships twenty canonical pointers, and list `context-menu` and the new aliases.
- Run `python3 tools/make_cursors.py` to write `theme/icons/org.macos8.desktop/cursors/context-menu` and the eight new alias files. The alias files must be byte-identical to their canonical cursor, and the existing files must keep their bytes.
- `tests/test_cursors_theme.py`: add `context-menu` to `CANONICAL`, `ALIASES` (empty), `HOTSPOTS` (16 `(1, 1)`, 24 `(2, 2)`, 32 `(2, 2)`) and `PINNED_PIXELS` (face `(1, 1)`, outline `(0, 0)`); add the new aliases to the matching `ALIASES` tuples. Leave `TRANSPARENT_CORNER_CURSORS` unchanged: like `help` and `progress`, the context-menu pointer keeps the arrow's white top-left corner. Add `test_context_menu_pins_the_menu_panel`: at 16px black at `(1, 1)`, `(8, 9)`, `(8, 10)`, `(14, 10)`, `(10, 11)`, `(10, 13)`, `(11, 13)` and `(8, 14)`; white at `(0, 0)`, `(1, 9)`, `(2, 9)`, `(3, 9)`, `(7, 10)`, `(9, 10)` and `(15, 10)`. Extend `test_dnd_aliases_reuse_the_landed_glyphs` with `cell`/`plus` -> `dnd-copy`, `col-resize`/`split_h` -> `size_hor`, `row-resize`/`split_v` -> `size_ver`, `openhand` -> `grab` and `closedhand` -> `grabbing`.
- `tests/test_icon_theme.py`: add `context-menu` and the eight new alias names to `SHIPPED_CURSORS`, so the installed-package inventory test sees them.
- `README.md`: in the cursor sentence, name the new `context-menu` pointer and add each new alias to its existing group (`cell`, `plus` with `dnd-copy`; `col-resize`, `split_h` with `size_hor`; `row-resize`, `split_v` with `size_ver`; `openhand` with `grab`; `closedhand` with `grabbing`), and narrow the fallback sentence to the roles the theme still does not name.
- `docs/invariants.md`: extend the `icons` cursor row's canonical and alias lists with the new names; keep the provenance exception that no reference screenshot shows a pointer and that the names and byte groups are X/KDE-required.

**Files touched.** `tools/cursor_art.py`, `theme/icons/org.macos8.desktop/cursors/context-menu` and eight new alias files (generated), `tests/test_cursors_theme.py`, `tests/test_icon_theme.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- `cursors/context-menu` exists at nominal sizes 16, 24 and 32, with the hotspot at the arrow tip and a fresh-generator result; the focused pixel test fails if the menu panel or its text bars move.
- `cell`, `plus`, `col-resize`, `split_h`, `row-resize`, `split_v`, `openhand` and `closedhand` are byte-identical to `dnd-copy`, `size_hor`, `size_ver`, `grab` and `grabbing` as mapped above, and `tests/test_icon_theme.py` sees every new file.
- The README and the `icons` invariant row name the new pointer and aliases, `tests/invariants.py` accepts the row, and `make check` is green.

### Platinum virtual-desktop pager: ship `widgets/pager.svg` for the optional Pager applet (planned 2026-10-23 by the plan role) — done 2026-10-23 by the feature role

**Goal.** The optional Pager (`org.kde.plasma.pager`; `org.kde.plasma.activitypager` shares its QML through `X-Plasma-RootPath`) draws every virtual-desktop cell with `KSvg.FrameSvgItem imagePath: "widgets/pager"` in `contents/ui/main.qml`, one frame per prefix `normal`, `hover` and `active`. The theme ships no `widgets/pager.svg`, so KSvg falls back to Breeze's pager frames and a Pager added to the Platinum menu bar draws Breeze's cells. Add a Platinum pager frame: an idle desktop as a thin grey outline, a hovered desktop as the translucent pale grey view trough, and the current desktop as the translucent lavender selection fill. The reference set shows no virtual-desktop pager, so this is our own Platinum art; the three prefixes are KDE-required and the colours reuse grounded palette tokens.

**Approach.**
- Add `theme/desktoptheme/org.macos8.desktop/widgets/pager.svg` on a 12x9 canvas: a 1px border around a 10x7 centre tile. It declares exactly these ids: `hint-tile-center`; for each prefix `normal`, `hover` and `active`, the four `-hint-{top,bottom,left,right}-margin` rects and the nine `-{top,bottom,left,right,center,topleft,topright,bottomleft,bottomright}` slice groups (39 ids besides `hint-tile-center`).
- Hints: `hint-tile-center` at (1,1,10,7); top/bottom margins at (1,0,10,1)/(1,8,10,1); left/right margins at (0,1,1,7)/(11,1,1,7). Slice groups translate to (1,0), (1,8), (0,1), (11,1), (1,1), (0,0), (11,0), (0,8) and (11,8).
- Paint the states as follows: `normal` is a 1px `#999999` border on its eight edge and corner tiles with a transparent 0.01-opacity `#FFFFFF` placeholder for the centre (an idle desktop is an outlined cell on the panel face); `hover` is the same `#999999` border around an `#EEEEEE` centre at `fill-opacity="0.2"`; `active` is a 1px `#000000` border around a `#CCCCFF` centre at `fill-opacity="0.6"`. Each colour is a `fill` attribute; the centre placeholder uses `style` plus `fill-opacity="0.01"`, the menubaritem convention, so the parsed fill set stays the art colours. The Pager draws each desktop's window previews in `clipRect` at z:1 with the frames above at z:2-4, so opaque hover and active centres would hide them; 0.2 and 0.6 are the installed default theme's centre opacities.
- `tests/support/desktoptheme_paths.py`: add `PAGER_SVG = os.path.join(PACKAGE, "widgets", "pager.svg")`.
- `tests/test_desktoptheme.py`: import `PAGER_SVG` and add `("pager.svg", PAGER_SVG, 12, 9)` to `SVG_CANVASES`, so the shared root-canvas, unique-id, self-containment and registry tests cover the new file.
- Add `tests/test_desktoptheme_pager.py` with `TestPager(NineSliceCase)`: set `SVG_PATH = PAGER_SVG` and `PREFIXES = ("normal", "hover", "active")`; pin the exact 40-id set and the exact hint map with `rect_geometry`; pin `normal`'s eight `#999999` edge tiles plus its fill-less centre; pin every `hover` tile to `#999999` on the border and `#EEEEEE` in the centre; pin every `active` tile to `#000000` on the border and `#CCCCFF` in the centre; pin each centre's fill and `fill-opacity` (`normal` has no `fill` attribute, only the `style` `#FFFFFF` placeholder at `0.01`, while `hover` pins `#EEEEEE`/`0.2` and `active` pins `#CCCCFF`/`0.6`) and the whole file's `fill-opacity` set to exactly `{"0.01", "0.2", "0.6"}`; pin the parsed `fill` set to exactly `{"#000000", "#999999", "#CCCCFF", "#EEEEEE"}`. Use `nine_slice_tile_sizes(12, 9, 1, 1, 1, 1)` and `assert_slice_pixels` so a one-pixel-short rect or a recoloured tile fails.
- `README.md`: after the `widgets/menubaritem.svg` sentence, add that `widgets/pager.svg` draws the optional Pager's virtual-desktop cells: an idle `#999999` outline, a translucent `#EEEEEE` hover wash and the current desktop's translucent `#CCCCFF` selection, as one 1px-border nine-slice shared by such a panel applet.
- `docs/invariants.md`: add a `## desktoptheme` row for `widgets/pager.svg`, citing `tests/test_desktoptheme_pager.py::TestPager`; its provenance exception records that no reference screenshot shows a virtual-desktop pager, the `normal`/`hover`/`active` prefixes are KDE-required (read from the installed Pager's `contents/ui/main.qml`), the 12x9 tile is this theme's own, the 0.2 and 0.6 hover/active centre opacities are the installed default theme's (its frames sit above the window previews, so opaque centres would hide them), and the colours reuse the grounded bevel, trough, outline and selection anchors.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/pager.svg`, `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, new `tests/test_desktoptheme_pager.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- `pager.svg` exists on a 12x9 canvas and declares exactly the id set above; `tests/test_desktoptheme.py`'s registry sees it, and a missing or extra prefix, hint or slice id fails the id-set test.
- Every prefix's four hints and nine slice groups sit at the geometry above; moving a group or hint off its tile fails `NineSliceCase.test_tiles_placed_by_margins` or the hint-map test.
- `normal` renders eight `#999999` border tiles around a fill-less centre, `hover` renders `#999999` borders around an `#EEEEEE` centre at 0.2 opacity, and `active` renders `#000000` borders around an `#CCCCFF` centre at 0.6 opacity; changing one pixel, dropping a state or recolouring a slice fails the pixel tests.
- The README names the new widget and its three states, and `tests/invariants.py` accepts the new `## desktoptheme` row.
- `make check` is green.

### Platinum task-manager buttons: ship `widgets/tasks.svg` for the optional Task Manager applet (planned 2026-10-23 by the plan role; independent of the waiting icon series) — done 2026-10-23 by the feature role

**Goal.** The default layout draws the window list with `widgets/menubaritem.svg`, but the optional Task Manager (`org.kde.plasma.taskmanager`) draws every task through `KSvg.FrameSvgItem imagePath: "widgets/tasks"` (`Task.qml`, `main.qml`, `TaskProgressOverlay.qml`, `GroupExpanderOverlay.qml`). The theme ships no `widgets/tasks.svg`, so KSvg falls back to Breeze's task backgrounds and a Task Manager added to the Platinum menu bar draws Breeze task items instead of Platinum ones. Add the missing nine-slice and its four group-expander arrows. The reference set shows no KDE task manager, so this is our own Platinum art; the element names are KDE-required and the colours reuse the already-grounded tokens (#CCCCFF selection, #FFFFCC tooltip, #999999 bevel, #FFFFFF placeholder).

**Approach.**
- Add `theme/desktoptheme/org.macos8.desktop/widgets/tasks.svg` on the same 20x12 canvas and 7px left/right, 3px top/bottom, 6x6-centre contract as `widgets/menubaritem.svg`. It declares exactly these ids: `hint-tile-center`; for each prefix `normal`, `hover`, `focus`, `attention`, `minimized` and `progress`, the four `-hint-{top,bottom,left,right}-margin` rects and the nine `-{top,bottom,left,right,center,topleft,topright,bottomleft,bottomright}` slice groups; and `group-expander-{top,bottom,left,right}`.
- Every prefix's hints and slices use the menubaritem geometry: `hint-tile-center` at (7,3,6,6); top/bottom hints at (7,0,6,3)/(7,9,6,3); left/right hints at (0,3,7,6)/(13,3,7,6); slice groups translated to (7,0), (7,9), (0,3), (13,3), (7,3), (0,0), (13,0), (0,9) and (13,9).
- Paint the states as follows: `normal` is the transparent 0.01-opacity #FFFFFF placeholder in all nine tiles (an idle task shows the menu-bar face); `hover` and `focus` are flat #CCCCFF in every tile; `attention` is flat #FFFFCC in every tile; `minimized` is the placeholder in six tiles, but `minimized-bottom`, `minimized-bottomleft` and `minimized-bottomright` each paint a 2px #999999 rule at the bottom of their 3px band (local y=1, height 2; the bottom tile is 6px wide, the corner tiles 7px wide); `progress` is the same six placeholders with a 2px #CCCCFF bottom rule. The transparent states keep the `fill-opacity="0.01"` placeholder convention so the existing no-fill helpers read them as empty.
- Ship only the bare state prefixes. `TaskTools.taskPrefix` in the installed task manager's `code/tools.js` returns `[edge-prefixed, bare]` for every state, and `taskPrefixHovered` appends `hover` before the base state, so the bare `normal`/`hover`/`focus`/`attention`/`minimized`/`progress` elements resolve on a top, bottom, left or right panel without duplicating the art four ways. The group overlay is the exception: it names `elementId: "group-expander-<edge>"` directly, so ship all four arrows.
- Draw each group expander as an 8x8 black triangle: top `M1 6 L4 3 L7 6 Z`, bottom `M1 2 L4 5 L7 2 Z`, left `M6 1 L3 4 L6 7 Z`, right `M2 1 L5 4 L2 7 Z`.
- `tests/support/desktoptheme_paths.py`: add `TASKS_SVG = os.path.join(PACKAGE, "widgets", "tasks.svg")`.
- `tests/test_desktoptheme.py`: import `TASKS_SVG` and add `("tasks.svg", TASKS_SVG, 20, 12)` to `SVG_CANVASES`, so the shared root-canvas, unique-id, self-containment and registry tests cover the new file.
- Add `tests/test_desktoptheme_tasks.py` with `TestTasks(NineSliceCase)`: set `SVG_PATH = TASKS_SVG`, `PREFIXES = ("normal", "hover", "focus", "attention", "minimized", "progress")` and `EXTRA_GROUPS` mapping the four expander ids to (0,0); pin the exact hint map, the exact id set, the flat fills (`hover`/`focus` #CCCCFF, `attention` #FFFFCC), the `normal` placeholders, the minimized/progress bottom rules pixel by pixel, and each expander's path and fill.
- `README.md`: in the desktop-theme widget list, after the `widgets/menubaritem.svg` sentence, add that `widgets/tasks.svg` draws an optional Task Manager's idle (transparent), hover/focus (#CCCCFF), attention (#FFFFCC), minimized (#999999 rule) and progress (#CCCCFF rule) task faces as one 7px/3px nine-slice shared by every panel edge, plus the four group-expander arrows.
- `docs/invariants.md`: add a `## desktoptheme` row for `widgets/tasks.svg`, citing `tests/test_desktoptheme_tasks.py::TestTasks`; its provenance exception records that no reference screenshot shows a KDE task manager, the six state prefixes and four expander ids are KDE-required (read from the installed task manager's `Task.qml`, `TaskProgressOverlay.qml` and `GroupExpanderOverlay.qml`), and the colours reuse the grounded selection, tooltip and bevel tokens.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/tasks.svg`, `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, new `tests/test_desktoptheme_tasks.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- `tasks.svg` exists on a 20x12 canvas and declares exactly the id set above; `tests/test_desktoptheme.py`'s registry sees it, and a missing or extra prefix, hint or slice id fails the id-set test.
- Every prefix's four hints and nine slice groups sit at the menubaritem geometry; moving a group or hint off its tile fails `NineSliceCase.test_tiles_placed_by_margins` or the hint-map test.
- `normal` renders no fill (0.01-opacity #FFFFFF placeholders), `hover` and `focus` render flat #CCCCFF, `attention` flat #FFFFCC, and `minimized`/`progress` render a 2px #999999/#CCCCFF rule across the bottom band with transparent tiles above it; changing one pixel, dropping a state or recolouring a slice fails the pixel tests.
- The four `group-expander-*` elements are 8x8 black triangles with the paths above; removing or repointing one fails.
- The README names the new widget and its five states, and `tests/invariants.py` accepts the new `## desktoptheme` row.
- `make check` is green.

### Platinum icon theme, part 2/2: ship 16x16 and 22x22 renditions of the hard-disk and document icons (planned 2026-10-23 by the plan role; "requires part 1/2 landed") — done 2026-10-23 by the feature role

**Goal.** After part 1/2 the places icons have small-size renditions, but `drive-harddisk` and `text-x-generic` still ship only at 32x32, and `index.theme` declares no 16x16 or 22x22 devices or mimetypes directory. Add four renditions and the four directory declarations so the hard disk and document icons also have purpose-drawn art at menu, tree-view and small desktop sizes. The art is our own drawing on the same four-fill Platinum palette as the places art; the reference set has no pixel ground truth for the icon theme, as `docs/invariants.md`'s `## icons` row records.

**Approach.**
- Add these files, each an `<svg>` whose `width`, `height` and `viewBox` are the declared size:
  - `theme/icons/org.macos8.desktop/16x16/devices/drive-harddisk.svg` (nine elements): rect `x=1 y=3 width=14 height=10` `#000000`; rect `x=2 y=4 width=12 height=8` `#DDDDDD`; rect `x=2 y=4 width=12 height=1` `#FFFFFF`; rect `x=2 y=4 width=1 height=8` `#FFFFFF`; rect `x=2 y=11 width=12 height=1` `#999999`; rect `x=13 y=4 width=1 height=8` `#999999`; rect `x=3 y=7 width=7 height=3` `#000000`; rect `x=4 y=8 width=5 height=1` `#FFFFFF`; circle `cx=12 cy=9 r=1` `#000000`.
  - `theme/icons/org.macos8.desktop/22x22/devices/drive-harddisk.svg` (nine elements): rect `x=2 y=4 width=18 height=15` `#000000`; rect `x=3 y=5 width=16 height=13` `#DDDDDD`; rect `x=3 y=5 width=16 height=2` `#FFFFFF`; rect `x=3 y=5 width=1 height=13` `#FFFFFF`; rect `x=3 y=17 width=16 height=1` `#999999`; rect `x=18 y=5 width=1 height=13` `#999999`; rect `x=4 y=10 width=8 height=4` `#000000`; rect `x=5 y=11 width=6 height=2` `#FFFFFF`; circle `cx=15 cy=12 r=2` `#000000`.
  - `theme/icons/org.macos8.desktop/16x16/mimetypes/text-x-generic.svg` (six elements): path `M3 1 h7 l3 3 v10 H3 Z` `#000000`; path `M4 2 h5 l3 3 v8 H4 Z` `#FFFFFF`; path `M9 2 L12 2 L12 5 Z` `#DDDDDD`; rect `x=5 y=7 width=6 height=1` `#999999`; rect `x=5 y=9 width=6 height=1` `#999999`; rect `x=5 y=11 width=4 height=1` `#999999`.
  - `theme/icons/org.macos8.desktop/22x22/mimetypes/text-x-generic.svg` (six elements): path `M4 1 h10 l4 4 v15 H4 Z` `#000000`; path `M5 2 h8 l4 4 v13 H5 Z` `#FFFFFF`; path `M13 2 L17 2 L17 6 Z` `#DDDDDD`; rect `x=7 y=10 width=8 height=1` `#999999`; rect `x=7 y=13 width=8 height=1` `#999999`; rect `x=7 y=16 width=5 height=1` `#999999`.
- `theme/icons/org.macos8.desktop/index.theme`: append `16x16/devices,16x16/mimetypes,22x22/devices,22x22/mimetypes` to `Directories`, and add four sections with `Size=16`/`Size=22`, `Context=Devices`/`Context=MimeTypes` and `Type=Fixed`.
- `tests/test_icon_theme.py`: add the four new paths to `SHIPPED_ICONS`; add each file to `ICON_SHAPES` with the exact element tuple above, using the existing `_shape` helper and document order. `TestIndex.test_every_shipped_icon_lives_in_a_declared_size_directory` then proves the four new directories are declared.
- `README.md`: in the icon-theme sentence (the lines that currently read `ships our own Platinum-style art for the desktop's hard-disk, folder, document, Trash and full-Trash icons`), add that the package draws these at 32x32 with 16x16 and 22x22 renditions. Do not touch the cursor sentence on the following line.

**Files touched.** `tests/test_icon_theme.py`, `theme/icons/org.macos8.desktop/index.theme`, `README.md`, and four new SVGs under `theme/icons/org.macos8.desktop/16x16/{devices,mimetypes}/` and `22x22/{devices,mimetypes}/`.

**Acceptance criteria.**
- The four files exist; each parses as an SVG whose width, height and viewBox equal 16 or 22, each fill is one of the four `PLATINUM_FILLS`, and each has no script, style, external reference or duplicate id.
- `index.theme` declares `16x16/devices`, `16x16/mimetypes`, `22x22/devices` and `22x22/mimetypes` in `Directories`, with the matching `Size`, `Context` and `Type` sections; `TestIndex` passes for every shipped icon.
- `ICON_SHAPES` equals `SHIPPED_ICONS`, and each new file's drawing elements equal the tuple above in document order. Deleting an element, changing a coordinate or fill, moving an element or dropping a size fails a test.
- The 32x32 art and the part 1/2 places renditions keep their pinned elements unchanged.
- `README.md` names the 16x16 and 22x22 renditions without claiming a size for the cursor set, and the cursor sentence is untouched.
- `make check` is green.

### Platinum icon theme, part 1/2: ship 16x16 and 22x22 renditions of the folder, directory and Trash icons (planned 2026-10-23 by the plan role; part 2/2 adds the hard-disk and document renditions) — done 2026-10-23 by the feature role

**Goal.** `theme/icons/org.macos8.desktop/index.theme` declares `16x16/places` and `22x22/places`, but those directories hold no `folder`, `inode-directory`, `user-trash` or `user-trash-full` file: the package ships those four names only at 32x32. Add eight pixel-aligned renditions so a menu, tree view or small desktop icon can draw a dedicated Platinum shape at its own size instead of relying on the 32x32 art. The 32x32 art is our own drawing, and `docs/invariants.md`'s `## icons` row records that the reference set has no pixel ground truth for the icon theme; these renditions are our own simplified redraws using only the four pinned palette fills (`#000000` outline, `#DDDDDD` face, `#FFFFFF` top/left bevel, `#999999` bottom/right bevel), not traced from Apple's artwork.

**Approach.**
- Add these files, each an `<svg>` whose `width`, `height` and `viewBox` are the directory's declared size:
  - `theme/icons/org.macos8.desktop/16x16/places/folder.svg` (six elements, in order): path `M1 4 h5 l2 2 h6 v7 H1 Z` `#000000`; path `M2 5 h4 l2 2 h5 v4 H2 Z` `#DDDDDD`; path `M2 5 h4 l2 2 h5 v1 h-5 l-2 -2 h-4 Z` `#FFFFFF`; rect `x=2 y=5 width=1 height=6` `#FFFFFF`; rect `x=2 y=11 width=11 height=1` `#999999`; rect `x=12 y=8 width=1 height=3` `#999999`.
  - `theme/icons/org.macos8.desktop/22x22/places/folder.svg` (six elements): path `M2 6 h7 l3 3 h8 v8 H2 Z` `#000000`; path `M3 7 h6 l3 3 h7 v6 H3 Z` `#DDDDDD`; path `M3 7 h6 l3 3 h7 v1 h-7 l-3 -3 h-6 Z` `#FFFFFF`; rect `x=3 y=7 width=1 height=8` `#FFFFFF`; rect `x=3 y=15 width=16 height=1` `#999999`; rect `x=18 y=10 width=1 height=5` `#999999`.
  - `theme/icons/org.macos8.desktop/16x16/places/inode-directory.svg` and `22x22/places/inode-directory.svg`: the same drawing elements as the matching `folder.svg`, in the same order; only the comment differs, saying the alias shares the folder geometry because Mac OS 8.6 draws one folder shape for both names.
  - `theme/icons/org.macos8.desktop/16x16/places/user-trash.svg` (ten elements): rect `x=6 y=1 width=4 height=2` `#000000`; rect `x=7 y=2 width=2 height=1` `#DDDDDD`; rect `x=3 y=3 width=10 height=3` `#000000`; rect `x=4 y=4 width=8 height=2` `#DDDDDD`; rect `x=4 y=4 width=8 height=1` `#FFFFFF`; rect `x=4 y=5 width=8 height=1` `#999999`; path `M5 6 h6 l-1 9 H6 Z` `#000000`; path `M6 7 h4 l-1 7 H7 Z` `#DDDDDD`; rect `x=7 y=8 width=1 height=5` `#999999`; rect `x=8 y=8 width=1 height=5` `#FFFFFF`.
  - `theme/icons/org.macos8.desktop/22x22/places/user-trash.svg` (twelve elements): rect `x=8 y=1 width=6 height=3` `#000000`; rect `x=9 y=2 width=4 height=2` `#DDDDDD`; rect `x=4 y=4 width=14 height=4` `#000000`; rect `x=5 y=5 width=12 height=3` `#DDDDDD`; rect `x=5 y=5 width=12 height=1` `#FFFFFF`; rect `x=5 y=7 width=12 height=1` `#999999`; path `M6 8 h10 l-1 12 H7 Z` `#000000`; path `M7 9 h8 l-1 10 H8 Z` `#DDDDDD`; rect `x=9 y=11 width=1 height=8` `#999999`; rect `x=10 y=11 width=1 height=8` `#FFFFFF`; rect `x=12 y=11 width=1 height=8` `#999999`; rect `x=13 y=11 width=1 height=8` `#FFFFFF`.
  - `theme/icons/org.macos8.desktop/16x16/places/user-trash-full.svg` (ten elements): the two paper paths path `M6 0 l2 1 l2 -1 l1 4 h-6 Z` `#000000` and path `M7 1 l1 1 l1 -1 l1 3 h-4 Z` `#FFFFFF`, then the `user-trash.svg` elements from its rim outline through its white rib (elements 3-10 above), in the same order.
  - `theme/icons/org.macos8.desktop/22x22/places/user-trash-full.svg` (twelve elements): the two paper paths path `M8 0 l3 2 l3 -2 l1 6 h-8 Z` `#000000` and path `M9 1 l2 1 l2 -1 l1 4 h-6 Z` `#FFFFFF`, then the `22x22/places/user-trash.svg` elements from its rim outline through its last white rib (elements 3-12 above), in the same order.
- `theme/icons/org.macos8.desktop/index.theme`: no change; `16x16/places` and `22x22/places` are already declared with `Size=16`/`Size=22`, `Context=Places` and `Type=Fixed`.
- `tests/test_icon_theme.py`: add the eight new paths to `SHIPPED_ICONS`; add each file to `ICON_SHAPES` with the exact element tuple listed above, using the existing `_shape` helper and the same document order. Extend `TestIconGeometry.test_the_folder_alias_shares_the_folder_art` to compare the `folder.svg` and `inode-directory.svg` drawings at 16x16, 22x22 and 32x32, so the alias cannot drift at a new size.
- `README.md` and `docs/invariants.md`: no change here. The existing README sentence names the icon art without claiming a size, and the existing `## icons` guarantee (`Every shipped icon draws its pinned drawing elements in document order`) already covers these files because `TestIconGeometry.test_the_geometry_registry_covers_every_shipped_icon` requires `ICON_SHAPES` to equal `SHIPPED_ICONS`. Part 2/2 updates the README sentence once the complete set of renditions ships.

**Files touched.** `tests/test_icon_theme.py` and eight new SVGs under `theme/icons/org.macos8.desktop/16x16/places/` and `22x22/places/`.

**Acceptance criteria.**
- The eight files exist; each parses as an SVG whose width, height and viewBox equal 16 or 22, each fill is one of the four `PLATINUM_FILLS`, and each has no script, style, external reference or duplicate id.
- `TestIndex` sees the eight files in its declared directories, `TestIconGeometry.test_the_geometry_registry_covers_every_shipped_icon` sees `ICON_SHAPES` equal to the shipped set, and every new file's drawing elements equal the tuple above in document order.
- The `inode-directory` drawing elements equal the matching `folder` elements at 16x16, 22x22 and 32x32.
- Deleting an element, changing a coordinate or fill, moving an element, dropping a size, or drawing an alias differently from its folder fails a test.
- `make check` is green.

### Platinum cursor set, part 4: ship the help, progress, pencil and zoom pointers (planned 2026-10-23 by the plan role; completes the cursor set after the landed parts 1-3) — done 2026-10-23 by the feature role

**Goal.** The icon theme's `cursors/` covers fourteen pointers; README records that `help`,
`progress`, `pencil`, `zoom-in` and `zoom-out` still come from the fallback cursor theme, so the
busy, help, drawing and zoom pointer roles change shape when the Platinum theme is selected. Add
the five remaining pointers and their aliases: `help` (the landed arrow plus a question mark),
`progress` (the arrow plus a small hourglass), `pencil` (a diagonal pencil), and `zoom-in` /
`zoom-out` (a magnifier with a plus or minus). No reference screenshot shows a pointer, so the art
stays our own `#000000`-face/`#FFFFFF`-outline drawing. The canonical names are X/KDE-required and
taken from the installed Breeze set (`/usr/share/icons/breeze_cursors/cursors`): `help`,
`left_ptr_help`, `question_arrow` and `whats_this` share one byte group there with the hash
aliases `5c6cd98b3f3ebcb1f9c7f1c204630408` and `d9ce0ab605698f320427677b458ad60b`; `progress`,
`half-busy` and `left_ptr_watch` share another with the hash aliases
`00000000000000020006000e7e9ffc3f`, `08e8e1c95fe2fc01f976f1e063a24ccd` and
`3ecb610c1bf2410f44200f48c40d3599`; `pencil`, `zoom-in` and `zoom-out` have no aliases there
(checked with `md5sum` over that directory).

**Approach.**
- `tools/cursor_art.py`: add five 16x16 grids in the existing `#` face / `.` white / space
transparent vocabulary and append them to `CURSORS`; `tools/make_cursors.py` needs no change.
  - `HELP_HOTSPOT = (1, 1)`; `HELP_GRID`: `ARROW_GRID` with a question mark stamped in the free
    right-hand area -- a white plate at columns 9-14, rows 2-8 carrying a black top bar
    `(10,3)-(13,3)`, a right stem `(13,4)-(13,5)`, a curve at `(12,5)` and a black dot `(12,7)`,
    with white at `(12,6)` separating the hook from the dot.
  - `PROGRESS_HOTSPOT = (1, 1)`; `PROGRESS_GRID`: `ARROW_GRID` with a white plate at columns
    9-14, rows 8-14 carrying a black hourglass -- a top bar `(10,9)-(13,9)`, a two-pixel-wide
    neck `(11,10)-(12,12)` and a bottom bar `(10,13)-(13,13)`, with white rows at 8 and 14.
  - `PENCIL_HOTSPOT = (2, 14)`; `PENCIL_GRID`: a two-pixel black shaft on the anti-diagonal
    `x+y = 15`/`16` from the writing tip `(2,14)` to the eraser `(13,2)`, each black edge bounded
    by one white cell; black at `(2,14)`, `(8,7)` and `(12,3)`, white at `(1,14)` and `(13,1)`.
  - `ZOOM_IN_HOTSPOT = (7, 7)` and `ZOOM_OUT_HOTSPOT = (7, 7)`; the two grids share a
    white-outlined black lens ring centred on `(7,7)` (black at `(7,3)`, `(3,7)`, `(11,7)`,
    `(7,11)` and white at `(7,2)`), a black handle along `(11,11)-(13,13)` (black at `(13,13)`),
    and a black plus in the lens at `(7,5)`, `(5,7)`, `(9,7)`, `(7,9)` and `(7,7)`; `ZOOM_OUT_GRID`
    keeps only the horizontal bar of the plus, leaving `(7,5)` and `(7,9)` transparent.
  - Append `("help", HELP_GRID, HELP_HOTSPOT, ("left_ptr_help", "question_arrow", "whats_this",
    "5c6cd98b3f3ebcb1f9c7f1c204630408", "d9ce0ab605698f320427677b458ad60b"))`,
    `("progress", PROGRESS_GRID, PROGRESS_HOTSPOT, ("half-busy", "left_ptr_watch",
    "00000000000000020006000e7e9ffc3f", "08e8e1c95fe2fc01f976f1e063a24ccd",
    "3ecb610c1bf2410f44200f48c40d3599"))`,
    `("pencil", PENCIL_GRID, PENCIL_HOTSPOT, ())`,
    `("zoom-in", ZOOM_IN_GRID, ZOOM_IN_HOTSPOT, ())` and
    `("zoom-out", ZOOM_OUT_GRID, ZOOM_OUT_HOTSPOT, ())` to `CURSORS`.
  - Update `tools/cursor_art.py`'s module docstring: the package ships nineteen canonical cursors, not fourteen, and
    list the new names and their aliases.
- `tests/test_cursors_theme.py`: extend `CANONICAL` with the five names and `ALIASES` with their
  alias tuples (empty for `pencil`, `zoom-in` and `zoom-out`). Add the five names to `HOTSPOTS` --
  `help`/`progress`: `(1,1)` at 16, `(2,2)` at 24, `(2,2)` at 32; `pencil`: `(2,14)`, `(3,21)`,
  `(4,28)`; `zoom-in`/`zoom-out`: `(7,7)`, `(11,11)`, `(14,14)` -- and to `PINNED_PIXELS` (face
  `(1,1)` / outline `(0,0)` for `help` and `progress`; face `(2,14)` / outline `(1,14)` for
  `pencil`; face `(7,7)` / outline `(7,2)` for `zoom-in` and `zoom-out`). Add `pencil`, `zoom-in`
  and `zoom-out` to `TRANSPARENT_CORNER_CURSORS`; `help` and `progress` keep the arrow's white
  top-left corner, so they stay out. The existing `TestCursorSet` loops then cover the new files,
  aliases, hotspots, face/outline pixels and determinism. Add focused tests:
  - `test_help_pins_the_arrow_and_question_mark`: at 16px black at `(1,1)`, `(10,3)`, `(13,5)` and
    `(12,7)`; white at `(0,0)` and `(12,6)`.
  - `test_progress_pins_the_arrow_and_hourglass`: at 16px black at `(1,1)`, `(10,9)`, `(11,10)`,
    `(11,11)`, `(11,12)`, `(12,11)` and `(10,13)`; white at `(12,8)` and `(12,14)`.
  - `test_pencil_draws_a_diagonal_shaft_to_its_writing_tip`: at 16px black at `(2,14)`, `(8,7)`
    and `(12,3)`; white at `(1,14)` and `(13,1)`; all four corners transparent.
  - `test_zoom_in_and_out_differ_only_at_the_plus_arms`: at 16px both have black at `(7,3)`,
    `(3,7)`, `(7,11)` and the handle tip `(13,13)`, and white at `(7,2)`; `zoom-in` is black at
    `(7,5)`, `(5,7)`, `(9,7)` and `(7,9)`, while `zoom-out` is black only at `(5,7)` and `(9,7)`
    and transparent at `(7,5)` and `(7,9)`.
  - `test_help_and_progress_alias_names_reuse_their_canonical`: `left_ptr_help`, `question_arrow`,
    `whats_this` and the two `help` hash names are byte-identical to `help`; `half-busy`,
    `left_ptr_watch` and the three `progress` hash names to `progress`.
- Regenerate the artifacts with `python3 tools/make_cursors.py` (deterministic output).
- `tests/test_icon_theme.py`: add the fifteen new X names (`help`, `left_ptr_help`, `question_arrow`,
  `whats_this`, `5c6cd98b3f3ebcb1f9c7f1c204630408`, `d9ce0ab605698f320427677b458ad60b`, `progress`,
  `half-busy`, `left_ptr_watch`, `00000000000000020006000e7e9ffc3f`,
  `08e8e1c95fe2fc01f976f1e063a24ccd`, `3ecb610c1bf2410f44200f48c40d3599`, `pencil`, `zoom-in`,
  `zoom-out`) to `SHIPPED_CURSORS`, so the shipped-file registry and the shared install-lifecycle
  list cover them.
- `README.md`: name the five new pointers and their aliases in the cursor sentence, and replace the
  fallback sentence with "Xcursor roles the theme does not name still come from the fallback cursor
  theme".
- `docs/invariants.md`: extend the `## icons` cursor row to name all nineteen canonical files and
  every alias, still citing `tests/test_cursors_theme.py::TestCursorArtifact` and `::TestCursorSet`;
  extend the provenance exception: no reference screenshot shows the pointer, the help, progress
  and zoom names are X/KDE-required and taken from the installed Breeze set, and the help/progress
  alias groups follow Breeze's byte groups while `pencil`, `zoom-in` and `zoom-out` have no alias.
- `PLANS.md`: in the scope-drift paragraph, add the help, progress, pencil and zoom pointers to the
  shipped cursor clause, and say Xcursor roles the theme does not name still fall back.

**Files touched.** `tools/cursor_art.py`, `tests/test_cursors_theme.py`,
`tests/test_icon_theme.py`, the new binaries under `theme/icons/org.macos8.desktop/cursors/`
(five canonical names and ten alias names), `README.md`, `docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the five new canonical files and the ten aliases; running
  it twice leaves every committed cursor byte-identical, and each new canonical parses to three
  chunks at nominal sizes 16/24/32 with its pinned hotspot, black face pixel and white outline
  pixel, and the pencil and zoom files keep transparent corners.
- The focused tests pin the arrow-plus-question-mark, the arrow-plus-hourglass, the diagonal
  pencil and the plus/minus magnifiers; deleting a grid, dropping a size, moving a hotspot,
  drawing `zoom-out` as a copy of `zoom-in`, or losing the pencil's white outline fails a test.
- `left_ptr_help`, `question_arrow`, `whats_this`, the two `help` hash names, `half-busy`,
  `left_ptr_watch` and the three `progress` hash names are byte-identical to their canonical
  files; the generator writes exactly the fifteen new names into a temp directory.
- `tests/test_icon_theme.py`'s shipped-file registry and install lifecycle include all fifteen new
  names; README and `docs/invariants.md` name them; `tests/invariants.py` accepts the updated
  `## icons` row; the scope-drift clause no longer lists help, progress, pencil or zoom as
  fallback.
- `make check` is green.

### Retire the `no-fake` validation gap with a fixture ledger (planned 2026-10-23 by the steward role; promotes the recurring `gap: no-fake` tag, 16 Fixed entries) — done 2026-10-23 by the feature role

**Goal.** Sixteen Fixed entries in BUGS-FIXED.md carry `gap: no-fake` — confirming the failure
needed a fake, shim or manufactured fixture the shipped suite did not have. The shared fixture kit
those records needed now exists (`symlinked_repo` in `tests/support/symlink_fixtures.py`, the
scratch/mutation helpers in `tests/support/checker_scratch.py`, `tests/support/invariants_mutations.py`
and `tests/support/placeholders_mutations.py`, and the chunk builders in
`tests/support/png_fixtures.py`), and the fixes have reproducing tests, but no ledger maps the
records to those fixtures and nothing stops a new `no-fake` record landing uncovered. Add the third
validation-gap ledger, mirroring the `no-observability` and `unclear-invariant` ones, and give the
one hand-assembled PNG stream a named builder, so a future no-fake failure lands with a fixture and
a test instead of growing the tag.

**Cited entries.** The sixteen `gap: no-fake` records in BUGS-FIXED.md:
- Symlink-escape fixtures (7): `tests/placeholders.py`'s `cross_check` reads a symlinked
  `PLACEHOLDERS.md` bare; `tests/invariants.py`'s `cross_check` reads a symlinked register bare;
  `tests/support/checker_mutations.py`'s register reads follow a symlinked register outside the
  repository; The color-scheme provenance test reads `MacOS8.colors` unguarded; The desktop-theme
  copy-identity tests read the secondary SVG copy unguarded; `tests/support/splash_fixtures.py`'s
  `read_qml` follows a symlinked `Splash.qml` outside the repository;
  `tests/support/package_metadata.py`'s `load_metadata` follows a symlinked `metadata.json`
  outside the repository.
- Unreadable / non-UTF-8 / dangling-path fixtures (4): `tests/invariants.py`'s `cross_check` lets
  an unreadable register escape as a bare `OSError`; `tests/support/package_metadata.py` lets an
  unreadable `metadata.json` escape as a bare `OSError`; `tests/placeholders.py` lets an unreadable
  register escape as a bare `OSError`; `tests/placeholders.py` lets a dangling symlink inside
  `theme/` escape as a bare `FileNotFoundError`.
- Process fixtures (2): A FIFO at either Firefox profile-discovery INI file blocks the install;
  A FIFO at a Firefox profile file blocks the install forever.
- Manufactured inputs (3): A palette image with `tRNS` before `PLTE` is accepted;
  `tests/invariants.py` lets a register reference with a NUL byte escape as an unrelated
  exception; `tests/invariants.py` lets a reference to an unreadable test file escape as an
  unrelated exception.

**Approach.**
- `tests/support/png_fixtures.py`: add `palette_trns_before_plte()`, returning the record's stream
  (`png_stream(ihdr_chunk(1, 1, 3), _chunk(b"tRNS", bytes([0, 128])), _chunk(b"PLTE", bytes([255,
  0, 0, 0, 255, 0])), _chunk(b"IDAT", zlib.compress(bytes([0, 0]))), _chunk(b"IEND", b""))`), so
  the malformed-order case has a named fixture rather than a hand-assembled chunk list.
  `tests/test_png_malformed.py::TestTrnsColorTypeValidation::test_palette_trns_before_plte_is_refused`
  calls the builder and keeps its two-decoder assertion and its `tRNS chunk before` / `PLTE chunk` /
  `follow` needles.
- `tests/support/validation_gaps.py`: name the third tag in the module docstring; add
  `NO_FAKE_BASELINE = 16`; add `NO_FAKE_REPRODUCTIONS`, reusing the `Reproduction` namedtuple
  (name, markers, reference), with one entry per record — markers name the module and the failure,
  and the reference is the reproducing test:
  - `firefox-ini-fifo` → `tests/test_firefox_install.py::TestProfileResolution::test_a_fifo_at_either_ini_file_is_refused_without_blocking`.
  - `firefox-profile-file-fifo` → `tests/test_firefox_install.py::TestRemove::test_a_fifo_at_either_profile_file_is_refused_without_blocking`.
  - `png-trns-before-plte` → `tests/test_png_malformed.py::TestTrnsColorTypeValidation::test_palette_trns_before_plte_is_refused`.
  - `placeholders-symlinked-register` → `tests/test_placeholders.py::TestHelpers::test_cross_check_refuses_a_symlinked_register_that_escapes`.
  - `invariants-symlinked-register` → `tests/test_invariants.py::TestHelpers::test_cross_check_refuses_a_symlinked_register_that_escapes`.
  - `checker-mutations-symlinked-register` → `tests/test_checker_mutations.py::TestCheckerMutations::test_register_reads_refuse_a_symlink_escape`.
  - `colorscheme-provenance-symlink` → `tests/test_containment.py::TestReadText::test_rejects_a_symlink_that_escapes_the_root`.
  - `desktoptheme-copy-symlink` → `tests/test_containment.py::TestReadBytes::test_rejects_a_symlink_that_escapes_the_root`.
  - `splash-symlink` → `tests/test_splash_qml.py::TestSplashQmlContainment::test_rejects_a_symlink_that_escapes_the_repository`.
  - `metadata-symlink` → `tests/test_package_metadata.py::TestLoadMetadataContainment::test_rejects_a_symlink_that_escapes_the_repository`.
  - `invariants-unreadable-register` → `tests/test_invariants.py::TestHelpers::test_cross_check_rejects_an_unreadable_register`.
  - `metadata-unreadable` → `tests/test_package_metadata.py::TestLoadMetadata::test_unreadable_file_names_the_path`.
  - `placeholders-unreadable-register` → `tests/test_placeholders.py::TestHelpers::test_register_entries_rejects_an_unreadable_register`.
  - `placeholders-dangling-symlink` → `tests/test_placeholders.py::TestHelpers::test_markers_rejects_a_dangling_symlink_within_the_theme_root`.
  - `invariants-nul-row` → `tests/test_invariants.py::TestHelpers::test_cross_check_rejects_a_reference_with_a_nul_byte`.
  - `invariants-unreadable-test-file` → `tests/test_checker_mutations.py::TestCheckerMutations::test_invariants_mutations` (which drives the `unreadable-test-file` mutation).
  Add `no_fake(records)` filtering the tag, `no_fake_reproduction(record)` using the existing
  `_lookup`, and extend `reproduction_for` to dispatch `no-fake` and say so in its docstring.
- `tests/test_validation_gaps.py`: update the module docstring to three ledgers; add
  `TestNoFakeLedger` mirroring `TestNoObservabilityLedger`: every `no-fake` record names a
  reproduction, every reproduction reference is a real test via `check_reference`, every entry
  covers a shipped record, the record count is at most `NO_FAKE_BASELINE` (message tells the next
  author to add an entry and raise the baseline by one), and an unmatched mechanism returns `None`.
- `docs/invariants.md`: extend the tooling row that names the two existing ledgers to name the
  `no-fake` ledger and `tests/test_validation_gaps.py::TestNoFakeLedger`.

**Files touched.** `tests/support/png_fixtures.py`, `tests/support/validation_gaps.py`,
`tests/test_png_malformed.py`, `tests/test_validation_gaps.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The task's gap query over BUGS.md and BUGS-FIXED.md returns the 16 `no-fake` records; each
  resolves to exactly one `NO_FAKE_REPRODUCTIONS` entry and each entry covers a shipped record.
- Every reproduction reference names a real test, so a deleted or misspelled reference fails
  `check_reference`; a new `no-fake` record without an entry, or a count above 16, fails the suite.
- The palette `tRNS`-before-`PLTE` test still refuses on both decode paths through the named
  builder; reversing the builder's chunk order or changing its payload fails the test.
- `tests/invariants.py` accepts the updated tooling row, and `make check` is green.

### Platinum panel edit-mode chrome, part 2/2: ship the panel resize and slider handles (planned 2026-10-23 by the plan role; follows the landed part 1/2 margin highlight) — done 2026-10-23 by the feature role

**Goal.** The desktop theme ships no `widgets/containment-controls.svg`, so while a panel is in
edit mode its offset, minimum and maximum drag handles and its centre indicators come from the
default theme's blue-grey artwork. Ship our own `widgets/containment-controls.svg` for the
twenty-six element ids the installed panel configuration and its ruler resolve, drawn as raised
Platinum thumbs, a black-edged face band and lavender centre lines. No reference screenshot
shows panel edit mode, so the art is our own: the element ids are KDE-required (its consumers
name them), the frame slice and indicator geometry plus the indicator opacity are the installed
default theme's, and the 9x9 slider size is this theme's own. The colours reuse the grounded
Platinum face/bevel palette and the `#CCCCFF` selection anchor.

**Approach.**
- New `theme/desktoptheme/org.macos8.desktop/widgets/containment-controls.svg`: a `<svg
width="42" height="42" viewBox="0 0 42 42">` whose twenty-six consumers are id-bearing `<g>`
elements at the origin, each holding rects with 0-based coordinates so KSvg reads that group's
bounding box as its natural size. Open with a comment naming the consumers
(`PanelConfiguration.qml` sets the north/south/east/west prefix, `Ruler.qml` is a
`KSvg.FrameSvgItem` for that prefix and asks for the two centre indicators, and
`SliderHandle.qml` builds `prefix + '-' + graphicElementName`), the ids,
and the provenance exception.
  - The twelve ruler frame groups are `north-center`, `north-top`, `north-bottom` and the
same three for `south`, plus `east-center`, `east-left`, `east-right` and the same three for
`west`. A horizontal ruler's top/bottom strips are 10x1 black and its centre 10x12 #DDDDDD; a
vertical ruler's left/right strips are 1x10 black and its centre 12x10 #DDDDDD, so the band is
14px thick. The geometry is the installed default theme's.
  - The twelve slider groups are `north-offsetslider`, `north-minslider`, `north-maxslider`,
`north` repeated for `south`, `east` and `west`. Each is a 9x9 raised Platinum thumb painted in
this document order (later rects override earlier ones, the slider.svg rule):
`<rect width="9" height="9" fill="#DDDDDD"/>`; `<rect y="1" width="9" height="1"
fill="#FFFFFF"/>`; `<rect y="7" width="9" height="1" fill="#999999"/>`; `<rect x="1"
width="1" height="9" fill="#FFFFFF"/>`; `<rect x="7" width="1" height="9"
fill="#999999"/>`; then the four outline rects `<rect width="9" height="1"
fill="#000000"/>`, `<rect y="8" width="9" height="1" fill="#000000"/>`, `<rect width="1"
height="9" fill="#000000"/>` and `<rect x="8" width="1" height="9" fill="#000000"/>`.
  - The grip is the last rect of each slider group: the four offset sliders carry a 3x3 black
centre dot `<rect x="3" y="3" width="3" height="3" fill="#000000"/>`; the north/south
min/max sliders carry a vertical 1x5 black bar `<rect x="4" y="2" width="1" height="5"
fill="#000000"/>`; the east/west min/max sliders carry the horizontal 5x1 bar `<rect x="2"
y="4" width="5" height="1" fill="#000000"/>`.
  - The two centre indicators are `vertical-centerindicator` (a vertical panel stretches it
across the panel width) with one `<rect width="42" height="1" fill="#CCCCFF"
fill-opacity="0.4"/>`, and `horizontal-centerindicator` (a horizontal panel stretches it down
the panel height) with one `<rect width="1" height="42" fill="#CCCCFF"
fill-opacity="0.4"/>`. The 42x1/1x42 natural geometry and the 0.4 opacity are the installed
default theme's; the colour is the grounded selection lavender.
- `tests/support/desktoptheme_paths.py`: add `CONTAINMENT_CONTROLS_SVG` pointing at
`widgets/containment-controls.svg`.
- `tests/test_desktoptheme.py`: add `("containment-controls.svg", CONTAINMENT_CONTROLS_SVG,
42, 42)` to `SVG_CANVASES` and `os.path.join("widgets", "containment-controls.svg")` to
`TestInstall.INSTALLED_FILES`, so the canvas, unique-id, self-containment, registry-completeness
and install-lifecycle checks cover the new file.
- New `tests/test_desktoptheme_containmentcontrols.py` (`SvgCase`, `SVG_PATH =
CONTAINMENT_CONTROLS_SVG`):
  - `test_containment_controls_contract`: all twenty-six ids are present, ids are unique, and
the file has no script, style or external reference.
  - `test_groups_sit_at_the_origin`: `tile_origins` finds every id-bearing group at (0, 0), so a
future transform cannot move a slice off its canvas region while the pixel tests still pass.
  - `test_ruler_frame_slices_are_black_edges_on_a_face_band`: each of the twelve frame groups
holds one rect at its pinned natural size and fill, and `render_slices` paints exactly that
pixel map.
  - `test_sliders_are_raised_platinum_thumbs_with_grips`: render each of the twelve slider
groups with `render_slices` and compare its full pixel map to `raised_thumb_pixels(9, 9)` from
`support.thumb_fixtures` with the pinned grip pixels overwritten to `BLACK` -- the 3x3 dot for
the offset sliders, the vertical 1x5 bar for north/south min/max, the horizontal 5x1 bar for
east/west min/max. This pins every pixel, the 9x9 natural size and the grip orientation, so a
shifted bevel, a resized group or a swapped grip fails.
  - `test_center_indicators_are_lavender_lines`: each indicator group renders exactly 42
`SELECTION` pixels in the pinned 42x1 or 1x42 shape, and each of its rects carries
`fill-opacity="0.4"`.
  - `test_containment_controls_colours`: `assert_fill_palette(self, self.tree,
extra={SELECTION})`, so the parsed fill set is exactly the Platinum face/bevel palette plus the
selection lavender.
- `README.md`: replace the sentence that says the panel resize and slider handles still come from
the fallback theme with one naming `widgets/containment-controls.svg`, its black-edged ruler
frame, its twelve offset/min/max sliders and its two centre indicators.
- `docs/invariants.md`: add a `## desktoptheme` row stating that the panel edit-mode ruler frame
is black-edged Platinum face slices, the sliders are raised Platinum thumbs and the centre
indicators lavender lines, pinned by
`tests/test_desktoptheme_containmentcontrols.py::TestContainmentControls`; the provenance
exception records that no reference screenshot shows panel edit mode; the twenty-six ids are
KDE-required (the consumers name them), the frame slice and 42x1/1x42 indicator geometry plus
0.4 opacity are the installed default theme's, and the 9x9 slider size and artwork are this
theme's own; the colours reuse the grounded Platinum and selection anchors.
- `PLANS.md`: in the scope-drift paragraph, change the widget-SVG count from twenty-five to
twenty-six, name the new containment-controls file, and drop the claim that its handles still
come from the default theme.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/containment-controls.svg` (new),
`tests/test_desktoptheme_containmentcontrols.py` (new),
`tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, `README.md`,
`docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- The new SVG parses as a 42x42 canvas with the twenty-six pinned ids present and unique, every
ruler frame group rendering its pinned 10x1/10x12 or 1x10/12x10 slice, every slider group
rendering as the pinned 9x9 raised thumb plus its orientation's grip, the two indicator groups
rendering as the pinned 42x1 or 1x42 lavender line at 0.4 opacity, and every id-bearing group at
the origin.
- The parsed fill set is exactly `#000000`, `#FFFFFF`, `#999999`, `#DDDDDD` and `#CCCCFF`;
dropping an id, resizing a group, swapping a bevel colour or turning a grip the wrong way fails
a test.
- `TestSvgRootCanvas`'s registry and `TestInstall.INSTALLED_FILES` cover the new file,
`tests/invariants.py` accepts the new `## desktoptheme` row, and README and the scope-drift
paragraph name it with the scope-drift count at twenty-six.
- `make check` is green.

### Platinum cursor set, part 3: ship the drag-and-drop, grab and forbidden pointers (planned 2026-10-23 by the plan role; follows the landed resize/diagonal/crosshair/not-allowed set) — done 2026-10-23 by the feature role

**Goal.** The icon theme's `cursors/` covers the arrow, text I-beam, pointing hand, busy
hourglass, move cross, the four resize arrows, the crosshair and the circle-slash, and README
records that drag-and-drop (`dnd-*`), grab, the separate `forbidden`/`no-drop` pointers, help,
progress, zoom and pencil still come from the fallback cursor theme. Add the drag-and-drop and
grab pointers: a new `dnd-copy` (white-outlined black copy plus), the landed four-way cross as
`dnd-move`, the landed arrow as `dnd-none`, the landed circle-slash as
`dnd-no-drop`/`no-drop`/`forbidden`, and the new `grab` (open hand) and `grabbing` (closed fist)
cursors. `help`, `progress`, `pencil`, `zoom-in` and `zoom-out` stay on the fallback theme and
are a later entry. No reference screenshot shows a pointer, so the art stays our own
`#000000`-face/`#FFFFFF`-outline drawing; the canonical names are X/KDE-required, taken from the
installed Breeze cursor set (`/usr/share/icons/breeze_cursors/cursors` ships exactly the four
`dnd-copy`/`dnd-move`/`dnd-no-drop`/`dnd-none` drag names, plus `forbidden`, `no-drop`, `grab` and
`grabbing`). The alias grouping is this theme's choice: Breeze's own byte groups are not copied.

**Approach.**
- `tools/make_cursors.py`: add three 16x16 grids in the existing `#` face / `.` white / space
transparent vocabulary and wire them into `CURSORS`; `cursor_bytes`, `NOMINAL_SIZES` and `main`
need no change.
  - `DND_COPY_HOTSPOT = (7, 7)`; `DND_COPY_GRID` -- a symmetric black plus whose vertical bar is
column 7 on rows 2-12 and horizontal arms run along row 7 from columns 2-12, split from the bar by
its white outline at columns 6 and 8, with a white outline cell around every black edge and
transparent corners; `(7, 7)` is black and `(6, 7)` is white.
  - `GRAB_HOTSPOT = (7, 12)`; `GRAB_GRID` -- an open hand: four 1px black fingers at columns 3, 6,
9 and 12 on rows 2-9, separated by white outline columns, over a black palm on rows 10-13 with a
white outline along its sides and bottom; the fingertips are black at row 2 and the palm is black
at `(7, 12)`, its left edge white at `(1, 12)`.
  - `GRABBING_HOTSPOT = (7, 12)`; `GRABBING_GRID` -- the same hand closed into a fist: a black block
on rows 5-13 with a white outline around it and the thumb folded across; row 2 is transparent (no
raised fingers) and the palm is black at `(7, 12)`, its left edge white at `(1, 12)`.
  - Append `("dnd-copy", DND_COPY_GRID, DND_COPY_HOTSPOT, ())`, `("grab", GRAB_GRID,
GRAB_HOTSPOT, ())` and `("grabbing", GRABBING_GRID, GRABBING_HOTSPOT, ())` to `CURSORS`; extend the
existing tuples so `fleur` also carries `dnd-move`, `left_ptr` also carries `dnd-none`, and
`not-allowed` also carries `forbidden`, `no-drop` and `dnd-no-drop` (byte-identical aliases).
  - Update the module docstring: the package ships fourteen canonical cursors, not eleven, and
list the new names and aliases.
- `tests/test_cursors_theme.py`: extend `CANONICAL` with `dnd-copy`, `grab` and `grabbing`, and
`ALIASES` with the three new canonical names (no aliases) plus `dnd-move` under `fleur`, `dnd-none`
under `left_ptr`, and `forbidden`/`no-drop`/`dnd-no-drop` under `not-allowed`. Add the three new
names to `HOTSPOTS` (`(7, 7)` at 16, `(11, 11)` at 24, `(14, 14)` at 32 for `dnd-copy`; `(7, 12)`
at 16, `(11, 18)` at 24, `(14, 24)` at 32 for `grab` and `grabbing`) and to `PINNED_PIXELS`
(face `(7, 7)` / outline `(6, 7)` for `dnd-copy`; face `(7, 12)` / outline `(1, 12)` for `grab` and
`grabbing`). Add `dnd-copy`, `grab` and `grabbing` to `TRANSPARENT_CORNER_CURSORS`. The existing
`TestCursorSet` loops then cover the new files, aliases, hotspots, face/outline pixels and
determinism. Add focused tests:
  - `test_dnd_copy_is_a_centred_plus`: at 16px, black at `(7, 2)`, `(7, 12)`, `(2, 7)`, `(12, 7)`
and `(7, 7)`; white at `(6, 7)` and `(7, 1)`; every corner transparent.
  - `test_grab_and_grabbing_pin_open_and_closed_hands`: at 16px both have black `(7, 12)` and white
`(1, 12)`; `grab` is black at the fingertip `(3, 2)` while `grabbing` is transparent there; the two
grids differ.
  - `test_dnd_aliases_reuse_the_landed_glyphs`: `dnd-move` is byte-identical to `fleur`, `dnd-none`
to `left_ptr`, and `forbidden`, `no-drop` and `dnd-no-drop` to `not-allowed`.
- Regenerate the artifacts with `python3 tools/make_cursors.py` (deterministic output).
- `tests/test_icon_theme.py`: add the eight new X names (`dnd-copy`, `dnd-move`, `dnd-none`,
`dnd-no-drop`, `forbidden`, `no-drop`, `grab`, `grabbing`) to `SHIPPED_CURSORS`, so the shipped-file
registry and the shared install-lifecycle list cover them.
- `README.md`: in the cursor sentence name the new pointers and aliases, and narrow the fallback
sentence to the `help`, `progress`, `pencil`, `zoom-in` and `zoom-out` pointers.
- `docs/invariants.md`: extend the `## icons` cursor row to name all fourteen canonical files and
every alias, still citing `tests/test_cursors_theme.py::TestCursorArtifact` and
`::TestCursorSet`. Extend the provenance exception: no reference screenshot shows the pointer; the
drag-and-drop, grab and forbidden names are X/KDE-required and taken from the installed Breeze set,
while grouping `dnd-move` with `fleur`, `dnd-none` with `left_ptr` and
`dnd-no-drop`/`no-drop`/`forbidden` with `not-allowed` is this theme's own choice.
- `PLANS.md`: in the scope-drift paragraph, add the drag-and-drop, grab and forbidden pointers to
the shipped cursor clause, and state that `help`, `progress`, `pencil`, `zoom-in` and `zoom-out`
still fall back.

**Files touched.** `tools/make_cursors.py`, `tests/test_cursors_theme.py`,
`tests/test_icon_theme.py`, the new binaries under `theme/icons/org.macos8.desktop/cursors/`
(three canonical names and five alias names), `README.md`, `docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the three new canonical files and the five aliases;
running it twice leaves every committed cursor byte-identical, and each new canonical parses to
three chunks at nominal sizes 16/24/32 with its pinned hotspot, black face pixel, white outline
pixel and transparent corners.
- `dnd-copy` draws the pinned centred plus, `grab` draws the open hand with black fingertips and
`grabbing` the closed fist with transparent finger cells; deleting a grid, dropping a size,
moving a hotspot, redrawing the plus off-centre or making `grabbing` a copy of `grab` fails a test.
- `dnd-move`, `dnd-none`, `forbidden`, `no-drop` and `dnd-no-drop` are byte-identical to their
canonical files; the generator writes exactly the eight new names into a temp directory.
- `tests/test_icon_theme.py`'s shipped-file registry and install lifecycle include all eight new
names, README and `docs/invariants.md` name them, and `tests/invariants.py` accepts the updated
`## icons` row; the scope-drift clause names only help, progress, pencil and zoom as fallback.
- `make check` is green.

### Platinum panel edit-mode chrome, part 1/2: ship the panel margin highlight (planned 2026-10-23 by the plan role; independent of the waiting cursor series) — done 2026-10-23 by the feature role

**Goal.** The desktop theme ships no `widgets/margins-highlight.svg`, so while a panel is in
edit mode Plasma falls back to the default theme's blue translucent margin band. Ship our own
4x4 highlight tile: the flat `fill` and four corner wedges the panel's `SideMargin` reads, tinted
the reference selection lavender instead of Breeze blue. The panel's resize/slider handles
(`widgets/containment-controls.svg`) stay on the fallback theme in this part; part 2/2 covers
them. No reference screenshot shows panel edit mode, so the tile is our own art: the lavender is
the grounded selection colour `#CCCCFF`, and the 0.3 translucency is the default theme's
margin-highlight opacity.

**Approach.**
- New `theme/desktoptheme/org.macos8.desktop/widgets/margins-highlight.svg`, a 4x4 canvas with the
five ids the installed `org.kde.panel` `main.qml` `SideMargin` resolves: `fill` for the flat band
and `topleft`, `topright`, `bottomleft`, `bottomright` for the corner wedges (the component builds
`side + 'left'`/`'right'`, or `'top'`/`'bottom'` + side, so those four names are the only ones it
asks for).
  - `fill` is `<rect id="fill" x="0" y="0" width="4" height="4" fill="#CCCCFF"
fill-opacity="0.3"/>`.
  - The four corner ids are half-canvas triangles, each `fill="#CCCCFF"` and
`fill-opacity="0.3"`: `topleft` `M 0,0 H 4 L 0,4 Z`, `topright` `M 0,0 H 4 V 4 Z`, `bottomleft`
`M 0,0 V 4 H 4 Z`, `bottomright` `M 4,0 V 4 H 0 Z`.
  - Open the SVG with a comment naming the consumer, the five ids, and the provenance: the
consumer stretches each element over the margin band, `#CCCCFF` is the reference selection colour,
and 0.3 is the default theme's margin-highlight opacity.
- `tests/support/desktoptheme_paths.py`: add `MARGINS_HIGHLIGHT_SVG` pointing at
`widgets/margins-highlight.svg`.
- `tests/test_desktoptheme.py`: add `("margins-highlight.svg", MARGINS_HIGHLIGHT_SVG, 4, 4)` to
`SVG_CANVASES`, so `TestSvgRootCanvas`'s canvas, unique-id and self-contained loops cover it.
- New `tests/test_desktoptheme_marginshighlight.py`: pin the five ids, the flat `fill` rect at
`(0,0,4,4)`, each corner path's exact `d` and the four corner orientations, every fill `#CCCCFF`,
every `fill-opacity` `0.3`, and the absence of scripts, styles and external references.
- `README.md`: after the `widgets/action-overlays.svg` sentence, record
`widgets/margins-highlight.svg` as the translucent lavender panel-margin highlight shown in edit
mode, and note that the panel resize/slider handles still come from the fallback theme.
- `docs/invariants.md`: add a `## desktoptheme` row stating that the margin highlight's flat fill
and four corner wedges share the grounded selection lavender at KDE's 0.3 highlight opacity, pinned
by `tests/test_desktoptheme_marginshighlight.py`; the provenance exception records that no
reference screenshot shows panel edit mode, so the five ids and 0.3 opacity are KDE-required while
the colour reuses the reference selection anchor.
- `PLANS.md`: in the scope-drift paragraph, change the desktop-theme count from twenty-four to
twenty-five widget SVGs, name the new margin highlight, and state that
`widgets/containment-controls.svg` still falls back.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/margins-highlight.svg` (new),
`tests/test_desktoptheme_marginshighlight.py` (new), `tests/support/desktoptheme_paths.py`,
`tests/test_desktoptheme.py`, `README.md`, `docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- The new SVG parses as a 4x4 square with the five ids present and unique, every fill `#CCCCFF`,
every `fill-opacity` `0.3`, and no script, style or external reference.
- `fill` is the full 4x4 rect and each corner id is its pinned half-canvas triangle; dropping
an id, nudging a path, changing a fill or changing the opacity fails a test.
- `TestSvgRootCanvas`'s registry covers the new file, and the README and `docs/invariants.md`
name it; `tests/invariants.py` accepts the new row and the scope-drift count is twenty-five.
- `make check` is green.

### Platinum cursor set, part 2: ship the resize, diagonal, crosshair and not-allowed pointers (planned 2026-10-23 by the plan role; follows the landed cursor set) — done 2026-10-23 by the feature role

**Goal.** The icon theme's `cursors/` covers the arrow, text I-beam, pointing hand, busy hourglass
and move cross, and README records that resize, diagonal, drag and not-allowed pointers still come
from the fallback cursor theme. Add the six pointers that make window resizing, precise pointing
and a forbidden action wear the same Platinum art: `size_hor` (horizontal double arrow),
`size_ver` (vertical double arrow), `size_fdiag` (NW-SE double arrow), `size_bdiag` (NE-SW double
arrow), `crosshair` (precision cross) and `not-allowed` (circle-slash). No reference screenshot
shows a pointer, so the art stays our own black-face/white-outline drawing; the canonical names and
the alias groups are KDE/X-required and are copied from the installed Breeze theme's own
byte-identical groups (verified with `md5sum` in `/usr/share/icons/breeze_cursors/cursors`):
`size_hor` with `e-resize`/`ew-resize`/`w-resize`/`h_double_arrow`/`sb_h_double_arrow`,
`size_ver` with
`n-resize`/`ns-resize`/`s-resize`/`sb_v_double_arrow`/`v_double_arrow`/`00008160000006810000408080010102`,
`size_fdiag` with `nw-resize`/`se-resize`/`nwse-resize`, `size_bdiag` with
`ne-resize`/`sw-resize`/`nesw-resize`, `crosshair` with `cross`/`tcross`, and `not-allowed` with
`circle`/`crossed_circle`/`03b6e0fcb3499374a867c041f52298f0`. Drag-and-drop (`dnd-*`), grab, help,
progress, zoom and the separate `forbidden`/`no-drop` pointers stay on the fallback theme.

**Approach.**
- `tools/make_cursors.py`: add six 16x16 grids in the existing `#` face / `.` white / space
transparent vocabulary, each with hotspot `(7, 7)`, and append their tuples to `CURSORS` (the
`cursor_bytes`, `NOMINAL_SIZES` and `main` paths need no change):
  - `SIZE_HOR_GRID` -- solid black left and right arrowheads joined by a black stem on rows 7-8,
    with a 1px white outline on the outside of every face cell.
  - `SIZE_VER_GRID` -- `SIZE_HOR_GRID` rotated a quarter turn; `SIZE_BDIAG_GRID` --
    `SIZE_FDIAG_GRID` mirrored left to right. Write both grids literally so the art is reviewable,
    and let the tests pin the relationship to their sibling (a wrong orientation fails).
  - `SIZE_FDIAG_GRID` -- the same double-arrow art along the NW-SE axis, arrowheads at the top-left
    and bottom-right, hotspot on the shaft.
  - `CROSSHAIR_GRID` -- a 1px black horizontal arm on row 7 and vertical arm on column 7 crossing at
    the hotspot, 1px white outline alongside each arm, transparent corners.
  - `NOT_ALLOWED_GRID` -- a black ring (1-2px, inset one pixel from the canvas edge) with a black
    NW-SE slash through the centre, a 1px white outline outside the ring and slash, the ring's
    interior transparent except the slash, transparent corners; (7, 7) is black on the slash.
  - Update the module docstring: the package ships eleven cursors, not five, and list the new names.
- `tests/test_cursors_theme.py`: extend `CANONICAL`, `ALIASES`, `HOTSPOTS` (`(7, 7)`, `(11, 11)`,
  `(14, 14)` at 16/24/32), `PINNED_PIXELS` (one black face and one white outline cell per new glyph)
  and `TRANSPARENT_CORNER_CURSORS`; the existing `TestCursorSet` loops then cover the new files,
  aliases and determinism. Add three focused tests:
  - `test_size_ver_is_the_horizontal_glyph_rotated_a_quarter_turn` and
    `test_size_bdiag_is_the_forward_diagonal_mirrored`: compare the 16px `render_rgba`
    results, rotating with destination `(x, y)` read from source `(y, GRID_SIZE - 1 - x)` and
    mirroring with destination `(x, y)` read from source `(GRID_SIZE - 1 - x, y)`.
  - `test_crosshair_black_cells_lie_on_the_centre_row_or_column`.
  - `test_not_allowed_is_a_ring_with_a_slash`: every corner transparent, `(7, 7)` black, and the
    four cardinal exterior cells (`(7, 0)`, `(7, 15)`, `(0, 7)`, `(15, 7)`) white.
- Regenerate and commit the artifacts with `python3 tools/make_cursors.py` (deterministic output).
- `tests/test_icon_theme.py`: add the twenty-eight new X names to `SHIPPED_CURSORS`, so the
  shipped-file registry and the shared install-lifecycle `INSTALLED_FILES` list include them.
- `README.md`: in the cursor sentence name the six new pointers and their aliases, and narrow the
  fallback sentence to drag-and-drop (`dnd-*`), grab, help, progress and zoom pointers.
- `docs/invariants.md`: extend the `## icons` cursor row to name all eleven canonical files and
every alias, still citing `tests/test_cursors_theme.py::TestCursorArtifact` and `::TestCursorSet`;
the provenance exception keeps "no reference screenshot shows the mouse pointer" and adds that the
six new alias groups mirror Breeze's own byte-identical files.
- `PLANS.md`: in the scope-drift paragraph, extend the cursor clause to name the resize, diagonal,
crosshair and not-allowed pointers alongside the five landed ones, and state what still falls back.

**Files touched.** `tools/make_cursors.py`, `tests/test_cursors_theme.py`,
`tests/test_icon_theme.py`, the new binaries under `theme/icons/org.macos8.desktop/cursors/` (six
canonical names and twenty-two aliases), `README.md`, `docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the six canonical files and twenty-two aliases; running it
  twice leaves every committed cursor byte-identical, and each new canonical parses to three chunks
  at nominal sizes 16/24/32 with its pinned hotspot, black face pixel, white outline pixel and
  transparent corners.
- Every new alias is byte-identical to its canonical file, and the generator writes exactly the
  twenty-eight new names into a temp directory.
- The rotation, mirror and crosshair-geometry tests pass; dropping a glyph or alias, rotating a
  grid the wrong way or redrawing the crosshair off the centre row/column fails a test.
- `tests/test_icon_theme.py`'s shipped-file registry and install lifecycle include all twenty-eight
  new files, README and `docs/invariants.md` name them, and `tests/invariants.py` accepts the updated
  `## icons` row.
- `make check` is green.

### Platinum Kvantum secondary controls: map toolbars, tree views and status bars onto the Platinum art (planned 2026-10-23 by the plan role; follows the landed four-part Kvantum series) — done 2026-10-23 by the feature role

**Goal.** The Kvantum style defines the core, track/value and surface controls, but the six
sections Kvantum maps common Qt widgets to are left to its compiled-in default: `[ToolbarButton]`
(a `QToolButton` in a `QToolBar`), `[ToolbarComboBox]`, `[ToolbarLineEdit]`, `[DropDownButton]`
(a tool button with a menu popup), `[TreeExpander]` (a `QTreeView`'s branch indicator) and
`[StatusBar]`. `org.macos8.desktop.kvconfig`'s own header records that Kvantum "merges this file
over its compiled-in default.kvconfig and draws an element the theme SVG lacks from its
compiled-in default.svg", so these six sections are not defined by the Platinum style. State
them explicitly so a KDE application's toolbar buttons, toolbar combo boxes and line edits,
split-button dropdowns, tree-view expanders and status bar draw the same grounded Platinum
controls as the rest of the style instead of inheriting Kvantum's default. The button, line-edit,
comboarrow and arrow-down elements already ship; the tree expander needs Kvantum's
`arrow-minus-*`/`arrow-plus-*` branch names added to the SVG, reusing the grounded down and right
arrow paths.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`: after `[Toolbar]`, add these
  sections with a short comment naming the provenance exception (no reference screenshot shows a
  KDE/Qt toolbar, tree view or status bar, so the section and key names are Kvantum-required):
  - `[ToolbarButton]` -- `inherits=PanelButtonCommand`, the 2px raised Platinum push button with
    its black label in every state.
  - `[ToolbarComboBox]` -- `inherits=ComboBox`, the raised face whose `comboarrow` indicator is
    the reference popup's double arrow at size 12.
  - `[ToolbarLineEdit]` -- `inherits=LineEdit`, the white sunken field.
  - `[DropDownButton]` -- `inherits=PanelButtonCommand`, the raised face with Kvantum's
    `arrow-down` indicator at size 9 (its unqualified `arrow` would resolve to the missing
    `arrow-normal` when Kvantum appends only the state).
  - `[TreeExpander]` -- `inherits=PanelButtonCommand`, `indicator.element=arrow`, `frame=false`,
    `interior=false`, so only the branch triangle is drawn (Kvantum names it
    `arrow-minus-<state>`/`arrow-plus-<state>`: black in the normal states, #999999 disabled).
  - `[StatusBar]` -- `inherits=GenericFrame`, `frame=false`, `interior=false`, a flat bar in the
    `[GeneralColors]` window face with no bevel.
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: add the eight branch triangles
  (`arrow-minus-*` pointing down, `arrow-plus-*` pointing right) for the normal, focused, pressed
  and disabled states, reusing the grounded arrow paths and fills; enlarge the canvas height to
  hold them.
- `tests/support/kvantum_config_spec.py`: add the four framed sections to `CORE_FRAME_MARGINS`
  (all 2) and to `CORE_CONTROL_CONFIG` with the element mappings they resolve to -- for
  `ToolbarButton` the frame and interior `button` and the indicator `arrow`, for `DropDownButton`
  the frame and interior `button` and the indicator `arrow-down`, for `ToolbarComboBox` the frame
  and interior `button` and the indicator `comboarrow`, for `ToolbarLineEdit` the frame and
  interior `lineedit`. Add `TreeExpander` and `StatusBar` to `FRAMELESS_SECTIONS` with
  `frame=false`, `interior=false` and their pinned `inherits` targets (plus the expander's
  `indicator.element=arrow`). The existing `test_every_section_is_pinned`,
  `test_every_core_section_mapping_is_pinned`, `test_every_core_section_resolves_to_the_expected_frame_margin`
  and `test_every_frameless_section_resolves_its_pins` then fail if a section, margin, inherited
  element target or frameless pin is dropped or changed.
- `tests/test_kvantum_svg.py`: pin that every branch triangle ships in every state and draws its
  grounded down/right path with the per-state fill.
- `README.md`: in the Kvantum paragraph, change "Its Platinum palette and core-control art live
  in ..." to "Its Platinum palette and control art live in ..." and add that the toolbar buttons,
  toolbar combo boxes and line edits, split-button dropdowns, tree-view expanders and status bar
  map to the same Platinum button, line-edit and arrow art.
- `docs/invariants.md`: add one `## kvantum` row -- the four framed secondary sections resolve to
  the grounded Platinum elements and margins above, the tree expander to the pinned branch
  triangles, and the status bar to no frame or interior, with both frameless sections' `inherits`
  targets pinned -- citing `tests/test_kvantum_config_elements.py::TestCoreControlElements`,
  `tests/test_kvantum_config.py::TestFrameMargins`, `tests/test_kvantum_config.py::TestSectionCoverage`
  and `tests/test_kvantum_svg.py::TestSvg`; its provenance exception is the missing reference
  screenshot (the section and key names are Kvantum-required, the art is grounded).

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`,
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, `tests/support/kvantum_config_spec.py`,
`tests/test_kvantum_config.py`, `tests/test_kvantum_svg.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- Each new section resolves (following `inherits`) to its pinned element mapping and, for the four
  framed sections, the 2px frame margin; `DropDownButton` resolves its indicator to `arrow-down`;
  `TreeExpander` and `StatusBar` resolve `frame` and `interior` to `false` with their `inherits`
  targets pinned.
- `test_every_section_is_pinned` names all six new sections, and deleting one, dropping its frame
  margin, repointing an inherited element target, or removing a branch arrow or one of its states
  fails a test.
- The SVG change is limited to the eight branch triangles and the canvas height they need, and no
  new colour is introduced.
- `make check` is green and `tests/invariants.py` accepts the new `## kvantum` row.

### Platinum cursor set: ship the text, hand, busy and move pointers (planned 2026-10-23 by the plan role; follows the landed arrow artifact) — done 2026-10-23 by the feature role

**Goal.** The icon theme package ships `cursors/{left_ptr,arrow,default,top_left_arrow}`, so after
`make apply-cursor` selects the theme every pointer except the arrow still comes from the user's
fallback theme: typing in a field, hovering a link, waiting for a task and dragging a window all
draw the fallback cursor. Add the four other pointer roles a desktop uses constantly -- the text
I-beam (`xterm`), the pointing hand (`hand2`), the busy hourglass (`watch`) and the move cross
(`fleur`) -- with the X-name aliases applications use, generated by the same tool. All art is our
own Platinum-style drawing on the pinned #000000 face and #FFFFFF outline, not traced from
Apple's artwork; no reference screenshot shows a pointer, so the existing `## icons` provenance
exception covers the new names. This entry does not change the arrow's bytes; the landed
"Platinum cursor selection" entry's `make apply-cursor` selects the set. Resize, diagonal, drag
and not-allowed pointers stay on the fallback theme and are recorded as such; a later entry can
complete them.

**Approach.**
- `tools/make_cursors.py`: replace the one-glyph constants' use with a fixed `CURSORS` table whose
  entries are `(canonical_name, rows, hotspot, aliases)`, in this order: `left_ptr` (the existing
  `ARROW_GRID`/`HOTSPOT`, aliases `arrow`, `default`, `top_left_arrow`), `xterm` (I-beam, aliases
  `text`, `ibeam`), `hand2` (pointing hand, aliases `hand1`, `pointer`, `pointing_hand`), `watch`
  (hourglass, alias `wait`) and `fleur` (move cross, aliases `move`, `all-scroll`, `size_all`).
  Keep `ARROW_GRID`, `HOTSPOT`, `NOMINAL_SIZES` and `cursor_bytes(rows=ARROW_GRID, sizes=
  NOMINAL_SIZES, hotspot=HOTSPOT)` so the landed artifact and its tests stay valid. Add a
  `*_GRID` and `*_HOTSPOT` constant per glyph and generalize `_checked_rows` to take the glyph
  name so a bad cell reports `"xterm grid cell (x, y) ..."` (the arrow keeps its `"arrow grid"`
  messages). `main` walks `CURSORS` in order and writes each canonical file then its aliases with
  the same containment guard, atomic write and stop-on-first-failure behavior.
- The new 16x16 grids use the existing `PIXELS` map (`#` black face, `.` white outline, space
  transparent) and keep the arrow's 1px black face fully inside a 1px white outline, transparent
  elsewhere: `xterm` is a vertical I-beam with top and bottom serifs, hotspot at its centre;
  `hand2` is a pointing hand with the index finger up and the thumb to the right, hotspot at the
  fingertip; `watch` is a top and bottom triangle joined at a narrow waist, hotspot at the
  centre; `fleur` is a four-way arrow cross, hotspot at the centre. Each grid must differ from
  `ARROW_GRID` so a copy-paste fails the set test.
- `tests/test_cursors_theme.py`: keep `TestCursorArtifact` for the arrow and add `TestCursorSet`
  covering every canonical name and alias: each file parses to 16/24/32 chunks, its hotspot is
  the glyph's pinned scaled hotspot, the four corners are transparent, the face is black and the
  outline white at pinned pixels, and every alias is byte-identical to its canonical file. Extend
  the determinism and `main` error cases to all files, including a corrupted grid, dropped size
  and moved hotspot per new glyph; keep the failed-write case failing on `arrow` so the write
  order is pinned. `HOTSPOTS` becomes a per-glyph mapping.
- `README.md`: the cursor sentence in the installed-theme paragraph names the arrow plus the
  `xterm`, `hand2`, `watch` and `fleur` pointers and their aliases, and says resize/drag pointers
  still come from the fallback theme. Keep the landed `make apply-cursor`/`make remove-cursor`
  selection sentences as they are.
- `docs/invariants.md`: extend the existing `## icons` cursor row to name every canonical file and
  alias and cite both `tests/test_cursors_theme.py::TestCursorArtifact` and `::TestCursorSet`; the
  provenance exception keeps "no reference screenshot shows the pointer; our own Platinum-style
  art on the pinned face and outline; the nominal sizes, Xcursor layout and X names are KDE/X
  required".
- `PLANS.md`: the scope-drift paragraph's artifact list names the cursor set instead of only the
  arrow; its selection sentence already names the landed `make apply-cursor`/`make remove-cursor`
  commands.

**Files touched.** `tools/make_cursors.py`, `tests/test_cursors_theme.py`, `tests/test_icon_theme.py`
(its shipped-cursor registry and installed-file list must name the new files), the new files under
`theme/icons/org.macos8.desktop/cursors/` (canonical names and aliases listed above), `README.md`,
`docs/invariants.md` and `PLANS.md` (this entry and the scope-drift artifact list). Do not edit
`tools/xcursor.py`, `tools/apply_cursor.py`, `PLANS-DONE.md`, or the arrow's committed bytes.

**Acceptance criteria.**
- `git diff --name-status` does not list `cursors/left_ptr`, `cursors/arrow`, `cursors/default` or
  `cursors/top_left_arrow`; running `python3 tools/make_cursors.py` twice leaves every committed
  cursor file byte-identical.
- Every alias is byte-identical to its canonical file, each canonical file holds three chunks at
  nominal sizes 16, 24 and 32, and each glyph's scaled hotspot is pinned at all three sizes
  (the arrow's are (1,1), (2,2) and (2,2)).
- Tests prove each new grid differs from the arrow, a corrupted grid, dropped size or moved
  hotspot changes that glyph's bytes, and an unknown cell names the glyph (`xterm grid cell ...`).
  A missing alias, a copied arrow grid, or swapping two glyphs' hotspots fails a test.
- The generator still refuses a `cursors/` symlink that escapes the repository, reports a failed
  write by path and stops, and writes nothing outside the icon theme package.
- `make check CHECK_TESTS=test_cursors_theme` passes, then `make check` is green (fixing the
  separately recorded stale `_write_atomic` test reference first if it is still open);
  `tests/invariants.py` accepts the updated `## icons` row.

### Platinum cursor selection: link the shipped cursor into the Xcursor user path and apply it (planned 2026-10-23 by the plan role; follows the landed cursor artifact) — done 2026-10-23 by the feature role

**Goal.** The icon theme package ships `cursors/{left_ptr,arrow,default,top_left_arrow}`, but nothing
selects them. Xcursor searches `~/.icons`, `/usr/share/icons` and `/usr/share/pixmaps` (its
`XcursorLibraryPath()` default), not `$XDG_DATA_HOME/icons`: `plasma-apply-cursortheme --list-themes`
and `XcursorLibraryPath()` both ignore a theme copied under `$XDG_DATA_HOME/icons`, and list it when
the same theme is under `~/.icons`. This part adds an opt-in `make apply-cursor` that exposes the
installed icon theme at `$HOME/.icons/org.macos8.desktop` as a symlink and selects it with
`plasma-apply-cursortheme org.macos8.desktop`; `make remove-cursor` removes only that link. `make
install` and `make apply` stay unchanged and select no cursor.

**Approach.**
- `tools/apply_cursor.py` (new CLI, `TOOL = "apply_cursor"`, `CURSOR_THEME =
  "org.macos8.desktop"`, `SELECT_TOOL = "plasma-apply-cursortheme"`, `COMMAND_TIMEOUT = 60.0`).
  It uses `tools.argument_parsing.EscapingArgumentParser` (`--remove`), reports through
  `tools.diagnostics.report_error`/`report_failure`/`report_missing_tool`, runs the selector with
  `tools.process_group.run_logged` into a temporary log, escapes path text with
  `tools.terminal.escape_controls`, and imports `tools.repo_root.ROOT`.
- `resolve_homes(env)` returns `(home, data_home, config_home)`: `$HOME` must be absolute; data home
  is an absolute `$XDG_DATA_HOME` else `$HOME/.local/share`; config home is an absolute
  `$XDG_CONFIG_HOME` else `$HOME/.config` (only for the removal note). A missing or relative `HOME`
  exits 2 naming it.
- `installed_theme(data_home)` is `$XDG_DATA_HOME/icons/org.macos8.desktop`; it must contain a
  regular `index.theme` and a regular `cursors/left_ptr`, else exit 2 naming the path. That file is
  the icon theme's own `index.theme`, so the symlinked directory is also a valid cursor theme (the
  KDE cursor model lists it by the directory name `org.macos8.desktop`).
- Install: the target path is `$HOME/.icons/org.macos8.desktop`. A missing `~/.icons` is created; an
  existing symlink to the installed theme is success (a repeat install changes nothing); any other
  existing path (a foreign symlink, a real directory or a file) is refused with exit 2 naming it and
  is not touched; a `~/.icons` that exists but is not a directory is refused the same way. A new link
  is created with `os.symlink(str(installed_theme), str(target))`.
  Then `plasma-apply-cursortheme org.macos8.desktop` runs with the inherited environment; a missing
  tool exits 2 through `report_missing_tool`, a timeout or non-zero exit returns `report_failure`
  (status 1) with the log tail.
- Remove (`--remove`): unlink the target only when it is a symlink whose link text is the installed
  theme path (a dangling link to a since-uninstalled theme counts as ours); a real directory, a file
  or a symlink elsewhere is left alone with a note and exit 0, like `remove-gtk` leaving a foreign
  file. Do not edit `kcminputrc`; if its `[Mouse] cursorTheme` still names `org.macos8.desktop`,
  print a note naming `plasma-apply-cursortheme breeze_cursors` as the reset. Leave `~/.icons`
  itself in place.
- `Makefile`: add `apply-cursor` and `remove-cursor` to `.PHONY` and `make help`. `apply-cursor`
  refuses a non-empty `DESTDIR` (like `apply`/`apply-gtk`), then runs
  `$(MAKE) --no-print-directory install INSTALL_PACKAGES=icon-theme` followed by
  `$(PYTHON) tools/apply_cursor.py`, behind `require_python`/`require_python_version`.
  `remove-cursor` runs `$(PYTHON) tools/apply_cursor.py --remove` behind the same Python guards.
- `README.md`: replace the cursor paragraph's "Nothing selects it yet." with the opt-in commands,
  the `$HOME/.icons/org.macos8.desktop` symlink, the selection name, the restart note (the selector
  says a restart is needed for the new pointer to display correctly), and the removal note. Add no
  new `?=` variable.
- `docs/invariants.md`: add one row under `## icons`: the opt-in link/selection exposes the shipped
  arrow at the Xcursor path and selects it, refuses a foreign path, and removal reverses only our
  link, leaving a foreign path and `kcminputrc` untouched; pinned to
  `tests/test_apply_cursor.py::TestInstall`, `::TestRemove` and `::TestSelection`. The provenance
  exception records that no reference screenshot shows a pointer, and that the `~/.icons` path, the
  theme name and the selector are Xcursor/KDE-required values.
- `PLANS.md`'s scope-drift paragraph changes its "nothing selects it yet" phrase to name `make
  apply-cursor`/`make remove-cursor` once this lands; the historical "not planned yet" wording in
  `PLANS-DONE.md` is left alone.

**Files touched.** `tools/apply_cursor.py` (new), `tests/test_apply_cursor.py` (new), `Makefile`,
`README.md`, `docs/invariants.md`, `tests/test_cursors_theme.py` and `PLANS.md` (this entry and
the scope-drift sentences). Do not edit `PLANS-DONE.md`, the cursor generator, any `theme/` file,
or the installed-theme layout.

**Pre-existing test repair.** `tests/test_cursors_theme.py` patched `make_cursors._write_atomic`,
which the landed dedupe change removed in favour of `write_bytes_atomically`; the stale reference
made `make check` fail. This change retargets that one mock to the function the generator now
calls, changing no generator code.

**Acceptance criteria.**
- `tests/test_apply_cursor.py` pins: an absolute `HOME` is required (unset and relative refused by
  name); the data-home fallback; a missing installed theme, `index.theme` or `cursors/left_ptr` is
  refused by name; install creates `$HOME/.icons/org.macos8.desktop` as a symlink to the installed
  icon theme, a repeat install succeeds, and a foreign symlink, real directory or file is refused
  without being changed; the selector is invoked as `plasma-apply-cursortheme org.macos8.desktop`,
  a missing selector exits 2 naming it, and a non-zero selector exits 1 with its log tail; removal
  unlinks only our symlink (including a dangling one), leaves a foreign path and `.icons` in place,
  succeeds when repeated, and prints the `kcminputrc` note only when the selection still names
  `org.macos8.desktop`. Changing the link target, deleting the installed-theme check or dropping
  the foreign-path guard makes the matching test fail.
- The Makefile tests pin `apply-cursor`'s dry run (`INSTALL_PACKAGES=icon-theme` before
  `tools/apply_cursor.py`), its `DESTDIR` refusal, and the Python-version refusal; `make help` lists
  both targets and README names `make apply-cursor` and `make remove-cursor`.
- `make check CHECK_TESTS=test_apply_cursor` passes, then `make check` is green; `tests/invariants.py`
  accepts the new `## icons` row.
- `git diff --name-status` names only the files listed under "Files touched" and does not name
  `PLANS-DONE.md`.

### Firefox Platinum chrome, part 2/2: Install the stylesheet and preference into a Firefox profile (planned 2026-10-23 by the plan role; GTK and Firefox series part 4/4, split from the stylesheet; "requires part 1/2 landed") — done 2026-10-23 by the feature role

**Goal.** Part 1/2 landed `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, but no
target puts it where Firefox reads it. This part makes the sheet usable for one opt-in profile:
`make install-firefox` copies the sheet into the profile's `chrome/userChrome.css` and adds the
marker-delimited `toolkit.legacyUserProfileCustomizations.stylesheets=true` preference to its
`user.js`, and `make remove-firefox` removes exactly those two changes. It is opt-in like the GTK
targets: `make install` and `make apply` stay unchanged and install no Firefox files.

**Approach.**
- `tools/install_firefox.py` (new CLI, `TOOL = "install_firefox"`). It takes `--profile PATH` and
  `--remove`, parses with `tools.argument_parsing.EscapingArgumentParser`, reports through
  `tools.diagnostics.report_error`/`report_failure`, and escapes path text with
  `tools.terminal.escape_controls`. Constants name the source
  (`theme/firefox/org.macos8.desktop/chrome/userChrome.css`), the CSS first-line marker
  (`/* org.macos8.desktop Firefox chrome, standalone userChrome.css`), the `user.js` marker
  (`// org.macos8.desktop Firefox Platinum userChrome`) and the exact pref line
  `user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);`.
- `resolve_profile(explicit, env)`: an explicit `--profile` (or `FIREFOX_PROFILE` when the flag is
  absent, which also lets the script run directly) must be an absolute existing directory, else
  exit 2. Otherwise `HOME` must be absolute and the profile root is `$HOME/.mozilla/firefox`.
  Build candidates in this order: the first non-empty `Default=` in any section of
  `installs.ini` (Firefox names the section by install hash, older releases by `Install` plus a
  suffix); the first `[Profile…]` section of `profiles.ini` whose `Default=1`; the first
  `[Profile…]` section with a `Path`. Read the INI files with `configparser` and
  `interpolation=None`, resolve a `Path` relative to the root unless `IsRelative=0`, and take the
  first candidate whose directory exists. When none exists, exit 2 with a diagnostic naming the
  root and the candidates tried.
- Install (`_apply(profile)`): read the shipped sheet through
  `tools.containment.read_bytes(SHEET, ROOT)`, then read an existing
  `<profile>/chrome/userChrome.css` before writing anything. An existing file whose first line is
  not the CSS marker is foreign: report with `report_failure` (status 1) naming its path and write
  nothing. Otherwise create `<profile>/chrome`, publish the sheet with
  `tools.atomic_write.write_atomically` (byte-for-byte), and publish `<profile>/user.js` with the
  same writer.
- `set_user_js(text)` and `remove_user_js(text)` are pure text transforms. They preserve every
  foreign line and that line's own CRLF/CR/LF ending, and a missing final newline. Install removes
  any earlier marker line plus the exact pref line immediately after it, then appends the marker
  and pref at the end, terminating an unterminated last line first and using the file's dominant
  ending (a new file uses `\n`), so a repeat install leaves exactly one block and our line follows
  any foreign setting of the same pref. Removal deletes only that marker-plus-pref pair and leaves
  a foreign `user_pref` for the same name untouched; it leaves an emptied `user.js` and the
  `chrome/` directory in place rather than deleting a file it cannot prove it created.
- Remove (`_remove(profile)`): delete `<profile>/chrome/userChrome.css` only when its first line
  is the CSS marker, then rewrite `user.js` with `remove_user_js`. A foreign file, a foreign pref
  line, and a repeated remove are all no-ops; an unreadable file or failed write exits 2 naming
  the path.
- `Makefile`: add `install-firefox` and `remove-firefox` to `.PHONY` and `make help`, each behind
  `require_python`/`require_python_version`, running
  `$(PYTHON) tools/install_firefox.py $(if $(FIREFOX_PROFILE),--profile "$(FIREFOX_PROFILE)")`
  (with `--remove` for removal). Add a `FIREFOX_PROFILE=path` help line naming the default
  (the active profile under `$HOME/.mozilla/firefox`); do not add a `?=` variable. No DESTDIR
  guard or data-home lock is needed because neither target writes the installed theme tree.
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: replace the header sentence saying no
  Makefile target installs it with the two target names and the profile rule; keep the provenance
  text, the preference name and every rule and hex value unchanged.
- `README.md`: replace the Firefox paragraph with the opt-in install/remove commands, profile
  resolution and `FIREFOX_PROFILE`, the restart note, and the existing
  `browser.tabs.inTitlebar=0` explanation; keep the artifact count and `tumwater:status` text.
  `PLANS.md`'s scope-drift paragraph already named part 2/2 as queued under `## Planned`;
  both mentions now say the profile install has landed.
- `docs/invariants.md`: add one row under `## firefox`: the opt-in install copies the sheet
  byte-for-byte, adds only the marker-delimited pref while preserving foreign lines and endings,
  refuses a foreign `userChrome.css`, and removal reverses only those two changes — pinned to
  `tests/test_firefox_install.py::TestInstall` and `::TestRemove`.

**Files touched.** `tools/install_firefox.py` (new), `tests/test_firefox_install.py` (new),
`Makefile`, `README.md`, `docs/invariants.md`, `theme/firefox/org.macos8.desktop/chrome/userChrome.css`
(header only) and `PLANS.md` (this entry and the scope-drift sentences). Do not edit
`PLANS-DONE.md`, any `theme/gtk/` path or any installed-theme directory layout.

**Acceptance criteria.**
- `tests/test_firefox_install.py` pins: explicit and `FIREFOX_PROFILE` profile resolution, an
  `installs.ini` `[Install…]` default and a hash-named section default, a `profiles.ini`
  `Default=1` and first-profile fallback, relative and
  absolute `Path`, and a named refusal when `HOME` is unusable or no candidate exists; install
  writes a byte-identical sheet and exactly one marker-plus-pref block; a foreign
  `userChrome.css` is refused with nothing written; a repeat install does not duplicate the block;
  foreign `user.js` lines, a foreign pref with the same name, CRLF endings and a missing final
  newline survive install and removal; removal deletes only our sheet and marker block and a
  repeated removal succeeds. Deleting the marker, changing the pref value, or dropping the foreign
  line assertion makes the matching test fail.
- `make check CHECK_TESTS=test_firefox_install` passes, then `make check` is green;
  `tests/invariants.py` accepts the new `## firefox` row. `tests/test_make_help.py` finds both new
  targets in `.PHONY`, `make help` and README, and the `FIREFOX_PROFILE` help line resolves to a
  variable the Makefile expands.
- `git diff --name-status` names only the files listed under "Files touched" and does not name
  `PLANS-DONE.md`.

### Retire the `unclear-invariant` validation gap with an invariant-register ledger (planned 2026-10-23 by the steward role; promotes the recurring `gap: unclear-invariant` tag, 22 Fixed entries) — done 2026-10-23 by the feature role

**Goal.** Twenty-two Fixed entries in BUGS-FIXED.md carry `gap: unclear-invariant` — each bug
could be confirmed only after reconstructing what the code was supposed to guarantee first.
`docs/invariants.md` already has rows for the KDE INI rules, the PNG chunk framing, PLTE, tRNS
and IDAT trailer, the `INSTALL_PACKAGES` guard, the icon theme, the palette anchors and the
fidelity gate, but it had no row for `tools/url_check.py`'s RFC 3986 rules, the render
session's config-search-path isolation or the lineedit corner tiles, and nothing tied an
archived record to its register row. Retire the tag with a ledger that maps each record to the
register row and the test that pins it, and a count cap so a new `unclear-invariant` tag fails
the suite until its invariant is recorded.

**Cited entries.** BUGS-FIXED.md lines recording `gap: unclear-invariant` (22 entries): the six
PNG rules (PLTE color-type legality, tRNS color-type validation, the empty IEND payload, chunks
after IEND, non-consecutive IDAT with late PLTE/tRNS, and the IDAT trailer), the two KDE
config-reader rules (an indented `[General]` header and last-duplicate-key precedence), the
`INSTALL_PACKAGES` guard, the render session's `XDG_CONFIG_DIRS` isolation, the lineedit corner
geometry, the eight `tools/url_check.py` RFC 3986 cases, and the three older one-line records
(icon-theme placeholder naming, the selection palette anchor and the objective fidelity check).
Corrected at implementation: the archive held 22 records (six PNG, two KDE INI) when this
landed, not the 17 the plan was written with; the tRNS and PLTE records landed after the plan
was written.

**Approach.**
- `tests/support/validation_gaps.py`: add `UNCLEAR_INVARIANT_BASELINE = 22` and one
  `UNCLEAR_INVARIANT_REPRODUCTIONS` entry per mechanism, matching both the prose and the older
  one-line record forms. Give each entry the register row's guarantee text in addition to its
  test reference, and add an `unclear_invariant(records)` selector plus a tag-aware lookup that
  returns `None` for an unmatched record, mirroring the `no-observability` ledger without
  changing its entries.
- `tests/test_validation_gaps.py`: add `TestUnclearInvariantLedger` asserting that every
  archived `unclear-invariant` record maps to an entry; that each entry's test reference passes
  `tests/invariants.check_reference`; that each entry's guarantee text occurs in a row
  `tests/invariants.parse_rows` returns from `docs/invariants.md`; that each entry covers a
  shipped record; and that the record count does not exceed 22.
- `docs/invariants.md`: add the missing register rows — `tools/url_check.py`'s RFC 3986
  well-formedness pinned to `tests/test_url_check.py` and the render session's
  `XDG_CONFIG_DIRS` isolation pinned to
  `tests/test_render_surface.py::TestFailurePaths::test_session_ignores_a_config_search_path_from_the_environment`
  under `## tooling`, and the lineedit corner tiles pinned to
  `tests/test_desktoptheme_lineedit.py::TestLineEditReference::test_corners_match_the_reference`
  under `## desktoptheme` — and extend the existing validation-gap ledger row to name both tags.
- `PLANS.md`: this entry moves under `## Done` when the work is done.

**Files touched.** `tests/support/validation_gaps.py`, `tests/test_validation_gaps.py`,
`docs/invariants.md` and `PLANS.md` (this entry). Do not edit `PLANS-DONE.md` or any `theme/`
path; the invariants are already recorded, so no shipped artwork or config changes.

**Acceptance criteria.**
- `tests/test_validation_gaps.py::TestUnclearInvariantLedger` passes, and deleting a ledger
  entry, pointing one at an absent register row or a non-existent test, or adding an
  `unclear-invariant` record without an entry makes the matching assertion fail.
- `make check` is green; `tests/invariants.py` accepts the new `## tooling` and `## desktoptheme`
  rows and the extended ledger row.
- `git diff --name-status` names only the files listed under "Files touched" and does not name
  `PLANS-DONE.md`; `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`.

### Platinum cursor theme, part 3/3: Generate and ship the Xcursor arrow cursor artifact (planned 2026-10-23 by the plan role; rewritten 2026-10-23 by the plan role; "requires part 2/3 landed") — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD by the feature role` to its `### ` heading. Do not edit `PLANS-DONE.md`:
tumwater archives `## Done` entries into that file after the merge, so neither its content nor
`PLANS.md` after the merge is evidence this change controls. Verify the move on the pre-merge
working diff only: `git diff --name-status` names `PLANS.md` and does not name `PLANS-DONE.md`, and
`grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`. Do not claim any grep output
for this entry's heading after the merge; tumwater may already have moved it out of `PLANS.md`.

**Goal.** The theme ships eight artifacts but no cursor, so a themed Plasma session still shows the
Breeze arrow. Mac OS 8.6 draws a black arrow with a white outline; this part builds that cursor as
a KDE/Xcursor theme artifact — `theme/icons/org.macos8.desktop/cursors/{left_ptr,arrow,default,top_left_arrow}`
(the last three byte-identical X-name copies of `left_ptr`, images at nominal sizes 16, 24 and 32
in one Xcursor file) — with a deterministic generator, and ships it inside the
`org.macos8.desktop` icon theme package, whose `make install` family already installs that whole
tree (so install and uninstall need no Makefile change) and whose directory is one of the paths the
XDG icon-spec lookup searches for `cursors/`. It touches no install or selection path: `make
uninstall` already removes the tree with its family, and the selection (`cursorTheme` in the global
terminal's `contents/defaults`) is not planned yet and is not part of this diff.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows the mouse pointer, so no
reference pixel is sampled and the arrow is our own Platinum-style art drawn from a pixel grid in
the generator, not traced from Apple's artwork (the icon theme's standing rule). Its two colours
are `#000000` face and `#FFFFFF` outline, both already pinned in the colour scheme; the nominal
sizes 16/24/32, the Xcursor binary format, the file name `left_ptr` and the X-name aliases are
X/KDE-required values the reference set does not show. Record that provenance exception in the
`## icons` row of `docs/invariants.md` (the artifact ships inside the icon theme package). Xcursor
files have no image extension, so Git LFS (`.gitattributes`) is
untouched. The files ride the icon theme artifact, so README's artifact count stays at eight
(status wording untouched); part 3/3 only extends their reader-facing description in the
"Installing" section.

**Approach.**
- `tools/make_cursors.py` (new): follow `tools/make_wallpaper.py`'s direct-or-package import block,
  `require_within_repo` containment guard and `report_error` diagnostics. It holds the 16x16 arrow
  pixel grid as ASCII rows (`#` black face, `.` white outline, space transparent) with the tip at
  (1,1), scales it nearest-neighbour to 16, 24 and 32 (hotspot scaled by the same mapping), encodes
  each frame with `encode_rgba_png` and assembles each file with `write_cursor`, writing `left_ptr`
  and the three aliases as byte-identical copies (not symlinks) into the repository's
  `theme/icons/org.macos8.desktop/cursors/`. The output is deterministic, so re-running it
  rewrites identical bytes; it refuses an output directory that resolves outside the repository,
  naming the path.
- Committed artifacts: the four generated files under
  `theme/icons/org.macos8.desktop/cursors/` (small binaries, regular git blobs, no LFS filter).
- `tests/test_cursors_theme.py` (new): run the generator into a temp directory twice, asserting
  byte-identical output; parse the committed `left_ptr` with `tests/support/xcursor.py` (part 2/3)
  and pin: exactly one image chunk per nominal size in {16, 24, 32}; each chunk's PNG payload
  decodes with `decode_rgba` and its width/height equal its nominal size; the 16px frame's hotspot is
  (1,1) and its tip pixel (1,1) is opaque `#000000`, the outline corner (0,0) opaque `#FFFFFF`, and
  (15,15) transparent (alpha 0); the committed `arrow`, `default` and `top_left_arrow` are
  byte-identical to `left_ptr`; and corrupting the grid, dropping a nominal size, or moving the
  hotspot fails the matching assertion (the regression pattern `tests/support/mutant_module.py`
  uses).
- `tests/test_icon_theme.py`: `test_icon_theme_ships_exactly_the_tracked_icons` extends its expected
  set and `TestInstall.INSTALLED_FILES` extends its registry, so both equal the package tree with
  the four cursor files added (the inherited `test_installed_files_registry_covers_the_package`
  compares that registry against `shipped_files(self.PACKAGE_DIR)`). The SVG-level assertions
  iterate the explicit `SHIPPED_ICONS` tuple, not `shipped_files`, so they need no change; the
  placeholder register stays untouched.
- `README.md`: in the "Installing" section's icon theme sentence, add that the package ships the
  `cursors/` Xcursor arrow (black face, white outline, nominal sizes 16/24/32, X-name aliases
  `arrow`, `default`, `top_left_arrow`) and that nothing selects it yet. Name no make target (none
  exists or is planned) and change no artifact count.
- `docs/invariants.md`: add one row to the existing `## icons` section — the icon theme's
  `cursors/left_ptr` draws the black face and white outline at nominal sizes 16/24/32 with the
  hotspot at the tip, and its `arrow`, `default` and `top_left_arrow` aliases are byte-identical to
  it — pinned to `tests/test_cursors_theme.py::TestCursorArtifact`, carrying the provenance
  exception above (no screenshot shows a pointer). Do not add a `## cursors` section:
  `tests/invariants.py` accepts only `theme/` subsystem sections plus
  `EXTRA_SECTIONS = ("tooling",)`, so an unregistered section fails `make check`.

**Files touched.** `tools/make_cursors.py` (new),
`theme/icons/org.macos8.desktop/cursors/` (four new generated files), `tests/test_cursors_theme.py`
(new), `tests/test_icon_theme.py`, `tools/xcursor.py` (only its module docstring's forward
reference to a `## cursors` section becomes the `## icons` row), `README.md`,
`docs/invariants.md`, and `PLANS.md` (the entry moves to `## Done`; see Plan record). The
`Makefile`, `.gitattributes` and `tests/invariants.py` are untouched; do not edit
`PLANS-DONE.md` (this replan already annotated its part 2/3 entry).

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the four files under
  `theme/icons/org.macos8.desktop/cursors/` deterministically: two runs into one temp directory
  are byte-identical, and the regenerated files equal the committed ones byte for byte.
- The test-side parser (`tests/support/xcursor.py`) accepts the committed `left_ptr` (magic,
  version 65536, three image chunks) and rejects a truncated or hand-corrupted copy; each chunk's
  PNG payload decodes with `tools.png.decode_rgba`, and its width/height equal the nominal size;
  the pinned pixels and hotspots hold for all three nominal sizes (scaled accordingly); the
  aliases are byte-identical to `left_ptr`; corrupting the committed file, dropping a nominal size
  from the generator's output or moving the hotspot fails the matching assertion.
- `tests/test_icon_theme.py`'s exact-tree pin and `TestInstall.INSTALLED_FILES` hold with the four
  cursor files (removing one, or editing the committed grid's colours, fails the matching test),
  while the SVG-level assertions still iterate only `SHIPPED_ICONS`.
- `make check` is green with the new modules included and `tests/invariants.py` accepts the
  `## icons` row; `grep -n '^## cursors' docs/invariants.md` prints nothing; `git diff
  --name-status` names only the files listed under "Files touched" (besides the backlog move) and
  none of `Makefile`, `.gitattributes`, `tests/invariants.py` or `PLANS-DONE.md`.
- The entry moves from `## Planned` under `## Done` with its Done stamp, verified on the pre-merge
  working diff: `git diff --name-status` names `PLANS.md` and does not name `PLANS-DONE.md`, and
  `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`. No acceptance criterion
  refers to `PLANS.md` or `PLANS-DONE.md` after the merge.

### Firefox Platinum chrome, part 1/2: Ship the `userChrome.css` stylesheet (planned 2026-10-23 by the plan role; GTK and Firefox series part 4/4, split from the profile install) — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD by the feature role` to its `### ` heading. Do not edit `PLANS-DONE.md`:
tumwater archives `## Done` entries into that file after the merge, so neither its content nor
`PLANS.md` after the merge is evidence this change controls. Verify the move on the pre-merge
working diff only: `git diff --name-status` names `PLANS.md` and does not name `PLANS-DONE.md`, and
`grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`. Do not claim any grep output
for this entry's heading after the merge; tumwater may already have moved it out of `PLANS.md`.

**Goal.** GTK series parts 1/4–3/4 landed the GTK 3 and GTK 4 Platinum sheets and their opt-in
install and selection. Part 4/4 is Firefox: `browser.tabs.inTitlebar=0` in a Firefox profile gives
Firefox a KWin-drawn Aurorae frame, but its tab strip, toolbars and menus keep Firefox's own look.
This part ships the stylesheet alone, `theme/firefox/org.macos8.desktop/chrome/userChrome.css`,
written against Firefox's `userChrome.css` chrome selectors and its own chrome theme variables,
with a test module. It adds no Makefile target, no profile write, no preference and no selection:
installing the sheet into a profile's `chrome/` directory and setting
`toolkit.legacyUserProfileCustomizations.stylesheets=true` is part 2/2, which is not queued yet (a
later plan run writes it with "requires part 1/2 landed" in its heading).

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows Firefox's chrome, so no
reference pixel is sampled; the sheet is checked only against the shared palette and its own
rules. Its palette is the reference-grounded values in `tests/support/platinum_palette.py`
(`#DDDDDD` face, `#FFFFFF` white, `#999999` grey, `#000000` black, `#EEEEEE` trough, `#CCCCFF`
selection) plus the GTK sheets' `#888888` etched-separator dark half. Firefox's
chrome custom-property names (`--lwt-accent-color`, `--toolbar-bgcolor`, `--tab-selected-bgcolor`,
`--arrowpanel-background`, …), its XUL selectors (`#TabsToolbar`, `.tab-background`, `#nav-bar`,
`#urlbar-background`, `menupopup`, …) and the `userChrome.css` filename are Firefox-required values
the reference set does not show; the geometry below adapts the desktop theme's Platinum tab,
toolbar and menu faces, not a reference crop. No repository test runs Firefox, so only the rules
and palette are pinned here — whether Firefox draws them is observable only after part 2/2
installs the sheet into a profile. Record that provenance
exception in `docs/invariants.md`. The sheet carries no image, so `.gitattributes` is untouched.

**Approach.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css` (new): a comment header naming the
  provenance exception, the palette source and the preference part 2/2 must set; no `@` character
  anywhere (so it has no at-rule and `tests/support/gtk_css.py::parse_css`, which walks plain rule
  blocks, reads it); every declaration that must beat Firefox's own chrome rule carries
  `!important`. The required rules are exactly these (extra palette-only rules are allowed, but
  the test pins these):
  - `:root` sets `--lwt-accent-color: #DDDDDD`, `--lwt-text-color: #000000`,
    `--toolbar-bgcolor: #DDDDDD`, `--toolbar-color: #000000`,
    `--tab-selected-bgcolor: #EEEEEE`, `--tab-selected-textcolor: #000000`,
    `--arrowpanel-background: #DDDDDD`, `--arrowpanel-color: #000000` and
    `--arrowpanel-border-color: #000000`, each `!important`.
  - `#navigator-toolbox`: `background-color: #DDDDDD !important; border-bottom: 1px solid
    #000000 !important;`.
  - `#TabsToolbar`: `background-color: #DDDDDD !important;`.
  - `#nav-bar`, `#PersonalToolbar` and `#toolbar-menubar`: `background-color: #DDDDDD
    !important; border-bottom: 1px solid #888888 !important; box-shadow: inset 0 -1px #FFFFFF
    !important;` (the GTK sheets' etched toolbar separator, light half under the dark line).
  - `.tab-background`: `background-color: #DDDDDD !important; border: 1px solid #000000
    !important; border-radius: 0 !important; box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px
    #999999 !important;` (the desktop theme's raised Platinum tab face).
  - `.tabbrowser-tab[selected] .tab-background`: `background-color: #EEEEEE !important;
    border-bottom-color: #EEEEEE !important;` (the reference selected-tab face, its bottom border
    dropped as the GTK checked tab does).
  - `#urlbar-background`: `background-color: #FFFFFF !important; border: 1px solid #000000
    !important; border-radius: 0 !important; box-shadow: none !important;` (the white sunken
    Platinum text field, squared).
  - `#statuspanel-label`: `background-color: #DDDDDD !important; color: #000000 !important;
    border: 1px solid #000000 !important; border-radius: 0 !important;`.
  - `menupopup`: `--panel-background: #DDDDDD !important; --panel-color: #000000 !important;
    --panel-border-color: #000000 !important;`.
  - `menupopup > menuitem:hover`: `background-color: #CCCCFF !important;` (the menu selection
    fill the desktop theme's `widgets/background.svg` and the GTK sheets paint).
- `tests/test_firefox_theme.py` (new): `TestFirefoxChrome(unittest.TestCase)` reads the sheet with
  `support.containment.read_text(path, ROOT, encoding="utf-8")` (the containment guard, so a
  checked-in symlink escaping the repository is refused instead of leaking a private file), parses
  it with `support.gtk_css.parse_css` and imports the palette from
  `support.platinum_palette`. A local `assert_rule(selector, expected)` helper asserts each
  required selector is present and carries every listed declaration, including the `!important`
  suffix. It also asserts: `set(HEX.findall(text))` is exactly {BLACK, WHITE, GREY, FACE, TROUGH,
  SELECTION, ETCH_DARK}; `"@" in text` is false; the text mentions no
  `adwaita`; no selector contains `*`; the header names the provenance exception and the
  preference (`toolkit.legacyUserProfileCustomizations.stylesheets`) part 2/2 will set; and
  `README.md`, read through the same containment reader, names the sheet's repository path.
- `README.md`: in the "Installing" section after the GTK paragraph, add a Firefox paragraph saying
  the standalone Platinum `userChrome.css` ships at
  `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, that no target installs or selects it
  yet, that part 2/2 will copy it into a Firefox profile's `chrome/` directory and set
  `toolkit.legacyUserProfileCustomizations.stylesheets=true`, and that setting
  `browser.tabs.inTitlebar=0` makes Firefox use the KWin Aurorae frame. Change no artifact count
  and no `tumwater:status` text.
- `docs/invariants.md`: add a `## firefox` section with one row — the standalone sheet paints the
  Platinum palette on Firefox's tab strip, navigation bar, toolbars, menus and status panel with
  no at-rule and no import — pinned to `tests/test_firefox_theme.py::TestFirefoxChrome`, with the
  provenance exception above (no reference screenshot shows Firefox chrome; the geometry is the
  theme's adaptation of the Platinum controls).
- `PLANS.md`: this entry moves under `## Done` (see Plan record) and the scope-drift paragraph's
  part 4/4 sentence now names part 1/2 and part 2/2.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css` (new),
`tests/test_firefox_theme.py` (new), `README.md`, `docs/invariants.md` and `PLANS.md` (this entry
and the scope-drift sentence). Do not edit `PLANS-DONE.md`, `Makefile`, `.gitattributes`, any
`theme/gtk/` path or any `tests/support/` module; no test-side spec module is needed for one sheet.

**Acceptance criteria.**
- `tests/test_firefox_theme.py` finds every required selector with every listed declaration and
  the `!important` suffix, the hex-literal set equal to the seven palette values above, no `@`
  character, no `adwaita`, no universal selector, the header naming the provenance exception and
  the profile preference, and the README path; deleting a rule, dropping `!important` from a
  declaration or writing a non-palette hex makes the matching assertion fail.
- `make check CHECK_TESTS=test_firefox_theme` passes, then `make check` is green; `tests/invariants.py`
  accepts the new `## firefox` row (it names a `theme/firefox` subsystem and a test that exists).
- `git diff --name-status` names only the files listed under "Files touched" (including the
  `PLANS.md` move) and does not name `PLANS-DONE.md`; `grep -n '^## ' PLANS.md` prints exactly
  `## Planned` and `## Done`. No acceptance criterion refers to `PLANS.md` or `PLANS-DONE.md` after
  the merge.

### Platinum cursor theme, part 2/3: Xcursor binary writer and test-side parser (planned 2026-10-23 by the plan role; rewritten 2026-10-23 by the plan role; "requires part 1/3 landed") — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD by the feature role` to its `### ` heading. Do not edit `PLANS-DONE.md`:
tumwater archives `## Done` entries into that file after the merge, so neither its content nor
`PLANS.md` after the merge is evidence this change controls. Verify the move on the pre-merge
working diff only: `git diff --name-status` names `PLANS.md` and does not name `PLANS-DONE.md`, and
`grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`. Do not claim any grep output
for this entry's heading after the merge; tumwater may already have moved it out of `PLANS.md`.

**Goal.** Part 1/3 added the RGBA PNG codec (`tools/png/write.py::encode_rgba_png`,
`tools/png/read.py::decode_rgba`). This part adds the Xcursor container the cursor artifact needs:
a standard-library writer that turns PNG frames into one Xcursor file, and an independent
test-side parser that reads that file back and cross-checks the writer's framing. Nothing else:
no generator, no committed cursor files, no Makefile, no README, no `theme/` change, no selection.
The generator, the shipped artifact and its registration are part 3/3 ("requires part 2/3
landed").

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a pointer, so no reference
pixel is sampled here; the Xcursor binary layout is an X/KDE-required value the reference set does
not show. Its facts: a 16-byte file header (`b"Xcur"`, header size 16, file version 0x00010000,
TOC count), one 12-byte TOC entry per chunk (type, subtype, byte offset), and the 36-byte image
chunk header (header size 36, type 0xfffd0002, subtype = nominal size, chunk version 1, width,
height, hotspot x, hotspot y, delay 0). The image payload is `width * height` little-endian
**premultiplied ARGB** words, not PNG bytes: the writer decodes each PNG frame with `decode_rgba`
and premultiplies each colour channel with `(channel * alpha + 127) // 255`, and the parser
converts the stored words back to RGBA and re-encodes them with `encode_rgba_png`. An opaque frame
(alpha 255) therefore round-trips byte for byte; a translucent frame does not, because
premultiplication loses colour precision — the tests pin the stored premultiplied word instead.
Record that provenance first here and carry it into the `## cursors` section part 3/3 adds.

> **Superseded 2026-10-23 by the plan role:** part 3/3 adds the cursor guarantee to the existing
> `## icons` section of `docs/invariants.md`, not a new `## cursors` section, because
> `tests/invariants.py` accepts only `theme/` subsystem sections plus
> `EXTRA_SECTIONS = ("tooling",)`. The rest of this archived entry records what part 2/3 did.

**Approach.**
- `tools/xcursor.py` (new): module constants `MAGIC = b"Xcur"`, `FILE_VERSION = 0x00010000`,
  `FILE_HEADER_SIZE = 16`, `TOC_ENTRY_SIZE = 12`, `IMAGE_TYPE = 0xFFFD0002`,
  `CHUNK_VERSION = 1`, `IMAGE_HEADER_SIZE = 36` and `MAX_IMAGE_SIZE = 0x7FFF`; follow
  `tools/make_wallpaper.py`'s direct-or-package import block and use
  `tools/ints.py::is_plain_int`. `write_cursor(images)` takes one `(nominal_size, width, height,
  hotspot_x, hotspot_y, png_bytes)` record per frame; it rejects a dimension outside 1..0x7FFF, a
  hotspot outside its image, a non-integer (including a bool) numeric field, a PNG field that is
  not `bytes`/`bytearray` and a PNG whose size disagrees with `width`/`height`, each with a
  `ValueError` naming the argument; it decodes with `decode_rgba`, premultiplies, writes the file
  header, one TOC entry per image and each image chunk at its declared offset, so the same records
  always produce byte-identical output. The public surface is `write_cursor` plus those constants;
  no comment chunks.
- `tests/support/xcursor.py` (new): the test-side parser, written independently of the writer and
  importing no symbol from `tools/xcursor.py`. `read_cursor(path)` validates the file header
  (magic, header size 16, version 0x00010000, `ntoc`), reads the TOC, skips a TOC entry whose type
  is not `0xfffd0002` (tolerating, for example, a comment chunk), rejects a chunk offset or length
  outside the file, validates the 36-byte image header (type, chunk version 1, nominal size, width,
  height, hotspot), slices the ARGB payload, converts it back to RGBA and returns a `CursorFile`
  NamedTuple of `CursorImage(nominal_size, width, height, hotspot_x, hotspot_y, png)` records whose
  `png` is `encode_rgba_png(width, height, rgba)`. Errors are `ValueError` naming the path and the
  field or offset that failed.
- `tests/test_xcursor.py` (new): round-trip synthetic opaque frames at 1x1, 2x2, 3x3 and 4x4 whose
  hotspot is the bottom-right tip and whose pixels vary by position: `write_cursor` → `read_cursor`
  reproduces every field and returns the original `encode_rgba_png` bytes exactly. Pin the
  container layout by unpacking the bytes: magic, header size, version, `ntoc`, each TOC entry's
  type/subtype/offset, each chunk's 36-byte header (delay 0) and one known translucent pixel's
  premultiplied ARGB word. Two runs with the same records are byte-identical. Rejections, using
  `tests/support/error_assertions.py`'s `assert_error_names` (the rejections raise `ValueError`, which `assert_rejection_names` does not observe): a truncated file header, a
  truncated image payload, a bad magic, a wrong header size, a wrong version, a corrupt `ntoc`
  whose TOC overruns the file, a hotspot outside its image, a zero dimension, a bool dimension, a
  PNG sized differently from its record and a non-`bytes` PNG, each message naming the argument or
  offset. One test builds a valid file plus a hand-appended unknown TOC entry and shows the parser
  skips it while still returning the image.
- `docs/invariants.md`: untouched. This part ships no artifact, so the `## cursors` row belongs to
  part 3/3, which pins the committed file; this part's guarantees are pinned by
  `tests/test_xcursor.py` alone.

**Files touched.** `tools/xcursor.py` (new), `tests/support/xcursor.py` (new),
`tests/test_xcursor.py` (new) and `PLANS.md` (the entry moves to `## Done`; see Plan record). Do not
edit `PLANS-DONE.md`, `Makefile`, `README.md`, `docs/invariants.md` or any `theme/` path.

**Acceptance criteria.**
- `tests/test_xcursor.py`'s round-trip case shows `write_cursor` → `read_cursor` agreeing on every
  field and on the exact PNG bytes for all four opaque synthetic sizes; two runs with the same
  records produce byte-identical files; the layout pin finds the constants above at their stated
  offsets with delay 0 and the expected premultiplied translucent word; each malformed input above
  raises `ValueError` whose message names the offending argument or offset; the hand-appended
  unknown TOC entry is skipped and the remaining image still parses.
- The test-side parser is independent of the writer:
  `grep -n 'from tools import xcursor\|from tools\.xcursor' tests/support/xcursor.py` prints no
  line.
- `make check CHECK_TESTS=test_xcursor` passes, then `make check` is green; removing a guard,
  offsetting a chunk or changing a constant makes the matching test fail.
- `git diff --name-status` names only the files listed under "Files touched" (including the
  `PLANS.md` move) and does not name `PLANS-DONE.md`; `grep -n '^## ' PLANS.md` prints exactly
  `## Planned` and `## Done`. No acceptance criterion refers to `PLANS.md` or `PLANS-DONE.md` after
  the merge; tumwater archives the `## Done` entry into `PLANS-DONE.md`.

### Retire the `no-observability` validation gap with test-side observability (planned 2026-10-23 by the steward role; promotes the recurring `gap: no-observability` tag, 21 Fixed entries) — done 2026-10-23 by the feature role

**Goal.** Twenty-one Fixed entries in BUGS-FIXED.md carry `gap: no-observability` — failures that left no trace the suite could see, so the bug could not be confirmed until instrumentation was added. Retire the tag by adding test-side observability helpers (trace capture, structured failure logging) that make such failures reproducible offline, so new bugs in those areas are confirmable without a real run.

**Cited entries.** BUGS-FIXED.md lines recording `gap: no-observability` (21 entries), including the aurorae reader FIFO, containment guard, config-reading quirks, and invariants/placeholders register rows.

**Acceptance criteria.** `make check` is green; the promoted tag's count stops growing.

**Implementation note (2026-10-23).** Twelve of the thirteen one-line records were already retired by the record-checker mutation harness (`tests/test_checker_mutations.py`), the remaining palette-provenance record was retired by `tests/test_colorscheme.py::TestProvenanceNote`, and each of the eight prose records already names the test that reproduces it offline. This change makes the coverage explicit and bounded: `tests/support/validation_gaps.py` parses both record forms into a structured ledger mapping each mechanism to its reproducing test, and `tests/test_validation_gaps.py` asserts every archived record maps to a real test and caps the count at its 21-record baseline, so a new `no-observability` tag fails the suite instead of growing the gap. The invariant register's tooling row records the guarantee.

### GTK opt-in, part 3/3: Select the installed GTK 3 and GTK 4 Platinum themes (planned 2026-10-21 by the plan role; rewritten 2026-10-23 by the plan role; parts 1/3 and 2/3 landed) — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it
directly under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
Before editing, record `grep -n '^## Done$' PLANS.md`; after the move, `grep -n '^## ' PLANS.md`
must print exactly two lines (`## Planned` and `## Done`) and `grep -n '^### GTK opt-in, part
3/3: Select the installed GTK 3 and GTK 4 Platinum themes' PLANS.md` must print exactly one line
whose number is greater than the `## Done` line's. The final report quotes the actual output of `grep -l "Select the
installed GTK 3 and GTK 4 Platinum themes" PLANS.md PLANS-DONE.md` (exactly `PLANS.md`) and of
`git diff --name-status`; never claim a file the diff does not name.

**Goal.** Part 3/4 installs the GTK 3 and GTK 4 sheets under
`$XDG_DATA_HOME/themes/org.macos8.desktop`, but nothing selects them, so GTK applications still
draw their system theme. Add `make apply-gtk` and `make remove-gtk` plus `tools/apply_gtk.py`:
set `gtk-theme-name=org.macos8.desktop` in both GTK settings files and give libadwaita
applications the GTK 4 sheet as user CSS. Parts 1/3 and 2/3 landed the opt-in install family and
the installed file layout; this entry does not reimplement them. It does not add Firefox chrome, which remains
GTK series part 4/4 and is not planned here.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget, so this part
adds no visual value and samples no pixel. The GTK settings path, the `gtk-theme-name` key and the
libadwaita user-CSS path are GTK-required values the reference set does not show; record that in
`docs/invariants.md` rather than claiming a GTK reference crop.

**Approach.**
- `Makefile`: add public targets `apply-gtk` (refuses a non-empty `DESTDIR`, requires Python with
  both `require_python` and `require_python_version`, runs the nested `$(MAKE) --no-print-directory
  install INSTALL_PACKAGES=gtk`, then `$(PYTHON) tools/apply_gtk.py`) and `remove-gtk` (requires
  Python the same way, runs `$(PYTHON) tools/apply_gtk.py --remove`). Add them to `.PHONY` and to
  `help`'s target list. Keep `install-gtk` unchanged.
- `tools/apply_gtk.py` (new): follow `tools/apply_theme.py`'s direct-or-package import block,
  `EscapingArgumentParser`, `report_error`, `report_failure` and `escape_controls`. Put the
  fallback in two module-level helpers so both are directly testable: `_config_home(env)` returns
  an absolute `$XDG_CONFIG_HOME`, else an absolute `$HOME/.config`, else `None`; `_data_home(env)`
  returns an absolute `$XDG_DATA_HOME`, else an absolute `$HOME/.local/share`, else `None`. `main`
  passes `os.environ` to both and, when either is `None`, exits 2 through `report_error` naming
  the ineffective variable and saying to set `XDG_DATA_HOME`/`XDG_CONFIG_HOME` or an absolute
  `HOME` -- the same resolution and refusal as the Makefile's `require_data_home`. Resolve both
  homes before requiring the installed sheet, so the refusal is testable without an install.
  Constants: `TOOL = "apply_gtk"`, `GTK_ID = "org.macos8.desktop"`, the marker comment
  `/* org.macos8.desktop GTK 4 user CSS */`, and the installed CSS path built from the resolved
  data home.
- `tools/apply_gtk.py`: for apply, require the installed
  `themes/org.macos8.desktop/gtk-4.0/gtk.css` (exit 1 naming `make install-gtk` when absent); in
  `$XDG_CONFIG_HOME/gtk-3.0/settings.ini` and `gtk-4.0/settings.ini` set
  `gtk-theme-name=org.macos8.desktop` in `[Settings]`, preserving every other line, stripping a
  leading UTF-8 BOM only for matching and writing it back, replacing the last `gtk-theme-name`
  line in the section or inserting one after the `[Settings]` header, and appending `[Settings]`
  when it is absent; write both files through a `.staging` sibling and `os.replace`. Write
  `$XDG_CONFIG_HOME/gtk-4.0/gtk.css` as the marker line followed by
  `@import url("<installed gtk-4.0/gtk.css as a file URI>");` (use `Path.as_uri()`), but leave an
  existing `gtk.css` whose first line is not the marker untouched and print a note. For `--remove`,
  delete the marker `gtk.css`, and delete only `gtk-theme-name` lines in `[Settings]` whose value
  is `org.macos8.desktop`, leaving foreign values and files. Both modes print a note that running
  GTK applications must be restarted.
- `tests/test_gtk_apply.py` (new): drive `tools.apply_gtk.main` with `XDG_CONFIG_HOME` and `HOME`
  pointed at a temp directory. Pin: apply writes both settings files with `[Settings]` and our
  `gtk-theme-name`; it preserves an existing `gtk-font-name` line and a comment; it replaces an
  existing `gtk-theme-name`; it appends `[Settings]` when absent; it creates the marker `gtk.css`
  whose second line imports the installed sheet as a file URI; it exits 1 naming `make install-gtk`
  when the installed sheet is missing; a foreign `gtk.css` is left byte-identical with a note;
  `--remove` removes our key and marker and leaves a foreign key and file. Add `TestHomeResolution`
  that patches the environment for `main` and pins every helper branch: an absolute
  `XDG_DATA_HOME` is used even with `HOME` unset (with `XDG_CONFIG_HOME` absolute); an empty and a
  relative `XDG_DATA_HOME` each fall back to `$HOME/.local/share`; an empty and a relative
  `XDG_CONFIG_HOME` each fall back to `$HOME/.config`; and the diagnostic pins
  `test_missing_data_home_names_xdg_data_home` and
  `test_missing_config_home_names_xdg_config_home` each call `main` with the variable unset or
  relative and `HOME` unusable, then, after `assert_failed` from `support.process_assertions`,
  assert `result.stderr` contains `XDG_DATA_HOME` or `XDG_CONFIG_HOME` respectively -- a bare
  exit-code assertion does not pin the diagnostic. Add `TestMakeApplyGtk` mirroring
  `tests/test_apply_theme.py`'s `TestMakeApply`, with all five pins as named methods, each also
  asserting its exact diagnostic or output substring, never the return code alone:
  `test_dry_run_shows_install_before_the_script` (`run_make(["-n", "apply-gtk"], ...)`) asserts
  `assert_succeeded`, that `result.stdout` contains both `INSTALL_PACKAGES=gtk` and
  `tools/apply_gtk.py`, and that `result.stdout.index("INSTALL_PACKAGES=gtk")` is less than
  `result.stdout.index("tools/apply_gtk.py")`; `test_non_empty_destdir_is_refused` runs
  `run_make(["apply-gtk", "DESTDIR=<temp dir>"], ...)`, asserts `assert_failed`, that
  `result.stderr` contains `DESTDIR must be empty`, and that neither stream names
  `apply_gtk.py`; `test_python_version_is_refused` follows `tests/test_make_check.py`'s
  `TestPythonVersion` (a fake interpreter script written to a temp dir, made executable, passed
  as `PYTHON=<fake>`, that exits non-zero for every invocation) and asserts `result.stderr`
  contains `Python 3.10 or newer` and the fake path; `test_dry_run_shows_remove_script`
  (`run_make(["-n", "remove-gtk"], ...)`) asserts `assert_succeeded` and that `result.stdout`
  contains `tools/apply_gtk.py --remove`; and `test_help_lists_both_targets`
  (`run_make(["help"], ...)`) asserts `assert_succeeded` and that a `result.stdout` line starts
  with ``  apply-gtk `` and a line starts with ``  remove-gtk ``.
  Every refusal assertion on an exit status states its diagnostic substring in the same method:
  `test_missing_sheet_names_make_install_gtk` asserts `result.stderr` contains both
  `make install-gtk` and `gtk-4.0/gtk.css`, and the foreign-`gtk.css` pin asserts the stdout
  note names `gtk.css`. A method that asserts only a return code does not implement its pin.
- `README.md`: extend the GTK paragraph from part 3/4 with `make apply-gtk` and `make remove-gtk`
  (the `test_make_help` README check requires the exact target names), both `gtk-theme-name`
  settings keys, the libadwaita `gtk-4.0/gtk.css` marker/import, the need to restart GTK
  applications, and that KDE users can also choose the theme in System Settings -> Application
  Style -> GNOME/GTK Application Style. State that `make remove-gtk` is what clears the selection.
- `docs/invariants.md`: in the existing `## gtk` section add a row for the opt-in selection pinned
  to `tests/test_gtk_apply.py`, with the provenance exception that no reference screenshot shows a
  GTK widget and the settings keys and user-CSS path are GTK-required.

**Files touched.** `Makefile`, `tools/apply_gtk.py` (new), `tests/test_gtk_apply.py` (new),
`README.md`, `docs/invariants.md`, and `PLANS.md` (the entry moves to `## Done`; see Plan record).
Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- `make apply-gtk` with `XDG_DATA_HOME`, `XDG_CONFIG_HOME` and `HOME` under a temp root writes
  `[Settings]`/`gtk-theme-name=org.macos8.desktop` to `gtk-3.0/settings.ini` and
  `gtk-4.0/settings.ini`, preserves an unrelated key and comment, and writes a `gtk-4.0/gtk.css`
  whose first line is the marker and whose second line is `@import url("file://<installed
  gtk-4.0/gtk.css>");`; the same command fails and its stderr names `make install-gtk` and
  `gtk-4.0/gtk.css` when the installed sheet is absent.
- `make remove-gtk` removes only our `gtk-theme-name` line and marker `gtk.css`; a foreign value
  in `gtk-3.0/settings.ini` and a foreign `gtk-4.0/gtk.css` survive byte for byte.
- `make check CHECK_TESTS='test_gtk_apply test_make_help'` passes; corrupting the settings edit,
  the marker check or a home helper makes the matching test fail; `tests/invariants.py` accepts
  the new row and `make check` is green.
- `make check CHECK_TESTS=test_gtk_apply` passes `TestHomeResolution`; making either helper skip
  the `HOME` fallback, accept a relative value, or return a path when both candidates are
  unusable makes a case fail.
- `make check CHECK_TESTS=test_gtk_apply` passes `TestMakeApplyGtk`; dropping any of its five
  named pins, or asserting a refusal pin only by return code while its named diagnostic
  substring (`DESTDIR must be empty`, `Python 3.10 or newer`, `tools/apply_gtk.py --remove`)
  goes unasserted, does not implement the pin above: mutating the matched message string in
  `tools/apply_gtk.py` or the Makefile recipes -- dropping `make install-gtk` from the
  missing-sheet error, `XDG_DATA_HOME`/`XDG_CONFIG_HOME` from a home refusal, or renaming an
  `apply-gtk`/`remove-gtk` help line -- makes the matching assertion fail.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move) and does not name `PLANS-DONE.md`.
- When the work lands, `grep -n '^### GTK opt-in, part 3/3: Select the installed GTK 3 and
  GTK 4 Platinum themes' PLANS.md` prints exactly one line whose number is greater than the
  `## Done` line's;
  `grep -F 'Select the installed GTK 3 and GTK 4 Platinum themes' PLANS-DONE.md` exits 1 with no
  output; `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`; and
  `git diff --name-status` does not name `PLANS-DONE.md`. The final report quotes the actual output
  of `grep -l "Select the installed GTK 3 and GTK 4 Platinum themes" PLANS.md PLANS-DONE.md`
  (exactly `PLANS.md`). The report's `SUMMARY` names the GTK selection tool and Makefile targets,
  and its `RISK` names the GTK settings files and libadwaita user CSS; a report that calls the
  change only backlog bookkeeping contradicts the diff.

### Platinum cursor theme, part 1/3: RGBA PNG encode, decode and read in tools/png (planned 2026-10-23 by the plan role; split from the too-large "Generate and ship the Xcursor arrow cursor artifact" entry) — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
After the move `grep -n '^## ' PLANS.md` must print exactly `## Planned` and `## Done`, and
`grep -F 'Platinum cursor theme, part 1/3: RGBA PNG encode, decode and read in tools/png' PLANS.md` must print exactly one line, whose
whose number is greater than the `## Done` line's. The final report quotes the actual output of
`grep -l "RGBA PNG encode, decode and read in tools/png" PLANS.md PLANS-DONE.md` (exactly
`PLANS.md`) and of `git diff --name-status`; never claim a file the diff does not name.

**Goal.** The cursor series needs PNG frames that keep alpha: part 2/3 ("requires part 1/3 landed")
decodes Xcursor image chunks that embed RGBA PNG, and part 3/3 generates them.
`tools/png` today only round-trips opaque pixels (`encode_png`, `decode_png`, `read_png`;
`tools/png/read.py` reduces everything through `_to_rgb`). Add `encode_rgba_png`, `decode_rgba` and
`read_rgba` beside the existing pipeline, in the same one-responsibility style, leaving every
existing function byte-identical and every existing caller untouched. Nothing in the repository
consumes the new names yet — that is deliberate ground-laying, not a finished feature, and the
later parts' headings name them. This part is independent of (and runs alongside) the queued GTK
opt-in parts 1/3–3/3.

**Reference grounding.** Codec plumbing carries no visual value and samples no pixel; the pixels
the later cursor parts pin come from part 3/3's own grid and carry its provenance exception. No
new KDE-required value appears in this part.

**Approach.**
- `tools/png/write.py`: add `encode_rgba_png(width, height, rgba)` beside `encode_png`: the same
  deterministic framing (colour type 6, bit depth 8, every row filter type 0, one IDAT at zlib
  level 9, so identical pixels produce identical bytes) but taking packed RGBA, rejecting anything
  that is not `bytes`/`bytearray` of exactly `width * height * 4` and reusing
  `_validate_dimension` for the bounds, each diagnostic naming the offending argument.
  `encode_png`'s behaviour and output stay byte-identical; nothing else in the module changes.
- `tools/png/read.py`: add `decode_rgba(data, max_rows=None)` that reuses the existing pipeline
  (`_CHANNELS`, `_validate_max_rows`, `_parse_ihdr`, `_check_pixel_limit`, `_collect_chunks` and
  the scanline unfiltering) but keeps four samples per pixel and bypasses `_to_rgb`'s palette
  reduction: it returns `(width, height, rgba)`, and its alpha is 255 wherever the source colour
  type has no alpha channel (every type in `_CHANNELS` — 0, 2, 3, 4 and 6). It touches neither
  `Image` nor `decode_png`.
- `tools/png/loader.py`: add `read_rgba(path)` that runs the existing `_read_png_data` file guards
  (non-blocking open, non-regular refusal, `_MAX_FILE_BYTES`, the LFS-pointer diagnostic) and hands
  the bytes to `decode_rgba`. `read_png` and `read_png_size` are untouched.
- `tools/png/__init__.py`: extend the module docstring's name list, the `__all__` list and the
  `from .…` imports with the three new public names, in the established order.
- `tests/test_png_rgba.py` (new, modelled on the codec tests): `encode_rgba_png` round-trips
  through `read_rgba` and `decode_rgba` byte for byte at every alpha value 0..255 in a small image;
  the encoded IHDR declares colour type 6; two runs with the same pixels produce identical bytes;
  a too-short or too-long RGBA buffer, a rejected dimension and a 3-bytes-per-pixel buffer raise
  `ValueError` naming the argument (reuse `tests/support/rejection_assertions.py`); `decode_rgba`
  on a colour-type-2 and a colour-type-3 fixture built with `tests/support/png_fixtures.py`'s
  `make_png` (the decoder tests' own builder) returns alpha 255 everywhere; and `encode_png`'s
  output for a small sample image is recorded as a literal in the test, so the RGBA work cannot
  disturb it.
- `docs/invariants.md`: in the existing `## tooling` section add one row — the RGBA PNG codec
  round-trips alpha byte for byte and leaves `encode_png`'s output unchanged — pinned to
  `tests/test_png_rgba.py`, column 3 `none`.

**Files touched.** `tools/png/write.py`, `tools/png/read.py`, `tools/png/loader.py`,
`tools/png/__init__.py`, `tests/test_png_rgba.py` (new), `docs/invariants.md`, and `PLANS.md`
(the entry moves to `## Done`; see Plan record). Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- `encode_rgba_png` followed by `read_rgba` returns the original RGBA bytes, at every alpha 0..255
  in the round-trip test; the encoded IHDR declares colour type 6; two runs with the same pixels
  produce identical bytes; an off-size buffer, a bad dimension or a 3-bytes-per-pixel buffer raises
  `ValueError` naming its argument; a colour-type-2 and a colour-type-3 PNG decode with alpha 255
  everywhere; `encode_png`'s pinned sample output is byte-identical to before this change, and no
  existing test changes its expectations.
- `make check` is green with the new module included; corrupting any of the pins above (encoding a
  wrong alpha row, dropping a guard, changing the framing) fails the matching test,
  `tests/invariants.py` accepts the new row, and `make check` is green.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move) and neither `PLANS-DONE.md` nor any `theme/` path.
- When the work lands, `grep -n '^### Platinum cursor theme, part 1/3: RGBA PNG encode, decode and read in tools/png' PLANS.md`
  prints exactly one line whose number is greater than the `## Done` line's, and
  `grep -F 'Platinum cursor theme, part 1/3: RGBA PNG encode, decode and read in tools/png'
  PLANS-DONE.md` exits 1 with no output.

### GTK opt-in, part 2/3: Uninstall the installed GTK 3 and GTK 4 Platinum themes (planned 2026-10-23 by the plan role; "requires part 1/3 landed") — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it
directly under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
Before editing, record `grep -n '^## Done$' PLANS.md`; after the move, `grep -n '^## ' PLANS.md`
must print exactly two lines (`## Planned` and `## Done`) and `grep -n '^### GTK opt-in, part
2/3: Uninstall the installed GTK 3 and GTK 4 Platinum themes' PLANS.md` must print exactly one
line whose number is greater than the `## Done` line's. The final report quotes the actual output
of `grep -l "Uninstall the installed GTK 3 and GTK 4 Platinum themes" PLANS.md PLANS-DONE.md`
(exactly `PLANS.md`) and of `git diff --name-status`; never claim a file the diff does not name.

**Goal.** Part 1/3 adds the opt-in `gtk` install family and the staged copies of the three sheets,
but leaves `make uninstall` alone, so uninstalling would leave an orphaned GTK theme and staging
leftovers in the shared `themes/org.macos8.desktop` directory. This part extends `make uninstall`
to remove exactly what part 1/3 installs — the three files, their three staging siblings and the
emptied `gtk-3.0`/`gtk-4.0` directories — and nothing else: `Kvantum/`, the theme directory itself
and every other theme stay in place. It is a follow-on, not a rewrite: the install half is part
1/3, and the selection that points GTK at the installed theme is part 3/3 (`requires part 2/3
landed`).

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget, so this part
adds no visual value and samples no pixel; the uninstall paths are GTK-required values the
reference set does not show. Part 1/3 already records that provenance exception on the install
row; this part extends that same row with the uninstall guarantee rather than adding a new one.

**Approach.**
- `Makefile`: in `_uninstall`, remove `index.theme`, `gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`
  relative to the part-1/3 `$(GTK_INSTALL_DIR)` and the three `.staging` siblings, then `rmdir`
  `gtk-3.0` and `gtk-4.0` when empty (`|| true`), leaving `Kvantum/` and every other theme
  directory alone. Extend the shared-parent comment to name the `themes/org.macos8.desktop`
  sharing. Do not touch `_install` or the `install_gtk` define.
- `tests/test_gtk_install.py`: add a `TestUninstall` class (modelled on the uninstall cases in
  `tests/test_kvantum_install.py`): after `make install INSTALL_PACKAGES=gtk`,
  `make uninstall` removes the three files and seeded staging leftovers, leaves a pre-planted
  `Kvantum/` file and a sibling second theme directory byte for byte, and repeats successfully.
- `README.md`: extend the part-1/3 GTK paragraph with one uninstall sentence — `make uninstall`
  removes the three GTK files, their `.staging` leftovers and the emptied `gtk-3.0`/`gtk-4.0`
  directories but leaves `Kvantum/` and the theme directory itself.
- `docs/invariants.md`: extend the part-1/3 `## gtk` row with the uninstall guarantee (remove only
  the three files, the staging siblings and the emptied `gtk-3.0`/`gtk-4.0` directories), still
  pinned to `tests/test_gtk_install.py`.

**Files touched.** `Makefile`, `tests/test_gtk_install.py`, `README.md`, `docs/invariants.md`,
and `PLANS.md` (the entry moves to `## Done`; see Plan record). Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- After `make install INSTALL_PACKAGES=gtk DESTDIR=<tmp>` with a planted `Kvantum/` file and a
  second theme directory under `<tmp>/share/themes/`, `make uninstall DESTDIR=<tmp>` removes
  `index.theme`, both `gtk-*/gtk.css` and any planted `.staging` siblings, removes the emptied
  `gtk-3.0` and `gtk-4.0` directories, and leaves the `Kvantum/` file, the second theme directory
  and the `org.macos8.desktop` directory itself untouched; a repeat uninstall succeeds, and so
  does an uninstall on a tree with no GTK install.
- `make check CHECK_TESTS='test_gtk_install test_make_help'` passes; dropping the staging-sibling
  removal, the empty-`rmdir` guard, or letting the removal touch `Kvantum/` makes the matching
  case fail; `tests/invariants.py` accepts the extended row and `make check` is green.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move) and does not name `PLANS-DONE.md`.
- When the work lands, `grep -n '^### GTK opt-in, part 2/3: Uninstall the installed GTK 3 and
  GTK 4 Platinum themes' PLANS.md` prints exactly one line whose number is greater than the
  `## Done` line's; `grep -F 'Uninstall the installed GTK 3 and GTK 4 Platinum themes'
  PLANS-DONE.md` exits 1 with no output; `grep -n '^## ' PLANS.md` prints exactly `## Planned`
  and `## Done`; and `git diff --name-status` does not name `PLANS-DONE.md`. The final report
  quotes the actual output of `grep -l "Uninstall the installed GTK 3 and GTK 4 Platinum themes"
  PLANS.md PLANS-DONE.md` (exactly `PLANS.md`). The report's `SUMMARY` names `make uninstall` and
  the three GTK files, and its `RISK` names the shared `themes/org.macos8.desktop` directory
  (`Kvantum/` must survive); a report that calls the change only backlog bookkeeping contradicts
  the diff.

### GTK opt-in, part 1/3: Install the GTK 3 and GTK 4 Platinum themes opt-in (planned 2026-10-23 by the plan role; part 1/3) — done 2026-10-23 by the feature role

**Goal.** Parts 1/4 and 2/4 ship `theme/gtk/org.macos8.desktop/index.theme`,
`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and
`theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, but no make target copies them, so a GTK
application cannot use them without a manual copy. Add an opt-in `gtk` install family, staged
copies, and an `install-gtk` target, keeping the default `make install` at the families
`INSTALL_PACKAGES` already names and copying no GTK files. Feature sent the 2026-10-21 entry this
splits back as too large for one run; this part carries the install half only. It installs the
three files but does not remove or select them: the uninstall cleanup is part 2/3
(`requires part 1/3 landed`) and the selection is part 3/3; neither is part of this diff.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget, so this part
adds no visual value and samples no pixel. The GTK theme directory name and its `gtk-3.0/` and
`gtk-4.0/` layout are GTK-required values the reference set does not show; record that in
`docs/invariants.md` rather than claiming a GTK reference crop. The sheets' palette is already
grounded through `tests/support/platinum_palette.py`.

**Approach.**
- `Makefile`: add `GTK_ID := org.macos8.desktop`, `GTK_PACKAGE := theme/gtk/$(GTK_ID)` and
  `GTK_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/themes/$(GTK_ID)`. This is the directory the
  Kvantum package already uses (`.../themes/org.macos8.desktop/Kvantum/`), so the two artifacts
  share a theme directory; do not use `install_package`, which would replace the whole directory
  and delete `Kvantum/`. Name the part-2/3 uninstall in the new comment so the sharing is
  documented before the removal lands.
- `Makefile`: add `gtk` to `INSTALL_FAMILIES` but not to the default `INSTALL_PACKAGES`; reword
  the comment above them so it says the default installs the families `INSTALL_PACKAGES` names and
  that `gtk` is opt-in. Add a `define install_gtk` after `install_kvantum`: create
  `$(GTK_INSTALL_DIR)/gtk-3.0` and `gtk-4.0`, copy `index.theme`, `gtk-3.0/gtk.css` and
  `gtk-4.0/gtk.css` to the hidden staging siblings `.index.theme.staging`,
  `gtk-3.0/.gtk.css.staging` and `gtk-4.0/.gtk.css.staging` under one EXIT trap that removes all
  three, then rename each into place. A failed copy leaves the previous files untouched and
  removes every staging sibling.
- `Makefile`: gate the `install_gtk` call on `gtk` in `_install`; do not touch `_uninstall` in
  this part.
- `Makefile`: add the public `install-gtk` target (runs the nested `$(MAKE) --no-print-directory
  install INSTALL_PACKAGES=gtk`), add it to `.PHONY` and the `help` target list.
- `tests/support/gtk_fixtures.py` (new): `GTK_ID`, `PACKAGE` and `SHIPPED_FILES` naming
  `index.theme`, `gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`, so this part's test and the part-2/3
  uninstall and part-3/3 selection tests can share them.
- `tests/test_gtk_install.py` (new, modelled on `tests/test_kvantum_install.py` because the theme
  shares `themes/org.macos8.desktop`): the source package's `shipped_files` equals
  `SHIPPED_FILES`; `make install INSTALL_PACKAGES=gtk` copies all three byte for byte beside a
  pre-existing `Kvantum/` file and is repeatable; a default `make install` writes no
  `index.theme` or `gtk-*/gtk.css` but still writes `Kvantum/`; a shadowed failing `install`
  leaves the previous three files intact and removes every staging sibling. The uninstall cases
  are part 2/3's additions to this module.
- `tests/support/installed_paths.py`: add `installed_gtk_theme(destdir)` returning
  `themes/org.macos8.desktop` below the module's `XDG_DATA_HOME`, and name the theme in the
  module docstring.
- `tests/support/theme_install.py`: add the GTK suite to the module docstring's artifact list and
  reword `install`'s docstring so it no longer says the default installs every family (the default
  installs every default family; `gtk` is opt-in).
- `README.md`: add a GTK paragraph after the Kvantum section that names `make install-gtk` (the
  `test_make_help` README check requires the exact target name), the installed path
  `$XDG_DATA_HOME/themes/org.macos8.desktop`, the shared `Kvantum/` directory, and that the
  default `make install` copies no GTK files. State that this part installs the files but does not
  select them, and hold the uninstall sentence for part 2/3. Do not add the GTK files to the
  default artifact list or change that list's count.
- `docs/invariants.md`: in the existing `## gtk` section add a row for the opt-in install pinned to
  `tests/test_gtk_install.py`, with the provenance exception that no reference screenshot shows a
  GTK widget and the theme directory layout is GTK-required.

**Files touched.** `Makefile`, `tests/support/gtk_fixtures.py` (new),
`tests/test_gtk_install.py` (new), `tests/support/installed_paths.py`,
`tests/support/theme_install.py`, `README.md`, `docs/invariants.md`, and `PLANS.md`
(the entry moves to `## Done`; see Plan record). Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- `make install INSTALL_PACKAGES=gtk DESTDIR=<tmp>` writes exactly `index.theme`,
  `gtk-3.0/gtk.css` and `gtk-4.0/gtk.css` under `<tmp>/share/themes/org.macos8.desktop/` and
  leaves a pre-existing `Kvantum/` file there untouched; the default `make install DESTDIR=<tmp>`
  still writes the default families and leaves all three GTK files absent.
- A shadowed `install` that fails on a GTK copy leaves the previous three files byte-identical and
  no `.staging` sibling.
- `make check CHECK_TESTS='test_gtk_install test_gtk_theme test_make_help test_theme_install'`
  passes; corrupting a staged copy, removing `gtk` from `INSTALL_FAMILIES`, or adding it to the
  default `INSTALL_PACKAGES` makes the matching test fail; `tests/invariants.py` accepts the new
  row and `make check` is green.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move), does not name `PLANS-DONE.md`, and the README's default artifact list does not gain a GTK
  entry or change its count.
- When the work lands, `grep -n '^### GTK opt-in, part 1/3: Install the GTK 3 and GTK 4
  Platinum themes opt-in' PLANS.md` prints exactly one line whose number is greater than the
  `## Done` line's;
  `grep -F 'Install the GTK 3 and GTK 4 Platinum themes opt-in' PLANS-DONE.md` exits 1 with no
  output; `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`; and
  `git diff --name-status` does not name `PLANS-DONE.md`. The final report quotes the actual output
  of `grep -l "Install the GTK 3 and GTK 4 Platinum themes opt-in" PLANS.md PLANS-DONE.md`
  (exactly `PLANS.md`). The report's `SUMMARY` names the opt-in GTK install family, the Makefile
  staging and the tests, and its `RISK` names the shared `themes/org.macos8.desktop` directory and
  the opt-in default; a report that calls the change only backlog bookkeeping contradicts the
  diff.

### Select the Lato body face in KDE, Plasma and Qt applications (planned 2026-10-22 by the plan role; UI font series part 3/3, body face only) — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it
directly under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
Before editing, record `grep -n '^## Done$' PLANS.md`; after the move, `grep -n '^## ' PLANS.md`
must print exactly two lines (`## Planned` and `## Done`) and `grep -n '^### Select the Lato body
face in KDE, Plasma and Qt applications' PLANS.md` must print exactly one line whose number is
greater than the `## Done` line's. The final report quotes the actual output of `grep -l "Select
the Lato body face in KDE, Plasma and Qt applications" PLANS.md PLANS-DONE.md` (exactly
`PLANS.md`) and of `git diff --name-status`; never claim a file the diff does not name.

**Goal.** Part 1/3 landed the Lato package and `make install` copies it, but the global theme's
`contents/defaults` names no font, so KDE, Plasma and Qt applications keep the user's font
(README's Status line calls the package "installed but not yet selected"). Make the global theme
select the installed `Lato` family for the general, menu, toolbar and smallest-readable fonts and
for window titles, at KDE's default point sizes, by adding those keys to `contents/defaults` —
the same declarative mechanism that already selects the colour scheme, icons, decoration and
Kvantum style. This is the body face of part 3/3 only: part 2/3 (a Chicago-style menu face) has no
confirmed redistribution licence and is not planned, so the menu bar and window titles wear Lato
for now and the part that vendors a Chicago-style face will update `menuFont`/`activeFont` then.
Monospaced text (`fixed`) keeps the user's fixed font because the package ships no monospace
face. No `Makefile`, `tools/` or install behaviour changes: `make install` still only copies the
family, and `make apply` selects it by re-applying the global theme.

**Reference grounding.** No reference pixel is sampled: Lato is this theme's substitute for
Charcoal (`theme/fonts/org.macos8.desktop/PROVENANCE.md`), and the point sizes are KDE's defaults
(10 for `font`, `menuFont`, `toolBarFont` and `activeFont`; 8 for `smallestReadableFont`), not a
metric measured in a screenshot. Record both as provenance exceptions in `docs/invariants.md`;
matching the reference's 12px body text would need a rendered comparison, which this part does
not claim.

**Approach.**
- `theme/look-and-feel/org.macos8.desktop/contents/defaults`: in `[kdeglobals][General]`, after
  `ColorScheme=MacOS8`, add `font=Lato,10`, `menuFont=Lato,10`, `toolBarFont=Lato,10` and
  `smallestReadableFont=Lato,8`; add a new `[kdeglobals][WM]` section between it and
  `[kdeglobals][Icons]` holding `activeFont=Lato,10`. Leave every other group, key and byte
  identical.
- `tests/test_lookandfeel.py`: add `WM_SECTION = "kdeglobals][WM"` beside the other section
  constants; in `TestDefaults.test_the_expected_sections_and_keys_are_set` put `WM_SECTION` after
  `DEFAULTS_SECTION`, extend the `DEFAULTS_SECTION` options to `["ColorScheme", "font",
  "menuFont", "toolBarFont", "smallestReadableFont"]` in file order, and expect
  `["activeFont"]` for `WM_SECTION`. Add
  `TestDefaults.test_fonts_name_the_installed_lato_family`: for each of the five
  (section, key) pairs, split the value at the first comma, assert the family is exactly
  `Lato`, assert the remaining point size parses as a positive integer, and assert
  `smallestReadableFont` is not larger than `font`. The test reads the shipped file only; it runs
  no KDE tool.
- `theme/fonts/org.macos8.desktop/PROVENANCE.md`: replace the `## Selection` paragraph's "it does
  not select it ... later part" with the selection this part adds (the five roles, KDE default
  sizes, monospace left alone, the Chicago-style face still pending part 2/3).
- `tests/test_fonts.py`: reword the module docstring's "but does not select it in KDE/Plasma/Qt"
  to say the global theme's defaults select the family; no assertion in the file changes.
- `README.md`: in the Status line change "installed but not yet selected" to "selected by the
  global theme"; in the Installing font sentence replace "this part installs the family but does
  not select it" with the five selected roles and KDE's default sizes, that monospaced text keeps
  the user's fixed font, and that menus and window titles use Lato until a Chicago-style face
  lands; in the `make apply` paragraph replace "(the Lato font package is installed but, like
  `make install`, not selected)" with a statement that `make apply` re-applies the global theme,
  which selects Lato, while a bare `make install` only copies it. Leave the artifact count
  (eight) and the target list unchanged.
- `docs/invariants.md`: extend the `## look-and-feel` row whose guarantee lists what
  `contents/defaults` selects to name the `Lato` font family, and add a `## fonts` row pinned to
  `tests/test_lookandfeel.py::TestDefaults`: the global theme selects the installed Lato family
  for the general, menu, toolbar, smallest-readable and window-title fonts; provenance exception:
  Lato is a Charcoal substitute, the point sizes are KDE defaults, and monospace keeps the user's
  fixed font.

**Files touched.** `theme/look-and-feel/org.macos8.desktop/contents/defaults`,
`tests/test_lookandfeel.py`, `theme/fonts/org.macos8.desktop/PROVENANCE.md`,
`tests/test_fonts.py`, `README.md`, `docs/invariants.md`, and `PLANS.md` (the entry moves to
`## Done`; see Plan record). Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- The defaults file holds exactly the five keys above with the `Lato` family and those sizes,
  `make check CHECK_TESTS='test_lookandfeel test_fonts'` passes, and changing `Lato` to another
  family, dropping a key, adding a sixth font role, or making a size zero, negative or
  non-numeric makes the matching `TestDefaults` assertion fail.
- `tests/invariants.py` accepts the extended look-and-feel row and the new fonts row, and
  `make check` is green.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move) and does not name `PLANS-DONE.md`, `Makefile` or any file under `tools/`; README still
  says eight artifacts and lists no new target.
- When the work lands, `grep -n '^### Select the Lato body face in KDE, Plasma and Qt
  applications' PLANS.md` prints exactly one line whose number is greater than the `## Done`
  line's; `grep -F 'Select the Lato body face in KDE, Plasma and Qt applications' PLANS-DONE.md`
  exits 1 with no output; and `git diff --name-status` does not name `PLANS-DONE.md`. The report's
  `SUMMARY` names the `contents/defaults` font selection and its `RISK` names KDE reading the
  font keys from the theme defaults and the menu/window-title face borrowing Lato until a
  Chicago-style face lands; a report that calls the change only backlog bookkeeping contradicts
  the diff.

### Vendor the Lato body font and install it (planned 2026-10-21 by the plan role; part 1/3) — done 2026-10-22

**Plan record.** The backlog move is part of this entry and must not touch any other file. Before
starting, record `grep -n '^## Done$' PLANS.md` (one line) and `grep -n '^### Vendor the Lato body
font and install it' PLANS.md` (one line). When the work is done, cut the whole entry from
`## Planned` and paste it directly under that `## Done` heading, which stays the file's last
heading, adding `— done YYYY-MM-DD` to its `### ` heading. Do **not** add a third `## ` heading, do
**not** rename or move `## Planned`/`## Done`, and do **not** edit `PLANS-DONE.md`: tumwater moves
the entry from `## Done` into that archive after the merge, so a feature-run diff to
`PLANS-DONE.md` is wrong even when it looks like the finished archive. After the move,
`grep -n '^## ' PLANS.md` must print exactly two lines (`## Planned` and `## Done`);
`grep -n '^### Vendor the Lato body font and install it' PLANS.md` must print exactly one line
whose number is greater than `## Done`'s line number; `grep -F 'Vendor the Lato body font'
PLANS-DONE.md` must exit 1 with no output; and `git diff --name-status` must not name
`PLANS-DONE.md`. The final `VERIFIED` line must quote the actual output of `grep -l "Vendor the Lato
body font" PLANS.md PLANS-DONE.md` (exactly `PLANS.md`) and of `git diff --name-status`; do not make
either claim unless that command printed it. If the entry cannot be moved, leave it under
`## Planned` and say so; never edit `PLANS-DONE.md`.

**Goal.** QUESTIONS.md's font answer (2026-10-19) directs the theme to vendor a Chicago/Charcoal-style
font, but no `theme/fonts` directory exists and `make install` copies no font. Ship Lato Regular and
Bold (SIL OFL 1.1, already installed on this machine, so no network fetch) as the Charcoal-style
body face under a new `theme/fonts/org.macos8.desktop` artifact, installed to
`$XDG_DATA_HOME/fonts/org.macos8.desktop`, so a later selection part can name the `Lato` family.
This is part 1/3 of the UI-font series: it vendors and installs the body face only. Part 2/3 will
vendor a Chicago-style menu face once a redistribution licence is confirmed (the ChicagoFLF
provenance is still unresolved, so it is deliberately not shipped here); part 3/3 will select the
installed families in KDE/Plasma/Qt. Neither sibling is in the queue yet, and this part does not
depend on them.

**Reference grounding.** `aboutsystem_betawiki.png`'s dialog body draws Charcoal's narrower
humanist forms at 12px, but the theme ships no Apple font and samples no font pixel: Lato is this
theme's substitute for Charcoal, and `PROVENANCE.md` records it as an approximation rather than a
reference anchor. The two screenshot crops (the menu bar in `desktop_betawiki.png` and the
`System` dialog body in `aboutsystem_betawiki.png`) are recorded there as context for the later
Chicago/selection parts, not copied.

**Approach.**
- Add `theme/fonts/org.macos8.desktop/Lato-Regular.ttf` and `Lato-Bold.ttf`, copied byte for byte
  from `/usr/share/fonts/truetype/lato/` (657,212 and 657,188 bytes; `.gitattributes` leaves
  `.ttf` out of Git LFS, so they are committed directly). Add `LICENSE-Lato.txt` as an exact
  byte-for-byte copy (`cp`, not an editor, heredoc or `sed`) of
  `/usr/share/doc/fonts-lato/copyright`: 5,157 bytes, SHA-256
  `1e6ccc54aa0b0aa4188cda121174f17cf1c28bac9734749bbe1128bb6dd89a97`, ending in the
  `Files: debian/*` stanza's `... for the text of the GNU General Public License version 2".` with
  **no trailing newline**. Do not append a newline (the prior attempt did, producing 5,158 bytes
  and SHA-256 `6664793a025c96e6bb4f319a8c8d5b929296bf0df229db8b1c19e80a5988eb25`); an editor or
  shell substitution that adds one makes the pinned test fail. The `Files: *` stanza carries the
  upstream copyright line and the complete OFL-1.1 body, while the trailing `Files: debian/*`
  stanza is Debian packaging GPL-2+ text that does not cover the fonts. `PROVENANCE.md` records the
  local source paths, the upstream source (`http://www.latofonts.com`, Debian package `fonts-lato`),
  the SHA-256 digests of all three files, that `LICENSE-Lato.txt` is the source byte for byte
  including its missing final newline (not a newline-appended variant), the internal family name
  `Lato`, the `debian/*` stanza's scope, and why the face is an approximation of Charcoal.
- `Makefile`: add `FONT_ID := org.macos8.desktop`, `FONT_PACKAGE := theme/fonts/$(FONT_ID)` and
  `FONT_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/fonts`; add `fonts` to `INSTALL_FAMILIES` and to
  the default `INSTALL_PACKAGES`; in `_install` create `$(FONT_INSTALL_DIR)` and copy the package
  with the existing `install_package` swap; in `_uninstall` remove
  `$(FONT_INSTALL_DIR)/$(FONT_ID)` together with its `.staging` and `.old` siblings. Update the
  `help` line's default family list (the default is compared against the `?=` value by
  `tests/test_make_help.py`). Update the two family comments: the `INSTALL_FAMILIES` comment's
  `all seven` becomes `all eight`, and `_uninstall`'s shared-parent-directory comment lists
  `fonts` with the other families.
- `tests/support/installed_paths.py`: add `installed_fonts_dir(destdir)` returning the `fonts`
  directory under `$DESTDIR`'s data home, built from the module's `XDG_DATA_HOME` constant like
  the other helpers, and `installed_font_package(destdir, package_id)` returning its `package_id`
  child, matching the Makefile paths; add the font package to the module docstring's list of
  installed artifacts.
- `tests/support/install_lifecycle_cases.py`: add the font suite to the module docstring's family
  list and change the `MAKE_PACKAGES` comment's `instead of all seven` to `instead of all eight`.
  `tests/support/install_failure_cases.py`: change the same `instead of all seven` comment to
  `instead of all eight` (the font package uses the shared staging swap, so the family count it
  describes gains one). `tests/support/theme_install.py`: add the font package to its module
  docstring's list of installable artifact suites.
- `tests/test_fonts.py` (new): `TestFontFiles` parses each TTF's sfnt `name` table (name ID 1 and
  2) with `struct` and asserts the family is `Lato` and the subfamily is `Regular`/`Bold`; pins the
  SHA-256 of both TTFs (`6f6940be0835c3ddec9199e5fc42be4cbc61ebcfd58c623fdf719366253f1780` and
  `bf1b8130069b44b9148eeece35e5423bedac49777ba746615b826b8276574a7b`) and of `LICENSE-Lato.txt`
  (`1e6ccc54aa0b0aa4188cda121174f17cf1c28bac9734749bbe1128bb6dd89a97`), asserts that licence's
  last byte is not a newline, and asserts `PROVENANCE.md` names all three digests; asserts
  `LICENSE-Lato.txt` contains `License: OFL-1.1`, the copyright line
  `(c) 2010-2011, Łukasz Dziedzic` and the OFL clause heading `PERMISSION & CONDITIONS` (the file
  has no `SIL OPEN FONT LICENSE` heading, so do not assert that phrase). `TestFontsInstall`
  subclasses `InstallLifecycleCases` with `MAKE_PACKAGES = "fonts"`,
  `PACKAGE_DIR = "theme/fonts/org.macos8.desktop"`, `INSTALLED_FILES` naming the four files, and
  `installed_parent`/`installed_package_dir` overridden to the new helpers, so it gets the
  byte-for-byte, registry-coverage, repeat-install and uninstall-leftover checks once. Add
  `test_uninstall_leaves_a_sibling_font_family`, which creates `$fonts/other-family` before the
  uninstall and asserts it survives.
- `tests/test_theme_install.py`: in `TestWhitespaceInInstallPaths`, add
  `installed_paths.installed_font_package(destdir, package)` to the `directories` list checked
  before and after the round trip, and change both `seven artifacts` docstrings to eight. In
  `TestInstallPackages.test_one_family_installs_only_that_family`, add
  `installed_paths.installed_fonts_dir(tmp)` to `other_dirs` so installing `color-scheme` leaves
  `fonts/` absent.
- `README.md`: change each of the four `seven artifacts` sentences -- the Status line, the
  Installing paragraph, the uninstall paragraph and the `make apply` paragraph -- to eight, and add
  the `org.macos8.desktop` Lato font package to each list with its
  `$XDG_DATA_HOME/fonts/org.macos8.desktop` path, its OFL-1.1 licence and the note that this part
  installs the family but does not select it. In the uninstall paragraph, add `fonts/` to the
  shared-directory list. Leave the Status paragraph's archive sentence (`... fixed bugs are
  archived in BUGS-FIXED.md.`) byte-identical: it is out of scope for this part, and mentioning
  `PLANS-DONE.md` here would contradict the Plan record above.
- `docs/invariants.md`: add a `## fonts` section between `## desktoptheme` and `## gtk` (every
  `theme/` subsystem needs one) with a row for the shipped Lato family/digests pinned to
  `tests/test_fonts.py::TestFontFiles` and a row for the install/uninstall lifecycle pinned to
  `tests/test_fonts.py::TestFontsInstall`, with the provenance exception stating that Lato is a
  Charcoal substitute, not a sampled reference face.

**Files touched.** `theme/fonts/org.macos8.desktop/Lato-Regular.ttf` (new),
`theme/fonts/org.macos8.desktop/Lato-Bold.ttf` (new),
`theme/fonts/org.macos8.desktop/LICENSE-Lato.txt` (new),
`theme/fonts/org.macos8.desktop/PROVENANCE.md` (new), `Makefile`,
`tests/support/installed_paths.py`, `tests/support/install_lifecycle_cases.py`,
`tests/support/install_failure_cases.py`, `tests/support/theme_install.py`,
`tests/test_fonts.py` (new), `tests/test_theme_install.py`, `README.md`,
`docs/invariants.md`, and `PLANS.md` (the entry moves to `## Done`; see Plan record). Do not edit
`PLANS-DONE.md`.

**Acceptance criteria.**
- `make install INSTALL_PACKAGES=fonts DESTDIR=<tmp>` writes exactly the four files above under
  `$XDG_DATA_HOME/fonts/org.macos8.desktop/`; a default `make install DESTDIR=<tmp>` writes them
  too; `make uninstall` removes that directory and its `.staging`/`.old` leftovers while leaving a
  sibling font family's directory in place (pinned by
  `tests/test_fonts.py::TestFontsInstall.test_uninstall_leaves_a_sibling_font_family`).
- `cmp -s theme/fonts/org.macos8.desktop/LICENSE-Lato.txt
  /usr/share/doc/fonts-lato/copyright` exits 0: the shipped licence is the source's 5,157 bytes
  including its missing final newline, not the 5,158-byte newline-appended variant.
- `make check CHECK_TESTS=test_fonts` passes; removing either TTF, changing a byte, renaming the
  family or subfamily in the font, editing `LICENSE-Lato.txt` (including appending a newline), or
  dropping a digest from `PROVENANCE.md` makes it fail.
- `tests/invariants.py` accepts `theme/fonts` with its `## fonts` section, and
  `make check CHECK_TESTS=test_theme_install test_make_help` passes with the new family.
- `grep -n seven README.md Makefile tests/support/install_lifecycle_cases.py
  tests/support/install_failure_cases.py tests/test_theme_install.py` finds no artifact-count
  text, and the README Status paragraph's archive sentence still reads exactly `Open work is
  tracked in PLANS.md (planned features), BUGS.md (known bugs), and QUESTIONS.md (decisions
  needed); fixed bugs are archived in BUGS-FIXED.md.` (a diff that rewrites it fails this plan).
- `git diff --name-status` names only the files listed under "Files touched"; an edit outside that
  list is out of scope for this part.
- When the work lands, `grep -n '^### Vendor the Lato body font and install it' PLANS.md` prints
  exactly one line whose number is greater than the `## Done` line's; `grep -F 'Vendor the Lato
  body font' PLANS-DONE.md` exits 1 with no output; `grep -n '^## ' PLANS.md` prints exactly
  `## Planned` and `## Done`; and `git diff --name-status` does not name `PLANS-DONE.md`. The final
  report quotes the actual output of `grep -l "Vendor the Lato body font" PLANS.md PLANS-DONE.md`
  (exactly `PLANS.md`) and of `git diff --name-status`; a `VERIFIED` line that says otherwise
  contradicts those commands and fails this plan.
- No `kdeglobals` write, global-theme `contents/defaults` change, `tools/apply_*` change, GTK,
  Firefox or README archive-sentence change is made in this part; `make check` is green.

### Ship a GTK 4/libadwaita Platinum stylesheet (planned 2026-10-21 by the plan role; GTK series part 2/4) — done 2026-10-21

**Goal.** Part 1/4 landed the standalone GTK 3 sheet and its test; GTK 4 applications, including
libadwaita ones such as Ghostty (QUESTIONS.md), still draw the system GTK 4 theme. Add a second
standalone sheet at `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css` that redefines the GTK and
libadwaita surface colours from the Platinum palette and paints the same Platinum controls and
bevels in the GTK 4 widget tree. This part ships the stylesheet and its test only: no install
target, no selection mechanism and no README claim. Part 3/4 installs and selects the GTK 3 and
GTK 4 sheets; part 4/4 adds the Firefox chrome. Neither sibling is planned yet, and this part
does not require them. Part 1/4 is finished in `PLANS-DONE.md`; its `index.theme` and
`gtk-3.0/gtk.css` are not changed here.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget. Take every
colour from `tests/support/platinum_palette.py` (`FACE` `#DDDDDD`, `WHITE`, `GREY` `#999999`,
`BLACK`, `BUTTON_SHADOW` `#AAAAAA`, `TROUGH` `#EEEEEE`, `SELECTION` `#CCCCFF`) and the etched
separator's dark half `#888888` that `tests/test_desktoptheme_line.py` pins. Record in the CSS
header and in `docs/invariants.md` that the palette is reference-grounded while the GTK 4
geometry is this theme's adaptation. Do not redefine `success_*`, `warning_*`, `error_*`,
`destructive_*` or the translucent `*_shade_color` roles: the reference set gives no Platinum
value for a status colour or a dimming overlay, so those keep the GTK 4 stylesheet's built-in
defaults rather than an invented value.

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css` (new): a standalone sheet with no `@import`, no
  `url(...)` and no Adwaita mention in its text. Define the GTK named colours with the values
  part 1 uses: `theme_bg_color`/`theme_fg_color`, `theme_base_color`/`theme_text_color`,
  `theme_selected_bg_color`/`theme_selected_fg_color`, `borders` and `unfocused_borders`.
  Define the opaque libadwaita surface names with those same values: `accent_bg_color` =
  `SELECTION`, `accent_fg_color` = `BLACK`, `window_bg_color`/`window_fg_color`,
  `view_bg_color` = `WHITE`/`view_fg_color` = `BLACK`, `headerbar_bg_color` `FACE`,
  `headerbar_fg_color` `BLACK`, `headerbar_border_color` `BLACK`,
  `headerbar_backdrop_color` `FACE`, `popover_bg_color` `FACE`, `popover_fg_color` `BLACK`,
  `card_bg_color` `FACE`, `card_fg_color` `BLACK`, `dialog_bg_color` `FACE`,
  `dialog_fg_color` `BLACK`, `sidebar_bg_color` `FACE`, `sidebar_fg_color` `BLACK`,
  `sidebar_backdrop_color` `FACE`, `sidebar_border_color` `BLACK`,
  `secondary_sidebar_bg_color` `FACE`, `secondary_sidebar_fg_color` `BLACK`,
  `secondary_sidebar_backdrop_color` `FACE`, `secondary_sidebar_border_color` `BLACK`,
  `thumbnail_bg_color` `WHITE`, `thumbnail_fg_color` `BLACK`, and
  `scrollbar_outline_color` `BLACK`.
- Write these scoped rules (no universal `*` selector):
  - `window, .background`: `FACE` background, `BLACK` text.
  - `headerbar, .titlebar`: `FACE` face, `background-image: none`, `1px solid BLACK` border,
    `border-radius: 0`, `box-shadow: none`; `headerbar` with `border-width: 0 0 1px 0`.
  - `button`: `FACE` face, no background image, `1px solid BLACK`, `border-radius: 0`,
    `box-shadow: inset 1px 1px WHITE, inset -1px -1px BUTTON_SHADOW`; `button:hover` keeps the
    `FACE`; `button:active, button:checked` inverts the bevel to
    `inset 1px 1px BUTTON_SHADOW, inset -1px -1px WHITE`.
  - `entry`: `WHITE` face, `1px solid BLACK`, `border-radius: 0`,
    `box-shadow: inset 1px 1px GREY`, `BLACK` text.
  - `notebook > header`: `FACE` background, `1px solid BLACK` border. Cover the same six tab
    states as part 1, each in plain and `notebook > header > tabs > tab` form: base, hover,
    checked, checked+hover, backdrop and backdrop+checked. Base/hover/backdrop carry the raised
    `FACE` face, `1px solid BLACK`, `border-radius: 0` and
    `box-shadow: inset 1px 1px WHITE, inset -1px -1px GREY`; the checked states use
    `border-bottom-color: FACE` and `box-shadow: none`.
  - `popover > contents, popover > arrow`: `FACE` face, `1px solid BLACK`, `border-radius: 0`,
    `box-shadow: none`.
  - `popover.menu modelbutton:hover, popover.menu modelbutton:selected`: `SELECTION` background.
  - `scrollbar > range > trough`: `TROUGH` background, `1px solid BLACK`, `border-radius: 0`.
  - `scrollbar > range > trough > slider`: `FACE` face, no background image,
    `1px solid BLACK`, `border-radius: 0`, `margin: 0`, and the raised `WHITE`/`GREY` bevel.
  - `.toolbar`: `FACE` face with the etched rule `border-bottom: 1px solid #888888` and
    `box-shadow: inset 0 -1px WHITE`.
- `tests/support/gtk_css.py` (new): move `parse_css` and the `DEFINE_COLOR`, `COMMENT`, `RULE`
  and `HEX` regular expressions out of `tests/test_gtk_theme.py` unchanged, with a short module
  docstring saying the two GTK sheet tests share them. Update `tests/test_gtk_theme.py` to import
  `HEX` and `parse_css` from `support.gtk_css` and delete its local copies, so both tests use one
  parser rather than a second copy of the same rules.
- `tests/test_gtk4_theme.py` (new): mirror `TestGtkTheme`. Pin the exact `@define-color` map,
  every selector/property above, and all six tab-state groups in both selector forms. Assert the
  CSS contains no `@import`, no `url(` and no Adwaita text; assert the only six-digit hex
  literals are exactly `{BLACK, WHITE, GREY, FACE, BUTTON_SHADOW, TROUGH, SELECTION, ETCH_DARK}`;
  assert no universal `*` selector; assert `border-radius: 0` on the window, headerbar, button,
  entry, notebook-header, popover, scrollbar and tab rules.
- `docs/invariants.md`: in the existing `## gtk` section add a second row: "The standalone GTK 4
  stylesheet redefines the Platinum palette and opaque libadwaita surface colours and paints the
  scoped Platinum control rules, including every tab state, without importing another
  stylesheet." pinned to `tests/test_gtk4_theme.py::TestGtk4Theme`, with the same provenance
  exception as part 1.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css` (new),
`tests/support/gtk_css.py` (new), `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- The new sheet exists at `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css` and carries the exact
  `@define-color` map and the scoped rules above; the original `index.theme` and
  `gtk-3.0/gtk.css` are unchanged.
- `make check CHECK_TESTS='test_gtk_theme test_gtk4_theme'` passes. Adding an `@import` or `url(`,
  removing a `@define-color` or a listed rule/state, replacing a bevel or the scoped
  `border-radius: 0`, or introducing a Breeze/default colour literal makes the GTK 4 test fail;
  the extracted parser leaves every part 1 assertion passing.
- The parsed GTK 4 hex set is exactly the eight pinned colours, and the CSS redefines no
  status or translucent shade role.
- `tests/invariants.py` accepts the second `## gtk` row, and `make check` is green.
- No install target, selection mechanism, `kdeglobals` write, README change or Firefox change is
  made in this part.

### Ship a GTK 3 Platinum theme for GTK applications (planned 2026-10-21 by the plan role; part 1/4) — done 2026-10-21

**Goal.** No GTK theme exists in the repository (no `theme/gtk` directory), so GTK 3
applications -- including Firefox's GTK chrome -- keep the desktop's Breeze GTK theme. Ship a
user-installable `org.macos8.desktop` GTK 3 theme whose windows, header bars, buttons, entries,
notebook tabs, menus, scroll bars and toolbars paint the Platinum palette and square bevels.
This is part 1/4 of the GTK and Firefox application-chrome series; it ships the artwork only.
Part 2/4 will ship the GTK 4/libadwaita CSS, part 3/4 installs and selects both, and part 4/4
adds the opt-in Firefox chrome. Those sibling plans are not in this queue yet and will be added
as separate entries.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget. Take every
colour from the already reference-grounded Platinum palette in
`tests/support/platinum_palette.py`: `FACE` `#DDDDDD`, `WHITE`, `GREY` `#999999`, `BLACK`,
`BUTTON_SHADOW` `#AAAAAA` (the raised push button's shadow), `TROUGH` `#EEEEEE` and `SELECTION`
`#CCCCFF`. The `#888888` etched-separator dark half is the value
`tests/test_desktoptheme_line.py` pins to the reference. Record in the CSS header and in
`docs/invariants.md` that the palette is reference-grounded while the GTK-specific geometry is
this theme's adaptation; do not claim a GTK reference crop.

**Approach.**
- `theme/gtk/org.macos8.desktop/index.theme`: `[Desktop Entry]` with `Type=X-GNOME-Metatheme`,
  `Name=Mac OS 8.6 Platinum`, `Encoding=UTF-8` and a short `Comment=`, plus an
  `[X-GNOME-Metatheme]` group naming the same theme.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: write a standalone sheet -- **do not**
  `@import` Adwaita. The rejected implementation imported Adwaita and then tried to out-specify
  its reorderable-tab rules; a standalone theme has no imported sheet whose
  `.reorderable-page` selectors can win, so the tab face cannot fall back to Adwaita's
  translucent or transparent fills. Define the theme colours with
  `@define-color theme_bg_color #DDDDDD;`, `theme_fg_color #000000`,
  `theme_base_color #FFFFFF`, `theme_text_color #000000`, `theme_selected_bg_color #CCCCFF`,
  `theme_selected_fg_color #000000`, `borders #000000` and `unfocused_borders #999999`.
  Write exactly these scoped rules (no `*` selector):
  - `window, .background`: `#DDDDDD` background, `#000000` text.
  - `headerbar, .titlebar`: `#DDDDDD` face, no background image, `1px solid #000000` border,
    `border-radius: 0`, no box shadow; `headerbar` keeps only its 1px black bottom rule.
  - `button`: `#DDDDDD` face, no background image, `1px solid #000000` border,
    `border-radius: 0`, `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA`;
    `button:hover` keeps the same face; `button:active, button:checked` inverts the bevel to
    `inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF`.
  - `entry`: white face, `1px solid #000000` border, `border-radius: 0`, sunken
    `box-shadow: inset 1px 1px #999999`, black text.
  - `notebook > header`: `#DDDDDD` background, black border. Every tab state carries the
    raised `#DDDDDD` face with `1px solid #000000`, `border-radius: 0` and
    `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999`; the checked states drop the
    bottom border to `#DDDDDD` and the bevel shadow. Cover both the plain and `.reorderable-page`
    forms in each state: base (`tab, tab.reorderable-page`), hover (`tab:hover,
    tab.reorderable-page:hover`), checked (`tab:checked, tab.reorderable-page:checked`),
    checked+hover (`tab:checked:hover, tab.reorderable-page:checked:hover`), backdrop
    (`tab:backdrop, tab.reorderable-page:backdrop`) and backdrop+checked
    (`tab:backdrop:checked, tab.reorderable-page:backdrop:checked`). The checked and backdrop
    states explicitly paint the face rather than leaving it to a default: the rejected diff left
    a non-hovered checked reorderable tab translucent and a backdrop one transparent.
  - `menu, .menu, popover, .popover`: `#DDDDDD` face, `1px solid #000000` border,
    `border-radius: 0`; `menuitem:hover, .menuitem:hover` paints `#CCCCFF`.
  - `scrollbar`: `#EEEEEE` trough with a `1px solid #000000` border; `scrollbar slider` is the
    raised `#DDDDDD` thumb with a `1px solid #000000` border, `border-radius: 0` and
    `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999`.
  - `toolbar, menubar`: `#DDDDDD` face with the reference's etched rule,
    `border-bottom: 1px solid #888888` and `box-shadow: inset 0 -1px #FFFFFF`.
- `tests/test_gtk_theme.py` (new): `TestGtkTheme` reads the two files as text. Pin the
  `index.theme` keys above; pin every `@define-color` name/value, and every selector/property
  above (a parser over brace blocks or explicit substring checks is fine). Assert the CSS
  contains no `@import` and no `Adwaita` text, so a future edit cannot reintroduce the imported
  rules that outranked the tabs. Assert the six tab-state selector groups above each exist with
  the raised face and bevel, and that each checked group also drops the bottom border and bevel,
  so neither a missing state nor a translucent/transparent fallback passes. Assert
  the only six-digit hex literals in the CSS are exactly
  `{BLACK, WHITE, GREY, FACE, BUTTON_SHADOW, TROUGH, SELECTION, ETCH_DARK}`, importing the
  palette constants from `support.platinum_palette` and defining `ETCH_DARK = "#888888"` beside
  the existing line-test value, so a stray Breeze colour fails. Assert the rules for
  `headerbar, .titlebar`, `button`, `entry`, `notebook > header > tabs > tab`,
  `menu, .menu, popover, .popover` and `scrollbar slider` each carry `border-radius: 0`, and
  that no rule uses the universal `*` selector.
- `docs/invariants.md`: add a `## gtk` section (a `theme/gtk` subsystem needs its own section;
  do not fold this into `tooling`) with one row: "The standalone GTK 3 Platinum theme redefines
  the Platinum palette and paints the scoped Platinum control rules, including every plain and
  reorderable tab state, without importing Adwaita." pinned to
  `tests/test_gtk_theme.py::TestGtkTheme`, provenance exception: no reference screenshot shows a
  GTK widget, so the palette comes from the pinned Platinum values and the geometry is this
  theme's adaptation.

**Files touched.** `theme/gtk/org.macos8.desktop/index.theme` (new),
`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` (new), `tests/test_gtk_theme.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- The two new files exist under `theme/gtk/org.macos8.desktop/`; the CSS imports nothing,
  defines the eight theme colours with the values above, and carries every scoped control rule
  and all six plain/reorderable tab-state groups.
- `make check CHECK_TESTS=test_gtk_theme` passes, and adding an `@import`, removing any
  `@define-color`, any listed selector or tab-state group, a bevel shadow or the scoped
  `border-radius: 0` makes it fail.
- The parsed CSS hex set is exactly the eight pinned colours; no Breeze or other colour is
  introduced.
- `tests/invariants.py`'s cross-check accepts the new `## gtk` section and
  `tests/test_gtk_theme.py::TestGtkTheme`.
- No install target, GTK selection, `kdeglobals` write or Firefox change is added in this part;
  `make check` is green.

### Ground the desktop theme dialog body's raised bevel shadow in the reference Get Info window body (planned 2026-10-19 by the plan role) — done 2026-10-21

**Goal.** `theme/desktoptheme/org.macos8.desktop/dialogs/background.svg` paints the raised
window body's bevel shadow `#999999`, and its header claims "the reference window body itself is
flat, so no window-body pixel grounds those two". But the Get Info window body in
`macos8.6-screenshots/aboutsystem_betawiki.png`, inside its 6px Aurorae frame, is a clean lossless
raised Platinum body: the frame's inner black row/column is the visible outline, a 1px `#FFFFFF`
highlight runs inside the top/left, a 1px `#AAAAAA` shadow inside the bottom/right, the face is
`#DDDDDD`, and the top-right and bottom-left mixed corners leave a `#DDDDDD` face pixel where the
bands would meet. Correct the shadow to `#AAAAAA`, notch those two corners, and pin them to those
pixels.
This is the same raised shadow the Kvantum `button` element and the desktop theme `button.svg`
already use (`PLANS-DONE.md`; PLANS.md), while the reference's sunken field keeps `#999999`, so
only the raised bevel moves. The other desktop-theme raised faces (`widgets/frame.svg`'s raised
state, `widgets/scrollbar.svg`'s thumb, `widgets/toolbar.svg`, `widgets/actionbutton.svg`) are
separate surfaces that the reference's window body does not directly ground; they keep `#999999`
and their shared corner geometry, and are out of scope.

**Reference.** `macos8.6-screenshots/aboutsystem_betawiki.png` (beta `8.6b2c4L8`, the same image
the Kvantum button/check-box groundings use). The Get Info window body: the 6px Aurorae frame's
inner black row/column at top `(200,46)`, left `(12,200)`, bottom `(200,419)` and right
`(354,200)` is `#000000`; the body paints top `(200,47)=#FFFFFF`, left `(13,200)=#FFFFFF`, face
`(200,100)=#DDDDDD`, bottom `(200,418)=#AAAAAA` (uniform across x=40..339) and right
`(353,200)=#AAAAAA`. The four 3x3 corners start at `(12,46)`, `(352,46)`, `(12,417)` and
`(352,417)`; their top-right and bottom-left mixed corners `(353,47)` and `(13,418)` are
`#DDDDDD`, while the shared raised table paints the shadow and highlight there. The retail
`#999999` sunken-field shadow (`firstboot_betawiki.png`) is unchanged.

**Approach.**
- `dialogs/background.svg`: in `bottom`, `right` and the four shadow corners, change the bevel
  shadow `#999999` to `#AAAAAA`; notch the top-right and bottom-left mixed corners to the
  reference's `#DDDDDD` face pixel; leave the `#000000` outline, `#FFFFFF` highlight and
  `#DDDDDD` face elsewhere. Correct the header: the reference window body is a raised bevel, name
  `aboutsystem_betawiki.png` and the sampled pixels (including that the black edge is the Aurorae
  frame's inner row/column), and drop the "flat" claim and the "same bevel rule as
  scrollbar.svg's thumb" cross-reference (the thumb keeps `#999999`).
- `tests/svg_assertions/faces.py`: give `face_corners` a `shadow="#999999"` keyword that rebuilds
  `RAISED_FACE_CORNERS` with the caller's shadow and substitutes it into the sunken tables;
  `face_edge_bands` already takes the keyword from the button plan.
- `tests/svg_assertions/pixels.py`: thread the same `shadow="#999999"` keyword through
  `assert_face_bevel` into `face_edge_bands`/`face_corners`, and add a `corners=None` override for
  a surface whose reference corner geometry differs.
- `tests/support/platinum_palette.py`: no change needed; the button plan already gave
  `assert_fill_palette` its `shadow=GREY` keyword, so this plan reuses it.
- `tests/support/raised_face_case.py`: add a `SHADOW = GREY` class attribute and a `CORNERS =
  None` override, and pass both to `assert_face_bevel`; pass `SHADOW` to `assert_fill_palette`.
- `tests/test_desktoptheme_dialog.py`: set `SHADOW = "#AAAAAA"` and `CORNERS` to the reference's
  four 3x3 corner table on `TestDialogBackground`; add
  `TestDialogBackgroundRaisedReference(ReferenceScreenshotMixin, unittest.TestCase)` with
  `REFERENCE`/`MAX_ROWS` from `support.aurorae_fixtures` (the existing
  `TestDialogBackgroundReference` already covers the archiveorg face) that re-derives the four
  colours and four 3x3 corners from the anchors above and asserts the rendered edges and corners,
  skipping when the Git LFS image is not materialized.
- `tests/test_svg_assertions_faces.py` and `tests/test_svg_assertions_pixels.py`: pin the new
  `shadow` keyword in the helper tables and `assert_face_bevel`, and the corner-table override.
- `tests/test_reference_image.py`: add the new reader to the aboutsystem shared-decode-bound
  check.
- `docs/invariants.md`: extend the `dialogs/background.svg` guarantees to name the reference's
  raised bevel shadow and mixed corners.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/dialogs/background.svg`,
`tests/svg_assertions/faces.py`, `tests/svg_assertions/pixels.py`,
`tests/support/raised_face_case.py`, `tests/test_desktoptheme_dialog.py`,
`tests/test_svg_assertions_faces.py`, `tests/test_svg_assertions_pixels.py`,
`tests/test_reference_image.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/aboutsystem_betawiki.png 200 418` prints
  `170,170,170 #AAAAAA`, `... 200 47` prints `#FFFFFF`, `... 12 200` prints `#000000`,
  `... 200 100` prints `#DDDDDD`, and `... 353 47` and `... 13 418` print `#DDDDDD`.
- `dialogs/background.svg`'s parsed fill set is exactly `{#000000, #FFFFFF, #AAAAAA, #DDDDDD}`
  and `test_desktoptheme_dialog.py` passes.
- `TestToolBar` and the frame/scrollbar/actionbutton raised tests still pin `#999999` and the
  shared raised corners; the line-edit's and Kvantum item-view's sunken `#999999` shadow is
  unchanged.
- The new reference test re-derives the four colours and four 3x3 corners from
  `aboutsystem_betawiki.png` and asserts both the edges and corners, passing when the image is
  materialized and skipping (not failing) when it is not, through the existing
  `ReferenceScreenshotMixin`/`skip_unless_materialized` path.
- The helper self-tests pin the `shadow` keyword in both the corner tables and
  `assert_face_bevel`, and the reference corner-table override.
- `make check` is green.

### Ground the Kvantum combo box indicator in the reference's double up/down arrow (planned 2026-10-20 by the plan role) — done 2026-10-21

**Goal.** `[ComboBox]` in `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`
inherits `PanelButtonCommand`, so its popup currently draws the shared `arrow` indicator: a single
9x9 down triangle (`arrow-down-*`). The reference's popup button draws a double up/down arrow --
two 7px-wide triangles separated by two face rows -- in a #DDDDDD cell. Ship a dedicated
`comboarrow` indicator for `[ComboBox]` and leave `arrow` (still used by `IndicatorArrow`, the
spin box and the splitter) unchanged.

**Reference grounding.** `macos8.6-screenshots/systeminfo_betawiki.png` (labelled in
`sources.txt` as the 8.6a3c2 beta build, About This Computer), the System Info window's "Show:"
popup. Its 12x12 arrow region `(233,106)..(244,117)` is exactly `#000000` and `#DDDDDD`: 32 black
pixels in eight one-row bands of widths 1/3/5/7 at y107..110 and 7/5/3/1 at y113..116, centred on
x238, with face rows y106, y111..112 and y117. The popup's arrow-cell face is 16x14
(x231..246, y105..118), so a 12x12 element centred in it lands on exactly that region (2px side
and 1px top/bottom face margins). The cell's divider (`x228` `#AAAAAA`), white highlight (`x230`
`#FFFFFF`) and right bevel (`x247` `#AAAAAA`, `x248` `#777777`) are frame art, not indicator art;
this plan does not ship them.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: add five single-element indicator
  groups `comboarrow-normal`, `comboarrow-focused`, `comboarrow-pressed`, `comboarrow-toggled`
  and `comboarrow-disabled` after the last existing `menubaritem` group. Each group holds a full
  12x12 `#DDDDDD` rect (which fixes the element's 12x12 bounds, so Kvantum scales it 1:1 at
  `indicator.size=12`), then eight arrow rects at cell-relative y=1 x=5 w=1, y=2 x=4 w=3, y=3
  x=3 w=5, y=4 x=2 w=7, y=7 x=2 w=7, y=8 x=3 w=5, y=9 x=4 w=3 and y=10 x=5 w=1; the disabled
  group paints the arrow rects `#999999`. Rects, not paths, so `render_slices` can paint and
  compare the element. Place the five groups at translate y positions 22870, 22930, 22990, 23050 and
  23110 and raise the root `height`/`viewBox` from 22920 to 23140. Extend the leading SVG comment
  to name the reference, the 12x12 cell and the frame-art exclusion.
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`: under `[ComboBox]`, add
  `indicator.element=comboarrow` and `indicator.size=12`, with a short comment naming the
  reference popup's double arrow.
- `tests/support/kvantum_config_spec.py`: set
  `CORE_CONTROL_CONFIG["ComboBox"]["indicator.element"]` to `"comboarrow"`; add
  `VALUE_KEYS["ComboBox"] = {"indicator.size": "12"}`.
- `tests/test_kvantum_svg.py`: add
  `"comboarrow": ("normal", "focused", "pressed", "toggled", "disabled")` to
  `INTERIOR_STATES`; add `_COMBOARROW` and `_COMBOARROW_DISABLED` draw lists to
  `INTERIOR_GROUP_SHAPES` for the five state ids; add `"comboarrow"` to the `elements` tuple in
  `test_remaining_interiors_draw_the_pinned_shapes`; update the table comments that enumerate
  single interior/indicator elements.
- `tests/support/kvantum_fixtures.py`: add
  `SYSTEMINFO_REFERENCE = os.path.join(ROOT, "macos8.6-screenshots", "systeminfo_betawiki.png")`
  and `SYSTEMINFO_MAX_ROWS = 118`, commented as the About This Computer screenshot and the
  deepest row the combo arrow samples (y117).
- `tests/test_kvantum_combobox_reference.py` (new): define
  `TestComboBoxReference(ReferenceScreenshotMixin, unittest.TestCase)` with
  `REFERENCE = SYSTEMINFO_REFERENCE`, `MAX_ROWS = SYSTEMINFO_MAX_ROWS`, `COMBO_X = 233`,
  `COMBO_Y = 106`, `COMBO_SIZE = 12` and the black-row table. One test samples all 144 pixels,
  asserts the colour set is exactly `{BLACK, FACE}` and asserts the black pixels are the row
  table, so the reference itself is pinned; another renders the SVG once with
  `render_slices(parse_svg(SVG))`, compares `comboarrow-normal` exactly to the sampled map,
  asserts `comboarrow-focused`, `comboarrow-pressed` and `comboarrow-toggled` equal it, and
  asserts `comboarrow-disabled` equals it with every `#000000` replaced by `GREY`.
- `docs/invariants.md`: add a kvantum row -- "The combo box indicator is the reference's double
  up/down arrow in a 12x12 `#DDDDDD` cell." -- naming
  `tests/test_kvantum_combobox_reference.py::TestComboBoxReference`, with the provenance
  exception that the popup is an 8.6a3c2 beta build and that the cell's divider and right bevel
  are frame art, not indicator art.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`,
`tests/support/kvantum_config_spec.py`, `tests/support/kvantum_fixtures.py`,
`tests/test_kvantum_svg.py`, `tests/test_kvantum_combobox_reference.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/systeminfo_betawiki.png 238 107` prints
  `0,0,0 #000000`; `... 238 111` prints `221,221,221 #DDDDDD`; `... 238 113` prints
  `0,0,0 #000000`; `... 233 106` and `... 244 117` print `221,221,221 #DDDDDD`.
- `make check CHECK_TESTS=test_kvantum_combobox_reference` passes when the Git LFS image is
  materialized and skips (does not fail) when it is not; changing any arrow or gap pixel in the
  12x12 cell makes it fail.
- `make check CHECK_TESTS=test_kvantum_svg` passes: the five `comboarrow-*` ids exist, each
  state's rects match the pinned shape, and the fill set stays the Platinum palette.
- `make check CHECK_TESTS=test_kvantum_config_elements` and `test_kvantum_config` pass:
  `[ComboBox]` resolves to `comboarrow` at size 12, and every config key remains pinned.
- The existing `arrow-*` ids, path `d` values and fills are unchanged; the four direction tests
  and the `IndicatorArrow`, spin box and splitter mappings still pass.
- The new `docs/invariants.md` row resolves through `tests/invariants.py`, and `make check` is
  green.

### Ground the desktop theme push button's raised bevel shadow in the reference's raised buttons (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `theme/desktoptheme/org.macos8.desktop/widgets/button.svg` paints the raised
bevel's shadow `#999999`: the `normal` state's bottom and right bands and its three shadow
corners, and the inverted `pressed` state's top and left bands and corners. The reference
set's lossless raised button bevels -- the Get Info window's two popup buttons in
`macos8.6-screenshots/aboutsystem_betawiki.png` -- use `#AAAAAA`, and the lossy Open dialog's
rounded push buttons (`opendialog_macrumors86.jpg`) show the same lighter shadow. The Kvantum
`button` element was already corrected from `#999999` to `#AAAAAA` against those popup buttons
(`PLANS-DONE.md`, "Ground the Kvantum button bevel's shadow"), so the desktop theme's push
button is now the odd one out. Correct its shadow to `#AAAAAA` and pin it to the reference. The
`#000000` outline, `#FFFFFF` highlight and `#DDDDDD` face already match; the rounded corner
stays, because the reference's push buttons are rounded while its popup buttons are square --
only the shadow colour is grounded.

**Reference.** `macos8.6-screenshots/aboutsystem_betawiki.png` (beta `8.6b2c4`, the same image
the Kvantum button and check-box groundings use). The "表示" popup button spans x=80..249,
y=103..122: `(150,103)=#000000`, `(150,104)=#FFFFFF`, `(150,108)=#DDDDDD`, `(150,121)=#AAAAAA`,
`(150,122)=#000000`; the "ラベル" popup button repeats it at y=275..292 (`(150,275)=#000000`,
`(150,276)=#FFFFFF`, `(150,291)=#AAAAAA`, `(150,292)=#000000`). The Open dialog's rounded push
buttons (`opendialog_macrumors86.jpg`, JPEG, corroboration only) show a ~`#ADADAD` shadow.

**Approach.**
- `theme/desktoptheme/org.macos8.desktop/widgets/button.svg`: change every bevel shadow
  `#999999` to `#AAAAAA` -- `normal-bottom`, `normal-right`, `normal-topright`,
  `normal-bottomleft`, `normal-bottomright`, and the inverted `pressed-top`, `pressed-left`,
  `pressed-topleft`, `pressed-topright`, `pressed-bottomleft`. Leave the `#000000` outline,
  `#FFFFFF` highlight and `#DDDDDD` face; the `focus` state has no shadow.
- `tests/support/platinum_palette.py`: add `BUTTON_SHADOW = "#AAAAAA"`, documented as the
  reference's raised-button shadow, and give `assert_fill_palette` a `shadow=GREY` keyword that
  swaps `GREY` for the caller's shadow in the expected set (the default keeps the current
  behaviour for every other widget test).
- `tests/svg_assertions/faces.py`: give `face_edge_bands(face, bevel)` a `shadow="#999999"`
  keyword and use it in place of the three `#999999` literals (the raised, sunken and
  sunken-outside bands), so the button test can pass `BUTTON_SHADOW` while
  `frame`/`lineedit`/`toolbar`/`scrollbar` keep the default.
- `tests/test_desktoptheme_button.py`: call `assert_fill_palette(self, self.tree,
  shadow=BUTTON_SHADOW)`; replace the `#999999` literals in `test_button_bevel_direction`'s
  `outward` and `corners` tables with `#AAAAAA`; pass `shadow=BUTTON_SHADOW` in
  `test_button_edge_pixels`.
- New `tests/test_desktoptheme_button_reference.py`, modelled on
  `tests/test_kvantum_button_reference.py`: a `TestButtonReference(ReferenceScreenshotMixin,
  unittest.TestCase)` with `REFERENCE`/`REFERENCE_ROWS` from `support.aurorae_fixtures` that
  re-derives the four colours from the popup-button anchors above and asserts the shipped
  `normal` slices paint the raised arrangement with `#AAAAAA` and the `pressed` slices the
  sunken one with the same shadow; skips when the Git LFS image is not materialized.
- `docs/invariants.md`: add a `desktoptheme` row `| widgets/button.svg's raised bevel shadow is
  the reference's #AAAAAA. | tests/test_desktoptheme_button_reference.py::TestButtonReference |
  The reference's raised button bevel is the Get Info popup button (aboutsystem_betawiki.png), a
  beta build; the reference's rounded push buttons are only in the lossy
  opendialog_macrumors86.jpg. |`.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/button.svg`,
`tests/support/platinum_palette.py`, `tests/svg_assertions/faces.py`,
`tests/test_desktoptheme_button.py`, `tests/test_desktoptheme_button_reference.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/aboutsystem_betawiki.png 150 121` prints
  `170,170,170 #AAAAAA` and `... 150 291` likewise; `(150,104)` is `#FFFFFF`, `(150,108)` is
  `#DDDDDD`, and `(150,103)`/`(150,122)` are `#000000`.
- Every `button.svg` `#999999` is now `#AAAAAA`, the file's fill set is exactly
  `{#000000, #FFFFFF, #AAAAAA, #DDDDDD}`, and `test_desktoptheme_button.py` passes.
- `face_edge_bands` with its default still returns the `#999999` shadow, so
  `test_desktoptheme_frame.py`, `test_desktoptheme_lineedit.py` and the
  `test_svg_assertions_faces.py` self-test are unchanged.
- The new reference test re-derives the four colours from `aboutsystem_betawiki.png` and passes
  when the image is materialized, skipping (not failing) when it is not, through the existing
  `ReferenceScreenshotMixin`/`skip_unless_materialized` path.
- The new `docs/invariants.md` row resolves through `tests/invariants.py`.
- `make check` is green.

### Correct the desktop theme tabbar to the reference's selected System Profiler tab (planned 2026-10-19 by the plan role) — done 2026-10-19

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

### Ground the Kvantum tab face in the reference's System Profiler tabs (planned 2026-10-19 by the plan role) — done 2026-10-19

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
- `tests/test_kvantum_svg.py`: add the unselected tab face `#CCCCCC` as a named `TAB_FACE`
  extra in `test_uses_exactly_the_platinum_palette`, so the exact-palette assertion still holds
  (the plan's files-touched list had missed this test).
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
`tests/test_kvantum_svg.py`, `docs/invariants.md`.

### Ground the Kvantum button bevel's shadow in the reference's popup buttons (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** The four `button-*` state groups in
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` paint their bevel shadow `#999999`
(the raised states' bottom/right bands and their three shadow corners, the sunken states'
top/left bands and their three shadow corners). The Get Info window in
`macos8.6-screenshots/aboutsystem_betawiki.png` draws its two popup buttons with a `#AAAAAA`
shadow, and `[ComboBox]` in the `.kvconfig` renders through that same `button` element
(`[ComboBox] inherits=PanelButtonCommand`, whose `frame.element` and `interior.element` are both
`button`), so the screenshot directly grounds the element. Correct the shadow to `#AAAAAA` and
pin it to the reference; the `#000000` outline, `#FFFFFF` highlight and `#DDDDDD` face already
match.

**Reference.** `macos8.6-screenshots/aboutsystem_betawiki.png` (beta `8.6b2c4`, the same image
the Kvantum check box grounding uses). The "表示" popup button spans x=80..249, y=103..122: top
outline (150,103)=`#000000`, top highlight (150,104)=`#FFFFFF`, left outline (80,108)=`#000000`,
left highlight (81,108)=`#FFFFFF`, face (150,108)=`#DDDDDD`, bottom shadow (150,121)=`#AAAAAA`,
bottom outline (150,122)=`#000000`. The "ラベル" popup button repeats it at y=275..292:
(150,275)=`#000000`, (150,276)=`#FFFFFF`, (150,291)=`#AAAAAA`, (150,292)=`#000000`. The
reference shadow is `#AAAAAA`, six levels lighter than the theme's `#999999`.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: in the four `button-*` state groups
  (`normal`, `focused`, `pressed`, `toggled`) change every bevel shadow `#999999` to `#AAAAAA` --
  the raised states' `-bottom`/`-right` bands and their
  `-topright`/`-bottomleft`/`-bottomright` corners, and the sunken states' `-top`/`-left` bands
  and their `-topleft`/`-topright`/`-bottomleft` corners. Leave the
  `#000000` outline, `#FFFFFF` highlight and `#DDDDDD` face. Reword the header comment's bevel
  sentence so it names the reference-grounded button shadow (the popup buttons in
  `aboutsystem_betawiki.png`) rather than stating `#999999` as the shared raised shadow; the other
  raised-frame elements (tab, menu, group, toolbar, ...) keep `#999999`, because the reference
  set's only lossless raised-button bevel is these popup buttons.
- `tests/test_kvantum_bevel_pixels.py`: add `BUTTON_SHADOW = "#AAAAAA"` and
  `SURFACE_SHADOW = "#999999"`; give `_button_edge_maps` a `shadow` parameter and turn the
  `BUTTON_CORNERS` literal into a `_button_corners(shadow)` helper; `TestButtonBevelPixels` passes
  `BUTTON_SHADOW` and `TestSurfaceBevelPixels` passes `SURFACE_SHADOW`, so the button states are
  pinned to `#AAAAAA` while the tab/menu/group/toolbar states keep `#999999`.
- New `tests/test_kvantum_button_reference.py`, modelled on
  `tests/test_kvantum_checkbox_reference.py`: a
  `TestButtonReference(ReferenceScreenshotMixin, unittest.TestCase)` with
  `REFERENCE = aboutsystem_betawiki.png` that derives the four bevel colours from the anchors above
  and asserts the shipped `button-normal` slices paint the raised arrangement with `#AAAAAA` and
  that `button-pressed` paints the sunken arrangement with the same `#AAAAAA` shadow, skipping when
  the Git LFS image is not materialized. `render_slices(parse_svg(SVG))` reads the nine
  `button-normal-*`/`button-pressed-*` slices.
- `tests/test_kvantum_svg.py`: add `BUTTON_SHADOW = "#AAAAAA"` and include it in
  `test_uses_exactly_the_platinum_palette`'s `extra` set, so the palette check accepts the
  button's new fill while still rejecting any other stray fill.
- `docs/invariants.md`: add the kvantum row `| The button bevel is the reference's raised
  popup-button bevel. | tests/test_kvantum_button_reference.py::TestButtonReference | The
  reference's popup button is a beta build (aboutsystem_betawiki.png); it is the set's only
  lossless raised-button bevel. |`.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`tests/test_kvantum_bevel_pixels.py`, `tests/test_kvantum_button_reference.py` (new),
`tests/test_kvantum_svg.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/aboutsystem_betawiki.png 150 121` prints
  `170,170,170 #AAAAAA`, and `(150,291)` likewise; `(150,104)` and `(81,108)` are `#FFFFFF`,
  `(150,108)` is `#DDDDDD`, and `(150,103)`, `(150,122)` and `(80,108)` are `#000000`.
- Every `button-*` raised state's bottom and right bands are `#AAAAAA`, every sunken state's top
  and left bands are `#AAAAAA`, and the four `button-*` state groups' fill set is exactly
  `{#000000, #FFFFFF, #AAAAAA, #DDDDDD}`; `TestButtonBevelPixels` passes.
- `TestSurfaceBevelPixels` still pins the tab/menu/group/toolbar `#999999` shadow, and the line
  edit's and item view's `#999999` sunken-field shadow (the shared `sunken_outside_face_corners`
  table) is unchanged.
- The new reference test re-derives the four colours from `aboutsystem_betawiki.png` and passes
  when the image is materialized, skipping (not failing) when it is not, through the existing
  `ReferenceScreenshotMixin`/`skip_unless_materialized` path.
- `make check` is green.

### Correct the shared sunken-outside field's bottom corners to the reference field's true bottom (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `sunken_outside_face_corners()` in `tests/svg_assertions/faces.py` derives its
bottom-left and bottom-right corners from the internal separator at y=350-351 inside the Setup
Assistant's sunken content field in `firstboot_betawiki.png`, not from the field's true bottom.
Correct the shared table and every artifact that paints from it, then re-anchor the two reference
tests on the field's true bottom.

**Approach.** The field in `firstboot_betawiki.png` runs (28,58)-(431,377): left shadow x=28
`y=58..376`, outline x=29, top shadow y=58, bottom highlight y=377 `x=29..431`, right highlight
x=431 `y=59..377`. Its bottom-left outer pixel (28,377)=#CCCCCC is unpainted (the window face) and
the highlight starts one pixel in at (29,377)=#FFFFFF; its bottom-right corner block is
(430,376)=#000000, (431,376)=#FFFFFF, (430,377)=#FFFFFF, (431,377)=#FFFFFF. The item view's
bottom-left in `setup_emaculation.png` ((22,478)=#CCCCCC, (23,478)=#FFFFFF) shows the same corner;
its bottom-right sits under the scrollbar corner (#CCCCCC), so the corrected shared geometry is
the only grounded arrangement. The field's bottom interior is the #DDDDDD footer, so the bottom
border run checks only the outline and highlight.

**Files touched.**
- `tests/svg_assertions/faces.py`: in `sunken_outside_face_corners`'s `bottomleft` table set
  `(0,2)` to `None` and `(1,2)` to `"#FFFFFF"`; in `bottomright` set `(1,2)` to `"#FFFFFF"`.
- `theme/desktoptheme/org.macos8.desktop/widgets/lineedit.svg`: redraw `base-bottomleft` and
  `base-bottomright` to the corrected 3x3 tables; reword the header comment's bottom-anchor
  sentence.
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: redraw `lineedit-normal-bottomleft`,
  `lineedit-normal-bottomright`, `lineedit-focused-bottomleft`, `lineedit-focused-bottomright` and
  `itemview-normal-bottomright`, `itemview-focused-bottomright` to the corrected 2x2 outer blocks;
  update the header comment's bottom anchors.
- `tests/test_kvantum_lineedit_reference.py`: `FIELD_BOTTOM=377`; bottom run `((100,376),
  "#000000"), ((100,377), "#FFFFFF")`; replace the bottom four `FIELD_CORNER_PIXELS` with the true
  (28,376)/(29,376)/(28,377)/(29,377) and (430,376)/(431,376)/(430,377)/(431,377) pixels.
- `tests/test_desktoptheme_lineedit.py`: the same bottom run and corner pixels; update comments.
- `tests/support/desktoptheme_paths.py`: `FIRSTBOOT_MAX_ROWS = 378`.
- `tests/test_svg_assertions_faces.py`: update the pinned `sunken_outside_face_corners("#DDDDDD")`
  table's `bottomleft`/`bottomright` rows.
- `tests/test_kvantum_itemview_reference.py`: drop the now-redundant `corners["bottomleft"]`
  override; update its comment.
- `tests/test_kvantum_bevel_pixels.py`: `_ITEMVIEW_BOTTOMLEFT` now equals the helper's block;
  remove the override if it is redundant.
- `macos8.6-screenshots/sources.txt`: extend the `firstboot_betawiki.png` note to record the
  field's true bottom and the shared bottom-left corner.
- `docs/invariants.md`: extend the item view row's provenance-exception cell to record that its
  bottom-right corner sits under the scrollbar and follows the line edit's grounded corner.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/firstboot_betawiki.png 28 377` prints #CCCCCC and
  `... 29 377` prints #FFFFFF; `... 30 375` prints #FFFFFF, `... 30 376` #000000, `... 30 377`
  #FFFFFF; `... 430 377` and `... 431 377` print #FFFFFF.
- `python3 tools/sample.py macos8.6-screenshots/setup_emaculation.png 22 478` prints #CCCCCC and
  `... 23 478` prints #FFFFFF.
- `tests/test_kvantum_lineedit_reference.py::TestLineEditReference` and
  `tests/test_desktoptheme_lineedit.py::TestLineEditReference` pass when the Git-LFS reference is
  materialized, and the corrected helper's bottom-left block is `("#999999", "#000000", None,
  "#FFFFFF")`.
- `tests/test_svg_assertions_faces.py::TestSunkenOutsideFaceCorners`,
  `tests/test_desktoptheme_lineedit.py::TestLineEdit` and
  `tests/test_kvantum_bevel_pixels.py::TestLineEditBevelPixels`/`TestItemViewBevelPixels` pass
  against the redrawn art.
- `make check` is green.

### Ground the Kvantum item view's sunken field in the reference Finder content area (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` draws the
`itemview-normal` and `itemview-focused` frames with the #000000 outline on the outer edge and
the bevel inside it (`itemview-normal-top` is #000000 then #999999, `itemview-normal-left` the
same) -- the same inversion the line edit had before its fix. The reference item view puts the
sunken bevel *outside* the outline -- `macos8.6-screenshots/setup_emaculation.png` (retail Mac
OS 8.6 installer CD Finder window, item view): left (22,250)=#999999, (23,250)=#000000,
(24,250)=#FFFFFF; top (200,118)=#999999, (200,119)=#000000, (200,120)=#FFFFFF; right
(452,200)=#000000, (453,200)=#FFFFFF; bottom (100,477)=#000000, (100,478)=#FFFFFF. Redraw the
Kvantum item view's tiles as that bevel-outside ring so a KDE application's list/tree view
matches the reference, exactly as the landed line-edit fix did for text fields.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: for each of the `itemview-normal-*`
  and `itemview-focused-*` frames, rewrite the four edge slices so the outer pixel is the bevel
  (#999999 top/left, #FFFFFF bottom/right) and the inner pixel is the #000000 outline, leaving
  the #FFFFFF centre face unchanged (the same pixels as the landed `lineedit-normal-*`/
  `lineedit-focused-*` art, except the bottom-left corner below). Rewrite each 2x2 corner as the
  outer 2x2 of `sunken_outside_face_corners("#FFFFFF")` in `tests/svg_assertions/faces.py`,
  except the bottom-left: the reference's bottom highlight starts one pixel in from the left
  ((22,478)=#CCCCCC, the window face), so its outer bottom pixel is left unpainted and the
  #FFFFFF highlight sits at the inner bottom pixel. The top-right outer pixel stays unpainted
  (reference (453,118)=#CCCCCC, the window face). Leave `itemview-pressed-*` and
  `itemview-toggled-*` flat #CCCCFF, and add a comment above the two groups naming the
  reference and its sampled pixels.
- Update the file-header comment (the sentence "the line edit is the white sunken field") to
  name the item view as sharing that field.
- `tests/test_kvantum_bevel_pixels.py`: keep `"itemview"`'s flat `pressed`/`toggled` states in
  `SURFACE_STATES` (so the flat #CCCCFF art stays pinned) and add a `TestItemViewBevelPixels`
  case mirroring `TestLineEditBevelPixels` (reusing `LINEEDIT_EDGES`, `_lineedit_edge_map` and
  `_lineedit_corners`, with an item-view bottom-left override) for prefixes `itemview-normal`
  and `itemview-focused`, so a state repeating the old outline-outside art fails there.
- New `tests/test_kvantum_itemview_reference.py`: a `ReferenceScreenshotMixin` case over
  `setup_emaculation.png` (`MAX_ROWS = 479`) that re-derives the field's four border runs, its
  top-left 2x2 corner and its bottom-left 2x2 corner and asserts the rendered Kvantum
  `itemview-normal` tiles paint the same sunken-outside arrangement; skips when the image is
  not materialized. The reference field's top-right and bottom-right corners sit under the
  status header and the scrollbars, so the test derives only the clean left/top/right/bottom
  runs and the two clean corners (the bottom-left's outer bottom pixel is the window face, so
  the shipped tile leaves it unpainted).
- `docs/invariants.md`: add a `kvantum` row `| The item view is the reference's sunken field:
  the bevel outside the #000000 outline. |
  tests/test_kvantum_itemview_reference.py::TestItemViewReference | none |`.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`tests/test_kvantum_bevel_pixels.py`, `tests/test_kvantum_itemview_reference.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- Every `itemview-normal-*` and `itemview-focused-*` edge slice paints the bevel on its outer
  pixel (#999999 top/left, #FFFFFF bottom/right) and the #000000 outline inside it, over the
  unchanged #FFFFFF centre face; the corners wrap that bevel around the outline, except the
  bottom-left, whose outer bottom pixel the reference leaves to the window face (the shipped
  tile leaves it unpainted and paints the #FFFFFF highlight one pixel in).
- `python3 tools/sample.py macos8.6-screenshots/setup_emaculation.png 22 250` prints
  `153,153,153 #999999`, `... 23 250` prints `0,0,0 #000000`, `... 24 250` prints
  `255,255,255 #FFFFFF`; the new test re-derives those pixels and the other three runs and
  passes, skipping when the image is not materialized.
- `TestItemViewBevelPixels` fails against the old outline-outside artwork and passes against the
  new.
- The new `docs/invariants.md` row resolves through `tests/invariants.py`.
- `make check` is green.

### Checker unreadable-input mutations: manufacture a register, asset or reference that cannot be read so the checker's own diagnostic is observable (planned 2026-10-19 by the steward role; from the recurring `no-fake` validation gap in four Fixed entries) — done 2026-10-19

**Goal.** Four Fixed entries share one shape: a record checker reads an input that cannot be read
-- a register path that is a directory, a text asset under `theme/` that is a dangling symlink
resolving inside the root, a register reference containing a NUL byte, or a reference to a test
file that cannot be decoded -- and the read raises a bare `OSError`/`ValueError` that names
neither the checker nor the offending row, aborting the check with an unrelated traceback. Each
was confirmed only by hand-building a shim the suite did not have (its `no-fake` gap).
The per-checker mutation tables in `tests/support/invariants_mutations.py` and
`tests/support/placeholders_mutations.py`, over the shared `tests/support/checker_scratch.py`,
already manufacture the malformed register and theme inputs the shipped data never holds; extend
them with the four unreadable-input shapes so confirming the next bug of this kind reuses the
scratch fixture instead of a one-off.

**From (the `no-fake` Fixed entries).**
- `tests/placeholders.py` lets an unreadable register escape as a bare `OSError`.
- `tests/placeholders.py` lets a dangling symlink inside `theme/` escape as a bare
  `FileNotFoundError`.
- `tests/invariants.py` lets a register reference with a NUL byte escape as an unrelated
  exception.
- `tests/invariants.py` lets a reference to an unreadable test file escape as an unrelated
  exception.

**Approach.**
- `tests/support/checker_scratch.py`: teach `Scratch` to clean up a directory it wrote (its
  `reset` only unlinks files today), then add four `Mutation` entries to the per-checker tables
  (`tests/support/invariants_mutations.py` and `tests/support/placeholders_mutations.py`):
  `unreadable-register` (replace the register path with a directory so `register_entries`'
  `OSError` arm fires; diagnostic `cannot be read`), `dangling-symlink-inside-theme` (a text
  asset under `theme/` symlinked to a missing path inside the root; diagnostic `cannot be read`),
  `reference-with-nul-byte` (`_replace_first_reference` with a `\x00` in the path; diagnostic
  `NUL byte`), and `unreadable-test-file` (point the first row's reference at a scratch file
  written as undecodable bytes; diagnostic `cannot be read as Python`).
- `tests/placeholders.py` and `tests/invariants.py`: add each new name to `REJECTION_SHAPES` in
  the same commit, so `test_checker_mutations.py`'s two set-equality guards keep each checker's
  boundary list and the mutation table in step.

**Implementation note.** `unreadable-test-file` overwrites the scratch copy of the existing
`MUTANT_MODULE` with undecodable bytes (and `Scratch.reset` now restores an overwritten file)
rather than adding a new scratch path, so the stage self-check's added-nonexistent-path guard
keeps seeing a repository path that exists.

**Files touched.** The checker-mutation fixtures (now `tests/support/checker_scratch.py`,
`tests/support/invariants_mutations.py` and `tests/support/placeholders_mutations.py`),
`tests/placeholders.py`, `tests/invariants.py`.

**Acceptance criteria.**
- `tests/test_checker_mutations.py` drives each of the four new mutations, and each makes its
  checker raise the named `AssertionError`; the two unreadable-read mutations fail if the
  checker's `OSError` arm is removed.
- The two `REJECTION_SHAPES` set-equality guards pass with the four new names.
- `make check` is green.

### Ground the Kvantum line edit's sunken bevel in the reference text field (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` draws the
`lineedit-normal` and `lineedit-focused` frames with the #000000 outline on the outer edge and
the bevel inside it (`lineedit-normal-top` is #000000 then #999999, `lineedit-normal-left` the
same). The reference text field puts the sunken bevel *outside* the outline --
`macos8.6-screenshots/firstboot_betawiki.png` (28,95)=#999999, (29,95)=#000000,
(30,95)=#FFFFFF -- the structure `theme/desktoptheme/org.macos8.desktop/widgets/lineedit.svg`
already paints and `tests/test_desktoptheme_lineedit.py` already pins. Redraw the Kvantum line
edit's tiles as that bevel-outside ring so a KDE application's text field matches the reference.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: for each of the `lineedit-normal-*`
  and `lineedit-focused-*` frames, rewrite the four edge slices so the outer pixel is the bevel
  (#999999 top/left, #FFFFFF bottom/right) and the inner pixel is the #000000 outline, leaving
  the #FFFFFF centre face unchanged: the top/left slices read #999999 then #000000 from the
  outer edge inward, and the bottom/right slices read #FFFFFF then #000000 the same way (in
  slice coordinates the bottom/right slices are #000000 then #FFFFFF, their outer edge being
  the last row/column). Rewrite each 2x2 corner as the outer 2x2 of the `sunken-outside`
  corner table in `tests/svg_assertions/faces.py` (`sunken_outside_face_corners("#FFFFFF")`), scaled to the 2px
  border: the #999999/#FFFFFF bevel wraps the #000000 outline, which meets at the inner corner,
  and the top-right outer pixel stays unpainted because the reference field's top shadow stops
  one pixel short of the outer highlight (reference (431,58)=#CCCCCC, the window face). Add a
  comment above the two line-edit groups naming the reference and its sampled pixels; leave the
  file header comment untouched.
- `tests/test_kvantum_bevel_pixels.py`: add a `TestLineEditBevelPixels` case that renders both
  states with `render_slices` and pins every slice and corner pixel, so a state repeating the
  old outline-outside art fails here.
- New `tests/test_kvantum_lineedit_reference.py`: a `ReferenceScreenshotMixin` case over
  `firstboot_betawiki.png` that re-derives the field's left/top/right/bottom border runs and its
  corner pixels (the same coordinates `tests/test_desktoptheme_lineedit.py` samples) and asserts
  the rendered Kvantum `lineedit-normal` tiles paint the same sunken-outside arrangement; skips
  when the image is not materialized.
- `docs/invariants.md`: add a `kvantum` row `| The line edit is the reference's sunken field:
  the bevel outside the #000000 outline. |
  tests/test_kvantum_lineedit_reference.py::TestLineEditReference | none |`.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`tests/test_kvantum_bevel_pixels.py`, `tests/test_kvantum_lineedit_reference.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- Every `lineedit-normal-*` and `lineedit-focused-*` edge slice paints the bevel on its outer
  pixel (#999999 top/left, #FFFFFF bottom/right) and the #000000 outline inside it, over the
  unchanged #FFFFFF centre face; the corners wrap that bevel around the outline.
- `python3 tools/sample.py macos8.6-screenshots/firstboot_betawiki.png 28 95` prints
  `153,153,153 #999999`, `... 29 95` prints `0,0,0 #000000`, `... 30 95` prints
  `255,255,255 #FFFFFF`; the new test re-derives those pixels and passes, skipping when the
  image is not materialized.
- `TestLineEditBevelPixels` fails against the old outline-outside artwork and passes against the
  new.
- The new `docs/invariants.md` row resolves through `tests/invariants.py`.
- `make check` is green.

### Ground the Kvantum check box face in the reference's raised Platinum check box (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` draws each `checkbox-*`
interior as a flat `#FFFFFF` square inside a 1px `#000000` outline (pinned as `_CHECKBOX_FACE`
in `tests/test_kvantum_svg.py`), so a KDE application's check box is a flat white square. The
reference set's check box — the Get Info window's "Locked" / "ロック" check box at
`macos8.6-screenshots/aboutsystem_betawiki.png` x=38..49, y=382..393 (the same face in
`systeminfo_betawiki.png` at the same pixels) — is a raised Platinum square: a 1px `#000000`
outline, a 1px `#FFFFFF` top/left highlight, a `#DDDDDD` face, and a 1px `#888888` bottom/right
shadow. Redraw the four `checkbox-*` faces as that raised square so the Kvantum check box matches
the reference, and pin it against the reference pixels.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: for each of `checkbox-normal`,
  `checkbox-focused`, `checkbox-checked-normal` and `checkbox-checked-focused`, replace the two
  face rects (the 14x14 `#000000` outline and the 12x12 `#FFFFFF` face) with the reference's
  raised structure on the same 14x14 canvas: the 14x14 `#000000` outline, a `#FFFFFF` top row and
  left column, the `#DDDDDD` face, and an `#888888` bottom row and right column, with the
  reference's bottom-left corner left `#DDDDDD`. Keep each checked state's five glyph rects
  unchanged (no reference shows a checked box, so the check stays KDE-required).
- `tests/test_kvantum_svg.py`: update `_CHECKBOX_FACE` to the new rect tuple, and add the
  check-box shadow `#888888` as a named extra in `test_uses_exactly_the_platinum_palette`'s
  `extra` set (the reference's check-box shadow), so the exact-palette assertion still holds.
- New `tests/test_kvantum_checkbox_reference.py`: a `ReferenceScreenshotMixin` case over
  `aboutsystem_betawiki.png` that re-derives the check box at x=38..49, y=382..393 — the outer
  ring `#000000`, the row and column inside it `#FFFFFF`, the interior `#DDDDDD`, and the inner
  bottom row and right column `#888888` — and asserts the shipped `checkbox-normal` interior
  paints those same four colours in a raised arrangement. Skips when the image is not
  materialized.
- `docs/invariants.md`: add a `kvantum` row `| The check box face is the reference's raised
  Platinum square. | tests/test_kvantum_checkbox_reference.py::TestCheckBoxReference | The
  reference's check box is a beta build (`aboutsystem_betawiki.png`, `systeminfo_betawiki.png`);
  no retail screenshot shows a check box. |`.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`tests/test_kvantum_svg.py`, `tests/test_kvantum_checkbox_reference.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- Each `checkbox-*` interior draws the reference's raised face (`#000000` outline, `#FFFFFF`
  top/left highlight, `#DDDDDD` face, `#888888` bottom/right shadow), and each checked state's
  glyph is unchanged.
- `python3 tools/sample.py macos8.6-screenshots/aboutsystem_betawiki.png 38 382` prints
  `0,0,0 #000000`, `... 39 383` prints `255,255,255 #FFFFFF`, `... 40 385` prints
  `221,221,221 #DDDDDD`, and `... 48 385` prints `136,136,136 #888888`; the new test re-derives
  those pixels and passes, skipping when the image is not materialized.
- `test_kvantum_svg`'s `_CHECKBOX_FACE` matches the new art, and
  `test_uses_exactly_the_platinum_palette` passes with the named `#888888` extra.
- The new `docs/invariants.md` row resolves through `tests/invariants.py`.
- `make check` is green.

### Ship the Platinum menu submenu arrow (`go-next-symbolic`) grounded in the open Apple menu (planned 2026-10-19 by the plan role) — done 2026-10-19

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

### Ground the Aurorae inactive frame in the reference's inactive windows (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** The `decoration-inactive` nine-slice and its header comment claim "the reference set has
no inactive window" and therefore paint KDE-required greys: the active tile's
`#FFFFFF`/`#777777` pinstripes and `#CCCCCC` field flattened to `#CCCCCC`, keeping the `#000000`
outlines and the `#999999` shadow. The reference set does show inactive windows:
`macos8.6-screenshots/desktop_fandom.png` (retail 8.6, the image the tabbar and progressbar
already sample) shows four unfocused windows (the "Mac OS 8.6", "Utilities", "Applications" and
"Apple System Profiler" windows), and the lossless beta `macos8.6-screenshots/
systeminfo_betawiki.png` shows a fifth behind the active "System Info" window. Their frame is a
flat `#DDDDDD` field with a 1px `#555555` outline on both the outer and inner edges of the
border (the outer edge and the inner edge that meets the client), with no pinstripes, no
white highlight and no `#999999` shadow (verified with `tools/sample.py`; the scheme's own
`[WM] inactiveBackground=221,221,221` agrees). Correct the art and the provenance, and pin the
inactive frame to the reference pixels.

**Approach.**
- `theme/aurorae/themes/org.macos8.desktop/decoration.svg`: rewrite every `decoration-inactive-*`
  tile to the reference's flat inactive frame — the 1px `#555555` outer and inner outlines
  (the top and bottom rows of `decoration-inactive-top`, the outer and inner columns of the
  side tiles, the outer and inner rows of the bottom tiles, and the corner pixels where they
  meet) and `#DDDDDD` everywhere between; recolor the `#000000` outlines to `#555555` and drop
  the `#999999` shadow and the `#FFFFFF`/`#777777`/`#CCCCCC` bevel fills. Keep the active
  geometry (18x34 canvas, 6px side/bottom border, 22px top border, 6x6 centre). Recompress
  `decoration.svgz` (`gzip -9 -n`) so `test_svgz_is_the_compressed_svg` still passes.
- Reword the `decoration.svg` header comment: name `desktop_fandom.png` (2 image px per logical
  px) as the inactive anchor and `systeminfo_betawiki.png` as lossless corroboration, state the
  flat `#DDDDDD` field with the 1px `#555555` outer and inner outlines, and delete the "the
  reference set has no inactive window" clause.
- `tests/support/aurorae_fixtures.py`: add `INACTIVE_REFERENCE` (`desktop_fandom.png`, with a row
  bound covering y=900), `INACTIVE_FRAME_GREY = "#DDDDDD"` and `INACTIVE_OUTLINE = "#555555"`;
  keep `INACTIVE_GREY = "#CCCCCC"` for the button boxes. Load `INACTIVE_REFERENCE` in
  `ReferenceImageCase.setUpClass` (skip when unmaterialized, like `REFERENCE`) and add an
  `inactive_pixel(x, y)` accessor.
- `tests/test_aurorae_frame.py`: replace `_assert_flattened_inactive_tile` and its callers with
  reference-derived checks; add `TestDecorationSvg.test_inactive_frame_matches_reference`, which
  derives each inactive tile from its active tile (pinned to the reference) with the `#000000`
  outlines recolored `#555555` and every other fill flattened to `#DDDDDD`, so no `#FFFFFF`,
  `#777777`, `#999999` or `#CCCCCC` pixel survives, and cross-checks the field and outline
  against `inactive_pixel(300, 75)`, `(1000, 130)`, `(1500, 80)`, `(300, 880)` (`#DDDDDD`) and
  `(300, 57)`, `(25, 75)` (`#555555`). Reword the module docstring and the inactive tests so they
  name the reference instead of claiming none exists.
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
  `1500 80`, `300 880`) prints `221,221,221 #DDDDDD`; `... 300 57` and `... 25 75` print
  `85,85,85 #555555`.
- `TestDecorationSvg.test_inactive_frame_matches_reference` passes when `desktop_fandom.png` is
  materialized and skips (not fails) when it is not, through the `skip_unless_materialized` path.
- No Aurorae SVG header or Aurorae test docstring still claims the reference set has no inactive
  window.
- `decoration.svgz` decompresses to the edited `decoration.svg`.
- `make check` is green.

### Correct the desktop theme's false "no menu-open / no combo-box" reference claims (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** Three desktop-theme SVG header comments justify a palette-only value by claiming the
reference set shows no such surface, but the set does show it, so the stated reason is false and
the real reason the value has no per-pixel sample is hidden.

- `theme/desktoptheme/org.macos8.desktop/widgets/viewitem.svg` says "the reference set has no
  open-menu screenshot, so the menu-item highlight has no per-pixel menu sample". The set's open
  Apple menu is `macos8.6-screenshots/desktop_archiveorg8.6hd.png` — the image the
  `widgets/background.svg` plan already sampled its grey menu body from. That menu shows no
  highlighted item (a scan of the image finds no `#CCCCFF` pixel, the highlight fill), so the
  conclusion holds but the stated reason is wrong.
- `theme/desktoptheme/org.macos8.desktop/widgets/menubaritem.svg` repeats the claim as "the
  reference set has no menu-open screenshot". The same open Apple menu is a menu-open screenshot;
  its open title is the Apple-logo kicker (a text title is never shown open), so the pressed
  text-title fill has no per-pixel sample for that different reason.
- `theme/desktoptheme/org.macos8.desktop/widgets/arrows.svg` says "no reference screenshot
  shows a combo box or menu button". The set does: the beta `macos8.6-screenshots/
  systeminfo_betawiki.png` Get Info window's "General Information" and "None" popups, and the
  JPEG `macos8.6-screenshots/opendialog_macrumors86.jpg` Open dialog's "ROM-new" popup. Their Mac
  OS indicator is a double (up+down) arrow, not the single `down-arrow` triangle
  `PlasmaComponents.ComboBox` draws, so the triangle is still a KDE-required shape — but the
  comment must give that reason instead of the false one.

Correct all three comments to state what the reference actually shows, and pin the corrected
provenance so the false claim cannot return.

**Approach.**
- `viewitem.svg`: replace the "the reference set has no open-menu screenshot, so the menu-item
  highlight has no per-pixel menu sample" clause with one naming the reference: the reference
  set's open Apple menu (`desktop_archiveorg8.6hd.png`) shows no highlighted item, so the
  menu-item highlight has no per-pixel sample. Keep the `[Colors:Selection]
  BackgroundNormal=204,204,255` token sentence and the `normal`-slices paragraph unchanged.
- `menubaritem.svg`: replace "the reference set has no menu-open screenshot, so the pressed fill
  has no per-pixel menu sample" with: the reference set's open Apple menu
  (`desktop_archiveorg8.6hd.png`) opens the Apple-logo kicker's title, not a text title, so the
  pressed text-title fill has no per-pixel sample. Keep the `[Colors:Selection]` token sentence
  and the side-padding grounding paragraph unchanged.
- `arrows.svg`: replace the "Provenance: no reference screenshot shows a combo box or menu
  button" sentence with one naming the beta Get Info's and the Open dialog's popup buttons and
  stating that their double-arrow indicator is not the single `down-arrow` triangle
  `PlasmaComponents.ComboBox` draws, so the triangle stays a KDE-required shape and the fill
  reuses the grounded Platinum black (`#000000`) `widgets/checkmarks.svg` pins. Keep the
  literal-attribute sentence.
- `tests/test_desktoptheme_provenance.py` (new): a `TestProvenance` case reading each SVG's
  leading XML comment with a small `header_comment(path)` helper (the SVGs open with a single
  `<!-- ... -->` after the XML declaration) and, per `(path, required, forbidden)` case, asserting
  the comment contains the reference filename it must cite and does not contain the false phrase.
  Import the three paths from `support.desktoptheme_paths` (`VIEWITEM_SVG`, `MENUBARITEM_SVG`,
  `ARROWS_SVG`). Cases:
  - `viewitem.svg`: requires `desktop_archiveorg8.6hd.png`; forbids `no open-menu screenshot`.
  - `menubaritem.svg`: requires `desktop_archiveorg8.6hd.png`; forbids `no menu-open screenshot`.
  - `arrows.svg`: requires `systeminfo_betawiki.png`; forbids `no reference screenshot shows a
    combo box`.
- `docs/invariants.md`: add a `desktoptheme` row `| The `viewitem.svg`, `menubaritem.svg` and
  `arrows.svg` provenance comments name the reference screenshot their claim rests on and do not
  claim the set shows no such surface. | tests/test_desktoptheme_provenance.py::TestProvenance |
  none |`.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/viewitem.svg`,
`theme/desktoptheme/org.macos8.desktop/widgets/menubaritem.svg`,
`theme/desktoptheme/org.macos8.desktop/widgets/arrows.svg`,
`tests/test_desktoptheme_provenance.py` (new), `docs/invariants.md`.

**Acceptance criteria.**
- `viewitem.svg`'s and `menubaritem.svg`'s headers name `desktop_archiveorg8.6hd.png` and no
  longer contain "no open-menu screenshot" / "no menu-open screenshot" respectively;
  `arrows.svg`'s header names `systeminfo_betawiki.png` and no longer contains "no reference
  screenshot shows a combo box".
- `tests/test_desktoptheme_provenance.py::TestProvenance` passes, and fails when any of the three
  comments is reverted to its false phrase or loses its reference filename.
- The new `docs/invariants.md` row resolves through `tests/invariants.py` (its named test case
  exists), and no existing widget assertion changes: the three SVGs' parsed elements and fills are
  untouched.
- `make check` is green.

### Correct the `[Colors:Selection]` anchor's provenance: the reference region is the Setup Assistant's Introduction banner, not a list selection (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`
grounds `[Colors:Selection] BackgroundNormal=204,204,255` in `firstboot_betawiki.png`, but its
comment calls the sampled region "the Setup Assistant's list selection ... a full-width
highlighted row". The region is the Setup Assistant window's "Introduction" title banner: a flat
`#CCCCFF` band spanning roughly x=31..428, y=61..85, under the `#000000` rule at y=59 and the
`#FFFFFF` highlight at y=60 (verified with `tools/sample.py`). `tests/support/platinum_palette.py`
compounds the error, calling the selection fill one of the "KDE-required `[Colors:Tooltip]` and
`[Colors:Selection]` roles no screenshot shows" — a claim `test_selection_background` itself
contradicts. Correct both to state what the reference shows, and widen the anchor so it pins the
banner's flat extent rather than a single pixel.

**Approach.**
- `tests/test_colorscheme_reference.py`:
  - Reword the `REFERENCE_FIRSTBOOT` comment: the sampled region is the Setup Assistant's flat
    `#CCCCFF` "Introduction" banner, not a list selection, and note that it is the reference
    set's flat `#CCCCFF` region.
  - In `test_selection_background`, reword the comment and assert the fill is flat across the
    banner by calling
    `assert_anchor_at("Colors:Selection", "BackgroundNormal", ..., path=REFERENCE_FIRSTBOOT)` at
    `(100, 63)`, `(200, 63)`, `(300, 63)` and `(200, 80)` (all inside the band, clear of its
    text), and one call for the same point with key `BackgroundAlternate`, which the scheme sets
    to the same `204,204,255`.
  - Reword the class docstring's "``firstboot_betawiki.png`` for the selection anchor" clause to
    name the Introduction banner.
- `tests/support/platinum_palette.py`: rewrite the module docstring so the selection fill is
  grounded by `test_colorscheme_reference.TestReferenceAnchors.test_selection_background` in the
  Setup Assistant's Introduction banner (`firstboot_betawiki.png`) and only the tooltip face is
  the KDE-required role no screenshot shows; update the `SELECTION` comment to name that
  reference.
- `macos8.6-screenshots/sources.txt`: extend the `firstboot_betawiki.png` entry with a grounding
  note (the Setup Assistant's Introduction banner is the flat `#CCCCFF` band at y=61..85 that
  grounds `[Colors:Selection] BackgroundNormal`), mirroring the `setup_emaculation.png` entry.

**Files touched.** `tests/test_colorscheme_reference.py`, `tests/support/platinum_palette.py`,
`macos8.6-screenshots/sources.txt`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/firstboot_betawiki.png 100 63` (and `300 63`,
  `200 80`) prints `204,204,255 #CCCCFF`, and
  `python3 tools/sample.py macos8.6-screenshots/firstboot_betawiki.png 200 59` prints
  `0,0,0 #000000`.
- `TestReferenceAnchors.test_selection_background` asserts the scheme's `BackgroundNormal` and
  `BackgroundAlternate` at all four banner points and still skips (not fails) when the Git-LFS
  reference is not materialized, through the existing `pixel`/`skip_unless_materialized` path.
- `tests/test_colorscheme_reference.py` and `tests/support/platinum_palette.py` no longer call
  the sampled region a "list selection" or claim `[Colors:Selection]` is a role "no screenshot
  shows".
- `macos8.6-screenshots/sources.txt`'s `firstboot_betawiki.png` entry names the selection anchor
  and `python3 tools/check_references.py` still accepts the record.
- `make check` is green.

### Ground the `[Colors:View] BackgroundAlternate` scroll-bar trough anchor in `setup_emaculation.png` (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** The color scheme's `[Colors:View] BackgroundAlternate=238,238,238` is the flat
`#EEEEEE` trough that `theme/desktoptheme/org.macos8.desktop/widgets/scrollbar.svg`,
`slider.svg` and `switch.svg` paint. It is the trough that `tests/support/platinum_palette.py`
records as "pinned only by the widget tests that draw it", unlike the face, view, chrome and
selection anchors that `tests/test_colorscheme_reference.py::TestReferenceAnchors` re-derives from
a retail screenshot. The retail installer window in `setup_emaculation.png` shows the trough, so
add an anchor there and tie the scroll bar's own slices to the same pixels.

**Approach.**
- `tests/test_colorscheme_reference.py`: add
  `REFERENCE_SCROLLBAR = os.path.join(ROOT, "macos8.6-screenshots", "setup_emaculation.png")`
  and `SCROLLBAR_ANCHOR_ROWS = 471` (the anchor is at y=470, so the bound must cover row 470),
  load it in `TestReferenceAnchors.setUpClass` next to `REFERENCE_DESKTOP` and
  `REFERENCE_FIRSTBOOT`, and add `test_view_background_alternate` calling
  `assert_anchor_at("Colors:View", "BackgroundAlternate", 200, 470, path=REFERENCE_SCROLLBAR)`.
  The pixel is inside the installer CD window's horizontal scroll bar: the 16px band has a
  `#000000` outline at y=462 and y=477 with a flat `#EEEEEE` trough between them, so (200, 470)
  is clear of both outlines and of the arrow boxes.
- `tests/test_desktoptheme_scrollbar.py`: add a `TestScrollbarReference(ReferenceScreenshotMixin)`
  class, following `tests/test_desktoptheme_line.py::TestLineReference`, with
  `REFERENCE = REFERENCE_SCROLLBAR` (import the path from `support.theme_install`/`ROOT` and
  `TROUGH`/`BLACK` from `support.platinum_palette`). Its `test_trough_matches_reference` asserts
  `self.pixel(200, 470)` is `TROUGH`, `self.pixel(200, 462)` and `self.pixel(200, 477)` are
  `BLACK`, and the trough is flat at `(50, 470)`, `(300, 470)` and `(400, 470)`, so the
  `background-vertical`/`background-horizontal` slices' pinned fills are tied to the screenshot
  and not only to `platinum_palette`.
- `tests/support/platinum_palette.py`: reword the module docstring, which says the trough "is
  pinned only by the widget tests that draw it", to name the new anchor and reference test.
- `macos8.6-screenshots/sources.txt`: extend the `setup_emaculation.png` note to record that it
  grounds the `[Colors:View] BackgroundAlternate` trough anchor (the flat scroll-bar band at
  y=462..477).

**Files touched.** `tests/test_colorscheme_reference.py`, `tests/test_desktoptheme_scrollbar.py`,
`tests/support/platinum_palette.py`, `macos8.6-screenshots/sources.txt`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/setup_emaculation.png 200 470` prints
  `238,238,238 #EEEEEE`, and the outlines at `(200, 462)` and `(200, 477)` are `#000000`.
- `TestReferenceAnchors.test_view_background_alternate` passes when the Git-LFS reference is
  materialized and skips (not fails) when it is not, through the existing
  `pixel`/`skip_unless_materialized` path; `SCROLLBAR_ANCHOR_ROWS` covers row 470 so the read
  stays in bounds.
- `TestScrollbarReference.test_trough_matches_reference` passes/skips the same way and pins the
  trough fill and both outlines.
- `tests/support/platinum_palette.py` no longer claims the trough is ungrounded.
- `make check` is green.

### Prove the beta `aboutsystem_betawiki.png` window chrome matches the retail `systemprofiler_betawiki.png` (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `macos8.6-screenshots/sources.txt` labels `aboutsystem_betawiki.png` "Mac OS 8.6b2c4LB
beta", and the README's reference policy says beta builds "must not be used as retail
reference" — yet `tests/test_render_surface.py` (the render fidelity gate) and
`tests/support/aurorae_fixtures.py` (the Aurorae decoration tests) read that file. The retail
`systemprofiler_betawiki.png` shows the same window chrome, and this run verified the title-bar
strip, the left and right frame borders, and the close and collapse boxes are byte-identical
between the two (0 differing pixels over 1760, 1272, 1272, 169 and 169 pixels). Add a test that
pins that equality, so the beta is an evidence-backed proxy instead of an unrecorded policy
exception, and record the exception in the docs.

**Approach.**
- New `tests/test_aurorae_reference_equivalence.py`: a `unittest.TestCase` that loads both PNGs
  with `tools.png.read_png`/`pixel_at` and asserts these five regions are pixel-for-pixel equal,
  skipping when either Git-LFS image is not materialized (use
  `support.reference_image.skip_unless_materialized`, the way `ReferenceImageCase` does):
  - title bar: aboutsystem `(30, 25, 80, 22)` vs profiler `(232, 22, 80, 22)`;
  - left border: `(7, 47, 6, 212)` vs `(209, 44, 6, 212)`;
  - right border: `(354, 47, 6, 212)` vs `(808, 44, 6, 212)`;
  - close box: `(11, 29, 13, 13)` vs `(213, 26, 13, 13)`;
  - collapse box: `(343, 29, 13, 13)` vs `(797, 26, 13, 13)`.
  Each region is a window-relative crop (`aboutsystem`'s window origin is `(7, 25)`, the
  profiler's `(209, 22)`, a `(+202, -3)` shift), so the test also records why those two origins
  differ.
- `docs/invariants.md`: add a row to the aurorae section naming the new test as the one that
  pins the beta reference's chrome against the retail screenshot.
- `macos8.6-screenshots/sources.txt` and the README "Reference screenshots" section: record that
  `aboutsystem_betawiki.png` is a beta used as a window-chrome proxy, backed by this test, and
  that the render gate's bottom-border crop (aboutsystem `(13, 419, 308, 6)`) stays on the beta
  because the System Profiler window's bottom differs (its sunken content field and bottom
  scrollbar) and the set has no other lossless retail window-bottom crop.

**Files touched.** `tests/test_aurorae_reference_equivalence.py` (new), `docs/invariants.md`,
`macos8.6-screenshots/sources.txt`, `README.md`.

**Acceptance criteria.**
- The new test passes with both LFS images materialized and skips cleanly when they are not.
- A one-pixel change in any of the five regions of either image makes the test fail (prove it by
  mutating a copy in the test itself, never the reference file).
- `docs/invariants.md`'s aurorae section names the test, and `tests/test_invariants.py` stays
  green.
- `make check` passes.

### Mac OS 8.6 Platinum text field: draw the sunken bevel outside the black outline in `widgets/lineedit.svg` (planned 2026-10-18 by the plan role) — done 2026-10-19

**Goal.** `theme/desktoptheme/org.macos8.desktop/widgets/lineedit.svg` paints the sunken
white field `PlasmaComponents.TextField`/`TextArea`/`SpinBox` and the editable `ComboBox` draw.
It puts the 1px `#000000` outline on the *outer* edge and the `#999999`/`#FFFFFF` bevel *inside*
it. The retail 8.6 reference draws the opposite: the bevel is *outside* the `#000000` outline,
which sits next to the white face. Correct the artwork so a text field matches the reference,
and ground it in reference pixels (the file cites none today). Independent of every other entry:
one artwork file plus its test and a shared assertion convention.

**Reference.** `macos8.6-screenshots/firstboot_betawiki.png` (retail Mac OS 8.6 Setup
Assistant, 1024x768 lossless PNG; `sources.txt` labels it "Mac OS 8.6"). Its body text field:
left border at (28, 95)=`#999999`, (29, 95)=`#000000`, (30, 95)=`#FFFFFF` (face); right border at
(429, 150)=`#FFFFFF` (face), (430, 150)=`#000000`, (431, 150)=`#FFFFFF`; bottom border at
(100, 349)=`#FFFFFF` (face), (100, 350)=`#000000`, (100, 351)=`#FFFFFF`. So the outer 1px ring is
the bevel (`#999999` top/left, `#FFFFFF` bottom/right), the inner 1px ring is `#000000`, and the
face is `#FFFFFF`. `systeminfo_betawiki.png` (8.6a3c2 alpha) and `aboutsystem_betawiki.png`
(8.6b2c4L8 beta) show the same order but are not retail and must not be cited.

**Approach.**
- `widgets/lineedit.svg`: rewrite the eight `base-*` tiles as the ring-swap of the current
  geometry -- the outer 1px ring becomes the bevel (`#999999` top/left, `#FFFFFF` bottom/right),
  the inner 1px ring becomes `#000000`, the face stays `#FFFFFF`. Edges: `base-top` rows
  `#999999`/`#000000`/`#FFFFFF`; `base-bottom` rows `#FFFFFF` (face)/`#000000`/`#FFFFFF` (outer);
  `base-left` columns `#999999`/`#000000`/`#FFFFFF`; `base-right` columns `#FFFFFF`
  (face)/`#000000`/`#FFFFFF` (outer). Corners (row-major 3x3): `base-topleft`
  `#999999 #999999 #999999 / #999999 #000000 #000000 / #999999 #000000 #FFFFFF`; `base-topright`
  `#999999 #999999 #999999 / #000000 #000000 #FFFFFF / #FFFFFF #000000 #FFFFFF`;
  `base-bottomleft` `#999999 #000000 #FFFFFF / #999999 #000000 #000000 / #999999 #FFFFFF #FFFFFF`;
  `base-bottomright` `#FFFFFF #000000 #FFFFFF / #000000 #000000 #FFFFFF / #FFFFFF #FFFFFF #FFFFFF`.
  Keep the 12x12 canvas, the 3px border around the 6px centre, and every hint id.
- Rewrite the header: the sunken bevel sits outside the `#000000` outline, sampled from
  `firstboot_betawiki.png` at the pixels above; drop "the frame's sunken bevel inside it".
- `tests/svg_assertions/faces.py`: add a `"sunken-outside"` bevel to `_require_known_bevel`, to
  `face_edge_bands` (`("#999999", "#000000", face)` outward, `(face, "#000000", "#FFFFFF")`
  mirrored) and to `face_corners` via a new `sunken_outside_face_corners(face)` table holding the
  four corners above. Leave the existing `"sunken"` convention for `frame.svg`.
- `tests/test_desktoptheme_lineedit.py`: switch `test_lineedit_edge_bevels_are_sunken` and
  `test_lineedit_corner_bevels_turn_the_corner` to `"sunken-outside"`; add
  `TestLineEditReference(ReferenceScreenshotMixin, unittest.TestCase)` with `REFERENCE` =
  `firstboot_betawiki.png`, `MAX_ROWS = 352`, asserting `hex_colour(self.pixel(x, y))` equals
  `#999999`/`#000000`/`#FFFFFF` for the three border runs above.
- `tests/test_svg_assertions_faces.py`: add the new convention's edge and corner expectations
  beside the existing sunken ones.
- `docs/invariants.md`: the `widgets/lineedit.svg` row's guarantee and its `none` provenance
  exception are unchanged.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/lineedit.svg`,
`tests/test_desktoptheme_lineedit.py`, `tests/svg_assertions/faces.py`,
`tests/svg_assertions/__init__.py` (re-export the new corner table),
`tests/svg_assertions/pixels.py` (docstring only: `assert_face_bevel`'s bevel vocabulary), and
`tests/test_svg_assertions_faces.py`.

**Acceptance criteria.**
- The `base-*` tiles' outer ring is `#999999` (top/left) / `#FFFFFF` (bottom/right) and the inner
  ring `#000000`, with the `#FFFFFF` face; the parsed `fill` set is still
  {`#FFFFFF`, `#999999`, `#000000`}.
- A reference test re-derives the field's left, right and bottom border runs from
  `firstboot_betawiki.png` and skips when the Git LFS image is not materialized.
- The header names `firstboot_betawiki.png` and the sampled pixels and no longer says the bevel is
  inside the outline.
- `frame.svg`'s sunken test and artwork are unchanged.
- `make check` is green.

### Mac OS 8.6 Platinum dialog body: ground `dialogs/background.svg`'s face in the lossless window body (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `theme/desktoptheme/org.macos8.desktop/dialogs/background.svg` paints the raised
Platinum body that a `PlasmaCore.Dialog` and a `PlasmaCore.AppletPopup` resolve to (the applet and
clock popups). Its header comment says the reference set shows the same grey window bodies but
they are dithered 8-bit captures, so "no single pixel is screenshot-anchored: the values are
palette-derived and recorded as such". Two retail 8.6 references do show an undithered `#DDDDDD`
window body, so the face can be pinned to a pixel and the palette-derived claim dropped.
Independent of every other entry: one reference test class plus one comment rewrite, touching no
artwork.

**Reference.** `macos8.6-screenshots/desktop_archiveorg8.6hd.png` (800x600, lossless PNG): the
About This Computer window body below its title bar, (583..586, 95..100) a solid 4x6 `#DDDDDD`
block ((584, 97) is `#DDDDDD`). Cross-check `macos8.6-screenshots/desktop_fandom.png` (2x,
WebP re-encoded but flat faces exact): the same window body at (1750..1757, 1100..1105) is a solid
8x6 `#DDDDDD` block and (1792, 1126) is `#DDDDDD`. `about_betawiki.png` and
`setup_emaculation.png` are dithered and must not be sampled. `test_colorscheme_reference`
already anchors `[Colors:Window] BackgroundNormal` at (400, 5) of `desktop_archiveorg8.6hd.png`
-- that pixel is the menu bar; this plan anchors the *window body* at a second location, which is
the pixel the header comment says does not exist.

**Approach.**
- `tests/test_desktoptheme_dialog.py`: add `import os`, `from support.platinum_palette import FACE,
  hex_colour`, `from support.reference_image import ReferenceScreenshotMixin` and
  `from support.repo_root import ROOT` (the import pattern `tests/test_desktoptheme_tabbar.py`
  uses); add `TestDialogBackgroundReference(ReferenceScreenshotMixin, unittest.TestCase)` with
  `REFERENCE = os.path.join(ROOT, "macos8.6-screenshots", "desktop_archiveorg8.6hd.png")` and
  `MAX_ROWS = 101` (the deepest sampled row is 100), asserting
  `hex_colour(self.pixel(x, y)) == FACE` for the 4x6 block. The mixin skips the class when the Git
  LFS image is not materialized. Leave `TestDialogBackground(RaisedFaceCase, unittest.TestCase)`
  unchanged.
- `theme/desktoptheme/org.macos8.desktop/dialogs/background.svg`: rewrite the provenance
  paragraph -- the `#DDDDDD` face is the window body sampled from `desktop_archiveorg8.6hd.png` at
  (584, 97) and cross-checked at (1792, 1126) of `desktop_fandom.png`; the 1px `#000000` outline
  and the `#FFFFFF`/`#999999` bevel are the shared raised-face rule (the reference window body
  itself is flat, so no window-body pixel grounds them); delete "no single pixel is
  screenshot-anchored: the values are palette-derived and recorded as such".
- `docs/invariants.md`: the `dialogs/background.svg` row's guarantee and its `none` provenance
  exception are unchanged, now that the face is reference-sampled.

**Files touched.** `tests/test_desktoptheme_dialog.py`,
`theme/desktoptheme/org.macos8.desktop/dialogs/background.svg`.

**Acceptance criteria.**
- `TestDialogBackgroundReference` re-derives `#DDDDDD` from `desktop_archiveorg8.6hd.png`'s window
  body and skips when the Git LFS image is not materialized.
- `dialogs/background.svg`'s parsed `fill` set is unchanged (the Platinum four `#DDDDDD`,
  `#000000`, `#FFFFFF`, `#999999`; the hints are painted with `style` and so are not in the parsed
  `fill` set), so `RaisedFaceCase`'s `test_hint_geometry`, `test_frame_bevel` and `test_colours`
  still pass.
- The header comment names `desktop_archiveorg8.6hd.png` (and the `desktop_fandom.png`
  cross-check) with the sampled pixels and no longer calls the face palette-derived or unanchored.
- `make check` is green.

### Mac OS 8.6 Platinum progress bar: paint the reference's vertical gradient in `bar_meter_horizontal.svg` (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `theme/desktoptheme/org.macos8.desktop/widgets/bar_meter_horizontal.svg` paints its
`bar-active` fill as a flat `#9B9BEA` face with a `#9A9A9A`/`#7878D1` bevel, sampled from the
low-resolution boot thumbnail `boot2_betawiki.png`. Mac OS 8.6's progress-bar fill is a vertical
gradient — dark at the top and bottom, `#CBCCFF` at the centre — and the lossless 2x reference
`macos8.6-screenshots/desktop_fandom.png` resolves all ten rows of it. Paint that gradient so the
Plasma progress bar matches the reference instead of a flat fill.

**Reference.** `desktop_fandom.png` (2 image px per logical px), the "Mac OS 30.4 MB" memory meter
of the About This Computer window. The fill spans x=1458..1817, y=1230..1249. Its interior column
x=1600 has, at image rows 1230, 1232, 1234, 1236, 1238, 1240, 1242, 1244, 1246, 1248:
`#515372`, `#666799`, `#8484BB`, `#B0B0EB`, `#CBCCFF`, `#B2B2E8`, `#8586BC`, `#66679B`, `#50527F`,
`#24244D`. The fill's 1px left edge column is `#68688D` ((1458, 1238)) and its 1px right edge
column `#50527F` ((1816, 1238)). The boot2 fill rows at x=102, y=99..102 (`#7D7D9A`, `#9B9BEA`,
`#7878D1`, `#83839D`) are the same gradient downscaled, so the two references agree.

**Approach.**
- `widgets/bar_meter_horizontal.svg`: leave `bar-inactive` (the track) unchanged. Replace the
  `bar-active` flat face and its `#9A9A9A`/`#7878D1` bevel with the ten sampled rows: in the
  `bar-active-top` (rows 0-2), `bar-active-center` (rows 3-6) and `bar-active-bottom` (rows 7-9)
  tiles one 4x1 rect per row carrying that row's colour, and in each of the four corner tiles and
  the `bar-active-left`/`bar-active-right` tiles the same per-row rects (3px wide) plus one 1x3 or
  1x4 rect on the outer column carrying `#68688D` (left) or `#50527F` (right). Keep the 3px border
  around a 4px centre tile, the 10x10 canvas and the `hint-bar-size` 10x10 hint.
- Rewrite the header comment's fill paragraph: the fill is the reference's vertical gradient
  sampled from `desktop_fandom.png` at the ten pixels above, with the two edge columns sampled at
  (1458, 1238) and (1816, 1238); the boot2 pixels are the downscaled evidence. Record the
  deviations: the reference's 1px `#000000` outline and its ~12px total height are not drawn (the
  bar keeps the 10px canvas), and the edge columns are painted flat rather than row by row.
- `tests/test_desktoptheme_progressbar.py`: replace `FILL_FACE`/`FILL_LIGHT` with a ten-colour
  `FILL_ROWS` table and the two edge constants; `_assert_bar_pixels` builds the top/centre/bottom
  bands and the corner expectations from the table; `test_progressbar_colours` expects the parsed
  fill set of the track's three colours plus the eleven distinct fill colours. Keep the existing
  `TestProgressBarReference` (the boot2 track) for the three track colours and drop its two fill
  pixels; add a second reference class whose `REFERENCE` is `desktop_fandom.png`,
  `MAX_ROWS = 1250`, sampling the ten interior rows and the two edge columns and comparing each to
  the artwork's own parsed fill.
- `README.md`: the `widgets/bar_meter_horizontal.svg` sentence says a lavender-to-white vertical
  gradient fill instead of "a lavender fill".
- `docs/invariants.md`: the `widgets/bar_meter_horizontal.svg` guarantee ("draws the Platinum
  progress bar") is unchanged; no provenance exception is needed because every fill colour is
  reference-sampled.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/bar_meter_horizontal.svg`,
`tests/test_desktoptheme_progressbar.py`, `README.md`.

**Acceptance criteria.**
- The `bar-active` fill's ten rows are exactly the ten sampled `desktop_fandom.png` colours and the
  left/right edge columns are `#68688D`/`#50527F`, asserted slice by slice.
- A reference test re-derives all ten row colours and the two edge colours from
  `desktop_fandom.png` and skips when the Git LFS image is not materialized.
- `bar-inactive`'s track pixels and the 10x10 nine-slice contract (`hint-tile-center`,
  `hint-bar-size`) are unchanged.
- The header comment names `desktop_fandom.png` and the sampled pixels and no longer calls the
  fill a flat `#9B9BEA` face.
- `make check` is green.

### Mac OS 8.6 Platinum tab face: ground `widgets/tabbar.svg` in the System Profiler tabs (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `theme/desktoptheme/org.macos8.desktop/widgets/tabbar.svg` paints every tab face
`#DDDDDD`, the same grey as the menu bar and the dialog body, so a Plasma tab (`TabBar`,
`TabButton`, the kickoff footer, the system-tray current-item and panel expanded applets) reads
as a bare outline on an identical background. The high-resolution lossless reference
`macos8.6-screenshots/desktop_fandom.png` (English retail 8.6, the "Apple System Profiler"
window) shows the Platinum tab face is one grey darker, `#CCCCCC`, with a `#DDDDDD` highlight
inside the `#000000` outline rather than the `#FFFFFF` the artwork paints. The SVG's provenance
comment claims "No screenshot reference exists for tabs", which this reference contradicts.

**Grounding.** In `desktop_fandom.png` the four System Profiler tabs run y=124..157 (a 2x
upscale of a 1280x721 screen, so 2 image pixels per logical pixel). Each tab's interior is
uniformly `#CCCCCC`: the 12x5 rectangles x=2056..2068 y=149..154 (inside "Applications"),
x=2200..2212 y=149..154 ("System Folders") and x=1920..1932 y=149..154 ("Extensions") are each
60/60 `#CCCCCC` (`tools/sample.py`). The 1px band just inside the top black outline is
`#DDDDDD` (rows 128..129 at x=2064), the outline `#000000` (rows 124..125), the tab-bar
background between tabs `#DDDDDD` (221,221,221). Only the solid face, highlight and outline
colours are taken from the reference; the 2x scale leaves the exact 1px bevel placement
unresolved, so the bevel keeps its current black/highlight/face geometry.

**Approach.**
- `theme/desktoptheme/org.macos8.desktop/widgets/tabbar.svg`: in all four `*-active-tab`
  prefixes change the face fill `#DDDDDD` to `#CCCCCC` and the raised-bevel highlight
  `#FFFFFF` to `#DDDDDD`; keep the `#000000` outline, the `#999999` shadow and the face-only
  open edge. Update the header comment to name `desktop_fandom.png` and the sampled rectangles
  and to drop the "No screenshot reference exists for tabs" claim.
- `tests/test_desktoptheme_tabbar.py`: set `FACE = "#CCCCCC"`, add `HIGHLIGHT = "#DDDDDD"`,
  and build `TOP_LEFT_BAND`/`BOTTOM_RIGHT_BAND` and the two fully-raised corners in
  `tab_corners` from `HIGHLIGHT`/`FACE` (the shared `svg_assertions.face_corners` table is
  hard-coded for the `#DDDDDD`/`#FFFFFF` button face, so the tab gets its own raised corner
  table, as the file's `band_rows`/`band_columns` helpers already do for the mixed corners).
  Replace `test_tabbar_colours`'s `assert_fill_palette(self, self.tree)` with an explicit
  `attribute_values(self.tree, "fill") == {"#000000", "#CCCCCC", "#DDDDDD", "#999999"}`,
  and update `test_tabbar_palette`'s expected raw strings to `#CCCCCC`, `#DDDDDD`, `#999999`,
  `#000000`. Add `TestTabBarReference(ReferenceScreenshotMixin, unittest.TestCase)` with
  `REFERENCE` = `desktop_fandom.png` and `MAX_ROWS = 160`, asserting `hex_colour(self.pixel(x, y))`
  is `FACE` for each of the three rectangles above.
- `tests/support/reference_image.py`: give `ReferenceScreenshotMixin` a `MAX_ROWS = None` class
  attribute and pass `max_rows=cls.MAX_ROWS` to `read_reference` in `setUpClass`, so the
  2560x1442 reference decodes only its first 160 rows (0.4s) instead of all of it (3.4s).
- `docs/invariants.md`: the desktoptheme row already names
  `tests/test_desktoptheme_tabbar.py::TestTabBar`; its guarantee ("draws the Platinum tab bar")
  is unchanged.

**Acceptance criteria.**
- Every `*-active-tab` centre and the face part of every slice is `#CCCCCC`, and every
  raised-bevel highlight is `#DDDDDD`; `test_tabbar_centres_are_the_face`,
  `test_tabbar_closed_edges_are_raised` and `test_tabbar_corners` pass.
- The new reference test re-derives `#CCCCCC` from the three `desktop_fandom.png` rectangles and
  passes; a face painted `#DDDDDD` fails it. The test skips, not fails, when the reference is
  not materialized (`skip_unless_materialized`).
- `tabbar.svg`'s comment no longer claims no screenshot reference exists and names the
  reference and the rectangles.
- `make check` exits 0.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/tabbar.svg`,
`tests/test_desktoptheme_tabbar.py`, `tests/support/reference_image.py`.

**Recorded deviation.** The reference tab is a trapezoid whose sides slant outward over the
full tab height; a KSvg nine-slice draws a fixed-corner rectangle, so the shape stays
rectangular. The Kvantum `tab` element (`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`)
keeps its own `#DDDDDD`/`#FFFFFF` raised face: it is a separate Qt-widget surface, not part of
this desktop-theme change.

### Mac OS 8.6 Platinum translucent applet background: ship `widgets/translucentbackground.svg` (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `BasicAppletContainer.qml` — the Plasma applet container the desktop containment uses for
applets placed on the desktop — picks its background from the applet's
`effectiveBackgroundHints`: the `TranslucentBackground` bit resolves to
`imagePath: "widgets/translucentbackground"`. The desktop theme ships no such file, so KSvg falls
back to the default theme's Breeze `translucentbackground.svgz`, a rounded translucent rectangle
that clashes with Platinum. Ship the Platinum body so those applet containers are Platinum too.

**Grounding.** `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/private/containmentlayoutmanager/BasicAppletContainer.qml`
chooses the path in `background.imagePath`: `effectiveBackgroundHints & TranslucentBackground` →
`widgets/translucentbackground`, else `& StandardBackground` → `widgets/background` (already
shipped), else `""`. The same item sets `prefix: blurEnabled ? "blurred" : ""`; `blurEnabled`
requires the `StandardBackground` bit, so a translucent-hint container reads the **unprefixed**
elements. The installed applets that set the bit are those with `PlasmaCore.Types.DefaultBackground`
(`= StandardBackground | TranslucentBackground`) — `org.kde.plasma.weather`, `org.kde.plasma.comic`
and `org.kde.plasma.systemmonitor` each set `Plasmoid.backgroundHints: PlasmaCore.Types.DefaultBackground
| PlasmaCore.Types.ConfigurableBackground`, and `BasicAppletContainer` tests `TranslucentBackground`
first, so they take the translucent path. Mac OS 8.6 has no translucent applet surface: no reference
screenshot shows one and every Platinum body is opaque, so the KDE-required translucent-hint surface
takes the same opaque Platinum body as the standard hint. No new palette value: the file is a
byte-identical copy of `widgets/background.svg` (the Platinum body the standard hint already draws),
exactly as `solid/widgets/tooltip.svg` copies `widgets/tooltip.svg`.

**Approach.**
- Add `theme/desktoptheme/org.macos8.desktop/widgets/translucentbackground.svg`, byte-identical to
`theme/desktoptheme/org.macos8.desktop/widgets/background.svg` (no header change, so the copy test
compares bytes).
- `tests/support/desktoptheme_paths.py`: add `TRANSLUCENT_BACKGROUND_SVG = os.path.join(PACKAGE,
"widgets", "translucentbackground.svg")` beside `BACKGROUND_SVG`.
- `tests/test_desktoptheme.py`: import `TRANSLUCENT_BACKGROUND_SVG`, add
`("translucentbackground.svg", TRANSLUCENT_BACKGROUND_SVG, 16, 16)` to `SVG_CANVASES` (so the
registry, canvas, id and self-containment tests cover it) and
`os.path.join("widgets", "translucentbackground.svg")` to `TestInstall.INSTALLED_FILES`.
- `tests/test_desktoptheme_background.py`: import `TRANSLUCENT_BACKGROUND_SVG` and add
`test_translucent_copy_is_identical` to `TestBackground`, opening `BACKGROUND_SVG` and
`TRANSLUCENT_BACKGROUND_SVG` in binary and asserting equal bytes (mirroring
`TestTooltip::test_solid_copy_is_identical`).
- `docs/invariants.md`: extend the desktoptheme `widgets/background.svg` row's guarantee to "…and
its `widgets/translucentbackground.svg` copy is byte-identical." The row already names
`TestBackground`, which holds the new test.
- `README.md`: in the `widgets/background.svg` sentence, add that a byte-identical copy ships at
`widgets/translucentbackground.svg`, where `BasicAppletContainer.qml` looks for a translucent-hint
applet container's background.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/translucentbackground.svg`
(new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`,
`tests/test_desktoptheme_background.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `widgets/translucentbackground.svg` is byte-identical to `widgets/background.svg`, asserted by
`TestBackground::test_translucent_copy_is_identical`.
- `test_registry_covers_every_shipped_svg` passes with the new file in `SVG_CANVASES`, and
`test_root_canvas_matches_the_artwork_layout`, `test_every_svg_declares_unique_ids` and
`test_every_svg_is_self_contained` cover it (its 16x16 canvas, unique ids, no style/script or
external reference).
- `TestInstall` still passes with the new file listed in `INSTALLED_FILES`.
- `make check` exits 0, including `tests/test_readme_theme_files.py` (the README prose names the
file) and `tests/test_invariants.py`.
- Removing `widgets/translucentbackground.svg` makes `test_translucent_copy_is_identical` fail (the
open raises) and `test_registry_covers_every_shipped_svg` fail (the shipped set no longer equals
the registry).

### Mac OS 8.6 grey menu body: ground `widgets/background.svg` in the open Apple menu (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `theme/desktoptheme/org.macos8.desktop/widgets/background.svg` paints the body of every
`PlasmaComponents.Menu` (context menus and combo-box dropdowns), `Drawer`, `Popup` and planar
applet container as a flat `#FFFFFF` face, and its comment justifies that with
`[Colors:View] BackgroundNormal`. But the open Apple menu in the retail screenshot
`macos8.6-screenshots/desktop_archiveorg8.6hd.png` — the same image
`tests/test_colorscheme_reference.py::TestReferenceAnchors` samples the menu-bar face from — has a
flat `#DDDDDD` body, the Platinum face, not white. Ship the reference's grey menu body and pin it
to the reference pixels.

**Reference.** The Apple menu is open in `desktop_archiveorg8.6hd.png`, dropping from the top-left
(its body spans roughly x=6..160, y=16..355). The menu's empty right margin, clear of item text and
icons, is flat `#DDDDDD`: (150, 60) = (221, 221, 221) and (150, 200) = (221, 221, 221). The Finder
window's content in the same image is white at (470, 300) — already the `[Colors:View]` anchor —
so the menu body is a distinct grey, not the View background. (The image is stored with Git LFS,
so a clone without it must skip this test, as `test_colorscheme_reference` does.)

**Approach.**
- `widgets/background.svg`: change the face — the centre tile and the interiors of the four edge
tiles — from `#FFFFFF` to `#DDDDDD`, keeping the 1px `#000000` outline and the 3px/10px nine-slice
contract. Rewrite the header comment's face paragraph: the body is the Platinum grey `#DDDDDD`
sampled from the open Apple menu in `desktop_archiveorg8.6hd.png`, not `[Colors:View]`; drop the
"flat white" wording.
- `tests/test_desktoptheme_background.py`: `test_background_pixels` passes `FACE` instead of
`WHITE` to `assert_face_bevel`; `test_background_colours` expects `{BLACK, FACE}`; import `FACE`
from `support.platinum_palette` (it is already `#DDDDDD`). Add a reference case, mirroring the
`ReferenceScreenshotMixin` use in `tests/test_desktoptheme_panel.py` and
`tests/test_desktoptheme_menubaritem.py`, whose `REFERENCE` is
`macos8.6-screenshots/desktop_archiveorg8.6hd.png` and which compares `pixel(150, 60)` and
`pixel(150, 200)` to the artwork's own rendered face, skipping when the LFS image is not
materialized.
- `README.md`: the `widgets/background.svg` sentence at the desktop-theme paragraph says the
Platinum grey menu body instead of "the flat white Platinum body".
- `docs/invariants.md`: the desktoptheme `background.svg` row's guarantee ("draws the Platinum
menu body") still holds; no provenance exception is needed now that the face is reference-sampled.

**Acceptance criteria.**
- `background.svg`'s parsed fill set is exactly `{#000000, #DDDDDD}`, its 10x10 centre and four
edge tiles are `#DDDDDD`, and its outline is 1px `#000000` with no bevel.
- The new reference test compares the artwork's own rendered face to the two `#DDDDDD` pixels
from `desktop_archiveorg8.6hd.png` and skips when the image is missing, exactly as the other
reference-screenshot cases do.
- `background.svg`'s comment names the reference and the sampled pixels and no longer derives the
face from `[Colors:View]`.
- README.md no longer calls the menu body white.
- `make check` is green.

### Fidelity gate for the rendered window's title-bar boxes (close, zoom, collapse) (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** The rendered-window fidelity gate byte-compares the title-bar's middle strip and the
side and bottom borders, but not the three Platinum title-bar boxes, so a regression in how
Aurorae places or sizes them renders unnoticed. Extend `tests/test_render_surface.py::TestRender`
to byte-compare the close, zoom and collapse box regions of the render against the reference
screenshots.

**Grounding (verified 2026-10-18 with `tools/render_surface.py --settle 3` on this tree and
`tools/png`).** The 320x240 render puts the window at the capture's origin, and each box region is
byte-identical to the reference (0 differing pixels):
- close box: render `(4,4,13,13)` vs `aboutsystem_betawiki.png` `(11,29,13,13)`;
- collapse box: render `(303,4,13,13)` vs `aboutsystem_betawiki.png` `(343,29,13,13)`;
- zoom box: render `(282,4,21,13)` vs `systemprofiler_betawiki.png` `(776,26,21,13)`.
The close and collapse boxes use `aboutsystem_betawiki.png` (its collapse box at x=343); the zoom
box uses `systemprofiler_betawiki.png`, the only reference whose window shows a zoom box
(`aboutsystem`'s window cannot be zoomed, as `tests/support/aurorae_fixtures.py` records), with
`ZOOM_BOX_X = 5` matching the 21px gap-plus-box canvas. The title-bar strip gate deliberately
starts at x=30 to clear the close box, so these three regions are currently ungated at render
time.

**Approach.**
- `tests/test_render_surface.py`: beside the existing border crops, add
  `PROFILER_REFERENCE = str(repo_root.ROOT / "macos8.6-screenshots" / "systemprofiler_betawiki.png")`
  and the six crop tuples `CLOSE_CANDIDATE`/`CLOSE_REFERENCE`,
  `COLLAPSE_CANDIDATE`/`COLLAPSE_REFERENCE`, `ZOOM_CANDIDATE`/`ZOOM_REFERENCE` with the values
  above.
- Generalize `TestRender.assert_strip_pixels_match` to take a `reference_path=REFERENCE`
  argument and load that image with `support.reference_image.read_reference` +
  `skip_unless_materialized` (so the zoom test skips when the profiler LFS image is absent), then
  add `test_title_bar_boxes_match_the_reference` iterating the three
  `(candidate_crop, reference_crop, reference_path)` triples. It reuses the render `setUpClass`
  already makes, so no second render runs.
- `docs/invariants.md`: add a `tooling` row `| The rendered window's title-bar boxes are
  byte-identical to the same regions of the reference screenshots. |
  tests/test_render_surface.py::TestRender::test_title_bar_boxes_match_the_reference | none |`.
- `README.md`: in the Fidelity checking paragraph, name the box regions beside the title-bar and
  border strips.

**Files touched.** `tests/test_render_surface.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `TestRender.test_title_bar_boxes_match_the_reference` passes where the render tools and both
  references are materialized, and skips when either reference is an unmaterialized LFS pointer.
- Each region is pinned to zero differing pixels: shifting any crop by one pixel, or changing the
  box art or the Aurorae box geometry in `org.macos8.desktoprc`, makes the test fail.
- `docs/invariants.md` resolves the new `tooling` row, and `make check` is green.

### Mac OS 8.6 opaque menu bar: ship the `solid/widgets/panel-background.svg` copy (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `Panel.qml` draws an opaque panel from `solid/widgets/panel-background`, but the
desktop theme ships only `widgets/panel-background.svg`, so the menu bar loses its Platinum bevel
whenever the panel is opaque. Ship the solid copy so the opaque menu bar is Platinum too.

**Grounding.** `/usr/share/plasma/shells/org.kde.plasma.desktop/contents/views/Panel.qml` gives
its two opaque items (`opaqueItem`, `floatingOpaqueItem`) `imagePath:
"solid/widgets/panel-background"`, while the two translucent items use
`widgets/panel-background`. Plasma 6's default panel opacity mode is Adaptive
(`PanelConfiguration.qml`'s opacity combo defaults to index 0), and in Adaptive mode a window
touching the panel (`screenCovered`) drives `panelOpacity` to 1, which hides the translucent item
and shows the opaque one; choosing the Opaque mode does the same always. KSvg does not map
`solid/widgets/panel-background` onto `widgets/panel-background` — the same behaviour
`tests/test_desktoptheme_tooltip.py::TestTooltip::test_solid_copy_is_identical` records for
`PlasmaComponents.ToolTip`'s hardcoded `solid/widgets/tooltip` — so today the opaque menu bar
resolves to the default theme's Breeze `solid/widgets/panel-background.svgz` (the default theme
ships a solid copy; ours ships only `solid/widgets/tooltip.svg`). `widgets/panel-background.svg`
is already fully opaque (its fills are the solid `#FFFFFF`/`#DDDDDD`/`#999999`/`#000000` with no
alpha), so a byte-identical copy is the correct solid variant. Out of scope: a
`solid/widgets/background.svg` (the default theme ships one, but no installed QML requests it —
`DialogBackground.qml` hardcodes `widgets/background` and `libPlasmaQuick` carries no `solid/`
path), so it is not shipped here.

**Approach.**
- Add `theme/desktoptheme/org.macos8.desktop/solid/widgets/panel-background.svg`, byte-identical
to `widgets/panel-background.svg` (no header change, so the copy test compares bytes), matching
the existing `solid/widgets/tooltip.svg`.
- `tests/support/desktoptheme_paths.py`: add `SOLID_PANEL_SVG = os.path.join(PACKAGE, "solid",
"widgets", "panel-background.svg")` beside `SOLID_TOOLTIP_SVG`.
- `tests/test_desktoptheme.py`: import `SOLID_PANEL_SVG`, add `("solid/widgets/panel-background.svg",
SOLID_PANEL_SVG, 12, 22)` to `SVG_CANVASES` (so the registry, canvas, id and self-containment
tests cover it), add `"solid/widgets/panel-background.svg": ("",)` to `ORIGIN_STATES` (its
unprefixed margin rects sit at the origin of the canvas grown to hold the 22px-tall `north-`
state, like `panel-background.svg`), and add
`os.path.join("solid", "widgets", "panel-background.svg")` to `TestInstall.INSTALLED_FILES`.
- `tests/test_desktoptheme_panel.py`: import `SOLID_PANEL_SVG` and add
`test_solid_copy_is_identical` to `TestPanelBackground`, opening `PANEL_SVG` and `SOLID_PANEL_SVG`
in binary and asserting equal bytes (mirroring `TestTooltip::test_solid_copy_is_identical`).
- `docs/invariants.md`: extend the desktoptheme `widgets/panel-background.svg` row's guarantee
to "`widgets/panel-background.svg` draws the menu bar, including its top-panel north state, and
its `solid/` copy is byte-identical." The row already names `TestPanelBackground`, which holds
the new test.
- `README.md`: in the `widgets/panel-background.svg` sentence, add that a byte-identical copy
ships at `solid/widgets/panel-background.svg`, where `Panel.qml` looks for an opaque panel's
background.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/solid/widgets/panel-background.svg`
(new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`,
`tests/test_desktoptheme_panel.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `solid/widgets/panel-background.svg` is byte-identical to `widgets/panel-background.svg`,
asserted by `TestPanelBackground::test_solid_copy_is_identical`.
- `test_registry_covers_every_shipped_svg` passes with the new file in `SVG_CANVASES`, and
`test_root_canvas_matches_the_artwork_layout`, `test_every_svg_declares_unique_ids` and
`test_every_svg_is_self_contained` cover it (its 12x22 canvas, unique ids, no style/script or
external reference).
- `TestInstall` still passes with the new file listed in `INSTALLED_FILES`.
- `make check` exits 0, including `tests/test_readme_theme_files.py` (its `*/*.svg` glob does not
reach the two-level `solid/` path, and the README prose names the file) and
`tests/test_invariants.py`.
- Removing `solid/widgets/panel-background.svg` makes `test_solid_copy_is_identical` fail (the
open raises) and `test_registry_covers_every_shipped_svg` fail (the shipped set no longer
equals the registry).

### Mac OS 8.6 splash: draw the reference's full "Mac OS 8.6" wordmark (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** The startup splash's wordmark draws the truncated label `Mac OS`;
`macos8.6-screenshots/boot2_betawiki.png` shows the full `Mac OS 8.6`. Draw the full label so the
login splash matches the reference.

**Grounding.** In `macos8.6-screenshots/boot2_betawiki.png` (240x180, the retail 8.6 boot screen
whose `8.6` is legible) the wordmark's black glyphs occupy `x=89..150, y=71..83` — 62 of the 80
columns of the panel's white face (`x=80..159, y=39..88`, re-derived by
`tests/test_splash_reference.py::TestSplashGeometry::test_grid_geometry`). `Splash.qml`'s
`wordmark` Text draws `text: "Mac OS"`, roughly 38 columns centred on the panel, leaving the
reference's leftmost (`x=89..~100`) and rightmost (`x=~140..150`) glyph columns blank. The
original splash plan (PLANS.md `## Done`, "Mac OS 8.6 Platinum startup splash") and
`tests/test_splash_qml.py::test_wordmark_shows_the_reference_label_at_its_grid_size` both call
`Mac OS` the reference label, which the thumbnail does not support.

**Approach.**
- `theme/look-and-feel/org.macos8.desktop/contents/splash/Splash.qml`: change the `wordmark`
  `Text`'s `text` from `"Mac OS"` to `"Mac OS 8.6"`. Leave its `y: 71 * root.unit`,
  `anchors.horizontalCenter: panel.horizontalCenter` and `font.pixelSize: 12 * root.unit`
  unchanged: the 12-row band and the panel centring already match the reference.
- `tests/test_splash_qml.py`: change `test_wordmark_shows_the_reference_label_at_its_grid_size`
  to require `text: "Mac OS 8.6"` and correct its comment, which calls `Mac OS` the reference
  label.
- `tests/test_splash_reference.py`: add `test_wordmark_spans_the_reference_band` to
  `TestSplashGeometry`. Derive the wordmark's black-pixel bounding box from the thumbnail (dark
  pixels with all three channels below a fixed threshold in the band `y=68..86`, `x=84..156`,
  which excludes the logo stem above `y=68`) and assert its width is at least 55 of the face's 80
  columns, so a reference whose label is no wider than `Mac OS` fails instead of silently passing.

**Files touched.** `theme/look-and-feel/org.macos8.desktop/contents/splash/Splash.qml`,
`tests/test_splash_qml.py`, `tests/test_splash_reference.py`.

**Acceptance criteria.**
- The `wordmark` Text's `text` is exactly `"Mac OS 8.6"`; any other string fails
  `test_wordmark_shows_the_reference_label_at_its_grid_size`.
- `test_wordmark_spans_the_reference_band` re-derives the reference wordmark bbox on
  `boot2_betawiki.png` and passes; a label that spans fewer than 55 face columns fails it.
- `make check` exits 0.
- Recorded deviation (not fixed here): the reference wordmark is a high-contrast serif (Apple's
  Garamond-family wordmark) while the QML draws the system UI font, so glyph shapes still differ;
  shipping a typeface is out of scope and the reference set has no larger boot capture to ground
  one.

### Mac OS 8.6 Platinum full-Trash icon (`32x32/places/user-trash-full.svg`) for the icon theme (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** KDE asks for the icon name `user-trash-full` whenever the Trash holds something
(`/usr/share/plasma/plasmoids/org.kde.plasma.trash/contents/ui/main.qml`:
`hasContents ? "user-trash-full" : "user-trash"`; Dolphin's Places panel and the desktop do the
same). The icon theme ships only `theme/icons/org.macos8.desktop/32x32/places/user-trash.svg`, so
the non-empty state falls through `Inherits=breeze` to Breeze's flat modern `user-trash-full.svg`
— the desktop's Trash visibly stops being Platinum the moment it holds a file. Ship our own
full-Trash art so the non-empty state stays Platinum.

**Approach.**
- Add `theme/icons/org.macos8.desktop/32x32/places/user-trash-full.svg`: our own 32x32 Platinum
drawing, the same can as `user-trash.svg` (lid, body outline/face, the two grey/white rib pairs),
with the handle replaced by a `#FFFFFF` paper sheet outlined in `#000000` rising above the lid, so
the can reads as full. Recommended drawing, in document order (the implementer may adjust the
paper shape, but the constraints below hold):
  ```xml
  <path d="M12 2 l3 2 l3 -2 l1 7 h-8 Z" fill="#000000"/>
  <path d="M13 3 l2 1 l2 -1 l1 5 h-6 Z" fill="#FFFFFF"/>
  <rect x="6" y="8" width="20" height="5" fill="#000000"/>
  <rect x="7" y="9" width="18" height="4" fill="#DDDDDD"/>
  <rect x="7" y="9" width="18" height="1" fill="#FFFFFF"/>
  <rect x="7" y="12" width="18" height="1" fill="#999999"/>
  <path d="M9 13 h14 l-2 16 H11 Z" fill="#000000"/>
  <path d="M10 14 h12 l-2 14 H12 Z" fill="#DDDDDD"/>
  <rect x="13" y="16" width="1" height="10" fill="#999999"/>
  <rect x="14" y="16" width="1" height="10" fill="#FFFFFF"/>
  <rect x="17" y="16" width="1" height="10" fill="#999999"/>
  <rect x="18" y="16" width="1" height="10" fill="#FFFFFF"/>
  ```
- Register the file in `tests/test_icon_theme.py`: add its package-relative path to `SHIPPED_ICONS`
and its exact drawing-element tuple (via the module's `_shape` helper) to `ICON_SHAPES`. The
existing `TestIndex`/`TestIcons`/`TestIconGeometry` tests then cover the new icon: it must be a
32x32 square SVG whose fills are a subset of `PLATINUM_FILLS`, with no scripts, `<style>`,
external references or duplicate ids, and every drawing element must match the pinned tuple.
`TestInstall.INSTALLED_FILES` is derived from `SHIPPED_ICONS`, so the install lifecycle covers it
with no further edit.
- `32x32/places` is already a declared directory in `theme/icons/org.macos8.desktop/index.theme`,
so the metadata does not change and no new size directory is added.
- `README.md`: in the icon-theme sentence, change "the desktop's hard-disk, folder, document and
Trash icons" to name the full-Trash art as well (e.g. "…document, Trash and full-Trash icons").
- `docs/invariants.md`: the `icons` section's "ships exactly the tracked icons" row already names
`tests/test_icon_theme.py::TestIndex`, which covers the new file; no text change.

**Files touched.** `theme/icons/org.macos8.desktop/32x32/places/user-trash-full.svg` (new),
`tests/test_icon_theme.py`, `README.md`.

**Acceptance criteria.**
- `tests/test_icon_theme.py`'s `SHIPPED_ICONS` and `ICON_SHAPES` both list the new icon, and
`test_the_geometry_registry_covers_every_shipped_icon` passes; changing one drawing element in the
SVG fails `TestIconGeometry::test_each_icon_draws_its_pinned_artwork`.
- Deleting the SVG, or removing it from either registry, fails `make check`.
- `make check` is green, and `make install XDG_DATA_HOME=<tmp>` installs the new icon
(`TestInstall` covers the installed file set).

### Record-checker mutation harness: manufacture the malformed inputs from the shipped registers so a silent accept or drop is observable (planned 2026-10-18 by the steward role; from the recurring `no-observability` validation gap in thirteen Fixed entries) — done 2026-10-18

**Goal.** Twelve Fixed entries share one mechanism: a record checker (`tests/invariants.py`'s
register parser and reference resolver, `tests/placeholders.py`'s marker scanner) accepted or
silently dropped malformed input that the shipped records never contain, so no test or real run
could surface the bug — each was found by reading the checker and fixed with one hand-written case.
Add a mutation harness that manufactures each malformed shape from the shipped registers
(`docs/invariants.md`, `PLACEHOLDERS.md` and the shipped placeholder markers) and asserts the
checker reports it, so the acceptance boundary is exercised by data and the next silent accept or
drop fails a test instead of waiting for a reader.

**From (the `no-observability` Fixed entries).**
- `tests/invariants.py` register checker, ten entries (all fixed 2026-10-18): accepts a class whose
locally defined base only looks like a test case; accepts a register reference that escapes the
repository; accepts a method reference into a class that is not a test case; accepts a register
reference to a class with no tests; accepts a register reference to a non-test method; accepts a
register reference with a segment after the method; accepts a register reference ending in `::`,
pinning a guarantee to no test; drops a row that does not split into three cells; drops a row whose
Test cell has no backticked reference; drops a row whose cell contains an escaped pipe.
- `tests/placeholders.py` marker scanner, two entries (both fixed 2026-10-18): ignores
`PLACEHOLDER:` markers in the theme's `.kvconfig` file; ignores them in the theme's `.js` and
`.desktoprc` files.
- The thirteenth `no-observability` entry, "Palette anchors are not re-derivable from the reference
screenshots" (fixed 2026-10-08), is a different mechanism — a hard-coded anchor assertion — and is
retired by the register's provenance-exception row and `TestProvenanceNote`, not by this harness.

**Approach.**
- Add `tests/support/checker_scratch.py` and its two per-checker tables
(`tests/support/invariants_mutations.py` and `tests/support/placeholders_mutations.py`): one named
mutation per rejection shape the two checkers must catch, each a transform of a copy of the real
register or of a scratch theme root plus the diagnostic substring the checker must raise. Seed
the table with the twelve shapes above. The reference mutations point the register's first row
at `tests/support/mutant_module.py`, a shipped
fixture holding the class shapes the shipped tests never define, and at a real test case in
`tests/test_checker_mutations.py`; the placeholder mutations name real shipped theme files, so
every path they cite exists in the tree.
- Add `tests/test_checker_mutations.py`: copy `docs/invariants.md` and the placeholder register into
a scratch root, apply each mutation, run the checker, and assert the named diagnostic; a mutation
the checker does not reject fails. Exercise the `.js`/`.desktoprc`/`.kvconfig` cases by writing one
marked file per text format the theme ships into the scratch theme root.
- Give each checker a `REJECTION_SHAPES` list naming the boundaries it must reject (the shapes its
`cross_check` docstring already enumerates), and add a test asserting the list and the mutation
table name the same rejection boundaries, so a boundary named in one without the other fails.

**Files touched.** The checker-mutation fixtures (now `tests/support/checker_scratch.py`,
`tests/support/invariants_mutations.py` and `tests/support/placeholders_mutations.py`),
`tests/test_checker_mutations.py` (new), `tests/support/mutant_module.py` (new),
`tests/invariants.py`, `tests/placeholders.py` (the `REJECTION_SHAPES` lists).

**Acceptance criteria.**
- Every shape above is a mutation entry, and applying it makes the matching checker raise the named
diagnostic; a scratch run with one mutation's expected diagnostic removed demonstrates the harness
fails.
- `REJECTION_SHAPES` for both checkers is covered by the mutation table; removing a table row fails
the guard test.
- `make check` is green, with the existing hand-written rejection tests still passing.

**Implementation note (2026-10-18).** The escaped-pipe and the three placeholder-format
shapes are acceptance boundaries, not rejections: the checker must keep the row or find the
marker, so the harness pins them with an `observe` assertion instead of a diagnostic. The
`REJECTION_SHAPES` lists hold the nine invariant rejections and the three placeholder
rejections; the guard test asserts each list equals the rejection mutation names, so a name
or a mutation added without the other fails. It is a sync check between two hand-maintained
lists, not a detector of a new rejection branch added to a checker on its own.

### Fidelity gate for the rendered window frame's side and bottom borders (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** The rendered-window fidelity gate compares only the title-bar strip
(`TestRender::test_title_bar_matches_the_reference`). The frame's six-pixel left, right and
bottom borders are still pinned only by the SVG unit tests (`tests/test_aurorae_frame.py`) and the
rc test (`tests/test_aurorae_rc.py`), so nothing checks that KWin paints them at the reference
geometry. Extend the same render-and-byte-compare gate to those three border strips. It reuses
the one render `TestRender.setUpClass` already makes; no second render runs.

**Grounding (sampled 2026-10-18 with `tools.png.read_png` + `pixel_at` on a render from
`tools/render_surface.py --settle 3`).** The 320x240 render puts the window at (0,0): a 6px left
border at x=0..5, a 6px right border at x=314..319 and a 6px bottom border at y=234..239.
`aboutsystem_betawiki.png`'s window has its left outline at x=7 and top outline at y=25, so its
left border is x=7..12, its right border x=354..359 and its bottom border y=419..424. The
reference window is taller than the render, so the side strips compare only the straight part
between the title bar and the bottom border (212 rows), and the bottom strip the horizontal
border between the two corners (308 columns). Byte-exact comparisons:
- left: candidate `(0, 22, 6, 212)` vs reference `(7, 47, 6, 212)` — 0 differing of 1272;
- right: candidate `(314, 22, 6, 212)` vs reference `(354, 47, 6, 212)` — 0 differing of 1272;
- bottom: candidate `(6, 234, 308, 6)` vs reference `(13, 419, 308, 6)` — 0 differing of 1848.

**Approach.**
- `tests/test_render_surface.py`: keep `CANDIDATE_CROP`/`REFERENCE_CROP` for the title bar and add
  six module constants beside them — `LEFT_BORDER_CANDIDATE = (0, 22, 6, 212)`,
  `LEFT_BORDER_REFERENCE = (7, 47, 6, 212)`, `RIGHT_BORDER_CANDIDATE = (314, 22, 6, 212)`,
  `RIGHT_BORDER_REFERENCE = (354, 47, 6, 212)`, `BOTTOM_BORDER_CANDIDATE = (6, 234, 308, 6)`,
  `BOTTOM_BORDER_REFERENCE = (13, 419, 308, 6)`, each with its grounding row above as its comment.
  Extract the body of `test_title_bar_matches_the_reference` (the `read_reference` +
  `skip_unless_materialized` guard and the `process_runner.run` of the real `FIDELITY` CLI with
  `--candidate-crop`/`--crop`) into a helper method
  `assert_strip_matches(self, candidate_crop, reference_crop)`; the title-bar test keeps its name
  and calls the helper with its two constants. Add
  `test_frame_borders_match_the_reference`, which loops the three `(candidate, reference)` border
  pairs and calls the helper under `self.subTest`, so a failure names the strip.
- `docs/invariants.md`: add a second `tooling` row
  `| The rendered window's side and bottom border strips are byte-identical to the same strips of
  the reference screenshot. | tests/test_render_surface.py::TestRender::test_frame_borders_match_the_reference | none |`.
- `README.md`: in the Fidelity checking paragraph's `make check` sentence, extend the compared
  region from the title-bar strip to the title bar and the side and bottom borders.

**Files touched.** `tests/test_render_surface.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `make check` passes. `test_frame_borders_match_the_reference` runs (does not skip) where the
  render tools are on `PATH` and the LFS reference is materialized, and skips when the reference
  is an unmaterialized pointer; the existing title-bar test still passes.
- Each strip reports `differing pixels: 0 / 1272` (left and right) and `0 / 1848` (bottom).
- Changing `BorderLeft`, `BorderRight` or `BorderBottom` in
  `theme/aurorae/themes/org.macos8.desktop/org.macos8.desktoprc`, or the border colours in
  `decoration.svg`, makes a named test fail.
- `tests/test_invariants.py` still resolves every register row against the repository.

### Fidelity gate for the rendered window decoration: byte-compare the title-bar strip to `aboutsystem_betawiki.png` (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `tools/render_surface.py` renders the themed window in a headless KWin session and
`tools/fidelity.py` compares a rendered PNG against a reference screenshot, but no reference crop
or threshold for a rendered surface is chosen, so nothing checks that the assembled theme renders
like the reference. This is the later plan the render entry's "Out of scope" names. Choose the
first such crop — the window title bar — add a `--candidate-crop` option so the candidate can be
cropped to the reference crop's size, and pin the whole pipeline (install, KWin, Aurorae, render)
with a `make check` test that byte-compares the strip.

**Grounding (sampled 2026-10-18 with `tools.png.read_png` + `pixel_at`).** A 320x240 render
(`tools/render_surface.py --settle 3`, `org.kde.plasma.calculator`) puts the window's title bar at
the top of the capture: row 0 is the `#000000` top outline, rows 1..20 are the Platinum pinstripes,
row 21 is the `#000000` title-bar bottom outline. `aboutsystem_betawiki.png` (retail) has the same
window chrome one row per row at `y=25..46`: row 25 the top outline, rows 26..45 the pinstripes,
row 46 the bottom outline. So the render's rows `0..21` map to the reference's rows `25..46`.
The pinstripes are horizontal, so the x offset does not matter as long as both crops stay clear of
the close box and the centred title text: the reference's close box face is x=11..22 with its
`#FFFFFF` highlight at x=23, and the title text is centred near x=180. The strip `x=30..109,
y=0..21` of the render is byte-identical to `x=30..109, y=25..46` of the reference (0 differing
pixels of 1760, max channel delta 0); the same render compared to `y=24..45` or `y=26..47` fails,
so the one-row alignment is pinned by the test.

**Approach.**
- `tools/fidelity.py`: add `--candidate-crop X,Y,W,H` (`type=parse_crop` from
  `tools/fidelity_arguments.py`, extracted 2026-10-25 by the organize role;
  `metavar="X,Y,W,H"`, help "crop the candidate to this region before comparing"), apply it as
  `candidate = crop(candidate, *args.candidate_crop)` before `compare` (beside the existing
  `reference = crop(reference, *args.crop)`), and print `candidate crop: X,Y,W,H` when set,
  beside the existing `reference crop:` line. Update the module docstring's usage line to
  `[--candidate-crop X,Y,W,H]`. A run without the option is byte-for-byte unchanged in
  behaviour and output.
- `tests/test_fidelity_cli.py`: cover the option in `TestCli`, mirroring the existing `--crop`
  tests: `_write_padded_surface_pair` returns a 2x2 surface and a 4x4 padded image that embeds it
  at (1,1), so pass the padded image as candidate and the surface as reference with
  `--candidate-crop 1,1,2,2` and assert it passes; the `candidate crop:` rectangle is echoed
  only when the option is given; a malformed rectangle (`1,2,3`) is a usage error naming
  `--candidate-crop`; and a rectangle outside the candidate is a read error from `crop()`.
- `tests/test_render_surface.py`: add module constants beside `SCRIPT` — `FIDELITY =
  str(repo_root.ROOT / "tools" / "fidelity.py")`, `REFERENCE =
  str(repo_root.ROOT / "macos8.6-screenshots" / "aboutsystem_betawiki.png")`,
  `CANDIDATE_CROP = (30, 0, 80, 22)` and `REFERENCE_CROP = (30, 25, 80, 22)` — and a
  `test_title_bar_matches_the_reference` method to `TestRender`. It loads `REFERENCE` with
  `support.reference_image.read_reference` + `skip_unless_materialized` (imported beside the
  other `support` imports, so it skips where the LFS image is absent, like the other reference
  tests), then runs the real CLI `[sys.executable, FIDELITY, cls.output, REFERENCE,
  "--candidate-crop", "30,0,80,22", "--crop", "30,25,80,22"]` through `process_runner` and
  asserts exit 0 and `differing pixels: 0 / 1760` in stdout. It reuses the render `setUpClass`
  already makes, so no second render runs.
- `docs/invariants.md`: add a `tooling` row
  `| The rendered window's title-bar strip is byte-identical to the same strip of the reference
  screenshot. | tests/test_render_surface.py::TestRender::test_title_bar_matches_the_reference |
  none |`.
- `README.md`: in the Fidelity checking paragraph, replace the closing sentence "no reference
  crop or threshold for a rendered surface is chosen yet" with the chosen crop: `make check`
  renders the window (`make render`) and byte-compares its title-bar strip at candidate
  `30,0,80,22` against reference `30,25,80,22` of `aboutsystem_betawiki.png`, naming
  `--candidate-crop`.

**Files touched.** `tools/fidelity.py`, `tests/test_fidelity_cli.py`, `tests/test_render_surface.py`,
`docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `python3 tools/fidelity.py <render.png> macos8.6-screenshots/aboutsystem_betawiki.png
  --candidate-crop 30,0,80,22 --crop 30,25,80,22` exits 0 and prints `differing pixels: 0 /
  1760`; without `--candidate-crop` the run still fails on the size mismatch, and a run with
  neither option is unchanged.
- `TestRender.test_title_bar_matches_the_reference` passes where the render tools and the
  materialized reference are present, and skips when the reference is an unmaterialized LFS
  pointer. Changing the Aurorae pinstripe colours, the title-bar height, or the close-box width
  (so the close box reaches x=30) makes it fail.
- The new `--candidate-crop` tests in `tests/test_fidelity_cli.py` pass, and the existing
  `--crop` tests still pass unchanged.
- `docs/invariants.md` resolves the new tooling row, and `make check` is green.

### Mac OS 8.6 Platinum desktop icon action buttons (`widgets/action-overlays.svg`) for the desktop theme (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** Ship `widgets/action-overlays.svg` so the desktop containment's folder-icon action buttons draw Platinum add/open/remove buttons instead of inheriting Breeze's. The theme ships no `widgets/action-overlays`, so `KSvg` resolves the name to the default theme's Breeze file. It is the last widget name the default session's applets reference and the theme does not ship: the layout's kicker, appmenu, systemtray, digitalclock, windowlist and desktopcontainment reference every other widget name the theme ships. Independent of every shipped widget: it adds one artwork file, one path constant, one test module and registry/README/register lines.

**Consumers (verified in the installed Plasma 6.3.6 tree).**
- `/usr/share/plasma/plasmoids/org.kde.desktopcontainment/contents/ui/FolderItemActionButton.qml` is an `SvgItem` whose `svg` is `KSvg.Svg { imagePath: "widgets/action-overlays"; multipleImages: true; size: "16x16" }`; it sets `elementId: element + "-normal"`, switching to `element + "-hover"` while the pointer is over it and `element + "-pressed"` while down. Its width and height are `Kirigami.Units.iconSizes` chosen from `Plasmoid.configuration.iconSize` (small 16, smallMedium 22, medium 32, large 48), so the 16x16 art scales.
- `/usr/share/plasma/plasmoids/org.kde.desktopcontainment/contents/ui/FolderItemDelegate.qml` instantiates it with `element: model.selected ? "remove" : "add"` (the selection toggle) and `element: "open"` (the folder-popup button); both appear on hover over a desktop icon in the layout the global theme applies. The default theme's `widgets/action-overlays.svg` ships the plain ids `add-`/`open-`/`remove-` plus `base`, and no size-prefixed ids, so the consumer resolves the plain ids.
- `main.qml` sets `imagePath: "widgets/toolbox"` on an `Svg` it never draws, and no installed desktop theme ships a `toolbox.svgz`; the toolbox is dead code, not a surface to style.

**Provenance.** No Mac OS 8.6 screenshot in the reference set shows a hover action button, so the shape and its three states are KDE-required; the fills reuse the grounded Platinum faces the other widgets ship (`#000000` outline, `#FFFFFF` highlight, `#999999` shadow, `#DDDDDD` face). No new palette constant is introduced.

**Approach.**
- New `theme/desktoptheme/org.macos8.desktop/widgets/action-overlays.svg`, a 16x16 canvas with nine groups, ids `add-normal`, `add-hover`, `add-pressed`, `open-normal`, `open-hover`, `open-pressed`, `remove-normal`, `remove-hover`, `remove-pressed` (the plain ids the consumer resolves):
  - each group opens with the invisible `0,0,16,16` `fill="none"` bounding rect, then the `actionbutton.svg` circle recipe at (8,8): a `#000000` r=7 outline circle, the two bevel half-discs of radius 6 split on the top-right to bottom-left diagonal, and the `#DDDDDD` r=5 face circle;
  - `normal` and `hover` keep the raised bevel (`#FFFFFF` top-left half, `#999999` bottom-right half) and `pressed` swaps it; the `hover` face is `#FFFFFF` (a lit Platinum button), the `normal` and `pressed` face `#DDDDDD`;
  - a `#000000` glyph over the face: `add` a plus, `remove` a minus (each a stroked path with `fill="none"`), `open` a right-pointing filled triangle, sized to fit inside the r=5 face.
- `tests/support/desktoptheme_paths.py`: add `ACTION_OVERLAYS_SVG = os.path.join(PACKAGE, "widgets", "action-overlays.svg")`.
- New `tests/test_desktoptheme_actionoverlays.py`, modelled on `tests/test_desktoptheme_actionbutton.py` (extends `SvgCase`): `TestActionOverlays` pins the nine ids (`assert_ids_present`), the parsed fill set (`PLATINUM_FILLS | {"none"}`), the stroke set (`{"#000000"}`), `assert_no_script_elements`, each group's bounds rect, each state's circle geometry and bevel order, and each kind's glyph path (`d`, `fill`, `stroke`, `stroke-width`).
- `tests/test_desktoptheme.py`: add `("action-overlays.svg", ACTION_OVERLAYS_SVG, 16, 16)` to `SVG_CANVASES` (and a clause about it to the canvas comment) and `os.path.join("widgets", "action-overlays.svg")` to `TestInstall.INSTALLED_FILES`.
- `docs/invariants.md`: add the desktoptheme row `widgets/action-overlays.svg` draws the Platinum desktop icon action buttons. | `tests/test_desktoptheme_actionoverlays.py::TestActionOverlays` | none.
- `README.md`: add `widgets/action-overlays.svg` to the desktop theme's widget inventory sentence.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/action-overlays.svg` (new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme_actionoverlays.py` (new), `tests/test_desktoptheme.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `action-overlays.svg` parses with a 16x16 root canvas; the nine element ids are present and unique; every fill is in `PLATINUM_FILLS | {"none"}` and every stroke `#000000`.
- Every group carries the `0,0,16,16` invisible bounds rect; `normal`/`hover` paint the white-top-left/grey-bottom-right bevel and `pressed` the swapped one; the `hover` face is `#FFFFFF`, the `normal`/`pressed` face `#DDDDDD`; each kind's glyph is pinned by its `d` and its stroke/fill attributes.
- `make install` copies the SVG into the installed desktop theme and `make uninstall` removes it (through `TestInstall`), `test_registry_covers_every_shipped_svg` and the README backtick test pass, and `docs/invariants.md` resolves the new row's test.
- `make check` is green.

### Mac OS 8.6 Platinum round action button (`widgets/actionbutton.svg`) for the desktop theme (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** Ship `widgets/actionbutton.svg` so `PlasmaComponents.RoundButton` and `PlasmaComponents.Dial` draw a Platinum circle instead of inheriting Breeze's blue one. The theme ships no `widgets/actionbutton`, so `KSvg` resolves the name to the default theme's Breeze file. It is the last of the `actionbutton`/`busy`/`switch` surfaces the done plans name (`busy` and `switch` are done). Independent of every shipped widget: it adds one artwork file, one path constant, one test module and registry/README lines.

**Consumers (verified in the installed Plasma 6.3.6 tree).**
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/RoundButton.qml` reads `imagePath: "widgets/actionbutton"` in one `KSvg.Svg`, draws element `pressed` while down/checked else `normal` (`buttonItem`), and overlays `Private.RoundShadow` with states `hidden`/`hover`/`focus`/`shadow`.
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/Dial.qml` reads `imagePath: "widgets/actionbutton"`, element `pressed` while pressed else `normal`.
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/private/RoundShadow.qml` reads `imagePath: "widgets/actionbutton"` and draws element `hover`, `focus` and (default state) `shadow`.
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/RadioIndicator.qml` uses the older combination: `imagePath: "widgets/actionbutton"`, element `normal`, over `widgets/checkmarks`.
- Breeze's `actionbutton.svg` (the default theme) ships elements `normal`, `pressed`, `hover`, `focus` and no `shadow` element (verified by decoding `/usr/share/plasma/desktoptheme/default/widgets/actionbutton.svgz`); a missing `shadow` draws nothing, so the theme keeps Breeze's behaviour there. No shipped plasmoid uses `RoundButton`/`Dial`/`RoundShadow`, so this surface is not visible in the default session; it completes the widget set for third-party Plasma widgets.

**Provenance.** Mac OS 8.6 draws no round button, so the shape and its hover/focus rings are KDE-required; the fills reuse the grounded Platinum face and bevel the other widgets ship (`#000000` outline, `#FFFFFF` highlight, `#999999` shadow, `#DDDDDD` face), and the focus ring reuses `button.svg`'s 1px `#000000` ring treatment. State this in the file's header comment.

**Approach.**
- New `theme/desktoptheme/org.macos8.desktop/widgets/actionbutton.svg`, a 36x36 canvas with four `<g>` elements, each opening with an invisible 36x36 bounding rect, so `KSvg` scales all four by the same bounds:
  - `normal` (raised): a filled `#000000` circle r=17 (outline), then a `#FFFFFF` half-disc path (top-left half, r=16) and a `#999999` half-disc path (bottom-right half, r=16) painting the 1px bevel, then a filled `#DDDDDD` circle r=15 (face). Each half-disc is one `M`/`A`/`Z` path, so `path_arcs` reads one 180-degree arc.
  - `pressed` (sunken): the same circles with the bevel halves swapped — `#999999` top-left, `#FFFFFF` bottom-right.
  - `hover` and `focus`: a 1px `#000000` ring in the outermost pixel, just outside the r=17 outline, drawn as one donut path — a full r=18 circle and a full r=17 circle wound the other way, so the nonzero fill rule leaves the interior transparent and the underlying `normal` art shows through.
  - no `shadow` element (Breeze ships none).
- `tests/support/desktoptheme_paths.py`: add `ACTIONBUTTON_SVG = os.path.join(PACKAGE, "widgets", "actionbutton.svg")`.
- New `tests/test_desktoptheme_actionbutton.py`, modelled on `tests/test_desktoptheme_radiobutton.py` (circles) and `tests/test_desktoptheme_busywidget.py` (arcs):
  - `TestActionButton(SvgCase, unittest.TestCase)` with `SVG_PATH = ACTIONBUTTON_SVG`.
  - `test_actionbutton_contract`: `assert_ids_present(self, self.tree, ("normal", "pressed", "hover", "focus"))`, the parsed fill set is exactly `PLATINUM_FILLS | {"none"}`, and `assert_no_script_elements`.
  - `test_actionbutton_geometry`: for `normal`, the circles are `(18, 18, 17, "#000000")` then `(18, 18, 15, "#DDDDDD")`, and the two half-disc paths' arcs reconstruct (18,18) at r=16; their fills in document order are `#FFFFFF` then `#999999`, so the paint order pins the top-left highlight. For `pressed`, the same geometry with the two fills swapped. For `hover` and `focus`, the group holds no circle but one `#000000` donut path whose four 180-degree arcs reconstruct (18,18) at radii 18, 18, 17, 17 with the inner pair wound the other way, so a filled disc, a same-winding path or a swapped inner/outer radius fails. Every group must also hold one invisible 36x36 bounding rect, so all four scale identically.
- `tests/test_desktoptheme.py`: add `("actionbutton.svg", ACTIONBUTTON_SVG, 36, 36)` to `SVG_CANVASES` and `os.path.join("widgets", "actionbutton.svg")` to `TestInstall.INSTALLED_FILES`.
- `docs/invariants.md`: add the desktop-theme row `| widgets/actionbutton.svg draws the Platinum round action button. | tests/test_desktoptheme_actionbutton.py::TestActionButton | none |`.
- `README.md`: add `widgets/actionbutton.svg` to the desktop theme's widget inventory sentence.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/actionbutton.svg` (new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme_actionbutton.py` (new), `tests/test_desktoptheme.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `actionbutton.svg` parses with a 36x36 root canvas and the four named groups; its parsed fills are exactly the Platinum four plus `none` (the bounding rects).
- `normal`/`pressed` are concentric circles at (18,18) with r=17/16/15 and opposite bevel orders; `hover`/`focus` are a r=17..18 `#000000` donut path with a transparent r=17 interior, all pinned by name.
- `make install` copies the file into the installed desktop theme and `make uninstall` removes it (through `TestInstall`), the SVG registry covers it (through `TestSvgRootCanvas.test_registry_covers_every_shipped_svg`), and the README and `docs/invariants.md` list it.
- `make check` is green.

- Mac OS 8.6 Platinum busy indicator (`widgets/busywidget.svg`) for the desktop theme (planned 2026-10-18, done 2026-10-18; commit b42c20a)
- Invariants register: `docs/invariants.md` pinning each subsystem's guarantee to its test (planned 2026-10-18, done 2026-10-18; commit 6dfe56b)
- Mac OS 8.6 Platinum switch widget (`widgets/switch.svg`) for the desktop theme (planned 2026-10-18, done 2026-10-18; commit 448301a)
- Mac OS 8.6 Kvantum widget style, part 4/4: select the Kvantum style from the global theme (planned 2026-10-18, done 2026-10-18; commit 1ce5330)
- Mac OS 8.6 Kvantum widget style, part 3/4: the Platinum surface controls (planned 2026-10-18, done 2026-10-18; commit d16dec4)
- Mac OS 8.6 Kvantum widget style, part 2/4: the Platinum track and value controls (planned 2026-10-18, done 2026-10-18; commit c8220b9)
- Mac OS 8.6 kicker logo: our own non-infringing `start-here-kde-symbolic` icon (planned 2026-10-18, done 2026-10-18; commit 397f190)
- Mac OS 8.6 Kvantum widget style, part 1/4: ship the `org.macos8.desktop` Kvantum theme with the Platinum palette and the core-control art (planned 2026-10-18, done 2026-10-18; commit 1e9762f)
- Mac OS 8.6 Platinum icon theme: replace the placeholder art with final non-infringing art (planned 2026-10-18, done 2026-10-18; commit ca89e96)
- Own icon art: `PLACEHOLDER:` markers and a test that keeps `PLACEHOLDERS.md` complete (planned 2026-10-18, done 2026-10-18; commit 58830a3)
- Mac OS 8.6 Platinum desktop icon theme: a minimal `org.macos8.desktop` icon package for the icons the desktop shows (planned 2026-10-18, done 2026-10-18; commit 364335d)
- Local theme apply, part 2/2: `make install-local-hook` writes an uncommitted `post-commit` hook that runs `make apply` (planned 2026-10-18, done 2026-10-18; commit e897ef0)
- Local theme apply, part 1/2: `make apply` installs and re-applies the theme to the running Plasma session (planned 2026-10-18, done 2026-10-18; commit c7c2d14)
- Mac OS 8.6 menu-bar top highlight: a `north-` panel-background state whose centre carries the white row 0 (planned 2026-10-18, done 2026-10-18; commit cdc6e60)
- Mac OS 8.6 Qt widget style: select Qt's built-in square-bevel `Windows` style from the global theme (planned 2026-10-18, done 2026-10-18; commit a318999)
- Mac OS 8.6 menu-title spacing: 7px horizontal padding in `widgets/menubaritem.svg` (planned 2026-10-18, done 2026-10-18; commit 31208c2)
- Mac OS 8.6 desktop icon labels: one line of text under each icon (planned 2026-10-18, done 2026-10-18; commit 727cde4)
- Mac OS 8.6 desktop icon arrangement: one right-aligned column of 32px icons (planned 2026-10-18, done 2026-10-18; commit aacf578)
- Mac OS 8.6 Platinum tooltip (`widgets/tooltip.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit 84cdbbb)
- Mac OS 8.6 menu-bar clock format: 12-hour time with AM/PM, no date, no seconds (planned 2026-10-17, done 2026-10-17; commit dc4dfce)
- Clear the title-bar pinstripes around the zoom box, as Mac OS 8.6 does (planned 2026-10-17, done 2026-10-17; commit d59e398)
- Grow the Aurorae title-bar boxes to 13x13 with their white highlight (planned 2026-10-17, done 2026-10-17; commit 73bd870)
- Mac OS 8.6 zoom box glyph and collapse (windowshade) box for the Aurorae decoration (planned 2026-10-17, done 2026-10-17; commit ffa77e7)
- Mac OS 8.6 Platinum applet-popup heading (`widgets/plasmoidheading.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit 262f2d9)
- Mac OS 8.6 Platinum etched separator (`widgets/line.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit 0446a33)
- Mac OS 8.6 menu-bar desktop layout for the global theme (`contents/layouts/`) (planned 2026-10-17, done 2026-10-17; commit 76ba0c4)
- Headless Plasma render-and-capture script that feeds `tools/fidelity.py` (planned 2026-10-17, done 2026-10-17; commit 4422d20)
- Wallpaper, part 2/2: Install the Mac OS 8.6 wallpaper package and select it from the global theme (planned 2026-10-17, done 2026-10-17; commit 884c659)
- Wallpaper, part 1/2: Mac OS 8.6 default desktop pattern as a Plasma wallpaper package (planned 2026-10-17, done 2026-10-17; commit d46c4eb)
- Mac OS 8.6 Platinum progress bar widget (`widgets/bar_meter_horizontal.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit a683b57)
- Mac OS 8.6 Platinum popup / dropdown arrow widget for the desktop theme (done 2026-10-17; commit 1b5c020)
- Mac OS 8.6 Platinum toolbar background widget for the desktop theme (done 2026-10-17; commit ff71c62)
- Mac OS 8.6 Platinum tab-bar highlight widget for the desktop theme (done 2026-10-17; commit c8d132b)
- Mac OS 8.6 Platinum menu-bar item widget for the desktop theme (done 2026-10-09; commit 370205e)

- Mac OS 8.6 Platinum view item widget for the desktop theme (planned 2026-10-09, done 2026-10-09; commit 1e1a455)
- Mac OS 8.6 Platinum slider widget for the desktop theme (planned 2026-10-09, done 2026-10-09; commit 698e2b2)
- Wire the Mac OS 8.6 window decoration into the global theme defaults (planned 2026-10-09, done 2026-10-09; commit 0063255)
- Mac OS 8.6 Platinum window decoration (`aurorae/themes/`) part B1: inactive frame and inactive widget state (planned 2026-10-08, done 2026-10-09; commit 91189a7)
- Mac OS 8.6 Platinum window decoration (`aurorae/themes/`) part A: active frame, close and zoom widgets (planned 2026-10-08, done 2026-10-08; commit 15bee80)
- Mac OS 8.6 Platinum startup splash (`contents/splash/`) for the global theme (planned 2026-10-08, done 2026-10-08; commit 395994f)
- Mac OS 8.6 Platinum menu / popup background (`widgets/background.svg`) for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 27b7439)
- Mac OS 8.6 Platinum dialog / applet-popup background for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 8df5661)
- Mac OS 8.6 Platinum scroll bar widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 9f51d5b)
- Mac OS 8.6 Platinum list item widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 7fe6ddc)
- Mac OS 8.6 Platinum text field widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 0fe5213)
- Mac OS 8.6 Platinum checkmarks widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 7313acd)
- Mac OS 8.6 Platinum radio button widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit a73c322)
- Mac OS 8.6 Platinum frame widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit ebb65ca)
- Mac OS 8.6 Platinum button widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit e553908)
- Mac OS 8.6 desktop theme package with the Platinum panel background (planned 2026-10-07, done 2026-10-07; commit 126538c)
- Mac OS 8.6 look-and-feel global theme package (planned 2026-10-07, done 2026-10-07; commit 0c0cd8b)
- Mac OS 8.6 Platinum color scheme and project check harness (planned 2026-10-07, done 2026-10-07; commit 2e58776)
