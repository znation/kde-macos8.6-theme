# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Group the flat tools/ modules into per-subsystem packages (planned 2026-11-19 by the organize role)

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

### Firefox panels suite extraction: move the bookmark-editor cases into their own module (planned 2026-11-19 by the plan role)

**Goal.** Shrink the 743-line `tests/test_firefox_theme_panels.py` and keep
it on one concern, the popup panels' row and button paints. Its single class,
`TestFirefoxPanelRows(FirefoxChromeTestCase)`, also holds the two cases that
pin the bookmark editor (`#editBookmarkPanel` and the Library's
`#bookmarkpropertiesdialog` fields), which are not row paints. They are the
last two methods of the class and take up about a third of the file:
`test_bookmark_panel_control_paint_is_scoped_to_the_bookmark_panel` and
`test_bookmark_panel_provenance`.

**Independence.** The module defines no module-level constants or helpers.
The two bookmark cases use only `FirefoxChromeTestCase` methods
(`assert_rule_names_scoped_to`, `assert_rules_match_required`,
`assert_header_names`, `self.rules`), `element` and `matches` from
`support.selector_matching`, and `BUTTON_REFERENCES` and
`VIEWITEM_REFERENCES` from `support.firefox_chrome_cases`. They do not use
`FACE` or `SELECTION`, which only the staying downloads and all-tabs cases
use. So no `tests/support` module is needed. This plan is independent of the
waiting "Firefox Library suite extraction: move the downloads and
details-pane suites into their own module" plan, which moves code out of
`tests/test_firefox_theme_library.py`, not this file. The two plans do edit
the same module-list sentences in the two support docstrings named below.
Whichever plan merges second keeps the other's module name in those lists.

**Approach.**

1. Create `tests/test_firefox_theme_bookmark_editor.py`. Give it a module
   docstring saying it validates the Firefox Platinum sheet's bookmark-editor
   paints (the `#editBookmarkPanel` fields, folder dropdown and footer
   buttons) for the standalone `userChrome.css`. Add one class,
   `TestFirefoxBookmarkEditor(FirefoxChromeTestCase)`. It imports
   `BUTTON_REFERENCES`, `VIEWITEM_REFERENCES` and `FirefoxChromeTestCase`
   from `support.firefox_chrome_cases`, and `element` and `matches` from
   `support.selector_matching`. The file ends with the same
   `if __name__ == "__main__": unittest.main()` footer the source module
   uses.
2. Move the two methods into that class verbatim, with no change to their
   bodies.
3. In `tests/test_firefox_theme_panels.py`, delete the two methods. Drop
   "and the bookmark panel" from the module docstring's list. Keep every
   import, because the staying cases still use each one.
4. In `docs/invariants.md`, the bookmark editor's row (it begins "The
   bookmark editor's fields") names
   `tests/test_firefox_theme_panels.py::TestFirefoxPanelRows`. Point that
   anchor at `tests/test_firefox_theme_bookmark_editor.py::TestFirefoxBookmarkEditor`.
   Leave the other rows that name `TestFirefoxPanelRows` alone, because
   their cases stay.
5. Add `tests/test_firefox_theme_bookmark_editor.py` to the section-module
   lists in the docstrings of `tests/support/firefox_chrome_cases.py`
   (the "The sections live in …" sentence) and `tests/support/css_header.py`
   (the provenance-test call-site list).
6. Before finishing, re-run
   `grep -rn 'test_firefox_theme_panels\|TestFirefoxPanelRows' docs tests README.md Makefile`
   and `grep -rn 'test_bookmark_panel_' docs tests README.md`. Every hit
   must name a case that is still in the named file. Following L1, also
   check `docs/rendering.md`, `docs/fidelity.md`,
   `tests/test_ci_workflow.py` and `tests/support/validation_gaps/*.py`.
   At planning time they held no anchor for this module.

**Files touched.** `tests/test_firefox_theme_panels.py`,
`tests/test_firefox_theme_bookmark_editor.py` (new),
`tests/support/firefox_chrome_cases.py`, `tests/support/css_header.py`,
`docs/invariants.md`.

**Acceptance criteria.**

- `grep -rn 'def test_bookmark_panel_' tests` finds exactly two
  definitions, both in `tests/test_firefox_theme_bookmark_editor.py` under
  `TestFirefoxBookmarkEditor`. Their bodies are identical to the removed ones
  (compare with `git diff --color-moved`).
