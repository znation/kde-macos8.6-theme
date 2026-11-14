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

### The client-exit stub test `test_waits_for_client_termination_and_preserves_capture_status` fails under a parallel `make check` (found by the coverage role 2026-11-14)

In one full `make check` run the test failed with `AssertionError: 0 != None` at `tests/test_render_surface_units.py:1084` (`self.assertEqual(capture_status, status)`), with `capture_status=0`. The same module run alone passed (155 tests OK). BUGS-FIXED has a closed entry for a different load-sensitive test in the same client-exit stub family ("The client-exit stub regression is load-sensitive", closed 2026-11-12, naming `test_a_client_that_exits_during_the_capture_is_not_blamed_on_the_paint_budget`); this test is not named there. The coverage change that ran in the same `make check` touched only `tests/test_cursor_vector.py`, so it is not the cause as far as the diff shows.

Next step: check whether the stub's exit status is read before the stubbed client has finished writing it under load, and make the test wait for the status, not sample it.

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
