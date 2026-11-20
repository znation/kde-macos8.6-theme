# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### GTK 3 OSD suite extraction: isolate overlay-band declarations (planned 2026-11-19 by the plan role)

**Goal.** Give OSD overlay-container declaration coverage a focused module
outside `tests/test_gtk_theme_osd.py`, independently of the waiting
destructive-action extraction.

**Approach and files touched.** Move
`TestGtkThemeOsd.test_osd_overlay_bands` unchanged into
`tests/test_gtk_theme_osd_overlay.py::TestGtkThemeOsdOverlay`.
Follow `tests/test_gtk_theme_view_focus.py`: inherit `GtkSheetRuleCases`
and `unittest.TestCase`, set `CSS_PATH` to the shipped GTK 3 sheet through
`support.repo_root.ROOT`, and include the unittest main guard. Import
`ETCH_DARK` from `support.gtk_theme_spec` and `BLACK`, `FACE` and `WHITE`
from `support.platinum_palette`. The moved method uses no source-local
helper. Remove the source module's now-unused `WHITE` import; retain its
other required imports and the separate colorchooser-corner check.
Update the source routing docstring to point to the new module and
repoint the overlay-container row in `docs/invariants.md`, preserving
its recipe, missing-reference and toolkit provenance. Search live docs
and tests, including `docs/rendering.md`, `docs/fidelity.md`,
`tests/test_ci_workflow.py` and `tests/support/validation_gaps/`, for
other moved qualified anchors. No production or stylesheet changes.

**Acceptance criteria.**

- Discovery and a focused run execute the moved method under its new
  class without a GUI display; the source class no longer defines it.
- Given the shipped sheet, the moved check passes. A wrong overlay face,
  bottom border, highlight or shadow declaration fails its retained
  assertions, as does an unexpected selector within its filtered family.
- The remaining OSD suite runs independently. Live invariant anchors
  resolve to the moved method, with no stale qualified references to it
  in live docs or tests. Theme assets, source partials and generated
  sheets have no diff.
- `make check` passes after the final edit.

### GTK 3 OSD suite extraction: isolate flat-button declarations (planned 2026-11-19 by the plan role)

**Goal.** Give the OSD flat-button declaration inventory a focused module,
independent of the waiting overlay-band and pending destructive-action
extractions, keeping each test file easier to read.

**Approach and files touched.** Move
`TestGtkThemeOsd.test_osd_flat_button` from `tests/test_gtk_theme_osd.py`
to `tests/test_gtk_theme_osd_flat.py::TestGtkThemeOsdFlat`, retaining
its method name, assertion body, selector exclusions and provenance
docstring. Follow `tests/test_gtk_theme_osd_suggested.py`: inherit
`OsdSelectorAssertions`, `GtkSheetRuleCases` and `unittest.TestCase`,
bind `CSS_PATH` to the shipped GTK 3 sheet through `support.repo_root.ROOT`,
and include the unittest main guard. Import `BUTTON_BEVEL`,
`INVERTED_BUTTON_BEVEL` and `ETCH_DARK` from `support.gtk_theme_spec`,
and `BLACK` and `FACE` from `support.platinum_palette`. The existing
`support.gtk_osd_cases` helper suffices; the method has no source-local
helper dependency. Keep `test_scale_popup_buttons` in the source module,
along with imports still used by its remaining methods. Update the source
routing docstring and `test_osd_button` inventory comment to identify the
new flat-button module. In `docs/invariants.md`, repoint both the OSD
flat-button row and the linked-field end-corner row's extended-test anchor,
preserving their recipes and provenance. Search live docs and tests,
including `docs/rendering.md`, `docs/fidelity.md`,
`tests/test_ci_workflow.py` and `tests/support/validation_gaps/`, for other
moved qualified anchors. No production or stylesheet changes.

**Acceptance criteria.**

- Discovery and a focused run execute the moved method under its new
  class without a GUI display; the source class no longer defines it.
- Given the shipped sheet, the moved check passes. An incorrect flat-button
  face or active bevel, disabled ink, disabled/backdrop source ordering,
  or unexpected selector in its filtered inventory fails its retained
  assertions. Existing exclusions, including the scale-popup arm, remain
  covered by the same inventory assertion.
- The remaining OSD module runs independently. Live qualified anchors for
  the moved method resolve to its new class, including both invariant rows.
  Theme assets, source partials and generated sheets have no diff.
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
