# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Group the flat tools/ modules into per-subsystem packages (planned 2026-11-19 by the organize role)

**Needs review 2026-11-19 by feature: too large for one run**

**Needs review 2026-11-19 by feature: too large for one run.** Measured in this checkout: 106 flat `tools/*.py` modules (the entry says 107), 199 Python files that import a prefixed flat module (the entry says 97), 172 test files that call `mock.patch`, and 11 markdown/Makefile files naming flat modules. One change touching all of these, with per-module patch-target ownership decisions and the `tools/render_workflow.py` anchor (absent; its successor is not found by `git log --follow`), exceeds one run's budget. Suggest the plan role split it into one subsystem family per entry (e.g. `render_` first), each landing its own package and its importers together.

**Goal.** `tools/` holds 106 flat modules with no grouping beyond their name
prefixes: `render_` (12), `fidelity_` (12), `sample_` (11), `cursor_` (10),
`check_` (7), `firefox_` (5), `apply_` (5), `uninstall_` (4), `gtk_` (4), plus
single files for other subsystems. A reader cannot see subsystem boundaries from
the directory listing, and 97 files import these modules by their flat names.
Regroup them into subpackages, following the existing `tools/png/` package.

**Cost today.** Evidence: `ls tools/*.py | wc -l` gives 106 modules; `rg -l` finds 97
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

### Group the flat tests/support/ modules into per-family packages (planned 2026-11-21 by the organize role)

**Needs review 2026-11-21 by feature: too large for one run.** The entry covers 89 flat modules and 513 importing test files (counts re-verified: `ls tests/support/*.py | wc -l` gives 89; `rg -l 'from support\.|import support\.' tests` gives 513), plus per-module `mock.patch` retargeting and a family-by-family import graph analysis to decide which modules stay at top level. That is well beyond one run. Suggested split for the plan role: one entry per family slice (starting with `install_`), each landing its modules, importers, patch targets and doc paths together.

**Needs review 2026-11-21 by feature: too large for one run** — 89 flat modules and 513 importing files (`rg -l 'from support\.|import support\.' tests`), plus `mock.patch` targets and docs; the entry's own slicing by family needs several runs.

**Needs review 2026-11-21 by feature: too large for one run** — 89 flat modules and about 513 importing files (`rg -l`) must move family by family, each family landed whole with its patch targets and doc paths; that exceeds one run's budget. The entry's own `install_` slice is a reasonable first step for a later run.

**Needs review 2026-11-21 by feature: too large for one run.** 89 modules and 513 importers; the acceptance criteria need every family moved (`ls tests/support/*.py` lists only shared modules), beyond one run's reading and tool-call budget. The entry's own approach slices it by family, so a later run can land one family whole (install_ first, as the entry suggests).

**Needs review 2026-11-21 by feature: too large for one run.** Measured on this checkout: `ls tests/support/*.py | wc -l` is 89 and `rg -l 'from support\.|import support\.' tests` matches 513 files, so every family slice rewrites hundreds of importers and patch targets. The entry's own approach requires family-by-family landings, and a single tick cannot satisfy the acceptance criterion that `ls tests/support/*.py` lists only shared modules. Needs a plan role to split it into per-family entries.

**Goal.** `tests/support/` holds 89 flat `.py` modules beside its `validation_gaps/`
package. Shared plumbing (temp dirs, process runners, stubs, assertions) sits next to
per-suite case data and reference constants, all with the same flat namespace. A reader
cannot tell from the directory which helper belongs to which suite. Split the flat
modules into a shared top level plus one subpackage per family, following the
`tests/support/validation_gaps/` package that already exists.

**Cost today.** Evidence: `ls tests/support/*.py | wc -l` gives 89. `rg -l 'from support\.|import support\.' tests`
finds 513 files that import a flat support module by name, so a change to one family
is found by grepping names, not by path. Family prefixes are visible in the listing:
`gtk_` and `gtk4_` (8 modules together, 2 of them `gtk4_`), `firefox_` (4), `file_dialog_`
and `file_identity` (3), `install_` (3), `check_` (3), `render_` (3), and `splash_`,
`kvantum_`, `cursor_`, `apply_`, `svg_`, `fidelity_`, `kde_`, `process_` (2 each).
Several of these are per-suite case data (for example `gtk_osd_cases.py`,
`firefox_chrome_cases.py`), not shared helpers.

