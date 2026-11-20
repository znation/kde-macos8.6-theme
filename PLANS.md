# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Group the flat tools/ modules into per-subsystem packages (planned 2026-11-19 by the organize role)

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

### Render-surface suite extraction: isolate the splash gate's measured logo-cell map (planned 2026-11-19 by the plan role)

**Goal.** Shrink the 1278-line `tests/test_render_surface.py` by moving
the splash gate's measured pixel map out of the gate's assertions.
`TestSplashRender.LOGO_CELL_ROWS` (42 rows of 52 `#RRGGBB` strings) takes
up about 460 lines of the module. This follows the merged list-row fixture
extraction (`tests/support/file_dialog_list_fixtures.py`) and the waiting
file-dialog sidebar-map entry. It is independent of that entry, which edits
only `tests/test_render_file_dialog.py`, and of every waiting GTK 3 suite
extraction, which touch only `tests/test_gtk_theme_*.py` and
`docs/invariants.md`'s `## gtk` rows.

**Approach and files touched.**

- Add `tests/support/splash_capture_fixtures.py`. Don't reuse
  `tests/support/splash_fixtures.py`: that module holds the QML probes and
  reference loader for the shipped splash's source tests, not
  measurements from a render. Give the new module a docstring in the style
  of `file_dialog_list_fixtures.py`. It should say the map was measured
  from the 2026-11-11 `--splash` capture runs that `TestSplashRender`'s
  class docstring names, and that the owning assertion stays in
  `tests/test_render_surface.py`.
- Move `TestSplashRender.LOGO_CELL_ROWS` into it as a module-level
  `LOGO_CELL_ROWS`, keeping the literal as it is. Bring along the
  measurement comment above it: read from the first run, confirmed
  byte-equal in the other two, and a moved, dropped or resampled logo
  fails the byte-compare. Reword "named in the class docstring" so it
  names `TestSplashRender` in `tests/test_render_surface.py`.
- Keep the geometry and colour constants in the class (`LOGO_CELL`,
  `BEVEL_BOX`, `PANEL_BOX`, `PANEL_FACE`, `WORDMARK_BAND`, `TRACK_BOX`,
  `TRACK_FILL` and the `*_COLOUR` values), along with the class docstring.
- In `tests/test_render_surface.py`, import the module as
  `from support import splash_capture_fixtures` beside the other `support`
  imports. Have `test_the_logo_cell_pins_its_art` pass
  `splash_capture_fixtures.LOGO_CELL_ROWS` to `assert_band`, and reword its
  "the measured map above" comment so it names the support module. Test
  names and assertion logic don't change. The module-level
  `Renders.request("applet", "desktop", "splash")` call and every skip
  guard also stay as they are.
- The planning grep found `LOGO_CELL_ROWS` only in
  `tests/test_render_surface.py` outside the archives: nothing in `docs/`,
  `README.md`, `PLACEHOLDERS.md`, `tests/test_ci_workflow.py`,
  `tests/support/validation_gaps/*.py` or the `_GATE_FILES` lists. Re-grep
  at implementation. No production code, theme file, render kind or gate
  class moves.

**Acceptance criteria.**

- `tests/support/splash_capture_fixtures.py` exposes `LOGO_CELL_ROWS` as
  42 rows of 52 `#RRGGBB` strings. It equals the class attribute it
  replaces on main, as an `ast.literal_eval` comparison of the old and new
  literals shows (no render needed).
- `TestSplashRender` no longer defines `LOGO_CELL_ROWS`, and
  `tests/test_render_surface.py` holds no other copy of the map. The
  module is shorter by roughly the map's size.
- Test discovery lists the same `tests/test_render_surface.py` test IDs as
  before. On a host with the splash tools, the logo-cell test still
  byte-compares the same 52x42 cell at (294, 110). Without the tools it
  skips under the existing guard, as before.
- Importing the new support module starts no GUI process, render session
  or capture.
- `make check` passes after the final edit.

### Firefox Library suite extraction: move the downloads and details-pane suites into their own module (planned 2026-11-19 by the plan role)

**Goal.** Shrink the 864-line `tests/test_firefox_theme_library.py` so it
stays on one concern: the Library window's trees, search box, column
headers and toolbar. Its last two classes, `TestFirefoxLibraryDownloadsChrome`
and `TestFirefoxLibraryDetailsPaneChrome`, pin the downloads view, the Clear
Downloads button and the details pane. Together with their constants they
come to about 420 lines. This entry is independent of every waiting entry:
none of them touches `tests/test_firefox_theme_*.py`,
`tests/support/firefox_chrome_cases.py`, `tests/support/css_header.py` or
`docs/invariants.md`'s Firefox Library rows.

