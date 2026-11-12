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



### GTK 4 suite extraction, part 9/9: isolate calendar declarations (planned 2026-11-11 by the plan role; "requires part 1/9 landed")

**Goal.** Establish one complete declaration-surface suite alongside the probe moves; this part is independent of parts 2–8.

**Approach and files.** Move the declaration methods whose names start `test_calendar` from `TestGtk4Theme` into new `tests/test_gtk4_calendar.py::TestGtk4Calendar(Gtk4SheetRuleCases, unittest.TestCase)`, importing their constants from `support/gtk4_sheet.py` and existing palette/spec modules. Move `TestCalendarDisabledGreyReference` whole into that module with its reference imports. Preserve method bodies and class reference limits. Update the moved anchors in `docs/invariants.md`, prune unused original-module imports, and leave the scrollbar reference class and its calendar-color cross-check where they are. Keep the original module for the remaining surfaces; do not rewrite historical `PLANS-DONE.md` records or promise removal of every old path mention.

**Acceptance.** Calendar declaration and disabled-grey reference methods each appear once under the new module in discovery, retain their assertion bodies and reference coordinates, and pass or report the same missing-reference skip as before. Existing non-calendar tests remain discoverable. The invariants checker resolves the calendar anchors, and `make check` passes. No stylesheet or production behavior changes.

### README fidelity troubleshooting: distinguish mismatches from input refusals (planned 2026-11-11 by the plan role)

**Goal.** Give contributors a short corrective path when a comparison cannot run, alongside the existing aligned-crop and diagnostic-selection guides. This is independent of the waiting GTK 4 calendar extraction and pending scrollbar extraction.

