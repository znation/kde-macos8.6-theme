# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Group the tests/support fidelity and kvantum modules into subpackages (part 3/6 of the tests/support regroup) (planned 2026-11-21 by the plan role)

**Needs review 2026-11-21 by feature: too large for one run**

**Goal.** Land the fidelity- and kvantum-family slices of the
tests/support regroup (see part 1/6 for the split's counts and rules; the
parts are independent).

**Modules to move (importer files counted on main).** `fidelity_cli_case`
(40) and `fidelity_delta_fixtures` (4) → `tests/support/fidelity/` with
`__init__.py`: `cli_case.py`, `delta_fixtures.py`. `kvantum_config_spec`
(4) → `tests/support/kvantum/` with `__init__.py`: `config_spec.py`.

**Approach.** As in part 1/6: move, rewrite importer lines and bare
references, retarget `mock.patch` strings, verify importers before each
move. Known stays, already measured: `kvantum_fixtures` (imported by
kvantum tests and the render dialog-gate tests), `jpeg_sampler_fixture`
(fidelity and sample tests), `png_fixtures` (fidelity, png and sample
tests), `sunken_field_reference` and `firstboot_lineedit` (each spans
desktoptheme, kvantum and render tests).

**Files touched.** The three moved modules, their importer files under
`tests/`, any `mock.patch` target strings, and docs naming the old paths.

**Acceptance criteria.**

- `ls tests/support/fidelity/ tests/support/kvantum/` lists both
  `__init__.py` files and the three moved modules;
  `rg -n 'support\.(fidelity_cli_case|fidelity_delta_fixtures|kvantum_config_spec)'`
  over `tests/`, `tools/`, `Makefile`, `docs/` and `*.md` finds no stale
  reference.
- Every `mock.patch` string naming a moved module resolves, and the tests
  that patch them pass.
- No behavior change: `git diff` shows moves, import lines, patch targets
  and doc paths only.
- `make check` passes after the final edit, apart from main's known-red
  tests.

### Parallel-check suite extraction: move the empty-run verdict tests into their own module (planned 2026-11-21 by the plan role; independent of the waiting tests/support regroup, GTK rule cases, Makefile refusal and terminal palette entries)

**Goal.** `tests/test_check_parallel.py` is 702 lines, nearly all in one
`TestCoordinator` class. Six of its tests, plus one helper, cover a single
concern: whether the coordinator trusts a worker's exit 5 as unittest's
"NO TESTS RAN" empty run. Move them into a new
`tests/test_check_parallel_empty_run.py`. Put the scratch-suite setup both
classes need in a support base, so neither test module imports the other.
No tool, Makefile or check behaviour changes. No test is added, removed
or renamed except by its class.

**Approach.**

- New `tests/support/check_parallel_coordinator.py`: a module docstring
  saying it holds the base class for tests that run
  `tools/check_parallel.py` against scratch suites. It defines
  `CoordinatorTestCase(unittest.TestCase)`, holding `TestCoordinator`'s
  current `setUp` (the `XDG_CACHE_HOME` patch with its comment) plus its
  `_project` and `_run` helpers, moved verbatim. Import only what those
  three use (`os`, `unittest`, `mock`, `make_tmp_dir`, `make_suite_dir`,
  `_write_module`, `run_main`, `check_parallel`). Keep it flat in
  `tests/support/` next to `check_parallel_fixtures.py`, which keeps the
  fixture module sources only.
- `tests/test_check_parallel.py`: `TestCoordinator` subclasses
  `CoordinatorTestCase` and loses the moved `setUp`, `_project` and `_run`.
  Delete the moved tests (listed below) and drop any import left unused
  (`tests/test_no_unused_imports.py` flags leftovers). Add
  ``test_check_parallel_empty_run.py`` to the module docstring's
  "The checks split by the module they cover" sentence, describing it as
  covering the exit-5 empty-run verdicts.
- New `tests/test_check_parallel_empty_run.py`: a module docstring saying
  it pins the coordinator's exit-5 / NO TESTS RAN verdicts, and pointing to
  `tests/test_check_parallel_marker.py` for the per-byte marker scan. Add
  `class TestEmptyRunVerdicts(CoordinatorTestCase)`, holding verbatim, with
  their comments: `test_a_module_with_no_tests_does_not_fail_the_run`,
  `test_an_exit_5_without_the_no_tests_ran_summary_fails_the_run`,
  `test_a_forged_no_tests_ran_summary_fails_the_run`,
  `test_an_exit_5_with_only_one_empty_run_marker_fails`,
  `test_a_forged_summary_with_a_test_docstring_fails_the_run`,
  `test_a_started_test_hidden_before_the_bounded_log_tail_fails`, and the
  `_assert_forged_summary_fails` helper. Put the class above the
  `if __name__ == "__main__":` block, which mirrors the one in
  `tests/test_check_parallel.py`.