**Approach and files touched.**

- Add `tests/test_firefox_theme_library_panes.py`. Give it a docstring in the
  style of the existing one: it validates the Library window's downloads
  list with its Clear button and the details pane's fields, rows and tag
  selector for the standalone `userChrome.css`, and it points to
  `test_firefox_theme_library.py` for the trees, search box, headers and
  toolbar. No existing `tests/test_firefox_theme_*.py` module covers these
  panes (checked with `ls` at planning time), so a new module is the right
  move, not a merge into a sibling.
- Move these into it verbatim, with their comments: the module constants
  `DOWNLOADS_RULES`, `CLEAR_BUTTON_RULES`, `DETAILS_FIELD_RULES`,
  `DETAILS_MENULIST_RULES`, `DETAILS_TAGS_RULES` and `DETAILS_RULES`, plus both
  classes. Class names, docstrings, test names and bodies don't change. At
  planning time, a grep showed that the two classes use only
  `REQUIRED_RULES` and `FirefoxChromeTestCase` from
  `support.firefox_chrome_cases`, plus `element` and `matches` from
  `support.selector_matching`. They use no `support.platinum_palette` name
  and none of `TREE_RULES`, `SEARCH_RULE`, `HEADER_FACE_ARMS`,
  `HEADER_HOVER_ARMS` or `TOOLBAR_RULES`. The staying classes don't use
  the moved constants either. Re-check both directions with grep. The new
  module must not import from `test_firefox_theme_library.py`.
- In `tests/test_firefox_theme_library.py`, delete the moved constants and
  classes. Drop any import that is now unused (re-check each name with
  grep). Rewrite the module docstring so it names only the surfaces that
  stay, and add one sentence pointing to `test_firefox_theme_library_panes.py`.
- `docs/invariants.md`: the downloads-view row anchors
  `tests/test_firefox_theme_library.py::TestFirefoxLibraryDownloadsChrome`
  and the details-pane row anchors
  `tests/test_firefox_theme_library.py::TestFirefoxLibraryDetailsPaneChrome`.
  Re-point both to `tests/test_firefox_theme_library_panes.py`. The other
  four Library rows keep their anchors.
- Prose that names the module: add `tests/test_firefox_theme_library_panes.py`
  to the section-module lists in the docstrings of
  `tests/support/firefox_chrome_cases.py` and `tests/support/css_header.py`.
  Re-point the comment in `tests/test_firefox_theme_panels.py` that says the
  Library's own `#downloadsListBox` rules "have their own suite in
  tests/test_firefox_theme_library.py" to the new module. The docstring of
  `FirefoxChromeTestCase.assert_arms_match_required` says "The four Library
  chrome suites". That counts classes, not modules, and stays true, so leave it.
- At planning time, a grep for the two class names and the moved constant
  names found no anchors in `README.md`, `docs/rendering.md`,
  `docs/fidelity.md`, `tests/test_ci_workflow.py` or
  `tests/support/validation_gaps/*.py`. Re-grep at implementation.
- No change to theme files, production code or the Makefile.

**Acceptance criteria.**

- Test discovery lists every test ID of `TestFirefoxLibraryDownloadsChrome`
  and `TestFirefoxLibraryDetailsPaneChrome` under
  `test_firefox_theme_library_panes` and none under
  `test_firefox_theme_library`. The remaining `test_firefox_theme_library`
  IDs (the trees, search, header and toolbar classes) are the same as on
  main.
- `tests/test_firefox_theme_library.py` no longer defines the two classes
  or the six moved constants. Each import it still has is used, as a grep
  for each name shows.
- `docs/invariants.md`'s downloads-view and details-pane rows name
  `tests/test_firefox_theme_library_panes.py::<Class>`, and
  `tests/support/invariants.py`'s register cross-check passes. Outside the
  archives, a grep for `test_firefox_theme_library.py::TestFirefoxLibraryDownloadsChrome`
  or `test_firefox_theme_library.py::TestFirefoxLibraryDetailsPaneChrome`
  finds nothing.
- `make check CHECK_PATTERN='test_firefox_theme_*.py'` passes, and
  `make check` passes after the final edit.

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
