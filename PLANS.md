# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Reference-pixel sampler: filter histogram colors by region fraction (planned 2026-11-02 by the plan role) — done 2026-11-02 by the feature role

**Goal.** Suppress minor palette fragments with a crop-size-independent cutoff. Implemented `--min-color-fraction` alongside minimum-count filtering. The cutoff uses each color's fraction of the requested region and preserves full-region totals and diagnostics.

**Approach and files.** Added optional `--min-color-fraction F` with default `None` and a finite 0–1 validator in `tools/sample_arguments.py`, plus pre-read histogram dependency validation. Histogram selection in `tools/sample_report_histogram.py` applies the inclusive full-region fraction and minimum-count predicates before top-color selection. Explicit filtering reports original distinct-color totals and omitted pixels. Added focused crop, composition, spatial, alpha, parser, and validation coverage in `tests/test_sample_histogram_min_fraction.py` and `tests/test_sample_option_validation.py`; documented behavior in README.md and the sampler invariants.

**Acceptance criteria.** Tests pin offset crop thresholds, proportional crops, F=0/F=1 behavior, totals, joint count/fraction and top-N filtering, spatial diagnostics, RGBA separation and opaque fallback, invalid-value pre-read rejection, parser default, decimal/exponent acceptance, and direct-script parity. `make check` passed after final edits. No theme visual values changed.

