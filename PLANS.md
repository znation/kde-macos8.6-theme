# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role; shipped-SVG count updated
2026-10-27 by the feature role; Firefox content scope refreshed
2026-10-29 by the steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (thirty-one widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight and the
`widgets/containment-controls.svg` panel resize and slider handles, plus
`dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's;
the 2026-10-29 user decision supersedes its final-art status and queues placeholder tracking
below); the `org.macos8.desktop` Kvantum widget
style (Platinum palette and core-control art); the
`org.macos8.desktop` Lato font package (Lato Regular and Bold, the Debian copyright file
carrying the upstream SIL OFL 1.1 body, and the provenance record; installed by `make install`,
and the global theme selects its `Lato` family for the general, menu, toolbar, smallest-readable
and window-title fonts, while monospaced text keeps the user's fixed font); the GTK 3 and GTK 4
Platinum stylesheets under `theme/gtk/` (installed by the opt-in `install-gtk` target and
selected by `apply-gtk`; `make install` copies no GTK files); the standalone Firefox Platinum
sheets under `theme/firefox/` (its `userChrome.css` and `userContent.css` copied, and its
profile preference written, only by the opt-in `install-firefox` target); and the render and
fidelity tooling.
The live reference-comparison gate in `tests/test_render_surface.py` checks Aurorae window-chrome
regions when its render prerequisites are available (README.md, "Fidelity checking").
Firefox's `tests/test_firefox_theme_*.py` and `tests/test_firefox_content_*.py` modules
check stylesheet declarations and selector behavior;
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
sidebar frame, the menu-bar title box, the tab faces and the app-menu rows). The
`userContent.css` sheet now styles surfaces within six internal pages:
about:downloads, about:config, about:preferences, about:support, about:networking
and about:telemetry. These include preferences navigation and controls, support
tables and buttons, and telemetry navigation, tables and histograms; this is
surface coverage, not a claim of complete page theming. The opt-in profile install
copies this sheet alongside `userChrome.css`. This content work extends the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

_None yet._ (Only the standing scope-drift note above.)

### Kvantum color dialog render gate: pin a captured kdialog color picker's basic-color swatches, sunken value fields and push buttons on the landed palette and art recipe (planned 2026-11-10 by the plan role; the same CLI-plumbing files as the waiting calendar-dialog entry ahead of it, a further widget surface — the two entries share no assertion region and may merge in any order, so at implementation re-read the landed mode lists and re-grep every anchor this entry names)

**Goal.** No render gate captures the color dialog: kdialog's `--getcolor` opens KDE's color dialog, whose swatch grid, shade selector, value fields and push buttons are drawn by the widget engine with the theme's palette, so a change to the landed color scheme (`[Colors:Window]` `BackgroundNormal=221,221,221`, `[Colors:Button]`, `[Colors:View]` in `theme/color-schemes/MacOS8.colors`) or to the engine's spin-box, line-edit or push-button painting would ship green. Verified today (2026-11-10) on this host: a probe full-lifecycle render sequenced through `tools/render_workflow.py`'s setup (client `kdialog --title Test --getcolor`, settle 8, 480x360 virtual desktop, timeout 90) returned a themed capture: a flat #DDDDDD window face carrying, on the left, the basic-color swatch grid (eight columns of flat 18px cells at x=17..34, 45..62, 73..90, … separated by #DDDDDD gaps; row one leads with the black #000000 cell and the red #AA0000 second cell, row two the navy #00007F first cell — Qt's constant 48-color grid, not palette ink), below it the empty custom-color grid's white #FFFFFF cells, on the right a vertically shading gradient selector whose rows darken from #F9F9F9 toward #0D0D0D, a row of sunken value fields (white #FFFFFF faces with the #999999 top-left shadow and black outlines, y≈196..315 at x≈242..467) and the OK/Cancel push buttons in the lower right. Two consecutive full captures agreed byte for byte under `cmp`, so every band is deterministic without any date or default pin: the dialog shows no clock-dependent content. No collected reference screenshot shows a color dialog, so the comparison values are the shipped art recipe and the palette's own entries plus the swatch grid's Qt constants, recorded in the invariants row with this provenance.

**Approach and files.** In `tools/render_clients.py` add `color_dialog_client(_session)` beside `menu_dialog_client`, returning `kdialog --title Test --getcolor` with its docstring recording the determinism rationale above. In `tools/render_surface.py` add a mutually exclusive `--color-dialog` flag into the existing `dialog_flags` list and the `kdialog_flags` tuple, rejecting `--width`, `--height` and a non-default `--applet` and fixed at 480x360 like the other dialog modes; include the flag in the help text. In `tools/render_workflow.py` import the new client in both the package and the direct-run import blocks and extend the `dialog` OR-chain and the client dispatch beside `menu_dialog`. In the `Makefile` `RENDER_MODE` case add `color-dialog) set -- --color-dialog ;;` beside the `calendar-dialog`/`menu-dialog` branches and extend both enumeration error strings. In `tests/test_render_surface.py` add unit cases beside the landed dialog-mode cases (mutually exclusive with the other dialog flags and the calculator surface, missing-tool naming names kdialog, `--help` names the mode, `test_only_dialog_renders_add_kdeglobals_to_the_session_configs` reads unchanged) and extend `TestDialogGateSkipGuards`' gate tuple in `test_all_dialog_gates_skip_only_when_a_tool_is_absent` with the new class, aligning its docstring. Model the gate class `TestColorDialogRender` on `TestMenuDialogRender` (same `_DialogGate` base, prerequisite and software-renderer-guard skips): measure the window origin and crops from two consecutive full `--color-dialog` captures on the implementation host that agree byte for byte under `cmp`, and record both measured-crop dates in the class comment the way the landed crops' comments do; this plan's probe numbers are not the gate's anchors — the gate re-derives every crop and expected hex from fresh same-render double captures, choosing bands clear of the gradient selector's dithered rows and of every glyph row wherever a flat band exists. Pin four bands: (a) one window-face interior crop chosen in a column/row region clear of the swatch grids, the value fields, the gradient selector and all four window borders, expecting the flat #DDDDDD palette window face with no other ink inside; (b) one band over the basic-color grid's first row expecting the exact measured flat cell fills of the black lead cell and its red #AA0000 neighbour separated by the #DDDDDD gap, so a resampled, recoloured or dropped swatch fill fails; (c) one band over the sunken value-field row expecting the white #FFFFFF face inside the black outline with the #999999 top-left shadow arm, so a shifted outline, a lost shadow or a full-strength text ink fails; (d) one band over the OK or Cancel push button's full-height label-free cell expecting the landed raised push-button recipe re-derived from the shipped button art (the 1px black border, the white bevel arm, the flat #DDDDDD face and the #AAAAAA shadow arm), so a stock-rounded, recoloured or duplicated-face button fails. README's dialog-mode enumeration sentences (the command list, the `RENDER_MODE` list, the dialog descriptions and the capture table's dialog rows) collect the new mode to whatever count and wording the landed state shows at implementation (the waiting calendar entry also extends those sentences); docs/invariants.md's `## tooling` table gains one dated (2026-11-10) end-of-table row naming the gate's tests, the missing color-dialog reference surface, the Qt-constant swatch and art/palette value sources above, and the determinism probe's provenance with its date.

