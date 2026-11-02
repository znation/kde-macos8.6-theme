# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Split reference sampler report handlers by mode (planned 2026-11-02 by the organize role)

**Goal and grounding.** Reduce the concentration of unrelated behavior in `tools/sample_reports.py::report`. The 209-line module's single dispatcher implements four distinct modes—scanline runs, color histogram, color search, and individual pixel listing—and mixes pixel traversal, aggregation, result assembly, and text/JSON output. Its shape, rather than module length alone, is the reason to split it; the current implementation is too concentrated to refactor safely as this run's direct edit.

**Approach and files.** Keep `tools/sample_reports.py` as the small public dispatcher and move each mode's handler and mode-specific output assembly into `tools/sample_report_runs.py`, `tools/sample_report_histogram.py`, `tools/sample_report_search.py`, and `tools/sample_report_pixels.py`, respectively. Move shared pixel traversal and RGB formatting helpers (`_region_pixels`, `_positioned_region_pixels`, `_region_alpha`, `_hex`) into `tools/sample_report_pixels.py` as shared primitives, with the pixel-list handler named distinctly there. The dispatcher selects the existing mode precedence and passes the same arguments, image, dimensions, and header through. Update imports and references in source, tests, and markdown documentation; touch `tools/sample_reports.py`, the four new modules, tests that import internal helpers, README.md only if references require it, and `docs/invariants.md` if the tested guarantee's ownership changes. No CLI behavior or output changes.

**Acceptance criteria.** Preserve the current precedence (runs, histogram, find-color, JSON pixel listing, single pixel, region listing), text and JSON fields/order, alpha behavior, deterministic histogram sorting and bounds, and the current bounded coordinate behavior for color search. Add or adapt focused tests to exercise each handler through the CLI and pin its existing output; keep tests passing without introducing dependencies. Search source, tests, and markdown for moved names and old module references, then run `make check` after the final edits.

## Done
