# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Fidelity diagnostics: filter short vertical mismatch runs (planned 2026-11-02 by the plan role) — done 2026-11-02 by the feature role

**Goal.** Isolate sustained side-border mismatches from short vertical fragments in fidelity reports. Source and related archive searches found vertical interval lists and longest summaries but no vertical minimum-length filter. This is independent of the waiting sampler plan and extends the finished horizontal fidelity filter.

**Approach and files.** Added optional `--min-difference-column-run-length N` using the existing `positive_int` factory and `None` default. The CLI requires `--difference-column-runs` before reading sources. It filters collected column intervals inclusively after computing the longest summary. Documentation and invariants describe the behavior.

**Acceptance criteria.** Added tests for crop-relative vertical intervals, inclusive filtering, cutoff one, empty output, retained longest summaries, helper reuse, parser behavior, invalid values and pre-read dependency validation. `make check` verifies the completed change.

### Reference-pixel sampler: filter histogram colors by region fraction (planned 2026-11-02 by the plan role)

**Goal.** Suppress minor palette fragments with a crop-size-independent cutoff. Searches of sampler code, tests and plan headings found count filtering and fraction reporting, but no fraction filter; the finished minimum-count and color-fractions plans cover those separate capabilities. This work is independent of the queued fidelity filter.

**Approach and files.** Add optional `--min-color-fraction F` with default `None` in `tools/sample_arguments.py::build_parser`, a local validator using `plain_number(..., float)` accepting finite values from 0 through 1 inclusive, and an `option_error` dependency diagnostic `--min-color-fraction requires --histogram`. In `tools/sample_report_histogram.py::_histogram_result`, retain colors whose `count / (args.width * args.height) >= F`, using the same Python float division as `--color-fractions`. Apply this and any minimum-count predicate before top-color selection; both predicates must hold. Extend the existing totals condition in result assembly and `report_histogram` so explicit fraction filtering emits original `total_colors` and full-region `omitted_pixels`, including at F=0. Preserve tuple tie order, full counts, fraction denominators and emitted-color spatial diagnostics; add no traversal or dependency. Add `tests/test_sample_histogram_min_fraction.py` following `TestSampleHistogramMinimumCount`, extend `tests/test_sample_option_validation.py`, and document the option in README.md and the sampler rows of docs/invariants.md. These six files bound one implementation run.

**Acceptance criteria.** Pin text and JSON results for an offset nonsquare crop with color shares below, equal to and above the cutoff; verify equivalent proportions at two crop sizes. Cover F=0 (same colors as no filter, with totals), F=1 for uniform and mixed regions, an empty palette, tuple ties, joint minimum-count filtering and top-N truncation. Check original distinct-color totals and omitted-pixel accounting, full-region reported fractions, and absolute bounds/positions/centroids for retained colors. Include RGBA separation, RGB beneath alpha zero and opaque fallback. Reject negative, above-one, NaN, infinity, underscore, whitespace, non-ASCII, malformed and missing values with status 2 and empty stdout; accept ordinary decimal and exponent notation. Mock image reads to establish that invalid scalar values and histogram dependency errors precede I/O. Pin parser default, help visibility, direct-script/package parity and omitted-option output; run `make check` after final edits. No theme visual values change.

## Done
