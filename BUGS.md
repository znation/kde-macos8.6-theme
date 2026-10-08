# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### No objective fidelity check for "pixel-perfect" (structural risk, found 2026-10-07)

**Symptom:** The initial prompt asks for theming "as close as possible to pixel-perfect," but the
repo cannot measure a rendered surface against its Mac OS 8.6 reference image. Any loop can claim a
surface matches and no reviewer can confirm or reject the claim.

**How to reproduce:** Ask for the current fidelity of any surface (menu bar, title bar, scrollbar).
There is no render path, no capture step and no comparison, so the only possible answer is
qualitative.

**Suspected cause:** No visual-fidelity harness exists. The repo holds the reference screenshots and
their provenance, but no code renders the theme, captures a surface, and compares it against the
retail-labelled images in `macos8.6-screenshots/`. This is missing infrastructure, not a one-line
bug.

**Next step:** Plan a fidelity-check harness — a fixed-size Plasma render, a surface-capture step,
and a repeatable comparison against the retail-labelled references — before surfaces are claimed
done.

## Fixed

_None yet._
