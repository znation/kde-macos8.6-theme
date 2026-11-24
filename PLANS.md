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

### Invariants checker extraction, part 1/2: move the cross-check register-shape tests into their own module (planned 2026-11-22 by the plan role; independent of the waiting parallel-check, terminal-palette, tests/support-regroup and shadowed-definition entries)

**Goal.** `tests/test_invariants.py` is 751 lines, and one class,
`TestHelpers`, drives both halves of `tests/support/invariants.py` against
a synthetic repository: `parse_rows` (register text) and `cross_check`
(register against repository). Move the `cross_check` tests into a new
`tests/test_invariants_cross_check.py`, in two independently mergeable
parts; this part lands the shared fixture base and the register-shape
tests — what a valid register is and how `cross_check` rejects a malformed
or unreadable one, from the data row through the blank provenance cell.
No tool, register or check behaviour changes. No test is added, removed or
renamed except by its class.

**Approach.**

- New `tests/support/invariants_register_case.py`: module docstring
  saying it holds the base class for tests that drive `support.invariants`
  against a synthetic repository (a temp root holding a `docs/invariants.md`
  register plus test modules that discovery never collects). It defines
  `InvariantsRegisterCase(unittest.TestCase)`, holding `TestHelpers`' current
  `MODULE` and `NO_TESTS_MODULE` constants with the comment above them, its
  `setUp` and its `_write`, moved verbatim. Import only what those use
  (`unittest`, `make_tmp_dir`, `write_file`).
- New `tests/test_invariants_cross_check.py`: module docstring saying it
  pins `cross_check`'s register validation on a synthetic repository, that
  the shipped-register drive stays in `tests/test_invariants.py`, and
  pointing at the shared base. Add `class TestCrossCheck(InvariantsRegisterCase)`
  holding verbatim, with their comments, in their current order:
  `test_cross_check_rejects_a_data_row_without_a_test_reference`,
  `test_cross_check_accepts_a_matching_register`,
  `test_parsed_module_reuses_an_unchanged_files_parse`,
  `test_parsed_module_rechecks_containment_on_a_cache_hit`,
  `test_cross_check_reuses_an_unchanged_modules_parse`,
  `test_cross_check_reparses_a_module_that_changed`,
  `test_cross_check_rejects_an_unreadable_register`,
  `test_cross_check_rejects_a_non_utf8_register`,
  `test_cross_check_refuses_a_symlinked_register_that_escapes`,
  `test_cross_check_rejects_a_bare_file_with_no_test_case`,
  `test_cross_check_accepts_a_test_case_inherited_from_a_module_base`,
  `test_cross_check_accepts_a_test_case_with_a_local_non_test_base`,
  `test_cross_check_rejects_a_module_with_a_base_cycle`,
  `test_cross_check_rejects_a_missing_subsystem_section`,
  `test_cross_check_rejects_a_section_with_no_rows`,
  `test_cross_check_rejects_a_missing_tooling_section`,
  `test_cross_check_rejects_a_missing_theme_directory`,
  `test_cross_check_reports_an_unreadable_theme_directory`,
  `test_cross_check_rejects_a_section_for_a_missing_subsystem`,
  `test_cross_check_rejects_a_blank_guarantee`,
  `test_cross_check_rejects_a_blank_provenance` — plus the helpers only
  these tests call: `_register`, `_table`, `_valid_register` and
  `assert_cross_check_rejects` (12 moved tests call it; recount across both
  modules before editing, per the helper-sharing lesson). Imports:
  `unittest`, `mock`, `cross_check`, the base. Put the class above the
  `if __name__ == "__main__":` block, which mirrors the one in
  `tests/test_invariants.py`.
- `tests/test_invariants.py`: `TestHelpers` subclasses
  `InvariantsRegisterCase` and keeps the seven `test_parse_rows_*` tests
  verbatim (including
  `test_parse_rows_escapes_control_characters_in_a_malformed_row`);
  `TestRepositoryRegister` stays as it is. Trim the module docstring's
  drive description to `parse_rows` plus the shipped register. Drop every
  import left unused (`tests/test_no_unused_imports.py` flags leftovers).
