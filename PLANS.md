# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._

### Fidelity mismatch counts: share row and column scanline collection (planned 2026-11-02 by the plan role)

**Goal.** Reduce duplicated mismatch-count logic while preserving the dense row and column diagnostics. `tools/fidelity_spatial.py::difference_rows` and `difference_columns` currently implement separate loops and equivalent tolerance predicates. Source and archive-heading searches found their diagnostic additions and the separate bounds/run extractions, but no shared count collector. This is independent of the queued vertical sampler summary.

**Approach and files.** Extract `_difference_axis_counts(candidate, reference, tolerance, *, vertical)` in `tools/fidelity_spatial.py`; retain the public functions as wrappers selecting the axis. Select scanline count/length once, map scanline/offset to the row-major pixel index, and count each pixel once when `max(_absolute_deltas(...)) > tolerance`. Cache image byte buffers locally as the row implementation does. Return a dense integer list including empty scanlines, with no mask, transpose buffer or interval-list intermediary. Extend `tests/test_fidelity_difference_rows.py::TestDifferenceRows` and `tests/test_fidelity_difference_columns.py::TestDifferenceColumns`; these three files bound the implementation. Preserve package/direct imports and the contracts in docs/invariants.md's fidelity row/column count entries. No CLI or report-format change is intended; keep separately requested diagnostics as separate scans.

**Acceptance criteria.** Literal expected row and column arrays on a nonsquare fixture pin axis mapping, zero scanlines, edge pixels and multiple changed channels contributing just one count. Cover single pixel, single row, single column, identical images and full mismatches; retain strict tolerance-boundary exclusion, tolerance 255, alpha-only differences, missing alpha as 255 in either operand, and stored RGB beneath zero alpha. For each axis assert the array sum equals `tools/fidelity_metrics.py::compare(...).differing`. Retain existing CLI crop-relative text/JSON, flag composition, verdict, default omission and error coverage; extend the combined-options case to assert both arrays explicitly and cover direct-script invocation with both flags. Keep the extraction and tests within a few hundred changed lines and run `make check` after final edits.

## Done
