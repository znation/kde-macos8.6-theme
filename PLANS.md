# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Fidelity diagnostics: filter short vertical mismatch runs (planned 2026-11-02 by the plan role) — done 2026-11-02 by the feature role

**Goal.** Isolate sustained side-border mismatches from short vertical fragments in fidelity reports. Source and related archive searches found vertical interval lists and longest summaries but no vertical minimum-length filter. This is independent of the waiting sampler plan and extends the finished horizontal fidelity filter.

**Approach and files.** Added optional `--min-difference-column-run-length N` using the existing `positive_int` factory and `None` default. The CLI requires `--difference-column-runs` before reading sources. It filters collected column intervals inclusively after computing the longest summary. Documentation and invariants describe the behavior.

**Acceptance criteria.** Added tests for crop-relative vertical intervals, inclusive filtering, cutoff one, empty output, retained longest summaries, helper reuse, parser behavior, invalid values and pre-read dependency validation. `make check` verifies the completed change.

### Reference-pixel sampler: filter histogram colors by region fraction (planned 2026-11-02 by the plan role) — done 2026-11-02 by the feature role

**Goal.** Suppress minor palette fragments with a crop-size-independent cutoff. Implemented `--min-color-fraction` alongside minimum-count filtering. The cutoff uses each color's fraction of the requested region and preserves full-region totals and diagnostics.

**Approach and files.** Added optional `--min-color-fraction F` with default `None` and a finite 0–1 validator in `tools/sample_arguments.py`, plus pre-read histogram dependency validation. Histogram selection in `tools/sample_report_histogram.py` applies the inclusive full-region fraction and minimum-count predicates before top-color selection. Explicit filtering reports original distinct-color totals and omitted pixels. Added focused crop, composition, spatial, alpha, parser, and validation coverage in `tests/test_sample_histogram_min_fraction.py` and `tests/test_sample_option_validation.py`; documented behavior in README.md and the sampler invariants.

**Acceptance criteria.** Tests pin offset crop thresholds, proportional crops, F=0/F=1 behavior, totals, joint count/fraction and top-N filtering, spatial diagnostics, RGBA separation and opaque fallback, invalid-value pre-read rejection, parser default, decimal/exponent acceptance, and direct-script parity. `make check` passed after final edits. No theme visual values changed.

