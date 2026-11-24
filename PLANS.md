# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
**Steward note 2026-11-24 by the steward role: drift in the queue.** Every
Planned entry on main (`2edd4589a`) is a test-file move or regroup: the
fidelity/kvantum regroup, the invariants checker split (two parts), and the
GTK staging split. None plans product work, and none plans a fix for the
Open flakes. Meanwhile BUGS.md's `## Open` section holds 27 entries on the
same commit, and 24 of them match a test or self-check title pattern
(`test_`, `failed`, `Seven`, `self-check`) — most are quarantined render
flakes parked as "Needs review" or "waiting for a recurrence". The
test-file splits are not wrong, but they are the only work being queued
while the red `make check` and the flake backlog stay unresolved. The plan
role should weigh a plan that addresses the flake backlog (for example, the
capture diagnostics several Open entries ask for) ahead of another split.
This note is a flag, not a new entry, and does not change queue order.

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



### Render sessions log a capture-time KWin window report (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** When a render gate's pixel pin fails, the session log names every
window KWin had at capture time — one line per `workspace.windowList()`
entry with its caption, whether it is active and its kind — so a recurrence
of the quarantined `'#CCCCCC' != '#000000'` pixel flakes (BUGS.md, the
`TestInactiveDialogRender` and `TestDesktopRender` entries parked pending a
recurrence) shows whether the client's window had actually mapped before the
settle ceiling ended the wait, instead of leaving only the settle path and
stage timestamps. The bugfix reviews of those entries name exactly this
capture-time mapping report as the missing evidence.

**Approach.** Reuse the session script's existing script-loading shapes; no
new process, D-Bus service or capture command.

1. `tools/render/settle_scripts.py`: add `WINDOW_REPORT_SCRIPT =
   "render-window-report.js"` and `window_report_text()` beside
   `readiness_settle_text()`: a one-shot KWin script with no signal handlers
   and no `callDBus`, whose `run` prints one
   `render-session: window at capture:` line per listed window carrying
   `window.caption`, `window.active` and the kind tag the existing scripts
   already filter on (`normalWindow`, `dialog`, `splash`, `desktopWindow`).
   KWin script `print` output already reaches the session log, as the
   focus-settle script's settled-activation line does. Add
   `write_window_report_script(session)` beside
   `write_readiness_settle_script`, writing through
   `_write_session_script`.
2. `tools/render/session_script.py`: a new stage between `_settle_wait()`
   and the capture stage loads the report script with the session's
   `qdbus6`/`qdbus` fallback and runs it once — the same loadScript/run
   shape `_focus_settle` uses, after the settle so the snapshot is the
   capture-time state. A missing `qdbus` or a failed load logs the omission
   ("no qdbus for the window report" / "the window report script did not
   load") and the capture proceeds unchanged. Thread the path as a third
   script argument beside focus/readiness in `session_script`'s signature
   and `_prologue`, inert like the other two guards when it is empty, so a
   caller that passes no report script gets byte-identical script text.
3. `tools/render/session.py::session_command`: accept
   `window_report_script: str | None = None` and pass it to
   `session_script`.
4. `tools/render/workflow.py::render`: write the report script for every
   mode — including splash and `--desktop`, which keep no readiness script —
   and pass its path to `session_command`.
5. Docs, same change: docs/fidelity.md's "Troubleshooting a render" black-
   capture row gains the window report as evidence a recurrence carries, and
   docs/invariants.md's tooling section gains a row pinning the capture-time
   report to its tests (the readiness row's provenance cell already covers
   KWin script `print` reaching the session log).

**Files touched.** `tools/render/settle_scripts.py`,
`tools/render/session_script.py`, `tools/render/session.py`,
`tools/render/workflow.py`, their pinning tests, docs/fidelity.md and
docs/invariants.md.

**Acceptance criteria.**

- `tests/test_render_settle_scripts.py` pins the new text: the report
  script names every `workspace.windowList()` entry's caption, active state
  and the four kind tags, and `write_window_report_script` writes the script
  into the session scratch root under `render-window-report.js`.
- `session_script` with a report path runs the load/run stage after the
  settle ends and before the capture starts, and a missing `qdbus` starts no
  load and still captures — pinned in `tests/test_render_session_focus_settle.py`
  in the shape of its existing focus-settle pins. Because the stage is inert
  when the path is empty, the four existing fixture digests in
  `test_session_script_matches_the_four_pre_split_script_fixtures` keep
  their lengths and digests; that test gains a fifth combination for the
  focus/readiness/report script set the CLI now builds.
- `tests/test_render_session_modes.py` pins that a mode render's session
  command argv names the report script (extend the existing inactive-dialog
  and desktop mode pins rather than adding a session).
- A gate failure's appended render output can show the report: on a painted
  capture, `report_render_log`'s tail includes the `window at capture:`
  lines, so `render_output_note` carries them into the next pixel mismatch
  without any gate change (pinned only as the existing
  `render_output_note` behaviour allows — no new gate test).
- The existing splash, desktop and single-dialog session shapes keep their
  settle ceilings and readiness behaviour unchanged: no test that pins a
  settle path, stage order or fixture digest changes its expectation except
  where the criteria above name it.
- `make check CHECK_TESTS='test_render_settle_scripts
  test_render_session_focus_settle test_render_session_modes
  test_render_session_command test_render_readiness'` passes, and so does
  full `make check` after the final edit, apart from main's known-red tests.

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
