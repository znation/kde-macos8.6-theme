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

### File-dialog render mode, part 1/2: plumb a `--file-dialog` kdialog file-chooser capture through the render CLI, workflow and Makefile (planned 2026-11-11 by the plan role; part 1 of a two-part series — part 2/2 will add the rendered-pixel gate for the captured file dialog's surfaces to `tests/test_render_surface.py` and will be planned once this part lands, its heading naming this part as its landed prerequisite in the allocator's clause form, so this part lands mergeable on its own; independent of the waiting inactive-window part 2/2 entry — that entry edits `tests/test_render_surface.py`'s gate scaffolding, `tests/test_dialog_gate_count_prose.py`, `tests/test_ci_workflow.py`, README's dialog-gate enumeration and `docs/invariants.md` and touches no production tool, while this part edits the shared dialog plumbing (`tools/render_clients.py`, `tools/render_dialogs.py`, `tools/render_workflow.py`, `tools/render_surface.py`), the `Makefile`, the table and CLI unit suites and README's dialog-mode enumeration — the README sentences the two entries extend are different lists (dialog modes vs dialog gates), so whichever merge order holds, the second re-reads both enumerations before extending them; at implementation re-grep every anchor this part names)

**Goal.** The thirteen landed dialog modes cover kdialog's widget palette — buttons, indicators, lists, calendar, colors, sliders, text boxes — but never KDE's file dialog: `kdialog --getopenfilename` opens the native KIO file chooser whose places sidebar, file list view, toolbar and name-filter surfaces are Kvantum- and colorscheme-painted widgets no other render mode reaches (grepped `PLANS.md ## Planned`, `PLANS-DONE.md`, `BUGS.md`, `BUGS-FIXED.md` and `tools/` for `getopenfilename`, `file-dialog` and `KFileDialog`: no entry, test or tool names them; `kdialog --help` on this host lists `--getopenfilename`). This part adds the mode and its capture plumbing; the pixel gate is part 2/2's deliverable, so this part carries no assertion against capture pixels.

