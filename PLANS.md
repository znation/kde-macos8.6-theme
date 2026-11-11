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

_None yet._

### Desktop render gate, part 2/2: pin the rendered menu bar's structure in `TestDesktopRender` (planned 2026-11-11 by the plan role; completes the two-part series whose part 1/2 landed 2026-11-11 — the landed part plumbed the `--desktop` plasmashell capture and recorded the capture's mechanism, size and settle in the `## tooling` invariants row, and no allocator dependency clause remains because the prerequisite is in `## Done`; independent of the waiting cursor-alias entry — that entry edits `tools/cursor_art.py`, the regenerated `theme/icons/org.macos8.desktop/cursors/` files, `tests/test_cursors_theme.py`, README's pointer-set paragraph and the `## icons` cursor row, while this entry edits `tests/test_render_surface.py`'s gate scaffolding, README's `## Rendering a candidate` render prose and the `## tooling` desktop row, so the two share no test, no anchor and only incidental file overlap in README and `docs/invariants.md`, whose touched paragraphs and rows are disjoint — whichever merge order holds, the second re-reads both before extending; at implementation re-grep every anchor this entry names)

**Goal.** The landed `--desktop` render publishes the 640x400 capture of the theme's own menu bar but pins none of its pixels: the landed `## tooling` row's closing sentence leaves the menu-bar rows and the desktop area below the bar unpinned until this gate lands, so a regression that recolours the bar's face, drops the `#999999`/`#000000` bottom rules, flattens the white top row or disturbs the desktop area below would pass every landed test. This part adds the gate, keeping every dynamic region out of the pins.

**Grounding (measured fresh 2026-11-11 by the plan role: two consecutive full `python3 tools/render_surface.py <scratch>/desktop.png --desktop` runs on this host, both exit 0, both 640x400 PNGs).** The two captures differ in exactly 162 pixels, all inside x=401..479, y=4..14 — the `org.kde.plasma.digitalclock` digits — so every bar pixel left of x=359 (the tray icons begin at x=359) and the rules and desktop area below are run-stable. The bar occupies rows 0..19 and its measured structure is: row 0 all `#ffffff`; rows 1, 2 and 17 all `#dddddd` with no ink anywhere in the width; the bar's leftmost mark draws as a 14x10 raised box at x=3..16, y=3..12 — a 1px `#000000` outline rectangle, a white `#ffffff` top/left inner bevel (row 4 spanning x=4..14 and column x=4 spanning rows 4..10), a `#999999` bottom/right inner shadow (column x=15 rows 4..10 and row 11 spanning x=4..15) and a flat `#dddddd` interior (x=5..14, y=5..10) — plasma's rendering of the bar's leftmost mark, pinned at the pixel level whatever scale or crop plasma applies to the shipped `start-here-kde-symbolic` source; the corridor x=17..358, y=1..17 is entirely `#dddddd` (empty app-menu and panel-spacer area, zero dirty pixels); the bottom rules hold row 18 `#999999` for x=0..513 and `#9a9a9a` for x=514..639 and row 19 `#000000` for x=0..513 and `#020202` for x=514..639 (the 126-column tail's one-shade lighter pair measured identical in both runs); and rows 20..399 are flat `#cccccc` full width with zero dirty pixels, so the wallpaper stays out of the series as part 1/2 recorded. The bar's right half (x=359..639, rows 3..16) holds the tray icons, the clock digits and the shell label and is deliberately unpinned: the two-run diff confines its movement to the digits, and the tray and label pixels change with session state. These are session-measured platform values (plasmashell on this host, 2026-11-11) no reference screenshot shows.

**Approach.**

