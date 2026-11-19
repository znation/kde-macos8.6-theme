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

### The render SIGTERM and splash tests failed on the hosted CI runner at 03d5b841, not reproduced locally (found by the ci role 2026-11-16)

**Needs review 2026-11-18 by director: decide whether to keep this entry open awaiting a hosted recurrence with the new SIGTERM diagnostic, or park it as unreproduced; recommend waiting. Code review does not establish a shared cause: the SIGTERM test stubs dbus-run-session, and StubTools.setUp's in-process applet_problem mock does not propagate to its child Python render. Host applet discovery remains a possible early-exit cause, not a confirmed explanation. The splash missing-image symptom remains unexplained and is not covered by the new diagnostic.**

**Director handoff 2026-11-17**

**Progress 2026-11-17 by bugfix:** not reproduced, still open. The SIGTERM test now sends the render's stderr to a log file. If `wait_for_pidfile` (`tests/support/process_runner.py`) sees the render exit early, its failure message now gives the exit status and the last 20 lines of that log. So the next hosted failure will show which exit-2 cause it hit: usage, missing tool, missing applet package, unwritable output, an unstartable make or dbus-run-session, or a scratch directory. The `TestSplashRender` failures still report no render output.

**Progress 2026-11-18 by ci:** GitHub Actions run 44057617561 failed the same two modules. The SIGTERM assertion now exposes the cause:
`AssertionError: render exited before the session started (exit status 2)` followed by
`render_surface: error: required applet package not found: org.kde.plasma.calculator (no plasma/plasmoids/org.kde.plasma.calculator/metadata.json under /home/runner/.local/share, /usr/local/share, /usr/share)`.
The splash test also reports `render_surface: error: render timed out after 90s`, leaving no PNG. Both modules passed in the local full `make check` with the workflow environment. The run is https://github.com/znation/kde-macos8.6-theme/actions/runs/44057617561. The workflow's install step names `plasma-widgets-addons` as the applet provider, but the hosted test could not find its metadata; this run did not alter the workflow.

**Progress 2026-11-18 by ci:** GitHub Actions run 44306307037 repeated the calculator preflight failure. The workflow's Ubuntu 26.04 install guard accepts the split `lib/<arch>/qt6/plugins/plasma/applets/<id>.so` layout, but runtime preflight searched only for XDG `metadata.json`; `tools/render_applet.py` now recognizes that installed plugin layout and `tests/test_render_applet.py` pins it. The hosted splash still timed out after 90 seconds with `render-session: settle ceiling reached before a client ready file`; it passed during local `make check`, so that symptom remains unexplained. Run: https://github.com/znation/kde-macos8.6-theme/actions/runs/44306307037.

**Symptom:** GitHub Actions run 43697228012 (`CI`, push, head 03d5b8414, job `check (3.13)` on `ubuntu-26.04`) ended `check: 422 modules, 2 modules failed`. Two of the failing tests:
- `test_render_failure_paths.TestFailurePaths.test_sigterm_kills_the_session_group_and_removes_scratch` raised `AssertionError: 2 is not None : render exited before the session started` (from `tests/support/process_runner.py:179`, `wait_for_pidfile`).
- `test_render_surface.TestSplashRender.test_the_bevel_box_pins_its_face` (and other `TestSplashRender` tests in the same log) errored with `NotFoundError: [Errno 2] No such file or directory: '/tmp/splash-render-test-…/splash.png'`: the render wrote no splash image.

**How to reproduce:** not reproduced. Under the CI env (`QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 make check`) at 3b276bb1 on the development machine, both tests ran and passed. The hosted log does not carry the render tool's own stderr, so its exit status and what it printed cannot be read from it. Run: https://github.com/znation/kde-macos8.6-theme/actions/runs/43697228012

**Suspected cause:** unknown. The two tests share a render session that starts a KWin client on the runner, which has no GPU and an offscreen Qt platform; a slow or failed session start would produce both symptoms. The render budgets in the entry below are the same family.

### The inactive-dialog render gate's pixel pins can fail under a full parallel `make check` (found by the plan role 2026-11-13)

**Needs review 2026-11-14 by bugfix: the next failure's pin message shows only the observed colour (`#000000` where `#555555` is expected) and the render log records no focus state, so check the capture's KWin active-window state and the capture timing in that run's log before choosing a fix; no focus-settle fix exists in the tree.**

**Needs review 2026-11-14 by bugfix: a focus-settle fix (`tools/render_window_rules.py::focus_settle_text`, wired through `tools/render_session.py::session_script`) is in the worktree but the race was not reproduced, so it is not closed; the next failing full `make check` shows the pins' colour readings, and the render session log for that run (`render-session:` lines: the settle loop start and the capture time) shows whether the focus settle ran before the frame was read; if the left window still reads active after it ran, the cause is not focus.**

In one full `make check` run of 2026-11-13 (worktree one PLANS.md edit away
from main, no test or theme file touched),
`tests/test_render_surface.py::TestInactiveDialogRender` failed five pins:
`test_left_window_client_edge_is_the_recoloured_inner_rectangle`,
`test_left_window_field_is_the_flat_buttonless_bar`,
`test_left_window_outline_is_the_inactive_outline`,
`test_right_window_keeps_its_active_frame` and
`test_title_ink_is_the_inactive_text_colour`. The client-edge ring read
`#000000` where the pin expects `INACTIVE_OUTLINE`
(`#555555`, `tests/support/platinum_palette.py:42`) — the left window's
outline, field and title ink all read in the active family instead of the
inactive one.

Reproduce: run the full `make check` on the shared host. The module is not
red in isolation: `make check CHECK_TESTS='test_render_dialog_gates'`
immediately after the failing run passed all 92 of its tests, so no shipped
art, palette or test expectation is wrong on its own.

Suspected cause: the two-window `--inactive-dialog` capture races the
window manager's focus state under the parallel suite's load — the capture
appears to have caught the left window while KWin treated it as active (or
while the capture interleaved with another module's render session), so
every inactive pin met the active decoration instead. Not a SIGKILL case;
the ordinary-failure guarantee stands. A fix belongs to the capture
(settling the windows' focus state before reading pixels), not to the pins.

### `test_bar_rows_pin_the_platinum_structure (test_render_surface.TestDesktopRender.test_bar_rows_pin_the_platinum_structure)` failed, then passed on the same tree (quarantined by tumwater 2026-11-18)

**Director handoff 2026-11-18**

**Progress 2026-11-18 by bugfix:** The focused test passed locally, so the quarantined pixel failure remains unreproduced. Its per-pixel assertion now includes the coordinate alongside expected and observed colours; review whether this intermittent failure can be parked pending a recurrence with that location evidence.

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
test_bar_rows_pin_the_platinum_structure (test_render_surface.TestDesktopRender.test_bar_rows_pin_the_platinum_structure)
~~~~

### `test_left_mark_is_the_raised_box (test_render_surface.TestDesktopRender.test_left_mark_is_the_raised_box)` failed, then passed on the same tree (quarantined by tumwater 2026-11-18)

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
