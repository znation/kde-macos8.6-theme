# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Group the flat tools/ modules into per-subsystem packages (planned 2026-11-19 by the organize role)

**Needs review 2026-11-19 by feature: too large for one run**

**Needs review 2026-11-19 by feature: too large for one run.** Measured in this checkout: 106 flat `tools/*.py` modules (the entry says 107), 199 Python files that import a prefixed flat module (the entry says 97), 172 test files that call `mock.patch`, and 11 markdown/Makefile files naming flat modules. One change touching all of these, with per-module patch-target ownership decisions and the `tools/render_workflow.py` anchor (absent; its successor is not found by `git log --follow`), exceeds one run's budget. Suggest the plan role split it into one subsystem family per entry (e.g. `render_` first), each landing its own package and its importers together.

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

### Firefox installer suite extraction: move the write-failure and interrupt rollback tests into their own module (planned 2026-11-21 by the plan role)

**Goal.** `tests/test_install_firefox.py` is 687 lines, and its `TestInstall` class is about 570
of them. PRINCIPLES.md asks for files small enough to read in one sitting. One concern inside
that class is self-contained: the tests that pin the install transaction's rollback when a write
fails or an interrupt lands mid-publish. That is the guarantee the docs/invariants.md row
"Firefox installation publishes both sheets then `user.js` as one transaction" names. This plan
moves those tests unchanged into a new `tests/test_install_firefox_rollback.py` class. No tool
behavior or test body changes. It does not depend on any other Planned entry.

**Approach and files touched.**

- New `tests/test_install_firefox_rollback.py`:
  - Module docstring: it pins the Firefox install transaction's rollback, covering write
    failures and interrupts before or after each file publishes. Installs, refusals and size caps
    stay in `tests/test_install_firefox.py`, and the shared temp-home case is
    `support.firefox_profile_case`.
  - `class TestInstallRollback(FirefoxProfileTestCase)` gets these `TestInstall` methods,
    verbatim and in their current order:
    - `test_an_uncreatable_chrome_directory_is_reported_by_path`
    - `test_a_failed_user_js_write_is_reported_by_path`
    - `test_a_failed_user_js_write_restores_both_previous_sheets`
    - `test_a_failed_user_js_write_keeps_a_block_that_was_already_installed`
    - `test_a_failed_sheet_restore_is_reported_with_the_original_error`
    - `test_an_interrupt_during_the_user_js_write_restores_the_previous_sheet`
    - `test_an_interrupt_after_the_user_js_write_takes_effect_restores_it`
    - `test_an_interrupt_after_a_created_user_js_is_published_removes_it`
    - `test_a_failed_user_js_restore_is_reported_with_the_original_error`
    - `test_an_interrupt_after_the_sheet_write_takes_effect_removes_it`
    - `test_a_failed_new_sheet_restore_is_reported_with_the_original_error`
    - `test_a_failed_sheet_write_is_reported_by_path`
    - `test_a_failed_user_content_write_removes_the_published_user_chrome`
    - `test_an_interrupt_after_the_user_content_write_takes_effect_removes_both`

    These are the 14 contiguous methods from the uncreatable-chrome test through the
    user-content interrupt test. `test_a_missing_shipped_sheet_is_reported_by_path` and
    everything after it stay.
  - The moved bodies call only base-class helpers (`run_tool`, `run_with_failed_write`,
    `interrupt_write_to`, `fail_unlink_to`, `assert_profile_absent`, the path helpers) plus
    the module-level `SHEET_PATH`. Nothing has to move into `tests/support` (L4). Define
    `SHEET_PATH = Path(repo_root.ROOT) / install_firefox.SHEET` in the new module, the same
    one-line derivation the old module keeps for its own callers. `CONTENT_SHEET_PATH` is
    not used by the moved bodies.
  - Imports: only what the moved bodies use. As of this plan that is `unittest`, `Path`,
    `mock`, `containment`, `repo_root`, `write_file as _write`, `FirefoxProfileTestCase`,
    `read_utf8 as _read`, `firefox_user_files` and `install_firefox`. Confirm each with grep.
    `errno` is not used by the moved range.
  - Add the class above an `if __name__ == "__main__": unittest.main()` footer (L1).
- `tests/test_install_firefox.py`: delete the moved methods. Keep every import a remaining body
  still uses; as of this plan `mock`, `containment`, `firefox_user_files`, `SHEET_PATH` and
  `CONTENT_SHEET_PATH` are all still used, so check each with grep before dropping anything.
  In the module docstring, add that the rollback cases live in
  `tests/test_install_firefox_rollback.py`.
- `tests/support/firefox_profile_case.py` docstrings (recount with grep after the move):
  - The module docstring should name the new module among the case's users.
  - `run_with_failed_write`: all six `tests/test_install_firefox.py` callers move, so the
    sentence becomes six callers in `tests/test_install_firefox_rollback.py` and one in
    `tests/test_remove_firefox.py`.
  - `interrupt_write_to`: all five callers move, so "Five callers in
    `tests/test_install_firefox.py`" names the new module.
- `tests/support/theme_install.py`, `write_file` docstring: add
  `test_install_firefox_rollback.py` to the modules that bind `_write` as an import alias. If
  the "``user.js`` fixture" left unconverted in `tests/test_install_firefox.py` is one of the
  moved bodies, repoint that mention too. Otherwise leave it.
- `docs/invariants.md`:
  - In the row beginning "The Firefox install copies both sheets", rewrite the eight
    `tests/test_install_firefox.py::TestInstall::<method>` anchors whose method moved to
    `tests/test_install_firefox_rollback.py::TestInstallRollback::<method>`. These are the
    failed new-sheet restore, failed sheet restore, failed user-content write, failed user.js
    write restoring both sheets, and the four interrupt tests. Leave its other anchors.
  - In the transaction row ("Firefox installation publishes both sheets then `user.js` as one
    transaction"), replace the bare `tests/test_install_firefox.py::TestInstall` anchor with
    `tests/test_install_firefox_rollback.py::TestInstallRollback`, because every test for that
    guarantee moves.
- Per L1/L3, grep `docs/rendering.md`, `docs/fidelity.md`, `tests/test_ci_workflow.py` and
  `tests/support/validation_gaps/*.py` for the moved method names. As of this plan, the
  validation-gap anchors on `TestInstall` name only methods that stay (oversize user chrome,
  empty sheet adopted, symlinked profile files, BOM before marker). These are not render gates,
  so `_GATE_FILES` does not apply. Archives keep their historical anchors.

**Acceptance criteria.**

- `tests/test_install_firefox_rollback.py` defines `TestInstallRollback` with the 14 methods
  above, with the same names and bodies they had in `TestInstall`. None of those names
  is still defined in `tests/test_install_firefox.py`.
- Taken together, the `test_*` names in the two modules equal the set the original
  `tests/test_install_firefox.py` defined, with nothing lost or duplicated.
  `tests/test_install_firefox.py` is under 500 lines (`wc -l`).
- `grep -n 'test_install_firefox.py::TestInstall::test_a_failed_sheet_restore\|test_install_firefox.py::TestInstall::test_an_interrupt' docs/invariants.md`
  prints nothing, and the invariants-anchor and validation-gap tests pass.
- Nothing under `theme/`, `tools/` or the `Makefile` changes.
- `make check` passes after the final edit. The only allowed exception is main's known-red
  `TestNoReproLedger` tests, if main still fails them (L6). Do not edit `BUGS-FIXED.md` or
  the ledger baseline to make them pass.

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