1. First re-verify stability: run two consecutive full `--desktop` renders on this host and compare every pixel; require every differing pixel to lie inside x=359..639 (measured 2026-11-11: x=401..479, y=4..14, the clock digits) — a difference outside the excluded right half means an unstable value: stop and re-derive every region from the fresh capture, never pin an unstable one, and record the re-derivation in the test comments.
2. `tests/test_render_surface.py`: append `("desktop", ("--desktop",), "desktop.png")` to `_Renders.KINDS` after the `"inactive"` entry, and add `class TestDesktopRender(unittest.TestCase)` beside the gate classes with its own `setUpClass` waiting on `_Renders.ensure("desktop")` and reading the capture through the module's `read_png` helper — a plain gate, not a `_DialogGate` subclass, because the capture is 640x400 into `desktop.png`, not the shared 480x360 `dialog.png`, and the desktop is not a dialog mode so no dialog count word moves. Extend the gate-guard scaffolding so the desktop gate skips where its tools are missing or Mesa is forced onto a software driver, mirroring `_dialog_gate_guard`'s attribute-writing shape (either a parameterized variant of that helper or a sibling `_desktop_gate_guard`); the guarded tool set is the set the landed desktop preflight checks for the mode — the session tools plus `plasmashell`, not `kdialog`/`zenity`/`plasmawindowed` — and the skip reason names `plasmashell`.
3. `TestDesktopRender`'s tests, each reading the capture through its `candidate_image` helper and quoting the measured values in comments with the two-run provenance:
   - `test_exits_zero_and_writes_a_640x400_png`: returncode 0 and the image is 640x400.
   - `test_bar_rows_pin_the_platinum_structure`: row 0 all `#ffffff`; rows 1, 2 and 17 all `#dddddd`; row 18 `#999999` for x=0..513 and `#9a9a9a` for x=514..639; row 19 `#000000` for x=0..513 and `#020202` for x=514..639; rows 20..399 all `#cccccc` full width — the white top row, the face rows, the two bottom rules and the flat desktop area below.
   - `test_left_mark_is_the_raised_box`: the exact measured pixel map of x=3..16, y=3..12 (black outline rectangle, white top/left inner bevel, `#999999` bottom/right inner shadow, `#dddddd` interior as itemized in the grounding) — a moved, resized or restyled leftmost mark fails here.
   - `test_the_bar_between_the_mark_and_the_right_half_is_empty`: every pixel of x=17..358, y=1..17 equals `#dddddd` — this kills stray art, a dropped face row or a bevel bleeding into the empty app-menu area.
   - `test_the_right_half_draws_its_live_content`: x=359..639, rows 3..16 hold at least one non-`#dddddd` pixel — the excluded region must really carry the tray icons, clock digits and shell label, or the exclusion would hide a bar that painted nothing (mirrors the inactive gate's two-state check).
4. `README.md`: one sentence in the `## Rendering a candidate` desktop paragraph (beside the landed `--desktop` prose) naming the gate that now pins the capture — check the tail of the section before writing, since the landed file-dialog part 1/2 also extended it.
5. `docs/invariants.md`: in the `## tooling` desktop row (the landed part 1/2 row), replace the closing "This part ships no pixel gate … until the queued part 2/2 gate lands" sentence with the gate's landed record: the pinned structure, the two-run comparison whose differences stayed inside the excluded right half, the exclusion rationale (tray icons, wall-clock digits, shell label), and the session-measured provenance dated 2026-11-11. No count-bearing row moves: the desktop gate is not a dialog gate, so the thirteen-gates and twelve/thirteen-kdialog-mode counts stay as they are.

**Files.** `tests/test_render_surface.py` (`_Renders.KINDS`, the guard helper, `TestDesktopRender`), `README.md` (one sentence), `docs/invariants.md` (one row's closing sentences). No production tool changes: `tools/render_surface.py`, `tools/render_workflow.py`, `tools/render_setup.py` and the `Makefile` stay untouched; no dialog-mode count prose (`tests/test_render_dialogs.py`, `tests/test_dialog_gate_count_prose.py`) moves because the desktop is not a dialog mode.

**Acceptance criteria.**

- On this host `tests/test_render_surface.py::TestDesktopRender` runs under `make check`'s gate pass: it renders `--desktop` at the fixed 640x400 defaults, exits 0, and its five region tests pass against the pinned values; at implementation the two-run comparison shows every differing pixel inside x=359..639, and a third render's pinned regions compare equal to the first's.
- A host missing any required desktop tool or running Mesa on a software driver skips `TestDesktopRender` with the shared skip-guard shape (attributes written even when not skipping); every landed gate class, its unit tests and the count-prose tests compare unchanged.
- README's render prose names the desktop gate, the `## tooling` desktop row no longer leaves the bar unpinned and records the gate's provenance, and `make check` passes after the final edit.

## Done

### Fidelity CLI: extract parser construction from comparison orchestration (planned 2026-11-02 by the plan role) — done 2026-11-11 by the feature role

**Goal and grounding.** Make the fidelity entry point readable as a comparison workflow. `tools/fidelity.py::main` currently starts with parser construction and a nested `worst_pixel_limit` validator before it reads images. `tools/fidelity_arguments.py` already owns the other argument validators. The finished report-extraction plan deliberately retained parser setup in the entry point; heading searches found no separate parser-extraction plan. This maintenance task is independent of the queued sampler work.

**Approach and files.** Create `tools/fidelity_cli_parser.py::build_parser`, moving the existing `EscapingArgumentParser` construction and option declarations there without changing their order, help strings, defaults, destinations or types. Move `worst_pixel_limit` to `tools/fidelity_arguments.py` and import the validators into the new parser module. In `tools/fidelity.py::main`, replace the construction block with `build_parser().parse_args(argv)` and remove imports made unused by the move. Support package imports and direct-script execution using the existing conditional import pattern. Keep image reads, crop application, optional diagnostic scans and reporting in their current owners. Inspect repository references to validators imported through `tools.fidelity` before removing those imports; preserve an existing consumer's import path if needed. Bound the change to those three production files and a new `tests/test_fidelity_cli_parser.py`; adjust ownership docstrings in the touched files. No CLI behavior change or new dependency is intended.

**Acceptance criteria.** Before moving declarations, capture characterization fixtures in the new test module for normalized help text and parsed default/explicit namespaces, including both crops, diagnostic switches and combined budgets. The same fixtures pass after extraction. Use the existing unittest framework to verify two independently constructed parsers work, malformed crop/budget/worst-pixel arguments retain status 2 and escaped diagnostics, and help and invalid arguments do not call `tools/fidelity.py::_read_source`. Existing fidelity CLI, JSON, crop and direct-script tests continue to pass. Run `make check` after final edits. This structural change adds no guarantee to docs/invariants.md; its existing tooling contracts remain the acceptance boundary.

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
