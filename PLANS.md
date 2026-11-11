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
2026-10-29 by the steward role; landed-series narration trimmed 2026-11-11 by the
steward role):** The
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

Two answers on 2026-10-19 widened the scope, and both are recorded below in their landed
state (their landed-series entry narration trimmed 2026-11-11 by the steward role;
the entries themselves are archived in PLANS-DONE.md).
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19): the GTK 3
and GTK 4/libadwaita Platinum stylesheets under `theme/gtk/` are installed — and selected —
only by the opt-in `install-gtk` and `apply-gtk` targets (`make install` copies no GTK
files), and the opt-in `install-firefox` target copies the Firefox `userChrome.css` and
`userContent.css` sheets into a profile and writes the preference that selects them.
**The UI font** is vendored (QUESTIONS.md, answered 2026-10-19): Lato is installed as the
Charcoal-style body face and selected by the global theme for the general, menu, toolbar,
smallest-readable and window-title fonts, and monospaced text keeps the user's fixed font;
a Chicago-style menu face (part 2/3 of the font series) remains unplanned because its
redistribution licence is unresolved, and Lato is the only family the package installs.
GTK and Firefox applications keep their own chrome unless the opt-in GTK targets or the
Firefox install are used. Firefox chrome work since that series landed as single-surface
chrome plans (the downloads-panel and all-tabs rows, the sidebar frame, the menu-bar title
box, the tab faces and the app-menu rows). The `userContent.css` sheet styles surfaces
within six internal pages — about:downloads, about:config, about:preferences,
about:support, about:networking and about:telemetry — including preferences navigation and
controls, support tables and buttons, and telemetry navigation, tables and histograms; this
is surface coverage, not a claim of complete page theming. This content work extends the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

### Splash render gate, part 2/2: pin the rendered startup splash's field, panel, logo cell and track in `TestSplashRender` (planned 2026-11-11 by the plan role; independent of the waiting file-dialog content-faces part 1/2 — that entry extends `TestFileDialogRender` beside its landed tests, rewords the closing sentence of README's `--file-dialog` paragraph and amends the `--file-dialog` gate row in `docs/invariants.md`, while this entry adds a `("splash", …)` kind to `_Renders.KINDS`, a `SPLASH_REAL_TOOLS` constant beside `DESKTOP_REAL_TOOLS` and a new `TestSplashRender` class at `tests/test_render_surface.py`'s tail, adds one `--splash` paragraph after README's `--desktop` one and amends the `--splash` `## tooling` row in place — no test method, README sentence or invariant row is shared, though both entries edit `tests/test_render_surface.py` and README's `### Rendering a candidate` section, so whichever merges later re-reads the file tail and the section before writing; at implementation re-grep every anchor this entry names; completes the splash series the landed `--splash` plumbing entry opened)

**Goal.** The landed `--splash` plumbing publishes a 640x400 capture of the look-and-feel's own `Splash.qml` but pins no pixel — its `## tooling` row and `tests/test_render_surface_units.py`'s capture-size comment both record that the splash's pixel gate is a later part. So today a runtime-only regression — a recoloured field, a moved or resized panel or logo, a dropped wordmark, a lost or right-anchored progress fill — passes every landed splash test. This entry adds that gate.

