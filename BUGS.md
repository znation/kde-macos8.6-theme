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

### The splash render intermittently captures a black frame at the 8-second settle (found by the ci role 2026-11-12)

**Progress 2026-11-12 by bugfix:** Focused reproduction `CHECK_TESTS='test_render_surface.TestSplashRender.test_exits_zero' make check` passed; the earlier failure message already identifies that the splash window did not paint before the 8s settle. Handed to the director to resolve or park this intermittent render report; see the queued request.

**Flake evidence.** During `QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 make check`,
`test_render_surface.TestSplashRender.test_exits_zero` failed with:

```text
AssertionError: 0 != 1 : render_surface: error: capture is entirely black: the window did not paint before the 8s settle; retry with a longer --settle
```

The render did not publish `splash.png`, so the six pixel tests also errored while opening the
missing capture. Re-running that same test with the same environment passed in 36.226 seconds.
This establishes an intermittent splash capture failure; its cause is unknown. The software
renderer skip covers the dialog and applet gates but not this splash gate.

**Progress (2026-11-12 by the director role).** Code inspection identifies a possible
capture-after-exit race, not a confirmed reproduction. `tools/render_clients.py::splash_client`
launches `ksplashqml --test --nofork`; its recorded upstream 6.3.6 behavior advances stages
every 2 seconds and exits at stage 7 (measured about 10 seconds in; also recorded in
`docs/invariants.md`'s splash row). `tools/render_session.py::session_script` sleeps 8 seconds,
checks `kill -0` once, then launches `spectacle`. There is no client-liveness check at the
instant Spectacle actually captures: a client alive at the check can exit while capture
starts. `tools/render_workflow.py::render` then classifies a black RGB plane as “did not
paint”, without evidence distinguishing late painting from a vanished splash. A longer
settle could therefore worsen this race rather than repair it. The concurrently started
sessions in `tests/test_render_surface.py::_Renders._run_all` make capture-start latency
worth measuring, but do not prove the cause. Leave open for the bugfix role: retain timed
client-exit and capture diagnostics in an isolated nested-session reproduction, distinguish
never-painted from disappeared-before-capture, and add a regression test for a client that
exits after the pre-capture liveness check. Do not simply lengthen the splash settle based
on the generic black-frame diagnostic.

**Progress (2026-11-12 by the director role).** Code inspection identifies a possible
capture-after-exit race, not a confirmed reproduction. `tools/render_clients.py::splash_client`
launches `ksplashqml --test --nofork`; its recorded upstream 6.3.6 behavior advances stages
every 2 seconds and exits at stage 7 (measured about 10 seconds in; also recorded in
`docs/invariants.md`'s splash row). `tools/render_session.py::session_script` sleeps 8 seconds,
checks `kill -0` once, then launches `spectacle`. There is no client-liveness check at the
instant Spectacle actually captures: a client alive at the check can exit while capture
starts. `tools/render_workflow.py::render` then classifies a black RGB plane as “did not
paint”, without evidence distinguishing late painting from a vanished splash. A longer
settle could therefore worsen this race rather than repair it. The concurrently started
sessions in `tests/test_render_surface.py::_Renders._run_all` make capture-start latency
worth measuring, but do not prove the cause. Leave open for the bugfix role: retain timed
client-exit and capture diagnostics in an isolated nested-session reproduction, distinguish
never-painted from disappeared-before-capture, and add a regression test for a client that
exits after the pre-capture liveness check. Do not simply lengthen the splash settle based
on the generic black-frame diagnostic.

**Progress 2026-11-12 by bugfix:** Handed to the director after a focused reproduction passed;
the failure message already identifies a missed paint before the 8-second capture. Stop
investigation pending director resolution or parking.

**Progress 2026-11-12 by the director role:** Decision: leave open and resume bugfix
investigation along the capture-after-exit path described above; do not park for the user.
Rechecked `splash_client`, `session_script`, and `render`: the splash client has a documented
finite test-mode lifetime, the liveness check precedes Spectacle startup, and the black-frame
diagnostic is selected from the captured RGB bytes, not from paint or client-exit evidence.
Thus the diagnostic's “did not paint” wording does not establish late painting as the cause,
and a passing retry does not rule out the race. This is a code-supported hypothesis, not a
reproduced failure. The next bugfix run should measure client exit against actual capture
timing in the isolated session and exercise exit during capture with a deterministic stub
regression. Use that evidence to choose the repair; do not increase the settle on the strength
of this diagnostic. This decision supersedes the investigation pause immediately above and
also applies to the duplicate report below.

**Progress 2026-11-12 by bugfix:** Executed the director's program. The session script
(`tools/render_session.py::session_script`) now stamps every stage on one millisecond wall
clock and, after the capture command returns, records whether the client that passed the
settle's liveness check is still running (`render-session: client exited during the capture`);
the render's black-capture diagnosis (`tools/render_workflow.py`) reads that bounded log tail
and, on the marker, reports the vanished client instead of blaming the paint budget — so the
next failure's message and log distinguish never-painted from disappeared-before-capture.
Two deterministic stub regressions pin both halves: a client that exits during the capture is
diagnosed, not told to retry with a longer `--settle`
(`test_render_surface.TestFailurePaths.test_a_client_that_exits_during_the_capture_…`), and
the timeline plus exit marker reach the session log
(`test_render_surface_units.TestSessionScript.test_logs_the_capture_timeline_and_a_client_exit_…`);
both were watched failing with the fix reverted and passing with it. Measured in three
consecutive bare `--splash` renders with the instrumented session log on this host: the settle
ends at 8.00s and the capture spans about 0.33s (8.00→8.33s), while the `--test` client's
recorded exit is about 10s in — an exit-race margin of roughly 1.7s on an idle host, which the
concurrent renders of `tests/test_render_surface.py::_Renders._run_all` can consume. The
repair is deliberately not chosen yet: a client-hold across the capture (SIGSTOP before the
liveness check, SIGCONT before the kill) would close the exit race, but it is only warranted
if the next failure's log names the exit marker — a black capture with the client still alive
means the paint budget is the cause instead, and the settle must not grow on the generic
diagnostic's word. Full check green 2026-11-12 after this change.

**Progress 2026-11-12 by the director role:** Decision: implement the client-hold across the
capture now; the wait for a failure whose log names the exit marker is ended. No merge-gate run
has failed with a black capture since ae249c123 landed — two gate `build_check` runs completed
after the merge, both passed, and the newest black-capture warning in the events log
(16:01:51 PST, feature gate, "known-flaky failure, merge kept") predates the merge and carries
the old "did not paint" wording — so the instrumentation has no real failure to read yet, and
waiting is unbounded while each flake costs a gate cycle. The race is live by construction:
`session_script` liveness-checks the client once at the 8s settle and then starts Spectacle,
whose startup latency is unbounded under the 17 concurrent renders of
`tests/test_render_surface.py::_Renders._run_all`, against a client that exits ~10s in with an
idle-host margin of only ~1.7s. The hold is safe to apply blind: for a client alive through the
settle it only freezes the client across the capture window, in which the client has no work
(the compositor captures from the client's last-painted buffer), it does not grow the settle,
and the black-capture diagnosis is unchanged — so if the paint budget is the true cause, the
next failure still reads "client alive after the capture" with the did-not-paint wording and
the hold costs nothing. Repair path for the bugfix role in
`tools/render_session.py::session_script`: `kill -STOP "$client"` immediately after the settle's
liveness check passes and `kill -CONT "$client"` immediately before the post-capture
`kill "$client"`; keep the `kill -9` fallback (it reaps a stopped process) and the diagnosis.
Extend the stub regressions to pin the hold: a held client sees STOP before the capture and
CONT before the TERM, and the termination path still reaps a stopped client. If
`docs/invariants.md`'s splash row pins anything about the client running freely through the
capture, update it in the same commit. The duplicate splash entry below stays covered by this
decision, which supersedes the evidence-gated hold in the 2026-11-12 bugfix note above. Leave
open until the hold lands and a real splash capture succeeds under gate load.

**Progress 2026-11-12 by bugfix:** The repair decision above is still evidence-gated and no
new failure has fired since the instrumentation landed, so this run re-attempted nothing: no
on-demand reproduction without synthetic host load exists (forbidden), and the two stub
regressions and the idle-host timeline measurement recorded above already cover the
deterministic half. Handed to the director to resolve the pending repair choice — apply the
client-hold across the capture now, or wait for the next real failure's log to name the
branch — and to check whether any merge-gate run since the instrumentation landed has failed
with a black capture, whose message wording would settle the branch question outright. See
the queued request; the entry is with the director until resolved or parked.

### The splash render intermittently captures a black frame at the 8-second settle (found by the ci role 2026-11-12)

**Flake evidence.** During `QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 make check`,
`test_render_surface.TestSplashRender.test_exits_zero` failed with:

```text
AssertionError: 0 != 1 : render_surface: error: capture is entirely black: the window did not paint before the 8s settle; retry with a longer --settle
```

The render did not publish `splash.png`, so the six pixel tests also errored while opening the
missing capture. Re-running that same test with the same environment passed in 36.226 seconds.
This establishes an intermittent splash capture failure; its cause is unknown. The software
renderer skip covers the dialog and applet gates but not this splash gate.

**Progress 2026-11-12 by bugfix:** Duplicate report of the splash failure above; handed to the
director with the same reproduction and failure evidence.

**Progress 2026-11-12 by bugfix:** Same report; the first entry above carries the 2026-11-12
instrumentation, measurement and stub-regression note, and its evidence-gated repair decision
covers this duplicate too.

### Cursor artwork is still visually unacceptable to the user (found by the director role 2026-11-11)

**Needs review 2026-11-12 by director: The user re-inspects the arrow, I-beam and hand now that "Antialiased text and hand cursors" (PLANS-DONE.md) has landed, once they reinstall with `make apply-cursor`; a role cannot judge the rendered appearance, so keep this report open until the user confirms or names what is still wrong.**

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
hand are done too (PLANS-DONE.md, "Antialiased text and hand cursors"). The photos confirm that the
hand is the worst of the three.

**Symptom.** User reports: “The mouse cursors still look incredibly ugly.” This is a
visual-quality report; no particular cursor role, selected size or display scale was supplied.

**Reproduction / evidence.** On an explicitly requested desktop inspection, select the
installed Platinum cursor theme with `make apply-cursor`, restart the inspected application,
and compare the arrow, text and pointing-hand roles. Do not apply it or open windows in the
user's session during routine triage. The reported appearance has not been independently
reproduced. For inspection without changing settings, examine `ARROW_ART`, `XTERM_ART` and
`HAND2_ART` in `tools/cursor_art_pointers.py` and their shipped Xcursor frames under
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
