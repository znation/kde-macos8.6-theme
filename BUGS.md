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

### `plasma-apply-colorscheme` writes a scheme ID that does not survive a restart (found 2026-10-07)

**Symptom:** `plasma-apply-colorscheme MacOS8` — the ID the tool lists for
`theme/color-schemes/MacOS8.6.colors` — reports success and writes `[General]
ColorScheme=MacOS8` into `kdeglobals`. On the next load KDE resolves that value to
`MacOS8.colors`, which does not exist, so the scheme silently falls back to BreezeLight. The value
that resolves to the shipped file is `MacOS8.6`.

**How to reproduce:** With `XDG_DATA_HOME` pointing at a data dir holding
`theme/color-schemes/MacOS8.6.colors`, set the temp `XDG_CONFIG_HOME`'s `kdeglobals` to
`[General] ColorScheme=MacOS8` and run `plasma-apply-colorscheme` with no argument: it prints
`Could not find color scheme "MacOS8" falling back to BreezeLight`. Repeat with
`ColorScheme=MacOS8.6`: it resolves. Applying via the CLI looks correct in the running session, so
the breakage appears only at the next start.

**Suspected cause:** The tool derives a scheme's CLI id from the filename up to the first dot
(`MacOS8`), while its resolver turns the `ColorScheme` config value into `<value>.colors`. A
filename containing a dot therefore has a CLI id that no longer names the file.

**Next step:** Rename the scheme to a dotless filename whose stem equals its `[General]
ColorScheme` (e.g. `MacOS8.colors` with `ColorScheme=MacOS8`, keeping `Name=Mac OS 8.6`), updating
`Makefile`, `tests/test_colorscheme.py`, the README, and — once the look-and-feel package lands —
its `contents/defaults` and test. The look-and-feel plan sets `ColorScheme=MacOS8.6` to match the
file as it stands today, so whichever of the two lands second updates that value.

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
