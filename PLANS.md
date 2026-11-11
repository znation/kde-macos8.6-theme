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

### Fidelity CLI: refuse contradictory min/max mismatch-run filter windows and rewrite the empty-result fixtures (planned 2026-11-11 by the plan role; independent of the waiting GTK 3 menu scroll-arrow entry — that entry touches the GTK 3 sheet, `tests/test_gtk_theme_views.py` and an appended `## gtk` row of `docs/invariants.md`, while this entry touches `tools/fidelity.py`, five fidelity test modules and the `## tooling` rows of `docs/invariants.md`, so no file, test or invariants row is shared and either merge order leaves all working — at implementation re-grep every anchor this entry names)

**Goal.** The sampler refuses a minimum above its paired maximum before any image read — the user answered the 2026-11-11 QUESTIONS.md fork with "option 2, refuse", and the landed sampler change gave all five sampler pairs the diagnostic — but the fidelity CLI's two length-filter pairs still accept a contradictory window and exit 0 with an empty list: `--min-difference-run-length 3 --max-difference-run-length 2 --difference-runs --json` prints `"difference_runs": []` beside a full `difference_run_count` and the full comparison's metrics, indistinguishable from a genuine no-mismatch measurement. A typo'd window looks like a real measurement, exactly the shape the sampler's refusal exists to kill. The fidelity validation block already refuses misleading combinations before image reads (`--min-difference-run-length requires --difference-runs` and its siblings); the cross-check is the one missing member of that family. No queued or archived entry covers it (grepped PLANS.md, PLANS-DONE.md, BUGS.md for `must not exceed`, `contradict` and the fidelity pair names).

**Grounding (verified fresh 2026-11-11).** `tools/fidelity.py::main`'s validation block (the nine `parser.error` checks before `_read_source`, ~lines 96–105) carries only per-flag `requires`/`requires-cap` checks; `grep -rn "must not exceed" tools/fidelity.py tools/fidelity_cli_parser.py tools/fidelity_arguments.py` finds nothing. The landed sampler shape is `tools/sample_arguments.py::option_error` (the `must not exceed` arms at the color-count, color-fraction, run-length, match-run-length and match-column-run-length pairs), wording `--min-run-length must not exceed --max-run-length (3 > 2)`, placed after that pair's own `requires` checks. Four test sites use the contradictory window as their empty fixture: `tests/test_fidelity_difference_runs_max_length.py` (min 3 / max 2 on the 9x2 `difference_pair(9, 2, ({0,2,3,5,6,7}, {0,1,2,3,8}), vertical=False)` fixture whose runs are lengths 1,2,3,4,1 — longest 4), `tests/test_fidelity_difference_runs_limit.py` (min 3 / max 2 / cap 1, same fixture), `tests/test_fidelity_column_runs_max_length.py` (min 3 / max 2 on the `difference_pair(2, 9, ({0,2,3,5,6,7}, {0,1,2,3,8}), vertical=True)` fixture whose longest column run is 3) and `tests/test_fidelity_run_count.py` (min 4 / max 1 on its 4x3 fixture whose runs are lengths 2,1,4). `tests/test_fidelity_column_runs_limit.py` already uses the legal empty window (min 9, above every run), the rewrite's shape.

**Approach.**

1. `tools/fidelity.py::main`: insert two checks mirroring the sampler's placement and wording, each immediately after that pair's second `requires` check:
   - after the `--max-difference-run-length requires --difference-runs` check (before the `--max-difference-runs` check): `if args.min_difference_run_length is not None and args.max_difference_run_length is not None and args.min_difference_run_length > args.max_difference_run_length: parser.error(f"--min-difference-run-length must not exceed --max-difference-run-length ({args.min_difference_run_length} > {args.max_difference_run_length})")`;
   - the column twin after the `--max-difference-column-run-length requires --difference-column-runs` check, with the `--min-difference-column-run-length` / `--max-difference-column-run-length` names in the diagnostic.
   Nothing else in the block changes, so a contradictory window without `--difference-runs` (or without `--difference-column-runs`) still reports the pre-existing `requires` diagnostic, exactly as the landed sampler refusal reports `requires` first when the mode flag is missing.
