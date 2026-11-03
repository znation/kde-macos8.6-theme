# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Reference-pixel reports: share lazy pixel-record assembly (planned 2026-11-02 by the plan role)

**Goal and grounding.** Make ordinary sample records testable independently of printing and remove the separate RGB/alpha assembly paths in `tools/sample_report_pixels.py::report_pixels`. That handler builds JSON records, directly indexes a text singleton, and separately traverses text rectangles. `_positioned_region_pixels` supplies coordinates but not report records. Source and planned/finished-heading searches found no shared ordinary-record assembler; the archived pixel-handler split moved these branches together. This work is independent of the waiting histogram extraction.

**Approach and files.** Add `_pixel_records(args, image)` in `tools/sample_report_pixels.py`: a lazy iterator yielding the existing JSON pixel dictionaries, in insertion order `x`, `y`, `rgb`, `hex`, then optional `alpha`. Reuse `_positioned_region_pixels`, `_region_alpha` and `_hex`, leaving those shared primitives' signatures intact. Make `report_pixels` consume that iterator for JSON, text singleton and text rectangle output. JSON may materialize its existing `pixels` list; text must consume records incrementally rather than allocate a rectangle-sized list. Leave envelope construction in `report_pixels`; no new option, module, dependency or result class. Extend `tests/test_sample_report_pixels.py` for direct iterator tests and `tests/test_sample_alpha.py` for exact CLI characterization. Read the tooling rows in `docs/invariants.md`; this internal extraction does not change their CLI guarantees or require a register change. Limit implementation to these three files and a few hundred changed lines including tests.

**Acceptance criteria.** Direct tests assert explicit records for an offset multi-row RGB rectangle, RGBA with zero and intermediate alpha, opaque alpha fallback, singleton shape, absolute row-major coordinates and uppercase hex. Without `--alpha`, records omit alpha and never access the alpha plane. Assert iterator construction reads no pixels and requesting the first record does not consume the next positioned pixel; assert no stdout or argument mutation. Pin complete text and JSON CLI output for singleton and offset rectangle samples, with and without alpha, including header dimensions, spacing, key order and trailing newline. Compare package/direct-script stdout, stderr and status for an ordinary RGBA case. Retain the bounded-decode and stored-RGB-under-zero-alpha coverage in `TestSampleAlpha`, and the shared traversal test in `TestPositionedRegionPixels`. Run `make check` after final edits.

## Done
