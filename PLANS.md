# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Group the flat tools/ modules into per-subsystem packages (planned 2026-11-19 by the organize role)

**Needs review 2026-11-19 by feature: too large for one run** — 106 modules in `tools/`, about 195 import lines matching the prefixed families across the tree (grep `from tools.<family>_` / `import <family>_`), plus every `mock.patch` target, the Makefile and docs; the whole move must land as one change, which exceeds one run's scope.

**Goal.** `tools/` holds 107 flat modules with no grouping beyond their name
prefixes: `render_` (12), `fidelity_` (12), `sample_` (11), `cursor_` (10),
`check_` (7), `firefox_` (5), `apply_` (5), `uninstall_` (4), `gtk_` (4), plus
single files for other subsystems. A reader cannot see subsystem boundaries from
the directory listing, and 97 files import these modules by their flat names.
Regroup them into subpackages, following the existing `tools/png/` package.

**Cost today.** Evidence: `ls tools | wc -l` gives 107 modules; `rg -l` finds 97
files that import a prefixed flat module; `render_` names appear in 123 files
(code, tests and docs). Nothing marks which `render_*` modules form the render
subsystem, so a change to one family is found by grepping names, not by path.

**Target structure.** One subpackage per subsystem, each with `__init__.py`:
`tools/render/`, `tools/fidelity/`, `tools/sample/`, `tools/cursor/`,
`tools/firefox/`, `tools/uninstall/`, `tools/gtk/`, `tools/check/`. The module
names lose their prefix inside the package (`tools/render_workflow.py` becomes
`tools/render/workflow.py`). The CLI entry points stay in `tools/` and keep their
paths, because the Makefile, `docs/*.md` and the help text run
`python3 tools/sample.py`, `tools/fidelity.py` and similar commands. Shared
modules (`atomic_write`, `text_lines`, `process_group`, `repo_root`, ...) stay at
the top of `tools/`. Modules that serve two families are assigned to one owner,
and the other family imports it.

**Files touched.** Every moved module; every importer in `tools/` and `tests/`
(about 97 files); every `mock.patch` target string (retarget each moved name to
the module whose global the caller resolves, per the L4 lesson); the Makefile;
`docs/*.md`, README, `docs/invariants.md`, and the rendered help text.

**Approach.** Land the whole move in one change so the tree never sits between
two layouts. Order: create the packages, move modules with `git mv`, rewrite
imports, retarget `mock.patch` strings, then grep every old flat name across
source, tests and markdown before running `make check`.

**Acceptance criteria.**

- `ls tools/*.py` lists only the CLI entry points and shared top-level modules;
  each subsystem family lives in its own package directory.
- A grep for every old flat name (`render_workflow`, `fidelity_metrics`, ...) over
  `*.py`, `*.md` and `Makefile` finds no stale reference.
- Every `mock.patch` string that names a moved module resolves; the tests that patch
  them still pass.
- The CLI entry points run unchanged: `python3 tools/sample.py --help` and
  `python3 tools/fidelity.py --help` exit 0 and print the same usage text as before.
- `make check` passes after the final edit.
- No behavior change: `git diff` shows moves, import lines and patch targets only.

### Render-surface suite extraction: isolate the splash gate's measured logo-cell map (planned 2026-11-19 by the plan role)

**Goal.** Shrink the 1278-line `tests/test_render_surface.py` by moving
the splash gate's measured pixel map out of the gate's assertions.
`TestSplashRender.LOGO_CELL_ROWS` (42 rows of 52 `#RRGGBB` strings) takes
up about 460 lines of the module. This follows the merged list-row fixture
extraction (`tests/support/file_dialog_list_fixtures.py`) and the waiting
file-dialog sidebar-map entry. It is independent of that entry, which edits
only `tests/test_render_file_dialog.py`, and of every waiting GTK 3 suite
extraction, which touch only `tests/test_gtk_theme_*.py` and
`docs/invariants.md`'s `## gtk` rows.

**Approach and files touched.**

- Add `tests/support/splash_capture_fixtures.py`. Don't reuse
  `tests/support/splash_fixtures.py`: that module holds the QML probes and
  reference loader for the shipped splash's source tests, not
  measurements from a render. Give the new module a docstring in the style
  of `file_dialog_list_fixtures.py`. It should say the map was measured
  from the 2026-11-11 `--splash` capture runs that `TestSplashRender`'s
  class docstring names, and that the owning assertion stays in
  `tests/test_render_surface.py`.
- Move `TestSplashRender.LOGO_CELL_ROWS` into it as a module-level
  `LOGO_CELL_ROWS`, keeping the literal as it is. Bring along the
  measurement comment above it: read from the first run, confirmed
  byte-equal in the other two, and a moved, dropped or resampled logo
  fails the byte-compare. Reword "named in the class docstring" so it
  names `TestSplashRender` in `tests/test_render_surface.py`.
