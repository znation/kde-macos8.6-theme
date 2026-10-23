# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### Fidelity drops alpha, so a fully transparent candidate passes the byte-exact gate (found by the qa role 2026-10-23)

`python3 tools/fidelity.py CANDIDATE REFERENCE` compares only each pixel's red, green and blue
bytes. A candidate that matches the reference's RGB but not its alpha therefore reports zero
error and passes the default no-differing-pixel gate. Reproduction (any 8-bit RGBA PNG encoder;
this uses ImageMagick, and the two images differ only in alpha):

```
$ tmp=$(mktemp -d) && cd "$tmp"
$ magick -size 2x2 xc:'rgba(0,0,0,1)' PNG32:opaque.png
$ magick -size 2x2 xc:'rgba(0,0,0,0)' PNG32:clear.png
$ python3 <repo>/tools/fidelity.py clear.png opaque.png
candidate: clear.png  2x2
reference: opaque.png  2x2
pixels compared: 4
mean absolute error: 0.0000
per-channel MAE (R, G, B): 0.0000 0.0000 0.0000
RMSE: 0.0000
max channel delta: 0 at (0, 0)
differing pixels: 0 / 4 (0.000000)
PASS: max-mae=unset max-frac=unset tolerance=0
$ echo $?
0
```

Expected: the default gate fails with exit 1 and a nonzero differing-pixel count, because every
pixel's alpha differs by 255; README's "Fidelity checking" says a run passes only when no pixel
differs from the reference, and docs/invariants.md's tooling row says the gate passes only when no
pixel differs beyond its tolerance. Actual: exit 0 and a byte-exact report for a fully
transparent surface. If RGB-only comparison is intentional, the README and that invariant need to
say alpha is not compared; as written a user cannot tell a transparent surface from the reference.

Suspected cause: `tools/png/read.py`'s `decode_png` drops the alpha byte of a color-type-6 image
(`drop_alpha`) before unfiltering, and `read_png` returns the `Image` type that
`tools/png/image.py` describes as an 8-bit RGB buffer, so `tools/fidelity_metrics.compare` never
sees alpha. The RGBA decoder (`read_rgba`) exists for the cursor PNGs but the fidelity CLI uses
the RGB path.

**Validation gap:** none — the dropped alpha bytes are deterministic and the CLI reproduces
the pass offline.

### The cursor generator test patches a removed `_write_atomic` symbol (found by the plan role 2026-10-23)

`tests/test_cursors_theme.py::TestMainErrors.test_reports_a_failed_write_and_stops_at_that_cursor`
reads and patches `make_cursors._write_atomic`, but `tools/make_cursors.py` no longer defines that
name: the dedupe change `15a43bb2` replaced the generator's private wrapper with the shared
`tools.atomic_write.write_bytes_atomically`. Running
`make check CHECK_TESTS=test_cursors_theme` errors with `AttributeError: module
'tools.make_cursors' has no attribute '_write_atomic'`. The test's intent is still valid --
simulate a failed write on the `arrow` alias and assert the generator stops after writing
`left_ptr` -- so patch the imported `make_cursors.write_bytes_atomically` name the generator
actually calls and keep the attempted/stop expectations.

**Validation gap:** none — the stale symbol fails deterministically when the module runs.

## Fixed
