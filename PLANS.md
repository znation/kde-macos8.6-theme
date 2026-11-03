# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._

### Fidelity mismatch runs: share axis traversal and interval assembly (planned 2026-11-02 by the plan role)

**Goal and grounding.** Keep horizontal and vertical mismatch segmentation consistent as fidelity tooling evolves. `tools/fidelity_pixels.py::difference_runs` and `difference_column_runs` duplicate predicate evaluation, gap handling and final-interval flushing with swapped axes. Source and archive heading searches found the two diagnostic additions, but no shared fidelity run collector. This maintenance task is independent of the waiting histogram extraction.

**Approach and files.** In `tools/fidelity_pixels.py`, extract `_difference_axis_runs(candidate, reference, tolerance, *, vertical)` and retain the two public functions as wrappers passing false and true respectively. Choose outer scanline count and inner scanline length from the axis once; map scanline/offset to x/y, compute the row-major pixel index, and reuse `_absolute_deltas` for the existing strict tolerance predicate. Share start tracking, gap emission and end-of-scanline flushing; construct records in x, y, length field order. Return the existing flat list without a full-image mask, transposed image or new dependency. Extend `tests/test_fidelity_difference_runs.py` and `tests/test_fidelity_column_runs.py`; these three files bound the implementation. Read the fidelity run rows in `docs/invariants.md`; this extraction preserves those guarantees and requires no CLI or report changes.

**Acceptance criteria.** Add explicit expected records for both public wrappers on one nonsquare fixture with separated intervals, adjacent mismatches of different magnitudes, empty scanlines, edge intervals and mismatches on opposite sides of a scanline boundary. Cover single-row, single-column and single-pixel images, equality at tolerance and tolerance 255, alpha-only differences, absent alpha as opaque and stored RGB beneath zero alpha. For each axis assert summed lengths equal `tools/fidelity_metrics.py::compare(...).differing`. Expected lists must be literal, not generated using the helper or by transposing its output. Preserve the existing CLI crop, text/JSON, composed-options, opt-in omission and direct-script tests. Run `make check` after final edits; keep implementation and tests within a few hundred changed lines.

## Done
