# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### GTK 3 suite extraction: move the disabled-selected row and child inventory into the disabled-views suite (planned 2026-11-19 by the plan role)

**Goal.** Put GTK 3 disabled-selected checks next to the other GTK 3
disabled-view checks and shrink the oversized views module. This move does
not depend on the waiting entry-icon, row-press, stepper/check-corner or
selected icon-view/treeview extractions. Those touch other methods of
`tests/test_gtk_theme_views.py`, plus its docstring and import block.

**Approach and files touched.**

- Move `TestGtkThemeViews.test_disabled_selected_row_and_child_arms` from
  `tests/test_gtk_theme_views.py` to
  `tests/test_gtk_theme_disabled_views.py::TestGtkThemeDisabledViews`. Put
  it after `test_disabled_view_face_and_ink`. Keep its body, docstring and
  comments the same. The method only calls `assert_disabled_text` and reads
  `self.rules`. Both come from `support.gtk_rule_cases.GtkSheetRuleCases`,
  which the destination already inherits, and the destination already sets
  the same GTK 3 `CSS_PATH`. So the destination needs no new import and no
  shared helper changes.
- In the views module, leave the import block alone. The moved method
  imports no names of its own.
- Update the views module docstring's routing prose: add one sentence saying
  disabled-selected row, child and tree-view declarations live in
  `tests/test_gtk_theme_disabled_views.py`. Write it against the docstring
  as it reads at implementation time, because sibling extractions edit the
  same paragraph.
- In `docs/invariants.md`, repoint each
  `tests/test_gtk_theme_views.py::TestGtkThemeViews::test_disabled_selected_row_and_child_arms`
  anchor to
  `tests/test_gtk_theme_disabled_views.py::TestGtkThemeDisabledViews::test_disabled_selected_row_and_child_arms`.
  A grep on 2026-11-19 found three rows with this anchor: the GTK 3
  disabled-selected rows/flow-box/tree-column row, the GTK 3 selected-text
  arms row, and the disabled activatable-list-row row. Keep every guarantee's
  wording. Do not touch the separate GTK 4 anchors
  `tests/test_gtk4_disabled.py::TestGtk4Disabled::test_disabled_selected_row_and_child_arms`.
- Grep `docs/rendering.md`, `docs/fidelity.md`,
  `tests/test_ci_workflow.py`, `tests/support/` (including
  `tests/support/validation_gaps/*.py`) and `PLANS.md` `## Planned` for the
  old anchor, and repoint any hit. The 2026-11-19 grep found none outside
  `docs/invariants.md`. This is not a render gate, so the `_GATE_FILES`
  lists are not involved.
- No changes to theme sheets, source partials or `test_flowbox_child_selected_arms`.
  The flow-box test stays in views and is a later candidate.

**Acceptance criteria.**

- Test discovery lists `test_disabled_selected_row_and_child_arms` under
  `TestGtkThemeDisabledViews` and no longer lists it under
  `TestGtkThemeViews`. `TestGtkThemeDisabledViews` still has
  `test_disabled_view_face_and_ink`, and both modules pass when run on
  their own through the project's unittest runner.
- With the moved test in its new suite, changing the grey ink on
  `flowbox flowboxchild:backdrop:disabled:selected` in the GTK 3 sheet fails
  it. Adding any new GTK 3 selector containing `:disabled:selected` also
  fails it (the family inventory). So does deleting
  `treeview.view:disabled:selected:backdrop`.
- Every `docs/invariants.md` anchor naming
  `test_disabled_selected_row_and_child_arms` resolves to an existing
  method. After the change, a grep finds no reference to the method under
  `tests/test_gtk_theme_views.py`.
- `git diff --stat` shows changes only to the two test modules,
  `docs/invariants.md` and the backlog files. Theme sheets, partials and generated files have no
  diff.
- `make check` passes after the final edit.

### GTK 3 suite extraction: move the separator and frame declarations into the frames suite (planned 2026-11-19 by the plan role)

**Goal.** Put the GTK 3 standalone-separator and sunken-frame declaration
checks next to the flat-frame and viewport frame checks they relate to.
This makes the views module smaller and mirrors GTK 4, where
`tests/test_gtk4_frame_corners.py::TestGtk4FrameCorners` holds both
checks. This move is independent of the waiting spin-button,
selected-views and disabled-selected extractions. Each of those touches
different methods of `tests/test_gtk_theme_views.py`, so a merge
conflict there can only come from neighbouring lines.

**Approach and files touched.**
- Move `TestGtkThemeViews.test_separator` (`self.assert_separators()`)
  and `TestGtkThemeViews.test_frame`
  (`self.assert_frame(("frame > border", ".frame"))`) unchanged from
  `tests/test_gtk_theme_views.py` into
  `tests/test_gtk_theme_frames.py::TestGtkThemeFrames`. That class
  already inherits `GtkSheetRuleCases` with the same GTK 3 `CSS_PATH`,
  so it needs no new imports, base classes or helper changes. Both
  helpers live in `tests/support/gtk_rule_cases.py` and stay there.
  Neither test calls `_run_gtk_child`, so `Gtk3ChildProbeCases` skips
  nothing for them.