- Keep the geometry and colour constants in the class (`LOGO_CELL`,
  `BEVEL_BOX`, `PANEL_BOX`, `PANEL_FACE`, `WORDMARK_BAND`, `TRACK_BOX`,
  `TRACK_FILL` and the `*_COLOUR` values), along with the class docstring.
- In `tests/test_render_surface.py`, import the module as
  `from support import splash_capture_fixtures` beside the other `support`
  imports. Have `test_the_logo_cell_pins_its_art` pass
  `splash_capture_fixtures.LOGO_CELL_ROWS` to `assert_band`, and reword its
  "the measured map above" comment so it names the support module. Test
  names and assertion logic don't change. The module-level
  `Renders.request("applet", "desktop", "splash")` call and every skip
  guard also stay as they are.
- The planning grep found `LOGO_CELL_ROWS` only in
  `tests/test_render_surface.py` outside the archives: nothing in `docs/`,
  `README.md`, `PLACEHOLDERS.md`, `tests/test_ci_workflow.py`,
  `tests/support/validation_gaps/*.py` or the `_GATE_FILES` lists. Re-grep
  at implementation. No production code, theme file, render kind or gate
  class moves.

**Acceptance criteria.**

- `tests/support/splash_capture_fixtures.py` exposes `LOGO_CELL_ROWS` as
  42 rows of 52 `#RRGGBB` strings. It equals the class attribute it
  replaces on main, as an `ast.literal_eval` comparison of the old and new
  literals shows (no render needed).
- `TestSplashRender` no longer defines `LOGO_CELL_ROWS`, and
  `tests/test_render_surface.py` holds no other copy of the map. The
  module is shorter by roughly the map's size.
- Test discovery lists the same `tests/test_render_surface.py` test IDs as
  before. On a host with the splash tools, the logo-cell test still
  byte-compares the same 52x42 cell at (294, 110). Without the tools it
  skips under the existing guard, as before.
- Importing the new support module starts no GUI process, render session
  or capture.
- `make check` passes after the final edit.

### Parallel-check suite extraction: move the direct results-report cases into the results suite (planned 2026-11-19 by the plan role)

**Goal.** Shrink the 953-line `tests/test_check_parallel.py` and keep it on
one concern: running the coordinator end to end. Its single class,
`TestCoordinator`, also holds cases that never run the coordinator. They
call `check_parallel.print_results(modules, statuses, log_paths, timeout)`
directly on hand-written log files. That function is
`tools/check_parallel_results.print_results`, which
`tests/test_check_parallel_results.py` already covers in its
`TestPrintResults` class. The module docstring of `test_check_parallel.py`
already says the results report is pinned in `test_check_parallel_results.py`,
but these cases were left behind when `tools/check_parallel_results.py` was split out.

**The cases to move.** These are the `TestCoordinator` methods whose only
action is a direct `print_results` call. None of them use `self._run`,
`self._project` or the `setUp` cache-home patch. The moved methods are:
`test_missing_worker_log_fails_even_when_worker_exited_zero`,
`test_fifo_worker_log_read_fails_without_blocking`,
`test_a_fifo_started_test_scan_fails_without_blocking`,
`test_missing_worker_status_reports_did_not_finish_and_keeps_log`,
`test_a_flooded_log_prints_a_bounded_tail_with_a_hidden_byte_note`,
`test_a_flooded_log_keeps_its_end_of_log_summary_verdict`,
`test_invalid_utf8_in_worker_log_is_replaced`,
`test_a_window_without_any_line_break_is_shown_whole`,
`test_crlf_worker_log_lines_end_before_the_line_breaks`,
`test_mixed_empty_and_failed_modules_report_both_outcomes`,
`test_summary_combines_failed_timed_out_and_unfinished_modules`,
`test_summary_counts_multiple_failed_workers_including_a_signal_exit` and
`test_summary_counts_empty_module_alongside_a_timeout`. Leave
`test_fifo_worker_log_fails_without_blocking` (the spawn-side FIFO case) and
every case that calls `self._run` where they are. So do the cases that patch
`tools.check_parallel.print_results` to test `main`.

**Approach.** Move the thirteen methods into
`tests/test_check_parallel_results.py::TestPrintResults` with their names,
docstrings, comments and assertions unchanged. The results suite imports
`print_results` from `tools.check_parallel_results` directly, so replace
`check_parallel.print_results(` with `print_results(`. Keep each case's
scratch files on `support.tmp_dir.make_tmp_dir(self)`. Keep the
`mock.patch("tools.check_parallel_results._bounded_log_text", ...)` target
in the FIFO-scan case as it is, because it already names the defining module.
Add the `os`, `io`/`contextlib` (or reuse the module's
`StringIO`/`redirect_stdout` imports), `mock` and `make_tmp_dir` imports
the moved cases need. Do not import `tests/test_check_parallel.py`.
In `tests/test_check_parallel.py`, then drop any import that is no longer used.
Expect `io`, `contextlib` and `os` to stay, because the remaining
stderr-capturing and scratch-directory cases still use them, but check each one with grep.