**Grounding (code-level, verified 2026-11-11).** `tools/render_dialogs.py::DIALOG_MODES` declares one `DialogMode(attr, flag, help, client, client_tool)` per mode and is the single source the CLI parser (`tools/render_surface.py` builds one `--*-dialog` flag per entry into its `dialog_flags` mutual-exclusion list), the required-tools preflight (`dialog_clients` collects each mode's `client_tool`) and the workflow dispatch (`tools/render_workflow.py::_client_command` and `_select_dialog_theme`) all read. `tools/render_clients.py` holds one factory per mode; the landed `inactive_dialog_client(session)` shows the factory receives the `Session` (fields `root`, `config`, `data`, `home` at `tools/render_session.py::Session`) and the landed `checkbox_dialog_client` already reads scratch paths. `tests/test_render_dialogs.py` pins the table whole (the flag tuple, the attribute derivation, the factory pairing), `tests/test_render_make.py` pins `Makefile`'s `RENDER_MODE_VALUES` against `DIALOG_MODES`, and `tests/test_render_surface_units.py` pins the CLI delegation cases beside the landed line-edit ones.

**Approach.**

1. `tools/render_clients.py`: add `file_dialog_client(session)` beside `inactive_dialog_client`. The factory creates the fixed scratch directory `session.home / "Documents"` (mkdir with `exist_ok=True`) holding exactly three fixed empty files — `alpha.txt`, `bravo.txt`, `delta.rtf` — and returns `("kdialog", "--title", "Test", "--getopenfilename", str(that directory))` with no filter argument. Its docstring records the determinism rationale (a fresh scratch session with fixed filenames, no clock-dependent content, no directory the caller's disk can vary) and the warning the icon gate's factory carries: the per-file type icons the chooser draws are the fallback icon theme's, not theme-owned art, so part 2/2's gate must keep its crops off icon cells the way `TestIconDialogRender`'s bands do. The directory and its three files are the factory's side effect, pinned by the unit test in step 5.
2. `tools/render_dialogs.py`: import `file_dialog_client` in both import blocks and append the fourteenth `DialogMode` entry at the end of `DIALOG_MODES`, after `inactive`: attr `file_dialog`, flag `--file-dialog`, help text naming the KIO file chooser capture at the 480x360 size in the established phrasing, client `file_dialog_client`, `client_tool` `kdialog`, `extra_config_files` empty like every one-window mode.
3. `tools/render_workflow.py`: the dispatch reads `DIALOG_MODES`, so no workflow code changes beyond confirming nothing keys on a literal mode list (re-grep the file for `inactive`/`menu_dialog`-style literals; extend anything found). `tools/render_surface.py`: the parser builds flags from the table, so extend only the module docstring's mode list (lines 18–22) with `--file-dialog` and confirm the `dialog_flags`/`kdialog` naming paths stay table-driven (re-grep; extend any literal list found).
4. `Makefile`: append `file-dialog` to `RENDER_MODE_VALUES`, add the `file-dialog) set -- --file-dialog ;;` case beside `inactive-dialog`'s, and confirm both enumeration error strings that name the mode list still spell the full set (the `RENDER_MODE must be one of` diagnostic and its twin).
5. Tests: `tests/test_render_dialogs.py` gains `"--file-dialog"` in the whole-table flag tuple, the factory in the pairing tuple and the tool tuple as the landed whole-table pins require, and its module docstring moves thirteen→fourteen dialog modes. `tests/test_render_surface_units.py` adds cases beside the landed line-edit ones modeled on `test_cli_delegates_the_lineedit_dialog_capture_size` and `test_rejects_an_applet_with_the_lineedit_dialog`: `--file-dialog` delegates at the fixed 480x360 dialog capture size, refuses `--applet` with the established diagnostic, is mutually exclusive with every other dialog flag, names `kdialog` in the missing-tool diagnostic, `--help` names the mode, and the factory creates exactly `Documents` with exactly the three fixed files and returns the argv of step 1 (a seventh file, a different name set or a different directory is a failure).
6. `README.md`: extend the `## Rendering a candidate` section's dialog-mode command list with one `--file-dialog` example line and add one per-mode paragraph beside the landed ones (after the `--inactive-dialog` paragraph, whichever paragraph the tail then ends with — re-read the tail before writing) naming what the capture opens and that its surfaces await the part 2/2 gate. No `docs/invariants.md` row in this part: the precedent split (the landed radiolist part 1/2) carries the tooling row with the part 2/2 gate row.

**Files.** `tools/render_clients.py`, `tools/render_dialogs.py`, `tools/render_surface.py` (help text and any literal list found), `tools/render_workflow.py` (only if the re-grep finds a literal), `Makefile`, `tests/test_render_dialogs.py`, `tests/test_render_surface_units.py`, `README.md`. No gate scaffolding: `tests/test_render_surface.py`, `tests/test_ci_workflow.py`, `tests/test_dialog_gate_count_prose.py` and `docs/invariants.md` stay untouched.

**Acceptance criteria.**

- On this host `python3 tools/render_surface.py <scratch>/file.png --file-dialog` opens the kdialog file chooser rooted at the scratch `Documents` directory holding exactly `alpha.txt`, `bravo.txt` and `delta.rtf`, captures a 480x360 PNG and exits 0; the scratch directory and its three files exist only under the session root, never beside the caller's tree.
- The preflight refuses a `--file-dialog` run with `kdialog` absent (exit 2, diagnostic naming `kdialog`) before any session, and refuses combining `--file-dialog` with any other `--*-dialog` flag, with `--applet`, or with `--width`/`--height` overrides using the landed diagnostics' shape.
- The whole-table pins pass with fourteen modes in `DIALOG_MODES`; `tests/test_render_make.py`'s `RENDER_MODE_VALUES` pin passes against the extended `Makefile` list and case; `make render RENDER_MODE=file-dialog` routes to the same capture; README's command list and per-mode paragraph name the mode; `make check` passes after the final edit.

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