- Update both module docstrings:
  - In views, add that separator and frame declarations are in
    `tests/test_gtk_theme_frames.py`.
  - In frames, add the etched standalone separators and the
    `frame > border, .frame` bevel declaration to the slice it owns.
- In `docs/invariants.md`, change the separator row's
  `tests/test_gtk_theme_views.py::TestGtkThemeViews::test_separator`
  anchor to
  `tests/test_gtk_theme_frames.py::TestGtkThemeFrames::test_separator`.
  Keep the guarantee text and provenance.
- The GTK 3 control-rules summary row cites both classes, not their
  methods, so it needs no edit: it already lists
  `tests/test_gtk_theme_frames.py::TestGtkThemeFrames`, and
  `TestGtkThemeViews` still has tests after the move.
- Before finishing, grep `docs/rendering.md`, `docs/fidelity.md`,
  `tests/test_ci_workflow.py` and `tests/support/` for
  `TestGtkThemeViews::test_separator` and `TestGtkThemeViews::test_frame`.
  A grep on 2026-11-19 found none.
- No theme sheet, partial or generated file changes.

**Acceptance criteria.**
- Discovery lists `test_separator` and `test_frame` under
  `test_gtk_theme_frames.TestGtkThemeFrames`, and neither name under
  `test_gtk_theme_views.TestGtkThemeViews`. Each module passes when run
  alone through the project's check selectors.
- In the GTK 3 sheet, either of these makes the moved `test_separator`
  fail: changing `separator.horizontal`'s `border-bottom` away from
  `1px solid #FFFFFF`, or adding a `margin` to `separator.vertical`.
  Changing the `frame > border, .frame` rule's `box-shadow` away from
  `inset 1px 1px #999999` makes the moved `test_frame` fail.
- `grep -rn 'TestGtkThemeViews::test_separator\|TestGtkThemeViews::test_frame' docs tests README.md`
  finds nothing outside `__pycache__`. Every invariants anchor resolves.
- `git diff --stat` shows changes only to the two test modules,
  `docs/invariants.md` and the backlog files.
- `make check` passes after the final edit. This move adds no claim about
  rendered pixels.

### GTK 3 suite extraction: move the stack-switcher tab check into the notebook suite (planned 2026-11-19 by the plan role)

**Goal.** Put the GTK 3 stack-switcher tab-face check next to the GTK 3
notebook tab checks it shares a recipe with, and shrink the views module.
The method sits apart from the disabled-selected, spin-button and
separator/frame extractions. All of them edit
`tests/test_gtk_theme_views.py`, its docstring and `docs/invariants.md`, so
whichever merges later re-reads those and rewrites only its own lines.

**Approach and files touched.**

- Move `TestGtkThemeViews.test_stack_switcher_tabs` from
  `tests/test_gtk_theme_views.py` to
  `tests/test_gtk_theme_notebook.py::TestGtkThemeNotebook`, after
  `test_notebook_tab_focus_outline`. Keep its body the same. It calls only
  `assert_tab_faces` from `support.gtk_rule_cases.GtkSheetRuleCases`, which
  the destination already inherits. The destination already sets the same
  GTK 3 `CSS_PATH`. The method names no module-level constant, so neither
  module's import block changes. Keep the blank-line layout before the
  destination's `if __name__ == "__main__":` guard.
- Widen the destination's one-line module docstring to say it covers GTK 3
  notebook and stack-switcher tab declarations.
- In the views module docstring, drop "the stack switcher" from the list of
  what this module owns. Add one sentence saying stack-switcher tab
  declarations are in `tests/test_gtk_theme_notebook.py`. Write it against
  the docstring as it reads at implementation time.
- In `docs/invariants.md`, repoint the
  `tests/test_gtk_theme_views.py::TestGtkThemeViews::test_stack_switcher_tabs`
  anchor to
  `tests/test_gtk_theme_notebook.py::TestGtkThemeNotebook::test_stack_switcher_tabs`.
  A grep on 2026-11-19 found it once, in the "Both GTK sheets paint a stack
  switcher's page buttons" row. Keep the row's wording and its GTK 4 anchor
  `tests/test_gtk4_navigation.py::TestGtk4Navigation::test_stack_switcher_tabs`.
- Grep `docs/rendering.md`, `docs/fidelity.md`,
  `tests/test_ci_workflow.py` and `tests/support/` (including
  `tests/support/validation_gaps/*.py`) for the old anchor and repoint any
  hit. The 2026-11-19 grep found none outside `docs/invariants.md`. This is
  not a render gate, so the `_GATE_FILES` lists are not involved.
- Do not change theme sheets, source partials or
  `tests/test_gtk_theme_path_bar.py`.