**Acceptance criteria.**

- `python3 tools/render_surface.py --color-dialog out.png` and `make render RENDER_MODE=color-dialog out.png` reach the same argv; using the new flag with any other dialog flag or the calculator surface, or with `--width`/`--height`/a non-default `--applet`, exits 2 before installing; a missing kdialog is named as the first missing tool; `--help` and the Makefile's RENDER_MODE enumeration name the new mode.
- When the documented render prerequisites are present and the software-renderer guard is quiet, two consecutive full `--color-dialog` captures agree byte for byte under `cmp`, and the gate's four pinned bands match the expected pixels: the window-face crop paints the flat #DDDDDD face with no other ink inside, the swatch band paints the measured flat black and #AA0000 cells with the #DDDDDD gap between them, the value-field band paints the white face inside the black outline with the #999999 shadow arm, and the button band paints the recipe-derived raised bevel with the flat #DDDDDD face. The gate skips cleanly when its tools are missing or the software-renderer guard triggers, so `make check` passes with today's skip behavior on the hosted job.
- The gate code reads no reference screenshot and mentions no brand or library name (the landed sheet-level conventions); the invariants row records the measured-capture provenance and the swatch/art/palette value sources. `make check` passes after the final edit.

### Kvantum icon dialog render gate: pin a captured kdialog icon chooser's sunken list field, top-row search field and push buttons on the landed art recipe (planned 2026-11-10 by the plan role; the same CLI-plumbing files as the waiting color-dialog entry ahead of it, a further widget surface — the two entries share no assertion region and may merge in any order, so at implementation re-read the landed mode lists and re-grep every anchor this entry names)

**Goal.** No render gate captures the icon chooser dialog: kdialog's `--geticon` opens KDE's icon chooser, whose search row, sunken icon-list field and push buttons are drawn by the widget engine with the theme's palette and art, so a change to the landed color scheme ([Colors:Window] `BackgroundNormal=221,221,221`, [Colors:View] `BackgroundNormal=255,255,255` in `theme/color-schemes/MacOS8.colors`) or to the engine's line-edit, item-view or push-button painting would ship green. Verified today (2026-11-10) on this host: a probe full-lifecycle render sequenced through `tools/render_workflow.py`'s setup (Session.create, install_theme, link_kvantum_themes, write_session_configs with `_dialog_config_files()`, write_kvantum_selection, session_command settle 8, 480x360 virtual desktop, timeout 90, run_logged; client `kdialog --title Test --geticon application ""` — no default, format or date pin needed) returned a themed capture: the Aurorae title-bar strip over a flat #DDDDDD window face; a top row carrying a flat #DDDDDD combo/field region and a sunken white search field on the right; a large white #FFFFFF icon-grid field below (roughly y≈58..323 at x≈14..473 on the probe) whose cells carry the fallback icon theme's colorful art in large white cells with black outline rules along the field's top and bottom edges; and a bottom row of raised push buttons (#DDDDDD face, #AAAAAA shadow arm, black border) in the lower right above the window's bottom black outline. Two consecutive full captures agreed byte for byte under `cmp`, so every band is deterministic without any pin. The grid's icon art is the fallback icon theme's, not theme-owned: every band must avoid icon-art cells and glyph rows, and no band may pin any icon's pixels. No collected reference screenshot shows an icon chooser, so the comparison values are the shipped art recipe and the palette's own entries, recorded in the invariants row with this provenance.

