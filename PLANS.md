# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._

### Fidelity mismatch bounds: share row and column interval collection (planned 2026-11-02 by the plan role)

**Goal.** Keep the two enclosing-interval diagnostics consistent with less duplicated bookkeeping. `tools/fidelity_spatial.py::difference_row_bounds` and `difference_column_bounds` repeat the same predicate and first/last tracking with swapped axes. Source and archive searches found the public diagnostics and the separate run-collector extraction, but no shared bounds collector. This cleanup is independent of the waiting sampler summary.

**Approach and files.** Extract `_difference_axis_bounds(candidate, reference, tolerance, *, vertical)` in `tools/fidelity_spatial.py`; keep both public functions as wrappers selecting the axis. Choose scanline count/length and output keys once: horizontal uses height/width and `x`/`width`, vertical uses width/height and `y`/`height`. Map each scanline/offset to the existing row-major pixel index, compare with `_absolute_deltas` using strict maximum-channel delta greater than tolerance, and collect first/last offsets. Emit one entry per scanline, `None` for no mismatch or an inclusive enclosing interval, preserving key order and gaps. Retain direct/package imports and avoid a mask, transposed image or run-list intermediary. Extend `tests/test_fidelity_row_bounds.py::TestDifferenceRowBounds` and `tests/test_fidelity_column_bounds.py::TestDifferenceColumnBounds`; these three files bound the change. The row/column bounds guarantees in docs/invariants.md remain the contract; no guarantee, CLI or report-format change is intended.

**Acceptance criteria.** Explicit expected dictionaries for nonsquare fixtures pin each axis, disconnected mismatches, empty scanlines, first/last offsets and inclusive lengths. Cover single pixel, single row, single column, identical images and full mismatch coverage; retain strict tolerance-boundary exclusion, absent alpha as 255, alpha-only differences and RGB beneath zero alpha. Existing CLI cases retain crop-relative JSON/text output, combined row/column reporting, PASS/FAIL behavior, omission without flags, direct-script invocation and usage/read errors. Add a transpose-equivalence test with an explicit expected result as well, so axis mapping cannot pass solely through shared assumptions. Run `make check` after final edits. Keep this a small extraction without combining scans across separately requested diagnostics.

## Done
