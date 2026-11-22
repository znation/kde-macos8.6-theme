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

### GTK rule cases: move the shared control cases into their own support module (planned 2026-11-21 by the plan role; independent of the waiting tests/support regroup, desktop wallpaper and file-dialog gate parts)

**Goal.** `tests/support/gtk_rule_cases.py` is 880 lines holding three
classes: `SheetRuleAssertions`, the parametrised `GtkSheetRuleCases`
assertions, and `GtkSharedControlCases` (the shared `test_*` control cases
the GTK 3 `TestGtkTheme` and the GTK 4 `Gtk4SheetRuleCases` inherit once
each). Move `GtkSharedControlCases` whole into a new flat module
`tests/support/gtk_shared_control_cases.py`, so each file holds one
concern and is readable in one sitting. No test is added, removed or
renamed and no stylesheet changes.

**Approach.**

- New `tests/support/gtk_shared_control_cases.py`: a module docstring
  saying it holds the control test cases each inheriting GTK suite runs
  once, and that the parametrised assertions they call live in
  `tests/support/gtk_rule_cases.py`. Then `GtkSharedControlCases`
  verbatim (its docstring, `assert_infobar_message_type_ban`,
  `test_headerbar` … `test_tab_states`, `assert_separator_label_foreground`),
  subclassing `GtkSheetRuleCases` imported from `support.gtk_rule_cases`.
  Import only the names the class body uses: the spec constants from
  `support.gtk_theme_spec` (for example `BUTTON_BEVEL`, `CHECK`,
  `ENTRY_FIELD`, `TAB_STATES`, `TOOLTIP`) and the palette names from
  `support.platinum_palette` (`BLACK`, `FACE`, `GREY`,
  `INACTIVE_OUTLINE`). Keep it flat at `tests/support/`, like the other
  cross-family gtk/gtk4 stays (its importers span `tests/test_gtk_theme.py`
  and `tests/support/gtk4_sheet.py`).
- `tests/support/gtk_rule_cases.py`: delete the class; drop each import
  the remaining classes no longer use (`tests/test_no_unused_imports.py`
  flags any left behind). Rewrite the module docstring's
  `GtkSharedControlCases` sentence to point at the new module. The
  `ROW_SELECTED_BUTTON_ARM_*` constants stay (`tests/test_gtk4_sidebar.py`
  imports them).
- Importers: `tests/test_gtk_theme.py` and `tests/support/gtk4_sheet.py`
  import `GtkSharedControlCases` from `support.gtk_shared_control_cases`.
- `docs/invariants.md`: retarget the ten
  `tests/support/gtk_rule_cases.py::GtkSharedControlCases::…` anchors to
  `tests/support/gtk_shared_control_cases.py::GtkSharedControlCases::…`.
  The `GtkSheetRuleCases::assert_progressbar`, `assert_scale` and
  `assert_tab_faces` anchors stay as they are. The `test_tab_states`
  docstring's own `tests/support/gtk_rule_cases.py::GtkSharedControlCases::test_tab_states`
  pointer moves with it and is retargeted the same way.

**Files touched.** `tests/support/gtk_rule_cases.py`, new
`tests/support/gtk_shared_control_cases.py`, `tests/test_gtk_theme.py`,
`tests/support/gtk4_sheet.py`, `docs/invariants.md`.

**Acceptance criteria.**

- `rg -n 'class GtkSharedControlCases' tests` finds only
  `tests/support/gtk_shared_control_cases.py`; `rg -n
  'gtk_rule_cases(\.py)?::GtkSharedControlCases|gtk_rule_cases import
  GtkSharedControlCases' tests docs` finds nothing.
- `make check CHECK_TESTS='test_gtk_theme test_gtk4_theme test_invariants
  test_no_unused_imports'` passes.
- The set of test ids `make check` runs is unchanged: listing every id
  ending in one of `GtkSharedControlCases`' `test_*` names (for example
  `test_headerbar`, `test_tab_states`) before and after the move gives the
  same classes, starting with `test_gtk_theme.TestGtkTheme` and each GTK 4
  class that inherits `Gtk4SheetRuleCases`.
- `tests/support/gtk_rule_cases.py` is under 660 lines and the new module
  under 280.
- No behaviour change: `git diff` shows the moved class, import lines,
  docstring pointers and anchor paths only.
- `make check` passes after the final edit, apart from main's known-red
  tests.

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
