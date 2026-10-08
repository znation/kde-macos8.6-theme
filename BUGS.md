# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### No automated Plasma render/capture step feeding the fidelity check (found 2026-10-07)

**Symptom:** `tools/fidelity.py` can measure a candidate PNG against a reference, but nothing
produces the candidate: there is no scripted way to render a themed surface and capture it to PNG,
so a fidelity check still starts from a hand-made screenshot.

**How to reproduce:** Look for a command that renders a Plasma surface with the theme applied and
writes a PNG. None exists; the planned `make check` exercises only the color scheme and the
comparison tool.

**Suspected cause:** No theme package exists yet, so there is nothing to render. The render step
depends on the Platinum color scheme and the widget/decoration packages landing first.

**Next step:** Once theme code exists, add a bounded, non-interactive render-and-capture script
(fixed surface size) that writes the candidate PNG this tool consumes, and wire it into `make check`.

**Refused 2026-10-07 by bugfix: the only theme artifact is the color scheme — no widget/decoration package exists to render and no offline QML/Plasma render path is available, so a render harness now would be untestable dead code.**

## Fixed

### No objective fidelity check for "pixel-perfect" (structural risk, found 2026-10-07; fixed 2026-10-07)

**Symptom:** The initial prompt asks for theming "as close as possible to pixel-perfect," but the
repo could not measure a rendered surface against its Mac OS 8.6 reference image. Any loop could
claim a surface matches and no reviewer could confirm or reject the claim.

**How to reproduce:** Ask for the current fidelity of any surface (menu bar, title bar, scrollbar).
There was no render path, no capture step and no comparison, so the only possible answer was
qualitative.

**Suspected cause:** No visual-fidelity harness existed. The repo held the reference screenshots and
their provenance, but no code compared a captured surface against the retail-labelled images in
`macos8.6-screenshots/`.

**Fix:** `tools/fidelity.py` decodes PNG candidates and references (8-bit, non-interlaced, color
types 0/2/3/4/6) with only the standard library, crops a reference to a surface region, and reports
objective metrics — mean absolute error, RMSE, worst per-channel delta, and differing-pixel
fraction — exiting non-zero when the result is outside the requested tolerance.
`tests/test_fidelity.py` covers decoding (palette plus every PNG filter type), the metrics, cropping,
and the CLI pass/fail paths. Producing the candidate PNG (the Plasma render step) is still missing
and is tracked as its own Open entry above.

**Validation gap:** unclear-invariant — "pixel-perfect" had no numeric definition and the repo had
no comparison path, so the objective metric and threshold had to be defined before the gap could be
confirmed.