- `tests/support/validation_gaps/no_fake.py`: retarget the
  `invariants-symlinked-register` and `invariants-unreadable-register`
  reproductions, whose named tests move in this part, to
  `tests/test_invariants_cross_check.py::TestCrossCheck::<same method>`.
  Leave the other invariants reproductions (`invariants-nul-row`,
  `invariants-unreadable-test-file`) until part 2: their named tests stay
  in `TestHelpers` for now.
- Before editing, grep `tests docs README.md .github` for the moved test
  names and for `TestHelpers`, to find any other anchor or prose pointer.

**Files touched.** new `tests/test_invariants_cross_check.py`, new
`tests/support/invariants_register_case.py`, `tests/test_invariants.py`,
`tests/support/validation_gaps/no_fake.py`.

**Acceptance criteria.**

- `rg -n 'def test_cross_check|def test_parsed_module' tests/test_invariants.py`
  finds nothing, and each of the 21 moved test names is defined only in
  `tests/test_invariants_cross_check.py`.
- `rg -n 'from test_invariants import|import test_invariants\b' tests tools`
  finds nothing: the new module does not import the old one.
- `rg -n 'invariants-(symlinked|unreadable)-register' tests/support/validation_gaps/no_fake.py`
  shows both reproductions naming
  `tests/test_invariants_cross_check.py::TestCrossCheck`.
- `make check CHECK_TESTS='test_invariants test_invariants_cross_check
  test_validation_gaps test_no_unused_imports'` passes, and its output
  shows the moved tests running under
  `test_invariants_cross_check.TestCrossCheck`.
- `tests/test_invariants.py` is under 450 lines, and the new test module
  is under 420 lines.
- No behaviour change: `git diff` shows only moved code, import lines,
  docstrings, and the no_fake retarget.
- `make check` passes after the final edit, apart from main's known-red
  tests.

### Invariants checker extraction, part 2/2: move the cross-check reference-resolution tests into their own module (planned 2026-11-22 by the plan role; "requires part 1/2 landed")

**Goal.** Finish the split planned in part 1/2: move the remaining
`cross_check` tests — how a row's test reference is resolved against the
repository (missing files, classes and methods, test-case bases, unreadable
and oversize modules, the repository boundary) and the control-character
escapes — out of `tests/test_invariants.py`, so the module keeps only the
`parse_rows` tests and the shipped-register drive.

**Approach.**

- `tests/test_invariants_cross_check.py`: append to `TestCrossCheck`, in
  their current order, with their comments:
  `test_cross_check_rejects_a_missing_test_file`,
  `test_cross_check_rejects_a_reference_to_an_unparseable_file`,
  `test_cross_check_rejects_a_reference_to_a_file_it_cannot_read`,
  `test_cross_check_rejects_an_oversize_module_instead_of_loading_it_whole`,
  `test_cross_check_rejects_a_reference_with_a_nul_byte`,
  `test_cross_check_rejects_a_missing_class`,
  `test_cross_check_rejects_an_empty_qualifier`,
  `test_cross_check_rejects_a_reference_with_a_trailing_segment`,
  `test_cross_check_rejects_a_missing_method`,
  `test_cross_check_rejects_a_reference_to_a_non_test_method`,
  `test_cross_check_rejects_a_class_with_no_tests`,
  `test_cross_check_rejects_a_method_on_a_class_with_no_test_case`,
  `test_cross_check_rejects_a_local_base_that_only_looks_like_a_test_case`,
  `test_cross_check_rejects_a_reference_outside_the_repository`,
  `test_cross_check_escapes_control_characters_in_a_section_heading`,
  `test_cross_check_escapes_control_characters_in_a_reference`,
  `test_cross_check_escapes_control_characters_in_a_syntax_error`,
  `test_cross_check_escapes_control_characters_in_a_theme_subsystem`.
  Add the imports they need that part 1 did not bring in
  (`write_file`, `traceback`, `containment_impl`,
  `assert_escapes_escape_character`); keep the module docstring's pointer
  to the shared base.
- `tests/test_invariants.py`: delete the moved tests; `TestHelpers` keeps
  only the seven `test_parse_rows_*` tests and `TestRepositoryRegister`
  stays as it is. Drop every import left unused.
