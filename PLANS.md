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

### File-dialog content faces, part 1/2: pin the list panel's header band, file rows and type-icon cells in `TestFileDialogRender` (planned 2026-11-11 by the plan role; independent of the waiting splash plumbing entry — that entry edits `tools/render_surface.py`, `tools/render_clients.py`, `tools/render_workflow.py` and the `Makefile`, the unit/mode/CI/failure-path suites beside `TestFailurePaths`, README's prerequisites and capture-enumeration prose, and appends its own `## tooling` row, while this entry only extends `tests/test_render_surface.py`'s `TestFileDialogRender` beside its landed tests, rewords the one closing sentence of README's `--file-dialog` paragraph and amends the `--file-dialog` gate row in `docs/invariants.md` — no test method, production function or README sentence is shared, though both entries append at the `## tooling` table's end and write into the `### Capturing a candidate` section, so whichever merges later re-reads the table tail and the section before writing; at implementation re-grep every anchor this entry names; the places sidebar's entries, group headers and capacity bars are the later part 2/2 a later plan writes, which will spell its dependency on this part in the quoted landed-clause form the claim allocator reads)

**Goal.** The landed `TestFileDialogRender` gate pins the chooser's frame, title-bar bands and boxes, panels, selected places row, fields and toolbar/bottom buttons, but leaves the list panel's column-header band, the three file rows and their per-file type icons unpinned — README's `--file-dialog` paragraph and the gate's `## tooling` row both record them as deliberately unpinned, and the landed plumbing entry warned part 2/2 to keep its crops off the icon cells. So today a regression that recolours the alternate-row trough, drops a column divider, shifts a type-icon cell one pixel, loses the sort arrow or paints art into the empty rows passes every landed test. This entry pins those faces, byte-pinning the type-icon cells and the style-drawn sort arrow as measured (the landed window-icon box's precedent), while the caption glyphs, the file names and the clock-dependent date column stay live ink.

**Grounding (measured fresh 2026-11-11 by the plan role: two consecutive full `python3 tools/render_surface.py <scratch>/f1.png --file-dialog` and `f2.png` runs on this host, both exit 0, both 480x360, differing in exactly the 16 caret-strip pixels the landed record names — x=200, y=267..282 — so every region below is run-stable).** The list panel spans x=147..473; its content sits right of the landed scrollbar-strip exclusion x=147..151, rows 96..253 (app widget content, not theme art — it stays excluded). The column-header band rows 99..120 draws face `#dddddd` with two full-height `#000000` column dividers at x=343 and x=393 (measured rows 99..120 black at both, row 121 `#aaaaaa` and row 122 `#000000`); the captions ink rows 105..114 — "Name" x≈155..187, "Size" x≈348..370, "Date" x≈399..424 — and the sort arrow is a small solid `#000000` triangle x≈329..337, rows 106..113, drawn by the style, so it is pinnable as measured. Below the band the list field's top edge runs row 121 `#aaaaaa` and row 122 `#000000` across x=152..473 (the client frame's own outline at x=474 is already pinned). The three seeded file rows: rows 123..142 face `#FFFFFF`, rows 143..162 face `#EEEEEE` (the alternate-row trough), rows 163..182 `#FFFFFF`; the type icons draw inside measured cells — row 1 x=173..182, y=126..138; row 2 x=173..182, y=146..158; row 3 x=172..183, y=167..178, the RTF entry's distinct glyph; the name text inks x≈191..241, the size text x≈367..385 ("0 B", stable), and the date text x≈398..471 — the seeded files' modification times are the render session's wall clock, so the date column's ink band x=395..473 stays live-only like the caret (a run on another day or minute inks different digits there); the empty rows 183..251 are flat `#FFFFFF`. Every ink bounding box above is measured over all non-face pixels, so antialiased edges stay inside them.

**Approach.**

1. First re-verify stability the landed gates' way: two consecutive full `--file-dialog` renders on this host must differ only inside the caret strip; re-derive every region from the fresh capture — a value the fresh pair disagrees on is unpinnable: record it, never pin it, and note the re-derivation in the test comments.
2. `tests/test_render_surface.py`: extend `TestFileDialogRender` beside its landed tests (extend the class docstring's pin inventory), each test quoting the measured values in comments with the two-run provenance:
   - `test_the_column_header_band_pins_its_face_and_dividers`: rows 99..120, x=152..473 `#DDDDDD` except the divider columns x=343 and x=393 `#000000` for rows 99..120 and the measured caption/arrow ink bands — a lost divider or a recoloured header face fails here.
   - `test_the_header_inks_its_captions_and_sort_arrow`: live ink (at least one pixel darker than `#DDDDDD`) inside each caption band, and the sort arrow byte-compared to its measured pixel map (x=329..337, rows 106..113) — a dropped, moved or resampled arrow fails here.
   - `test_the_list_rows_pin_their_band_faces`: rows 123..142 and 163..182 `#FFFFFF`, rows 143..162 `#EEEEEE`, and rows 183..251 flat `#FFFFFF`, each across x=152..473 except the measured icon and text ink regions — and the date band x=395..473 excluded from exactness with live ink demanded instead — a lost alternate-row trough or stray art in the empty rows fails here.
   - `test_the_file_rows_draw_their_type_icons`: the three icon cells byte-compared to measured row maps in the landed `ICON_BOX_ROWS` shape, at offsets (173, 126), (173, 146) and (172, 167) — a shifted cell, a dropped icon or a resampled glyph fails here.
   - `test_the_file_rows_ink_their_columns`: at least one dark pixel inside each row's name, size and date bands — a dropped listing or an empty date cell fails here.
3. `README.md`: reword the `--file-dialog` paragraph's closing sentence ("the chooser's per-file type icons are the fallback icon theme's and stay deliberately unpinned") to name the landed pin — the gate pins the header band, dividers, sort arrow, row faces and each type-icon cell as measured, while the caption glyphs, the file names and the clock-dependent date column stay live ink and the icon art remains the fallback icon theme's. Re-read the section before writing (the splash entry also extends it elsewhere).
4. `docs/invariants.md`: amend the `--file-dialog` gate row — extend its pinned-regions prose with the header band, dividers, sort arrow, row faces, icon cells and empty rows, and shrink its exclusion sentence: the icon art stays unpinned but the cells are now pinned as measured, the date text band x=395..473 joins the caret strip as a clock-dependent exclusion (the seeded files' mtime display follows the wall clock), and the scrollbar strip stays excluded; record the fresh two-run provenance dated 2026-11-11. No gate count or kdialog-mode count word moves.

**Files.** `tests/test_render_surface.py`, `README.md`, `docs/invariants.md`. No production tool, render plumbing or Makefile change, and no new render mode, flag or `KINDS` entry.

**Acceptance criteria.**

- On this host the fresh two-render pair differs only inside the caret strip, `TestFileDialogRender`'s new tests pass under `make check`'s gate pass against the same pooled capture the landed tests read, and a third render's pinned regions compare equal to the first's.
- A regression that drops a column divider, flattens the `#EEEEEE` trough, shifts an icon cell one pixel, drops the sort arrow or paints art into the empty rows fails the corresponding new test (each byte-compare and band scan names the region it kills).
- README's `--file-dialog` paragraph names the landed pin, the amended `## tooling` row records the new regions, the amended exclusions with reasons and the 2026-11-11 two-run provenance, and `make check` passes after the final edit.

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
