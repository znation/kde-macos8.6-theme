# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### GTK 3 suite extraction: isolate selected icon-view and treeview check/radio declarations (planned 2026-11-19 by the plan role)

**Goal.** Give the GTK 3 selected-view arms a focused module outside the
oversized views suite: the selected icon-view fill and the selected
treeview-row check and radio faces. This is independent of the waiting
entry-icon, list-row press and vertical-stepper/content-view check corner
extractions.

**Approach and files touched.** Move
`TestGtkThemeViews.test_iconview_selected_arms` and
`TestGtkThemeViews.test_treeview_selected_check_radio_faces` from
`tests/test_gtk_theme_views.py` to new
`tests/test_gtk_theme_selected_views.py::TestGtkThemeSelectedViews`. Keep
their method names, assertion bodies and comments as they are. Follow
`tests/test_gtk_theme_server_button.py`: inherit
`support.gtk_rule_cases.GtkSheetRuleCases` and `unittest.TestCase`, set
`CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"` via
`support.repo_root.ROOT`, and include the unittest main guard. Import
`MIXED_GLYPH`, `RADIO_GLYPH` and `SELECTION_CHECK_STATES` from
`support.gtk_theme_spec`, and `BLACK` and `SELECTION` from
`support.platinum_palette`. Neither method uses a source-local helper.
In the source module, drop `MIXED_GLYPH` and `RADIO_GLYPH` (only the
moved treeview test uses them). Drop `SELECTION_CHECK_STATES` only if
no remaining method references it: today
`test_vertical_stepper_and_content_view_check_corners` still does,
unless the pending stepper-corner extraction has merged first. Keep
`BLACK` and `SELECTION`, which `test_flowbox_child_selected_arms` and
others still use. Add the new module to the source's routing docstring.
Two other edits:
- In `docs/invariants.md`, repoint only the Gtk 3 anchors of the
  selected-treeview check/radio row and of the enabled-selected icon-view
  row. Keep that row's Gtk 4 anchor
  (`tests/test_gtk4_selection_focus.py::TestGtk4SelectionFocus::test_iconview_selected_arms`),
  the guarantee and the provenance text unchanged.
- In `tests/support/gtk_theme_spec.py`, update the comment above
  `SELECTION_CHECK_STATES` that names each reader's module, so
  `test_iconview_selected_arms` is attributed to the new module. Each
  other reader stays named under whatever module holds it when you
  implement this. The "Exactly four tests" count is unchanged by this
  move; recount it with grep before keeping it.

A grep of `docs/` and `tests/` on 2026-11-19 found no other live
reference to either moved method. Recheck `docs/rendering.md`,
`docs/fidelity.md`, `tests/test_ci_workflow.py` and
`tests/support/validation_gaps/` before finishing. No theme, partial or
generated-sheet changes.

**Acceptance criteria.**

- Discovery runs both moved methods under the new class without a GUI
  display. `TestGtkThemeViews` defines neither one, and both modules pass
  when run on their own.
- The moved checks pass against the shipped sheet. Each of these
  mutations fails one of them:
  - giving a selected icon-view arm a non-`#CCCCFF` fill or a non-zero
    radius;
  - adding a stray `iconview` selector;
  - replacing the selected treeview check's black border;
  - swapping the checked-selected radio glyph for another asset;
  - adding a seventh `treeview.view check`/`radio` selector;
  - moving a restated treeview spelling ahead of `radio:checked`.
- Every module and test named in the `SELECTION_CHECK_STATES` comment
  exists and reads the constant. Each invariants row's Gtk 3 anchor
  resolves to its moved method, and the icon-view row's Gtk 4 anchor is
  unchanged. Theme assets, source partials and generated sheets have no
  diff.
- `make check` passes after the final edit.

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
