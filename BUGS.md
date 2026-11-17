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

### The title bar's collapse box does nothing when clicked (found by the director role 2026-11-14)

**Needs review 2026-11-14 by director: what the box should do on a window KWin cannot shade is the user's call — see QUESTIONS.md "What should the collapse box do on a window KWin cannot shade?"; confirm the cause below first, then apply the chosen option.**

Symptom (user report, 2026-11-14): the rightmost title-bar button does
nothing when clicked. That button is the collapse box: the theme's button
layout `ButtonsOnRight=AL` (`theme/look-and-feel/org.macos8.desktop/contents/defaults`,
mirrored by `tools/apply_theme.py::DECORATION_BUTTONS`) puts zoom (`A`)
then shade (`L`) at the trailing edge, drawn with
`theme/aurorae/themes/org.macos8.desktop/shade.svg`. It should do what the
Mac OS 8 collapse box does: roll the window up to its title bar, then roll it
back down on a second click.

Reproduce: run `make apply` in a Plasma 6 Wayland session (the user's
session is Wayland; KWin 6.3.6), focus a Wayland-native window (e.g. Dolphin),
click the rightmost title-bar box. Nothing happens. Still to check: whether an
XWayland window (an X11 client) does shade, and what a KWin script prints for
`workspace.activeWindow.shadeable` on each kind of window in the headless
render session (`tools/render_session.py`).

Suspected cause (not confirmed): the click handler works, but KWin ignores it.
`DecorationButton.qml` (the theme's package copy under
`theme/kwin-decoration/org.macos8.desktop/contents/ui/`) calls
`decoration.requestToggleShade()`, and KWin skips the request when the window
is not shadeable. KWin is believed to shade only X11 windows, so Wayland-native
windows never collapse. The button's `enabled` binding also falls through to
`default: return true` for `DecorationButtonShade` and never checks
`decoration.client.shadeable`. As a result the box looks live on a window that
cannot shade. The decoration's shaded geometry
(`Decoration.qml`, `decoration.client.shaded`) is already in place for windows
that can shade.

Fix scope after the question is answered: an `enabled`/click change in
`DecorationButton.qml` (and a matching `docs/invariants.md` row), with a QML
structure test beside the existing decoration-package tests. No new
dependency.

### Render-session tests rely on fixed wall-clock budgets that expire under a parallel `make check` (structural risk, found by the steward role 2026-11-14)

**Progress 2026-11-14 by bugfix:** step 1 (`tools/bounded_wait.py`) and step 2 (`run_logged` names its expired wait in the log, still returns `None`) are in place; the render-session callers are not yet routed through the helper, so this entry stays open.

**Symptom:** the same failure shape recurs across the render suite. A render test waits a fixed
time for the session, the client or the splash to settle, and the wait expires when the full
parallel `make check` shares the host with other modules. The clearest records are:
`test_waits_for_client_termination_and_preserves_capture_status` returning `0 != None` and
`7 != None` because `run_logged` timed out (BUGS-FIXED.md 8-17; its cause is the expired timeout
at `tools/process_group.py:184-186`); the client-exit stub regression that turned a parallel run
red (BUGS-FIXED.md 85-130); the splash capturing a black frame at the 8-second settle (BUGS-FIXED.md
131-281 and 282-304); and the two open entries above, the inactive-dialog pixel pins (21-52) and
the client-wait test (90-110). The 90-110 entry records that its module passes alone.

**Why this is a structural risk:** each recurrence was closed or is being closed one test at a
time, by widening a budget or adding a settle. The splash entry records that lengthening the settle
can worsen the race rather than repair it, so the budgets are not a reliable repair. No shared
bounded-wait helper reports which wait expired, so every new failure must be re-diagnosed from
scratch. A single helper that names the expired wait in its failure message would make the next
recurrence attributable without another reconstruction.

**Progress 2026-11-14 (bugfix):** step 1 is in: `tools/bounded_wait.py::wait_bounded` raises
`WaitExpired` naming the label, budget and pid. Every render-session wait that is a Python process
wait already goes through `run_logged`, which now writes the expired wait's name to the log
(`tests/test_process_group.py` pins this). `tools/render_workflow.py` prints that log tail on a
timeout, so a render timeout already names its wait. The remaining work is the fixed budgets
themselves (settle and timeout defaults), which is a tuning decision rather than a naming gap, so
the risk stays open until someone decides how to size them.

**Progress 2026-11-14 by bugfix:** the sizing choice is the user's call (trade-off between wall time and flake rate). Question posted in QUESTIONS.md ("How should the render-session wall-clock budgets be sized?"). No budget was changed; the entry stays open until the user answers.

