# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Reference-pixel sampler: isolate header-based region validation (planned 2026-11-02 by the plan role)

**Goal and grounding.** Make the sampler's pixel-versus-rectangle bounds policy directly testable without PNG reads. `tools/sample.py::main` currently formats and returns these errors inline between `read_png_size` and `read_png`; `tools/sample_arguments.py::option_error` covers option compatibility, not image bounds. Searches of sampler symbols and planned/finished headings found no bounds-validator extraction. This task is independent of the waiting lazy pixel-record assembly plan.

**Approach and files.** Add `tools/sample_arguments.py::region_error(args, image_width, image_height) -> str | None`. Move the existing singleton and rectangle bounds branches into it, returning the existing diagnostic or `None`, without printing, mutation or filesystem access. Its inputs are an already parsed namespace with positive extents and the PNG header dimensions; scalar validation remains in the parser. Call it from `tools/sample.py::main` immediately after the successful header read and before row decoding, reporting a returned message through `report_error("sample", message)`. Preserve package/direct-script imports and existing read entry points so decoder spies continue to work. Extend `tests/test_sample_option_validation.py` with direct bounds tests and CLI characterization. Read the sampler bounds row in `docs/invariants.md`; retain its guarantee and existing test anchor. Limit implementation to these three files, with no new module, dependency or CLI option.

**Acceptance criteria.** Direct tests cover valid corner pixels, a full-image rectangle, offset rectangles ending exactly at the right/bottom edges, one-row and one-column regions, negative origins, origins at the image dimensions, and right/bottom/combined overflow. Pin the exact singleton `pixel` and nonsingleton `region` diagnostics, including image dimensions; valid inputs return `None` and namespaces remain equal to their snapshots. CLI tests use mocked header dimensions and a decoder that fails if called to assert invalid bounds produce status 2, empty stdout and exact stderr. Preserve `TestSampleCli.test_decodes_only_through_the_samples`, `test_out_of_bounds_request_skips_the_row_decode` and corruption-below-sample coverage. Compare package and direct-script results for one invalid rectangle. Run `make check` after final edits.

## Done
