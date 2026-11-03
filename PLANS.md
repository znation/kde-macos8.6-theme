# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._

### Reference-pixel sampler: filter short scanline color runs (planned 2026-11-02 by the plan role)

**Goal.** Find long reference border bands without printing short glyph and texture fragments. Source and archive searches found RGB/RGBA scanline grouping, rectangular axes and report assembly, but no minimum-length filter. This is independent of the queued vertical fidelity summary.

**Approach and files.** Add `--min-run-length N` with `positive_int` and an absent default in `tools/sample_arguments.py::build_parser`; `option_error` requires `--runs` before image reads. In `tools/sample_report_runs.py::_runs_result`, filter completed `_color_runs` records by inclusive length before adding them to the emitted list. Keep grouping within each scanline: removing a short run must never join separated same-color runs. Preserve the existing JSON envelope and text header with no new metadata; an empty result is `runs: []` in JSON and just the existing header/region/axis lines in text. This is an output filter, not a decoding optimization. Add `tests/test_sample_runs_min_length.py` using `CliTestCase`, extend `tests/test_sample_option_validation.py`, and document the option in README.md and the sampler scanline guarantee in docs/invariants.md. Keep the change to these six files and a few hundred lines including tests; do not change match-run or fidelity diagnostics.

**Acceptance criteria.** Assert literal text and JSON results for offset horizontal and vertical rectangular regions with runs shorter than, equal to and longer than the cutoff. Include separated equal-color runs around an omitted segment and adjacent scanlines of the same color to prove neither merges. Cover inferred axes, an explicit vertical singleton, cutoff 1 matching omitted-option output, and a cutoff beyond scanline length yielding the defined empty output. Verify RGB grouping, RGBA boundaries, stored RGB beneath zero alpha and opaque alpha fallback. Reject zero, negative, non-ASCII, malformed and missing values with status 2; valid numeric use without `--runs` must emit `--min-run-length requires --runs` before either PNG reader runs. Compare direct-script and package output/status for a filtered case and retain the existing bounded-decoding checks. Run `make check` after final edits.

## Done
