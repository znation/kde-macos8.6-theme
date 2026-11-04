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

### Under a loaded host the live GTK dialog gate flakes: an all-black capture, or a mid-transition compose that misses four pinned cells (found by the plan role 2026-11-04)

**Symptom.** Two consecutive full `make check` runs (2026-11-04 00:36 and 00:41, this worktree unmodified at main except PLANS.md prose) failed their `test_render_surface` module on the GTK dialog gate alone while every other module and a focused `make check CHECK_TESTS=test_render_surface` run (`Ran 68 tests ... OK`) stayed green, and two consecutive serial `tools/render_surface.py ... --gtk-dialog` runs byte-matched all four pinned cells (`ENTRY_FIELD_CROP`, `OK_BUTTON_CROP`, `CANCEL_BUTTON_CROP`, `WINDOW_SHELL_EDGE_CROP`) by direct pixel read.

1. Run 1: `test_draws_the_entry_field_cell_1_to_1`, `test_draws_the_action_button_row_cell_1_to_1`, `test_draws_the_cancel_button_cell_1_to_1` and `test_draws_the_window_shell_edge_cell_1_to_1` all failed with blended actual colours (`#B2B2B2`, `#373737`, `#3A3A3A`, `#9C9C9C` and a shell face row reading `#000000` against the same single pooled capture — no cell matched). The composed window is off the pinned integer grid, consistent with a client still mid-placement or mid-animation inside the 8 s default settle when the capture fired. The render exited 0, so the landed all-black refusal did not catch this capture.
2. Run 2: `render_surface: error: capture is entirely black: the window did not paint before the 8s settle; retry with a longer --settle` — the landed refusal worked as designed, `test_exits_zero` failed, and six tests errored reading the unpublished `dialog.png`.

**How to reproduce.** Run the full `make check` on a loaded host (the parallel coordinator runs whole modules concurrently, and this machine carries other tenants); the gtk render starts with the four other render kinds in `tests/test_render_surface.py::TestGtkDialogRender`/`_Renders` and its 480x360 zenity window either is not painted at settle expiry or is captured mid-transition. Focused runs and serial renders with the same settle budget are green.

**Suspected cause.** Under load the GTK dialog client paints later than the fixed 8 s default `--settle` budget; the checkbox, combobox and menu gates passed in both failed runs, so it is specifically the painted-then-captured timing window of the GTK client. Candidate repairs (the fix decision is open): raise the settle/timeout the gate scaffolding passes, or replace the fixed settle for this client with a bounded readiness poll the way the `BUGS-FIXED.md` record of 2026-10-26 already made the radio-indicator test load-tolerant. Whether the mid-transition compose in run 1 (which paints, so it sneaks past the black refusal) needs its own acceptance check beyond a longer settle is part of that decision.

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
