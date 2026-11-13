# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### GTK 4 suite extraction: isolate emoji declarations (planned 2026-11-12 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still about 4,900 lines in one `TestGtk4Theme`
class. That breaks the principle that a file is small enough to read in one sitting.
Move the five `test_emoji_*` declaration checks (about 405 lines at this plan's base
commit) into their own module, the same way the landed OSD (`tests/test_gtk4_osd.py`)
and scale (`tests/test_gtk4_scale.py`) parts moved theirs. This is independent of
"README split, part 5/5" (that entry moves user-facing prose) and of the waiting
"GTK 4 suite extraction: isolate spinbutton declarations" (that entry moves only
`test_spinbutton_*` methods; the two method sets do not overlap and neither entry
edits the other's invariants rows). At implementation re-grep every anchor this
entry names, since both extraction entries edit `tests/test_gtk4_theme.py` and
`docs/invariants.md`. No stylesheet or production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_emoji.py` with
  `class TestGtk4Emoji(Gtk4SheetRuleCases, unittest.TestCase)` and a one-line
  module docstring. Move every `TestGtk4Theme` method whose name starts with
  `test_emoji_` into it, keeping each method's body and docstring unchanged:
  `test_emoji_section_button_focus_outline_color`, `test_emoji_strip_rims`,
  `test_emoji_completion_row_corners`, `test_emoji_picker_cell_corners` and
  `test_emoji_section_button_corners`. No spin-, view- or GTK 3-named method shares
  the prefix: the GTK 3 emoji check (`test_emoji_section_label_opacity`) already
  lives in `tests/test_gtk_theme.py` and stays there.
- The new module imports exactly the names the moved bodies use:
  `ETCH_DARK` and `ROW_HOVER` from `support.gtk_theme_spec`, and `BLACK`, `FACE`,
  `SELECTION` and `WHITE` from `support.platinum_palette` (the source module the
  original import block draws each name from). Every assertion helper the bodies
  call (`assert_rule`, `assert_rule_group`, `assert_rule_after`,
  `assert_exact_rule_once`, `assert_matches_frame`, `assert_square_corner`,
  `assert_tab_faces`, `assert_selected_row_button_arms`, `assert_rubberband`,
  `assert_row_selection_backdrop`, `assert_black_focus_outline`) and the
  `self.rules`/`self.selectors`/`self.css` attributes come with `Gtk4SheetRuleCases`
  and its base classes (grep-checked at this plan's base commit: all eleven are
  defined in `tests/support/gtk4_sheet.py` or `tests/support/gtk_rule_cases.py`).
  The moved bodies call no other support name (no `gtk_css`, `strip_comments`,
  `parse_css`, `HEX`, mock, tempfile or `re` use), so `tests/test_gtk4_theme.py`'s
  import block needs no change: each of the six constants is still referenced by
  remaining methods after the move (whole-file grep count exceeds the moved bodies'
  count for every name: `SELECTION` 23 vs 9, `BLACK` 94 vs 5, `ETCH_DARK` 14 vs 3,
  `FACE` 29 vs 2, `WHITE` 14 vs 2, `ROW_HOVER` 4 vs 2). Never import
  `tests/test_gtk4_theme.py` or inherit `TestGtk4Theme`.
- In `docs/invariants.md`, rewrite each dotted anchor
  `tests/test_gtk4_theme.py::TestGtk4Theme::test_emoji_…` to
  `tests/test_gtk4_emoji.py::TestGtk4Emoji::test_emoji_…` (`grep -n
  'TestGtk4Theme::test_emoji' docs/invariants.md` finds five rows at this plan's
  base commit). In the corners row whose anchor list also names the row-spin
  steppers and the sidebar button, rewrite only the emoji member and leave the
  other two members and the row's prose alone. Do not rewrite history in
  PLANS-DONE.md or BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of the five moved methods exactly once, under
  `test_gtk4_emoji.TestGtk4Emoji`, and none of them under
  `test_gtk4_theme.TestGtk4Theme`. Every other `TestGtk4Theme` method is still listed
  there.
- For each moved method, the AST of its function definition is identical to the
  original's at this plan's base commit, checked once during the run (for example by
  comparing `ast.dump` output). This is a run-time check, not a new committed test.
- `grep -n 'TestGtk4Theme::test_emoji' docs/invariants.md` prints nothing, and the
  invariants checker inside `make check` resolves every new anchor.
- `tests/test_gtk4_theme.py` shrinks by at least 400 lines, and
  `tests/test_gtk4_emoji.py` stays under about 500 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_emoji.py` and `docs/invariants.md`. `make check` passes after
  the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
