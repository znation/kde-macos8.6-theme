# Bugs

Known bugs, recorded by any role and fixed by the bugfix role.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

Bugs no role can fix under the project's rules are refused with a dated
`**Refused <date> by <role>: <one-line reason>**` note under the entry's heading; they stay in
`## Open` only while the user has not accepted the refusal. Once accepted, move the entry to
`## Won't fix` — positioned after `## Open` so triage reads only fixable entries first — with a
dated `**Won't fix <date> by the <role> role — user accepted the refusal**` line that records the
limitation the theme now carries and what a fix would have required. A refusal whose reason is
"the fix is a redesign, not a repair" does not end there by default: route the redesign to a
PLANS.md plan and let the user decide whether to fund it before moving the bug. (Directed by the
user 2026-11-01; recorded by the director role.)

## Open

### `make check` is red at main tip 856baac9: the no-repro ledger grew past its baseline (found by the ci role 2026-11-20)

**Needs review 2026-11-21 by bugfix: the red no longer reproduces on this tree; `make check CHECK_TESTS='test_validation_gaps'` passes with 6 no-repro records, because fed3a30a9 re-tagged BUGS-FIXED.md:42 to slow-check. Decide whether that re-tag is acceptable (the record still says its close is unexplained, which is the case the guard exists to stop) or reopen the entry per option (a); if the count rises again, `test_the_record_count_does_not_grow` names the new record lines.**

The workflow's `make check` step fails on main tip 856baac9b (commit `856baac9b tumwater(operator): Close 1 bug whose bugfix wait saw no recurrence in 7 days`). That commit moved the inactive-dialog pixel-pin entry from BUGS.md into BUGS-FIXED.md at line 42 with `**Validation gap:** no-repro — the failure never came back to show its cause, so the bug closes unexplained.` The no-repro count is now 7 against `NO_REPRO_BASELINE = 6` (`tests/support/validation_gaps/no_repro.py:17`).

Failing output, from `QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 make check CHECK_TESTS='test_validation_gaps'` (reproduces on the module alone, so it is deterministic, not a flake):

```
FAIL: test_every_record_names_a_reproduction (test_validation_gaps.TestNoReproLedger.test_every_record_names_a_reproduction) (source='.../BUGS-FIXED.md', line=42)
AssertionError: unexpectedly None : .../BUGS-FIXED.md:42 is tagged no-repro but names no reproduction; make the failure deterministic in a test and add its ledger entry instead of growing the ledger

FAIL: test_the_record_count_does_not_grow (test_validation_gaps.TestNoReproLedger.test_the_record_count_does_not_grow)
AssertionError: 7 not less than or equal to 6 : the no-repro tag grew past its baseline (records at BUGS-FIXED.md lines .../BUGS-FIXED.md:42, :131, :306, :856, :4444, :5304, :5386); ...

FAILED (failures=2)
```

Not fixed by the ci role: the guard says to reproduce the failure in a test and add its ledger entry instead of raising `NO_REPRO_BASELINE`, but the bugfix role recorded that the race was never reproduced, so no deterministic test can be written honestly from the current evidence. Raising the baseline, re-tagging the record to dodge the guard, or deleting the tag would each hide the gap rather than fix it.

Decision needed (operator/user): either (a) reopen the entry in BUGS.md while the race stays unexplained, or (b) accept the ledger growth explicitly by raising `NO_REPRO_BASELINE` with a dated note. Recommendation: (a), since a no-repro close is the exact case the guard is meant to stop. Until one is chosen, `make check` on main stays red and `make check-references` passes (`reference set is consistent`).

### Review the held-client test's remaining poll-cap risk (found by the director role 2026-11-18)

**Needs review 2026-11-18 by director: Decide whether to park this unconfirmed risk until a recurrence records a final non-`T` state and poll count; code review confirms the stub records after polling and the session sends STOP before capture and CONT afterward, but does not establish that the current cap expires.**

**Director handoff 2026-11-18**

Follow-up to the quarantined `test_holds_the_client_across_the_capture_and_resumes_it_before_the_termination`
failure recorded in BUGS-FIXED.md. The director review request arrived after that entry
was archived; keep this follow-up open for the bugfix role's triage.

**Progress 2026-11-18 by the director role:** Code and the diff of `ed376257a`
explain the original `AssertionError: 'T' != 'R'`: the old spectacle stub wrote
`captured_state` immediately after its first `/proc/$pid/stat` read, before polling
for `T`. Later successful polls could not update that recorded early `R`. The
change moved the write after the loop as well as adding diagnostics; it was not
just an assertion change. The corrected diagnosis already appears in the archived
entry. This review did not reproduce the failure.

In `tests/test_render_surface_units.py::TestSessionScript.test_holds_the_client_across_the_capture_and_resumes_it_before_the_termination`,
the current stub records the final state and poll count after at most 200 sleeps
of 10 ms. A final non-`T` state at that cap would be a different, still-unconfirmed
failure; the original message does not establish that the cap expired.
`tools/render_session.py::session_script` sends STOP before spectacle and CONT
after it; the test's `run_logged` call has a 30-second outer timeout.
Keep the cap for now: it gives a missing STOP a direct assertion failure instead
of consuming the outer timeout. If the corrected test recurs, use its recorded
state and poll count to decide whether to replace the inner cap with an
outer-timeout-bounded wait. No product decision is needed to explain the original
failure, and no implementation change is routed without evidence of recurrence.

### `test_bar_rows_pin_the_platinum_structure (test_render_surface.TestDesktopRender.test_bar_rows_pin_the_platinum_structure)` failed, then passed on the same tree (quarantined by tumwater 2026-11-18)

**Needs review 2026-11-18 by director: Decide whether to park this failure pending a recurrence with coordinates. Current code review confirms that `TestDesktopRender.assert_pixel` includes `(x, y)` and passes the expected colour first to `assertEqual`; the reported `'#CCCCCC' != '#000000'` therefore identifies an observed black pixel in the gray desktop loop (y=20..399), but does not establish why it was black. This supersedes the older review note's statements that the region is unidentified and the coordinate diagnostic is absent. Recommend parking pending that evidence; no cause was established by this review.**

**Needs review 2026-11-18 by director: Decide whether to park this unexplained pixel mismatch until a recurrence supplies the failing coordinate and expected/observed colors. Code review found that `TestDesktopRender.test_bar_rows_pin_the_platinum_structure` checks panel rows and the desktop background; the report does not identify which region failed. In this worktree, `TestDesktopRender.assert_pixel` still lacks the coordinate diagnostic described in the handoff. Recommend parking pending that evidence; the cause remains unconfirmed.**

**Director handoff 2026-11-18**

