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

### The Kvantum button-reference test still pins the `button-default-indicator` group the reviewer fix removed from the shipped SVG, and the color and icon dialog gates draw a gradient push-button face (found by the plan role 2026-11-11)

**Symptom.** `make check` fails in two modules. First, `tests/test_kvantum_button_reference.py::TestButtonReference::test_default_button_indicator_keeps_the_face_flat` asserts exactly one `button-default-indicator` group in the shipped `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` and got zero — commit `dfd954379` (the 2026-11-11 reviewer fix for a993c56b) deleted the whole `<g id="button-default-indicator">` block when removing the duplicate 7x7/8x8 markers, but that commit touched no test, so the landed assertion still counts the removed group. Second, `tests/test_render_surface.py`'s `TestColorDialogRender` and `TestIconDialogRender` fail their two push-button tests each (`test_draws_the_push_button_frame_and_cell`, `test_draws_the_push_button_face_at_the_landed_recipe`): the asserted flat `#DDDDDD` face rows and right-bevel column read a `#E4E4E4`→`#E7E7E7` gradient instead (first differing element 72 of the face row).

**Reproduce.** `python3 tests/test_render_surface.py TestColorDialogRender` on this host fails the same two tests in isolation (twice, ~32 s each), and `make check` reports 336 modules with those 2 failed. The failing worktree differs from HEAD only in backlog prose files, so neither failure is caused by the recording run's change; `TestFileDialogRender` and every other render gate in the module passes.

**Suspected cause.** For the button-reference failure, the reviewer fix removed the group id the landed test pins without updating the test (the commit message says the shipped indicator stays the parent's slot-measured 8x8 art, but no group carries that id any more). For the dialog gates, the same default-button area is the prime suspect: with the indicator art gone, Kvantum's own default-button painting (a subtle gradient interior) may now cover the flat face the flat recipe pins; whether the two symptoms share that root is for the fix to establish.

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