**Approach and files.** In `tools/render_clients.py` add `icon_dialog_client(_session)` beside `menu_dialog_client`, returning `kdialog --title Test --geticon application ""` with its docstring recording the determinism rationale and the not-theme-owned icon-art warning above. In `tools/render_surface.py` add a mutually exclusive `--icon-dialog` flag into the existing `dialog_flags` list and the `kdialog_flags` tuple, rejecting `--width`, `--height` and a non-default `--applet` and fixed at 480x360 like the other dialog modes; include the flag in the help text. In `tools/render_workflow.py` import the new client in both the package and the direct-run import blocks and extend the `dialog` OR-chain and the client dispatch beside `menu_dialog`. In the `Makefile` `RENDER_MODE` case add `icon-dialog) set -- --icon-dialog ;;` beside the `color-dialog`/`calendar-dialog`/`menu-dialog` branches and extend both enumeration error strings. In `tests/test_render_surface.py` add unit cases beside the landed dialog-mode cases (mutually exclusive with the other dialog flags and the calculator surface, missing-tool naming names kdialog, `--help` names the mode, `test_only_dialog_renders_add_kdeglobals_to_the_session_configs` reads unchanged) and extend `TestDialogGateSkipGuards`' gate tuple in `test_all_dialog_gates_skip_only_when_a_tool_is_absent` with the new class, aligning its docstring. Model the gate class `TestIconDialogRender` on `TestMenuDialogRender` (same `_DialogGate` base, prerequisite and software-renderer-guard skips): measure the window origin and crops from two consecutive full `--icon-dialog` captures on the implementation host that agree byte for byte under `cmp`, and record both measured-crop dates in the class comment the way the landed crops' comments do; this plan's probe numbers are not the gate's anchors — the gate re-derives every crop and expected hex from fresh same-render double captures, choosing bands clear of the icon-grid's icon-art cells and every glyph row wherever a flat band exists. Pin four bands: (a) one window-face interior crop chosen in the flat #DDDDDD face clear of the search row, the icon-grid field, the buttons and all four window borders, expecting the flat #DDDDDD palette window face with no other ink inside; (b) one band over the icon-grid field's top edge expecting the measured black outline rule with the white #FFFFFF field face below it, so a lost outline, a shifted field or a recoloured view face fails; (c) one band over the top-row search field expecting the white #FFFFFF face inside the black outline with the #999999 top-left shadow arm as freshly measured per the landed line-edit recipe, so a shifted outline, a lost shadow or a full-strength text ink fails; (d) one band over one push button's full-height label-free cell expecting the landed raised push-button recipe re-derived from the shipped button art (the 1px black border, the white bevel arm, the flat #DDDDDD face and the #AAAAAA shadow arm), so a stock-rounded, recoloured or duplicated-face button fails. README's dialog-mode enumeration sentences (the command list, the `RENDER_MODE` list, the dialog descriptions and the capture table's dialog rows) collect the new mode to whatever count and wording the landed state shows at implementation (the waiting color-dialog entry also extends those sentences); docs/invariants.md's `## tooling` table gains one dated (2026-11-10) end-of-table row naming the gate's tests, the missing icon-dialog reference surface, the art/palette value sources above, the probe's provenance with its date, and that the grid cells' icon art is the fallback icon theme's and deliberately unpinned.

**Acceptance criteria.**

- `python3 tools/render_surface.py --icon-dialog out.png` and `make render RENDER_MODE=icon-dialog out.png` reach the same argv; using the new flag with any other dialog flag or the calculator surface, or with `--width`/`--height`/a non-default `--applet`, exits 2 before installing; a missing kdialog is named as the first missing tool; `--help` and the Makefile's RENDER_MODE enumeration name the new mode.
- When the documented render prerequisites are present and the software-renderer guard is quiet, two consecutive full `--icon-dialog` captures agree byte for byte under `cmp`, and the gate's four pinned bands match the expected pixels: the window-face crop paints the flat #DDDDDD face with no other ink inside, the field-edge band paints the measured black outline rule over the white #FFFFFF field face, the search-field band paints the white face inside the black outline with the #999999 shadow arm, and the button band paints the recipe-derived raised bevel with the flat #DDDDDD face. No pinned band contains icon-art pixels, so the gate fails on a theme change but never on a fallback-icon-set change. The gate skips cleanly when its tools are missing or the software-renderer guard triggers, so `make check` passes with today's skip behavior on the hosted job.
- The gate code reads no reference screenshot and mentions no brand or library name (the landed sheet-level conventions); the invariants row records the measured-capture provenance, the art/palette value sources and the icon-art exclusion. `make check` passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
