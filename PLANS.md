# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Reference-pixel histogram: separate result assembly from printing (planned 2026-11-02 by the plan role)

**Goal and grounding.** Make palette calculations testable without capturing stdout. `tools/sample_report_histogram.py::report_histogram` combines counting, top-color selection, optional positions/bounds and two output formats. The archived histogram-handler split moved that branch together; source and archive searches found no separate histogram result assembler. This maintenance change is independent of the waiting color-search series.

**Approach and files.** Extract `_histogram_result(args, image, width, height) -> dict` in `tools/sample_report_histogram.py`, returning the existing JSON envelope, including its ordered color records and optional truncation totals. Keep counting, sorting and optional positioned traversal in that helper. Have `report_histogram` call it once, then print JSON or render text from its fields, preserving the current text suffix order (alpha, bounds, fraction, position), which differs from JSON field order. Keep both functions in the existing module; add no result class, wrapper or dependency. Add `tests/test_sample_histogram_result.py` using parser namespaces and synthetic images, following the fixtures in `tests/test_sample_histogram_positions.py`. Read the sampler guarantees in `docs/invariants.md`; this extraction introduces no new CLI guarantee and requires no register change. Limit changes to the handler and focused test file.

**Acceptance criteria.** Direct helper tests assert explicit dictionaries for RGB tie ordering and a cropped RGBA histogram combining top-color truncation, fractions, disconnected bounds and first positions; include zero-alpha RGB and opaque fallback. Assert no stdout or namespace mutation. Characterize exact text and JSON CLI output for the combined case, including field/line order and omitted totals, and compare package/direct-script stdout, stderr and status. Preserve full-region counts and fraction denominators, absolute coordinates, optional diagnostic omission and one shared positioned traversal when bounds and positions are combined; retain existing traversal/PNG-decode tests. Do not change the accumulation algorithm or add options in this extraction. Run `make check` after final edits. Keep the implementation within a few hundred changed lines including tests.

## Done