- `tests/test_firefox_theme_panels.py` still defines the six row and button
  cases (downloads list, downloads buttons, all-tabs, app menu, overflow,
  unified extensions) and no bookmark-editor case. Its docstring no longer
  mentions the bookmark panel.
- The bookmark-editor invariant row in `docs/invariants.md` names the new
  module's class, and `tests/test_invariants.py` passes.
- `make check CHECK_TESTS='test_firefox_theme_panels test_firefox_theme_bookmark_editor test_invariants'`
  passes, and `make check` passes after the final edit.

### Firefox popup suite extraction: isolate notification-doorhanger button checks (planned 2026-11-20 by the plan role)

**Goal.** Give notification-doorhanger button paint and provenance a focused
suite, leaving identity, protections and trust row checks in the popup suite.
This is independent of the queued bookmark-editor extraction and the pending
menubar extraction; preserve their additions to shared documentation lists.

**Approach and files touched.**

- Create `tests/test_firefox_theme_notification_popup.py` with
  `TestFirefoxNotificationPopup(FirefoxChromeTestCase)`. Move
  `test_notification_popup_primary_button_paint_is_scoped_to_the_notification_popup`
  and `test_notification_popup_provenance` from
  `tests/test_firefox_theme_popups.py` verbatim, including comments and
  formatting. Import `unittest`, `REQUIRED_RULES`, `VIEWITEM_REFERENCES` and
  `FirefoxChromeTestCase` from the same sources as the popup suite, and
  `element` and `matches` from `support.selector_matching`. Include a focused
  docstring and the usual unittest main footer. The methods need no local
  helper extraction.
- Remove the moved methods from the popup suite and remove notification
  popups from its docstring's coverage list. Drop the now-unused
  `VIEWITEM_REFERENCES` import; keep the imports used by the staying cases.
- Add the new module to the section list in
  `tests/support/firefox_chrome_cases.py` and the provenance list in
  `tests/support/css_header.py`. Remove the popup module from the latter
  list, since its remaining methods do not call `assert_header_names`.
- In `docs/invariants.md`, point the notification-doorhanger primary-button
  row at the new module and class, preserving the method name and guarantee.
  Search docs, tests, README and Makefile for both moved names and the old
  module/class anchors; update references to moved coverage, preserving
  references to staying coverage. Include `docs/rendering.md`,
  `docs/fidelity.md`, `tests/test_ci_workflow.py` and
  `tests/support/validation_gaps/*.py` in this check (L1).

**Acceptance criteria.**

- Unittest discovery exposes both named methods under
  `test_firefox_theme_notification_popup.TestFirefoxNotificationPopup`,
  with their pre-move bodies intact and no definitions in the popup suite.
  Their existing primary-button token, selector-isolation and provenance
  assertions pass against the shipped sheet.
- Identity, protections and trust row checks remain discoverable in
  `TestFirefoxPopupRows` and pass. The invariant register resolves the
  notification-doorhanger method at its new path. The shared documentation
  lists describe where section and provenance checks now live.
- No shipped stylesheet or artwork changes. The focused check
  `make check CHECK_TESTS='test_firefox_theme_popups test_firefox_theme_notification_popup test_invariants'`
  passes, followed by `make check` after the final edit.

## Done

### Firefox Page Info suite extraction: isolate meta and image tree declarations (planned 2026-11-20 by the plan role) — done 2026-11-20 by the review role

**Goal.** Give Page Info's meta and image trees a focused declaration suite,
reducing the mixed-surface `tests/test_firefox_theme_page_info.py`. This is
independent of the bookmark-editor and preferences extractions; its paint
and provenance checks form one concern and move together.

**Approach and files touched.**

- Create `tests/test_firefox_theme_page_info_trees.py` with
  `TestFirefoxPageInfoTrees(FirefoxChromeTestCase)`. Move
  `test_page_info_tree_paint_is_scoped_to_page_info` and
  `test_page_info_tree_provenance` from `TestFirefoxPageInfo` verbatim.
  Import `REQUIRED_RULES`, `VIEWITEM_REFERENCES` and `FirefoxChromeTestCase`
  from `support.firefox_chrome_cases`, and `element` and `matches` from
  `support.selector_matching`. Include the usual unittest footer. These
  methods need no new shared helper or import from another test module.
- Remove the moved methods from `tests/test_firefox_theme_page_info.py`.
  Narrow its docstring and point readers to the new suite for the trees;
  describe the tree scope in the new module's docstring. Retain imports
  needed by the remaining checks.
