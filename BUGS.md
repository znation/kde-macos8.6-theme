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

### Cursor artwork is still visually unacceptable to the user (found by the director role 2026-11-11)

**Needs review 2026-11-12 by director: The user re-inspects the arrow, I-beam and hand after "Antialiased text and hand cursors" (PLANS.md) lands and they reinstall with `make apply-cursor`; a role cannot judge the rendered appearance, so keep this report open until the user confirms or names what is still wrong.**

**User evidence 2026-11-12 (recorded by the director role).** The user sent three photos of the
screen, showing the cursors installed at `~/.local/share/icons/org.macos8.desktop/cursors/`.
The photos are evidence only. Keep them out of the repo.
- *Arrow (gray desktop):* a small solid-black triangle with a staircase diagonal edge and a stubby
  square tail. No antialiasing is visible, and the white outline cannot be seen against the light
  gray. The installed `left_ptr` (installed 2026-11-12 01:38) differs from main's file
  (`cmp`), so this photo shows the old `ARROW_GRID` art, not the vector arrow from 01f2f3184.
  The installed `hand2`, `xterm` and `pointer` match main byte for byte.
- *I-beam (over body text):* a serifed black I-beam that is legible. It is crisp but plain, about
  1.3× the text's cap height.
- *Pointing hand (over a white page):* it does not read as a hand. It shows as a black comb-like
  block (vertical prongs above a solid bar). That is consistent with `HAND2_GRID`'s single
  1-cell finger and rectangular palm after nearest-neighbour enlargement. Moiré in the photo may
  add some of the striping.
- The user did not state the selected size or display scale, and the photos do not establish
  either.

**Direction.** QUESTIONS.md is answered: Option 2, smoother original antialiased art (user,
2026-11-12). The arrow is done (PLANS-DONE.md, "Antialiased cursors, part 3/3"). The I-beam and
hand are queued in PLANS.md as "Antialiased text and hand cursors". The photos confirm that the
hand is the worst of the three.

**Symptom.** User reports: “The mouse cursors still look incredibly ugly.” This is a
visual-quality report; no particular cursor role, selected size or display scale was supplied.

**Reproduction / evidence.** On an explicitly requested desktop inspection, select the
installed Platinum cursor theme with `make apply-cursor`, restart the inspected application,
and compare the arrow, text and pointing-hand roles. Do not apply it or open windows in the
user's session during routine triage. The reported appearance has not been independently
reproduced. For inspection without changing settings, examine `ARROW_GRID`, `XTERM_GRID` and
`HAND2_GRID` in `tools/cursor_art_pointers.py` and their shipped Xcursor frames under
`theme/icons/org.macos8.desktop/cursors/`.

**Suspected cause.** `tools/make_cursors.py::render_rgba` enlarges a shared 16×16 source grid
using nearest-neighbour sampling for `NOMINAL_SIZES = (16, 24, 32)`. At 24 pixels this gives
unequal source-pixel widths; coarse silhouettes and outlines are also possible contributors.
These are code observations and hypotheses, not a diagnosis of the user's selected cursor.

**Routing.** The open cursor-direction question in QUESTIONS.md records the aesthetic fork.
Do not close this report merely because frame encoding, aliases or grid-equality tests pass.
After direction is settled, route a redraw as small per-family PLANS.md entries, with original
artwork, explicit size/hotspot expectations, regression tests and provenance for the reference
surface that is missing. Investigate selection or scale defects separately if demonstrated;
this report does not establish either defect.

**Progress 2026-11-11 by bugfix:** Handed to the director because the reported visual defect
cannot be reproduced without an explicitly requested desktop inspection, and the replacement
direction is still an open user decision. No desktop selection or rendering was attempted. The
recorded inspection path is to select the installed theme and compare arrow, text and pointing-hand
roles; static source inspection identifies nearest-neighbour enlargement from 16×16 to 24/32 and
coarse silhouettes as hypotheses, not a confirmed cause. Do not close on encoding or grid tests.

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
