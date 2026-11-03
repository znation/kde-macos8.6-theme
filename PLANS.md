# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Fidelity diagnostics: filter short vertical mismatch runs (planned 2026-11-02 by the plan role) — done 2026-11-02 by the feature role

**Goal.** Isolate sustained side-border mismatches from short vertical fragments in fidelity reports. Source and related archive searches found vertical interval lists and longest summaries but no vertical minimum-length filter. This is independent of the waiting sampler plan and extends the finished horizontal fidelity filter.

**Approach and files.** Added optional `--min-difference-column-run-length N` using the existing `positive_int` factory and `None` default. The CLI requires `--difference-column-runs` before reading sources. It filters collected column intervals inclusively after computing the longest summary. Documentation and invariants describe the behavior.

**Acceptance criteria.** Added tests for crop-relative vertical intervals, inclusive filtering, cutoff one, empty output, retained longest summaries, helper reuse, parser behavior, invalid values and pre-read dependency validation. `make check` verifies the completed change.

## Done