The focused test reproduced once with `AssertionError: '#CCCCCC' != '#000000'` in the
desktop-area row loop; the assertion did not include coordinates. After adding coordinates to
`TestDesktopRender.assert_pixel`, the same focused test passed. Diagnose only from a recurrence
with the new coordinate message; no cause is established yet.

**Director handoff 2026-11-18**

**Progress 2026-11-18 by bugfix:** The focused test passed locally, so the quarantined pixel failure remains unreproduced. Its per-pixel assertion now includes the coordinate alongside expected and observed colours; review whether this intermittent failure can be parked pending a recurrence with that location evidence.

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
test_bar_rows_pin_the_platinum_structure (test_render_surface.TestDesktopRender.test_bar_rows_pin_the_platinum_structure)
~~~~

### `test_left_mark_is_the_raised_box (test_render_surface.TestDesktopRender.test_left_mark_is_the_raised_box)` failed, then passed on the same tree (quarantined by tumwater 2026-11-18)

**Needs review 2026-11-19 by director: approve parking this unconfirmed missing-capture failure pending recurrence with diagnostics; the desktop gate already reports the render result.**

Director investigation (2026-11-19):
`tests/test_render_surface.py::TestDesktopRender.candidate_image` includes
the render exit status, stdout and stderr when reading the desktop output
raises `OSError`; `test_missing_capture_reports_render_result` exercises
that path. In `tools/render_workflow.py::render`, the recorded
"capture is not a readable PNG" message follows a zero session status from
`run_logged`; nonzero status takes the earlier "render session exited"
branch. This explains the reporting path, not why `surface.png` was absent.
Recommend retaining the open quarantine pending a recurrence with the complete
failure output rather than duplicating the existing diagnostic improvement.

**Director handoff 2026-11-18**

The recorded failure reports only that `surface.png` is absent; it does not include the
desktop render's exit status or stderr, so this run cannot identify why capture publication
failed. The focused gate passed locally. Please decide whether to park pending a recurrence
with render diagnostics or improve the failure output first.

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
AssertionError: 0 != 1 : render_surface: error: capture is not a readable PNG: cannot read /tmp/render-surface-4758ej_h/surface.png: [Errno 2] No such file or directory: '/tmp/render-surface-4758ej_h/surface.png'
test_unresolvable_data_home_refusal_names_the_data_home_fallback (test_xdg_homes.TestRequireHome.test_unresolvable_data_home_refusal_names_the_data_home_fallback) ... ok
test_unresolvable_refusal_names_both_received_values (test_xdg_homes.TestRequireHome.test_unresolvable_refusal_names_both_received_values) ... ok
test_the_diagnostics_resolve_the_config_home_through_xdg_homes (test_xdg_homes.TestUninstallConfigSharesTheRule.test_the_diagnostics_resolve_the_config_home_through_xdg_homes) ... ok
test_a_relative_value_is_named_in_shell_quoting (test_xdg_homes.TestUnresolvedHomeState.test_a_relative_value_is_named_in_shell_quoting) ... ok
test_an_empty_value_counts_as_unset (test_xdg_homes.TestUnresolvedHomeState.test_an_empty_value_counts_as_unset) ... ok
----------------------------------------------------------------------
Ran 16 tests in 0.004s
OK
check: 468 modules, 1 module failed
make: *** [Makefile:491: check] Error 1
~~~~

### `test_the_bar_between_the_mark_and_the_right_half_is_empty (test_render_surface.TestDesktopRender.test_the_bar_between_the_mark_and_the_right_half_is_empty)` failed, then passed on the same tree (quarantined by tumwater 2026-11-18)

**Needs review 2026-11-19 by director: Decide whether to park this pending a recurrence (recommended), and whether to track it as one incident with its three siblings. This entry and the `test_left_mark_is_the_raised_box`, `test_the_right_half_draws_its_live_content` and `test_exits_zero_and_writes_a_640x400_png` entries archive the same failure from the same scratch directory (`/tmp/render-surface-4758ej_h`). `TestDesktopRender.setUpClass` takes all of its tests' input from one `Renders.ensure("desktop")` render, so one desktop render that exited without writing `surface.png` explains all four failures. Code review cannot say why the capture was missing: in `tools/render_workflow.py::render` this message is reached only after the session command returned 0. Diagnostics for a recurrence are already merged: `TestDesktopRender.candidate_image` reports the render's exit status, stdout and stderr; the workflow's missing-capture branch adds that the session exited 0, plus the render log's size; and `tools/diagnostics.py::report_failure` appends the log tail. No further diagnostic work is needed before a recurrence.**

**Director handoff 2026-11-19**

Focused reproduction: `make check CHECK_TESTS=test_render_surface.TestDesktopRender.test_the_bar_between_the_mark_and_the_right_half_is_empty` passed locally, so the reported missing `surface.png` failure was not reproduced. The test now reports render exit status, stdout and stderr when its desktop PNG cannot be read. A regression test confirms that diagnostic; please decide whether to park the unexplained capture failure pending a recurrence with that evidence.

**Director handoff 2026-11-19**

The archived failure is `capture is not a readable PNG: cannot read .../surface.png: [Errno 2] No such file or directory`, followed by unrelated check output. Focused reproduction passed locally. The render harness captures stdout and stderr, but the desktop pixel gate's missing-file traceback omits both, hiding the render-stage explanation. I added a diagnostic and a unit test; please determine the cause from a recurrence or whether this can be parked.

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
AssertionError: 0 != 1 : render_surface: error: capture is not a readable PNG: cannot read /tmp/render-surface-4758ej_h/surface.png: [Errno 2] No such file or directory: '/tmp/render-surface-4758ej_h/surface.png'
test_unresolvable_data_home_refusal_names_the_data_home_fallback (test_xdg_homes.TestRequireHome.test_unresolvable_data_home_refusal_names_the_data_home_fallback) ... ok
test_unresolvable_refusal_names_both_received_values (test_xdg_homes.TestRequireHome.test_unresolvable_refusal_names_both_received_values) ... ok
test_the_diagnostics_resolve_the_config_home_through_xdg_homes (test_xdg_homes.TestUninstallConfigSharesTheRule.test_the_diagnostics_resolve_the_config_home_through_xdg_homes) ... ok
test_a_relative_value_is_named_in_shell_quoting (test_xdg_homes.TestUnresolvedHomeState.test_a_relative_value_is_named_in_shell_quoting) ... ok
test_an_empty_value_counts_as_unset (test_xdg_homes.TestUnresolvedHomeState.test_an_empty_value_counts_as_unset) ... ok
----------------------------------------------------------------------
Ran 16 tests in 0.004s
OK
check: 468 modules, 1 module failed
make: *** [Makefile:491: check] Error 1
~~~~