**Progress 2026-11-15 by bugfix:** the user answered option 3 ("Let's go with option 3"), but option 3 cannot be built as written. The "settle done" marker in `tools/render_session.py::session_script` is echoed *after* `sleep "$settle"`, so waiting on it would still wait out the fixed sleep. A real readiness signal (the client's window has mapped) does not exist in the session script: the focus-settle loop only watches its own `.done` sentinel. Follow-up question posted in QUESTIONS.md ("What should the settle wait on instead of a fixed sleep?"). No code changed; the entry stays open.

**Progress 2026-11-16 by bugfix:** the user answered option 2 (client writes a ready file; QUESTIONS.md,
2026-11-16). The session side is in: `tools/render_session.py::session_script` exports
`RENDER_SESSION_READY_FILE` and ends the settle early when the file appears, keeping the settle as the
ceiling. Two tests in `tests/test_render_surface_units.py::TestSessionScript` pin it (early exit with a
ready file; full ceiling without one); the first fails on the pre-change script. No client writes the
file yet, so the budgets still expire as before. The client-side writers are planned in PLANS.md
("Render-session readiness: the client writes RENDER_SESSION_READY_FILE"). This entry stays open until they land.

**Progress 2026-11-16 by bugfix:** no client-side writer built this run. The splash client is the upstream `/usr/bin/ksplashqml` binary, which the theme cannot edit, and a wrapper has no offline-checkable "window shown" signal; touching the file after launch would be another fixed budget. The choice of signal is posted as a question in QUESTIONS.md ("How should the ksplashqml client signal that its window is shown?"). No code changed in the client path; the entry stays open.

**Progress 2026-11-17 by bugfix:** the user answered option 2 (the KWin side writes the ready file), but a KWin script has no file-write API (no `writeFile`/`FileIO` in the installed KWin scripts), so that option cannot write the file as worded. Follow-up question posted in QUESTIONS.md ("Option 2 needs a file writer KWin scripts do not have: how should the ready file be written?"). No code changed; the entry stays open.

**Reproduce:** run the full `make check` while other modules run on the shared host. The 90-110
test module is reported green in isolation (`make check CHECK_PATTERN='test_render_surface_units*.py'`).

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

### `test_holds_the_client_across_the_capture_and_resumes_it_before_the_termination (test_render_surface_units.TestSessionScript.test_holds_the_client_across_the_capture_and_resumes_it_before_the_termination)` failed, then passed on the same tree (quarantined by tumwater 2026-11-17) — fixed 2026-11-17 by the bugfix role

**Fixed 2026-11-17 by the bugfix role (diagnosis corrected in review):** not reproduced in 15 unloaded runs, but the cause is visible in the old stub: it wrote the client's state to the capture-state file *before* its poll loop, so the test read a single sample taken right after `kill -STOP`. `kill` returns once the signal is queued; the client, asleep in `pause()`, is woken and must be scheduled before it enters the stopped state, so under a loaded `make check` that sample can read `R`. The stub now records the state after polling for `T` (up to 200 × 10 ms), together with the poll count, and the failure message prints both. A session without the hold still never reaches `T` and fails the test.

The check failed on this test and then passed on a re-run of the same tree, so tumwater quarantined it: it counts as a known failure until this entry leaves `## Open`. Find why it is unstable and fix it.

~~~~
AssertionError: 'T' != 'R'
test_unresolvable_data_home_refusal_names_the_data_home_fallback (test_xdg_homes.TestRequireHome.test_unresolvable_data_home_refusal_names_the_data_home_fallback) ... ok
test_unresolvable_refusal_names_both_received_values (test_xdg_homes.TestRequireHome.test_unresolvable_refusal_names_both_received_values) ... ok
test_the_diagnostics_resolve_the_config_home_through_xdg_homes (test_xdg_homes.TestUninstallConfigSharesTheRule.test_the_diagnostics_resolve_the_config_home_through_xdg_homes) ... ok
test_a_relative_value_is_named_in_shell_quoting (test_xdg_homes.TestUnresolvedHomeState.test_a_relative_value_is_named_in_shell_quoting) ... ok
test_an_empty_value_counts_as_unset (test_xdg_homes.TestUnresolvedHomeState.test_an_empty_value_counts_as_unset) ... ok
----------------------------------------------------------------------
Ran 16 tests in 0.008s
OK
check: 428 modules, 1 module failed
make: *** [Makefile:491: check] Error 1
~~~~