**Approach and files.** Edit README.md only, outside the brief. Insert `### Troubleshooting a comparison` between Comparing a region and Choosing a diagnostic, and link it from the Fidelity checking introduction. Add a compact symptom/action table for an unmaterialized LFS pointer (link Validating the reference set), a missing or unreadable input (check the named path), missing JPEG `convert` (install ImageMagick and check PATH), a rejected PNG decode (inspect the named image and obtain a valid supported input), an out-of-image crop (correct that source's crop coordinates), and a size mismatch (choose corresponding equal-size regions using Comparing a region). Explain that a completed failing comparison returns 1 and should lead to Choosing a diagnostic; usage/read refusals return 2, while a passing comparison returns 0. Explain that `--quiet` suppresses comparison reports, so omit it to inspect a mismatch; retain the documented distinction between direct CLI statuses and Make's recipe-failure status. Do not advise raising thresholds as a repair for input errors. No runtime change or prose-pinning test is needed.

**Grounding.** `tools/fidelity.py::main` selects statuses and suppresses reports under `quiet`; `tools/fidelity_sources.py::read_source` dispatches PNG/JPEG loading; `tools/jpeg_convert.py::convert_jpeg` diagnoses missing ImageMagick; `tools/png/loader.py` names read/decode and LFS problems. `tools/fidelity_geometry.py::crop` rejects overflowing rectangles and `tools/fidelity_metrics.py::compare` rejects unequal dimensions. These are evidence anchors, not implementation targets. Archived README fidelity plans cover aligned crops, the report-selection table and its links, rather than this corrective guide; the existing render and sampler troubleshooting sections concern different CLIs.

**Acceptance criteria.** A reader encountering each listed symptom gets a concrete next action and a resolving link where another section supplies the procedure. A mismatch with status 1 is described as a completed comparison, distinct from status-2 refusals; removing `--quiet` is identified as the way to see its report. The guide directs size errors to equal-size corresponding crops without implying image resizing or threshold changes fix them. Existing comparison examples and diagnostic reference remain available. Run `make check` after the final edit; the existing `TestReadmeCommands` and `TestReadmeLinks` checks validate documented paths and local fragments without opening GUI windows.

### README fidelity chooser: expose distribution and channel tuning reports (planned 2026-11-11 by the plan role)

**Goal.** Help a contributor investigating palette drift choose the existing distribution and channel reports from the compact diagnostic table, rather than searching the long flag reference. This is independent of the waiting comparison-refusal guide.

**Approach and files.** Edit README.md only, outside the brief. Append four rows to `### Choosing a diagnostic`: distribution of error magnitudes (`--delta-histogram --json`), typical and tail error (`--delta-percentiles --json`), direction of channel drift (`--channel-bias --json`), and worst error per channel (`--channel-maxima --json`). Describe the visible results respectively as counts by maximum absolute RGBA delta, nearest-rank p50/p95/p99, signed mean candidate-minus-reference RGBA deltas, and per-channel maximum absolute deltas. Make each Need label link to a new standalone explicit anchor immediately before its existing explanation in Diagnostic reference: `fidelity-report-delta-histogram`, `fidelity-report-delta-percentiles`, `fidelity-report-channel-bias`, and `fidelity-report-channel-maxima`. Add a short note that these raw-byte diagnostics include zero and sub-tolerance errors where applicable, do not change the verdict, and that opposite signed errors can cancel in the bias. Preserve the existing six rows and their links. No runtime or invariant guarantee changes; no new prose-pinning test is needed.

**Grounding.** Inspected `tools/fidelity.py::main`, `tools/fidelity_pixels.py::delta_histogram`, `channel_bias`, `channel_maxima`, and `tools/fidelity_reports.py::delta_percentiles`: these reports already exist. README documents their flags in the detailed reference, but its chooser offers six other report choices. Archived plans for the compact chooser and its per-report links specify those six rows; the archived channel-maxima repair reunites its detailed explanation rather than exposing it in the chooser. `tests/test_readme_links.py::local_link_errors` recognizes explicit anchors; `TestReadmeLinks` and `tests/test_readme_commands.py::TestReadmeCommands` supply existing documentation checks. These code paths are evidence anchors, not implementation targets.

**Acceptance criteria.** A reader can select each of the four reports from the table, append its options to the existing aligned-crop command, and follow its link to the matching explanation. The table distinguishes a signed mean from an absolute maximum and identifies the histogram's grouping and percentile ranks without implying perceptual error or automatic threshold adjustment. Each option cell parses with `tools/fidelity_cli_parser.py::build_parser` using placeholder candidate/reference paths, without image reads or GUI activity. Existing diagnostic links still resolve. Run `make check` after the final edit.

## Done

### GTK 4 suite extraction, part 5/9: isolate the progressbar probe (planned 2026-11-11 by the plan role; "requires part 1/9 landed") — done 2026-11-11 by the review role

**Goal.** Give the progressbar rendered check its own small suite; sibling parts 2–8 move different probes and do not depend on each other.

**Approach and files.** Move only `TestGtk4Theme.test_progressbar_faces_render` from `tests/test_gtk4_theme.py` into new `tests/test_gtk4_progressbar_probe.py::TestGtk4ProgressbarProbe(unittest.TestCase)`. Import required constants from `support/gtk4_sheet.py` and palette/spec modules directly; do not import the original test module or inherit its test class. Preserve the complete method, including child-source string, opt-in guard, exit-77 handling, environment and timeout. Repoint the corresponding test anchors in `docs/invariants.md` in the same change; retain historical completed-plan records. Prune imports from the old module only when unused. The recursive guard in `tests/test_no_gtk_introspection.py` already covers new Python modules; no scanner extension is needed.

**Acceptance.** Discovery finds `test_progressbar_faces_render` once at the new dotted ID and no longer at the old one; its AST body and embedded child program match the original. Without GUI opt-in the moved probe skips, with no desktop window. The documented isolated Xvfb invocation, adapted to this new ID, either exercises the same assertions or reports the existing capability skip. The invariants checker resolves its moved anchors and `make check` passes. No probe-prelude extraction or pixel changes are part of this move.

**Completion and verification.** The probe moved intact to its standalone unittest class; the invariant anchor and isolated README invocation use the new ID. Focused unittest discovery without GUI opt-in found the new test and skipped before launching a child; the old module no longer defines it. The child source, environment, timeout and pixel assertions are unchanged. Xvfb is unavailable here, so the isolated render invocation was not executed; no new rendered-pixel verification is claimed. Tumwater owns the full project check.


### Reference-pixel sampler: select named colors in scanline runs (planned 2026-11-03 by the plan role) — done 2026-11-03 by the feature role

**Goal.** Isolate known border and stripe shades in a reference crop while retaining their separate equal-color runs. The current run report filters lengths, while named inclusion is limited to histograms; source and related finished-plan searches found no named run selection. This feature is independent of the waiting histogram plan.

**Approach and files.** Add repeatable `--run-color RRGGBB` in `tools/sample_arguments.py::build_parser`, destination `run_colors`, default None, using `tools/sample_validators.py::rgb_argument`. In `option_error`, immediately after the maximum-run-length dependency check, require `--runs` with diagnostic `--run-color requires --runs`. In `tools/sample_report_runs.py::_runs_result`, build a set of requested RGB tuples once and intersect membership with the existing length predicates on completed `_color_runs` records. Selection ignores opacity, but segmentation still uses RGB or RGBA according to `--alpha`; retain separate adjacent runs of different selected colors. Preserve the report schema, traversal order and absolute coordinates. Add `tests/test_sample_runs_colors.py` using `CliTestCase` and fixture patterns from `tests/test_sample_runs_max_length.py::TestSampleRunsMaximumLength`; extend `tests/test_sample_option_validation.py::TestSampleOptionValidation`. Document the flag beside the run length filters in README.md and amend the scanline-run row in docs/invariants.md. These six files form one bounded change of a few hundred lines including tests; decoding and search-mode diagnostics remain outside scope.

**Acceptance criteria.**
- For a crop at (2,1) containing successive pixels A,A,B,B,B,A,C,C, where A=`010203`, B=`090807`, C=`040506`, selecting A emits starts (2,1) and (7,1) with lengths 2 and 1. Selecting A and C also emits (8,1) with length 2, in scan order. Adding minimum length 2 removes the singleton A; maximum length 1 retains only that singleton. Omitted B never joins the A runs. Selecting adjacent distinct colors retains their individual run records.
- Repetition, lowercase and optional `#` give the same selection. An absent color yields JSON `runs: []` and text with image, region and axis lines but no run lines or added metadata. Selecting the complete crop palette matches the unfiltered report. Literal expected records cover an offset nonsquare rectangle in both axes, inferred single-column traversal, an explicit vertical singleton, crop-edge runs and equal colors on adjacent scanlines that remain separate. Text and JSON agree; direct-script and package invocations agree; omitting the flag retains existing fixtures.
- For adjacent RGBA pixels (1,2,3,0), (1,2,3,128), (4,5,6,255), selecting `010203` yields one length-2 run in RGB mode and two length-1 runs with their original alpha bytes in alpha mode. Minimum length 2 in alpha mode yields an empty list, proving segmentation precedes selection and length filtering. An RGB-only fixture reports alpha 255 when requested.
- Missing and malformed values exit 2 with empty stdout. Valid use outside runs mode, including ordinary samples, histogram and find-color modes, exits 2 with `--run-color requires --runs` before image access; guard `os.open`, `read_png_size` and `read_png` in validation tests. Earlier incompatible-option diagnostics retain precedence. Help lists the repeatable option and the absent parser default is None. Run `make check` after final edits.

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
