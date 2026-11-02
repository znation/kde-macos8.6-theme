# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Split reference sampler report handlers by mode (planned 2026-11-02 by the organize role)

Needs review 2026-11-02 by feature: too large for one run

**Goal and grounding.** Reduce the concentration of unrelated behavior in `tools/sample_reports.py::report`. The 209-line module's single dispatcher implements four distinct modes—scanline runs, color histogram, color search, and individual pixel listing—and mixes pixel traversal, aggregation, result assembly, and text/JSON output. Its shape, rather than module length alone, is the reason to split it; the current implementation is too concentrated to refactor safely as this run's direct edit.

**Approach and files.** Keep `tools/sample_reports.py` as the small public dispatcher and move each mode's handler and mode-specific output assembly into `tools/sample_report_runs.py`, `tools/sample_report_histogram.py`, `tools/sample_report_search.py`, and `tools/sample_report_pixels.py`, respectively. Move shared pixel traversal and RGB formatting helpers (`_region_pixels`, `_positioned_region_pixels`, `_region_alpha`, `_hex`) into `tools/sample_report_pixels.py` as shared primitives, with the pixel-list handler named distinctly there. The dispatcher selects the existing mode precedence and passes the same arguments, image, dimensions, and header through. Update imports and references in source, tests, and markdown documentation; touch `tools/sample_reports.py`, the four new modules, tests that import internal helpers, README.md only if references require it, and `docs/invariants.md` if the tested guarantee's ownership changes. No CLI behavior or output changes.

**Acceptance criteria.** Preserve the current precedence (runs, histogram, find-color, JSON pixel listing, single pixel, region listing), text and JSON fields/order, alpha behavior, deterministic histogram sorting and bounds, and the current bounded coordinate behavior for color search. Add or adapt focused tests to exercise each handler through the CLI and pin its existing output; keep tests passing without introducing dependencies. Search source, tests, and markdown for moved names and old module references, then run `make check` after the final edits.

### Fidelity diagnostics: locate horizontal mismatch bounds per row (planned 2026-11-02 by the plan role)

**Goal and grounding.** Locate the horizontal extent of mismatch bands, such as the button rows in BUGS.md, without manually inspecting individual pixels. `tools/fidelity_pixels.py::difference_rows` gives counts but not locations; `Metrics.difference_bounds` gives one enclosing rectangle for the compared surface. Searches of fidelity source/tests and planned/finished headings found no per-row bounds report. This is independent of the queued sampler refactor and does not prescribe a fix for either held bug.

**Approach and files.** In `tools/fidelity.py::main`, add opt-in `--difference-row-bounds` beside the existing row/column diagnostics and wire both import paths. Add `tools/fidelity_pixels.py::difference_row_bounds(candidate, reference, tolerance)`, using `_absolute_deltas` to return a dense list indexed by crop-relative y: `None` for an unchanged row, otherwise `{"x": first, "width": last-first+1}` for the smallest horizontal interval enclosing pixels with any absolute RGBA delta strictly above tolerance. Gaps within an interval need not differ. Missing alpha is 255; compare stored RGB beneath transparency. In `tools/fidelity_reports.py::report_data` add optional keyword `row_bounds=None` and emit `difference_row_bounds` only when supplied; `render_text` prints `difference row bounds: ` plus the same JSON array immediately before the verdict, after existing row/column diagnostics. Keep metrics and verdict calculation intact. Add `tests/test_fidelity_row_bounds.py` using `FidelityCliTestCase`, document crop-relative coordinates and gaps in README.md, and add a dated tooling invariant in `docs/invariants.md`. These six files bound one run; no dependency or theme changes.

**Acceptance criteria.** Synthetic helper fixtures pin empty rows, a single pixel, separated pixels with an unchanged gap, differing left/right extents across rows, and far-edge pixels. Cover tolerance equality versus exceedance, tolerance 255, alpha-only changes against an RGB image, and stored RGB differences beneath zero alpha. CLI tests pin exact text/JSON arrays including null rows, unequal candidate/reference crop origins yielding crop-relative bounds, composition with `--difference-rows` and `--difference-columns`, FAIL and aggregate-budget PASS with nonempty bounds, direct-script imports, and existing read/dimension error status 2 with empty stdout. Assert the helper is not called and its key/text are absent without the flag. Run `make check` after final edits.

## Done