**Files touched.** `tests/test_check_parallel.py`,
`tests/test_check_parallel_results.py`, `docs/invariants.md`.

**Anchors.** `docs/invariants.md` names six of the moved cases as
`tests/test_check_parallel.py::TestCoordinator::<name>`:
`test_missing_worker_log_fails_even_when_worker_exited_zero`,
`test_fifo_worker_log_read_fails_without_blocking` (in two rows: the
`make check` tooling row and the regular-file worker-log row),
`test_a_fifo_started_test_scan_fails_without_blocking`, both flooded-log cases,
`test_a_window_without_any_line_break_is_shown_whole` and
`test_crlf_worker_log_lines_end_before_the_line_breaks`. Retarget each one to
`tests/test_check_parallel_results.py::TestPrintResults::<name>`. In the
tooling row, also correct the prose that credits "the named verdict, ordering,
unreadable-log, terminal-control, and flooded-log cases in `TestCoordinator`"
so that the flooded-log and unreadable-log cases are credited to
`TestPrintResults`. A grep on 2026-11-19 found no anchor for any of the
thirteen names in `tests/support/validation_gaps/*.py`, README.md or
`docs/rendering.md`/`docs/fidelity.md`. The `no_fake.py` reproductions
that name `TestCoordinator` point at cases that stay. Re-run that grep before
finishing.

**Acceptance criteria.**

- `grep -n 'print_results(' tests/test_check_parallel.py` finds only the
  `mock.patch("tools.check_parallel.print_results", ...)` targets. No
  `TestCoordinator` case calls the report function directly.
- Each of the thirteen names above is defined once in the tree, under
  `TestPrintResults` in `tests/test_check_parallel_results.py`. Its assertions
  are unchanged, apart from the `check_parallel.` prefix being dropped.
- `grep -rn 'test_check_parallel.py::TestCoordinator::<name>'` for each moved
  name finds no match in `docs/`, `tests/` or README.md. Each invariant row that
  named one now names the `test_check_parallel_results.py::TestPrintResults`
  anchor, and `tests/test_invariants.py` passes.
- `make check CHECK_TESTS='test_check_parallel test_check_parallel_results test_invariants'`
  passes, and `make check` passes after the final edit.

## Done

### GTK 3 suite extraction: isolate drag-and-drop declarations (planned 2026-11-18 by the plan role) — done 2026-11-18 by the feature role

**Goal.** Give GTK 3 header drag-feedback declaration checks a focused
suite outside the oversized views module. This relocation is independent
of the waiting paned-handle and pending message-dialog extractions.

**Approach and files touched.** Move
`TestGtkThemeViews.test_header_drop_indicator`,
`test_header_drop_arm_carries_no_padding` and
`test_no_dndtarget_node_declared` from `tests/test_gtk_theme_views.py` to
new `tests/test_gtk_theme_drag_drop.py::TestGtkThemeDragDrop`, preserving
their bodies. Inherit `support.gtk_rule_cases.GtkSheetRuleCases` and
`unittest.TestCase`; set
`CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"`, importing
`ROOT` from `support.repo_root` and `BLACK` and `SELECTION` from
`support.platinum_palette`. The base supplies sheet parsing and assertions;
no shared helper change is needed. Update the source routing docstring and
repoint the moved anchors in the GTK 3 drag-and-drop row of
`docs/invariants.md`, retaining its guarantee and stock-resource provenance.
Search `docs/rendering.md`, `docs/fidelity.md`, `tests/test_ci_workflow.py`
and `tests/support/` for other moved anchors. Keep GTK 4 coverage and GTK 3
rubberband checks in their existing suites; theme sheets need no changes.

**Acceptance criteria.**

- Discovery exposes the named methods in the destination without duplicate
  methods in views or inherited shared-control tests in the destination.
  Source and destination pass independently through project check selectors.
- The plain, legacy dotted-header and spaced-header selector spellings,
  each with plain, hover, active and selected states, retain selection fill,
  black ink, cleared background image and shadows, no border and zero
  radius checks. Changing just the legacy hovered header arm's fill fails
  a moved check.
- Adding padding to `treeview.view button.dnd` or declaring a `dndtarget`
  node in the GTK 3 sheet fails a moved check.
- Invariant anchors resolve and full `make check` passes. This relocation
  adds no rendered-pixel claim.

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