**Acceptance criteria.**

- Test discovery lists `test_stack_switcher_tabs` under
  `test_gtk_theme_notebook.TestGtkThemeNotebook` and no longer under
  `test_gtk_theme_views.TestGtkThemeViews`. The notebook suite still lists
  its four existing `test_notebook_*` methods. Both modules pass when run
  on their own through the project's unittest runner.
- The moved method's function-definition AST is identical to the original
  at the base commit.
- With the test in its new suite, removing `box-shadow` from the GTK 3
  sheet's `stackswitcher > button` rule fails it. So does deleting the
  `stackswitcher > button:checked:hover` selector from its group.
- The `docs/invariants.md` GTK 3 stack-switcher anchor resolves to an
  existing method. After the change, a grep finds no
  `test_stack_switcher_tabs` in `tests/test_gtk_theme_views.py`.
- `git diff --stat` shows changes only to the two test modules,
  `docs/invariants.md` and the backlog files. Theme sheets, partials and
  generated files have no diff.
- `make check` passes after the final edit.

### GTK 3 suite extraction: move the flow-box selected check into the selected-views suite (planned 2026-11-19 by the plan role)

**Goal.** Put the GTK 3 selected flow-box child check next to the selected
icon-view and treeview checks it shares a recipe with, and shrink
`tests/test_gtk_theme_views.py` further. The method sits apart from the
disabled-selected, spin-button, separator/frame and stack-switcher
extractions. All of them edit `tests/test_gtk_theme_views.py`, its docstring
and `docs/invariants.md`, so whichever merges later re-reads those and
rewrites only its own lines.

**Approach and files touched.**

- Move `TestGtkThemeViews.test_flowbox_child_selected_arms` from
  `tests/test_gtk_theme_views.py` to
  `tests/test_gtk_theme_selected_views.py::TestGtkThemeSelectedViews`,
  after `test_iconview_selected_arms`. Keep its body and docstring the
  same. It calls only `assert_rule` from
  `support.gtk_rule_cases.GtkSheetRuleCases`, which the destination already
  inherits, and the destination already sets the same GTK 3 `CSS_PATH`. It
  reads `BLACK` and `SELECTION`, which the destination already imports from
  `support.platinum_palette`, so the destination's import block does not
  change.
- In the views module, drop `BLACK` and `SELECTION` from the
  `support.platinum_palette` import only if no method left in the module
  reads them at implementation time (on 2026-11-19 only the moved method
  did). If that leaves the import empty, remove the whole import statement.
- Widen the destination's module docstring to say it also covers selected
  flow-box children.
- In the views module docstring, extend the existing "Selected icon-view
  fill and selected treeview check and radio faces are in
  `tests/test_gtk_theme_selected_views.py`" sentence to name selected
  flow-box children too. Write it against the docstring as it reads at
  implementation time.
- In `docs/invariants.md`, repoint the
  `tests/test_gtk_theme_views.py::TestGtkThemeViews::test_flowbox_child_selected_arms`
  anchor to
  `tests/test_gtk_theme_selected_views.py::TestGtkThemeSelectedViews::test_flowbox_child_selected_arms`.
  A grep on 2026-11-19 found it once, in the "GTK 3 selected flow-box
  children restate the existing row-selection treatment" row. Keep that
  row's wording.
- Grep `docs/rendering.md`, `docs/fidelity.md`,
  `tests/test_ci_workflow.py` and `tests/support/` (including
  `tests/support/validation_gaps/*.py`) for the old anchor and repoint any
  hit. The 2026-11-19 grep found none outside `docs/invariants.md`. This is
  not a render gate, so the `_GATE_FILES` lists are not involved.
- Do not change theme sheets, source partials or the
  `test_row_selection_backdrop` method, which stays in the views module.

**Acceptance criteria.**

- Test discovery lists `test_flowbox_child_selected_arms` under
  `test_gtk_theme_selected_views.TestGtkThemeSelectedViews` and no longer
  under `test_gtk_theme_views.TestGtkThemeViews`. The selected-views suite
  still lists `test_iconview_selected_arms` and
  `test_treeview_selected_check_radio_faces`. Both modules pass when run on
  their own through the project's unittest runner.
- The moved method's function-definition AST is identical to the original
  at the base commit.
- With the test in its new suite, changing `background-color` in the GTK 3
  sheet's `flowbox flowboxchild:selected` rule fails it. So does deleting
  the `flowbox flowboxchild:backdrop:selected` rule.
- The `docs/invariants.md` flow-box anchor resolves to an existing method.
  After the change, a grep finds no `test_flowbox_child_selected_arms` in
  `tests/test_gtk_theme_views.py`, and every name that module imports from
  `support.platinum_palette` is still read in it.
- `git diff --stat` shows changes only to the two test modules,
  `docs/invariants.md` and the backlog files. Theme sheets, partials and
  generated files have no diff.
- `make check` passes after the final edit.

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