2. Rewrite the four contradictory fixtures to legal empty windows, the landed sampler rewrite's shape — a minimum above the fixture's longest run, with any paired maximum kept at or above the minimum and any cap or offset context kept: `test_fidelity_difference_runs_max_length.py`'s `empty` case becomes min 5 / max 9; `test_fidelity_difference_runs_limit.py`'s `conflict` case becomes min 5 / max 9 / cap 1; `test_fidelity_column_runs_max_length.py`'s `contradictory` case becomes min 4 / max 9; `test_fidelity_run_count.py`'s `conflict` invocation becomes min 5 / max 9. Every assertion at each site stays as written (empty list, full-scan `longest_difference_run`/`difference_run_count`, unchanged metrics and `passed`); rename no test.
3. Add `tests/test_fidelity_option_validation.py` beside `tests/test_sample_option_validation.py`'s refusal class, built on `support.fidelity_cli_case.FidelityCliTestCase` like the per-flag modules: with `mock.patch.object(fidelity, "_read_source", side_effect=AssertionError("read"))` and `missing.png`/`missing.png` invocations (the `tests/test_fidelity_difference_runs_max_length.py::test_dependency_and_invalid_lengths_are_usage_errors_before_read` pattern), both contradictory windows exit 2 with empty stdout and the exact two diagnostics above; both equal-window invocations (min 2 / max 2 with the required list flag) exit 0 and reach the image read — the row a `>=` mutation fails; a contradictory horizontal window without `--difference-runs` reports the `requires` diagnostic first; direct-script and package invocations agree.
4. `README.md`'s fidelity section: beside the `--min-difference-run-length` / `--max-difference-run-length` sentences (the "Pass `--min-difference-run-length N` with `--difference-runs` …" paragraphs and the vertical twins) add one sentence per pair stating that a minimum above its paired maximum is refused with a diagnostic naming both flags and both values before any image read.
5. `docs/invariants.md` `## tooling` rows: extend the four rows — the minimum and maximum horizontal mismatch-run length rows (`tests/test_fidelity_difference_runs_min_length.py`, `tests/test_fidelity_difference_runs_max_length.py`) and the minimum and maximum vertical mismatch-run length rows (the column-run pair's rows) — each with "a minimum above its paired maximum is refused before image reads (added 2026-11-11 by the feature role)", the landed sampler amendment's clause wording, and cite `tests/test_fidelity_option_validation.py` in each row's test column.

**Files.** `tools/fidelity.py`, `tests/test_fidelity_option_validation.py` (new), `tests/test_fidelity_difference_runs_max_length.py`, `tests/test_fidelity_difference_runs_limit.py`, `tests/test_fidelity_column_runs_max_length.py`, `tests/test_fidelity_run_count.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**

- `tools/fidelity.py a.png b.png --difference-runs --min-difference-run-length 3 --max-difference-run-length 2` exits 2 with empty stdout and prints `--min-difference-run-length must not exceed --max-difference-run-length (3 > 2)`; the vertical twin prints `--min-difference-column-run-length must not exceed --max-difference-column-run-length (3 > 2)`; both failures happen before any image read; without `--difference-runs` (respectively `--difference-column-runs`) a contradictory window still reports the pre-existing `requires` diagnostic; min 2 / max 2 still runs the comparison.
- The rewritten fixtures keep every assertion as written under the legal windows (empty list, full-scan count, unchanged metrics, unchanged `passed`); `tests/test_fidelity_option_validation.py::TestFidelityOptionValidation` passes and fails on a `>`→`>=` mutation, a swapped pair name in a diagnostic, or a removed check; the per-flag modules' existing usage-error rows pass unchanged.
- README carries one refusal sentence per pair; the four `## tooling` rows carry the added clause and name the new test module; `make check` passes after the final edit.

### Fidelity CLI: read JPEG candidate and reference screenshots through the landed sampler convert bridge (planned 2026-11-11 by the plan role; independent of the waiting fidelity min/max-refusal entry — that entry edits `tools/fidelity.py::main`'s validation block, the four existing fidelity fixture-window modules and the new `tests/test_fidelity_option_validation.py`, while this entry edits `tools/fidelity_sources.py::read_source`, adds `tests/test_fidelity_jpeg.py`, and touches only README's `## Fidelity checking` section and one appended `docs/invariants.md` `## tooling` row, so the two share no production function, no test module and no assertion and either merge order leaves all working — at implementation re-grep every anchor this entry names)

**Goal.** The fidelity CLI is the tool an operator points at the reference set to measure a rendered surface, but it still refuses every non-PNG reference: `python3 tools/fidelity.py render.png macos8.6-screenshots/opendialog_macrumors86.jpg` exits 2 with `fidelity: error: cannot decode macos8.6-screenshots/opendialog_macrumors86.jpg: not a PNG file: the input is a JPEG image, not a PNG; convert it to PNG first` (verified fresh 2026-11-11). The reference set carries JPEG screenshots (`opendialog_macrumors86.jpg`, `apps_macrumors8.6.jpg`, `boot_powerbookphoto_macrumors.jpg`, `desktop_archiveorg.jpg`) whose widget recipes the GTK plans cite, so measuring against them needs a manual `convert` round-trip whose output path and cleanup the operator nurses by hand — exactly the friction the landed sampler JPEG plan (PLANS-DONE.md, "Sample JPEG screenshots directly", 2026-11-10) removed for `tools/sample.py` and explicitly scoped out of the fidelity CLI ("No change to `tools/fidelity.py`; this plan covers the sampler only"). Grep of PLANS.md, PLANS-DONE.md, BUGS.md and BUGS-FIXED.md for fidelity-and-JPEG coverage finds no other entry carrying it.

**Grounding (verified fresh 2026-11-11).** `tools/fidelity_sources.py::read_source` is the single source loader for both comparison sides (`tools/fidelity.py` imports it as `_read_source`, package and direct-script branches; the pre-read validation spies in `tests/test_fidelity_column_runs_limit.py` and siblings patch `fidelity._read_source` at that boundary). It calls `tools.containment.require_within_repo` then `read_png(path, alpha=True)` with a `max_rows` bound from the crop and a sideways-overflow retry — PNG only. The landed bridge is reusable as-is: `tools/jpeg_convert.py::is_jpeg`/`convert_jpeg` (supervised `convert jpeg:- PNG24:<temp>` through `tools.process_group.py::run_logged_split`, `shutil.which` for the tool, diagnostic returned as a problem string), and `tests/support/jpeg_sampler_fixture.py` ships `QUILT_JPEG` (a 32x24 JPEG) with `QUILT_WIDTH`/`QUILT_HEIGHT`. `read_png(alpha=True)` on an RGB-only PNG derives an all-`255` alpha plane (run against a generated 4x4 PNG), and `tools/fidelity_pixels.py` treats a missing alpha plane as opaque `255`, so a JPEG converted to PNG24 compares coherently against an RGBA render with no alpha refusal — fidelity has no alpha flag to refuse. `tools/fidelity.py::main` catches `(PngError, FidelityError, ValueError)` and routes them through `report_error`, so a loader-side failure needs no `main` change; `FidelityError` lives in `tools/fidelity_geometry.py`.

**Approach.**

1. `tools/fidelity_sources.py::read_source`: after `require_within_repo`, open the path once and read its first three bytes; when `is_jpeg` holds, read the file whole, `tempfile.mkdtemp(prefix="fidelity-jpeg-")` a private directory, and `convert_jpeg(bytes, temp_png)` into it — never the input's directory. A `convert_jpeg` problem string raises `FidelityError(f"cannot decode {path}: {problem}")`, the same user-facing-path shape every other loader failure uses. On success, run today's decode against the temp PNG exactly as against the original: `read_png(temp, alpha=True, max_rows=…)`, the same sideways-overflow retry re-reading the same temp file unbounded, any `PngError` message having the temp path rewritten to `path` (the sampler's scrub pattern), and `shutil.rmtree(directory, ignore_errors=True)` in a `finally` before returning. A sniff `open` that raises `OSError` falls through to the PNG path so absent and unreadable paths keep `read_png`'s own diagnostics; PNG inputs keep the entire current code path with no conversion attempt; a non-PNG non-JPEG head (WebP, GIF, arbitrary bytes) keeps today's exact `not a PNG file` decode refusal. Import `is_jpeg`, `convert_jpeg` and `FidelityError` in both the package and direct-script import branches; `tests/test_no_unused_imports.py` keeps the imports honest.
2. Add `tests/test_fidelity_jpeg.py`, built on `support.fidelity_cli_case.FidelityCliTestCase` and using `tests/support/jpeg_sampler_fixture.py`'s `QUILT_JPEG`, mirroring `tests/test_sample_jpeg.py`'s class shapes: (a) the self-comparison `quilt.jpg quilt.jpg` exits 0 with the zero-difference report (all-zero metrics, `passed` true) — identical inputs decode identically on any `convert` build, so no lossy pixel value is pinned, and stdout names the given `.jpg` paths and no temporary path; (b) a crop run (`--crop 0,0,64,64`) fails naming the decoded JPEG's own 32x24 dimensions, pinning the converted decode's geometry without pinning lossy pixels; a within-bounds crop with `--difference-run-count` reports count 0; (c) a PNG pair with `mock.patch.object` turning the loader's `convert_jpeg` into an `AssertionError` runs the comparison unchanged — the PNG path never converts; (d) with `mock.patch.object(jpeg_convert.shutil, "which", return_value=None)` a JPEG pair exits 2 with empty stdout and a diagnostic naming the user path and `convert`, reaching no decode; (e) a truncated JPEG (`QUILT_JPEG` head plus a garbage tail) exits 2 naming the user-facing `.jpg` path and never a temporary path; (f) a WebP-headed file (`RIFF`…`WEBP` bytes) keeps the exact `not a PNG file` decode refusal; (g) a repo-symlink escape is still refused before any sniff or decode, and a path outside the repository is converted and read as before; (h) direct-script and package invocations agree.
3. README's `## Fidelity checking` opening paragraph: add one sentence after the crop-options sentence stating that a JPEG candidate or reference is decoded once through ImageMagick into a private temporary PNG before the comparison, other non-PNG formats keep the decode refusal, and the reference set's JPEG screenshots are therefore comparable directly.
4. `docs/invariants.md` `## tooling` table: append one end-of-table row naming `tests/test_fidelity_jpeg.py`, recording the bridge reuse, the opaque-alpha reading, the user-facing-path diagnostics, and the provenance sentence modeled on the sampler's JPEG row (row: "The reference-pixel sampler reads JPEG screenshots directly … (added 2026-11-10 by the feature role)") — ImageMagick's `convert` performs the JPEG decode, no reference screenshot pins the decoder itself, and the shipped fixture's recorded constants mean no test runs ImageMagick at check time.

**Files.** `tools/fidelity_sources.py`, `tests/test_fidelity_jpeg.py` (new), `README.md`, `docs/invariants.md`.

**Acceptance criteria.**

- `python3 tools/fidelity.py a.jpg a.jpg` (the fixture JPEG written to a scratch path) exits 0 and prints the zero-difference report naming both given paths; `--crop 0,0,64,64` on a JPEG pair exits 2 naming the decoded 32x24 dimensions; within-bounds cropped runs report the same empty-difference results the same PNG pair reports.
- A JPEG with `convert` absent from `PATH` exits 2 before any decode, naming the user path and `convert`; a truncated JPEG exits 2 naming the user path with no temporary path anywhere in the diagnostic; a WebP-headed file keeps today's exact `not a PNG file` refusal; a repository-symlink escape is refused before any read of the file's bytes.
- Every existing PNG-path fidelity test passes unchanged, including the pre-read validation spies at the `_read_source` boundary; the loader's `tests/test_fidelity_sources.py` rows pass unchanged; a PNG pair never enters the conversion path (the mocked converter is not called); `make check` passes after the final edit.

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