- `docs/invariants.md`: retarget every
  `tests/test_check_parallel.py::TestCoordinator::<moved test>` anchor to
  `tests/test_check_parallel_empty_run.py::TestEmptyRunVerdicts::<moved test>`.
  Those anchors are in the parallel-check row (which also cites the
  module's other tests) and the "trusts an exit-5 `NO TESTS RAN` summary"
  row. In the parallel-check row's prose, "the named verdict, ordering,
  and terminal-control cases in `TestCoordinator`" becomes the ordering and
  terminal-control cases in `TestCoordinator` and the exit-5 verdict cases
  in `TestEmptyRunVerdicts` (`tests/test_check_parallel_empty_run.py`).
  Leave the other anchors as they are.
- `tests/support/validation_gaps/no_fake.py`: retarget the
  `check-parallel-forged-empty-summary`, `check-parallel-testless-module`
  and `check-parallel-forged-exit-5` reproductions to the new module and
  class. Leave the other `TestCoordinator` reproductions as they are
  (log-stem collision and unterminated log).
- Before editing, grep `tests docs README.md .github` for each moved test
  name, to find any other anchor or prose pointer to update.

**Files touched.** `tests/test_check_parallel.py`, new
`tests/test_check_parallel_empty_run.py`, new
`tests/support/check_parallel_coordinator.py`, `docs/invariants.md`,
`tests/support/validation_gaps/no_fake.py`.

**Acceptance criteria.**

- `rg -n 'test_check_parallel\.py::TestCoordinator::(test_a_module_with_no_tests|test_an_exit_5|test_a_forged|test_a_started_test_hidden)' tests docs`
  finds nothing. Each of the six moved test names is defined only in
  `tests/test_check_parallel_empty_run.py`.
- `rg -n 'from test_check_parallel import|import test_check_parallel\b' tests`
  finds nothing: the new module does not import the old test module.
- `make check CHECK_TESTS='test_check_parallel test_check_parallel_empty_run test_invariants test_validation_gaps test_no_unused_imports test_suite_discovery'`
  passes, and its output shows the six moved tests running under
  `test_check_parallel_empty_run.TestEmptyRunVerdicts`.
- `tests/test_check_parallel.py` is under 560 lines, and the new test
  module is under 220 lines.
- No behaviour change: `git diff` shows only moved code, import lines,
  docstrings, and anchor paths or class names.
- `make check` passes after the final edit, apart from main's known-red
  tests.

### Suite-discovery extraction: move the shadowed-definition guard into its own module (planned 2026-11-21 by the plan role; independent of the waiting tests/support regroup, terminal palette and parallel-check plans)

**Goal.** `tests/test_suite_discovery.py` mixes two responsibilities: the
import-based discovery guards (empty, misnamed, non-package and
test-bearing-package modules) and a static AST guard against a `def` name
defined twice in one scope. Moving the static guard into its own module
leaves each file focused on one check family.

**Approach.** Create `tests/test_suite_shadowed_defs.py` holding
`TestShadowedDefinitions(unittest.TestCase)` (above the `__main__` block)
and move these into it from `tests/test_suite_discovery.py` with unchanged
bodies:
- the module helpers `python_files`, `shadowed_definitions` and
  `shadowed_def_files` (used only by the moved tests, so they move with them
  rather than into `tests/support/`);
- `TestSuiteDiscovery.test_no_test_module_defines_a_name_twice_in_the_same_scope`,
  `test_a_shadowed_test_method_is_reported`,
  `test_a_shadowed_async_test_method_is_reported`,
  `test_a_shadowed_module_level_helper_is_reported` and
  `test_the_same_method_name_in_two_classes_is_not_reported`.

The new module defines its own `TESTS_DIR` the same way the source does and
imports `make_tmp_dir` from `support.tmp_dir`. In the moved real-tree test,
the non-vacuity `assertIn` names the new module's own filename
(`test_suite_shadowed_defs.py`) instead of `test_suite_discovery.py`.
Move the source docstring's "fifth mistake" paragraph to the new module's
docstring and leave a one-sentence pointer to the new module in its place.
Drop the `ast` import from the source if nothing there uses it any more
(`tests/test_no_unused_imports.py` enforces this).
Repoint the five anchors in the `docs/invariants.md` shadowed-`def` row from
`tests/test_suite_discovery.py::TestSuiteDiscovery::…` to
`tests/test_suite_shadowed_defs.py::TestShadowedDefinitions::…`, guarantee
text unchanged. Grep `docs/`, `README.md`, `tests/support/` (including
`validation_gaps/`) and `tests/test_ci_workflow.py` for the moved test and
helper names; at planning time only the invariants row names them (the
`validation_gaps/no_fake.py` reproduction names a test that stays).

**Files touched.** `tests/test_suite_discovery.py`,
`tests/test_suite_shadowed_defs.py` (new), `docs/invariants.md`.

**Acceptance criteria.**
- Test discovery lists the five moved test names under
  `test_suite_shadowed_defs.TestShadowedDefinitions` and no longer under
  `test_suite_discovery.TestSuiteDiscovery`; every other
  `TestSuiteDiscovery` and `TestMakefileReadContainment` test id is unchanged.
- `tests/test_suite_discovery.py` no longer defines `python_files`,
  `shadowed_definitions` or `shadowed_def_files`, and no test module imports
  from another test module.
- Adding a second `def test_ok` to one class in any `tests/**/*.py` file
  still fails the moved real-tree test, naming the file and both line numbers.
- `make check CHECK_TESTS='test_suite_discovery test_suite_shadowed_defs
  test_invariants test_no_unused_imports'` passes, and so does full
  `make check` after the final edit, apart from main's known-red tests.

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