- `tests/support/validation_gaps/no_fake.py`: retarget the
  `invariants-nul-row` reproduction, whose named test moves in this part,
  to `tests/test_invariants_cross_check.py::TestCrossCheck::<same method>`.
  `invariants-unreadable-test-file` names a `test_checker_mutations.py`
  test and stays as it is.
- `docs/invariants.md`: retarget the tooling row that anchors
  `tests/test_invariants.py::TestHelpers::test_cross_check_rejects_an_oversize_module_instead_of_loading_it_whole`
  to `tests/test_invariants_cross_check.py::TestCrossCheck::<same method>`;
  keep the guarantee text. The register cross-check validates that anchor,
  so the retarget must land in the same change.
- Before editing, grep `tests docs README.md .github` for the moved test
  names, to find any other anchor or prose pointer.

**Files touched.** `tests/test_invariants_cross_check.py`,
`tests/test_invariants.py`, `tests/support/validation_gaps/no_fake.py`,
`docs/invariants.md` (one anchor cell).

**Acceptance criteria.**

- `rg -n 'def test_cross_check|def test_parsed_module' tests/test_invariants.py`
  finds nothing, and each of the 18 moved test names is defined only in
  `tests/test_invariants_cross_check.py`.
- `rg -n 'TestHelpers::test_cross_check' tests docs` finds nothing.
- `rg -n 'invariants-nul-row' tests/support/validation_gaps/no_fake.py`
  names `tests/test_invariants_cross_check.py::TestCrossCheck`.
- `make check CHECK_TESTS='test_invariants test_invariants_cross_check
  test_validation_gaps test_no_unused_imports'` passes, with all
  `test_cross_check_*` names running under `TestCrossCheck`.
- `tests/test_invariants.py` is under 250 lines.
- No behaviour change: `git diff` shows only moved code, import lines,
  docstrings, and the anchor and no_fake retargets.
- `make check` passes after the final edit, apart from main's known-red
  tests.

### GTK staging suite extraction: move the commit rollback tests into their own module (planned 2026-11-23 by the plan role; independent of the waiting tests/support regroup, parallel-check, suite-discovery and invariants extraction plans)

**Goal.** After the backup-sibling extraction moved `TestCommitBackups`
into `tests/test_gtk_staging_backups.py`, `tests/test_gtk_staging.py`
(580 lines) is still mostly `TestCommit`: twelve rollback tests, about 305
lines, pinning what happens when `tools/gtk/staging.py`'s `commit` fails
mid-publication — a failed rename, link, restore or interrupt puts every
target it already changed back. The other classes pin `_stage`,
`_attempt_all`, `stage_all`, `discard` and `_restore` on their own. Moving
`TestCommit` into `tests/test_gtk_staging_commit.py` gives each module one
concern. The support base already exists
(`support.gtk.staging_case.StagingTestCase`, whose docstring already says
it serves ``tests/test_gtk_staging*.py``), so no new base is needed.

**Approach.**

- New `tests/test_gtk_staging_commit.py`: a module docstring saying it
  pins `commit`'s replacement and rollback behaviour — a later failure
  restores every earlier target, including a user-CSS removal, and an
  interrupt (`KeyboardInterrupt`) rolls back like any other failure — and
  pointing to `tests/test_gtk_staging.py` for the staging, attempt, discard
  and restore helpers and to `tests/test_gtk_staging_backups.py` for the
  `.backup`-sibling pins. Define `class TestCommit(StagingTestCase)` above
  the `if __name__ == "__main__":` block (L1), holding these twelve methods
  verbatim, with their comments:
  `test_removing_a_missing_file_is_a_no_op`,
  `test_renames_each_staged_file_over_its_target`,
  `test_a_failed_rename_is_reported_by_name_and_restores_the_earlier_target`,
  `test_a_backup_link_failure_is_reported_by_name_and_restores_the_earlier_target`,
  `test_rollback_restores_a_symlink_target_it_replaced`,
  `test_a_created_target_is_removed_again_when_a_later_step_fails`,
  `test_an_interrupt_during_the_commit_restores_the_earlier_target`,
  `test_a_failed_restore_is_reported_with_the_original_failure`,
  `test_every_failed_restore_is_joined_newest_first_and_none_stops_the_rest`,
  `test_a_failed_removal_restores_earlier_replacements_and_removals`,
  `test_a_directory_target_is_refused_and_the_earlier_write_is_restored`,
  and `test_removal_of_a_directory_target_and_a_created_file_rolls_back`.
  Import only what those bodies use (expect `os`, `unittest`, `mock`,
  `Path`, `StagingTestCase`, `write_file`, `_restore`, `_stage`, `commit`,
  `discard`, `stage_all` and `ConfigError`; check each against the bodies).
  End with the usual `__main__` guard mirroring the source module's.
