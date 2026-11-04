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

### Hovering or pressing an unfocused window's title-bar button erases it (found by the director role 2026-11-04)

**Symptom.** With focus on another window, moving the pointer over an unfocused window's close
box makes it vanish entirely against its `#DDDDDD` title bar; it reappears when the pointer
leaves. Pressing an unfocused window's close, zoom or shade button erases it the same way: no
hover or pressed feedback ever appears on an unfocused button. The focused window is
unaffected.

**How to reproduce.** On a Plasma session with Platinum applied, activate a second window so
the first sits unfocused, then move the pointer over the unfocused window's close box: the box
disappears while the pointer is over it.

**Suspected cause (verified against the installed engine).** KWin composites Aurorae buttons
from state overlays keyed by KSvg prefixes (`/usr/share/kwin/aurorae/AuroraeButton.qml`, KWin
6.3.6, inspected 2026-11-04). The four button SVGs in
`theme/aurorae/themes/org.macos8.desktop/` define only `active` and `inactive` prefixes, so
`supportsHover`, `supportsPressed`, `supportsInactiveHover`, `supportsInactivePressed` and the
deactivated companions are all false. `buttonInactive` hides whenever `hovered || pressed`,
and the `hover-inactive` and `pressed-inactive` overlays that should take over are absent, so
on hover or press every overlay's opacity is 0 and nothing is drawn. On a focused window this
cannot happen because `buttonActive` stays shown when the hover/pressed/deactivated prefixes
are missing.

**Fix direction.** Add `hover-inactive` and `pressed-inactive` prefixes to the four button
SVGs, rendering identically to `inactive`: the reference set shows no hover or pressed
appearance for unfocused title-bar boxes, so keeping the unfocused box's own art unchanged is
the grounded value. The PLANS.md plan that empties the inactive button art per the reference
subsumes this symptom; fix it only if that plan is refused, and re-triage this entry after
that plan leaves `## Planned`.

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