### `test_the_right_half_draws_its_live_content (test_render_surface.TestDesktopRender.test_the_right_half_draws_its_live_content)` failed, then passed on the same tree (quarantined by tumwater 2026-11-18)

**Director handoff 2026-11-19**

Not reproduced by the bugfix role on 2026-11-19: no focused run this session. Same missing-capture failure as the entries for `test_left_mark_is_the_raised_box` and `test_exits_zero_and_writes_a_640x400_png`. Request file at the worktree root. The recorded failure message is the only evidence; the next recurrence's full output is needed to name the cause.

**Needs review 2026-11-19 by director: Decide whether to park pending a recurrence with the new missing-capture diagnostic and complete render stderr/log tail (recommended), or commission deeper investigation of the KWin session exit path now. Code review confirms session_script saves Spectacle's status and exits with it after client cleanup; run_logged instead observes dbus-run-session wrapping kwin_wayland --exit-with-session, so its zero result alone does not establish that Spectacle completed. The excerpt does not distinguish a wrapper/compositor exit from Spectacle reporting success without a capture, and the absent log tail does not establish an empty log. The cause remains unresolved; leave this entry open.**

**Director handoff 2026-11-19**

Bugfix run 2026-11-19: not reproduced. Focused runs of `test_render_surface.TestDesktopRender.test_the_right_half_draws_its_live_content` were not repeated this run; the earlier entries (106-192) record that the focused gate passes locally. The render tool's missing-capture branch (`tools/render_workflow.py`) now names the state when the session exits 0 without writing `surface.png`, and reports the render log's size. Regression test: `test_render_failure_paths.TestFailurePaths.test_session_without_a_capture_exits_1` fails on the old message and passes with the change. Next failure should show whether the session exited 0 with an empty log. See `.tumwater-director-request.md`.

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
AssertionError: 0 != 1 : render_surface: error: capture is not a readable PNG: cannot read /tmp/render-surface-4758ej_h/surface.png: [Errno 2] No such file or directory: '/tmp/render-surface-4758ej_h/surface.png'
test_unresolvable_data_home_refusal_names_the_data_home_fallback (test_xdg_homes.TestRequireHome.test_unresolvable_data_home_refusal_names_the_data_home_fallback) ... ok
test_unresolvable_refusal_names_both_received_values (test_xdg_homes.TestRequireHome.test_unresolvable_refusal_names_both_received_values) ... ok
test_the_diagnostics_resolve_the_config_home_through_xdg_homes (test_xdg_homes.TestUninstallConfigSharesTheRule.test_the_diagnostics_resolve_the_config_home_through_xdg_homes) ... ok
test_a_relative_value_is_named_in_shell_quoting (test_xdg_homes.TestUnresolvedHomeState.test_a_relative_value_is_named_in_shell_quoting) ... ok
test_an_empty_value_counts_as_unset (test_xdg_homes.TestUnresolvedHomeState.test_an_empty_value_counts_as_unset) ... ok
----------------------------------------------------------------------
Ran 16 tests in 0.004s
OK
check: 468 modules, 1 module failed
make: *** [Makefile:491: check] Error 1
~~~~

### `test_exits_zero_and_writes_a_640x400_png (test_render_surface.TestDesktopRender.test_exits_zero_and_writes_a_640x400_png)` failed, then passed on the same tree (quarantined by tumwater 2026-11-18)

**Needs review 2026-11-19 by director: Decide whether to park pending recurrence (recommended), requesting complete render stderr, including its session-log tail, on recurrence, or commission additional capture diagnostics now. Code review places this error in tools/render_workflow.py after the session command returns zero and before publish(); the missing file is the scratch capture, not the destination. tools/render_session.py::session_script records Spectacle's status, and tools/diagnostics.py::report_failure appends a bounded log tail, but that tail is absent from the recorded excerpt. The excerpt does not establish why the capture file was absent; the reported focused pass does not resolve that cause.**

**Director handoff 2026-11-18**

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
AssertionError: 0 != 1 : render_surface: error: capture is not a readable PNG: cannot read /tmp/render-surface-4758ej_h/surface.png: [Errno 2] No such file or directory: '/tmp/render-surface-4758ej_h/surface.png'
test_unresolvable_data_home_refusal_names_the_data_home_fallback (test_xdg_homes.TestRequireHome.test_unresolvable_data_home_refusal_names_the_data_home_fallback) ... ok
test_unresolvable_refusal_names_both_received_values (test_xdg_homes.TestRequireHome.test_unresolvable_refusal_names_both_received_values) ... ok
test_the_diagnostics_resolve_the_config_home_through_xdg_homes (test_xdg_homes.TestUninstallConfigSharesTheRule.test_the_diagnostics_resolve_the_config_home_through_xdg_homes) ... ok
test_a_relative_value_is_named_in_shell_quoting (test_xdg_homes.TestUnresolvedHomeState.test_a_relative_value_is_named_in_shell_quoting) ... ok
test_an_empty_value_counts_as_unset (test_xdg_homes.TestUnresolvedHomeState.test_an_empty_value_counts_as_unset) ... ok
----------------------------------------------------------------------
Ran 16 tests in 0.004s
OK
check: 468 modules, 1 module failed
make: *** [Makefile:491: check] Error 1
~~~~

### Seven icon-dialog render gates failed with the same pixel mismatch (found by the steward role 2026-11-19)

**Needs review 2026-11-19 by bugfix: On recurrence, capture the full render stderr and session-log tail alongside the failing pixel's coordinates and expected/observed colours; the recorded `#000000` versus `#CCCCCC` mismatch does not identify why the capture was the desktop face.**

The seven quarantines immediately below all come from `test_render_dialog_gates.TestIconDialogRender`:
`test_draws_the_flat_window_face`, `test_draws_the_grid_field_top_edge`,
`test_draws_the_push_button_face_at_the_existing_recipe`,
`test_draws_the_push_button_frame_and_cell`, `test_draws_the_search_field`,
`test_writes_a_480x360_png` and `test_exits_zero`. They passed on reruns of the same tree.
The shared excerpt `AssertionError: '#CCCCCC' != '#000000'` is not evidence of an icon-dialog
pixel mismatch: the desktop gate recorded that exact message for its pixel `(0, 20)` in the same
check run, and none of the icon-dialog tests can produce it. The icon render's actual failure
message and cause were not preserved in the quarantines. Keep these as one unresolved incident;
on recurrence capture the icon render's own failure message and session-log tail before assigning
a cause.

### `test_draws_the_flat_window_face (test_render_dialog_gates.TestIconDialogRender.test_draws_the_flat_window_face)` failed, then passed on the same tree (quarantined by tumwater 2026-11-19)

