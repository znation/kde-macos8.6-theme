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

### Clicking where an unfocused window's title-bar buttons would be presses those invisible buttons (found by the director role 2026-11-04) — fixed 2026-11-05

**Fixed 2026-11-05 (user-directed, live-verified).** Three defects were behind the report. The
hit surfaces were gated on 2026-11-04 by the KWin/Decoration package's
`decoration.client.active` QML (parts 1/3-3/3 of the PLANS.md redesign the refusal routed), but
that gate sat in the package's `DecorationButton.qml`, whose type the explicit
`org.kde.kwin.decoration` import shadows: the module exports its own `DecorationButton`, so the
local copy never ran and the unfocused close cell still closed its window. The effective gate now
sits on the `AuroraeButton.qml` subclass item (`enabled` returns false unless `decoration.client.active`, then the base's
capability switch) and on the `AppMenuButton.qml` fallback, while `MenuButton.qml` and
`AuroraeMaximizeButton.qml` keep their gated standalone MouseAreas; a click on an unfocused bar
therefore falls through to the title bar's activation. Pinned by
`tests/test_aurorae_ui_qml.py::TestHitSurfaces::test_aurorae_button_gates_the_subclass_item`
beside the existing hit-surface pins. The art stayed wrong too: each button SVG's
`inactive-center` group was empty, and
KSvg's `FrameSvg::hasElementPrefix("inactive")` resolves through `hasElement("inactive-center")`
to a valid `boundsOnElement`; an empty group has zero bounds and reports false, so
`AuroraeButton.qml` drew its `buttonActive` overlay on unfocused windows. Each of
`close.svg`, `maximize.svg`, `restore.svg` and `shade.svg` now carries one paintless
full-canvas path (`fill="none"`) in that group, which gives it bounds without paint; the
inactive slice still renders no pixel. Pinned by
`tests/test_aurorae_buttons.py::TestButtons::test_inactive_center_keeps_paintless_geometry`
beside the existing empty-slice pin, with the art digests re-recorded in
`tests/test_aurorae_ui_qml.py`. Live evidence this run: after installing the art and reloading
the decoration, `~/.cache/ksvg-elements` resolves the group (the installed `close.svg` now holds
valid element rects instead of one), and a screenshot shows the unfocused Firefox title bar with
no close, zoom or collapse art while the focused Konsole bar draws all three boxes. After a fresh
KWin loaded the package, a synthetic absolute-pointer click on an unfocused close cell activated
that window and left it open, while the same click on a focused window closed it.

**Validation gap:** real-run-needed — the shadowed-component gate and the corrected one are
session-level: only a live click on an unfocused title-bar cell exposed that the imported
module's `DecorationButton`, not the package copy, owned the hit area. The offline pin is the
subclass gate plus the art tests, and the live close-cell click above is the observation.
