# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Reference-pixel histogram: separate result assembly from printing (planned 2026-11-02 by the plan role)

**Goal and grounding.** Make palette calculations testable without capturing stdout. `tools/sample_report_histogram.py::report_histogram` combines counting, top-color selection, optional positions/bounds and two output formats. The archived histogram-handler split moved that branch together; source and archive searches found no separate histogram result assembler. This maintenance change is independent of the waiting color-search series.

**Approach and files.** Extract `_histogram_result(args, image, width, height) -> dict` in `tools/sample_report_histogram.py`, returning the existing JSON envelope, including its ordered color records and optional truncation totals. Keep counting, sorting and optional positioned traversal in that helper. Have `report_histogram` call it once, then print JSON or render text from its fields, preserving the current text suffix order (alpha, bounds, fraction, position), which differs from JSON field order. Keep both functions in the existing module; add no result class, wrapper or dependency. Add `tests/test_sample_histogram_result.py` using parser namespaces and synthetic images, following the fixtures in `tests/test_sample_histogram_positions.py`. Read the sampler guarantees in `docs/invariants.md`; this extraction introduces no new CLI guarantee and requires no register change. Limit changes to the handler and focused test file.

**Acceptance criteria.** Direct helper tests assert explicit dictionaries for RGB tie ordering and a cropped RGBA histogram combining top-color truncation, fractions, disconnected bounds and first positions; include zero-alpha RGB and opaque fallback. Assert no stdout or namespace mutation. Characterize exact text and JSON CLI output for the combined case, including field/line order and omitted totals, and compare package/direct-script stdout, stderr and status. Preserve full-region counts and fraction denominators, absolute coordinates, optional diagnostic omission and one shared positioned traversal when bounds and positions are combined; retain existing traversal/PNG-decode tests. Do not change the accumulation algorithm or add options in this extraction. Run `make check` after final edits. Keep the implementation within a few hundred changed lines including tests.

### Reference-pixel scanline reports: separate result assembly from printing (planned 2026-11-02 by the plan role)

**Goal and grounding.** Make rectangular run-report assembly directly testable without capturing stdout. `tools/sample_report_runs.py::_color_runs` returns one scanline's segments, but `report_runs` still chooses the axis, enumerates scanlines, flattens segments and builds the JSON envelope alongside printing. The archived scanline-handler extraction and rectangular-axis feature cover those earlier steps, not a complete report assembler. This change is independent of the waiting histogram extraction.

**Approach and files.** Extract `_runs_result(args, image, width, height) -> dict` inside `tools/sample_report_runs.py`, returning the existing JSON envelope with image metadata, region, axis and JSON-ready run records. Move axis selection and scanline enumeration into it, retaining `_color_runs` and its grouping algorithm. Have `report_runs` call the helper once and print JSON or text from its fields. Preserve record insertion order, including the existing alpha-before-hex JSON order when alpha is enabled, and text's length-before-alpha suffix. Add `tests/test_sample_runs_result.py` following the parser-namespace and synthetic-image pattern in `tests/test_sample_search_result.py`; extend `tests/test_sample_runs.py` for exact CLI output where needed. Read the scanline guarantee in `docs/invariants.md`; no new CLI guarantee or register update is intended. Keep implementation and tests within a few hundred changed lines, with no new module abstraction or dependency.

**Acceptance criteria.** Direct helper tests assert explicit complete dictionaries for cropped horizontal and vertical rectangular scans, including equal colors on neighboring scanlines that must remain separate, separated occurrences within one scanline, inferred axes and an explicit vertical singleton. Cover RGBA transitions, stored RGB beneath zero alpha, RGB-only grouping and opaque alpha fallback; assert no stdout or mutation of arguments/image buffers. Characterize exact text and serialized JSON for a cropped RGBA case, including key order and trailing newline, and compare package/direct-script stdout, stderr and exit status. Preserve absolute origins, traversal order and omitted alpha fields; retain existing single-line, rectangle, argument-validation and bounded-decode coverage. Do not change grouping, decoding or options. Run `make check` after final edits.

## Done