**Target structure.**
- `tests/support/` keeps only modules whose importers span more than one family:
  process and temp-dir helpers, stubs, error and rejection assertions, and the
  `containment.py`, `repo_root.py` and `xcursor.py` copies that stay on purpose (L7).
- One subpackage per family with `__init__.py`: `tests/support/gtk/`,
  `tests/support/firefox/`, `tests/support/render/`, `tests/support/splash/`,
  `tests/support/kvantum/`, `tests/support/cursor/`, `tests/support/apply/`,
  `tests/support/install/`, `tests/support/fidelity/`, and so on for the families
  above. A module moves into the family whose tests import it; a module that two
  families import stays at the top level.
- The module names lose their family prefix inside the package
  (`tests/support/gtk_css.py` becomes `tests/support/gtk/css.py`). When two modules
  would share a name inside one package, keep the `gtk4_`/`gtk_` distinction in the
  file name.
- `validation_gaps/` and any other existing subpackage keep their paths.

**Files touched.** Each moved module; every importer under `tests/` (the 513 files
above, counted by `rg -l`); every `mock.patch` target string that names a moved module
(retarget each to the module whose global the caller resolves, per the L4 lesson);
`docs/invariants.md` and any doc that names a `tests/support/` path (grep
`tests/support/`).

**Approach.** Cut the work into slices by family, and land each family whole: its
modules, its importers, its patch targets and its doc references in one change. A slice
never leaves one family under two paths. Do the smallest family first (`install_`, 3
modules) to measure the import-rewrite cost, then `gtk`, which is the largest. The
`tools/` regroup (`## Planned`, "Group the flat tools/ modules") is independent: it
touches `tools/` and the `tools/` imports, not `tests/support/`.

**Acceptance criteria.**

- `ls tests/support/*.py` lists only the shared top-level modules; each family lives in
  its own subpackage directory with an `__init__.py`.
- For every moved module, `rg -n` for its old flat import (`support\.<old_name>` and
  `from support import <old_name>`) over `tests/`, `tools/`, `Makefile` and `*.md` finds no
  stale reference.
- Every `mock.patch` string that names a moved module resolves, and the tests that patch
  them pass.
- No behavior change: `git diff` shows moves, import lines, patch targets and doc paths
  only.
- `make check` passes after the final edit, apart from main's known-red tests.

### Xcursor suite extraction: move the test-side reader's tests into their own module (planned 2026-11-21 by the plan role)

**Goal.** `tests/test_xcursor.py` is 607 lines and covers two subjects. Its docstring names both:
"Tests for ``tools/xcursor.py`` and the independent test-side Xcursor reader". The last four
classes (`TestParserRejections`, `TestUnknownChunk`, `TestReadCache` and `TestContainment`,
about 230 lines) test only `support.xcursor.read_cursor`. They use the production writer only to
build valid input bytes. PRINCIPLES.md asks for one responsibility per file, so move those four
classes, with their bodies unchanged, into a new `tests/test_xcursor_reader.py`. No tool or
reader behavior changes. The plan is independent of every other Planned entry, because no other
entry touches these files. It adds one flat module under `tests/support/`. The held
"Group the flat tests/support/ modules into per-family packages" entry will then count one more
module. That entry recounts its modules when it runs, so this plan does not edit it.

**Approach and files touched.**

- **New `tests/support/xcursor_frames.py`.** The moved classes and the classes that stay both
  use the module-level fixtures `opaque_frame` and `frame_record` and the constants
  `FILE_HEADER_SIZE` and `TOC_ENTRY_SIZE` (L4). Move those four names into this module, with
  their bodies and literal values unchanged. Keep the constants as literals. Do not import
  them from `tools.xcursor_container`, so the tests stay independent of the code under test.
  `frame_record` needs `tools.png.write.encode_rgba_png`, so import it here. Give the module a
  one-line docstring that says the writer and reader suites share these fixtures. Keep `SIZES`,
  `IMAGE_TYPE` and `IMAGE_HEADER_SIZE` in `tests/test_xcursor.py`, because only the classes
  that stay use them.
