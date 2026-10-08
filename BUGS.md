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
writes a PNG. None exists; `make check` exercises the installed packages and the comparison tool,
but nothing renders a surface.

**Suspected cause:** The desktop theme now ships `widgets/panel-background.svg`, so there is a
surface to render, but no offline render path exists: capturing a themed Plasma surface needs a
running session or a QML harness, neither of which `make check` can drive.

**Next step:** With the Platinum panel background now shipping, add a bounded, non-interactive
render-and-capture script (fixed surface size) that writes the candidate PNG this tool consumes,
once an offline render path is available, and wire it into `make check`.

**Refused 2026-10-07 by bugfix: no offline QML/Plasma render path is available, so a render harness now would be untestable dead code.**

### Palette anchors are not re-derivable from the reference screenshots (structural risk, found 2026-10-07)

**Symptom:** `tests/test_colorscheme.py`'s `TestAnchors` pins the Platinum palette (Window/Button/
Header face `221,221,221`, view `255,255,255`, selection `206,206,255`, tooltip `255,255,204`,
chrome `0,0,0`) and PLANS.md attributes each value to a named retail screenshot
(`desktop_archiveorg8.6hd.png`, `desktop_fandom.png`, `opendialog_macrumors86.jpg`), but no code
reads those images' pixels. The test compares the scheme file to hard-coded strings, so a wrong
anchor or a swapped reference image passes unnoticed: the image-to-value chain lives only in prose.

**How to reproduce:** Search `tests/` and `tools/` for code that reads pixel data from
`macos8.6-screenshots/`. Only `tools/check_references.py` opens that directory, and only for
provenance (the file exists, is a materialized image of an accepted format), never pixel values.
Edit an expected string in `TestAnchors` to any other in-range value and `make check` still passes.

**Suspected cause:** The palette was sampled by hand with ImageMagick while planning; neither the
sample coordinates nor a re-derivation step were recorded, so the assertions check the scheme
against itself rather than against the reference set. `tools/fidelity.py` compares a candidate PNG
against a reference, but nothing points it at the shipped references or the scheme constants.

**Next step:** Record the sample point behind each anchor and add a check that decodes the
retail-labelled PNG references with `tools/png.py` and asserts the scheme's anchor values at those
points. The selection anchor's source (`opendialog_macrumors86.jpg`) is a JPEG, which the repo
cannot decode yet, so cover the PNG-sourced anchors first.

This complements the Open render/capture entry above: that one covers producing the candidate
surface, this one covers the ground truth it is measured against.

## Fixed

### `plasma-apply-colorscheme` writes a scheme ID that does not survive a restart (found 2026-10-07; fixed 2026-10-07)

**Symptom:** `plasma-apply-colorscheme MacOS8` — the ID the tool lists for the
then-named dotted scheme file — reports success and writes `[General]
ColorScheme=MacOS8` into `kdeglobals`. On the next load KDE resolves that value to
`MacOS8.colors`, which does not exist, so the scheme silently falls back to BreezeLight. The value
that resolves to the shipped file is `MacOS8.6`.

**How to reproduce:** With `XDG_DATA_HOME` pointing at a data dir holding the scheme file under
its old dotted name, set the temp `XDG_CONFIG_HOME`'s `kdeglobals` to
`[General] ColorScheme=MacOS8` and run `plasma-apply-colorscheme` with no argument: it prints
`Could not find color scheme "MacOS8" falling back to BreezeLight`. Repeat with
`ColorScheme=MacOS8.6`: it resolves. Applying via the CLI looks correct in the running session, so
the breakage appears only at the next start.

**Suspected cause:** The tool derives a scheme's CLI id from the filename up to the first dot
(`MacOS8`), while its resolver turns the `ColorScheme` config value into `<value>.colors`. A
filename containing a dot therefore has a CLI id that no longer names the file.

**Fix:** Renamed the scheme file from its old dotted name to `MacOS8.colors` and set its `[General]
ColorScheme=MacOS8`, so the filename stem KDE lists as the CLI id equals the value it writes into
`kdeglobals` and resolves back to the file. Updated the `Makefile` install target, the install-path
assertion in `tests/test_colorscheme.py`, the README Installing section, and the look-and-feel
plan's `ColorScheme`. `tests/test_colorscheme.py` adds
`test_cli_id_matches_filename_and_config_value` (asserts the filename stem equals `[General]
ColorScheme` and that `<stem>.colors` exists) and
`TestRestartRoundTrip.test_applied_id_survives_restart` (applies the listed id in a temp
`XDG_DATA_HOME`/`XDG_CONFIG_HOME`, then runs `plasma-apply-colorscheme` with no argument and fails
if it prints `Could not find`); both fail against the dotted filename and pass after the rename.

**Validation gap:** real-run-needed — the breakage appears only on the next load, and no existing
test exercised KDE's scheme resolver, so confirming it required a bounded run of the real
`plasma-apply-colorscheme` against a temp config (now covered by the round-trip test).

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
`tests/test_png.py` covers decoding (palette plus every PNG filter type); `tests/test_fidelity.py`
covers the metrics, cropping, and the CLI pass/fail paths. Producing the candidate PNG (the Plasma
render step) is still missing and is tracked as its own Open entry above.

**Validation gap:** unclear-invariant — "pixel-perfect" had no numeric definition and the repo had
no comparison path, so the objective metric and threshold had to be defined before the gap could be
confirmed.
