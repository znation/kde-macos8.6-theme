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

### Terminal palette: move the classic 16-colour table out of the Ghostty test into support (planned 2026-11-21 by the plan role; independent of the waiting tests/support regroup, desktop wallpaper, GTK rule cases and Makefile refusal parts)

**Goal.** `tests/test_konsole_theme.py` imports `PALETTE` from another test
module (`from test_ghostty_theme import PALETTE`), so loading the Konsole
suite also loads, and couples it to, the Ghostty suite. Move the classic
16-colour table into a new support module both suites import, so no test
module imports another. No test is added, removed or renamed and no shipped
colour changes.

**Approach.**

- New `tests/support/terminal_palette.py`: a module docstring saying it
  holds the classic Platinum-era 16-colour system table, ANSI slot -> colour,
  that no reference screenshot shows a terminal so the table itself is the
  contract, and that slots 12 and 14 repeat 4 and 6 (no bright blue or
  bright cyan). Then `PALETTE` verbatim, with the comment that sits above it
  in `tests/test_ghostty_theme.py`.
- `tests/test_ghostty_theme.py`: delete `PALETTE` and its comment; add
  `from support.terminal_palette import PALETTE`. Its module docstring's
  "pinned against the table written below" becomes a pointer to
  `tests/support/terminal_palette.py`.
- `tests/test_konsole_theme.py`: replace `from test_ghostty_theme import
  PALETTE` with `from support.terminal_palette import PALETTE`; its module
  docstring's "pinned in `tests/test_ghostty_theme.py`" names the support
  module instead.
- Retarget the other prose pointers to the table: the Ghostty and Konsole
  rows of `docs/invariants.md` (the Konsole row names
  `tests/test_ghostty_theme.py` as where the table is pinned; keep each
  row's test-file column as it is) and the source comment in
  `theme/konsole/MacOS8.colorscheme` ("as tests/test_ghostty_theme.py pins
  it"). Touch only that comment line in the colorscheme, no colour value.

**Files touched.** new `tests/support/terminal_palette.py`,
`tests/test_ghostty_theme.py`, `tests/test_konsole_theme.py`,
`docs/invariants.md`, `theme/konsole/MacOS8.colorscheme` (comment only).

**Acceptance criteria.**

- `rg -n '^PALETTE = ' tests` finds only `tests/support/terminal_palette.py`.
- `rg -n 'from test_ghostty_theme|import test_ghostty_theme' tests` finds
  nothing, and `rg -n 'test_ghostty_theme' docs theme tests/test_konsole_theme.py`
  finds no claim that the table is pinned there (the invariants Ghostty
  row's test-file column may still name the module).
- Loading the Konsole suite alone no longer loads the Ghostty suite:
  `cd tests && python3 -c 'import sys, test_konsole_theme; assert "test_ghostty_theme" not in sys.modules'` exits 0.
- The 16 entries of `PALETTE` are unchanged: `git diff` shows the table's
  lines moved, not edited, and the colour lines of
  `theme/konsole/MacOS8.colorscheme` and
  `theme/ghostty/org.macos8.desktop/Platinum` are untouched.
- `make check CHECK_TESTS='test_ghostty_theme test_konsole_theme
  test_invariants test_no_unused_imports'` passes, with the same test ids
  as before the move.
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
