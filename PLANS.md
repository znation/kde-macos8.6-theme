# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### GTK 3 suite extraction: isolate embedded entry-icon declarations (planned 2026-11-19 by the plan role)

**Goal.** Give embedded entry-icon ink and spacing coverage a focused
module, independent of the waiting OSD push-button extraction.

**Approach and files touched.** Move
`TestGtkThemeEntry.test_entry_image_inks` from
`tests/test_gtk_theme_entry.py` to
`tests/test_gtk_theme_entry_images.py::TestGtkThemeEntryImages`, retaining
its method name, assertion body and provenance comments. Follow
`tests/test_gtk_theme_entry_tags.py`: inherit `GtkSheetRuleCases` and
`unittest.TestCase`, bind `CSS_PATH` to the shipped GTK 3 sheet through
`support.repo_root.ROOT`, and include the unittest main guard. Import
`strip_comments` from `support.gtk_css` and `BLACK` from
`support.platinum_palette`. This method has no source-local helper
dependency. Keep the progress probe, focus, colour-class and state-face
checks in the source module; retain imports they still use and update
its routing docstring. Repoint the embedded GTK 3 entry-icon row in
`docs/invariants.md`, preserving its recipe and provenance. Search live
docs and tests, including `docs/rendering.md`, `docs/fidelity.md`,
`tests/test_ci_workflow.py` and `tests/support/validation_gaps/`, for
other moved qualified anchors. No production or stylesheet changes.

**Acceptance criteria.**

- Discovery and a focused run execute the moved method under its new
  class without a GUI display; the source class no longer defines it.
- Given the shipped sheet, the moved check passes. A wrong icon ink,
  swapped side margin, missing or duplicate declaration, extra selector
  in the filtered icon family, or icon block preceding the base field
  anchor fails its retained assertions.
- The remaining entry suite runs independently with its existing GUI
  isolation and skip conditions. Live qualified anchors resolve to the
  moved method. Theme assets, source partials and generated sheets have
  no diff.
- `make check` passes after the final edit.

### GTK 3 suite extraction: isolate vertical-stepper and content-view check corner declarations (planned 2026-11-19 by the plan role)

**Goal.** Give the GTK 3 vertical spin-button stepper halves and the
content-view tile-check faces a focused module. This is the largest
method still in `tests/test_gtk_theme_views.py`. The plan is independent
of the waiting entry-icon and list-row press/popup extractions: it moves
a different method, and its only shared file is the views module, where
it touches a different method and different import names.

**Approach and files touched.** Move
`TestGtkThemeViews.test_vertical_stepper_and_content_view_check_corners`
from `tests/test_gtk_theme_views.py` to
`tests/test_gtk_theme_stepper_check_corners.py::TestGtkThemeStepperCheckCorners`.
Keep its method name, docstring, assertion body and provenance comments.
Follow `tests/test_gtk_theme_content_views.py` for the module's shape:
inherit `GtkSheetRuleCases` and `unittest.TestCase`, bind `CSS_PATH` to
the shipped GTK 3 sheet through `support.repo_root.ROOT`, and end with
the unittest main guard. Give the module a short docstring saying what it
pins. Import `CHECK_GLYPH`, `SELECTION_CHECK_STATES` and
`TILE_CHECK_FACE` from `support.gtk_theme_spec`. The method uses no
helper local to the source module.

In the source module, drop the `CHECK_GLYPH` and `TILE_CHECK_FACE`
imports, which no remaining method uses. Keep `SELECTION_CHECK_STATES`,
because `test_iconview_selected_arms` still uses it, and keep every other
import a remaining method uses. Add a routing sentence for the new module
to the views module docstring.

In the `docs/invariants.md` `## gtk` vertical spin-button stepper row,
repoint the `tests/test_gtk_theme_views.py::TestGtkThemeViews::…` anchor
to the new module and class. Keep the row's second anchor
(`test_gtk_theme_spinbutton.py`), its recipe and its provenance. A grep
on 2026-11-19 found no other live reference to the moved method in
`docs/`, `tests/test_ci_workflow.py`, `tests/support/validation_gaps/`
or the Makefile; the PLANS-DONE.md mentions are history and stay. Grep
again before editing. No production, stylesheet or theme-asset changes.

**Acceptance criteria.**

- Discovery and a focused run
  (`python3 -m unittest test_gtk_theme_stepper_check_corners` from
  `tests/`) execute the moved method under its new class without a GUI
  display. `TestGtkThemeViews` no longer defines it.
- Against the shipped sheet, the moved check passes. Each of the
  following fails a retained assertion:
  - a wrong stepper `border-style` half or a non-zero radius;
  - a missing glyph on a checked tile spelling;
  - a dropped or folded `:not(list)` guard;
  - an extra rule carrying the `content-view.check` or the
    `spinbutton.vertical button.up` token;
  - a duplicated spelling;
  - a moved spelling that sits before the bare `check` recipe.
- The remaining views suite runs on its own and passes. Its module
  imports no name it does not use.
- The invariants row's anchor resolves to the moved method; the
  invariants tests in `make check` pass.
- Theme assets, source partials and generated sheets have no diff.
- `make check` passes after the final edit.

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