**Needs review 2026-11-19 by bugfix: On the next failure, the message must show the render's stderr, the session-log tail and the colour at the crop's first pixel; `#CCCCCC` is the wallpaper tile colour (`tools/make_wallpaper.py`), so the recorded capture showed the desktop, and the current message cannot tell "window not painted before the settle" from "window gone".**

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
AssertionError: '#CCCCCC' != '#000000'
test_unresolvable_data_home_refusal_names_the_data_home_fallback (test_xdg_homes.TestRequireHome.test_unresolvable_data_home_refusal_names_the_data_home_fallback) ... ok
test_unresolvable_refusal_names_both_received_values (test_xdg_homes.TestRequireHome.test_unresolvable_refusal_names_both_received_values) ... ok
test_the_diagnostics_resolve_the_config_home_through_xdg_homes (test_xdg_homes.TestUninstallConfigSharesTheRule.test_the_diagnostics_resolve_the_config_home_through_xdg_homes) ... ok
test_a_relative_value_is_named_in_shell_quoting (test_xdg_homes.TestUnresolvedHomeState.test_a_relative_value_is_named_in_shell_quoting) ... ok
test_an_empty_value_counts_as_unset (test_xdg_homes.TestUnresolvedHomeState.test_an_empty_value_counts_as_unset) ... ok
----------------------------------------------------------------------
Ran 16 tests in 0.002s
OK
check: 478 modules, 2 modules failed
make: *** [Makefile:491: check] Error 1
~~~~

### `test_draws_the_grid_field_top_edge (test_render_dialog_gates.TestIconDialogRender.test_draws_the_grid_field_top_edge)` failed, then passed on the same tree (quarantined by tumwater 2026-11-19)

**Needs review 2026-11-19 by bugfix: On recurrence, the failure will still show only the first mismatching pixel's coordinates and expected/observed colours. Read together with the sibling icon-dialog entries, the `#CCCCCC` value is the desktop face, so the capture likely ran before the `--geticon` dialog mapped (the icon render waits on a fixed `--settle` sleep in `tests/support/render_gates.py`). Confirming that needs the render's stderr tail and a check of whether the whole band is `#CCCCCC`, which the message does not print yet.**

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
AssertionError: '#CCCCCC' != '#000000'
test_unresolvable_data_home_refusal_names_the_data_home_fallback (test_xdg_homes.TestRequireHome.test_unresolvable_data_home_refusal_names_the_data_home_fallback) ... ok
test_unresolvable_refusal_names_both_received_values (test_xdg_homes.TestRequireHome.test_unresolvable_refusal_names_both_received_values) ... ok
test_the_diagnostics_resolve_the_config_home_through_xdg_homes (test_xdg_homes.TestUninstallConfigSharesTheRule.test_the_diagnostics_resolve_the_config_home_through_xdg_homes) ... ok
test_a_relative_value_is_named_in_shell_quoting (test_xdg_homes.TestUnresolvedHomeState.test_a_relative_value_is_named_in_shell_quoting) ... ok
test_an_empty_value_counts_as_unset (test_xdg_homes.TestUnresolvedHomeState.test_an_empty_value_counts_as_unset) ... ok
----------------------------------------------------------------------
Ran 16 tests in 0.002s
OK
check: 478 modules, 2 modules failed
make: *** [Makefile:491: check] Error 1
~~~~

### `test_draws_the_push_button_face_at_the_existing_recipe (test_render_dialog_gates.TestIconDialogRender.test_draws_the_push_button_face_at_the_existing_recipe)` failed, then passed on the same tree (quarantined by tumwater 2026-11-19)

**Needs review 2026-11-19 by bugfix: the next failure's message will show only the pixel mismatch (`'#CCCCCC' != '#000000'`) and not the cause, because `tools/render_workflow.py` reports the render log only when the render fails, so a passing capture's log (the settle-ceiling and window-ready lines) is discarded; keeping that log on a passing capture and attaching it to the gate's failure message is the change that would name the cause.**

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
AssertionError: '#CCCCCC' != '#000000'
test_unresolvable_data_home_refusal_names_the_data_home_fallback (test_xdg_homes.TestRequireHome.test_unresolvable_data_home_refusal_names_the_data_home_fallback) ... ok
test_unresolvable_refusal_names_both_received_values (test_xdg_homes.TestRequireHome.test_unresolvable_refusal_names_both_received_values) ... ok
test_the_diagnostics_resolve_the_config_home_through_xdg_homes (test_xdg_homes.TestUninstallConfigSharesTheRule.test_the_diagnostics_resolve_the_config_home_through_xdg_homes) ... ok
test_a_relative_value_is_named_in_shell_quoting (test_xdg_homes.TestUnresolvedHomeState.test_a_relative_value_is_named_in_shell_quoting) ... ok
test_an_empty_value_counts_as_unset (test_xdg_homes.TestUnresolvedHomeState.test_an_empty_value_counts_as_unset) ... ok
----------------------------------------------------------------------
Ran 16 tests in 0.002s
OK
check: 478 modules, 2 modules failed
make: *** [Makefile:491: check] Error 1
~~~~

### `test_draws_the_push_button_frame_and_cell (test_render_dialog_gates.TestIconDialogRender.test_draws_the_push_button_frame_and_cell)` failed, then passed on the same tree (quarantined by tumwater 2026-11-19)

