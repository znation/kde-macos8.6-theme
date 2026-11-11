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

### Platinum GTK 4 progress meter: pin the rendered trough, fill and disabled fill with an offscreen pixel probe (planned 2026-11-11 by the plan role; independent of the waiting file-dialog content-faces part 2/2 — that entry extends `tests/test_render_surface.py`'s `TestFileDialogRender` beside its landed tests and edits README's `--file-dialog` paragraph and `docs/invariants.md`'s `## tooling` table, while this entry adds one probe to `tests/test_gtk4_theme.py` beside its landed rendered probes and appends one end-of-table `## gtk` row to `docs/invariants.md` — the two share no test, no file region and no README sentence, so either merge order holds; at implementation re-grep every anchor this entry names)

**Goal.** The GTK 4 sheet's plain meter recipe — `progressbar > trough` (the `#EEEEEE` face, 1px `#000000` border, `inset 1px 1px #999999` shadow arm, 10px minimums), `progressbar > trough > progress` (the `#CCCCFF` fill, margin 0) and the `progressbar > trough > progress:disabled` group (the `#999999` disabled fill) — is pinned today only by declaration checks (`tests/test_gtk4_theme.py::TestGtk4Theme::test_progressbar`, `::test_progressbar_disabled_filter`, `::test_disabled_meter_trough_faces`), and the `## gtk` invariants rows for the disabled-filter restatements say so explicitly: declaration coverage, not rendered-pixel evidence. A GTK-side regression — a trough rule that never matches the rendered node tree, a fill colour that never paints, the stock disabled `filter: Opacity(...)` surviving at higher specificity than the landed `filter: none` arm — would ship green, unlike the GTK 3 meter whose offscreen probe (`tests/test_gtk_theme_controls.py::TestGtkThemeControls::test_progressbar_fill_spans_the_trough`) already pins rendered pixels. The suite's three landed GTK 4 rendered probes (`test_mixed_indicators_draw_black_dashes`, `test_spin_field_renders_the_mirrored_etch_in_rtl`, `test_notebook_tab_faces_render` in `tests/test_gtk4_theme.py`) prove the route works; no rendered probe of a `Gtk.ProgressBar` exists (a grep over the file finds no `Gtk.ProgressBar` construction anywhere), and a grep of PLANS.md and PLANS-DONE.md finds no entry carrying it.

**Approach and files.**

1. `tests/test_gtk4_theme.py`: add `TestGtk4Theme::test_progressbar_faces_render` beside `test_notebook_tab_faces_render`, the same shape: `require_gui_opt_in()` first (`tests/support/gui_tests.py`), then a child interpreter subprocess with `GDK_BACKEND=x11` and `GSK_RENDERER=cairo` that imports `gi` with `Gtk` 4.0 (exit 77 when introspection or an X11 display is missing, mapped by the parent to a skip naming what is missing), loads the shipped sheet's bytes into a `Gtk.CssProvider` at priority 801 with the `'../assets/'` URL rewrite the landed probes use, sets the stock theme name to Adwaita the way the notebook probe does, then builds a `Gtk.Window` holding one horizontal `Gtk.ProgressBar` at `set_fraction(0.5)` with `set_show_text(False)` — every pinned region sits clear of any text, so no font metric or glyph row becomes a fixture — plus a second bar at the same fraction whose parent carries the disabled state (`set_sensitive(False)`), pumps the main context until both bars are allocated, snapshots each bar's `trough` node (guarded with `assert trough.get_css_name() == "trough"`, the `progress` child likewise guarded, walking the node tree the way the landed probe guards its `header`) with `Gtk.WidgetPaintable`, renders it through `renderer.render_texture` into a pixbuf with the same deadline loop and failure reporting as the landed probe, and asserts each pinned pixel as a literal tuple at positions derived from the fresh node allocations (the trough node's allocation and the progress child's allocation), exactly as the notebook probe derives its tab positions. The plan states no absolute coordinates. Pin five discriminating bands, each derived so antialiasing edges stay clear: (a) one pixel inside the enabled bar's filled half's interior, away from every border and shadow arm, expecting `#CCCCFF` — so a lost or recoloured fill fails; (b) one pixel on the trough's top border row over the filled half, expecting `#000000` — so a lost trough border fails; (c) one pixel in the unfilled half just inside the top border, expecting the `#999999` inset shadow arm, and one pixel in the unfilled half's interior clear of the arm and borders, expecting the `#EEEEEE` trough face — so a dropped shadow arm or a recoloured face fails; (d) on the disabled bar, one pixel in its filled half's interior expecting `#999999` and one pixel in its unfilled half's interior expecting `#EEEEEE`, plus one pixel on its trough's top border row expecting full-strength `#000000` — so a restored stock translucency filter or a recoloured disabled fill fails; and (e) the relative pixel immediately below the enabled trough's bottom border row, outside the window, expecting the window's `#DDDDDD` surface — so a bar painting outside its bounds fails. Every expectation comes from the landed recipe and the palette constants already imported in `tests/test_gtk4_theme.py` (`TROUGH`, `BLACK`, `SELECTION` and the greys read from `support.platinum_palette` — re-grep the import list before writing and add only what is missing), never from a capture's own pixels. The probe imports no GTK in the suite process (the `tests/test_no_gtk_introspection.py` guard pins that) and mentions no brand or toolkit name.
2. `docs/invariants.md`: append one dated (2026-11-11) end-of-table `## gtk` row naming the new probe: a GTK 4 plain meter paints the landed trough, fill and disabled fill; recording the missing reference surface (no collected screenshot in `macos8.6-screenshots/` shows a GTK meter — the GTK scope's standing adaptation premise), the value sources (the sheet's landed `progressbar > trough`, `progressbar > trough > progress` and `:disabled` groups and the platinum palette constants), and that the probe runs under the opt-in guard through the child interpreter, establishing rendered pixels only where GTK 4 introspection and an X display are present, as the landed declaration rows never have.

**Files.** `tests/test_gtk4_theme.py` (one probe beside the landed rendered probes), `docs/invariants.md` (one appended end-of-table `## gtk` row). No sheet change, no production tool change, no render-harness change, and no other GTK 4 widget is touched.

**Acceptance criteria.**

- `make check` stays green where GTK 4 probes are not runnable: without `PLATINUM_RUN_GUI_TESTS=1` the new probe raises the same skip as the landed probes, and where GTK 4 introspection or a display is missing despite the opt-in, the child exits 77 and the probe skips with its own reason — the hosted job keeps today's behavior.
- Where GTK 4 introspection and an X display are present with `PLATINUM_RUN_GUI_TESTS=1`, the child completes and every pinned pixel reads its literal tuple: the enabled fill `#CCCCFF` and trough border `#000000`, the unfilled half's `#999999` shadow arm over the `#EEEEEE` face, the disabled bar's `#999999` fill with opaque faces and its border still `#000000`, and the window surface outside the bar `#DDDDDD`. Deleting or weakening any landed meter rule — the fill rule, the trough face, the inset shadow arm, or the disabled `filter: none` arm letting the stock translucency filter back in — changes at least one pinned pixel and fails the probe.
- The landed neighbouring probes (`test_notebook_tab_faces_render`, `test_spin_field_renders_the_mirrored_etch_in_rtl`, `test_mixed_indicators_draw_black_dashes`) and the meter declaration tests (`test_progressbar`, `test_progressbar_disabled_filter`, `test_disabled_meter_trough_faces`) pass unchanged, the no-GTK-in-suite guard passes, and `make check` passes after the final edit.

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