- In `docs/invariants.md`, re-point the meta-and-image-tree row's scope-test
  anchor to the new module and class, preserving the guarantee and provenance.
  Add the new module to the suite lists in
  `tests/support/firefox_chrome_cases.py` and `tests/support/css_header.py`,
  preserving names added by other extractions.
- Search the old module/class anchors and moved method names across docs,
  tests, README and Makefile, including `docs/rendering.md`,
  `docs/fidelity.md`, `tests/test_ci_workflow.py` and
  `tests/support/validation_gaps/`. Update live anchors for the moved checks;
  historical plans remain historical. At planning time, the moved scope-test
  anchor appeared in `docs/invariants.md`.

**Acceptance criteria.**

- Discovery finds the moved methods under
  `test_firefox_theme_page_info_trees.TestFirefoxPageInfoTrees` and no longer
  under the original class; their assertion bodies and comments match the
  removed methods. The original class retains its other method bodies.
- The new suite passes against the shipped sheet, checking the meta/image
  tree rules, unrelated-tree exclusions and provenance; the remaining Page
  Info suite passes independently.
- The tree invariant resolves to the new scope-test location, and the support
  docstrings list the new suite. No live fully qualified anchor for a moved
  method points to the original class.
- `make check` passes after the final edit. The implementation diff contains
  test organization and documentation changes, with no shipped theme changes.

**Review verification.** Restored the moved method text against the supplied
diff; checked imports, invariant anchors and suite inventories. Tumwater owns
test execution; the reviewer did not run the suite.

### Firefox popup suite extraction: isolate permission-control declarations (planned 2026-11-20 by the plan role) — done 2026-11-20 by the feature role

**Goal.** Separate the permission popup's remove-button and dropdown checks
from the row-paint suite in `tests/test_firefox_theme_popups.py`. Moving its
permission method brings that currently 615-line module below 500 lines.
This is independent of the queued bookmark-editor and Page Info extractions.

**Approach and files touched.**

- Create `tests/test_firefox_theme_permission_popup.py` with
  `TestFirefoxPermissionPopup(FirefoxChromeTestCase)`. Move
  `test_permission_popup_control_paint_is_scoped_to_the_permission_popup`
  from `TestFirefoxPopupRows`, preserving its body and comments. Import
  `REQUIRED_RULES` and `FirefoxChromeTestCase` from
  `support.firefox_chrome_cases`, and `element` and `matches` from
  `support.selector_matching`. Add a scope docstring and the usual
  `unittest.main()` guard. No helper extraction or test-module import is
  needed: the method uses those support imports and local fixtures only.
- Remove the method from `tests/test_firefox_theme_popups.py` and remove
  permission from its scope docstring, pointing readers to the new suite.
  Its existing imports remain used by the staying methods.
- Re-point the permission-popup control row's declaration-test anchor in
  `docs/invariants.md` to the new module and class, preserving its visual
  reference anchors and provenance. Add the new module to the section list
  in `tests/support/firefox_chrome_cases.py`, retaining sibling additions.
  Leave the permission provenance assertions in the shell suite in place;
  the new suite has no provenance method, so it does not belong in
  `tests/support/css_header.py`'s provenance-call-site list.
- Search the moved method and old class/module names across docs and tests,
  including `docs/rendering.md`, `docs/fidelity.md`,
  `tests/test_ci_workflow.py` and `tests/support/validation_gaps/`, and
  correct any additional live anchor for the moved method. Historical
  backlog entries remain historical. Theme sheets and production tools
  are outside this relocation.

**Acceptance criteria.**

- Discovery exposes the moved method under
  `test_firefox_theme_permission_popup.TestFirefoxPermissionPopup`, with
  its assertion body preserved and no definition remaining in the original
  module. The original class retains its pre-change method set minus that
  method, and its module is below 500 lines.
- The new suite passes against the shipped sheet: the permission remove
  button and dropdown match their scoped normal and enabled-hover rules,
  disabled controls do not match hover rules, and surrounding elements and
  controls outside the popup remain excluded by the existing fixtures.
- The permission-control invariant resolves to the new declaration test;
  the existing shell provenance check still passes, and no live anchor
  outside historical backlog records names the moved method's old location.
- The focused popup, permission-popup, shell and invariants suites pass
  through the existing check runner; `make check` passes after the final edit.

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