- **`tests/test_xcursor.py`.** Delete the four moved classes and the moved helpers. Import
  `opaque_frame`, `frame_record`, `FILE_HEADER_SIZE` and `TOC_ENTRY_SIZE` from
  `support.xcursor_frames`. Drop any import the remaining code no longer uses; the suite's
  unused-import check (`tests/support/unused_imports.py`) catches leftovers. Narrow the
  docstring to the writer (`tools/xcursor.py`). Every class that stays keeps its name and body,
  including `TestWriterRejections`. Two `docs/invariants.md` rows cite that class (its
  non-iterable and empty-list rejection tests), so those anchors do not change.
- **New `tests/test_xcursor_reader.py`.** Add a docstring naming `tests/support/xcursor.py` as
  the subject. Add the imports the moved code needs (`struct`, `unittest`, `support.repo_root`,
  `support.xcursor as xcursor_reader`, `assert_error_names`, `make_tmp_dir`,
  `tools.xcursor`, plus the fixtures from `support.xcursor_frames`). Then add the four classes,
  with their names and bodies unchanged, above an `if __name__ == "__main__": unittest.main()`
  guard (L1).
- **`tests/test_file_identity.py`.** Its module docstring says the missing-file stat-failure
  case lives in ``test_xcursor``. That test is `TestReadCache.test_a_failed_read_is_not_cached`,
  which moves, so change the parenthetical to ``test_xcursor_reader``.
- Anchor sweep, done while planning: a whole-repository grep for `TestParserRejections`,
  `TestUnknownChunk`, `TestReadCache` and `TestContainment\b` found them only in
  `tests/test_xcursor.py`. Nothing in docs, `docs/invariants.md`, `tests/test_ci_workflow.py` or
  `tests/support/validation_gaps/` names them. The implementer re-runs that grep before
  finishing.

**Acceptance criteria.**

- `python3 -m unittest test_xcursor_reader` run from `tests/` runs the four moved classes, and
  they pass. Their test method names match the names those classes had in `tests/test_xcursor.py`
  before the move.
- `tests/test_xcursor.py` no longer defines `TestParserRejections`, `TestUnknownChunk`,
  `TestReadCache`, `TestContainment`, `opaque_frame` or `frame_record`. Every other class keeps
  its name and its test methods.
- Each of the two files is under 400 lines (`wc -l`).
- `grep -rn 'def frame_record\|def opaque_frame' tests` lists only
  `tests/support/xcursor_frames.py`.
- The `tests/test_file_identity.py` docstring names ``test_xcursor_reader`` as the home of the
  missing-file case.
- The two `docs/invariants.md` rows citing `tests/test_xcursor.py::TestWriterRejections::...`
  still resolve, and the invariants-anchor tests pass.
- Nothing under `theme/`, `tools/` or the `Makefile` changes, and neither does
  `tests/support/xcursor.py`.
- `make check` passes after the final edit. The only allowed exception is main's known-red
  `TestNoReproLedger` tests, if main still fails them (L6). Do not edit `BUGS-FIXED.md` or the
  ledger baseline to make them pass.

### Render failure-paths suite extraction: move the live-session capture tests into their own module (planned 2026-11-21 by the plan role)

**Goal.** `tests/test_render_failure_paths.py` is still 534 lines after the per-mode session
tests moved out. PRINCIPLES.md asks for files small enough to read in one sitting. The largest
concern left inside `TestFailurePaths` is the live-session capture group. These tests either run
the tool's real session script under stubs (`stub_live_session`) or hand back a bad capture
(`stub_capture`), and they pin what the render does with a crashed client, a failed, wrong-size
or black capture, or a client that dies mid-capture. This plan moves that group, with its two
helpers and with each test body unchanged, into a new `tests/test_render_live_capture.py`. No tool
behavior changes. No other Planned entry touches these modules.

**Approach and files touched.**