**Grounding (measured fresh 2026-11-11 by the plan role: three consecutive full `python3 tools/render_surface.py <scratch>/sN.png --splash` runs on this host, all exit 0, all 640x400, byte-identical under `cmp`; `Splash.qml`'s `unit` = floor(min(640/240, 400/180)) = 2, so the 240x180 content grid paints at 2x centred — content origin (80,20)).** The capture is flat `#63639C` everywhere outside the bevel box x=222..417, y=82..233 (all 226208 outside pixels field-coloured in run 1). The bevel (`bevelX`/`bevelY` 71/31, 98x76 grid) fills that box `#DDDDDD` except the panel box x=236..403, y=94..201 and the track box x=282..357, y=218..225. The panel (`panelX`/`panelY` 78/37, 84x54 grid, 2-grid-px `#BFBFBF` border) draws its full 4px border band `#BFBFBF` and its inner face x=240..399, y=98..197 `#FFFFFF` except the logo cell and the wordmark's antialiased band x=270..368, y=169..187. The logo (`logoX`/`logoY` 107/45, 26x21 grid → 52x42 at (294,110)) paints the placeholder `macos-logo.svg` art, byte-stable across the three runs. The wordmark "Platinum" carries 30 full-strength `#000000` pixels in x=272..364, y=171..186. The progress track (`trackX`/`trackY` 101/99, 38x4 grid) drew its whole 76x8 box `#9B9BEA` in all three runs — the fill is `min(1, stage/6)` of the track's width, left-anchored, and the stage is the `ksplashqml --test` clock (the landed `## tooling` row records one stage every 2 s, so the 8 s settle captures at stage ≥ 3) — so the fill's extent is clock-dependent in principle even though the fresh runs all caught it full; the desktop gate's clock-digit exclusion is the precedent.

**Approach.**

1. First re-verify stability the landed gates' way: two consecutive full `--splash` renders on this host must agree byte-for-byte on every region the tests pin (a pair may differ only inside the track box x=282..357, y=218..225, where the fill extent lives); re-derive every region from the fresh capture — a value the fresh pair disagrees on is unpinnable: record it, never pin it, and note the re-derivation in the test comments.
2. `tests/test_render_surface.py`: add the splash kind and gate class (the `_Renders` and `TestRender` docstrings' concurrent-session counts and the class comments re-read and reworded where the new kind makes them stale):
   - `("splash", ("--splash",), "splash.png")` in `_Renders.KINDS` directly after the desktop kind, and `SPLASH_REAL_TOOLS = REAL_TOOLS + ("ksplashqml",)` beside `DESKTOP_REAL_TOOLS`.
   - New `TestSplashRender(_PixelPins, unittest.TestCase)` at the file's tail, skipping like `TestRender` but on `SPLASH_REAL_TOOLS` plus the shared software-renderer skip, reading its capture through `_Renders.ensure("splash")` with a `candidate_image` accessor in the landed shape; the class docstring inventories the pins:
   - `test_exits_zero` and `test_writes_a_640x400_png` in the landed shape.
   - `test_the_field_fills_everything_outside_the_bevel_box`: every pixel outside x=222..417, y=82..233 is `#63639C` — a recoloured field, a stray client surface or a moved content origin fails here.
   - `test_the_bevel_box_pins_its_face`: inside the bevel box, every pixel outside the panel box and the track box is `#DDDDDD` — a shifted panel or track, a lost bevel arm or stray ink fails here.
   - `test_the_panel_pins_its_border_and_face`: the border band (panel box minus inner face) all `#BFBFBF`; the inner face all `#FFFFFF` except the logo cell and the wordmark band x=270..368, y=169..187 — a recoloured rule, a collapsed border width or wordmark ink escaping its band fails here.
   - `test_the_logo_cell_pins_its_art`: the 52x42 cell at (294,110) byte-compared to the measured pixel map in the landed `ICON_BOX_ROWS` shape — a moved, dropped or resampled logo fails here.
   - `test_the_wordmark_inks_platinum`: at least one full-strength `#000000` pixel inside the band — a dropped wordmark fails here; the glyph antialiasing stays unpinned, mirroring the display-digit and title-glyph live-ink checks.
   - `test_the_track_pins_its_left_anchored_fill`: x=282..293, rows 218..225 all `#9B9BEA` — the fill is left-anchored and one stage's twelfth of the track is already wider than those twelve columns at every stage ≥ 1 — so a dropped fill, a right-anchored fill or a recoloured fill fails here; the fill's extent beyond those columns is the stage clock's and stays deliberately unpinned, with the stage-timing provenance quoted in the test comment.
3. `README.md`: add one `--splash` paragraph to `### Rendering a candidate` directly after the `--desktop` paragraph, in the landed gate-paragraph shape: `--splash` opens the look-and-feel's own startup splash fullscreen at 640x400, and the splash gate (`tests/test_render_surface.py::TestSplashRender`) pins the flat field, the bevel and panel boxes, the logo cell as measured, the wordmark ink and the track's left-anchored fill, while the fill's extent — the splash engine's stage clock — stays deliberately unpinned. Re-read the section before writing (the file-dialog entry edits it too).
4. `docs/invariants.md`: amend the `--splash` `## tooling` row in place — replace its "the plumbing pins no pixel" sentence with the gate's pinned regions, the stage-clock extent exclusion with its reason, the byte-pinned logo cell and the fresh two-run provenance dated 2026-11-11, and gain `tests/test_render_surface.py::TestSplashRender` in its test cell. No other row moves.

**Files.** `tests/test_render_surface.py`, `README.md`, `docs/invariants.md`. No production tool, render plumbing or Makefile change, and no new render mode, flag or capture size.

**Acceptance criteria.**

- On this host the fresh two-render pair agrees byte-for-byte outside the track box, `TestSplashRender`'s new tests pass under `make check`'s gate pass, and a third render's pinned regions compare equal to the first's.
- A regression that recolours the field, moves the panel or logo one pixel, drops the wordmark, loses or right-anchors the progress fill or resamples the logo art fails the corresponding new test (each scan names the region it kills).
- README's `### Rendering a candidate` names the splash gate and its deliberately unpinned fill extent, the amended `--splash` `## tooling` row records the pins, the exclusion with its reason and the 2026-11-11 provenance, and `make check` passes after the final edit.

### File-dialog content faces, part 2/2: pin the places sidebar's entries, group headers and capacity bars in `TestFileDialogRender` (planned 2026-11-11 by the plan role; completes the content-faces series the landed list-panel part 1/2 opened — that prerequisite landed 2026-11-11, so nothing holds this part; independent of the waiting splash render gate part 2/2 — that entry adds a new `TestSplashRender` class at `tests/test_render_surface.py`'s tail, one `--splash` paragraph after README's `--desktop` one and the `--splash` `## tooling` row, while this entry extends `TestFileDialogRender`'s constants and tests beside its landed ones, rewords the closing sentences of README's `--file-dialog` paragraph and amends the `--file-dialog` `## tooling` row — no test method, README sentence or invariant row is shared, though both entries edit `tests/test_render_surface.py` and README's `### Rendering a candidate` section, so whichever merges later re-reads the file tail and the section before writing; at implementation re-grep every anchor this entry names)

**Goal.** The landed file-dialog gate pins the places sidebar's selected row (`#CCCCFF` across x=6..138, rows 108..159) but leaves every other sidebar surface unpinned: today a regression that recolours the sidebar's face, drops a group header, moves or resamples an entry's icon cell, drops a device entry's capacity bar or right-anchors its fill passes every landed test. README's `--file-dialog` paragraph and the `--file-dialog` `## tooling` row still record "the places entries below the selected row" as deliberately unpinned. This entry adds the sidebar's remaining pins — the two group headers, the three entry icon cells and the two capacity-bar troughs — completing the content-faces series the landed list-panel part 1/2 opened.

**Grounding (measured fresh 2026-11-11 by the plan role: two consecutive full `python3 tools/render_surface.py <scratch>/file.png --file-dialog` runs on this host, both exit 0, both 480x360, differing in exactly the 16 caret-strip pixels x=200, y=267..282 the landed gate already excludes — the sidebar region x=6..138, rows 26..349 compared byte-identical across the pair, capacity-bar fill extents included).** The sidebar's structure below and above the landed selected-row band: face `#DDDDDD` everywhere outside the ink named here. Two group headers ink live: "Places" inside x=13..47, rows 39..48, and "Devices" inside x=13..56, rows 171..180. Three entry icon cells, each a 40x26 box drawn by the fallback icon theme: the Home entry's folder cell x=14..53, rows 70..95, and the two device entries' drive cells x=14..53, rows 202..227 and rows 254..279 — the two drive cells are byte-identical to each other at the +52 offset (measured: zero differing pixels), so one measured map pins both, like the landed type-icon cells' shared shapes. The entry labels and the device names ink live to the cells' right (Home measured inside x=58..96, rows 73..84; the device labels inside x=62..119, rows 209..215 and rows 261..267). Each device entry carries a capacity-bar trough x=62..134 (72px), rows 218..223 and rows 270..275: no `#DDDDDD` face pixel inside the trough box; the left cap x=62..63, rows 219..222 draws the fill-side blends (`#C8C8E4`/`#CACAF8` with `#CCCCFF` at x=63); the right cap pins `#B1B1B1` at x=133 with the `#C5C5C5`/`#DCDCDC` edge at x=134, rows 218..223; at least one full-strength `#CCCCFF` and one `#B1B1B1` pixel per trough; and the fill is left-anchored — x=63, rows 219..222 and 271..274 measured `#CCCCFF`. The fill's extent is the host filesystem's live used-space total — the scratch home and `/tmp` share the root filesystem the measured bars report, so session writes can move the fill/free boundary between runs — and stays deliberately unpinned (the splash track's fill-extent and the date band's clock-dependence precedents), even though today's pair measured both boundaries byte-identical.

**Approach.**

1. First re-verify stability the landed gate's way: two consecutive full `--file-dialog` renders on this host must agree byte-for-byte outside the caret strip x=200, y=267..282; re-derive every sidebar value from the fresh pair — a value the fresh pair disagrees on is unpinnable: record it, never pin it, and note the re-derivation in the test comments.
2. `tests/test_render_surface.py`: extend `TestFileDialogRender` in place (no `_Renders.KINDS`, skip-guard or gate-count change — the gate class already exists):
   - reword the class docstring's sidebar claims and `test_the_sidebar_pins_its_selected_row`'s closing comment, which today say the places entries below the band stay deliberately unpinned — after this entry only the labels' glyphs, the group-header glyphs, the type-icon art provenance and the capacity bars' fill/free boundary stay unpinned;
   - add the sidebar constants beside the landed ones (the icon cells in the landed `ICON_CELLS` shape — the two drive cells sharing one measured rows map at their +52 offset — plus the group-header and label live-ink bands and the trough geometry), quoting the measured values and the fresh two-run provenance in comments;
   - new tests: `test_the_sidebar_group_headers_ink_their_live_labels` (one non-face pixel inside each header band — a dropped header fails here); `test_the_places_entry_pins_its_folder_cell` (the Home cell byte-compared to its measured map, plus its live-label check); `test_the_device_entries_pin_their_drive_cells` (both drive cells byte-compared to the shared map — a moved, dropped or resampled cell fails here); `test_the_device_entries_ink_their_live_labels`; `test_the_capacity_bars_pin_their_troughs` (the trough-box, cap and left-anchored-fill pins above, with the fill-extent exclusion's reason quoted — a dropped bar, a moved trough, a recoloured cap, a lost fill or a right-anchored fill fails here); and `test_the_sidebar_face_stays_flat_outside_its_ink` (every sidebar pixel in x=6..138, rows 26..349 outside the pinned cells, trough boxes and live-ink bands is `#DDDDDD` — a stray widget or recoloured face fails here).
3. `README.md`: in the `--file-dialog` paragraph, extend the gate's pin list with the sidebar's group headers, the places and device icon cells, the live labels and the capacity-bar troughs, and state the fill-extent exclusion with its disk-usage reason; keep the sentence that leaves the icon art the fallback icon theme's. Re-read the section before writing (the splash entry edits this section too).
4. `docs/invariants.md`: in the `--file-dialog` `## tooling` row, replace the exclusion clause "and the places entries below the selected row (per README)" with the narrowed set (the group-header and label glyphs, and the capacity bars' fill/free boundary with its disk-usage reason), add the sidebar pins to the row's pinned-regions list, and append the fresh two-run provenance (dated 2026-11-11, differences confined to the caret strip) to the row's provenance cell in the landed re-derivation shape. No other row moves.

**Files.** `tests/test_render_surface.py` (`TestFileDialogRender`'s docstring, constants and tests), `README.md` (one paragraph), `docs/invariants.md` (the `--file-dialog` row in place). No production tool, render plumbing, Makefile or workflow change, and no new render mode, flag, capture size or gate class.

**Acceptance criteria.**

- On this host the fresh two-render pair agrees byte-for-byte outside the caret strip, `TestFileDialogRender`'s new tests pass under `make check`'s gate pass, and a third render's pinned regions compare equal to the first's.
- A regression that recolours the sidebar's face, moves or resamples an entry icon cell one pixel, drops a group header, drops a capacity-bar trough, recolours a cap, loses or right-anchors a fill fails the corresponding new test (each scan names the region it kills).
- README's `--file-dialog` paragraph and the amended `## tooling` row name the sidebar pins and the narrowed deliberately-unpinned set with its reasons, and `make check` passes after the final edit.

## Done

### Fidelity CLI: extract parser construction from comparison orchestration (planned 2026-11-02 by the plan role) — done 2026-11-11 by the feature role

**Goal and grounding.** Make the fidelity entry point readable as a comparison workflow. `tools/fidelity.py::main` currently starts with parser construction and a nested `worst_pixel_limit` validator before it reads images. `tools/fidelity_arguments.py` already owns the other argument validators. The finished report-extraction plan deliberately retained parser setup in the entry point; heading searches found no separate parser-extraction plan. This maintenance task is independent of the queued sampler work.

**Approach and files.** Create `tools/fidelity_cli_parser.py::build_parser`, moving the existing `EscapingArgumentParser` construction and option declarations there without changing their order, help strings, defaults, destinations or types. Move `worst_pixel_limit` to `tools/fidelity_arguments.py` and import the validators into the new parser module. In `tools/fidelity.py::main`, replace the construction block with `build_parser().parse_args(argv)` and remove imports made unused by the move. Support package imports and direct-script execution using the existing conditional import pattern. Keep image reads, crop application, optional diagnostic scans and reporting in their current owners. Inspect repository references to validators imported through `tools.fidelity` before removing those imports; preserve an existing consumer's import path if needed. Bound the change to those three production files and a new `tests/test_fidelity_cli_parser.py`; adjust ownership docstrings in the touched files. No CLI behavior change or new dependency is intended.

**Acceptance criteria.** Before moving declarations, capture characterization fixtures in the new test module for normalized help text and parsed default/explicit namespaces, including both crops, diagnostic switches and combined budgets. The same fixtures pass after extraction. Use the existing unittest framework to verify two independently constructed parsers work, malformed crop/budget/worst-pixel arguments retain status 2 and escaped diagnostics, and help and invalid arguments do not call `tools/fidelity.py::_read_source`. Existing fidelity CLI, JSON, crop and direct-script tests continue to pass. Run `make check` after final edits. This structural change adds no guarantee to docs/invariants.md; its existing tooling contracts remain the acceptance boundary.

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