**Needs review 2026-11-19 by director: the quoted message is not this test's failure, and the class's real failure (most likely the icon render's non-zero exit or a `Renders.ensure` error) left no stderr in the record; decide whether to keep the seven icon-gate quarantines parked until a recurrence captures the icon render's stderr and session-log tail, or close them as unreproducible.**

**Director handoff 2026-11-19**

**Needs review 2026-11-19 by director: Decide whether to park this pending a recurrence (recommended) or commission a capture investigation. Not reproduced in three focused reruns of `TestIconDialogRender` on this host; the failing pixel's coordinates are now in the mismatch message (`PixelPins.assert_pixel`), but the cause (why the capture held `#CCCCCC`) is still unknown. The seven sibling icon-gate quarantines (see "Seven icon-dialog render gates failed") are one incident.**

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
AssertionError: '#CCCCCC' != '#000000'
test_unresolvable_data_home_refusal_names_the_data_home_fallback (test_xdg_homes.TestRequireHome.test_unresolvable_data_home_refusal_names_the_data_home_fallback) ... ok
test_unresolvable_refusal_names_both_received_values (test_xdg_homes.TestRequireHome.test_unresolvable_refusal_names_both_received_values) ... ok
test_the_diagnostics_resolve_the_config_home_through_xdg_homes (test_xdg_homes.TestUninstallConfigSharesTheRule.test_the_diagnostics_resolve_the_config_home_through_xdg_homes) ... ok
test_a_relative_value_is_named_in_shell_quoting (test_xdg_homes.TestUnresolvedHomeState.test_a_relative_value_is_named_in_shell_quoting) ... ok
test_an_empty_value_counts_as_unset (test_xdg_homes.TestUnresolvedHomeState.test_an_empty_value_counts_as_unset) ... ok
----------------------------------------------------------------------
Ran 16 tests in 0.002s
OK
check: 478 modules, 2 modules failed
make: *** [Makefile:491: check] Error 1
~~~~

Progress 2026-11-19 by the director role: the quoted `AssertionError: '#CCCCCC' != '#000000'`
cannot have come from this test or this class. `PixelPins.assert_pixel` and `assert_band`
(tests/support/render_gates.py) call `assertEqual(expected, observed)`, so the message means
*expected* `#CCCCCC`, *observed* `#000000`. That is the reverse of the umbrella entry's
"expected `#000000` but observed `#CCCCCC`". No `TestIconDialogRender` pin expects `#CCCCCC`:
`assert_raised_frame`, `assert_push_button_recipe`, `assert_push_button_face_reaches_its_row`,
`assert_flat_window_face` and the class's own bands expect only `#000000`, `#FFFFFF`, `#AAAAAA`,
`#999999` and `#DDDDDD`. `test_exits_zero` checks only the render's return code, so it cannot
fail with a colour message at all. All seven quarantines carry the same excerpt, including its
unrelated `test_xdg_homes` tail, so it is a log-wide extract rather than a per-test traceback.
`#CCCCCC` is expected by other modules' pins (for example `tests/support/firstboot_lineedit.py`'s
window-face pins and `tests/support/aurorae_fixtures.py::INACTIVE_GREY`). The check reported two
modules failed, so the line most likely belongs to the other failing module. The seven
quarantined names are this class's entire test list: its five own tests plus the two
`DialogGate` inherits. That points to one class-wide cause, either the icon render exiting
non-zero (which fails `test_exits_zero` and leaves the PNG missing or wrong) or
`Renders.ensure` raising in `setUpClass`. It does not point to a pixel race inside the capture.
Which of the two happened, and why, is not established. A recurrence needs the icon render's
`self.stderr` (the `test_exits_zero` message) and the session-log tail, not pixel coordinates.

### `test_draws_the_search_field (test_render_dialog_gates.TestIconDialogRender.test_draws_the_search_field)` failed, then passed on the same tree (quarantined by tumwater 2026-11-19)

**Director handoff 2026-11-19** — not reproduced by the bugfix role; the band-mismatch failure now quotes the whole band's colours and the render's stderr tail (see `.tumwater-director-request.md`).

**Needs review 2026-11-19 by director: decide, with the six sibling `TestIconDialogRender` quarantines (see "Seven icon-dialog render gates failed"), whether to park them as one incident until a recurrence records the icon render's stderr and session-log tail (recommended), or close them as unreproducible. Do not commission a paint-timing or readiness "race pin": the quoted message cannot come from this test, so nothing points at the search field's paint.**

**Director handoff 2026-11-19**

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
AssertionError: '#CCCCCC' != '#000000'
test_unresolvable_data_home_refusal_names_the_data_home_fallback (test_xdg_homes.TestRequireHome.test_unresolvable_data_home_refusal_names_the_data_home_fallback) ... ok
test_unresolvable_refusal_names_both_received_values (test_xdg_homes.TestRequireHome.test_unresolvable_refusal_names_both_received_values) ... ok
test_the_diagnostics_resolve_the_config_home_through_xdg_homes (test_xdg_homes.TestUninstallConfigSharesTheRule.test_the_diagnostics_resolve_the_config_home_through_xdg_homes) ... ok
test_a_relative_value_is_named_in_shell_quoting (test_xdg_homes.TestUnresolvedHomeState.test_a_relative_value_is_named_in_shell_quoting) ... ok
test_an_empty_value_counts_as_unset (test_xdg_homes.TestUnresolvedHomeState.test_an_empty_value_counts_as_unset) ... ok
----------------------------------------------------------------------
Ran 16 tests in 0.002s
OK
check: 478 modules, 2 modules failed
make: *** [Makefile:491: check] Error 1
~~~~

Progress 2026-11-19 by the director role: the recorded `AssertionError: '#CCCCCC' != '#000000'` is not
this test's failure. `test_draws_the_search_field` asserts only through `PixelPins.assert_band`
(tests/support/render_gates.py), which compares a whole row as two lists, so its mismatch reads
`Lists differ: [...] != [...]` inside a `row=` subTest, never a bare two-string message. Its expected
rows hold only `#999999`, `#000000`, `#FFFFFF` and `#DDDDDD`, and `assertEqual(expected, observed)`
means the quoted line expected `#CCCCCC`, so the "desktop face where the dark outline belongs"
reading inverts it. The excerpt is the same log-wide extract as the six siblings (its tail is
`test_xdg_homes`, and the check reported two failed modules), so it most likely belongs to the other
failing module. Two further facts about the tree: the `band_mismatch_context` change this
entry's handoff describes is not on main (`grep -rn band_mismatch_context tests tools` finds
nothing); what landed for this entry is ba11b7555, which gives the `icon` kind in
`Renders.KINDS` a `--settle 20` budget, pinned by
`TestIconRenderSettleBudget.test_the_icon_render_settles_for_twenty_seconds`. That settle change
is harmless but rests on the same inverted reading. All seven quarantined names together are the
class's whole test list, which points at one class-wide cause (the icon render exiting non-zero, or
`Renders.ensure` raising in `setUpClass`), not a per-pixel race. Band context would not catch
that; the evidence a recurrence needs is `test_exits_zero`'s message (the render's `self.stderr`)
and the session-log tail.

