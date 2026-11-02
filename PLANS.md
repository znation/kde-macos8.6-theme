# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Fidelity diagnostics: locate vertical mismatch bounds per column (planned 2026-11-02 by the plan role)

**Goal and grounding.** Locate the vertical extent of side-border and widget-edge mismatches without inspecting individual pixels. `tools/fidelity_pixels.py::difference_columns` counts mismatches but does not locate them; `difference_row_bounds` provides the horizontal counterpart. Searches of source, tests and planned/finished entries found no column-bounds diagnostic. This is independent of the queued sampler extractions.

**Approach and files.** Add opt-in `--difference-column-bounds` in `tools/fidelity.py::main`, wiring both package and direct-script imports. Add `tools/fidelity_pixels.py::difference_column_bounds(candidate, reference, tolerance)` using `_absolute_deltas`: return a dense list indexed by crop-relative x, with `None` for an unchanged column or `{"y": first, "height": last-first+1}` for its smallest enclosing vertical interval of pixels with any raw RGBA delta strictly above tolerance. Unchanged gaps may lie inside an interval; missing alpha means 255 and stored RGB beneath transparency participates. Extend `tools/fidelity_reports.py::report_data` with optional keyword `column_bounds=None`, emitting `difference_column_bounds` only when supplied. In `render_text`, print `difference column bounds: ` plus the JSON array after row bounds and before the verdict. Keep metrics and budgets intact. Add `tests/test_fidelity_column_bounds.py` using `FidelityCliTestCase`, document crop-relative coordinates and source-origin translation in README.md, and add a dated tooling invariant in `docs/invariants.md`. These six files bound one run; no theme or dependency changes.

**Acceptance criteria.** Synthetic fixtures assert unchanged columns, a singleton, separated mismatches enclosing an unchanged gap, different vertical extents across columns, and bottom-edge mismatches on a nonsquare image. Cover tolerance equality versus exceedance, tolerance 255, alpha-only differences against an RGB image and stored RGB beneath zero alpha. CLI fixtures pin exact text/JSON arrays including null columns, unequal candidate/reference crop origins with nonzero y yielding crop-relative intervals, composition with row bounds and row/column counts, FAIL and aggregate-budget PASS with nonempty bounds, and direct-script execution. Assert no helper call, JSON key or text line without the flag; malformed input and dimension mismatch retain status 2 and empty stdout. Run `make check` after final edits.

## Done
