# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._

### Reference-pixel sampler: filter histogram colors by minimum count (planned 2026-11-02 by the plan role)

**Goal.** Let palette measurements suppress rare color fragments with an explicit frequency cutoff. `tools/sample_report_histogram.py::_histogram_result` supports a top-N limit but no minimum frequency; sampler code and related archive-heading searches found no minimum-count filter. This task is independent of the queued fidelity summary.

**Approach and files.** Add optional `--min-color-count N` with `positive_int` in `tools/sample_arguments.py::build_parser`, defaulting to None; `option_error` rejects use without `--histogram` before image access. In `tools/sample_report_histogram.py::_histogram_result`, count the complete crop as today, filter entries to count >= N, then apply the existing top-color selection and descending-count/ascending-color ordering. When either cutoff or top-N is supplied, report `total_colors` as the original distinct-color count and `omitted_pixels` as crop area minus emitted counts; `report_histogram` prints the existing totals under the same condition. A cutoff above the crop area succeeds with an empty colors array and the complete area omitted. Fractions retain the full crop denominator; spatial diagnostics operate on emitted colors and retain their existing meaning. Preserve output when the cutoff is omitted. Add `tests/test_sample_histogram_min_count.py` using the existing CLI fixtures, extend compatibility cases in `tests/test_sample_option_validation.py`, and document the option in README.md and the sampler histogram row of docs/invariants.md. Keep this to a few hundred changed lines; no decoding, search-mode or theme-art changes.

**Acceptance criteria.** Use literal expected text and JSON on an offset synthetic crop with unequal counts and a tie: prove inclusive threshold equality, excluded outside-crop pixels, stable ordering, threshold 1, a threshold exceeding area, and composition with top-N. Assert original distinct totals and omitted-pixel accounting for filtering alone and combined truncation, including no omissions. Cover RGB grouping versus RGBA separation, opaque-alpha fallback, full-region fractions, and emitted-color bounds/positions/centroids after filtering. Retain existing no-option output expectations and include direct-script invocation. Reject zero, negative, fractional, non-ASCII, missing and malformed N, plus use in pixel, runs and color-search modes, with exit 2, empty stdout and no image-size or decoder calls. Run `make check` after final implementation and documentation edits.

## Done