- `tests/test_gtk_staging.py`: delete `TestCommit` and drop the imports
  its removal orphans (`commit` at minimum; check every import against the
  remaining bodies — `tests/test_no_unused_imports.py` flags leftovers).
  Move the module docstring's commit-rollback prose (the sentences about a
  failed rename, the one-line `ConfigError`, the `.staging` cleanup and the
  rollback covering `KeyboardInterrupt`) to the new module's docstring, and
  leave a one-sentence pointer to `tests/test_gtk_staging_commit.py` in
  their place, keeping the existing pointer to
  `tests/test_gtk_staging_backups.py`.
- `docs/invariants.md`: in the GTK settings row, change the class anchor
  `tests/test_gtk_staging.py::TestCommit` to
  `tests/test_gtk_staging_commit.py::TestCommit`; keep the row wording and
  the row's other cells (`TestCommitBackups`, `TestSettingsErrors` and the
  rest) as they are. Leave the staging-discard row's `TestStageAll` cells
  alone — those tests stay.
- `tests/support/validation_gaps/unclear_invariant.py`: re-point the
  `gtk-commit-rollback` entry's citation from
  `tests/test_gtk_staging.py::TestCommit::…` to
  `tests/test_gtk_staging_commit.py::TestCommit::…` (same method name).
  The invariants cross-check validates tooling anchors, so retarget it in
  this same change (L3).
- `tests/support/theme_install.py`: its `write_file` docstring names where
  the write pairs live; name the new module alongside
  `tests/test_gtk_staging.py` and `tests/test_gtk_staging_backups.py`.
- Per L1/L3, grep `docs/`, `README.md`, `tests/test_ci_workflow.py` and
  `tests/support/validation_gaps/` for `TestCommit` and each moved test
  name; at planning time the two anchor sites above are the only hits
  outside `tests/test_gtk_staging*.py` and the archives.

**Files touched.** `tests/test_gtk_staging.py`,
`tests/test_gtk_staging_commit.py` (new), `docs/invariants.md`,
`tests/support/validation_gaps/unclear_invariant.py`,
`tests/support/theme_install.py` (docstring only).

**Acceptance criteria.**

- Test discovery lists the twelve moved test names under
  `test_gtk_staging_commit.TestCommit` and no longer under
  `test_gtk_staging.TestCommit`; every other test id in
  `tests/test_gtk_staging.py` and `tests/test_gtk_staging_backups.py` is
  unchanged.
- Neither test module imports the other, and neither keeps an import its
  bodies no longer use (`tests/test_no_unused_imports.py` passes).
- Probe: temporarily break the rollback in `tools/gtk/staging.py` (for
  example, make a failed rename report the failure without restoring the
  earlier targets). The moved
  `test_a_failed_rename_is_reported_by_name_and_restores_the_earlier_target`
  must fail. Restore the file; `git diff --exit-code tools/` must be clean.
  Describe the probe in VERIFIED.
- `rg -n 'test_gtk_staging\.py::TestCommit' docs tests/support README.md`
  finds nothing, and `rg -n 'TestCommit' docs tests/support` finds the
  moved anchors only under `test_gtk_staging_commit.py` (plus the
  `TestCommitBackups` cells, which keep their own module). The invariants
  register cross-check passes with the re-pointed anchors.
- `tests/test_gtk_staging.py` is under 300 lines and the new module is
  under 340 lines. Nothing under `theme/`, `tools/` or the `Makefile`
  changes; `git diff` shows only the moved class, import lines and
  docstrings.
- `make check CHECK_TESTS='test_gtk_staging test_gtk_staging_backups
  test_gtk_staging_commit test_invariants test_no_unused_imports'` passes,
  and so does full `make check` after the final edit, apart from main's
  known-red tests.

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
