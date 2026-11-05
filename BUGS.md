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

### Clicking where an unfocused window's title-bar buttons would be presses those invisible buttons (found by the director role 2026-11-04)

**Symptom.** As designed since 2026-11-04, an unfocused window's title bar is a flat buttonless
strip. But the button actions are still live there: clicking in the unfocused title bar at the
spot where the close box would sit closes the window, and similar clicks trigger maximize/shade.
The user's screenshot shows a focused-looking window whose bar buttons appear correctly — the
failure is on the *unfocused* windows: art says nothing is there, hits say otherwise, so a click
the user intended merely as refocusing can close a document window.

**How to reproduce.** On a Plasma session with Platinum applied, focus another window, then
click in the first window's title bar where its close box would be (13×13 px cells flush at the
title-edge, `ButtonWidth=13`/`ButtonMarginTop=4` in `org.macos8.desktoprc`): the window closes.
Moving the pointer there shows no hover feedback, so the target is invisible.

**Suspected cause (verified against the installed engine).** KWin composites Aurorae buttons
from a per-button QML item whose art and hit area are independent. In
`/usr/share/kwin/aurorae/AuroraeButton.qml` (KWin 6.3.6, inspected 2026-11-04) `visible` is set
once at `Component.onCompleted` from `buttonSvg.imagePath != ""` — never bound to
`decoration.client.active` — and in `/usr/share/kwin/aurorae/DecorationButton.qml` the
`MouseArea` accepts clicks purely on geometry with `enabled` gated only on closeable,
maximizeable and minimizeable. The fixed no-box look emptied the four button SVGs'
`inactive-center` groups (BUGS-FIXED "Hovering or pressing an unfocused window's title-bar
button erases it", pinned in `tests/test_aurorae_buttons.py`), which removed the *art* but left
`theme/aurorae/themes/org.macos8.desktop/close.svg`, `maximize.svg` and `shade.svg` present, so
`AuroraeButtonGroup.qml::createButtons()` still creates interactive close, maximize-restore and
shade items for both focused and unfocused windows. A button whose SVG file is absent entirely
(the theme ships no `minimize.svg`) gets an empty path and a `visible=false` item that QML Row
positioners skip, so it is genuinely inert — corroborating that the reachable ghosts are exactly
the buttons still backed by an SVG file.

**Fix direction.** Make interaction follow the art: gate each button item on window
activity so an unfocused window has nothing there to press (a click then falls through to the
title bar and only activates/moves the window). Stock Aurorae exposes no such binding, but an
aurorae theme is a KPackage (`KPackageStructure: KWin/Aurorae` in
`theme/aurorae/themes/org.macos8.desktop/metadata.json`) and the installed loader
`org.kde.kwin.aurorae.so` ships the strings `"/contents/ui/main.qml"` and "Trying to load QML
Decoration", indicating it prefers a `contents/ui/main.qml` from the theme package over the
built-in `/usr/share/kwin/aurorae/aurorae.qml` — to be verified before building on it (e.g. by
shipping a copy of the built-in component set in `theme/aurorae/themes/org.macos8.desktop/contents/ui/`
with the copy's button items bound to `decoration.client.active` and confirming the live session
loads it). If the loader does not honor a package `main.qml`, there is no in-theme fix and this
entry is a refusal candidate with the phantom-click trade-off spelled out to the user.
Acceptance: clicking in an unfocused title bar over the close/maximize cells does not close or
resize the window; the focused window's buttons stay drawn and clickable; the empty
`inactive-center` pins in `tests/test_aurorae_buttons.py` remain true.

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