- New `tests/test_render_live_capture.py`:
  - Module docstring: it pins the render's live-session and capture outcomes against the shell
    stubs, meaning the real session script's applet liveness check, the crashed-applet setup-wait
    diagnosis, and the refusal of a failed, wrong-size, black or vanished-client capture. The
    other failure paths stay in `tests/test_render_failure_paths.py`.
  - Module-level function `crashed_applet_setup_diagnosis`, moved verbatim. Only the two
    crashed-applet tests below call it; check with grep before moving it.
  - `class TestLiveCapture(StubTools, unittest.TestCase)` gets these `TestFailurePaths` members,
    copied verbatim and kept in their current order:
    - the helper method `stub_live_session`
    - `test_a_running_applet_is_still_captured`
    - `test_a_painted_capture_reports_the_session_log_on_stdout`
    - `test_a_crashed_applet_is_not_captured_as_a_successful_render`
    - `test_an_expired_setup_wait_is_reported_by_name_not_as_a_status_mismatch`
    - `test_a_failing_capture_session_exits_1_writes_no_output_and_removes_scratch`
    - `test_a_capture_of_the_wrong_size_exits_1_and_writes_nothing`
    - `test_an_unpainted_capture_exits_1_and_writes_nothing`
    - `test_a_client_that_exits_during_the_capture_is_not_blamed_on_the_paint_budget`
  - Imports: `shlex`, `unittest`, `support.cli_fixtures.run_main`, `tools.render_surface`,
    `tools.png.write.encode_png` and `support.render_stub_tools.StubTools`. Copy the old module's
    `from __future__` line and import layout. Put the class above an
    `if __name__ == "__main__": unittest.main()` guard (L1).
- `tests/test_render_failure_paths.py`: delete the members listed above and
  `crashed_applet_setup_diagnosis`. `test_failed_session_exits_1_and_removes_scratch`,
  `test_session_without_a_capture_exits_1`, the timeout and SIGTERM tests, and every member before
  them stay. Imports used only by the moved code go: `shlex`, `encode_png`, and `run_main` from
  the `support.cli_fixtures` import (`call_main` and `assert_missing_tool_named` stay). Re-check
  each with grep after the deletion. Add one sentence to the module docstring pointing at
  `tests/test_render_live_capture.py` for the live-session capture outcomes.
- `tests/support/render_stub_tools.py`: add the new module to the module docstring's "Used by"
  list. `assert_failed_run`'s docstring says "Shared by the 22 failure-path tails in
  :mod:`tests.test_render_failure_paths`". At planning time, 22 is the call count of
  `self.assert_failed_run(` across `test_render_failure_paths.py` (17, counting the one inside
  `assert_unrunnable_command_is_reported`) and `test_render_session_modes.py` (5). Six of those
  calls move. Recount with grep after the move and reword the docstring so it names every module
  that calls the helper and gives the total you counted.
- `docs/invariants.md`: re-point each `tests/test_render_failure_paths.py::TestFailurePaths::<moved test>`
  anchor to `tests/test_render_live_capture.py::TestLiveCapture::<same test>`. At planning time
  these are the plasmawindowed-liveness row (the crashed-applet test) and the black-capture row
  (the unpainted-capture test). Re-grep at implementation time. Change no row's guarantee text.
- `tests/support/validation_gaps/no_repro.py` (the `client-exit-stub-pidfile-race` reproduction)
  and `tests/support/validation_gaps/slow_check.py` (the `crashed-applet-setup-wait`
  reproduction) cite moved tests as `file::TestFailurePaths::test`. Re-point both to the new
  file and class (L3), and change none of their other fields.
- Per L1, grep `docs/rendering.md`, `docs/fidelity.md`, `tests/test_ci_workflow.py` and README.md
  for the moved names. At planning time, none of them names one.

**Acceptance criteria.**

- From `tests/`, the way `make check` runs it, `python3 -m unittest test_render_live_capture` runs
  the eight named tests under `TestLiveCapture`, and they pass.
- None of the eight test names, `stub_live_session` or `crashed_applet_setup_diagnosis` is defined
  in `tests/test_render_failure_paths.py`. Each is defined exactly once under `tests/`.
- In `git diff -M --color-moved`, the moved bodies show as moved lines, not as edited ones.
- `git grep -n 'test_render_failure_paths.py' -- docs tests` finds no citation of a moved test.
  The invariants-anchor and validation-gap tests pass.
- `python3 -m pyflakes`, if it is installed, reports no unused import in either render module.
  Without pyflakes, grep each import that was dropped or kept to show it is still used.
- Nothing under `theme/`, `tools/` or the `Makefile` changes.
- `make check` passes after the final edit. The only allowed exception is main's known-red
  `TestNoReproLedger` tests, if main still fails them (L6). Do not edit `BUGS-FIXED.md` or the
  ledger baseline to make them pass.

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
