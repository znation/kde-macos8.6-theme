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

**Symptom:** `tests/test_colorscheme.py`'s `TestReferenceAnchors` now ties the menu-bar face
(`Window`/`Button`/`Header`), view background and chrome foreground to pixels of
`desktop_archiveorg8.6hd.png`, and the selection background to a pixel of `firstboot_betawiki.png`,
but the tooltip anchor (`255,255,204`) still lives only as a hard-coded string in `TestAnchors`: in
`macos8.6-screenshots/` that colour occurs only as anti-aliasing fragments — diagonal edges and a
few small glyph-like clusters — never as a balloon, so there is no pixel to re-derive it from.

**How to reproduce:** Decode every PNG in `macos8.6-screenshots/` with `tools/png.py` and search
for `255,255,204`. The hits are anti-aliasing fragments, not a balloon: a 185-pixel diagonal edge
(at (966–984, 289–311) in `desktop_betawiki.png` and `firstboot_betawiki.png`, and (838–856, 33–55)
in `desktop_betawiki86b9.png`), small glyph-like clusters near (388–397, 77–88) in
`firstboot_betawiki.png`, and isolated single pixels in `desktop_fandom.png` and several
`*_betawiki.png` screenshots. Decoding the JPEGs (via a converter, since `tools/png.py` cannot read
them) and searching likewise finds no pale-yellow balloon.

**Suspected cause:** The palette was sampled by hand with ImageMagick while planning; the tooltip
token has no recorded sample point, and none of the collected reference screenshots happens to show
a tooltip.

**Next step:** Source a retail Mac OS 8.6 screenshot that shows a tooltip / Balloon Help balloon,
then record its sample point and add the tooltip anchor to `TestReferenceAnchors`.

This complements the Open render/capture entry above: that one covers producing the candidate
surface, this one covers the ground truth it is measured against.

## Fixed

### Selection palette anchor is not re-derivable (found 2026-10-07; fixed 2026-10-08)

**Symptom:** `TestAnchors` pinned the selection anchor (`206,206,255`) to a hard-coded string and
no test read a reference pixel for it, so a wrong value passed unnoticed. The value had been
sampled from `opendialog_macrumors86.jpg`, a lossy JPEG the repository cannot decode.

**How to reproduce:** Point `TestReferenceAnchors` at the Setup Assistant list selection in the
retail `firstboot_betawiki.png` (its fill at `(200, 63)`). With the scheme at `206,206,255` the
test fails: `(204, 204, 255) != (206, 206, 255)`.

**Suspected cause:** JPEG chroma loss shifted the hand-sampled value; the lossless retail PNGs
(`firstboot_betawiki.png`, `setup_betawiki.png`) show the selection fill as `204,204,255`.

**Fix:** Corrected `[Colors:Selection] BackgroundNormal`/`BackgroundAlternate` to `204,204,255` in
`theme/color-schemes/MacOS8.colors`, updated `TestAnchors`, and added
`TestReferenceAnchors.test_selection_background`, which decodes `firstboot_betawiki.png` with
`tools/png.py` and asserts the selection fill at `(200, 63)`. The tooltip anchor remains ungrounded
(see the palette-anchor entry under Open).

**Validation gap:** unclear-invariant — confirming the bug meant deciding which reference was
authoritative, because the lossless retail PNG (`204,204,255`) disagreed with the value hand-sampled
from the lossy JPEG (`206,206,255`).

### `--tolerance` does not gate the fidelity exit status; README documents no pass threshold (found 2026-10-07; fixed 2026-10-07)

**Symptom:** README's "Fidelity checking" section says the tool exits non-zero "when the result is
outside the requested tolerance" and documents only `--crop`. Requesting a tolerance with
`--tolerance N` on a candidate whose worst channel delta is exactly `N` still exits 1 (FAIL),
because the verdict also requires `mae <= --max-mae` and `frac_differing <= --max-frac`, both
defaulting to 0 and neither mentioned in the README. The tool's own `--help` epilog ("0 within
tolerance") has the same contradiction, so a first-time user cannot make a within-tolerance
comparison pass from the documentation alone.

**How to reproduce:**

```
cd <repo>
python3 - <<'PY'
import sys; sys.path[:0] = ['.', 'tests']
from png_fixtures import make_png, rgb_image
ref, ref_png = rgb_image(3, 3, lambda x, y: (x * 20, y * 20, 60))
open('/tmp/ref.png', 'wb').write(ref_png)
c = bytearray(ref.rgb); c[4] = 50  # pixel (1,0) green: 0 -> 50
open('/tmp/cand.png', 'wb').write(make_png(3, 3, [bytes(c[i:i+9]) for i in range(0, 27, 9)]))
PY
python3 tools/fidelity.py /tmp/cand.png /tmp/ref.png --tolerance 50
```

Expected: exit 0 (PASS) — the worst channel delta, 50, is within the requested `--tolerance 50`
and the tool reports `differing pixels: 0 / 9`. Actual: exit 1 (FAIL), printing
`FAIL: max-mae=0.0000 max-frac=0.000000 tolerance=50`.

**Suspected cause:** `main` computes `ok = metrics.mae <= args.max_mae and
metrics.frac_differing <= args.max_frac`; `--tolerance` only feeds `compare(tolerance=...)`, which
affects the differing-pixel count, not `mae`. The README and the help epilog present `--tolerance`
as the pass/fail knob when it is not.

**Fix:** `--max-mae` and `--max-frac` now default to unset (`None`) instead of 0, and the verdict
is the conjunction of the budgets the caller actually set; with neither set it falls back to the
strictest gate, no pixel differing by more than `--tolerance` (so the default stays byte-exact, and
`--tolerance` alone now gates as the README promised). The verdict line prints `unset` for an
unset budget, and the README's Fidelity section and the `--help` epilog document the rule.
`tests/test_fidelity_cli.py` adds `TestCli.test_tolerance_is_the_default_gate` (a candidate whose worst
delta equals `--tolerance` passes and one above it fails) and
`TestCli.test_explicit_budget_replaces_default_gate` (`--max-mae` alone is the criterion); both
fail before the change and pass after. A coverage pass (2026-10-08) added
`TestCli.test_max_frac_budget_is_the_verdict` (`--max-frac` alone is the criterion; its generous
case fails before the fix) and `TestCli.test_both_budgets_must_be_met` (with both budgets set,
either unmet budget fails the run, pinning the conjunction rather than `any()`).

**Validation gap:** none — the existing suite had no case for it, but a deterministic scratch repro
built from the shipped `png_fixtures` confirmed the failure offline, so nothing was missing.

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
`tests/test_png.py` covers decoding (palette plus every PNG filter type);
`tests/test_fidelity_metrics.py` covers the metrics and cropping, and
`tests/test_fidelity_cli.py` covers the CLI pass/fail paths. Producing the candidate PNG (the Plasma
render step) is still missing and is tracked as its own Open entry above.

**Validation gap:** unclear-invariant — "pixel-perfect" had no numeric definition and the repo had
no comparison path, so the objective metric and threshold had to be defined before the gap could be
confirmed.
