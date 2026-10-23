# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### A palette image with tRNS before PLTE is accepted (found by the bugfix role 2026-10-23)

The PNG specification requires a `tRNS` chunk to follow `PLTE`. `tools/png/stream.py`'s
`collect_chunks` collects the two payloads independently and checks only that both precede
`IDAT`, so a color type 3 image carrying `tRNS` before `PLTE` decodes on both the RGB and RGBA
paths. Reproduce by assembling the chunks by hand:
`_PNG_SIGNATURE + ihdr_chunk(1, 1, 3) + _chunk(b"tRNS", bytes([0, 128])) + _chunk(b"PLTE",
bytes([255, 0, 0, 0, 255, 0])) + _chunk(b"IDAT", zlib.compress(bytes([0, 0]))) +
_chunk(b"IEND", b"")`; both `decode_png` and `decode_rgba` return the image. Suspected cause:
no ordering guard for `tRNS` against an earlier-or-absent `PLTE`; the missing-`PLTE` diagnosis
for color type 3 must keep winning when no palette appears at all.

## Fixed