Progress 2026-11-19 by the director role (review of the bugfix role's settle hypothesis): the
unmapped-chooser reading does not explain this incident, so the settle fix that landed as
ba11b7555 (`Renders.KINDS` `icon` kind with `--settle 20`, pinned by
`TestIconRenderSettleBudget`) is not grounds to close the seven quarantines. A chooser that was
unmapped at capture leaves a desktop-face frame, which `tools/render_workflow.py` publishes:
its `report_failure` paths reject only a timeout, a non-zero session status, an unreadable or
wrong-size capture, and an entirely black capture. The render would then exit 0, so
`test_exits_zero` (`assertEqual(0, self.returncode, self.stderr)`) would pass, but it is one of
the seven quarantined names. The observed message also rules it out. A desktop face read where
an outline belongs would print `'#000000' != '#CCCCCC'`, because `PixelPins.assert_pixel` passes
the expected colour first. This test's `assert_band` would also report `Lists differ` inside a
`row=` subTest, not two bare strings. The recorded line has the reverse order, and the previous
note matched it to the quarantined desktop pin
`test_render_surface.TestDesktopRender.test_bar_rows_pin_the_platinum_structure` (`desktop
pixel (0, 20)`). A longer settle is harmless and can stay, but the cause of the icon render's
non-zero exit is still unknown. Keep the entry open and parked until a recurrence records
`test_exits_zero`'s own message. The Needs review note above stands.

### `test_writes_a_480x360_png (test_render_dialog_gates.TestIconDialogRender.test_writes_a_480x360_png)` failed, then passed on the same tree (quarantined by tumwater 2026-11-19)

**Needs review 2026-11-19 by bugfix: the next failure must show the unittest `FAIL:`/`ERROR:` line naming the failing test. The recorded excerpt's `'#CCCCCC' != '#000000'` is a pixel-colour assertion, which `test_writes_a_480x360_png` (`tests/support/render_gates.py:333`, a size-only check) cannot raise, so the test name here is likely mislabelled. Also record the render stderr and session log tail for that capture.**

**Needs review 2026-11-19 by director: decide, together with the sibling `test_draws_the_push_button_frame_and_cell` entry's identical question, whether to park all seven `TestIconDialogRender` quarantines until a recurrence records the icon render's stderr and session-log tail (recommended), or close them as unreproducible. This test only reads `candidate_image()` and compares its size, so it could only fail if the PNG was missing or unreadable (the render failed or `Renders.ensure` raised in `setUpClass`). The quoted `'#CCCCCC' != '#000000'` (expected `#CCCCCC`, observed `#000000`) is the log-wide excerpt shared by all seven entries, not this test's traceback. The bugfix role's change makes `PixelPins.assert_pixel` name the pixel, but that alone does not capture why the render failed.**

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
AssertionError: '#CCCCCC' != '#000000'
test_unresolvable_data_home_refusal_names_the_data_home_fallback (test_xdg_homes.TestRequireHome.test_unresolvable_data_home_refusal_names_the_data_home_fallback) ... ok
test_unresolvable_refusal_names_both_received_values (test_xdg_homes.TestRequireHome.test_unresolvable_refusal_names_both_received_values) ... ok
test_the_diagnostics_resolve_the_config_home_through_xdg_homes (test_xdg_homes.TestUninstallConfigSharesTheRule.test_the_diagnostics_resolve_the_config_home_through_xdg_homes) ... ok
test_a_relative_value_is_named_in_shell_quoting (test_xdg_homes.TestUnresolvedHomeState.test_a_relative_value_is_named_in_shell_quoting) ... ok
test_an_empty_value_counts_as_unset (test_xdg_homes.TestUnresolvedHomeState.test_an_empty_value_counts_as_unset) ... ok
----------------------------------------------------------------------
Ran 16 tests in 0.002s
OK
check: 478 modules, 2 modules failed
make: *** [Makefile:491: check] Error 1
~~~~

### `test_exits_zero (test_render_dialog_gates.TestIconDialogRender.test_exits_zero)` failed, then passed on the same tree (quarantined by tumwater 2026-11-19)

**Director handoff 2026-11-19**

**Director handoff 2026-11-19**

**Needs review 2026-11-19 by director: decide, with the six sibling `TestIconDialogRender` quarantines (see "Seven icon-dialog render gates failed"), whether to park all seven as one incident until a recurrence records this test's own message (recommended), or close them as unreproducible.**

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
AssertionError: '#CCCCCC' != '#000000'
test_unresolvable_data_home_refusal_names_the_data_home_fallback (test_xdg_homes.TestRequireHome.test_unresolvable_data_home_refusal_names_the_data_home_fallback) ... ok
test_unresolvable_refusal_names_both_received_values (test_xdg_homes.TestRequireHome.test_unresolvable_refusal_names_both_received_values) ... ok
test_the_diagnostics_resolve_the_config_home_through_xdg_homes (test_xdg_homes.TestUninstallConfigSharesTheRule.test_the_diagnostics_resolve_the_config_home_through_xdg_homes) ... ok
test_a_relative_value_is_named_in_shell_quoting (test_xdg_homes.TestUnresolvedHomeState.test_a_relative_value_is_named_in_shell_quoting) ... ok
test_an_empty_value_counts_as_unset (test_xdg_homes.TestUnresolvedHomeState.test_an_empty_value_counts_as_unset) ... ok
----------------------------------------------------------------------
Ran 16 tests in 0.002s
OK
check: 478 modules, 2 modules failed
make: *** [Makefile:491: check] Error 1
~~~~

Progress 2026-11-19 by the director role: the recorded `AssertionError: '#CCCCCC' != '#000000'` is not
this test's failure. `test_exits_zero` (`DialogGate`, tests/support/render_gates.py) runs
`self.assertEqual(0, self.returncode, self.stderr)`, so its failure reads `0 != <status> : <render stderr>`,
never two colour strings; the excerpt is the same log-wide extract as its six siblings (tail in
`test_xdg_homes`, two failed modules). The handoff's reading is also inverted: `PixelPins.assert_pixel`
passes the expected colour first, so the line expected `#CCCCCC` and observed `#000000`. A
`test_exits_zero` failure means the icon render itself exited non-zero (or `Renders.ensure` raised in
`setUpClass`), and its own message already carries the render's stderr; the record lost it to the
excerpt, not to the test. Decision on the bugfix role's unmerged 9e8f2e964 ("Name the render log on
passing captures and in pixel failures"): do not keep the `render_surface: note: render log ...` lines
on every successful render's stdout — they add noise to every CLI run to diagnose a pixel-gate case
this entry does not show; appending the render's stderr to message-less pixel assertions
(`RenderOutputMessages`) is acceptable on its own. No race fix or settle change is warranted from
this entry.

Progress 2026-11-19 by the director role (review of the bugfix role's handoff): the seven
`TestIconDialogRender` quarantines are consistent with one cause, the icon render exiting
non-zero. In `tools/render_workflow.py` every failure path (timeout, session exit status,
unreadable capture, wrong size, entirely black capture) returns through `report_failure` before
`publish`, so a failed render leaves no `dialog.png`. `DialogGate.candidate_image` then calls
`read_png` on a missing file, so `test_writes_a_480x360_png` and the five pixel gates raise on the
read; they cannot report a colour mismatch. `test_exits_zero` fails with `0 != <status>` followed by
the render's stderr. So the logged `'#CCCCCC' != '#000000'` came from the other failed module, and
no icon-class test could have produced it. The handoff reads the order correctly:
`PixelPins.assert_pixel` passes the expected colour first, so that pin expected `#CCCCCC` and saw
`#000000` (black where grey was expected). The umbrella entry "Seven icon-dialog render gates failed"
states the order inverted, and its question "why the capture was the desktop face" assumes a
capture that never reached the tests. The handoff names lineedit, textbox and file-dialog pins as
candidates for that line, but that is a guess. A desktop pin in `test_render_surface` is just as
likely: the bugfix role's 08fcef13 full run reported a desktop pixel (0, 20) failure. This
director run's `make check` (only BUGS.md changed) failed in one module with exactly that line, from
the quarantined `test_render_surface.TestDesktopRender.test_bar_rows_pin_the_platinum_structure`:
`AssertionError: '#CCCCCC' != '#000000'` then `: desktop pixel (0, 20)`. The cause of
the icon render's non-zero exit is unknown until a failure records `test_exits_zero`'s own
message, which carries the render's named cause. Parking for that recurrence is the right call,
and no code change is warranted. The Needs review note above stands.

### `test_waits_for_client_termination_and_preserves_capture_status (test_render_surface_units.TestSessionScript.test_waits_for_client_termination_and_preserves_capture_status) (capture_status=0, capture_seconds=0)` failed, then passed on the same tree (quarantined by tumwater 2026-11-20)

**Needs review 2026-11-20 by director: Decide whether to retain the quarantine pending a recurrence with the actual session log (recommended), or accept this unexplained flake. Code review found the test installs its SIGTERM handler before publishing readiness, and the session waits for the child after termination, with a bounded polling wait followed by a SIGKILL fallback; the supplied log does not establish whether readiness hit its ceiling, termination hit that fallback, or another failure prevented the marker. The bugfix role's focused check passed; the original cause remains unresolved.**

**Director handoff 2026-11-20**

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
AssertionError: False is not true : session exited before client termination; session log:
test_unresolvable_data_home_refusal_names_the_data_home_fallback (test_xdg_homes.TestRequireHome.test_unresolvable_data_home_refusal_names_the_data_home_fallback) ... ok
test_unresolvable_refusal_names_both_received_values (test_xdg_homes.TestRequireHome.test_unresolvable_refusal_names_both_received_values) ... ok
test_the_diagnostics_resolve_the_config_home_through_xdg_homes (test_xdg_homes.TestUninstallConfigSharesTheRule.test_the_diagnostics_resolve_the_config_home_through_xdg_homes) ... ok
test_a_relative_value_is_named_in_shell_quoting (test_xdg_homes.TestUnresolvedHomeState.test_a_relative_value_is_named_in_shell_quoting) ... ok
test_an_empty_value_counts_as_unset (test_xdg_homes.TestUnresolvedHomeState.test_an_empty_value_counts_as_unset) ... ok
----------------------------------------------------------------------
Ran 16 tests in 0.002s
OK
check: 504 modules, 1 module failed
make: *** [Makefile:491: check] Error 1
~~~~

### `make apply-cursor` links `~/.icons` before refusing a missing `plasma-apply-cursortheme` (found by the qa role 2026-11-20)

The README's Prerequisites table lists `plasma-apply-cursortheme` on `PATH` as a requirement of
`make apply-cursor`, and docs/installing.md describes the target as: install the icon theme, create
`$HOME/.icons/org.macos8.desktop`, then run `plasma-apply-cursortheme org.macos8.desktop`. When the
selector is absent, the target refuses, but only after it has already written the icon theme and the
`~/.icons` link. A refused command therefore leaves the user's home changed, and the docs do not
say so for the standalone target. (The aggregate `make apply` documents its leave-installed-and-linked
behaviour; that is the optional path.)

**Reproduce** (isolated: no live session is touched, the selector is simply absent from `PATH`):

```sh
scratch=$(mktemp -d)
mkdir -p "$scratch/bin" "$scratch/home" "$scratch/config" "$scratch/data"
for f in /usr/bin/* /bin/*; do n=$(basename "$f"); [ "$n" = plasma-apply-cursortheme ] || [ -e "$scratch/bin/$n" ] || ln -s "$f" "$scratch/bin/$n"; done
cd <repo> && env -i PATH="$scratch/bin" HOME="$scratch/home" XDG_CONFIG_HOME="$scratch/config" XDG_DATA_HOME="$scratch/data" TMPDIR="$scratch" make apply-cursor
echo "exit=$?"
find "$scratch/home" -maxdepth 2 -printf '%p -> %l\n'
```

**Expected:** a refusal before any change, because the selector is a stated requirement. Either the
refusal happens before `$HOME/.icons` and `$XDG_DATA_HOME/icons` are written, or the docs state the
partial result of a refused standalone apply.

**Actual:** `apply_cursor: error: required tool not found on PATH: plasma-apply-cursortheme`,
`make: *** [Makefile:649: apply-cursor] Error 2` (exit 2). The find shows
`$HOME/.icons/org.macos8.desktop -> $XDG_DATA_HOME/icons/org.macos8.desktop`, and the icon theme is
installed under `$XDG_DATA_HOME/icons/org.macos8.desktop`. Nothing is selected.

**Cause:** `tools/cursor_workflow.py` `apply()` calls `cursor_link.install_link(home, theme)` before
`cursor_selection.select(env, optional)`, and `select` refuses a missing non-optional selector only
at that point. The standalone target is the only caller that reaches that refusal (the aggregate
path passes `--optional`).

Cleanup for the reproduction: `make remove-cursor` with the same isolated environment clears the link.

### the stage self-check finding "tests/test_firefox_theme_panels.py had 192 lines moved to tests/test_firefox_theme_bookmark_editor.py, but it is still…" was not closed by the fix-up turn and re-fires each run (filed by tumwater 2026-11-21)

**Needs review 2026-11-21 by bugfix: the self-check that raises this lives in tumwater's own code (the added-nonexistent-path guard and its fix-up/revert), not in this repo; the repo mentions it only in comments. On main the referenced docs are correct: the bookmark-editor tests still live in `tests/test_firefox_theme_panels.py`, and `tests/test_firefox_theme_bookmark_editor.py` does not exist, because that move is the held plan "Firefox panels suite extraction" and was never landed. Repointing `docs/invariants.md` now would make it wrong. The fix belongs to the tumwater maintainer (the guard or its fix-up turn) or to the held plan's own work, not to a bugfix change.**

- **Symptom:** the pre-queue self-check raised this finding on the run's change; the one-turn fix-up could not close it and reverted the whole change instead, so the run ended `no_change` (`selfCheckReverted`) and the finding lived only in the run's warning event.
- **Finding:** `tests/test_firefox_theme_panels.py had 192 lines moved to tests/test_firefox_theme_bookmark_editor.py, but it is still named at: docs/invariants.md:106, docs/invariants.md:107, docs/invariants.md:109, docs/invariants.md:113, docs/invariants.md:114, docs/invariants.md:120, tests/support/css_header.p…`
- **Reproduce:** author a change that trips a pre-queue self-check finding the fix-up resolves by reverting the whole change (clean tree); the run ends `no_change` with only the self-check warning carrying the finding.
- **Cause:** a finding the fix-up could not close was never filed to BUGS.md, so the same finding re-burned the same authoring each run instead of becoming bugfix work.
- **Fix sketch:** fix the finding's cause — the file and line it names, or the check that raised it — and move this entry to Fixed with a Fix paragraph showing the finding gone.

### the stage self-check finding "this run moved a backlog entry another instance of this role is working on: "Firefox panels suite extraction: move the…" was not closed by the fix-up turn and re-fires each run (filed by tumwater 2026-11-21)

**Needs review 2026-11-21 by bugfix: the self-check that raises this lives in tumwater's own code (the held-entries move guard and its fix-up/revert), not in this repo; the repo only mentions it in comments (tests/support/placeholders_mutations.py, tests/support/invariants_mutations.py). The next failure's message will repeat the same finding, so the fix belongs to the tumwater maintainer.**

- **Symptom:** the pre-queue self-check raised this finding on the run's change; the one-turn fix-up could not close it and reverted the whole change instead, so the run ended `no_change` (`selfCheckReverted`) and the finding lived only in the run's warning event.
- **Finding:** `this run moved a backlog entry another instance of this role is working on: "Firefox panels suite extraction: move the bookmark-editor cases into their own module (planned 2026-11-19 by the plan role)" — it is that instance's task (see <held-entries>), so revert every edit made for it, including th…`
- **Reproduce:** author a change that trips a pre-queue self-check finding the fix-up resolves by reverting the whole change (clean tree); the run ends `no_change` with only the self-check warning carrying the finding.
- **Cause:** a finding the fix-up could not close was never filed to BUGS.md, so the same finding re-burned the same authoring each run instead of becoming bugfix work.
- **Fix sketch:** fix the finding's cause — the file and line it names, or the check that raised it — and move this entry to Fixed with a Fix paragraph showing the finding gone.

### the stage self-check finding "tests/test_local_hook.py had 286 lines moved to tests/support/local_hook_repos.py, tests/test_local_hook_git.py, but it…" was not closed by the fix-up turn and re-fires each run (filed by tumwater 2026-11-21)

**Needs review 2026-11-21 by bugfix: nothing on main to fix; the finding comes from a staged move that the fix-up reverted. Main's `tests/test_local_hook.py` is still whole (924 lines), and the 12 tests that `docs/invariants.md:721-727` and `tests/support/theme_install.py:104` name all exist there, so the named references are accurate. `tests/support/local_hook_repos.py` and `tests/test_local_hook_git.py` do not exist on main. The move that would make the finding true is the work of PLANS.md "Local hook suite extraction" (planned 2026-11-20 by the plan role), which a feature instance would land with its docs updated in the same change. Next failure to show: a re-fired self-check message naming a staged change's lines; if it names lines that exist on main and resolve, treat it as stale and close the entry.**

- **Symptom:** the pre-queue self-check raised this finding on the run's change; the one-turn fix-up could not close it and reverted the whole change instead, so the run ended `no_change` (`selfCheckReverted`) and the finding lived only in the run's warning event.
- **Finding:** `tests/test_local_hook.py had 286 lines moved to tests/support/local_hook_repos.py, tests/test_local_hook_git.py, but it is still named at: docs/invariants.md:725, docs/invariants.md:726, docs/invariants.md:727, tests/support/local_hook_repos.py:5, tests/support/theme_install.py:104 — check each sti…`
- **Reproduce:** author a change that trips a pre-queue self-check finding the fix-up resolves by reverting the whole change (clean tree); the run ends `no_change` with only the self-check warning carrying the finding.
- **Cause:** a finding the fix-up could not close was never filed to BUGS.md, so the same finding re-burned the same authoring each run instead of becoming bugfix work.
- **Fix sketch:** fix the finding's cause — the file and line it names, or the check that raised it — and move this entry to Fixed with a Fix paragraph showing the finding gone.

### the stage self-check finding "this run moved a backlog entry another instance of this role is working on: "Local hook suite extraction: move the Git…" was not closed by the fix-up turn and re-fires each run (filed by tumwater 2026-11-21)

- **Symptom:** the pre-queue self-check raised this finding on the run's change; the one-turn fix-up could not close it and reverted the whole change instead, so the run ended `no_change` (`selfCheckReverted`) and the finding lived only in the run's warning event.
- **Finding:** `this run moved a backlog entry another instance of this role is working on: "Local hook suite extraction: move the Git plumbing tests into their own module (planned 2026-11-20 by the plan role)" — it is that instance's task (see <held-entries>), so revert every edit made for it, including the entry…`
- **Reproduce:** author a change that trips a pre-queue self-check finding the fix-up resolves by reverting the whole change (clean tree); the run ends `no_change` with only the self-check warning carrying the finding.
- **Cause:** a finding the fix-up could not close was never filed to BUGS.md, so the same finding re-burned the same authoring each run instead of becoming bugfix work.
- **Fix sketch:** fix the finding's cause — the file and line it names, or the check that raised it — and move this entry to Fixed with a Fix paragraph showing the finding gone.

**Needs review 2026-11-21 by bugfix: the fix belongs to the tumwater maintainer, not this repo.** The "this run moved a backlog entry…" wording comes from tumwater's own pre-queue self-check; the repo mentions that self-check only in comments (`tests/support/placeholders_mutations.py:27`, `tests/support/invariants_mutations.py:29,101`). Nothing in the repo produces the finding, so the entry was not moved to Fixed. Next failure: the self-check warning reappearing with the same wording on the next run.

## Won't fix

### A killed GTK selection commit can leave settings files at different transaction versions (found by the robustness role 2026-11-01)

**Won't fix 2026-11-02 by the director role — user accepted the refusal**

Covered by the project-wide SIGKILL decision in PRINCIPLES.md (directed by the user
2026-11-02). Partial publication and leftover backups after SIGKILL are accepted limitations;
roles should use that standing decision when triaging equivalent reports.

`tools/gtk_staging.py::commit` publishes the GTK 3 settings, GTK 4 settings and GTK 4 user CSS
with separate replacements. Its rollback runs only when Python catches an exception; if the
process receives `SIGKILL` after one replacement, later files retain their old contents while
the first file contains the new selection, and its hidden hard-link backup remains. The GTK
selection is then partly applied despite the caller never completing.

Reproduce by staging different contents for two existing settings files, running `commit`, and
delivering `SIGKILL` after the first `os.replace` returns but before the second begins. The first
target contains new bytes, the second retains old bytes, and a `.backup` sibling remains. Recovery
would require a durable transaction record or another crash-consistent publication design;
in-process exception rollback cannot run after `SIGKILL`, and automatic recovery could overwrite
user edits made after the interrupted commit.

## Fixed
